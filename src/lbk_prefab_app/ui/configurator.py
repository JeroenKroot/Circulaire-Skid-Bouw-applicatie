from __future__ import annotations

# Standaardbibliotheken
from collections import defaultdict
from io import BytesIO
from pathlib import Path

# Third-party bibliotheken
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw
from sqlalchemy import select

# Eigen modules
from src.lbk_prefab_app.constants import (
    ACTIVE_LABEL_RGB,
    IMAGE_LABEL_AREAS,
    POSITION_TO_IMAGE_LABEL,
    SET_POSITIONS,
)
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
    """Bouw een leesbaar label voor een componentoptie."""
    return f"{component.component_code} | {component.merk} | {component.type}"


def _handle_component_selection_change(select_key: str, position_code: str) -> None:
    """Werk het actieve label in de visual bij op basis van de dropdownkeuze."""
    selected_value = st.session_state.get(select_key, "NVT")

    # # Alleen groen maken als er echt iets anders dan N.v.t. gekozen is.
    if selected_value == "NVT":
        st.session_state.active_visual_label = None
        return

    image_label = POSITION_TO_IMAGE_LABEL.get(position_code)
    st.session_state.active_visual_label = image_label


def render_component_select(
    session,
    label: str,
    family: str,
    key: str,
    position_code: str,
):
    """Render een component-selectbox en koppel wijziging aan de afbeelding."""
    # # Haal alle componentopties op voor deze familie.
    components = list_component_options(session, family)

    # # Voeg N.v.t. toe als standaardoptie.
    option_keys = ["NVT"] + [component.selection_code for component in components]

    # # Bouw een leesbare mapping voor de dropdown.
    option_map = {
        component.selection_code: build_component_label(component)
        for component in components
    }

    # # Render de selectbox en koppel een callback aan wijziging.
    selected_key = st.selectbox(
        label,
        options=option_keys,
        format_func=lambda value: "N.v.t." if value == "NVT" else option_map[value],
        key=key,
        on_change=_handle_component_selection_change,
        args=(key, position_code),
    )

    # # Geen component ophalen als N.v.t. geselecteerd is.
    if selected_key == "NVT":
        return None

    return get_component_by_selection_code(session, selected_key)


def _get_preview_image_path() -> Path | None:
    """Zoek de preview-afbeelding, met fallback op de oude bestandsnaam."""
    preferred = Path("assets/LBK_Preview.png")
    fallback = Path("assets/lbk_preview.png")

    if preferred.exists():
        return preferred
    if fallback.exists():
        return fallback
    return None


@st.cache_data(show_spinner=False)
def _load_preview_image_bytes(image_path_str: str) -> bytes:
    """Laad de bronafbeelding één keer in voor hergebruik."""
    return Path(image_path_str).read_bytes()


def _get_base_preview_image(image_path: Path) -> Image.Image:
    """Laad de bronafbeelding als Pillow-image."""
    image_bytes = _load_preview_image_bytes(str(image_path))
    return Image.open(BytesIO(image_bytes)).convert("RGBA")


