from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ai.schemas.assistant import ChatRequest, ChatResponse
from ai.services.assistant.query_executor import query_executor
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/ai", tags=["AI Financial Assistant"])


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await query_executor.answer(
        db=db,
        user_id=current_user.id,
        message=payload.message
    )
