"""Sentinel run manifests and fixed input hashing."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_input_hash(sources: dict[str, Path]) -> str:
    entries = []
    for logical in sorted(sources):
        path = Path(sources[logical])
        if not path.is_file():
            raise FileNotFoundError(f"sentinel input missing: {logical} -> {path}")
        entries.append((logical, sha256_file(path)))
    h = hashlib.sha256()
    for logical, file_sha in entries:
        h.update(logical.encode("utf-8"))
        h.update(b"\x00")
        h.update(file_sha.encode("ascii"))
        h.update(b"\x00")
    return h.hexdigest()


@dataclass(frozen=True)
class RunManifest:
    schema_version: int = SCHEMA_VERSION
    run_id: str = ""
    circuit_id: str = ""
    search_policy: str = ""
    period_ns: float = 0.0
    input_hash: str = ""
    run_spec_hash: str = ""
    resolved_snapshot: str = ""
    started_at_utc: str = ""
    argv: list[str] = field(default_factory=list)
    toolchain: dict = field(default_factory=dict)
    outcome: dict = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def new_run_id(circuit_id: str, policy: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{circuit_id}-{policy}-{stamp}-{uuid.uuid4().hex[:8]}"


def collect_soft_cost_events(trials: list[dict], soft_cap_s: float = 60.0) -> list[dict]:
    """Aggregate STA trials over a soft runtime cap into cost-only events.

    Soft-cost events never change acceptance; the caller records them in the
    manifest outcome so a large circuit like b17 can show that a slow STA run
    was a cost event, not a false failure.
    """
    events = []
    for trial in trials:
        runtime_s = trial.get("runtime_s")
        if runtime_s is None:
            continue
        if runtime_s > soft_cap_s:
            events.append(
                {
                    "kind": "soft_cost_over_limit",
                    "message": f"STA {runtime_s:.1f}s > {soft_cap_s:.0f}s soft cap",
                    "measured_s": runtime_s,
                    "candidate_hash": trial.get("candidate_hash", ""),
                    "accepted": bool(trial.get("accepted")),
                }
            )
    return events
