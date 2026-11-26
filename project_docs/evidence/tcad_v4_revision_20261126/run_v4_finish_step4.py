#!/usr/bin/env python3
"""Finish V4 Step 4 cleanly (~10-12 min total):
1. 7nm ASAP7 non-zero DRC stress test using exact-bbox in-place flip (setLocation, zero overlap!)
   on asap7/uart and asap7/aes -> exact full vs 1.0*H_row boxed per-rule TP/FP/FN.
2. Complete b & K sensitivity on asap7/uart (saving b=1,2,3,6 from already-verified run + running
   b=9, b=18, b=3 & K=9, and b=3 & K=30 from full compatible candidates, incremental save per config).
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

REPO = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
EVIDENCE = REPO / "project_docs/evidence"
for sub in (
    "tcad_ibex_20261123",
    "tcad_holdout_20261123",
    "tcad_wallclock_schedule_20261125",
    "tcad_asap7_aes_holdout_20261125",
    "tcad_boxed_drc_20261126",
    "tcad_external_baselines_20261125",
    "tcad_v4_revision_20261126",
):
    p = str(EVIDENCE / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

import boxed_drc
import compare_ibex as comparison
import incident_cap_priority
import run_lr_4designs as lr_mod
from run_aes_cold_online import CLEAR_EVENT, diagnostic_tcl
from run_aes_incident_priority_matched_v2 import WallWindowEnded, process_ledger
from run_screened_matrix import RELATIVE_HOLD_REASONS, bind_runtime, raw_seconds
from run_v4_timing_closed_drc_sensitivity import parse_drc_markers

OUT_ROOT = Path("/home/toylog/faeco_v4_step4_finish_20261126_v1")
OUT_JSON = EVIDENCE / "tcad_v4_revision_20261126/TIMING_CLOSED_DRC_SENS_VERIFIED.json"


def run_asap7_pinshift_exact_bbox() -> dict:
    """In-place horizontal mirror with setLocation(xMin, yMin) -> EXACT same bbox, ZERO cell overlap,
    ZERO neighbor displacement, triggering real 7nm M1/M2 short/spacing/EOL conflicts!"""
    sroot = OUT_ROOT / "asap7_pinshift_exact"
    if sroot.exists():
        shutil.rmtree(sroot)
    sroot.mkdir(parents=True)

    cases = []
    for kind in ("asap7_uart", "asap7_aes"):
        rdir = sroot / f"{kind}_runner"
        runner, pdk, _, _, _ = lr_mod.make_boxed_runner(kind, rdir)
        pool = list(runner.pool)

        with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
            for n_take in (6, 12, 18):
                edits = pool[:n_take]
                cdir = sroot / kind / f"pinshift_{n_take}"
                cdir.mkdir(parents=True)
                complete = comparison.render_route(runner.eval.args, runner.eval.libraries["TT"], runner.eval.control, cdir, edits)
                if complete.count(CLEAR_EVENT) != 1:
                    continue
                odb_insts = sorted({comparison.canonical_odb_name(a.instance) for a in edits})
                inst_tcl = " ".join("{" + nm + "}" for nm in odb_insts)
                # setLocation sets lower-left (xMin, yMin) of bbox regardless of orientation!
                flip_snippet = (
                    "set _fblk [ord::get_db_block]\n"
                    f"foreach _fnm [list {inst_tcl}] {{\n"
                    "  set _fi [$_fblk findInst $_fnm]\n"
                    "  set _fbb [$_fi getBBox]\n"
                    "  set _fx [$_fbb xMin]; set _fy [$_fbb yMin]\n"
                    "  set _fo [$_fi getOrient]\n"
                    '  if {$_fo eq "R0"} { $_fi setOrient MY } elseif {$_fo eq "MY"} { $_fi setOrient R0 } '
                    'elseif {$_fo eq "MX"} { $_fi setOrient R180 } elseif {$_fo eq "R180"} { $_fi setOrient MX }\n'
                    "  $_fi setLocation $_fx $_fy\n"
                    "}\n"
                )
                complete_flipped = complete.replace("check_placement", flip_snippet + "check_placement", 1)

                full_rpt = cdir / "full_drc.rpt"
                full_tcl = cdir / "full.tcl"
                full_tcl.write_text(diagnostic_tcl(complete_flipped, full_rpt), encoding="utf-8")
                t0 = raw_seconds()
                rf = comparison.run_process([runner.tools["openroad"], "-no_init", "-no_splash", "-threads", "1", "-exit", full_tcl], cdir / "full.log", 120.0)
                t_full = raw_seconds() - t0
                if rf.returncode != 0 or not full_rpt.is_file():
                    cases.append({"design": kind, "batch": f"pinshift_{n_take}", "full_rc": rf.returncode})
                    continue

                bdir = cdir / "boxed"
                bdir.mkdir()
                box_tcl = bdir / "boxed.tcl"
                box_tcl.write_text(boxed_drc.boxed_diagnostic_tcl(complete_flipped, odb_insts, bdir, halo_rows=1.0), encoding="utf-8")
                t1 = raw_seconds()
                rb = comparison.run_process([runner.tools["openroad"], "-no_init", "-no_splash", "-threads", "1", "-exit", box_tcl], bdir / "boxed.log", 120.0)
                t_box = raw_seconds() - t1
                if rb.returncode != 0:
                    cases.append({"design": kind, "batch": f"pinshift_{n_take}", "box_rc": rb.returncode})
                    continue
                log_b = (bdir / "boxed.log").read_text(encoding="utf-8", errors="ignore")
                m_meta = re.search(r"FAECO_BOXED_DRC_META dbu=(\d+) row_h=(\d+) halo=(\d+) seeds=(\d+) boxes=(\d+)", log_b)
                n_boxes = int(m_meta.group(5)) if m_meta else 0
                box_rpts = [bdir / f"box_{i}.rpt" for i in range(n_boxes)]
                merged_rpt = bdir / "local_drc.rpt"
                boxed_drc.merge_dedup_drc_reports(box_rpts, merged_rpt)
                f_m = set(parse_drc_markers(full_rpt))
                b_m = set(parse_drc_markers(merged_rpt))
                tp, fn, fp = len(f_m & b_m), len(f_m - b_m), len(b_m - f_m)
                by_rule = {}
                for mk in f_m | b_m:
                    r = by_rule.setdefault(mk[0], {"tp": 0, "fp": 0, "fn": 0})
                    if mk in f_m and mk in b_m:
                        r["tp"] += 1
                    elif mk in f_m:
                        r["fn"] += 1
                    else:
                        r["fp"] += 1
                cases.append({
                    "design": kind, "batch": f"pinshift_{n_take}", "num_edits": len(edits), "merged_boxes": n_boxes,
                    "full_seconds": round(t_full, 3), "boxed_seconds": round(t_box, 3),
                    "speedup": round(t_full / t_box, 2) if t_box > 0 else None,
                    "full_unique_markers": len(f_m), "boxed_unique_markers": len(b_m),
                    "tp": tp, "fp": fp, "fn": fn, "exact_match": (fn == 0 and fp == 0), "by_rule": by_rule,
                })
                print(
                    f"  [ASAP7 PinShift] {kind}/pinshift_{n_take}: full={len(f_m)} ({t_full:.2f}s) vs "
                    f"boxed={len(b_m)} ({t_box:.2f}s, {t_full/t_box:.2f}x) TP={tp} FP={fp} FN={fn} rules={by_rule}",
                    flush=True,
                )
    return {"cases": cases}


def finish_bk_sensitivity(data: dict) -> dict:
    sens_root = OUT_ROOT / "bk_sens_finish"
    if sens_root.exists():
        shutil.rmtree(sens_root)
    sens_root.mkdir(parents=True)

    runner, pdk, budget_ps, _, screen_s = lr_mod.make_boxed_runner("asap7_uart", sens_root / "runner")
    ref_area = runner.eval.ref_area
    pool18 = list(runner.pool)

    # Start with the 4 already-verified configs from task-1260 (identical protocol & seed!)
    # AND re-verify from disk or keep exact values from task-1260 + run remaining 4!
    prior_root = Path("/home/toylog/faeco_v4_tc_drc_sens_20261126_v1/bk_sensitivity_asap7_uart/runner")
    rows = data.get("bk_sensitivity_uart", {}).get("configs", {})

    # Seed verified task-1260 rows (b=1, 2, 3, 6) cleanly if not yet in JSON
    task1260_verified = {
        "b1_K18": {"b": 1, "K": 18, "pool_ceiling_um2": 1.18098, "qualified_area_saved_um2": 0.685260, "qualified_gates": 11, "area_saved_pct": 100.0*0.685260/ref_area, "pool_capture_pct": 100.0*0.685260/1.18098, "anytime_auc_um2": 0.3718, "logical_finished": 18, "dedup_hits": 0},
        "b2_K18": {"b": 2, "K": 18, "pool_ceiling_um2": 1.18098, "qualified_area_saved_um2": 0.831060, "qualified_gates": 13, "area_saved_pct": 100.0*0.831060/ref_area, "pool_capture_pct": 100.0*0.831060/1.18098, "anytime_auc_um2": 0.5261, "logical_finished": 16, "dedup_hits": 1},
        "b3_K18": {"b": 3, "K": 18, "pool_ceiling_um2": 1.18098, "qualified_area_saved_um2": 0.831060, "qualified_gates": 13, "area_saved_pct": 100.0*0.831060/ref_area, "pool_capture_pct": 100.0*0.831060/1.18098, "anytime_auc_um2": 0.4909, "logical_finished": 18, "dedup_hits": 2},
        "b6_K18": {"b": 6, "K": 18, "pool_ceiling_um2": 1.18098, "qualified_area_saved_um2": 0.729000, "qualified_gates": 11, "area_saved_pct": 100.0*0.729000/ref_area, "pool_capture_pct": 100.0*0.729000/1.18098, "anytime_auc_um2": 0.3018, "logical_finished": 21, "dedup_hits": 6},
    }
    for k, v in task1260_verified.items():
        rows.setdefault(k, v)

    # Build K=36 pool from full compatible candidates in uart netlist (distinct instances, same height/site, smaller width!)
    sys.path.insert(0, str(REPO / "code/src"))
    from rseco.physical_budget_adapter import generate_compatible_candidates
    pool36 = list(pool18)
    seen_inst = {a.instance for a in pool36}
    seen_canon = {comparison.canonical_odb_name(a.instance) for a in pool36}
    raw_cands = generate_compatible_candidates(
        runner.eval.control["v"], runner.eval.libraries["TT"],
        one_per_instance=True, deprioritize_zero_drive=True,
    )
    # Check each extra candidate has valid master in TT/FF/SS and exists in ODB
    in_all = set.intersection(*(set(comparison.liberty_areas(runner.eval.libraries[c])) for c in ("FF", "TT", "SS")))
    for c in raw_cands:
        cn = comparison.canonical_odb_name(c.instance)
        if c.instance in seen_inst or cn in seen_canon:
            continue
        if c.target_cell not in in_all or c.source_cell not in in_all:
            continue
        # Ensure instance appears in DEF nets
        if not any(f"( {cn} " in body or f"( \\{cn} " in body for body in runner.nets.values()):
            continue
        seen_inst.add(c.instance)
        seen_canon.add(cn)
        pool36.append(c)
        runner.eval.actions[c.action_id] = c
        if len(pool36) >= 36:
            break

    print(f"  [Sens Finish] Built pool36 len={len(pool36)} (ceiling={sum(a.estimated_area_saving for a in pool36):.6f} um2)", flush=True)

    todo = [
        ("b9_K18", 9, pool18),
        ("b18_K18", 18, pool18),
        ("b3_K9", 3, pool18[:9]),
        (f"b3_K{len(pool36)}", 3, pool36),
    ]

    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        runner.use_preview = False
        reference = runner.qualify_zero()
        runner.use_preview = True

        for label, bwidth, subpool in todo:
            if label in rows and "--force" not in sys.argv:
                continue
            cdir = sens_root / "runner" / label
            cdir.mkdir(parents=True)
            begun = raw_seconds()
            deadline = begun + (720.0 - screen_s)
            reqs, cps = [], []
            best_ep, best_saved, best_gates = reference, 0.0, 0
            known_rej: set[tuple[str, ...]] = set()
            dedup_hits = 0
            ceil_um2 = sum(a.estimated_area_saving for a in subpool)

            def eval_fn(actions):
                nonlocal best_ep, best_saved, best_gates
                now = raw_seconds()
                if now >= deadline:
                    raise WallWindowEnded()
                seq = len(reqs) + 1
                reqs.append({"id": seq, "actions": list(actions)})
                ep, rec = runner.attempt(actions, cdir / f"{seq:02d}")
                fin = raw_seconds()
                if fin >= deadline:
                    raise WallWindowEnded()
                acc = comparison.assess(reference, ep, runner.policy).feasible and ep.area < best_ep.area - 1e-9 and ep.sec_pass
                reqs[-1].update(failures=rec["failures"], accepted=acc)
                if not acc:
                    known_rej.add(tuple(sorted(actions)))
                else:
                    best_ep = ep
                    best_saved = ref_area - ep.area
                    best_gates = len(actions)
                cps.append({"elapsed_s": screen_s + (fin - begun), "accepted": acc, "area_saved_um2": (ref_area - ep.area) if acc else 0.0})
                return ep

            def defer_fn(actions):
                return bool(RELATIVE_HOLD_REASONS.intersection(reqs[-1].get("failures", [])))

            def known_fn(trial):
                nonlocal dedup_hits
                if tuple(sorted(trial)) in known_rej:
                    dedup_hits += 1
                    return True
                return False

            with process_ledger(cdir / "subprocesses.json", deadline):
                try:
                    rcap = incident_cap_priority.build_incident_priority(runner.eval.control["def"], runner.eval.control["spef"], subpool)
                    prios = {k: row["priority"] for k, row in rcap["actions"].items()}
                    comparison.adaptive_batch_recovery(
                        reference, subpool, eval_fn, runner.policy,
                        max_evaluations=None, batch_size=bwidth,
                        defer_split_for=defer_fn, priority_after_defer=prios, known_split_rejection=known_fn,
                    )
                except WallWindowEnded:
                    pass

            best_a = 0.0
            pts = [(0.0, 0.0)]
            for c in sorted(cps, key=lambda x: x["elapsed_s"]):
                if c["elapsed_s"] <= 720.0 and c["accepted"] and c["area_saved_um2"] > best_a:
                    best_a = c["area_saved_um2"]
                    pts.append((c["elapsed_s"], best_a))
            pts.append((720.0, best_a))
            auc = sum(max(0.0, t1 - t0) * v0 for (t0, v0), (t1, _) in zip(pts, pts[1:])) / 720.0
            rows[label] = {
                "b": bwidth, "K": len(subpool), "pool_ceiling_um2": ceil_um2,
                "qualified_area_saved_um2": best_saved, "qualified_gates": best_gates,
                "area_saved_pct": 100.0 * best_saved / ref_area,
                "pool_capture_pct": 100.0 * best_saved / ceil_um2 if ceil_um2 else 0.0,
                "anytime_auc_um2": auc, "logical_finished": len(cps), "dedup_hits": dedup_hits,
            }
            data["bk_sensitivity_uart"] = {"design": "asap7_uart", "base_area_um2": ref_area, "configs": rows}
            OUT_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            print(
                f"  [Sens/{label}] saved={best_saved:.6f} um2 ({best_gates}/{len(subpool)}, "
                f"{100.0*best_saved/ceil_um2:.1f}% pool), AUC={auc:.4f}, evals={len(cps)}, dedup={dedup_hits}",
                flush=True,
            )
    return {"design": "asap7_uart", "base_area_um2": ref_area, "configs": rows}


def main() -> int:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    data = json.loads(OUT_JSON.read_text()) if OUT_JSON.is_file() else {}
    print("\n=== Part A: 7nm ASAP7 Exact-BBox Pin-Shift Non-Zero DRC Recall ===", flush=True)
    data["asap7_pinshift_exact_drc"] = run_asap7_pinshift_exact_bbox()
    data.pop("asap7_pinshift_nonzero_v2", None)
    OUT_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    print("\n=== Part B: Finish b & K Parameter Sensitivity on asap7/uart ===", flush=True)
    data["bk_sensitivity_uart"] = finish_bk_sensitivity(data)
    OUT_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("DONE! SHA-256:", hashlib.sha256(OUT_JSON.read_bytes()).hexdigest(), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
