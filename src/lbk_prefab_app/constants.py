"""Domeinconstanten voor de prefab LBK-app."""

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
    "polymeren en composieten",
    "Injectie gevormde magneet",
    "elektra",
)

SET_POSITIONS: tuple[dict[str, object], ...] = (
    {
        "position_code": "PUMP",
        "label": "Pomp (CP01)",
        "family": "CP01",
        "quantity": 1,
        "allow_na": True,
    },
    {
        "position_code": "IRA_1",
        "label": "Inregelafsluiter 1 (IRA01)",
        "family": "IRA01",
        "quantity": 1,
        "allow_na": True,
    },
    {
        "position_code": "IRA_2",
        "label": "Inregelafsluiter 2 (IRA02)",
        "family": "IRA01",
        "quantity": 1,
        "allow_na": True,
    },
    {
        "position_code": "AF_1",
        "label": "Kogelkraan (AF01)",
        "family": "AF01",
        "quantity": 1,
        "allow_na": True,
    },
    {
        "position_code": "RA_1",
        "label": "Regelafsluiter (RA-01)",
        "family": "RA-01",
        "quantity": 1,
        "allow_na": True,
    },
    {
        "position_code": "TI_1",
        "label": "Thermometer (TI01)",
        "family": "TI01",
        "quantity": 1,
        "allow_na": True,
    },
    {
        "position_code": "TI_2",
        "label": "Thermometer (TI02)",
        "family": "TI01",
        "quantity": 1,
        "allow_na": True,
    },
    {
        "position_code": "TT_1",
        "label": "Transmitter (TT)",
        "family": "TT01",
        "quantity": 1,
        "allow_na": True,
    },
    {
        "position_code": "VA_1",
        "label": "Vul- en aftapkraan (VA01)",
        "family": "VA01",
        "quantity": 1,
        "allow_na": True,
    },
)

PIPE_OPTIONS: tuple[dict[str, str], ...] = (
    {"family": "S", "label": "Stalen buis"},
    {"family": "FF", "label": "FlowFit buis"},
)

POSITION_TO_IMAGE_LABEL: dict[str, str] = {
    "PUMP": "CP01",
    "IRA_1": "IRA01",
    "IRA_2": "IRA02",
    "AF_1": "AF01",
    "RA_1": "RA-01",
    "TI_1": "TI01",
    "TI_2": "TI02",
    "TT_1": "TT",
    "VA_1": "VA01",
}

IMAGE_LABEL_AREAS: dict[str, dict[str, object]] = {
    "AF01": {"bbox": (71, 202, 215, 234), "radius": 16},
    "RA-01": {"bbox": (71, 330, 215, 362), "radius": 16},
    "CP01": {"bbox": (71, 585, 215, 618), "radius": 16},
    "TI01": {"bbox": (71, 717, 215, 749), "radius": 16},
    "TT": {"bbox": (71, 931, 215, 963), "radius": 16},
    "VA01": {"bbox": (71, 1077, 215, 1109), "radius": 16},
    "IRA01": {"bbox": (546, 327, 690, 359), "radius": 16},
    "IRA02": {"bbox": (546, 584, 690, 616), "radius": 16},
    "TI02": {"bbox": (546, 717, 689, 749), "radius": 16},
}

ACTIVE_LABEL_RGB: tuple[int, int, int] = (34, 197, 94)