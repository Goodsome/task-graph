from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings using pydantic-settings.
    Loads configuration from environment variables and .env files.
    """
    # Database Configuration
    DATABASE_URL: Optional[PostgresDsn] = Field(
        default=None,
        description="PostgreSQL Database Connection String"
    )

    # Logging Configuration
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    # General Configuration
    PROJECT_ROOT: str = Field(
        default=".",
        description="Root directory of the project"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore unexpected environment variables
    )

_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Singleton getter for settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
