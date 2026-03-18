"""Loggingconfiguratie."""

from __future__ import annotations

# standaardbibliotheken
import logging


def configure_logging(level: str = "INFO") -> None:
    """Initialiseer logging voor de applicatie."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
