"""R22 K1/K4/K5 regressions; process-local checks only, never EDA."""
from pathlib import Path
import re

import pytest

import rseco.real_wns as rw
from rseco.logic_rewrite import parse_liberty_cells
from test_r22_static_action_gates import LIB, _chain, _evaluator, _job, _patch


LIB_PATH = (Path(__file__).resolve().parents[2] / "data/raw/benchmarks/raw/"
            "openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/"
            "lib/sky130_fd_sc_hd__tt_025C_1v80.lib")


@pytest.fixture(scope="module")
def sky_lib():
    return LIB_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize("abc_compatible", [False, True])
def test_every_real_sky_multioutput_cell_has_each_function(tmp_path, sky_lib, abc_compatible):
    cells = {name: cell for name, cell in parse_liberty_cells(sky_lib).items()
             if not cell.sequential_kind and len(cell.output_functions) > 1}
    assert len(cells) == 10
    text = rw.write_liberty_cell_models(sky_lib, tmp_path / "cells.v", used_cells=set(cells),
                                       abc_compatible=abc_compatible).read_text()
    for name, cell in cells.items():
        block = re.search(r"module " + re.escape(name) + r"\b(.*?)endmodule", text, re.S).group(1)
        assignments = dict(re.findall(r"assign\s+(\w+)\s*=\s*(.*?);", block))
        assert set(assignments) == set(cell.output_functions), name
        for pin, function in cell.output_functions.items():
            expected = re.sub(r"\b([01])\b", lambda m: "1'b" + m.group(1),
                              function.replace("*", "&").replace("+", "|"))
            assert assignments[pin] == expected, (name, pin)


def _constant_output():
    return _chain(2).replace("module top(A, B, Y);", "module top(A, B, Y, Z);").replace(
        "output Y;", "output Y, Z;\nassign Z = 1'b0;")


@pytest.mark.parametrize("edit", [
    lambda text: text.replace("assign Z = 1'b0;", "assign Z = 1'b1;"),
    lambda text: text.replace("assign Z = 1'b0;", "assign Z = A;"),
    lambda text: text.replace("assign Z = 1'b0;", ""),
    lambda text: text.replace("input A, B;", "input A;\noutput B;"),
    lambda text: text.replace("top(A, B, Y, Z)", "top(B, A, Y, Z)"),
    lambda text: text.replace("endmodule", "dff seq1 (.CK(A), .D(B), .Q(Z));\nendmodule"),
])
def test_local_f1_rejects_changes_outside_rgb_cells(edit):
    before = _constant_output()
    result = rw.build_real_equivalence_checker(LIB)(before, edit(before))
    assert result.status == "fail", result


def test_local_f1_identical_constants_and_legal_buffer_still_pass(tmp_path):
    ev = _evaluator(tmp_path, n=2, enable_buffer=True)
    before = _constant_output()
    check = rw.build_real_equivalence_checker(LIB)
    assert check(before, before).status == "pass"
    after = ev._apply(before, "g2", "B", "buf:sky130_fd_sc_hd__buf_1:B:new_B", {})
    assert check(before, after).status == "pass"


@pytest.mark.parametrize("old_wire,new_wire", [
    ("wire n1;", "wire n1, new_wire;"),
    ("wire n1, n2;", "wire n2;\nwire n1;\nwire new_wire;"),
    ("wire [3:0] n1, n2;", "wire [3:0] n2;\nwire [3:0] n1, new_wire;"),
    ("wire signed [3:0] n1;", "wire signed [3:0] n1, new_wire;"),
    ("wire unsigned [3:0] n1;", "wire [3:0] n1, new_wire;"),
    ("wire [W-1:0] n1;", "wire [ W - 1 : 0 ] n1, new_wire;"),
])
def test_local_f1_allows_wire_regrouping_with_same_net_types(old_wire, new_wire):
    before = _chain(2).replace("wire n1;", old_wire)
    after = before.replace(old_wire, new_wire)
    result = rw.build_real_equivalence_checker(LIB)(before, after)
    assert result.status == "pass", result


