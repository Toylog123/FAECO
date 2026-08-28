# FAECO Phase 2 Sentinel Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that the Phase 1 semantic contracts (RunSpec + config hash, budget/soft-cost separation, pure AcceptancePolicy, fast/balanced/exhaustive search policy) solve real problems on a fixed sentinel circuit set, without running the full benchmark. Every sentinel run is recorded with a fixed input hash and a resolved RunSpec manifest so Phase 3 refactors can re-run the same sentinels and Phase 4 can aggregate them.

**Architecture:** Phase 2 adds two small infrastructure pieces first (sentinel manifest + input hash; explicit search-policy wiring with additive diagnostic fields, no behavior change), then runs the six sentinel cases strictly in order `s27 -> s382 -> b15 -> b17 -> b18 -> picorv32`. A case must pass its own gate before the next, more expensive case starts. No full benchmark, no modularization (Phase 3), no manifest-driven evidence system (Phase 4).

**Tech Stack:** Python 3.11, pytest, PowerShell, Yosys/OpenSTA (native OSS-CAD 0.67 at `C:\oss-cad-suite-build\oss-cad-suite`), git worktrees.

---

## 0. Fixed references and worktree layout

Read the spec first: `docs/superpowers/specs/2026-08-28-faeco-stabilization-modularization-design.md` (§4.4 SearchPolicy, §4.6 AcceptancePolicy, §4.7 EvidenceStore, §9 rollback, G5).

Worktrees used by this plan:

- Governance worktree: `C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-unified-loop` (branch `codex/faeco-unified-loop`; contains design/plan docs; force-added because `docs/superpowers/` is gitignored).
- Implementation worktree: `C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-phase0-stabilization` (branch `codex/faeco-phase0-stabilization`).

Phase 2 implementation starts at commit `611ffe8` (Phase 1 complete; verification summary at head `e90e134` refreshed in `611ffe8`).

No task may modify the dirty main checkout at `D:\BaiduSyncdisk\03_FAECO` except reading raw benchmark files and old experiment artifacts. Sentinel runs write only into the implementation worktree:

- Experiment outputs: `experiments/20260828_phase2_sentinel/` (gitignored `experiments/2026*/`; new run IDs only, never overwrite).
- Raw benchmark files needed for the sentinels: copied into `benchmarks/raw/` (gitignored) from the main checkout.
- Committed evidence: `docs/phase2/*.md` + `docs/phase2/manifests/*.json`.

---

## 1. File structure

| File | Responsibility |
|---|---|
| `src/rseco/sentinel.py` | Sentinel run manifest schema, fixed input hash, run ID |
| `tests/test_sentinel.py` | Hash determinism/sensitivity, manifest schema, run ID |
| `src/rseco/search_policy.py` | Add pure `resolve_search_policy` and `round_coverage` helpers |
| `tests/test_search_policy.py` | Extend with policy resolution and coverage helpers |
| `src/rseco/real_wns.py` | Accept `search_policy`, keep `early_stop` deprecated compat, record coverage + round stop reason (additive) |
| `scripts/run_outerloop_real_wns.py` | Pass policy to evaluator; write `sentinel_manifest.json`; record input hash + argv |
| `tests/test_search_policy_wiring.py` | Wiring tests (no STA execution) |
| `docs/phase2/sentinel-{s27,s382,b15,b17,b18,picorv32}.md` | Per-case evidence records |
| `docs/phase2/manifests/*.json` | Committed manifest copies per sentinel run |
| `docs/phase2/g5-matrix.md` | G5 gate matrix and final Phase 2 exit record |

---

## 2. Sentinel contract

Every sentinel run MUST produce, next to `outerloop_result.json`, a `sentinel_manifest.json` with:

- `schema_version: 1`
- `run_id`: `{circuit}-{policy}-{YYYYMMDD}T{HHMMSS}Z` (unique, never reused)
- `circuit_id`, `search_policy`, `period_ns`
- `input_hash`: SHA-256 over sorted `(logical_name, file_sha256)` entries for the actual files consumed (source Verilog, Liberty lib, priority table if used). Missing file => hard failure, never a partial run.
- `run_spec_hash`: `config_hash(RunSpec)` where the RunSpec fields supported by the CLI are filled from CLI overrides
- `resolved_snapshot`: the RunSpec JSON snapshot
- `argv`: the exact command line (replay contract)
- `toolchain`: `{git_head_sha, yosys_version, opensta_version, oss_cad_root}` (version capture failures recorded as `null` + note, not silent)
- `outcome`: `{success, iterations, wns_history, baseline_wns, final_patch_id, n_candidate_sta_runs, round_stop_reasons, soft_cost_events, hard_timeout_events}`

