"""Tests for the strategy decision layer (failure-aware candidate pruning)."""

from __future__ import annotations

import json
import pytest

from rseco.strategy_selector import (
    StrategySelector,
    build_feature_vector,
    strategy_stats,
)


def test_build_feature_vector() -> None:
    fv = build_feature_vector(
        from_type="sky130_fd_sc_hd__lpflow_inputiso1p_1",
        has_larger_size=False,
        fanout=3,
        is_critical=True,
    )
    assert fv["has_larger_size"] is False
    assert fv["fanout"] == 3
    assert fv["is_critical"] is True


def test_strategy_stats_counts_by_kind() -> None:
    trials = [
        {"kind": "R", "accepted": True},
        {"kind": "R", "accepted": False},
        {"kind": "G", "accepted": True},
        {"kind": "B", "accepted": True},
    ]
    stats = strategy_stats(trials)
    assert stats["R"]["n"] == 2
    assert stats["R"]["accepted"] == 1
    assert stats["G"]["accepted"] == 1
    assert stats["B"]["accepted"] == 1


def test_selector_orders_by_accept_rate() -> None:
    trials = [
        {"kind": "R", "accepted": True},
        {"kind": "R", "accepted": True},
        {"kind": "G", "accepted": False},
        {"kind": "B", "accepted": False},
    ]
    sel = StrategySelector.from_trials(trials)
    order = sel.priority_order()
    assert order[0] == "R"  # highest accept rate


def test_selector_prediction_uses_features() -> None:
    trials = [
        {"kind": "R", "accepted": True, "from_type": "sky130_fd_sc_hd__lpflow_inputiso1p_1"},
        {"kind": "R", "accepted": True, "from_type": "sky130_fd_sc_hd__lpflow_inputiso1p_1"},
        {"kind": "G", "accepted": False, "from_type": "sky130_fd_sc_hd__lpflow_inputiso1p_1"},
        {"kind": "B", "accepted": False, "from_type": "sky130_fd_sc_hd__lpflow_inputiso1p_1"},
    ]
    sel = StrategySelector.from_trials(trials)
    # a cell with no larger size, high delay, should prefer R
    pred = sel.predict(features={"from_type": "sky130_fd_sc_hd__lpflow_inputiso1p_1", "has_larger_size": False})
    assert pred[0] == "R"


def test_exploration_guard_keeps_gr_ahead() -> None:
    """Priority reorder must keep at least one G/R candidate ahead of a B-only
    queue so multi-round greedy keeps logic-level exploration."""
    from rseco.strategy_selector import exploration_order
    cands = [("b1", {}, "B"), ("b2", {}, "B"), ("g1", {}, "G"), ("r1", {}, "R")]
    out = exploration_order(cands)
    kinds = [k for _, _, k in out]
    # G/R group must come before any B
    assert kinds[0] in ("G", "R")
    assert kinds[1] in ("G", "R")
    assert kinds[2] == "B"
    assert set(kinds) == {"B", "G", "R"}
