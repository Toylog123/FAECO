#!/usr/bin/env python3
"""Protected 2-net repair of the 2 M3 DRC markers on asap7/aes CONTROL, restoring ROUTED status, then full P0 qualification."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from types import SimpleNamespace

REPO = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
EVIDENCE = REPO / "project_docs/evidence"
IBEX = EVIDENCE / "tcad_ibex_20261123"
HOLDOUT = EVIDENCE / "tcad_holdout_20261123"
ANYTIME = Path("/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1")
sys.path[:0] = list(map(str, (IBEX, HOLDOUT, IBEX / "asap7_control", IBEX / "sky130_control")))

import compare_ibex as cmp
import qualify_asap7_control as audit
import qualify_sky_holdout as sky
from probe_gcd_local_route_reentry import independent_physical

OPENROAD = sky.OPENROAD
FLOW = audit.FLOW
STA = Path("/usr/local/bin/sta-3.1.0")
CORNERS = ("FF", "TT", "SS")
WORK = Path("/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes")
REPAIR = WORK / "repaired_control_v4"
TOP = "aes_cipher_top"
# Target the 2 violating M3 nets + immediate non-clock M3 neighbors within +-350 DBU of (18648, 33917)
MARKER_X, MARKER_Y, HALO = 18648, 33917, 350


def find_local_m3_open_nets(orig_def: Path) -> set[str]:
    txt = orig_def.read_text(encoding="utf-8")
    beg = txt.index("\nNETS ")
    end = txt.index("\nEND NETS", beg)
    open_nets = {"net4557", "net5205"}
    for ch in re.split(r"(?m)(?=^\s*-\s+\S+)", txt[beg:end])[1:]:
        m = re.match(r"^\s*-\s+(\S+)", ch)
        if not m:
            continue
        name = m.group(1)
        if "+ USE SIGNAL" not in ch or "clk" in name.lower():
            continue
        if " M3 " not in ch:
            continue
        for rx, ry in re.findall(r"\(\s*(\d+)\s+(\d+)(?:\s+\d+)?\s*\)", ch):
            if abs(int(rx) - MARKER_X) <= HALO and abs(int(ry) - MARKER_Y) <= HALO:
                open_nets.add(name)
                break
    return open_nets


def run(command, logfile, seconds):
    start = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
    with logfile.open("wb") as stream:
        result = subprocess.run(
            ["/usr/bin/timeout", "--kill-after=5s", f"{seconds}s", *map(str, command)],
            stdout=stream, stderr=subprocess.STDOUT, check=False, timeout=seconds + 15,
        )
    return {
        "command": list(map(str, command)),
        "returncode": result.returncode,
        "elapsed_raw_seconds": time.clock_gettime(time.CLOCK_MONOTONIC_RAW) - start,
        "log": cmp.bind(logfile),
    }


def canonical_sdc(path):
    return sorted(" ".join(line.split()) for line in path.read_text().splitlines() if line.strip() and not line.lstrip().startswith("#"))


def write_fixed_nets_def(orig_def: Path, fixed_def: Path, open_nets: set[str]):
    """Slice raw NETS section verbatim (preserving all ASAP7 RECT patchwires), marking untouched nets FIXED."""
    text = orig_def.read_text(encoding="utf-8")
    header = "\n".join(re.findall(r"(?m)^(?:VERSION|DIVIDERCHAR|BUSBITCHARS|DESIGN|UNITS) .+?;$", text))
    beg = text.index("\nNETS ")
    end = text.index("\nEND NETS", beg)
    net_section = text[beg:end]
    # Split per net entry starting with "\n- " or "\n  - "
    parts = re.split(r"(?m)(?=^\s*-\s+\S+)", net_section)
    out_parts = [parts[0]]
    fixed_count = 0
    for chunk in parts[1:]:
        m = re.match(r"^\s*-\s+(\S+)", chunk)
        name = m.group(1) if m else ""
        if name not in open_nets and "+ ROUTED " in chunk:
            chunk = chunk.replace("+ ROUTED ", "+ FIXED ", 1)
            fixed_count += 1
        out_parts.append(chunk)
    fixed_def.write_text(header + "".join(out_parts) + "\nEND NETS\nEND DESIGN\n", encoding="utf-8")
    return fixed_count


def write_unlocked_nets_def(routed_def: Path, unlocked_def: Path):
    """Exact same verbatim slice as audit_aes_unlocked_drc.py."""
    text = routed_def.read_text(encoding="utf-8")
    header = "\n".join(re.findall(r"(?m)^(?:VERSION|DIVIDERCHAR|BUSBITCHARS|DESIGN|UNITS) .+?;$", text))
    beg = text.index("\nNETS ")
    end = text.index("\nEND NETS", beg)
    net_section = text[beg:end]
    unlocked_section, _ = re.subn(r"\+ FIXED ", "+ ROUTED ", net_section)
    unlocked_def.write_text(header + unlocked_section + "\nEND NETS\nEND DESIGN\n", encoding="utf-8")


def main():
    REPAIR.mkdir(parents=True, exist_ok=True)
    orig_dir = WORK / "results/asap7/aes/base"
    orig_odb = orig_dir / "6_final.odb"
    orig_def = orig_dir / "6_final.def"
    orig_sdc = orig_dir / "6_final.sdc"
    orig_v = orig_dir / "6_final.v"
    source_sdc = FLOW / "designs/asap7/aes/constraint.sdc"
    orig_libs = {c: [FLOW / "platforms/asap7/lib/NLDM" / ("asap7sc7p5t_" + n.format(view=c)) for n in audit.LIBS] for c in CORNERS}
    libs = cmp.materialize_views(orig_libs, REPAIR / "libraries")

    open_nets = find_local_m3_open_nets(orig_def)
    fixed_def = REPAIR / "fixed_wires.def"
    fixed_cnt = write_fixed_nets_def(orig_def, fixed_def, open_nets)
    print(f"Prepared fixed_wires.def with {fixed_cnt} FIXED nets, opening {len(open_nets)} nets: {sorted(open_nets)}", flush=True)

    mid_odb = REPAIR / "mid_repaired.odb"
    mid_def = REPAIR / "mid_repaired.def"
    out_odb = REPAIR / "6_final.odb"
    out_def = REPAIR / "6_final.def"
    out_v = REPAIR / "6_final.v"
    out_sdc = REPAIR / "6_final.sdc"
    out_spef = REPAIR / "6_final.spef"
    drc_rpt = REPAIR / "5_route_drc.rpt"
    util_tcl = FLOW / "scripts/util.tcl"
    fastroute_tcl = FLOW / "platforms/asap7/fastroute.tcl"
    setrc_tcl = FLOW / "platforms/asap7/setRC.tcl"
    rcx_rules = FLOW / "platforms/asap7/rcx_patterns.rules"

    # Step 1: Protected DRT on only the 2 nets
    tcl1 = REPAIR / "step1_repair_drt.tcl"
    lines1 = [f"read_liberty {cmp.tcl(lib)}" for lib in libs["TT"]] + [
        f"read_db {cmp.tcl(orig_odb)}",
        f"read_def -floorplan_initialize {cmp.tcl(fixed_def)}",
        f"read_sdc {cmp.tcl(orig_sdc)}",
        f"source {cmp.tcl(setrc_tcl)}",
        "set ::env(MIN_ROUTING_LAYER) M2",
        "set ::env(MIN_CLK_ROUTING_LAYER) M4",
        "set ::env(MAX_ROUTING_LAYER) M7",
        "set ::env(ROUTING_LAYER_ADJUSTMENT) 0.25",
        f"source {cmp.tcl(fastroute_tcl)}",
        "set block [ord::get_db_block]",
        "foreach nname {" + " ".join(sorted(open_nets)) + "} {",
        "  set net [$block findNet $nname]",
        '  if { $net eq "NULL" } { continue }',
        "  set wire [$net getWire]",
        '  if { $wire ne "NULL" } { odb::dbWire_destroy $wire; puts "ERASED $nname" }',
        "}",
        f"detailed_route -output_drc {cmp.tcl(drc_rpt)} -droute_end_iter 64 -or_seed 2 -verbose 1",
        'puts "REPAIR_DRT_VIOLATIONS [detailed_route_num_drvs]"',
        f"write_def {cmp.tcl(mid_def)}",
        f"write_db {cmp.tcl(mid_odb)}",
        "puts STEP1_DONE",
        "exit",
    ]
    tcl1.write_text("\n".join(lines1) + "\n", encoding="utf-8")
    op1 = run([OPENROAD, "-no_init", "-no_splash", "-threads", "4", "-exit", tcl1], REPAIR / "step1_repair_drt.log", 360)
    if op1["returncode"] or "STEP1_DONE" not in (REPAIR / "step1_repair_drt.log").read_text(errors="replace"):
        print("STEP1 FAILED")
        return 1
    print(f"Step 1 protected DRT finished in {op1['elapsed_raw_seconds']:.2f}s", flush=True)

    # Step 2: Restore ROUTED status, verify DRC=0, run RCX, export clean 6_final.*
    unlocked_def = REPAIR / "unlocked_wires.def"
    write_unlocked_nets_def(mid_def, unlocked_def)
    tcl2 = REPAIR / "step2_unlock_rcx.tcl"
    lines2 = [f"read_liberty {cmp.tcl(lib)}" for lib in libs["TT"]] + [
        f"read_db {cmp.tcl(mid_odb)}",
        f"read_def -floorplan_initialize {cmp.tcl(unlocked_def)}",
        f"read_sdc {cmp.tcl(orig_sdc)}",
        f"source {cmp.tcl(setrc_tcl)}",
        f"drt::check_drc -output_file {cmp.tcl(drc_rpt)}",
        "check_antennas",
        f"set ::env(REPORTS_DIR) {cmp.tcl(REPAIR)}",
        f"source {cmp.tcl(util_tcl)}",
        f"write_verilog {cmp.tcl(out_v)} -remove_cells [find_physical_only_masters]",
        f"write_def {cmp.tcl(out_def)}",
        f"write_sdc {cmp.tcl(out_sdc)}",
        f"write_db {cmp.tcl(out_odb)}",
        "define_process_corner -ext_model_index 0 X",
        f"extract_parasitics -ext_model_file {cmp.tcl(rcx_rules)}",
        f"write_spef {cmp.tcl(out_spef)}",
        "puts STEP2_DONE",
        "exit",
    ]
    tcl2.write_text("\n".join(lines2) + "\n", encoding="utf-8")
    op2 = run([OPENROAD, "-no_init", "-no_splash", "-threads", "1", "-exit", tcl2], REPAIR / "step2_unlock_rcx.log", 300)
    if op2["returncode"] or "STEP2_DONE" not in (REPAIR / "step2_unlock_rcx.log").read_text(errors="replace"):
        print("STEP2 FAILED")
        return 1
    print(f"Step 2 unlock + DRC + RCX finished in {op2['elapsed_raw_seconds']:.2f}s", flush=True)

    # Step 3: Full P0 qualification
    cmp.TOP = TOP
    sdc_tcl = REPAIR / "source_sdc_readback.tcl"
    sdc_diag = REPAIR / "source_sdc_readback.sdc"
    sdc_tcl.write_text(
        "\n".join(f"read_liberty {cmp.tcl(lib)}" for lib in libs["TT"])
        + f"""
