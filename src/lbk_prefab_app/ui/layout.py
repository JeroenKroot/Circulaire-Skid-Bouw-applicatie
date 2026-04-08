from __future__ import annotations
from pathlib import Path
import base64
import streamlit as st

def _image_to_base64(image_path: Path) -> str | None:
    if not image_path.exists():
        return None
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")

def render_shell_header() -> None:
    logo_path = Path("assets/Kuijpers_logo_RGB.png")
    logo_b64 = _image_to_base64(logo_path)
    logo_html = f'<div class="app-brand-logo"><img src="data:image/png;base64,{logo_b64}" alt="Kuijpers logo"></div>' if logo_b64 else ""
    st.markdown(f'''
        <div class="app-title-row">
            <div class="app-title-icon">♻</div>
            <div class="app-title-text">Circulaire component standaard</div>
            {logo_html}
        </div>
    ''', unsafe_allow_html=True)

def render_stepbar(active_step: str) -> None:
    step_1_class = "step active" if active_step == "configuratie" else "step"
    step_2_class = "step active" if active_step == "materialen" else "step"
    st.markdown(f'''
        <div class="stepbar">
            <div class="{step_1_class}">1. Configuratie</div>
            <div class="{step_2_class}">2. Materialen &amp; CO₂</div>
        </div>
    ''', unsafe_allow_html=True)
