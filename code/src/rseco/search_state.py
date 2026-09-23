"""Auditable search state (FAECO-v2, path B) — the single runtime state owner.

Implements G2 and G3 from
``project_docs/planning/FAECO_V2_IMPL_CONTRACT_20260923.md``:

* **G2** — which fields ``feedback-off`` / ``reject`` / ``rollback`` each update.
  The rule of thumb: ``rollback`` restores the *decision* state, never the
  *audit and budget* state.
* **G3** — the checkpoint field set, ``netlist_epoch``, and restore consistency
  (R1-R6).

Two deliberate deviations from the contract's illustrative pseudocode, both
recorded as amendments in §8.6 of that document:

1. ``round_id`` is advanced by :meth:`begin_round`, once per round, rather than
   inside ``accept_patch`` / ``record_rejection`` — otherwise a round that both
   rejects candidates and accepts one would advance the counter twice.
2. ``candidate identity`` is the composite ``sha256(netlist_hash || candidate_hash)``
   (:meth:`candidate_key`), because the pre-existing ``candidate_hash`` omits the
   base netlist and would therefore de-duplicate legitimate candidates across
   rounds.
"""

from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .failures import FailureType
from .feedback import (
    FeedbackConfig,
    FailureFeedbackState,
    describe_actions,
    update_feedback,
)
from .refinement import RefinementWeights

#: Values accepted by :meth:`SearchState.set_stop_reason` (kept identical to the
#: codex-lineage implementation so persisted artifacts stay readable).
_STOP_REASONS = frozenset(
    {
        "timing_met",
        "no_new_candidate",
        "stagnation",
        "sta_budget",
        "formal_budget",
        "wall_timeout",
        "max_patches",
        "max_iterations",
    }
)

#: Checkpoint format version.  Bumped only on an incompatible change; restore
#: refuses anything else rather than silently degrading (contract R1).
SCHEMA_VERSION = 1

#: F1-F6 — the *method* failure layer.  Only these may move weights or the EMA.
ATTRIBUTABLE_FAILURES: frozenset[FailureType] = frozenset(FailureType)

#: ``W_*`` — the *tool / implementation / infrastructure* layer.  These are
#: recorded for audit and reported separately; they must never enter the EMA
#: (contract §4.1), otherwise method failure and tool failure become
#: indistinguishable and "Failure-Aware" stops meaning anything.
W_STAGE_TAGS: frozenset[str] = frozenset(
    {
        "W_EXTRACT_INVARIANT",
        "W_ABC_ERR",
        "W_ABC_TIMEOUT",
        "W_LIB_OUT_OF_SET",
        "W_GRAFT_ERROR",
        "W_STRUCT_ERROR",
        "W_STALE_CANDIDATE",
        "W_BUDGET_EXHAUSTED",
    }
)

#: Failure layer that is *not* F1-F6 and *not* a ``W_*`` tag either: the
#: techmap-stage equivalence check runs after resynthesis, so its failure says
#: nothing about the method's candidate logic and must be tracked on its own.
TECHMAP_MISMATCH_TAG = "S_TECHMAP_MISMATCH"


class StateConsistencyError(RuntimeError):
    """The state was asked to do something that would break an invariant."""


class CheckpointError(RuntimeError):
    """A checkpoint failed the R1-R6 restore contract."""


def split_attribution(
    failures: set[FailureType], stage_tags: list[str] | tuple[str, ...] = ()
) -> tuple[set[FailureType], list[str]]:
    """Split pipeline results into the layer that may move weights and the layer that may not.

    Returns ``(attributable, w_tags)``.  Only ``attributable`` may be handed to
    :func:`~rseco.feedback.update_feedback` (contract §4.3).
    """
    tags = [str(tag) for tag in stage_tags]
    unknown = [tag for tag in tags if tag not in W_STAGE_TAGS and tag != TECHMAP_MISMATCH_TAG]
    if unknown:
        raise ValueError(f"unclassified stage tag(s): {sorted(unknown)}")
    return {failure for failure in failures if failure in ATTRIBUTABLE_FAILURES}, tags


