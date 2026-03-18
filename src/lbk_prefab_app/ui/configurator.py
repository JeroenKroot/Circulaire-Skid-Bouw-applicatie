"""Streamlit-scherm voor configuratie en resultaatweergave."""

from __future__ import annotations

# standaardbibliotheken
from collections import defaultdict

# third-party bibliotheken
import pandas as pd
import streamlit as st
from sqlalchemy import select

# eigen modules
from src.lbk_prefab_app.constants import SET_POSITIONS
from src.lbk_prefab_app.database import get_session
from src.lbk_prefab_app.models.db_models import PriceRule
from src.lbk_prefab_app.services.calculation_service import (
    calculate_component_co2,
    calculate_material_passport,
    calculate_sales_price,
)
from src.lbk_prefab_app.services.component_service import (
    get_component_by_selection_code,
    get_pipe_choices,
    list_component_options,
)


def build_component_label(component) -> str:
    """Maak een nette labeltekst voor dropdowns."""
    return f"{component.component_code} | {component.merk} | {component.type}"


def _render_component_select(session, label: str, family: str, key: str):
    """Render een selectbox met N.v.t. plus nette componentlabels."""
    components = list_component_options(session, family)
    option_keys = ["NVT"] + [component.selection_code for component in components]
    option_map = {
        component.selection_code: build_component_label(component)
        for component in components
    }

    selected_key = st.selectbox(
        label,
        options=option_keys,
        format_func=lambda value: "N.v.t." if value == "NVT" else option_map[value],
        key=key,
    )

    if selected_key == "NVT":
        return None

    return get_component_by_selection_code(session, selected_key)


def render_app(settings) -> None:
    """Render de configurator en resultaten."""
    st.title("Circulaire economie app")
    st.caption("Prefab LBK-set configurator — module 5 conform ISSO 44")

    with get_session() as session:
        st.header("1. Configuratie")

        selected_components = []

        for position in SET_POSITIONS:
            component = _render_component_select(
                session=session,
                label=str(position["label"]),
                family=str(position["family"]),
                key=f"select_{position['position_code']}",
            )
            if component is not None:
                selected_components.append((component, float(position["quantity"])))

        st.subheader("Leidingwerk")
        pipe_choices = get_pipe_choices(session)
        pipe_option_map = {
            pipe.selection_code: build_component_label(pipe)
            for pipe in pipe_choices
        }
        pipe_option_keys = ["NVT"] + [pipe.selection_code for pipe in pipe_choices]

        selected_pipe_key = st.selectbox(
            "Leidingtype",
            options=pipe_option_keys,
            format_func=lambda value: "N.v.t." if value == "NVT" else pipe_option_map[value],
            key="pipe_select",
        )
        pipe_length = st.number_input("Totale leidinglengte (meter)", min_value=0.0, value=2.5, step=0.5)

        if st.button("Bereken"):
            items_with_price_rules = []
            total_co2 = 0.0
            material_totals = defaultdict(float)
            bom_rows = []

            for component, quantity in selected_components:
                rule = session.scalar(
                    select(PriceRule).where(PriceRule.selection_code == component.selection_code)
                )
                if rule is None:
                    st.warning(f"Geen prijsregel gevonden voor {build_component_label(component)}")
                    continue

                items_with_price_rules.append((component, quantity, rule))
                total_co2 += calculate_component_co2(component, quantity)

                for material_name, value in calculate_material_passport(component, quantity).items():
                    material_totals[material_name] += value

                article_number = component.artikelnummer_eriks or component.artikelnummer_tu or "-"
                bom_rows.append(
                    {
                        "Artikel": component.component_code,
                        "Artikelnummer": article_number,
                        "Omschrijving": component.omschrijving,
                        "Aantal": quantity,
                    }
                )

            if selected_pipe_key != "NVT" and pipe_length > 0:
                pipe_component = get_component_by_selection_code(session, selected_pipe_key)
                if pipe_component is not None:
                    pipe_rule = session.scalar(
                        select(PriceRule).where(PriceRule.selection_code == pipe_component.selection_code)
                    )
                    if pipe_rule is not None:
                        items_with_price_rules.append((pipe_component, pipe_length, pipe_rule))
                        total_co2 += calculate_component_co2(pipe_component, pipe_length)

                        for material_name, value in calculate_material_passport(pipe_component, pipe_length).items():
                            material_totals[material_name] += value

                        article_number = pipe_component.artikelnummer_eriks or pipe_component.artikelnummer_tu or "-"
                        bom_rows.append(
                            {
                                "Artikel": pipe_component.component_code,
                                "Artikelnummer": article_number,
                                "Omschrijving": f"{pipe_component.omschrijving} ({pipe_length:.1f} m)",
                                "Aantal": pipe_length,
                            }
                        )

            if not items_with_price_rules:
                st.info("Er zijn nog geen componenten geselecteerd.")
                return

            price_summary = calculate_sales_price(settings, items_with_price_rules)

            st.header("2. Resultaat")
            col1, col2 = st.columns(2)
            col1.metric("Verkoopprijs", f"€ {price_summary['sales_price']:.2f}")
            col2.metric("Totale CO₂-uitstoot", f"{total_co2:.2f} kg CO₂e")

            st.subheader("Stuklijst")
            st.dataframe(pd.DataFrame(bom_rows), use_container_width=True)

            st.subheader("Materialenpaspoort")
            material_rows = [
                {"Materiaal": name, "Totaal (kg)": round(value, 3)}
                for name, value in material_totals.items()
                if value > 0
            ]
            material_df = pd.DataFrame(material_rows).sort_values(by="Materiaal")
            st.dataframe(material_df, use_container_width=True)
