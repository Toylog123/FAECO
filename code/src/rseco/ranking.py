"""Deterministic timing-aware patch ranking for the first FAECO prototype."""

from dataclasses import dataclass

from .patch import PatchCandidate


@dataclass(frozen=True)
class RankingWeights:
    timing_gain: float = 1.0
    patch_size: float = 1.0
    boundary_complexity: float = 1.0
    verification_cost: float = 1.0
    equivalence_confidence: float = 1.0
    equivalence_failure_penalty: float = 10.0


@dataclass(frozen=True)
class RankedPatch:
    rank: int
    patch_id: str
    score: float
    features: dict[str, float]
    patch: PatchCandidate

    def to_dict(self) -> dict[str, object]:
        payload = self.patch.to_dict()
        payload.update(
            {
                "rank": self.rank,
                "score": self.score,
                "ranking_features": self.features,
            }
        )
        return payload


def score_patch_candidate(
    patch: PatchCandidate,
    *,
    timing_gain: float = 0.0,
    verification_cost: float = 0.0,
    weights: RankingWeights | None = None,
) -> RankedPatch:
    """Score one candidate with the interpretable first-version ranking formula."""
    weights = weights or RankingWeights()
    equivalence_confidence = 1.0 if patch.equivalence_result == "pass" else 0.0
    features = {
        "timing_gain": float(timing_gain),
        "patch_size": float(patch.patch_size),
        "boundary_complexity": float(
            len(patch.boundary_inputs) + len(patch.boundary_outputs)
        ),
        "verification_cost": float(verification_cost),
        "equivalence_confidence": equivalence_confidence,
    }

    score = (
        weights.timing_gain * features["timing_gain"]
        - weights.patch_size * features["patch_size"]
        - weights.boundary_complexity * features["boundary_complexity"]
        - weights.verification_cost * features["verification_cost"]
        + weights.equivalence_confidence * features["equivalence_confidence"]
    )
    if equivalence_confidence == 0.0:
        score -= weights.equivalence_failure_penalty

    return RankedPatch(
        rank=0,
        patch_id=patch.patch_id,
        score=score,
        features=features,
        patch=patch,
    )


def rank_patch_candidates(
    patches: list[PatchCandidate],
    *,
    timing_gains: dict[str, float] | None = None,
    verification_costs: dict[str, float] | None = None,
    weights: RankingWeights | None = None,
) -> list[RankedPatch]:
    """Return candidates sorted by descending score with stable patch-id ties."""
    timing_gains = timing_gains or {}
    verification_costs = verification_costs or {}
    weights = weights or RankingWeights()
    scored = [
        score_patch_candidate(
            patch,
            timing_gain=timing_gains.get(patch.patch_id, 0.0),
            verification_cost=verification_costs.get(patch.patch_id, 0.0),
            weights=weights,
        )
        for patch in patches
    ]
    ordered = sorted(
        scored,
        key=lambda entry: (
            -entry.features["equivalence_confidence"],
            -entry.score,
            _cut_method_priority(entry.patch.cut_method),
            entry.patch_id,
        ),
    )
    return [
        RankedPatch(
            rank=index,
            patch_id=entry.patch_id,
            score=entry.score,
            features=entry.features,
            patch=entry.patch,
        )
        for index, entry in enumerate(ordered, start=1)
    ]


def _cut_method_priority(cut_method: str) -> int:
    priorities = {
        "size_refined_cut": 0,
        "weighted_st_min_cut_v1": 1,
        "size_only_cut": 2,
        "critical_path_only_cut": 3,
        "fixed_min_cut": 4,
    }
    return priorities.get(cut_method, 10)