@pytest.mark.parametrize("old_wire,new_wire", [
    ("wire n1;", "wire [1:0] n1;"),
    ("wire [3:0] n1;", "wire [7:0] n1;"),
    ("wire [3:0] n1;", "wire [0:3] n1;"),
    ("wire signed [3:0] n1;", "wire [3:0] n1;"),
    ("wire [3:0] n1;", "wire signed [3:0] n1;"),
    ("wire [3:0] n1, n2;", "wire [3:0] n1;\nwire [7:0] n2;"),
    ("wire n1;", "wire new_wire;"),
    ("wire n1;", "wire n1;\nwire [7:0] n1;"),
    ("wire n1 [3:0];", "wire n1 [7:0];"),
])
def test_local_f1_rejects_existing_wire_type_or_identity_changes(old_wire, new_wire):
    before = _chain(2).replace("wire n1;", old_wire)
    after = before.replace(old_wire, new_wire)
    result = rw.build_real_equivalence_checker(LIB)(before, after)
    assert result.status == "fail", result


@pytest.mark.parametrize("second_carry", ["A | B", "A & B"])
def test_multioutput_function_gate_checks_every_output(second_carry):
    lib = "\n".join(
        f'cell ("sky130_fd_sc_hd__adder_{size}") {{ '
        'pin ("A") { direction : "input"; } '
        'pin ("B") { direction : "input"; } '
        f'pin ("COUT") {{ direction : "output"; function : "{carry}"; }} '
        'pin ("SUM") { direction : "output"; function : "A ^ B"; } }'
        for size, carry in ((1, "A & B"), (2, second_carry)))
    text = """module top(A, B, Y, Z);
input A, B;
output Y, Z;
sky130_fd_sc_hd__adder_1 add (.A(A), .B(B), .COUT(Y), .SUM(Z));
endmodule
"""
    after = text.replace("adder_1", "adder_2")
    result = rw.build_real_equivalence_checker(lib)(text, after)
    assert result.status == ("pass" if second_carry == "A & B" else "fail"), result


def test_multioutput_rewrite_availability_excludes_last_output_only_matches(tmp_path):
    lib = "\n".join(
        f'cell ("sky130_fd_sc_hd__{family}_1") {{ '
        'pin ("A") { direction : "input"; } '
        'pin ("B") { direction : "input"; } '
        f'pin ("COUT") {{ direction : "output"; function : "{carry}"; }} '
        'pin ("SUM") { direction : "output"; function : "A ^ B"; } }'
        for family, carry in (("adder", "A & B"), ("other", "A | B")))
    text = """module top(A, B, Y, Z);
input A, B;
output Y, Z;
sky130_fd_sc_hd__adder_1 add (.A(A), .B(B), .COUT(Y), .SUM(Z));
endmodule
"""
    assert rw.build_r_available(lib, ["add"], text) == set()
    ev = rw.RealWnsEvaluator(mapped_text=text, top_module="top", period=1,
                            liberty_text=lib, baseline_wns=-1, output_dir=tmp_path)
    assert ev._r_candidates("sky130_fd_sc_hd__adder_1") == []


def _duplicates(wrapper=False):
    if wrapper:
        extra = "dff g1 (.CK(A), .D(B), .Q(Y));"
    else:
        extra = "sky130_fd_sc_hd__and2_1 g1 (.A(A), .B(B), .Y(Y));"
    return _chain(2).replace("endmodule", extra + "\nendmodule")


@pytest.mark.parametrize("wrapper", [False, True])
@pytest.mark.parametrize("factory", [lambda: rw.build_real_equivalence_checker(LIB),
                                     lambda: rw.build_boundary_closure_checker()])
def test_local_gates_reject_duplicate_physical_instance_names(factory, wrapper):
    text = _duplicates(wrapper)
    result = factory()(text, text)
    assert result.status == "fail", result
    assert "duplicate" in result.reason.lower(), result


@pytest.mark.parametrize("kind,new_type", [("G", "sky130_fd_sc_hd__and2_2"),
                                         ("R", "sky130_fd_sc_hd__andx_1"),
                                         ("B", "buf:sky130_fd_sc_hd__buf_1:B:new_B")])
def test_actions_reject_duplicate_physical_instances(tmp_path, kind, new_type):
    ev = _evaluator(tmp_path, n=2)
    with pytest.raises(ValueError, match="[Dd]uplicate"):
        ev._apply(_duplicates(), "g1", kind, new_type, {})


