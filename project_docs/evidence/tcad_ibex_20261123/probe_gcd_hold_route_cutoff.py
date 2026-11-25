#!/usr/bin/env python3
"""Separate early DRT cutoff from freezing outside-neighbor wires."""

from argparse import ArgumentParser
from dataclasses import asdict
from pathlib import Path
import re
from types import SimpleNamespace

from probe_gcd_local_hold_preview import CORNERS, ORDER, comparison, geometry, physical_view, read, verify


CUTOFFS = (0, 2)


def run_case(original, out, stage, tools, templates, control):
    out.mkdir()
    start = geometry.raw_seconds()
    source_dir = original.parent
    tcl = original.read_text(encoding="utf-8")
    marker = "-droute_end_iter 64"
    if tcl.count(marker) != 1 or "/fixed_wires.def" in tcl:
        raise ValueError("route cutoff must start from the original unlocked full backend")
    text = tcl.replace(str(source_dir), str(out)).replace(marker, f"-droute_end_iter {stage}")
    text = text.replace("detailed_route -output_drc", 'set drt_start [clock microseconds]\ndetailed_route -output_drc', 1)
    text = text.replace('puts "IBEX_DRT_VIOLATIONS', 'puts "CUTOFF_DRT_US [expr {[clock microseconds] - $drt_start}]"\nputs "IBEX_DRT_VIOLATIONS', 1)
    deck, logfile = out / "route.tcl", out / "route.log"
    deck.write_text(text, encoding="utf-8")
    proc = comparison.run_process([tools["openroad"], "-threads", "4", "-exit", deck], logfile, 30)
    row = {"route": asdict(proc), "original_tcl": comparison.bind(original), "error": None, "views": {}, "sta": {}}
    try:
        output = comparison.checked_output(proc, "IBEX_ROUTE_COMPLETE")
        row["drt_raw_marker_us"] = int(re.search(r"(?m)^CUTOFF_DRT_US (\d+)$", output)[1])
        row["drc_violations"] = int(re.search(r"(?m)^IBEX_DRT_VIOLATIONS (\d+)$", output)[1])
        row["geometry"] = comparison.changed_geometry(control["def"], out / "routed.def", set())
        if comparison.sha(out / "routed.v") != comparison.sha(source_dir / "routed.v"):
            raise ValueError("functional netlist diverged from the full trial")
        for corner in CORNERS:
            row["views"][corner], row["sta"][corner] = physical_view(templates, out, corner)
    except (comparison.TrialFailure, ValueError, OSError) as error:
        row["error"] = str(error)
    row["elapsed_raw_seconds"] = geometry.raw_seconds() - start
    return row


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("main_pair", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    primary = args.main_pair.resolve(strict=True)
    measured_path = primary / "results.json"
    measured = read(measured_path)
    protocol = read(verify(measured["protocol"]))
    settings = read(verify(protocol["seed"]))
    assets = settings["bindings"]
    control = {key: verify(ref) for key, ref in assets["control"].items()}
    libraries = {view: [verify(ref) for ref in refs] for view, refs in assets["used_libraries"].items()}
    tools = {key: verify(ref) for key, ref in assets["tools"].items()}
    feature = read(verify(protocol["score"]))
    reference = read(verify(read(verify(feature["protocol"]))["reference"]))["views"]
    setup = SimpleNamespace(args=SimpleNamespace(sta=tools["opensta"]), control=control,
                            libraries=libraries, ref_views=reference)
    floor = protocol["hold_floors_ps"]
    out = args.output.resolve()
    out.mkdir()
    comparison.save(out / "protocol.json", {"full_benchmark": comparison.bind(measured_path), "cutoffs": CUTOFFS,
                                             "source": comparison.bind(Path(__file__).resolve()), "original_gate": floor, "order": ORDER})
    cases = {}
    with geometry.bind_runtime("gcd", None):
        for block, order in enumerate(ORDER, 1):
            for last_iteration in (CUTOFFS if block == 1 else CUTOFFS[::-1]):
                for role in order:
                    source = verify(measured["cases"][f"{block}_full_{role}"]["physical"]).parent / "route.tcl"
                    key = f"block{block}_iter{last_iteration}_{role}"
                    case = run_case(source, out / key, last_iteration, tools, setup, control)
                    case["passes"] = {corner: view["hold_wns_ps"] >= floor[corner] for corner, view in case["views"].items()}
                    cases[key] = case
                    comparison.save(out / "progress.json", cases)
                    print(key, round(case["elapsed_raw_seconds"], 3), case["passes"], case["error"], flush=True)
    summary = {}
    for last_iteration in CUTOFFS:
        comparisons = []
        for block, baseline in enumerate(measured["comparisons"], 1):
            pair = {role: cases[f"block{block}_iter{last_iteration}_{role}"] for role in ORDER[0]}
            correct = all(row["passes"] == baseline["full_label"][role] for role, row in pair.items())
            previews = sum(row["elapsed_raw_seconds"] for row in pair.values())
            net_budget = baseline["full_pair_seconds"] - measured["cases"][f"{block}_full_r093"]["elapsed_raw_seconds"]
            comparisons.append({"correct": correct, "screen_both_seconds": previews, "screen_budget_seconds": net_budget,
                                "would_save_if_correct": net_budget - previews, "eligible": correct and previews < net_budget})
        summary[last_iteration] = comparisons
    comparison.save(out / "results.json", {"protocol": comparison.bind(out / "protocol.json"), "cases": cases, "summary": summary})


if __name__ == "__main__":
    main()
