"""Failure classification for failure-aware ECO refinement."""

from dataclasses import dataclass, field
from typing import Any
from enum import Enum

from .metrics import change_ratio, logic_level_reduction


class FailureType(str, Enum):
    EQUIVALENCE = "F1_equivalence_failure"
    BOUNDARY_INVALID = "F2_boundary_invalid"
    PATCH_TOO_LARGE = "F3_patch_too_large"
    TIMING_GAIN_INSUFFICIENT = "F4_timing_gain_insufficient"
    VERIFICATION_TOO_EXPENSIVE = "F5_verification_too_expensive"
    PHYSICAL_LOAD_FAILURE = "F6_physical_load_failure"


@dataclass(frozen=True)
class FailureEvent:
    """One measured, auditable failure in the F1--F6 taxonomy.

    ``evidence`` stores tool reports/checker provenance rather than a boolean
    inferred from a search weight.  ``severity=hard`` is consumed by the
    acceptance predicate for F1/F2/F3/F5.
    """

    type: FailureType | str
    candidate_hash: str
    cut_hash: str
    endpoint: str | None = None
    path: list[str] = field(default_factory=list)
    net: str | None = None
    action_scope: list[str] = field(default_factory=list)
    threshold: Any = None
    observed_value: Any = None
    severity: str = "hard"
    runtime_s: float = 0.0
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value if isinstance(self.type, FailureType) else str(self.type),
            "candidate_hash": self.candidate_hash,
            "cut_hash": self.cut_hash,
            "endpoint": self.endpoint,
            "path": list(self.path),
            "net": self.net,
            "action_scope": list(self.action_scope),
            "threshold": self.threshold,
            "observed_value": self.observed_value,
            "severity": self.severity,
            "runtime_s": self.runtime_s,
            "evidence": dict(self.evidence),
        }


@dataclass(frozen=True)
class AcceptanceEvidence:
    """Metrics and backend provenance consumed by the acceptance predicate."""

    setup_wns: float | None = None
    setup_tns: float | None = None
    hold_min_slack: float | None = None
    area: float | None = None
    max_transition: float | None = None
    max_capacitance: float | None = None
    max_fanout: float | None = None
    backend_provenance: dict[str, Any] = field(default_factory=dict)
    unavailable: tuple[str, ...] = ()
    violations: tuple[str, ...] = ()
    epsilon: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "setup_wns": self.setup_wns, "setup_tns": self.setup_tns,
            "hold_min_slack": self.hold_min_slack, "area": self.area,
            "max_transition": self.max_transition,
            "max_capacitance": self.max_capacitance, "max_fanout": self.max_fanout,
            "backend_provenance": dict(self.backend_provenance),
            "unavailable": list(self.unavailable), "violations": list(self.violations),
            "epsilon": self.epsilon,
        }

    @property
    def admissible(self) -> bool:
        return not self.unavailable and not self.violations


@dataclass(frozen=True)
class FailureThresholds:
    max_patch_ratio: float = 0.15
    min_logic_level_reduction: int = 1
    max_verification_time_s: float = 60.0


def classify_failures(
    *,
    equivalence_passed: bool,
    boundary_closed: bool,
    patch_size: int,
    original_gate_count: int,
    logic_level_before: int,
    logic_level_after: int,
    verification_runtime_s: float,
    thresholds: FailureThresholds | None = None,
) -> set[FailureType]:
    """Classify a candidate patch into zero or more FAECO failure types."""
    thresholds = thresholds or FailureThresholds()
    failures: set[FailureType] = set()

    if not equivalence_passed:
        failures.add(FailureType.EQUIVALENCE)
    if not boundary_closed:
        failures.add(FailureType.BOUNDARY_INVALID)
    if change_ratio(patch_size, original_gate_count) > thresholds.max_patch_ratio:
        failures.add(FailureType.PATCH_TOO_LARGE)
    if logic_level_reduction(logic_level_before, logic_level_after) < thresholds.min_logic_level_reduction:
        failures.add(FailureType.TIMING_GAIN_INSUFFICIENT)
    if verification_runtime_s > thresholds.max_verification_time_s:
        failures.add(FailureType.VERIFICATION_TOO_EXPENSIVE)

    return failures
