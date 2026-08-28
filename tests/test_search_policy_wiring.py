"""RealWnsEvaluator accepts search_policy without changing legacy behavior."""

from __future__ import annotations

import pytest

from rseco.real_wns import RealWnsEvaluator


def _minimal_evaluator(**kwargs) -> RealWnsEvaluator:
    return RealWnsEvaluator(
        mapped_text="module top;\nendmodule\n",
        top_module="top",
        period=1.0,
        liberty_text="LIB",
        baseline_wns=-1.0,
        output_dir="unused",
        **kwargs,
    )


def test_fast_maps_to_early_stop() -> None:
    ev = _minimal_evaluator(search_policy="fast")
    assert ev.early_stop is True
    assert ev.search_policy.value == "fast"


def test_balanced_is_full_round() -> None:
    ev = _minimal_evaluator(search_policy="balanced")
    assert ev.early_stop is False
    assert ev.search_policy.value == "balanced"


def test_exhaustive_is_full_round() -> None:
    ev = _minimal_evaluator(search_policy="exhaustive")
    assert ev.early_stop is False
    assert ev.search_policy.value == "exhaustive"


def test_legacy_early_stop_deprecation_warning() -> None:
    with pytest.warns(DeprecationWarning):
        ev = _minimal_evaluator(early_stop=True)
    assert ev.early_stop is True
    assert ev.search_policy.value == "fast"


def test_explicit_policy_beats_legacy_flag() -> None:
    with pytest.warns(DeprecationWarning):
        ev = _minimal_evaluator(early_stop=True, search_policy="exhaustive")
    assert ev.early_stop is False
    assert ev.search_policy.value == "exhaustive"
