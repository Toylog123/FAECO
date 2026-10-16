"""A Liberty output's high-impedance condition is part of rewrite semantics."""

from dataclasses import replace
from pathlib import Path
import re

import pytest

from rseco.logic_rewrite import LibCell, apply_rewrite, equivalence_candidates, parse_liberty_cells


ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"


@pytest.fixture(scope="module")
def actual_lib():
    return parse_liberty_cells(LIBRARY.read_text(encoding="utf-8"))


def _cell(name, *, data="A", enable="EN", output="Z", disable=None):
    return LibCell(
        name, name, 1, output, f"(!{data})", [data, enable],
        output_functions={output: f"(!{data})"},
        three_state_functions={output: disable or f"({enable})"},
    )


def test_new_metadata_defaults_preserve_legacy_libcell_construction():
    assert LibCell("inv", "inv", 1, "Y", "(!A)").three_state_functions == {}


def test_actual_liberty_captures_every_three_state_output(actual_lib):
    text = LIBRARY.read_text(encoding="utf-8")
    expected_count = len(re.findall(r"\bthree_state\s*:", text))
    assert expected_count == 13
    assert sum(len(cell.three_state_functions) for cell in actual_lib.values()) == expected_count
    assert actual_lib["sky130_fd_sc_hd__einvn_1"].three_state_functions == {"Z": "(TE_B)"}
    assert actual_lib["sky130_fd_sc_hd__einvp_1"].three_state_functions == {"Z": "(TE')"}


def test_nested_pin_body_keeps_three_state_after_timing_blocks():
    text = '''cell ("sky130_fd_sc_hd__test_1") {
      pin ("A") { direction : "input"; }
      pin ("EN") { direction : "input"; }
      pin ("Z") { direction : "output"; function : "(!A)";
        timing () { related_pin : "A"; cell_rise (x) { values("0"); } }
        three_state : "(EN)";
      }
      pin ("Y") { direction : "output"; function : "(A)";
        internal_power () { when : "A"; }
        three_state : "(!EN)";
      }
    }'''
    cell = parse_liberty_cells(text)["sky130_fd_sc_hd__test_1"]
    assert cell.output_functions == {"Z": "(!A)", "Y": "(A)"}
    assert cell.three_state_functions == {"Z": "(EN)", "Y": "(!EN)"}


@pytest.mark.parametrize("source", ["clkinv_1", "inv_1"])
def test_plain_inverter_cannot_rewrite_to_tristate_inverter(actual_lib, source):
    candidates = equivalence_candidates(actual_lib[f"sky130_fd_sc_hd__{source}"], actual_lib)
    assert candidates
    assert not any(name.startswith(("sky130_fd_sc_hd__einvn_", "sky130_fd_sc_hd__einvp_")) for name, _ in candidates)


def test_tristate_inverter_cannot_drop_enable_semantics(actual_lib):
    candidates = dict(equivalence_candidates(actual_lib["sky130_fd_sc_hd__einvn_1"], actual_lib))
    assert "sky130_fd_sc_hd__inv_1" not in candidates
    assert "sky130_fd_sc_hd__clkinv_1" not in candidates
    assert "sky130_fd_sc_hd__einvp_1" not in candidates


def test_actual_tristate_equivalence_preserves_enable_pin(actual_lib):
    candidates = dict(equivalence_candidates(actual_lib["sky130_fd_sc_hd__einvn_1"], actual_lib))
    assert candidates["sky130_fd_sc_hd__einvn_2"] == {"A": "A", "TE_B": "TE_B"}


def test_renamed_data_enable_and_output_roles_are_mapped_together():
    source = _cell("src")
    target = _cell("dst", data="D", enable="OE_N", output="Y")
    candidates = dict(equivalence_candidates(source, {"src": source, "dst": target}))
    assert candidates["dst"] == {"A": "D", "EN": "OE_N", "Z": "Y"}
    updated = apply_rewrite("sky130_fd_sc_hd__src_1 u (.A(a), .EN(e), .Z(z));", "u", "sky130_fd_sc_hd__dst_1", candidates["dst"])
    assert ".D(a)" in updated and ".OE_N(e)" in updated and ".Y(z)" in updated


def test_data_and_enable_variable_sharing_cannot_be_canonicalized_independently():
    source = _cell("src", disable="(A)")
    target = _cell("dst", data="D", enable="OE_N", disable="(OE_N)")
    assert equivalence_candidates(source, {"dst": target}) == []


@pytest.mark.parametrize("invalid", ["undeclared_enable", "unmapped_required_input", "different_polarity"])
def test_incomplete_or_different_tristate_roles_fail_closed(invalid):
    source = _cell("src")
    target = _cell("dst")
    if invalid == "undeclared_enable":
        target = replace(target, three_state_functions={"Z": "(GHOST)"})
    elif invalid == "unmapped_required_input":
        target = replace(target, input_pins=["A", "EN", "EXTRA"])
    else:
        target = replace(target, three_state_functions={"Z": "(!EN)"})
    assert equivalence_candidates(source, {"dst": target}) == []


def test_all_output_roles_are_checked_not_only_last_output():
    source = replace(_cell("src"), output_pin="Y", function="(A)",
                     output_functions={"Z": "(!A)", "Y": "(A)"})
    target = replace(source, name="dst", three_state_functions={"Y": "(EN)"})
    assert equivalence_candidates(source, {"dst": target}) == []
