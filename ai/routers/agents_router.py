from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ai.schemas.agents import AgentRunRequest, AgentRunResponse
from ai.services.agents.base_agent import financial_agent
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/ai/agent", tags=["AI Financial Agent"])


@router.post("/run", response_model=AgentRunResponse)
async def run_financial_agent(
    payload: AgentRunRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await financial_agent.run(
        db=db,
        user_id=current_user.id,
        task=payload.task
    )
