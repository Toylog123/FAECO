# Multi-iteration failure-aware refinement loop (X19).
#
# flow.py currently performs a single refinement proxy: it calls
# refine_weights once and records one iteration.  This module implements the
# real loop: cut -> classify -> refine weights -> re-cut, until a candidate
# succeeds or max_iterations is reached.
#
# The loop is deliberately decoupled from any concrete cut implementation:
# callers pass an evaluator callback (failures, weights) -> (success, patch_id),
# which makes it unit-testable without Yosys/OpenSTA.

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .failures import FailureType
from .refinement import RefinementWeights, refine_weights


@dataclass(frozen=True)
class RefinementConfig:
    # Maximum refinement iterations (default matches faeco_algorithm.md).
    max_iterations: int = 10


def simulate_refinement_loop(
    evaluator: Callable[[set[FailureType], RefinementWeights], tuple[bool, str | None]],
    config: RefinementConfig | None = None,
    *,
    on_refine: Callable[[list[str]], None] | None = None,
    enable_feedback: bool = True,
) -> dict:
    """Run the failure-aware refinement loop.

    evaluator(failures, weights) returns (success, patch_id).  On failure the
    loop classifies the failure set and (if enable_feedback) calls
    refine_weights, then re-invokes the evaluator with updated weights.
    enable_feedback=False is the ablation control: weights stay fixed.
    """
    config = config or RefinementConfig()
    weights = RefinementWeights()
    history: list[dict] = []
    actions_history: list[list[str]] = []

    for iteration in range(1, config.max_iterations + 1):
        failures: set[FailureType] = set()
        success, patch_id = evaluator(failures, weights)
        if success:
            history.append(
                {
                    "iteration": iteration,
                    "status": "success",
                    "patch_id": patch_id,
                    "actions": [],
                }
            )
            return {
                "success": True,
                "iterations": iteration,
                "final_patch_id": patch_id,
                "history": history,
                "weights": weights,
            }
        decision = refine_weights(weights, failures) if enable_feedback else None
        if decision is not None:
            weights = decision.weights
            actions = decision.actions
        else:
            actions = []
        if on_refine is not None and enable_feedback:
            on_refine(actions)
        actions_history.append(actions)
        history.append(
            {
                "iteration": iteration,
                "status": "refined",
                "actions": actions,
                "failures": sorted(f.value for f in failures),
            }
        )

    return {
        "success": False,
        "iterations": config.max_iterations,
        "final_patch_id": None,
        "history": history,
        "actions_history": actions_history,
        "weights": weights,
    }
