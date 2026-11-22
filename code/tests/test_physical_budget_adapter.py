"""Unit tests for the online physical evaluator adapter."""
from pathlib import Path

from rseco.budgeted_recovery import BudgetPolicy, Endpoint, bounded_search
from rseco.physical_budget_adapter import (
    DEFAULT_LIBERTY,
    PhysicalAction,
    PhysicalEvaluator,
    adaptive_batch_recovery,
    compute_mapped_area,
    generate_compatible_candidates,
    load_actions_from_space_audit,
    parse_sta_log,
    render_physical_flow_tcl,
    render_propagated_sta_tcl,
)


def test_compute_mapped_area_includes_escaped_identifiers(tmp_path: Path):
    v = tmp_path / "net.v"
    v.write_text(
        "module top(input clk, input a, output y);\n"
        "  sky130_fd_sc_hd__tapvpwrvgnd_1 tap_0 ();\n"
        "  sky130_fd_sc_hd__nor4_1 _096_ (.Y(y));\n"
        "  sky130_fd_sc_hd__dfxtp_2 \\dff_reg[0] (.CLK(clk), .D(a), .Q(y));\n"
        "endmodule\n",
        encoding="utf-8",
    )
    areas = {
        "sky130_fd_sc_hd__nor4_1": 6.256,
        "sky130_fd_sc_hd__dfxtp_2": 21.2704,
    }
    assert compute_mapped_area(v, areas) == 27.5264


def test_render_physical_flow_tcl_quotes_hierarchical_instances(tmp_path: Path):
    tcl = render_physical_flow_tcl(
        odb_path=tmp_path / "in.odb",
        spef_path=tmp_path / "in.spef",
        out_dir=tmp_path / "out",
        top_module="s382",
        period=0.5,
        clk_port="CK",
        replacements=[("DFF_0/_0_", "sky130_fd_sc_hd__dfxtp_1"), ("_096_", "sky130_fd_sc_hd__nor4_1")],
    )
    assert "replace_cell {DFF_0/_0_} {sky130_fd_sc_hd__dfxtp_1}" in tcl
    assert "replace_cell {_096_} {sky130_fd_sc_hd__nor4_1}" in tcl
    assert "PHYSICAL_PROBE_OK" in tcl


def test_parse_sta_log_extracts_all_metrics():
    log = (
        "ROUTED_WNS_MAX -8.51556880565596e-10\n"
        "ROUTED_WNS_MIN 4.6721415625228246e-10\n"
        "tns max -13.654525\n"
    )
    m = parse_sta_log(log)
    assert abs(m["setup_ns"] - (-0.851556880565596)) < 1e-12
    assert abs(m["hold_ns"] - 0.46721415625228246) < 1e-12
    assert m["tns_ns"] == -13.654525


def test_physical_evaluator_integrates_with_bounded_search(tmp_path: Path):
    actions = [
        PhysicalAction("a1", "_096_", "sky130_fd_sc_hd__nor4_2", "sky130_fd_sc_hd__nor4_1", 6.256),
        PhysicalAction("a2", "_057_", "sky130_fd_sc_hd__o31a_2", "sky130_fd_sc_hd__o31a_1", 3.7536),
    ]
    ref = Endpoint("CONTROL", 100.0, -0.85, -13.4, 0.46, "scope1", "ref", valid=True, sec_pass=True)

    def fake_runner(argv: list[str], logfile: Path, timeout_s: int) -> int:
        out_dir = logfile.parent
        if "openroad" in argv[4]:
            logfile.write_text("PHYSICAL_PROBE_OK\n", encoding="utf-8")
            (out_dir / "drc.rpt").write_text("", encoding="utf-8")
            (out_dir / "routed.spef").write_text("*SPEF\n", encoding="utf-8")
            flow_tcl = (out_dir / "flow.tcl").read_text(encoding="utf-8")
            if "_096_" in flow_tcl and "_057_" in flow_tcl:
                (out_dir / "routed.v").write_text("module s382; sky130_fd_sc_hd__nor4_1 _096_ (); endmodule\n", encoding="utf-8")
            else:
                (out_dir / "routed.v").write_text("module s382; sky130_fd_sc_hd__nor4_2 _096_ (); endmodule\n", encoding="utf-8")
            return 0
        # standalone sta
        flow_tcl = (out_dir / "flow.tcl").read_text(encoding="utf-8")
        if "_096_" in flow_tcl and "_057_" in flow_tcl:
            logfile.write_text("ROUTED_WNS_MAX -8.55e-10\nROUTED_WNS_MIN 4.65e-10\ntns max -13.5\n", encoding="utf-8")
        else:
            logfile.write_text("ROUTED_WNS_MAX -8.52e-10\nROUTED_WNS_MIN 4.65e-10\ntns max -13.5\n", encoding="utf-8")
        return 0

    evaluator = PhysicalEvaluator(
        odb_path=tmp_path / "control.odb",
        spef_path=tmp_path / "control.spef",
        top_module="s382",
        period=0.5,
        clk_port="CK",
        scope_id="scope1",
        areas={"sky130_fd_sc_hd__nor4_1": 90.0, "sky130_fd_sc_hd__nor4_2": 95.0},
        actions=actions,
        work_dir=tmp_path / "work",
        runner=fake_runner,
    )
    res = bounded_search(
        ref,
        [a.to_action() for a in actions],
        evaluator,
        BudgetPolicy.from_ps(10.0),
        max_evaluations=5,
        beam_width=2,
        max_depth=2,
        require_sec=False,
    )
    assert res.selected.valid is True
    assert res.selected.area == 90.0
    assert evaluator.eval_count == 3


