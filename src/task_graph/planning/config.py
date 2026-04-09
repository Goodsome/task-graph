from pathlib import Path
from pydantic import Field
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    """Planning context specific settings."""

    # Event Bus Configuration
    event_bus_channel: str = Field(
        default="planning_events",
        description="PostgreSQL NOTIFY channel for planning domain events"
    )

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore"
    )


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Singleton getter for planning context settings."""
    global _settings
    if _settings is None:
        # Inherit environment variables from shared settings
        _settings = Settings()
    return _settings
