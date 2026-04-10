from __future__ import annotations

from src.lbk_prefab_app.constants import MATERIAL_COLUMNS


def calculate_component_co2(component, quantity: float) -> float:
    """Bereken de CO₂-uitstoot voor een component.

    In de brondata is co2_eq_kg de CO₂-factor per kg materiaal/product.
    Daarom rekenen we:
        co2_eq_kg × gewicht_kg × hoeveelheid
    """
    co2_per_kg = float(getattr(component, "co2_eq_kg", 0.0) or 0.0)
    weight_kg = float(getattr(component, "gewicht_kg", 0.0) or 0.0)
    return co2_per_kg * weight_kg * float(quantity)


def calculate_material_passport(component, quantity: float) -> dict[str, float]:
    """Bereken de materiaalinhoud voor een component.

    De materiaalvelden in de brondata zijn percentages/fracties van het totaalgewicht.
    Daarom rekenen we per materiaal:
        gewicht_kg × materiaalfactor × hoeveelheid
    """
    material_totals: dict[str, float] = {}
    weight_kg = float(getattr(component, "gewicht_kg", 0.0) or 0.0)

    for material_name in MATERIAL_COLUMNS:
        attribute_name = _normalize_material_column_name(material_name)
        material_fraction = float(getattr(component, attribute_name, 0.0) or 0.0)
        material_totals[material_name] = weight_kg * material_fraction * float(quantity)

    return material_totals


def calculate_sales_price(selected_items: list[tuple[object, float]]) -> dict[str, float]:
    """Bereken de totale verkoopprijs op basis van echte stuk-/meterprijzen."""
    total_sales_price = 0.0

    for component, quantity in selected_items:
        unit_price = float(getattr(component, "prijs_verkoop", 0.0) or 0.0)
        total_sales_price += unit_price * float(quantity)

    return {
        "sales_price": round(total_sales_price, 2),
    }


def _normalize_material_column_name(column_name: str) -> str:
    """Zet Excel-kolomnamen om naar geldige Python-attribuutnamen."""
    normalized = column_name.strip().lower()
    normalized = normalized.replace(" ", "_")
    normalized = normalized.replace("-", "_")
    normalized = normalized.replace("/", "_")
    normalized = normalized.replace("[", "")
    normalized = normalized.replace("]", "")
    return normalized