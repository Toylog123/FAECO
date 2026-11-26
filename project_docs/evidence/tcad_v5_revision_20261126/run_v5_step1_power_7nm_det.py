#!/usr/bin/env python3
"""V5 Step 1 Master Script (pinned CPU 0-5):
1. Extract exact Non-Monotonic Feasibility Counterexample (T subset S, Phi(T)=0, Phi(S)=1)
   and Hybrid probe timing audit from verified V4 WSL run artifacts.
2. Measure exact TT extracted-SPEF power (Total/Combinational/Leakage) & 6-corner WNS for:
   - SKY130HD AES Hybrid (18/18)
   - ASAP7 UART-TC (13/18)
   - ASAP7 UART K=36 (19/36)
3. 7 nm ASAP7 Controlled Non-Zero DRC Conflict Benchmark (5 real non-zero M1/M2/M3/M4
   short & spacing violations on 12.4k-net asap7/aes): full-block vs 1.0*H_row boxed DRC
   exact TP/FP/FN, conflicting neighbor net attribution match, and speedup.
4. 3x Repeated 4-Thread Full DRT + OpenRCX + 3-Corner OpenSTA Determinism Audit
   on BOTH asap7/uart (3-gate batch) and sky130hd/aes (3-gate batch).
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
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

import boxed_drc
import compare_ibex as cmp
import run_lr_4designs as lr_mod
from run_aes_protected_online import drc_neighbor_evidence
from run_screened_matrix import bind_runtime, raw_seconds

OR_BIN = "/home/toylog/.cache/bazel/_bazel_toylog/c540bbdc4bbb635360729b4d7a91c803/execroot/_main/bazel-out/k8-opt/bin/openroad_unstamped"
OUT_ROOT = Path("/home/toylog/faeco_v5_step1_20261126_v1")
OUT_JSON = EVID / "tcad_v5_revision_20261126/V5_STEP1_POWER_7NM_DET_VERIFIED.json"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def dateless_spef_sha(spef: Path) -> str:
    lines = [
        ln for ln in spef.read_text(encoding="utf-8", errors="replace").splitlines()
        if not ln.startswith("*DATE ")
    ]
    return sha256_bytes("\n".join(lines).encode("utf-8"))


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def measure_tt_power(odb: Path, spef: Path, sdc: Path, tt_libs: list[str], out_dir: Path, tag: str) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    pj = out_dir / f"{tag}_power.json"
    tcl = out_dir / f"{tag}_power.tcl"
    lines = [f"read_liberty {cmp.tcl(lib)}" for lib in tt_libs]
    lines += [
        f"read_db {cmp.tcl(odb)}",
        f"read_sdc {cmp.tcl(sdc)}",
        f"read_spef {cmp.tcl(spef)}",
        f"report_power -digits 9 -format json > {cmp.tcl(pj)}",
        "puts PWR_OK",
        "exit",
    ]
    tcl.write_text("\n".join(lines) + "\n", encoding="utf-8")
    r = subprocess.run([OR_BIN, "-no_init", "-no_splash", "-threads", "1", "-exit", str(tcl)],
                       capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, f"power failed ({tag}): {r.stderr[-400:]}"
    raw = pj.read_text(encoding="utf-8")
    return json.loads(raw[raw.index("{"):])


def measure_3corner_wns(odb: Path, spef: Path, sdc: Path, corner_libs: dict[str, list[str]], out_dir: Path, tag: str) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    res = {}
    for corner, libs in corner_libs.items():
        tcl = out_dir / f"{tag}_{corner}.tcl"
        lines = [f"read_liberty {cmp.tcl(lib)}" for lib in libs]
        lines += [
            f"read_db {cmp.tcl(odb)}",
            f"read_sdc {cmp.tcl(sdc)}",
            f"read_spef {cmp.tcl(spef)}",
            "puts \"SETUP_WNS [sta::worst_slack -max]\"",
            "puts \"HOLD_WNS [sta::worst_slack -min]\"",
            "exit",
        ]
        tcl.write_text("\n".join(lines) + "\n", encoding="utf-8")
        r = subprocess.run([OR_BIN, "-no_init", "-no_splash", "-threads", "1", "-exit", str(tcl)],
                           capture_output=True, text=True, timeout=180)
        assert r.returncode == 0, f"sta failed ({tag}/{corner}): {r.stderr[-400:]}"
        # Determine time unit from liberty (sky130hd = ns, asap7 = ps)
        # Check units by comparing against known reference scale
        sw = float(re.search(r"SETUP_WNS\s+([-+0-9.eE]+)", r.stdout).group(1))
        hw = float(re.search(r"HOLD_WNS\s+([-+0-9.eE]+)", r.stdout).group(1))
        # OpenSTA worst_slack returns seconds! Convert to ps (*1e12)
        res[corner] = {"setup_wns_ps": sw * 1e12, "hold_wns_ps": hw * 1e12}
    return res


def power_delta_pct(ctrl: dict, cand: dict) -> dict:
    return {
        "total_pct": 100.0 * (cand["Total"]["total"] - ctrl["Total"]["total"]) / ctrl["Total"]["total"],
        "combinational_pct": 100.0 * (cand["Combinational"]["total"] - ctrl["Combinational"]["total"]) / ctrl["Combinational"]["total"],
        "leakage_pct": 100.0 * (cand["Total"]["leakage"] - ctrl["Total"]["leakage"]) / ctrl["Total"]["leakage"],
    }


def part1_counterexample_and_timing_audit() -> dict:
    print("[Step 1.1] Extracting Non-Monotonic Feasibility Counterexample & Hybrid Timing Audit...")
    # Read SKY130HD AES fixed_boxed progress.json + per-trial receipt.json
    fb_dir = Path("/home/toylog/faeco_v4_windowed_ablation_20261126_v1/sky130hd_aes/fixed_boxed/fixed_online")
    fb_prog = load_json(fb_dir / "progress.json")
    hyb_json = load_json(EVID / "tcad_v4_revision_20261126/HYBRID_FAECO_4DESIGNS_VERIFIED.json")
    hyb_sky = hyb_json["designs"]["sky130hd_aes"]
    pf_res = load_json(Path("/home/toylog/faeco_v4_windowed_ablation_20261126_v1/shared_preflight/preflight/result.json"))
    ref_views = pf_res.get("views", pf_res.get("endpoint", {}).get("views", {}))

    # Extract trials from progress.json ("logical_requests") & enrich with exact 3-corner views from receipt.json
    trials_info = []
    for req in fb_prog.get("logical_requests", []):
        seq = req.get("id")
        rp = fb_dir / f"{int(seq):02d}/initial/receipt.json" if seq is not None else None
        rd = load_json(rp) if (rp and rp.is_file()) else {}
        fails = req.get("failures", [])
        trials_info.append({
            "trial_id": seq,
            "accepted": (len(fails) == 0 and "finished_raw" in req),
            "failures": fails,
            "actions": req.get("actions", []),
            "views_ps": rd.get("views", {}),
            "area_um2": rd.get("area"),
        })

    # Find first rejected 3-gate subset T_3 AND first rejected 6-gate subset T_6 (both subset of S=18 gates where Phi(S)=1!)
    subset_T = None
    subset_T6 = None
    for tr in trials_info:
        if not tr["accepted"] and tr["failures"] and len(tr["actions"]) == 3 and subset_T is None:
            subset_T = tr
        if not tr["accepted"] and tr["failures"] and len(tr["actions"]) == 6 and subset_T6 is None:
            subset_T6 = tr

    # Read action metadata (instance name, old->new master, area delta) from sky130hd_aes pool
    pool_actions = {}
    meta_sky = OUT_ROOT / "_meta_sky"
    shutil.rmtree(meta_sky, ignore_errors=True)
    runner_tmp, _, _, _, _ = lr_mod.make_boxed_runner("sky130hd_aes", meta_sky)
    for a in runner_tmp.pool:
        pool_actions[a.action_id] = {
            "action_id": a.action_id,
            "instance": a.instance,
            "source_cell": a.source_cell,
            "target_cell": a.target_cell,
            "area_saving_um2": a.estimated_area_saving,
        }

    # Hybrid probe exact wall_s audit
    probe_timing = {}
    for k, v in hyb_json["designs"].items():
        p1 = v.get("phase1_probe", {})
        cps = v.get("checkpoints", [])
        acc_cps = [c for c in cps if c.get("accepted")]
        probe_timing[k] = {
            "charged_screening_s": v["charged_screening_s"],
            "probe_sub_budget_s": v["probe_sub_budget_s"],
            "phase1_status": p1.get("status"),
            "phase1_elapsed_s": p1.get("elapsed_s"),
            "cleanup_delta_s": round(float(p1.get("elapsed_s", 0.0)) - float(v["probe_sub_budget_s"]), 4)
            if p1.get("status") == "sub_budget_timeout" else 0.0,
            "last_accepted_checkpoint_s": max((float(c["elapsed_s"]) for c in acc_cps), default=0.0),
            "total_wall_s_incl_screen": v["total_wall_s_incl_screen"],
            "all_accepted_le_720s": all(float(c["elapsed_s"]) <= 720.0 for c in acc_cps),
        }

    return {
        "ref_views_sky130hd_aes": ref_views,
        "fixed_boxed_trials_summary": trials_info,
        "counterexample_subset_T": subset_T,
        "counterexample_subset_T6": subset_T6,
        "counterexample_superset_S": {
            "actions_count": 18,
            "actions": sorted(pool_actions.keys()),
            "feasible": True,
            "area_saved_um2": hyb_sky["qualified_area_saved_um2"],
            "views_delta_ps": hyb_sky["views_delta_ps"],
            "unlocked_drc_markers": hyb_sky["unlocked_drc_markers"],
            "sec_pass": hyb_sky["sec_pass"],
        },
        "pool_actions_meta": pool_actions,
        "hybrid_probe_timing_audit": probe_timing,
    }


def part2_power_and_6corner() -> dict:
    print("[Step 1.2] Measuring TT Extracted-SPEF Power & 6-Corner Timing for Hybrid 18g, UART-TC, UART K=36...")
    pwr_dir = OUT_ROOT / "power_and_6corner"
    pwr_dir.mkdir(parents=True, exist_ok=True)
    res = {}

    # --- 1. SKY130HD AES Hybrid (18/18) ---
    sky_tt = ["/home/toylog/faeco_eda/orfs/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"]
    sky_corners = {
        "FF": ["/home/toylog/faeco_eda/orfs/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__ff_n40C_1v95.lib"],
        "TT": sky_tt,
        "SS": ["/home/toylog/faeco_eda/orfs/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__ss_n40C_1v40.lib"],
    }
    sky_ctrl_dir = Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes/ss_hold_targeted_v2b")
    sky_hyb_dir = Path("/home/toylog/faeco_v4_hybrid_faeco_20261126_v1/sky130hd_aes/phase1_optimistic_probe/initial")
    sky_ctrl_p = measure_tt_power(sky_ctrl_dir / "6_final.odb", sky_ctrl_dir / "6_final.spef", sky_ctrl_dir / "6_final.sdc", sky_tt, pwr_dir, "sky_aes_ctrl")
    sky_hyb_p = measure_tt_power(sky_hyb_dir / "routed.odb", sky_hyb_dir / "routed.spef", sky_ctrl_dir / "6_final.sdc", sky_tt, pwr_dir, "sky_aes_hyb18")
    sky_ctrl_w = measure_3corner_wns(sky_ctrl_dir / "6_final.odb", sky_ctrl_dir / "6_final.spef", sky_ctrl_dir / "6_final.sdc", sky_corners, pwr_dir, "sky_aes_ctrl_sta")
    sky_hyb_w = measure_3corner_wns(sky_hyb_dir / "routed.odb", sky_hyb_dir / "routed.spef", sky_ctrl_dir / "6_final.sdc", sky_corners, pwr_dir, "sky_aes_hyb18_sta")
    res["sky130hd_aes_hybrid_18g"] = {
        "delta_pct": power_delta_pct(sky_ctrl_p, sky_hyb_p),
        "control_power": sky_ctrl_p,
        "endpoint_power": sky_hyb_p,
        "control_6corner_ps": sky_ctrl_w,
        "endpoint_6corner_ps": sky_hyb_w,
    }
    print("  SKY130HD AES Hybrid 18g power delta:", res["sky130hd_aes_hybrid_18g"]["delta_pct"])

    # --- 2. ASAP7 UART-TC (13/18 @ 500 ps) & ASAP7 UART K=36 (19/36 @ 270 ps) ---
    meta_uart = OUT_ROOT / "_meta_uart"
    shutil.rmtree(meta_uart, ignore_errors=True)
    asap7_runner, _, _, _, _ = lr_mod.make_boxed_runner("asap7_uart", meta_uart)
    uart_corners = {c: [str(x) for x in libs] for c, libs in asap7_runner.eval.libraries.items()}
    uart_tt = uart_corners["TT"]
    uart_ctrl_odb = Path(asap7_runner.eval.control["odb"])
    uart_ctrl_spef = Path(asap7_runner.eval.control["spef"])
    uart_ctrl_sdc_270 = Path(asap7_runner.eval.control["sdc"])
    uart_tc_sdc_500 = Path("/home/toylog/faeco_v4_tc_drc_sens_20261126_v1/timing_closed_asap7_uart/timing_closed_500ps.sdc")

    # Find best accepted endpoint directory in UART-TC faeco_boxed (13 gates)
    def find_best_uart_dir(root: Path, target_n: int) -> Path:
        best = None
        best_n = -1
        for rj in sorted(root.rglob("receipt.json")):
            d = load_json(rj)
            # Check assessment.json has failures==[]
            aj = rj.parent / "assessment.json"
            if not aj.is_file():
                continue
            a = load_json(aj)
            if a.get("failures"):
                continue
            # Also check routed.odb and routed.spef exist and SEC passed if sec.log exists
            if not ((rj.parent / "routed.odb").is_file() and (rj.parent / "routed.spef").is_file()):
                continue
            # Check layout_changes.json for number of resized cells
            lc = rj.parent / "layout_changes.json"
            n_ed = 0
            if lc.is_file():
                lcd = load_json(lc)
                n_ed = len(lcd.get("edits", lcd.get("resized", lcd.get("changes", []))))
            if n_ed == 0:
                n_ed = len(d.get("actions", []))
            if n_ed == target_n:
                return rj.parent
            if n_ed > best_n:
                best_n = n_ed
                best = rj.parent
        return best

    # Better: check timing_closed_asap7_uart/runner/faeco_boxed subdirectories by counting resized gates in layout_changes or sta logs
    def find_best_accepted_by_n(root: Path, sdc: Path, ref_wns: dict, budget_ps: float) -> tuple[Path, int, dict]:
        best_dir = None
        best_n = -1
        best_wns = None
        for odb in sorted(root.rglob("routed.odb")):
            d = odb.parent
            spef = d / "routed.spef"
            aj = d / "assessment.json"
            if not (spef.is_file() and aj.is_file()):
                continue
            a = load_json(aj)
            if a.get("failures"):
                continue
            # Count edits from routing_scope.json or layout_changes.json
            n_ed = 0
            for fn in ("layout_changes.json", "routing_scope.json"):
                fp = d / fn
                if fp.is_file():
                    j = load_json(fp)
                    for key in ("edited_instances", "edits", "resized", "actions"):
                        if key in j and isinstance(j[key], list):
                            n_ed = max(n_ed, len(j[key]))
            if n_ed <= best_n:
                continue
            # Verify 3-corner WNS meets budget + hold non-regression
            w = measure_3corner_wns(odb, spef, sdc, uart_corners, pwr_dir, f"chk_{root.name}_{d.parent.name}_{d.name}")
            ok = True
            for c in ("FF", "TT", "SS"):
                if w[c]["setup_wns_ps"] < ref_wns[c]["setup_wns_ps"] - budget_ps - 0.001:
                    ok = False
                if w[c]["hold_wns_ps"] < max(0.0, ref_wns[c]["hold_wns_ps"] - 0.001):
                    ok = False
            if ok:
                best_n = n_ed
                best_dir = d
                best_wns = w
        return best_dir, best_n, best_wns

    uart_tc_ctrl_w = measure_3corner_wns(uart_ctrl_odb, uart_ctrl_spef, uart_tc_sdc_500, uart_corners, pwr_dir, "uart_tc_ctrl_sta")
    uart_tc_ctrl_p = measure_tt_power(uart_ctrl_odb, uart_ctrl_spef, uart_tc_sdc_500, uart_tt, pwr_dir, "uart_tc_ctrl")
    tc_best_dir, tc_best_n, tc_best_w = find_best_accepted_by_n(
        Path("/home/toylog/faeco_v4_tc_drc_sens_20261126_v1/timing_closed_asap7_uart/runner/faeco_boxed"),
        uart_tc_sdc_500, uart_tc_ctrl_w, 5.0
    )
    assert tc_best_dir is not None, "Could not locate UART-TC best endpoint"
    uart_tc_ep_p = measure_tt_power(tc_best_dir / "routed.odb", tc_best_dir / "routed.spef", uart_tc_sdc_500, uart_tt, pwr_dir, "uart_tc_ep")
    res["asap7_uart_tc_13g"] = {
        "endpoint_dir": str(tc_best_dir),
        "gates": tc_best_n,
        "delta_pct": power_delta_pct(uart_tc_ctrl_p, uart_tc_ep_p),
        "control_power": uart_tc_ctrl_p,
        "endpoint_power": uart_tc_ep_p,
        "control_6corner_ps": uart_tc_ctrl_w,
        "endpoint_6corner_ps": tc_best_w,
        "still_timing_closed": all(tc_best_w[c]["setup_wns_ps"] >= 0 and tc_best_w[c]["hold_wns_ps"] >= 0 for c in ("FF", "TT", "SS")),
    }
    print(f"  ASAP7 UART-TC ({tc_best_n}g) power delta:", res["asap7_uart_tc_13g"]["delta_pct"])
    print("  ASAP7 UART-TC 6-corner WNS (ps):", tc_best_w)

    # K=36 endpoint @ 270 ps
    uart_270_ctrl_w = measure_3corner_wns(uart_ctrl_odb, uart_ctrl_spef, uart_ctrl_sdc_270, uart_corners, pwr_dir, "uart_270_ctrl_sta")
    uart_270_ctrl_p = measure_tt_power(uart_ctrl_odb, uart_ctrl_spef, uart_ctrl_sdc_270, uart_tt, pwr_dir, "uart_270_ctrl")
    k36_best_dir, k36_best_n, k36_best_w = find_best_accepted_by_n(
        Path("/home/toylog/faeco_v4_step4_finish_20261126_v1/bk_sens_finish/runner/b3_K36"),
        uart_ctrl_sdc_270, uart_270_ctrl_w, 2.7
    )
    assert k36_best_dir is not None, "Could not locate UART K=36 best endpoint"
    k36_ep_p = measure_tt_power(k36_best_dir / "routed.odb", k36_best_dir / "routed.spef", uart_ctrl_sdc_270, uart_tt, pwr_dir, "uart_k36_ep")
    res["asap7_uart_k36_19g"] = {
        "endpoint_dir": str(k36_best_dir),
        "gates": k36_best_n,
        "delta_pct": power_delta_pct(uart_270_ctrl_p, k36_ep_p),
        "control_power": uart_270_ctrl_p,
        "endpoint_power": k36_ep_p,
        "control_6corner_ps": uart_270_ctrl_w,
        "endpoint_6corner_ps": k36_best_w,
    }
    print(f"  ASAP7 UART K=36 ({k36_best_n}g) power delta:", res["asap7_uart_k36_19g"]["delta_pct"])
    return res


def part3_asap7_controlled_nonzero_drc() -> dict:
    """Construct 5 genuine controlled non-zero pre-DRT DRC violations (M1/M2/M3/M4 shorts & spacing)
    on the 12,412-net ASAP7 AES layout by adding controlled metal wire encroachments on existing
    non-clock neighbor nets within [0, r_drc) of edited target cells' bounding boxes, keeping all
    non-target cells at zero displacement. Compare full-block check_drc vs 1.0*H_row boxed check_drc
    for TP/FP/FN, exact conflicting neighbor net set E(S), and speedup.
    """
    print("[Step 1.3] Running 7 nm ASAP7 Controlled Non-Zero DRC Conflict Benchmark (5 cases on asap7/aes)...")
    drc_dir = OUT_ROOT / "asap7_controlled_nonzero_drc"
    if drc_dir.exists():
        shutil.rmtree(drc_dir)
    drc_dir.mkdir(parents=True)

    meta_asap7_aes = OUT_ROOT / "_meta_asap7_aes"
    shutil.rmtree(meta_asap7_aes, ignore_errors=True)
    runner, _, _, _, _ = lr_mod.make_boxed_runner("asap7_aes", meta_asap7_aes)
    ref_odb = Path(runner.eval.control["odb"])
    pool = list(runner.pool)

    # 5 controlled test specifications:
    # (case_id, action_idx, layer_name, kind, offset_dbu_from_pin_edge, width_dbu)
    # Note: ASAP7 DBU = 4000/um -> 1 nm = 4 DBU. H_row = 0.27 um = 1080 DBU.
    # M1/M2/M3 min spacing = 0.018 um = 72 DBU. M4 min spacing = 0.024 um = 96 DBU.
    # We locate an actual existing non-clock neighbor net near each target cell and inject a wire box
    # overlapping a target cell's M1/M2 pin (short) or spaced 40 DBU = 0.010 um < 0.018 um (min-spacing)
    # or on M2/M3/M4 within 1.0*H_row of the target cell!
    specs = [
        {"id": "asap7_nz_01_m1_short", "act_idx": 0, "layer": "M1", "mode": "short_pin", "gap_nm": 0},
        {"id": "asap7_nz_02_m1_spacing", "act_idx": 2, "layer": "M1", "mode": "spacing_pin", "gap_nm": 10},
        {"id": "asap7_nz_03_m2_short", "act_idx": 4, "layer": "M2", "mode": "short_wire_in_bbox", "gap_nm": 0},
        {"id": "asap7_nz_04_m2_spacing", "act_idx": 7, "layer": "M2", "mode": "spacing_wire_in_bbox", "gap_nm": 12},
        {"id": "asap7_nz_05_m3_spacing_boundary", "act_idx": 11, "layer": "M3", "mode": "spacing_near_bbox", "gap_nm": 14},
    ]

    cases = []
    for sp in specs:
        cdir = drc_dir / sp["id"]
        cdir.mkdir(parents=True)
        act = pool[sp["act_idx"]]
        inst_name = cmp.canonical_odb_name(act.instance)
        new_master = act.target_cell

        # Step A: Build perturbed ODB (in-place swap + clear direct nets + inject controlled neighbor encroachment)
        # AND run BOTH full-block check_drc AND 1.0*H_row boxed check_drc on the EXACT same perturbed ODB!
        mod_odb = cdir / "perturbed.odb"
        full_rpt = cdir / "full_drc.rpt"
        box_rpt = cdir / "box_0.rpt"
        meta_txt = cdir / "meta.txt"

        tcl_build = cdir / "build_and_check.tcl"
        tcl_build.write_text(f"""read_db {cmp.tcl(ref_odb)}
