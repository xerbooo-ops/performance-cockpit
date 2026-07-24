import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def application_data_dir() -> Path:
    """Return a writable, user-local directory without requiring configuration."""
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return root / "PerformanceCockpit"


def default_database_url() -> str:
    return f"sqlite+pysqlite:///{(application_data_dir() / 'performance-cockpit.db').as_posix()}"


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
    database_url: str = Field(default_factory=default_database_url)
    cors_origins: list[str] = Field(default_factory=list)
    migrations_dir: Path | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
