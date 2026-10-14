"""STA event/record accounting contract; synthetic evidence, no EDA tools."""
from __future__ import annotations

import importlib
import importlib.util

import pytest


def summarize(trials, baseline=-1.0, launch_events=None):
    # A missing feature is an assertion failure, not a collection import error.
    assert importlib.util.find_spec("rseco.sta_ledger") is not None, "STA ledger summarizer is not implemented"
    return importlib.import_module("rseco.sta_ledger").summarize_sta_ledger(
        trials, baseline, launch_events=launch_events)


def trial(wns, *, accepted=False, seq=None, **fields):
    return {"wns": wns, "accepted": accepted, "sta_launch_seq": seq, **fields}


def test_events_count_timeout_but_not_cache_or_pre_sta_rejection():
    events = [
        {"kind": "baseline", "seq": 1, "wns": -1.0},
        {"kind": "candidate_ideal", "seq": 2, "status": "completed", "wns": -0.3},
        {"kind": "candidate_ideal", "seq": 3, "status": "timeout", "wns": 0.5},
        {"kind": "candidate_ideal", "seq": 4, "status": "completed", "wns": -0.8},
    ]
    trials = [
        trial(-0.3, accepted=True, seq=2, failure_events=[{"hard_gate": True}]),
        trial(-0.2, accepted=True, skipped_duplicate=True, sta_executed=False, cached_from_seq=2),
        trial(-1.0, sta_executed=False, failure_events=[{"hard_gate": True}]),
        trial(-0.8, accepted=True, seq=4, failure_events=[]),
    ]
    result = summarize(trials, launch_events=events)
    assert result["n_new_sta_runs"] == 3
    assert result["n_candidate_evaluation_records"] == 4
    assert result["n_cache_replays"] == 1
    assert result["best_wns_curve"] == pytest.approx([0.7, 0.7, 0.7])
    assert result["best_valid_wns_curve"] == pytest.approx([0.0, 0.0, 0.2])
    assert result["n_sta_to_first_improvement"] == 1
    assert result["n_sta_to_first_valid_improvement"] == 3
    assert result["sta_ledger_schema"]["source"] == "launch_events"


def test_legacy_fallback_excludes_replayed_provenance_and_invalid_results():
    provenance = {"tool": "OpenSTA", "report_path": "candidate/sta.log"}
    trials = [
        trial(-1.2, sta_provenance=provenance),
        trial(-0.4, sta_provenance=provenance, skipped_duplicate=True),
        trial(float("nan"), sta_provenance=provenance),
        trial(-0.6),
        trial(-0.8, accepted=True, sta_provenance={"tool": "OpenSTA", "report_path": "second/sta.log"}),
    ]
    result = summarize(trials)
    assert result["n_new_sta_runs"] == 2
    assert result["n_candidate_evaluation_records"] == 5
    assert result["n_cache_replays"] == 1
    assert result["best_wns_curve"] == pytest.approx([0.0, 0.2])
    assert result["best_valid_wns_curve"] == pytest.approx([0.0, 0.2])
    assert result["n_sta_to_first_improvement"] == 2
    assert result["sta_ledger_schema"]["source"] == "historical_trial_provenance"


def test_empty_event_table_is_authoritative_and_does_not_fall_back():
    result = summarize([trial(-0.5, accepted=True, sta_provenance={"tool": "OpenSTA"})], launch_events=[])
    assert result["n_new_sta_runs"] == 0
    assert result["best_wns_curve"] == result["best_valid_wns_curve"] == []
    assert result["n_sta_to_first_improvement"] is None


def test_event_aliases_and_sequence_order_override_trial_order():
    events = [{"phase": "candidate_ideal", "sta_launch_seq": 9},
              {"kind": "candidate_ideal", "seq": 3}]
    trials = [trial(-0.4, accepted=True, seq=9), trial(-0.9, accepted=True, seq=3)]
    result = summarize(trials, launch_events=events)
    assert result["best_wns_curve"] == pytest.approx([0.1, 0.6])
    assert result["n_new_sta_runs"] == 2


def test_event_wns_is_the_ideal_observation_not_trial_placeholder():
    result = summarize([trial(-1.0, accepted=True, seq=1)],
                       launch_events=[{"kind": "candidate_ideal", "seq": 1, "status": "completed", "wns": -0.4}])
    assert result["best_wns_curve"] == pytest.approx([0.6])
    assert result["best_valid_wns_curve"] == pytest.approx([0.6])


@pytest.mark.parametrize("event_fields", [{"status": "timeout"}, {"timeout": True},
                                         {"status": "error"}, {"error": "STA failed"},
                                         {"status": "running"}])
def test_incomplete_or_failed_launches_consume_k_without_observation(event_fields):
    events = [{"kind": "candidate_ideal", "seq": 1, "wns": 0.5, **event_fields}]
    result = summarize([trial(0.5, accepted=True, seq=1)], launch_events=events)
    assert result["n_new_sta_runs"] == 1
    assert result["best_wns_curve"] == result["best_valid_wns_curve"] == [0.0]
    assert result["n_sta_to_first_improvement"] is None


