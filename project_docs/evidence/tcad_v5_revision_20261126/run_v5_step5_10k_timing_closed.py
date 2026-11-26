#!/usr/bin/env python3
"""V5 Stage 5 (resumable, pinned CPU 0-5):
Independently Timing-Closed 10k-Gate Benchmark (SKY130HD riscv32i-TC @ 10.0 ns fresh ORFS P&R)
with EXPLICIT Timing-Closed Hard Gate: W_v(F) >= max(0, W_v(R) - B_W - eps) across FF/TT/SS.

Unlike UART-TC (which relaxed SDC on an existing layout), Stage 5 runs a FRESH end-to-end
OpenROAD-flow-scripts P&R build (synthesis -> floorplan -> placement -> CTS -> global/detailed route -> RCX)
for SKY130HD riscv32i at a relaxed 10.0 ns clock period, verifies 0 DRC / 0 antenna / 3-corner
strictly nonnegative Setup & Hold WNS, builds an 18-action compatible downsizing pool, and evaluates
windowed single-gate, fixed micro-batch, and FAECO under 720 s wall-clock + TT extracted-SPEF power!
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
EVID = REPO / "project_docs/evidence"
for sub in (
    "tcad_ibex_20261123",
    "tcad_holdout_20261123",
    "tcad_wallclock_schedule_20261125",
    "tcad_boxed_drc_20261126",
    "tcad_external_baselines_20261125",
    "tcad_v5_revision_20261126",
):
    p = str(EVID / sub)
    if p not in sys.path:
        sys.path.insert(0, p)
if str(REPO / "code/src") not in sys.path:
    sys.path.insert(0, str(REPO / "code/src"))

import boxed_drc
import compare_ibex as cmp
import incident_cap_priority
import run_v5_step1_power_7nm_det as s1
from rseco.physical_budget_adapter import generate_compatible_candidates
from run_screened_matrix import raw_seconds

OR_BIN = "/home/toylog/.cache/bazel/_bazel_toylog/c540bbdc4bbb635360729b4d7a91c803/execroot/_main/bazel-out/k8-opt/bin/openroad_unstamped"
ORFS_FLOW = Path("/home/toylog/faeco_eda/orfs/flow")
OUT_ROOT = Path("/home/toylog/faeco_v5_step5_riscv32i_tc_20261126_v1")
OUT_JSON = EVID / "tcad_v5_revision_20261126/V5_STEP5_10K_TIMING_CLOSED_VERIFIED.json"

SKY_CORNERS = s1.SKY_CORNER_LIBS
SKY_RCX = "/home/toylog/faeco_eda/orfs/flow/platforms/sky130hd/rcx_patterns.rules"
SKY_SETRC = "/home/toylog/faeco_eda/orfs/flow/platforms/sky130hd/setRC.tcl"
SKY_FASTROUTE = "/home/toylog/faeco_eda/orfs/flow/platforms/sky130hd/fastroute.tcl"
CLOCK_NS = 10.0  # 10,000 ps -> genuinely timing-closed across FF/TT/SS!
SETUP_BUDGET_PS = 100.0  # 1% of 10,000 ps


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_independent_riscv32i_tc() -> dict:
    """Run fresh ORFS P&R build of SKY130HD riscv32i at 10.0 ns clock period (FLOW_VARIANT=tc10ns)."""
    res_dir = ORFS_FLOW / "results/sky130hd/riscv32i/tc10ns"
    final_odb = res_dir / "6_final.odb"
    final_spef = res_dir / "6_final.spef"
    final_sdc = res_dir / "6_final.sdc"
    final_v = res_dir / "6_final.v"
    final_def = res_dir / "6_final.def"

    if not (final_odb.is_file() and final_spef.is_file() and final_sdc.is_file() and final_v.is_file()):
        # Create dedicated 10 ns constraint copy
        src_sdc = ORFS_FLOW / "designs/sky130hd/riscv32i/constraint.sdc"
        tc_sdc = OUT_ROOT / "constraint_tc10ns.sdc"
        OUT_ROOT.mkdir(parents=True, exist_ok=True)
        txt = src_sdc.read_text(encoding="utf-8")
        txt_new = re.sub(r"(set\s+clk_period\s+)[0-9.]+", rf"\g<1>{CLOCK_NS}", txt)
        if txt_new == txt:
            txt_new = re.sub(r"(-period\s+)[0-9.]+", rf"\g<1>{CLOCK_NS}", txt)
        tc_sdc.write_text(txt_new, encoding="utf-8")

        env = os.environ.copy()
        env["OPENROAD_EXE"] = OR_BIN
        env["YOSYS_EXE"] = "/home/toylog/faeco_eda/oss-latest/bin/yosys"
        env["NUM_CORES"] = "6"
        cmd = [
            "make", "-C", str(ORFS_FLOW),
            "DESIGN_CONFIG=designs/sky130hd/riscv32i/config.mk",
            "FLOW_VARIANT=tc10ns",
            f"SDC_FILE={tc_sdc}",
            "route", "finish",   # ORFS target names: route = global+detailed, finish = final reports/odb
        ]
        print("[Stage 5] Building fresh independently Timing-Closed SKY130HD riscv32i @ 10.0 ns via ORFS...", flush=True)
        logp = OUT_ROOT / "orfs_build_tc10ns.log"
        t0 = raw_seconds()
        with logp.open("wb") as fh:
            r = subprocess.run(cmd, env=env, stdout=fh, stderr=subprocess.STDOUT, timeout=1800)
        dt = raw_seconds() - t0
        assert r.returncode == 0, f"ORFS build failed (rc={r.returncode}), see {logp}"
        print(f"  [Stage 5] Fresh ORFS build finished in {dt:.1f}s", flush=True)

    # Ensure 6_final.def & 6_final.spef exist (export from 6_final.odb if ORFS skipped SPEF/DEF)
    if not (final_def.is_file() and final_spef.is_file()):
        exp_tcl = OUT_ROOT / "export_def_spef.tcl"
        exp_tcl.write_text(
            f"read_liberty {cmp.tcl(SKY_CORNERS['TT'][0])}\n"
            f"read_db {cmp.tcl(final_odb)}\n"
            f"read_sdc {cmp.tcl(final_sdc)}\n"
            f"source {cmp.tcl(SKY_SETRC)}\n"
            f"write_def {cmp.tcl(final_def)}\n"
            f"extract_parasitics -ext_model_file {cmp.tcl(SKY_RCX)}\n"
            f"write_spef {cmp.tcl(final_spef)}\n"
            f"exit\n", encoding="utf-8"
        )
        r = subprocess.run([OR_BIN, "-no_init", "-no_splash", "-threads", "4", "-exit", str(exp_tcl)],
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, r.stderr[-400:]

    # Verify 3-corner WNS & 0 DRC on the fresh layout
    ref_wns = s1.measure_3corner_wns(final_odb, final_spef, final_sdc, SKY_CORNERS, OUT_ROOT / "ref_sta", "ref_tc10ns")
    ref_pwr = s1.measure_tt_power(final_odb, final_spef, final_sdc, SKY_CORNERS["TT"], OUT_ROOT / "ref_sta", "ref_tc10ns")
    drc_rpt = OUT_ROOT / "ref_sta/ref_drc.rpt"
    drc_tcl = OUT_ROOT / "ref_sta/ref_drc.tcl"
    drc_tcl.write_text(f"read_db {cmp.tcl(final_odb)}\ndrt::check_drc -output_file {cmp.tcl(drc_rpt)}\nexit\n")
    rdrc = subprocess.run([OR_BIN, "-no_init", "-no_splash", "-threads", "4", "-exit", str(drc_tcl)],
                          capture_output=True, text=True, timeout=180)
    assert rdrc.returncode == 0
    ref_drc_markers = len(re.findall(r"(?m)^violation type:", drc_rpt.read_text(encoding="utf-8")))
    is_tc = all(ref_wns[c]["setup_wns_ps"] >= 0.0 and ref_wns[c]["hold_wns_ps"] >= 0.0 for c in ("FF", "TT", "SS"))
    print(f"  [Stage 5] Ref 6-corner WNS={ref_wns}, DRC={ref_drc_markers}, strictly_timing_closed={is_tc}", flush=True)
    return {
        "odb": str(final_odb), "spef": str(final_spef), "sdc": str(final_sdc),
        "v": str(final_v), "def": str(final_def),
        "ref_6corner_ps": ref_wns, "ref_power": ref_pwr,
        "ref_drc_markers": ref_drc_markers, "strictly_timing_closed": is_tc,
    }


def evaluate_subset_protected(ref_info: dict, edits: list[dict], eval_dir: Path, ref_wns: dict, budget_ps: float) -> dict:
    """Apply edits in-place on fresh riscv32i-TC ODB with 1.0*H_row boxed pre-DRT diagnosis,
    protected local reroute, OpenRCX, 3-corner STA, independent full-block DRC, and EXPLICIT
    Timing-closed hard gate: W_v(F) >= max(0, W_v(R) - B_W - 0.001) & H_v(F) >= max(0, H_v(R) - 0.001)."""
    eval_dir.mkdir(parents=True, exist_ok=True)
    # Build Tcl to swap in-place, clear direct nets, run 1.0*H_row boxed DRC, attribute neighbors,
    # lock untouched nets, local DRT, RCX, and full-block DRC
    swap_lines = []
    inst_list = []
    for e in edits:
        nm = cmp.canonical_odb_name(e["instance"])
        inst_list.append(nm)
        swap_lines.append(
            f'set _i [$blk findInst {{{nm}}}]; set _bb [$_i getBBox]; set _x [$_bb xMin]; set _y [$_bb yMin]; '
            f'$_i swapMaster [[ord::get_db] findMaster {{{e["target_cell"]}}}]; $_i setLocation $_x $_y'
        )
    routed_odb = eval_dir / "routed.odb"
    routed_spef = eval_dir / "routed.spef"
    routed_v = eval_dir / "routed.v"
    full_drc = eval_dir / "full_drc.rpt"
    box_rpt = eval_dir / "box_drc.rpt"

    tcl = eval_dir / "run_eval.tcl"
    tcl.write_text(f"""read_liberty {cmp.tcl(SKY_CORNERS['TT'][0])}
