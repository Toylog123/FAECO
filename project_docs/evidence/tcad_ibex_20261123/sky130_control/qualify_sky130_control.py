"""Audit routed SKY130HD Ibex with its original I/O timing and three Liberty views."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "asap7_control"))
from qualify_asap7_control import (  # noqa: E402
    FLOW, VIEWS, audit_final_sdc, collect_view, expected_sdc, file_ref, read_text,
)


WORK = Path("/home/toylog/faeco_tcad_ibex_20261123/control_sky130")
PINNED_OPENROAD = Path("/home/toylog/rseco_timing/vendor/OpenROAD-b511b6a")
ORFS_REVISION = "da8f092a02a8e75658cc3100691aabff05f35629"
SPEC = (10.0, 0.2, "core_clock", "clk_i", 1.095)
SOURCE_SHA = "2fb819cb8e9bcd2ff0fe825ed3f7d5a96ebfeea301d53c83bcf5225121255151"
STAGE = Path("sky130hd/ibex/base")
STA = Path(__file__).resolve().with_name("sta_from_odb.py")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--producer-log", required=True, type=Path)
    parser.add_argument("--producer-returncode", required=True, type=int)
    parser.add_argument("--raw-output", type=Path, default=WORK / "qualify_original_io")
    args = parser.parse_args()
    if args.producer_returncode:
        raise RuntimeError("CONTROL producer failed")

    output = Path(__file__).resolve().parent
    producer_log = WORK / "producer.log"
    shutil.copyfile(args.producer_log, producer_log)
    result_dir = WORK / "results" / STAGE
    logs = WORK / "logs" / STAGE
    reports = WORK / "reports" / STAGE
    artifact = result_dir / "6_final"
    source = FLOW / "designs/sky130hd/ibex/constraint.sdc"
    source_ref = file_ref(source)
    if source_ref["sha256"] != SOURCE_SHA:
        raise RuntimeError("original SKY130 SDC has drifted from the producer input")
    runtime_pins = [
        source_ref,
        file_ref(source.with_name("config.mk")),
        file_ref(PINNED_OPENROAD / "bazel-bin/openroad"),
        file_ref(Path("/usr/local/bin/yosys")),
    ]
    producer_text = read_text(producer_log)
    absent = [ref["path"] for ref in runtime_pins if ref["sha256"] + "  " + ref["path"] not in producer_text]
    orfs = subprocess.check_output(["git", "-C", str(FLOW), "rev-parse", "HEAD"], text=True, timeout=10).strip()
    if absent or orfs != ORFS_REVISION or producer_text.splitlines()[0] != ORFS_REVISION:
        raise RuntimeError(f"producer input/tool disagreement: ORFS {orfs}, files {absent}")
    spec = expected_sdc(read_text(source), pinned=SPEC, time_unit="ns")
    ports, extra = audit_final_sdc(read_text(artifact.with_suffix(".sdc")), spec)
    drc_report = reports / "5_route_drc.rpt"
    drc = json.loads(read_text(logs / "5_2_route.json"))["detailedroute__route__drc_errors"]
    if drc != 0 or drc_report.stat().st_size != 0:
        raise RuntimeError(f"CONTROL detailed-route DRC is nonzero: {drc}")

    native_lib = FLOW / "platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
    corner_libs = PINNED_OPENROAD / "test/sky130hd"
    libs = {
        "TT": [native_lib],
        "FF": [corner_libs / "sky130_fd_sc_hd__ff_n40C_1v95.lib"],
        "SS": [corner_libs / "sky130_fd_sc_hd__ss_n40C_1v40.lib"],
    }
    physical = {ext: artifact.with_suffix("." + ext) for ext in ("v", "odb", "def", "sdc", "spef")}
    for path in physical.values():
        if not path.stat().st_size:
            raise RuntimeError(f"empty CONTROL artifact: {path}")
    inputs = [*physical.values(), source, STA, *(lib for group in libs.values() for lib in group)]
    before = [file_ref(path) for path in inputs]
    raw = args.raw_output.resolve()
    if not raw.is_relative_to(WORK):
        raise ValueError("qualification output must stay in the CONTROL work home")
    raw.mkdir(exist_ok=False)
    views = {}
    for view in VIEWS:
        views[view] = collect_view(view, artifact, libs[view], ports, raw, sta_binary=STA)
        views[view]["effective_odb_tcl"] = file_ref(raw / f"{view}.odb.tcl")
        views[view]["library_paths"] = [str(path) for path in libs[view]]
        print(f"{view}: setup {views[view]['setup_wns_ps']:+.6f} ps, "
              f"hold {views[view]['hold_wns_ps']:+.6f} ps", flush=True)
    if before != [file_ref(path) for path in inputs]:
        raise RuntimeError("CONTROL pins changed during qualification")

    finish = json.loads(read_text(logs / "6_report.json"))
    setup = finish["finish__timing__setup__ws"] * 1000
    hold = finish["finish__timing__hold__ws"] * 1000
    match = abs(setup - views["TT"]["setup_wns_ps"]) <= 0.1 and abs(hold - views["TT"]["hold_wns_ps"]) <= 0.1
    hold_pass = all(view["hold_wns_ps"] >= 0 for view in views.values())
    raw_reports = [
        producer_log, logs / "5_2_route.log", logs / "5_2_route.json", logs / "6_report.log",
        logs / "6_report.json", drc_report, reports / "6_finish.rpt",
    ]
    report = {
        "schema_version": 1,
        "design": "ORFS SKY130HD Ibex / ibex_core",
        "status": "hold_qualified" if hold_pass else "hold_infeasible",
        "producer_returncode": args.producer_returncode,
        "producer_orfs_commit": orfs,
        "producer_input_bindings": runtime_pins,
        "openrcx_rules": file_ref(FLOW / "platforms/sky130hd/rcx_patterns.rules"),
        "source_sdc": source_ref,
        "source_sdc_semantics": {
            **spec,
            "expanded_port_counts": {key: len(group) for key, group in ports.items()},
            "source_io_matches_all_nonclock_inputs_and_outputs": True,
            "propagated_after_cts": spec["core_clock"],
            "other_exported_set_commands": extra,
        },
        "detailed_route_drc_count": drc,
        "control_output_paths": {ext: file_ref(path) for ext, path in physical.items()},
        "raw_reports": [file_ref(path) for path in raw_reports],
        "views": views,
        "library_paths": {view: [str(path) for path in group] for view, group in libs.items()},
        "view_liberty_groups": {view: [file_ref(path) for path in group] for view, group in libs.items()},
        "sta_binary": file_ref(STA),
        "sta_version": subprocess.check_output([str(STA), "-version"], text=True, timeout=10).strip(),
        "sta_representation": "Pinned OpenROAD read_db of the final routed ODB with the original SDC and its SPEF.",
        "tt_matches_native_producer_0p10_ps": match,
        "native_finish_setup_wns_ps": setup,
        "native_finish_hold_wns_ps": hold,
        "all_views_nonnegative_hold": hold_pass,
        "corner_scope": "Three SKY130HD PVT Liberties on one common extracted OpenRCX SPEF.",
        "counts": {"qualification_sta": 3, "candidate_routes": 0, "candidate_sta": 0, "candidate_sec": 0},
    }
    receipt = json.dumps(report, indent=2) + "\n"
    (raw / "CONTROL.json").write_text(receipt, encoding="utf-8")
    (output / "CONTROL.json").write_text(receipt, encoding="utf-8")
    shutil.copyfile(source, output / "original.sdc")
    shutil.copyfile(physical["sdc"], output / "routed.sdc")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
