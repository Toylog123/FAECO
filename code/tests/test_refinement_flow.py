"""Tests for the multi-iteration refinement flow (X19)."""

from __future__ import annotations

from rseco.refinement_loop import RefinementConfig, simulate_refinement_loop
from rseco.failures import FailureType


def test_flow_multi_iteration_returns_history() -> None:
    """The X19 loop returns iteration history even when it fails (no success)."""
    def never(failures, weights):
        failures.add(FailureType.TIMING_GAIN_INSUFFICIENT)
        return False, None

    result = simulate_refinement_loop(never, RefinementConfig(max_iterations=3))
    assert result["success"] is False
    assert result["iterations"] == 3
    assert len(result["history"]) == 3
    assert all(h["status"] == "refined" for h in result["history"])


def test_flow_multi_iteration_records_actions() -> None:
    """F4 (timing gain insufficient) should trigger critical-coverage reward."""
    def f4(failures, weights):
        failures.add(FailureType.TIMING_GAIN_INSUFFICIENT)
        return False, None

    result = simulate_refinement_loop(f4, RefinementConfig(max_iterations=2))
    actions = [a for h in result["history"] for a in h["actions"]]
    assert "increase_critical_coverage_reward" in actions