def test_missing_and_nonfinite_event_results_still_consume_k():
    events = [{"kind": "candidate_ideal", "seq": 1, "wns": None},
              {"kind": "candidate_ideal", "seq": 2, "wns": float("inf")}]
    result = summarize([trial(0.8, accepted=True, seq=1)], launch_events=events)
    assert result["n_new_sta_runs"] == 2
    assert result["best_wns_curve"] == [0.0, 0.0]


@pytest.mark.parametrize("fields", [
    {"failure_events": [{"hard_gate": True}]},
    {"trial_failure_events": [{"severity": "hard"}]},
    {"acceptance_evidence": {"violations": ["setup_tns"], "unavailable": []}},
    {"acceptance_evidence": {"violations": [], "unavailable": ["hold_min_slack"]}},
    {"failure_events": "malformed"},
    {"acceptance_evidence": {"passed": False}},
])
def test_valid_curve_fails_closed_on_explicit_or_malformed_failure_evidence(fields):
    result = summarize([trial(-0.5, accepted=True, seq=1, **fields)],
                       launch_events=[{"kind": "candidate_ideal", "seq": 1}])
    assert result["best_wns_curve"] == [0.5]
    assert result["best_valid_wns_curve"] == [0.0]


@pytest.mark.parametrize("accepted", [False, None, 1, "true"])
def test_eligibility_or_truthy_flags_do_not_imply_submission(accepted):
    result = summarize([trial(-0.5, accepted=accepted, seq=1,
                              acceptance_evidence={"passed": True, "violations": [], "unavailable": []})],
                       launch_events=[{"kind": "candidate_ideal", "seq": 1}])
    assert result["best_wns_curve"] == [0.5]
    assert result["best_valid_wns_curve"] == [0.0]


def test_a_cache_record_cannot_become_a_new_valid_observation():
    result = summarize([trial(-0.2, accepted=True, seq=1, skipped_duplicate=True,
                              sta_executed=False, cached_from_seq=1)],
                       launch_events=[{"kind": "candidate_ideal", "seq": 1, "wns": -0.2}])
    assert result["n_new_sta_runs"] == 1  # the original launch remains in the authoritative ledger
    assert result["n_cache_replays"] == 1
    assert result["best_wns_curve"] == [0.8]
    assert result["best_valid_wns_curve"] == [0.0]


@pytest.mark.parametrize("baseline", [None, True, float("nan"), float("inf"), "-1"])
def test_baseline_must_be_a_finite_number(baseline):
    with pytest.raises(ValueError, match="baseline"):
        summarize([], baseline=baseline)


@pytest.mark.parametrize("events", [
    [{"kind": "candidate_ideal", "seq": 1}, {"kind": "candidate_ideal", "seq": 1}],
    [{"kind": "candidate_ideal", "seq": 0}],
    [{"kind": "candidate_ideal", "seq": True}],
    [{"kind": "candidate_ideal"}],
    [{"kind": "candidate_ideal", "seq": 1, "sta_launch_seq": 2}],
])
def test_invalid_launch_identity_cannot_silently_change_the_count(events):
    with pytest.raises(ValueError, match="launch"):
        summarize([], launch_events=events)


def test_inputs_are_not_mutated():
    trials = [trial(-0.5, accepted=True, seq=2)]
    events = [{"kind": "candidate_ideal", "seq": 2}]
    summarize(trials, launch_events=events)
    assert trials == [trial(-0.5, accepted=True, seq=2)]
    assert events == [{"kind": "candidate_ideal", "seq": 2}]


def test_conflicting_noncache_trial_links_are_not_silently_overwritten():
    events = [{"kind": "candidate_ideal", "seq": 1, "wns": -0.5}]
    trials = [trial(-0.5, accepted=True, seq=1),
              trial(-0.5, accepted=False, seq=1, failure_events=[{"hard_gate": True}])]
    with pytest.raises(ValueError, match="trial.*launch"):
        summarize(trials, launch_events=events)


def test_physical_failure_cannot_enter_the_submitted_curve():
    result = summarize([trial(-0.5, accepted=True, seq=1, physical_failure=True)],
                       launch_events=[{"kind": "candidate_ideal", "seq": 1}])
    assert result["best_wns_curve"] == [0.5]
    assert result["best_valid_wns_curve"] == [0.0]


@pytest.mark.parametrize("committed", [False, None, 1, "true"])
def test_inner_selection_without_explicit_commit_cannot_enter_valid_curve(committed):
    result = summarize([trial(-0.5, accepted=True, seq=1, committed=committed)],
                       launch_events=[{"kind": "candidate_ideal", "seq": 1}])
    assert result["best_wns_curve"] == [0.5]
    assert result["best_valid_wns_curve"] == [0.0]
    assert result["n_sta_to_first_valid_improvement"] is None


def test_explicit_commit_contributes_to_the_valid_curve():
    result = summarize([trial(-0.5, accepted=True, seq=1, committed=True)],
                       launch_events=[{"kind": "candidate_ideal", "seq": 1}])
    assert result["best_valid_wns_curve"] == [0.5]
    assert result["n_sta_to_first_valid_improvement"] == 1
