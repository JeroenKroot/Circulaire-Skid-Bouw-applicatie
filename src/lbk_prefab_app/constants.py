"""Domeinconstanten voor de vaste module-5-template."""

from __future__ import annotations

MATERIAL_COLUMNS: tuple[str, ...] = (
    "Gietijzer",
    "Metalen",
    "Fossiele materialen",
    "Aluminium",
    "Staal",
    "RVS",
    "Koper",
    "Brons",
    "Keramiek",
    "Rubber",
    "polymeren en compositen",
    "Injectie gevormde magneet",
    "elektra",
)

SET_POSITIONS: tuple[dict[str, object], ...] = (
    {"position_code": "PUMP", "label": "Pomp", "family": "CP01", "quantity": 1, "allow_na": True},
    {"position_code": "IRA_1", "label": "Inregelafsluiter 1", "family": "IRA01", "quantity": 1, "allow_na": True},
    {"position_code": "IRA_2", "label": "Inregelafsluiter 2", "family": "IRA01", "quantity": 1, "allow_na": True},
    {"position_code": "AF_1", "label": "Kogelkraan", "family": "AF01", "quantity": 1, "allow_na": True},
    {"position_code": "TI_1", "label": "Thermometer 1", "family": "TI01", "quantity": 1, "allow_na": True},
    {"position_code": "TI_2", "label": "Thermometer 2", "family": "TI01", "quantity": 1, "allow_na": True},
    {"position_code": "TT_1", "label": "Transmitter", "family": "TT01", "quantity": 1, "allow_na": True},
    {"position_code": "VA_1", "label": "Vul- en aftapkraan", "family": "VA01", "quantity": 1, "allow_na": True},
)

PIPE_OPTIONS: tuple[dict[str, str], ...] = (
    {"family": "S", "label": "Stalen buis"},
    {"family": "FF", "label": "FlowFit buis"},
)
