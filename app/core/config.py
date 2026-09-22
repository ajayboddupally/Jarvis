from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Jarvis Intelligence Gateway"
    environment: str = "development"
    api_version: str = "v1"
    log_level: str = "INFO"

    jwt_secret: str = Field(min_length=32)
    admin_api_key: str = Field(min_length=16)
    api_key_pepper: str = Field(min_length=16)

    database_url: str
    redis_url: str

    intelligence_service_url: str = "http://localhost:8001"
    agent_service_url: str = "http://localhost:8002"

    request_timeout_seconds: float = 60.0
    rate_limit_per_minute: int = 60
    max_request_body_bytes: int = 1_048_576

    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
