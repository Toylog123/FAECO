"""Auditable STA-before candidate ranking for the real outer-loop runner."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ProxyWeights:
    """Weights for the pre-STA candidate ranking.

    The timing term is deliberately a library/structure proxy, not a measured
    WNS estimate.  Every component is emitted with each trial so the ranking
    can be audited and ablated against the same candidate set.
    """

    timing_gain: float = 1.0
    patch_size: float = 1.0
    boundary_complexity: float = 1.0
    verification_cost: float = 1.0
    equivalence_confidence: float = 1.0
    critical_path_coverage: float = 1.0
    strategy_priority: float = 0.25


def _cell_size(cell_type: str) -> int:
    match = re.search(r"_(\d+)$", cell_type or "")
    return int(match.group(1)) if match else 0


def _library_timing_gain(kind: str, from_type: str, to_type: str) -> float:
    old_size = _cell_size(from_type)
    new_size = _cell_size(to_type)
    if kind == "G" and old_size and new_size:
        return max(0.0, math.log1p(new_size / old_size - 1.0))
    if kind == "R" and old_size and new_size:
        return max(0.0, math.log1p(old_size / new_size - 1.0))
    if kind == "JOINT":
        return 0.0
    # A buffer adds a logic stage in the ideal-net model; it is therefore
    # ranked below an otherwise identical library replacement.
    if kind == "B":
        return -1.0
    return 0.0


def _row_features(row: dict) -> dict[str, float]:
    critical_count = max(1, int(row.get("critical_count", 1)))
    critical_rank = min(
        max(0, int(row.get("critical_rank", critical_count - 1))),
        critical_count - 1,
    )
    strategy_rank = max(0, int(row.get("strategy_rank", 0)))
    kind = str(row.get("kind", ""))
    patch_size = max(1, int(row.get("patch_size", 1)))
    boundary_complexity = max(0, int(row.get("boundary_complexity", 0)))
    return {
        "timing_gain": _library_timing_gain(
            kind,
            str(row.get("from_type", "")),
            str(row.get("to_type", "")),
        ),
        "patch_size": float(patch_size),
        "boundary_complexity": float(boundary_complexity),
        "verification_cost": {
            "R": 0.5,
            "G": 0.25,
            "B": 0.25,
            "JOINT": 1.0,
        }.get(kind, 0.5),
        "equivalence_confidence": 1.0,
        "critical_path_coverage": (
            float(critical_count - critical_rank) / float(critical_count)
        ),
        "strategy_priority": 1.0 / float(1 + strategy_rank),
    }


def _score(features: dict[str, float], weights: ProxyWeights) -> float:
    return (
        weights.timing_gain * features["timing_gain"]
        - weights.patch_size * features["patch_size"]
        - weights.boundary_complexity * features["boundary_complexity"]
        - weights.verification_cost * features["verification_cost"]
        + weights.equivalence_confidence * features["equivalence_confidence"]
        + weights.critical_path_coverage * features["critical_path_coverage"]
        + weights.strategy_priority * features["strategy_priority"]
    )


def rank_real_candidates(
    candidates: Iterable[dict],
    *,
    weights: ProxyWeights | None = None,
) -> list[dict]:
    """Return deterministically ranked candidates with auditable features."""

    weights = weights or ProxyWeights()
    scored: list[dict] = []
    for row in candidates:
        enriched = dict(row)
        features = _row_features(enriched)
        enriched["proxy_features"] = features
        enriched["proxy_score"] = _score(features, weights)
        scored.append(enriched)

    scored.sort(
        key=lambda row: (
            -float(row["proxy_score"]),
            -float(row["proxy_features"]["critical_path_coverage"]),
            int(row.get("strategy_rank", 0)),
            str(row.get("instance", "")),
            str(row.get("kind", "")),
            str(row.get("to_type", "")),
        )
    )
    for rank, row in enumerate(scored, start=1):
        row["proxy_rank"] = rank
    return scored
