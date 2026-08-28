# FAECO Phase 0-1 Stabilization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make FAECO's unified loop auditable and reproducible by fixing repository/test gates (Phase 0) and by separating RunSpec, budgets, acceptance, and search policies behind tested interfaces (Phase 1), without changing any accepted algorithm behavior.

**Architecture:** Phase 0 freezes a `phase0_validated_head_sha` with clean test entry, no diff-check violations, reproducible smoke, and tool/SEC evidence. Phase 1 introduces small new modules (`runspec.py`, `budget.py`, `acceptance.py`, `search_policy.py`) plus fixtures, while `RealWnsEvaluator` and `run_multi_iteration_case` keep their current public signatures.

**Tech Stack:** Python 3.11, pytest, PowerShell scripts, Yosys/ABC/OpenSTA (native + WSL), git worktrees.

---

## 0. Fixed references and worktree layout

Read the spec first: `docs/superpowers/specs/2026-08-28-faeco-stabilization-modularization-design.md`.

Frozen references (recorded in the spec):

| Variable | Value |
|---|---|
| `phase0_integration_base_sha` | `b8c37590d7960715a0ec132f9b1c152973803675` (`origin/main`) |
| `phase0_base_sha` | `c58ad8ec5e8bc8d8a58e7a77cdce655b8c3e6879` |
| `phase0_review_base_sha` | `79b8f05cf0274efca2895a588ada82f6e1234140` |
| `phase0_audit_range` | `79b8f05..c58ad8e` |

Worktrees used by this plan:

- Governance worktree: `C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-unified-loop` (branch `codex/faeco-unified-loop`; contains only the design/plan documents; never merged into the Phase 0 implementation branch).
- Phase 0 implementation worktree: `C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-phase0-stabilization` (new branch `codex/faeco-phase0-stabilization` created from `phase0_base_sha`).
- Integration rehearsal worktree: `C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-integration-audit` (new branch `codex/faeco-integration-audit` created from `phase0_integration_base_sha`).

No task may modify the dirty main checkout at `D:\BaiduSyncdisk\03_FAECO`.

---

## 1. File structure

| File | Responsibility |
|---|---|
| `docs/phase0/baseline-audit.json` | Machine-readable refs, git state, asset inventory summary |
| `docs/phase0/asset_inventory.md` | Human-readable protected/mutable asset lists |
| `docs/phase0/delta_review_20260828.md` | P0.2 review findings and closure matrix |
| `pyproject.toml` | pytest `pythonpath` includes `scripts`; smoke config |
| `tests/test_scripts_importable.py` | Locks direct import of scripts as modules |
| `src/rseco/equivalence.py` | Fix trailing blank line at EOF |
| `tests/test_graph_equivalence.py` | Fix trailing blank line at EOF |
| `scripts/smoke_check.ps1` | Independent smoke command with 3x timing |
| `scripts/run_verification_gates.ps1` | One-command Phase 0 gate runner |
| `docs/phase0/verification-summary.json` | Fresh Phase 0 evidence output |
| `docs/phase0/integration_rehearsal.md` | P0.4 merge rehearsal record |
| `tests/README.md`, `README.md` | Standard test commands without manual PYTHONPATH |
| `src/rseco/runspec.py` | RunSpec schema, defaults, config hash |
| `src/rseco/budget.py` | Cost events, budget kinds, stop reasons |
| `src/rseco/acceptance.py` | Pure acceptance policy and deterministic ranking |
| `src/rseco/search_policy.py` | fast/balanced/exhaustive policies and coverage |
| `tests/test_runspec.py` | RunSpec tests |
| `tests/test_budget_semantics.py` | Budget separation tests |
| `tests/test_acceptance_policy.py` | Acceptance tests |
| `tests/test_search_policy.py` | Policy contract tests |
| `tests/test_b15_b17_fixtures.py` | Search-quality and soft-cost fixtures |

---

## Task 1 (P0.1): Baseline audit and implementation branch

**Files:**
- Create: `docs/phase0/baseline-audit.json`
- Create: `docs/phase0/asset_inventory.md`

- [ ] **Step 1.1: Create the Phase 0 implementation branch and worktree**

From the governance worktree, run:

```powershell
git -C C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-unified-loop worktree add -b codex/faeco-phase0-stabilization C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-phase0-stabilization c58ad8ec5e8bc8d8a58e7a77cdce655b8c3e6879
```