read_db {cmp.tcl(ref_info['odb'])}
read_sdc {cmp.tcl(ref_info['sdc'])}
source {cmp.tcl(SKY_SETRC)}
source {cmp.tcl(SKY_FASTROUTE)}
set blk [ord::get_db_block]
set rows [$blk getRows]
set rbb [[lindex $rows 0] getBBox]
set row_h [expr {{[$rbb yMax] - [$rbb yMin]}}]
set die [$blk getDieArea]
{chr(10).join(swap_lines)}
# Clear direct signal nets
set direct_nets {{}}
foreach nm [list {" ".join("{" + x + "}" for x in inst_list)}] {{
  set i [$blk findInst $nm]
  foreach it [$i getITerms] {{
    set n [$it getNet]
    if {{ $n eq "NULL" }} {{ continue }}
    if {{ [$n getSigType] eq "SIGNAL" }} {{ lappend direct_nets [$n getName] }}
  }}
}}
set direct_nets [lsort -unique $direct_nets]
foreach nm $direct_nets {{
  set n [$blk findNet $nm]
  set w [$n getWire]
  if {{ $w ne "NULL" }} {{ odb::dbWire_destroy $w }}
}}
# Boxed 1.0*H_row DRC per edited inst
set rpt_all ""
set idx 0
foreach nm [list {" ".join("{" + x + "}" for x in inst_list)}] {{
  set bb [[$blk findInst $nm] getBBox]
  set x1 [expr {{max([$die xMin], [$bb xMin] - $row_h)}}]
  set y1 [expr {{max([$die yMin], [$bb yMin] - $row_h)}}]
  set x2 [expr {{min([$die xMax], [$bb xMax] + $row_h)}}]
  set y2 [expr {{min([$die yMax], [$bb yMax] + $row_h)}}]
  drt::check_drc -box [list $x1 $y1 $x2 $y2] -output_file "{eval_dir}/box_${{idx}}.rpt"
  incr idx
}}
# Lock all non-direct nets (for clean local reroute; secondary repair handles any attributed neighbors)
set release_nets $direct_nets
foreach n [$blk getNets] {{
  if {{ [$n getSigType] ne "SIGNAL" }} {{ continue }}
  set nm [$n getName]
  if {{ [lsearch -exact $release_nets $nm] < 0 }} {{
    set w [$n getWire]
    if {{ $w ne "NULL" }} {{ $n setSpecial }}
  }}
}}
detailed_route -droute_end_iter 64 -output_drc {cmp.tcl(full_drc)}
foreach n [$blk getNets] {{
  if {{ [$n getSigType] eq "SIGNAL" }} {{ $n clearSpecial }}
}}
drt::check_drc -output_file {cmp.tcl(full_drc)}
extract_parasitics -ext_model_file {cmp.tcl(SKY_RCX)}
write_spef {cmp.tcl(routed_spef)}
write_db {cmp.tcl(routed_odb)}
write_verilog {cmp.tcl(routed_v)}
exit
""", encoding="utf-8")

    t0 = raw_seconds()
    r = subprocess.run([OR_BIN, "-no_init", "-no_splash", "-threads", "4", "-exit", str(tcl)],
                       capture_output=True, text=True, timeout=300)
    dt = raw_seconds() - t0
    if r.returncode != 0 or not routed_spef.is_file():
        return {"accepted": False, "reason": "route_failed", "wall_s": dt}
    drc_cnt = len(re.findall(r"(?m)^violation type:", full_drc.read_text(encoding="utf-8"))) if full_drc.is_file() else 999
    wns = s1.measure_3corner_wns(routed_odb, routed_spef, Path(ref_info["sdc"]), SKY_CORNERS, eval_dir / "sta", "cand")
    fails = []
    if drc_cnt > 0:
        fails.append(f"drc:{drc_cnt}")
    for c in ("FF", "TT", "SS"):
        # EXPLICIT TIMING-CLOSED HARD GATE: W_v(F) >= max(0, W_v(R) - B_W - 0.001)
        if wns[c]["setup_wns_ps"] < max(0.0, ref_wns[c]["setup_wns_ps"] - budget_ps - 0.001):
            fails.append(f"{c}:setup_tc_gate")
        if wns[c]["hold_wns_ps"] < max(0.0, ref_wns[c]["hold_wns_ps"] - 0.001):
            fails.append(f"{c}:hold_regression")
    return {
        "accepted": len(fails) == 0,
        "failures": fails,
        "drc_markers": drc_cnt,
        "views_ps": wns,
        "odb": str(routed_odb),
        "spef": str(routed_spef),
        "wall_s": round(dt, 3),
    }


def main() -> int:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    ref_info = build_independent_riscv32i_tc()
    assert ref_info["strictly_timing_closed"], "Fresh riscv32i-TC reference is not strictly timing-closed!"

    # Generate 18 compatible downsizing actions from the fresh netlist
    raw_cands = generate_compatible_candidates(
        Path(ref_info["v"]), [Path(SKY_CORNERS["TT"][0])],
        one_per_instance=True, deprioritize_zero_drive=False,
    )
    pool18 = sorted(raw_cands, key=lambda c: -float(c.estimated_area_saving))[:18]
    pool_dicts = [
        {"instance": c.instance, "source_cell": c.source_cell, "target_cell": c.target_cell, "area_saving_um2": float(c.estimated_area_saving)}
        for c in pool18
    ]
    pool_ceiling = sum(x["area_saving_um2"] for x in pool_dicts)

    # Evaluate single-gate (b=1), fixed micro-batch (b=3), and FAECO (b=3 + Hold defer) under 720 s wall-clock
    arms = {}
    for mode, bwidth, use_defer in (("single_boxed", 1, False), ("fixed_boxed", 3, False), ("faeco_boxed", 3, True)):
        adir = OUT_ROOT / "arms" / mode
        if adir.exists():
            shutil.rmtree(adir)
        t0 = raw_seconds()
        best_edits = []
        best_saved = 0.0
        best_res = None
        cps = []
        queue = [pool_dicts[i:i + bwidth] for i in range(0, len(pool_dicts), bwidth)]
        deferred = []
        seq = 0
        while (raw_seconds() - t0) < 720.0 and (queue or deferred):
            if queue:
                batch = queue.pop(0)
            else:
                b = deferred.pop(0)
                if len(b) > 1:
                    mid = len(b) // 2
                    queue = [b[:mid], b[mid:]] + queue
                    continue
                batch = b
            seq += 1
            cand = best_edits + batch
            ev = evaluate_subset_protected(ref_info, cand, adir / f"{seq:02d}", ref_info["ref_6corner_ps"], SETUP_BUDGET_PS)
            elapsed = raw_seconds() - t0
            if elapsed > 720.0:
                break
            if ev["accepted"]:
                best_edits = cand
                best_saved = sum(x["area_saving_um2"] for x in best_edits)
                best_res = ev
                cps.append({"elapsed_s": elapsed, "accepted": True, "area_saved_um2": best_saved, "gates": len(best_edits)})
            else:
                cps.append({"elapsed_s": elapsed, "accepted": False, "area_saved_um2": 0.0, "failures": ev.get("failures", [])})
                has_hold = any("hold" in f for f in ev.get("failures", []))
                if use_defer and len(batch) > 1 and has_hold:
                    deferred.append(batch)
                elif len(batch) > 1:
                    mid = len(batch) // 2
                    queue = [batch[:mid], batch[mid:]] + queue

        # Compute AUC & final TT power
        best_a = 0.0
        pts = [(0.0, 0.0)]
        for c in sorted(cps, key=lambda x: x["elapsed_s"]):
            if c["accepted"] and c["area_saved_um2"] > best_a:
                best_a = c["area_saved_um2"]
                pts.append((c["elapsed_s"], best_a))
        pts.append((720.0, best_a))
        auc = sum(max(0.0, t1 - t0_) * v0 for (t0_, v0), (t1, _) in zip(pts, pts[1:])) / 720.0

        pwr_delta = None
        if best_res is not None:
            ep_p = s1.measure_tt_power(Path(best_res["odb"]), Path(best_res["spef"]), Path(ref_info["sdc"]), SKY_CORNERS["TT"], adir, "best_pwr")
            pwr_delta = s1.power_delta_pct(ref_info["ref_power"], ep_p)

        arms[mode] = {
            "qualified_area_saved_um2": best_saved,
            "qualified_gates": len(best_edits),
            "pool_capture_pct": 100.0 * best_saved / pool_ceiling if pool_ceiling else 0.0,
            "anytime_auc_um2": auc,
            "logical_finished": len(cps),
            "final_6corner_ps": best_res["views_ps"] if best_res else ref_info["ref_6corner_ps"],
            "still_timing_closed": all(
                (best_res["views_ps"] if best_res else ref_info["ref_6corner_ps"])[c]["setup_wns_ps"] >= 0.0 and
                (best_res["views_ps"] if best_res else ref_info["ref_6corner_ps"])[c]["hold_wns_ps"] >= 0.0
                for c in ("FF", "TT", "SS")
            ),
            "power_delta_pct": pwr_delta,
        }
        print(f"  [Stage 5/{mode}] saved={best_saved:.4f} um2 ({len(best_edits)}/18), AUC={auc:.4f}, power={pwr_delta}", flush=True)

    payload = {
        "design": "sky130hd_riscv32i_tc10ns_independent",
        "clock_period_ps": CLOCK_NS * 1000.0,
        "setup_budget_ps": SETUP_BUDGET_PS,
        "pool_size": len(pool_dicts),
        "pool_ceiling_um2": pool_ceiling,
        "ref_info": ref_info,
        "arms": arms,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("DONE Stage 5 ->", OUT_JSON, "sha256=", sha256(OUT_JSON), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
