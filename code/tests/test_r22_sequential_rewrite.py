"""Combinational R must never reinterpret a state output as an input pin."""
from dataclasses import replace
from pathlib import Path
import re

import pytest

from rseco.gate_sizing import build_available_sizes, larger_size_candidates
from rseco.logic_rewrite import LibCell, equivalence_candidates, parse_liberty_cells


ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
LIBERTY_TEXT = LIBRARY.read_text(encoding="utf-8")
# Independently enumerate the actual Liberty group markers; do not derive
# the expected sequential-cell domain from the production classification.
HEADERS = list(re.finditer(r'cell\s*\("(sky130_fd_sc_hd__[^\"]+)"\)\s*\{', LIBERTY_TEXT))
ACTUAL_SEQUENTIAL = {}
for index, header in enumerate(HEADERS):
    block = LIBERTY_TEXT[header.end():HEADERS[index + 1].start() if index + 1 < len(HEADERS) else len(LIBERTY_TEXT)]
    marker = re.search(r"\b(ff|latch)\s*\([^)]*\)\s*\{", block)
    if marker:
        ACTUAL_SEQUENTIAL[header.group(1)] = marker.group(1)


@pytest.fixture(scope="module")
def actual_lib():
    return parse_liberty_cells(LIBERTY_TEXT)


def test_actual_sequential_metadata_covers_all_ff_and_latch_groups(actual_lib):
    assert list(ACTUAL_SEQUENTIAL.values()).count("ff") == 45
    assert list(ACTUAL_SEQUENTIAL.values()).count("latch") == 18
    assert {name: cell.sequential_kind for name, cell in actual_lib.items()
            if cell.sequential_kind} == ACTUAL_SEQUENTIAL


@pytest.mark.parametrize("name", sorted(ACTUAL_SEQUENTIAL))
def test_every_actual_sequential_source_has_no_combinational_R(actual_lib, name):
    cell = actual_lib[name]
    assert cell.function  # The dangerous case includes functions such as IQ.
    assert equivalence_candidates(cell, actual_lib) == []


def test_actual_dfrtp_state_output_cannot_alias_reset_set_or_edge(actual_lib):
    source = actual_lib["sky130_fd_sc_hd__dfrtp_1"]
    assert source.function == "IQ"
    assert source.clear == "!RESET_B"
    assert actual_lib["sky130_fd_sc_hd__dfstp_1"].preset == "!SET_B"
    assert actual_lib["sky130_fd_sc_hd__dfrtn_1"].clocked_on != source.clocked_on
    assert equivalence_candidates(source, actual_lib) == []


def test_every_actual_combinational_source_excludes_all_sequential_targets(actual_lib):
    violations = {
        source.name: sorted(name for name, _ in equivalence_candidates(source, actual_lib)
                            if name in ACTUAL_SEQUENTIAL)
        for source in actual_lib.values() if source.name not in ACTUAL_SEQUENTIAL
    }
    assert not {source: targets for source, targets in violations.items() if targets}


@pytest.mark.parametrize("metadata", [
    {"sequential_kind": "ff"}, {"sequential_kind": "latch"},
    {"next_state": "D"}, {"clocked_on": "CLK"}, {"latch_enable": "GATE"},
    {"clear": "!RESET_B"}, {"preset": "!SET_B"},
    {"state_var": "IQ"}, {"state_inv_var": "IQ_N"},
])
def test_partial_or_legacy_sequential_metadata_is_not_combinational(metadata):
    source = LibCell("ordinary", "buf", 1, "X", "A", ["A"], output_functions={"X": "A"})
    sequential = replace(source, name="stateful", family="stateful", **metadata)
    lib = {source.name: source, sequential.name: sequential}
    assert equivalence_candidates(sequential, lib) == []
    assert equivalence_candidates(source, lib) == []


def test_actual_legal_combinational_R_remains_available(actual_lib):
    source = actual_lib["sky130_fd_sc_hd__lpflow_inputiso1p_1"]
    candidates = dict(equivalence_candidates(source, actual_lib))
    assert candidates["sky130_fd_sc_hd__or2_1"] == {"A": "A", "SLEEP": "B"}
    assert "sky130_fd_sc_hd__clkinv_1" in dict(equivalence_candidates(actual_lib["sky130_fd_sc_hd__inv_1"], actual_lib))


def test_sequential_same_family_G_sizes_remain_available(actual_lib):
    source = "sky130_fd_sc_hd__dfrtp_1"
    assert larger_size_candidates(source, build_available_sizes(LIBERTY_TEXT)) == [
        "sky130_fd_sc_hd__dfrtp_2", "sky130_fd_sc_hd__dfrtp_4"]
    assert equivalence_candidates(actual_lib[source], actual_lib) == []
