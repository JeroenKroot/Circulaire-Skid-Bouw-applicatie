"""Streamlit entrypoint voor de LBK prefab configurator."""

from __future__ import annotations

# standaardbibliotheken
from pathlib import Path

# third-party bibliotheken
import streamlit as st

# eigen modules
from src.lbk_prefab_app.config import AppSettings
from src.lbk_prefab_app.database import init_database
from src.lbk_prefab_app.logging_config import configure_logging
from src.lbk_prefab_app.services.import_service import seed_database_if_needed
from src.lbk_prefab_app.ui.configurator import render_app


def main() -> None:
    """Start de Streamlit-applicatie."""
    settings = AppSettings()
    configure_logging(settings.log_level)
    init_database(settings.database_url)
    seed_database_if_needed(settings=settings)
    st.set_page_config(
        page_title="Circulaire economie app",
        page_icon="♻️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    render_app(settings=settings)


if __name__ == "__main__":
    main()
