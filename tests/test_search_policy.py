"""fast/balanced/exhaustive must have explicit, testable semantics."""

from __future__ import annotations

from rseco.runspec import RunSpec
from rseco.search_policy import SearchPolicy, SearchPolicyConfig, map_legacy_early_stop


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
