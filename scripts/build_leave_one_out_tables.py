"""Build leave-one-out strategy priority tables for the decision layer.

For each target circuit, induce a StrategySelector from the OTHER 7 circuits
trial history (experiments/20260803_sequential_hybrid_tns_fixed), then write
{cell_type: [strategy order]} JSON consumable by run_outerloop_real_wns.py
--priority-table. This is the REAL cross-circuit transfer test: the target
circuit is repaired with a table that has never seen its own trials.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CIRCUITS = ["s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953"]
TRIAL_ROOT = ROOT / "experiments" / "20260803_sequential_hybrid_tns_fixed"


def load_trials(circuit):
    p = TRIAL_ROOT / circuit / circuit / "hybrid_result.json"
    if not p.exists():
        return []
    d = json.loads(p.read_text(encoding="utf-8"))
    return d.get("candidate_trials", [])


def build_table(trials):
    sys.path.insert(0, str(ROOT / "src"))
    from rseco.strategy_selector import StrategySelector
    sel = StrategySelector.from_trials(trials)
    table = {}
    types = sorted({t.get("from_type", "") for t in trials if t.get("from_type")})
    for ct in types:
        table[ct] = sel.priority_order(ct)
    return table


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path, default=ROOT / "experiments" / "20260804_loocv_tables")
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    all_trials = {c: load_trials(c) for c in CIRCUITS}
    print("trial counts:", {c: len(v) for c, v in all_trials.items()})
    for target in CIRCUITS:
        other = []
        for c in CIRCUITS:
            if c != target:
                other.extend(all_trials[c])
        table = build_table(other)
        out = args.output_dir / (target + "_loocv.json")
        out.write_text(json.dumps(table, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8")
        target_types = sorted({t.get("from_type", "") for t in all_trials[target] if t.get("from_type")})
        covered = [ct for ct in target_types if ct in table]
        print(f"{target}: table types={len(table)} target types={len(target_types)} covered={len(covered)} ({100*len(covered)/max(1,len(target_types)):.0f}%)")
    print("wrote tables to", args.output_dir)


if __name__ == "__main__":
    raise SystemExit(main())
