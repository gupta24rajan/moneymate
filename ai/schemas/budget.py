from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class BudgetForecastResponse(BaseModel):
    category_id: Optional[int] = Field(None, example=1)
    budget: Decimal = Field(..., example="8000.00")
    current_spent: Decimal = Field(..., example="6000.00")
    projected_total: Decimal = Field(..., example="9200.00")
    daily_burn_rate: Decimal = Field(..., example="300.00")
    will_exceed: bool = Field(..., example=True)
    overshoot: Decimal = Field(..., example="1200.00")
    days_until_exceeded: Optional[int] = Field(None, example=8)
    reason: str = Field(
        ...,
        example="At your current spending rate, you may exceed this budget before month end."
    )