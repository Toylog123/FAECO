#!/usr/bin/env python3
"""Run 7nm ASAP7 AES rank-aligned 6-arm forward/reverse 720 RAW s comparison:
faeco_full_drc vs faeco_boxed_drc vs single_boxed_drc (1.0 x H_row merged boxes)."""

from contextlib import ExitStack, contextmanager
from pathlib import Path
import sys

SCRIPT = Path(__file__).resolve()
sys.path.insert(0, str(SCRIPT.parent))
sys.path.insert(0, str(SCRIPT.parents[1] / "tcad_wallclock_schedule_20261125"))
sys.path.insert(0, str(SCRIPT.parents[1] / "tcad_asap7_aes_holdout_20261125"))

import boxed_drc
import run_qualified_wallclock as qualified
from run_asap7_aes_rank_aligned import install, run_aligned_strategy

matrix, comparison = qualified.matrix, qualified.comparison
BOXED_STRATEGIES = ("faeco_full_drc", "faeco_boxed_drc", "single_boxed_drc")


def main():
    expected_box = {"order": None}
    native_register = matrix.preregister
    native_strategy = matrix.run_strategy
    native_diagnose = qualified.QualifiedWallclockComparison.diagnose

    def register(runner, source, output):
        runner.config["rank_alignment_rule"] = (
            "Paired boxed-DRC comparison on 7nm asap7/aes: every arm executes a fresh timed TT sensitivity "
            "rank inside its 720 RAW s window and verifies identical ordering across all 6 arms."
        )
        runner.config["boxed_drc_protocol"] = {
            "strategies": list(BOXED_STRATEGIES),
            "halo_rows": boxed_drc.DEFAULT_HALO_ROWS,
            "box_rule": "1.0 * H_row around each edited instance bbox, clamped to die area, overlapping boxes merged",
            "signoff_drc_unchanged": "independent post-route unlocked_drc still runs full whole-block drt::check_drc",
        }
        runner.config["sources"][SCRIPT.name] = comparison.bind(SCRIPT)
        runner.config["sources"]["boxed_drc.py"] = comparison.bind(Path(boxed_drc.__file__).resolve())
        native_register(runner, source, output)

    def dispatch_strategy(runner, strategy, reference):
        if strategy == "faeco_full_drc":
            base = "faeco_dedup"
            use_boxed = False
        elif strategy == "faeco_boxed_drc":
            base = "faeco_dedup"
            use_boxed = True
        elif strategy == "single_boxed_drc":
            base = "single_sensitivity"
            use_boxed = True
        else:
            raise ValueError(f"unexpected strategy {strategy}")

        def active_diagnose(self_runner, actions, directory):
            if use_boxed:
                return boxed_drc.diagnose_boxed(self_runner, actions, directory, halo_rows=boxed_drc.DEFAULT_HALO_ROWS)
            return native_diagnose(self_runner, actions, directory)

        with install(qualified.QualifiedWallclockComparison, "diagnose", active_diagnose):
            return run_aligned_strategy(runner, base, reference, expected_box, native_strategy)

    if "--confirmed-only" not in sys.argv:
        sys.argv.append("--confirmed-only")

    with (
        install(qualified, "CONFIRMED_STRATEGIES", BOXED_STRATEGIES),
        install(matrix, "preregister", register),
        install(matrix, "run_strategy", dispatch_strategy),
    ):
        return qualified.main()


if __name__ == "__main__":
    raise SystemExit(main())
