from types import SimpleNamespace
from pathlib import Path
import sys
import shutil

from rseco.real_wns import (
    RealWnsEvaluator, build_boundary_closure_checker,
    build_real_equivalence_checker, build_full_netlist_sec_checker,
)
from rseco.replacement import (
    check_local_functional_equivalence, extract_combinational_window,
    generate_topology_replacement, parse_verilog_netlist_from_text,
    stitch_topology_replacement,
    run_full_netlist_sec_checkpoint,
)
from rseco.equivalence import EquivalenceResult
from rseco.flow import run_multi_iteration_case
import rseco.flow as flow_module
from rseco.cut import FaninCone, constrained_weighted_cut_candidates
import time
from rseco.refinement_loop import SearchState
from rseco.yosys_abc import check_yosys_abc_equivalence


LIB = """cell (\"sky130_fd_sc_hd__and2_1\") { pin (\"A\") { direction : \"input\"; } pin (\"B\") { direction : \"input\"; } pin (\"Y\") { direction : \"output\"; function : \"A & B\"; } }
cell (\"sky130_fd_sc_hd__and2_2\") { pin (\"A\") { direction : \"input\"; } pin (\"B\") { direction : \"input\"; } pin (\"Y\") { direction : \"output\"; function : \"A & B\"; } }
cell (\"sky130_fd_sc_hd__or2_1\") { pin (\"A\") { direction : \"input\"; } pin (\"B\") { direction : \"input\"; } pin (\"Y\") { direction : \"output\"; function : \"A | B\"; } }
"""
SEQ_LIB = LIB + """cell (\"sky130_fd_sc_hd__dfxtp_1\") {
  pin (\"D\") { direction : \"input\"; }
  pin (\"CLK\") { direction : \"input\"; }
  pin (\"Q\") { direction : \"output\"; }
  ff (IQ, IQ_N) { next_state : \"D\"; clocked_on : \"CLK\"; }
}
"""
SEQ_BASE = """module top(D, CLK, Q);
input D, CLK;
output Q;
sky130_fd_sc_hd__dfxtp_1 ff1 (.D(D), .CLK(CLK), .Q(Q));
endmodule
"""
BASE = """module top(A, B, Y);
input A, B;
output Y;
sky130_fd_sc_hd__and2_1 g1 (.A(A), .B(B), .Y(Y));
endmodule
"""
net_for_stop = """module top(A, Y);
input A;
output Y;
wire N1;
buf g1 (N1, A);
buf g2 (Y, N1);
endmodule
"""


def test_default_strict_budget_only_requires_measurable_setup_metrics(tmp_path, monkeypatch):
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1, baseline_tns=-2,
                          output_dir=tmp_path, workers=1, strict_gates=True,
                          strict_budgets=True, max_patch_ratio=1.0,
                          equivalence_checker=lambda a, b: True,
                          boundary_checker=lambda a, b: True)
    ev._candidates_for = lambda cells, inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, inst, kind, new, pin: text.replace("and2_1", "and2_2")
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kwargs: {"wns": -.5, "tns": -1})
    patch = SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"])
    assert ev(patch, None)["improved"] is True


def test_explicit_required_area_fails_closed_before_sta(tmp_path, monkeypatch):
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1, baseline_tns=-2,
                          output_dir=tmp_path, workers=1, strict_gates=True,
                          strict_budgets=True, required_metrics=("setup_wns", "setup_tns", "area"),
                          equivalence_checker=lambda a, b: True,
                          boundary_checker=lambda a, b: True)
    ev._candidates_for = lambda cells, inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, inst, kind, new, pin: text.replace("and2_1", "and2_2")
    calls = []
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kwargs: (calls.append(kwargs) or {"wns": -.5, "tns": -1}))
    patch = SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"])
    result = ev(patch, None)
    assert result["improved"] is False
    assert calls == []
    assert any(e["type"] == "acceptance_budget_unavailable"
               for trial in ev.trials for e in trial["failure_events"])


def test_real_f1_rejects_pin_to_net_swap():
    checker = build_real_equivalence_checker(LIB)
    swapped = BASE.replace(".B(B)", ".B(A)").replace(".A(A)", ".A(B)")
    assert checker(BASE, swapped).status == "fail"


def test_real_f2_rejects_broken_output_driver():
    checker = build_boundary_closure_checker()
    broken = BASE.replace(".Y(Y)", ".Y(N_BROKEN)")
    assert checker(BASE, broken).status == "fail"


def test_named_pin_topology_stitch_preserves_real_pin_names():
    text = """module top(A, B, Y);
input A, B;
output Y;
wire N1, N2;
sky130_fd_sc_hd__and2_1 g1 (.A(A), .B(B), .Y(N1));
sky130_fd_sc_hd__and2_1 g2 (.A(A), .B(B), .Y(N2));
sky130_fd_sc_hd__or2_1 g3 (.A(N1), .B(N2), .Y(Y));
endmodule
"""
    netlist = parse_verilog_netlist_from_text(text)
    replacement = generate_topology_replacement(
        extract_combinational_window(netlist, ["g1", "g2", "g3"])
    )
    stitched = stitch_topology_replacement(text, replacement)
    assert ".A(A)" in stitched and ".B(B)" in stitched and ".Y(Y)" in stitched
    assert "sky130_fd_sc_hd__and2_1 g1 (" in stitched
    assert check_local_functional_equivalence(
        extract_combinational_window(netlist, ["g1", "g2", "g3"]), stitched
    ).status == "pass"
    assert run_full_netlist_sec_checkpoint(text, stitched).status == "unavailable"


def test_flow_recomputes_critical_path_for_second_cut(tmp_path, monkeypatch):
    case_dir = tmp_path / "case"
    (case_dir / "original").mkdir(parents=True)
    (case_dir / "resynthesized").mkdir(parents=True)
    net = """module top(A, Y);
input A;
output Y;
wire N1;
buf g1 (N1, A);
buf g2 (Y, N1);
endmodule
"""
    (case_dir / "original" / "original.v").write_text(net)
    (case_dir / "resynthesized" / "resynthesized.v").write_text(net)
    (case_dir / "case.yaml").write_text("case_id: dyn\ntarget:\n  output: Y\n")
    seen = []
    original_candidates = flow_module._cone_candidates

    def capture(cone, weights, critical, available, **kwargs):
        seen.append(list(critical))
        return original_candidates(cone, weights, critical, available, **kwargs)

    monkeypatch.setattr(flow_module, "_cone_candidates", capture)

    class Evaluator:
        use_constrained_cuts = False
        refresh_cone = False
        strict_gates = False
        boundary_checker = object()
        critical_instances = ["g2"]
        def __call__(self, patch, weights, *, state):
            n = len(state.accepted_patches) + 1
            return {"wns": -.8 + n * .1, "tns": -1,
                    "improved": True, "candidate_netlist_text": net + f"// G{n}\n",
                    "critical_instances": ["g1"] if n == 1 else ["g2"]}

    result = run_multi_iteration_case(
        case_dir, max_iterations=3, max_patches=2,
        equivalence_checker=lambda *a, **k: EquivalenceResult("pass", "test", "ok"),
        wns_evaluator=Evaluator(), critical_instances=["g2"],
    )
    assert result["success"] is True
    assert len(result["state"]["accepted_patches"]) == 2
    assert seen[0] == ["g2"]
    assert seen[1] == ["g1"]


