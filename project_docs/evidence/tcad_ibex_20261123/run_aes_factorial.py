#!/usr/bin/env python3
"""Run fresh AES scheduler × diagnostic-backend cells in forward and reverse order."""

from argparse import ArgumentParser
from pathlib import Path

from run_aes_cold_online import ColdOnlineComparison
from run_aes_incident_priority_matched_v2 import CorrectedComparison, comparison
from run_screened_matrix import bind_runtime, raw_seconds


def ordered_cells():
    forward = [("fixed_legacy", "fixed", False), ("fixed_online", "fixed", True),
               ("faeco_legacy", "faeco", False), ("faeco_online", "faeco", True)]
    return {"forward": forward, "reverse": list(reversed(forward))}


def run_cell(matrix, preflight, cell_root, cohort, label, scheduler, online, protocol):
    runner = ColdOnlineComparison(matrix, cell_root)
    method = "fixed_online" if scheduler == "fixed" and online else scheduler
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        reference = runner.prepare_online(preflight)
        source = Path(__file__).resolve()
        runner.config["driver_sources"][source.name] = comparison.bind(source)
        (cell_root / "producer_sources" / source.name).write_bytes(source.read_bytes())
        runner.config.update({"methods": [method], "diagnostic_methods": [method] if online else [],
                              "factorial_protocol": protocol, "factorial_cell": label, "factorial_order": cohort,
                              "scheduler": scheduler, "online_diagnostics": online})
        comparison.save(cell_root / "config.json", runner.config)
        print(f"{cohort}/{label}: {method}; online diagnostics={online}", flush=True)
        if online:
            result = runner.arm(method, reference)
        else:
            runner.use_preview = False
            result = CorrectedComparison.arm(runner, method, reference)
    comparison.save(cell_root / "result.json", result)
    return method, result


def main():
    parser = ArgumentParser(description=__doc__)
    for field in ("matrix", "preflight", "output"):
        parser.add_argument(field, type=Path)
    args = parser.parse_args()
    matrix, preflight = (item.resolve(strict=True) for item in (args.matrix, args.preflight))
    out = args.output.resolve()
    out.mkdir(parents=True)
    plan = out / "factorial_protocol.json"
    comparison.save(plan, {"driver": comparison.bind(Path(__file__)), "matrix": comparison.bind(matrix / "config.json"),
                           "preflight": comparison.bind(preflight), "orders": ordered_cells(),
                           "wall_limit_seconds_including_screen": 720.0, "maximum_requests_per_cell": 6,
                           "area_target_pct": 0.01, "execution": "serial, fresh physical work per cell"})
    protocol = comparison.bind(plan)
    outcomes = []
    for cohort, cells in ordered_cells().items():
        for label, scheduler, online in cells:
            start = raw_seconds()
            cell_root = out / cohort / label
            method, summary = run_cell(matrix, preflight, cell_root, cohort, label, scheduler, online, protocol)
            stop = raw_seconds()
            outcomes.append({"order": cohort, "cell": label, "method": method, "outer_start_raw": start,
                             "outer_stop_raw": stop, "manifest": comparison.bind(cell_root / "config.json"),
                             "summary": comparison.bind(cell_root / method / "summary.json"), "result": summary})
            comparison.save(out / "results.json", outcomes)
            window = summary["window"]
            print(f"{cohort}/{label}: first={window['time_to_target_seconds']}; area={window['area_saved']}", flush=True)


if __name__ == "__main__":
    main()
