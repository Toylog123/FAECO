#!/usr/bin/env python3
"""Exchange the measured UART netlists and SPEFs in SS without rerouting."""

from argparse import ArgumentParser
from dataclasses import asdict
import json
import math
from pathlib import Path
import re

from run_uart_online import comparison, read, verify
from run_screened_matrix import bind_runtime, raw_seconds


BASE = "two_gate"
RESERVED = "with_0562"
TARGETED = "with_0886"
VIEWS = (BASE, RESERVED, TARGETED)
CASES = [(name, name) for name in VIEWS] + [(cell, spef) for candidate in VIEWS[1:]
                                             for cell, spef in ((candidate, BASE), (BASE, candidate))]
TIMING_KEYS = ("setup_wns_ps", "setup_tns_ps", "hold_wns_ps", "hold_tns_ps")
MATCH_PS = 1e-6
# The path report and scalar metrics use separate OpenSTA float conversions.
PATH_REPORT_MATCH_PS = 2e-5
SWAP_TIMEOUT_SECONDS = 30.0
EXPANDED_MARKER = "UART_EXPANDED_MIN"


def measure_inputs(reservation, targeted, require_full):
    source_protocol = reservation / "protocol.json"
    probe_protocol = targeted / "protocol.json"
    protocol = read(source_protocol)
    probe = read(probe_protocol)
    if probe["seed"] != protocol["seed"] or probe["reference"] != protocol["reference"] or probe["gate"] != protocol["gate"]:
        raise ValueError("the two experiments must bind the same original seed, view and gate")
    if require_full:
        received = reservation / "independent_verification.json"
        receipt = read(received)
        if verify(receipt["protocol"]) != source_protocol or len(receipt["arms"]) != 6:
            raise ValueError("run this diagnostic after the six-arm reservation audit")
    else:
        received = None
    targeted_audit = targeted / "targeted_verification.json"
    target_receipt = read(targeted_audit)
    if verify(target_receipt["protocol"]) != probe_protocol or target_receipt["proof_count"] != [567, 0]:
        raise ValueError("the targeted UART endpoint lacks its independent SEC audit")

    matrix = read(verify(protocol["seed"]))
    assets = matrix["bindings"]
    if (matrix["top"], matrix["pdk"]) != ("uart", "asap7"):
        raise ValueError("expected the same ASAP7 UART seed")
    reference = read(verify(protocol["reference"]))["views"]["SS"]
    reserved_arm = reservation / "cell_02/faeco"
    selected = {
        BASE: (reserved_arm / "05/result.json", {"_0814_", "_1027_"}, []),
        RESERVED: (reserved_arm / "06/result.json", {"_0562_", "_0814_", "_1027_"}, ["SS:hold_regression"]),
        TARGETED: (targeted / "trial/result.json", {"_0814_", "_0886_", "_1027_"}, []),
    }
    rows = {}
    for name, (path, actions, failures) in selected.items():
        item = read(path)
        instances = {comparison.canonical_odb_name(key.split("=", 1)[0]) for key in item["actions"]}
        if instances != actions or item["failures"] != failures or item["endpoint"]["valid"] != (not failures):
            raise ValueError(f"wrong measured proposal or result for {name}")
        if name == TARGETED and target_receipt["candidate"] != item:
            raise ValueError("the targeted candidate differs from its audit")
        physical = verify(item["physical_receipt"])
        data = read(physical)
        matched_tcl = physical.with_name("sta_SS.tcl")
        matched_log = physical.with_name("sta_SS.log")
        if data["actions"] != item["actions"] or data["control_sdc"] != assets["control"]["sdc"]:
            raise ValueError(f"the physical receipt did not use the original SDC and proposed action set for {name}")
        known = data["views"]["SS"]
        # Confirm that the source measurement used the same plain Verilog STA
        # executable path and the rendered recipe that the exchange will use.
        view_record = data["operations"]["STA_SS"]
        if Path(view_record["log"]) != matched_log or view_record["returncode"] != 0:
            raise ValueError(f"source SS STA did not finish for {name}")
        verify(data["artifacts"]["v"])
        verify(data["artifacts"]["spef"])
        libraries = [verify(lib) for lib in assets["used_libraries"]["SS"]]
        sdc = verify(assets["control"]["sdc"])
        expected = comparison.render_sta(libraries, Path(data["artifacts"]["v"]["path"]), sdc,
                                         Path(data["artifacts"]["spef"]["path"]), report_setup_endpoints=True)
        if expected != matched_tcl.read_text(encoding="utf-8") or comparison.parse_sta(matched_log.read_text(encoding="utf-8")) != known:
            raise ValueError(f"matched source SS Tcl or log does not reconstruct for {name}")
        rows[name] = {"result": comparison.bind(path), "physical_receipt": item["physical_receipt"],
                      "netlist": data["artifacts"]["v"], "spef": data["artifacts"]["spef"],
                      "matched_tcl": comparison.bind(matched_tcl), "matched_log": comparison.bind(matched_log),
                      "expected_ss": known, "actions": item["actions"]}
    return {
        "source_protocols": [comparison.bind(path) for path in (source_protocol, probe_protocol)],
        "audits": [comparison.bind(path) for path in (received, targeted_audit) if path is not None],
        "seed": protocol["seed"], "tool": assets["tools"]["opensta"], "sdc": assets["control"]["sdc"],
        "liberty_ss": assets["used_libraries"]["SS"], "reference_ss": reference,
        "hold_tolerance_ps": protocol["hold_tolerance_ps"], "matched_endpoints": rows,
        "timeout_seconds_per_sta": SWAP_TIMEOUT_SECONDS, "cases": CASES,
        "driver": comparison.bind(Path(__file__).resolve()),
        "production_renderer": comparison.bind(Path(comparison.render_sta.__code__.co_filename).resolve()),
    }


