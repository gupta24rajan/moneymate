from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense


class BudgetService:
    async def forecast_budget(
        self,
        db: AsyncSession,
        user_id: int,
        budget: Decimal,
        category_id: Optional[int] = None
    ) -> dict:
        today = date.today()
        year = today.year
        month = today.month
        days_in_month = monthrange(year, month)[1]
        days_passed = today.day

        stmt = (
            select(func.coalesce(func.sum(Expense.amount), Decimal("0.00")))
            .where(
                Expense.user_id == user_id,
                extract("year", Expense.expense_date) == year,
                extract("month", Expense.expense_date) == month
            )
        )

        if category_id is not None:
            stmt = stmt.where(Expense.category_id == category_id)

        result = await db.execute(stmt)
        current_spent = Decimal(result.scalar_one() or Decimal("0.00"))

        daily_burn_rate = current_spent / Decimal(days_passed)
        projected_total = daily_burn_rate * Decimal(days_in_month)

        daily_burn_rate = daily_burn_rate.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )
        projected_total = projected_total.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        will_exceed = projected_total > budget
        overshoot = max(projected_total - budget, Decimal("0.00"))

        days_until_exceeded = None

        if daily_burn_rate > 0 and current_spent < budget:
            remaining_budget = budget - current_spent
            days_until_exceeded = int(remaining_budget / daily_burn_rate) + 1
        elif current_spent >= budget:
            days_until_exceeded = 0

        if will_exceed:
            reason = (
                "At your current spending rate, you may exceed this budget "
                "before month end."
            )
        else:
            reason = (
                "Your projected spending is currently within the selected budget."
            )

        return {
            "category_id": category_id,
            "budget": budget,
            "current_spent": current_spent,
            "projected_total": projected_total,
            "daily_burn_rate": daily_burn_rate,
            "will_exceed": will_exceed,
            "overshoot": overshoot,
            "days_until_exceeded": days_until_exceeded,
            "reason": reason
        }


budget_service = BudgetService()