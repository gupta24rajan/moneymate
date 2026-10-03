from decimal import Decimal

from pydantic_settings import BaseSettings, SettingsConfigDict


class AIConfig(BaseSettings):
    GEMINI_API_KEY: str = ""
    LLM_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = ""
    PINECONE_DIMENSION: int = 768
    RAG_ENABLED: bool = True

    # LLM cost tracking (USD per 1M tokens) used by ai/observability.py
    LLM_INPUT_COST_PER_MILLION: Decimal = Decimal("0.30")
    LLM_OUTPUT_COST_PER_MILLION: Decimal = Decimal("2.50")

    # Optional webhook for AI error alerts
    AI_ALERT_WEBHOOK_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


config = AIConfig()