from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ShadowPlant AI"
    environment: str = "dev"
    secret_key: str = Field(default="change-me", min_length=8)
    access_token_expire_minutes: int = 60
    database_url: str = "postgresql+psycopg://shadow:shadow@db:5432/shadowplant"
    rate_limit: str = "60/minute"
    max_upload_rows: int = 100000
    max_upload_size_mb: int = 10
    mssql_database_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
