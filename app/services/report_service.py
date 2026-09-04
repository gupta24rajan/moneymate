import calendar
from decimal import Decimal
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.expense import Expense
from app.models.category import Category
from app.schemas.report import (
    TotalExpenseReport,
    CategoryReportItem,
    MonthlyReportItem,
    PaymentMethodReportItem,
)


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_total_expenses(self, user_id: int) -> TotalExpenseReport:
        # SQL: SELECT COALESCE(SUM(amount), 0), COUNT(id) FROM expenses WHERE user_id = :user_id
        stmt = select(
            func.coalesce(func.sum(Expense.amount), Decimal("0.00")).label("total_amount"),
            func.count(Expense.id).label("total_count"),
        ).where(Expense.user_id == user_id)

        result = await self.db.execute(stmt)
        row = result.one()
        return TotalExpenseReport(
            total_amount=row.total_amount, 
            total_count=row.total_count
        )

    async def get_category_breakdown(self, user_id: int) -> List[CategoryReportItem]:
        # SQL: JOIN categories, GROUP BY category_id, name ORDER BY SUM(amount) DESC
        stmt = (
            select(
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                func.coalesce(func.sum(Expense.amount), Decimal("0.00")).label("total_amount"),
                func.count(Expense.id).label("expense_count"),
            )
            .join(Category, Expense.category_id == Category.id)
            .where(Expense.user_id == user_id)
            .group_by(Category.id, Category.name)
            .order_by(func.sum(Expense.amount).desc())
        )

        result = await self.db.execute(stmt)
        return [
            CategoryReportItem(
                category_id=row.category_id,
                category_name=row.category_name,
                total_amount=row.total_amount,
                expense_count=row.expense_count,
            )
            for row in result.all()
        ]

    async def get_monthly_breakdown(self, user_id: int) -> List[MonthlyReportItem]:
        # SQL: GROUP BY EXTRACT(YEAR), EXTRACT(MONTH)
        year_col = func.extract("year", Expense.expense_date).label("year")
        month_col = func.extract("month", Expense.expense_date).label("month")

        stmt = (
            select(
                year_col,
                month_col,
                func.coalesce(func.sum(Expense.amount), Decimal("0.00")).label("total_amount"),
                func.count(Expense.id).label("expense_count"),
            )
            .where(Expense.user_id == user_id)
            .group_by(year_col, month_col)
            .order_by(year_col.desc(), month_col.desc())
        )

        result = await self.db.execute(stmt)
        items = []
        for row in result.all():
            year_val = int(row.year)
            month_val = int(row.month)
            items.append(
                MonthlyReportItem(
                    year=year_val,
                    month=month_val,
                    month_name=calendar.month_name[month_val],
                    total_amount=row.total_amount,
                    expense_count=row.expense_count,
                )
            )
        return items

    async def get_payment_method_breakdown(self, user_id: int) -> List[PaymentMethodReportItem]:
        # SQL: GROUP BY payment_method ORDER BY SUM(amount) DESC
        stmt = (
            select(
                Expense.payment_method,
                func.coalesce(func.sum(Expense.amount), Decimal("0.00")).label("total_amount"),
                func.count(Expense.id).label("expense_count"),
            )
            .where(Expense.user_id == user_id)
            .group_by(Expense.payment_method)
            .order_by(func.sum(Expense.amount).desc())
        )

        result = await self.db.execute(stmt)
        return [
            PaymentMethodReportItem(
                payment_method=row.payment_method,
                total_amount=row.total_amount,
                expense_count=row.expense_count,
            )
            for row in result.all()
        ]