from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.expense import Expense


class ForecastingService:
    @staticmethod
    def _previous_completed_months(
        reference_date: date,
        count: int = 3
    ) -> List[Tuple[int, int]]:
        months = []
        year = reference_date.year
        month = reference_date.month

        for _ in range(count):
            month -= 1

            if month == 0:
                month = 12
                year -= 1

            months.append((year, month))

        return list(reversed(months))

    @staticmethod
    def _round_amount(amount: Decimal) -> Decimal:
        return amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

    async def _get_category_totals_for_month(
        self,
        db: AsyncSession,
        user_id: int,
        year: int,
        month: int
    ) -> Dict[str, Decimal]:
        start_date = date(year, month, 1)
        end_date = date(year, month, monthrange(year, month)[1])

        stmt = (
            select(
                Category.name,
                func.coalesce(
                    func.sum(Expense.amount),
                    Decimal("0.00")
                )
            )
            .select_from(Expense)
            .join(Category, Expense.category_id == Category.id)
            .where(
                Expense.user_id == user_id,
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date
            )
            .group_by(Category.name)
        )

        result = await db.execute(stmt)

        return {
            category_name: Decimal(amount)
            for category_name, amount in result.all()
        }

    async def forecast_next_month(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Dict[str, dict]:
        completed_months = self._previous_completed_months(date.today())

        monthly_data = []

        for year, month in completed_months:
            category_totals = await self._get_category_totals_for_month(
                db=db,
                user_id=user_id,
                year=year,
                month=month
            )
            monthly_data.append(category_totals)

        all_categories = set()

        for category_data in monthly_data:
            all_categories.update(category_data.keys())

        forecasts = {}

        for category in sorted(all_categories):
            amounts = [
                month_data.get(category, Decimal("0.00"))
                for month_data in monthly_data
            ]

            predicted_total = self._round_amount(
                sum(amounts, Decimal("0.00")) / Decimal("3")
            )

            oldest_amount = amounts[0]
            latest_amount = amounts[-1]

            if oldest_amount == 0 and latest_amount > 0:
                trend = "increasing"
            elif oldest_amount > 0 and latest_amount == 0:
                trend = "decreasing"
            elif latest_amount > oldest_amount * Decimal("1.10"):
                trend = "increasing"
            elif latest_amount < oldest_amount * Decimal("0.90"):
                trend = "decreasing"
            else:
                trend = "stable"

            forecasts[category] = {
                "predicted_total": predicted_total,
                "trend": trend
            }

        return forecasts

    async def get_savings_potential(
        self,
        db: AsyncSession,
        user_id: int
    ) -> dict:
        today = date.today()
        days_in_month = monthrange(today.year, today.month)[1]
        days_passed = max(today.day, 1)

        current_month_totals = await self._get_category_totals_for_month(
            db=db,
            user_id=user_id,
            year=today.year,
            month=today.month
        )

        completed_months = self._previous_completed_months(today)
        historical_months = []

        for year, month in completed_months:
            category_totals = await self._get_category_totals_for_month(
                db=db,
                user_id=user_id,
                year=year,
                month=month
            )
            historical_months.append(category_totals)

        current_trajectory = Decimal("0.00")
        total_recommended_cuts = Decimal("0.00")
        suggested_cuts = []

        for category, current_spent in current_month_totals.items():
            projected_category_total = self._round_amount(
                (current_spent / Decimal(days_passed))
                * Decimal(days_in_month)
            )

            current_trajectory += projected_category_total

            historical_average = self._round_amount(
                sum(
                    (
                        month_data.get(category, Decimal("0.00"))
                        for month_data in historical_months
                    ),
                    Decimal("0.00")
                )
                / Decimal("3")
            )

            if historical_average <= 0:
                continue

            excess_amount = projected_category_total - historical_average
            minimum_excess = historical_average * Decimal("0.10")

            if excess_amount > minimum_excess:
                recommended_cut = self._round_amount(excess_amount)
                total_recommended_cuts += recommended_cut

                suggested_cuts.append(
                    f"{category}: reduce by {recommended_cut}/month"
                )

        current_trajectory = self._round_amount(current_trajectory)
        potential_with_cuts = self._round_amount(
            max(
                current_trajectory - total_recommended_cuts,
                Decimal("0.00")
            )
        )

        return {
            "current_trajectory": current_trajectory,
            "potential_with_cuts": potential_with_cuts,
            "suggested_cuts": suggested_cuts
        }


forecasting_service = ForecastingService()