def _highlight_label_region(
    image: Image.Image,
    label_code: str,
) -> Image.Image:
    """Maak het bestaande witte labelvlak in de afbeelding groen.

    Hierbij blijven tekst en rand zoveel mogelijk intact doordat alleen
    de lichte vulpixels binnen het afgeronde labelvlak worden aangepast.
    """
    label_area = IMAGE_LABEL_AREAS.get(label_code)
    if label_area is None:
        return image

    x1, y1, x2, y2 = label_area["bbox"]
    radius = int(label_area["radius"])

    # # Snijd het labelgebied uit.
    crop = image.crop((x1, y1, x2, y2)).convert("RGBA")
    crop_array = np.array(crop)

    # # Maak een mask voor de afgeronde vorm van het labelvlak.
    mask_image = Image.new("L", (crop.width, crop.height), 0)
    mask_draw = ImageDraw.Draw(mask_image)
    mask_draw.rounded_rectangle(
        (0, 0, crop.width - 1, crop.height - 1),
        radius=radius,
        fill=255,
    )
    rounded_mask = np.array(mask_image) > 0

    # # Detecteer de lichte vulpixels van het witte label.
    rgb = crop_array[:, :, :3].astype(np.uint8)
    brightness = rgb.mean(axis=2)
    color_spread = rgb.max(axis=2) - rgb.min(axis=2)

    # # Alleen de lichte, weinig verzadigde pixels binnen het labelvlak kleuren.
    fill_mask = (
        rounded_mask
        & (brightness >= 218)
        & (color_spread <= 24)
        & (crop_array[:, :, 3] > 0)
    )

    # # Kleur de witte vulpixels groen.
    crop_array[fill_mask, 0] = ACTIVE_LABEL_RGB[0]
    crop_array[fill_mask, 1] = ACTIVE_LABEL_RGB[1]
    crop_array[fill_mask, 2] = ACTIVE_LABEL_RGB[2]

    # # Plaats de aangepaste crop terug in de afbeelding.
    updated_crop = Image.fromarray(crop_array, mode="RGBA")
    updated_image = image.copy()
    updated_image.paste(updated_crop, (x1, y1))

    return updated_image


def _build_visual_image(image_path: Path, active_label: str | None) -> Image.Image:
    """Bouw de preview-afbeelding op, inclusief actieve labelhighlight."""
    base_image = _get_base_preview_image(image_path)

    # # Geen actief label betekent: originele afbeelding tonen.
    if not active_label:
        return base_image

    return _highlight_label_region(base_image, active_label)


def render_visual_panel() -> None:
    """Render de centrale preview-afbeelding."""
    st.markdown('<div class="card">', unsafe_allow_html=True)

    image_path = _get_preview_image_path()
    pdf_path = Path("assets/W-PF-5000-000-0-01.pdf")
    active_label = st.session_state.get("active_visual_label")

    if image_path is not None:
        visual_image = _build_visual_image(image_path, active_label)
        st.image(visual_image, use_container_width=True)
    elif pdf_path.exists():
        st.info("Plaats een PNG in assets/LBK_Preview.png voor de mooiste weergave.")
    else:
        st.warning("Geen visualisatiebestand gevonden.")

    st.markdown("</div>", unsafe_allow_html=True)


def _build_live_results(
    settings,
    session,
    selected_components,
    selected_pipe_key: str,
    pipe_length: float,
):
    """Bereken de live resultaten van de huidige configuratie."""
    items_with_price_rules = []
    total_co2 = 0.0
    material_totals = defaultdict(float)
    bom_rows = []

    for component, quantity in selected_components:
        rule = session.scalar(
            select(PriceRule).where(PriceRule.selection_code == component.selection_code)
        )
        if rule is None:
            continue

        items_with_price_rules.append((component, quantity, rule))
        total_co2 += calculate_component_co2(component, quantity)

        for material_name, value in calculate_material_passport(component, quantity).items():
            material_totals[material_name] += value

        bom_rows.append(
            {
                "Artikel": component.component_code,
                "Artikelnummer": component.artikelnummer_eriks
                or component.artikelnummer_tu
                or "-",
                "Omschrijving": component.omschrijving,
                "Aantal": quantity,
            }
        )

    if selected_pipe_key != "NVT" and pipe_length > 0:
        pipe_component = get_component_by_selection_code(session, selected_pipe_key)

        if pipe_component is not None:
            pipe_rule = session.scalar(
                select(PriceRule).where(
                    PriceRule.selection_code == pipe_component.selection_code
                )
            )

            if pipe_rule is not None:
                items_with_price_rules.append((pipe_component, pipe_length, pipe_rule))
                total_co2 += calculate_component_co2(pipe_component, pipe_length)

                for material_name, value in calculate_material_passport(
                    pipe_component,
                    pipe_length,
                ).items():
                    material_totals[material_name] += value

                bom_rows.append(
                    {
                        "Artikel": pipe_component.component_code,
                        "Artikelnummer": pipe_component.artikelnummer_eriks
                        or pipe_component.artikelnummer_tu
                        or "-",
                        "Omschrijving": f"{pipe_component.omschrijving} ({pipe_length:.1f} m)",
                        "Aantal": pipe_length,
                    }
                )

    price_summary = calculate_sales_price(
        settings=settings,
        selected_items=items_with_price_rules,
    )

    material_rows = [
        {"Materiaal": name, "Totaal (kg)": round(value, 3)}
        for name, value in material_totals.items()
        if value > 0
    ]

    return {
        "items_with_price_rules": items_with_price_rules,
        "total_co2": total_co2,
        "material_rows": material_rows,
        "bom_rows": bom_rows,
        "price_summary": price_summary,
    }


