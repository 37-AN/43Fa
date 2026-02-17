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
    expected_alembic_revision: str = "0001_init"
    worker_heartbeat_file: str = "/tmp/shadowplant/worker_heartbeat"
    worker_heartbeat_ttl_seconds: int = 180
    worker_heartbeat_interval_seconds: int = 30
    worker_analytics_interval_seconds: int = 300
    collector_input_dir: str = "/collector/inbox"
    collector_archive_dir: str = "/collector/archive"
    collector_error_dir: str = "/collector/error"
    collector_poll_seconds: int = 30
    collector_api_url: str = "http://shadowplant-api:8000"
    collector_admin_username: str = "admin"
    collector_admin_password: str = "admin123"


@lru_cache
def get_settings() -> Settings:
    return Settings()