RunSpec defaults relevant to sentinels: `search_policy=balanced`, `balanced_min_validated_per_family=3`, `balanced_joint_quota=2`, `min_gain_ns=0.001`, `max_patch_ratio=0.02`.

---

## Task 1 (P2.1): Sentinel manifest and fixed input hash

**Files:**
- Create: `src/rseco/sentinel.py`
- Create: `tests/test_sentinel.py`
- Modify: `scripts/run_outerloop_real_wns.py`

- [ ] **Step 1.1: Write failing tests**

`tests/test_sentinel.py`:

```python
"""Sentinel manifest and fixed input hash contracts."""

from __future__ import annotations

import json

from rseco.sentinel import RunManifest, compute_input_hash, new_run_id, sha256_file


def test_input_hash_is_stable_and_order_independent(tmp_path) -> None:
    a = tmp_path / "a.v"; b = tmp_path / "b.lib"
    a.write_text("module a;\n", encoding="utf-8")
    b.write_text("LIB\n", encoding="utf-8")
    first = compute_input_hash({"b": b, "a": a})
    second = compute_input_hash({"a": a, "b": b})
    third = compute_input_hash({"a": a, "b": b})
    assert first == second == third
    assert len(first) == 64


def test_input_hash_changes_on_content_change(tmp_path) -> None:
    f = tmp_path / "c.v"; f.write_text("v1", encoding="utf-8")
    before = compute_input_hash({"c": f})
    f.write_text("v2", encoding="utf-8")
    after = compute_input_hash({"c": f})
    assert before != after


def test_input_hash_raises_on_missing_file(tmp_path) -> None:
    import pytest

    with pytest.raises(FileNotFoundError):
        compute_input_hash({"missing": tmp_path / "nope.v"})


def test_sha256_file_matches_bytes(tmp_path) -> None:
    f = tmp_path / "x.v"; f.write_bytes(b"abc")
    assert sha256_file(f) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_manifest_roundtrip_schema() -> None:
    m = RunManifest(
        run_id="b15-balanced-20260828T000000Z",
        circuit_id="b15",
        search_policy="balanced",
        period_ns=0.5,
        input_hash="0" * 64,
        run_spec_hash="1" * 64,
        resolved_snapshot="{}",
        started_at_utc="2026-08-28T00:00:00Z",
        toolchain={"git_head_sha": "abc"},
        outcome={"success": True},
    )
    data = json.loads(m.to_json())
    assert data["schema_version"] == 1
    assert data["run_id"] == m.run_id
    assert data["toolchain"]["git_head_sha"] == "abc"


def test_new_run_id_unique_and_parseable() -> None:
    first = new_run_id("b15", "fast")
    second = new_run_id("b15", "fast")
    assert first != second
    assert first.startswith("b15-fast-")
```

- [ ] **Step 1.2: Run tests; confirm failure**

```powershell
python -m pytest -q -p no:cacheprovider tests/test_sentinel.py
```

- [ ] **Step 1.3: Implement `src/rseco/sentinel.py`**

```python
"""Sentinel run manifests and fixed input hashing."""

from __future__ import annotations

import hashlib
import json
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
    return f"{circuit_id}-{policy}-{stamp}"
```

- [ ] **Step 1.4: Run tests; confirm pass**

```powershell
python -m pytest -q -p no:cacheprovider tests/test_sentinel.py
```

- [ ] **Step 1.5: Wire manifest into `scripts/run_outerloop_real_wns.py`**

Add `--run-id` (default `new_run_id(circuit, policy)`). After the outer loop:

- build the RunSpec from CLI where the field maps: `case_id`, `input_hash`, `search_policy`, `strategies`, `max_iterations`, `sta_budget`, `formal_budget`, `required_metrics`, `min_gain_ns` (from `--epsilon`), `output_dir`;
- write `sentinel_manifest.json` next to `outerloop_result.json` with `input_hash`, `run_spec_hash`, `resolved_snapshot`, `argv`, `toolchain` (git head sha, `yosys -V`, `opensta --version` best-effort), and `outcome`;
- also add `input_hash` and `run_spec_hash` to `outerloop_result.json`.

