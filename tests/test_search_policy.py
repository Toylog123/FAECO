"""fast/balanced/exhaustive must have explicit, testable semantics."""

from __future__ import annotations

from rseco.runspec import RunSpec
from rseco.search_policy import (
    SearchPolicy,
    SearchPolicyConfig,
    map_legacy_early_stop,
    resolve_search_policy,
    round_coverage,
)


def test_balanced_requires_coverage() -> None:
    config = SearchPolicyConfig.from_run_spec(RunSpec.defaults())
    assert config.policy == SearchPolicy.BALANCED
    assert config.min_validated_per_family == 3
    assert config.joint_quota == 2


def test_legacy_early_stop_maps_to_fast() -> None:
    warnings: list[str] = []

    def warn(msg: str) -> None:
        warnings.append(msg)

    policy = map_legacy_early_stop(True, warn=warn)
    assert policy == SearchPolicy.FAST
    assert warnings and "deprecated" in warnings[0]


def test_exhaustive_can_report_partial() -> None:
    from rseco.search_policy import CoverageState

    state = CoverageState(total_generated=10, validated=6)
    assert state.partial
    assert state.is_exhaustive_result is False


def test_resolve_policy_fast_from_early_stop() -> None:
    warnings: list[str] = []
    policy = resolve_search_policy(early_stop=True, search_policy="balanced", warn=warnings.append)
    assert policy == SearchPolicy.FAST
    assert warnings and "deprecated" in warnings[0]


def test_resolve_policy_explicit_search_policy_wins() -> None:
    policy = resolve_search_policy(early_stop=True, search_policy="exhaustive", warn=lambda m: None)
    assert policy == SearchPolicy.EXHAUSTIVE


def test_round_coverage_records_partial() -> None:
    cov = round_coverage(validated=6, generated=10, stopped_early=False)
    assert cov["validated"] == 6
    assert cov["generated"] == 10
    assert cov["partial"] is True
    assert cov["round_stop_reason"] == "budget_partial"


def test_round_coverage_fast_first_acceptable() -> None:
    cov = round_coverage(validated=3, generated=10, stopped_early=True)
    assert cov["partial"] is True
    assert cov["round_stop_reason"] == "first_acceptable"


def test_round_coverage_complete() -> None:
    cov = round_coverage(validated=10, generated=10, stopped_early=False)
    assert cov["partial"] is False
    assert cov["round_stop_reason"] == "round_complete"
