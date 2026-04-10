from __future__ import annotations

from sqlalchemy import or_, select

from src.lbk_prefab_app.models.db_models import Component


def list_component_options(session, family: str) -> list[Component]:
    """Geef alle componenten terug die horen bij een componentfamilie.

    De volgorde blijft gelijk aan de oorspronkelijke Excel-volgorde
    doordat we sorteren op het database-id.
    """
    statement = (
        select(Component)
        .where(Component.component_family == family)
        .order_by(Component.id)
    )
    return list(session.scalars(statement).all())


def get_component_by_selection_code(session, selection_code: str) -> Component | None:
    """Haal exact één component op basis van de unieke selection_code."""
    statement = select(Component).where(Component.selection_code == selection_code)
    return session.scalar(statement)


def get_pipe_choices(session) -> list[Component]:
    """Geef alle leidingopties terug in Excel-volgorde."""
    statement = (
        select(Component)
        .where(or_(Component.component_family == "S", Component.component_family == "FF"))
        .order_by(Component.id)
    )
    return list(session.scalars(statement).all())