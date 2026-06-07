"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from .env or environment variables."""

    # Database
    database_url: str = "sqlite:///./data/ai_wellness.db"

    # Application
    app_name: str = "AI Wellness Platform"
    debug: bool = True
    language: str = "en"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
