#!/usr/bin/env python3
"""Measure matched TT real-SPEF power of the newly unlocked 9-gate SKY130HD AES endpoint (98.8448 um2) vs CONTROL."""
import json
import subprocess
import sys
from pathlib import Path

EVIDENCE = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence")
sys.path.insert(0, str(EVIDENCE / "tcad_ibex_20261123"))
import compare_ibex as cmp

OR_BIN = "/home/toylog/.cache/bazel/_bazel_toylog/c540bbdc4bbb635360729b4d7a91c803/execroot/_main/bazel-out/k8-opt/bin/openroad_unstamped"
TT_LIB = "/home/toylog/faeco_eda/orfs/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
CTRL_DIR = Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes/ss_hold_targeted_v2b")
VERIFIED = json.loads((EVIDENCE / "tcad_boxed_drc_20261126/BOXED_DRC_VERIFIED.json").read_text())

sky_boxed = [a for a in VERIFIED["sky130hd_aes"]["arms"] if a["order"] == "forward" and a["diagnosis_mode"] == "boxed"][0]
ep = sky_boxed["best_endpoint"]
out_dir = Path("/tmp/faeco_sky_aes_9g_power")
out_dir.mkdir(parents=True, exist_ok=True)


def run_power(tag, odb, spef):
    pj = out_dir / f"{tag}.json"
    tcl = out_dir / f"{tag}.tcl"
    tcl.write_text(
        f"read_liberty {cmp.tcl(TT_LIB)}\n"
        f"read_db {cmp.tcl(odb)}\n"
        f"read_sdc {cmp.tcl(CTRL_DIR / '6_final.sdc')}\n"
        f"read_spef {cmp.tcl(spef)}\n"
        f"report_power -digits 9 -format json > {cmp.tcl(pj)}\n"
        f"puts PWR_DONE\nexit\n"
    )
    r = subprocess.run([OR_BIN, "-no_init", "-no_splash", "-threads", "1", "-exit", str(tcl)], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    txt = pj.read_text()
    return json.loads(txt[txt.index("{"):])


ctrl_p = run_power("control", CTRL_DIR / "6_final.odb", CTRL_DIR / "6_final.spef")
ep9_p = run_power("ep9g", ep["odb_path"], ep["spef_path"])

res = {
    "endpoint_actions": ep["actions"],
    "views_delta_ps": ep["views_delta_ps"],
    "control_power": ctrl_p,
    "ep9g_power": ep9_p,
    "delta_pct": {
        "total": 100.0 * (ep9_p["Total"]["total"] - ctrl_p["Total"]["total"]) / ctrl_p["Total"]["total"],
        "combinational": 100.0 * (ep9_p["Combinational"]["total"] - ctrl_p["Combinational"]["total"]) / ctrl_p["Combinational"]["total"],
        "leakage": 100.0 * (ep9_p["Total"]["leakage"] - ctrl_p["Total"]["leakage"]) / ctrl_p["Total"]["leakage"],
    },
}
(EVIDENCE / "tcad_boxed_drc_20261126/SKY130_AES_9G_POWER.json").write_text(json.dumps(res, indent=2) + "\n")
print("9-gate views_delta_ps:", json.dumps(ep["views_delta_ps"], indent=2))
print("9-gate power delta_pct:", json.dumps(res["delta_pct"], indent=2))
