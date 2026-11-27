#!/usr/bin/env python3
"""Measure GCD with the previously observed repair neighbor released on the first pass."""

from argparse import ArgumentParser
import json
from pathlib import Path

from run_gcd_window_diagnosis import GcdWindowComparison, bind_runtime, comparison, raw_seconds


NEIGHBOR = "net242"


class GcdKnownNeighborComparison(GcdWindowComparison):
    def diagnose(self, actions, directory):
        _, incident = self.direct_nets(actions)
        if NEIGHBOR in incident or "+ ROUTED " not in self.nets[NEIGHBOR]:
            raise ValueError("known release must be an initially protected routed net")
        directory.mkdir(parents=True)
        comparison.save(directory / "known_neighbor.json", {
            "actions": list(actions), "released_neighbors": [NEIGHBOR],
            "source": "post hoc control using the previously recorded GCD retry decision",
        })
        return {NEIGHBOR}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("seed", type=Path)
    parser.add_argument("historical_root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    history = args.historical_root.resolve(strict=True)
    runner = GcdKnownNeighborComparison(args.seed.resolve(strict=True), output)
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        protocol = runner.checked_protocol(history)
        known = history / "cell_01/ordinary/01/retry_decision.json"
        if json.loads(known.read_bytes())["released_neighbors"] != [NEIGHBOR]:
            raise ValueError("recorded repair decision does not support the intervention")
        protocol["sources"][Path(__file__).name] = comparison.bind(Path(__file__).resolve())
        protocol.update(protocol_order=["known_neighbor"], execution_methods={"known_neighbor": "online"},
                        release_source=comparison.bind(known), initial_release_cap=1)
        del protocol["halo_rows"]
        output.mkdir(parents=True)
        comparison.save(output / "protocol.json", protocol)
        reference = runner.qualify_zero()
        cell = output / "cell_01"
        cell.mkdir()
        started = raw_seconds()
        result = runner.run_cell("online", reference, cell)
        comparison.save(output / "results.json", [{
            "cell": 1, "method": "online", "diagnosis_mode": "known_neighbor", "result": result,
            "outer_start_raw": started, "outer_stop_raw": raw_seconds(),
        }])
        print(f"GCD known neighbor: area={result['window']['area_saved']}", flush=True)


if __name__ == "__main__":
    main()
