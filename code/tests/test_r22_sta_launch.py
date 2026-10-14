"""Candidate ideal-STA launch identities, without invoking EDA tools."""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from threading import Barrier
from types import SimpleNamespace

import pytest

import rseco.real_wns as rw
from rseco.refinement_loop import SearchState


LIB = "\n".join(
    f'cell ("sky130_fd_sc_hd__and2_{size}") {{ '
    'pin ("A") { direction : "input"; } '
    'pin ("B") { direction : "input"; } '
    'pin ("Y") { direction : "output"; function : "A & B"; } }'
    for size in (1, 2, 4)
)
BASE = """module top(A, B, Y);
input A, B;
output Y;
sky130_fd_sc_hd__and2_1 g1 (.A(A), .B(B), .Y(Y));
endmodule
"""


def _evaluator(tmp_path, **options):
    return rw.RealWnsEvaluator(
        mapped_text=BASE, top_module="top", period=1, liberty_text=LIB,
        baseline_wns=-1, baseline_tns=-2, output_dir=tmp_path,
        workers=1, enable_topology=False, **options,
    )


def _job(ev, size=2, index=0):
    return ("g1", "sky130_fd_sc_hd__and2_1", f"sky130_fd_sc_hd__and2_{size}",
            {}, "G", ev.mapped_text, ev.output_dir, "top", index, {})


def test_actual_ideal_call_has_one_launch_event_and_result_link(tmp_path, monkeypatch):
    ev = _evaluator(tmp_path)
    calls = []
    monkeypatch.setattr(rw, "run_opensta_sequential",
                        lambda **kw: calls.append(kw) or {"wns": -0.5, "tns": -1})
    result = ev._eval_one(_job(ev))
    assert result["sta_executed"] is True
    assert result["sta_launch_seq"] == 1
    assert len(calls) == len(ev.sta_launch_events) == 1
    event = ev.sta_launch_events[0]
    assert event["seq"] == 1 and event["kind"] == "candidate_ideal"
    assert event["candidate_hash"] == result["candidate_hash"]
    assert event["base_netlist_hash"] == result["base_netlist_hash"]
    assert event["report_dir"] == str(calls[0]["output_dir"])
    assert event["wns"] == -0.5 and event["tns"] == -1
    assert event["timeout"] is False and event["error"] is None
    assert event["runtime_s"] >= 0


def test_cached_result_retains_history_without_consuming_new_sequence(tmp_path, monkeypatch):
    ev = _evaluator(tmp_path)
    calls = []
    monkeypatch.setattr(rw, "run_opensta_sequential",
                        lambda **kw: calls.append(kw) or {"wns": -1.2, "tns": -2})
    first = ev._eval_one(_job(ev))
    cached = ev._eval_one(_job(ev, index=1))
    assert len(calls) == len(ev.sta_launch_events) == 1
    assert cached["sta_executed"] is False
    assert cached["sta_launch_seq"] is None
    assert cached["cached_from_seq"] == first["sta_launch_seq"]
    assert cached["skipped_duplicate"] is True
    assert cached["sta_provenance"] == first["sta_provenance"]


@pytest.mark.parametrize("failure", [TimeoutError("candidate timeout"), RuntimeError("bad tool")])
def test_tool_exception_consumes_launch_and_is_linked_to_failure_result(
    tmp_path, monkeypatch, failure,
):
    ev = _evaluator(tmp_path)

    def failed_sta(**_kw):
        raise failure

    monkeypatch.setattr(rw, "run_opensta_sequential", failed_sta)
    result = ev._eval_one(_job(ev))
    assert result["sta_executed"] is True and result["sta_launch_seq"] == 1
    assert len(ev.sta_launch_events) == 1
    event = ev.sta_launch_events[0]
    assert event["wns"] is None
    assert event["error"] == str(failure)
    assert event["timeout"] is isinstance(failure, TimeoutError)
    assert event["status"] == ("timeout" if isinstance(failure, TimeoutError) else "error")


def test_budget_rejection_is_not_an_ideal_launch(tmp_path, monkeypatch):
    ev = _evaluator(tmp_path)
    ev._active_state = SearchState(current_netlist_text=BASE, budget={"sta_budget": 0})
    monkeypatch.setattr(rw, "run_opensta_sequential",
                        lambda **_kw: pytest.fail("exhausted budget must reject before STA"))
    result = ev._eval_one(_job(ev))
    assert result["sta_executed"] is False and result["sta_launch_seq"] is None
    assert ev.sta_launch_events == []
    assert result["failure_events"][0]["type"] == "sta_budget_exhausted"


