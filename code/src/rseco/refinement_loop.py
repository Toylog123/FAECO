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
    init_weights: dict | None = None,
) -> dict:
    """Run the failure-aware refinement loop.

    evaluator(failures, weights) returns (success, patch_id).  On failure the
    loop classifies the failure set and (if enable_feedback) calls
    refine_weights, then re-invokes the evaluator with updated weights.
    enable_feedback=False is the ablation control: weights stay fixed.
    """
    config = config or RefinementConfig()
    weights = RefinementWeights()
    if init_weights:
        weights = RefinementWeights(
            boundary_penalty=float(init_weights.get("boundary_penalty", weights.boundary_penalty)),
            size_penalty=float(init_weights.get("size_penalty", weights.size_penalty)),
            critical_coverage_reward=float(init_weights.get("critical_coverage_reward", weights.critical_coverage_reward)),
            verification_cost_penalty=float(init_weights.get("verification_cost_penalty", weights.verification_cost_penalty)),
            equivalence_stability_reward=float(init_weights.get("equivalence_stability_reward", weights.equivalence_stability_reward)),
            max_cone_gates=int(init_weights.get("max_cone_gates", weights.max_cone_gates)),
        )
    history: list[dict] = []
    actions_history: list[list[str]] = []

    for iteration in range(1, config.max_iterations + 1):
        failures: set[FailureType] = set()
        evaluated = evaluator(failures, weights)
        if isinstance(evaluated, tuple) and len(evaluated) == 3:
            success, patch_id, extra = evaluated
        else:
            success, patch_id = evaluated
            extra = None
        if success:
            history.append(
                {
                    "iteration": iteration,
                    "status": "success",
                    "patch_id": patch_id,
                    "wns": extra.get("wns") if extra else None,
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
                "wns": extra.get("wns") if extra else None,
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