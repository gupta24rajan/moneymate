from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.report_service import ReportService
from app.schemas.report import (
    TotalExpenseReport,
    CategoryReportItem,
    MonthlyReportItem,
    PaymentMethodReportItem,
)

router = APIRouter(prefix="/reports", tags=["Expense Reports"])


@router.get("/total", response_model=TotalExpenseReport)
async def get_total_expenses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReportService(db)
    return await service.get_total_expenses(current_user.id)


@router.get("/category", response_model=List[CategoryReportItem])
async def get_category_breakdown(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReportService(db)
    return await service.get_category_breakdown(current_user.id)


@router.get("/monthly", response_model=List[MonthlyReportItem])
async def get_monthly_breakdown(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReportService(db)
    return await service.get_monthly_breakdown(current_user.id)


@router.get("/payment-method", response_model=List[PaymentMethodReportItem])
async def get_payment_method_breakdown(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReportService(db)
    return await service.get_payment_method_breakdown(current_user.id)