def test_flow_roundtrips_optional_physical_hold_none(tmp_path):
    import json
    case_dir = tmp_path / "optional-none"
    (case_dir / "original").mkdir(parents=True)
    (case_dir / "resynthesized").mkdir(parents=True)
    net = "module top(A, Y);\ninput A;\noutput Y;\nbuf g1 (Y, A);\nendmodule\n"
    (case_dir / "original" / "original.v").write_text(net)
    (case_dir / "resynthesized" / "resynthesized.v").write_text(net)
    (case_dir / "case.yaml").write_text("case_id: optional-none\ntarget:\n  output: Y\n")

    class Evaluator:
        use_constrained_cuts = False
        refresh_cone = False
        strict_gates = False
        boundary_checker = object()
        critical_instances = ["g1"]
        def __call__(self, patch, weights, *, state):
            return {"wns": -.8, "tns": None, "min_slack": None,
                    "improved": True, "candidate_netlist_text": net,
                    "candidate_hash": "optional-none-hash",
                    "physical_baseline": -1.2, "physical_candidate": -1.1,
                    "physical_baseline_tns": None, "physical_candidate_tns": None,
                    "physical_baseline_min_slack": None,
                    "physical_candidate_min_slack": None,
                    "physical_status": "paired_improved",
                    "failure_events": []}

    result = run_multi_iteration_case(
        case_dir, max_iterations=1, max_patches=1,
        equivalence_checker=lambda *a, **k: EquivalenceResult("pass", "test", "ok"),
        wns_evaluator=Evaluator(), critical_instances=["g1"],
    )
    assert result["min_slack"] is None
    record = result["state"]["accepted_patches"][0]
    assert record["min_slack"] is None
    assert record["metadata"]["physical_metrics"]["candidate_hold"] is None
    assert json.loads(json.dumps(result["state"]))["accepted_patches"][0]["min_slack"] is None


def test_physical_acceptance_uses_paired_baseline_not_ideal_baseline(tmp_path, monkeypatch):
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-.9,
                          output_dir=tmp_path, workers=1, physical_gate=True,
                          min_physical_gain_ns=0.01)
    ev._candidates_for = lambda cells, inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, inst, kind, new, pin: text.replace("and2_1", "and2_2")

    def paired_sta(**kwargs):
        if kwargs.get("spef_path") is None:
            return {"wns": -.8, "tns": -1}
        if "physical_baseline" in str(kwargs["output_dir"]):
            return {"wns": -1.2, "tns": -2, "min_slack": -0.9}
        return {"wns": -1.1, "tns": -1.5, "min_slack": -0.8}

    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential", paired_sta)
    patch = SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"])
    result = ev(patch, None)
    assert result["improved"] is True
    assert result["wns"] == -1.1


def test_epsilon_applies_to_wns_tns_tie_break(tmp_path, monkeypatch):
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1, baseline_tns=-2,
                          output_dir=tmp_path, workers=1, tns_aware=True,
                          epsilon=0.01)
    ev._candidates_for = lambda cells, inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, inst, kind, new, pin: text.replace("and2_1", "and2_2")
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kwargs: {"wns": -.995, "tns": -1})
    patch = SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"])
    result = ev(patch, None)
    assert result["improved"] is True


def test_constrained_cut_uses_bounded_beam_and_singleton_policy():
    gates = [f"g{i}" for i in range(60)]
    inputs = {g: (["A"] if i == 0 else [f"N{i-1}"]) for i, g in enumerate(gates)}
    outputs = {g: ("Y" if i == len(gates) - 1 else f"N{i}") for i, g in enumerate(gates)}
    cone = FaninCone(roots=["Y"], boundary_inputs=["A"], boundary_outputs=["Y"],
                    internal_nets=list(outputs.values()), gates=gates,
                    gate_outputs=outputs, gate_inputs=inputs)
    weights = SimpleNamespace(boundary_penalty=1, size_penalty=1,
                              critical_coverage_reward=1,
                              verification_cost_penalty=1, physical_penalty=1)
    start = time.perf_counter()
    rows, diagnostics = constrained_weighted_cut_candidates(
        cone, weights, k=5, critical_instances=["g59"], min_critical_coverage=1,
        window_size=8, allow_singleton=False, return_diagnostics=True)
    assert time.perf_counter() - start < 1.0
    assert len(rows) == 5
    assert all(len(row.gates) > 1 for row in rows)
    assert diagnostics["algorithm"] == "bounded_beam"


def test_failure_events_have_stable_ids_and_unknown_hard_is_not_retyped():
    state = SearchState(current_netlist_text="G0")
    event = {"type": "new_unknown_failure", "candidate_hash": "c", "cut_hash": "k",
             "severity": "hard", "evidence": {"checker": "x"}}
    state.record_failure(event)
    state.record_failure(event)
    assert len(state.failure_history) == 1
    assert state.failure_history[0]["event_id"]
    assert state.failure_history[0]["type"] == "new_unknown_failure"


def test_flow_unknown_hard_event_blocks_timing_improvement(tmp_path):
    case_dir = tmp_path / "unknown-hard"
    (case_dir / "original").mkdir(parents=True)
    (case_dir / "resynthesized").mkdir(parents=True)
    (case_dir / "original" / "original.v").write_text(net_for_stop)
    (case_dir / "resynthesized" / "resynthesized.v").write_text(net_for_stop)
    (case_dir / "case.yaml").write_text("case_id: unknown\ntarget:\n  output: Y\n")

    class Eval:
        use_constrained_cuts = False
        refresh_cone = False
        strict_gates = False
        boundary_checker = object()
        critical_instances = ["g1"]

        def __call__(self, patch, weights, *, state):
            return {"wns": 0.5, "improved": True,
                    "failure_events": [{"type": "checker_unknown", "severity": "hard",
                                         "candidate_hash": "candidate", "cut_hash": "cut",
                                         "evidence": {"checker": "unavailable"}}]}

    result = run_multi_iteration_case(
        case_dir, max_iterations=1,
        equivalence_checker=lambda *a, **k: EquivalenceResult("pass", "t", "ok"),
        wns_evaluator=Eval(),
    )
    assert result["success"] is False
    assert result["state"]["accepted_patches"] == []
    assert any(event["type"] == "checker_unknown"
               for event in result["state"]["failure_history"])


