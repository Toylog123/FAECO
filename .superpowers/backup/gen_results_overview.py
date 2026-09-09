"""Aggregate every paper-evidence experiment summary into a single
experiments/results.json.  Reuses pre-existing summary files where
present (so we do not re-parse outer-loop JSON for datasets that
already have a curated summary).
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

ROOT = Path("D:/BaiduSyncdisk/03_FAECO")
EXP = ROOT / "experiments"


def _load(p: Path) -> dict | list | None:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _summarize_iscas89_isc99_picorv32(agg: dict) -> dict:
    out = {"iscas89": [], "itc99": [], "picorv32": []}
    for ds in out:
        for r in agg.get(ds, []):
            improvement = (
                round(r["final_wns"] - r["baseline_wns"], 3)
                if r.get("final_wns") is not None and r.get("baseline_wns") is not None
                else None
            )
            out[ds].append({
                "circuit": r["circuit"],
                "baseline_wns": r["baseline_wns"],
                "final_wns": r.get("final_wns"),
                "improvement_ns": improvement,
                "success": r.get("success"),
                "iterations": r.get("iterations"),
                "n_candidate_sta_runs": r.get("n_candidate_sta_runs"),
                "accepted_patch": r.get("final_patch_id"),
            })
    return out


def _stats(rows: list[dict], imp_key: str = "improvement_ns") -> dict:
    if not rows:
        return {"n_circuits": 0}
    imps = [r[imp_key] for r in rows if r.get(imp_key) is not None]
    finals = [r["final_wns"] for r in rows if r.get("final_wns") is not None]
    succ = sum(1 for r in rows if r.get("success"))
    return {
        "n_circuits": len(rows),
        "n_success": succ,
        "n_with_improvement": len(imps),
        "mean_improvement_ns": round(statistics.mean(imps), 3) if imps else None,
        "median_improvement_ns": round(statistics.median(imps), 3) if imps else None,
        "max_improvement_ns": max(imps) if imps else None,
        "min_improvement_ns": min(imps) if imps else None,
        "mean_final_wns": round(statistics.mean(finals), 3) if finals else None,
    }


def _section(rows: list[dict]) -> dict:
    return {"rows": rows, "stats": _stats(rows)}


def _read_joint_depth() -> list[dict]:
    j = _load(EXP / "20260908_joint_depth_ablation" / "joint_depth_summary.json")
    if not j:
        return []
    rows = []
    for depth, d in j.get("joint_depth_ablation", {}).items():
        if depth.startswith("_"):
            continue
        rows.append({
            "case": depth,
            "baseline_wns": d.get("baseline_wns"),
            "final_wns": d.get("final_wns"),
            "improvement_ns": d.get("improvement_ns"),
            "iterations": d.get("iterations"),
            "n_candidate_sta_runs": d.get("n_candidate_sta_runs"),
            "joint_candidate_count": d.get("joint_candidate_count"),
            "joint_best_wns": d.get("joint_best_wns"),
            "accepted_patch": d.get("accepted_patch"),
        })
    return rows


def _read_hold_mode() -> list[dict]:
    arr = _load(EXP / "20260908_hold_mode_itc99" / "hold_mode_summary.json")
    if not arr:
        return []
    rows = []
    for r in arr:
        rows.append({
            "circuit": r.get("circuit"),
            "runtime_s": r.get("runtime_s"),
            "baseline_wns": r.get("baseline_wns"),
            "baseline_min_slack": r.get("baseline_min_slack"),
            "final_wns": r.get("final_wns"),
            "success": r.get("success"),
            "n_candidate_sta_runs": r.get("n_candidate_sta_runs"),
            "accepted_patch": r.get("accepted_patch"),
            "improvement_ns": r.get("improvement_ns"),
            "min_slack_improvement": r.get("min_slack_improvement"),
        })
    return rows


def _read_multi_iter_fix() -> dict:
    j = _load(EXP / "20260908_multi_iter_fix_full" / "multi_iter_fix_summary.json")
    return j or {}


def _read_multi_iter_ablation() -> dict:
    j = _load(EXP / "20260908_multi_iter_ablation" / "multi_iter_summary.json")
    return j or {}


def _read_b17_phase2() -> dict:
    r = _load(EXP / "20260908_phase2_b17_resume" / "b17" / "outerloop_result.json")
    if not r:
        return {}
    final_wns = (r.get("history") or [{}])[-1].get("wns")
    sec_path = EXP / "20260908_phase2_b17_resume" / "sec" / "sec_result.json"
    sec = _load(sec_path) if sec_path.exists() else None
    return {
        "baseline_wns": r.get("baseline_wns"),
        "final_wns": final_wns,
        "improvement_ns": (
            round(final_wns - r["baseline_wns"], 3)
            if final_wns and r.get("baseline_wns") is not None else None
        ),
        "iterations": r.get("iterations"),
        "n_candidate_sta_runs": r.get("n_candidate_sta_runs"),
        "accepted_patch": r.get("final_patch_id"),
        "endpoint": r.get("endpoint"),
        "target_net": r.get("target_net"),
        "strategies": r.get("strategies"),
        "sec": sec,
    }


def main() -> None:
    agg = _load(EXP / "20260826_aggregation" / "summary.json") or {}
    ds = _summarize_iscas89_isc99_picorv32(agg)

    out: dict[str, dict] = {
        "ISCAS89_unified": _section(ds["iscas89"]),
        "ITC-99_unified":  _section(ds["itc99"]),
        "PicoRV32_unified": _section(ds["picorv32"]),
        "b17_phase2_resume": _read_b17_phase2(),
        "joint_depth_ablation": {
            "rows": _read_joint_depth(),
            "stats": _stats(_read_joint_depth()),
        },
        "hold_mode_itc99": {
            "rows": _read_hold_mode(),
            "stats": _stats(_read_hold_mode()),
        },
        "multi_iter_fix_b17": _read_multi_iter_fix(),
        "multi_iter_ablation_b17_b18_b19": _read_multi_iter_ablation(),
    }

    out_path = EXP / "results.json"
    out_path.write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
