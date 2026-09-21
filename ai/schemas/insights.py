from decimal import Decimal
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class MonthlyInsightResponse(BaseModel):
    year: int = Field(..., example=2026)
    month: int = Field(..., example=9)
    total: Decimal = Field(..., example="12000.00")
    total_count: int = Field(..., example=8)
    breakdown_by_category: Dict[str, Decimal] = Field(
        ...,
        example={
            "Food": "4500.00",
            "Bills": "3500.00",
            "Travel": "2000.00",
            "Other": "2000.00"
        }
    )
    top_category: Optional[str] = Field(None, example="Food")


class CategoryComparisonItem(BaseModel):
    month1_amount: Decimal = Field(..., example="500.00")
    month2_amount: Decimal = Field(..., example="900.00")
    change_amount: Decimal = Field(..., example="400.00")
    change_percent: Optional[Decimal] = Field(None, example="80.00")
    direction: Literal["increase", "decrease", "no_change", "new", "removed"] = Field(
        ...,
        example="increase"
    )

class ComparisonInsightResponse(BaseModel):
    year1: int = Field(..., example=2026)
    month1: int = Field(..., example=8)
    year2: int = Field(..., example=2026)
    month2: int = Field(..., example=9)
    total_month1: Decimal = Field(..., example="9375.00")
    total_month2: Decimal = Field(..., example="12000.00")
    change_percent: Decimal = Field(..., example="28.00")
    change_direction: Literal["increase", "decrease", "no_change"] = Field(
        ...,
        example="increase"
    )
    top_increased_category: Optional[str] = Field(None, example="Food")
    top_decreased_category: Optional[str] = Field(None, example="Travel")
    category_comparison: Dict[str, CategoryComparisonItem]
    ai_explanation: str = Field(
        ...,
        example="Your spending increased mainly due to higher food and travel expenses."
    )

    ai_tips: List[str] = Field(
        default_factory=list,
        example=[
            "Set a weekly food delivery budget.",
            "Review high-growth categories before month end."
        ]
    )
    ai_generated: bool = Field(..., example=True)