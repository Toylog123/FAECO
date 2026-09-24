"""k=1 Fixed-vs-Adaptive discriminant analysis (L2 final adjudication).

Pre-locked verdict rules (user ruling 2026-09-24, BEFORE the k=1 runs):

  * k=1 Adaptive > Fixed  -> EMA retained but repositioned as
    "budget-sensitive adaptive selection";
  * k=1 Adaptive = Fixed  -> EMA demoted; core = candidate space +
    weighted ranking + failure attribution;
  * k=1 Adaptive < Fixed  -> EMA withdrawn to ablation / negative result.

Per circuit the two arms are compared on the r2 §3.6 metrics (final dWNS,
max B(k), k_first, N_STA) plus a mechanism metric only meaningful at k=1:
the number of rounds where the weight change actually changed WHICH single
candidate was verified.

Candidate-identity comparison (per round t, k=1 => one cut per round):
  * rounds where both arms have the same ``base_netlist_hash`` (same
    decision point) are directly comparable;
      - same ``cut_hash``            -> same decision;
      - different ``cut_hash``       -> EMA changed the candidate identity;
  * the first round with differing ``base_netlist_hash`` is the trajectory
    divergence point; later rounds are NOT comparable (different netlist
    state) and are counted as "post-divergence", never as evidence either way.

Per-circuit classification (better/equal/worse), lexicographic:
  1. final dWNS higher -> better; lower -> worse;
  2. tie -> max B(k) higher -> better; lower -> worse;
  3. tie -> k_first lower -> better; higher -> worse;
  4. tie -> N_STA lower -> better; higher -> worse;
  5. else equal.
Verdict = majority direction across circuits (no significance claims).

Usage:
  python scripts/analyze_k1_discriminant.py --root experiments/20260924_l2_k1 \
      [--json-out out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ARMS = ("fixed", "adaptive")
ALL8 = ("s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953")


def load_run(root: Path, arm: str, circuit: str) -> dict | None:
    path = root / arm / circuit / "outerloop_result.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    curve = data.get("best_wns_curve")
    if not curve:
        return None
    trials_path = root / arm / circuit / "eval_trials.json"
    trials: list[dict] = []
    if trials_path.exists():
        payload = json.loads(trials_path.read_text(encoding="utf-8"))
        trials = [t for t in payload.get("trials", [])
                  if "sta_provenance" in t]
    baseline = data.get("baseline_wns")
    final = data.get("wns")
    return {
        "arm": arm,
        "circuit": circuit,
        "n_sta": len(curve),
        "k_first": data.get("n_sta_to_first_improvement"),
        "max_bk": round(max(curve), 6),
        "final_dwns": (None if baseline is None or final is None
                       else round(final - baseline, 6)),
        "stop_reason": data.get("stop_reason"),
        # per-round decision identity, k=1: first real-STA trial of each
        # iteration carries the round's cut identity and netlist state
        "rounds": _round_identities(trials),
    }


def _round_identities(trials: list[dict]) -> dict[int, dict]:
    """iteration -> {base_netlist_hash, cut_hash} (first real-STA trial)."""
    rounds: dict[int, dict] = {}
    for trial in trials:
        if "sta_provenance" not in trial:
            continue  # pre-STA placeholder: not a decision point
        it = trial.get("iteration")
        if it is None or it in rounds:
            continue
        rounds[int(it)] = {
            "base_netlist_hash": trial.get("base_netlist_hash"),
            "cut_hash": trial.get("cut_hash"),
        }
    return rounds


def compare_identities(fixed_rounds: dict[int, dict],
                       adaptive_rounds: dict[int, dict]) -> dict:
    """Rounds where EMA changed WHICH candidate was verified at k=1."""
    same_state_same_cut = 0
    same_state_diff_cut = 0
    divergence_round: int | None = None
    comparable = sorted(set(fixed_rounds) & set(adaptive_rounds))
    for it in comparable:
        if divergence_round is not None:
            break
        f = fixed_rounds[it]
        a = adaptive_rounds[it]
        if f["base_netlist_hash"] != a["base_netlist_hash"]:
            divergence_round = it
            break
        if f["cut_hash"] == a["cut_hash"]:
            same_state_same_cut += 1
        else:
            same_state_diff_cut += 1
    return {
        "comparable_rounds_before_divergence": (
            divergence_round - 1 if divergence_round is not None
            else len(comparable)),
        "same_decision_rounds": same_state_same_cut,
        "identity_changed_rounds": same_state_diff_cut,
        "trajectory_divergence_round": divergence_round,
    }


def classify(fixed: dict, adaptive: dict) -> str:
    """Pre-locked lexicographic per-circuit classification."""
    if adaptive["final_dwns"] > fixed["final_dwns"]:
        return "better"
    if adaptive["final_dwns"] < fixed["final_dwns"]:
        return "worse"
    if adaptive["max_bk"] > fixed["max_bk"]:
        return "better"
    if adaptive["max_bk"] < fixed["max_bk"]:
        return "worse"
    kf_a = adaptive["k_first"] if adaptive["k_first"] is not None else 10**9
    kf_f = fixed["k_first"] if fixed["k_first"] is not None else 10**9
    if kf_a < kf_f:
        return "better"
    if kf_a > kf_f:
        return "worse"
    if adaptive["n_sta"] < fixed["n_sta"]:
        return "better"
    if adaptive["n_sta"] > fixed["n_sta"]:
        return "worse"
    return "equal"


def adjudicate(rows: list[dict]) -> dict:
    counts = {"better": 0, "equal": 0, "worse": 0}
    for row in rows:
        counts[row["classification"]] += 1
    n = sum(counts.values())
    if n == 0:
        verdict = "INSUFFICIENT_DATA"
    elif counts["better"] > counts["worse"] and \
            counts["better"] >= n // 2 + 1:
        verdict = "EMA_POSITIVE_BUDGET_SENSITIVE"
    elif counts["worse"] > counts["better"] and \
            counts["worse"] >= n // 2 + 1:
        verdict = "EMA_NEGATIVE"
    else:
        verdict = "EMA_NO_INDEPENDENT_BENEFIT"
    return {"counts": counts, "n_circuits": n, "verdict": verdict}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path,
                   default=Path("experiments/20260924_l2_k1"))
    p.add_argument("--circuits", default=",".join(ALL8))
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args()
    circuits = tuple(c.strip() for c in args.circuits.split(",") if c.strip())

    runs: dict[str, dict] = {}
    rows: list[dict] = []
    for circuit in circuits:
        fixed = load_run(args.root, "fixed", circuit)
        adaptive = load_run(args.root, "adaptive", circuit)
        if fixed is None or adaptive is None:
            print(f"{circuit}: MISSING ({'fixed' if fixed is None else ''}"
                  f"{'adaptive' if adaptive is None else ''})",
                  file=sys.stderr)
            continue
        runs[circuit] = {"fixed": fixed, "adaptive": adaptive}
        ident = compare_identities(fixed["rounds"], adaptive["rounds"])
        rows.append({
            "circuit": circuit,
            "fixed": {k: fixed[k] for k in
                      ("n_sta", "k_first", "max_bk", "final_dwns",
                       "stop_reason")},
            "adaptive": {k: adaptive[k] for k in
                         ("n_sta", "k_first", "max_bk", "final_dwns",
                          "stop_reason")},
            "identity_comparison": ident,
            "classification": classify(fixed, adaptive),
        })

    verdict = adjudicate(rows)
    report = {"pre_locked_criteria": {
        "better": "EMA_POSITIVE_BUDGET_SENSITIVE",
        "equal": "EMA_NO_INDEPENDENT_BENEFIT",
        "worse": "EMA_NEGATIVE",
    }, "rows": rows, "verdict": verdict}
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")

    print(f"{'circuit':8s} {'cls':7s} "
          f"{'nSTA f->a':>14s} {'k1st f->a':>11s} "
          f"{'dWNS f->a':>13s} {'id-changed':>10s} {'diverge@':>8s}")
    for row in rows:
        ident = row["identity_comparison"]
        print(f"{row['circuit']:8s} {row['classification']:7s} "
              f"{row['fixed']['n_sta']:>6d}->{row['adaptive']['n_sta']:<6d} "
              f"{str(row['fixed']['k_first']):>5}->{str(row['adaptive']['k_first']):<5}"
              f" {row['fixed']['final_dwns']:>6.3f}->{row['adaptive']['final_dwns']:<6.3f}"
              f" {ident['identity_changed_rounds']:>10d} "
              f"{str(ident['trajectory_divergence_round']):>8s}")
    print(f"\nverdict: {verdict['verdict']}  counts={verdict['counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