@dataclass(frozen=True)
class DecisionSnapshot:
    """Everything :meth:`SearchState.rollback` must undo, captured atomically.

    Deliberately excludes the netlist *text*: it is recoverable from
    ``accepted_patches`` (or ``initial_netlist_text``), so storing it would
    multiply checkpoint size for no information gain.  ``netlist_hash`` is kept
    so the reconstruction can be verified on restore (contract R5).
    """

    netlist_epoch: int
    netlist_hash: str
    current_wns: float | None
    current_tns: float | None
    current_min_slack: float | None
    critical_endpoints: tuple[str, ...]
    critical_instances: tuple[str, ...]
    cone_gates: tuple[str, ...]
    refinement_weights: RefinementWeights
    failure_feedback: FailureFeedbackState
    cone_limit: int

    def to_dict(self) -> dict:
        return {
            "netlist_epoch": int(self.netlist_epoch),
            "netlist_hash": self.netlist_hash,
            "current_wns": self.current_wns,
            "current_tns": self.current_tns,
            "current_min_slack": self.current_min_slack,
            "critical_endpoints": list(self.critical_endpoints),
            "critical_instances": list(self.critical_instances),
            "cone_gates": list(self.cone_gates),
            "refinement_weights": asdict(self.refinement_weights),
            "failure_feedback": self.failure_feedback.to_dict(),
            "cone_limit": int(self.cone_limit),
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "DecisionSnapshot":
        return cls(
            netlist_epoch=int(payload["netlist_epoch"]),
            netlist_hash=str(payload["netlist_hash"]),
            current_wns=payload.get("current_wns"),
            current_tns=payload.get("current_tns"),
            current_min_slack=payload.get("current_min_slack"),
            critical_endpoints=tuple(payload.get("critical_endpoints") or ()),
            critical_instances=tuple(payload.get("critical_instances") or ()),
            cone_gates=tuple(payload.get("cone_gates") or ()),
            refinement_weights=RefinementWeights(**payload.get("refinement_weights", {})),
            failure_feedback=FailureFeedbackState.from_dict(payload.get("failure_feedback") or {}),
            cone_limit=int(payload.get("cone_limit", 1000)),
        )


@dataclass
class SearchState:
    """Auditable mutable state for one timing-closure search.

    ``current_netlist_text`` is the transaction value: callers either append an
    accepted patch with :meth:`accept_patch`, or leave the state untouched.  A
    multi-round run is therefore restartable, and ``accepted_patches`` is the
    source of truth for :meth:`replay`.
    """

    initial_netlist_text: str
    current_netlist_text: str
    run_config: dict = field(default_factory=dict)

    netlist_epoch: int = 0
    round_id: int = 0

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

    # Decision state (path B: the EMA history lives here, never in the weights).
    refinement_weights: RefinementWeights = field(default_factory=RefinementWeights)
    failure_feedback: FailureFeedbackState = field(default_factory=FailureFeedbackState)
    cone_limit: int = 1000
    enable_feedback: bool = True
    feedback_config: FeedbackConfig = field(default_factory=FeedbackConfig)

    _snapshots: list[DecisionSnapshot] = field(default_factory=list, repr=False)
    _budget_lock: object = field(default_factory=threading.Lock, repr=False, compare=False)

    # ------------------------------------------------------------------ hashing

    @staticmethod
    def hash_text(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @property
    def current_netlist_hash(self) -> str:
        return self.hash_text(self.current_netlist_text)

    @property
    def config_hash(self) -> str:
        """Deterministic fingerprint of the effective run configuration."""
        payload = json.dumps(self.run_config, sort_keys=True, separators=(",", ":"), default=str)
        return self.hash_text(payload)

    def candidate_hash(
        self, *, gates=(), boundary_inputs=(), boundary_outputs=(), action_hash=""
    ) -> str:
        """Hash the canonical cut/action identity, independent of the base netlist."""
        payload = {
            "gates": sorted(set(map(str, gates))),
            "boundary_inputs": sorted(set(map(str, boundary_inputs))),
            "boundary_outputs": sorted(set(map(str, boundary_outputs))),
            "action": str(action_hash),
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return self.hash_text(raw)

    def candidate_key(self, candidate_hash: str | None = None) -> str:
        """Composite identity: (base netlist content) x (cut/action identity).

        ``candidate_hash`` alone omits the base netlist, so the same cut window
        on a different epoch would look like a candidate that was already
        tested.  The composite key is what :attr:`tested_candidate_hashes` holds.
        """
        return self.hash_text(f"{self.current_netlist_hash}:{candidate_hash or ''}")

    def mark_candidate_tested(self, candidate_hash: str | None = None) -> bool:
        """Return ``False`` when this candidate was already tested (including failures)."""
        key = self.candidate_key(candidate_hash)
        if key in self.tested_candidate_hashes:
            return False
        self.tested_candidate_hashes.add(key)
        return True

    def is_stale(self, epoch_at_generation: int) -> bool:
        """Contract §3.1: a candidate is stale once the netlist has moved on."""
        return int(epoch_at_generation) < self.netlist_epoch

    # ---------------------------------------------------------------- budgeting

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

    def budget_used(self, kind: str) -> int:
        return int(self.budget.get(f"{kind}_used", 0))

    def deadline_expired(self) -> bool:
        deadline = self.budget.get("_deadline_monotonic")
        return deadline is not None and __import__("time").perf_counter() >= float(deadline)

    # ------------------------------------------------------- round bookkeeping

    def begin_round(self) -> int:
        """Advance and return the round counter.  Once per round (amendment 1)."""
        self.round_id += 1
        return self.round_id

    # ------------------------------------------------------------------- events

    def record_failure(self, event: dict) -> None:
        """Append one failure event, de-duplicated by content-derived ``event_id``."""
        normalized = dict(event)
        candidate_hash = str(normalized.get("candidate_hash") or self.current_netlist_hash)
        normalized["candidate_hash"] = candidate_hash
        normalized["cut_hash"] = str(normalized.get("cut_hash") or candidate_hash)
        normalized.setdefault("round_id", int(self.round_id))
        normalized.setdefault("result_layer", "F" if normalized.get("failures") else "W")
        normalized.setdefault("endpoint", None)
        normalized.setdefault("path", [])
        normalized.setdefault("net", None)
        normalized.setdefault("action_scope", [])
        normalized.setdefault("threshold", None)
        normalized.setdefault("observed_value", None)
        normalized.setdefault("severity", "hard")
        normalized.setdefault("runtime_s", 0.0)
        normalized.setdefault("stage_tags", [])
        normalized.setdefault("failures", [])
        normalized.setdefault("evidence", {})
        normalized.setdefault("invalidated_by_rollback", False)
        normalized.setdefault(
            "event_id",
            hashlib.sha256(
                json.dumps(
                    {
                        "type": normalized.get("type"),
                        "candidate_hash": candidate_hash,
                        "cut_hash": normalized["cut_hash"],
                        "round_id": normalized["round_id"],
                        "endpoint": normalized.get("endpoint"),
                        "path": normalized.get("path", []),
                        "net": normalized.get("net"),
                        "action_scope": normalized.get("action_scope", []),
                        "threshold": normalized.get("threshold"),
                        "observed_value": normalized.get("observed_value"),
                        "stage_tags": normalized.get("stage_tags", []),
                        "failures": normalized.get("failures", []),
                        "evidence": normalized.get("evidence", {}),
                    },
                    sort_keys=True,
                    default=str,
                ).encode()
            ).hexdigest(),
        )
        if any(existing.get("event_id") == normalized["event_id"] for existing in self.failure_history):
            return
        self.failure_history.append(normalized)

    def record_rejection(
        self,
        *,
        candidate_hash: str | None = None,
        failures: set[FailureType] | None = None,
        stage_tags: list[str] | tuple[str, ...] = (),
        runtime_s: float = 0.0,
        patch_id: str | None = None,
        endpoint: str | None = None,
        evidence: dict | None = None,
    ) -> list[str]:
        """Handle one rejected candidate.  Returns the weight actions applied.

        Contract §2.3 ruling 1 — ``feedback-off`` closes only the
        *feedback -> parameters* edge: classification, the failure log, the
        de-duplication mark and budget accounting all still happen; only the
        weights, the EMA and the cone limit are frozen.
        """
        attributable, tags = split_attribution(failures or set(), stage_tags)
        self.record_failure(
            {
                "type": "candidate_rejected",
                "candidate_hash": candidate_hash or self.current_netlist_hash,
                "patch_id": patch_id,
                "endpoint": endpoint,
                "runtime_s": float(runtime_s),
                "stage_tags": sorted(tags),
                "failures": sorted(failure.value for failure in attributable),
                "evidence": dict(evidence or {}),
            }
        )
        if candidate_hash is not None:
            self.mark_candidate_tested(candidate_hash)
        if not (self.enable_feedback and attributable):
            return []
        actions = describe_actions(attributable, self.feedback_config, self.failure_feedback, self.round_id)
        self.failure_feedback, self.refinement_weights, self.cone_limit = update_feedback(
            self.failure_feedback,
            self.refinement_weights,
            attributable,
            self.cone_limit,
            self.feedback_config,
            self.round_id,
        )
        return actions

    def record_stale_candidate(self, *, candidate_hash: str | None = None, epoch_at_generation: int = 0) -> None:
        """Log a candidate invalidated by a commit in the same round (contract §3.1).

        Stale candidates are not evaluated and not billed, so this deliberately
        leaves the EMA, the weights, the cone limit and
        ``tested_candidate_hashes`` untouched.
        """
        self.record_failure(
            {
                "type": "candidate_stale",
                "candidate_hash": candidate_hash or self.current_netlist_hash,
                "stage_tags": ["W_STALE_CANDIDATE"],
                "observed_value": int(epoch_at_generation),
                "threshold": int(self.netlist_epoch),
            }
        )

    def accept_patch(
        self,
        patch_id: str,
        candidate_netlist_text: str,
        *,
        wns=None,
        tns=None,
        min_slack=None,
        candidate_hash=None,
        critical_endpoints=None,
        critical_instances=None,
        cone_gates=None,
        metadata=None,
    ) -> dict:
        """Atomically append an accepted patch, advance ``G_r`` and the epoch.

        The decision snapshot is pushed here, in the same call as the
        transaction snapshot, so the two can never be taken at different points
        in time (contract §2.4).
        """
        record = {
            "patch_id": str(patch_id),
            "candidate_hash": candidate_hash or self.hash_text(candidate_netlist_text),
            "base_netlist_hash": self.current_netlist_hash,
            "netlist_hash": self.hash_text(candidate_netlist_text),
            "netlist_text": candidate_netlist_text,
            "round_id": int(self.round_id),
            "epoch_before": int(self.netlist_epoch),
            "epoch_after": int(self.netlist_epoch) + 1,
            "wns": wns,
            "tns": tns,
            "min_slack": min_slack,
            "metadata": dict(metadata or {}),
        }
        self._snapshots.append(self._capture_decision_snapshot())
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

        self.netlist_epoch = len(self.accepted_patches)
        # Contract §2.3 ruling 3: an accepting round does not advance the EMA.
        return record

    def _capture_decision_snapshot(self) -> DecisionSnapshot:
        return DecisionSnapshot(
            netlist_epoch=int(self.netlist_epoch),
            netlist_hash=self.current_netlist_hash,
            current_wns=self.current_wns,
            current_tns=self.current_tns,
            current_min_slack=self.current_min_slack,
            critical_endpoints=tuple(self.critical_endpoints),
            critical_instances=tuple(self.critical_instances),
            cone_gates=tuple(self.current_cone_gates),
            refinement_weights=self.refinement_weights,
            failure_feedback=self.failure_feedback,
            cone_limit=int(self.cone_limit),
        )

    def rollback(self) -> bool:
        """Undo the last accepted patch.

        Contract §2.3 ruling 2 — restores the *decision* state (epoch, weights,
        EMA, cone limit) together with the transaction and measurement fields,
        but never the *audit and budget* state: ``tested_candidate_hashes``,
        ``budget`` and ``failure_history`` are irreversible facts.  Events that
        belonged to the undone step are flagged ``invalidated_by_rollback``
        instead of being deleted.
        """
        if not self._snapshots or not self.accepted_patches:
            return False

        snapshot = self._snapshots[-1]
        previous_text = (
            self.accepted_patches[-2]["netlist_text"]
            if len(self.accepted_patches) >= 2
            else self.initial_netlist_text
        )
        if self.hash_text(previous_text) != snapshot.netlist_hash:
            raise StateConsistencyError(
                "rollback refused: the patch log is not contiguous with the snapshot"
            )

        undone = self.accepted_patches.pop()
        self._snapshots.pop()

        self.current_netlist_text = previous_text
        self.current_wns = snapshot.current_wns
        self.current_tns = snapshot.current_tns
        self.current_min_slack = snapshot.current_min_slack
        self.critical_endpoints = list(snapshot.critical_endpoints)
        self.critical_instances = list(snapshot.critical_instances)
        self.current_cone_gates = list(snapshot.cone_gates)
        self.refinement_weights = snapshot.refinement_weights
        self.failure_feedback = snapshot.failure_feedback
        self.cone_limit = int(snapshot.cone_limit)

        self.netlist_epoch = len(self.accepted_patches)
        accepted_round = int(undone.get("round_id", self.round_id))
        for event in self.failure_history:
            if int(event.get("round_id", 0)) >= accepted_round:
                event["invalidated_by_rollback"] = True
        return True

    @staticmethod
    def replay(initial_netlist_text: str, accepted_patches: list[dict]) -> str:
        """Replay recorded candidate texts and return the final netlist."""
        current = initial_netlist_text
        for index, patch in enumerate(accepted_patches):
            base = patch.get("base_netlist_hash")
            if base and base != SearchState.hash_text(current):
                raise CheckpointError(
                    f"accepted patch log is not a contiguous replay (patch index {index})"
                )
            current = str(patch["netlist_text"])
        return current

    def set_stop_reason(self, reason: str) -> None:
        if reason not in _STOP_REASONS:
            raise ValueError(f"unsupported stop_reason: {reason}")
        if self.stop_reason is not None and self.stop_reason != reason:
            raise ValueError(f"stop_reason already set to {self.stop_reason}")
        self.stop_reason = reason

    def check_invariants(self) -> None:
        """``netlist_epoch == len(accepted_patches)`` and ``round_id >= netlist_epoch``."""
        if self.netlist_epoch != len(self.accepted_patches):
            raise StateConsistencyError(
                f"netlist_epoch ({self.netlist_epoch}) != len(accepted_patches) ({len(self.accepted_patches)})"
            )
        if self.round_id < self.netlist_epoch:
            raise StateConsistencyError(
                f"round_id ({self.round_id}) < netlist_epoch ({self.netlist_epoch})"
            )

    # -------------------------------------------------------------- checkpoint

    def to_dict(self) -> dict:
        """Full checkpoint payload (contract §3.2).  Deterministic under ``sort_keys``."""
        return {
            "schema_version": SCHEMA_VERSION,
            "config_hash": self.config_hash,
            "run_config": self.run_config,
            "initial_netlist_text": self.initial_netlist_text,
            "current_netlist_text": self.current_netlist_text,
            "current_netlist_hash": self.current_netlist_hash,
            "netlist_epoch": int(self.netlist_epoch),
            "round_id": int(self.round_id),
            "accepted_patches": list(self.accepted_patches),
            "snapshots": [snapshot.to_dict() for snapshot in self._snapshots],
            "current_wns": self.current_wns,
            "current_tns": self.current_tns,
            "current_min_slack": self.current_min_slack,
            "critical_endpoints": list(self.critical_endpoints),
            "critical_instances": list(self.critical_instances),
            "current_cone_gates": list(self.current_cone_gates),
            "refinement_weights": asdict(self.refinement_weights),
            "failure_feedback": self.failure_feedback.to_dict(),
            "cone_limit": int(self.cone_limit),
            "enable_feedback": bool(self.enable_feedback),
            "feedback_config": asdict(self.feedback_config),
            "effective_config": {
                "enable_feedback": bool(self.enable_feedback),
                "strategies": self.run_config.get("strategies"),
                "init_weights": self.run_config.get("init_weights"),
                "random_order": self.run_config.get("random_order"),
                "seed": self.run_config.get("seed"),
            },
            "failure_history": [dict(event) for event in self.failure_history],
            "tested_candidate_hashes": sorted(self.tested_candidate_hashes),
            "budget": {key: value for key, value in self.budget.items() if not str(key).startswith("_")},
            "stop_reason": self.stop_reason,
        }

    def to_checkpoint_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, indent=2, default=str)

    def checkpoint_filename(self) -> str:
        return f"state_checkpoint_e{self.netlist_epoch:03d}_r{self.round_id:03d}.json"

    def save_checkpoint(self, directory: Path) -> Path:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / self.checkpoint_filename()
        path.write_text(self.to_checkpoint_json(), encoding="utf-8")
        return path

    @classmethod
    def from_dict(cls, payload: dict) -> "SearchState":
        """Restore a checkpoint under the R1-R6 contract.  Raises on any violation."""
        if int(payload.get("schema_version", -1)) != SCHEMA_VERSION:
            raise CheckpointError(
                f"unsupported schema_version: {payload.get('schema_version')!r} (expected {SCHEMA_VERSION})"
            )

        state = cls(
            initial_netlist_text=str(payload["initial_netlist_text"]),
            current_netlist_text=str(payload["current_netlist_text"]),
            run_config=dict(payload.get("run_config") or {}),
            netlist_epoch=int(payload.get("netlist_epoch", 0)),
            round_id=int(payload.get("round_id", 0)),
            current_wns=payload.get("current_wns"),
            current_tns=payload.get("current_tns"),
            current_min_slack=payload.get("current_min_slack"),
            critical_endpoints=list(payload.get("critical_endpoints") or []),
            critical_instances=list(payload.get("critical_instances") or []),
            current_cone_gates=list(payload.get("current_cone_gates") or []),
            accepted_patches=[dict(patch) for patch in payload.get("accepted_patches") or []],
            failure_history=[dict(event) for event in payload.get("failure_history") or []],
            tested_candidate_hashes=set(payload.get("tested_candidate_hashes") or []),
            budget=dict(payload.get("budget") or {}),
            stop_reason=payload.get("stop_reason"),
            refinement_weights=RefinementWeights(**payload.get("refinement_weights", {})),
            failure_feedback=FailureFeedbackState.from_dict(payload.get("failure_feedback") or {}),
            cone_limit=int(payload.get("cone_limit", 1000)),
            enable_feedback=bool(payload.get("enable_feedback", True)),
            feedback_config=FeedbackConfig(**payload.get("feedback_config", {})),
            _snapshots=[DecisionSnapshot.from_dict(item) for item in payload.get("snapshots") or []],
        )

        # R1: configuration must match — refuse rather than degrade silently.
        if str(payload.get("config_hash", "")) != state.config_hash:
            raise CheckpointError("config_hash mismatch: checkpoint was produced by a different run configuration")

        # R2 + R3: replay must be contiguous and land on the recorded hash.
        replayed = cls.replay(state.initial_netlist_text, state.accepted_patches)
        if cls.hash_text(replayed) != str(payload.get("current_netlist_hash", "")):
            raise CheckpointError("current_netlist_hash does not match the replayed netlist")

        # R4: epoch invariant.
        if state.netlist_epoch != len(state.accepted_patches):
            raise CheckpointError(
                f"netlist_epoch ({state.netlist_epoch}) != len(accepted_patches) ({len(state.accepted_patches)})"
            )

        # R5: every snapshot must sit exactly where it claims in the replay chain.
        if len(state._snapshots) != len(state.accepted_patches):
            raise CheckpointError(
                f"snapshot count ({len(state._snapshots)}) != accepted patch count ({len(state.accepted_patches)})"
            )
        for index, snapshot in enumerate(state._snapshots):
            if int(snapshot.netlist_epoch) != index:
                raise CheckpointError(f"snapshot {index} records epoch {snapshot.netlist_epoch}")
            expected_text = (
                state.accepted_patches[index - 1]["netlist_text"]
                if index >= 1
                else state.initial_netlist_text
            )
            if cls.hash_text(expected_text) != snapshot.netlist_hash:
                raise CheckpointError(f"snapshot {index} hash does not match the replay chain")
        return state
