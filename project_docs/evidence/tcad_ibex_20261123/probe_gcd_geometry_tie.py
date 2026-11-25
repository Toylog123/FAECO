#!/usr/bin/env python3
"""Check what the matched-area GCD geometry tie conceals using the original TT/SS views."""

from argparse import ArgumentParser
from itertools import product
import math
from pathlib import Path
import re

from probe_gcd_hold_geometry_transfer import comparison, geometry, read, verify


ROLES = ("passed", "rejected")
VIEWS = ("TT", "SS")
METRICS = ("hold_wns_ps", "hold_tns_ps", "setup_wns_ps", "setup_tns_ps")
MARKER = "GCD_TIE_HOLD_PATH"


def inventory(text):
    block = text.split(f"\n{MARKER}_BEGIN\n")[1].split(f"\n{MARKER}_END\n")[0]
    candidates = []
    for path in re.split(r"(?m)(?=^Startpoint: )", block):
        if path.startswith("Startpoint: "):
            fields = dict(re.findall(r"(?m)^(Startpoint|Endpoint|Path Group): (.+)$", path))
            slack = re.search(rf"(?m)^\s*({comparison.NUMBER})\s+slack \(", path)
            candidates.append({"fields": fields, "slack_ps": float(slack[1]),
                               "nets": re.findall(r"(?m)^\s+(\S+) \(net\)$", path)})
    return min(candidates, key=lambda row: row["slack_ps"])


def measure(tool, spec, netlist, spef, assets, corner, out):
    out.mkdir()
    libraries = [verify(item) for item in assets["used_libraries"][corner]]
    sdc = verify(assets["control"]["sdc"])
    tcl, log = out / "hold.tcl", out / "hold.log"
    expected_script = comparison.render_sta(libraries, netlist, sdc, spef)
    expanded = f"""
set_cmd_units -time ps
puts {MARKER}_BEGIN
report_checks -path_delay min -group_path_count 1 -endpoint_path_count 1 \\
  -no_line_splits -digits 9 -format full_clock_expanded -fields {{input_pin net}}
puts {MARKER}_END
"""
    tcl.write_text(expected_script.replace("puts IBEX_STA_COMPLETE", expanded + "puts IBEX_STA_COMPLETE"), encoding="utf-8")
    start = geometry.raw_seconds()
    process = comparison.run_process([tool, "-exit", tcl], log, 45)
    duration = geometry.raw_seconds() - start
    text = comparison.checked_output(process, "IBEX_STA_COMPLETE")
    metrics = comparison.parse_sta(text)
    if spec is not None and (any(not math.isclose(spec[key], metrics[key], abs_tol=1e-6, rel_tol=0) for key in METRICS)
                             or metrics["ports"] != spec["ports"]):
        raise ValueError(f"original matched {corner} metrics changed")
    min_path = inventory(text)
    if not math.isclose(min_path["slack_ps"], metrics["hold_wns_ps"], rel_tol=3e-7, abs_tol=2e-5):
        raise ValueError(f"path display and hold scalar disagree for {corner}")
    annotation = re.findall(r"(?m)^Found (\d+) ((?:partially )?unannotated drivers)\.$", text)
    return {"metrics": {key: metrics[key] for key in METRICS}, "ports": metrics["ports"],
            "annotation": {label: int(count) for count, label in annotation}, "minimum_path": min_path,
            "elapsed_raw_seconds": duration, "script": comparison.bind(tcl), "log": comparison.bind(log)}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("transfer", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    transfer = args.transfer.resolve(strict=True)
    result_path = transfer / "results.json"
    result = read(result_path)
    scoring = read(verify(result["score_receipt"]))
    source = read(verify(scoring["protocol"]))
    assets = read(verify(source["seed"]))["bindings"]
    reference = read(verify(source["reference"]))["views"]
    receipts = {role: result["known_equal_area_pair"][role]["sources"][0] for role in ROLES}
    rows = {role: read(verify(ref)) for role, ref in receipts.items()}
    if (any(row["control_sdc"] != assets["control"]["sdc"] for row in rows.values())
            or rows["passed"]["failures"] or not all(f"{corner}:hold_regression" in rows["rejected"]["failures"] for corner in VIEWS)
            or not math.isclose(rows["passed"]["area_saved"], rows["rejected"]["area_saved"], abs_tol=1e-7, rel_tol=0)):
        raise ValueError("the physical receipts do not represent the audited equal-area hold tie")
    inputs = {role: {key: verify(rows[role]["artifacts"][key]) for key in ("v", "spef")} for role in ROLES}
    tool = verify(assets["tools"]["opensta"])
    out = args.output.resolve()
    out.mkdir()
    manifest = out / "protocol.json"
    comparison.save(manifest, {"transfer_results": comparison.bind(result_path), "physical_receipts": receipts,
                               "source_seed": source["seed"], "tool": assets["tools"]["opensta"],
                               "sdc": assets["control"]["sdc"], "liberties": {v: assets["used_libraries"][v] for v in VIEWS},
                               "driver": comparison.bind(Path(__file__).resolve()), "roles": ROLES, "views": VIEWS})
    outputs, effects = {}, {}
    started = geometry.raw_seconds()
    with geometry.bind_runtime("gcd", None):
        for corner in VIEWS:
            entries = {}
            for v_role, spef_role in product(ROLES, repeat=2):
                key = f"{v_role}__{spef_role}"
                expected = rows[v_role]["views"][corner] if v_role == spef_role else None
                entries[key] = measure(tool, expected, inputs[v_role]["v"], inputs[spef_role]["spef"],
                                       assets, corner, out / f"{corner}_{key}")
            baseline = entries["passed__passed"]
            if not baseline["annotation"] or any(row["annotation"] != baseline["annotation"] or row["ports"] != baseline["ports"]
                                                for row in entries.values()):
                raise ValueError(f"changed annotation coverage or ports after {corner} input exchange")
            outputs[corner] = entries
            base, spef, netlist, full = (row["metrics"]["hold_wns_ps"] for row in entries.values())
            floor = max(source["absolute_hold_ps"], reference[corner]["hold_wns_ps"] - source["hold_tolerance_ps"])
            effects[corner] = {"original_floor_ps": floor, "actual_delta_ps": full - base,
                               "only_spef_delta_ps": spef - base, "only_netlist_delta_ps": netlist - base,
                               "interaction_ps": full - spef - netlist + base}
            print(f"{corner} hold: base {base:.9f}, swap SPEF {spef:.9f}, swap netlist {netlist:.9f}, rejected {full:.9f}", flush=True)
    comparison.save(out / "results.json", {"protocol": comparison.bind(manifest), "views": outputs,
                                            "effects": effects, "sta_calls": sum(map(len, outputs.values())),
                                            "drt_rcx_sec_calls": 0, "elapsed_raw_seconds": geometry.raw_seconds() - started})


if __name__ == "__main__":
    main()
