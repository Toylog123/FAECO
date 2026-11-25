#!/usr/bin/env python3
"""Perturb the same local window by removing only the capture clock leaf once."""

from argparse import ArgumentParser
import os
from pathlib import Path

import run_uart_tt_capture_window as window


comparison, read, verify = window.comparison, window.read, window.verify


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("window", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    selected = args.window.resolve(strict=True) / "results.json"
    results = read(selected)
    configured = read(verify(results["protocol"]))
    if tuple(case["label"] for case in results["cases"]) != window.CASES or any(
            not all(attempt["failures"] and attempt.get("scope_check", {}).get("changed_nets") == []
                    for attempt in case["attempts"]) for case in results["cases"]):
        raise ValueError("leaf diagnostic is for cases with two completed no-change window failures")
    prior = read(verify(configured["source"]))
    full = read(verify(configured["full_unlocked"]))
    source = read(verify(prior["protocol"]))
    if sorted(os.sched_getaffinity(0)) != configured["affinity"]:
        raise ValueError("leaf diagnostic must use the original affinity")
    candidates = {case["proposal"]["label"]: case for case in prior["cases"]}
    baseline = {case["label"]: case for case in full["cases"]}
    seed = read(verify(source["source"]))
    online = read(verify(source["historical_online_protocol"]))
    assets = seed["bindings"]
    control = {key: verify(ref) for key, ref in assets["control"].items()}
    lib = {corner: [verify(ref) for ref in group] for corner, group in assets["used_libraries"].items()}
    out = args.output.resolve()
    out.mkdir()
    runtime = window.seed_args(seed, online)
    runtime.out = out
    views = read(verify(source["reference"]))["views"]
    protocol = out / "protocol.json"
    profiles = configured["profiles"]
    comparison.save(protocol, {"driver": comparison.bind(Path(__file__).resolve()), "source": comparison.bind(selected),
                               "policy": "same capture window; clear only its already eligible clock leaf",
                               "route_timeout": window.ROUTE_LIMIT, "affinity": configured["affinity"],
                               "cleared_leaf": {label: row["shared_leaf"] for label, row in profiles.items()}})
    rows = []
    with window.GEOMETRY.bind_runtime("uart", verify(assets["flow"]["fastroute.tcl"])):
        masters = comparison.logical_masters(control["v"], comparison.liberty_areas(lib["TT"]))
        pool = [comparison.PhysicalAction(**row) for row in online["ordered_pool"]]
        eval = comparison.Evaluator(runtime, control, lib, masters, views, pool, seed["scope"])
        for label in window.CASES:
            profile = dict(profiles[label])
            # The original insertion mode clears exactly the supplied net. Its internal
            # marker retains the field name used by the original D-feeder experiment.
            profile["optional_clear"] = profile["shared_leaf"]
            trial = window.run_trial(eval, out / label, candidates[label], profile, baseline[label], "clear_capture_d")
            trial["mode"] = "clear_capture_clock_leaf"
            trial["cleared_net"] = profile["shared_leaf"]
            trial["label"] = label
            trial["confirmation"] = None
            if not trial["failures"]:
                confirm = window.run_trial(eval, out / f"{label}_confirm", candidates[label], profile, baseline[label], "clear_capture_d")
                trial["confirmation"] = {"result": confirm, "equivalence": window.phase.physical_equivalence(trial, confirm)}
            rows.append(trial)
            comparison.save(out / "progress.json", rows)
            print(label, profile["shared_leaf"], trial["failures"], round(trial["paid_raw_seconds"], 4), flush=True)
    comparison.save(out / "results.json", {"protocol": comparison.bind(protocol), "cases": rows})


if __name__ == "__main__":
    main()
