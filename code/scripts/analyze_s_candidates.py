"""Characterise the S candidates the loop actually measured (why none was accepted).

Reads ``eval_trials.json`` from the {S on} arm and, for every trial with
``kind == "S"``, reports the r2 §4.8 two-layer depth delta, the R_S verdict, and
the measured WNS delta against the *concurrently committed* baseline.

Reconstructing the concurrent baseline matters: the loop's baseline moves with
every accept, so comparing an S candidate's WNS against the final baseline would
overstate the gap.  Walking the trial sequence in order and advancing the
baseline on every ``accepted`` trial recovers the delta the accept decision
actually used.

The headline number for the report is the cross-tabulation of
``ΔL(SKY130) > 0`` against ``ΔWNS > 0``: it separates "S failed to reduce
structure" from "S reduced structure but the SKY130 depth (the authoritative
layer, r2 §4.8) did not move".

Usage:
  python code/scripts/analyze_s_candidates.py --root experiments/20260924_l3s_ablation/on
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ALL8 = ("s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953")


def _trials(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("trials", [])
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, required=True,
                    help="Directory containing <circuit>/eval_trials.json")
    ap.add_argument("--circuits", default=",".join(ALL8))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    circuits = [c.strip() for c in args.circuits.split(",") if c.strip()]
    rows: list[dict] = []
    for c in circuits:
        result_path = args.root / c / "outerloop_result.json"
        baseline = None
        if result_path.exists():
            baseline = json.loads(result_path.read_text(encoding="utf-8")).get(
                "baseline_wns")
        trial_list = _trials(args.root / c / "eval_trials.json")
        # reconstruct the concurrent baseline through the accept chain
        for t in trial_list:
            if t.get("kind") == "S":
                r = t.get("resynth") or {}
                db, da = r.get("depth_before_sky130"), r.get("depth_after_sky130")
                rows.append({
                    "circuit": c,
                    "patch_id": t.get("patch_id"),
                    "iteration": t.get("iteration"),
                    "variant": r.get("variant"),
                    "r_s": r.get("r_s"),
                    "r_s_verdict": r.get("r_s_verdict"),
                    "win_before": r.get("window_gates_before"),
                    "win_after": r.get("window_gates_after"),
                    "dl_blif": (None if (r.get("depth_before") is None
                                         or r.get("depth_after") is None)
                                else r["depth_before"] - r["depth_after"]),
                    "dl_sky130": (None if (db is None or da is None) else db - da),
                    "depth_layer": r.get("depth_layer"),
                    "wns": t.get("wns"),
                    "baseline_at_trial": baseline,
                    "dwns": (None if (t.get("wns") is None or baseline is None)
                             else round(t["wns"] - baseline, 6)),
                    "improved": t.get("improved"),
                })
            if t.get("accepted") and t.get("wns") is not None:
                baseline = t["wns"]

    if not rows:
        print("no S trials found under %s" % args.root)
        return 1

    print(f"S candidates measured: {len(rows)}")
    print()
    print("circuit  variant  R_S   win(b->a)  dL(blif)  dL(sky130)  dWNS     improved")
    print("-" * 76)
    for r in rows:
        rs = f"{r['r_s']:.2f}" if r["r_s"] is not None else "-"
        win = f"{r['win_before']}->{r['win_after']}"
        print(f"{r['circuit']:<8} {r['variant']:<8} {rs:>4}  {win:>9}  "
              f"{r['dl_blif']:>8}  {str(r['dl_sky130']):>10}  "
              f"{r['dwns']:>7}  {r['improved']}")
    print()

    def _count(pred) -> int:
        return sum(1 for r in rows if pred(r))

    n = len(rows)
    dl_sky_pos = _count(lambda r: (r["dl_sky130"] or 0) > 0)
    dl_blif_pos = _count(lambda r: (r["dl_blif"] or 0) > 0)
    dwns_pos = _count(lambda r: (r["dwns"] or 0) > 0)
    both = _count(lambda r: (r["dl_sky130"] or 0) > 0 and (r["dwns"] or 0) > 0)
    print("== cross-tabulation ==")
    print(f"  ΔL(SKY130) > 0           : {dl_sky_pos}/{n}")
    print(f"  ΔL(BLIF)   > 0           : {dl_blif_pos}/{n}")
    print(f"  ΔWNS       > 0           : {dwns_pos}/{n}")
    print(f"  ΔL(SKY130)>0 AND ΔWNS>0  : {both}/{n}")
    print(f"  R_S verdicts             : "
          f"{ {v: _count(lambda r, v=v: r['r_s_verdict'] == v) for v in sorted({r['r_s_verdict'] for r in rows})} }")
    print()
    print("Reading: a candidate whose BLIF depth falls while the SKY130 depth does")
    print("not has not changed the layer STA actually measures (r2 §4.8).  Those are")
    print("structural no-ops for timing, not evidence that the mechanism is broken.")

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps({
            "rows": rows,
            "summary": {
                "n": n,
                "dl_sky130_pos": dl_sky_pos,
                "dl_blif_pos": dl_blif_pos,
                "dwns_pos": dwns_pos,
                "dl_sky130_pos_and_dwns_pos": both,
            },
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
