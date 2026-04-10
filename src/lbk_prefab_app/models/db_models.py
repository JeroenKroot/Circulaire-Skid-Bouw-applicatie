"""Database-tabellen."""

from __future__ import annotations

# third-party bibliotheken
from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

# eigen modules
from src.lbk_prefab_app.database import Base


class Component(Base):
    """Broncomponent uit CSV/XLSX."""

    __tablename__ = "components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    selection_code: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    merk: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[str] = mapped_column(String(200), nullable=False)
    omschrijving: Mapped[str] = mapped_column(String(200), nullable=False)

    component_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    component_family: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # # Nieuwe kolom: echte verkoopprijs uit Excel.
    # # Deze wordt straks direct gebruikt in de app voor stukprijs of meterprijs.
    prijs_verkoop: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    artikelnummer_eriks: Mapped[str | None] = mapped_column(String(100), nullable=True)
    artikelnummer_tu: Mapped[str | None] = mapped_column(String(100), nullable=True)

    co2_eq_kg: Mapped[float] = mapped_column(Float, nullable=False)
    gewicht_kg: Mapped[float] = mapped_column(Float, nullable=False)

    gietijzer: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    metalen: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    fossiele_materialen: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    aluminium: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    staal: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rvs: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    koper: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    brons: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    keramiek: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rubber: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    polymeren_en_composieten: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    injectie_gevormde_magneet: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    elektra: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class PriceRule(Base):
    """Prototype prijsregel gekoppeld aan een unieke selectie."""

    __tablename__ = "price_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    selection_code: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
    material_price_eur: Mapped[float] = mapped_column(Float, nullable=False)
    assembly_minutes: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_pipe: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)