read_db {cmp.tcl(out_odb)}
read_sdc {cmp.tcl(source_sdc)}
unset_clock_latency [get_clocks clk]
set_propagated_clock [all_clocks]
write_sdc {cmp.tcl(sdc_diag)}
puts "QUALIFICATION_GUIDES [grt::have_routes]"
puts QUALIFICATION_SDC_COMPLETE
exit
"""
    )
    sop = run([OPENROAD, "-no_init", "-no_splash", "-threads", "1", "-exit", sdc_tcl], REPAIR / "source_sdc_readback.log", 90)
    sraw = Path(sop["log"]["path"]).read_text()
    left, right = canonical_sdc(sdc_diag), canonical_sdc(out_sdc)
    sdc_check = {
        "exact_canonical_commands": left == right,
        "source_only": sorted(set(left) - set(right)),
        "export_only": sorted(set(right) - set(left)),
        "source_readback": cmp.bind(sdc_diag),
        "operation": sop,
        "embedded_guides_available": bool(re.search(r"(?m)^QUALIFICATION_GUIDES (?:1|true)$", sraw)),
    }

    views = {}
    for c in CORNERS:
        ctcl = REPAIR / f"sta_{c}.tcl"
        ctcl.write_text(cmp.render_sta(libs[c], out_v, out_sdc, out_spef, report_setup_endpoints=True))
        info = run([STA, "-exit", ctcl], REPAIR / f"sta_{c}.log", 180)
        raw = Path(info["log"]["path"]).read_text()
        views[c] = cmp.parse_sta(raw) | {"operation": info, "script": cmp.bind(ctcl)}
        print(f"repaired asap7/aes {c} setup={views[c]['setup_wns_ps']:+.3f} hold={views[c]['hold_wns_ps']:+.6f} ps elec={views[c]['electrical']}", flush=True)

    refs = {kind: cmp.bind(REPAIR / f"6_final.{kind}") for kind in ("odb", "def", "v", "sdc", "spef")}
    orig_run_process = cmp.run_process
    cmp.run_process = lambda argv, logfile, timeout, *, env=None: orig_run_process(argv, logfile, max(timeout, 180.0), env=env)
    try:
        physical_audit = independent_physical(SimpleNamespace(args=SimpleNamespace(openroad=OPENROAD)), refs, REPAIR / "independent")
    finally:
        cmp.run_process = orig_run_process

    os.environ.update(FAECO_DESIGN_TOP=TOP, FAECO_SEC_LIBRARIES=json.dumps([str(p) for p in libs["TT"]]))
    sec_op = run([ANYTIME / "sec_native.py", orig_v, out_v, REPAIR / "sec"], REPAIR / "sec.log", 240)
    sec_proof = json.loads((REPAIR / "sec/receipt.json").read_text()) if (REPAIR / "sec/receipt.json").exists() else {}
    sec_res = {
        "operation": sec_op, "result": sec_proof,
        "passed": sec_op["returncode"] == 0 and sec_proof.get("passed") is True and sec_proof.get("proven", 0) > 0 and sec_proof.get("unproven") == 0,
    }

    drc_cnt = len(re.findall(r"(?m)^violation type: ", drc_rpt.read_text(encoding="utf-8", errors="replace"))) if drc_rpt.is_file() else -1
    failures = (["source_sdc_export_drift"] if not sdc_check["exact_canonical_commands"] else []) + physical_audit["failures"]
    if drc_cnt != 0:
        failures.append(f"repair_drc={drc_cnt}")
    if not sec_res["passed"]:
        failures.append("sec_model")
    for c, v in views.items():
        if v["hold_wns_ps"] < 0 or v["hold_tns_ps"] < 0:
            failures.append(c + ":negative_hold")
        if any(v["electrical"].values()):
            failures.append(c + ":absolute_electrical")

    status = "hold_qualified" if not failures else "qualification_incomplete"
    receipt = dict(
        platform="asap7", design="aes", top=TOP, status=status, failures=failures,
        driver=cmp.bind(Path(__file__)),
        original_native_odb=cmp.bind(orig_odb),
        repair_step1=op1, repair_step2=op2,
        control_output_paths=refs,
        source_sdc=cmp.bind(source_sdc),
        source_sdc_comparison=sdc_check,
        views=views,
        detailed_route_drc_count=drc_cnt,
        native_drc_report=cmp.bind(drc_rpt),
        raw_reports=[cmp.bind(p) for p in (WORK / "input_manifest.log", WORK / "command.sh", WORK / "producer.log", REPAIR / "step1_repair_drt.log", REPAIR / "step2_unlock_rcx.log", drc_rpt)],
        independent=physical_audit,
        sec=sec_res,
        library_paths={c: list(map(str, ls)) for c, ls in orig_libs.items()},
        used_libraries={c: [cmp.bind(l) for l in ls] for c, ls in libs.items()},
        all_views_nonnegative_hold=all(v["hold_wns_ps"] >= 0 and v["hold_tns_ps"] >= 0 for v in views.values()),
        sta_binary=cmp.bind(STA),
        source_sdc_semantics={
            "sdc_time_unit": "ps", "period_sdc_units": 380.0, "period_ps": 380.0,
            "io_delay_sdc_units": 76.0, "virtual_latency_sdc_units": 77.930,
            "core_clock": "clk", "clock_port": "clk",
            "source_io_matches_all_nonclock_inputs_and_outputs": sdc_check["exact_canonical_commands"],
        },
        view_liberty_groups={c: [cmp.bind(l) for l in ls] for c, ls in orig_libs.items()},
        tool_openroad=cmp.bind(OPENROAD), tool_opensta=cmp.bind(STA),
    )
    out_json = REPAIR / "CONTROL.json"
    out_json.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"FINAL STATUS: {status} failures={failures} independent_drc={physical_audit['drc']} ant={physical_audit['antenna']} sec={sec_proof.get('proven')}/{sec_proof.get('unproven')}", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
