"""Adjudicate the L3 S ablation (r2 §4.9): {S off} vs {S on}.

Reads ``outerloop_result.json`` from both arms produced by
``run_s_ablation_batch.sh`` and emits:

  1. a per-circuit paired table (final dWNS, max B(k), #real-STA, k-to-first,
     accepted patches, stop reason, STA used);
  2. the S engagement ledger per circuit (windows offered/extracted,
     candidates produced, measured, accepted, rejection labels);
  3. paired differences ``on - off`` per circuit (never only means: 8 circuits
     cannot support a significance claim, only direction consistency);
  4. a verdict that separates the two ways "S did nothing" can happen:
     *S never engaged* (windows_extracted == 0) is a **procedure** result and
     invalidates the arm; *S engaged but was rejected/never improved* is a
     **capability** result and is the honest negative finding.

Exit code is always 0 when the data loads; the verdict is a report, not a gate.

Usage:
  python code/scripts/compare_s_ablation.py \
      --root experiments/20260924_l3s_ablation [--json-out out.json] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ARMS = ("off", "on")
ALL8 = ("s27", "s382", "s420", "s641", "s713", "s820", "s832", "s953")
EPS = 1e-9


def load_run(arm_root: Path, arm: str, circuit: str) -> dict | None:
    """One arm x circuit result, or None when missing/incomplete.

    ``arm_root`` is the directory that *contains* the per-circuit run dirs
    (i.e. ``<...>/off`` or ``<...>/on``).
    """
    path = arm_root / circuit / "outerloop_result.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    baseline = data.get("baseline_wns")
    final = data.get("wns")
    curve = data.get("best_wns_curve") or []
    state = data.get("state") or {}
    budget = state.get("budget") or {}
    ledger = data.get("structure_resynth") or {}
    return {
        "arm": arm,
        "circuit": circuit,
        "success": data.get("success"),
        "stop_reason": data.get("stop_reason"),
        "baseline_wns": baseline,
        "final_wns": final,
        "final_dwns": (None if (baseline is None or final is None)
                       else round(final - baseline, 6)),
        "max_bk": round(max(curve), 6) if curve else None,
        "n_sta": len(curve),
        "k_first": data.get("n_sta_to_first_improvement"),
        "n_accepted": len(state.get("accepted_patches") or []),
        "sta_used": budget.get("sta_used"),
        "sta_budget": budget.get("sta_budget"),
        "s": {
            "enabled": ledger.get("enabled"),
            "windows_offered": ledger.get("windows_offered"),
            "windows_extracted": ledger.get("windows_extracted"),
            "candidates": ledger.get("candidates"),
            "measured": ledger.get("measured"),
            "accepted": ledger.get("accepted"),
            "rounds_with_s": ledger.get("rounds_with_s") or [],
            "rejection_labels": sorted({
                r.get("label") for r in (ledger.get("rejections") or [])
                if r.get("label")
            }),
        },
    }


def _fmt(value, width: int = 8, nd: int = 3) -> str:
    if value is None:
        return " " * (width - 1) + "-"
    if isinstance(value, float):
        return f"{value:>{width}.{nd}f}"
    return f"{value:>{width}}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None,
                    help="Single root holding both <arm>/<circuit>/ trees "
                         "(default when --off-root/--on-root are omitted)")
    ap.add_argument("--off-root", type=Path, default=None,
                    help="Explicit control-arm root (overrides --root/off)")
    ap.add_argument("--on-root", type=Path, default=None,
                    help="Explicit treatment-arm root (overrides --root/on) — "
                         "lets one control arm be compared against several "
                         "treatment configurations held in separate roots")
    ap.add_argument("--circuits", default=",".join(ALL8))
    ap.add_argument("--json-out", type=Path, default=None)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.root is None and (args.off_root is None or args.on_root is None):
        ap.error("provide --root, or both --off-root and --on-root")
    # roots point at the directory that *contains* the per-circuit run dirs.
    roots = {
        "off": args.off_root if args.off_root is not None else args.root / "off",
        "on": args.on_root if args.on_root is not None else args.root / "on",
    }

    circuits = [c.strip() for c in args.circuits.split(",") if c.strip()]
    runs: dict[tuple[str, str], dict | None] = {}
    for arm in ARMS:
        for c in circuits:
            runs[(arm, c)] = load_run(roots[arm], arm, c)

    missing = [f"{a}/{c}" for a in ARMS for c in circuits if runs[(a, c)] is None]
    paired = [c for c in circuits
              if runs[("off", c)] is not None and runs[("on", c)] is not None]
    if not paired:
        print("no paired runs found (off=%s on=%s)" % (roots["off"], roots["on"]),
              file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"off root: {roots['off']}")
        print(f"on  root: {roots['on']}")
        print(f"paired circuits: {len(paired)}/{len(circuits)}"
              + (f"  MISSING: {missing}" if missing else ""))
        print()
        print("== per-circuit paired table ==")
        header = ("circuit  |   off dWNS   on dWNS  diff  |  off maxBk  on maxBk"
                  "  |  off k1st  on k1st |  off acc  on acc |  on S(w/e/c/m/a)"
                  "         | off sta  on sta | on stop")
        print(header)
        print("-" * len(header))
        for c in paired:
            o, n = runs[("off", c)], runs[("on", c)]
            diff = (None if (o["final_dwns"] is None or n["final_dwns"] is None)
                    else round(n["final_dwns"] - o["final_dwns"], 6))
            s = n["s"]
            sled = (f"{s['windows_offered']}/{s['windows_extracted']}/"
                    f"{s['candidates']}/{s['measured']}/{s['accepted']}")
            print(f"{c:<8} | {_fmt(o['final_dwns'])} {_fmt(n['final_dwns'])} "
                  f"{_fmt(diff)} | {_fmt(o['max_bk'])} {_fmt(n['max_bk'])} | "
                  f"{_fmt(o['k_first'], 8)} {_fmt(n['k_first'], 8)} | "
                  f"{_fmt(o['n_accepted'], 8)} {_fmt(n['n_accepted'], 8)} | "
                  f"{sled:>22} | {_fmt(o['sta_used'], 8)} {_fmt(n['sta_used'], 8)} | "
                  f"{n['stop_reason']}")
        print()

        print("== S engagement ledger ==")
        for c in paired:
            s = runs[("on", c)]["s"]
            labels = ",".join(s["rejection_labels"]) or "-"
            print(f"  {c:<8} enabled={s['enabled']} "
                  f"rounds_with_s={len(s['rounds_with_s'])} "
                  f"offered={s['windows_offered']} extracted={s['windows_extracted']} "
                  f"cand={s['candidates']} measured={s['measured']} "
                  f"accepted={s['accepted']} rejections=[{labels}]")
        print()

        print("== paired differences (on - off) ==")
        for c in paired:
            o, n = runs[("off", c)], runs[("on", c)]
            d_dwns = (None if (o["final_dwns"] is None or n["final_dwns"] is None)
                      else round(n["final_dwns"] - o["final_dwns"], 6))
            d_bk = (None if (o["max_bk"] is None or n["max_bk"] is None)
                    else round(n["max_bk"] - o["max_bk"], 6))
            d_acc = n["n_accepted"] - o["n_accepted"]
            print(f"  {c:<8} dWNS={_fmt(d_dwns)}  maxBk={_fmt(d_bk)}  "
                  f"accepted={d_acc:+d}")
        print()

    # ---- verdict --------------------------------------------------------
    engaged = [c for c in paired if (runs[("on", c)]["s"]["windows_extracted"] or 0) > 0]
    accepted = [c for c in paired if (runs[("on", c)]["s"]["accepted"] or 0) > 0]
    d_dwns = []
    for c in paired:
        o, n = runs[("off", c)], runs[("on", c)]
        if o["final_dwns"] is not None and n["final_dwns"] is not None:
            d_dwns.append((c, round(n["final_dwns"] - o["final_dwns"], 6)))
    improved = [c for c, d in d_dwns if d > EPS]
    worsened = [c for c, d in d_dwns if d < -EPS]
    tied = [c for c, d in d_dwns if abs(d) <= EPS]

    verdict = []
    verdict.append(f"S engaged (>=1 window extracted) on {len(engaged)}/{len(paired)} circuits")
    verdict.append(f"S produced an accepted candidate on {len(accepted)}/{len(paired)} circuits")
    verdict.append(f"final dWNS: improved {len(improved)}, tied {len(tied)}, "
                   f"worsened {len(worsened)} (of {len(d_dwns)} paired)")
    if not engaged:
        verdict.append("VERDICT: INVALID ARM — S never engaged on any circuit; "
                       "the {S on} run does not exercise S and cannot be read as "
                       "'S has no contribution'.")
    elif not accepted and not improved:
        verdict.append("VERDICT: NEGATIVE (capability) — S engaged and was given "
                       "the same budget but produced no accepted candidate and no "
                       "final-WNS change: under this regime S is an optional type, "
                       "not an independent contribution.")
    elif improved and not worsened:
        verdict.append("VERDICT: POSITIVE — S adds a final-WNS improvement on at "
                       "least one circuit and never regresses any circuit.")
    else:
        verdict.append("VERDICT: MIXED — S changes the outcome on at least one "
                       "circuit but not uniformly; report the paired per-circuit "
                       "diffs, never a mean.")

    if not args.quiet:
        print("== verdict ==")
        for line in verdict:
            print("  " + line)

    if args.json_out is not None:
        payload = {
            "off_root": str(roots["off"]),
            "on_root": str(roots["on"]),
            "paired": paired,
            "missing": missing,
            "runs": {f"{a}/{c}": runs[(a, c)] for a in ARMS for c in circuits},
            "paired_dwns": d_dwns,
            "verdict": verdict,
        }
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
