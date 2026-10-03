from typing import Any

from ai.foundation.llm_client import LLMClient
from ai.foundation.prompts.templates import FINANCIAL_ASSISTANT_PROMPT


class AdviceService:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def generate_response(
        self,
        message: str,
        financial_context: dict[str, Any],
        retrieved_context: list[dict[str, Any]],
    ) -> str:
        prompt = FINANCIAL_ASSISTANT_PROMPT.format(
            message=message,
            financial_context=financial_context,
            retrieved_context=retrieved_context,
        )
        return await self.llm_client.generate(prompt)


advice_service = AdviceService(LLMClient())
