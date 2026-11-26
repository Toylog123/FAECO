#!/usr/bin/env python3
"""V5 Stage 3 (resumable, pinned CPU 0-5):
Independent Online Multi-Budget Setup Sweep (B_W / P_clk in {0.0%, 0.5%, 1.0%, 2.0%})
under identical 1.0*H_row boxed DRC backend, 18-action pool, and 720 s wall-clock budget
on BOTH asap7/uart (Setup-sensitive small block) and sky130hd/aes (wall-clock/Hold-dominated 10k-gate block).
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from dataclasses import asdict
from pathlib import Path
from tempfile import mkdtemp

REPO = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
EVID = REPO / "project_docs/evidence"
for sub in (
    "tcad_ibex_20261123",
    "tcad_holdout_20261123",
    "tcad_wallclock_schedule_20261125",
    "tcad_asap7_aes_holdout_20261125",
    "tcad_boxed_drc_20261126",
    "tcad_external_baselines_20261125",
):
    p = str(EVID / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

import compare_ibex as cmp
import incident_cap_priority
import run_lr_4designs as lr_mod
import run_qualified_wallclock as qualified
import run_setup_budget_sweep as sweep
from run_aes_incident_priority_matched_v2 import WallWindowEnded, process_ledger
from run_screened_matrix import RELATIVE_HOLD_REASONS, bind_runtime, raw_seconds

OUT_ROOT = Path("/home/toylog/faeco_v5_step3_multibudget_20261126_v1")
OUT_JSON = EVID / "tcad_v5_revision_20261126/V5_STEP3_MULTIBUDGET_VERIFIED.json"
LIMIT_S = 720.0
SETUP_REASONS = {f"{view}:{reason}" for view in cmp.CORNERS
                 for reason in ("setup_budget", "setup_tns_budget", "setup_floor")}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_auc(cps: list[dict], limit_s: float = 720.0) -> float:
    best = 0.0
    pts = [(0.0, 0.0)]
    for c in sorted(cps, key=lambda x: x["elapsed_s"]):
        if c["elapsed_s"] <= limit_s and c["accepted"] and c["area_saved_um2"] > best:
            best = float(c["area_saved_um2"])
            pts.append((float(c["elapsed_s"]), best))
    pts.append((limit_s, best))
    return sum(max(0.0, t1 - t0) * v0 for (t0, v0), (t1, _) in zip(pts, pts[1:])) / limit_s


def apply_search_budget(runner, clk_ps: float, pct: float) -> None:
    frozen_clock = runner.eval.args.clock_period_ps
    if not math.isclose(frozen_clock, clk_ps, rel_tol=0, abs_tol=1e-6):
        raise ValueError(f"frozen clock {frozen_clock} ps differs from the registered {clk_ps} ps")
    runner.gate = sweep.budget_gate(runner.eval, pct, protect_clean=runner.gate.protect_clean)
    runner.policy = cmp.BudgetPolicy.from_ps(runner.gate.wns_ps, tolerance_ns=cmp.PS_TOLERANCE / 1000)


def run_one_budget(kind: str, clk_ps: float, pct: float) -> dict:
    tag = f"{kind}__pct_{pct:.1f}".replace(".", "p")
    attempts = OUT_ROOT / tag
    attempts.mkdir(parents=True, exist_ok=True)
    rdir = Path(mkdtemp(prefix="attempt_", dir=attempts)) / "runner"
    runner, _, _, _, _ = lr_mod.make_boxed_runner(kind, rdir)
    if not hasattr(runner, "initial_hint"):
        runner.initial_hint = set()

    ref_area = runner.eval.ref_area
    pool = list(runner.pool)
    pool_ceiling = sum(a.estimated_area_saving for a in pool)
    screen_s = runner.screen
    if len(pool) != 18 or not 0 < screen_s < LIMIT_S or pool_ceiling <= 0:
        raise ValueError("the frozen pool or charged screening cost differs from the registered sweep")

    with (
        bind_runtime(runner.top, runner.flow["fastroute.tcl"]),
        qualified.qualified_ranking(),
        qualified.qualified_process_clock(),
    ):
        if kind == "sky130hd_aes":
            pf_res = Path("/home/toylog/faeco_v4_hybrid_faeco_20261126_v1/sky_shared_preflight/preflight/result.json")
            reference = runner.prepare_online(pf_res.resolve(strict=True))
        else:
            runner.use_preview = False
            reference = runner.qualify_zero()
            runner.use_preview = True
            pf_res = rdir / "preflight/zero/result.json"

        # Transfer the frozen no-edit qualification under its original gate first.
        apply_search_budget(runner, clk_ps, pct)
        gate = sweep.gate_summary(runner.gate, runner.eval.ref_views)
        protocol_path = rdir / "stage3_protocol.json"
        cmp.save(protocol_path, {
            "clock_period_ps": clk_ps, "setup_budget_pct": pct, "gate": gate,
            "control": {name: cmp.bind(path) for name, path in runner.eval.control.items()},
            "preflight": cmp.bind(pf_res), "base_views": runner.eval.ref_views,
            "ordered_pool": [asdict(action) for action in pool],
            "driver": cmp.bind(Path(__file__)), "wall_window_seconds": LIMIT_S,
            "boxed_backend": cmp.bind(Path(lr_mod.boxed_drc.__file__)),
            "charged_screening_seconds": screen_s, "route_threads": runner.eval.args.threads,
        })
        (rdir / "trials").mkdir()

        begun = raw_seconds()
        deadline = begun + (LIMIT_S - screen_s)
        reqs = []
        cps = []
        best_ep = reference
        best_saved = 0.0
        best_gates = 0
        known_rej: set[tuple[str, ...]] = set()
        dedup_hits = 0
        setup_rejs = 0
        hold_rejs = 0

        def eval_fn(actions):
            nonlocal best_ep, best_saved, best_gates, setup_rejs, hold_rejs
            now = raw_seconds()
            if now >= deadline:
                raise WallWindowEnded()
            seq = len(reqs) + 1
            reqs.append({"id": seq, "actions": list(actions)})
            trial_dir = rdir / "trials" / f"{seq:02d}"
            ep, rec = runner.attempt(actions, trial_dir)
            fin = raw_seconds()
            if fin >= deadline:
                raise WallWindowEnded()
            acc = (not rec["failures"] and cmp.assess(reference, ep, runner.policy).feasible
                   and ep.area < best_ep.area - 1e-9 and ep.sec_pass)
            fails = set(rec["failures"])
            reqs[-1].update(failures=sorted(fails), accepted=acc)
            if not acc:
                if fails & SETUP_REASONS:
                    setup_rejs += 1
                if fails & RELATIVE_HOLD_REASONS:
                    hold_rejs += 1
                if fails and fails.issubset(SETUP_REASONS):
                    known_rej.add(tuple(sorted(actions)))
            else:
                best_ep = ep
                best_saved = ref_area - ep.area
                best_gates = len(actions)
            cps.append({"id": seq, "elapsed_s": screen_s + (fin - begun), "accepted": acc,
                        "area_saved_um2": (ref_area - ep.area) if acc else 0.0,
                        "failures": sorted(fails), "result": cmp.bind(trial_dir / "result.json")})
            return ep

        def defer_fn(actions):
            return bool(RELATIVE_HOLD_REASONS.intersection(reqs[-1].get("failures", [])))

        def known_fn(trial):
            nonlocal dedup_hits
            if tuple(sorted(trial)) in known_rej:
                dedup_hits += 1
                return True
            return False

        window_ended = False
        ledger_path = rdir / "subprocesses.json"
        with process_ledger(ledger_path, deadline):
            try:
                rcap = incident_cap_priority.build_incident_priority(runner.eval.control["def"], runner.eval.control["spef"], pool)
                prios = {k: row["priority"] for k, row in rcap["actions"].items()}
                cmp.adaptive_batch_recovery(
                    reference, pool, eval_fn, runner.policy,
                    max_evaluations=None, batch_size=3,
                    defer_split_for=defer_fn,
                    priority_after_defer=prios,
                    known_split_rejection=known_fn,
                )
            except WallWindowEnded:
                window_ended = True

        auc = compute_auc(cps, LIMIT_S)
        return {
            "design": kind,
            "clock_period_ps": clk_ps,
            "setup_budget_pct": pct,
            "setup_budget_ps": runner.gate.wns_ps,
            "gate": gate,
            "protocol": cmp.bind(protocol_path),
            "raw_directory": str(rdir),
            "subprocess_ledger": cmp.bind(ledger_path) if ledger_path.is_file() else None,
            "window_ended": window_ended,
            "qualified_endpoint": asdict(best_ep),
            "qualified_area_saved_um2": best_saved,
            "qualified_gates": best_gates,
            "area_saved_pct": 100.0 * best_saved / ref_area,
            "pool_capture_pct": 100.0 * best_saved / pool_ceiling,
            "anytime_auc_um2": auc,
            "logical_finished": len(cps),
            "logical_started": len(reqs),
            "setup_rejections": setup_rejs,
            "hold_rejections": hold_rejs,
            "dedup_hits": dedup_hits,
            "checkpoints": cps,
        }


def main() -> int:
    force = "--force" in sys.argv
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(OUT_JSON.read_text()) if OUT_JSON.is_file() else {"runs": {}}

    matrix = [
        ("asap7_uart", 270.0, 0.0),
        ("asap7_uart", 270.0, 0.5),
        ("asap7_uart", 270.0, 1.0),
        ("asap7_uart", 270.0, 2.0),
        ("sky130hd_aes", 3600.0, 0.0),
        ("sky130hd_aes", 3600.0, 0.5),
        ("sky130hd_aes", 3600.0, 1.0),
        ("sky130hd_aes", 3600.0, 2.0),
    ]
    for kind, clk_ps, pct in matrix:
        key = f"{kind}::{pct:.1f}pct"
        if key in data["runs"] and not force:
            print(f"[Stage 3] Skipping existing {key}", flush=True)
            continue
        print(f"\n=== [Stage 3] Running online FAECO {key} (B_W={clk_ps*pct/100:.2f} ps) ===", flush=True)
        row = run_one_budget(kind, clk_ps, pct)
        data["runs"][key] = row
        cmp.save(OUT_JSON, data)
        print(f"  DONE {key}: saved={row['qualified_area_saved_um2']:.6f} um2 ({row['qualified_gates']}/18), "
              f"AUC={row['anytime_auc_um2']:.4f}, setup_rej={row['setup_rejections']}, hold_rej={row['hold_rejections']}", flush=True)

    print("DONE Stage 3 ->", OUT_JSON, "sha256=", sha256(OUT_JSON), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
