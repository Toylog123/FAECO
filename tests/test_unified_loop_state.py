from pathlib import Path

from rseco.equivalence import EquivalenceResult
from rseco.flow import run_multi_iteration_case
from rseco.refinement_loop import SearchState
from rseco.failures import FailureEvent, FailureType
from rseco.real_wns import RealWnsEvaluator


def test_search_state_hashes_and_replays_accepted_netlists():
    state = SearchState(current_netlist_text="G0", current_wns=-1.0)
    h0 = state.current_netlist_hash
    state.accept_patch("p1", "G1", wns=-0.8, tns=-2.0)
    state.accept_patch("p2", "G2", wns=-0.6, tns=-1.0)
    assert h0 != state.current_netlist_hash
    assert [p["patch_id"] for p in state.accepted_patches] == ["p1", "p2"]
    assert state.current_netlist_text == "G2"
    assert SearchState.replay("G0", state.accepted_patches) == "G2"
    state.rollback()
    assert state.current_netlist_text == "G1"


def test_failure_event_is_structured_and_serializable():
    event = FailureEvent(type=FailureType.BOUNDARY_INVALID,
                         candidate_hash="c", cut_hash="k", endpoint="Y",
                         path=["g1"], net="N1", action_scope=["g1"],
                         threshold=1, observed_value=2, severity="hard",
                         runtime_s=0.1, evidence={"checker": "boundary"})
    payload = event.to_dict()
    assert payload["type"] == FailureType.BOUNDARY_INVALID.value
    assert payload["evidence"]["checker"] == "boundary"


def test_real_evaluator_returns_candidate_netlist_for_atomic_commit(tmp_path, monkeypatch):
    text = """module top(A, B, Y);
input A, B;
output Y;
and g1 (Y, A, B);
endmodule
"""
    lib = """cell (sky130_fd_sc_hd__and2_1) { area : 1; pin(A) { direction : input; } pin(B) { direction : input; } pin(Y) { direction : output; } }
"""
    evaluator = RealWnsEvaluator(mapped_text=text, top_module="top", period=1,
                                  liberty_text=lib, baseline_wns=-1,
                                  output_dir=tmp_path, critical_instances=["g1"], workers=1)
    class P:
        patch_id = "p"
        gates = ["g1"]
        boundary_inputs = []
        boundary_outputs = ["Y"]
    monkeypatch.setattr("rseco.real_wns.run_opensta_sequential",
                        lambda **kw: {"wns": -.5, "tns": -1})
    from types import SimpleNamespace
    monkeypatch.setattr("rseco.real_wns.parse_mapped_netlist",
                        lambda _: [SimpleNamespace(instance="g1", cell_type="x")])
    evaluator._candidates_for = lambda cells, inst: [("new", {}, "G")]
    evaluator._apply = lambda text, inst, kind, new, pin: text.replace("g1", "g2")
    result = evaluator(P(), None)
    assert result["candidate_netlist_text"]


def test_real_evaluator_accept_candidate_advances_baseline(tmp_path):
    ev = RealWnsEvaluator(mapped_text="G0", top_module="top", period=1,
                          liberty_text="", baseline_wns=-1,
                          output_dir=tmp_path)
    state = SearchState(current_netlist_text="G0", current_wns=-1)
    state.accept_patch("p", "G1", wns=-.8, tns=-2)
    ev.accept_candidate({"candidate_netlist_text": "G1", "wns": -.8,
                         "tns": -2}, state=state)
    assert ev.mapped_text == "G1"
    assert ev.baseline_wns == -.8


def test_multi_iteration_commits_two_candidates_and_passes_state_forward(tmp_path):
    case_dir = tmp_path / "case"
    (case_dir / "original").mkdir(parents=True)
    (case_dir / "resynthesized").mkdir(parents=True)
    (case_dir / "case.yaml").write_text("case_id: c\ntarget:\n  output: Y\n")
    net = """module top(A, B, Y);
input A, B;
output Y;
and g1 (Y, A, B);
endmodule
"""
    (case_dir / "original" / "original.v").write_text(net)
    (case_dir / "resynthesized" / "resynthesized.v").write_text(net)
    seen = []

    def equiv(*args, **kwargs):
        return EquivalenceResult(status="pass", method="test", reason="test")

    def evaluate(patch, weights, *, state):
        seen.append((state.current_netlist_text, state.current_netlist_hash))
        n = len(state.accepted_patches) + 1
        return {"wns": -1.0 + n * .1, "tns": -n, "improved": True,
                "candidate_netlist_text": f"G{n}",
                "critical_instances": [f"g{n}"]}

    result = run_multi_iteration_case(case_dir, max_iterations=4,
                                      max_patches=2,
                                      equivalence_checker=equiv,
                                      wns_evaluator=evaluate)
    assert result["success"] is True
    assert result["stop_reason"] == "max_patches"
    assert len(result["state"]["accepted_patches"]) == 2
    assert seen[0][0] == net
    assert seen[1][0] == "G1"
    assert seen[0][1] != seen[1][1]
