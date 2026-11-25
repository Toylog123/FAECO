#!/usr/bin/env python3
"""Run matched-gate OpenROAD native repair_timing -recover_power and power audit on AES, UART, riscv32i."""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
IBEX_DIR = REPO / "project_docs/evidence/tcad_ibex_20261123"
HOLDOUT_DIR = REPO / "project_docs/evidence/tcad_holdout_20261123"
WALL_DIR = REPO / "project_docs/evidence/tcad_wallclock_schedule_20261125"
for p in (IBEX_DIR, HOLDOUT_DIR, WALL_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import compare_ibex as cmp
import run_setup_budget_sweep as sweep

OR_BIN = Path("/home/toylog/.cache/bazel/_bazel_toylog/c540bbdc4bbb635360729b4d7a91c803/execroot/_main/bazel-out/k8-opt/bin/openroad_unstamped")
OUT_ROOT = Path("/home/toylog/faeco_tcad_native_recover_power_20261125_v1")
EVIDENCE_OUT = REPO / "project_docs/evidence/tcad_external_baselines_20261125"


def raw_now():
    return time.clock_gettime(time.CLOCK_MONOTONIC_RAW)


def run_cmd(argv, logfile, timeout=300):
    t0 = raw_now()
    with open(logfile, "wb") as fh:
        res = subprocess.run(
            ["/usr/bin/timeout", "--kill-after=10s", f"{int(timeout)}s", *[str(a) for a in argv]],
            stdout=fh, stderr=subprocess.STDOUT, check=False, timeout=timeout + 20,
        )
    elapsed = raw_now() - t0
    return {"returncode": res.returncode, "elapsed_raw_seconds": elapsed, "log": str(logfile)}


def measure_power_and_area(odb_path, spef_path, sdc_path, tt_libs, out_dir, tag):
    out_dir.mkdir(parents=True, exist_ok=True)
    pj = out_dir / f"{tag}_power.json"
    tcl = out_dir / f"{tag}_power.tcl"
    lines = [f"read_liberty {cmp.tcl(lib)}" for lib in tt_libs]
    lines += [
        f"read_db {cmp.tcl(odb_path)}",
        f"read_sdc {cmp.tcl(sdc_path)}",
        f"read_spef {cmp.tcl(spef_path)}",
        f"report_power -digits 9 -format json > {cmp.tcl(pj)}",
        f"report_power -digits 6",
        "puts POWER_AUDIT_DONE",
        "exit",
    ]
    tcl.write_text("\n".join(lines) + "\n", encoding="utf-8")
    op = run_cmd([OR_BIN, "-no_init", "-no_splash", "-threads", "1", "-exit", tcl], out_dir / f"{tag}_power.log", 120)
    data = None
    if pj.is_file():
        raw_txt = pj.read_text(encoding="utf-8", errors="replace")
        brace = raw_txt.find("{")
        if brace >= 0:
            data = json.loads(raw_txt[brace:])
    return {"op": op, "power_json_path": str(pj), "power": data}


def count_master_diffs(top, v_ref, v_cand, tt_libs):
    cmp.TOP = top
    areas = cmp.liberty_areas([Path(x) for x in tt_libs])
    m_ref = cmp.logical_masters(Path(v_ref), areas)
    m_cand = cmp.logical_masters(Path(v_cand), areas)
    area_ref = sum(areas[m] for m in m_ref.values())
    area_cand = sum(areas[m] for m in m_cand.values())
    added = sorted(set(m_cand) - set(m_ref))
    removed = sorted(set(m_ref) - set(m_cand))
    resized = sorted(k for k in (set(m_ref) & set(m_cand)) if m_ref[k] != m_cand[k])
    return {
        "ref_instances": len(m_ref), "cand_instances": len(m_cand),
        "ref_area_um2": area_ref, "cand_area_um2": area_cand,
        "area_saved_um2": area_ref - area_cand,
        "area_saved_pct": 100.0 * (area_ref - area_cand) / area_ref if area_ref else 0.0,
        "resized_count": len(resized), "added_count": len(added), "removed_count": len(removed),
        "sample_resized": [(k, m_ref[k], m_cand[k]) for k in resized[:10]],
    }


def run_native_arm(design_cfg, mode_name, extra_flags, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    pdk = design_cfg["pdk"]
    top = design_cfg["top"]
    ctrl = design_cfg["control"]
    tt_libs = design_cfg["libs"]["TT"]
    flow = design_cfg["flow"]

    # Step 1: Run native repair_timing -recover_power + legalize + DRT + RCX + independent DRC
    # Note: we keep the exact same platform setRC.tcl, fastroute.tcl, rcx_rules, and threads=4
    tcl = out_dir / "native_recover.tcl"
    out_odb = out_dir / "routed.odb"
    out_def = out_dir / "routed.def"
    out_v = out_dir / "routed.v"
    out_spef = out_dir / "routed.spef"
    drc_rpt = out_dir / "drc.rpt"
    pre_v = out_dir / "post_rsz.v"
    pre_odb = out_dir / "post_rsz.odb"

    util_tcl = "/home/toylog/faeco_eda/orfs/flow/scripts/util.tcl"
    lines = [f"read_liberty {cmp.tcl(lib)}" for lib in tt_libs]
    lines += [
        f"read_db {cmp.tcl(ctrl['odb'])}",
        f"read_sdc {cmp.tcl(ctrl['sdc'])}",
        f"read_spef {cmp.tcl(ctrl['spef'])}",
        f"source {cmp.tcl(flow['setRC.tcl'])}",
        "remove_fillers",
        "puts NATIVE_BEFORE_REPAIR",
        f"repair_timing -recover_power 100 {extra_flags} -verbose",
        "puts NATIVE_AFTER_REPAIR",
        f"set ::env(REPORTS_DIR) {cmp.tcl(out_dir)}",
        f"source {cmp.tcl(util_tcl)}",
        f"write_verilog {cmp.tcl(pre_v)} -remove_cells [find_physical_only_masters]",
        f"write_db {cmp.tcl(pre_odb)}",
        "puts NATIVE_RSZ_DONE",
        "exit",
    ]
    tcl.write_text("\n".join(lines) + "\n", encoding="utf-8")
    rsz_op = run_cmd([OR_BIN, "-no_init", "-no_splash", "-threads", "1", "-exit", tcl], out_dir / "rsz.log", 240)
    rsz_log = (out_dir / "rsz.log").read_text(encoding="utf-8", errors="replace")
    rsz_ok = rsz_op["returncode"] == 0 and "NATIVE_RSZ_DONE" in rsz_log and pre_v.is_file()
    if not rsz_ok:
        return {"mode": mode_name, "status": "rsz_failed", "rsz_op": rsz_op, "tail": rsz_log[-600:]}

    diff = count_master_diffs(top, ctrl["v"], pre_v, tt_libs)
    rsz_m = re.search(r"Resized (\d+) instances", rsz_log)
    rsz_reported = int(rsz_m.group(1)) if rsz_m else 0
    result = {
        "mode": mode_name, "extra_flags": extra_flags,
        "rsz_op": rsz_op, "rsz_reported_resized": rsz_reported, "netlist_diff": diff,
    }
    if diff["resized_count"] == 0 and diff["added_count"] == 0 and diff["removed_count"] == 0 and rsz_reported == 0:
        result["status"] = "zero_edits"
        result["accepted_area_saved_um2"] = 0.0
        result["total_elapsed_raw_seconds"] = rsz_op["elapsed_raw_seconds"]
        return result

    # Step 2: Legalize + full/incremental DRT + RCX + full DRC/antenna on the modified ODB
    route_tcl = out_dir / "route_rcx.tcl"
    rcx_rules = flow["rcx_patterns.rules"]
    fastroute = flow["fastroute.tcl"]
    util_tcl = "/home/toylog/faeco_eda/orfs/flow/scripts/util.tcl"
    sig_layer, clk_layer, top_layer = ("met1", "met3", "met5") if pdk == "sky130hd" else ("M2", "M4", "M7")
    grt_cmd = "global_route -congestion_iterations 30 -allow_congestion" + (" -resistance_aware" if pdk == "asap7" else "")
    rlines = [f"read_liberty {cmp.tcl(lib)}" for lib in tt_libs]
    rlines += [
        f"read_db {cmp.tcl(pre_odb)}",
        f"read_sdc {cmp.tcl(ctrl['sdc'])}",
        f"source {cmp.tcl(flow['setRC.tcl'])}",
        f"set ::env(MIN_ROUTING_LAYER) {sig_layer}",
        f"set ::env(MIN_CLK_ROUTING_LAYER) {clk_layer}",
        f"set ::env(MAX_ROUTING_LAYER) {top_layer}",
        "set ::env(ROUTING_LAYER_ADJUSTMENT) 0.25",
        f"set ::env(REPORTS_DIR) {cmp.tcl(out_dir)}",
        "remove_fillers",
        "detailed_placement",
        "check_placement -verbose",
        f"source {cmp.tcl(fastroute)}",
        grt_cmd,
        f"detailed_route -output_drc {cmp.tcl(drc_rpt)} -droute_end_iter 64 -verbose 0",
        "check_antennas",
        f"define_process_corner -ext_model_index 0 X",
        f"extract_parasitics -ext_model_file {cmp.tcl(rcx_rules)}",
        f"write_spef {cmp.tcl(out_spef)}",
        f"write_db {cmp.tcl(out_odb)}",
        f"write_def {cmp.tcl(out_def)}",
        f"source {cmp.tcl(util_tcl)}",
        f"write_verilog {cmp.tcl(out_v)} -remove_cells [find_physical_only_masters]",
        "puts NATIVE_ROUTE_RCX_DONE",
        "exit",
    ]
    route_tcl.write_text("\n".join(rlines) + "\n", encoding="utf-8")
    route_op = run_cmd([OR_BIN, "-no_init", "-no_splash", "-threads", "4", "-exit", route_tcl], out_dir / "route_rcx.log", 600)
    route_log = (out_dir / "route_rcx.log").read_text(encoding="utf-8", errors="replace")
    result["route_op"] = route_op
    if route_op["returncode"] != 0 or "NATIVE_ROUTE_RCX_DONE" not in route_log:
        result["status"] = "route_rcx_failed"
        result["route_tail"] = route_log[-800:]
        return result

    drc_text = drc_rpt.read_text(encoding="utf-8", errors="replace") if drc_rpt.is_file() else ""
    drc_count = len(re.findall(r"(?m)^violation type: ", drc_text))
    ant_match = re.findall(r"Found (\d+) net violations", route_log)
    ant_count = int(ant_match[-1]) if ant_match else None

    # Step 3: 3-corner STA (FF/TT/SS) using exact same OpenROAD binary on routed ODB + SPEF + original SDC
    # Note: SKY130HD Liberty time unit is ns (STA reports ns); ASAP7 Liberty time unit is ps (STA reports ps).
    scale_to_ps = 1000.0 if pdk == "sky130hd" else 1.0
    views = {}
    sta_total_s = 0.0
    for corner in ("FF", "TT", "SS"):
        ctcl = out_dir / f"sta_{corner}.tcl"
        clines = [f"read_liberty {cmp.tcl(lib)}" for lib in design_cfg["libs"][corner]]
        clines += [
            f"read_db {cmp.tcl(out_odb)}",
            f"read_sdc {cmp.tcl(ctrl['sdc'])}",
            f"read_spef {cmp.tcl(out_spef)}",
            "report_wns -max",
            "report_tns -max",
            "report_wns -min",
            "report_tns -min",
            "report_worst_slack -max -digits 6",
            "report_worst_slack -min -digits 6",
            "report_check_types -max_slew -max_capacitance -max_fanout -violators",
            "puts STA_CORNER_DONE",
            "exit",
        ]
        ctcl.write_text("\n".join(clines) + "\n", encoding="utf-8")
        sop = run_cmd([OR_BIN, "-no_init", "-no_splash", "-threads", "1", "-exit", ctcl], out_dir / f"sta_{corner}.log", 180)
        sta_total_s += sop["elapsed_raw_seconds"]
        slog = (out_dir / f"sta_{corner}.log").read_text(encoding="utf-8", errors="replace")
        def grab_ps(pat):
            m = re.search(pat, slog)
            return float(m.group(1)) * scale_to_ps if m else None
        views[corner] = {
            "setup_wns_ps": grab_ps(r"(?m)^worst slack max\s+([+-]?\d+(?:\.\d+)?)"),
            "hold_wns_ps": grab_ps(r"(?m)^worst slack min\s+([+-]?\d+(?:\.\d+)?)"),
            "setup_tns_ps": grab_ps(r"(?m)^tns max\s+([+-]?\d+(?:\.\d+)?)"),
            "hold_tns_ps": grab_ps(r"(?m)^tns min\s+([+-]?\d+(?:\.\d+)?)"),
            "has_slew_cap_viol": "VIOLATED" in slog,
            "op": sop,
        }

    # Check gate against reference views
    ref_views = design_cfg["ref_views"]
    gate_failures = []
    if drc_count > 0:
        gate_failures.append(f"drc={drc_count}")
    if ant_count not in (None, 0):
        gate_failures.append(f"antenna={ant_count}")
    deltas = {}
    for corner in ("FF", "TT", "SS"):
        rv = ref_views[corner]
        cv = views[corner]
        dw = (cv["setup_wns_ps"] - rv["setup_wns_ps"]) if (cv["setup_wns_ps"] is not None and rv["setup_wns_ps"] is not None) else None
        dt = (cv["setup_tns_ps"] - rv["setup_tns_ps"]) if (cv["setup_tns_ps"] is not None and rv["setup_tns_ps"] is not None) else None
        dh = (cv["hold_wns_ps"] - rv["hold_wns_ps"]) if (cv["hold_wns_ps"] is not None and rv["hold_wns_ps"] is not None) else None
        deltas[corner] = {"d_setup_wns_ps": dw, "d_setup_tns_ps": dt, "d_hold_wns_ps": dh, "abs_hold_wns_ps": cv["hold_wns_ps"]}
        if dw is None or dw < -design_cfg["wns_budget_ps"] - 1e-6:
            gate_failures.append(f"{corner}:setup_wns")
        if dt is None or dt < -design_cfg["tns_budget_ps"][corner] - 1e-6:
            gate_failures.append(f"{corner}:setup_tns")
        if cv["hold_wns_ps"] is None or cv["hold_wns_ps"] < 0.0:
            gate_failures.append(f"{corner}:abs_hold")
        if dh is None or dh < -0.001 - 1e-9:
            gate_failures.append(f"{corner}:rel_hold")
        if cv["has_slew_cap_viol"]:
            gate_failures.append(f"{corner}:electrical_viol")

    # Step 4: Power on routed endpoint
    power = measure_power_and_area(out_odb, out_spef, ctrl["sdc"], tt_libs, out_dir, "native")
    final_diff = count_master_diffs(top, ctrl["v"], out_v, tt_libs)

    result.update({
        "status": "passed_gates" if not gate_failures else "rejected_by_gates",
        "drc_markers": drc_count,
        "antenna_violations": ant_count,
        "views": views,
        "deltas_vs_control": deltas,
        "gate_failures": gate_failures,
        "final_netlist_diff": final_diff,
        "power": power["power"],
        "total_elapsed_raw_seconds": rsz_op["elapsed_raw_seconds"] + route_op["elapsed_raw_seconds"] + sta_total_s,
    })
    return result


def load_designs():
    # AES
    aes_m = json.loads(Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_matrix_v1/config.json").read_text())
    aes_ref = json.loads(Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_matrix_v1/control/receipt.json").read_text())["views"]
    aes_f = json.loads(Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_factorial_20261124_v1/forward/fixed_online/config.json").read_text())
    aes_best_odb = "/home/toylog/faeco_tcad_sky_holdout_20261123/aes_factorial_20261124_v1/forward/faeco_online/faeco/04/initial/routed.odb"
    aes_best_spef = "/home/toylog/faeco_tcad_sky_holdout_20261123/aes_factorial_20261124_v1/forward/faeco_online/faeco/04/initial/routed.spef"

    # UART
    uart_p = json.loads(Path("/home/toylog/faeco_tcad_uart_wallclock_20261125_v1/protocol.json").read_text())
    uart_s = json.loads(Path(uart_p["seed"]["path"]).read_text())
    uart_ref = json.loads(Path(uart_p["reference"]["path"]).read_text())["views"]
    uart_best_odb = "/home/toylog/faeco_tcad_uart_wallclock_20261125_v1/cell_03/faeco/16/initial/routed.odb"
    uart_best_spef = "/home/toylog/faeco_tcad_uart_wallclock_20261125_v1/cell_03/faeco/16/initial/routed.spef"

    # RISCV32I
    riscv_p = json.loads(Path("/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i/matrix_rank_aligned_v1/protocol.json").read_text())
    riscv_s = json.loads(Path(riscv_p["seed"]["path"]).read_text())
    riscv_ref = json.loads(Path(riscv_p["reference"]["path"]).read_text())["views"]
    riscv_best_odb = "/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i/matrix_rank_aligned_v1/cell_03/faeco/03/retry/routed.odb"
    riscv_best_spef = "/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i/matrix_rank_aligned_v1/cell_03/faeco/03/retry/routed.spef"

    def extract_views(vdict):
        out = {}
        for c in ("FF", "TT", "SS"):
            v = vdict[c]
            out[c] = {
                "setup_wns_ps": v["setup_wns_ps"],
                "setup_tns_ps": v["setup_tns_ps"],
                "hold_wns_ps": v["hold_wns_ps"],
            }
        return out

    def extract_gate(gdict):
        wns = gdict["budget_ps"]
        tns = {c: gdict["setup_tns_budget_ps_by_view"][c] for c in ("FF", "TT", "SS")}
        return wns, tns

    aes_wns, aes_tns = extract_gate(aes_f["gate"])
    uart_wns, uart_tns = extract_gate(uart_p["gate"])
    riscv_wns, riscv_tns = extract_gate(riscv_p["gate"])

    return [
        {
            "name": "sky130hd_aes", "pdk": "sky130hd", "top": aes_m["top"],
            "control": {k: v["path"] for k, v in aes_m["bindings"]["control"].items()},
            "libs": {c: [x["path"] for x in aes_m["bindings"]["used_libraries"][c]] for c in ("FF", "TT", "SS")},
            "flow": {k: v["path"] for k, v in aes_m["bindings"]["flow"].items()},
            "ref_views": extract_views(aes_ref), "wns_budget_ps": aes_wns, "tns_budget_ps": aes_tns,
            "faeco_best": {"odb": aes_best_odb, "spef": aes_best_spef, "area_saved_um2": 67.5648},
        },
        {
            "name": "asap7_uart", "pdk": "asap7", "top": uart_s["top"],
            "control": {k: v["path"] for k, v in uart_s["bindings"]["control"].items()},
            "libs": {c: [x["path"] for x in uart_s["bindings"]["used_libraries"][c]] for c in ("FF", "TT", "SS")},
            "flow": {k: v["path"] for k, v in uart_s["bindings"]["flow"].items()},
            "ref_views": extract_views(uart_ref), "wns_budget_ps": uart_wns, "tns_budget_ps": uart_tns,
            "faeco_best": {"odb": uart_best_odb, "spef": uart_best_spef, "area_saved_um2": 0.83106},
        },
        {
            "name": "sky130hd_riscv32i", "pdk": "sky130hd", "top": riscv_s["top"],
            "control": {k: v["path"] for k, v in riscv_s["bindings"]["control"].items()},
            "libs": {c: [x["path"] for x in riscv_s["bindings"]["used_libraries"][c]] for c in ("FF", "TT", "SS")},
            "flow": {k: v["path"] for k, v in riscv_s["bindings"]["flow"].items()},
            "ref_views": extract_views(riscv_ref), "wns_budget_ps": riscv_wns, "tns_budget_ps": riscv_tns,
            "faeco_best": {"odb": riscv_best_odb, "spef": riscv_best_spef, "area_saved_um2": 75.072},
        },
    ]


def reparse_existing_aes(d, existing_aes_dir):
    """Reparse already-completed AES native runs with exact ns->ps scaling (x1000)."""
    out = {
        "pdk": d["pdk"], "top": d["top"],
        "wns_budget_ps": d["wns_budget_ps"], "tns_budget_ps": d["tns_budget_ps"],
        "faeco_best_area_saved_um2": d["faeco_best"]["area_saved_um2"],
    }
    prev = json.loads((EVIDENCE_OUT / "NATIVE_RECOVER_POWER_RESULTS.json").read_text())["designs"]["sky130hd_aes"]
    out["control_power"] = prev["control_power"]
    out["faeco_best_power"] = prev["faeco_best_power"]
    for key in ("native_default", "native_allow_setup"):
        arm = dict(prev[key])
        views = {}
        deltas = {}
        gate_failures = []
        if arm["drc_markers"] > 0:
            gate_failures.append(f"drc={arm['drc_markers']}")
        if arm["antenna_violations"] not in (None, 0):
            gate_failures.append(f"antenna={arm['antenna_violations']}")
        for c in ("FF", "TT", "SS"):
            # Raw logs on sky130hd are in ns -> multiply by 1000 to get ps
            raw_v = arm["views"][c]
            cv = {
                "setup_wns_ps": raw_v["setup_wns_ps"] * 1000.0,
                "hold_wns_ps": raw_v["hold_wns_ps"] * 1000.0,
                "setup_tns_ps": raw_v["setup_tns_ps"] * 1000.0,
                "hold_tns_ps": raw_v["hold_tns_ps"] * 1000.0,
                "has_slew_cap_viol": raw_v["has_slew_cap_viol"],
                "op": raw_v["op"],
            }
            views[c] = cv
            rv = d["ref_views"][c]
            dw = cv["setup_wns_ps"] - rv["setup_wns_ps"]
            dt = cv["setup_tns_ps"] - rv["setup_tns_ps"]
            dh = cv["hold_wns_ps"] - rv["hold_wns_ps"]
            deltas[c] = {"d_setup_wns_ps": dw, "d_setup_tns_ps": dt, "d_hold_wns_ps": dh, "abs_hold_wns_ps": cv["hold_wns_ps"]}
            if dw < -d["wns_budget_ps"] - 1e-6:
                gate_failures.append(f"{c}:setup_wns")
            if dt < -d["tns_budget_ps"][c] - 1e-6:
                gate_failures.append(f"{c}:setup_tns")
            if cv["hold_wns_ps"] < 0.0:
                gate_failures.append(f"{c}:abs_hold")
            if dh < -0.001 - 1e-9:
                gate_failures.append(f"{c}:rel_hold")
            if cv["has_slew_cap_viol"]:
                gate_failures.append(f"{c}:electrical_viol")
        arm["views"] = views
        arm["deltas_vs_control"] = deltas
        arm["gate_failures"] = gate_failures
        arm["status"] = "passed_gates" if not gate_failures else "rejected_by_gates"
        out[key] = arm
    return out


def main():
    reuse_aes = "--reuse-aes" in sys.argv
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    EVIDENCE_OUT.mkdir(parents=True, exist_ok=True)
    summary = {"openroad_bin": str(OR_BIN), "designs": {}}
    for d in load_designs():
        name = d["name"]
        ddir = OUT_ROOT / name
        if reuse_aes and name == "sky130hd_aes" and (ddir / "native_default/sta_SS.log").is_file():
            print("=== Reparsing existing sky130hd_aes with ns->ps x1000 ===", flush=True)
            summary["designs"][name] = reparse_existing_aes(d, ddir)
            nd = summary["designs"][name]["native_default"]
            print(f"  sky130hd_aes: default={nd['status']} failures={nd['gate_failures']}", flush=True)
            continue
        ddir.mkdir(parents=True, exist_ok=True)
        print(f"=== Running {name} ===", flush=True)
        ctrl_pwr = measure_power_and_area(d["control"]["odb"], d["control"]["spef"], d["control"]["sdc"], d["libs"]["TT"], ddir / "power", "control")
        faeco_pwr = measure_power_and_area(d["faeco_best"]["odb"], d["faeco_best"]["spef"], d["control"]["sdc"], d["libs"]["TT"], ddir / "power", "faeco_best")
        native_default = run_native_arm(d, "recover_power_100", "", ddir / "native_default")
        native_allow = run_native_arm(d, "recover_power_100_allow_setup", "-allow_setup_violations", ddir / "native_allow_setup")
        summary["designs"][name] = {
            "pdk": d["pdk"], "top": d["top"],
            "wns_budget_ps": d["wns_budget_ps"], "tns_budget_ps": d["tns_budget_ps"],
            "control_power": ctrl_pwr["power"],
            "faeco_best_area_saved_um2": d["faeco_best"]["area_saved_um2"],
            "faeco_best_power": faeco_pwr["power"],
            "native_default": native_default,
            "native_allow_setup": native_allow,
        }
        (OUT_ROOT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        (EVIDENCE_OUT / "NATIVE_RECOVER_POWER_RESULTS.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"  {name}: default={native_default['status']} (edits={native_default.get('netlist_diff',{}).get('resized_count')}, fails={native_default.get('gate_failures')}), allow={native_allow['status']} (edits={native_allow.get('netlist_diff',{}).get('resized_count')}, fails={native_allow.get('gate_failures')})", flush=True)


if __name__ == "__main__":
    main()
