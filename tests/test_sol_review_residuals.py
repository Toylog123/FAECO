from types import SimpleNamespace

from rseco.real_wns import (
    RealWnsEvaluator, build_boundary_closure_checker,
    build_real_equivalence_checker,
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


LIB = """cell (\"sky130_fd_sc_hd__and2_1\") { pin (\"A\") { direction : \"input\"; } pin (\"B\") { direction : \"input\"; } pin (\"Y\") { direction : \"output\"; function : \"A & B\"; } }
cell (\"sky130_fd_sc_hd__and2_2\") { pin (\"A\") { direction : \"input\"; } pin (\"B\") { direction : \"input\"; } pin (\"Y\") { direction : \"output\"; function : \"A & B\"; } }
cell (\"sky130_fd_sc_hd__or2_1\") { pin (\"A\") { direction : \"input\"; } pin (\"B\") { direction : \"input\"; } pin (\"Y\") { direction : \"output\"; function : \"A | B\"; } }
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
            return {"wns": -1.2, "tns": -2}
        return {"wns": -1.1, "tns": -1.5}

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