Expected: new worktree checked out at `c58ad8e`; `git -C ... status --short --branch` shows `## codex/faeco-phase0-stabilization` and a clean tree.

- [ ] **Step 1.2: Capture refs and git state**

In the Phase 0 worktree, run and record all values:

```powershell
git rev-parse HEAD
git rev-parse origin/main
git rev-parse 79b8f05cf0274efca2895a588ada82f6e1234140
git log --oneline --decorate -20
git status --short --branch
```

- [ ] **Step 1.3: Inventory the dirty main checkout (read-only)**

Run `git -C D:\BaiduSyncdisk\03_FAECO status --short --branch` and save the output verbatim into `docs/phase0/asset_inventory.md`. Classify each line as `code_modified`, `doc_modified`, `paper_deleted`, `paper_untracked`, `experiment_untracked`, or `scratch_tmp`; do not modify, restore, delete, or move any of them.

- [ ] **Step 1.4: Write `docs/phase0/baseline-audit.json`**

Use schema_version 1 with these exact top-level keys:

```json
{
  "schema_version": 1,
  "checked_at_utc": "<ISO-8601 UTC>",
  "phase0_integration_base_sha": "b8c37590d7960715a0ec132f9b1c152973803675",
  "phase0_base_sha": "c58ad8ec5e8bc8d8a58e7a77cdce655b8c3e6879",
  "phase0_review_base_sha": "79b8f05cf0274efca2895a588ada82f6e1234140",
  "phase0_validated_head_sha": null,
  "governance_head_sha": "<HEAD of codex/faeco-unified-loop>",
  "refs_match_spec": true,
  "dirty_main_inventory": "<path to asset_inventory.md>",
  "risks": []
}
```

If any ref does not match the spec table, set `refs_match_spec: false` and stop before committing; the plan must be updated by the design owner.

- [ ] **Step 1.5: Run the G1 local checks**

```powershell
git -C C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-phase0-stabilization diff --check
git -C C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-phase0-stabilization status --porcelain=v1
```

Expected: `diff --check` exits 0 with no output; porcelain output is empty.

- [ ] **Step 1.6: Commit**

```powershell
git add docs/phase0/baseline-audit.json docs/phase0/asset_inventory.md
git commit -m "docs(phase0): record baseline audit and asset inventory"
```

**Gate:** G1. Deliverable: `baseline-audit.json` with `refs_match_spec: true`.

---

## Task 2 (P0.2): Delta review of the 16 implementation commits

**Files:**
- Create: `docs/phase0/delta_review_20260828.md`

- [ ] **Step 2.1: Enumerate the range**

```powershell
git log --oneline --decorate 79b8f05cf0274efca2895a588ada82f6e1234140..c58ad8ec5e8bc8d8a58e7a77cdce655b8c3e6879
git diff --stat 79b8f05cf0274efca2895a588ada82f6e1234140..c58ad8ec5e8bc8d8a58e7a77cdce655b8c3e6879
```

Expected: 16 commits; changed files match the known set (src/rseco/cut.py, equivalence.py, failures.py, flow.py, logic_rewrite.py, netlist.py, real_wns.py, refinement.py, refinement_loop.py, replacement.py, yosys_abc.py, scripts, tests).

- [ ] **Step 2.2: Review each commit for correctness and gate integrity**

For each commit, inspect the diff with `git show --stat <sha>` and `git show <sha> -- <changed files>`. Record findings in the review doc. Use the Sol final review categories:

| ID | Category | Critical if... |
|---|---|---|
| C1 | Cross-cell boolean pin roles | equivalence could pass while input roles are swapped |
| C2 | Sequential async clear/preset SEC | wrong D-path/reset modeling could pass a changed D path |
| I1 | Stateful timing early-stop | timing-met state could be lost or misreported |
| I2 | Stop reason / final patch | incomplete state could be reported as success |
| I3 | Physical hold ranking | hold mode could accept a worse hold candidate |
| I4 | Baseline/cache semantics | parallel candidates could share wrong baseline |

Also check the 2026-08-24 residual tests (`tests/test_sol_review_residuals.py`) still match the current behavior in the new branch.

- [ ] **Step 2.3: Write `delta_review_20260828.md`**

Required sections:

