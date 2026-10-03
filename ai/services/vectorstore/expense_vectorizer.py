import logging
from decimal import Decimal
from typing import Any

from ai.foundation.embeddings import EmbeddingManager
from ai.foundation.llm_client import LLMClient
from ai.vectorstore.pinecone_client import pinecone_client

logger = logging.getLogger(__name__)


def _decimal_to_str(v: Decimal | float | str | None) -> str | None:
    if v is None:
        return None
    if isinstance(v, Decimal):
        return format(v, "f")
    return str(v)


class ExpenseVectorizer:
    def __init__(self, embedding_manager: EmbeddingManager | None = None):
        self.embedding_manager = embedding_manager or EmbeddingManager(LLMClient())

    async def upsert_expense(self, expense_id: int, user_id: int, **fields: Any) -> None:
        try:
            desc = fields.get("description") or ""
            text = f"Expense: {desc}. Amount: {_decimal_to_str(fields.get('amount'))}. Category: {fields.get('category_name') or fields.get('category') or ''}. Date: {fields.get('expense_date') or ''}. Payment: {fields.get('payment_method') or ''}"
            vec = await self.embedding_manager.get_embedding(text)
            pinecone_client.upsert_vectors(
                vectors=[
                    (
                        f"expense:{expense_id}",
                        vec,
                        {
                            "user_id": user_id,
                            "expense_id": expense_id,
                            "description": desc[:500],
                            "amount": _decimal_to_str(fields.get("amount")),
                            "category": fields.get("category_name") or fields.get("category"),
                            "expense_date": str(fields.get("expense_date")) if fields.get("expense_date") else None,
                            "payment_method": fields.get("payment_method"),
                        },
                    )
                ]
            )
        except Exception:
            logger.warning("Failed to upsert expense vector %s", expense_id, exc_info=True)

    async def delete_expense(self, expense_id: int) -> None:
        try:
            pinecone_client.delete_vectors(ids=[f"expense:{expense_id}"])
        except Exception:
            logger.warning("Failed to delete expense vector %s", expense_id, exc_info=True)


expense_vectorizer = ExpenseVectorizer()
