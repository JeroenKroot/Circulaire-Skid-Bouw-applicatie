"""Applicatieconfiguratie."""

from __future__ import annotations

# standaardbibliotheken
from pathlib import Path

# third-party bibliotheken
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Centrale applicatie-instellingen."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "LBK Prefab App"
    log_level: str = "INFO"
    hourly_rate_eur: float = 80.0
    surcharge_pct: float = 0.15
    margin_pct: float = 0.05
    database_url: str = "sqlite:///data/app.db"
    source_xlsx_path: Path = Field(default=Path("data/source/input app.xlsx"))
    source_csv_path: Path = Field(default=Path("data/source/input app.csv"))
