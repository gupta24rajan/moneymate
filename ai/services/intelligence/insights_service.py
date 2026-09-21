from decimal import Decimal
import logging
from typing import Dict, Any

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.foundation.llm_client import LLMClient
from ai.foundation.prompts.templates import MONTHLY_COMPARISON_PROMPT
from app.models.category import Category
from app.models.expense import Expense


logger = logging.getLogger(__name__)


class InsightsService:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def get_monthly_insight(
        self,
        db: AsyncSession,
        user_id: int,
        year: int,
        month: int
    ) -> Dict[str, Any]:

        total_stmt = (
            select(
                func.coalesce(func.sum(Expense.amount), Decimal("0.00")),
                func.count(Expense.id)
            )
            .where(
                Expense.user_id == user_id,
                extract("year", Expense.expense_date) == year,
                extract("month", Expense.expense_date) == month
            )
        )

        total_result = await db.execute(total_stmt)
        total_amount, total_count = total_result.one()

        category_stmt = (
            select(
                Category.name,
                func.coalesce(func.sum(Expense.amount), Decimal("0.00"))
            )
            .join(Category, Expense.category_id == Category.id)
            .where(
                Expense.user_id == user_id,
                extract("year", Expense.expense_date) == year,
                extract("month", Expense.expense_date) == month
            )
            .group_by(Category.name)
            .order_by(func.sum(Expense.amount).desc())
        )

        category_result = await db.execute(category_stmt)

        breakdown_by_category = {
            category_name: amount
            for category_name, amount in category_result.all()
        }

        top_category = None

        if breakdown_by_category:
            top_category = max(
                breakdown_by_category,
                key=breakdown_by_category.get
            )

        return {
            "year": year,
            "month": month,
            "total": total_amount,
            "total_count": total_count,
            "breakdown_by_category": breakdown_by_category,
            "top_category": top_category
        }

    async def compare_months(
        self,
        db: AsyncSession,
        user_id: int,
        year1: int,
        month1: int,
        year2: int,
        month2: int
    ) -> Dict[str, Any]:

        m1_data = await self.get_monthly_insight(
            db=db,
            user_id=user_id,
            year=year1,
            month=month1
        )

        m2_data = await self.get_monthly_insight(
            db=db,
            user_id=user_id,
            year=year2,
            month=month2
        )

        m1_total = m1_data["total"]
        m2_total = m2_data["total"]

        if m1_total == 0:
            change_pct = Decimal("0.00")
        else:
            change_pct = round(
                ((m2_total - m1_total) / m1_total) * Decimal("100"),
                2
            )

        if change_pct > 0:
            change_direction = "increase"
        elif change_pct < 0:
            change_direction = "decrease"
        else:
            change_direction = "no_change"

        category_comparison = {}
        all_categories = (
            set(m1_data["breakdown_by_category"])
            | set(m2_data["breakdown_by_category"])
        )

        for category in all_categories:
            month1_amount = m1_data["breakdown_by_category"].get(
                category, Decimal("0.00")
            )
            month2_amount = m2_data["breakdown_by_category"].get(
                category, Decimal("0.00")
            )
            change_amount = month2_amount - month1_amount

            if month1_amount == 0 and month2_amount > 0:
                category_change_percent = None
                direction = "new"
            elif month1_amount > 0 and month2_amount == 0:
                category_change_percent = Decimal("-100.00")
                direction = "removed"
            elif month1_amount == 0 and month2_amount == 0:
                category_change_percent = Decimal("0.00")
                direction = "no_change"
            else:
                category_change_percent = round(
                    (change_amount / month1_amount) * Decimal("100"),
                    2
                )

                if change_amount > 0:
                    direction = "increase"
                elif change_amount < 0:
                    direction = "decrease"
                else:
                    direction = "no_change"

            category_comparison[category] = {
                "month1_amount": month1_amount,
                "month2_amount": month2_amount,
                "change_amount": change_amount,
                "change_percent": category_change_percent,
                "direction": direction
            }

        increased_categories = {
            category: data["change_amount"]
            for category, data in category_comparison.items()
            if data["change_amount"] > 0
        }
        decreased_categories = {
            category: abs(data["change_amount"])
            for category, data in category_comparison.items()
            if data["change_amount"] < 0
        }
        top_increased_category = (
            max(increased_categories, key=increased_categories.get)
            if increased_categories
            else None
        )
        top_decreased_category = (
            max(decreased_categories, key=decreased_categories.get)
            if decreased_categories
            else None
        )

        ai_tips = [
            "Review the category with the biggest increase and set a weekly limit.",
            "Track recurring expenses to avoid unexpected month-end increases."
        ]

        prompt = MONTHLY_COMPARISON_PROMPT.format(
            year1=year1,
            month1=month1,
            total_month1=m1_total,
            year2=year2,
            month2=month2,
            total_month2=m2_total,
            change_percent=change_pct,
            change_direction=change_direction,
            breakdown_month1=m1_data["breakdown_by_category"],
            breakdown_month2=m2_data["breakdown_by_category"],
            category_comparison=category_comparison,
            top_increased_category=top_increased_category,
            top_decreased_category=top_decreased_category
        )

        try:
            explanation = await self.llm_client.generate(prompt)
            explanation = explanation.strip()
            ai_generated = True

        except Exception:
            logger.exception("LLM failed while generating monthly comparison insight")
            if top_increased_category:
                explanation = (
                    f"Your expenses changed by {change_pct}% compared to the "
                    f"selected month. The biggest increase came from "
                    f"{top_increased_category}."
                )
            else:
                explanation = (
                    f"Your expenses changed by {change_pct}% compared to the "
                    f"selected month."
                )
            ai_generated = False

        return {
            "year1": year1,
            "month1": month1,
            "year2": year2,
            "month2": month2,
            "total_month1": m1_total,
            "total_month2": m2_total,
            "change_percent": change_pct,
            "change_direction": change_direction,
            "top_increased_category": top_increased_category,
            "top_decreased_category": top_decreased_category,
            "category_comparison": category_comparison,
            "ai_explanation": explanation,
            "ai_tips": ai_tips,
            "ai_generated": ai_generated
        }


insights_service = InsightsService(LLMClient())
