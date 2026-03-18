"""Tests voor hulpfuncties uit import_service."""

from __future__ import annotations

from src.lbk_prefab_app.services.import_service import _component_family


def test_component_family_mapping() -> None:
    assert _component_family("IRA01-32-ST") == "IRA01"
    assert _component_family("AF01-40-ST") == "AF01"
    assert _component_family("S40") == "S"
    assert _component_family("FF32") == "FF"
