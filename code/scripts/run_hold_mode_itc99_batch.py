"""Run hold-mode outer-loop batch on a sub-set of ITC-99 circuits.

The hold-mode runner (`run_outerloop_real_wns.py --hold-mode`) is the
only mode in the unified-loop batch that exercises the
``set_clock_uncertainty -hold`` path and that accepts a patch only when
strict worst-min-slack improves without regressing setup WNS.  The
2026-08-26 batch ran hold-mode only on ISCAS89; this script extends
that to ITC-99 so §7 of the manuscript can quote a hold-mode result
on the larger circuits.

Usage:
    PYTHONPATH=src python scripts/run_hold_mode_itc99_batch.py \
        --circuits b01 b02 b03 b04 b05 b06 b07 b08 b09 b10 b11 b12 b13 b14 \
        --period 0.5 \
        --output-dir experiments/20260908_hold_mode_itc99
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ITC99 = ROOT / "benchmarks" / "raw" / "itc99" / "v"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--circuits", nargs="+",
        default=[
            "b01", "b02", "b03", "b04", "b05", "b06", "b07", "b08", "b09",
            "b10", "b11", "b12", "b13", "b14",
        ],
    )
    p.add_argument("--period", type=float, default=0.5)
    p.add_argument(
        "--output-dir", type=Path,
        default=ROOT / "experiments" / "20260908_hold_mode_itc99",
    )
    p.add_argument(
        "--hold-uncertainty", type=float, default=0.8,
        help="Clock hold uncertainty (ns) injected via set_clock_uncertainty -hold",
    )
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--strategies", default="R,G")
    p.add_argument("--early-stop", action="store_true", default=True)
    p.add_argument("--max-iterations", type=int, default=1)
    p.add_argument(
        "--skip-mapped", action="store_true",
        help="Skip Yosys mapping (rely on cached mapped.v)",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    summary: list[dict] = []
    for circuit in args.circuits:
        src = ITC99 / f"{circuit}.v"
        if not src.exists():
            print(f"{circuit}: source not found, skipping", flush=True)
            continue
        per = out / circuit
        per.mkdir(parents=True, exist_ok=True)
        cmd = [
            "python",
            str(ROOT / "scripts" / "run_outerloop_real_wns.py"),
            "--circuit", circuit,
            "--source-file", str(src),
            "--period", str(args.period),
            "--output-dir", str(per),
            "--strategies", args.strategies,
            "--workers", str(args.workers),
            "--max-iterations", str(args.max_iterations),
            "--clock-port", "CK",
            "--hold-mode",
            "--hold-uncertainty", str(args.hold_uncertainty),
        ]
        if args.skip_mapped:
            cmd += ["--skip-mapping"]
        t0 = time.time()
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        elapsed = round(time.time() - t0, 1)
        log_path = per / "hold_run.log"
        log_path.write_text(proc.stdout + proc.stderr, encoding="utf-8")
        # Try to load the runner's outerloop_result.json
        result_path = per / circuit / "outerloop_result.json"
        record = {
            "circuit": circuit,
            "exit_code": proc.returncode,
            "runtime_s": elapsed,
            "result_path": str(result_path) if result_path.exists() else None,
        }
        if result_path.exists():
            r = json.loads(result_path.read_text(encoding="utf-8"))
            final_wns = (r.get("history") or [{}])[-1].get("wns")
            record.update({
                "baseline_wns": r.get("baseline_wns"),
                "baseline_min_slack": r.get("baseline_min_slack"),
                "final_wns": final_wns,
                "success": r.get("success"),
                "n_candidate_sta_runs": r.get("n_candidate_sta_runs"),
                "accepted_patch": r.get("final_patch_id"),
                "improvement_ns": (
                    round(final_wns - r["baseline_wns"], 3)
                    if final_wns and r.get("baseline_wns") is not None
                    else None
                ),
                "min_slack_improvement": (
                    round((r.get("baseline_min_slack") or 0) -
                          (final_wns or 0), 3)
                    if final_wns is not None
                    else None
                ),
            })
        summary.append(record)
        print(f"{circuit}: exit={proc.returncode} {elapsed}s "
              f"final_wns={record.get('final_wns')} "
              f"improvement={record.get('improvement_ns')} ns", flush=True)
    out_summary = out / "hold_mode_summary.json"
    out_summary.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    succ = sum(1 for r in summary if r.get("success"))
    print(f"\nbatch done: {succ}/{len(summary)} circuits accepted in "
          f"hold-mode; summary written to {out_summary}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