def test_load_actions_from_real_space_audit_if_present():
    audit = Path("project_docs/evidence/strict_area_search_20261113/space_audit/SPACE_AUDIT.json")
    if audit.exists():
        actions = load_actions_from_space_audit(audit)
        assert len(actions) == 36


def test_generate_compatible_candidates_tool_agnostic(tmp_path: Path):
    if not DEFAULT_LIBERTY.exists():
        return
    net = tmp_path / "routed.v"
    net.write_text(
        "module tiny(input clk, input a, input b, output y);\n"
        "  sky130_fd_sc_hd__tapvpwrvgnd_1 tap_0 ();\n"
        "  sky130_fd_sc_hd__nor4_2 _096_ (.A(a), .B(b), .C(a), .D(b), .Y(y));\n"
        "  sky130_fd_sc_hd__buf_6 rebuffer1 (.A(a), .X(y));\n"
        "  sky130_fd_sc_hd__dfxtp_4 \\dff_reg[0] (.CLK(clk), .D(a), .Q(y));\n"
        "endmodule\n",
        encoding="utf-8",
    )
    comb = generate_compatible_candidates(net, categories=("combinational_other",))
    assert any(a.instance == "_096_" and a.target_cell == "sky130_fd_sc_hd__nor4_1" for a in comb)
    assert any(a.instance == "rebuffer1" and a.target_cell == "sky130_fd_sc_hd__buf_1" for a in comb)
    assert all(a.category == "combinational_other" for a in comb)

    all_cats = generate_compatible_candidates(net, categories=("combinational_other", "sequential"))
    assert any(a.instance == "\\dff_reg[0]" and a.target_cell == "sky130_fd_sc_hd__dfxtp_1" for a in all_cats)


def test_render_propagated_sta_tcl_injects_extra_io_ocv(tmp_path: Path):
    tcl = render_propagated_sta_tcl(
        netlist_path=tmp_path / "routed.v",
        spef_path=tmp_path / "routed.spef",
        top_module="s713",
        period=0.5,
        clk_port="CK",
        extra_sta_tcl="set_timing_derate -early 0.90\nset_timing_derate -late 1.10",
    )
    assert "set_propagated_clock [all_clocks]" in tcl
    assert "set_timing_derate -early 0.90" in tcl
    assert "set_timing_derate -late 1.10" in tcl


def test_generate_compatible_candidates_skips_lpflow_and_clkload(tmp_path: Path):
    if not DEFAULT_LIBERTY.exists():
        return
    net = tmp_path / "routed.v"
    net.write_text(
        "module tiny(input clk, input a, output y);\n"
        "  sky130_fd_sc_hd__buf_6 rebuffer1 (.A(a), .X(y));\n"
        "  sky130_fd_sc_hd__bufinv_16 clkload0 (.A(clk), .Y(y));\n"
        "  sky130_fd_sc_hd__lpflow_isobufsrc_4 iso0 (.A(a), .SLEEP(clk), .X(y));\n"
        "endmodule\n",
        encoding="utf-8",
    )
    comb = generate_compatible_candidates(net, one_per_instance=True)
    assert all(not a.instance.startswith("clkload") for a in comb)
    assert all("lpflow_" not in a.target_cell and "lpflow_" not in a.source_cell for a in comb)
    assert len([a for a in comb if a.instance == "rebuffer1"]) == 1


def test_adaptive_batch_recovery_commits_batch_and_bisects_tipping_gate():
    ref = Endpoint("CONTROL", 1000.0, -0.500, -10.0, 0.400, "s", "ref", True, True)
    actions = [
        PhysicalAction("g1=c1", "g1", "c4", "c1", 10.0),
        PhysicalAction("g2=c1", "g2", "c4", "c1", 9.0),
        PhysicalAction("g3_bad=c1", "g3", "c4", "c1", 8.0),
        PhysicalAction("g4=c1", "g4", "c4", "c1", 7.0),
    ]
    saving_map = {a.action_id: a.estimated_area_saving for a in actions}

    def fake_eval(aids: tuple[str, ...]) -> Endpoint:
        area = 1000.0 - sum(saving_map[x] for x in aids)
        wns = -0.550 if "g3_bad=c1" in aids else -0.502
        return Endpoint("+".join(aids), area, wns, -10.0, 0.400, "s", "ev", True, False)

    res = adaptive_batch_recovery(
        ref,
        actions,
        fake_eval,
        BudgetPolicy.from_ps(10.0),
        max_evaluations=6,
        batch_size=2,
    )
    assert res["committed"] == ["g1=c1", "g2=c1", "g4=c1"]
    assert res["selected"].area == 1000.0 - 26.0
    assert res["evaluations_used"] == 4


def test_generate_compatible_candidates_safe_drive_first(tmp_path: Path):
    if not DEFAULT_LIBERTY.exists():
        return
    net = tmp_path / "routed.v"
    net.write_text(
        "module tiny(input a, input b, input c, input d, output y1, output y2);\n"
        "  sky130_fd_sc_hd__o21ai_4 g0 (.A1(a), .A2(b), .B1(c), .Y(y1));\n"
        "  sky130_fd_sc_hd__buf_8 g1 (.A(d), .X(y2));\n"
        "endmodule\n",
        encoding="utf-8",
    )
    cands = generate_compatible_candidates(
        net,
        one_per_instance=True,
        deprioritize_zero_drive=True,
    )
    assert cands[0].instance == "g1"
    assert not cands[0].target_cell.endswith("_0")
