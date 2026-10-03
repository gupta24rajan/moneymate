import json
import re
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.foundation.llm_client import LLMClient
from app.models.category import Category
from app.models.expense import Expense


class CategorizationService:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    @staticmethod
    def extract_merchant(description: str) -> str:
        cleaned = re.sub(
            r"₹|\d+|rs|paytm|upi|pos",
            "",
            description,
            flags=re.IGNORECASE,
        )
        words = cleaned.strip().split()
        return words[0].capitalize() if words else "Unknown"

    async def suggest_category(
        self,
        description: str,
        amount: Decimal
    ) -> dict[str, Any]:
        merchant = self.extract_merchant(description)
        prompt = f'''You are a financial classifier. Return only raw JSON.

Expense description: "{description}"
Amount: {amount}
Merchant: "{merchant}"

Return exactly:
{{
  "suggested_category": "Food",
  "subcategory": "Food Delivery",
  "merchant": "{merchant}",
  "confidence": 0.95
}}'''

        try:
            raw_response = await self.llm_client.generate(prompt)
            cleaned_json = re.sub(
                r"^```(?:json)?|```$",
                "",
                raw_response.strip(),
                flags=re.MULTILINE,
            ).strip()
            return json.loads(cleaned_json)
        except Exception:
            return {
                "suggested_category": "Other",
                "subcategory": "General",
                "merchant": merchant,
                "confidence": 0.50,
            }

    async def accept_suggestion(
        self,
        db: AsyncSession,
        expense_id: int,
        category_id: int,
        user_id: int
    ) -> bool:
        category = await db.execute(
            select(Category).where(
                Category.id == category_id,
                Category.user_id == user_id
            )
        )
        if not category.scalar_one_or_none():
            return False

        result = await db.execute(
            select(Expense).where(
                Expense.id == expense_id,
                Expense.user_id == user_id
            )
        )
        expense = result.scalar_one_or_none()
        if expense is None:
            return False

        expense.category_id = category_id
        await db.commit()
        return True


categorization_service = CategorizationService(LLMClient())
