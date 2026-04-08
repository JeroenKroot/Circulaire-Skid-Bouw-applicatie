from src.lbk_prefab_app.constants import SET_POSITIONS, VISUAL_LABEL_POSITIONS


def test_all_set_positions_have_visual_mapping() -> None:
    """Controleer dat alle configureerbare posities een visual mapping hebben."""
    for position in SET_POSITIONS:
        position_code = str(position["position_code"])
        assert position_code in VISUAL_LABEL_POSITIONS