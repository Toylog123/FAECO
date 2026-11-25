#!/usr/bin/env python3
"""Qualify frozen original-constraint ASAP7 AES (aes_cipher_top) CONTROL endpoint."""

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
TOP = "aes_cipher_top"


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


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def canonical_sdc(path):
    return sorted(" ".join(line.split()) for line in path.read_text().splitlines() if line.strip() and not line.lstrip().startswith("#"))


def original_sdc_check(sdc, original, libs, odb, out):
    script = out / "source_sdc_readback.tcl"
    diagnostic = out / "source_sdc_readback.sdc"
    script.write_text(
        "\n".join(f"read_liberty {cmp.tcl(lib)}" for lib in libs)
        + f"""
read_db {cmp.tcl(odb)}
read_sdc {cmp.tcl(original)}
unset_clock_latency [get_clocks clk]
set_propagated_clock [all_clocks]
write_sdc {cmp.tcl(diagnostic)}
puts "QUALIFICATION_GUIDES [grt::have_routes]"
puts QUALIFICATION_SDC_COMPLETE
exit
"""
    )
    op = run([OPENROAD, "-no_init", "-no_splash", "-threads", "1", "-exit", script], out / "source_sdc_readback.log", 90)
    raw = Path(op["log"]["path"]).read_text()
    if op["returncode"] or "QUALIFICATION_SDC_COMPLETE" not in raw or re.search(r"(?m)^\s*(?:\[ERROR|Error:)", raw):
        return {"exact_canonical_commands": False, "source_readback": None, "operation": op, "comparison_error": "source_sdc_replay_failed"}
    left, right = canonical_sdc(diagnostic), canonical_sdc(sdc)
    return {
        "exact_canonical_commands": left == right,
        "source_only": sorted(set(left) - set(right)),
        "export_only": sorted(set(right) - set(left)),
        "source_readback": cmp.bind(diagnostic),
        "operation": op,
        "embedded_guides_available": bool(re.search(r"(?m)^QUALIFICATION_GUIDES (?:1|true)$", raw)),
    }


def sec(top, netlist, libraries, out):
    runner = ANYTIME / "sec_native.py"
    os.environ.update(FAECO_DESIGN_TOP=top, FAECO_SEC_LIBRARIES=json.dumps([str(p) for p in libraries]))
    op = run([runner, netlist, netlist, out / "sec"], out / "sec.log", 240)
    path = out / "sec/receipt.json"
    proof = json.loads(path.read_text()) if path.exists() else {}
    return {
        "operation": op,
        "result": proof,
        "passed": op["returncode"] == 0 and proof.get("passed") is True and proof.get("proven", 0) > 0 and proof.get("unproven") == 0,
    }