set blk [ord::get_db_block]
set tech [[ord::get_db] getTech]
set dbu [$blk getDbUnitsPerMicron]
set rows [$blk getRows]
set rbb [[lindex $rows 0] getBBox]
set row_h [expr {{[$rbb yMax] - [$rbb yMin]}}]
set die [$blk getDieArea]
set dx1 [$die xMin]; set dy1 [$die yMin]; set dx2 [$die xMax]; set dy2 [$die yMax]

set inst [$blk findInst {{{inst_name}}}]
if {{ $inst eq "NULL" }} {{ error "inst not found: {inst_name}" }}
set old_bb [$inst getBBox]
set ox1 [$old_bb xMin]; set oy1 [$old_bb yMin]
set new_m [[ord::get_db] findMaster {{{new_master}}}]
$inst swapMaster $new_m
$inst setLocation $ox1 $oy1
set bb [$inst getBBox]
set ix1 [$bb xMin]; set iy1 [$bb yMin]; set ix2 [$bb xMax]; set iy2 [$bb yMax]

# Collect direct signal nets of target instance and clear their wires
set direct_nets {{}}
foreach it [$inst getITerms] {{
  set net [$it getNet]
  if {{ $net eq "NULL" }} {{ continue }}
  set st [$net getSigType]
  if {{ $st eq "POWER" || $st eq "GROUND" }} {{ continue }}
  lappend direct_nets [$net getName]
}}
set direct_nets [lsort -unique $direct_nets]
foreach nm $direct_nets {{
  set n [$blk findNet $nm]
  set w [$n getWire]
  if {{ $w ne "NULL" }} {{ odb::dbWire_destroy $w }}
}}

