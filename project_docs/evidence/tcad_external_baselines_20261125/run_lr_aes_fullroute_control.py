#!/usr/bin/env python3
"""Control check: run the exact same 18-gate LR commit on sky130hd/aes with STANDARD full reroute
(without FAECO's boxed pre-DRT DRC protected-routing backend) to isolate the causal contribution of our backend."""
import json
import re
import sys
from pathlib import Path

REPO = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
EXT_DIR = REPO / "project_docs/evidence/tcad_external_baselines_20261125"
IBEX_DIR = REPO / "project_docs/evidence/tcad_ibex_20261123"
sys.path.insert(0, str(EXT_DIR))
sys.path.insert(0, str(IBEX_DIR))

import compare_ibex as cmp
import run_native_recover_power as nrp

lr_data = json.loads((EXT_DIR / "LR_4DESIGNS_VERIFIED.json").read_text())
aes_lr = lr_data["designs"]["sky130hd_aes"]
aes_cfg = [d for d in nrp.load_designs() if d["name"] == "sky130hd_aes"][0]

out_dir = Path("/home/toylog/faeco_tcad_lr_4designs_20261126_v1/sky130hd_aes_standard_fullroute")
out_dir.mkdir(parents=True, exist_ok=True)

# Swap the exact same 18 LR-committed masters in-place on CONTROL ODB, then run standard OpenROAD full reroute + RCX + 3-corner STA
ctrl = aes_cfg["control"]
tt_libs = aes_cfg["libs"]["TT"]
flow = aes_cfg["flow"]
util_tcl = "/home/toylog/faeco_eda/orfs/flow/scripts/util.tcl"
out_odb = out_dir / "routed.odb"
out_def = out_dir / "routed.def"
out_v = out_dir / "routed.v"
out_spef = out_dir / "routed.spef"
drc_rpt = out_dir / "drc.rpt"

swap_lines = []
for aid in aes_lr["lr_solve"]["committed_actions"]:
    inst_raw, tgt = aid.split("=", 1)
    inst_odb = cmp.canonical_odb_name(inst_raw)
    swap_lines.append(f'set _i [[ord::get_db_block] findInst "{inst_odb}"]; $_i swapMaster [[ord::get_db] findMaster "{tgt}"]')

rlines = [f"read_liberty {cmp.tcl(lib)}" for lib in tt_libs] + [
    f"read_db {cmp.tcl(ctrl['odb'])}",
    f"read_sdc {cmp.tcl(ctrl['sdc'])}",
    f"source {cmp.tcl(flow['setRC.tcl'])}",
    "set ::env(MIN_ROUTING_LAYER) met1",
    "set ::env(MIN_CLK_ROUTING_LAYER) met3",
    "set ::env(MAX_ROUTING_LAYER) met5",
    "set ::env(ROUTING_LAYER_ADJUSTMENT) 0.25",
    f"set ::env(REPORTS_DIR) {cmp.tcl(out_dir)}",
    "remove_fillers",
    *swap_lines,
    "detailed_placement",
    "check_placement -verbose",
    "foreach _n [[ord::get_db_block] getNets] { if { [$_n getSigType] ni {POWER GROUND CLOCK} } { set _w [$_n getWire]; if { $_w ne \"NULL\" } { odb::dbWire_destroy $_w } } }",
    f"source {cmp.tcl(flow['fastroute.tcl'])}",
    "pin_access",
    "global_route -congestion_iterations 30 -allow_congestion",
    f"detailed_route -output_drc {cmp.tcl(drc_rpt)} -droute_end_iter 64 -verbose 0",
    "check_antennas",
    f"write_db {cmp.tcl(out_odb)}",
    f"write_def {cmp.tcl(out_def)}",
    f"source {cmp.tcl(util_tcl)}",
    f"write_verilog {cmp.tcl(out_v)} -remove_cells [find_physical_only_masters]",
    "define_process_corner -ext_model_index 0 X",
    f"extract_parasitics -ext_model_file {cmp.tcl(flow['rcx_patterns.rules'])}",
    f"write_spef {cmp.tcl(out_spef)}",
    "puts LR_FULLROUTE_DONE",
    "exit",
]
rtcl = out_dir / "route_rcx.tcl"
rtcl.write_text("\n".join(rlines) + "\n", encoding="utf-8")
rop = nrp.run_cmd([nrp.OR_BIN, "-no_init", "-no_splash", "-threads", "4", "-exit", rtcl], out_dir / "route_rcx.log", 600)
rlog = (out_dir / "route_rcx.log").read_text(encoding="utf-8", errors="replace")
assert rop["returncode"] == 0 and "LR_FULLROUTE_DONE" in rlog, rlog[-600:]
drc_count = len(re.findall(r"(?m)^violation type: ", drc_rpt.read_text(encoding="utf-8", errors="replace"))) if drc_rpt.is_file() else -1
ant_m = re.findall(r"Found (\d+) net violations", rlog)
ant_count = int(ant_m[-1]) if ant_m else None

