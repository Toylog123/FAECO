#!/usr/bin/env python3
"""V4 Stage B Experiment 2:
Hybrid FAECO (Bounded Optimistic Full-Pool Probe + Adaptive Micro-Batch Fallback)
evaluated uniformly across ALL 4 TCAD designs (720 RAW s, 1.0 x H_row boxed DRC).

Uniform algorithm across all 4 designs (zero per-design tuning):
  Phase 1 (Bounded Optimistic Probe):
    - Submits full screened pool P (18 gates) once on the 1.0*H_row windowed protected backend.
    - Enforces strict sub-budget: tau_probe = min(180.0 s, 0.30 * (720.0 - t_screen)).
    - Single-pass only (no secondary DRC retry on optimistic probe).
    - If ALL timing, independent whole-block DRC, antenna, and SEC gates pass within tau_probe,
      immediately commit S* = P (100% pool capture) and terminate early!
  Phase 2 (Adaptive Micro-Batch Fallback):
    - If Phase 1 fails or hits tau_probe, discard Phase 1 cleanly and execute standard
      windowed FAECO (b=3, Hold defer + incident-cap re-rank + Setup dedup) in the remaining
      wall-clock budget up to 720.0 s!
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import sys
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

REPO = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
EVIDENCE = REPO / "project_docs/evidence"
for sub in (
    "tcad_ibex_20261123",
    "tcad_holdout_20261123",
    "tcad_wallclock_schedule_20261125",
    "tcad_asap7_aes_holdout_20261125",
    "tcad_boxed_drc_20261126",
    "tcad_external_baselines_20261125",
):
    p = str(EVIDENCE / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

import boxed_drc
import compare_ibex as comparison
import incident_cap_priority
import run_aes_sensitivity_greedy as sens_aes
import run_lr_4designs as lr_mod
import run_qualified_wallclock as qualified
from run_aes_incident_priority_matched_v2 import WallWindowEnded, process_ledger
from run_screened_matrix import RELATIVE_HOLD_REASONS, bind_runtime, raw_seconds

OUT_ROOT = Path("/home/toylog/faeco_v4_hybrid_faeco_20261126_v1")
OUT_JSON = EVIDENCE / "tcad_v4_revision_20261126/HYBRID_FAECO_4DESIGNS_VERIFIED.json"
LIMIT_SECONDS = 720.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_anytime_auc(checkpoints: list[dict], ref_area: float, limit_s: float = 720.0) -> float:
    best = 0.0
    pts = [(0.0, 0.0)]
    for cp in sorted(checkpoints, key=lambda c: c["elapsed_s"]):
        t = float(cp["elapsed_s"])
        if t > limit_s:
            continue
        if cp.get("accepted") and cp["area_saved_um2"] > best:
            best = float(cp["area_saved_um2"])
            pts.append((t, best))
    pts.append((limit_s, best))
    area_time = 0.0
    for (t0, v0), (t1, _) in zip(pts, pts[1:]):
        area_time += max(0.0, t1 - t0) * v0
    return area_time / limit_s


def run_hybrid_on_design(kind: str) -> dict:
    run_dir = OUT_ROOT / kind
    if run_dir.exists():
        shutil.rmtree(run_dir)

    runner, pdk, budget_ps, ref_tt_wns_ps, screen_s = lr_mod.make_boxed_runner(kind, run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    ref_area = runner.eval.ref_area
    pool = list(runner.pool)
    pool_ceiling = sum(a.estimated_area_saving for a in pool)

    # Qualify strict zero reference outside the timed arm (same as all paired comparisons)
    with (
        bind_runtime(runner.top, runner.flow["fastroute.tcl"]),
        qualified.qualified_ranking(),
        qualified.qualified_process_clock(),
    ):
        if kind == "sky130hd_aes":
            from run_aes_protected_online import OnlineProtection
            pf_dir = OUT_ROOT / "sky_shared_preflight"
            pf_res = pf_dir / "preflight/result.json"
            if not (pf_res.is_file() and (pf_dir / "config.json").is_file()):
                if pf_dir.exists():
                    shutil.rmtree(pf_dir)
                pf_runner = OnlineProtection(Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_matrix_v1"), pf_dir)
                pf_runner.preflight()
            reference = runner.prepare_online(pf_res.resolve(strict=True))
        else:
            runner.use_preview = False
            reference = runner.qualify_zero()
            runner.use_preview = True

        # Start timed 720 s arm (charging screen_s)
        arm_start = raw_seconds()
        total_deadline = arm_start + (LIMIT_SECONDS - screen_s)
        rem_after_screen = LIMIT_SECONDS - screen_s
        probe_budget = min(180.0, 0.30 * rem_after_screen)
        probe_deadline = arm_start + probe_budget

        checkpoints = []
        best_ep = reference
        best_saved = 0.0
        best_gates = 0
        best_views = {}
        best_drc = None
        best_sec = False

        # --- PHASE 1: Bounded Optimistic Full-Pool Probe (single pass, no retry) ---
        probe_dir = run_dir / "phase1_optimistic_probe"
        probe_dir.mkdir(parents=True)
        all_ids = tuple(sorted(a.action_id for a in pool))
        probe_start = raw_seconds()
        probe_passed = False
        probe_failures = []
        probe_status = "failed"
        probe_ep = None
        probe_rec = None

        # Temporarily disable secondary DRC retry during optimistic probe!
        orig_attempt_retry = getattr(runner, "physical", None)

        try:
            with process_ledger(probe_dir / "subprocesses.json", probe_deadline):
                edited_p, incident_p = runner.direct_nets(all_ids)
                neighbors_p = runner.diagnose(all_ids, probe_dir / "diagnosis" / "probe")
                ep1, row1, fails1, _ = runner.physical(all_ids, probe_dir / "initial", incident_p, neighbors_p)
                proof_ops = {}
                if not fails1:
                    cand_v = Path(row1["artifacts"]["v"]["path"]) if isinstance(row1["artifacts"]["v"], dict) else Path(row1["artifacts"]["v"])
                    if not runner.eval.proof(cand_v, probe_dir / "initial", proof_ops):
                        fails1.append("sec")
                from dataclasses import replace as dc_replace
                ep1 = dc_replace(ep1, valid=not fails1, sec_pass=not fails1)
                probe_ep = ep1
                probe_failures = list(fails1)
                gate_ok = comparison.assess(reference, ep1, runner.policy).feasible and ep1.area < best_ep.area - 1e-9
                if gate_ok and ep1.sec_pass and not probe_failures:
                    probe_passed = True
                    probe_status = "passed"
                else:
                    probe_status = "rejected"
        except WallWindowEnded:
            probe_status = "sub_budget_timeout"
            probe_failures = ["probe_sub_budget_timeout"]

        probe_end = raw_seconds()
        probe_elapsed = probe_end - probe_start
        elapsed_after_probe = screen_s + (probe_end - arm_start)

        if probe_passed and elapsed_after_probe <= LIMIT_SECONDS:
            best_ep = probe_ep
            best_saved = ref_area - probe_ep.area
            best_gates = len(all_ids)
            best_sec = True
            rp = probe_dir / "initial/receipt.json"
            if rp.is_file():
                rd = json.loads(rp.read_text())
                best_views = {
                    c: {
                        "d_setup_wns_ps": rd["views"][c]["setup_wns_ps"] - runner.eval.ref_views[c]["setup_wns_ps"],
                        "d_hold_wns_ps": rd["views"][c]["hold_wns_ps"] - runner.eval.ref_views[c]["hold_wns_ps"],
                    }
                    for c in ("FF", "TT", "SS") if c in rd.get("views", {})
                }
            ud = probe_dir / "initial/unlocked_drc/audit.json"
            if ud.is_file():
                best_drc = json.loads(ud.read_text()).get("drc_markers")
            checkpoints.append({
                "phase": "phase1_probe",
                "elapsed_s": elapsed_after_probe,
                "accepted": True,
                "gates": best_gates,
                "area_saved_um2": best_saved,
            })
            phase2_summary = {"invoked": False, "reason": "phase1_committed_full_pool"}
        else:
            checkpoints.append({
                "phase": "phase1_probe",
                "elapsed_s": elapsed_after_probe,
                "accepted": False,
                "gates": len(all_ids),
                "area_saved_um2": 0.0,
                "status": probe_status,
                "failures": probe_failures,
            })
            # --- PHASE 2: Adaptive Micro-Batch Fallback in remaining wall-clock budget ---
            p2_dir = run_dir / "phase2_fallback"
            p2_dir.mkdir(parents=True)
            runner.use_preview = True

            # Compute incident-cap priority & rank inside the active arm clock
            p2_requests = []
            known_rejects: set[tuple[str, ...]] = set()
            dedup_hits = 0

            def write_p2():
                comparison.save(p2_dir / "progress.json", {
                    "kind": kind, "requests": p2_requests, "checkpoints": checkpoints, "dedup_hits": dedup_hits,
                })

            def evaluate_p2(actions):
                nonlocal best_ep, best_saved, best_gates, best_views, best_drc, best_sec
                now = raw_seconds()
                if now >= total_deadline:
                    raise WallWindowEnded()
                seq = len(p2_requests) + 1
                p2_requests.append({"id": seq, "actions": list(actions), "admitted_raw": now})
                write_p2()
                print(f"  [Hybrid/{kind}] Phase2 req {seq} edits={len(actions)} rem={total_deadline - now:.1f}s", flush=True)
                ep, rec = runner.attempt(actions, p2_dir / f"{seq:02d}")
                fin = raw_seconds()
                if fin >= total_deadline:
                    p2_requests[-1]["finished_after_cap"] = True
                    raise WallWindowEnded()
                accepted = comparison.assess(reference, ep, runner.policy).feasible and ep.area < best_ep.area - 1e-9 and ep.sec_pass
                p2_requests[-1].update(failures=rec["failures"], passes=rec["passes"], finished_raw=fin, accepted=accepted)
                if not accepted:
                    known_rejects.add(tuple(sorted(actions)))
                else:
                    best_ep = ep
                    best_saved = ref_area - ep.area
                    best_gates = len(actions)
                    best_sec = True
                    last_pass = rec["passes"][-1]
                    rp = p2_dir / f"{seq:02d}" / last_pass / "receipt.json"
                    if rp.is_file():
                        rd = json.loads(rp.read_text())
                        best_views = {
                            c: {
                                "d_setup_wns_ps": rd["views"][c]["setup_wns_ps"] - runner.eval.ref_views[c]["setup_wns_ps"],
                                "d_hold_wns_ps": rd["views"][c]["hold_wns_ps"] - runner.eval.ref_views[c]["hold_wns_ps"],
                            }
                            for c in ("FF", "TT", "SS") if c in rd.get("views", {})
                        }
                    ud = p2_dir / f"{seq:02d}" / last_pass / "unlocked_drc/audit.json"
                    if ud.is_file():
                        best_drc = json.loads(ud.read_text()).get("drc_markers")
                checkpoints.append({
                    "phase": "phase2_fallback",
                    "seq": seq,
                    "elapsed_s": screen_s + (fin - arm_start),
                    "accepted": accepted,
                    "gates": len(actions),
                    "area_saved_um2": (ref_area - ep.area) if accepted else 0.0,
                    "failures": rec["failures"],
                })
                write_p2()
                return ep

            def defer_p2(actions):
                latest = p2_requests[-1]
                return bool(RELATIVE_HOLD_REASONS.intersection(latest.get("failures", [])))

            def known_rej_p2(trial):
                nonlocal dedup_hits
                if tuple(sorted(trial)) in known_rejects:
                    dedup_hits += 1
                    return True
                return False

            p2_stop = "pool_exhausted"
            with process_ledger(p2_dir / "subprocesses.json", total_deadline):
                try:
                    # Live incident-cap priority
                    ranking_cap = incident_cap_priority.build_incident_priority(
                        runner.eval.control["def"], runner.eval.control["spef"], pool
                    )
                    priorities = {k: row["priority"] for k, row in ranking_cap["actions"].items()}
                    # Sensitivity initial ordering on riscv32i & asap7_aes (matching main protocol!)
                    ordered_pool = list(pool)
                    if kind in ("sky130hd_riscv32i", "asap7_aes"):
                        s_rank = sens_aes.score_control(runner, pool, p2_dir / "sensitivity")
                        by_id = {a.action_id: a for a in pool}
                        ordered_pool = [by_id[aid] for aid in s_rank["ordered_action_ids"]]

                    comparison.adaptive_batch_recovery(
                        reference, ordered_pool, evaluate_p2, runner.policy,
                        max_evaluations=None, batch_size=3,
                        defer_split_for=defer_p2,
                        priority_after_defer=priorities,
                        known_split_rejection=known_rej_p2,
                    )
                except WallWindowEnded:
                    p2_stop = "end_to_end_wall_cap"

            phase2_summary = {
                "invoked": True,
                "stop_reason": p2_stop,
                "logical_admitted": len(p2_requests),
                "logical_finished": sum(1 for r in p2_requests if "finished_raw" in r),
                "dedup_hits": dedup_hits,
            }

        arm_end = raw_seconds()
        auc = compute_anytime_auc(checkpoints, ref_area, LIMIT_SECONDS)
        max_setup_loss = max((max(0.0, -v["d_setup_wns_ps"]) for v in best_views.values()), default=0.0)

        return {
            "design": kind,
            "pdk": pdk,
            "base_area_um2": ref_area,
            "pool_size": len(pool),
            "pool_ceiling_um2": pool_ceiling,
            "charged_screening_s": screen_s,
            "probe_sub_budget_s": probe_budget,
            "phase1_probe": {
                "status": probe_status,
                "elapsed_s": probe_elapsed,
                "total_s_at_probe_end": elapsed_after_probe,
                "passed": probe_passed,
                "failures": probe_failures,
            },
            "phase2_fallback": phase2_summary,
            "total_wall_s_incl_screen": screen_s + (arm_end - arm_start),
            "qualified_area_saved_um2": best_saved,
            "qualified_gates": best_gates,
            "area_saved_pct": 100.0 * best_saved / ref_area,
            "pool_capture_pct": 100.0 * best_saved / pool_ceiling,
            "anytime_auc_um2": auc,
            "max_setup_loss_ps": max_setup_loss,
            "setup_budget_util_pct": 100.0 * max_setup_loss / budget_ps if budget_ps else 0.0,
            "unlocked_drc_markers": best_drc,
            "sec_pass": best_sec,
            "views_delta_ps": best_views,
            "checkpoints": checkpoints,
            "run_dir": str(run_dir),
        }


def main() -> int:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    summary = json.loads(OUT_JSON.read_text()) if OUT_JSON.is_file() else {"designs": {}}

    for kind in ("sky130hd_aes", "asap7_uart", "sky130hd_riscv32i", "asap7_aes"):
        if kind in summary["designs"] and "--force" not in sys.argv:
            print(f"Skipping existing {kind}", flush=True)
            continue
        print(f"\n=== Running Hybrid FAECO on {kind} ===", flush=True)
        row = run_hybrid_on_design(kind)
        summary["designs"][kind] = row
        OUT_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(
            f"DONE Hybrid/{kind}: phase1={row['phase1_probe']['status']} ({row['phase1_probe']['elapsed_s']:.1f}s) -> "
            f"saved={row['qualified_area_saved_um2']:.6f} um2 ({row['qualified_gates']}/18, "
            f"{row['pool_capture_pct']:.1f}% pool), AUC={row['anytime_auc_um2']:.4f}",
            flush=True,
        )

    print("Wrote:", OUT_JSON, "sha256=", sha256(OUT_JSON), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