def render(libraries, netlist, sdc, spef):
    text = comparison.render_sta(libraries, netlist, sdc, spef, report_setup_endpoints=True)
    marker = "puts IBEX_STA_COMPLETE"
    if text.count(marker) != 1:
        raise ValueError("unexpected production STA completion marker")
    expanded = f"""
set_cmd_units -time ps
puts {EXPANDED_MARKER}_BEGIN
report_checks -path_delay min -group_path_count 1 -endpoint_path_count 1 \\
    -digits 9 -no_line_splits -format full_clock_expanded -fields {{capacitance slew fanout input_pin net}}
puts {EXPANDED_MARKER}_END
"""
    return text.replace(marker, expanded + marker, 1)


def worst_path(text, slack_ps):
    marker = re.search(rf"(?ms)^{EXPANDED_MARKER}_BEGIN\n(.*?)^{EXPANDED_MARKER}_END$", text)
    if marker is None:
        raise ValueError("missing expanded hold path report")
    paths = []
    for path in re.split(r"(?m)(?=^Startpoint: )", marker[1]):
        start = re.search(r"(?m)^Startpoint: (\S+)", path)
        endpoint = re.search(r"(?m)^Endpoint: (\S+)", path)
        slack = re.search(rf"(?m)^\s*({comparison.NUMBER})\s+slack \(", path)
        if start and endpoint and slack:
            paths.append({"startpoint": start[1], "endpoint": endpoint[1], "slack_ps": float(slack[1]), "path_report": path})
    if not paths:
        raise ValueError("no numeric minimum-delay path")
    selected = min(paths, key=lambda row: row["slack_ps"])
    if not math.isclose(selected["slack_ps"], slack_ps, abs_tol=PATH_REPORT_MATCH_PS, rel_tol=0):
        raise ValueError("expanded minimum-delay path slack does not agree with SS WNS in ps")
    return selected


