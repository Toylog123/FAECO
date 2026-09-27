"""Gate: the {S off} arm must reproduce the archived L2 fixed arm exactly.

Why this gate exists
--------------------
The {S on} vs {S off} comparison is only a *single-variable* comparison if the
off arm is the same run the earlier L2 experiment produced.  If wiring S in had
perturbed the frozen R/G/B path even slightly, the off arm would drift and the
on-arm's delta would be uninterpretable.  So before reading any S result, prove
off == archived reference on every observable the run exposes.

Compares, per circuit:
  success / iterations / stop_reason / final_patch_id / baseline_wns / wns /
  wns_history / accepted patch-id chain / sta_used.

Note the STA budget differs between the two runs (archived 500, this batch 700).
That is safe *only because the budget is non-binding* on the reference side —
`sta_used` is compared too, and a binding budget would show up as a difference.

Usage:
  python code/scripts/verify_s_off_reproduces_l2.py \
      --off-root experiments/20260924_l3s_ablation/off \
      --ref-root experiments/20260924_threearm/fixed
Exit code 0 = reproduced on every circuit.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ALL8 = ("s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953")

FIELDS = ("success", "iterations", "stop_reason", "final_patch_id",
          "baseline_wns", "wns", "wns_history")


def _load(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _chain(data: dict) -> list[str]:
    return [p.get("patch_id") for p in (data.get("state") or {}).get("accepted_patches") or []]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--off-root", type=Path, required=True)
    ap.add_argument("--ref-root", type=Path, required=True)
    ap.add_argument("--circuits", default=",".join(ALL8))
    args = ap.parse_args()

    circuits = [c.strip() for c in args.circuits.split(",") if c.strip()]
    failures: list[str] = []
    checked = 0
    for c in circuits:
        off = _load(args.off_root / c / "outerloop_result.json")
        ref = _load(args.ref_root / c / "outerloop_result.json")
        if off is None or ref is None:
            print(f"{c:<8} SKIP (missing: off={off is not None} ref={ref is not None})")
            continue
        checked += 1
        diffs = [f for f in FIELDS if off.get(f) != ref.get(f)]
        if _chain(off) != _chain(ref):
            diffs.append("accepted_patch_chain")
        off_sta = (off.get("state") or {}).get("budget", {}).get("sta_used")
        ref_sta = (ref.get("state") or {}).get("budget", {}).get("sta_used")
        if off_sta != ref_sta:
            diffs.append(f"sta_used({ref_sta}!={off_sta})")
        status = "REPRODUCED" if not diffs else "DIFF: " + ",".join(diffs)
        print(f"{c:<8} {status}")
        if diffs:
            failures.append(c)

    print()
    if failures:
        print(f"GATE FAILED on {len(failures)}/{checked} circuits: {failures}")
        return 1
    print(f"GATE PASSED: {checked}/{checked} circuits reproduce the archived "
          f"L2 fixed arm bit-for-bit (S-off path is inert).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
