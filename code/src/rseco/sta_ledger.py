"""Separate candidate evaluation records, new ideal-STA launches, and submissions.

Launch events are the authority when provided (including an empty list).
Historical provenance is a limited fallback: it cannot charge unknown timeouts
or reconstruct executions whose result/source fields were never recorded.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
import math
from numbers import Real


def _finite(value: object) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value)


def _cache_replay(trial: Mapping) -> bool:
    return (trial.get("skipped_duplicate") is True
            or (trial.get("sta_executed") is False and trial.get("cached_from_seq") is not None))


def _submitted_without_hard_failure(trial: Mapping | None) -> bool:
    # Eligibility is weaker than submission; a 'passed' check does not replace
    # an explicit acceptance flag. Malformed failure evidence fails closed.
    if (trial is None or trial.get("accepted") is not True
            or trial.get("hard_gate") or trial.get("physical_failure")):
        return False
    # Inner evaluator selection is not sufficient when the outer-loop commit
    # field is available (a cone refresh or submission gate may still fail).
    if "committed" in trial and trial["committed"] is not True:
        return False
    for name in ("failure_events", "trial_failure_events"):
        events = trial.get(name, [])
        if events is None:
            events = []
        if not isinstance(events, (list, tuple)):
            return False
        for event in events:
            if not isinstance(event, Mapping):
                return False
            if event.get("hard_gate") or event.get("severity") == "hard":
                return False
    evidence = trial.get("acceptance_evidence")
    if evidence is not None:
        if not isinstance(evidence, Mapping):
            return False
        if evidence.get("passed") is False:
            return False
        for name in ("violations", "unavailable"):
            values = evidence.get(name, [])
            if not isinstance(values, (list, tuple)) or values:
                return False
    return True


def _launch_sequence(event: Mapping) -> int:
    seq = event.get("seq", event.get("sta_launch_seq"))
    if ("seq" in event and "sta_launch_seq" in event
            and event["seq"] != event["sta_launch_seq"]):
        raise ValueError("launch sequence aliases disagree")
    if not isinstance(seq, int) or isinstance(seq, bool) or seq <= 0:
        raise ValueError("candidate launch sequence must be a positive integer")
    return seq


def _launch_observation(event: Mapping, trial: Mapping | None) -> float | None:
    if (event.get("timeout") or event.get("error")
            or event.get("status") in {"running", "error", "timeout"}):
        return None
    # The event records the actual ideal-net result. A trial may subsequently
    # carry a baseline placeholder after another gate rejected the candidate.
    value = event["wns"] if "wns" in event else (trial.get("wns") if trial else None)
    return float(value) if _finite(value) else None


def summarize_sta_ledger(
    trials: Iterable[Mapping],
    baseline: float,
    launch_events: Iterable[Mapping] | None = None,
) -> dict:
    """Return accounting and two gain curves relative to the initial baseline.

    Canonical events use ``kind='candidate_ideal', seq=<positive int>``;
    ``phase`` and ``sta_launch_seq`` are accepted aliases. Trials associate via
    ``sta_launch_seq``. Other launch kinds do not consume candidate k. Events
    sort by sequence; timeout/error/incomplete launches still consume k and
    keep the previous best. Event WNS takes precedence over trial WNS.

    ``best_wns_curve`` is observed best ideal gain, including unselected or
    rejected candidates. ``best_valid_wns_curve`` admits only measured trials
    explicitly marked ``accepted is True`` without hard/invalid evidence and,
    when present, ``committed is True``. Historical records without committed
    retain an accepted-only fallback (inner selection may not be submission).
    This trajectory is not a proof of final SEC.
    Both retain the no-modification option (zero). Cache results never add k
    or independently qualify for the submitted trajectory.

    With no events, only finite non-cache trials carrying nonempty provenance
    are counted. Missing-source historical runs cannot be interpreted as zero
    physical executions; this fallback reports identifiable finite records.
    """
    if not _finite(baseline):
        raise ValueError("baseline must be a finite number")
    baseline = float(baseline)
    records = list(trials)
    if any(not isinstance(trial, Mapping) for trial in records):
        raise ValueError("trial records must be mappings")
    cache_count = sum(_cache_replay(trial) for trial in records)
    sequence: list[tuple[float | None, Mapping | None]] = []
    if launch_events is not None:
        launches = {}
        for event in launch_events:
            if not isinstance(event, Mapping):
                raise ValueError("launch events must be mappings")
            if event.get("kind", event.get("phase")) != "candidate_ideal":
                continue
            seq = _launch_sequence(event)
            if seq in launches:
                raise ValueError("candidate launch sequence is duplicated")
            launches[seq] = event
        linked = {}
        for trial in records:
            if _cache_replay(trial) or trial.get("sta_executed") is False:
                continue
            seq = trial.get("sta_launch_seq")
            if isinstance(seq, int) and not isinstance(seq, bool) and seq in launches:
                if seq in linked:
                    raise ValueError("multiple noncache trial records link to one launch")
                linked[seq] = trial
        for seq in sorted(launches):
            trial = linked.get(seq)
            sequence.append((_launch_observation(launches[seq], trial), trial))
        source = "launch_events"
        k_unit = "new_candidate_ideal_sta_launch_including_failed_launches"
    else:
        for trial in records:
            provenance = trial.get("sta_provenance")
            if (_cache_replay(trial) or trial.get("sta_executed") is False
                    or not isinstance(provenance, Mapping) or not provenance
                    or not _finite(trial.get("wns"))):
                continue
            sequence.append((float(trial["wns"]), trial))
        source = "historical_trial_provenance"
        k_unit = "identifiable_finite_noncache_candidate_sta_result"

    observed_curve = []
    valid_curve = []
    best_observed = best_valid = 0.0
    first_observed = first_valid = None
    for k, (wns, trial) in enumerate(sequence, 1):
        if wns is not None:
            gain = wns - baseline
            best_observed = max(best_observed, gain)
            if _submitted_without_hard_failure(trial):
                best_valid = max(best_valid, gain)
        observed_curve.append(best_observed)
        valid_curve.append(best_valid)
        if first_observed is None and best_observed > 0:
            first_observed = k
        if first_valid is None and best_valid > 0:
            first_valid = k
    return {
        "n_new_sta_runs": len(sequence),
        "n_candidate_evaluation_records": len(records),
        "n_cache_replays": cache_count,
        "best_wns_curve": observed_curve,
        "best_valid_wns_curve": valid_curve,
        "n_sta_to_first_improvement": first_observed,
        "n_sta_to_first_valid_improvement": first_valid,
        "sta_ledger_schema": {
            "version": "r22_sta_ledger_v1",
            "source": source,
            "k_unit": k_unit,
            "baseline": "initial_run_baseline_wns",
            "observed_curve": "best_measured_candidate_ideal_gain_including_rejected_candidates",
            "valid_curve": "measured_accepted_and_explicitly_committed_when_recorded_without_hard_failure",
            "legacy_valid_limit": "accepted-only fallback may reflect inner selection rather than outer submission",
            "historical_limit": "fallback cannot count missing-source or failed nonfinite executions",
        },
    }
