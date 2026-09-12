"""Tests for WNS-aware success criterion in the refinement loop."""

from __future__ import annotations

from rseco.refinement_loop import RefinementConfig, simulate_refinement_loop
from rseco.failures import FailureType


def test_timing_aware_loop_succeeds_when_wns_improves() -> None:
    """A loop whose evaluator accepts when the (fake) WNS improves should
    succeed and record the improved wns."""
    wns_series = iter([-1.5, -1.2, -0.9])
    wns_history = []

    def eval_fn(failures, weights):
        wns = next(wns_series)
        wns_history.append(wns)
        failures.add(FailureType.TIMING_GAIN_INSUFFICIENT)
        # succeed once WNS crosses -1.0 (improvement threshold)
        if wns >= -1.0:
            return True, "patch_ok"
        return False, None

    result = simulate_refinement_loop(eval_fn, RefinementConfig(max_iterations=5))
    assert result["success"] is True
    assert result["iterations"] == 3
    assert result["final_patch_id"] == "patch_ok"
    assert len(wns_history) == 3


def test_loop_stops_immediately_on_first_success() -> None:
    """The loop must stop at the first success without extra refinement
    iterations (WNS criterion reached on iteration 1)."""
    calls = {"n": 0}

    def eval_fn(failures, weights):
        calls["n"] += 1
        return True, "patch_first"

    result = simulate_refinement_loop(eval_fn, RefinementConfig(max_iterations=5))
    assert result["success"] is True
    assert result["iterations"] == 1
    assert calls["n"] == 1
    assert result["final_patch_id"] == "patch_first"
