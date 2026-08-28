"""RunSpec: single serializable source of truth for one FAECO run."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field

SCHEMA_VERSION = 1


@dataclass(frozen=True)
class RunSpec:
    schema_version: int = SCHEMA_VERSION
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    commit: str = ""
    branch: str = ""
    toolchain: dict = field(default_factory=dict)
    case_id: str = ""
    input_hash: str = ""
    search_policy: str = "balanced"
    seed: int = 20260828
    strategies: tuple[str, ...] = ("R", "G", "B", "JOINT", "TOPOLOGY")
    candidate_timeout_s: float = 300.0
    campaign_wall_timeout_s: float = 0.0
    sta_budget: int = 2000
    formal_budget: int = 200
    patch_budget: int = 32
    max_iterations: int = 8
    min_gain_ns: float = 0.001
    max_patch_ratio: float = 0.02
    required_metrics: tuple[str, ...] = ("setup_wns", "setup_tns")
    balanced_min_validated_per_family: int = 3
    balanced_joint_quota: int = 2
    artifact_retention: str = "A"
    output_dir: str = ""

    @classmethod
    def defaults(cls) -> "RunSpec":
        return cls()

    def with_overrides(self, overrides: dict) -> "RunSpec":
        data = asdict(self)
        data.update(overrides)
        return RunSpec(**data)

    def resolved_snapshot(self) -> str:
        return json.dumps(
            asdict(self),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )


def config_hash(spec: RunSpec) -> str:
    """Stable hash over configuration, excluding the run-id identity field.

    Two runs with identical configuration (same inputs, policy, budgets,
    seed) must produce the same hash so manifests and replay checks can
    compare them; ``run_id`` is identity, not configuration.
    """
    data = asdict(spec)
    data.pop("run_id", None)
    canonical = json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
