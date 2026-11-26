#!/usr/bin/env python3
"""V5 Stage 3 (resumable, pinned CPU 0-5):
Independent Online Multi-Budget Setup Sweep (B_W / P_clk in {0.0%, 0.5%, 1.0%, 2.0%})
under identical 1.0*H_row boxed DRC backend, 18-action pool, and 720 s wall-clock budget
on BOTH asap7/uart (Setup-sensitive small block) and sky130hd/aes (wall-clock/Hold-dominated 10k-gate block).
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

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
from run_aes_incident_priority_matched_v2 import WallWindowEnded, process_ledger
from run_screened_matrix import RELATIVE_HOLD_REASONS, bind_runtime, raw_seconds

OUT_ROOT = Path("/home/toylog/faeco_v5_step3_multibudget_20261126_v1")
OUT_JSON = EVID / "tcad_v5_revision_20261126/V5_STEP3_MULTIBUDGET_VERIFIED.json"
LIMIT_S = 720.0
SETUP_REASONS = {"FF:setup_budget", "TT:setup_budget", "SS:setup_budget", "FF:tns_budget", "TT:tns_budget", "SS:tns_budget"}


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


def run_one_budget(kind: str, clk_ps: float, pct: float) -> dict:
    budget_ps = clk_ps * pct / 100.0
    tag = f"{kind}__pct_{pct:.1f}".replace(".", "p")
    rdir = OUT_ROOT / tag
    if rdir.exists():
        shutil.rmtree(rdir)
    runner, pdk, _, _, screen_s = lr_mod.make_boxed_runner(kind, rdir)
    if not hasattr(runner, "initial_hint"):
        runner.initial_hint = set()
    runner.gate = cmp.Gate(
        wns_ps=budget_ps,
        tns_ps=max(0.10 * clk_ps, 0.01 * abs(runner.eval.ref_views["TT"]["setup_tns_ps"])) if hasattr(runner.eval, "ref_views") else runner.gate.tns_ps,
    ) if hasattr(cmp, "Gate") else runner.gate
    runner.policy = cmp.BudgetPolicy.from_ps(budget_ps, tolerance_ns=cmp.PS_TOLERANCE / 1000)

    ref_area = runner.eval.ref_area
    pool = list(runner.pool)
    pool_ceiling = sum(a.estimated_area_saving for a in pool)

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

        # Re-bind policy after prepare_online/qualify_zero in case runner overwrites it
        runner.policy = cmp.BudgetPolicy.from_ps(budget_ps, tolerance_ns=cmp.PS_TOLERANCE / 1000)

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
            ep, rec = runner.attempt(actions, rdir / "trials" / f"{seq:02d}")
            fin = raw_seconds()
            if fin >= deadline:
                raise WallWindowEnded()
            acc = cmp.assess(reference, ep, runner.policy).feasible and ep.area < best_ep.area - 1e-9 and ep.sec_pass
            fails = set(rec["failures"])
            reqs[-1].update(failures=list(fails), accepted=acc)
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
            cps.append({"elapsed_s": screen_s + (fin - begun), "accepted": acc, "area_saved_um2": (ref_area - ep.area) if acc else 0.0, "failures": list(fails)})
            return ep

        def defer_fn(actions):
            return bool(RELATIVE_HOLD_REASONS.intersection(reqs[-1].get("failures", [])))

        def known_fn(trial):
            nonlocal dedup_hits
            if tuple(sorted(trial)) in known_rej:
                dedup_hits += 1
                return True
            return False

        with process_ledger(rdir / "subprocesses.json", deadline):
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
                pass

        auc = compute_auc(cps, LIMIT_S)
        return {
            "design": kind,
            "clock_period_ps": clk_ps,
            "setup_budget_pct": pct,
            "setup_budget_ps": budget_ps,
            "qualified_area_saved_um2": best_saved,
            "qualified_gates": best_gates,
            "area_saved_pct": 100.0 * best_saved / ref_area,
            "pool_capture_pct": 100.0 * best_saved / pool_ceiling,
            "anytime_auc_um2": auc,
            "logical_finished": len(cps),
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
        OUT_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"  DONE {key}: saved={row['qualified_area_saved_um2']:.6f} um2 ({row['qualified_gates']}/18), "
              f"AUC={row['anytime_auc_um2']:.4f}, setup_rej={row['setup_rejections']}, hold_rej={row['hold_rejections']}", flush=True)

    print("DONE Stage 3 ->", OUT_JSON, "sha256=", sha256(OUT_JSON), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
