from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User


from ai.schemas.insights import MonthlyInsightResponse, ComparisonInsightResponse
from ai.services.intelligence.insights_service import insights_service

logger = logging.getLogger(__name__)

CURRENT_YEAR = datetime.now().year

router = APIRouter(prefix="/ai/insights", tags=["AI Intelligent Insights"])


@router.get(
        "/monthly",
         response_model=MonthlyInsightResponse,
         summary="Get AI monthly spending insight"
)
async def get_monthly_insights(
    year: int = Query(..., example=2026, ge=2000,
        le=CURRENT_YEAR, description="Year for insight calculation"),
    month: int = Query(..., example=9, ge=1, le=12, description="Month number from 1 to 12"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        data = await insights_service.get_monthly_insight(
            db=db,
            user_id=current_user.id,
            year=year,
            month=month
        )
        return data
    except Exception as e:
        logger.exception("Failed to calculate monthly insights")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate monthly insights"
        )

@router.get(
        "/compare",
        response_model=ComparisonInsightResponse,
        summary="Compare monthly spending insights"
)
async def compare_monthly_insights(
    year1: int = Query(..., example=2026, ge=2000, le=CURRENT_YEAR),
    month1: int = Query(..., example=8, ge=1, le=12),
    year2: int = Query(..., example=2026, ge=2000, le=CURRENT_YEAR),
    month2: int = Query(..., example=9, ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        comparison = await insights_service.compare_months(
            db=db,
            user_id=current_user.id,
            year1=year1,
            month1=month1,
            year2=year2,
            month2=month2
        )
        return comparison
    except Exception as e:
        logger.exception("Failed to compare spending periods")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compare spending periods"
        )