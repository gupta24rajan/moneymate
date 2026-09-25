from decimal import Decimal
from math import sqrt
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense


class AnomalyDetectionService:
    async def detect_anomalies(
        self,
        db: AsyncSession,
        user_id: int,
        category_id: Optional[int] = None,
        threshold: float = 2.0,
        min_samples: int = 3
    ) -> List[dict]:
        stmt = select(Expense).where(Expense.user_id == user_id)

        if category_id is not None:
            stmt = stmt.where(Expense.category_id == category_id)

        stmt = stmt.order_by(Expense.expense_date.desc())

        result = await db.execute(stmt)
        expenses = result.scalars().all()

        if len(expenses) < min_samples:
            return []

        amounts = [Decimal(expense.amount) for expense in expenses]
        count = Decimal(len(amounts))
        average = sum(amounts) / count

        variance = sum((amount - average) ** 2 for amount in amounts) / count
        std_dev = Decimal(str(sqrt(float(variance))))

        if std_dev == 0:
            return [
                {
                    "expense_id": expense.id,
                    "category_id": expense.category_id,
                    "amount": expense.amount,
                    "average_amount": average,
                    "z_score": 0.0,
                    "is_anomaly": False,
                    "reason": "All expenses are similar, so no anomaly was detected.",
                    "description": expense.description
                }
                for expense in expenses
            ]

        anomaly_results = []

        for expense in expenses:
            amount = Decimal(expense.amount)
            z_score = float((amount - average) / std_dev)
            is_anomaly = abs(z_score) >= threshold

            if is_anomaly and z_score > 0:
                reason = (
                    "This expense is unusually high compared to your normal spending."
                )
            elif is_anomaly:
                reason = (
                    "This expense is unusually low compared to your normal spending."
                )
            else:
                reason = "This expense is within your normal spending range."

            anomaly_results.append(
                {
                    "expense_id": expense.id,
                    "category_id": expense.category_id,
                    "amount": amount,
                    "average_amount": average,
                    "z_score": round(z_score, 2),
                    "is_anomaly": is_anomaly,
                    "reason": reason,
                    "description": expense.description
                }
            )

        return anomaly_results


anomaly_detection_service = AnomalyDetectionService()