Input set for the hash: `{"source": circuit_path, "liberty": LIB, "priority_table": table_path}` (priority table only when used).

- [ ] **Step 1.6: Full suite and commit**

```powershell
python -m pytest -q -p no:cacheprovider
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_verification_gates.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/smoke_check.ps1
git diff --check
git add src/rseco/sentinel.py tests/test_sentinel.py scripts/run_outerloop_real_wns.py
git commit -m "feat(sentinel): manifest and fixed input hash for sentinel runs"
```

**Gate:** G5 infrastructure part (input hash + RunSpec + manifest exist and are tested).

---

## Task 2 (P2.2): Explicit search-policy wiring (additive)

**Files:**
- Modify: `src/rseco/search_policy.py`
- Modify: `tests/test_search_policy.py`
- Modify: `src/rseco/real_wns.py`
- Create: `tests/test_search_policy_wiring.py`
- Modify: `scripts/run_outerloop_real_wns.py`

- [ ] **Step 2.1: Write failing tests**

`tests/test_search_policy.py` additions:

```python
def test_resolve_policy_fast_from_early_stop() -> None:
    warnings: list[str] = []
    policy = resolve_search_policy(early_stop=True, search_policy="balanced", warn=warnings.append)
    assert policy == SearchPolicy.FAST
    assert warnings and "deprecated" in warnings[0]


def test_resolve_policy_explicit_search_policy_wins() -> None:
    policy = resolve_search_policy(early_stop=True, search_policy="exhaustive", warn=lambda m: None)
    assert policy == SearchPolicy.EXHAUSTIVE


def test_round_coverage_records_partial() -> None:
    cov = round_coverage(validated=6, generated=10, stopped_early=False)
    assert cov["validated"] == 6
    assert cov["generated"] == 10
    assert cov["partial"] is True
    assert cov["round_stop_reason"] == "budget_partial"


def test_round_coverage_fast_first_acceptable() -> None:
    cov = round_coverage(validated=3, generated=10, stopped_early=True)
    assert cov["partial"] is True
    assert cov["round_stop_reason"] == "first_acceptable"
```

`tests/test_search_policy_wiring.py`:

```python
"""RealWnsEvaluator accepts search_policy without changing legacy behavior."""

from __future__ import annotations

import warnings

import pytest

from rseco.real_wns import RealWnsEvaluator


def _minimal_evaluator(**kwargs):
    return RealWnsEvaluator(
        mapped_text="module top;\nendmodule\n",
        top_module="top",
        period=1.0,
        liberty_text="LIB",
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


def test_exhaustive_is_full_round() -> None:
    ev = _minimal_evaluator(search_policy="exhaustive")
    assert ev.early_stop is False


def test_legacy_early_stop_deprecation_warning() -> None:
    with pytest.warns(DeprecationWarning):
        ev = _minimal_evaluator(early_stop=True)
    assert ev.early_stop is True
    assert ev.search_policy.value == "fast"
```

- [ ] **Step 2.2: Run tests; confirm failure**

- [ ] **Step 2.3: Implement helpers in `search_policy.py`**

```python
def resolve_search_policy(early_stop: bool, search_policy: str = "balanced", warn=None) -> SearchPolicy:
    if early_stop:
        if warn is not None:
            warn("--early-stop is deprecated; use --search-policy fast")
        if search_policy == "balanced":
            return SearchPolicy.FAST
    return SearchPolicy(search_policy)


def round_coverage(validated: int, generated: int, stopped_early: bool) -> dict:
    partial = validated < generated
    reason = "first_acceptable" if stopped_early else ("budget_partial" if partial else "round_complete")
    return {"validated": validated, "generated": generated, "partial": partial, "round_stop_reason": reason}
```

- [ ] **Step 2.4: Wire into `RealWnsEvaluator` (additive only)**

- `__init__`: add `search_policy: str = "balanced"`; keep `early_stop: bool = False`; call `resolve_search_policy(early_stop, search_policy, warn=warnings.warn)`; store `self.search_policy` and `self.early_stop`. Import `warnings` and the helpers.
- serial branch: after `if self.early_stop and improved_now: break`, compute `stopped_early = self.early_stop and any(r.get("accepted") for r in results)`.
- record `result["coverage"] = round_coverage(len(results), len(jobs), stopped_early)` and mirror `coverage` + `search_policy` into `call_log`.

