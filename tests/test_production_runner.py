import inspect

import rseco.flow as flow_module
from rseco.real_wns import (
    build_real_equivalence_checker, build_boundary_closure_checker,
)


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


def test_real_equivalence_checker_accepts_same_function_and_rejects_changed_function():
    checker = build_real_equivalence_checker(LIB)
    good = BASE.replace("and2_1", "and2_2")
    bad = BASE.replace("and2_1", "or2_1")
    assert checker(BASE, good).status == "pass"
    assert checker(BASE, bad).status == "fail"


def test_boundary_checker_is_real_and_fail_closed():
    checker = build_boundary_closure_checker()
    assert checker(BASE, BASE).status == "pass"
    broken = BASE.replace("module top(A, B, Y);", "module top(A, B, Z);")
    assert checker(BASE, broken).status == "fail"


def test_sta_cache_is_base_aware_and_caches_negative_results(tmp_path):
    from rseco.real_wns import RealWnsEvaluator
    from types import SimpleNamespace
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1,
                          output_dir=tmp_path, workers=1)
    ev._candidates_for = lambda cells, inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, inst, kind, new, pin: text.replace("and2_1", "and2_2")
    ev._eval_one = ev._eval_one
    patch = SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"])
    calls = []
    import rseco.real_wns as rw
    original = rw.run_opensta_sequential
    rw.run_opensta_sequential = lambda **kwargs: (calls.append(kwargs) or {"wns": -1.2, "tns": -2})
    try:
        ev(patch, None)
        ev(patch, None)
        assert len(calls) == 1
        ev.mapped_text = BASE.replace("and2_1", "and2_2")
        ev(patch, None)
        assert len(calls) >= 2
    finally:
        rw.run_opensta_sequential = original


def test_boundary_hard_gate_rejects_wns_improvement(tmp_path, monkeypatch):
    from rseco.real_wns import RealWnsEvaluator
    from types import SimpleNamespace
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1,
                          output_dir=tmp_path, workers=1, strict_gates=True,
                          equivalence_checker=lambda a, b: True,
                          boundary_checker=lambda a, b: False)
    ev._candidates_for = lambda cells, inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, inst, kind, new, pin: text.replace("and2_1", "and2_2")
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kwargs: {"wns": -.5, "tns": -1})
    patch = SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"])
    result = ev(patch, None)
    assert result["improved"] is False
    events = [e for trial in ev.trials for e in trial["failure_events"]]
    assert any(e["type"] == "F2_boundary_invalid" and e["candidate_hash"] for e in events)


def test_strict_f3_hard_gate_rejects_wns_improvement(tmp_path, monkeypatch):
    from rseco.real_wns import RealWnsEvaluator
    from types import SimpleNamespace
    checker = lambda a, b: True
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1,
                          output_dir=tmp_path, workers=1, strict_gates=True,
                          equivalence_checker=checker,
                          boundary_checker=checker, max_patch_ratio=0.0)
    ev._candidates_for = lambda cells, inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, inst, kind, new, pin: text.replace("and2_1", "and2_2")
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kwargs: {"wns": -.5, "tns": -1})
    patch = SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"])
    result = ev(patch, None)
    assert result["improved"] is False
    assert any(e["type"] == "F3_patch_too_large"
               for trial in ev.trials for e in trial["failure_events"])


def test_physical_mode_rejects_ideal_prefilter_without_paired_measurement(tmp_path, monkeypatch):
    from rseco.real_wns import RealWnsEvaluator
    from types import SimpleNamespace
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1.0,
                          output_dir=tmp_path, workers=1, physical_gate=True,
                          min_physical_gain_ns=0.01)
    ev._candidates_for = lambda cells, inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, inst, kind, new, pin: text.replace("and2_1", "and2_2")
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kwargs: {"wns": -.995, "tns": -1})
    patch = SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"])
    result = ev(patch, None)
    assert result["improved"] is False
    assert any(e["type"] == "F6_physical_load_failure"
               for trial in ev.trials for e in trial["failure_events"])


def test_runner_result_carries_selected_failure_events_and_acceptance_evidence(tmp_path, monkeypatch):
    from rseco.real_wns import RealWnsEvaluator
    from types import SimpleNamespace
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1,
                          output_dir=tmp_path, workers=1, strict_gates=True,
                          equivalence_checker=lambda a, b: True,
                          boundary_checker=lambda a, b: False)
    ev._candidates_for = lambda cells, inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, inst, kind, new, pin: text.replace("and2_1", "and2_2")
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kwargs: {"wns": -.5, "tns": -1})
    patch = SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"])
    result = ev(patch, None)
    assert result["improved"] is False
    assert any(e["type"] == "F2_boundary_invalid" for e in result["failure_events"])
    assert result["trial_failure_events"]


