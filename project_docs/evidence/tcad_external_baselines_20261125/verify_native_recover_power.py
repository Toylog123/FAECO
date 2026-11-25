#!/usr/bin/env python3
"""Independent raw-log verifier for OpenROAD native repair_timing -recover_power and power audit."""

import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
IBEX_DIR = REPO / "project_docs/evidence/tcad_ibex_20261123"
EVIDENCE_DIR = REPO / "project_docs/evidence/tcad_external_baselines_20261125"
RAW_ROOT = Path("/home/toylog/faeco_tcad_native_recover_power_20261125_v1")
if str(IBEX_DIR) not in sys.path:
    sys.path.insert(0, str(IBEX_DIR))
if str(EVIDENCE_DIR) not in sys.path:
    sys.path.insert(0, str(EVIDENCE_DIR))

import compare_ibex as cmp
from run_native_recover_power import load_designs, count_master_diffs


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def parse_power_json(path: Path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    return json.loads(txt[txt.index("{"):])


def parse_sta_log_ps(path: Path, pdk: str):
    scale = 1000.0 if pdk == "sky130hd" else 1.0
    txt = path.read_text(encoding="utf-8", errors="replace")
    def grab(pat):
        m = re.search(pat, txt)
        return float(m.group(1)) * scale if m else None
    return {
        "setup_wns_ps": grab(r"(?m)^worst slack max\s+([+-]?\d+(?:\.\d+)?)"),
        "hold_wns_ps": grab(r"(?m)^worst slack min\s+([+-]?\d+(?:\.\d+)?)"),
        "setup_tns_ps": grab(r"(?m)^tns max\s+([+-]?\d+(?:\.\d+)?)"),
        "hold_tns_ps": grab(r"(?m)^tns min\s+([+-]?\d+(?:\.\d+)?)"),
        "has_slew_cap_viol": "VIOLATED" in txt,
        "sha256": sha256(path),
    }


def main():
    verified = {"raw_root": str(RAW_ROOT), "designs": {}}
    for d in load_designs():
        name, pdk, top = d["name"], d["pdk"], d["top"]
        ddir = RAW_ROOT / name
        ctrl_pwr = parse_power_json(ddir / "power/control_power.json")
        faeco_pwr = parse_power_json(ddir / "power/faeco_best_power.json")
        row = {
            "pdk": pdk, "top": top,
            "wns_budget_ps": d["wns_budget_ps"], "tns_budget_ps": d["tns_budget_ps"],
            "ref_views": d["ref_views"],
            "faeco_best_area_saved_um2": d["faeco_best"]["area_saved_um2"],
            "control_total_power_W": ctrl_pwr["Total"]["total"],
            "control_comb_power_W": ctrl_pwr["Combinational"]["total"],
            "control_leakage_W": ctrl_pwr["Total"]["leakage"],
            "faeco_total_power_W": faeco_pwr["Total"]["total"],
            "faeco_comb_power_W": faeco_pwr["Combinational"]["total"],
            "faeco_leakage_W": faeco_pwr["Total"]["leakage"],
            "faeco_total_power_delta_pct": 100.0 * (faeco_pwr["Total"]["total"] - ctrl_pwr["Total"]["total"]) / ctrl_pwr["Total"]["total"],
            "faeco_comb_power_delta_pct": 100.0 * (faeco_pwr["Combinational"]["total"] - ctrl_pwr["Combinational"]["total"]) / ctrl_pwr["Combinational"]["total"],
            "faeco_leakage_delta_pct": 100.0 * (faeco_pwr["Total"]["leakage"] - ctrl_pwr["Total"]["leakage"]) / ctrl_pwr["Total"]["leakage"],
            "arms": {},
        }
        for arm_name in ("native_default", "native_allow_setup"):
            adir = ddir / arm_name
            rsz_log = (adir / "rsz.log").read_text(encoding="utf-8", errors="replace")
            route_log = (adir / "route_rcx.log").read_text(encoding="utf-8", errors="replace")
            rsz_m = re.search(r"Resized (\d+) instances", rsz_log)
            rsz_rt = re.search(r"\[INFO RSZ-0507\] Runtime:\s*([0-9.]+)s", rsz_log)
            drc_txt = (adir / "drc.rpt").read_text(encoding="utf-8", errors="replace")
            drc_cnt = len(re.findall(r"(?m)^violation type: ", drc_txt))
            ant_m = re.findall(r"Found (\d+) net violations", route_log)
            ant_cnt = int(ant_m[-1]) if ant_m else 0
            diff = count_master_diffs(top, d["control"]["v"], adir / "routed.v", d["libs"]["TT"])
            views, deltas, failures = {}, {}, []
            if drc_cnt > 0:
                failures.append(f"drc={drc_cnt}")
            if ant_cnt > 0:
                failures.append(f"antenna={ant_cnt}")
            if diff["area_saved_um2"] <= 1e-9:
                failures.append("no_positive_area_recovery")
            for c in ("FF", "TT", "SS"):
                cv = parse_sta_log_ps(adir / f"sta_{c}.log", pdk)
                views[c] = cv
                rv = d["ref_views"][c]
                dw = cv["setup_wns_ps"] - rv["setup_wns_ps"]
                dt = cv["setup_tns_ps"] - rv["setup_tns_ps"]
                dh = cv["hold_wns_ps"] - rv["hold_wns_ps"]
                deltas[c] = {"d_setup_wns_ps": dw, "d_setup_tns_ps": dt, "d_hold_wns_ps": dh, "abs_hold_wns_ps": cv["hold_wns_ps"]}
                if dw < -d["wns_budget_ps"] - 1e-6:
                    failures.append(f"{c}:setup_wns")
                if dt < -d["tns_budget_ps"][c] - 1e-6:
                    failures.append(f"{c}:setup_tns")
                if cv["hold_wns_ps"] < 0.0:
                    failures.append(f"{c}:abs_hold")
                if dh < -0.001 - 1e-9:
                    failures.append(f"{c}:rel_hold")
                if cv["has_slew_cap_viol"]:
                    failures.append(f"{c}:electrical_viol")
            npwr = parse_power_json(adir / "native_power.json")
            row["arms"][arm_name] = {
                "rsz_reported_resized": int(rsz_m.group(1)) if rsz_m else 0,
                "rsz_runtime_s": float(rsz_rt.group(1)) if rsz_rt else None,
                "final_area_saved_um2": diff["area_saved_um2"],
                "final_area_saved_pct": diff["area_saved_pct"],
                "final_resized_count": diff["resized_count"],
                "drc_markers": drc_cnt,
                "antenna_violations": ant_cnt,
                "views_ps": views,
                "deltas_vs_control_ps": deltas,
                "gate_failures": failures,
                "qualified_area_saved_um2": diff["area_saved_um2"] if not failures else 0.0,
                "native_total_power_W": npwr["Total"]["total"],
                "native_total_power_delta_pct": 100.0 * (npwr["Total"]["total"] - ctrl_pwr["Total"]["total"]) / ctrl_pwr["Total"]["total"],
            }
        verified["designs"][name] = row
        print(f"=== {name} ===")
        print(f"  FAECO best: area_saved={row['faeco_best_area_saved_um2']} um2 | P_tot {row['faeco_total_power_delta_pct']:+.4f}% | P_comb {row['faeco_comb_power_delta_pct']:+.4f}% | P_leak {row['faeco_leakage_delta_pct']:+.4f}%")
        for arm_name, a in row["arms"].items():
            dlt = a["deltas_vs_control_ps"]
            print(f"  {arm_name}: rsz={a['rsz_reported_resized']} area={a['final_area_saved_um2']:.4f} um2 ({a['final_area_saved_pct']:.4f}%) DRC={a['drc_markers']} ANT={a['antenna_violations']} | "
                  f"dWNS(FF/TT/SS)={dlt['FF']['d_setup_wns_ps']:+.2f}/{dlt['TT']['d_setup_wns_ps']:+.2f}/{dlt['SS']['d_setup_wns_ps']:+.2f} | "
                  f"dTNS(TT/SS)={dlt['TT']['d_setup_tns_ps']:+.2f}/{dlt['SS']['d_setup_tns_ps']:+.2f} | "
                  f"dHold(FF/TT/SS)={dlt['FF']['d_hold_wns_ps']:+.3f}/{dlt['TT']['d_hold_wns_ps']:+.3f}/{dlt['SS']['d_hold_wns_ps']:+.3f} | "
                  f"FAILS={a['gate_failures']}")
    out_path = EVIDENCE_DIR / "NATIVE_RECOVER_POWER_VERIFIED.json"
    out_path.write_text(json.dumps(verified, indent=2) + "\n", encoding="utf-8")
    print("Wrote", out_path, "sha256=", sha256(out_path))


if __name__ == "__main__":
    main()
