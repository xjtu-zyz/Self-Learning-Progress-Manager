"""Minimal application settings for local development."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://star_user:star_password@localhost:5432/star_db",
    )


settings = Settings()
