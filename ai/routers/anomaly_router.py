from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from ai.schemas.anomaly import AnomalyResponse
from ai.services.intelligence.anomaly_detection import anomaly_detection_service


router = APIRouter(prefix="/ai", tags=["AI Anomaly Detection"])


@router.get("/anomalies", response_model=List[AnomalyResponse])
async def get_anomalies(
    category_id: Optional[int] = Query(None, example=1),
    threshold: float = Query(2.0, ge=1.0, le=5.0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await anomaly_detection_service.detect_anomalies(
        db=db,
        user_id=current_user.id,
        category_id=category_id,
        threshold=threshold
    )