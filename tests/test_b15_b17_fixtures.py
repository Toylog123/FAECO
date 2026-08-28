"""b15 and b17 quality-cost contracts without running full benchmarks."""

from __future__ import annotations

from rseco.acceptance import CandidateMetrics, DefaultAcceptancePolicy
from rseco.budget import BudgetKind, BudgetState, CostEvent
from rseco.runspec import RunSpec
from rseco.search_policy import CoverageState


def test_b15_quality_cost_tradeoff_is_structural() -> None:
    fast_stops_early = CoverageState(total_generated=12, validated=1)
    exhaustive = CoverageState(total_generated=12, validated=12)
    assert fast_stops_early.partial
    assert exhaustive.is_exhaustive_result
    assert exhaustive.validated > fast_stops_early.validated


def test_b17_soft_cost_does_not_invalidate_accepted_candidate() -> None:
    state = BudgetState(candidate_timeout_s=180.0)
    state.record(CostEvent(BudgetKind.SOFT_COST_OVER_LIMIT, "STA 113s > 60s soft cap", 113.0))
    policy = DefaultAcceptancePolicy(RunSpec.defaults(), baseline_wns=-16.53)
    verdict = policy.evaluate(
        CandidateMetrics(
            candidate_hash="b17_iter1_joint",
            setup_wns=-16.10,
            setup_tns=-1.0,
            patch_ratio=0.001,
            required_ok=True,
        )
    )
    assert verdict.accepted
