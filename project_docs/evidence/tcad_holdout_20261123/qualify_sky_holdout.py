#!/usr/bin/env python3
"""Audit original I/O, three SKY130HD Liberty views, and routed holdout identity."""

import argparse
from decimal import Decimal
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from holdout_tools import IBEX

sys.path.insert(0, str(IBEX / "asap7_control"))
import qualify_asap7_control as audit


BASE = Path("/home/toylog/faeco_tcad_sky_holdout_20261123")
PINNED = Path("/home/toylog/rseco_timing/vendor/OpenROAD-b511b6a")
OPENROAD = PINNED / "bazel-bin/openroad"
ORFS_SHA = "da8f092a02a8e75658cc3100691aabff05f35629"
STA = Path(__file__).resolve().with_name("sta_holdout.py")
DESIGNS = {
    "aes": ("aes_cipher_top", (3.6, 0.2, "clk", "clk", 0.710)),
    "gcd": ("gcd", (1.1, 0.2, "core_clock", "clk", 0.290)),
}
LIBRARIES = {
    "TT": [audit.FLOW / "platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"],
    "FF": [PINNED / "test/sky130hd/sky130_fd_sc_hd__ff_n40C_1v95.lib"],
    "SS": [PINNED / "test/sky130hd/sky130_fd_sc_hd__ss_n40C_1v40.lib"],
}


def collect(corner, artifact, expected_ports, out, top):
    """Use the established STA parser and preserve a RAW duration for the readback."""
    audit.TOP = top
    source, log = (out / f"{corner}{suffix}" for suffix in (".tcl", ".log"))
    source.write_text(audit.produce_tcl(artifact, LIBRARIES[corner]), encoding="utf-8")
    command = ["/usr/bin/timeout", "--kill-after=5s", "120s", str(STA), "-no_splash", "-exit", str(source)]
    start = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
    with log.open("wb") as stream:
        run = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, timeout=130,
                             env={**os.environ, "FAECO_DESIGN_TOP": top})
    elapsed = time.clock_gettime(time.CLOCK_MONOTONIC_RAW) - start
    if run.returncode:
        raise RuntimeError(f"{corner} readback rc {run.returncode}, see {log}")
    view = audit.collect_view(corner, artifact, LIBRARIES[corner], expected_ports, out,
                              reuse_existing=True, sta_binary=STA)
    view.update(elapsed_seconds=elapsed, receipt_reuses_saved_success_log=False,
                wall_clock="CLOCK_MONOTONIC_RAW", effective_odb_tcl=audit.file_ref(source.with_suffix(".odb.tcl")))
    return view