def test_structural_rejection_has_no_launch(tmp_path, monkeypatch):
    ev = _evaluator(tmp_path, strict_gates=True,
                    equivalence_checker=lambda *_a: True, boundary_checker=lambda *_a: False)
    monkeypatch.setattr(rw, "run_opensta_sequential",
                        lambda **_kw: pytest.fail("structural failure must reject before STA"))
    result = ev._eval_one(_job(ev))
    assert result["sta_executed"] is False and result["sta_launch_seq"] is None
    assert ev.sta_launch_events == []


def test_physical_sta_does_not_inflate_candidate_ideal_launch_count(tmp_path, monkeypatch):
    ev = _evaluator(tmp_path, physical_gate=True)
    calls = []

    def sta(**kw):
        calls.append(kw)
        return {"wns": -0.5, "tns": -1}

    monkeypatch.setattr(rw, "run_opensta_sequential", sta)
    monkeypatch.setattr("rseco.spef.write_spef", lambda path, *_a, **_kw: Path(path))
    result = ev._eval_one(_job(ev))
    assert len(calls) == 3  # ideal candidate + paired physical baseline/candidate
    assert len(ev.sta_launch_events) == 1
    assert result["sta_launch_seq"] == 1
    assert ev.sta_launch_events[0]["report_dir"] == str(calls[0]["output_dir"])
    assert all(event["kind"] == "candidate_ideal" for event in ev.sta_launch_events)


def test_trials_link_launches_and_cache_hits_to_distinct_identities(tmp_path, monkeypatch):
    ev = _evaluator(tmp_path, early_stop=True)
    calls = []
    monkeypatch.setattr(rw, "run_opensta_sequential",
                        lambda **kw: calls.append(kw) or {"wns": -0.5, "tns": -1})
    patch = SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=["A", "B"],
                            boundary_outputs=["Y"])
    ev(patch, None)
    ev(patch, None)
    assert len(calls) == len(ev.sta_launch_events) == 1
    assert len(ev.trials) == 2
    assert [trial["sta_launch_seq"] for trial in ev.trials] == [1, None]
    assert [trial["sta_executed"] for trial in ev.trials] == [True, False]
    assert ev.trials[1]["cached_from_seq"] == 1


def test_new_base_gets_new_launch_even_for_same_action(tmp_path, monkeypatch):
    ev = _evaluator(tmp_path)
    monkeypatch.setattr(rw, "run_opensta_sequential", lambda **_kw: {"wns": -0.5, "tns": -1})
    first = ev._eval_one(_job(ev))
    ev.mapped_text = BASE + "\n// different committed base\n"
    second = ev._eval_one(_job(ev, index=1))
    assert [event["seq"] for event in ev.sta_launch_events] == [1, 2]
    assert first["base_netlist_hash"] != second["base_netlist_hash"]
    assert second["sta_executed"] is True and second["sta_launch_seq"] == 2


def test_parallel_distinct_launches_have_unique_sequences(tmp_path, monkeypatch):
    ev = _evaluator(tmp_path)
    simultaneous = Barrier(2)

    def sta(**_kw):
        simultaneous.wait(timeout=5)
        return {"wns": -0.5, "tns": -1}

    monkeypatch.setattr(rw, "run_opensta_sequential", sta)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(ev._eval_one, [_job(ev, 2, 0), _job(ev, 4, 1)]))
    assert sorted(result["sta_launch_seq"] for result in results) == [1, 2]
    assert [event["seq"] for event in ev.sta_launch_events] == [1, 2]
    assert len({event["candidate_hash"] for event in ev.sta_launch_events}) == 2


def test_trial_archive_keeps_launch_ledger_and_trial_links(tmp_path, monkeypatch):
    ev = _evaluator(tmp_path, early_stop=True)
    monkeypatch.setattr(rw, "run_opensta_sequential", lambda **_kw: {"wns": -0.5, "tns": -1})
    patch = SimpleNamespace(patch_id="p", gates=["g1"], boundary_inputs=["A", "B"],
                            boundary_outputs=["Y"])
    ev(patch, None)
    path = tmp_path / "eval_trials.json"
    ev.write_trials(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert len(payload["sta_launch_events"]) == 1
    assert payload["sta_launch_events"][0]["seq"] == payload["trials"][0]["sta_launch_seq"]
    assert payload["sta_launch_events"][0]["candidate_hash"] == payload["trials"][0]["candidate_hash"]
