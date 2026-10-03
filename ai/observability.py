import logging
from decimal import Decimal

import httpx

from ai.config import config

logger = logging.getLogger("ai.observability")


def log_llm_call(model: str, latency_ms: int, input_tokens: int, output_tokens: int, success: bool) -> None:
    cost = (
        (Decimal(input_tokens) / Decimal("1000000")) * config.LLM_INPUT_COST_PER_MILLION
        + (Decimal(output_tokens) / Decimal("1000000")) * config.LLM_OUTPUT_COST_PER_MILLION
    )
    logger.info(
        "llm_call model=%s success=%s latency_ms=%s input_tokens=%s output_tokens=%s estimated_cost_usd=%s",
        model, success, latency_ms, input_tokens, output_tokens, cost.quantize(Decimal("0.00000001"))
    )


async def send_error_alert(event: str, error: Exception) -> None:
    if not config.AI_ALERT_WEBHOOK_URL:
        return
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                config.AI_ALERT_WEBHOOK_URL,
                json={"event": event, "error": type(error).__name__}
            )
    except Exception:
        logger.exception("Failed to send AI error alert")
