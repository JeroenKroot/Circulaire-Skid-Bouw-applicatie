"""Hoofd-UI voor configuratie en materialen/CO2."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import select

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
from src.lbk_prefab_app.services.report_service import build_result_pdf
from src.lbk_prefab_app.ui.layout import render_shell_header, render_stepbar
from src.lbk_prefab_app.ui.styles import get_app_css


def build_component_label(component) -> str:
    return f"{component.component_code} | {component.merk} | {component.type}"


def render_component_select(session, label: str, family: str, key: str):
    components = list_component_options(session, family)
    option_keys = ["NVT"] + [component.selection_code for component in components]
    option_map = {component.selection_code: build_component_label(component) for component in components}

    selected_key = st.selectbox(
        label,
        options=option_keys,
        format_func=lambda value: "N.v.t." if value == "NVT" else option_map[value],
        key=key,
    )
    return None if selected_key == "NVT" else get_component_by_selection_code(session, selected_key)


def render_visual_panel() -> None:
    st.markdown(
        """
        <div class="card">
            <div class="visual-tab-row">
                <div class="visual-tab active">3D weergave</div>
                <div class="visual-tab">Schema</div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    pdf_path = Path("assets/W-PF-5000-000-0-01.pdf")
    image_path = Path("assets/lbk_preview.png")

    if image_path.exists():
        st.image(str(image_path), use_container_width=True)
    elif pdf_path.exists():
        st.info("Plaats een geëxporteerde PNG van de PDF in assets/lbk_preview.png voor de mooiste weergave.")
        st.caption("De visuele referentie hoort bij de prefab LBK-set uit de tekening.")
    else:
        st.warning("Geen visualisatiebestand gevonden.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_app(settings) -> None:
    st.markdown(get_app_css(), unsafe_allow_html=True)
    st.markdown('<div class="app-shell">', unsafe_allow_html=True)

    render_shell_header()

    if "active_step" not in st.session_state:
        st.session_state.active_step = "configuratie"

    render_stepbar(st.session_state.active_step)

    st.markdown('<div class="page-title">Instellingen prefab LBK set</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Stel hier je prefab aansluitset samen. Het systeem berekent automatisch de CO₂-uitstoot, materiaalinhoud en verkoopprijs.</div>',
        unsafe_allow_html=True,
    )

    with get_session() as session:
        if st.session_state.active_step == "configuratie":
            left_col, mid_col, right_col = st.columns([1.0, 2.1, 1.1], gap="large")

            with left_col:
                st.markdown('<div class="card"><div class="card-title">Configuratie</div>', unsafe_allow_html=True)

                selected_components = []
                for position in SET_POSITIONS:
                    component = render_component_select(
                        session=session,
                        label=str(position["label"]),
                        family=str(position["family"]),
                        key=f"select_{position['position_code']}",
                    )
                    if component is not None:
                        selected_components.append((component, float(position["quantity"])))

                pipe_choices = get_pipe_choices(session)
                pipe_option_map = {pipe.selection_code: build_component_label(pipe) for pipe in pipe_choices}
                pipe_keys = ["NVT"] + [pipe.selection_code for pipe in pipe_choices]

                selected_pipe_key = st.selectbox(
                    "Leidingtype",
                    options=pipe_keys,
                    format_func=lambda value: "N.v.t." if value == "NVT" else pipe_option_map[value],
                    key="pipe_select",
                )

                pipe_length = st.number_input(
                    "Totale leidinglengte (meter)",
                    min_value=0.0,
                    value=2.5,
                    step=0.5,
                )

                if st.button("Bereken", use_container_width=True):
                    st.session_state.active_step = "materialen"
                    st.session_state.selected_components = selected_components
                    st.session_state.selected_pipe_key = selected_pipe_key
                    st.session_state.pipe_length = pipe_length
                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

            with mid_col:
                render_visual_panel()
                st.markdown(
                    '<div class="note-text">Referentiecomponenten uit de tekening: CP01, RA01-32, IRA01-32, AF01-40, TI01, TT en VA01-15.</div>',
                    unsafe_allow_html=True,
                )

            with right_col:
                st.markdown('<div class="card"><div class="card-title">Uitkomst</div>', unsafe_allow_html=True)
                st.markdown(
                    '<div class="result-highlight"><div class="result-label">Totale CO₂ uitstoot</div><div class="result-value">Nog niet berekend</div></div><div class="note-text">Klik op Bereken om de resultaten te tonen en het PDF-rapport te downloaden.</div>',
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

        else:
            selected_components = st.session_state.get("selected_components", [])
            selected_pipe_key = st.session_state.get("selected_pipe_key", "NVT")
            pipe_length = st.session_state.get("pipe_length", 0.0)

            items_with_price_rules = []
            total_co2 = 0.0
            material_totals = defaultdict(float)
            bom_rows = []

            for component, quantity in selected_components:
                rule = session.scalar(select(PriceRule).where(PriceRule.selection_code == component.selection_code))
                if rule is None:
                    continue

                items_with_price_rules.append((component, quantity, rule))
                total_co2 += calculate_component_co2(component, quantity)

                for material_name, value in calculate_material_passport(component, quantity).items():
                    material_totals[material_name] += value

                bom_rows.append(
                    {
                        "Artikel": component.component_code,
                        "Artikelnummer": component.artikelnummer_eriks or component.artikelnummer_tu or "-",
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

                        bom_rows.append(
                            {
                                "Artikel": pipe_component.component_code,
                                "Artikelnummer": pipe_component.artikelnummer_eriks or pipe_component.artikelnummer_tu or "-",
                                "Omschrijving": f"{pipe_component.omschrijving} ({pipe_length:.1f} m)",
                                "Aantal": pipe_length,
                            }
                        )

            price_summary = calculate_sales_price(settings, items_with_price_rules)
            material_rows = [
                {"Materiaal": name, "Totaal (kg)": round(value, 3)}
                for name, value in material_totals.items()
                if value > 0
            ]

            top_col_1, top_col_2 = st.columns([2, 1])

            with top_col_1:
                st.metric("Totale CO₂-uitstoot", f"{total_co2:.2f} kg CO₂e")
            with top_col_2:
                st.metric("Verkoopprijs", f"€ {price_summary['sales_price']:.2f}")

            pdf_bytes = build_result_pdf(
                sales_price=price_summary["sales_price"],
                total_co2=total_co2,
                bom_rows=bom_rows,
                material_rows=material_rows,
            )

            st.download_button(
                "Download PDF resultaten",
                data=pdf_bytes,
                file_name="prefab_lbk_resultaten.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            st.subheader("Stuklijst")
            st.dataframe(pd.DataFrame(bom_rows), use_container_width=True)

            st.subheader("Materialenpaspoort")
            st.dataframe(pd.DataFrame(material_rows), use_container_width=True)

            if st.button("Terug naar configuratie"):
                st.session_state.active_step = "configuratie"
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)