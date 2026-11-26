#!/usr/bin/env python3
"""V5 Stage 4 (resumable, pinned CPU 0-5):
Hybrid Probe Sub-Budget Sensitivity: tau_probe in {0, 60, 120, 180, 240} s
on BOTH sky130hd_aes and asap7_aes under identical 1.0*H_row boxed DRC & 720 s wall-clock.
- Imports already-verified 0 s (Pure FAECO) & default 180 s / 169.1 s (Hybrid FAECO) receipts.
- Runs fresh controlled experiments for tau_probe in {60, 120, 240} s on BOTH AES designs.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from dataclasses import replace as dc_replace
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
    "tcad_v4_revision_20261126",
):
    p = str(EVID / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

import compare_ibex as cmp
import incident_cap_priority
import run_aes_sensitivity_greedy as sens_aes
import run_lr_4designs as lr_mod
import run_qualified_wallclock as qualified
from run_aes_incident_priority_matched_v2 import WallWindowEnded, process_ledger
from run_screened_matrix import RELATIVE_HOLD_REASONS, bind_runtime, raw_seconds

OUT_ROOT = Path("/home/toylog/faeco_v5_step4_probe_sens_20261126_v1")
OUT_JSON = EVID / "tcad_v5_revision_20261126/V5_STEP4_PROBE_SENS_VERIFIED.json"
LIMIT_S = 720.0


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


def run_hybrid_custom_probe(kind: str, probe_budget_s: float) -> dict:
    rdir = OUT_ROOT / f"{kind}__probe_{int(probe_budget_s)}s"
    if rdir.exists():
        shutil.rmtree(rdir)
    runner, pdk, budget_ps, _, screen_s = lr_mod.make_boxed_runner(kind, rdir)
    rdir.mkdir(parents=True, exist_ok=True)
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

        arm_start = raw_seconds()
        total_deadline = arm_start + (LIMIT_S - screen_s)
        probe_deadline = min(total_deadline, arm_start + probe_budget_s)
        checkpoints = []
        best_ep = reference
        best_saved = 0.0
        best_gates = 0

        # Phase 1: Bounded Optimistic Full-Pool Probe
        probe_dir = rdir / "phase1_probe"
        probe_dir.mkdir(parents=True)
        all_ids = tuple(sorted(a.action_id for a in pool))
        p_start = raw_seconds()
        probe_passed = False
        probe_status = "failed"
        try:
            with process_ledger(probe_dir / "subprocesses.json", probe_deadline):
                _, incident_p = runner.direct_nets(all_ids)
                neighbors_p = runner.diagnose(all_ids, probe_dir / "diag")
                ep1, row1, fails1, _ = runner.physical(all_ids, probe_dir / "initial", incident_p, neighbors_p)
                if not fails1:
                    cand_v = Path(row1["artifacts"]["v"]["path"]) if isinstance(row1["artifacts"]["v"], dict) else Path(row1["artifacts"]["v"])
                    if not runner.eval.proof(cand_v, probe_dir / "initial", {}):
                        fails1.append("sec")
                ep1 = dc_replace(ep1, valid=not fails1, sec_pass=not fails1)
                if cmp.assess(reference, ep1, runner.policy).feasible and ep1.area < best_ep.area - 1e-9 and ep1.sec_pass:
                    probe_passed = True
                    probe_status = "passed"
                    best_ep = ep1
                    best_saved = ref_area - ep1.area
                    best_gates = len(all_ids)
                else:
                    probe_status = "rejected"
        except WallWindowEnded:
            probe_status = "sub_budget_timeout"

        p_end = raw_seconds()
        probe_elapsed = p_end - p_start
        elapsed_after_probe = screen_s + (p_end - arm_start)

        if probe_passed and elapsed_after_probe <= LIMIT_S:
            checkpoints.append({"phase": "phase1", "elapsed_s": elapsed_after_probe, "accepted": True, "gates": best_gates, "area_saved_um2": best_saved})
        else:
            checkpoints.append({"phase": "phase1", "elapsed_s": elapsed_after_probe, "accepted": False, "gates": len(all_ids), "area_saved_um2": 0.0, "status": probe_status})
            # Phase 2 fallback
            p2_dir = rdir / "phase2_fallback"
            p2_dir.mkdir(parents=True)
            runner.use_preview = True
            reqs = []
            known_rej: set[tuple[str, ...]] = set()

            def eval_p2(actions):
                nonlocal best_ep, best_saved, best_gates
                now = raw_seconds()
                if now >= total_deadline:
                    raise WallWindowEnded()
                seq = len(reqs) + 1
                reqs.append({"id": seq, "actions": list(actions)})
                ep, rec = runner.attempt(actions, p2_dir / f"{seq:02d}")
                fin = raw_seconds()
                if fin >= total_deadline:
                    raise WallWindowEnded()
                acc = cmp.assess(reference, ep, runner.policy).feasible and ep.area < best_ep.area - 1e-9 and ep.sec_pass
                reqs[-1].update(failures=rec["failures"], accepted=acc)
                if not acc:
                    known_rej.add(tuple(sorted(actions)))
                else:
                    best_ep = ep
                    best_saved = ref_area - ep.area
                    best_gates = len(actions)
                checkpoints.append({"phase": "phase2", "elapsed_s": screen_s + (fin - arm_start), "accepted": acc, "gates": len(actions), "area_saved_um2": (ref_area - ep.area) if acc else 0.0})
                return ep

            def defer_p2(actions):
                return bool(RELATIVE_HOLD_REASONS.intersection(reqs[-1].get("failures", [])))

            def known_p2(trial):
                return tuple(sorted(trial)) in known_rej

            with process_ledger(p2_dir / "subprocesses.json", total_deadline):
                try:
                    rcap = incident_cap_priority.build_incident_priority(runner.eval.control["def"], runner.eval.control["spef"], pool)
                    prios = {k: row["priority"] for k, row in rcap["actions"].items()}
                    ordered = list(pool)
                    if kind == "asap7_aes":
                        s_rank = sens_aes.score_control(runner, pool, p2_dir / "sensitivity")
                        by_id = {a.action_id: a for a in pool}
                        ordered = [by_id[aid] for aid in s_rank["ordered_action_ids"]]
                    cmp.adaptive_batch_recovery(
                        reference, ordered, eval_p2, runner.policy,
                        max_evaluations=None, batch_size=3,
                        defer_split_for=defer_p2, priority_after_defer=prios, known_split_rejection=known_p2,
                    )
                except WallWindowEnded:
                    pass

        auc = compute_auc(checkpoints, LIMIT_S)
        return {
            "design": kind,
            "tau_probe_s": probe_budget_s,
            "phase1_status": probe_status,
            "phase1_elapsed_s": round(probe_elapsed, 3),
            "qualified_area_saved_um2": best_saved,
            "qualified_gates": best_gates,
            "pool_capture_pct": 100.0 * best_saved / pool_ceiling,
            "anytime_auc_um2": auc,
            "checkpoints": checkpoints,
        }


def main() -> int:
    force = "--force" in sys.argv
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(OUT_JSON.read_text()) if OUT_JSON.is_file() else {"runs": {}, "imported_references": {}}

    # Import already-verified 0s (Pure FAECO) & default Hybrid (180s / 169.1s) for clean 5-point table
    hyb = json.loads((EVID / "tcad_v4_revision_20261126/HYBRID_FAECO_4DESIGNS_VERIFIED.json").read_text())
    boxed = json.loads((EVID / "tcad_boxed_drc_20261126/BOXED_DRC_VERIFIED.json").read_text())
    data["imported_references"] = {
        "sky130hd_aes::0s": {"tau_probe_s": 0.0, "qualified_area_saved_um2": 98.8448, "qualified_gates": 9, "anytime_auc_um2": 19.37, "source": "BOXED_DRC_VERIFIED.json"},
        "sky130hd_aes::180s": {
            "tau_probe_s": 180.0,
            "qualified_area_saved_um2": hyb["designs"]["sky130hd_aes"]["qualified_area_saved_um2"],
            "qualified_gates": hyb["designs"]["sky130hd_aes"]["qualified_gates"],
            "anytime_auc_um2": hyb["designs"]["sky130hd_aes"]["anytime_auc_um2"],
            "source": "HYBRID_FAECO_4DESIGNS_VERIFIED.json",
        },
        "asap7_aes::0s": {"tau_probe_s": 0.0, "qualified_area_saved_um2": 0.61236, "qualified_gates": 6, "anytime_auc_um2": 0.254, "source": "BOXED_DRC_VERIFIED.json"},
        "asap7_aes::169s_default": {
            "tau_probe_s": round(hyb["designs"]["asap7_aes"]["probe_sub_budget_s"], 2),
            "qualified_area_saved_um2": hyb["designs"]["asap7_aes"]["qualified_area_saved_um2"],
            "qualified_gates": hyb["designs"]["asap7_aes"]["qualified_gates"],
            "anytime_auc_um2": hyb["designs"]["asap7_aes"]["anytime_auc_um2"],
            "source": "HYBRID_FAECO_4DESIGNS_VERIFIED.json",
        },
    }

    for kind in ("sky130hd_aes", "asap7_aes"):
        for tau in (60.0, 120.0, 240.0):
            key = f"{kind}::{int(tau)}s"
            if key in data["runs"] and not force:
                print(f"[Stage 4] Skipping existing {key}", flush=True)
                continue
            print(f"\n=== [Stage 4] Running Hybrid probe sensitivity {key} ===", flush=True)
            row = run_hybrid_custom_probe(kind, tau)
            data["runs"][key] = row
            OUT_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            print(f"  DONE {key}: p1={row['phase1_status']} ({row['phase1_elapsed_s']}s) -> "
                  f"saved={row['qualified_area_saved_um2']:.6f} um2 ({row['qualified_gates']}/18), AUC={row['anytime_auc_um2']:.4f}", flush=True)

    print("DONE Stage 4 ->", OUT_JSON, "sha256=", sha256(OUT_JSON), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
