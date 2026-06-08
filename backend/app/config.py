"""Application configuration via environment variables."""

from typing import ClassVar

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from .env or environment variables."""

    # Database
    database_url: str = "sqlite:///./data/ai_wellness.db"

    # Application
    app_name: str = "AI Wellness Platform"
    debug: bool = False
    language: str = "en"

    # JWT Authentication
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: list[str] = [
        "http://localhost:8501",
        "http://localhost:8000",
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8000",
    ]

    model_config: ClassVar[dict] = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Support both JSON array and comma-separated values."""
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                import json
                return json.loads(v)
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    def check_production_readiness(self) -> list[str]:
        """Return a list of issues that should be fixed for production."""
        issues: list[str] = []
        if not self.jwt_secret or len(self.jwt_secret) < 16:
            issues.append(
                "JWT_SECRET is too short or not set. "
                "Generate a random 64-character string for production."
            )
        if self.cors_origins == ["*"]:
            issues.append(
                "CORS_ORIGINS is set to wildcard. "
                "Restrict to specific origins for production."
            )
        if self.debug:
            issues.append(
                "DEBUG is enabled. Set DEBUG=false in production."
            )
        return issues


settings = Settings()
