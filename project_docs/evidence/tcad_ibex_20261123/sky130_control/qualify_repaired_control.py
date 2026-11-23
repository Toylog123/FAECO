"""Qualify a separate SKY130HD hold-repair endpoint under the original IO timing."""

import argparse
import json
from pathlib import Path
import re
import subprocess

from qualify_sky130_control import (
    FLOW, SOURCE_SHA, STA, VIEWS, audit_final_sdc, collect_view, file_ref, read_text,
)


HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("control_dir", type=Path)
    parser.add_argument("--drc-report", required=True, type=Path)
    parser.add_argument("--repair-log", required=True, type=Path)
    parser.add_argument("--antenna-report", required=True, type=Path)
    parser.add_argument("--sec-receipt", required=True, type=Path)
    args = parser.parse_args()
    endpoint_dir = args.control_dir.resolve(strict=True)
    original = json.loads(read_text(HERE / "CONTROL.json"))
    if original["status"] != "hold_infeasible":
        raise ValueError("a separate repair is expected after the original failed hold")
    source = FLOW / "designs/sky130hd/ibex/constraint.sdc"
    source_ref = file_ref(source)
    if source_ref["sha256"] != SOURCE_SHA:
        raise ValueError("source SDC has drifted")

    artifact = endpoint_dir / "6_final"
    paths = {ext: artifact.with_suffix("." + ext) for ext in ("odb", "def", "v", "sdc", "spef")}
    physical = {ext: file_ref(path) for ext, path in paths.items()}
    if not all(ref["bytes"] for ref in physical.values()):
        raise ValueError("an endpoint file is empty")
    if physical["sdc"]["sha256"] != original["control_output_paths"]["sdc"]["sha256"]:
        raise ValueError("repaired CONTROL does not use the original routed SDC")
    if physical["odb"]["sha256"] == original["control_output_paths"]["odb"]["sha256"]:
        raise ValueError("expected a separate physical endpoint after repair")
    drc = args.drc_report.resolve(strict=True)
    if drc.stat().st_size:
        raise ValueError("repaired CONTROL has nonzero detailed-route DRC")
    repair_log = args.repair_log.resolve(strict=True)
    log = read_text(repair_log)
    if "[INFO RCX-0045]" not in log or "[INFO RCX-0443]" not in log:
        raise ValueError("missing completed OpenRCX extraction in the producer log")
    if "Number of violations = 0." not in log:
        raise ValueError("missing detailed-router convergence in the producer log")
    antenna = args.antenna_report.resolve(strict=True)
    counts = re.findall(r"(?m)^HOLD_REPAIR_ANTENNA_VIOLATIONS (\d+)\s*$", log)
    if not counts:
        raise ValueError("missing post-route antenna check")
    antenna_count = int(counts[-1])
    if antenna_count == 0 and antenna.stat().st_size != 0:
        raise ValueError("antenna report disagrees with zero violations")

    spec = original["source_sdc_semantics"]
    ports, extra = audit_final_sdc(read_text(paths["sdc"]), spec)
    raw = endpoint_dir / "qualification"
    raw.mkdir(exist_ok=False)
    views = {}
    libs = {view: [Path(path) for path in original["library_paths"][view]] for view in VIEWS}
    for view in VIEWS:
        if original["view_liberty_groups"][view] != [file_ref(path) for path in libs[view]]:
            raise ValueError(f"{view} libraries changed after the original CONTROL")
        views[view] = collect_view(view, artifact, libs[view], ports, raw, sta_binary=STA)
        views[view]["effective_odb_tcl"] = file_ref(raw / f"{view}.odb.tcl")
        views[view]["library_paths"] = [str(path) for path in libs[view]]
        print(f"{view}: setup {views[view]['setup_wns_ps']:+.6f} ps, "
              f"hold {views[view]['hold_wns_ps']:+.6f} ps", flush=True)

    if physical != {ext: file_ref(path) for ext, path in paths.items()}:
        raise ValueError("CONTROL changed during the three-view replay")
    hold_pass = all(view["hold_wns_ps"] >= 0 for view in views.values())
    sec = json.loads(read_text(args.sec_receipt))
    if sec["gold"] != original["control_output_paths"]["v"] or sec["gate"] != physical["v"]:
        raise ValueError("original-to-repaired SEC has mismatched inputs")
    if not hold_pass:
        status = "hold_infeasible"
    elif antenna_count:
        status = "antenna_infeasible"
    elif not (sec["passed"] and sec["proven"] > 0 and sec["unproven"] == 0):
        status = "sec_infeasible"
    else:
        status = "hold_qualified"
    report = {
        "schema_version": 1,
        "design": original["design"],
        "status": status,
        "source_sdc": source_ref,
        "source_sdc_semantics": {**spec, "other_exported_set_commands": extra},
        "all_views_nonnegative_hold": hold_pass,
        "detailed_route_drc_count": 0,
        "antenna_violation_count": antenna_count,
        "control_output_paths": physical,
        "raw_reports": [file_ref(path) for path in (drc, antenna, repair_log)],
        "original_qualification": file_ref(HERE / "CONTROL.json"),
        "views": views,
        "library_paths": original["library_paths"],
        "view_liberty_groups": original["view_liberty_groups"],
        "sta_binary": file_ref(STA),
        "sta_version": subprocess.check_output([str(STA), "-version"], text=True, timeout=10).strip(),
        "sta_representation": original["sta_representation"],
        "preconditioning_sec": sec,
        "counts": {"qualification_sta": 3, "preconditioning_sec": 1, "candidate_routes": 0},
    }
    receipt = json.dumps(report, indent=2) + "\n"
    (raw / "CONTROL.json").write_text(receipt, encoding="utf-8")
    print(f"{report['status']} {raw / 'CONTROL.json'}", flush=True)


if __name__ == "__main__":
    main()
