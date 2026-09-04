from decimal import Decimal
from typing import List
from pydantic import BaseModel


class TotalExpenseReport(BaseModel):
    total_amount: Decimal
    total_count: int


class CategoryReportItem(BaseModel):
    category_id: int
    category_name: str
    total_amount: Decimal
    expense_count: int


class MonthlyReportItem(BaseModel):
    year: int
    month: int
    month_name: str
    total_amount: Decimal
    expense_count: int


class PaymentMethodReportItem(BaseModel):
    payment_method: str
    total_amount: Decimal
    expense_count: int