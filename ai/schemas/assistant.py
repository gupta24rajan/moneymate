from typing import List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        ..., min_length=3, max_length=1000, example="How much did I spend on food last month?"
    )


class ChatResponse(BaseModel):
    response: str
    sources: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0, le=1, example=0.92)
