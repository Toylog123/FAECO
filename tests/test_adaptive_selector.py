# -*- coding: utf-8 -*-
"""TDD tests for the online adaptive strategy selector (decision layer v2).

The v1 decision layer is a *static* per-cell-type priority table induced from
12205 historical trials.  The v2 layer keeps the same per-cell-type interface
but updates its ordering online from every measured trial (UCB1-style
exploration + exponential recency weighting), so a running repair session
adapts to the circuit it is actually fixing.
"""

from rseco.adaptive_selector import AdaptiveStrategySelector


def _trials(seq):
    """Build trial-like dicts from (kind, accepted) pairs."""
    return [{"kind": k, "accepted": a, "from_type": "sky130_fd_sc_hd__and2_1"} for k, a in seq]


def test_cold_start_uses_fallback_order():
    sel = AdaptiveStrategySelector()
    assert sel.priority_order("sky130_fd_sc_hd__and2_1") == ["R", "G", "B"]


def test_unknown_cell_type_falls_back():
    sel = AdaptiveStrategySelector()
    assert sel.priority_order("no_such_cell") == ["R", "G", "B"]


def test_acceptance_moves_strategy_up():
    sel = AdaptiveStrategySelector()
    sel.record("sky130_fd_sc_hd__and2_1", "R", accepted=True)
    sel.record("sky130_fd_sc_hd__and2_1", "R", accepted=True)
    sel.record("sky130_fd_sc_hd__and2_1", "R", accepted=True)
    sel.record("sky130_fd_sc_hd__and2_1", "G", accepted=False)
    order = sel.priority_order("sky130_fd_sc_hd__and2_1")
    assert order[0] == "R"


def test_rejection_moves_strategy_down():
    sel = AdaptiveStrategySelector()
    sel.record("sky130_fd_sc_hd__and2_1", "R", accepted=False)
    sel.record("sky130_fd_sc_hd__and2_1", "R", accepted=False)
    sel.record("sky130_fd_sc_hd__and2_1", "G", accepted=True)
    order = sel.priority_order("sky130_fd_sc_hd__and2_1")
    assert order[0] == "G"


def test_exploration_bonus_keeps_under_tried_strategy_visible():
    sel = AdaptiveStrategySelector()
    for _ in range(20):
        sel.record("sky130_fd_sc_hd__and2_1", "G", accepted=True)
    sel.record("sky130_fd_sc_hd__and2_1", "R", accepted=False)
    order = sel.priority_order("sky130_fd_sc_hd__and2_1")
    assert order[0] == "G" or order[1] == "G"
    assert "R" in order
    assert order.index("R") < order.index("B")


def test_recency_decay_favors_recent_trend():
    sel = AdaptiveStrategySelector()
    for _ in range(50):
        sel.record("sky130_fd_sc_hd__and2_1", "G", accepted=True)
    for _ in range(3):
        sel.record("sky130_fd_sc_hd__and2_1", "R", accepted=True)
    order = sel.priority_order("sky130_fd_sc_hd__and2_1")
    assert order[0] == "R"


def test_fit_from_historical_trials_warm_starts():
    hist = _trials([("R", True), ("R", True), ("R", True), ("G", False)])
    sel = AdaptiveStrategySelector.from_trials(hist)
    assert sel.priority_order("sky130_fd_sc_hd__and2_1")[0] == "R"


def test_serializable_snapshot_roundtrip():
    sel = AdaptiveStrategySelector()
    sel.record("sky130_fd_sc_hd__and2_1", "G", accepted=True)
    snap = sel.snapshot()
    sel2 = AdaptiveStrategySelector.load_snapshot(snap)
    assert sel2.priority_order("sky130_fd_sc_hd__and2_1") == sel.priority_order(
        "sky130_fd_sc_hd__and2_1"
    )


def test_warm_start_cross_circuit_then_adapt():
    # Cross-circuit warm start: other circuits favour G for this cell type.
    # Pure success evidence cannot overturn an all-success prior (correct
    # UCB behaviour), but *failure* evidence on the target circuit must:
    # the online layer can correct a wrong transferred prior, something a
    # static leave-one-out table cannot do once frozen.
    other = _trials([("G", True), ("G", True), ("G", True), ("G", True)])
    sel = AdaptiveStrategySelector.from_trials(other)
    assert sel.priority_order("sky130_fd_sc_hd__and2_1")[0] == "G"
    for _ in range(3):
        sel.record("sky130_fd_sc_hd__and2_1", "G", accepted=False)
    for _ in range(3):
        sel.record("sky130_fd_sc_hd__and2_1", "R", accepted=True)
    assert sel.priority_order("sky130_fd_sc_hd__and2_1")[0] == "R"
