"""Soft cost events must not invalidate completed candidates."""

from __future__ import annotations

from rseco.budget import (
    BudgetKind,
    BudgetState,
    CostEvent,
    stop_reason_for,
)


def test_soft_cost_does_not_change_stop_reason() -> None:
    state = BudgetState(campaign_wall_timeout_s=60.0)
    state.record(CostEvent(BudgetKind.SOFT_COST_OVER_LIMIT, "b17-like", measured_s=113.0))
    assert stop_reason_for(state) is None


def test_hard_candidate_timeout_has_own_stop_reason() -> None:
    state = BudgetState(candidate_timeout_s=60.0)
    state.record(CostEvent(BudgetKind.CANDIDATE_HARD_TIMEOUT, "timed out", measured_s=60.0))
    assert stop_reason_for(state) == "candidate_hard_timeout"


def test_budgets_have_distinct_reasons() -> None:
    wall = BudgetState(campaign_wall_timeout_s=1.0)
    wall.record(CostEvent(BudgetKind.CAMPAIGN_WALL, "wall", 1.0))
    assert stop_reason_for(wall) == "campaign_wall_exhausted"
    assert stop_reason_for(BudgetState(sta_budget=0)) == "sta_budget_exhausted"
    assert stop_reason_for(BudgetState(formal_budget=0)) == "formal_budget_exhausted"
