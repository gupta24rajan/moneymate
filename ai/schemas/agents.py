from typing import Any, Dict, List, Literal

from pydantic import BaseModel, ConfigDict, Field


class AgentRunRequest(BaseModel):
    task: str = Field(
        ..., min_length=5, max_length=1000, example="Why did I spend more on food this month?"
    )


class AgentAction(BaseModel):
    tool: str

    model_config = ConfigDict(extra="allow")


class AgentRunResponse(BaseModel):
    status: Literal["success", "error"]
    response: str
    actions: List[AgentAction] = Field(default_factory=list)
