#!/usr/bin/env python3
"""Independent verification of 7nm asap7/aes rank-aligned 6-arm holdout + matched native recover_power & power audit."""

import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
IBEX_DIR = REPO / "project_docs/evidence/tcad_ibex_20261123"
EVIDENCE_DIR = REPO / "project_docs/evidence/tcad_asap7_aes_holdout_20261125"
RAW_ROOT = Path("/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes")
MATRIX_ROOT = RAW_ROOT / "matrix_rank_aligned_v1"
CTRL_DIR = RAW_ROOT / "repaired_control_v4"
OR_BIN = Path("/home/toylog/.cache/bazel/_bazel_toylog/c540bbdc4bbb635360729b4d7a91c803/execroot/_main/bazel-out/k8-opt/bin/openroad_unstamped")
STA_BIN = Path("/usr/local/bin/sta-3.1.0")
FLOW = Path("/home/toylog/faeco_eda/orfs/flow")

if str(IBEX_DIR) not in sys.path:
    sys.path.insert(0, str(IBEX_DIR))
import compare_ibex as cmp


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def spef_dateless_sha(path: Path) -> str:
    h = hashlib.sha256()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True):
        if line.startswith("*DATE "):
            continue
        h.update(line.encode("utf-8"))
    return h.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def raw_now():
    return time.clock_gettime(time.CLOCK_MONOTONIC_RAW)


def run_cmd(argv, logfile, timeout=420):
    t0 = raw_now()
    with open(logfile, "wb") as fh:
        res = subprocess.run(
            ["/usr/bin/timeout", "--kill-after=10s", f"{int(timeout)}s", *[str(a) for a in argv]],
            stdout=fh, stderr=subprocess.STDOUT, check=False, timeout=timeout + 20,
        )
    return {"returncode": res.returncode, "elapsed_raw_seconds": raw_now() - t0, "log": str(logfile)}


def measure_power(odb_path, spef_path, sdc_path, tt_libs, out_dir, tag):
    out_dir.mkdir(parents=True, exist_ok=True)
    pj = out_dir / f"{tag}_power.json"
    tcl = out_dir / f"{tag}_power.tcl"
    lines = [f"read_liberty {cmp.tcl(lib)}" for lib in tt_libs] + [
        f"read_db {cmp.tcl(odb_path)}",
        f"read_sdc {cmp.tcl(sdc_path)}",
        f"read_spef {cmp.tcl(spef_path)}",
        f"report_power -digits 9 -format json > {cmp.tcl(pj)}",
        "puts POWER_DONE",
        "exit",
    ]
    tcl.write_text("\n".join(lines) + "\n", encoding="utf-8")
    op = run_cmd([OR_BIN, "-no_init", "-no_splash", "-threads", "1", "-exit", tcl], out_dir / f"{tag}_power.log", 180)
    txt = pj.read_text(encoding="utf-8", errors="replace")
    return {"op": op, "power": json.loads(txt[txt.index("{"):])}


