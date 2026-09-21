from pydantic_settings import BaseSettings, SettingsConfigDict

class AIConfig(BaseSettings):
    # OPENAI_API_KEY: str = ""
    # LLM_MODEL: str = "gpt-4o-mini"
    # EMBEDDING_MODEL: str = "text-embedding-3-small"
    # PINECONE_API_KEY: str = ""

    GEMINI_API_KEY: str = ""
    LLM_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    PINECONE_API_KEY: str = ""


    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
        )

config = AIConfig()