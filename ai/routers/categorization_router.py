from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ai.schemas.categorization import (
    CategorizationRequest,
    CategorizationResponse,
    CategoryAcceptRequest
)
from ai.services.categorization import categorization_service
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/ai/categorization", tags=["AI Expense Categorization"])

@router.post("/suggest", response_model=CategorizationResponse)
async def suggest_expense_category(
    payload: CategorizationRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        suggestion = await categorization_service.suggest_category(
            description=payload.description,
            amount=payload.amount
        )
        return suggestion
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Categorization failed: {str(e)}"
        )

@router.post("/accept/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def accept_category_suggestion(
    expense_id: int,
    payload: CategoryAcceptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    success = await categorization_service.accept_suggestion(
        db=db,
        expense_id=expense_id,
        category_id=payload.category_id,
        user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    return {
        "status": "success",
        "message": f"Category ID {payload.category_id} accepted for Expense {expense_id}"
    }