No change to acceptance, ranking, physical, or budget behavior.

- [ ] **Step 2.5: Update script to pass `search_policy=policy` (keep `early_stop=args.early_stop`)**

- [ ] **Step 2.6: Full suite and commit**

```powershell
python -m pytest -q -p no:cacheprovider
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_verification_gates.ps1
git diff --check
git add src/rseco/search_policy.py tests/test_search_policy.py src/rseco/real_wns.py tests/test_search_policy_wiring.py scripts/run_outerloop_real_wns.py
git commit -m "feat(search-policy): explicit policy wiring and round coverage records"
```

**Gate:** G4 extension (policy resolution + coverage helpers tested; behavior equivalence verified by full suite).

---

## 3. Sentinel run configuration

Copy from the main checkout (read-only source) into the implementation worktree `benchmarks/raw/`:

- `iscas89/s27.v`, `iscas89/s382.v`
- `itc99/v/b15.v`, `itc99/v/b17.v`, `itc99/v/b18.v`
- `openroad_flow_scripts_sky130hd/` (Liberty lib for mapping/STA)
- `picorv32/picorv32.v`

Base command template (PowerShell):

```powershell
$env:PYTHONPATH="src"
python scripts/run_outerloop_real_wns.py --circuit CASE --period 0.5 `
  --source-file benchmarks/raw/SRC --output-dir experiments/20260828_phase2_sentinel `
  --search-policy POLICY --max-iterations N --candidates-per-iteration 1 `
  --joint-enumerate-depth D --strategies R,G,B `
  --priority-table src/rseco/strategy_priority_table.json --workers 1
```

`fast` policy MUST run with `--workers 1` so the serial early-stop semantics are actually exercised; the manifest records `workers` via `argv`.

Per-case matrix (fixed before running; recorded in each manifest):

| Case | source | policy | iterations | joint depth | special flags |
|---|---|---|---|---|---|
| s27 | iscas89/s27.v | balanced | 3 | 0 | — |
| s382 | iscas89/s382.v | balanced | 4 | 0 | run twice for replayability |
| b15 | itc99/v/b15.v | fast, then balanced | 4 | 3 | JOINT quota observed |
| b17 | itc99/v/b17.v | balanced | 4 | 3 | watch soft-cost events |
| b18 | itc99/v/b18.v | balanced | 3 | 2 | `--physical-gate --min-physical-gain 0.0` |
| picorv32 | picorv32/picorv32.v | balanced | 4 | 0 | top module auto-selected |

Each run must finish before the next starts (no parallel expansion across cases). Long runs use session monitoring; if a case cannot complete because the tool or data is unavailable, G5 for that case is **blocked** and the case is recorded as blocked with diagnosis, never substituted with old results.

---

## Task 3 (P2.3): s27 sentinel

- [ ] **Step 3.1:** Materialize raw benchmark files in the worktree (copies, gitignored).
- [ ] **Step 3.2:** Run s27 balanced per matrix.
- [ ] **Step 3.3:** Verify the full chain: mapped netlist exists, STA ran (`sta.log`), candidates evaluated (`eval_trials.json`), SEC artifacts exist (`topology-sec`), and `sentinel_manifest.json` has input_hash + run_spec_hash + outcome.
- [ ] **Step 3.4:** Write `docs/phase2/sentinel-s27.md`, copy manifest to `docs/phase2/manifests/`, commit `docs(phase2): s27 sentinel passed`.

**Gate:** G5 s27 row (mapping/STA/candidates/SEC/manifest all present).

---

## Task 4 (P2.4): s382 sentinel

- [ ] **Step 4.1:** Run s382 balanced twice with identical config (replayability check: same input_hash and run_spec_hash; consistent success and accepted patch).
- [ ] **Step 4.2:** Verify accept/reject evidence complete: every trial has structured failure_events or accepted=True.
- [ ] **Step 4.3:** Record `docs/phase2/sentinel-s382.md` + manifests; commit `docs(phase2): s382 sentinel passed`.

**Gate:** G5 s382 row (balanced replayable; accept/reject evidence complete).

---

## Task 5 (P2.5): b15 sentinel

