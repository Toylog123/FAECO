"""K2: Liberty output roles preserve physical instance counts and closure."""

from pathlib import Path

import pytest

from rseco.logic_rewrite import parse_liberty_cells
from rseco.netlist import Gate, Netlist, parse_verilog_netlist
from rseco.netlist_io import load_analysis_netlist
from rseco.replacement import parse_verilog_netlist_from_text


ROOT = Path(__file__).resolve().parents[2]
LIBERTY = ROOT / "data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
CONB = "sky130_fd_sc_hd__conb_1"


@pytest.fixture(scope="module")
def output_functions():
    cells = parse_liberty_cells(LIBERTY.read_text(encoding="utf-8"))
    return {name: cell.output_functions for name, cell in cells.items()}


def _design(instance, *, inputs="A, B, C", outputs="S, CO"):
    return f"module top(A, B, C, S, CO);\ninput {inputs};\noutput {outputs};\n{instance}\nendmodule\n"


def test_gate_all_outputs_keeps_legacy_constructor():
    gate = Gate("buf", "u", "Y", ("A",))
    assert gate.additional_outputs == ()
    assert gate.all_outputs == ("Y",)


@pytest.mark.parametrize("with_metadata", [False, True])
def test_real_conb_preserves_both_drivers_and_constant_aliases(output_functions, with_metadata):
    kwargs = {"cell_output_functions": output_functions} if with_metadata else {}
    net = parse_verilog_netlist_from_text(
        _design(f"{CONB} tie (.HI(S), .LO(CO));"), **kwargs
    )
    assert net.gate_count == 1
    assert net.gates[0].all_outputs == ("S", "CO")
    assert net.gates[0].inputs == ()
    assert net.resolve_alias("S") == "1'b1"
    assert net.resolve_alias("CO") == "1'b0"
    assert net.logic_level("S") == net.logic_level("CO") == 0


@pytest.mark.parametrize("family", ["fa_1", "fa_2", "fa_4", "fah_1", "fahcin_1"])
def test_actual_liberty_full_adder_outputs_do_not_become_inputs(output_functions, family):
    cell = f"sky130_fd_sc_hd__{family}"
    assert set(output_functions[cell]) == {"SUM", "COUT"}
    carry_pin = "CI" if family == "fah_1" else "CIN"
    net = parse_verilog_netlist_from_text(
        _design(f"{cell} add (.A(A), .B(B), .{carry_pin}(C), .SUM(S), .COUT(CO));"),
        cell_output_functions=output_functions,
    )
    assert net.gate_count == 1
    assert net.gates[0].all_outputs == ("CO", "S")
    assert net.gates[0].inputs == ("A", "B", "C")
    assert net.logic_level("S") == net.logic_level("CO") == 1


@pytest.mark.parametrize("connections, expected", [
    (".SUM(S)", ("S",)),
    (".SUM(), .COUT(CO)", ("CO",)),
    (".SUM(S), .COUT()", ("S",)),
    (".SUM(), .COUT()", ()),
    ("", ()),
])
def test_omitted_or_empty_outputs_still_count_one_physical_cell(output_functions, connections, expected):
    suffix = f", {connections}" if connections else ""
    net = parse_verilog_netlist_from_text(
        _design(f"sky130_fd_sc_hd__fa_1 add (.A(A), .B(B), .CIN(C){suffix});"),
        cell_output_functions=output_functions,
    )
    assert net.gate_count == 1
    assert net.gates[0].all_outputs == expected
    assert net.gates[0].inputs == ("A", "B", "C")
    assert "" not in net.logic_levels()


@pytest.mark.parametrize("entry", [parse_verilog_netlist, load_analysis_netlist])
def test_file_entry_points_forward_liberty_roles(tmp_path, output_functions, entry):
    source = tmp_path / "top.v"
    source.write_text(_design("sky130_fd_sc_hd__fa_1 add (.A(A), .B(B), .CIN(C), .SUM(S), .COUT(CO));"), encoding="utf-8")
    net = entry(source, cell_output_functions=output_functions)
    assert net.gate_count == 1
    assert net.gates[0].all_outputs == ("CO", "S")


def test_secondary_output_drives_downstream_gate(output_functions):
    source = _design("""sky130_fd_sc_hd__fa_1 add (.A(A), .B(B), .CIN(C), .SUM(sum_wire), .COUT(CO));
sky130_fd_sc_hd__buf_1 b (.A(sum_wire), .X(S));""")
    net = parse_verilog_netlist_from_text(source, cell_output_functions=output_functions)
    assert net.gate_count == 2
    assert net.logic_level("S") == 2
    assert net.logic_level("CO") == 1


@pytest.mark.parametrize("output_pin", ["Y", "X", "Z", "Q", "Q_N"])
def test_legacy_named_output_remains_supported_without_metadata(output_pin):
    net = parse_verilog_netlist_from_text(_design(f"ordinary u (.A(A), .{output_pin}(S));"))
    assert net.gates[0].all_outputs == ("S",)
    assert net.gates[0].inputs == ("A",)


@pytest.mark.parametrize("instances", [
    "buf u (S, A);\nbuf u (CO, B);",
    "buf u (.A(A), .Y(S));\nbuf u (.A(B), .Y(CO));",
])
def test_duplicate_physical_instances_rejected(instances):
    with pytest.raises(ValueError, match="[Dd]uplicate instance"):
        parse_verilog_netlist_from_text(_design(instances))


def test_literal_constant_inputs_and_assign_aliases_have_levels():
    net = parse_verilog_netlist_from_text(_design("""buf b (.A(1'b0), .Y(S));
assign CO = 1'b1;"""))
    assert net.logic_level("S") == 1
    assert net.logic_level("CO") == 0


def test_zero_input_gate_levels_cover_every_output():
    net = Netlist("top", [], ["S", "CO"], [], [Gate("source", "u", "S", (), additional_outputs=("CO",))])
    assert net.logic_levels()["S"] == net.logic_levels()["CO"] == 1


def test_metadata_overrides_legacy_output_guess_and_constant_fallback():
    net = parse_verilog_netlist_from_text(
        _design(f"{CONB} tie (.HI(A), .LO(S), .Y(B));"),
        cell_output_functions={CONB: {"LO": "1"}},
    )
    assert net.gates[0].all_outputs == ("S",)
    assert net.gates[0].inputs == ("A", "B")
    assert net.resolve_alias("S") == "1'b1"


@pytest.mark.parametrize("connections", ["", ".HI(), .LO()", ".LO(CO)"])
def test_conb_all_or_one_output_disconnected_keeps_physical_count(connections):
    net = parse_verilog_netlist_from_text(_design(f"{CONB} tie ({connections});"))
    assert net.gate_count == 1
    expected = ("CO",) if connections == ".LO(CO)" else ()
    assert net.gates[0].all_outputs == expected
    assert net.gates[0].inputs == ()
    assert "" not in net.logic_levels()


def test_unknown_conb_variant_is_not_assigned_invented_semantics():
    with pytest.raises(ValueError, match="cannot determine output pin"):
        parse_verilog_netlist_from_text(_design("sky130_fd_sc_hd__conb_999 tie (.HI(S), .LO(CO));"))
