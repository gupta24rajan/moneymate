from pydantic import BaseModel, Field
from typing import Optional

class CategorizationRequest(BaseModel):
    description: str = Field(..., example="Swiggy ₹450")
    amount: float = Field(..., example=450.0)

class CategorizationResponse(BaseModel):
    suggested_category: str = Field(..., example="Food")
    subcategory: Optional[str] = Field(None, example="Food Delivery")
    merchant: Optional[str] = Field(None, example="Swiggy")
    confidence: float = Field(..., example=0.98)

class CategoryAcceptRequest(BaseModel):
    category_id: int = Field(..., example=3)