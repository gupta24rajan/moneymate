from datetime import date, datetime
from decimal import Decimal
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

# Generic Type for Pagination Wrapper
T = TypeVar("T")


class CategoryMinimalResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserMinimalResponse(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)


# Base schema with shared field validation
class ExpenseBase(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Must be greater than 0")
    description: str = Field(..., min_length=3, max_length=500)
    payment_method: str = Field(..., min_length=2, max_length=50)
    expense_date: date


# Request Schema (Create - Requires Foreign Key IDs)
class ExpenseCreate(ExpenseBase):
    category_id: int = Field(..., description="Valid Category ID from categories table")


# Request Schema (PATCH / Partial Update)
class ExpenseUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2, description="Must be greater than 0")
    description: Optional[str] = Field(None, min_length=3, max_length=500)
    payment_method: Optional[str] = Field(None, min_length=2, max_length=50)
    expense_date: Optional[date] = Field(None)
    category_id: Optional[int] = Field(None)


# Response Schema (Full payload with relationship schemas)
class ExpenseResponse(ExpenseBase):
    id: int
    user_id: int
    category_id: int
    category: Optional[CategoryMinimalResponse] = None  # Loaded via selectinload
    user: Optional[UserMinimalResponse] = None          # Loaded via selectinload
    created_at: datetime
    updated_at: datetime

    # Compatible with SQLAlchemy models directly
    model_config = ConfigDict(from_attributes=True)


class PaginatedExpenseResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
    total_pages: int