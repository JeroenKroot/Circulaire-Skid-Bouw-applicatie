"""Services voor componentselectie en lookup."""

from __future__ import annotations

# third-party bibliotheken
from sqlalchemy import select
from sqlalchemy.orm import Session

# eigen modules
from src.lbk_prefab_app.models.db_models import Component


def list_component_options(session: Session, family: str) -> list[Component]:
    """Geef alle componenten terug voor een componentfamilie."""
    statement = (
        select(Component)
        .where(Component.component_family == family)
        .order_by(Component.merk.asc(), Component.type.asc())
    )
    return list(session.scalars(statement).all())


def get_component_by_selection_code(session: Session, selection_code: str) -> Component | None:
    """Haal precies één component op via de unieke selection_code."""
    statement = select(Component).where(Component.selection_code == selection_code)
    return session.scalar(statement)


def get_pipe_choices(session: Session) -> list[Component]:
    """Geef leidingopties terug.

    In deze prototypefase vallen leidingopties onder familie S of FF.
    """
    statement = (
        select(Component)
        .where(Component.component_family.in_(["S", "FF"]))
        .order_by(Component.component_code.asc(), Component.type.asc())
    )
    return list(session.scalars(statement).all())