def verify_matrix():
    proto = load_json(MATRIX_ROOT / "protocol.json")
    seed = load_json(Path(proto["seed"]["path"]))
    ref_views = load_json(Path(proto["reference"]["path"]))["views"]
    zero_res = load_json(MATRIX_ROOT / "preflight/zero/result.json")
    base_area = zero_res["endpoint"]["area"]
    screen_s = proto["charged_screening_seconds_per_arm"]

    arms = []
    best_by_strat = {}
    all_diag_markers = 0
    all_diag_calls = 0
    diag_seconds = []

    for cell_idx in range(1, 7):
        cdir = MATRIX_ROOT / f"cell_{cell_idx:02d}"
        arm = load_json(cdir / "arm.json")
        strat = arm["strategy"]
        direction = arm["direction"]
        method_folder = {"fixed_online": "fixed", "single_sensitivity": "single", "faeco_dedup": "faeco"}[strat]
        mdir = cdir / method_folder
        prog = load_json(mdir / "progress.json")
        res = arm["result"]
        win = res["window"]

        # Read time to reach >= 0.204120 um2 (common matched area = single_sensitivity max)
        t_matched = None
        area_at_matched = None
        best_cp_idx = None
        best_area = base_area
        for idx, cp in enumerate(prog["checkpoints"], 1):
            if cp["accepted"]:
                saved = base_area - cp["endpoint"]["area"]
                if saved >= 0.20412 - 1e-6 and t_matched is None:
                    t_matched = cp["elapsed_seconds"]
                    area_at_matched = saved
                if cp["endpoint"]["area"] < best_area:
                    best_area = cp["endpoint"]["area"]
                    best_cp_idx = idx

        # Collect diagnosis stats
        arm_diag_calls = 0
        arm_diag_markers = 0
        for dp in sorted((mdir / "diagnosis").glob("*/diagnosis.json")):
            dj = load_json(dp)
            arm_diag_calls += 1
            all_diag_calls += 1
            mc = dj.get("marker_count") or 0
            arm_diag_markers += mc
            all_diag_markers += mc
            diag_seconds.append(dj["seconds"])

        # Inspect best endpoint physical receipt & SEC
        best_rec = load_json(mdir / f"{best_cp_idx:02d}/result.json")
        final_pass = best_rec["passes"][-1]
        phys = load_json(mdir / f"{best_cp_idx:02d}/{final_pass}/receipt.json")
        sec_rec = load_json(mdir / f"{best_cp_idx:02d}/{final_pass}/sec/receipt.json")
        fp = {
            "actions": best_rec["actions"],
            "area": best_rec["endpoint"]["area"],
            "area_saved_um2": base_area - best_rec["endpoint"]["area"],
            "area_saved_pct": 100.0 * (base_area - best_rec["endpoint"]["area"]) / base_area,
            "odb_path": phys["artifacts"]["odb"]["path"],
            "spef_path": phys["artifacts"]["spef"]["path"],
            "odb_sha": sha256(Path(phys["artifacts"]["odb"]["path"])),
            "def_sha": sha256(Path(phys["artifacts"]["def"]["path"])),
            "v_sha": sha256(Path(phys["artifacts"]["v"]["path"])),
            "spef_dateless_sha": spef_dateless_sha(Path(phys["artifacts"]["spef"]["path"])),
            "sec_proven": sec_rec["proven"],
            "sec_unproven": sec_rec["unproven"],
            "views_delta_ps": {
                c: {
                    "d_setup_wns_ps": phys["views"][c]["setup_wns_ps"] - ref_views[c]["setup_wns_ps"],
                    "d_setup_tns_ps": phys["views"][c]["setup_tns_ps"] - ref_views[c]["setup_tns_ps"],
                    "d_hold_wns_ps": phys["views"][c]["hold_wns_ps"] - ref_views[c]["hold_wns_ps"],
                    "abs_hold_wns_ps": phys["views"][c]["hold_wns_ps"],
                }
                for c in ("FF", "TT", "SS")
            },
        }
        best_by_strat.setdefault(strat, {})[direction] = fp

        row = {
            "cell": cell_idx,
            "direction": direction,
            "strategy": strat,
            "logical_finished": res["logical_finished"],
            "logical_admitted": res["logical_admitted"],
            "area_saved_um2": win["area_saved"],
            "area_saved_pct": 100.0 * win["area_saved"] / base_area,
            "first_0p01pct_s": win["time_to_target_seconds"],
            "first_matched_0p20412_s": t_matched,
            "area_at_matched_um2": area_at_matched,
            "diag_calls": arm_diag_calls,
            "diag_markers": arm_diag_markers,
            "route_tools": res["route_tools"],
            "sec_tools": res["sec_tools"],
            "best_endpoint": fp,
        }
        arms.append(row)
        print(f"cell_{cell_idx:02d} {direction:7s} {strat:18s} | fin={row['logical_finished']}/{row['logical_admitted']} | "
              f"area={row['area_saved_um2']:.5f} um2 ({row['area_saved_pct']:.4f}%) | "
              f"t_0.01%={row['first_0p01pct_s']:.2f}s | t_matched(0.20412)={row['first_matched_0p20412_s']:.2f}s | "
              f"diag_markers={arm_diag_markers}/{arm_diag_calls} | SEC={fp['sec_proven']}/{fp['sec_unproven']}")

    cross_order_exact = {}
    for strat, by_dir in best_by_strat.items():
        f, r = by_dir["forward"], by_dir["reverse"]
        cross_order_exact[strat] = (
            f["actions"] == r["actions"]
            and f["odb_sha"] == r["odb_sha"]
            and f["def_sha"] == r["def_sha"]
            and f["v_sha"] == r["v_sha"]
            and f["spef_dateless_sha"] == r["spef_dateless_sha"]
        )
    fixed_vs_faeco_exact = (
        best_by_strat["fixed_online"]["forward"]["odb_sha"] == best_by_strat["faeco_dedup"]["forward"]["odb_sha"]
        and best_by_strat["fixed_online"]["forward"]["spef_dateless_sha"] == best_by_strat["faeco_dedup"]["forward"]["spef_dateless_sha"]
    )
    print("\nCross-order exact ODB/DEF/V/dateless-SPEF match:", cross_order_exact)
    print("Fixed vs FAECO exact same 6-gate physical endpoint:", fixed_vs_faeco_exact)
    print(f"Total pre-DRT diagnosis calls={all_diag_calls}, total markers={all_diag_markers}, mean diag_s={sum(diag_seconds)/len(diag_seconds):.2f}s")
    return {
        "base_functional_area_um2": base_area,
        "charged_screening_seconds": screen_s,
        "gate": proto["gate"],
        "arms": arms,
        "cross_order_exact": cross_order_exact,
        "fixed_vs_faeco_exact_same_endpoint": fixed_vs_faeco_exact,
        "total_diag_calls": all_diag_calls,
        "total_diag_markers": all_diag_markers,
        "mean_diag_seconds": sum(diag_seconds) / len(diag_seconds) if diag_seconds else 0.0,
        "faeco_best": best_by_strat["faeco_dedup"]["forward"],
        "seed": seed,
        "ref_views": ref_views,
    }


