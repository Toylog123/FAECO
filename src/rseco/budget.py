"""Budget kinds, cost events, and distinct stop reasons."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BudgetKind(str, Enum):
    SOFT_COST_OVER_LIMIT = "soft_cost_over_limit"
    CANDIDATE_HARD_TIMEOUT = "candidate_hard_timeout"
    CAMPAIGN_WALL = "campaign_wall"
    STA_COUNT = "sta_count"
    FORMAL_COUNT = "formal_count"


@dataclass(frozen=True)
class CostEvent:
    kind: BudgetKind
    message: str
    measured_s: float


@dataclass
class BudgetState:
    candidate_timeout_s: float = 300.0
    campaign_wall_timeout_s: float = 0.0
    sta_budget: int = 2000
    formal_budget: int = 200
    events: list[CostEvent] = None

    def __post_init__(self) -> None:
        if self.events is None:
            self.events = []

    def record(self, event: CostEvent) -> None:
        self.events.append(event)


def stop_reason_for(state: BudgetState) -> str | None:
    if any(e.kind == BudgetKind.CANDIDATE_HARD_TIMEOUT for e in state.events):
        return "candidate_hard_timeout"
    if state.campaign_wall_timeout_s > 0 and any(
        e.kind == BudgetKind.CAMPAIGN_WALL for e in state.events
    ):
        return "campaign_wall_exhausted"
    if state.sta_budget <= 0:
        return "sta_budget_exhausted"
    if state.formal_budget <= 0:
        return "formal_budget_exhausted"
    return None