1. Review basis (commits, range, baseline).
2. Per-commit or per-area findings.
3. Closure matrix with columns: ID, Finding, Evidence, Verdict (`closed` / `needs_behavior_change`), Notes.
4. New findings introduced after `79b8f05`, especially the 2026-08-26 b15/b17 analysis interactions.
5. Conclusion: `APPROVED` only if no Critical/Important remains open and no finding requires behavior change. If any finding requires behavior change, conclusion is `BLOCKED` and the finding is escalated to a new P0.x correctness task; do not modify behavior inside this task.

- [ ] **Step 2.4: Commit**

```powershell
git add docs/phase0/delta_review_20260828.md
git commit -m "docs(phase0): delta review of implementation commits"
```

**Gate:** G1. Deliverable: review doc with zero open Critical/Important findings or an explicit `BLOCKED` escalation list.

---

## Task 3 (P0.3): Test entry, smoke, and verification gates

**Files:**
- Create: `tests/test_scripts_importable.py`
- Modify: `pyproject.toml`
- Modify: `src/rseco/equivalence.py` (EOF blank line)
- Modify: `tests/test_graph_equivalence.py` (EOF blank line)
- Create: `scripts/smoke_check.ps1`
- Create: `scripts/run_verification_gates.ps1`
- Modify: `tests/README.md`
- Modify: `README.md`

- [ ] **Step 3.1: Write the failing import test**

Create `tests/test_scripts_importable.py`:

```python
"""Scripts must be importable without manual PYTHONPATH setup."""

from __future__ import annotations


def test_scripts_modules_importable() -> None:
    from run_sequential_timing_check import run_opensta, run_yosys_mapping
    from run_outerloop_real_wns import main

    assert callable(run_opensta)
    assert callable(run_yosys_mapping)
    assert callable(main)
```

- [ ] **Step 3.2: Run it and confirm it fails at collection**

```powershell
python -m pytest -q -p no:cacheprovider tests/test_scripts_importable.py
```

Expected: ERROR during collection with `ModuleNotFoundError: No module named 'run_sequential_timing_check'`.

- [ ] **Step 3.3: Fix pytest pythonpath**

Change `pyproject.toml`:

```toml
[tool.pytest.ini_options]
pythonpath = ["src", "scripts"]
testpaths = ["tests"]
```

- [ ] **Step 3.4: Run the import test and full suite**

```powershell
python -m pytest -q -p no:cacheprovider tests/test_scripts_importable.py
python -m pytest -q -p no:cacheprovider
```

Expected: import test passes; full suite passes with no collection errors. Baseline expectation: `366 passed, 4 skipped, 1 subtests passed`.

- [ ] **Step 3.5: Fix EOF blank lines**

Remove the extra blank line at end of `src/rseco/equivalence.py` and `tests/test_graph_equivalence.py`, then verify:

```powershell
git diff --check
```

Expected: no output and exit 0.

- [ ] **Step 3.6: Create the smoke command**

Create `scripts/smoke_check.ps1`:

```powershell
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).ProviderPath
$smokeTests = @(
    "tests/test_strategy_selector.py",
    "tests/test_ranking.py",
    "tests/test_proxy_ranking.py",
    "tests/test_metrics_and_failures.py",
    "tests/test_cut_patch.py",
    "tests/test_scripts_importable.py"
)
$runs = @()
foreach ($i in 1..3) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    & python -m pytest -q -p no:cacheprovider @smokeTests
    if ($LASTEXITCODE -ne 0) { throw "smoke run $i failed" }
    $sw.Stop()
    $runs += [pscustomobject]@{ run = $i; seconds = [math]::Round($sw.Elapsed.TotalSeconds, 2) }
}
foreach ($r in $runs) {
    if ($r.seconds -gt 60) { throw "smoke run $($r.run) took $($r.seconds)s > 60s" }
}
$result = [pscustomobject]@{
    schema_version = 1
    command = "python -m pytest -q -p no:cacheprovider tests/test_strategy_selector.py tests/test_ranking.py tests/test_proxy_ranking.py tests/test_metrics_and_failures.py tests/test_cut_patch.py tests/test_scripts_importable.py"
    max_seconds = 60
    runs = $runs
    passed = $true
}
$outDir = Join-Path $repoRoot "docs\phase0"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$outPath = Join-Path $outDir "smoke_timings.json"
$result | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $outPath -Encoding utf8
Write-Output "smoke passed in $($runs.seconds -join ', ')s"
```

- [ ] **Step 3.7: Create the verification gate runner**

Create `scripts/run_verification_gates.ps1`:

```powershell
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).ProviderPath
$phase0Dir = Join-Path $repoRoot "docs\phase0"
New-Item -ItemType Directory -Force -Path $phase0Dir | Out-Null

function Invoke-Step {
    param([string]$Name, [scriptblock]$Body)
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        & $Body
        if ($LASTEXITCODE -ne 0) { throw "step '$Name' exited with $LASTEXITCODE" }
        $sw.Stop()
        return [pscustomobject]@{ name = $Name; ok = $true; seconds = [math]::Round($sw.Elapsed.TotalSeconds, 2); detail = "ok" }
    } catch {
        $sw.Stop()
        return [pscustomobject]@{ name = $Name; ok = $false; seconds = [math]::Round($sw.Elapsed.TotalSeconds, 2); detail = $_.Exception.Message }
    }
}

$steps = @()
$steps += Invoke-Step "git_diff_check" { git diff --check }
$steps += Invoke-Step "toolchain_snapshot" { & (Join-Path $repoRoot "scripts\check_toolchain.ps1") -OutputPath (Join-Path $phase0Dir "toolchain_snapshot.json") | Out-Null }
$steps += Invoke-Step "full_pytest" { python -m pytest -q -p no:cacheprovider }
$steps += Invoke-Step "smoke_3x" { & (Join-Path $repoRoot "scripts\smoke_check.ps1") | Out-Null }
$steps += Invoke-Step "real_sec_smoke" { python -m pytest -q -p no:cacheprovider tests/test_sol_review_residuals.py::test_real_wsl_sec_models_async_clear_polarity_and_connection }
$steps += Invoke-Step "yosys_map_encoding" { python -m pytest -q -p no:cacheprovider tests/test_yosys_map_script_encoding.py }

$allOk = ($steps | Where-Object { -not $_.ok }).Count -eq 0
$summary = [pscustomobject]@{
    schema_version = 1
    checked_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    head_sha = (git rev-parse HEAD)
    worktree = $repoRoot
    all_gates_passed = $allOk
    steps = $steps
}
$summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $phase0Dir "verification-summary.json") -Encoding utf8
if (-not $allOk) { throw "verification gates failed; see docs/phase0/verification-summary.json" }
Write-Output "verification gates passed"
```

- [ ] **Step 3.8: Run the gate runner and iterate**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_verification_gates.ps1
```

Expected: exit 0, `verification-summary.json` has `all_gates_passed: true`, and every real SEC test ran (not skipped). If WSL is unavailable on the machine, record it as a blocked G3 and stop; do not rewrite skip reasons.

- [ ] **Step 3.9: Update test documentation**

In `tests/README.md` and the README verification section, replace the manual `$env:PYTHONPATH='src'` instructions with:

```powershell
python -m pytest -q -p no:cacheprovider        # full regression
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/smoke_check.ps1
```

- [ ] **Step 3.10: Commit**

```powershell
git add pyproject.toml src/rseco/equivalence.py tests/test_graph_equivalence.py tests/test_scripts_importable.py scripts/smoke_check.ps1 scripts/run_verification_gates.ps1 tests/README.md README.md docs/phase0/verification-summary.json docs/phase0/smoke_timings.json docs/phase0/toolchain_snapshot.json
git commit -m "test(phase0): freeze test entry and verification gates"
```

**Gate:** G2 + G3. Deliverable: `docs/phase0/verification-summary.json` with `all_gates_passed: true`; the resulting commit becomes `phase0_validated_head_sha` (or an additional P0.x correctness commit is created first if Task 2 blocked).

---

## Task 4 (P0.4): Integration rehearsal

**Files:**
- Create: `docs/phase0/integration_rehearsal.md` (committed on the governance branch)

- [ ] **Step 4.1: Create the integration rehearsal branch and worktree**

```powershell
git -C C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-unified-loop worktree add -b codex/faeco-integration-audit C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-integration-audit b8c37590d7960715a0ec132f9b1c152973803675
```

- [ ] **Step 4.2: Merge only the validated head**

```powershell
git -C C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-integration-audit merge --no-ff <phase0_validated_head_sha> -m "chore(phase0): rehearsal merge of validated head"
```

Expected: merge completes without conflict, or conflict resolution is recorded without pushing. Never merge `governance_head_sha`.

- [ ] **Step 4.3: Verify the merged tree**

```powershell
git -C C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-integration-audit diff --check
python -m pytest -q -p no:cacheprovider
```

Expected: both pass.

- [ ] **Step 4.4: Write `integration_rehearsal.md` on the governance branch**

Record the base SHA, merged SHA, resulting merge SHA, conflict notes, test result, and the statement `not pushed`.

- [ ] **Step 4.5: Commit the rehearsal doc**

```powershell
git -C C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-unified-loop add docs/phase0/integration_rehearsal.md
git -C C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-unified-loop commit -m "docs(phase0): record integration rehearsal"
```

**Gate:** G1-G3. Deliverable: rehearsal doc with exact merge SHA and `not pushed` confirmation.

## Task 5 (P1.1): RunSpec schema and config hash

**Files:**
- Create: `src/rseco/runspec.py`
- Create: `tests/test_runspec.py`

- [ ] **Step 5.1: Write failing tests**

Create `tests/test_runspec.py`:

```python
"""RunSpec schema, default expansion, and stable config hash tests."""

