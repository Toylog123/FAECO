"""Failure classification for failure-aware ECO refinement."""

from dataclasses import dataclass
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
