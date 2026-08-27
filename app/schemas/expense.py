from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field



#Base schema with shared field validation
class ExpenseBase(BaseModel):
    amount: Decimal = Field(...,gt=0,decimal_places=2, description="Must be greater than 0")
    description: str = Field(...,min_length=1, max_length=500)
    category: str = Field(...,min_length=1,max_length=100)
    payment_method: str =Field(...,min_length=1, max_length=50)
    expense_date: date

#payload sent by user(create schema)
class ExpensesCreate(ExpenseBase):
    user_id: str = Field(..., min_length=1, max_length=100)
    

# Payload sent by user (Update schema - all fields optional for PATCH)
class ExpenseUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2, description="Must be greater than 0")
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    payment_method: Optional[str] = Field(None, min_length=1, max_length=50)
    expense_date: Optional[date] = None

    
# payload returned to client (Response schema)
class ExpenseResponse(ExpenseBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

#Compatible with SQLAlchemy models directly 
    model_config =ConfigDict(from_attributes=True)