from __future__ import annotations

import json

from rseco.runspec import RunSpec, config_hash


def test_defaults_are_expanded_and_stable() -> None:
    spec = RunSpec.defaults()
    assert spec.schema_version == 1
    assert spec.search_policy == "balanced"
    first = config_hash(spec)
    second = config_hash(spec)
    assert first == second
    assert len(first) == 64


def test_cli_override_lands_in_resolved_snapshot() -> None:
    spec = RunSpec.defaults().with_overrides({"search_policy": "fast"})
    assert spec.search_policy == "fast"
    snapshot = spec.resolved_snapshot()
    assert "fast" in snapshot


def test_snapshot_is_canonical_json() -> None:
    spec = RunSpec.defaults()
    data = json.loads(spec.resolved_snapshot())
    assert data["schema_version"] == 1
    assert "run_id" in data
```

- [ ] **Step 5.2: Run tests; confirm failure**

```powershell
python -m pytest -q -p no:cacheprovider tests/test_runspec.py
```

Expected: import error `No module named 'rseco.runspec'`.

- [ ] **Step 5.3: Implement `src/rseco/runspec.py`**

```python
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
    return hashlib.sha256(spec.resolved_snapshot().encode("utf-8")).hexdigest()
```

- [ ] **Step 5.4: Run tests; confirm pass**

```powershell
python -m pytest -q -p no:cacheprovider tests/test_runspec.py
```

- [ ] **Step 5.5: Run full suite and commit**

```powershell
python -m pytest -q -p no:cacheprovider
git add src/rseco/runspec.py tests/test_runspec.py
git commit -m "feat(runspec): add serializable run configuration and hash"
```

**Gate:** G4 (RunSpec part).

---

## Task 6 (P1.2): Budget semantics separation

**Files:**
- Create: `src/rseco/budget.py`
- Create: `tests/test_budget_semantics.py`

- [ ] **Step 6.1: Write failing tests**

Create `tests/test_budget_semantics.py`:

```python
"""Soft cost events must not invalidate completed candidates."""

from __future__ import annotations

from rseco.budget import (
    BudgetKind,
    BudgetState,
    CostEvent,
    stop_reason_for,
)


def test_soft_cost_does_not_change_stop_reason() -> None:
    state = BudgetState(campaign_wall_timeout_s=60.0)
    state.record(CostEvent(BudgetKind.SOFT_COST_OVER_LIMIT, "b17-like", measured_s=113.0))
    assert stop_reason_for(state) is None


def test_hard_candidate_timeout_has_own_stop_reason() -> None:
    state = BudgetState(candidate_timeout_s=60.0)
    state.record(CostEvent(BudgetKind.CANDIDATE_HARD_TIMEOUT, "timed out", measured_s=60.0))
    assert stop_reason_for(state) == "candidate_hard_timeout"


def test_budgets_have_distinct_reasons() -> None:
    assert stop_reason_for(BudgetState(campaign_wall_timeout_s=1.0)) == "campaign_wall_exhausted"
    assert stop_reason_for(BudgetState(sta_budget=0)) == "sta_budget_exhausted"
    assert stop_reason_for(BudgetState(formal_budget=0)) == "formal_budget_exhausted"
