import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.foundation.embeddings import EmbeddingManager
from ai.foundation.llm_client import LLMClient
from ai.schemas.assistant import ChatResponse
from ai.services.advice import advice_service
from ai.vectorstore.pinecone_client import pinecone_client
from app.models.category import Category
from app.models.expense import Expense

logger = logging.getLogger(__name__)

RETRIEVAL_TOP_K = 5
NO_VECTOR_CONTEXT_CONFIDENCE = 0.35
VECTOR_CONTEXT_CONFIDENCE = 0.8


class QueryExecutor:
    """User question ko verified DB context + vector retrieval ke saath LLM tak pahuchata hai."""

    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager

    async def answer(
        self,
        db: AsyncSession,
        user_id: int,
        message: str
    ) -> ChatResponse:
        financial_context = await self._build_financial_context(db, user_id)
        retrieved_context, sources, scores = await self._retrieve(message, user_id)

        response = await advice_service.generate_response(
            message=message,
            financial_context=financial_context,
            retrieved_context=retrieved_context,
        )

        if scores:
            conf = max(scores)
        else:
            conf = 0.0
        if conf < 0.0:
            conf = 0.0
        if conf > 1.0:
            conf = 1.0

        return ChatResponse(
            response=response.strip(),
            sources=sources,
            confidence=round(conf, 4),
        )

    async def _build_financial_context(
        self,
        db: AsyncSession,
        user_id: int
    ) -> dict[str, Any]:
        today = date.today()
        window_start = today - timedelta(days=90)

        totals = (
            select(
                func.coalesce(func.sum(Expense.amount), Decimal("0.00")),
                func.count(Expense.id)
            )
            .where(
                Expense.user_id == user_id,
                Expense.expense_date >= window_start
            )
        )
        total_amount, total_count = (await db.execute(totals)).one()

        breakdown = (
            select(
                Category.name,
                func.coalesce(func.sum(Expense.amount), Decimal("0.00"))
            )
            .join(Category, Expense.category_id == Category.id)
            .where(
                Expense.user_id == user_id,
                Expense.expense_date >= window_start
            )
            .group_by(Category.name)
            .order_by(func.sum(Expense.amount).desc())
        )
        breakdown_by_category = {
            name: str(amount) for name, amount in (await db.execute(breakdown)).all()
        }

        return {
            "today": today.isoformat(),
            "window_start": window_start.isoformat(),
            "last_90_days_total": str(total_amount),
            "last_90_days_count": total_count,
            "last_90_days_breakdown_by_category": breakdown_by_category
        }

    async def _retrieve(
        self,
        message: str,
        user_id: int
    ) -> tuple[list[dict[str, Any]], list[str], list[float]]:
        try:
            index = pinecone_client.get_index()
            vector = await self.embedding_manager.get_embedding(message)
            result = index.query(
                vector=vector,
                top_k=RETRIEVAL_TOP_K,
                include_metadata=True,
                filter={"user_id": {"$eq": user_id}},
            )
        except RuntimeError as re:
            logger.warning("Vector retrieval unavailable (runtime): %s — answering from DB context only", re)
            return [], [], []
        except Exception:
            logger.warning(
                "Vector retrieval failed — answering from database context only",
                exc_info=True,
            )
            return [], [], []

        matches = result.get("matches", []) or []
        records: list[dict[str, Any]] = []
        sources: list[str] = []
        scores: list[float] = []

        for match in matches:
            metadata = match.get("metadata") or {}
            records.append({
                "description": metadata.get("description", ""),
                "amount": metadata.get("amount"),
                "category": metadata.get("category"),
                "expense_date": metadata.get("expense_date"),
            })
            description = metadata.get("description")
            if description:
                sources.append(description)
            try:
                scores.append(float(match.get("score") or 0.0))
            except Exception:
                scores.append(0.0)

        return records, sources, scores


query_executor = QueryExecutor(EmbeddingManager(LLMClient()))
