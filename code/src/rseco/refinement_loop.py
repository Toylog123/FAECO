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

from dataclasses import asdict, dataclass, field
import hashlib
import json
import threading
from typing import Callable

from .failures import FailureType
from .refinement import RefinementWeights, refine_weights
from .feedback import (
    FailureFeedbackState,
    FeedbackConfig,
    describe_actions,
    update_feedback,
)


_STOP_REASONS = {
    "timing_met", "no_new_candidate", "stagnation", "sta_budget",
    "formal_budget", "wall_timeout", "max_patches", "max_iterations",
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
    _budget_lock: object = field(default_factory=threading.Lock, repr=False, compare=False)

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

    def reserve_budget(self, kind: str, limit: int | None = None) -> bool:
        """Atomically reserve one tool slot before invoking a tool."""
        used_key = f"{kind}_used"
        limit_key = f"{kind}_budget"
        if limit is None:
            raw_limit = self.budget.get(limit_key)
            limit = int(raw_limit) if raw_limit is not None else None
        with self._budget_lock:
            used = int(self.budget.get(used_key, 0))
            if limit is not None and used >= limit:
                return False
            self.budget[used_key] = used + 1
            return True

    def deadline_expired(self) -> bool:
        """Return whether this run's monotonic wall-clock deadline elapsed."""
        deadline = self.budget.get("_deadline_monotonic")
        return deadline is not None and __import__("time").perf_counter() >= float(deadline)

    def budget_used(self, kind: str) -> int:
        return int(self.budget.get(f"{kind}_used", 0))

    def record_failure(self, event: dict) -> None:
        normalized = dict(event)
        candidate_hash = str(normalized.get("candidate_hash") or self.current_netlist_hash)
        normalized["candidate_hash"] = candidate_hash
        normalized["cut_hash"] = str(normalized.get("cut_hash") or candidate_hash)
        normalized.setdefault("endpoint", None)
        normalized.setdefault("path", [])
        normalized.setdefault("net", None)
        normalized.setdefault("action_scope", [])
        normalized.setdefault("threshold", None)
        normalized.setdefault("observed_value", None)
        normalized.setdefault("severity", "hard")
        normalized.setdefault("runtime_s", 0.0)
        normalized.setdefault("evidence", {})
        normalized.setdefault("event_id", hashlib.sha256(json.dumps({
            "type": normalized.get("type"), "candidate_hash": candidate_hash,
            "cut_hash": normalized["cut_hash"], "endpoint": normalized.get("endpoint"),
            "path": normalized.get("path", []), "net": normalized.get("net"),
            "action_scope": normalized.get("action_scope", []),
            "threshold": normalized.get("threshold"),
            "observed_value": normalized.get("observed_value"),
            "evidence": normalized.get("evidence", {}),
        }, sort_keys=True, default=str).encode()).hexdigest())
        if any(existing.get("event_id") == normalized["event_id"]
               for existing in self.failure_history):
            return
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
            "min_slack": min_slack,
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
            "budget": {k: v for k, v in self.budget.items() if not str(k).startswith("_")},
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
    should_stop: Callable[[], bool] | None = None,
    feedback_config: FeedbackConfig | None = None,
) -> dict:
    """Run the failure-aware refinement loop.

    evaluator(failures, weights) returns (success, patch_id).  On failure the
    loop classifies the failure set and (if enable_feedback) calls
    refine_weights, then re-invokes the evaluator with updated weights.
    enable_feedback=False is the ablation control: weights stay fixed.

    ``feedback_config`` selects *which* feedback mechanism advances the weights
    (r2 §3.4):

    * ``None`` (default) — the legacy per-round ``refine_weights`` ``+=1.0``
      update.  This is the exact behaviour the 0a equivalence gate pinned, so
      the default must stay bit-identical.
    * ``LEGACY_CONFIG`` — the EMA formulation at ``(rho=0, eta=1, clip off)``.
      By r2 §3.3 property 2 it is bit-identical to the default path; the two
      exist so a run can *prove* the equivalence on the same CLI rather than
      only in a unit test.
    * ``ADAPTIVE_CONFIG`` — ``rho=0.5, eta_add=0.5, eta_c=0.25, clip on``: the
      L2 experiment arm.

    ``enable_feedback=False`` still wins: the failure set is recorded (so the
    failure history stays comparable across arms) but neither mechanism runs
    and the EMA does not advance (contract §2.3 ruling 1 / ruling 3).
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
    feedback_state = FailureFeedbackState()
    weights_trace: list[dict] = []
    ema_trace: list[dict] = []
    cone_limit_trace: list[int] = []

    def _snapshot(round_id: int) -> None:
        """r2 §3.6: per-round traces for explainability / review reproducibility."""
        weights_trace.append({"round_id": round_id, **asdict(weights)})
        ema_trace.append({
            "round_id": round_id,
            "ema": {key.value: float(value)
                    for key, value in sorted(feedback_state.ema.items(),
                                             key=lambda kv: kv[0].value)},
            "count": {key.value: int(value)
                      for key, value in sorted(feedback_state.count.items(),
                                               key=lambda kv: kv[0].value)},
        })
        cone_limit_trace.append(
            int(getattr(weights, "max_cone_gates", 1000)))

    history: list[dict] = []
    actions_history: list[list[str]] = []
    accepted_any = False

    def _extras() -> dict:
        """r2 §3.6 collection fields carried into every return shape."""
        return {
            "enable_feedback": bool(enable_feedback),
            "feedback_config": (None if feedback_config is None
                                else asdict(feedback_config)),
            "weights_trace": weights_trace,
            "failure_ema_trace": ema_trace,
            "cone_limit_trace": cone_limit_trace,
        }

    for iteration in range(1, config.max_iterations + 1):
        # r2 §3.6: record the parameter state *in force for this round* —
        # this is what the round's candidate ordering was computed from.
        _snapshot(iteration)
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
            stop_after_success = should_stop is not None and should_stop()
            history.append(
                {
                    "iteration": iteration,
                    "status": "accepted" if (continue_after_success or stop_after_success) else "success",
                    "patch_id": patch_id,
                    "wns": extra.get("wns") if extra else None,
                    "actions": [],
                }
            )
            if stop_after_success:
                history.append({
                    "iteration": iteration, "status": "stopped",
                    "patch_id": patch_id, "wns": extra.get("wns") if extra else None,
                    "actions": [], "failures": sorted(f.value for f in failures),
                })
                return {
                    "success": True,
                    "iterations": iteration,
                    "final_patch_id": patch_id,
                    "history": history,
                    "actions_history": actions_history,
                    "weights": weights,
                    **_extras(),
                }
            if not continue_after_success:
                return {
                    "success": True,
                    "iterations": iteration,
                    "final_patch_id": patch_id,
                    "history": history,
                    "weights": weights,
                    **_extras(),
                }
            continue
        if should_stop is not None and should_stop():
            history.append({
                "iteration": iteration, "status": "stopped",
                "patch_id": patch_id, "wns": extra.get("wns") if extra else None,
                "actions": [], "failures": sorted(f.value for f in failures),
            })
            return {
                "success": accepted_any,
                "iterations": iteration,
                "final_patch_id": patch_id if accepted_any else None,
                "history": history,
                "actions_history": actions_history,
                "weights": weights,
                **_extras(),
            }
        if enable_feedback and feedback_config is not None:
            # L2 arm (r2 §3.2): additive EMA-smoothed feedback.  An accepted
            # round never reaches this line (the success branches return or
            # `continue` above), which is contract §2.3 ruling 3 — accept does
            # not advance the EMA.
            cone_limit = int(getattr(weights, "max_cone_gates", 1000))
            # describe_actions reads the same private plan as update_feedback,
            # so the recorded action list can never disagree with the mutation.
            actions = describe_actions(failures, feedback_config,
                                       feedback_state, iteration)
            feedback_state, weights, cone_limit = update_feedback(
                feedback_state, weights, failures, cone_limit,
                feedback_config, iteration,
            )
        elif enable_feedback:
            decision = refine_weights(weights, failures)
            if decision is not None:
                weights = decision.weights
                actions = decision.actions
            else:
                actions = []
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
        **_extras(),
    }