```

- [ ] **Step 6.2: Run tests; confirm failure**

```powershell
python -m pytest -q -p no:cacheprovider tests/test_budget_semantics.py
```

- [ ] **Step 6.3: Implement `src/rseco/budget.py`**

```python
"""Budget kinds, cost events, and distinct stop reasons."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BudgetKind(str, Enum):
    SOFT_COST_OVER_LIMIT = "soft_cost_over_limit"
    CANDIDATE_HARD_TIMEOUT = "candidate_hard_timeout"
    CAMPAIGN_WALL = "campaign_wall"
    STA_COUNT = "sta_count"
    FORMAL_COUNT = "formal_count"


@dataclass(frozen=True)
class CostEvent:
    kind: BudgetKind
    message: str
    measured_s: float


@dataclass
class BudgetState:
    candidate_timeout_s: float = 300.0
    campaign_wall_timeout_s: float = 0.0
    sta_budget: int = 2000
    formal_budget: int = 200
    events: list[CostEvent] = None

    def __post_init__(self) -> None:
        if self.events is None:
            self.events = []

    def record(self, event: CostEvent) -> None:
        self.events.append(event)


def stop_reason_for(state: BudgetState) -> str | None:
    if any(e.kind == BudgetKind.CANDIDATE_HARD_TIMEOUT for e in state.events):
        return "candidate_hard_timeout"
    if state.campaign_wall_timeout_s > 0 and any(
        e.kind == BudgetKind.CAMPAIGN_WALL for e in state.events
    ):
        return "campaign_wall_exhausted"
    if state.sta_budget <= 0:
        return "sta_budget_exhausted"
    if state.formal_budget <= 0:
        return "formal_budget_exhausted"
    return None
```

- [ ] **Step 6.4: Run tests; confirm pass**

```powershell
python -m pytest -q -p no:cacheprovider tests/test_budget_semantics.py
```

- [ ] **Step 6.5: Full suite and commit**

```powershell
python -m pytest -q -p no:cacheprovider
git add src/rseco/budget.py tests/test_budget_semantics.py
git commit -m "feat(budget): separate soft cost from hard budget stop reasons"
```

**Gate:** G4 (budget part).

---

## Task 7 (P1.3): Pure AcceptancePolicy interface

**Files:**
- Create: `src/rseco/acceptance.py`
- Create: `tests/test_acceptance_policy.py`

- [ ] **Step 7.1: Write failing tests**

Create `tests/test_acceptance_policy.py`:

```python
"""Acceptance policy must be pure logic over measured metrics."""

from __future__ import annotations

from rseco.acceptance import CandidateMetrics, DefaultAcceptancePolicy, rank_candidates
from rseco.runspec import RunSpec


def _metrics(**kw) -> CandidateMetrics:
    base = dict(
        candidate_hash="c1",
        setup_wns=-1.0,
        setup_tns=-5.0,
        patch_ratio=0.001,
        required_ok=True,
    )
    base.update(kw)
    return CandidateMetrics(**base)


def test_fail_closed_when_required_metric_missing() -> None:
    policy = DefaultAcceptancePolicy(RunSpec.defaults())
    verdict = policy.evaluate(_metrics(required_ok=False))
    assert not verdict.accepted
    assert "required_metrics" in verdict.reasons


def test_accepts_strict_improvement_over_epsilon() -> None:
    policy = DefaultAcceptancePolicy(RunSpec.defaults())
    verdict = policy.evaluate(_metrics(setup_wns=-0.5, setup_tns=-2.0))
    assert verdict.accepted


def test_rejects_insufficient_gain() -> None:
    policy = DefaultAcceptancePolicy(RunSpec.defaults())
    verdict = policy.evaluate(_metrics(setup_wns=-1.0005, setup_tns=-5.0))
    assert not verdict.accepted


def test_ranking_is_deterministic_and_mode_aware() -> None:
    ranked = rank_candidates(
        [
            _metrics(candidate_hash="b", setup_wns=-0.9),
            _metrics(candidate_hash="a", setup_wns=-0.8),
        ],
        mode="setup",
    )
    assert [m.candidate_hash for m in ranked] == ["a", "b"]
```

- [ ] **Step 7.2: Run tests; confirm failure**

```powershell
python -m pytest -q -p no:cacheprovider tests/test_acceptance_policy.py
```

- [ ] **Step 7.3: Implement `src/rseco/acceptance.py`**

```python
"""Pure acceptance policy and deterministic candidate ranking."""

from __future__ import annotations

from dataclasses import dataclass

from rseco.runspec import RunSpec


@dataclass(frozen=True)
class CandidateMetrics:
    candidate_hash: str
    setup_wns: float
    setup_tns: float
    patch_ratio: float
    required_ok: bool
    hold_min_slack: float | None = None
    physical_primary: float | None = None
    physical_secondary: float | None = None


@dataclass(frozen=True)
class AcceptanceVerdict:
    accepted: bool
    reasons: tuple[str, ...] = ()


class DefaultAcceptancePolicy:
    def __init__(self, spec: RunSpec) -> None:
        self.spec = spec

    def evaluate(self, m: CandidateMetrics) -> AcceptanceVerdict:
        reasons: list[str] = []
        if not m.required_ok:
            reasons.append("required_metrics")
        gain = m.setup_wns - (-1.0)
        if gain <= self.spec.min_gain_ns:
            reasons.append("insufficient_gain")
        if m.patch_ratio > self.spec.max_patch_ratio:
            reasons.append("patch_ratio_exceeded")
        return AcceptanceVerdict(accepted=not reasons, reasons=tuple(reasons))


def rank_candidates(candidates: list[CandidateMetrics], mode: str) -> list[CandidateMetrics]:
    def key(m: CandidateMetrics) -> tuple:
        if mode == "hold":
            hold = m.hold_min_slack if m.hold_min_slack is not None else float("-inf")
            return (-hold, -m.setup_wns, m.patch_ratio, m.candidate_hash)
        return (-m.setup_wns, -m.setup_tns, m.patch_ratio, m.candidate_hash)

    return sorted(candidates, key=key)
```

- [ ] **Step 7.4: Run tests; confirm pass**

```powershell
python -m pytest -q -p no:cacheprovider tests/test_acceptance_policy.py
```

- [ ] **Step 7.5: Full suite and commit**

```powershell
python -m pytest -q -p no:cacheprovider
git add src/rseco/acceptance.py tests/test_acceptance_policy.py
git commit -m "feat(acceptance): extract pure acceptance policy and ranking"
```

**Gate:** G4 (acceptance part).

---

## Task 8 (P1.4): Search policies and CLI compatibility

**Files:**
- Create: `src/rseco/search_policy.py`
- Create: `tests/test_search_policy.py`
- Modify: `scripts/run_outerloop_real_wns.py` (compatibility mapping only)

- [ ] **Step 8.1: Write failing tests**

Create `tests/test_search_policy.py`:

```python
"""fast/balanced/exhaustive must have explicit, testable semantics."""

from __future__ import annotations

from rseco.runspec import RunSpec
from rseco.search_policy import SearchPolicy, SearchPolicyConfig, map_legacy_early_stop


def test_balanced_requires_coverage() -> None:
    config = SearchPolicyConfig.from_run_spec(RunSpec.defaults())
    assert config.policy == SearchPolicy.BALANCED
    assert config.min_validated_per_family == 3
    assert config.joint_quota == 2


def test_legacy_early_stop_maps_to_fast() -> None:
    warnings: list[str] = []

    def warn(msg: str) -> None:
        warnings.append(msg)

    policy = map_legacy_early_stop(True, warn=warn)
    assert policy == SearchPolicy.FAST
    assert warnings and "deprecated" in warnings[0]


def test_exhaustive_can_report_partial() -> None:
    from rseco.search_policy import CoverageState

    state = CoverageState(total_generated=10, validated=6)
    assert state.partial
    assert state.is_exhaustive_result is False
```

- [ ] **Step 8.2: Run tests; confirm failure**

```powershell
python -m pytest -q -p no:cacheprovider tests/test_search_policy.py
```

- [ ] **Step 8.3: Implement `src/rseco/search_policy.py`**

```python
"""Search policy semantics and legacy early-stop mapping."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from rseco.runspec import RunSpec


