from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "MoneyMate — Financial Expense Management API"
    app_env: str = "development"
    database_url: str
    db_echo: bool = False

    # JWT Settings
    secret_key: str
    algorithm: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()