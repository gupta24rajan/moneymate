from decimal import Decimal
from typing import Dict, List, Literal

from pydantic import BaseModel, Field, RootModel


class CategoryForecast(BaseModel):
    predicted_total: Decimal = Field(..., example="6200.00")
    trend: Literal["increasing", "decreasing", "stable"] = Field(
        ...,
        example="increasing"
    )


class NextMonthForecastResponse(RootModel[Dict[str, CategoryForecast]]):
    pass


class SavingsPotentialResponse(BaseModel):
    current_trajectory: Decimal = Field(..., example="45000.00")
    potential_with_cuts: Decimal = Field(..., example="38000.00")
    suggested_cuts: List[str] = Field(
        default_factory=list,
        example=[
            "Food: reduce by 500.00/month",
            "Transport: reduce by 300.00/month"
        ]
    )