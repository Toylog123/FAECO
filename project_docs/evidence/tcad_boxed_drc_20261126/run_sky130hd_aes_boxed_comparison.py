#!/usr/bin/env python3
"""Run 130nm SKY130HD AES 4-arm forward/reverse 720 RAW s comparison:
faeco_full_drc vs faeco_boxed_drc (1.0 x H_row merged boxes)."""

from argparse import ArgumentParser
from pathlib import Path
import sys

SCRIPT = Path(__file__).resolve()
sys.path.insert(0, str(SCRIPT.parent))
IBEX_DIR = SCRIPT.parents[1] / "tcad_ibex_20261123"
if str(IBEX_DIR) not in sys.path:
    sys.path.insert(0, str(IBEX_DIR))

import boxed_drc
from run_aes_cold_online import ColdOnlineComparison
from run_aes_incident_priority_matched_v2 import comparison
from run_aes_protected_online import OnlineProtection
from run_screened_matrix import bind_runtime, raw_seconds


class BoxedDrcComparison(ColdOnlineComparison):
    """Extend ColdOnlineComparison with switchable full vs 1.0*H_row boxed pre-DRT DRC."""

    def __init__(self, matrix, output, diagnosis_mode="full", halo_rows=boxed_drc.DEFAULT_HALO_ROWS):
        super().__init__(matrix, output)
        self.diagnosis_mode = diagnosis_mode
        self.halo_rows = halo_rows

    def diagnose(self, actions, directory):
        if self.diagnosis_mode == "boxed":
            return boxed_drc.diagnose_boxed(self, actions, directory, halo_rows=self.halo_rows)
        if self.diagnosis_mode == "full":
            return super().diagnose(actions, directory)
        raise ValueError(f"unsupported diagnosis_mode {self.diagnosis_mode}")


def ordered_cells():
    forward = [
        ("faeco_full_drc", "full"),
        ("faeco_boxed_drc", "boxed"),
    ]
    return {"forward": forward, "reverse": list(reversed(forward))}


def run_cell(matrix, preflight, cell_root, cohort, label, diag_mode, protocol):
    runner = BoxedDrcComparison(matrix, cell_root, diagnosis_mode=diag_mode)
    method = "faeco"
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        reference = runner.prepare_online(preflight)
        for src in (SCRIPT, Path(boxed_drc.__file__).resolve()):
            runner.config["driver_sources"][src.name] = comparison.bind(src)
            (cell_root / "producer_sources" / src.name).write_bytes(src.read_bytes())
        runner.config.update({
            "methods": [method],
            "diagnosis_mode": diag_mode,
            "halo_rows": boxed_drc.DEFAULT_HALO_ROWS if diag_mode == "boxed" else None,
            "boxed_protocol": protocol,
            "boxed_cell": label,
            "boxed_order": cohort,
        })
        comparison.save(cell_root / "config.json", runner.config)
        print(f"{cohort}/{label}: diagnosis_mode={diag_mode}", flush=True)
        result = runner.arm(method, reference)
    comparison.save(cell_root / "result.json", result)
    return method, result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--preflight", type=Path, default=None)
    parser.add_argument("--fresh-preflight", action="store_true")
    args = parser.parse_args()

    matrix = args.matrix.resolve(strict=True)
    out = args.output.resolve()
    out.mkdir(parents=True)

    if args.fresh_preflight:
        pf_runner = OnlineProtection(matrix, out / "shared_preflight")
        with bind_runtime(pf_runner.top, pf_runner.flow["fastroute.tcl"]):
            pf_runner.preflight()
        preflight = (out / "shared_preflight/preflight/result.json").resolve(strict=True)
    else:
        if args.preflight is None:
            parser.error("--preflight required unless --fresh-preflight is passed")
        preflight = args.preflight.resolve(strict=True)

    orders = ordered_cells()
    plan = out / "boxed_protocol.json"
    comparison.save(plan, {
        "driver": comparison.bind(SCRIPT),
        "boxed_helper": comparison.bind(Path(boxed_drc.__file__).resolve()),
        "matrix": comparison.bind(matrix / "config.json"),
        "preflight": comparison.bind(preflight),
        "orders": orders,
        "wall_limit_seconds_including_screen": 720.0,
        "maximum_requests_per_cell": 6,
        "area_target_pct": 0.01,
        "diagnosis_modes": {
            "full": "Full-block single-thread drt::check_drc after in-place swapMaster and erasing direct signal wires",
            "boxed": "Merged 1.0*H_row per-edited-instance drt::check_drc -box with canonical marker deduplication",
        },
        "signoff_drc_unchanged": "independent post-route unlocked_drc still runs full whole-block drt::check_drc",
        "execution": "serial, CPU 0-5 exclusive, fresh physical work per cell",
    })
    protocol = comparison.bind(plan)

    outcomes = []
    for cohort, cells in orders.items():
        for label, diag_mode in cells:
            start = raw_seconds()
            cell_root = out / cohort / label
            method, summary = run_cell(matrix, preflight, cell_root, cohort, label, diag_mode, protocol)
            stop = raw_seconds()
            outcomes.append({
                "order": cohort,
                "cell": label,
                "diagnosis_mode": diag_mode,
                "method": method,
                "outer_start_raw": start,
                "outer_stop_raw": stop,
                "manifest": comparison.bind(cell_root / "config.json"),
                "summary": comparison.bind(cell_root / method / "summary.json"),
                "result": summary,
            })
            comparison.save(out / "results.json", outcomes)
            window = summary["window"]
            print(
                f"DONE {cohort}/{label}: first={window['time_to_target_seconds']} "
                f"area={window['area_saved']} finished={summary['logical_finished']}/{summary['logical_admitted']}",
                flush=True,
            )


if __name__ == "__main__":
    raise SystemExit(main())
