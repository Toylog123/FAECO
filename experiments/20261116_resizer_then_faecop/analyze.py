"""P1' pilot analysis: does our ECO still find anything on top of the resizer endpoint?

Arms
----
R_own  : resizer reading from P1 archive (its own flow, post-CTS repair) -- reference only
R'     : exported resizer netlist, re-entered through the standard signoff flow
RF     : our ECO (FAECO-P, single-patch accept, placed_ens gate) applied on top of R'

Gates (written in PREREGISTRATION.md, before any reading of this experiment)
--------------------------------------------------------------------------
H1 feasibility : all three circuits produce R' readings with DRC=0, no error
H2 residual    : RF - R' positive on >=2/3 circuits AND mean(RF - R') >= +0.05 ns
H3 cost        : report only (our stage wall clock / resizer stage wall clock <= 3.0)
Report-only    : re-entry gap = R' - R_own (flagged when |gap| > 0.15 ns)
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
UTILS = (0.30, 0.35, 0.40)
CIRCUITS = ("s382", "s641", "s832")

# P1 archive: resizer arm, three-layout means (experiments/20261115_p1_resizer_vs_faeco/summary.json)
R_OWN = {"s382": -0.84143, "s641": -1.12950, "s832": -1.05870}
# P1 archive: FAECO-P arm (reference only)
F_OWN = {"s382": -0.9962, "s641": -1.6580, "s832": -1.6421}


def _path(util: float, arm: str, circuit: str) -> Path:
    sub = "" if abs(util - 0.35) < 1e-9 else f"_u{util:.2f}"
    return HERE / f"endpoint{sub}" / arm / circuit / "result.json"


def load_arm(arm: str, circuit: str) -> list[dict]:
    out = []
    for u in UTILS:
        p = _path(u, arm, circuit)
        if not p.is_file():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        d["util"] = u
        out.append(d)
    return out


def mean_wns(rows: list[dict]) -> float | None:
    vals = [r["wns"] for r in rows if r.get("wns") is not None]
    return sum(vals) / len(vals) if vals else None


def main() -> int:
    summary: dict = {"circuits": {}, "utils": list(UTILS)}
    h1_ok = True
    deltas: list[float] = []
    gaps: list[float] = []

    for c in CIRCUITS:
        rp = load_arm("Rprime", c)
        rf = load_arm("RF", c)
        rec = {
            "rprime_n": len(rp),
            "rf_n": len(rf),
            "rprime_drc": [r.get("drc_violations") for r in rp],
            "rf_drc": [r.get("drc_violations") for r in rf],
            "rprime_wns_per_util": {f"{r['util']:.2f}": r.get("wns") for r in rp},
            "rf_wns_per_util": {f"{r['util']:.2f}": r.get("wns") for r in rf},
        }
        if len(rp) < len(UTILS) or any(r.get("wns") is None for r in rp) or any(
            (r.get("drc_violations") or 0) != 0 for r in rp
        ):
            h1_ok = False
            rec["h1"] = "FAIL (R' incomplete or dirty)"
        rp_mean = mean_wns(rp)
        rf_mean = mean_wns(rf)
        rec["rprime_mean"] = rp_mean
        rec["rf_mean"] = rf_mean
        rec["r_own"] = R_OWN[c]
        rec["f_own"] = F_OWN[c]
        if rp_mean is not None:
            gaps.append(rp_mean - R_OWN[c])
            rec["reentry_gap"] = rp_mean - R_OWN[c]
        if rp_mean is not None and rf_mean is not None:
            d = rf_mean - rp_mean
            deltas.append(d)
            rec["rf_minus_rprime"] = d
        summary["circuits"][c] = rec

    n_circ = len(CIRCUITS)
    mean_delta = sum(deltas) / len(deltas) if len(deltas) == n_circ else None
    pos = sum(1 for d in deltas if d > 0)
    h2_ok = (len(deltas) == n_circ) and pos >= 2 and mean_delta is not None and mean_delta >= 0.05
    mean_gap = sum(gaps) / len(gaps) if len(gaps) == n_circ else None

    summary["gates"] = {
        "H1_feasibility": "PASS" if h1_ok else "FAIL",
        "H2_residual": {
            "verdict": "PASS" if h2_ok else "FAIL",
            "positive_circuits": f"{pos}/{len(deltas)}",
            "mean_delta_ns": mean_delta,
            "threshold": {"min_positive": "2/3", "min_mean_ns": 0.05},
        },
        "H3_cost": "report-only (see logs)",
        "reentry_gap_mean_ns": mean_gap,
        "reentry_gap_flag": bool(mean_gap is not None and abs(mean_gap) > 0.15),
        "PROMOTE": "YES" if (h1_ok and h2_ok) else "NO",
    }

    print(f"{'circuit':8}{'R_own':>10}{'Rprime':>10}{'RF':>10}{'RF-Rprim':>10}{'gap':>8}")
    for c in CIRCUITS:
        r = summary["circuits"][c]
        def f(x):
            return f"{x:+.4f}" if isinstance(x, (int, float)) else "--"
        print(f"{c:8}{f(r.get('r_own')):>10}{f(r.get('rprime_mean')):>10}"
              f"{f(r.get('rf_mean')):>10}{f(r.get('rf_minus_rprime')):>10}{f(r.get('reentry_gap')):>8}")
    print()
    for k, v in summary["gates"].items():
        print(f"{k}: {v}")

    (HERE / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\nwrote summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())