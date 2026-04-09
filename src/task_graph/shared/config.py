from pathlib import Path
from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

_ENV_FILE_PATH = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Shared kernel application settings."""

    # Database Configuration
    database_url: Optional[PostgresDsn] = Field(
        default=None,
        description="PostgreSQL Database Connection String"
    )
    test_database_url: Optional[PostgresDsn] = Field(
        default=None,
        description="PostgreSQL Test Database Connection String"
    )

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore unexpected environment variables
    )


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Singleton getter for shared kernel settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