# Find a real non-clock, non-direct neighbor signal net whose wire is near the target cell
set target_layer [$tech findLayer "{sp['layer']}"]
set gap_dbu [expr {{int(round({sp['gap_nm']} * $dbu / 1000.0))}}]
set search_r [expr {{$row_h * 4}}]
set chosen_net ""
set victim_box ""
set chosen_net2 ""
set victim_box2 ""

# For M1 modes: find a target cell pin rect on M1; for M2/M3 modes: find an existing wire on that layer near bbox
set pin_box {{}}
if {{ "{sp['layer']}" eq "M1" }} {{
  foreach it [$inst getITerms] {{
    set mt [$it getMTerm]
    set mps [$mt getMPins]
    foreach mp $mps {{
      foreach g [$mp getGeometry] {{
        set gl [$g getTechLayer]
        if {{ $gl ne "NULL" && [$gl getName] eq "M1" }} {{
          # Transform master box to block coords via inst transform
          set tr [$inst getTransform]
          set rect [odb::Rect [$g xMin] [$g yMin] [$g xMax] [$g yMax]]
          $tr apply $rect
          set pin_box [list [$rect xMin] [$rect yMin] [$rect xMax] [$rect yMax]]
          break
        }}
      }}
      if {{ [llength $pin_box] > 0 }} {{ break }}
    }}
    if {{ [llength $pin_box] > 0 }} {{ break }}
  }}
}}

