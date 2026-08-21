# Multi-iteration failure-aware refinement loop (X19).
#
# flow.py currently performs a single refinement proxy: it calls
# refine_weights once and records one iteration.  This module implements the
# real loop: cut -> classify -> refine weights -> re-cut, until a candidate
# succeeds or max_iterations is reached.
#
# The loop is deliberately decoupled from any concrete cut implementation:
# callers pass an evaluator callback (failures, weights) -> (success, patch_id),
# which makes it unit-testable without Yosys/OpenSTA.

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Callable

from .failures import FailureType
from .refinement import RefinementWeights, refine_weights


_STOP_REASONS = {
    "timing_met", "no_new_candidate", "stagnation", "sta_budget",
    "formal_budget", "wall_timeout", "max_patches",
}


@dataclass
class SearchState:
    """Auditable mutable state for one timing-closure search.

    ``current_netlist_text`` is the transaction value: callers either append
    an accepted patch with :meth:`accept_patch`, or leave the state untouched.
    This makes a multi-round run restartable and keeps the accepted log as the
    source of truth for replay.
    """

    current_netlist_text: str
    current_wns: float | None = None
    current_tns: float | None = None
    current_min_slack: float | None = None
    critical_endpoints: list[str] = field(default_factory=list)
    critical_instances: list[str] = field(default_factory=list)
    current_cone_gates: list[str] = field(default_factory=list)
    accepted_patches: list[dict] = field(default_factory=list)
    failure_history: list[dict] = field(default_factory=list)
    tested_candidate_hashes: set[str] = field(default_factory=set)
    budget: dict[str, float | int] = field(default_factory=dict)
    stop_reason: str | None = None
    _snapshots: list[dict] = field(default_factory=list, repr=False)

    @staticmethod
    def hash_text(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @property
    def current_netlist_hash(self) -> str:
        return self.hash_text(self.current_netlist_text)

    def candidate_hash(self, *, gates=(), boundary_inputs=(),
                       boundary_outputs=(), action_hash="") -> str:
        """Hash canonical gate/boundary/action identity for STA de-duplication."""
        payload = {
            "gates": sorted(set(map(str, gates))),
            "boundary_inputs": sorted(set(map(str, boundary_inputs))),
            "boundary_outputs": sorted(set(map(str, boundary_outputs))),
            "action": str(action_hash),
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return self.hash_text(raw)

    def mark_candidate_tested(self, candidate_hash: str) -> bool:
        """Return false when this candidate was already tested (including failure)."""
        if candidate_hash in self.tested_candidate_hashes:
            return False
        self.tested_candidate_hashes.add(candidate_hash)
        return True

    def record_failure(self, event: dict) -> None:
        normalized = dict(event)
        candidate_hash = str(normalized.get("candidate_hash") or self.current_netlist_hash)
        normalized["candidate_hash"] = candidate_hash
        normalized["cut_hash"] = str(normalized.get("cut_hash") or candidate_hash)
        normalized.setdefault("severity", "hard")
        normalized.setdefault("runtime_s", 0.0)
        normalized.setdefault("evidence", {})
        self.failure_history.append(normalized)

    def accept_patch(self, patch_id: str, candidate_netlist_text: str, *,
                     wns=None, tns=None, candidate_hash=None,
                     min_slack=None,
                     critical_endpoints=None, critical_instances=None,
                     cone_gates=None,
                     metadata=None) -> dict:
        """Atomically append an accepted patch and advance ``G_r``."""
        previous = {
            "current_netlist_text": self.current_netlist_text,
            "current_wns": self.current_wns,
            "current_tns": self.current_tns,
            "current_min_slack": self.current_min_slack,
            "critical_endpoints": list(self.critical_endpoints),
            "critical_instances": list(self.critical_instances),
            "current_cone_gates": list(self.current_cone_gates),
        }
        record = {
            "patch_id": str(patch_id),
            "candidate_hash": candidate_hash or self.hash_text(candidate_netlist_text),
            "base_netlist_hash": self.current_netlist_hash,
            "netlist_hash": self.hash_text(candidate_netlist_text),
            "netlist_text": candidate_netlist_text,
            "wns": wns,
            "tns": tns,
            "metadata": dict(metadata or {}),
        }
        self._snapshots.append(previous)
        self.accepted_patches.append(record)
        self.current_netlist_text = candidate_netlist_text
        self.current_wns = wns
        self.current_tns = tns
        self.current_min_slack = min_slack
        if critical_endpoints is not None:
            self.critical_endpoints = list(critical_endpoints)
        if critical_instances is not None:
            self.critical_instances = list(critical_instances)
        if cone_gates is not None:
            self.current_cone_gates = list(cone_gates)
        return record

    def rollback(self) -> bool:
        """Undo the last accepted patch, preserving its log for audit."""
        if not self._snapshots or not self.accepted_patches:
            return False
        previous = self._snapshots.pop()
        self.accepted_patches.pop()
        self.current_netlist_text = previous["current_netlist_text"]
        self.current_wns = previous["current_wns"]
        self.current_tns = previous["current_tns"]
        self.current_min_slack = previous.get("current_min_slack")
        self.critical_endpoints = previous["critical_endpoints"]
        self.critical_instances = previous["critical_instances"]
        self.current_cone_gates = previous.get("current_cone_gates", [])
        return True

    @staticmethod
    def replay(initial_netlist_text: str, accepted_patches: list[dict]) -> str:
        """Replay the recorded candidate texts and return the final netlist."""
        current = initial_netlist_text
        for patch in accepted_patches:
            base = patch.get("base_netlist_hash")
            if base and base != SearchState.hash_text(current):
                raise ValueError("accepted patch log is not a contiguous replay")
            current = str(patch["netlist_text"])
        return current

    def set_stop_reason(self, reason: str) -> None:
        if reason not in _STOP_REASONS:
            raise ValueError(f"unsupported stop_reason: {reason}")
        if self.stop_reason is not None and self.stop_reason != reason:
            raise ValueError(f"stop_reason already set to {self.stop_reason}")
        self.stop_reason = reason

    def to_dict(self) -> dict:
        return {
            "current_netlist_text": self.current_netlist_text,
            "current_netlist_hash": self.current_netlist_hash,
            "current_wns": self.current_wns,
            "current_tns": self.current_tns,
            "current_min_slack": self.current_min_slack,
            "critical_endpoints": list(self.critical_endpoints),
            "critical_instances": list(self.critical_instances),
            "current_cone_gates": list(self.current_cone_gates),
            "accepted_patches": list(self.accepted_patches),
            "failure_history": list(self.failure_history),
            "tested_candidate_hashes": sorted(self.tested_candidate_hashes),
            "budget": dict(self.budget),
            "stop_reason": self.stop_reason,
        }


@dataclass(frozen=True)
class RefinementConfig:
    # Maximum refinement iterations (default matches faeco_algorithm.md).
    max_iterations: int = 10


def simulate_refinement_loop(
    evaluator: Callable[[set[FailureType], RefinementWeights], tuple[bool, str | None]],
    config: RefinementConfig | None = None,
    *,
    on_refine: Callable[[list[str]], None] | None = None,
    enable_feedback: bool = True,
    init_weights: dict | None = None,
) -> dict:
    """Run the failure-aware refinement loop.

    evaluator(failures, weights) returns (success, patch_id).  On failure the
    loop classifies the failure set and (if enable_feedback) calls
    refine_weights, then re-invokes the evaluator with updated weights.
    enable_feedback=False is the ablation control: weights stay fixed.
    """
    config = config or RefinementConfig()
    weights = RefinementWeights()
    if init_weights:
        weights = RefinementWeights(
            boundary_penalty=float(init_weights.get("boundary_penalty", weights.boundary_penalty)),
            size_penalty=float(init_weights.get("size_penalty", weights.size_penalty)),
            critical_coverage_reward=float(init_weights.get("critical_coverage_reward", weights.critical_coverage_reward)),
            verification_cost_penalty=float(init_weights.get("verification_cost_penalty", weights.verification_cost_penalty)),
            equivalence_stability_reward=float(init_weights.get("equivalence_stability_reward", weights.equivalence_stability_reward)),
            max_cone_gates=int(init_weights.get("max_cone_gates", weights.max_cone_gates)),
            physical_penalty=float(init_weights.get("physical_penalty", weights.physical_penalty)),
        )
    history: list[dict] = []
    actions_history: list[list[str]] = []
    accepted_any = False

    for iteration in range(1, config.max_iterations + 1):
        failures: set[FailureType] = set()
        evaluated = evaluator(failures, weights)
        continue_after_success = False
        if isinstance(evaluated, tuple) and len(evaluated) == 4:
            success, patch_id, extra, continue_after_success = evaluated
        elif isinstance(evaluated, tuple) and len(evaluated) == 3:
            success, patch_id, extra = evaluated
        else:
            success, patch_id = evaluated
            extra = None
        if success:
            accepted_any = True
            history.append(
                {
                    "iteration": iteration,
                    "status": "accepted" if continue_after_success else "success",
                    "patch_id": patch_id,
                    "wns": extra.get("wns") if extra else None,
                    "actions": [],
                }
            )
            if not continue_after_success:
                return {
                    "success": True,
                    "iterations": iteration,
                    "final_patch_id": patch_id,
                    "history": history,
                    "weights": weights,
                }
            continue
        decision = refine_weights(weights, failures) if enable_feedback else None
        if decision is not None:
            weights = decision.weights
            actions = decision.actions
        else:
            actions = []
        if on_refine is not None and enable_feedback:
            on_refine(actions)
        actions_history.append(actions)
        history.append(
            {
                "iteration": iteration,
                "status": "refined",
                "actions": actions,
                "failures": sorted(f.value for f in failures),
                "wns": extra.get("wns") if extra else None,
            }
        )

    return {
        "success": accepted_any,
        "iterations": config.max_iterations,
        "final_patch_id": None,
        "history": history,
        "actions_history": actions_history,
        "weights": weights,
    }
