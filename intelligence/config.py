from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class IntelligenceSettings(BaseSettings):
    service_name: str = "Jarvis Intelligence Service"
    environment: str = "development"
    service_version: str = "0.1.0"

    database_url: str

    default_model: str = "jarvis-local"
    max_context_messages: int = Field(default=20, ge=1, le=200)

    external_model_url: str | None = None
    external_model_api_key: str | None = None
    external_model_name: str = "external-default"
    model_timeout_seconds: float = 60.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> IntelligenceSettings:
    return IntelligenceSettings()


settings = get_settings()
