"""Layout helpers voor de visuele opbouw van de app."""

from __future__ import annotations

import streamlit as st


def render_shell_header() -> None:
    """Render de hoofdheader van de app."""
    st.markdown(
        """
        <div class="app-title-row">
            <div class="app-title-icon">♻</div>
            <div class="app-title-text">Circulaire economie App</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stepbar(active_step: str) -> None:
    """Render de stappenbalk."""
    step_1_class = "step active" if active_step == "configuratie" else "step"
    step_2_class = "step active" if active_step == "materialen" else "step"

    st.markdown(
        f"""
        <div class="stepbar">
            <div class="{step_1_class}">1. Configuratie</div>
            <div class="{step_2_class}">2. Materialen &amp; CO₂</div>
        </div>
        """,
        unsafe_allow_html=True,
    )