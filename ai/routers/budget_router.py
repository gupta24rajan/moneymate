from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from ai.schemas.budget import BudgetForecastResponse
from ai.services.intelligence.budget_service import budget_service


router = APIRouter(prefix="/ai/budget", tags=["AI Budget Forecasting"])


@router.get("/forecast", response_model=BudgetForecastResponse)
async def forecast_budget(
    budget: Decimal = Query(..., gt=0, example="8000.00"),
    category_id: Optional[int] = Query(None, example=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await budget_service.forecast_budget(
        db=db,
        user_id=current_user.id,
        budget=budget,
        category_id=category_id
    )