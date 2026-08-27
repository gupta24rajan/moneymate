from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

# Import setup modules
from app.database import get_db
from app.schemas.expense import ExpenseResponse, ExpensesCreate, ExpenseUpdate
from app.services.expense_service import ExpenseService

expense_router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)


# Service dependency helper
def get_expense_service(db: AsyncSession = Depends(get_db)) -> ExpenseService:
    return ExpenseService(db)


# Mock user authentication dependency (Replace with actual Auth/JWT setup later)
async def get_current_user_id() -> str:
    return "user_123"


@expense_router.post(
    "/",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new expense"
)
async def create_expense(
    payload: ExpensesCreate,
    current_user_id: str = Depends(get_current_user_id),
    service: ExpenseService = Depends(get_expense_service)
):
    payload.user_id = current_user_id
    return await service.create_expense(payload)


@expense_router.get(
    "/",
    response_model=List[ExpenseResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all expenses for current user"
)
async def get_all_expenses(
    current_user_id: str = Depends(get_current_user_id),
    service: ExpenseService = Depends(get_expense_service)
):
    return await service.get_all_expenses(user_id=current_user_id)


@expense_router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single expense by ID"
)
async def get_expense_by_id(
    expense_id: int,
    current_user_id: str = Depends(get_current_user_id),
    service: ExpenseService = Depends(get_expense_service)
):
    return await service.get_expense_by_id(expense_id=expense_id, user_id=current_user_id)


@expense_router.put(
    "/{expense_id}",
    response_model=ExpenseResponse,
    status_code=status.HTTP_200_OK,
    summary="Completely replace an existing expense"
)
async def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    current_user_id: str = Depends(get_current_user_id),
    service: ExpenseService = Depends(get_expense_service)
):
    return await service.update_expense(
        expense_id=expense_id,
        user_id=current_user_id,
        expense_in=payload
    )


@expense_router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an expense"
)
async def delete_expense(
    expense_id: int,
    current_user_id: str = Depends(get_current_user_id),
    service: ExpenseService = Depends(get_expense_service)
):
    await service.delete_expense(expense_id=expense_id, user_id=current_user_id)
    return None