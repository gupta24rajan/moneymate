from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "MoneyMate — Financial Expense Management API"
    app_env: str ="development"
    database_url: str

    # JWT Settings
    secret_key: str  # .env se SECRET_KEY ki value automatic load karega
    algorithm: str = "HS256"  # .env se ALGORITHM load karega, default HS256

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Extra env variables hone par error prevent karta hai
    )

settings = Settings()