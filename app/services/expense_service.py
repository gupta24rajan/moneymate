from fastapi import HTTPException, status
from sqlalchemy import Sequence, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense
from app.schemas.expense import ExpensesCreate,ExpenseUpdate
class ExpenseService:
    def __init__(self, db: AsyncSession):
        self.db=db


    async def create_expense(self,expense_in:ExpensesCreate) ->Expense:
        """Create a new expense record safely with explicit rollback."""
        expense = Expense(**expense_in.model_dump())
        self.db.add(expense)
        try:
            await self.db.commit()
            await self.db.refresh(expense)
            return expense
        except SQLAlchemyError as err:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create expense."
            ) from err

    async def get_expense_by_id(self,expense_id: int, user_id:str)->Expense:
        """Fetch a single expense scoped to a specific user."""
        stmt = select(Expense).where(
            Expense.id == expense_id,
            Expense.user_id == user_id
        )

        result =await self.db.execute(stmt)
        expense = result.scalar_one_or_none()


        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Expense with ID {expense_id} not found."
            )
        return expense

    async def get_all_expenses(self, user_id: str) -> Sequence[Expense]:
        """Fetch all expenses for a specific user ordered by date."""
        stmt = select(Expense).where(Expense.user_id == user_id).order_by(Expense.expense_date.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_expense(self,
        expense_id: int,
        user_id: str,
        expense_in: ExpenseUpdate
    ) -> Expense:
        """Partially update an existing expense."""
        expense = await self.get_expense_by_id(expense_id, user_id)

        update_data =expense_in.model_dump()
        for field,value in update_data.items():
            setattr(expense,field,value)

        try:
            await self.db.commit()
            await self.db.refresh(expense)
            return expense
        except SQLAlchemyError as err:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update expense."
            ) from err

    async def delete_expense(self, expense_id: int, user_id: str) -> None:
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