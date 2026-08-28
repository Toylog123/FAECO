"""Pure acceptance policy and deterministic candidate ranking."""

from __future__ import annotations

from dataclasses import dataclass

from rseco.runspec import RunSpec


@dataclass(frozen=True)
class CandidateMetrics:
    candidate_hash: str
    setup_wns: float
    setup_tns: float
    patch_ratio: float
    required_ok: bool
    hold_min_slack: float | None = None
    physical_primary: float | None = None
    physical_secondary: float | None = None


@dataclass(frozen=True)
class AcceptanceVerdict:
    accepted: bool
    reasons: tuple[str, ...] = ()


class DefaultAcceptancePolicy:
    def __init__(self, spec: RunSpec, baseline_wns: float = -1.0) -> None:
        self.spec = spec
        self.baseline_wns = baseline_wns

    def evaluate(self, m: CandidateMetrics) -> AcceptanceVerdict:
        reasons: list[str] = []
        if not m.required_ok:
            reasons.append("required_metrics")
        gain = m.setup_wns - self.baseline_wns
        if gain <= self.spec.min_gain_ns:
            reasons.append("insufficient_gain")
        if m.patch_ratio > self.spec.max_patch_ratio:
            reasons.append("patch_ratio_exceeded")
        return AcceptanceVerdict(accepted=not reasons, reasons=tuple(reasons))


def rank_candidates(candidates: list[CandidateMetrics], mode: str) -> list[CandidateMetrics]:
    def key(m: CandidateMetrics) -> tuple:
        if mode == "hold":
            hold = m.hold_min_slack if m.hold_min_slack is not None else float("-inf")
            return (-hold, -m.setup_wns, m.patch_ratio, m.candidate_hash)
        return (-m.setup_wns, -m.setup_tns, m.patch_ratio, m.candidate_hash)

    return sorted(candidates, key=key)
