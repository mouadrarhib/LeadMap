from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    google_maps_api_key: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""
    google_oauth_redirect_uri: str = "http://localhost:8080/"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/leadmap_db"
    daily_email_limit: int = Field(default=20, ge=1, le=100)
    max_pages_per_domain: int = Field(default=5, ge=1, le=5)
    request_timeout_seconds: int = Field(default=10, ge=3, le=30)
    app_user_agent: str = "LeadMap/1.0 (+local-business-research)"

    @field_validator("google_maps_api_key", "google_client_id", "google_client_secret")
    @classmethod
    def strip_secrets(cls, value: str) -> str:
        return value.strip()


@lru_cache
def get_settings() -> Settings:
    return Settings()