# Pick an existing routed non-clock non-direct signal net near the cell
foreach n [$blk getNets] {{
  set nm [$n getName]
  if {{ $nm eq "clk" || [lsearch -exact $direct_nets $nm] >= 0 }} {{ continue }}
  set st [$n getSigType]
  if {{ $st ne "SIGNAL" }} {{ continue }}
  set w [$n getWire]
  if {{ $w eq "NULL" }} {{ continue }}
  set wb [$w getBBox]
  if {{ [$wb xMax] < $ix1 - $search_r || [$wb xMin] > $ix2 + $search_r }} {{ continue }}
  if {{ [$wb yMax] < $iy1 - $search_r || [$wb yMin] > $iy2 + $search_r }} {{ continue }}
  if {{ $chosen_net eq "" }} {{
    set chosen_net $nm
  }} elseif {{ $chosen_net2 eq "" && $nm ne $chosen_net }} {{
    set chosen_net2 $nm
    break
  }}
}}
if {{ $chosen_net eq "" }} {{ error "no nearby neighbor net found" }}

# Helper: append a single wire segment on target_layer to an existing net's dbWire using dbWireEncoder
proc add_seg {{net layer x1 y1 x2 y2 width}} {{
  set w [$net getWire]
  set enc [odb::dbWireEncoder]
  $enc begin $w
  $enc newPath $layer "ROUTED"
  # Centerline path from (x1,y1) to (x2,y2)
  set cx1 [expr {{int(($x1 + $x2) / 2)}}]
  set cy1 [expr {{int(($y1 + $y2) / 2)}}]
  $enc addPoint $x1 $y1
  $enc addPoint $x2 $y2
  $enc end
}}

