"""P1 analysis: FAECO-P vs OpenROAD resizer on signoff (routed) WNS.

Protocol (see PREREGISTRATION.md §3 + §7 A2):
  base    : standard signoff flow on the W1 mapped.v, 3 layouts (util .30/.35/.40)
  faecop  : standard signoff flow on the FAECO-P final netlist, 3 layouts
  resizer : the resizer arm's OWN flow (standard + repair_timing + detailed_placement),
            3 layouts; reading = that flow's routed.v + routed.spef STA

All three are therefore "each arm measured through the flow it defines", with the same
STA convention (ideal clock + extracted SPEF), same lib, period, util and density.
"""
from __future__ import annotations

import json
from math import comb
from pathlib import Path

from config import BASE_ENDPOINT_DIR, CIRCUITS, ROOT, UTILS

EXP = ROOT
H1_MIN_WINS = 5
H1_MIN_MEAN_DIFF = 0.05


def _read(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return d if d and d.get("wns") is not None and not d.get("error") else d


def endpoint_path(util: float, circuit: str, arm: str) -> Path:
    base = EXP / ("endpoint" if abs(util - 0.35) < 1e-9 else f"endpoint_u{util:.2f}")
    return base / circuit / f"arm{arm}" / "result.json"


def base_path(util: float, circuit: str) -> Path:
    """base readings: this experiment first, then the 20261110 archive (same W1 mapped.v)."""
    here = endpoint_path(util, circuit, "base")
    if here.is_file():
        return here
    sub = "endpoint" if abs(util - 0.35) < 1e-9 else f"endpoint_u{util:.2f}"
    return BASE_ENDPOINT_DIR.parent / sub / circuit / "base" / "result.json"


def resizer_path(util: float, circuit: str) -> Path:
    d = "arms/Resizer" if abs(util - 0.35) < 1e-9 else f"arms/Resizer_u{util:.2f}"
    return EXP / d / circuit / "result.json"


def collect_arm(arm: str) -> dict[str, dict]:
    out = {}
    for c in CIRCUITS:
        vals, drcs, missing = [], [], []
        for util in UTILS:
            if arm == "resizer":
                d = _read(resizer_path(util, c))
            elif arm == "base":
                d = _read(base_path(util, c))
            else:
                d = _read(endpoint_path(util, c, arm))
            if d is None or d.get("wns") is None:
                missing.append(f"{util:.2f}")
                continue
            vals.append(d["wns"])
            drcs.append(d.get("drc_violations"))
        out[c] = {
            "mean": (sum(vals) / len(vals)) if vals else None,
            "per_util": vals,
            "drc": drcs,
            "missing": missing,
            "n_layouts": len(vals),
        }
    return out


def sign_test_p(wins: int, n: int) -> float:
    return sum(comb(n, k) for k in range(wins, n + 1)) / (2 ** n)


def main() -> int:
    base = collect_arm("base")
    faecop = collect_arm("faecop")
    resizer = collect_arm("resizer")
    f2 = collect_arm("f2")  # optional: accept-all variant, if measured

    print("P1 — FAECO-P vs OpenROAD resizer (signoff routed WNS, ns; 3-layout mean)")
    print(f"{'c':6s} {'base':>9s} {'resizer':>9s} {'FAECO-P':>9s} {'F-base':>8s} {'F-R':>8s}  status")

    rows, valid = [], []
    for c in CIRCUITS:
        b, a, f = base[c]["mean"], resizer[c]["mean"], faecop[c]["mean"]
        missing = base[c]["missing"] + resizer[c]["missing"] + faecop[c]["missing"]
        drc_bad = any((v or 0) > 0 for arm in (base, resizer, faecop) for v in arm[c]["drc"])
        if b is None or a is None or f is None:
            status = "incomplete(" + ",".join(missing) + ")"
            rows.append({"circuit": c, "base": b, "resizer": a, "faecop": f, "status": status})
            print(f"{c:6s} {str(round(b,4) if b else None):>9s} {str(round(a,4) if a else None):>9s} "
                  f"{str(round(f,4) if f else None):>9s} {'-':>8s} {'-':>8s}  {status}")
            continue
        g = f - b
        d = f - a
        status = "invalid(drc)" if drc_bad else ("better" if d > 0 else "worse/tie")
        rows.append({"circuit": c, "base": b, "resizer": a, "faecop": f,
                     "faecop_minus_base": g, "faecop_minus_resizer": d, "status": status})
        if not drc_bad:
            valid.append((c, d))
        print(f"{c:6s} {b:9.4f} {a:9.4f} {f:9.4f} {g:+8.4f} {d:+8.4f}  {status}")

    wins = sum(1 for _, d in valid if d > 0)
    n = len(valid)
    mean_diff = sum(d for _, d in valid) / n if n else float("nan")
    p = sign_test_p(wins, n) if n else float("nan")
    h1_wins = wins >= H1_MIN_WINS and n == len(CIRCUITS)
    h1_mean = mean_diff >= H1_MIN_MEAN_DIFF
    promote = bool(h1_wins and h1_mean)

    print(f"\nH1 wins: {wins}/{n} (need ≥{H1_MIN_WINS}) -> {'PASS' if h1_wins else 'FAIL'}")
    print(f"H1 mean diff (F−R): {mean_diff:+.4f} ns (need ≥+{H1_MIN_MEAN_DIFF}) -> {'PASS' if h1_mean else 'FAIL'}")
    print(f"sign test p (one-sided): {p:.6f}")
    print(f"PROMOTE = {'YES' if promote else 'NO'}")

    if any(f2[c]["mean"] is not None for c in CIRCUITS):
        print("\nF2 (accept-all, supplementary, not part of H1):")
        for c in CIRCUITS:
            print(f"  {c:6s} base={base[c]['mean']} F2={f2[c]['mean']}")

    out = {
        "protocol": "base/faecop via standard signoff flow (3 layouts); resizer via its own flow (+repair_timing), 3 layouts",
        "rows": rows,
        "wins": wins,
        "n_valid": n,
        "mean_diff_faecop_minus_resizer": mean_diff,
        "sign_test_p": p,
        "h1_wins_pass": h1_wins,
        "h1_mean_pass": h1_mean,
        "promote": promote,
        "arms": {"base": base, "faecop": faecop, "resizer": resizer, "f2_accept_all": f2},
    }
    (EXP / "summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nWrote {EXP / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())