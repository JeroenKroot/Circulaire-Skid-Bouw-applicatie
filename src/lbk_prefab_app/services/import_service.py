"""Importeer brondata en seed database."""

from __future__ import annotations

# standaardbibliotheken
import logging

# third-party bibliotheken
import pandas as pd

# eigen modules
from src.lbk_prefab_app.config import AppSettings
from src.lbk_prefab_app.database import get_session
from src.lbk_prefab_app.models.db_models import Component, PriceRule

logger = logging.getLogger(__name__)


def _normalize_text(value) -> str | None:
    """Normaliseer optionele tekstvelden en behandel n.v.t. als leeg."""
    if pd.isna(value):
        return None

    text = str(value).strip()
    if not text:
        return None

    if text.lower() in {"n.v.t.", "n.v.t", "nvt", "niet van toepassing", "-"}:
        return None

    return text


def _component_family(component_code: str) -> str:
    """Bepaal de componentfamilie op basis van de broncode."""
    code = component_code.upper()

    if code.startswith("CP01"):
        return "CP01"
    if code.startswith("IRA01"):
        return "IRA01"
    if code.startswith("AF01"):
        return "AF01"
    if code.startswith("TI01"):
        return "TI01"
    if code.startswith("TT01"):
        return "TT01"
    if code.startswith("VA01"):
        return "VA01"
    if code.startswith("S"):
        return "S"
    if code.startswith("FF"):
        return "FF"

    return code


def _build_selection_code(row: pd.Series, index: int) -> str:
    """Maak een gegarandeerd unieke sleutel per bronregel."""
    component_code = str(row["Component code"]).strip().upper()
    item_type = str(row["Type"]).strip().upper()

    artikel_eriks = _normalize_text(row.get("Artikelnummer Eriks"))
    artikel_tu = _normalize_text(row.get("Artikelnummer TU"))

    if artikel_eriks:
        return f"{component_code}__ERIKS__{artikel_eriks.upper()}__{index}"

    if artikel_tu:
        return f"{component_code}__TU__{artikel_tu.upper()}__{index}"

    return f"{component_code}__TYPE__{item_type}__{index}"


def _seed_price_rule(component: Component) -> PriceRule:
    """Genereer een prototype-prijsregel op basis van componentcategorie."""
    if component.component_family == "CP01":
        price = max(220.0, component.gewicht_kg * 110.0)
        minutes = 18.0
    elif component.component_family == "IRA01":
        price = max(45.0, component.gewicht_kg * 95.0)
        minutes = 8.0
    elif component.component_family == "AF01":
        price = max(35.0, component.gewicht_kg * 85.0)
        minutes = 6.0
    elif component.component_family == "TI01":
        price = 25.0
        minutes = 4.0
    elif component.component_family == "TT01":
        price = 75.0
        minutes = 8.0
    elif component.component_family == "VA01":
        price = 30.0
        minutes = 5.0
    elif component.component_family == "S":
        price = max(8.0, component.gewicht_kg * 4.5)
        minutes = 6.0
    elif component.component_family == "FF":
        price = max(10.0, component.gewicht_kg * 12.5)
        minutes = 4.0
    else:
        price = max(10.0, component.gewicht_kg * 20.0)
        minutes = 5.0

    return PriceRule(
        selection_code=component.selection_code,
        material_price_eur=round(price, 2),
        assembly_minutes=minutes,
        is_pipe=component.component_family in {"S", "FF"},
    )


def seed_database_if_needed(settings: AppSettings) -> None:
    """Lees de brondata in en seed de database opnieuw."""
    with get_session() as session:
        session.query(PriceRule).delete()
        session.query(Component).delete()
        session.commit()

        source_path = settings.source_xlsx_path if settings.source_xlsx_path.exists() else settings.source_csv_path
        logger.info("Lees bronbestand: %s", source_path)

        if source_path.suffix.lower() == ".csv":
            dataframe = pd.read_csv(source_path)
        else:
            dataframe = pd.read_excel(source_path)

        components: list[Component] = []

        for index, row in dataframe.iterrows():
            try:
                component_code = str(row["Component code"]).strip().upper()
                selection_code = _build_selection_code(row, index)

                component = Component(
                    selection_code=selection_code,
                    merk=str(row["Merk"]).strip(),
                    type=str(row["Type"]).strip(),
                    omschrijving=str(row["Omschrijving"]).strip(),
                    component_code=component_code,
                    component_family=_component_family(component_code),
                    artikelnummer_eriks=_normalize_text(row.get("Artikelnummer Eriks")),
                    artikelnummer_tu=_normalize_text(row.get("Artikelnummer TU")),
                    co2_eq_kg=float(row["Co2 eq kg"]),
                    gewicht_kg=float(row["Gewicht [kg]"]),
                    gietijzer=float(row.get("Gietijzer", 0.0) or 0.0),
                    metalen=float(row.get("Metalen", 0.0) or 0.0),
                    fossiele_materialen=float(row.get("Fossiele materialen", 0.0) or 0.0),
                    aluminium=float(row.get("Aluminium", 0.0) or 0.0),
                    staal=float(row.get("Staal", 0.0) or 0.0),
                    rvs=float(row.get("RVS", 0.0) or 0.0),
                    koper=float(row.get("Koper", 0.0) or 0.0),
                    brons=float(row.get("Brons", 0.0) or 0.0),
                    keramiek=float(row.get("Keramiek", 0.0) or 0.0),
                    rubber=float(row.get("Rubber", 0.0) or 0.0),
                    polymeren_en_composieten=float(row.get("polymeren en compositen", 0.0) or 0.0),
                    injectie_gevormde_magneet=float(row.get("Injectie gevormde magneet", 0.0) or 0.0),
                    elektra=float(row.get("elektra", 0.0) or 0.0),
                )

                components.append(component)

            except Exception as exc:
                logger.warning("Fout bij inlezen rij %s: %s", index, exc)

        session.add_all(components)
        session.flush()

        price_rules = [_seed_price_rule(component) for component in components]
        session.add_all(price_rules)

        logger.info("Database succesvol gevuld met %s componenten", len(components))
