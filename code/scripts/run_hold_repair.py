"""Run the failure-aware hold-time repair loop on a sequential circuit.

N31-05 review shortboard 3 (scenario expansion): the pre-layout ideal-net
benchmarks have no natural hold violations, so this runner injects a
*controlled* hold scenario via ``set_clock_uncertainty -hold X`` and lets
the B (buffer-insertion) strategy fix the worst min (hold) path:

  1. Yosys -> pure SKY130 mapped netlist;
  2. baseline OpenSTA under the injected hold uncertainty (reports worst
     slack min);
  3. min-path report -> worst hold endpoint DFF + critical instances;
  4. HoldRepairEvaluator measures D-input buffer-chain candidates with real
     OpenSTA and accepts only candidates that strictly improve the worst
     min slack (setup WNS is guarded, not allowed to degrade below the
     baseline);
  5. iterate: keep the accepted candidate netlist, re-measure, and repair
     the next worst endpoint until no strict improvement remains or
     --max-iterations is reached.

Usage (PowerShell):
  $env:PYTHONPATH=\"src\"; python scripts/run_hold_repair.py \\
      --circuit s382 --period 0.5 --hold-uncertainty 0.8 \\
      --output-dir experiments/20260805_hold_repair
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from run_sequential_timing_check import run_opensta, run_yosys_mapping

from rseco.hold_repair import (
    HoldRepairEvaluator,
    parse_hold_critical_instances,
    parse_worst_hold_endpoint,
)
from rseco.opensta import run_opensta_sequential


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--circuit", default="s382", help="ISCAS89 circuit id")
    p.add_argument("--iscas89-dir", type=Path,
                   default=ROOT / "benchmarks" / "raw" / "iscas89")
    p.add_argument("--period", type=float, default=0.5,
                   help="Clock period (ns)")
    p.add_argument("--hold-uncertainty", type=float, default=0.8,
                   help="set_clock_uncertainty -hold value (ns)")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--workers", type=int, default=4,
                   help="Parallel OpenSTA evaluations (1 = serial)")
    p.add_argument("--max-chain", type=int, default=2,
                   help="Max buffers inserted in series per candidate")
    p.add_argument("--max-iterations", type=int, default=5,
                   help="Max repair iterations (one worst endpoint per iteration)")
    p.add_argument("--buf-types", default="sky130_fd_sc_hd__buf_1,sky130_fd_sc_hd__buf_2",
                   help="Comma-separated buffer cell types to try")
    p.add_argument("--skip-mapping", action="store_true",
                   help="Reuse existing mapped.v instead of re-running Yosys")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    circuit_path = args.iscas89_dir / f"{args.circuit}.v"
    if not circuit_path.exists():
        print(f"{args.circuit}: circuit not found: {circuit_path}",
              file=sys.stderr)
        return 1
    out = args.output_dir / args.circuit
    out.mkdir(parents=True, exist_ok=True)

    # 1. Yosys -> pure SKY130 netlist
    mapped = out / "mapped.v"
    if args.skip_mapping and mapped.exists():
        print(f"{args.circuit}: reusing existing mapped.v")
    else:
        errors = run_yosys_mapping(circuit_path, out)
        if errors or not mapped.exists():
            print(f"{args.circuit}: mapping failed", file=sys.stderr)
            return 1
    mapped_text = mapped.read_text(encoding="utf-8", errors="replace")

    # 2. baseline under the injected hold uncertainty
    base = run_opensta(mapped, args.period, out,
                       top_module=args.circuit,
                       hold_uncertainty=args.hold_uncertainty)
    baseline_min = base.get("min_slack")
    baseline_wns = base.get("wns")
    print(f"baseline: wns={baseline_wns} min_slack={baseline_min}")
    if baseline_min is None:
        print(f"{args.circuit}: OpenSTA returned no worst slack min",
              file=sys.stderr)
        return 1

    # 3-5. iterate: parse worst endpoint -> repair with real STA -> keep the
    #       accepted netlist and repeat until no strict improvement
    history: list[dict] = []
    current_text = mapped_text
    current_min = baseline_min
    current_wns = baseline_wns
    for it in range(1, args.max_iterations + 1):
        it_dir = out / f"iter{it:02d}"
        it_dir.mkdir(parents=True, exist_ok=True)
        current_net = it_dir / "mapped.v"
        current_net.write_text(current_text, encoding="utf-8")
        min_dir = it_dir / "minpath"
        min_dir.mkdir(parents=True, exist_ok=True)
        run_opensta_sequential(
            netlist_path=current_net,
            period=args.period,
            output_dir=min_dir,
            top_module=args.circuit,
            hold_uncertainty=args.hold_uncertainty,
            min_path=True,
        )
        sta_text = (min_dir / "sta.log").read_text(encoding="utf-8",
                                                   errors="replace")
        endpoint = parse_worst_hold_endpoint(sta_text)
        path_insts = parse_hold_critical_instances(sta_text)
        cur_base = run_opensta(current_net, args.period, it_dir,
                               top_module=args.circuit,
                               hold_uncertainty=args.hold_uncertainty)
        cur_min = cur_base.get("min_slack")
        cur_wns = cur_base.get("wns")
        print(f"[iter {it}] endpoint={endpoint} min_slack={cur_min} wns={cur_wns} path_insts={len(path_insts)}")
        if endpoint is None or cur_min is None:
            print(f"[iter {it}] no endpoint/min slack, stopping")
            break
        evaluator = HoldRepairEvaluator(
            mapped_text=current_text,
            top_module=args.circuit,
            period=args.period,
            baseline_min_slack=cur_min,
            output_dir=it_dir / "eval",
            critical_instances=[endpoint],
            workers=args.workers,
            buf_types=tuple(t for t in args.buf_types.split(",") if t),
            max_chain=args.max_chain,
            hold_uncertainty=args.hold_uncertainty,
        )

        class _Patch:
            patch_id = f"hold_iter{it}"
            gates = [endpoint]

        result = evaluator(_Patch, weights=None)
        evaluator.write_trials(it_dir / "hold_trials.json")
        improved = bool(result.get("improved"))
        accepted = None
        if evaluator.call_log:
            accepted = evaluator.call_log[-1].get("accepted")
        new_min = result.get("min_slack", cur_min)
        entry = {
            "iteration": it,
            "endpoint": endpoint,
            "baseline_min_slack": cur_min,
            "final_min_slack": new_min,
            "improved": improved,
            "accepted": accepted,
            "n_trials": len(evaluator.trials),
        }
        history.append(entry)
        print(f"[iter {it}] -> min_slack={new_min} improved={improved}")
        if improved and accepted is not None and accepted.get("candidate_path"):
            current_text = Path(accepted["candidate_path"]).read_text(
                encoding="utf-8", errors="replace")
            current_min = new_min
        else:
            break

    # 6. write the outcome + full history
    final_min = history[-1]["final_min_slack"] if history else current_min
    summary = {
        "circuit": args.circuit,
        "period_ns": args.period,
        "hold_uncertainty_ns": args.hold_uncertainty,
        "baseline_wns": baseline_wns,
        "baseline_min_slack": baseline_min,
        "final_min_slack": final_min,
        "improved": final_min > baseline_min,
        "n_iterations": len(history),
        "history": history,
        "synthetic_note": "pre-layout ideal nets have no natural hold violations; uncertainty injected for scenario validation",
    }
    (out / "hold_result.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("hold repair summary:", json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
