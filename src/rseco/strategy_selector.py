# Strategy decision layer for failure-aware hybrid repair.
#
# Given historical trial data (candidate -> accepted/rejected), the selector
# induces per-cell-type accept rates per strategy and orders strategies for
# candidate generation. This is the "decision layer" that makes the hybrid
# repair failure-aware rather than pure brute-force search: before evaluating
# every candidate with OpenSTA, we predict which strategy is most likely to
# improve WNS and only generate those candidates first.
#
# Deliberately simple and interpretable (no GNN/RL): a per-cell-type
# acceptance-rate table that can be audited and analysed for cross-circuit
# transfer.

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


def build_feature_vector(
    *,
    from_type: str,
    has_larger_size: bool,
    fanout: int,
    is_critical: bool,
) -> dict[str, object]:
    # Build the feature vector used for strategy prediction.
    return {
        "from_type": from_type,
        "has_larger_size": has_larger_size,
        "fanout": int(fanout),
        "is_critical": bool(is_critical),
    }


def strategy_stats(trials: list[dict]) -> dict[str, dict]:
    # Aggregate accepted/rejected counts per strategy from trial records.
    # Each trial dict has at least kind (R/G/B/JOINT) and accepted (bool).
    counts: dict[str, dict] = defaultdict(lambda: {"n": 0, "accepted": 0})
    for tr in trials:
        kind = tr.get("kind", "?")
        counts[kind]["n"] += 1
        if tr.get("accepted"):
            counts[kind]["accepted"] += 1
    return dict(counts)


def exploration_order(
    cands: list[tuple[str, dict, str]],
) -> list[tuple[str, dict, str]]:
    """Keep at least one G/R candidate ahead of a B-dominated queue.

    Pure priority reordering can collapse multi-round greedy onto buffer
    insertion (observed on s820: 2 rounds, final -1.03 vs -0.20 full search).
    This guard lifts every G/R candidate to the front so logic-level options
    still compete each round.
    """
    gr = [c for c in cands if c[2] in ("G", "R")]
    if gr and len(cands) > len(gr):
        rest = [c for c in cands if c[2] not in ("G", "R")]
        return gr + rest
    return list(cands)


@dataclass
class StrategySelector:
    # Per-cell-type strategy acceptance table induced from trial history.
    # accept_rates maps cell_type -> {strategy: acceptance_rate}.
    accept_rates: dict[str, dict[str, float]] = field(default_factory=dict)
    fallback_order: tuple[str, ...] = ("R", "G", "B")

    @classmethod
    def from_trials(cls, trials: list[dict]) -> "StrategySelector":
        # Induce accept rates from trial records; group by from_type.
        per_type: dict[str, dict[str, list[bool]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for tr in trials:
            kind = tr.get("kind", "?")
            from_type = tr.get("from_type", "")
            per_type[from_type][kind].append(bool(tr.get("accepted")))
        accept_rates: dict[str, dict[str, float]] = {}
        for ctype, by_kind in per_type.items():
            rates = {}
            for kind, acc in by_kind.items():
                rates[kind] = sum(acc) / len(acc)
            accept_rates[ctype] = rates
        return cls(accept_rates=accept_rates)

    def priority_order(self, from_type: str = "") -> list[str]:
        # Return strategies sorted by accept rate (desc), stable tie-break.
        rates = self.accept_rates.get(from_type)
        if not rates:
            return list(self.fallback_order)
        known = sorted(rates, key=lambda k: (-rates[k], self._tie(k)))
        result = known + [s for s in self.fallback_order if s not in known]
        return result

    def predict(
        self, features: dict[str, object], *, top_n: int = 2
    ) -> list[str]:
        # Return the top-N strategies to try for the given feature vector.
        from_type = str(features.get("from_type", ""))
        order = self.priority_order(from_type)
        return order[:top_n]

    @staticmethod
    def _tie(kind: str) -> int:
        return {"R": 0, "G": 1, "B": 2}.get(kind, 9)
