from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class AnomalyResponse(BaseModel):
    expense_id: int = Field(..., example=123)
    category_id: int = Field(..., example=1)
    amount: Decimal = Field(..., example="7850.00")
    average_amount: Decimal = Field(..., example="1200.00")
    z_score: float = Field(..., example=3.2)
    is_anomaly: bool = Field(..., example=True)
    reason: str = Field(
        ...,
        example="This expense is unusually high compared to your normal spending."
    )
    description: Optional[str] = Field(None, example="Restaurant bill")