def main():
    stage = Path("asap7/aes/base")
    endpoint, logs, reports = [WORK / d / stage for d in ("results", "logs", "reports")]
    source = FLOW / "designs/asap7/aes/constraint.sdc"
    route_json = logs / "5_2_route.json"
    route_drc = reports / "5_route_drc.rpt"
    out = WORK / "qualification"
    out.mkdir(parents=True, exist_ok=True)
    if (WORK / "producer.rc").read_text().strip() != "0":
        raise RuntimeError("ORFS producer did not finish successfully")
    native = json.loads(route_json.read_text())
    frozen_source = cmp.bind(source)
    manifest = (WORK / "input_manifest.log").read_text()
    if f'{frozen_source["sha256"]}  {source}' not in manifest:
        raise RuntimeError("original SDC drifted after ORFS launch")
    rcx_reads = re.findall(r"(?m)^\[INFO RCX-0045\] Extract (\d+) nets, (\d+) rsegs, (\d+) caps, (\d+) ccs$", (logs / "6_report.log").read_text())
    if len(rcx_reads) != 1 or any(int(v) <= 0 for v in rcx_reads[0]):
        raise RuntimeError("native 6_report does not certify coupling RCX extraction")
    orig_libs = {c: [FLOW / "platforms/asap7/lib/NLDM" / ("asap7sc7p5t_" + n.format(view=c)) for n in audit.LIBS] for c in CORNERS}
    libs = cmp.materialize_views(orig_libs, out / "libraries")
    physical = {kind: endpoint / f"6_final.{kind}" for kind in ("odb", "def", "v", "sdc", "spef")}
    refs = {kind: cmp.bind(path) for kind, path in physical.items()}
    if not all(item["bytes"] for item in refs.values()):
        raise RuntimeError("missing physical payload")
    native_antenna = {key: native[f"detailedroute__antenna__violating__{key}"] for key in ("nets", "pins")}
    cmp.TOP = TOP
    sdc = original_sdc_check(physical["sdc"], source, libs["TT"], physical["odb"], out)
    views = {}
    for c in CORNERS:
        tcl = out / f"sta_{c}.tcl"
        text = cmp.render_sta(libs[c], physical["v"], physical["sdc"], physical["spef"], report_setup_endpoints=True)
        tcl.write_text(text)
        run_info = run([STA, "-exit", tcl], out / f"sta_{c}.log", 180)
        raw = Path(run_info["log"]["path"]).read_text()
        if run_info["returncode"] or "IBEX_STA_COMPLETE" not in raw or re.search(r"(?m)^\s*(?:\[ERROR|Error:)", raw):
            raise RuntimeError(f"{c} STA incomplete: {run_info}")
        views[c] = cmp.parse_sta(raw) | {"operation": run_info, "script": cmp.bind(tcl)}
        print(f"asap7/aes {c} setup={views[c]['setup_wns_ps']:+.3f} hold={views[c]['hold_wns_ps']:+.6f} ps elec={views[c]['electrical']}", flush=True)
    # Give independent whole-block DRC a generous 180s timeout (larger than 45s)
    orig_run_process = cmp.run_process
    def longer_run(argv, logfile, timeout, *, env=None):
        return orig_run_process(argv, logfile, max(timeout, 180.0), env=env)
    cmp.run_process = longer_run
    try:
        physical_audit = independent_physical(SimpleNamespace(args=SimpleNamespace(openroad=OPENROAD)), refs, out / "independent")
    finally:
        cmp.run_process = orig_run_process
    proof = sec(TOP, physical["v"], libs["TT"], out)
    failures = (["source_sdc_export_drift"] if not sdc["exact_canonical_commands"] else []) + physical_audit["failures"]
    if native["detailedroute__route__drc_errors"] or route_drc.stat().st_size:
        failures.append("native_drc")
    if any(native_antenna.values()):
        failures.append("native_antenna")
    if not proof["passed"]:
        failures.append("sec_model")
    for c, v in views.items():
        if v["hold_wns_ps"] < 0 or v["hold_tns_ps"] < 0:
            failures.append(c + ":negative_hold")
        if any(v["electrical"].values()):
            failures.append(c + ":absolute_electrical")
    if refs != {k: cmp.bind(v) for k, v in physical.items()} or frozen_source != cmp.bind(source):
        failures.append("physical_input_drift")
    if not failures:
        status = "hold_qualified"
    elif any(f.endswith(":negative_hold") for f in failures):
        status = "hold_infeasible"
    else:
        status = "qualification_incomplete"
    receipt = dict(
        platform="asap7", design="aes", top=TOP, status=status, failures=failures,
        driver=cmp.bind(Path(__file__)), control_output_paths=refs, source_sdc=frozen_source,
        native_rcx=dict(zip(("nets", "rsegs", "caps", "couplings"), map(int, rcx_reads[0]))),
        source_sdc_comparison=sdc, views=views, native_antenna=native_antenna,
        detailed_route_drc_count=native["detailedroute__route__drc_errors"],
        native_drc_report=cmp.bind(route_drc), independent=physical_audit, sec=proof,
        library_paths={c: list(map(str, ls)) for c, ls in orig_libs.items()},
        used_libraries={c: [cmp.bind(l) for l in ls] for c, ls in libs.items()},
        raw_reports=[cmp.bind(p) for p in (WORK / "input_manifest.log", WORK / "command.sh", WORK / "producer.log", route_json, route_drc, logs / "6_report.json")],
        all_views_nonnegative_hold=all(v["hold_wns_ps"] >= 0 and v["hold_tns_ps"] >= 0 for v in views.values()),
        sta_binary=cmp.bind(STA),
        source_sdc_semantics={
            "sdc_time_unit": "ps", "period_sdc_units": 380.0, "period_ps": 380.0,
            "io_delay_sdc_units": 76.0, "virtual_latency_sdc_units": 77.930,
            "core_clock": "clk", "clock_port": "clk",
            "source_io_matches_all_nonclock_inputs_and_outputs": sdc["exact_canonical_commands"],
        },
        view_liberty_groups={c: [cmp.bind(l) for l in ls] for c, ls in orig_libs.items()},
        tool_openroad=cmp.bind(OPENROAD), tool_opensta=cmp.bind(STA),
        counts={"qualification_sta": len(views), "candidate_route": 0, "candidate_sta": 0, "candidate_sec": 0},
    )
    write(out / "CONTROL.json", receipt)
    print(status, failures, out / "CONTROL.json", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
