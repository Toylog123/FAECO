"""Search policy semantics and legacy early-stop mapping."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from rseco.runspec import RunSpec


class SearchPolicy(str, Enum):
    FAST = "fast"
    BALANCED = "balanced"
    EXHAUSTIVE = "exhaustive"


@dataclass(frozen=True)
class SearchPolicyConfig:
    policy: SearchPolicy
    min_validated_per_family: int
    joint_quota: int

    @classmethod
    def from_run_spec(cls, spec: RunSpec) -> "SearchPolicyConfig":
        return cls(
            policy=SearchPolicy(spec.search_policy),
            min_validated_per_family=spec.balanced_min_validated_per_family,
            joint_quota=spec.balanced_joint_quota,
        )


@dataclass(frozen=True)
class CoverageState:
    total_generated: int
    validated: int

    @property
    def partial(self) -> bool:
        return self.validated < self.total_generated

    @property
    def is_exhaustive_result(self) -> bool:
        return not self.partial


def map_legacy_early_stop(value: bool, warn) -> SearchPolicy:
    if value:
        warn("--early-stop is deprecated; use --search-policy fast")
        return SearchPolicy.FAST
    return SearchPolicy.BALANCED


def resolve_search_policy(
    early_stop: bool, search_policy: str = "balanced", warn=None
) -> SearchPolicy:
    """Resolve the explicit policy, honoring the deprecated boolean alias."""
    if early_stop:
        if warn is not None:
            warn("--early-stop is deprecated; use --search-policy fast")
        if search_policy == "balanced":
            return SearchPolicy.FAST
    return SearchPolicy(search_policy)


def round_coverage(validated: int, generated: int, stopped_early: bool) -> dict:
    """Coverage accounting for one candidate round (design 4.4)."""
    partial = validated < generated
    reason = (
        "first_acceptable"
        if stopped_early
        else ("budget_partial" if partial else "round_complete")
    )
    return {
        "validated": validated,
        "generated": generated,
        "partial": partial,
        "round_stop_reason": reason,
    }
