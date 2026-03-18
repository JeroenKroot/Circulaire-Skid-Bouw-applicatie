"""Berekeningen voor prijs, CO2 en materialenpaspoort."""

from __future__ import annotations

# standaardbibliotheken
from collections import Counter, defaultdict

# eigen modules
from src.lbk_prefab_app.config import AppSettings
from src.lbk_prefab_app.constants import MATERIAL_COLUMNS
from src.lbk_prefab_app.models.db_models import Component, PriceRule


DB_MATERIAL_FIELDS = {
    "Gietijzer": "gietijzer",
    "Metalen": "metalen",
    "Fossiele materialen": "fossiele_materialen",
    "Aluminium": "aluminium",
    "Staal": "staal",
    "RVS": "rvs",
    "Koper": "koper",
    "Brons": "brons",
    "Keramiek": "keramiek",
    "Rubber": "rubber",
    "polymeren en compositen": "polymeren_en_composieten",
    "Injectie gevormde magneet": "injectie_gevormde_magneet",
    "elektra": "elektra",
}


def calculate_component_co2(component: Component, quantity: float) -> float:
    """Bereken CO2 conform de opgegeven formule."""
    return component.co2_eq_kg * component.gewicht_kg * quantity


def calculate_material_passport(component: Component, quantity: float) -> dict[str, float]:
    """Bereken materiaalmassa's per materiaalcategorie."""
    results: dict[str, float] = {}
    for label, field in DB_MATERIAL_FIELDS.items():
        fraction = getattr(component, field)
        results[label] = component.gewicht_kg * fraction * quantity
    return results


def calculate_sales_price(
    settings: AppSettings,
    selected_items: list[tuple[Component, float, PriceRule]],
) -> dict[str, float]:
    """Bereken de verkoopprijs volgens het afgesproken prototype-model."""
    material_cost = sum(rule.material_price_eur * quantity for _, quantity, rule in selected_items)
    assembly_minutes = sum(rule.assembly_minutes * quantity for _, quantity, rule in selected_items)
    assembly_cost = (assembly_minutes / 60.0) * settings.hourly_rate_eur
    subtotal = material_cost + assembly_cost
    subtotal_with_surcharge = subtotal * (1.0 + settings.surcharge_pct)
    sales_price = subtotal_with_surcharge * (1.0 + settings.margin_pct)
    return {
        "material_cost": round(material_cost, 2),
        "assembly_cost": round(assembly_cost, 2),
        "subtotal": round(subtotal, 2),
        "sales_price": round(sales_price, 2),
    }