def test_flow_stop_reasons_are_distinct_and_budget_counts_are_traceable(tmp_path):
    def make_case(name, net=net_for_stop):
        case_dir = tmp_path / name
        (case_dir / "original").mkdir(parents=True)
        (case_dir / "resynthesized").mkdir(parents=True)
        (case_dir / "original" / "original.v").write_text(net)
        (case_dir / "resynthesized" / "resynthesized.v").write_text(net)
        (case_dir / "case.yaml").write_text("case_id: stop\ntarget:\n  output: Y\n")
        return case_dir

    class Eval:
        use_constrained_cuts = False
        refresh_cone = False
        strict_gates = False
        boundary_checker = object()
        critical_instances = ["g1"]
        def __init__(self, mode):
            self.mode = mode
            self.trials = []
        def __call__(self, patch, weights, *, state):
            self.trials.append({"failure_events": []})
            if self.mode == "stagnation":
                return {"wns": -1, "improved": False, "failure_events": []}
            n = len(state.accepted_patches) + 1
            return {"wns": .1, "tns": -1, "improved": True,
                    "candidate_netlist_text": state.current_netlist_text + f"//{n}\n",
                    "critical_instances": ["g1"]}

    cases = {}
    for mode, kwargs in (("sta_budget", {"sta_budget": 0}),
                         ("formal_budget", {"formal_budget": 0}),
                         ("wall_timeout", {"wall_timeout_s": 0}),
                         ("max_patches", {"max_patches": 1})):
        ev = Eval("accept")
        result = run_multi_iteration_case(
            make_case(mode), max_iterations=2, equivalence_checker=lambda *a, **k: EquivalenceResult("pass", "t", "ok"),
            wns_evaluator=ev, **kwargs)
        cases[mode] = result["stop_reason"]
    cases["timing_met"] = run_multi_iteration_case(
        make_case("timing_met"), max_iterations=2, max_patches=3,
        equivalence_checker=lambda *a, **k: EquivalenceResult("pass", "t", "ok"),
        wns_evaluator=Eval("accept"))["stop_reason"]
    cases["stagnation"] = run_multi_iteration_case(
        make_case("stagnation"), max_iterations=2,
        equivalence_checker=lambda *a, **k: EquivalenceResult("pass", "t", "ok"),
        wns_evaluator=Eval("stagnation"))["stop_reason"]
    cases["no_new_candidate"] = run_multi_iteration_case(
        make_case("no_new_candidate", net="module top(A, Y);\ninput A;\noutput Y;\nassign Y = A;\nendmodule\n"),
        max_iterations=1, equivalence_checker=lambda *a, **k: EquivalenceResult("pass", "t", "ok"),
        wns_evaluator=Eval("accept"))["stop_reason"]
    assert set(cases) == {"timing_met", "no_new_candidate", "stagnation", "sta_budget",
                          "formal_budget", "wall_timeout", "max_patches"}
    assert len(set(cases.values())) == 7


def test_zero_max_patches_is_an_atomic_stop_before_any_candidate(tmp_path):
    case_dir = tmp_path / "zero-patches"
    (case_dir / "original").mkdir(parents=True)
    (case_dir / "resynthesized").mkdir(parents=True)
    (case_dir / "original" / "original.v").write_text(net_for_stop)
    (case_dir / "resynthesized" / "resynthesized.v").write_text(net_for_stop)
    (case_dir / "case.yaml").write_text("case_id: zero\ntarget:\n  output: Y\n")

    class Eval:
        use_constrained_cuts = False
        refresh_cone = False
        strict_gates = False
        boundary_checker = object()
        critical_instances = ["g1"]

        def __init__(self):
            self.calls = 0

        def __call__(self, patch, weights, *, state):
            self.calls += 1
            return {"wns": 1.0, "improved": True,
                    "candidate_netlist_text": state.current_netlist_text}

    evaluator = Eval()
    result = run_multi_iteration_case(
        case_dir, max_iterations=2, max_patches=0,
        equivalence_checker=lambda *a, **k: EquivalenceResult("pass", "test", "ok"),
        wns_evaluator=evaluator,
    )
    assert result["stop_reason"] == "max_patches"
    assert evaluator.calls == 0
    assert result["state"]["accepted_patches"] == []


TOPOLOGY_TEXT = """module top(A, B, Y);
input A, B;
output Y;
wire N1, N2;
sky130_fd_sc_hd__and2_1 g1 (.A(A), .B(B), .Y(N1));
sky130_fd_sc_hd__and2_1 g2 (.A(A), .B(B), .Y(N2));
sky130_fd_sc_hd__or2_1 g3 (.A(N1), .B(N2), .Y(Y));
endmodule
"""
TOPOLOGY_LIB = LIB + """cell ("sky130_fd_sc_hd__or2_1") {
  pin ("A") { direction : "input"; }
  pin ("B") { direction : "input"; }
  pin ("Y") { direction : "output"; function : "A | B"; }
}
"""


def _topology_patch():
    return SimpleNamespace(patch_id="topology-p", gates=["g1", "g2", "g3"],
                           boundary_inputs=["A", "B"], boundary_outputs=["Y"])


def test_topology_requires_full_netlist_sec_before_sta_and_commit(tmp_path, monkeypatch):
    ev = RealWnsEvaluator(
        mapped_text=TOPOLOGY_TEXT, top_module="top", period=1,
        liberty_text=TOPOLOGY_LIB, baseline_wns=-1, output_dir=tmp_path,
        workers=1, strict_gates=True, max_patch_ratio=1.0,
        equivalence_checker=lambda *_a, **_k: True,
        boundary_checker=lambda *_a, **_k: True,
        topology_sec_checker=None,
    )
    ev._candidates_for = lambda _cells, _inst: []
    sta_calls = []
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kwargs: (sta_calls.append(kwargs) or {"wns": -.5, "tns": -1}))
    result = ev(_topology_patch(), None)
    events = result["failure_events"]
    assert result["improved"] is False
    assert len(events) == 1
    assert events[0]["type"] == "F1_equivalence_failure"
    assert events[0]["severity"] == "hard"
    assert events[0]["evidence"]["stage"] == "full_netlist_sec"
    assert sta_calls == []


