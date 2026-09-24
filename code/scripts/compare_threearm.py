"""Aggregate and adjudicate the r2 §6 three-arm experiment (L2 EMA feedback).

Reads the ``outerloop_result.json`` of every arm x circuit produced by
``run_threearm_batch.sh`` and emits:

  1. a per-circuit table (per arm: final dWNS, #real-STA, k-to-first-
     improvement, max B(k));
  2. per-circuit PAIRED differences adaptive - fixed and adaptive -
     mean(random seeds)  (r2 §6.4: report paired diffs, never only means);
  3. the §6.4 adjudication verdict based on direction consistency across
     circuits (8 circuits -> no significance claims, ever);
  4. the B(k) curve export for plotting.

Exit code is always 0 when the data loads; the verdict is a *report*, not a
gate -- the three-arm comparison answers a research question, not a contract.

Usage:
  python scripts/compare_threearm.py --root experiments/20260924_threearm \
      [--json-out out.json] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ARMS = ("fixed", "random_s1", "random_s2", "random_s3", "adaptive")
RANDOM_ARMS = ("random_s1", "random_s2", "random_s3")
ALL8 = ("s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953")


def load_run(root: Path, arm: str, circuit: str) -> dict | None:
    """One arm x circuit result, or None when missing/incomplete."""
    path = root / arm / circuit / "outerloop_result.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    curve = data.get("best_wns_curve")
    if not curve:
        return None  # B(k) is the adjudication substrate; a run without it
                     # (crashed before any real STA) cannot be paired.
    baseline = data.get("baseline_wns")
    final = data.get("wns")
    return {
        "arm": arm,
        "circuit": circuit,
        "success": data.get("success"),
        "stop_reason": data.get("stop_reason"),
        "baseline_wns": baseline,
        "final_wns": final,
        # dWNS vs the *initial* baseline (positive = improvement; WNS closer
        # to zero is better, so delta = final - baseline).  The result's own
        # wns is the accepted-chain endpoint; B(k) max may exceed it when a
        # measured candidate was never accepted (§6.3).
        "final_dwns": None if (baseline is None or final is None)
                     else round(final - baseline, 6),
        "max_bk": round(max(curve), 6),
        "n_sta": len(curve),
        "k_first": data.get("n_sta_to_first_improvement"),
        "gain_per_100_sta": data.get("wns_gain_per_100_sta"),
        "enable_feedback": data.get("enable_feedback"),
        "random_order": data.get("random_order"),
        "seed": data.get("seed"),
    }


def load_all(root: Path, circuits: tuple[str, ...] = ALL8,
             arms: tuple[str, ...] = ARMS) -> dict[tuple[str, str], dict]:
    out: dict[tuple[str, str], dict] = {}
    for arm in arms:
        for circuit in circuits:
            run = load_run(root, arm, circuit)
            if run is not None:
                out[(arm, circuit)] = run
    return out


def paired_diffs(runs: dict[tuple[str, str], dict],
                 circuits: tuple[str, ...],
                 metric: str) -> tuple[list[dict], dict[str, float | None]]:
    """Per-circuit adaptive-fixed and adaptive-mean(random) paired diffs.

    Returns (per-circuit rows, direction summary).  A diff is None when
    either side is missing -- never imputed, never averaged over gaps.
    """
    rows: list[dict] = []
    for circuit in circuits:
        adaptive = runs.get(("adaptive", circuit))
        fixed = runs.get(("fixed", circuit))
        randoms = [runs[(a, circuit)] for a in RANDOM_ARMS
                   if (a, circuit) in runs]
        random_mean = (statistics.fmean(r[metric] for r in randoms)
                       if randoms and all(r.get(metric) is not None
                                          for r in randoms) else None)
        row: dict = {"circuit": circuit}
        row["adaptive"] = None if adaptive is None else adaptive.get(metric)
        row["fixed"] = None if fixed is None else fixed.get(metric)
        row["random_mean"] = random_mean
        row["diff_vs_fixed"] = (None if row["adaptive"] is None
                                or row["fixed"] is None
                                else round(row["adaptive"] - row["fixed"], 6))
        row["diff_vs_random_mean"] = (None if row["adaptive"] is None
                                      or random_mean is None
                                      else round(row["adaptive"]
                                                 - random_mean, 6))
        rows.append(row)
    diffs = [r["diff_vs_fixed"] for r in rows if r["diff_vs_fixed"] is not None]
    summary = {
        "n_pairs_vs_fixed": len(diffs),
        "adaptive_better_vs_fixed": sum(1 for d in diffs if d > 0),
        "adaptive_worse_vs_fixed": sum(1 for d in diffs if d < 0),
        "adaptive_equal_vs_fixed": sum(1 for d in diffs if d == 0),
        "mean_diff_vs_fixed": (round(statistics.fmean(diffs), 6)
                               if diffs else None),
    }
    return rows, summary


def _not_worse_at_equal_k(curve_a: list[float], curve_f: list[float]) -> bool:
    """adaptive B(k) not below fixed B(k) at every shared k (r2 §6.4)."""
    n = min(len(curve_a), len(curve_f))
    return all(a >= f - 1e-9 for a, f in zip(curve_a[:n], curve_f[:n]))


def adjudicate(root: Path, runs: dict[tuple[str, str], dict],
               circuits: tuple[str, ...]) -> dict:
    """r2 §6.4 verdict from direction consistency (no significance claims)."""
    detail: dict[str, dict] = {}
    for circuit in circuits:
        adaptive = runs.get(("adaptive", circuit))
        fixed = runs.get(("fixed", circuit))
        if adaptive is None or fixed is None:
            continue
        curve_a = json.loads((root / "adaptive" / circuit
                              / "outerloop_result.json").read_text(
                                  encoding="utf-8"))["best_wns_curve"]
        curve_f = json.loads((root / "fixed" / circuit
                              / "outerloop_result.json").read_text(
                                  encoding="utf-8"))["best_wns_curve"]
        detail[circuit] = {
            "bk_not_worse_at_equal_k": _not_worse_at_equal_k(curve_a, curve_f),
            "k_first_lower": (adaptive["k_first"] is not None
                              and (fixed["k_first"] is None
                                   or adaptive["k_first"] < fixed["k_first"])),
            "final_dwns_higher": ((adaptive["final_dwns"] or 0.0)
                                  > (fixed["final_dwns"] or 0.0)),
            "adaptive_used_more_sta": adaptive["n_sta"] > fixed["n_sta"],
        }
    n = len(detail)
    verdict = {
        "n_circuits_paired": n,
        "per_circuit": detail,
        "counts": {
            "bk_not_worse": sum(1 for d in detail.values()
                                if d["bk_not_worse_at_equal_k"]),
            "k_first_lower": sum(1 for d in detail.values()
                                 if d["k_first_lower"]),
            "final_dwns_higher": sum(1 for d in detail.values()
                                     if d["final_dwns_higher"]),
        },
    }
    if n == 0:
        verdict["verdict"] = "INSUFFICIENT_DATA"
        return verdict
    c = verdict["counts"]
    # §6.4 row 3: B(k) curves basically coincide -> no independent
    # contribution.  Operationalise "coincide" as: adaptive not-worse on at
    # most half the circuits AND first-improvement rarely earlier.
    if c["bk_not_worse"] <= n // 2 and c["k_first_lower"] <= n // 2:
        verdict["verdict"] = "NO_INDEPENDENT_CONTRIBUTION"
    elif c["bk_not_worse"] >= n // 2 + 1 and c["k_first_lower"] >= n // 2 + 1:
        verdict["verdict"] = "EMA_FASTER_TO_FIRST_IMPROVEMENT"
    elif c["final_dwns_higher"] >= n // 2 + 1 and c["bk_not_worse"] >= n // 2:
        verdict["verdict"] = "HIGHER_CEILING_AT_STA_COST"
    else:
        verdict["verdict"] = "MIXED"
    return verdict


def export_curves(root: Path, runs: dict[tuple[str, str], dict],
                  circuits: tuple[str, ...]) -> dict:
    curves: dict[str, dict[str, list[float]]] = {}
    for arm in ARMS:
        curves[arm] = {}
        for circuit in circuits:
            if (arm, circuit) not in runs:
                continue
            path = root / arm / circuit / "outerloop_result.json"
            curves[arm][circuit] = json.loads(
                path.read_text(encoding="utf-8"))["best_wns_curve"]
    return curves


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path("experiments/20260924_threearm"))
    p.add_argument("--circuits", default=",".join(ALL8))
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()
    circuits = tuple(c.strip() for c in args.circuits.split(",") if c.strip())

    runs = load_all(args.root, circuits)
    if not args.quiet:
        print(f"loaded {len(runs)} arm-circuit results from {args.root}")
    if not runs:
        print("no complete results found", file=sys.stderr)
        return 1

    table, dwns_summary = paired_diffs(runs, circuits, "final_dwns")
    kfirst_rows, kfirst_summary = paired_diffs(runs, circuits, "k_first")
    verdict = adjudicate(args.root, runs, circuits)
    curves = export_curves(args.root, runs, circuits)

    report = {
        "per_circuit": table,
        "paired_diff_final_dwns": dwns_summary,
        "per_circuit_k_first": kfirst_rows,
        "paired_diff_k_first": kfirst_summary,
        "adjudication": verdict,
        "runs": {f"{a}/{c}": r for (a, c), r in sorted(runs.items())},
    }
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")

    if not args.quiet:
        hdr = f"{'circuit':8s} {'arm':10s} {'dWNS':>8s} {'nSTA':>5s} {'k1st':>5s} {'maxB(k)':>8s} {'stop':>12s}"
        print(hdr)
        for (arm, circuit), r in sorted(runs.items()):
            print(f"{circuit:8s} {arm:10s} "
                  f"{(r['final_dwns'] if r['final_dwns'] is not None else float('nan')):>8.3f} "
                  f"{r['n_sta']:>5d} "
                  f"{(r['k_first'] if r['k_first'] is not None else '-'):>5} "
                  f"{r['max_bk']:>8.3f} {str(r['stop_reason']):>12s}")
        print("\npaired diffs (adaptive - fixed):")
        for row in table:
            print(f"  {row['circuit']:8s} "
                  f"dWNS diff={row['diff_vs_fixed']}  "
                  f"k_first {row['fixed']}->{row['adaptive']}")
        print(f"\nverdict: {verdict['verdict']}  counts={verdict['counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
