#!/usr/bin/env bash
# Build and qualify the native ASAP7 UART CONTROL from its original ORFS SDC.
set -euo pipefail

exec python3 -B - "${BASH_SOURCE[0]}" "$@" <<'PY'
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time


SCRIPT = Path(sys.argv[1]).resolve(strict=True)
sys.path.insert(0, str(SCRIPT.parent.parent / "tcad_ibex_20261123" / "asap7_control"))
import qualify_asap7_control as audit


FLOW = audit.FLOW
DESIGN = FLOW / "designs/asap7/uart"
RTL = FLOW / "designs/src/uart"
PLATFORM = FLOW / "platforms/asap7"
SOURCE_SDC = DESIGN / "constraint.sdc"
OPENROAD_SOURCE = Path("/home/toylog/rseco_timing/vendor/OpenROAD-b511b6a")
OPENROAD = OPENROAD_SOURCE / "bazel-bin/openroad"
YOSYS = Path("/usr/local/bin/yosys")
ORFS_HEAD = "da8f092a02a8e75658cc3100691aabff05f35629"
OPENROAD_HEAD = "b511b6a2bc936844b0319efc8b4972bb4ad7d911"
TOOL_HASHES = {
    OPENROAD: "2d9662715130538b50e93b614c33099a5e183eef0cc31b642099daea8d203e19",
    YOSYS: "4f8e613d835c248c63f0e487fb956e1667b9291ef87f0514fffb4dc07878d379",
    audit.STA: "4f0727aefff89b124f09f3a782d45bb8e96a895fd2425f87bdb6b56fdcc16628",
}
WORK_DEFAULT = Path("/home/toylog/faeco_tcad_holdout_qualification_20261124_v1/asap7/uart")
STAGE = Path("asap7/uart/base")
PRODUCER_TIMEOUT = 1800
PORT_COUNTS = {"input": 28, "output": 15}


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], text=True, timeout=10).strip()


def json_write(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def preflight():
    if git(FLOW, "rev-parse", "HEAD") != ORFS_HEAD or git(OPENROAD_SOURCE, "rev-parse", "HEAD") != OPENROAD_HEAD:
        raise RuntimeError("unexpected ORFS or OpenROAD revision")
    dirty = git(FLOW, "status", "--porcelain", "--untracked-files=all", "--",
                "Makefile", "scripts", "designs/asap7/uart", "designs/src/uart", "platforms/asap7")
    if dirty:
        raise RuntimeError(f"dirty UART flow inputs:\n{dirty}")
    spec = audit.expected_sdc(audit.read_text(SOURCE_SDC), pinned=(270.0, 0.2, "clk", "clk", 66.270))
    libraries = {corner: [PLATFORM / "lib/NLDM" / ("asap7sc7p5t_" + lib.format(view=corner))
                          for lib in audit.LIBS] for corner in audit.VIEWS}
    inputs = [*TOOL_HASHES, DESIGN / "config.mk", SOURCE_SDC, FLOW / "Makefile",
              PLATFORM / "config.mk", PLATFORM / "rcx_patterns.rules", *sorted(RTL.glob("*.v")),
              *(lib for group in libraries.values() for lib in group)]
    refs = {str(path): audit.file_ref(path) for path in inputs}
    for path, expected in TOOL_HASHES.items():
        if refs[str(path)]["sha256"] != expected:
            raise RuntimeError(f"unexpected pinned executable: {path}")
    return spec, libraries, refs


def produce(work, refs):
    work.mkdir(parents=True, exist_ok=False)
    target = work / "logs" / STAGE / "6_report.log"
    command = ["/usr/bin/timeout", "--signal=TERM", "--kill-after=15s", f"{PRODUCER_TIMEOUT}s",
               "taskset", "-c", "0-5", "/usr/bin/time", "-p", "/usr/bin/make", "--no-print-directory", "-j1",
               "-C", str(FLOW), f"DESIGN_CONFIG={DESIGN / 'config.mk'}", f"WORK_HOME={work}", "FLOW_VARIANT=base",
               f"OPENROAD_EXE={OPENROAD}", f"YOSYS_EXE={YOSYS}", "NUM_CORES=4", str(target)]
    receipt = {"status": "started", "command": command, "orfs_git_head": ORFS_HEAD,
               "openroad_git_head": OPENROAD_HEAD, "producer_launcher": audit.file_ref(SCRIPT),
               "inputs_before": refs}
    path = work / "producer_receipt.json"
    json_write(path, receipt)
    print(f"Building native UART CONTROL in {work}", flush=True)
    start = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
    with (work / "producer.log").open("wb") as stream:
        run = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, check=False)
    receipt.update(status="finished", returncode=run.returncode,
                   raw_wall_seconds=time.clock_gettime(time.CLOCK_MONOTONIC_RAW) - start)
    json_write(path, receipt)
    if run.returncode:
        raise RuntimeError(f"native UART flow exited {run.returncode}; see {work / 'producer.log'}")
    receipt["inputs_after"] = preflight()[2]
    json_write(path, receipt)