def run_exchange(inputs, output):
    tool = verify(inputs["tool"])
    sdc = verify(inputs["sdc"])
    libraries = [verify(lib) for lib in inputs["liberty_ss"]]
    sources = inputs["matched_endpoints"]
    rows = {}
    started = raw_seconds()
    for cell, spef in CASES:
        key = f"{cell}__{spef}"
        out = output / key
        out.mkdir()
        script, log = out / "sta_SS.tcl", out / "sta_SS.log"
        script.write_text(render(libraries, verify(sources[cell]["netlist"]), sdc, verify(sources[spef]["spef"])), encoding="utf-8")
        start_raw = raw_seconds()
        process = comparison.run_process([tool, "-exit", script], log, SWAP_TIMEOUT_SECONDS)
        stop_raw = raw_seconds()
        text = comparison.checked_output(process, "IBEX_STA_COMPLETE")
        measurements = comparison.parse_sta(text)
        expected = sources[cell]["expected_ss"]
        if measurements["ports"] != expected["ports"] or (cell == spef and (
                any(not math.isclose(measurements[key], expected[key], abs_tol=MATCH_PS, rel_tol=0) for key in TIMING_KEYS)
                or any(measurements[key] != expected[key] for key in ("electrical", "setup_negative_endpoints")))):
            raise ValueError(f"measured SS replay disagrees with the matched original for {key}")
        annotation = re.findall(r"(?m)^Found (\d+) ((?:partially )?unannotated drivers)\.$", text)
        rows[key] = {"netlist_role": cell, "spef_role": spef, "matched_physical_artifacts": cell == spef,
                     "metrics": measurements, "minimum_hold_path": worst_path(text, measurements["hold_wns_ps"]),
                     "annotation_unannotated_driver_counts": {label: int(count) for count, label in annotation},
                     "process": asdict(process), "start_raw": start_raw, "stop_raw": stop_raw,
                     "script": comparison.bind(script), "log": comparison.bind(log)}
        comparison.save(output / "partial_results.json", rows)
        print(f"{key}: SS hold {measurements['hold_wns_ps']:.9f} ps", flush=True)

    annotation = rows[f"{BASE}__{BASE}"]["annotation_unannotated_driver_counts"]
    if not annotation or annotation.get("partially unannotated drivers") != 0 or any(
            row["annotation_unannotated_driver_counts"] != annotation for row in rows.values()):
        raise ValueError("SPEF exchange changed the original annotation coverage")
    floor = inputs["reference_ss"]["hold_wns_ps"] - inputs["hold_tolerance_ps"]

    def hold(cell, spef):
        return rows[f"{cell}__{spef}"]["metrics"]["hold_wns_ps"]

    base = hold(BASE, BASE)
    effects = {}
    for candidate in VIEWS[1:]:
        full, v_only, rc_only = hold(candidate, candidate), hold(candidate, BASE), hold(BASE, candidate)
        effects[candidate] = {"actual_delta_ps": full - base, "swap_verilog_only_delta_ps": v_only - base,
                              "swap_spef_only_delta_ps": rc_only - base, "interaction_ps": full - v_only - rc_only + base,
                              "fixed_spef_ss_hold_only_pass": v_only >= max(floor, 0),
                              "actual_ss_hold_only_pass": full >= max(floor, 0)}
    comparison.save(output / "results.json", {"manifest": comparison.bind(output / "protocol.json"), "cases": rows,
                                                 "original_relative_ss_hold_floor_ps": floor, "effects": effects,
                                                 "elapsed_raw_seconds": raw_seconds() - started,
                                                 "sta_calls": len(rows), "drt_rcx_calls": 0, "candidate_sec_calls": 0})


def main():
    parser = ArgumentParser(description=__doc__)
    for key in ("reservation_run", "targeted_run", "output"):
        parser.add_argument(key, type=Path)
    parser.add_argument("--check-inputs", action="store_true", help="validate original receipts and Tcl; launch no tools")
    args = parser.parse_args()
    with bind_runtime("uart", None):
        inputs = measure_inputs(args.reservation_run.resolve(strict=True), args.targeted_run.resolve(strict=True), not args.check_inputs)
        verify(inputs["tool"])
        if args.check_inputs:
            print(json.dumps({"matched": len(inputs["matched_endpoints"]), "planned_ss_sta_calls": len(CASES),
                              "processes_launched": 0, "hold_wns_ps": {tag: row["expected_ss"]["hold_wns_ps"]
                                                                        for tag, row in inputs["matched_endpoints"].items()}}, indent=2))
            return
        output = args.output.resolve()
        output.mkdir(parents=True)
        comparison.save(output / "protocol.json", inputs)
        run_exchange(inputs, output)


if __name__ == "__main__":
    main()