class SearchPolicy(str, Enum):
    FAST = "fast"
    BALANCED = "balanced"
    EXHAUSTIVE = "exhaustive"


@dataclass(frozen=True)
class SearchPolicyConfig:
    policy: SearchPolicy
    min_validated_per_family: int
    joint_quota: int

    @classmethod
    def from_run_spec(cls, spec: RunSpec) -> "SearchPolicyConfig":
        return cls(
            policy=SearchPolicy(spec.search_policy),
            min_validated_per_family=spec.balanced_min_validated_per_family,
            joint_quota=spec.balanced_joint_quota,
        )


@dataclass(frozen=True)
class CoverageState:
    total_generated: int
    validated: int

    @property
    def partial(self) -> bool:
        return self.validated < self.total_generated

    @property
    def is_exhaustive_result(self) -> bool:
        return not self.partial


def map_legacy_early_stop(value: bool, warn) -> SearchPolicy:
    if value:
        warn("--early-stop is deprecated; use --search-policy fast")
        return SearchPolicy.FAST
    return SearchPolicy.BALANCED
```

- [ ] **Step 8.4: Run tests; confirm pass**

```powershell
python -m pytest -q -p no:cacheprovider tests/test_search_policy.py
```

- [ ] **Step 8.5: Add CLI compatibility mapping**

In `scripts/run_outerloop_real_wns.py`, keep `--early-stop` accepted but emit a deprecation warning and translate to the policy module. Do not change the default behavior of the CLI beyond the warning.

- [ ] **Step 8.6: Full suite and commit**

```powershell
python -m pytest -q -p no:cacheprovider
git add src/rseco/search_policy.py tests/test_search_policy.py scripts/run_outerloop_real_wns.py
git commit -m "feat(search-policy): explicit fast/balanced/exhaustive and legacy mapping"
```

**Gate:** G4 (policy part).

---

## Task 9 (P1.5): b15/b17 contract fixtures

**Files:**
- Create: `tests/test_b15_b17_fixtures.py`

- [ ] **Step 9.1: Write fixture tests**

Create `tests/test_b15_b17_fixtures.py`:

```python
"""b15 and b17 quality-cost contracts without running full benchmarks."""