- [ ] **Step 5.1:** Run b15 `fast` (run A) and b15 `balanced` (run B) with separate run IDs.
- [ ] **Step 5.2:** Verify: run A `coverage.round_stop_reason == first_acceptable` with fewer trials than run B; run B evaluates the JOINT candidate before selecting best (JOINT present in trials when joint-enumerate-depth=3 produces one; otherwise the reason is recorded as `unavailable`, not silently skipped); both results recorded separately in manifests.
- [ ] **Step 5.3:** Record `docs/phase2/sentinel-b15.md` + manifests; commit `docs(phase2): b15 sentinel passed`.

**Gate:** G5 b15 row (fast vs balanced/exhaustive recorded separately; balanced does not end before checking JOINT).

---

## Task 6 (P2.6): b17 sentinel

- [ ] **Step 6.1:** Run b17 balanced.
- [ ] **Step 6.2:** Verify: any STA cost over soft cap is recorded as `BudgetKind.SOFT_COST_OVER_LIMIT` cost events only; a completed candidate that passed AcceptancePolicy is not invalidated by those events; hard candidate timeout (if any) is distinguishable with its own stop reason.
- [ ] **Step 6.3:** Record `docs/phase2/sentinel-b17.md` + manifest; commit `docs(phase2): b17 sentinel passed`.

**Gate:** G5 b17 row.

---

## Task 7 (P2.7): b18 sentinel

- [ ] **Step 7.1:** Run b18 balanced with JOINT + `--physical-gate`.
- [ ] **Step 7.2:** Verify: paired physical data (baseline/candidate SPEF WNS) and tool provenance fields are complete; the record explicitly does not claim P&R signoff.
- [ ] **Step 7.3:** Record `docs/phase2/sentinel-b18.md` + manifest; commit `docs(phase2): b18 sentinel passed`.

If b18 cannot complete fresh (tool/data unavailable), record G5 b18 as **blocked** with diagnosis and stop expanding to picorv32 until resolved.

**Gate:** G5 b18 row (paired physical data + provenance complete; no P&R signoff extrapolation).

---

## Task 8 (P2.8): picorv32 sentinel

- [ ] **Step 8.1:** Run picorv32 balanced (OOD case; top module `picorv32`).
- [ ] **Step 8.2:** Verify: correct top/clock selection (STA reports sane clock period); N/A and failures recorded separately from accepted results.
- [ ] **Step 8.3:** Record `docs/phase2/sentinel-picorv32.md` + manifest; commit `docs(phase2): picorv32 sentinel passed`.

**Gate:** G5 picorv32 row.

---

## Task 9 (P2.9): Phase 2 exit gate

- [ ] **Step 9.1:** Build `docs/phase2/g5-matrix.md` mapping every G5 row to run_id, input_hash, run_spec_hash, evidence files, and pass/blocked status.
- [ ] **Step 9.2:** Re-run `run_verification_gates.ps1` and `smoke_check.ps1`; confirm no behavior regression.
- [ ] **Step 9.3:** Rollback audit: if any policy degraded on the sentinel set, the policy batch is rolled back (not the infra); record the decision.
- [ ] **Step 9.4:** Commit `docs(phase2): phase 2 exit gate passed`; report to user with G5 matrix and the Phase 3 boundary.

**Gate:** G5 all rows passed or explicitly blocked with diagnosis.

---

## 4. Batch state machine and reporting

Each task batch is one of: `planned -> in_progress -> gate_check -> review -> completed`, or on gate failure `gate_check -> failed -> diagnose -> revised -> gate_check`. A failed gate blocks all successor tasks.

Each completed task records: task/phase, scope, files, contract changes, test commands + full results, gate matrix, risks/skips, exact commit SHA.

## 5. Rollback and recovery

- One commit per small batch; no `git reset --hard`.
- New experiment runs use new run IDs under `experiments/20260828_phase2_sentinel/`; never overwrite old results.
- If a policy degrades, roll back the policy commit, keep sentinel infra and evidence.
- If a case is tool/data-blocked, G5 is blocked for that case; old results are never substituted for fresh sentinel runs.

## 6. Commit conventions

- `feat(sentinel): ...`, `feat(search-policy): ...`, `test(...): ...`, `docs(phase2): ...`
- Governance docs (`docs/superpowers/`) committed with `git add -f` on the governance branch only.

## 7. Handoff package for the next agent

Each follow-up task package must include: task ID + phase, single objective, input commit and allowed paths, forbidden paths/actions, design/plan files to read first, tests to add/update, gate commands, deliverables and completion criteria, stop conditions, and handoff notes for the next agent.
