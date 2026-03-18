"""Pydantic-schema's voor validatie van brondata en configuratie."""

from __future__ import annotations

# standard libraries
from typing import Literal

# third-party
from pydantic import BaseModel, Field, field_validator


class ComponentImportRecord(BaseModel):
    """Gevalideerd record uit CSV/XLSX."""

    merk: str = Field(alias="Merk")
    type: str = Field(alias="Type")
    omschrijving: str = Field(alias="Omschrijving")
    component_code: str = Field(alias="Component code")
    artikelnummer_eriks: str | None = Field(alias="Artikelnummer Eriks", default=None)
    artikelnummer_tu: str | None = Field(alias="Artikelnummer TU", default=None)
    co2_eq_kg: float = Field(alias="Co2 eq kg")
    gewicht_kg: float = Field(alias="Gewicht [kg]")

    @field_validator("component_code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        """Normaliseer componentcodes zodat filters consistent werken."""
        return value.strip().upper().replace("LX", "LX")


class PipeSelection(BaseModel):
    """Gebruikerskeuze voor leidingwerk."""

    pipe_family: Literal["S", "FF"]
    diameter: str
    total_length_m: float = Field(ge=0.0, default=0.0)


class PositionSelection(BaseModel):
    """Gebruikerskeuze voor een vaste positie in de prefab-template."""

    position_code: str
    selected_component_code: str | None = None
