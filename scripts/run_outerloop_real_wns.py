"""Run the real-WNS outer-loop recovery on an ISCAS89 sequential circuit.

N31-05 real-STA closure: drives the FAECO outer refinement loop
(run_multi_iteration_case) with a real OpenSTA evaluator
(RealWnsEvaluator) instead of a logic-level proxy.  For each candidate
cut produced by the weighted min-cut search, the evaluator:

  1. maps the cut gates onto the real SKY130 mapped netlist;
  2. generates R (equivalent-cell rewrite) / G (gate sizing) / optional B
     (buffer insertion) candidates for the critical-path instances;
  3. measures every candidate with real OpenSTA (pre-layout, ideal nets);
  4. accepts only candidates that strictly improve the baseline WNS.

The outer loop explores candidate cuts in weight order within each
iteration; if none improves WNS it classifies the failure (F4 timing gain
insufficient) and refines the F1-F5 search weights, then re-cuts.  This
makes the recovery genuinely failure-aware and measured end-to-end.

Usage (PowerShell):
  $env:PYTHONPATH='src'; python scripts/run_outerloop_real_wns.py
      --circuit s382 --period 0.5 --output-dir experiments/20260804_outerloop_realwns
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
import subprocess
import sys
import warnings
from pathlib import Path

try:
    from run_sequential_timing_check import (  # reuse verified runners
        _find_oss_cad_root,
        _yosys_env,
        run_opensta,
        run_yosys_mapping,
    )
except ModuleNotFoundError:  # imported by a test runner rather than executed as a script
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run_sequential_timing_check import (
        _find_oss_cad_root,
        _yosys_env,
        run_opensta,
        run_yosys_mapping,
    )

from rseco.flow import run_multi_iteration_case
from rseco.runspec import RunSpec, config_hash
from rseco.search_policy import map_legacy_early_stop
from rseco.sentinel import (
    RunManifest,
    collect_soft_cost_events,
    compute_input_hash,
    new_run_id,
)
from rseco.real_wns import (
    RealWnsEvaluator,
    build_full_netlist_sec_checker,
    build_real_equivalence_checker,
    build_boundary_closure_checker,
    build_r_available,
    dff_d_input_net,
    parse_critical_instances,
    parse_worst_endpoint,
    strip_to_single_module,
)


ROOT = Path(__file__).resolve().parents[1]
LIB = (
    ROOT
    / "benchmarks"
    / "raw"
    / "openroad_flow_scripts_sky130hd"
    / "da8f092a02a8e75658cc3100691aabff05f35629"
    / "lib"
    / "sky130_fd_sc_hd__tt_025C_1v80.lib"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--circuit", default="s382", help="ISCAS89 circuit id")
    p.add_argument("--iscas89-dir", type=Path, default=ROOT / "benchmarks" / "raw" / "iscas89")
    p.add_argument("--source-file", type=Path, default=None,
                   help="Explicit RTL/netlist path (overrides --circuit in iscas89-dir)")
    p.add_argument("--period", type=float, default=0.5, help="Clock period (ns)")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--max-iterations", type=int, default=6)
    p.add_argument("--max-patches", type=int, default=None,
                   help="Hard maximum accepted patches; 0 stops before any candidate")
    p.add_argument("--sta-budget", type=int, default=None,
                   help="Hard maximum candidate STA reservations")
    p.add_argument("--formal-budget", type=int, default=None,
                   help="Hard maximum candidate formal-check reservations")
    p.add_argument("--wall-timeout-s", type=float, default=None,
                   help="Hard wall-clock budget for the outer loop")
    p.add_argument("--candidates-per-iteration", type=int, default=8,
                   help="Cut candidates explored per iteration (beam width; 1 isolates feedback)")
    p.add_argument("--no-feedback", action="store_true",
                   help="Disable F1-F5 weight refinement (ablation control)")
    p.add_argument("--workers", type=int, default=4,
                   help="Parallel OpenSTA evaluations per candidate (1 = serial)")
    p.add_argument("--enable-buffer", action="store_true",
                   help="Also try strategy B (buffer insertion)")
    p.add_argument("--tns-aware", action="store_true",
                   help="Accept WNS-equal candidates that improve TNS")
    p.add_argument("--max-instances", type=int, default=8,
                   help="Max patch gates evaluated per candidate (critical first)")
    p.add_argument("--joint-k", type=int, default=0,
                   help="Enable joint repair: also test a candidate that resizes the top-k "
                        "actionable gates simultaneously (0 disables)")
    p.add_argument("--adaptive", action="store_true",
                   help="Online adaptive decision layer: update per-cell-type strategy "
                        "priority from measured trials (UCB + recency decay) instead of "
                        "the static priority table")
    p.add_argument("--hold-mode", action="store_true",
                   help="Hold-repair mode: evaluate candidates under set_clock_uncertainty "
                        "-hold and accept only strict worst-min-slack improvements that "
                        "do not degrade setup WNS below the baseline")
    p.add_argument("--hold-uncertainty", type=float, default=0.8,
                   help="Clock hold uncertainty (ns) injected via set_clock_uncertainty "
                        "-hold in hold mode")
    p.add_argument("--priority-table", type=Path, default=None,
                   help="Path to strategy_priority_table.json; orders R/G/B by decision layer")
    proxy_group = p.add_mutually_exclusive_group()
    proxy_group.add_argument(
        "--proxy-ranking", action="store_true", dest="proxy_ranking",
        help="Enable auditable pre-STA proxy ranking (opt-in; not used by historical batches)",
    )
    proxy_group.add_argument(
        "--no-proxy-ranking", action="store_false", dest="proxy_ranking",
        help="Preserve the legacy strategy-priority order",
    )
    p.set_defaults(proxy_ranking=False)
    p.add_argument("--skip-mapping", action="store_true",
                   help="Reuse existing mapped.v instead of re-running Yosys")
    p.add_argument("--clock-port", default="CK",
                   help="Clock port name in the mapped netlist (CK for ISCAS89/ITC-99, clk for PicoRV32)")
    p.add_argument("--yosys-wsl", action="store_true",
                   help="Fall back to WSL2 Ubuntu Yosys 0.33 (default is the native\n                   OSS-CAD Suite nightly Yosys 0.67, unified FAECO toolchain)")
    p.add_argument("--early-stop", action="store_true",
                   help="Stop evaluating candidates at first WNS improvement (serial only)")
    p.add_argument("--search-policy", choices=["fast", "balanced", "exhaustive"],
                   default="balanced",
                   help="Explicit search policy; --early-stop is a deprecated alias for fast")
    p.add_argument("--run-id", default=None,
                   help="Explicit sentinel run id; default is {circuit}-{policy}-{timestamp}-{suffix}")
    p.add_argument("--soft-cap-s", type=float, default=60.0,
                   help="STA soft runtime cap (s) for cost-event aggregation in the sentinel manifest")
    p.add_argument("--physical-gate", action="store_true",
                   help="Enable paired physical gating: candidate SPEF WNS gain must meet "
                        "--min-physical-gain and paired TNS/hold must not regress (F6 feedback)")
    p.add_argument("--min-physical-gain", type=float, default=0.010,
                   help="Minimum paired physical candidate-vs-baseline WNS gain in ns")
    p.add_argument("--physical-fanout-penalty", type=float, default=1.0,
                   help="SPEF fanout penalty multiplier (>1 lengthens high-fanout nets)")
    p.add_argument("--physical-depth-penalty", type=float, default=1.0,
                   help="SPEF logic-depth penalty multiplier (>1 lengthens deep paths)")
    p.add_argument("--joint-enumerate-depth", type=int, default=0,
                   help="TCAD sprint: enumerate multi-gate joint candidates along the "
                        "critical path within a sliding window of this depth "
                        "(2..window subsets, bounded to 50); OpenSTA picks the best")
    p.add_argument("--strategies", default="R,G,B",
                   help="Comma-separated strategy kinds to enable (ablation: R, G, B, "
                        "R,G, R,B, G,B, R,G,B)")
    p.add_argument("--init-boundary-penalty", type=float, default=1.0,
                   help="Initial cut boundary penalty (sensitivity analysis lambda_1)")
    p.add_argument("--init-size-penalty", type=float, default=1.0,
                   help="Initial cut size penalty (sensitivity analysis lambda_2)")
    p.add_argument("--init-critical-coverage-reward", type=float, default=1.0,
                   help="Initial critical-coverage reward (sensitivity analysis lambda_3)")
    p.add_argument("--epsilon", type=float, default=0.0,
                   help="Configured timing-comparison epsilon (ns), recorded in logs")
    p.add_argument("--required-metrics", default="setup_wns,setup_tns",
                   help="Comma-separated hard acceptance metrics; default uses only measurable setup WNS/TNS. "
                        "Area/transition/cap/fanout are explicit and fail closed when unavailable.")

    p.add_argument("--physical-unit-len", type=float, default=40.0,
                   help="SPEF unit wire length (um); lower = lighter physical load "
                        "(2um approximates post-placement Manhattan distance)")
    return p.parse_args()


def _git_head_sha() -> str | None:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10
        )
        if proc.returncode == 0:
            return proc.stdout.strip() or None
    except Exception:
        pass
    return None


def _tool_versions() -> dict:
    root = _find_oss_cad_root()
    info = {"oss_cad_root": str(root) if root else None}
    env = _yosys_env() if root is not None else dict(os.environ)
    for name, argv in (
        ("yosys_version", ["yosys", "-V"]),
        ("opensta_version", ["opensta", "--version"]),
    ):
        try:
            proc = subprocess.run(
                argv, capture_output=True, text=True, timeout=10, env=env
            )
            line = (proc.stdout or proc.stderr).strip().splitlines()
            info[name] = line[0] if line and proc.returncode == 0 else None
        except Exception:
            info[name] = None
    return info


def _build_spec(args, policy: str, run_id: str, input_hash: str, out: Path) -> RunSpec:
    strategies = tuple(s.strip() for s in args.strategies.split(",") if s.strip())
    required = tuple(m.strip() for m in args.required_metrics.split(",") if m.strip())
    return RunSpec.defaults().with_overrides(
        {
            "run_id": run_id,
            "case_id": args.circuit,
            "input_hash": input_hash,
            "search_policy": policy,
            "strategies": strategies,
            "max_iterations": args.max_iterations,
            "sta_budget": args.sta_budget if args.sta_budget is not None else 2000,
            "formal_budget": args.formal_budget if args.formal_budget is not None else 200,
            "required_metrics": required,
            "min_gain_ns": float(args.epsilon),
            "output_dir": str(out),
        }
    )


def main() -> int:
    args = parse_args()
    policy = args.search_policy
    if args.early_stop:
        warnings.warn("--early-stop is deprecated; use --search-policy fast",
                      DeprecationWarning, stacklevel=2)
        policy = map_legacy_early_stop(True, warn=lambda m: None).value
    args.early_stop = policy == "fast"
    circuit_path = args.source_file or (args.iscas89_dir / f"{args.circuit}.v")
    if not circuit_path.exists():
        print(f"{args.circuit}: circuit not found: {circuit_path}", file=sys.stderr)
        return 1
    out = args.output_dir / args.circuit
    out.mkdir(parents=True, exist_ok=True)
    run_id = args.run_id or new_run_id(args.circuit, policy)
    sources = {"source": circuit_path, "liberty": LIB}
    if args.priority_table is not None:
        sources["priority_table"] = args.priority_table
    input_hash = compute_input_hash(sources)
    spec = _build_spec(args, policy, run_id, input_hash, out)

    # 1. Yosys -> pure SKY130 netlist (skip if reusing existing mapped.v)
    mapped = out / "mapped.v"
    errors = []
    if args.skip_mapping and mapped.exists():
        print(f"{args.circuit}: reusing existing mapped.v (skip mapping)")
    else:
        yosys_cmd = (["wsl.exe", "-d", "Ubuntu", "--", "/usr/bin/yosys"]
                     if args.yosys_wsl else None)
        errors = run_yosys_mapping(circuit_path, out, yosys_cmd=yosys_cmd)
    if errors or not mapped.exists():
        print(f"{args.circuit}: mapping failed", file=sys.stderr)
        return 1
    mapped_text = mapped.read_text(encoding="utf-8")

    # 2. baseline OpenSTA (single worst path -> parse critical instances)
    base = run_opensta(mapped, args.period, out, top_module=args.circuit,
                       hold_uncertainty=args.hold_uncertainty if args.hold_mode else 0.0,
                       clock_port=args.clock_port, multi_path=True)
    baseline_wns = base["wns"]
    if baseline_wns is None:
        print(f"{args.circuit}: baseline OpenSTA returned no WNS", file=sys.stderr)
        return 1
    baseline_min_slack = base.get("min_slack")
    if args.hold_mode and baseline_min_slack is None:
        print(f"{args.circuit}: hold mode needs worst slack min from OpenSTA "
              "(got None)", file=sys.stderr)
        return 1
    sta_text = (out / "sta.log").read_text(encoding="utf-8", errors="replace")
    critical = parse_critical_instances(sta_text)
    endpoint = parse_worst_endpoint(sta_text)
    target_net = dff_d_input_net(mapped_text, endpoint) if endpoint else None
    if not critical or target_net is None:
        print(f"{args.circuit}: no critical instances / endpoint D net "
              f"(endpoint={endpoint})", file=sys.stderr)
        return 1
    print(f"baseline: wns={baseline_wns} min_slack={baseline_min_slack} "
          f"endpoint={endpoint} D={target_net}")
    print(f"critical path: {critical}")

    # 3. build the FAECO case from the mapped netlist (analysis domain:
    #    single-module version; original == resynthesized placeholder, the
    #    real success criterion is WNS, not logic-level reduction)
    case_dir = out / "case"
    (case_dir / "original").mkdir(parents=True, exist_ok=True)
    (case_dir / "resynthesized").mkdir(parents=True, exist_ok=True)
    single = strip_to_single_module(mapped_text, args.circuit)
    (case_dir / "original" / "original.v").write_text(single, encoding="utf-8")
    (case_dir / "resynthesized" / "resynthesized.v").write_text(single, encoding="utf-8")
    (case_dir / "case.yaml").write_text(
        "case_id: " + args.circuit + "_real_wns\n"
        "target:\n"
        "  output: " + target_net + "\n",
        encoding="utf-8",
    )

    # 4. real-STA evaluator (decision layer: optional strategy priority table)
    priority_table = None
    if args.priority_table is not None:
        priority_table = json.loads(args.priority_table.read_text(encoding="utf-8"))
    evaluator = RealWnsEvaluator(
        mapped_text=mapped_text,
        top_module=args.circuit,
        period=args.period,
        liberty_text=LIB.read_text(encoding="utf-8"),
        baseline_wns=baseline_wns,
        baseline_tns=base.get("tns"),
        output_dir=out / "eval",
        critical_instances=critical,
        workers=args.workers,
        enable_buffer=args.enable_buffer,
        tns_aware=args.tns_aware,
        max_instances=args.max_instances,
        priority_table=priority_table,
        proxy_ranking=args.proxy_ranking,
        adaptive=args.adaptive,
        hold_mode=args.hold_mode,
        baseline_min_slack=baseline_min_slack,
        hold_uncertainty=args.hold_uncertainty,
        search_policy=policy,
        joint_k=args.joint_k,
        joint_enumerate_depth=args.joint_enumerate_depth,
        strategy_filter=tuple(s.strip() for s in args.strategies.split(',') if s.strip()),
        init_boundary_penalty=args.init_boundary_penalty,
        init_size_penalty=args.init_size_penalty,
        init_critical_coverage_reward=args.init_critical_coverage_reward,
        clock_port=args.clock_port,
        physical_gate=args.physical_gate,
        min_physical_gain_ns=args.min_physical_gain,
        physical_fanout_penalty=args.physical_fanout_penalty,
        physical_depth_penalty=args.physical_depth_penalty,
        physical_unit_len_um=args.physical_unit_len,
        strict_gates=True,
        strict_budgets=True,
        required_metrics=tuple(m.strip() for m in args.required_metrics.split(",") if m.strip()),
        epsilon=args.epsilon,
        equivalence_checker=build_real_equivalence_checker(LIB.read_text(encoding="utf-8")),
        topology_sec_checker=build_full_netlist_sec_checker(
            top_module=args.circuit,
            liberty_text=LIB.read_text(encoding="utf-8"),
            artifact_dir=out / "topology-sec",
        ),
        boundary_checker=build_boundary_closure_checker(),
    )

    # 5. outer loop.  Candidate-level equivalence is intentionally fail
    # closed when no functional checker is configured; timing gain alone is
    # never presented as proof of correctness.
    # Joint bi-objective cut: pass which critical-path gates have an R
    # equivalence candidate so the cut graph applies the hard equivalence
    # constraint and the critical-path cover is a first-round default.
    r_available = build_r_available(
        LIB.read_text(encoding="utf-8"), critical, mapped_text
    )
    result = run_multi_iteration_case(
        case_dir,
        max_iterations=args.max_iterations,
        enable_feedback=not args.no_feedback,
        wns_evaluator=evaluator,
        candidates_per_iteration=args.candidates_per_iteration,
        critical_instances=critical,
        r_available=r_available,
        init_weights={
            "boundary_penalty": args.init_boundary_penalty,
            "size_penalty": args.init_size_penalty,
            "critical_coverage_reward": args.init_critical_coverage_reward,
        },
        epsilon=args.epsilon,
        max_patches=args.max_patches,
        sta_budget=args.sta_budget,
        formal_budget=args.formal_budget,
        wall_timeout_s=args.wall_timeout_s,
    )
    result["circuit"] = args.circuit
    result["search_policy"] = policy
    result["run_id"] = run_id
    result["input_hash"] = input_hash
    result["run_spec_hash"] = config_hash(spec)
    result["period_ns"] = args.period
    result["baseline_wns"] = baseline_wns
    result["baseline_min_slack"] = baseline_min_slack
    result["hold_mode"] = args.hold_mode
    result["strategies"] = [s.strip() for s in args.strategies.split(',') if s.strip()]
    result["joint_enumerate_depth"] = args.joint_enumerate_depth
    result["init_weights"] = {
        "boundary_penalty": args.init_boundary_penalty,
        "size_penalty": args.init_size_penalty,
        "critical_coverage_reward": args.init_critical_coverage_reward,
    }
    result["hold_uncertainty_ns"] = args.hold_uncertainty if args.hold_mode else None
    result["min_physical_gain_ns"] = args.min_physical_gain
    result["critical_instances"] = critical
    result["proxy_ranking"] = args.proxy_ranking
    result["endpoint"] = endpoint
    result["target_net"] = target_net
    result["n_candidate_sta_runs"] = len(evaluator.trials)
    if hasattr(result.get("weights"), "__dataclass_fields__"):
        result["weights"] = asdict(result["weights"])
    (out / "outerloop_result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    evaluator.write_trials(out / "eval_trials.json")
    soft_cost_events = collect_soft_cost_events(evaluator.trials, soft_cap_s=args.soft_cap_s)
    toolchain = _tool_versions()
    toolchain["git_head_sha"] = _git_head_sha()
    manifest = RunManifest(
        run_id=run_id,
        circuit_id=args.circuit,
        search_policy=policy,
        period_ns=args.period,
        input_hash=input_hash,
        run_spec_hash=result["run_spec_hash"],
        resolved_snapshot=spec.resolved_snapshot(),
        started_at_utc=datetime.now(timezone.utc).isoformat(),
        argv=list(sys.argv),
        toolchain=toolchain,
        outcome={
            "success": bool(result.get("success")),
            "iterations": result.get("iterations"),
            "wns_history": result.get("wns_history"),
            "baseline_wns": baseline_wns,
            "final_patch_id": result.get("final_patch_id"),
            "n_candidate_sta_runs": len(evaluator.trials),
            "round_stop_reasons": [
                c.get("coverage", {}).get("round_stop_reason")
                for c in evaluator.call_log
                if c.get("coverage")
            ],
            "soft_cost_events": soft_cost_events,
            "hard_timeout_events": [
                e
                for t in evaluator.trials
                for e in t.get("failure_events", [])
                if e.get("type")
                in {
                    "deadline_exhausted",
                    "sta_budget_exhausted",
                    "formal_budget_exhausted",
                    "candidate_hard_timeout",
                }
            ],
        },
    )
    (out / "sentinel_manifest.json").write_text(manifest.to_json(), encoding="utf-8")

    print(f"outer loop: success={result['success']} iterations={result['iterations']}")
    print(f"wns_history={result.get('wns_history')}")
    if result["success"]:
        print(f"accepted patch: {result['final_patch_id']} at wns="
              f"{result['history'][-1].get('wns')}")
    else:
        print("no candidate improved WNS; see outerloop_result.json for the "
              "refined weights / failure history")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
