"""Acceptance policy must be pure logic over measured metrics."""

from __future__ import annotations

from rseco.acceptance import CandidateMetrics, DefaultAcceptancePolicy, rank_candidates
from rseco.runspec import RunSpec


def _metrics(**kw) -> CandidateMetrics:
    base = dict(
        candidate_hash="c1",
        setup_wns=-1.0,
        setup_tns=-5.0,
        patch_ratio=0.001,
        required_ok=True,
    )
    base.update(kw)
    return CandidateMetrics(**base)


def test_fail_closed_when_required_metric_missing() -> None:
    policy = DefaultAcceptancePolicy(RunSpec.defaults())
    verdict = policy.evaluate(_metrics(required_ok=False))
    assert not verdict.accepted
    assert "required_metrics" in verdict.reasons


def test_accepts_strict_improvement_over_epsilon() -> None:
    policy = DefaultAcceptancePolicy(RunSpec.defaults())
    verdict = policy.evaluate(_metrics(setup_wns=-0.5, setup_tns=-2.0))
    assert verdict.accepted


def test_rejects_insufficient_gain() -> None:
    policy = DefaultAcceptancePolicy(RunSpec.defaults())
    verdict = policy.evaluate(_metrics(setup_wns=-1.0005, setup_tns=-5.0))
    assert not verdict.accepted


def test_ranking_is_deterministic_and_mode_aware() -> None:
    ranked = rank_candidates(
        [
            _metrics(candidate_hash="b", setup_wns=-0.9),
            _metrics(candidate_hash="a", setup_wns=-0.8),
        ],
        mode="setup",
    )
    assert [m.candidate_hash for m in ranked] == ["a", "b"]
