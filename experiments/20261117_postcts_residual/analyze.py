"""Judge the 20261117 post-CTS residual experiment (PREREGISTRATION.md §3).

Reads the endpoint caches written by measure.py:

  endpoint/{RprimePost,RFpost}/<c>/result.json          (util 0.35)
  endpoint_u0.30/{...}/result.json, endpoint_u0.40/{...}/result.json

and prints H1/H2/H3 plus the re-entry gap against the P1 resizer arm.
Writes summary.json next to this file.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P1_SUMMARY = ROOT / "experiments" / "20261115_p1_resizer_vs_faeco" / "summary.json"

CIRCUITS = ("s382", "s641", "s832")
UTILS = (0.30, 0.35, 0.40)
ARMS = ("RprimePost", "RFpost")

H2_MIN_POSITIVE = 2          # of 3
H2_MIN_MEAN_DELTA = 0.05     # ns
GAP_DECLARE = 0.15           # ns


def sub_dir(util: float) -> str:
    return "endpoint" if abs(util - 0.35) < 1e-9 else f"endpoint_u{util:.2f}"


def read_reading(arm: str, circuit: str, util: float) -> dict | None:
    p = HERE / sub_dir(util) / arm / circuit / "result.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def arm_stats(arm: str) -> dict:
    out = {}
    for c in CIRCUITS:
        per_util = []
        drc = []
        missing = []
        for u in UTILS:
            d = read_reading(arm, c, u)
            if d is None or d.get("wns") is None:
                missing.append(u)
                continue
            per_util.append(float(d["wns"]))
            drc.append(d.get("drc_violations"))
        out[c] = {
            "per_util": per_util,
            "mean": sum(per_util) / len(per_util) if per_util else None,
            "drc": drc,
            "missing": missing,
            "n_layouts": len(per_util),
        }
    return out


def p1_resizer_means() -> dict:
    if not P1_SUMMARY.is_file():
        return {}
    d = json.loads(P1_SUMMARY.read_text(encoding="utf-8"))
    out = {}
    for c in CIRCUITS:
        row = (d.get("arms") or {}).get("resizer", {}).get(c) or {}
        # P1 used label "resizer"; keep a tolerant lookup for "R"
        if not row:
            for key, val in (d.get("arms") or {}).items():
                if key.lower().startswith("resiz") and c in val:
                    row = val[c]
                    break
        if row.get("mean") is not None:
            out[c] = float(row["mean"])
    return out


def main() -> int:
    stats = {arm: arm_stats(arm) for arm in ARMS}
    r_own = p1_resizer_means()

    print("=== three-layout means (WNS ns) ===")
    print(f"{'circuit':8} {'RprimePost':>12} {'RFpost':>12} {'delta':>10} {'R_own(P1)':>11} {'gap':>9}")
    deltas = {}
    gaps = {}
    h1_ok = True
    for c in CIRCUITS:
        rp = stats["RprimePost"][c]
        rf = stats["RFpost"][c]
        if rp["mean"] is None or rf["mean"] is None or rp["missing"] or rf["missing"]:
            h1_ok = False
        if any(d not in (0, None) for d in rp["drc"] + rf["drc"]):
            h1_ok = False
        delta = None if (rp["mean"] is None or rf["mean"] is None) else rf["mean"] - rp["mean"]
        deltas[c] = delta
        gap = None if (rp["mean"] is None or c not in r_own) else rp["mean"] - r_own[c]
        gaps[c] = gap
        print(f"{c:8} {_f(rp['mean']):>12} {_f(rf['mean']):>12} {_f(delta):>10} "
              f"{_f(r_own.get(c)):>11} {_f(gap):>9}")

    valid = [c for c in CIRCUITS if deltas.get(c) is not None]
    positive = [c for c in valid if deltas[c] > 0]
    mean_delta = sum(deltas[c] for c in valid) / len(valid) if valid else None

    gap_vals = [g for g in gaps.values() if g is not None]
    gap_mean = sum(gap_vals) / len(gap_vals) if gap_vals else None
    gap_flag = any(abs(g) > GAP_DECLARE for g in gap_vals)

    h2_pos_pass = len(positive) >= H2_MIN_POSITIVE
    h2_mean_pass = mean_delta is not None and mean_delta >= H2_MIN_MEAN_DELTA
    h2_pass = h2_pos_pass and h2_mean_pass

    print()
    print(f"H1_feasibility: {'PASS' if h1_ok else 'FAIL'}  "
          f"(3 layouts x 3 circuits, DRC=0, all readings present)")
    print(f"H2_residual: {'PASS' if h2_pass else 'FAIL'}  "
          f"positive={len(positive)}/{len(valid)} (need >={H2_MIN_POSITIVE}), "
          f"mean_delta={_f(mean_delta)} (need >={H2_MIN_MEAN_DELTA})")
    print(f"re-entry gap (RprimePost - R_own): mean={_f(gap_mean)} declare_terms={gap_flag}")
    if gap_flag:
        print("  !! at least one |gap| > 0.15 ns -> conclusions are limited to the "
              "RFpost vs RprimePost pairing (PREREGISTRATION.md §3).")
    print(f"PROMOTE={'YES' if (h1_ok and h2_pass) else 'NO'}")

    sta = {}
    for c in CIRCUITS:
        for cand in (HERE / "arms" / "RFpost" / c, HERE / "arms" / "RFpost" / c / c):
            p = cand / "outerloop_result.json"
            if p.is_file():
                try:
                    d = json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    continue
                st = d.get("state") or {}
                acc = st.get("accepted_patches") or []
                kinds = {}
                for a in acc:
                    if isinstance(a, dict):
                        k = a.get("kind") or "?"
                        kinds[k] = kinds.get(k, 0) + 1
                sta[c] = {
                    "n_candidate_sta_runs": d.get("n_candidate_sta_runs"),
                    "n_new_sta_runs": d.get("n_new_sta_runs"),
                    "n_accepted": len(acc),
                    "accepted_kinds": kinds,
                    "success": d.get("success"),
                    "iterations": d.get("iterations"),
                    "stop_reason": d.get("stop_reason"),
                    "runner_wns": d.get("wns"),
                    "baseline_wns": d.get("baseline_wns"),
                    "result_path": str(p.relative_to(ROOT)),
                }
                break
    print()
    print("=== cost (report only) ===")
    for c, s in sta.items():
        print(f"{c:8} sta_runs={s['n_candidate_sta_runs']} accepted={s['n_accepted']} "
              f"kinds={s['accepted_kinds']} iters={s['iterations']} "
              f"stop={s['stop_reason']} success={s['success']} "
              f"judged_wns={s['runner_wns']} (baseline {s['baseline_wns']})")

    summary = {
        "experiment": "20261117_postcts_residual",
        "arms": stats,
        "r_own_p1_resizer": r_own,
        "deltas_rfpost_minus_rprimepost": deltas,
        "reentry_gap": gaps,
        "reentry_gap_mean_ns": gap_mean,
        "reentry_gap_declare_terms": gap_flag,
        "h1_feasibility": h1_ok,
        "h2_positive": len(positive),
        "h2_mean_delta_ns": mean_delta,
        "h2_residual": h2_pass,
        "promote": "YES" if (h1_ok and h2_pass) else "NO",
        "rfpost_runs": sta,
    }
    (HERE / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {HERE / 'summary.json'}")
    return 0


def _f(v) -> str:
    return "n/a" if v is None else f"{v:+.4f}" if abs(v) < 1e3 else f"{v:.1f}"


if __name__ == "__main__":
    raise SystemExit(main())