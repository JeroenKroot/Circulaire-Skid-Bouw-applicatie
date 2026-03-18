"""Tests voor prijs-, CO2- en materiaalberekeningen."""

from __future__ import annotations

from types import SimpleNamespace

from src.lbk_prefab_app.config import AppSettings
from src.lbk_prefab_app.services.calculation_service import (
    calculate_component_co2,
    calculate_material_passport,
    calculate_sales_price,
)


def test_calculate_component_co2() -> None:
    component = SimpleNamespace(co2_eq_kg=1.22, gewicht_kg=1.0)
    assert calculate_component_co2(component, 2) == 2.44


def test_calculate_material_passport() -> None:
    component = SimpleNamespace(
        gewicht_kg=10.0,
        gietijzer=0.5,
        metalen=0.1,
        fossiele_materialen=0.0,
        aluminium=0.1,
        staal=0.1,
        rvs=0.1,
        koper=0.05,
        brons=0.0,
        keramiek=0.0,
        rubber=0.0,
        polymeren_en_composieten=0.03,
        injectie_gevormde_magneet=0.01,
        elektra=0.01,
    )
    passport = calculate_material_passport(component, 1)
    assert passport["Gietijzer"] == 5.0
    assert round(sum(passport.values()), 2) == 10.0


def test_calculate_sales_price() -> None:
    settings = AppSettings()
    component = SimpleNamespace()
    rule = SimpleNamespace(material_price_eur=100.0, assembly_minutes=30.0)
    result = calculate_sales_price(settings, [(component, 2, rule)])
    assert result["material_cost"] == 200.0
    assert result["assembly_cost"] == 80.0
    assert result["sales_price"] > result["subtotal"]
