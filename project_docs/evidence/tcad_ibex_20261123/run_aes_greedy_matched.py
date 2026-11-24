#!/usr/bin/env python3
"""Compare fresh single-gate and FAECO searches on the same online AES backend."""

from argparse import ArgumentParser
from pathlib import Path

from run_aes_cold_online import ColdOnlineComparison
from run_aes_incident_priority_matched_v2 import CorrectedComparison, comparison
from run_aes_protected_online import LIMIT_SECONDS, MAX_REQUESTS
from run_screened_matrix import bind_runtime, raw_seconds


def ordered_methods():
    forward = ("single", "faeco")
    return {"forward": forward, "reverse": tuple(reversed(forward))}


def run_online_arm(runner, method, reference):
    runner.use_preview = True
    try:
        return CorrectedComparison.arm(runner, method, reference)
    finally:
        runner.use_preview = False


def run_cell(matrix, preflight, output, order, method, protocol):
    runner = ColdOnlineComparison(matrix, output)
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        reference = runner.prepare_online(preflight)
        source = Path(__file__).resolve()
        runner.config["driver_sources"][source.name] = protocol["driver"]
        (output / "producer_sources" / source.name).write_bytes(source.read_bytes())
        runner.config.update({"methods": [method], "diagnostic_methods": [method], "matched_order": order,
                              "matched_protocol": protocol["binding"], "scheduler": method})
        comparison.save(output / "config.json", runner.config)
        summary = run_online_arm(runner, method, reference)
    comparison.save(output / "result.json", summary)
    return summary


def main():
    parser = ArgumentParser(description=__doc__)
    for field in ("matrix", "preflight", "output"):
        parser.add_argument(field, type=Path)
    args = parser.parse_args()
    matrix, preflight = (item.resolve(strict=True) for item in (args.matrix, args.preflight))
    out = args.output.resolve()
    out.mkdir(parents=True)
    orders = ordered_methods()
    manifest = out / "matched_protocol.json"
    plan = {"driver": comparison.bind(Path(__file__).resolve()), "matrix": comparison.bind(matrix / "config.json"),
            "preflight": comparison.bind(preflight), "orders": orders, "area_target_pct": 0.01,
            "wall_limit_seconds_including_screen": LIMIT_SECONDS, "maximum_requests_per_cell": MAX_REQUESTS,
            "execution": "serial, fresh physical work per cell; both schedulers use current-candidate pre-DRT diagnosis"}
    comparison.save(manifest, plan)
    protocol = {**plan, "binding": comparison.bind(manifest)}
    outcomes = []
    for order, methods in orders.items():
        for method in methods:
            started = raw_seconds()
            cell = out / order / method
            print(f"{order}/{method}: fresh online diagnostic backend", flush=True)
            summary = run_cell(matrix, preflight, cell, order, method, protocol)
            stopped = raw_seconds()
            outcomes.append({"order": order, "cell": method, "method": method, "outer_start_raw": started,
                             "outer_stop_raw": stopped, "manifest": comparison.bind(cell / "config.json"),
                             "summary": comparison.bind(cell / method / "summary.json"), "result": summary})
            comparison.save(out / "results.json", outcomes)
            window = summary["window"]
            print(f"{order}/{method}: first={window['time_to_target_seconds']}; area={window['area_saved']}", flush=True)


if __name__ == "__main__":
    main()
