# -*- coding: utf-8 -*-
"""Online adaptive strategy selector (decision layer v2).

v1 (StrategySelector / strategy_priority_table.json) is a static per-cell-type
priority table induced offline from historical trials. v2 keeps the same
priority_order interface but updates its ordering online from every measured
trial during a repair session, so the decision layer adapts to the circuit
actually being fixed (UCB1-style exploration + exponential recency weighting).
The update cost is O(1) per trial and the state is a small JSON-serializable
table, so it scales to very large netlists where running a full offline
learning pass is impractical.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field

STRATEGIES = ("R", "G", "B")
_TIE = {"R": 0, "G": 1, "B": 2}


@dataclass
class _CellStats:
    weight: dict = field(default_factory=lambda: defaultdict(float))
    n: dict = field(default_factory=lambda: defaultdict(float))
    global_n: float = 0.0

    def record(self, kind, accepted, gamma):
        for k in list(self.weight):
            self.weight[k] *= gamma
            self.n[k] *= gamma
        self.global_n *= gamma
        self.weight[kind] += 1.0 if accepted else 0.0
        self.n[kind] += 1.0
        self.global_n += 1.0

    def ucb(self, kind, alpha):
        if self.n.get(kind, 0.0) <= 0.0:
            # Untried arm: fixed mild exploration score (below any seen arm
            # with a success, above an arm rejected enough times).  Pure UCB1
            # optimistic prior would rank every untried arm first, which
            # contradicts the domain prior that B is weak in pre-layout.
            return 0.5
        n_k = max(self.n.get(kind, 0.0), 1e-9)
        rate = self.weight.get(kind, 0.0) / n_k
        return rate + alpha * math.sqrt(math.log(self.global_n + 2.0) / n_k)

    def to_dict(self):
        return {"weight": dict(self.weight), "n": dict(self.n), "global_n": self.global_n}

    @classmethod
    def from_dict(cls, d):
        return cls(
            weight=defaultdict(float, d.get("weight", {})),
            n=defaultdict(float, d.get("n", {})),
            global_n=float(d.get("global_n", 0.0)),
        )


@dataclass
class AdaptiveStrategySelector:
    gamma: float = 0.98
    alpha: float = 0.4
    fallback_order: tuple = ("R", "G", "B")
    cells: dict = field(default_factory=dict)

    @classmethod
    def from_trials(cls, trials, gamma=0.98, alpha=0.4):
        sel = cls(gamma=gamma, alpha=alpha)
        for tr in trials:
            from_type = str(tr.get("from_type", ""))
            kind = str(tr.get("kind", "?"))
            if kind not in STRATEGIES or not from_type:
                continue
            sel.record(from_type, kind, accepted=bool(tr.get("accepted")))
        return sel

    def record(self, from_type, kind, accepted=True):
        if kind not in STRATEGIES:
            return
        stats = self.cells.setdefault(from_type, _CellStats())
        stats.record(kind, accepted, gamma=self.gamma)

    def _score(self, from_type, kind):
        stats = self.cells.get(from_type)
        if stats is None:
            return -1.0
        return stats.ucb(kind, alpha=self.alpha)

    def priority_order(self, from_type=""):
        stats = self.cells.get(from_type)
        if stats is None:
            return list(self.fallback_order)
        return sorted(STRATEGIES, key=lambda k: (-self._score(from_type, k), _TIE[k]))

    def predict(self, from_type="", top_n=2):
        return self.priority_order(from_type)[:top_n]

    def snapshot(self):
        return {
            "gamma": self.gamma,
            "alpha": self.alpha,
            "fallback_order": list(self.fallback_order),
            "cells": {k: v.to_dict() for k, v in self.cells.items()},
        }

    @classmethod
    def load_snapshot(cls, snap):
        return cls(
            gamma=float(snap.get("gamma", 0.98)),
            alpha=float(snap.get("alpha", 0.4)),
            fallback_order=tuple(snap.get("fallback_order", ["R", "G", "B"])),
            cells={k: _CellStats.from_dict(v) for k, v in snap.get("cells", {}).items()},
        )