def qualify(design, endpoint_dir=None, drc_report=None, output=None):
    top, pinned_sdc = DESIGNS[design]
    work = BASE / design
    stage = Path("sky130hd") / design / "base"
    source = audit.FLOW / "designs/sky130hd" / design / "constraint.sdc"
    logs, reports = work / "logs" / stage, work / "reports" / stage
    native_drc = reports / "5_route_drc.rpt"
    native = endpoint_dir is None
    endpoint = (work / "results" / stage) if native else endpoint_dir.resolve(strict=True)
    drc_report = native_drc if native else drc_report.resolve(strict=True)
    raw = (work / "qualification") if output is None else output.resolve()
    producer_rc = int((work / "producer.rc").read_text())
    if producer_rc:
        raise RuntimeError(f"holdout {design} producer rc={producer_rc}")
    manifest = work / "input_manifest.log"
    producer_pins = [audit.file_ref(path) for path in
                     (source.with_name("config.mk"), source, OPENROAD, Path("/usr/local/bin/yosys"))]
    saved = audit.read_text(manifest)
    current = subprocess.check_output(["git", "-C", str(audit.FLOW), "rev-parse", "HEAD"],
                                      text=True, timeout=10).strip()
    if current != ORFS_SHA or saved.splitlines()[0] != ORFS_SHA:
        raise RuntimeError("ORFS source revision drift")
    if any(ref["sha256"] + "  " + ref["path"] not in saved for ref in producer_pins):
        raise RuntimeError("pinned native settings or tools drifted")

    artifact = endpoint / "6_final"
    physical = {ext: artifact.with_suffix("." + ext) for ext in ("v", "def", "odb", "sdc", "spef")}
    if any(path.stat().st_size == 0 for path in physical.values()):
        raise RuntimeError("empty routed output")
    if native and json.loads(audit.read_text(logs / "5_2_route.json"))["detailedroute__route__drc_errors"] != 0:
        raise RuntimeError("nonzero native DRC count")
    if drc_report.stat().st_size != 0:
        raise RuntimeError("nonempty detailed route DRC report")
    spec = audit.expected_sdc(audit.read_text(source), pinned=pinned_sdc, time_unit="ns")
    # Write_sdc emits decimal text. Avoid binary multiplication noise in the exact I/O audit.
    spec["io_delay_sdc_units"] = float(Decimal(str(pinned_sdc[0])) * Decimal(str(pinned_sdc[1])))
    spec["io_delay_ps"] = spec["io_delay_sdc_units"] * 1000.0
    ports, extra = audit.audit_final_sdc(audit.read_text(physical["sdc"]), spec)
    checks = [*physical.values(), source, STA, *(path for group in LIBRARIES.values() for path in group)]
    before = [audit.file_ref(path) for path in checks]
    raw.mkdir(parents=True)
    views = {corner: collect(corner, artifact, ports, raw, top) for corner in LIBRARIES}
    if before != [audit.file_ref(path) for path in checks]:
        raise RuntimeError("physical or timing inputs changed during qualification")
    hold_pass = all(row["hold_wns_ps"] >= 0 for row in views.values())
    ref = audit.file_ref
    raw_reports = [manifest, work / "producer.log", logs / "6_report.json", native_drc]
    if not native:
        raw_reports.append(drc_report)
    result = {
        "schema_version": 1, "design": design, "top": top,
        "status": "hold_qualified" if hold_pass else "hold_infeasible",
        "producer_returncode": producer_rc, "producer_orfs_commit": ORFS_SHA,
        "producer_input_bindings": producer_pins, "source_sdc": ref(source),
        "source_sdc_semantics": {
            **spec, "expanded_port_counts": {key: len(value) for key, value in ports.items()},
            "source_io_matches_all_nonclock_inputs_and_outputs": True,
            "propagated_after_cts": spec["core_clock"], "other_exported_set_commands": extra,
        },
        "detailed_route_drc_count": 0, "control_output_paths": {ext: ref(path) for ext, path in physical.items()},
        "raw_reports": [ref(path) for path in raw_reports], "views": views,
        "library_paths": {name: [str(path) for path in group] for name, group in LIBRARIES.items()},
        "view_liberty_groups": {name: [ref(path) for path in group] for name, group in LIBRARIES.items()},
        "sta_binary": ref(STA), "all_views_nonnegative_hold": hold_pass,
        "counts": {"qualification_sta": 3, "candidate_routes": 0, "candidate_sta": 0, "candidate_sec": 0},
    }
    (raw / "CONTROL.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for corner, values in views.items():
        print(f"{design}/{corner}: Setup WNS/TNS {values['setup_wns_ps']:.6f}/{values['setup_tns_ps']:.6f} ps, "
              f"hold WNS/TNS {values['hold_wns_ps']:.6f}/{values['hold_tns_ps']:.6f} ps", flush=True)
    print(f"{result['status']} {raw / 'CONTROL.json'}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("design", choices=DESIGNS)
    parser.add_argument("--endpoint-dir", type=Path)
    parser.add_argument("--drc-report", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if bool(args.endpoint_dir) != bool(args.drc_report):
        parser.error("a hold-repaired endpoint requires its matching DRC report")
    qualify(args.design, args.endpoint_dir, args.drc_report, args.out)


if __name__ == "__main__":
    main()
