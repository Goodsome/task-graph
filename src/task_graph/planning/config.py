from pathlib import Path
from pydantic import Field
from pydantic_settings import SettingsConfigDict
from typing import Optional
from task_graph.shared.config import Settings as SharedSettings, get_settings as get_shared_settings


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class Settings(SharedSettings):
    """Planning context specific settings."""

    # Event Bus Configuration
    EVENT_BUS_CHANNEL: str = Field(
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