def test_topology_sec_failure_is_single_f1_and_named_pin_sec_pass_can_reach_sta(tmp_path, monkeypatch):
    sec_calls = []
    ev = RealWnsEvaluator(
        mapped_text=TOPOLOGY_TEXT, top_module="top", period=1,
        liberty_text=TOPOLOGY_LIB, baseline_wns=-1, output_dir=tmp_path,
        workers=1, strict_gates=True, max_patch_ratio=1.0,
        equivalence_checker=lambda *_a, **_k: True,
        boundary_checker=lambda *_a, **_k: True,
        topology_sec_checker=lambda before, after: sec_calls.append((before, after)) or False,
    )
    ev._candidates_for = lambda _cells, _inst: []
    sta_calls = []
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kwargs: (sta_calls.append(kwargs) or {"wns": -.5, "tns": -1}))
    failed = ev(_topology_patch(), None)
    assert len(sec_calls) == 1
    assert len(failed["failure_events"]) == 1
    assert failed["failure_events"][0]["type"] == "F1_equivalence_failure"
    assert sta_calls == []

    ev = RealWnsEvaluator(
        mapped_text=TOPOLOGY_TEXT, top_module="top", period=1,
        liberty_text=TOPOLOGY_LIB, baseline_wns=-1, output_dir=tmp_path / "pass",
        workers=1, strict_gates=True, max_patch_ratio=1.0,
        equivalence_checker=lambda *_a, **_k: True,
        boundary_checker=lambda *_a, **_k: True,
        topology_sec_checker=lambda *_a: True,
    )
    ev._candidates_for = lambda _cells, _inst: []
    passed = ev(_topology_patch(), None)
    assert passed["improved"] is True
    assert passed["kind"] == "TOPOLOGY"
    assert len(sta_calls) == 1
    assert ".A(A)" in passed["candidate_netlist_text"]
    assert ".B(B)" in passed["candidate_netlist_text"]


def test_topology_local_checker_waits_for_formal_budget_and_deadline(tmp_path, monkeypatch):
    from rseco.refinement_loop import SearchState
    import rseco.real_wns as rw
    ev = RealWnsEvaluator(
        mapped_text=TOPOLOGY_TEXT, top_module="top", period=1,
        liberty_text=TOPOLOGY_LIB, baseline_wns=-1, output_dir=tmp_path,
        workers=1, strict_gates=True, max_patch_ratio=1.0,
        topology_sec_checker=lambda *_a: True,
        boundary_checker=lambda *_a: True,
    )
    ev._candidates_for = lambda _cells, _inst: []
    local_calls = []
    monkeypatch.setattr(rw, "check_local_functional_equivalence",
                        lambda *_a: (local_calls.append(True) or EquivalenceResult("pass", "local", "ok")))
    sta_calls = []
    monkeypatch.setattr(rw, "run_opensta_sequential",
                        lambda **kwargs: (sta_calls.append(kwargs) or {"wns": -.5, "tns": -1}))
    state = SearchState(current_netlist_text=TOPOLOGY_TEXT,
                        budget={"formal_budget": 0, "sta_budget": 9})
    result = ev(_topology_patch(), None, state=state)
    assert local_calls == []
    assert sta_calls == []
    assert result["failure_events"][0]["type"] == "formal_budget_exhausted"