def render_app(settings) -> None:
    """Render de volledige Streamlit-app."""
    st.markdown(get_app_css(), unsafe_allow_html=True)
    st.markdown('<div class="app-shell">', unsafe_allow_html=True)

    render_shell_header()

    if "active_step" not in st.session_state:
        st.session_state.active_step = "configuratie"

    if "active_visual_label" not in st.session_state:
        st.session_state.active_visual_label = None

    render_stepbar(st.session_state.active_step)

    st.markdown(
        '<div class="page-title">Instellingen prefab LBK set</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        (
            '<div class="page-subtitle">'
            "Stel hier je prefab aansluitset samen. Het systeem berekent automatisch "
            "de CO₂-uitstoot, materiaalinhoud en verkoopprijs."
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    with get_session() as session:
        if st.session_state.active_step == "configuratie":
            left_col, mid_col, right_col = st.columns([1.0, 2.1, 1.1], gap="large")

            selected_components = []
            selected_pipe_key = "NVT"
            pipe_length = 2.5

            with left_col:
                st.markdown(
                    '<div class="card"><div class="card-title">Configuratie</div>',
                    unsafe_allow_html=True,
                )

                for position in SET_POSITIONS:
                    component = render_component_select(
                        session=session,
                        label=str(position["label"]),
                        family=str(position["family"]),
                        key=f"select_{position['position_code']}",
                        position_code=str(position["position_code"]),
                    )

                    if component is not None:
                        selected_components.append(
                            (component, float(position["quantity"]))
                        )

                pipe_choices = get_pipe_choices(session)
                pipe_option_map = {
                    pipe.selection_code: build_component_label(pipe)
                    for pipe in pipe_choices
                }
                pipe_keys = ["NVT"] + [pipe.selection_code for pipe in pipe_choices]

                selected_pipe_key = st.selectbox(
                    "Leidingtype",
                    options=pipe_keys,
                    format_func=lambda value: "N.v.t."
                    if value == "NVT"
                    else pipe_option_map[value],
                    key="pipe_select",
                )

                pipe_length = st.number_input(
                    "Totale leidinglengte (meter)",
                    min_value=0.0,
                    value=2.5,
                    step=0.5,
                )

                live_results = _build_live_results(
                    settings=settings,
                    session=session,
                    selected_components=selected_components,
                    selected_pipe_key=selected_pipe_key,
                    pipe_length=pipe_length,
                )

                if st.button("Bereken", use_container_width=True):
                    st.session_state.active_step = "materialen"
                    st.session_state.live_results = live_results
                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

            with mid_col:
                render_visual_panel()

            with right_col:
                st.markdown(
                    '<div class="card"><div class="card-title">Uitkomst</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
                    <div class="result-highlight">
                        <div class="result-label">Totale CO₂ uitstoot</div>
                        <div class="result-value">{live_results["total_co2"]:.2f} kg CO₂e</div>
                    </div>
                    <div class="note-text">
                        De CO₂-uitstoot wordt live bijgewerkt zodra je een keuze in de configuratie wijzigt.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)

        else:
            live_results = st.session_state.get("live_results")

            if not live_results:
                st.warning(
                    "Geen resultaten gevonden. Ga terug naar configuratie en klik op Bereken."
                )

                if st.button("Terug naar configuratie"):
                    st.session_state.active_step = "configuratie"
                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)
                return

            total_co2 = live_results["total_co2"]
            price_summary = live_results["price_summary"]
            bom_rows = live_results["bom_rows"]
            material_rows = live_results["material_rows"]

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