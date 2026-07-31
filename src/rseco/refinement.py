"""Failure-aware search-weight refinement for the FAECO prototype."""

from dataclasses import dataclass

from .failures import FailureType


@dataclass(frozen=True)
class RefinementWeights:
    """Search priorities consumed by a future weighted cut implementation."""

    boundary_penalty: float = 1.0
    size_penalty: float = 1.0
    critical_coverage_reward: float = 1.0
    verification_cost_penalty: float = 1.0
    equivalence_stability_reward: float = 1.0
    max_cone_gates: int = 1000


@dataclass(frozen=True)
class RefinementDecision:
    """Updated weights and their ordered, auditable feedback actions."""

    weights: RefinementWeights
    actions: list[str]


def refine_weights(
    weights: RefinementWeights,
    failures: set[FailureType],
) -> RefinementDecision:
    """Apply the fixed first-version F1-F5 feedback rules to search weights."""
    boundary_penalty = weights.boundary_penalty
    size_penalty = weights.size_penalty
    critical_coverage_reward = weights.critical_coverage_reward
    verification_cost_penalty = weights.verification_cost_penalty
    equivalence_stability_reward = weights.equivalence_stability_reward
    max_cone_gates = weights.max_cone_gates
    actions: list[str] = []

    if FailureType.EQUIVALENCE in failures:
        boundary_penalty += 1.0
        equivalence_stability_reward += 1.0
        actions.extend(
            ["increase_boundary_penalty", "increase_equivalence_stability_reward"]
        )
    if FailureType.BOUNDARY_INVALID in failures:
        boundary_penalty += 1.0
        actions.append("increase_boundary_penalty")
    if FailureType.PATCH_TOO_LARGE in failures:
        size_penalty += 1.0
        actions.append("increase_size_penalty")
    if FailureType.TIMING_GAIN_INSUFFICIENT in failures:
        critical_coverage_reward += 1.0
        actions.append("increase_critical_coverage_reward")
    if FailureType.VERIFICATION_TOO_EXPENSIVE in failures:
        verification_cost_penalty += 1.0
        max_cone_gates = max(1, max_cone_gates // 2)
        actions.extend(["increase_verification_cost_penalty", "reduce_max_cone_gates"])

    return RefinementDecision(
        weights=RefinementWeights(
            boundary_penalty=boundary_penalty,
            size_penalty=size_penalty,
            critical_coverage_reward=critical_coverage_reward,
            verification_cost_penalty=verification_cost_penalty,
            equivalence_stability_reward=equivalence_stability_reward,
            max_cone_gates=max_cone_gates,
        ),
        actions=actions,
    )
