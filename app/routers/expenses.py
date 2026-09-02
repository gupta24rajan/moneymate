from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

# Import setup modules
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.expense import ExpenseResponse, ExpenseCreate, ExpenseUpdate, PaginatedExpenseResponse
from app.services.expense_service import ExpenseService

expense_router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)


# Service dependency helper
def get_expense_service(db: AsyncSession = Depends(get_db)) -> ExpenseService:
    return ExpenseService(db)






@expense_router.post(
    "/",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new expense"
)
async def create_expense(
    payload: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service)
):
    return await service.create_expense(payload, user_id=current_user.id)


@expense_router.get(
    "/",
    response_model=PaginatedExpenseResponse[ExpenseResponse],
    status_code=status.HTTP_200_OK,
    summary="Get expenses with filtering, searching, sorting & pagination"
)
async def get_expenses(
    category_name: Optional[str] = Query(None, alias="category", description="Filter by category name"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    start_date: Optional[date] = Query(None, description="Format: YYYY-MM-DD"),
    end_date: Optional[date] = Query(None, description="Format: YYYY-MM-DD"),
    min_amount: Optional[Decimal] = Query(None, ge=0, description="Minimum amount filter"),
    max_amount: Optional[Decimal] = Query(None, ge=0, description="Maximum amount filter"),
    search: Optional[str] = Query(None, description="Search term in description"),
    sort_by: str = Query("expense_date", pattern="^(expense_date|amount|created_at)$", description="Field to sort by"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service)
):
    return await service.get_expenses(
        user_id=current_user.id,
        category_name=category_name,
        category_id=category_id,
        payment_method=payment_method,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        search=search,
        sort_by=sort_by,
        order=order,
        page=page,
        limit=limit
    )

@expense_router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single expense by ID"
)
async def get_expense_by_id(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service)
):
    return await service.get_expense_by_id(
        expense_id=expense_id, user_id=current_user.id
    )


@expense_router.put(
    "/{expense_id}",
    response_model=ExpenseResponse,
    status_code=status.HTTP_200_OK,
    summary="Completely replace an existing expense"
)
async def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service)
):
    return await service.update_expense(
        expense_id=expense_id,
        user_id=current_user.id,
        expense_in=payload
    )


@expense_router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an expense"
)

async def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service)
):
    await service.delete_expense(expense_id=expense_id, user_id=current_user.id)
    return None