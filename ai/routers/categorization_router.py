from fastapi import APIRouter, HTTPException, status
from ai.schemas.categorization import (
    CategorizationRequest,
    CategorizationResponse,
    CategoryAcceptRequest
)
from ai.services.intelligence.categorization_service import categorization_service

router = APIRouter(prefix="/ai/categorization", tags=["AI Expense Categorization"])

@router.post("/suggest", response_model=CategorizationResponse)
async def suggest_expense_category(payload: CategorizationRequest):
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
async def accept_category_suggestion(expense_id: int, payload: CategoryAcceptRequest):
    success = await categorization_service.accept_suggestion(
        expense_id=expense_id,
        category_id=payload.category_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense ID not found"
        )
    return {
        "status": "success",
        "message": f"Category ID {payload.category_id} accepted for Expense {expense_id}"
    }