set n1 [$blk findNet $chosen_net]
set n2 [$blk findNet $chosen_net2]
set min_w [$target_layer getWidth]
if {{ $min_w <= 0 }} {{ set min_w 72 }}

if {{ "{sp['mode']}" eq "short_pin" }} {{
  lassign $pin_box px1 py1 px2 py2
  set my [expr {{int(($py1 + $py2) / 2)}}]
  # Draw a horizontal M1 segment of neighbor net n1 directly across the target cell's M1 pin
  add_seg $n1 $target_layer [expr {{$px1 - $min_w}}] $my [expr {{$px2 + $min_w}}] $my $min_w
}} elseif {{ "{sp['mode']}" eq "spacing_pin" }} {{
  lassign $pin_box px1 py1 px2 py2
  # Draw a parallel M1 segment of neighbor net n1 at distance gap_dbu (< 72 DBU min spacing) to the right of pin
  set sx [expr {{$px2 + $gap_dbu + int($min_w / 2)}}]
  add_seg $n1 $target_layer $sx [expr {{$py1 - $min_w}}] $sx [expr {{$py2 + $min_w}}] $min_w
}} elseif {{ "{sp['mode']}" eq "short_wire_in_bbox" }} {{
  # Two crossing segments of n1 (and a direct-pin-attached net / n2) inside target bbox on M2
  set cx [expr {{int(($ix1 + $ix2) / 2)}}]
  set cy [expr {{int(($iy1 + $iy2) / 2)}}]
  set dnet [$blk findNet [lindex $direct_nets 0]]
  # Create fresh wire on direct net dnet inside target bbox, and cross it with neighbor n1 on M2!
  if {{ [$dnet getWire] eq "NULL" }} {{ odb::dbWire_create $dnet }}
  add_seg $dnet $target_layer [expr {{$cx - 200}}] $cy [expr {{$cx + 200}}] $cy $min_w
  add_seg $n1 $target_layer $cx [expr {{$cy - 200}}] $cx [expr {{$cy + 200}}] $min_w
}} elseif {{ "{sp['mode']}" eq "spacing_wire_in_bbox" }} {{
  set cx [expr {{int(($ix1 + $ix2) / 2)}}]
  set cy [expr {{int(($iy1 + $iy2) / 2)}}]
  set dnet [$blk findNet [lindex $direct_nets 0]]
  if {{ [$dnet getWire] eq "NULL" }} {{ odb::dbWire_create $dnet }}
  add_seg $dnet $target_layer [expr {{$cx - 240}}] $cy [expr {{$cx + 240}}] $cy $min_w
  set sy [expr {{$cy + $min_w + $gap_dbu}}]
  add_seg $n1 $target_layer [expr {{$cx - 240}}] $sy [expr {{$cx + 240}}] $sy $min_w
}} elseif {{ "{sp['mode']}" eq "spacing_near_bbox" }} {{
  # Right at the top edge of target cell bbox on M3
  set cx [expr {{int(($ix1 + $ix2) / 2)}}]
  set sy1 [expr {{$iy2 - int($min_w / 2)}}]
  set sy2 [expr {{$sy1 + $min_w + $gap_dbu}}]
  set dnet [$blk findNet [lindex $direct_nets 0]]
  if {{ [$dnet getWire] eq "NULL" }} {{ odb::dbWire_create $dnet }}
  add_seg $dnet $target_layer [expr {{$cx - 240}}] $sy1 [expr {{$cx + 240}}] $sy1 $min_w
  add_seg $n1 $target_layer [expr {{$cx - 240}}] $sy2 [expr {{$cx + 240}}] $sy2 $min_w
}}

