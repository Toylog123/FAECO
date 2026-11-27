#!/usr/bin/env python3
"""Run the frozen GCD proposal with no, windowed, and full pre-DRT diagnosis."""

from argparse import ArgumentParser
import json
from pathlib import Path
import sys

from run_aes_cold_online import CLEAR_EVENT, diagnostic_tcl
from run_gcd_marker_mechanism import GcdMarkerComparison, bind_runtime, comparison, raw_seconds


SOURCE = Path(__file__).resolve()
sys.path.insert(0, str(SOURCE.parents[1] / "tcad_boxed_drc_20261126"))
from boxed_drc import DEFAULT_HALO_ROWS, boxed_diagnostic_tcl, diagnose_boxed


ORDER = (("ordinary", "ordinary"), ("boxed", "online"), ("online", "online"))
HISTORICAL_SHA256 = {
    "protocol.json": "be1e8b5e6aa0fe00554346f506d0fdd5bdf1a378402d4d8908822eddbbec4c6c",
    "results.json": "08eec7bdc16ba260d8cbb10afdf2db7f7129707c2617f8f58e640e81abb3849c",
}


class GcdWindowComparison(GcdMarkerComparison):
    diagnosis_mode = "ordinary"

    def diagnose(self, actions, directory):
        if self.diagnosis_mode == "boxed":
            return diagnose_boxed(self, actions, directory, halo_rows=DEFAULT_HALO_ROWS)
        return super().diagnose(actions, directory)

    def checked_protocol(self, historical_root):
        history = {name: comparison.bind(historical_root / name) for name in HISTORICAL_SHA256}
        if {name: record["sha256"] for name, record in history.items()} != HISTORICAL_SHA256:
            raise ValueError("historical GCD protocol or result changed")
        previous = json.loads((historical_root / "protocol.json").read_text(encoding="utf-8"))
        static = self.static_check()
        frozen = json.loads(json.dumps(self.config | {"static_check": static}))
        if {key: frozen.get(key) for key in previous if key != "sources"} != {
            key: value for key, value in previous.items() if key != "sources"
        }:
            raise ValueError("GCD inputs, scope, gates, affinity, or historical settings changed")

        _, edits = self.eval.expected_masters(self.actions)
        route = comparison.render_route(self.eval.args, self.eval.libraries["TT"], self.eval.control, self.output, edits)
        full = diagnostic_tcl(route, self.output / "full_drc.rpt")
        boxed = boxed_diagnostic_tcl(route, [edit.instance for edit in edits], self.output)
        if (full.split(CLEAR_EVENT)[0] != boxed.split(CLEAR_EVENT)[0]
                or "drt::check_drc -box " not in boxed or "detailed_route " in boxed):
            raise ValueError("boxed and full DRC must share the same pre-DRT edits and wire clearing")
        sources = dict(self.config["sources"])
        for path in (SOURCE, Path(diagnose_boxed.__code__.co_filename), SOURCE.with_name("prove_ibex.py")):
            sources[path.name] = comparison.bind(path)
        return self.config | {
            "protocol_order": [mode for mode, _ in ORDER],
            "execution_methods": dict(ORDER),
            "halo_rows": DEFAULT_HALO_ROWS,
            "historical": history,
            "sources": sources,
            "static_check": static | {"same_pre_drt_prefix": True},
        }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("seed", type=Path)
    parser.add_argument("historical_root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--check-inputs", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    runner = GcdWindowComparison(args.seed.resolve(strict=True), output)
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        protocol = runner.checked_protocol(args.historical_root.resolve(strict=True))
        if args.check_inputs:
            print(json.dumps(protocol, indent=2))
            return

        output.mkdir(parents=True)
        comparison.save(output / "protocol.json", protocol)
        reference = runner.qualify_zero()
        results = []
        for index, (mode, method) in enumerate(ORDER, 1):
            cell = output / f"cell_{index:02d}"
            cell.mkdir()
            runner.diagnosis_mode = mode
            started = raw_seconds()
            result = runner.run_cell(method, reference, cell)
            results.append({
                "cell": index, "method": method, "diagnosis_mode": mode,
                "outer_start_raw": started, "outer_stop_raw": raw_seconds(), "result": result,
            })
            comparison.save(output / "results.json", results)
            print(f"GCD cell {index} {mode}: area={result['window']['area_saved']}", flush=True)


if __name__ == "__main__":
    main()
