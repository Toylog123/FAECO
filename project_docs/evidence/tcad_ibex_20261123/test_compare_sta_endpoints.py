from pathlib import Path

import pytest

from compare_ibex import TrialFailure, parse_sta, render_sta


BASE_REPORT = """IBEX_SETUP_PS -2
IBEX_HOLD_PS 3
IBEX_TNS_PS -5
IBEX_HOLD_TNS_PS 0
IBEX_MAX_SLEW_START
IBEX_MAX_SLEW_END
IBEX_MAX_CAPACITANCE_START
IBEX_MAX_CAPACITANCE_END
IBEX_INPUT in
IBEX_OUTPUT out
"""


def test_sta_inventory_preserves_endpoint_names_and_deduplicates_path_groups():
    output = BASE_REPORT + """IBEX_SETUP_NEG_BEGIN
IBEX_SETUP_NEG reg[1]/D
IBEX_SETUP_NEG reg[1]/D
IBEX_SETUP_NEG out
IBEX_SETUP_NEG_END
"""
    assert parse_sta(output)["setup_negative_endpoints"] == ["out", "reg[1]/D"]


def test_sta_inventory_distinguishes_empty_from_missing_or_truncated():
    assert "setup_negative_endpoints" not in parse_sta(BASE_REPORT)
    assert parse_sta(BASE_REPORT + "IBEX_SETUP_NEG_BEGIN\nIBEX_SETUP_NEG_END\n")["setup_negative_endpoints"] == []
    with pytest.raises(TrialFailure, match="incomplete setup violation endpoint inventory"):
        parse_sta(BASE_REPORT + "IBEX_SETUP_NEG_BEGIN\nIBEX_SETUP_NEG out\n")


def test_sta_inventory_report_is_opt_in():
    path = Path("input")
    assert "IBEX_SETUP_NEG_BEGIN" not in render_sta([], path, path, path)
    assert "-endpoint_path_count 1" in render_sta([], path, path, path, report_setup_endpoints=True)