def test_joint_action_rejects_duplicate_physical_instances(tmp_path):
    ev = _evaluator(tmp_path, n=2)
    with pytest.raises(ValueError, match="[Dd]uplicate"):
        ev._apply_joint(_duplicates(), {"g1": ("sky130_fd_sc_hd__and2_2", {}, "G")})


def test_evaluator_rejects_duplicates_before_sta_or_action_dict(tmp_path, monkeypatch):
    ev = _evaluator(tmp_path, n=2)
    ev.mapped_text = _duplicates()
    monkeypatch.setattr(rw, "run_opensta_sequential", lambda **kw: pytest.fail("STA forbidden"))
    with pytest.raises(ValueError, match="[Dd]uplicate"):
        ev(_patch(["g1"]), None)


def _conb_top():
    return """module top(A, Y, Z);
input A;
output Y, Z;
wire H, L;
sky130_fd_sc_hd__conb_1 tie (.HI(H), .LO(L));
sky130_fd_sc_hd__buf_1 g1 (.A(H), .X(Y));
sky130_fd_sc_hd__buf_1 g2 (.A(L), .X(Z));
endmodule
"""


def test_f2_uses_liberty_outputs_and_constants_for_legal_conb_identity(sky_lib):
    text = _conb_top()
    result = rw.build_boundary_closure_checker(liberty_text=sky_lib)(text, text)
    assert result.status == "pass", result


def test_f2_counts_additional_output_drivers_and_not_as_inputs(sky_lib):
    text = """module top(A, B, C, Y, Z);
input A, B, C;
output Y, Z;
wire carry;
sky130_fd_sc_hd__fa_1 adder (.A(A), .B(B), .CIN(C), .COUT(carry), .SUM(Y));
sky130_fd_sc_hd__buf_1 g1 (.A(carry), .X(Z));
endmodule
"""
    check = rw.build_boundary_closure_checker(liberty_text=sky_lib)
    assert check(text, text).status == "pass"
    bad = text.replace("endmodule", "sky130_fd_sc_hd__buf_1 duplicate (.A(A), .X(carry));\nendmodule")
    result = check(text, bad)
    assert result.status == "fail"
    assert "multiple-driver" in result.reason


def test_f2_constant_alias_does_not_hide_duplicate_physical_driver(sky_lib):
    text = _conb_top()
    bad = text.replace("endmodule", "sky130_fd_sc_hd__buf_1 extra (.A(A), .X(H));\nendmodule")
    result = rw.build_boundary_closure_checker(liberty_text=sky_lib)(text, bad)
    assert result.status == "fail", result
    assert "multiple-driver" in result.reason


def test_f2_distinct_constant_outputs_do_not_become_shared_physical_driver(sky_lib):
    text = _conb_top().replace("wire H, L;", "wire H, L, H2, L2;").replace(
        "endmodule", "sky130_fd_sc_hd__conb_1 tie2 (.HI(H2), .LO(L2));\nendmodule")
    result = rw.build_boundary_closure_checker(liberty_text=sky_lib)(text, text)
    assert result.status == "pass", result


def test_f3_uses_physical_count_with_multioutput_and_wrapper(tmp_path, sky_lib, monkeypatch):
    top = _conb_top().replace("endmodule", "dff seq1 (.CK(A), .D(A), .Q(Q));\nendmodule")
    top = top.replace("wire H, L;", "wire H, L, Q;").replace("output Y, Z;", "output Y, Z, Q;")
    ev = rw.RealWnsEvaluator(mapped_text=top, top_module="top", period=1,
                            liberty_text=sky_lib, baseline_wns=-1, output_dir=tmp_path,
                            strict_gates=True, max_patch_ratio=0.24,
                            equivalence_checker=rw.build_real_equivalence_checker(sky_lib),
                            boundary_checker=rw.build_boundary_closure_checker(liberty_text=sky_lib))
    monkeypatch.setattr(rw, "run_opensta_sequential", lambda **kw: {"wns": -0.5, "tns": -1})
    job = ("g1", "sky130_fd_sc_hd__buf_1", "sky130_fd_sc_hd__buf_2", {}, "G",
           top, tmp_path, "top", 0, {})
    result = ev._eval_one(job)
    f3 = [event for event in result["failure_events"] if event["type"] == "F3_patch_too_large"]
    assert f3 and f3[0]["evidence"]["gate_count"] == 4
    assert f3[0]["observed_value"]["value"] == pytest.approx(1 / 4)
