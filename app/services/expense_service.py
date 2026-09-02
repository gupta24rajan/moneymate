from datetime import date
from decimal import Decimal
import math
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.expense import Expense
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
    PaginatedExpenseResponse,
)


class ExpenseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _validate_category_ownership(self, category_id: int, user_id: int) -> None:
        """Private helper: Verifies if the category exists and belongs to the user."""
        stmt = select(Category).where(
            Category.id == category_id,
            Category.user_id == user_id
        )
        result = await self.db.execute(stmt)
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category_id {category_id}. Category does not exist or belong to you."
            )

    async def create_expense(self, expense_in: ExpenseCreate, user_id: int) -> Expense:
        """Create a new expense record linked to current user."""
        # 1. Check if category belongs to current user
        await self._validate_category_ownership(expense_in.category_id, user_id)

        # 2. Inject user_id
        expense_data = expense_in.model_dump()
        expense_data["user_id"] = user_id

        expense = Expense(**expense_data)
        self.db.add(expense)
        try:
            await self.db.commit()
            await self.db.refresh(expense)
            # Re-fetch with relationships loaded for serialization
            return await self.get_expense_by_id(expense.id, user_id)
        except SQLAlchemyError as err:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create expense."
            ) from err

    async def get_expense_by_id(self, expense_id: int, user_id: int) -> Expense:
        """Fetch a single expense scoped to a specific user."""
        stmt = (
            select(Expense)
            .options(
                selectinload(Expense.category),
                selectinload(Expense.user)
            )
            .where(
                Expense.id == expense_id,
                Expense.user_id == user_id
            )
        )

        result = await self.db.execute(stmt)
        expense = result.scalar_one_or_none()

        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Expense with ID {expense_id} not found."
            )
        return expense

    async def get_expenses(
        self,
        user_id: int,
        category_name: Optional[str] = None,
        category_id: Optional[int] = None,
        payment_method: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        search: Optional[str] = None,
        sort_by: str = "expense_date",
        order: str = "desc",
        page: int = 1,
        limit: int = 20
    ) -> PaginatedExpenseResponse[ExpenseResponse]:  # <--- Changed Expense to ExpenseResponse
        """Fetch expenses with dynamic filters, partial search, sorting, and pagination."""
        
        # Base Query scoped strictly to current user
        query = (
            select(Expense)
            .options(
                selectinload(Expense.category),
                selectinload(Expense.user)
            )
            .where(Expense.user_id == user_id)
        )

        # 1. Filter by Category ID or Category Name
        if category_id:
            query = query.where(Expense.category_id == category_id)
        elif category_name:
            query = query.join(Expense.category).where(
                func.lower(Category.name) == category_name.lower()
            )

        # 2. Filter by Payment Method
        if payment_method:
            query = query.where(func.lower(Expense.payment_method) == payment_method.lower())

        # 3. Filter by Date Range
        if start_date:
            query = query.where(Expense.expense_date >= start_date)
        if end_date:
            query = query.where(Expense.expense_date <= end_date)

        # 4. Filter by Amount (Min / Max)
        if min_amount is not None:
            query = query.where(Expense.amount >= min_amount)
        if max_amount is not None:
            query = query.where(Expense.amount <= max_amount)

        # 5. Search in description
        if search:
            query = query.where(Expense.description.ilike(f"%{search}%"))

        # Calculate Total Count for Pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_count = (await self.db.execute(count_query)).scalar_one()

        # 6. Sorting
        sort_column = getattr(Expense, sort_by, Expense.expense_date)
        if order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # 7. Pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        expenses = result.scalars().all()

        total_pages = math.ceil(total_count / limit) if limit > 0 else 1

        return PaginatedExpenseResponse[ExpenseResponse](
            items=expenses,
            total=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages
        )

    async def update_expense(
        self,
        expense_id: int,
        user_id: int,
        expense_in: ExpenseUpdate
    ) -> Expense:
        """Partially update an existing expense."""
        expense = await self.get_expense_by_id(expense_id, user_id)

        if expense_in.category_id is not None:
            await self._validate_category_ownership(expense_in.category_id, user_id)

        update_data = expense_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(expense, field, value)

        try:
            await self.db.commit()
            return await self.get_expense_by_id(expense_id, user_id)
        except SQLAlchemyError as err:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update expense."
            ) from err

    async def delete_expense(self, expense_id: int, user_id: int) -> None:
        """Delete an expense record."""
        expense = await self.get_expense_by_id(expense_id, user_id)
        try:
            await self.db.delete(expense)
            await self.db.commit()
        except SQLAlchemyError as err:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete expense."
            ) from err