def qualify(work, output, spec, libraries, refs):
    receipt_path = work / "producer_receipt.json"
    receipt = json.loads(audit.read_text(receipt_path))
    if receipt.get("returncode") != 0 or receipt.get("inputs_before") != refs or receipt.get("inputs_after") != refs:
        raise RuntimeError("native producer is incomplete or its input bindings drifted")
    artifact = work / "results" / STAGE / "6_final"
    logs, reports = work / "logs" / STAGE, work / "reports" / STAGE
    drc_report = reports / "5_route_drc.rpt"
    physical = {ext: artifact.with_suffix(f".{ext}") for ext in ("odb", "def", "v", "sdc", "spef")}
    physical_refs = {ext: audit.file_ref(path) for ext, path in physical.items()}
    if any(binding["bytes"] == 0 for binding in physical_refs.values()):
        raise RuntimeError("empty final UART physical artifact")
    route = json.loads(audit.read_text(logs / "5_2_route.json"))
    drc = route["detailedroute__route__drc_errors"]
    antenna = {kind: route[f"detailedroute__antenna__violating__{kind}"] for kind in ("nets", "pins")}
    if drc or drc_report.stat().st_size or any(antenna.values()):
        raise RuntimeError(f"native UART route gate failed: DRC={drc}, antenna={antenna}; see {logs}")
    exported_ports, extra = audit.audit_final_sdc(audit.read_text(physical["sdc"]), spec)
    if {kind: len(names) for kind, names in exported_ports.items()} != PORT_COUNTS or extra:
        raise RuntimeError(f"UART export does not match original ports or SDC commands: extra={extra}")

    audit.TOP = "uart"
    output.mkdir(exist_ok=False)
    views = {}
    for corner, libs in libraries.items():
        values = audit.collect_view(corner, artifact, libs, exported_ports, output)
        views[corner] = values
        print(f"UART {corner}: setup WNS/TNS {values['setup_wns_ps']:+.6f}/{values['setup_tns_ps']:+.6f} ps; "
              f"hold WNS/TNS {values['hold_wns_ps']:+.6f}/{values['hold_tns_ps']:+.6f} ps", flush=True)
    if {ext: audit.file_ref(path) for ext, path in physical.items()} != physical_refs or preflight()[2] != refs:
        raise RuntimeError("physical or timing inputs drifted during UART readback")
    native = json.loads(audit.read_text(logs / "6_report.json"))
    hold_pass = all(view["hold_wns_ps"] >= 0 for view in views.values())
    status = "hold_qualified" if hold_pass else "hold_infeasible"
    state = {
        "schema_version": 1, "design": "uart", "top": audit.TOP, "platform": "asap7", "status": status,
        "producer": audit.file_ref(receipt_path), "launcher": audit.file_ref(SCRIPT),
        "shared_qualifier": audit.file_ref(Path(audit.__file__)), "source_sdc": refs[str(SOURCE_SDC)],
        "control_output_paths": physical_refs, "detailed_route_drc_count": drc, "native_antenna": antenna,
        "source_sdc_semantics": {**spec, "expanded_port_counts": PORT_COUNTS,
                                 "source_io_matches_all_nonclock_inputs_and_outputs": True,
                                 "propagated_after_cts": spec["core_clock"]},
        "views": views, "view_liberty_groups": {corner: [refs[str(lib)] for lib in libs]
                                               for corner, libs in libraries.items()},
        "sta_binary": refs[str(audit.STA)], "all_views_nonnegative_hold": hold_pass,
        "native_finish_stdcell_area_um2": native.get("finish__design__instance__area__stdcell"),
        "native_finish_stdcell_count": native.get("finish__design__instance__count__stdcell"),
        "native_tt_setup_wns_ps": native.get("finish__timing__setup__ws"),
        "native_tt_hold_wns_ps": native.get("finish__timing__hold__ws"),
        "raw_reports": [audit.file_ref(path) for path in [work / "producer.log", logs / "5_2_route.log",
                        logs / "5_2_route.json", logs / "6_report.log", logs / "6_report.json", drc_report]],
        "counts": {"qualification_sta": len(views), "candidate_routes": 0, "candidate_sta": 0, "candidate_sec": 0},
    }
    json_write(output / "CONTROL.json", state)
    print(f"{status} {output / 'CONTROL.json'}", flush=True)


parser = argparse.ArgumentParser(description="Build and qualify native ASAP7 UART without changing its SDC.")
parser.add_argument("work", nargs="?", type=Path, default=WORK_DEFAULT)
mode = parser.add_mutually_exclusive_group()
mode.add_argument("--check-inputs", action="store_true", help="check exact source and tool inputs without running EDA")
mode.add_argument("--qualify-only", metavar="NEW_DIRECTORY", help="replay STA into a new directory under existing work")
args = parser.parse_args(sys.argv[2:])
spec, libraries, refs = preflight()
if args.check_inputs:
    print(json.dumps({"design": "uart", "orfs_git_head": ORFS_HEAD, "source_sdc_semantics": spec,
                      "rtl_port_counts": PORT_COUNTS, "libraries_per_view": {key: len(libs) for key, libs in libraries.items()},
                      "producer_timeout_s": PRODUCER_TIMEOUT}, indent=2))
else:
    work = args.work.resolve()
    output = (work / (args.qualify_only or "qualification")).resolve()
    if output.parent != work:
        parser.error("qualification directory must be a new direct child of work")
    if args.qualify_only is None:
        produce(work, refs)
    qualify(work, output, spec, libraries, refs)
PY