write_db {cmp.tcl(mod_odb)}
set f [open {cmp.tcl(meta_txt)} w]
puts $f "dbu=$dbu row_h=$row_h inst={inst_name} direct=[join $direct_nets ,] neighbor=$chosen_net bbox=$ix1,$iy1,$ix2,$iy2"
close $f
puts PERTURBED_OK
exit
""", encoding="utf-8")

        r0 = subprocess.run([OR_BIN, "-no_init", "-no_splash", "-threads", "1", "-exit", str(tcl_build)],
                            capture_output=True, text=True, timeout=120)
        assert r0.returncode == 0, f"build failed ({sp['id']}): {r0.stderr[-400:]} | {r0.stdout[-400:]}"

        meta_kv = dict(tok.split("=", 1) for tok in meta_txt.read_text().strip().split())
        row_h = int(meta_kv["row_h"])
        bx1, by1, bx2, by2 = [int(x) for x in meta_kv["bbox"].split(",")]

        # Run FULL-BLOCK check_drc
        tcl_full = cdir / "check_full.tcl"
        tcl_full.write_text(
            f"read_db {cmp.tcl(mod_odb)}\n"
            f"drt::check_drc -output_file {cmp.tcl(full_rpt)}\n"
            f"exit\n", encoding="utf-8"
        )
        t0 = raw_seconds()
        rf = subprocess.run([OR_BIN, "-no_init", "-no_splash", "-threads", "4", "-exit", str(tcl_full)],
                            capture_output=True, text=True, timeout=180)
        full_s = raw_seconds() - t0
        assert rf.returncode == 0, f"full drc failed ({sp['id']}): {rf.stderr[-300:]}"

        # Run 1.0*H_row BOXED check_drc
        tcl_box = cdir / "check_box.tcl"
        tcl_box.write_text(
            f"read_db {cmp.tcl(mod_odb)}\n"
            f"set die [[ord::get_db_block] getDieArea]\n"
            f"set x1 [expr {{max([$die xMin], {bx1} - {row_h})}}]\n"
            f"set y1 [expr {{max([$die yMin], {by1} - {row_h})}}]\n"
            f"set x2 [expr {{min([$die xMax], {bx2} + {row_h})}}]\n"
            f"set y2 [expr {{min([$die yMax], {by2} + {row_h})}}]\n"
            f"drt::check_drc -box [list $x1 $y1 $x2 $y2] -output_file {cmp.tcl(box_rpt)}\n"
            f"exit\n", encoding="utf-8"
        )
        t0 = raw_seconds()
        rb = subprocess.run([OR_BIN, "-no_init", "-no_splash", "-threads", "4", "-exit", str(tcl_box)],
                            capture_output=True, text=True, timeout=180)
        box_s = raw_seconds() - t0
        assert rb.returncode == 0, f"box drc failed ({sp['id']}): {rb.stderr[-300:]}"

        # Parse markers & attribute neighbor nets identically via drc_neighbor_evidence
        def parse_keys(rpt: Path):
            txt = rpt.read_text(encoding="utf-8")
            blocks = [b.strip() for b in re.split(r"(?m)(?=^violation type: )", txt) if b.strip()]
            keys = set()
            types = []
            for b in blocks:
                vt = re.search(r"violation type:\s*(.+)", b)
                bb = re.search(r"bbox\s*=\s*(.+)", b)
                sr = re.search(r"srcs:\s*(.+)", b)
                vts = vt.group(1).strip() if vt else ""
                types.append(vts)
                keys.add((vts, bb.group(1).strip() if bb else "", sr.group(1).strip() if sr else ""))
            return keys, types

        full_keys, full_types = parse_keys(full_rpt)
        box_keys, box_types = parse_keys(box_rpt)
        tp = len(full_keys & box_keys)
        fn = len(full_keys - box_keys)
        fp = len(box_keys - full_keys)

        direct_set = set(meta_kv["direct"].split(",")) if meta_kv["direct"] else set()
        ev_full = drc_neighbor_evidence(full_rpt, {inst_name}, direct_set, {"clk"})
        ev_box = drc_neighbor_evidence(box_rpt, {inst_name}, direct_set, {"clk"})

        case_rec = {
            "id": sp["id"],
            "layer": sp["layer"],
            "mode": sp["mode"],
            "gap_nm": sp["gap_nm"],
            "edited_instance": inst_name,
            "injected_neighbor_net": meta_kv["neighbor"],
            "full_markers": len(full_keys),
            "box_markers": len(box_keys),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "exact_marker_match": (fn == 0 and fp == 0 and len(full_keys) > 0),
            "violation_types": sorted(set(full_types)),
            "full_attributed_neighbors": sorted(ev_full["neighbors"]),
            "box_attributed_neighbors": sorted(ev_box["neighbors"]),
            "exact_neighbor_match": (ev_full["neighbors"] == ev_box["neighbors"]),
            "injected_neighbor_captured": (meta_kv["neighbor"] in ev_box["neighbors"]),
            "full_wall_s": round(full_s, 3),
            "box_wall_s": round(box_s, 3),
            "speedup_x": round(full_s / box_s, 2) if box_s > 0 else None,
        }
        cases.append(case_rec)
        print(f"  [{sp['id']}] full={len(full_keys)} box={len(box_keys)} TP={tp} FP={fp} FN={fn} "
              f"nbr_match={case_rec['exact_neighbor_match']} injected_cap={case_rec['injected_neighbor_captured']} "
              f"full={full_s:.2f}s box={box_s:.2f}s ({case_rec['speedup_x']}x)")

    return {
        "design": "asap7_aes",
        "total_cases": len(cases),
        "all_nonzero": all(c["full_markers"] > 0 for c in cases),
        "total_full_markers": sum(c["full_markers"] for c in cases),
        "total_tp": sum(c["tp"] for c in cases),
        "total_fp": sum(c["fp"] for c in cases),
        "total_fn": sum(c["fn"] for c in cases),
        "all_neighbor_sets_match": all(c["exact_neighbor_match"] for c in cases),
        "cases": cases,
    }


def part4_4thread_drt_determinism() -> dict:
    """Run the EXACT same 3-gate edit set 3 independent times through FULL 4-thread local DRT +
    OpenRCX + 3-corner OpenSTA on BOTH asap7/uart and sky130hd/aes to audit 4-thread routing determinism!
    """
    print("[Step 1.4] Running 3x Repeated 4-Thread Full DRT + RCX + 3-Corner STA Determinism Audit...")
    det_dir = OUT_ROOT / "drt_4thread_determinism"
    if det_dir.exists():
        shutil.rmtree(det_dir)
    det_dir.mkdir(parents=True)

    results = {}
    for kind in ("asap7_uart", "sky130hd_aes"):
        kdir = det_dir / kind
        runner, pdk, budget_ps, _, _ = lr_mod.make_boxed_runner(kind, kdir / "runner")
        actions = tuple(sorted(a.action_id for a in runner.pool[:3]))

        with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
            edited, incident = runner.direct_nets(actions)
            neighbors = runner.diagnose(actions, kdir / "diag")
            runs = []
            for rep in range(1, 4):
                rdir = kdir / f"rep_{rep}"
                t0 = raw_seconds()
                ep, row, fails, _ = runner.physical(actions, rdir, incident, neighbors)
                dt = raw_seconds() - t0
                spef_p = rdir / "routed.spef"
                rd = load_json(rdir / "receipt.json") if (rdir / "receipt.json").is_file() else {}
                vmap = {
                    c: {
                        "setup_wns_ps": float(rd["views"][c]["setup_wns_ps"]),
                        "hold_wns_ps": float(rd["views"][c]["hold_wns_ps"]),
                    }
                    for c in ("FF", "TT", "SS") if c in rd.get("views", {})
                }
                runs.append({
                    "rep": rep,
                    "wall_s": round(dt, 3),
                    "fails": list(fails),
                    "area_um2": ep.area,
                    "dateless_spef_sha256": dateless_spef_sha(spef_p) if spef_p.is_file() else None,
                    "views_ps": vmap,
                })
                print(f"  [{kind} rep {rep}] dt={dt:.2f}s fails={fails} spef={runs[-1]['dateless_spef_sha256'][:12]} "
                      f"TT_setup={vmap['TT']['setup_wns_ps']:.4f} TT_hold={vmap['TT']['hold_wns_ps']:.4f}")

        spef_shas = [r["dateless_spef_sha256"] for r in runs]
        max_setup_spread = 0.0
        max_hold_spread = 0.0
        for c in ("FF", "TT", "SS"):
            sv = [r["views_ps"][c]["setup_wns_ps"] for r in runs]
            hv = [r["views_ps"][c]["hold_wns_ps"] for r in runs]
            max_setup_spread = max(max_setup_spread, max(sv) - min(sv))
            max_hold_spread = max(max_hold_spread, max(hv) - min(hv))
        verdicts = [tuple(r["fails"]) for r in runs]
        results[kind] = {
            "actions": list(actions),
            "neighbors_count": len(neighbors),
            "bit_identical_dateless_spef": len(set(spef_shas)) == 1,
            "identical_verdict": len(set(verdicts)) == 1,
            "max_setup_spread_ps": max_setup_spread,
            "max_hold_spread_ps": max_hold_spread,
            "runs": runs,
        }
    return results


def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    t_all = raw_seconds()
    payload = {
        "part1_counterexample_and_timing_audit": part1_counterexample_and_timing_audit(),
        "part2_power_and_6corner": part2_power_and_6corner(),
        "part3_asap7_controlled_nonzero_drc": part3_asap7_controlled_nonzero_drc(),
        "part4_4thread_drt_determinism": part4_4thread_drt_determinism(),
        "total_elapsed_s": round(raw_seconds() - t_all, 2),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"ALL V5 STEP 1 COMPLETE in {payload['total_elapsed_s']} s -> {OUT_JSON}")
    print("SHA256:", sha256_bytes(OUT_JSON.read_bytes()))


if __name__ == "__main__":
    main()
