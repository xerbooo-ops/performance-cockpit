from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PERFORMANCE_COCKPIT_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Performance Cockpit API"
    environment: str = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://performance_cockpit:change-me-locally@localhost:5432/performance_cockpit"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])


@lru_cache
def get_settings() -> Settings:
    return Settings()