def test_physical_acceptance_rejects_paired_tns_regression(tmp_path, monkeypatch):
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1, baseline_tns=-2,
                          output_dir=tmp_path, workers=1, physical_gate=True,
                          min_physical_gain_ns=0.01)
    ev._candidates_for = lambda _cells, _inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, _inst, _kind, _new, _pin: text.replace("and2_1", "and2_2")

    def paired_sta(**kwargs):
        if kwargs.get("spef_path") is None:
            return {"wns": -.8, "tns": -1}
        if "physical_baseline" in str(kwargs["output_dir"]):
            return {"wns": -1.0, "tns": -2.0}
        return {"wns": -.8, "tns": -3.0}

    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential", paired_sta)
    result = ev(SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"]), None)
    assert result["improved"] is False
    assert result["physical_candidate_tns"] == -3.0
    assert any(event["type"] == "F6_physical_load_failure" for event in result["failure_events"])


def test_physical_budget_reserves_baseline_and_candidate_sta_individually(tmp_path, monkeypatch):
    from rseco.refinement_loop import SearchState
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1,
                          output_dir=tmp_path, workers=1, physical_gate=True,
                          min_physical_gain_ns=0.01)
    ev._candidates_for = lambda _cells, _inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, _inst, _kind, _new, _pin: text.replace("and2_1", "and2_2")
    sta_calls = []
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kwargs: (sta_calls.append(kwargs) or {"wns": -.5, "tns": -1}))
    state = SearchState(current_netlist_text=BASE, budget={"sta_budget": 1})
    result = ev(SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"]), None, state=state)
    assert len(sta_calls) == 1
    assert any(event["type"] == "sta_budget_exhausted" for event in result["failure_events"])


def test_physical_pair_has_three_distinct_sta_measurements_when_budget_allows(tmp_path, monkeypatch):
    from rseco.refinement_loop import SearchState
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1,
                          output_dir=tmp_path, workers=1, physical_gate=True,
                          min_physical_gain_ns=0.01)
    ev._candidates_for = lambda _cells, _inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, _inst, _kind, _new, _pin: text.replace("and2_1", "and2_2")
    sta_calls = []
    def sta(**kwargs):
        sta_calls.append(kwargs)
        if kwargs.get("spef_path") is None:
            return {"wns": -.8, "tns": -1}
        if "physical_baseline" in str(kwargs["output_dir"]):
            return {"wns": -1.0, "tns": -2.0, "min_slack": -0.9}
        return {"wns": -.8, "tns": -1, "min_slack": -0.8}
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential", sta)
    state = SearchState(current_netlist_text=BASE, budget={"sta_budget": 3})
    result = ev(SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"]), None, state=state)
    assert result["improved"] is True
    assert len(sta_calls) == 3
    assert state.budget_used("sta") == 3


def test_boundary_checker_rejects_all_consumed_net_closure_failures():
    import json
    checker = build_boundary_closure_checker()
    valid = """module top(A, Y);
input A;
output Y;
wire N;
buf g1 (.A(A), .Y(N));
buf g2 (.A(N), .Y(Y));
endmodule
"""
    cases = {
            "declared-undriven": valid.replace("wire N;", "wire N, M;").replace("buf g1 (.A(A), .Y(N));", "buf g1 (.A(M), .Y(N));"),
        "undeclared-consumed": valid.replace(".A(A), .Y(N)", ".A(NOPE), .Y(N)"),
        "multiple-driver": valid.replace("buf g2 (.A(N), .Y(Y));", "buf g2 (.A(N), .Y(Y));\nbuf g3 (.A(A), .Y(N));"),
            "dangling-output": valid.replace("wire N;", "wire N, DANGLE;").replace("buf g2 (.A(N), .Y(Y));", "buf g2 (.A(N), .Y(Y));\nbuf g3 (.A(A), .Y(DANGLE));"),
        "rewired-module-output": valid.replace(".Y(Y)", ".Y(N)"),
    }
    for label, candidate in cases.items():
        result = checker(valid, candidate)
        assert result.status == "fail", label
        assert "stage" in result.reason or "boundary" in result.reason.lower(), (label, result.reason)
        reason = json.loads(result.reason)
        assert reason["kind"] == label, (label, result.reason)


def test_boundary_checker_handles_escaped_named_nets():
    checker = build_boundary_closure_checker()
    escaped = r"""module top(\A , Y);
input \A ;
output Y;
wire N;
buf g1 (.A(\A ), .Y(N));
buf g2 (.A(N), .Y(Y));
endmodule
"""
    assert checker(escaped, escaped).status == "pass"


def test_zero_max_patches_preserves_full_baseline_state_and_tns(tmp_path):
    case_dir = tmp_path / "zero-baseline"
    (case_dir / "original").mkdir(parents=True)
    (case_dir / "resynthesized").mkdir(parents=True)
    (case_dir / "original" / "original.v").write_text(net_for_stop)
    (case_dir / "resynthesized" / "resynthesized.v").write_text(net_for_stop)
    (case_dir / "case.yaml").write_text("case_id: zero-baseline\ntarget:\n  output: Y\n")
    class Eval:
        baseline_wns = -1.0
        baseline_tns = -2.0
        baseline_min_slack = -3.0
        critical_instances = ["g1"]
        use_constrained_cuts = False
    result = run_multi_iteration_case(case_dir, max_iterations=2, max_patches=0, wns_evaluator=Eval())
    assert result["state"]["current_wns"] == -1.0
    assert result["state"]["current_tns"] == -2.0
    assert result["state"]["current_min_slack"] == -3.0
    assert result["state"]["current_netlist_text"] == net_for_stop


def test_terminal_wall_timeout_breaks_refinement_at_triggering_iteration(tmp_path):
    case_dir = tmp_path / "terminal-timeout"
    (case_dir / "original").mkdir(parents=True)
    (case_dir / "resynthesized").mkdir(parents=True)
    (case_dir / "original" / "original.v").write_text(net_for_stop)
    (case_dir / "resynthesized" / "resynthesized.v").write_text(net_for_stop)
    (case_dir / "case.yaml").write_text("case_id: terminal\ntarget:\n  output: Y\n")
    calls = []

    class Eval:
        use_constrained_cuts = False
        refresh_cone = False
        strict_gates = False
        boundary_checker = object()
        critical_instances = ["g1"]

        def __call__(self, patch, weights, *, state):
            calls.append(True)
            state.set_stop_reason("wall_timeout")
            return {"wns": -1.0, "improved": False}

    result = run_multi_iteration_case(
        case_dir, max_iterations=5,
        equivalence_checker=lambda *a, **k: EquivalenceResult("pass", "test", "ok"),
        wns_evaluator=Eval(),
    )
    assert result["stop_reason"] == "wall_timeout"
    assert result["iterations"] == 1
    assert len(result["history"]) == 1
    assert len(calls) == 1


def test_patch_ratio_uses_non_timing_epsilon_not_timing_epsilon(tmp_path, monkeypatch):
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1, output_dir=tmp_path,
                          workers=1, strict_gates=True, max_patch_ratio=.9,
                          epsilon=.1, equivalence_checker=lambda *_a: True,
                          boundary_checker=lambda *_a: True)
    ev._candidates_for = lambda _cells, _inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, _inst, _kind, _new, _pin: text.replace("and2_1", "and2_2")
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kwargs: {"wns": -.5, "tns": -1})
    result = ev(SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"]), None)
    assert result["improved"] is False
    event = next(e for e in result["failure_events"] if e["type"] == "F3_patch_too_large")
    assert event["threshold"]["unit"] == "ratio"
    assert event["threshold"]["epsilon"] == 0.0


def test_full_netlist_sec_text_backend_runs_yosys_abc_production_wiring(tmp_path, monkeypatch):
    import rseco.yosys_abc as yosys_abc
    calls = []

    def fake_checker(_original, _revised, **kwargs):
        calls.append(kwargs)
        return SimpleNamespace(status="pass", method="yosys_blif_abc_cec",
                               reason="equivalent", tool="yosys+abc")

    monkeypatch.setattr(yosys_abc, "check_yosys_abc_equivalence", fake_checker)
    checker = build_full_netlist_sec_checker(
        top_module="top", liberty_text=LIB, artifact_dir=tmp_path,
    )
    result = checker(BASE, BASE)
    assert result.status == "pass"
    assert calls and calls[0]["outputs"] == ["Y"]
    assert calls[0]["yosys_command"] == "wsl.exe -e yosys"
    assert calls[0]["abc_command"] == "wsl.exe -e yosys-abc"


def test_full_netlist_sec_builder_materializes_verilog_cells_and_keeps_report(tmp_path):
    log = tmp_path / "yosys.log"
    fake_yosys = tmp_path / "fake_yosys.py"
    fake_yosys.write_text(
        "import pathlib, re, sys\n"
        "script=sys.argv[sys.argv.index('-p')+1]\n"
        f"pathlib.Path(r'{str(log)}').open('a', encoding='utf-8').write(script + '\\n')\n"
        "m=re.search(r'write_blif\\s+([^;]+)', script)\n"
        "p=pathlib.Path(m.group(1).strip().strip(chr(34))); p.parent.mkdir(parents=True, exist_ok=True)\n"
        "p.write_text('.model top\\n.inputs A B\\n.outputs Y\\n.names A B Y\\n11 1\\n.end\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )
    fake_abc = tmp_path / "fake_abc.py"
    fake_abc.write_text(
        "import sys\nprint('Networks are equivalent after structural hashing.')\n",
        encoding="utf-8",
    )
    checker = build_full_netlist_sec_checker(
        top_module="top", liberty_text=LIB, artifact_dir=tmp_path / "sec",
        yosys_command=f"{sys.executable} {fake_yosys}",
        abc_command=f"{sys.executable} {fake_abc}",
    )
    result = checker(BASE, BASE)
    assert result.status == "pass"
    cells_files = list((tmp_path / "sec").rglob("*_cells.v"))
    assert cells_files and "module sky130_fd_sc_hd__and2_1" in cells_files[0].read_text()
    assert not cells_files[0].read_text().lstrip().startswith("cell (")
    assert result.log_path and Path(result.log_path).exists()
    script = log.read_text(encoding="utf-8")
    assert script.count("read_verilog") >= 3


def test_liberty_sequential_model_has_clocked_next_state(tmp_path):
    from rseco.real_wns import write_liberty_cell_models
    path = write_liberty_cell_models(SEQ_LIB, tmp_path / "cells.v",
                                     used_cells={"sky130_fd_sc_hd__dfxtp_1"})
    text = path.read_text(encoding="utf-8")
    assert "always @(posedge CLK)" in text
    assert "Q <= D" in text


def test_real_wsl_sec_rejects_logic_pin_and_topology_changes(tmp_path):
    if shutil.which("wsl.exe") is None:
        import pytest
        pytest.skip("WSL executable unavailable")
    checker = build_full_netlist_sec_checker(
        top_module="top", liberty_text=LIB, artifact_dir=tmp_path / "wsl-sec",
    )
    assert checker(BASE, BASE).status == "pass"
    assert checker(BASE, BASE.replace("and2_1", "or2_1")).status == "fail"
    assert checker(BASE, BASE.replace(".B(B)", ".B(A)")).status == "fail"
    assert checker(TOPOLOGY_TEXT, TOPOLOGY_TEXT).status == "pass"


def test_unavailable_sec_persists_reason_log(tmp_path):
    original = tmp_path / "original.v"
    revised = tmp_path / "revised.v"
    original.write_text(BASE, encoding="utf-8")
    revised.write_text(BASE, encoding="utf-8")
    result = check_yosys_abc_equivalence(
        original, revised, outputs=["Y"], artifact_dir=tmp_path / "missing",
        yosys_command="definitely-missing-yosys", abc_command="definitely-missing-abc",
    )
    assert result.status == "unavailable"
    assert result.log_path and Path(result.log_path).exists()
    log = Path(result.log_path).read_text(encoding="utf-8")
    assert "definitely-missing-yosys" in log and "command not found" in log


def test_real_wsl_sec_observes_sequential_d_path_change(tmp_path):
    if shutil.which("wsl.exe") is None:
        import pytest
        pytest.skip("WSL executable unavailable")
    checker = build_full_netlist_sec_checker(
        top_module="top", liberty_text=SEQ_LIB, artifact_dir=tmp_path / "wsl-seq",
    )
    assert checker(SEQ_BASE, SEQ_BASE).status == "pass"
    changed = SEQ_BASE.replace(".D(D)", ".D(Q)")
    assert checker(SEQ_BASE, changed).status == "fail"


def test_topology_reserves_boundary_after_sec_and_deadline_before_boundary(tmp_path, monkeypatch):
    import rseco.real_wns as rw
    boundary_calls = []
    ev = RealWnsEvaluator(
        mapped_text=TOPOLOGY_TEXT, top_module="top", period=1,
        liberty_text=TOPOLOGY_LIB, baseline_wns=-1, output_dir=tmp_path,
        workers=1, strict_gates=True,
        topology_sec_checker=lambda *_a: True,
        boundary_checker=lambda *_a: boundary_calls.append(True) or True,
    )
    ev._candidates_for = lambda _cells, _inst: []
    monkeypatch.setattr(rw, "check_local_functional_equivalence",
                        lambda *_a: EquivalenceResult("pass", "local", "ok"))
    state = SearchState(current_netlist_text=TOPOLOGY_TEXT,
                        budget={"formal_budget": 2, "sta_budget": 9})
    result = ev(_topology_patch(), None, state=state)
    assert boundary_calls == []
    assert state.budget_used("formal") == 2
    assert result["failure_events"][0]["type"] == "formal_budget_exhausted"

    boundary_calls.clear()
    state = SearchState(current_netlist_text=TOPOLOGY_TEXT,
                        budget={"formal_budget": 9, "sta_budget": 9,
                                "_deadline_monotonic": time.perf_counter() + 1})
    ev._sta_cache.clear()
    def sec_expires(*_args):
        state.budget["_deadline_monotonic"] = time.perf_counter() - 1
        return True
    ev.topology_sec_checker = sec_expires
    result = ev(_topology_patch(), None, state=state)
    assert boundary_calls == []
    assert result["failure_events"][0]["type"] == "deadline_exhausted"


def test_physical_pair_accepts_without_ideal_baseline_comparison_and_records_provenance(tmp_path, monkeypatch):
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=0.0,
                          output_dir=tmp_path, workers=1, physical_gate=True,
                          min_physical_gain_ns=0.1, strict_budgets=True,
                          baseline_tns=-0.5, baseline_min_slack=-0.5)
    ev._candidates_for = lambda _cells, _inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, _inst, _kind, _new, _pin: text.replace("and2_1", "and2_2")

    def sta(**kwargs):
        out = Path(kwargs["output_dir"])
        out.mkdir(parents=True, exist_ok=True)
        (out / "sta.log").write_text(
            "Endpoint: phys_ff\n   0.10    0.20 v phys_g/A (sky130_fd_sc_hd__and2_2)\n",
            encoding="utf-8",
        )
        if kwargs.get("spef_path") is None:
            return {"wns": -100.0, "tns": -100.0, "min_slack": -100.0}
        if "physical_baseline" in str(out):
            return {"wns": -1.2, "tns": -3.0, "min_slack": -0.8}
        return {"wns": -1.1, "tns": -2.5, "min_slack": -0.7}

    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential", sta)
    result = ev(SimpleNamespace(patch_id="paired", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"]), None)
    assert result["improved"] is True
    assert result["wns"] == -1.1 and result["tns"] == -2.5
    assert result["critical_endpoints"] == ["phys_ff"]
    assert result["sta_provenance"]["report_path"].endswith("physical\\sta.log") or result["sta_provenance"]["report_path"].endswith("physical/sta.log")
    assert result["physical_baseline_provenance"]["wns"] == -1.2
    assert result["physical_candidate_provenance"]["wns"] == -1.1
    refs = result["acceptance_evidence"]["metric_references"]
    assert refs["setup_tns"] == -3.0
    assert refs["hold_min_slack"] == -0.8


def test_physical_pair_uses_real_min_gain_threshold(tmp_path, monkeypatch):
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1.0,
                          output_dir=tmp_path, workers=1, physical_gate=True,
                          min_physical_gain_ns=0.6)
    ev._candidates_for = lambda _cells, _inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, _inst, _kind, _new, _pin: text.replace("and2_1", "and2_2")
    def sta(**kwargs):
        if kwargs.get("spef_path") is None:
            return {"wns": -.5, "tns": -1, "min_slack": -.5}
        if "physical_baseline" in str(kwargs["output_dir"]):
            return {"wns": -1.2, "tns": -3, "min_slack": -.8}
        return {"wns": -.7, "tns": -2.5, "min_slack": -.7}
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential", sta)
    result = ev(SimpleNamespace(patch_id="gain", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"]), None)
    assert result["improved"] is False
    assert result["physical_status"] == "paired_rejected"
    f6 = next(e for e in result["failure_events"] if e["type"] == "F6_physical_load_failure")
    assert f6["evidence"]["threshold"] == {"value": 0.6, "unit": "ns", "epsilon": 0.0}
    assert f6["evidence"]["actual_delta"] == 0.5
    assert result["physical_config"]["min_physical_gain_ns"] == 0.6


def test_physical_pair_requires_hold_when_hold_mode_requires_it(tmp_path, monkeypatch):
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1.0,
                          output_dir=tmp_path, workers=1, physical_gate=True,
                          hold_mode=True, baseline_min_slack=-.8)
    ev._candidates_for = lambda _cells, _inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, _inst, _kind, _new, _pin: text.replace("and2_1", "and2_2")
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kwargs: {"wns": -.5, "tns": -1, "min_slack": None})
    result = ev(SimpleNamespace(patch_id="hold", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"]), None)
    assert result["improved"] is False


def test_setup_physical_pair_allows_optional_missing_hold(tmp_path, monkeypatch):
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1.0,
                          output_dir=tmp_path, workers=1, physical_gate=True)
    ev._candidates_for = lambda _cells, _inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, _inst, _kind, _new, _pin: text.replace("and2_1", "and2_2")
    def sta(**kwargs):
        if kwargs.get("spef_path") is None:
            return {"wns": -.5, "tns": -1}
        if "physical_baseline" in str(kwargs["output_dir"]):
            return {"wns": -1.2, "tns": -3}
        return {"wns": -.7, "tns": -2.5}
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential", sta)
    result = ev(SimpleNamespace(patch_id="optional-hold", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"]), None)
    assert result["improved"] is True


def test_setup_optional_hold_regression_is_evidence_not_hard_gate(tmp_path, monkeypatch):
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1.0,
                          baseline_tns=-3.0, baseline_min_slack=-.8,
                          output_dir=tmp_path, workers=1, physical_gate=True,
                          strict_budgets=True)
    ev._candidates_for = lambda _cells, _inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, _inst, _kind, _new, _pin: text.replace("and2_1", "and2_2")
    def sta(**kwargs):
        if kwargs.get("spef_path") is None:
            return {"wns": -.5, "tns": -1, "min_slack": -.5}
        if "physical_baseline" in str(kwargs["output_dir"]):
            return {"wns": -1.2, "tns": -3, "min_slack": -.8}
        return {"wns": -.7, "tns": -2.5, "min_slack": -1.0}
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential", sta)
    result = ev(SimpleNamespace(patch_id="optional-degrade", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"]), None)
    assert result["improved"] is True
    assert not any(e.get("type") == "acceptance_budget_violation" for e in result["failure_events"])


def test_physical_hold_candidate_min_slack_propagates_to_state_record(tmp_path, monkeypatch):
    from rseco.refinement_loop import SearchState
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1.0,
                          baseline_tns=-3.0, baseline_min_slack=-.8,
                          output_dir=tmp_path, workers=1, physical_gate=True,
                          hold_mode=True)
    ev._candidates_for = lambda _cells, _inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, _inst, _kind, _new, _pin: text.replace("and2_1", "and2_2")
    def sta(**kwargs):
        if kwargs.get("spef_path") is None:
            return {"wns": -.9, "tns": -2.9, "min_slack": -.75}
        if "physical_baseline" in str(kwargs["output_dir"]):
            return {"wns": -1.0, "tns": -3.0, "min_slack": -.8}
        return {"wns": -.9, "tns": -2.9, "min_slack": -.7}
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential", sta)
    result = ev(SimpleNamespace(patch_id="hold-state", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"]), None)
    assert result["improved"] is True and result["min_slack"] == -.7
    state = SearchState(current_netlist_text=BASE)
    state.accept_patch("hold-state", result["candidate_netlist_text"],
                       wns=result["wns"], tns=result["tns"],
                       min_slack=result["min_slack"],
                       metadata={"physical_metrics": {
                           "candidate_hold": result["physical_candidate_min_slack"]}})
    assert state.current_min_slack == state.accepted_patches[-1]["min_slack"] == -.7
    assert state.accepted_patches[-1]["metadata"]["physical_metrics"]["candidate_hold"] == -.7


def test_unsupported_sequential_cell_returns_structured_sec_failure(tmp_path):
    unsupported = '''cell ("sky130_fd_sc_hd__dff_1") {
      pin ("D") { direction : "input"; }
      pin ("CLK") { direction : "input"; }
      pin ("Q") { direction : "output"; }
    }'''
    text = "module top(D, CLK, Q); input D, CLK; output Q; sky130_fd_sc_hd__dff_1 ff1 (.D(D), .CLK(CLK), .Q(Q)); endmodule\n"
    checker = build_full_netlist_sec_checker(top_module="top", liberty_text=unsupported,
                                             artifact_dir=tmp_path)
    result = checker(text, text)
    assert result.status in {"fail", "unavailable"}
    assert "unsupported sequential" in result.reason


def test_metric_budget_evidence_uses_physical_units(tmp_path, monkeypatch):
    ev = RealWnsEvaluator(
        mapped_text=BASE, top_module="top", period=1, liberty_text=LIB,
        baseline_wns=-1, output_dir=tmp_path, workers=1, strict_budgets=True,
        area_budget=1, max_transition_budget=1, max_capacitance_budget=1,
        max_fanout_budget=1,
        available_metrics=("setup_wns", "setup_tns", "area", "max_transition",
                           "max_capacitance", "max_fanout"),
    )
    ev._candidates_for = lambda _cells, _inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, _inst, _kind, _new, _pin: text.replace("and2_1", "and2_2")
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential", lambda **kwargs: {
        "wns": -.5, "tns": -1, "area": 2, "max_transition": 2,
        "max_capacitance": 2, "max_fanout": 2,
    })
    result = ev(SimpleNamespace(patch_id="units", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"]), None)
    event = next(e for e in result["failure_events"] if e["type"] == "acceptance_budget_violation")
    units = {key: value["unit"] for key, value in event["evidence"]["metric_budgets"].items()}
    assert units == {"area": "um^2", "max_transition": "ns",
                     "max_capacitance": "pF", "max_fanout": "count"}


def test_topology_structural_budget_reserves_local_sec_and_boundary_separately(tmp_path, monkeypatch):
    import rseco.real_wns as rw
    local_calls, sec_calls, boundary_calls = [], [], []
    ev = RealWnsEvaluator(
        mapped_text=TOPOLOGY_TEXT, top_module="top", period=1,
        liberty_text=TOPOLOGY_LIB, baseline_wns=-1, output_dir=tmp_path,
        workers=1, strict_gates=True,
        topology_sec_checker=lambda *_a: sec_calls.append(True) or True,
        boundary_checker=lambda *_a: boundary_calls.append(True) or True,
    )
    ev._candidates_for = lambda _cells, _inst: []
    monkeypatch.setattr(rw, "check_local_functional_equivalence",
                        lambda *_a: (local_calls.append(True) or EquivalenceResult("pass", "local", "ok")))
    state = SearchState(current_netlist_text=TOPOLOGY_TEXT,
                        budget={"formal_budget": 1, "sta_budget": 9})
    result = ev(_topology_patch(), None, state=state)
    assert local_calls == [True]
    assert sec_calls == []
    assert boundary_calls == []
    assert state.budget_used("formal") == 1
    assert result["failure_events"][0]["type"] == "formal_budget_exhausted"


def test_terminal_budget_event_is_recorded_once_before_flow_stops(tmp_path):
    case_dir = tmp_path / "terminal-event"
    (case_dir / "original").mkdir(parents=True)
    (case_dir / "resynthesized").mkdir(parents=True)
    (case_dir / "original" / "original.v").write_text(net_for_stop)
    (case_dir / "resynthesized" / "resynthesized.v").write_text(net_for_stop)
    (case_dir / "case.yaml").write_text("case_id: terminal-event\ntarget:\n  output: Y\n")

    class Eval:
        use_constrained_cuts = False
        strict_gates = False
        boundary_checker = object()
        critical_instances = ["g1"]

        def __call__(self, patch, weights, *, state):
            return {"wns": -1.0, "improved": False, "failure_events": [{
                "type": "sta_budget_exhausted", "severity": "hard",
                "candidate_hash": "terminal", "evidence": {"stage": "sta"},
            }]}

    result = run_multi_iteration_case(
        case_dir, max_iterations=3,
        equivalence_checker=lambda *a, **k: EquivalenceResult("pass", "test", "ok"),
        wns_evaluator=Eval(),
    )
    events = [e for e in result["state"]["failure_history"]
              if e["type"] == "sta_budget_exhausted"]
    assert result["stop_reason"] == "sta_budget"
    assert len(events) == 1


def test_physical_hold_missing_is_rejected_and_physical_report_is_provenance(tmp_path, monkeypatch):
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                              liberty_text=LIB, baseline_wns=-1, output_dir=tmp_path,
                              workers=1, physical_gate=True, min_physical_gain_ns=.01,
                              baseline_min_slack=-1.0,
                              required_metrics=("setup_wns", "setup_tns", "hold_min_slack"))
    ev._candidates_for = lambda _cells, _inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, _inst, _kind, _new, _pin: text.replace("and2_1", "and2_2")

    def sta(**kwargs):
        out = kwargs["output_dir"]
        Path(out).mkdir(parents=True, exist_ok=True)
        Path(out, "sta.log").write_text(
            "Endpoint: physical_ff\n   0.10    0.20 v physical_g/A (sky130_fd_sc_hd__and2_2)\n",
            encoding="utf-8",
        )
        if kwargs.get("spef_path") is None:
            return {"wns": -.5, "tns": -1.0, "min_slack": -.5}
        if "physical_baseline" in str(out):
            return {"wns": -1.0, "tns": -2.0, "min_slack": -1.0}
        return {"wns": -.5, "tns": -1.0, "min_slack": None}

    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential", sta)
    result = ev(SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"]), None)
    assert result["improved"] is False
    assert result["physical_status"] == "paired_incomplete"
    assert result["physical_candidate_min_slack"] is None


def test_boundary_failure_event_preserves_exact_checker_kind(tmp_path):
    kind = "rewired-module-output"
    checker = lambda *_a: EquivalenceResult(
        "fail", "boundary_closure",
        '{"stage":"consumed_net_closure","kind":"rewired-module-output"}',
    )
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1,
                          output_dir=tmp_path, workers=1, strict_gates=True,
                          equivalence_checker=lambda *_a: True,
                          boundary_checker=checker)
    ev._candidates_for = lambda _cells, _inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, _inst, _kind, _new, _pin: text.replace("and2_1", "and2_2")
    result = ev(SimpleNamespace(patch_id="f2", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"]), None)
    assert len(result["failure_events"]) == 1
    assert result["failure_events"][0]["type"] == "F2_boundary_invalid"
    assert result["failure_events"][0]["evidence"]["kind"] == kind


def test_max_patches_one_returns_success_with_accepted_then_stopped_history(tmp_path):
    case_dir = tmp_path / "one-patch"
    (case_dir / "original").mkdir(parents=True)
    (case_dir / "resynthesized").mkdir(parents=True)
    (case_dir / "original" / "original.v").write_text(net_for_stop)
    (case_dir / "resynthesized" / "resynthesized.v").write_text(net_for_stop)
    (case_dir / "case.yaml").write_text("case_id: one-patch\ntarget:\n  output: Y\n")

    class Eval:
        use_constrained_cuts = False
        strict_gates = False
        boundary_checker = object()
        critical_instances = ["g1"]
        baseline_wns = -1.0

        def __call__(self, patch, weights, *, state):
            return {"wns": -.5, "tns": -1.0, "improved": True,
                    "candidate_netlist_text": net_for_stop,
                    "candidate_hash": "accepted-one"}

        def accept_candidate(self, result, *, state):
            return None

    result = run_multi_iteration_case(
        case_dir, max_iterations=3, max_patches=1,
        equivalence_checker=lambda *a, **k: EquivalenceResult("pass", "test", "ok"),
        wns_evaluator=Eval(),
    )
    assert result["success"] is True
    assert result["final_patch_id"] is not None
    assert [h["status"] for h in result["history"]] == ["accepted", "stopped"]
    assert result["iterations"] == 1


def test_non_timing_budget_event_records_metric_value_budget_epsilon_unit_and_backend(tmp_path, monkeypatch):
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1, output_dir=tmp_path,
                          workers=1, strict_budgets=True, area_budget=1.0,
                          metric_epsilons={"area": .01},
                          available_metrics=("setup_wns", "setup_tns", "area"),
                          equivalence_checker=lambda *_a: True,
                          boundary_checker=lambda *_a: True)
    ev._candidates_for = lambda _cells, _inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, _inst, _kind, _new, _pin: text.replace("and2_1", "and2_2")
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kwargs: {"wns": -.5, "tns": -1, "area": 2.0})
    result = ev(SimpleNamespace(patch_id="area", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"]), None)
    event = next(e for e in result["failure_events"] if e["type"] == "acceptance_budget_violation")
    metric = event["evidence"]["metric_budgets"]["area"]
    assert metric == {"value": 2.0, "budget": 1.0, "epsilon": .01,
                      "unit": "um^2", "backend": "OpenSTA"}
