"""Run multi-iter real-WNS ablation on a sub-set of large ITC-99 circuits.

Purpose: extend the 2026-08-26 unified-loop batch (which used
`--early-stop --candidates-per-iteration 1`) by disabling early-stop
and bumping both the per-iter candidate count and the max-iterations
budget, so that the multi-iter convergence claim can be put on real
WNS trajectories instead of the stage-A proxy.

Usage:
    PYTHONPATH=src python scripts/run_multi_iter_ablation.py \
        --circuits b17 b18 b19 \
        --period 0.5 \
        --output-dir experiments/20260908_multi_iter_ablation
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ITC99 = ROOT / "benchmarks" / "raw" / "itc99" / "v"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--circuits", nargs="+", default=["b17", "b18", "b19"])
    p.add_argument("--period", type=float, default=0.5)
    p.add_argument(
        "--output-dir", type=Path,
        default=ROOT / "experiments" / "20260908_multi_iter_ablation",
    )
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--strategies", default="R,G")
    p.add_argument("--max-instances", type=int, default=8)
    p.add_argument("--joint-enumerate-depth", type=int, default=0)
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
            "--clock-port", "CK",
            # Multi-iter ablation specific:
            "--no-early-stop",
            "--max-iterations", "6",
            "--candidates-per-iteration", "4",
            "--max-instances", str(args.max_instances),
            "--joint-enumerate-depth", str(args.joint_enumerate_depth),
        ]
        t0 = time.time()
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        elapsed = round(time.time() - t0, 1)
        log_path = per / "multi_iter_run.log"
        log_path.write_text(proc.stdout + proc.stderr, encoding="utf-8")
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
                "final_wns": final_wns,
                "success": r.get("success"),
                "iterations": r.get("iterations"),
                "n_candidate_sta_runs": r.get("n_candidate_sta_runs"),
                "wns_history": r.get("wns_history"),
                "accepted_patch": r.get("final_patch_id"),
                "improvement_ns": (
                    round(final_wns - r["baseline_wns"], 3)
                    if final_wns and r.get("baseline_wns") is not None
                    else None
                ),
            })
        summary.append(record)
        print(f"{circuit}: exit={proc.returncode} {elapsed}s "
              f"iter={record.get('iterations')} "
              f"baseline={record.get('baseline_wns')} "
              f"final={record.get('final_wns')} "
              f"improvement={record.get('improvement_ns')} ns", flush=True)
    out_summary = out / "multi_iter_summary.json"
    out_summary.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nbatch done; summary written to {out_summary}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
