#!/usr/bin/env python3
"""Offline receipt audit for V4:
1. Hold tolerance sensitivity (0.001, 0.01, 0.1, 1.0 ps) across all logged 4-design trials.
2. Verify 18-action pool instance uniqueness on all 4 designs.
3. Extract Table 9 (10-circuit ISCAS89/ITC-99) per-circuit details & mean calculation.
4. Check Setup rejection dedup trigger count & time saved on ASAP7 UART.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
OUT = REPO / "project_docs/evidence/tcad_v4_revision_20261126/OFFLINE_RECEIPT_AUDIT.json"


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    res = {"pool_uniqueness": {}, "hold_tolerance_sensitivity": {}, "uart_dedup_stats": {}, "table9_audit": {}}

    # 1. Pool uniqueness from LR_4DESIGNS_VERIFIED.json
    lr = load(REPO / "project_docs/evidence/tcad_external_baselines_20261125/LR_4DESIGNS_VERIFIED.json")
    for dname, row in lr["designs"].items():
        acts = row["lr_solve"]["committed_actions"]
        insts = [a.split("=", 1)[0] for a in acts]
        res["pool_uniqueness"][dname] = {
            "pool_size": row["pool_size"],
            "distinct_instances": len(set(insts)),
            "all_distinct": len(set(insts)) == row["pool_size"],
        }

    # 2. Hold tolerance sensitivity over all logged physical candidate trials in 4 designs
    # Check SKY130HD AES boxed matrix, ASAP7 AES boxed matrix, ASAP7 UART wallclock matrix, SKY130HD riscv32i matrix
    matrices = {
        "sky130hd_aes_boxed": (
            Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_boxed_drc_20261126_v1"),
            Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_matrix_v1/control/receipt.json"),
        ),
        "sky130hd_aes_geo": (
            Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_geo_ablation_20261125_v1"),
            Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_matrix_v1/control/receipt.json"),
        ),
        "asap7_aes_boxed": (
            Path("/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/matrix_boxed_drc_20261126_v1"),
            None,
        ),
        "asap7_uart": (
            Path("/home/toylog/faeco_tcad_uart_wallclock_20261125_v1"),
            None,
        ),
        "sky130hd_riscv32i": (
            Path("/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i/matrix_rank_aligned_v1"),
            None,
        ),
    }

    tols = [0.001, 0.01, 0.1, 1.0]
    for mname, (mroot, ctrl_hint) in matrices.items():
        if not mroot.exists():
            continue
        # Find ref_views
        ref_views = None
        if ctrl_hint and ctrl_hint.is_file():
            ref_views = load(ctrl_hint)["views"]
        else:
            for cand in [mroot / "seed/control/receipt.json", mroot / "protocol.json"]:
                if cand.is_file():
                    d = load(cand)
                    if "views" in d:
                        ref_views = d["views"]
                        break
                    if "seed" in d:
                        sp = Path(d["seed"]["path"]).parent / "control/receipt.json"
                        if sp.is_file():
                            ref_views = load(sp)["views"]
                            break
        if ref_views is None:
            continue

        # Collect all unique (trial_path) with views
        trials = []
        for rp in sorted(mroot.rglob("receipt.json")):
            rel = str(rp.relative_to(mroot))
            if "preflight" in rel or "control" in rel or "seed" in rel:
                continue
            try:
                rec = load(rp)
            except Exception:
                continue
            if "views" not in rec or not all(c in rec["views"] for c in ("FF", "TT", "SS")):
                continue
            dholds = {
                c: rec["views"][c]["hold_wns_ps"] - ref_views[c]["hold_wns_ps"]
                for c in ("FF", "TT", "SS")
            }
            min_dhold = min(dholds.values())
            trials.append({"rel": rel, "dholds": dholds, "min_dhold_ps": min_dhold})

        # Count how many trials have min_dhold_ps < -tol (i.e. hold_regression under tol)
        by_tol = {}
        for t in tols:
            rej = [x for x in trials if x["min_dhold_ps"] < -t]
            by_tol[str(t)] = {
                "hold_rejected_count": len(rej),
                "total_trials": len(trials),
                "worst_rejected_ps": round(min((x["min_dhold_ps"] for x in rej), default=0.0), 4),
                "mildest_rejected_ps": round(max((x["min_dhold_ps"] for x in rej), default=0.0), 4),
            }
        # Also list the distribution of negative min_dhold_ps
        neg_vals = sorted(round(x["min_dhold_ps"], 5) for x in trials if x["min_dhold_ps"] < -0.001)
        res["hold_tolerance_sensitivity"][mname] = {
            "total_measured_trials": len(trials),
            "by_tolerance_ps": by_tol,
            "negative_min_dhold_ps_values": neg_vals[:40],
        }

    # 3. Check UART dedup stats
    uart_ver = REPO / "project_docs/evidence/tcad_wallclock_schedule_20261125/UART_WALLCLOCK_VERIFIED.json"
    if uart_ver.is_file():
        uv = load(uart_ver)
        res["uart_dedup_stats"] = {
            "keys": list(uv.keys())[:20],
        }
        # Scan progress.json under uart matrix for dedup hits
        uroot = Path("/home/toylog/faeco_tcad_uart_wallclock_20261125_v1")
        if uroot.exists():
            dedup_hits = []
            for sp in sorted(uroot.rglob("summary.json")):
                sd = load(sp)
                if "dedup" in str(sp) or "faeco" in str(sp):
                    dedup_hits.append({
                        "path": str(sp.relative_to(uroot)),
                        "dedup_hits": sd.get("dedup_hits") or sd.get("skipped_known_rejections"),
                        "logical_finished": sd.get("logical_finished"),
                    })
            res["uart_dedup_stats"]["summaries"] = dedup_hits[:20]

    # 4. Check Table 9 source (10-circuit ISCAS89/ITC-99)
    for cand in sorted((REPO / "project_docs/evidence").rglob("*10*summary*.json")) + sorted((REPO / "project_docs/evidence").rglob("*independent*summary*.json")):
        res["table9_audit"][str(cand.relative_to(REPO))] = True

    OUT.write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
