"""Run the real-WNS outer-loop recovery across multiple ISCAS89 circuits in parallel.

N31-05 batch driver: launches one run_outerloop_real_wns.py subprocess per
circuit (each circuit is a separate OS process, so the OpenSTA/WSL2 calls do not
contend on the GIL), bounded by --parallel concurrent circuits. Inside each
circuit the candidate evaluations can additionally use --workers-per-circuit
parallel OpenSTA workers; the product parallel * workers_per_circuit is the
total concurrent OpenSTA load, so keep it aligned with the machine.

Usage (PowerShell):
  $env:PYTHONPATH='src;scripts'; python scripts/run_outerloop_batch.py \
      --output-dir experiments/20260804_outerloop_batch \
      --circuits s27,s382,s420,s641,s713,s820,s832,s953 \
      --parallel 4 --workers-per-circuit 1 \
      --period 0.5 --max-iterations 8 --candidates-per-iteration 1 \
      --priority-table src/rseco/strategy_priority_table.json --early-stop
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_outerloop_real_wns.py"

DEFAULT_CIRCUITS = [
    "s27", "s382", "s420", "s641",
    "s713", "s820", "s832", "s953",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path, required=True,
                   help="Root output dir; each circuit gets {output-dir}/{circuit}/")
    p.add_argument("--circuits", default=",".join(DEFAULT_CIRCUITS),
                   help="Comma-separated ISCAS89 circuit ids")
    p.add_argument("--parallel", type=int, default=4,
                   help="Max circuits running concurrently (default 4)")
    p.add_argument("--workers-per-circuit", type=int, default=1,
                   help="OpenSTA workers inside each circuit (runner --workers)")
    p.add_argument("--period", type=float, default=0.5)
    p.add_argument("--max-iterations", type=int, default=6)
    p.add_argument("--candidates-per-iteration", type=int, default=8)
    p.add_argument("--no-feedback", action="store_true")
    p.add_argument("--enable-buffer", action="store_true")
    p.add_argument("--tns-aware", action="store_true")
    p.add_argument("--max-instances", type=int, default=8)
    p.add_argument("--priority-table", type=Path, default=None)
    p.add_argument("--early-stop", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    circuits = [c.strip() for c in args.circuits.split(",") if c.strip()]
    if not circuits:
        print("--circuits empty", file=sys.stderr)
        return 1
    out_root = args.output_dir.resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    runner_cmd = [
        sys.executable,
        str(RUNNER),
        "--period", str(args.period),
        "--max-iterations", str(args.max_iterations),
        "--candidates-per-iteration", str(args.candidates_per_iteration),
        "--workers", str(args.workers_per_circuit),
        "--max-instances", str(args.max_instances),
    ]
    if args.no_feedback:
        runner_cmd.append("--no-feedback")
    if args.enable_buffer:
        runner_cmd.append("--enable-buffer")
    if args.tns_aware:
        runner_cmd.append("--tns-aware")
    if args.priority_table is not None:
        runner_cmd += ["--priority-table", str(args.priority_table.resolve())]
    if args.early_stop:
        runner_cmd.append("--early-stop")

    procs: dict = {}
    results: dict = {}
    start = time.time()
    queue = list(circuits)

    def _launch(circuit):
        cmd = runner_cmd + ["--circuit", circuit, "--output-dir", str(out_root / circuit)]
        log_path = out_root / circuit / "runner.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        fh = open(log_path, "w", encoding="utf-8")
        procs[circuit] = subprocess.Popen(cmd, stdout=fh, stderr=subprocess.STDOUT, cwd=str(ROOT))
        print(f"[batch] {circuit}: launched (pid={procs[circuit].pid})")

    initial = queue[: args.parallel]
    for circuit in initial:
        _launch(circuit)
    queue = queue[args.parallel:]

    while procs:
        done = []
        for circuit, proc in list(procs.items()):
            rc = proc.poll()
            if rc is None:
                continue
            results[circuit] = _collect(out_root, circuit, rc)
            done.append(circuit)
        for circuit in done:
            del procs[circuit]
            if queue:
                _launch(queue.pop(0))
        if procs:
            time.sleep(0.5)

    elapsed = time.time() - start
    summary = {
        "elapsed_sec": round(elapsed, 1),
        "parallel": args.parallel,
        "workers_per_circuit": args.workers_per_circuit,
        "circuits": results,
    }
    (out_root / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _print_summary(results, elapsed)
    return 0


def _collect(out_root, circuit, rc):
    res = {"exit_code": rc}
    result_file = out_root / circuit / circuit / "outerloop_result.json"
    if result_file.exists():
        d = json.loads(result_file.read_text(encoding="utf-8"))
        res.update({
            "success": d.get("success"),
            "iterations": d.get("iterations"),
            "wns_history": d.get("wns_history"),
            "baseline_wns": d.get("baseline_wns"),
            "n_candidate_sta_runs": d.get("n_candidate_sta_runs"),
            "final_patch_id": d.get("final_patch_id"),
        })
    else:
        res["error"] = f"no outerloop_result.json (rc={rc})"
    print(f"[batch] {circuit}: done rc={rc} success={res.get('success')} "
          f"sta={res.get('n_candidate_sta_runs')} wns={res.get('wns_history')}")
    return res


def _print_summary(results, elapsed):
    print("\n===== batch summary =====")
    print(f"elapsed: {elapsed:.1f}s")
    ok = [c for c, r in results.items() if r.get("success") is True]
    fail = [c for c, r in results.items() if r.get("success") is not True]
    print(f"success: {len(ok)}/{len(results)}  {sorted(ok)}")
    if fail:
        print(f"failed/unsuccessful: {sorted(fail)}")
    total_sta = sum((r.get("n_candidate_sta_runs") or 0) for r in results.values())
    print(f"total candidate STA runs: {total_sta}")


if __name__ == "__main__":
    raise SystemExit(main())
