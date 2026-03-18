"""Database-initialisatie en sessiebeheer."""

from __future__ import annotations

# standaardbibliotheken
from contextlib import contextmanager

# third-party bibliotheken
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""


_ENGINE = None
_SESSION_FACTORY: sessionmaker[Session] | None = None


def init_database(database_url: str) -> None:
    """Initialiseer de database-engine en maak tabellen aan."""
    global _ENGINE, _SESSION_FACTORY

    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    _ENGINE = create_engine(database_url, future=True, connect_args=connect_args)
    _SESSION_FACTORY = sessionmaker(bind=_ENGINE, autoflush=False, autocommit=False, future=True)

    # eigen modules
    from src.lbk_prefab_app.models.db_models import Component, PriceRule  # noqa: F401

    Base.metadata.create_all(_ENGINE)


@contextmanager
def get_session() -> Session:
    """Geef een database-sessie terug binnen een contextmanager."""
    if _SESSION_FACTORY is None:
        raise RuntimeError("Database is nog niet geïnitialiseerd.")

    session = _SESSION_FACTORY()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
