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

TRISTATE_LIB = LIB + '\n' + '\n'.join(
    f'cell ("sky130_fd_sc_hd__einvn_{size}") {{ '
    'pin ("A") { direction : "input"; } '
    'pin ("TE_B") { direction : "input"; } '
    'pin ("Z") { direction : "output"; function : "(!A)"; '
    f'three_state : "{enable}"; }} }}'
    for size, enable in ((1, "(TE_B)"), (2, "(TE_B)"), (3, "(!TE_B)")))
TRISTATE_LIB += '\ncell ("sky130_fd_sc_hd__inv_1") { '
TRISTATE_LIB += ('pin ("A") { direction : "input"; } '
                 'pin ("Y") { direction : "output"; function : "(!A)"; } }')


def _tristate_top(ports=".A(A), .TE_B(EN), .Z(Y)", cell_type="einvn_1"):
    return ("module top(A,EN,Y);\ninput A, EN;\noutput Y;\n"
            f"sky130_fd_sc_hd__{cell_type} g ({ports});\nendmodule\n")


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


def test_real_tristate_model_keeps_high_impedance_enable(tmp_path, sky_lib):
    text = rw.write_liberty_cell_models(
        sky_lib, tmp_path / "tristate.v", used_cells={"sky130_fd_sc_hd__einvn_1"}).read_text()
    assert re.search(r"assign Z\s*=\s*\(\(TE_B\)\)\s*\?\s*1'bz\s*:\s*\(\(!A\)\);", text), text


@pytest.mark.parametrize("size", [1, 2, 4, 8])
def test_actual_einvp_postfix_inversion_exports_valid_enable_expression(tmp_path, sky_lib, size):
    text = rw.write_liberty_cell_models(sky_lib, tmp_path / f"einvp_{size}.v",
        used_cells={f"sky130_fd_sc_hd__einvp_{size}"}).read_text()
    assert "TE'" not in text, text
    expression = re.search(r"assign Z = (.*?) \? 1'bz :", text).group(1)
    for te in (0, 1):
        assert eval(expression, {"__builtins__": {}}, {"TE": te}) & 1 == 1 - te


@pytest.mark.parametrize("expression,expected", [
    ("A'", lambda a, b: 1-a),
    ("(A&B)'", lambda a, b: 1-(a&b)),
    ("(A^B)''", lambda a, b: a^b),
    ("!(A'|B)", lambda a, b: 1-((1-a)|b)),
])
def test_liberty_postfix_converter_preserves_boolean_semantics(expression, expected):
    converted = rw.liberty_expression_to_verilog(expression)
    assert "'" not in converted
    for a in (0, 1):
        for b in (0, 1):
            assert eval(converted, {"__builtins__": {}}, {"A": a, "B": b}) & 1 == expected(a, b)


@pytest.mark.parametrize("expression", ["A ? B : C", "A@B", "(A&B", "A B"])
def test_liberty_expression_unknown_syntax_fails_closed(expression):
    with pytest.raises(ValueError, match="(?i)Liberty.*expression|unsupported.*syntax"):
        rw.liberty_expression_to_verilog(expression)


def test_postfix_in_sequential_fields_uses_shared_conversion(tmp_path):
    lib = '''cell ("sky130_fd_sc_hd__custom_1") {
      pin ("CLK") { direction : "input"; }
      pin ("D") { direction : "input"; }
      pin ("RESET") { direction : "input"; }
      pin ("Q") { direction : "output"; function : "IQ"; }
      ff ("IQ", "IQ_N") {
        next_state : "D'"; clocked_on : "CLK'"; clear : "RESET'";
      }
    }'''
    text = rw.write_liberty_cell_models(lib, tmp_path / "seq.v").read_text()
    assert "D'" not in text and "CLK'" not in text and "RESET'" not in text
    assert "~(D)" in text and "~(CLK)" in text and "~(RESET)" in text


def test_abc_model_rejects_tristate_semantics_instead_of_two_state_downgrade(tmp_path, sky_lib):
    with pytest.raises(ValueError, match="(?i)ABC.*three.state|three.state.*ABC"):
        rw.write_liberty_cell_models(sky_lib, tmp_path / "abc.v",
            used_cells={"sky130_fd_sc_hd__einvn_1"}, abc_compatible=True)


@pytest.mark.parametrize("ports", [".A(A), .Z(Y)", ".A(A), .TE_B(), .Z(Y)",
                                  ".A(), .TE_B(EN), .Z(Y)"])
@pytest.mark.parametrize("factory", [lambda: rw.build_real_equivalence_checker(TRISTATE_LIB),
                                     lambda: rw.build_boundary_closure_checker(liberty_text=TRISTATE_LIB)])
def test_local_gates_reject_missing_or_empty_actual_required_inputs(ports, factory):
    text = _tristate_top(ports)
    result = factory()(text, text)
    assert result.status == "fail", result
    assert "input" in result.reason.lower(), result


@pytest.mark.parametrize("pin", ["A", "B"])
def test_f2_required_input_gate_covers_ordinary_cells_too(pin):
    text = _chain(2)
    cell_text = "sky130_fd_sc_hd__and2_1 g1 (.A(A), .B(B), .Y(n1));"
    bad_cell = cell_text.replace(f".{pin}({pin}), ", "")
    bad = text.replace(cell_text, bad_cell)
    result = rw.build_boundary_closure_checker(liberty_text=LIB)(bad, bad)
    assert result.status == "fail", result
    assert "input" in result.reason.lower(), result


def test_f1_rejects_changed_tristate_enable_semantics():
    text = _tristate_top()
    result = rw.build_real_equivalence_checker(TRISTATE_LIB)(text, text.replace("einvn_1", "einvn_3"))
    assert result.status == "fail", result


def test_f1_rejects_plain_inverter_to_tristate_without_enable():
    before = _tristate_top(".A(A), .Y(Y)", "inv_1")
    after = _tristate_top(".A(A), .Z(Y)", "einvn_1")
    assert rw.build_real_equivalence_checker(TRISTATE_LIB)(before, after).status == "fail"


def test_legal_tristate_identity_and_same_semantics_size_change_are_supported():
    text = _tristate_top()
    for check in (rw.build_real_equivalence_checker(TRISTATE_LIB),
                  rw.build_boundary_closure_checker(liberty_text=TRISTATE_LIB)):
        assert check(text, text).status == "pass"
        assert check(text, text.replace("einvn_1", "einvn_2")).status == "pass"


def test_tristate_control_net_change_is_rejected():
    text = _tristate_top()
    result = rw.build_real_equivalence_checker(TRISTATE_LIB)(text, text.replace(".TE_B(EN)", ".TE_B(A)"))
    assert result.status == "fail"


def test_public_required_input_validator_checks_helpers_and_allows_unused_outputs():
    lib = parse_liberty_cells(TRISTATE_LIB)
    helper = _tristate_top(".A(A), .TE_B(EN), .Z()") .replace("module top", "module helper")
    top = _tristate_top()
    assert rw.validate_cell_input_connections(helper + top, lib) is None
    with pytest.raises(ValueError, match="(?i)input.*TE_B|TE_B.*input"):
        rw.validate_cell_input_connections(helper.replace(".TE_B(EN), ", "") + top, lib)


def test_required_input_validator_does_not_silently_skip_unsupported_sky_instance_names():
    text = _tristate_top(".A(), .TE_B(EN), .Z(Y)").replace(" g (", " \\escaped.g (")
    with pytest.raises(ValueError, match="(?i)unsupported.*instance|input"):
        rw.validate_cell_input_connections(text, parse_liberty_cells(TRISTATE_LIB))


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