def test_strict_acceptance_rejects_wns_gain_with_tns_budget_regression(tmp_path, monkeypatch):
    from rseco.real_wns import RealWnsEvaluator
    from types import SimpleNamespace
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1, baseline_tns=-2,
                          output_dir=tmp_path, workers=1, strict_gates=True,
                          strict_budgets=True, max_patch_ratio=1.0,
                          equivalence_checker=lambda a, b: True,
                          boundary_checker=lambda a, b: True)
    ev._candidates_for = lambda cells, inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, inst, kind, new, pin: text.replace("and2_1", "and2_2")
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kwargs: {"wns": -.5, "tns": -3,
                                           "area": 1, "max_transition": 1,
                                           "max_capacitance": 1, "max_fanout": 1})
    patch = SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"])
    result = ev(patch, None)
    assert result["improved"] is False
    assert any(e["type"] == "acceptance_budget_violation"
               for trial in ev.trials for e in trial["failure_events"])


def test_runner_accepts_topology_trial_and_records_structural_delta(tmp_path, monkeypatch):
    from rseco.real_wns import RealWnsEvaluator
    from rseco.replacement import parse_verilog_netlist_from_text
    from types import SimpleNamespace
    text = """module top(A, B, Y);
input A, B;
output Y;
wire N1, N2;
sky130_fd_sc_hd__and2_1 g1 (N1, A, B);
sky130_fd_sc_hd__and2_1 g2 (N2, A, B);
sky130_fd_sc_hd__or2_1 g3 (Y, N1, N2);
endmodule
"""
    topo_lib = LIB + """
cell (\"sky130_fd_sc_hd__or2_1\") { pin (\"A\") { direction : \"input\"; } pin (\"B\") { direction : \"input\"; } pin (\"Y\") { direction : \"output\"; function : \"A | B\"; } }
"""
    ev = RealWnsEvaluator(mapped_text=text, top_module="top", period=1,
                          liberty_text=topo_lib, baseline_wns=-1,
                          output_dir=tmp_path, workers=1, max_patch_ratio=1.0,
                          strict_gates=True, equivalence_checker=lambda a, b: True,
                          boundary_checker=lambda a, b: True)
    ev._candidates_for = lambda cells, inst: []
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kwargs: {"wns": -.5, "tns": -1})
    patch = SimpleNamespace(patch_id="topology-p", gates=["g1", "g2", "g3"],
                             boundary_inputs=["A", "B"], boundary_outputs=["Y"])
    result = ev(patch, None)
    assert result["improved"] is True
    assert result["kind"] == "TOPOLOGY"
    before = parse_verilog_netlist_from_text(text)
    after = parse_verilog_netlist_from_text(result["candidate_netlist_text"])
    assert len(after.gates) < len(before.gates)
    assert sum(len(g.inputs) for g in after.gates) < sum(len(g.inputs) for g in before.gates)
    metrics = result["topology_metrics"]
    assert metrics["before"]["levels"] > metrics["after"]["levels"]
    assert metrics["before"]["gates"] > metrics["after"]["gates"]
    assert metrics["before"]["edges"] > metrics["after"]["edges"]
    topology_trials = [t for t in ev.trials if t["kind"] == "TOPOLOGY"]
    assert topology_trials and topology_trials[0]["accepted"] is True


def test_strict_mode_without_checker_records_unavailable_f1_f2(tmp_path, monkeypatch):
    from rseco.real_wns import RealWnsEvaluator
    from types import SimpleNamespace
    ev = RealWnsEvaluator(mapped_text=BASE, top_module="top", period=1,
                          liberty_text=LIB, baseline_wns=-1,
                          output_dir=tmp_path, workers=1, strict_gates=True)
    ev._candidates_for = lambda cells, inst: [("sky130_fd_sc_hd__and2_2", {}, "G")]
    ev._apply = lambda text, inst, kind, new, pin: text.replace("and2_1", "and2_2")
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kwargs: {"wns": -.5, "tns": -1})
    patch = SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=[], boundary_outputs=["Y"])
    result = ev(patch, None)
    types = {e["type"] for trial in ev.trials for e in trial["failure_events"]}
    assert result["improved"] is False
    assert {"F1_equivalence_failure", "F2_boundary_invalid"} <= types


def test_legacy_flow_does_not_bypass_boundary_checker():
    source = inspect.getsource(flow_module)
    assert "boundary_closed=True" not in source
    assert 'boundary_closed = equivalence.status in {"pass", "fail"}' in source
