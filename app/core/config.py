from __future__ import annotations

import secrets
from typing import Optional, Literal

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- app metadata & environment ---
    APP_NAME: str = "Finance Assistant"
    ENV: Literal["local", "dev", "prod"] = "local"

    # --- database ---
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"

    # --- sessions / auth ---
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(64))
    SESSION_COOKIE_NAME: str = "fa_session"
    DEMO_USERNAME: Optional[str] = None  # set in .env for demo-only
    DEMO_PASSWORD: Optional[str] = None  # set in .env for demo-only

    # --- OpenAPI docs exposure ---
    ENABLE_DOCS: bool = True
    ENABLE_REDOC: bool = True

    # --- optional: outbound API client for the Queries page ---
    API_BASE_URL: Optional[AnyHttpUrl] = None
    API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",         # ignore unknown env vars instead of erroring
        case_sensitive=True,
    )


settings = Settings()