views = {}
deltas = {}
fails = []
if drc_count > 0:
    fails.append(f"drc={drc_count}")
if ant_count not in (None, 0):
    fails.append(f"antenna={ant_count}")

for corner in ("FF", "TT", "SS"):
    ctcl = out_dir / f"sta_{corner}.tcl"
    clines = [f"read_liberty {cmp.tcl(lib)}" for lib in aes_cfg["libs"][corner]] + [
        f"read_db {cmp.tcl(out_odb)}",
        f"read_sdc {cmp.tcl(ctrl['sdc'])}",
        f"read_spef {cmp.tcl(out_spef)}",
        "report_worst_slack -max -digits 6",
        "report_worst_slack -min -digits 6",
        "report_tns -max",
        "report_check_types -max_slew -max_capacitance -max_fanout -violators",
        "puts STA_DONE",
        "exit",
    ]
    ctcl.write_text("\n".join(clines) + "\n", encoding="utf-8")
    sop = nrp.run_cmd([nrp.OR_BIN, "-no_init", "-no_splash", "-threads", "1", "-exit", ctcl], out_dir / f"sta_{corner}.log", 180)
    slog = (out_dir / f"sta_{corner}.log").read_text(encoding="utf-8", errors="replace")
    def grab(pat):
        m = re.search(pat, slog)
        return float(m.group(1)) * 1000.0 if m else None
    cv = {
        "setup_wns_ps": grab(r"(?m)^worst slack max\s+([+-]?\d+(?:\.\d+)?)"),
        "hold_wns_ps": grab(r"(?m)^worst slack min\s+([+-]?\d+(?:\.\d+)?)"),
        "setup_tns_ps": grab(r"(?m)^tns max\s+([+-]?\d+(?:\.\d+)?)"),
        "has_slew_cap_viol": "VIOLATED" in slog,
    }
    views[corner] = cv
    rv = aes_cfg["ref_views"][corner]
    dw = cv["setup_wns_ps"] - rv["setup_wns_ps"]
    dt = cv["setup_tns_ps"] - rv["setup_tns_ps"]
    dh = cv["hold_wns_ps"] - rv["hold_wns_ps"]
    deltas[corner] = {"d_setup_wns_ps": dw, "d_setup_tns_ps": dt, "d_hold_wns_ps": dh, "abs_hold_wns_ps": cv["hold_wns_ps"]}
    if dw < -aes_cfg["wns_budget_ps"] - 1e-6:
        fails.append(f"{corner}:setup_wns")
    if dt < -aes_cfg["tns_budget_ps"][corner] - 1e-6:
        fails.append(f"{corner}:setup_tns")
    if cv["hold_wns_ps"] < 0.0:
        fails.append(f"{corner}:abs_hold")
    if dh < -0.001 - 1e-9:
        fails.append(f"{corner}:rel_hold")
    if cv["has_slew_cap_viol"]:
        fails.append(f"{corner}:electrical")

res = {
    "route_elapsed_s": rop["elapsed_raw_seconds"],
    "drc_markers": drc_count,
    "antenna_violations": ant_count,
    "deltas_vs_control": deltas,
    "failures": fails,
    "passed_all_gates": not fails,
    "qualified_area_saved_um2": 197.6896 if not fails else 0.0,
}
lr_data["sky130hd_aes_lr_standard_fullroute"] = res
(EXT_DIR / "LR_4DESIGNS_VERIFIED.json").write_text(json.dumps(lr_data, indent=2) + "\n", encoding="utf-8")
print("SKY130HD AES LR standard fullroute:", json.dumps(res, indent=2))