from __future__ import annotations

from rseco.acceptance import CandidateMetrics, DefaultAcceptancePolicy
from rseco.budget import BudgetKind, BudgetState, CostEvent
from rseco.runspec import RunSpec
from rseco.search_policy import CoverageState


def test_b15_quality_cost_tradeoff_is_structural() -> None:
    fast_stops_early = CoverageState(total_generated=12, validated=1)
    exhaustive = CoverageState(total_generated=12, validated=12)
    assert fast_stops_early.partial
    assert exhaustive.is_exhaustive_result
    assert exhaustive.validated > fast_stops_early.validated


def test_b17_soft_cost_does_not_invalidate_accepted_candidate() -> None:
    state = BudgetState(candidate_timeout_s=180.0)
    state.record(CostEvent(BudgetKind.SOFT_COST_OVER_LIMIT, "STA 113s > 60s soft cap", 113.0))
    policy = DefaultAcceptancePolicy(RunSpec.defaults())
    verdict = policy.evaluate(
        CandidateMetrics(
            candidate_hash="b17_iter1_joint",
            setup_wns=-16.10,
            setup_tns=-1.0,
            patch_ratio=0.001,
            required_ok=True,
        )
    )
    assert verdict.accepted
```

- [ ] **Step 9.2: Run tests; confirm pass**

```powershell
python -m pytest -q -p no:cacheprovider tests/test_b15_b17_fixtures.py
```

- [ ] **Step 9.3: Commit**

```powershell
git add tests/test_b15_b17_fixtures.py
git commit -m "test(fixtures): lock b15 quality-cost and b17 soft-cost contracts"
```

**Gate:** G4. Phase 1 exit gate: all four policy/budget/acceptance/runspec test files pass, full suite passes, and no behavior change to accepted benchmark results.

---

## 2. Phase gates and stop conditions

- If any Task 1-4 step fails, stop and diagnose; never edit the dirty main checkout.
- If Task 2 produces `needs_behavior_change`, create a separate P0.x correctness task before Task 3 and update `phase0_validated_head_sha`.
- If WSL SEC cannot run in Task 3, stop with G3 blocked; do not mark the phase complete.
- Phase 0 complete: Tasks 1-4 done, `verification-summary.json` all green, integration rehearsal recorded.
- Phase 1 complete: Tasks 5-9 done, all new tests green, full suite green, CLI behavior unchanged except deprecation warning.

## 3. Required verification commands

```powershell
python -m pytest -q -p no:cacheprovider
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_verification_gates.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/smoke_check.ps1
git diff --check
```

## 4. Commit conventions

- Phase 0 commits: `docs(phase0): ...`, `test(phase0): ...`, `chore(phase0): ...`
- Phase 1 commits: `feat(runspec): ...`, `feat(budget): ...`, `feat(acceptance): ...`, `feat(search-policy): ...`, `test(fixtures): ...`
- One commit per task; no combined cleanup commits.
