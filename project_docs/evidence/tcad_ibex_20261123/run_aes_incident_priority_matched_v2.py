#!/usr/bin/env python3
"""Run the unchanged AES comparison with wall-clipped timeouts classified at their source."""

from argparse import ArgumentParser
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path

import run_aes_incident_priority_matched as matched
from run_aes_incident_priority_matched import IncidentPriorityComparison, METHODS, WallWindowEnded, comparison
from run_screened_matrix import bind_runtime, raw_seconds


@contextmanager
def process_ledger(path, deadline):
    source = comparison.run_process
    rows = []

    def invoke(argv, logfile, timeout, *, env=None):
        start = raw_seconds()
        remaining = deadline - start
        if remaining <= 0:
            raise WallWindowEnded()
        wall_clipped = remaining <= timeout
        effective = min(timeout, remaining)
        row = {"command": [str(item) for item in argv], "start_raw": start,
               "effective_timeout_seconds": effective, "configured_timeout_seconds": timeout,
               "timeout_bound": "wall" if wall_clipped else "stage", "log": str(logfile)}
        rows.append(row)
        comparison.save(path, rows)
        result = source(argv, logfile, effective, env=env)
        stopped = raw_seconds()
        row.update(asdict(result), stop_raw=stopped)
        comparison.save(path, rows)
        # A timeout measured by the subprocess clock can return before the RAW deadline.
        if (wall_clipped and result.returncode is None) or stopped >= deadline:
            raise WallWindowEnded()
        return result

    try:
        comparison.run_process = invoke
        yield
    finally:
        comparison.run_process = source


class CorrectedComparison(IncidentPriorityComparison):
    def prepare_pair(self, preflight):
        reference = super().prepare_pair(preflight)
        source = Path(__file__).resolve()
        self.config["driver_sources"][source.name] = comparison.bind(source)
        self.config["timeout_classifier"] = "wall-clipped subprocess timeout ends the arm regardless of RAW return timestamp"
        (self.output / "producer_sources" / source.name).write_bytes(source.read_bytes())
        comparison.save(self.output / "config.json", self.config)
        return reference

    def arm(self, method, reference):
        source = matched.process_ledger
        try:
            matched.process_ledger = process_ledger
            return super().arm(method, reference)
        finally:
            matched.process_ledger = source


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("old_matrix", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("preflight", type=Path)
    args = parser.parse_args()
    runner = CorrectedComparison(args.old_matrix.resolve(strict=True), args.output.resolve())
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        reference = runner.prepare_pair(args.preflight.resolve(strict=True))
        results = {}
        for method in METHODS:
            results[method] = runner.arm(method, reference)
            comparison.save(runner.output / "results.json", results)


if __name__ == "__main__":
    main()
