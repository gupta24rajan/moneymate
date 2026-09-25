from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ai.schemas.forecast import (
    NextMonthForecastResponse,
    SavingsPotentialResponse,
)
from ai.services.intelligence.forecasting_service import forecasting_service
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/ai/forecast",
    tags=["AI Expense Forecasting"]
)


@router.get(
    "/next-month",
    response_model=NextMonthForecastResponse
)
async def forecast_next_month(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await forecasting_service.forecast_next_month(
        db=db,
        user_id=current_user.id
    )


@router.get(
    "/savings-potential",
    response_model=SavingsPotentialResponse
)
async def get_savings_potential(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await forecasting_service.get_savings_potential(
        db=db,
        user_id=current_user.id
    )