"""Tests for the multi-iteration failure-aware refinement loop (X19)."""

from __future__ import annotations

import pytest

from rseco.refinement_loop import (
    RefinementConfig,
    simulate_refinement_loop,
)


def test_loop_runs_until_success() -> None:
    """With a simulated evaluator that succeeds on iteration 3, the loop
    records 3 iterations and stops with success."""
    calls = {"n": 0}

    def fake_eval(failures, weights):
        calls["n"] += 1
        if calls["n"] >= 3:
            return True, "ok_patch"
        return False, None

    config = RefinementConfig(max_iterations=5)
    result = simulate_refinement_loop(fake_eval, config)
    assert result["success"] is True
    assert result["iterations"] == 3
    assert result["final_patch_id"] == "ok_patch"
    assert len(result["history"]) == 3


def test_loop_stops_at_max_iterations() -> None:
    """An evaluator that never succeeds stops at max_iterations."""
    def fake_eval(failures, weights):
        return False, None

    config = RefinementConfig(max_iterations=4)
    result = simulate_refinement_loop(fake_eval, config)
    assert result["success"] is False
    assert result["iterations"] == 4


def test_loop_tracks_weights_changes() -> None:
    """Each failed iteration calls refine_weights and records actions."""
    from rseco.failures import FailureType
    from rseco.refinement import RefinementWeights

    seen_actions: list[list[str]] = []

    def fake_eval(failures, weights):
        # force F1-equivalence failure every time until success on 2nd
        if len(seen_actions) == 0:
            failures.add(FailureType.EQUIVALENCE)
            return False, None
        return True, "patch_final"

    config = RefinementConfig(max_iterations=3)
    result = simulate_refinement_loop(fake_eval, config, on_refine=seen_actions.append)
    assert result["success"] is True
    # first iteration should have produced an F1 action
    assert len(seen_actions) >= 1
    assert "increase_boundary_penalty" in seen_actions[0]