def run_native_and_power(mdata):
    seed = mdata["seed"]
    libs = {c: [x["path"] for x in seed["bindings"]["used_libraries"][c]] for c in ("FF", "TT", "SS")}
    ctrl = {k: v["path"] for k, v in seed["bindings"]["control"].items()}
    out_dir = RAW_ROOT / "native_recover_power_v1"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Power of CONTROL vs FAECO best 6-gate endpoint
    ctrl_pwr = measure_power(ctrl["odb"], ctrl["spef"], ctrl["sdc"], libs["TT"], out_dir / "power", "control")["power"]
    faeco_pwr = measure_power(mdata["faeco_best"]["odb_path"], mdata["faeco_best"]["spef_path"], ctrl["sdc"], libs["TT"], out_dir / "power", "faeco_best")["power"]

    # 2. Run native repair_timing -recover_power 100
    ndir = out_dir / "native_default"
    ndir.mkdir(parents=True, exist_ok=True)
    pre_v = ndir / "post_rsz.v"
    pre_odb = ndir / "post_rsz.odb"
    tcl = ndir / "rsz.tcl"
    util_tcl = FLOW / "scripts/util.tcl"
    setrc = FLOW / "platforms/asap7/setRC.tcl"
    lines = [f"read_liberty {cmp.tcl(lib)}" for lib in libs["TT"]] + [
        f"read_db {cmp.tcl(ctrl['odb'])}",
        f"read_sdc {cmp.tcl(ctrl['sdc'])}",
        f"read_spef {cmp.tcl(ctrl['spef'])}",
        f"source {cmp.tcl(setrc)}",
        "remove_fillers",
        "puts NATIVE_BEFORE_REPAIR",
        "repair_timing -recover_power 100 -verbose",
        "puts NATIVE_AFTER_REPAIR",
        f"set ::env(REPORTS_DIR) {cmp.tcl(ndir)}",
        f"source {cmp.tcl(util_tcl)}",
        f"write_verilog {cmp.tcl(pre_v)} -remove_cells [find_physical_only_masters]",
        f"write_db {cmp.tcl(pre_odb)}",
        "puts NATIVE_RSZ_DONE",
        "exit",
    ]
    tcl.write_text("\n".join(lines) + "\n", encoding="utf-8")
    rsz_op = run_cmd([OR_BIN, "-no_init", "-no_splash", "-threads", "1", "-exit", tcl], ndir / "rsz.log", 300)
    rsz_log = (ndir / "rsz.log").read_text(encoding="utf-8", errors="replace")
    rsz_m = re.search(r"Resized (\d+) instances", rsz_log)
    rsz_cnt = int(rsz_m.group(1)) if rsz_m else 0

    cmp.TOP = "aes_cipher_top"
    areas = cmp.liberty_areas([Path(x) for x in libs["TT"]])
    m_ref = cmp.logical_masters(Path(ctrl["v"]), areas)
    m_pre = cmp.logical_masters(pre_v, areas)
    area_ref = sum(areas[m] for m in m_ref.values())
    area_pre = sum(areas[m] for m in m_pre.values())
    native_info = {
        "rsz_op": rsz_op, "rsz_reported_resized": rsz_cnt,
        "pre_area_saved_um2": area_ref - area_pre,
        "pre_area_saved_pct": 100.0 * (area_ref - area_pre) / area_ref,
    }
    print(f"\nNative recover_power on asap7/aes: rsz_cnt={rsz_cnt}, pre_area_saved={area_ref - area_pre:.5f} um2 ({native_info['pre_area_saved_pct']:.4f}%) in {rsz_op['elapsed_raw_seconds']:.2f}s", flush=True)

    if rsz_cnt > 0:
        # Legalize + GRT + DRT + write_db BEFORE RCX + 3-corner STA
        out_odb, out_def, out_v, out_spef = ndir / "routed.odb", ndir / "routed.def", ndir / "routed.v", ndir / "routed.spef"
        drc_rpt = ndir / "drc.rpt"
        rtcl = ndir / "route_rcx.tcl"
        rlines = [f"read_liberty {cmp.tcl(lib)}" for lib in libs["TT"]] + [
            f"read_db {cmp.tcl(pre_odb)}",
            f"read_sdc {cmp.tcl(ctrl['sdc'])}",
            f"source {cmp.tcl(setrc)}",
            "set ::env(MIN_ROUTING_LAYER) M2",
            "set ::env(MIN_CLK_ROUTING_LAYER) M4",
            "set ::env(MAX_ROUTING_LAYER) M7",
            "set ::env(ROUTING_LAYER_ADJUSTMENT) 0.25",
            f"set ::env(REPORTS_DIR) {cmp.tcl(ndir)}",
            "detailed_placement",
            "check_placement -verbose",
            f"source {cmp.tcl(FLOW / 'platforms/asap7/fastroute.tcl')}",
            "global_route -congestion_iterations 30 -allow_congestion -resistance_aware",
            f"detailed_route -output_drc {cmp.tcl(drc_rpt)} -droute_end_iter 64 -verbose 0",
            "check_antennas",
            f"source {cmp.tcl(util_tcl)}",
            f"write_verilog {cmp.tcl(out_v)} -remove_cells [find_physical_only_masters]",
            f"write_def {cmp.tcl(out_def)}",
            f"write_db {cmp.tcl(out_odb)}",
            "define_process_corner -ext_model_index 0 X",
            f"extract_parasitics -ext_model_file {cmp.tcl(FLOW / 'platforms/asap7/rcx_patterns.rules')}",
            f"write_spef {cmp.tcl(out_spef)}",
            "puts NATIVE_ROUTE_RCX_DONE",
            "exit",
        ]
        rtcl.write_text("\n".join(rlines) + "\n", encoding="utf-8")
        rop = run_cmd([OR_BIN, "-no_init", "-no_splash", "-threads", "4", "-exit", rtcl], ndir / "route_rcx.log", 720)
        rlog = (ndir / "route_rcx.log").read_text(encoding="utf-8", errors="replace")
        native_info["route_op"] = rop
        if rop["returncode"] == 0 and "NATIVE_ROUTE_RCX_DONE" in rlog:
            drc_cnt = len(re.findall(r"(?m)^violation type: ", drc_rpt.read_text(encoding="utf-8", errors="replace"))) if drc_rpt.is_file() else -1
            ant_m = re.findall(r"Found (\d+) net violations", rlog)
            ant_cnt = int(ant_m[-1]) if ant_m else 0
            views, deltas, fails = {}, {}, []
            if drc_cnt > 0:
                fails.append(f"drc={drc_cnt}")
            if ant_cnt > 0:
                fails.append(f"antenna={ant_cnt}")
            wns_bud = mdata["gate"]["budget_ps"]
            tns_bud = mdata["gate"]["setup_tns_budget_ps_by_view"]
            for c in ("FF", "TT", "SS"):
                ctcl = ndir / f"sta_{c}.tcl"
                ctcl.write_text(cmp.render_sta(libs[c], out_v, ctrl["sdc"], out_spef, report_setup_endpoints=True))
                sop = run_cmd([STA_BIN, "-exit", ctcl], ndir / f"sta_{c}.log", 180)
                stxt = (ndir / f"sta_{c}.log").read_text(encoding="utf-8", errors="replace")
                pv = cmp.parse_sta(stxt)
                views[c] = pv
                rv = mdata["ref_views"][c]
                dw = pv["setup_wns_ps"] - rv["setup_wns_ps"]
                dt = pv["setup_tns_ps"] - rv["setup_tns_ps"]
                dh = pv["hold_wns_ps"] - rv["hold_wns_ps"]
                deltas[c] = {"d_setup_wns_ps": dw, "d_setup_tns_ps": dt, "d_hold_wns_ps": dh, "abs_hold_wns_ps": pv["hold_wns_ps"]}
                if dw < -wns_bud - 1e-6:
                    fails.append(f"{c}:setup_wns")
                if dt < -tns_bud[c] - 1e-6:
                    fails.append(f"{c}:setup_tns")
                if pv["hold_wns_ps"] < 0.0:
                    fails.append(f"{c}:abs_hold")
                if dh < -0.001 - 1e-9:
                    fails.append(f"{c}:rel_hold")
                if any(pv["electrical"].values()):
                    fails.append(f"{c}:electrical")
            native_info.update({
                "drc_markers": drc_cnt, "antenna_violations": ant_cnt,
                "deltas_vs_control_ps": deltas, "gate_failures": fails,
                "qualified_area_saved_um2": (area_ref - area_pre) if not fails else 0.0,
            })
            print(f"  Native routed result: DRC={drc_cnt} ANT={ant_cnt} dWNS(FF/TT/SS)={deltas['FF']['d_setup_wns_ps']:+.2f}/{deltas['TT']['d_setup_wns_ps']:+.2f}/{deltas['SS']['d_setup_wns_ps']:+.2f} "
                  f"dHold(FF/TT/SS)={deltas['FF']['d_hold_wns_ps']:+.3f}/{deltas['TT']['d_hold_wns_ps']:+.3f}/{deltas['SS']['d_hold_wns_ps']:+.3f} FAILS={fails}", flush=True)
        else:
            native_info["status"] = "route_failed"
            print("  Native route failed or timed out rc=", rop["returncode"])

    pwr_summary = {
        "control_total_W": ctrl_pwr["Total"]["total"],
        "faeco_total_W": faeco_pwr["Total"]["total"],
        "total_delta_pct": 100.0 * (faeco_pwr["Total"]["total"] - ctrl_pwr["Total"]["total"]) / ctrl_pwr["Total"]["total"],
        "comb_delta_pct": 100.0 * (faeco_pwr["Combinational"]["total"] - ctrl_pwr["Combinational"]["total"]) / ctrl_pwr["Combinational"]["total"],
        "leakage_delta_pct": 100.0 * (faeco_pwr["Total"]["leakage"] - ctrl_pwr["Total"]["leakage"]) / ctrl_pwr["Total"]["leakage"],
    }
    print(f"Power on asap7/aes FAECO best: P_tot {pwr_summary['total_delta_pct']:+.4f}% | P_comb {pwr_summary['comb_delta_pct']:+.4f}% | P_leak {pwr_summary['leakage_delta_pct']:+.4f}%", flush=True)
    return pwr_summary, native_info


def main():
    mdata = verify_matrix()
    pwr, native = run_native_and_power(mdata)
    out = {
        "raw_root": str(MATRIX_ROOT),
        "base_functional_area_um2": mdata["base_functional_area_um2"],
        "charged_screening_seconds": mdata["charged_screening_seconds"],
        "gate": mdata["gate"],
        "arms": mdata["arms"],
        "cross_order_exact": mdata["cross_order_exact"],
        "fixed_vs_faeco_exact_same_endpoint": mdata["fixed_vs_faeco_exact_same_endpoint"],
        "total_diag_calls": mdata["total_diag_calls"],
        "total_diag_markers": mdata["total_diag_markers"],
        "mean_diag_seconds": mdata["mean_diag_seconds"],
        "power_summary": pwr,
        "native_recover_power": native,
    }
    out_path = EVIDENCE_DIR / "ASAP7_AES_HOLDOUT_VERIFIED.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("Wrote", out_path, "sha256=", sha256(out_path))


if __name__ == "__main__":
    main()
