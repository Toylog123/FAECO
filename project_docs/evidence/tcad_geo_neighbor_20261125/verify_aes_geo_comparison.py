#!/usr/bin/env python3
"""Independent verifier for AES geometric-neighbor vs live pre-DRT DRC diagnosis 6-arm matrix."""

import hashlib
import json
from pathlib import Path

RAW_ROOT = Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_geo_vs_online_faeco_20261125_v1")
OUT_JSON = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/tcad_geo_neighbor_20261125/AES_GEO_VS_ONLINE_VERIFIED.json")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def spef_dateless_sha(path: Path) -> str:
    h = hashlib.sha256()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True):
        if line.startswith("*DATE "):
            continue
        h.update(line.encode("utf-8"))
    return h.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    results = load_json(RAW_ROOT / "results.json")
    assert len(results) == 6, f"expected 6 arms, got {len(results)}"
    arms = []
    req3_compare = {}
    online_best_fingerprints = {}

    for entry in results:
        order = entry["order"]
        cell = entry["cell"]
        backend = entry["backend"]
        method = entry["method"]
        cell_dir = RAW_ROOT / order / cell
        arm_dir = cell_dir / method
        summary = load_json(arm_dir / "summary.json")
        progress = load_json(arm_dir / "progress.json")
        tools = load_json(arm_dir / "subprocesses.json")
        ref_views = load_json(Path(load_json(cell_dir / "config.json")["control_sta"]["path"]))["views"]

        # Inspect each logical request
        req_details = []
        retries = 0
        total_pre_released = 0
        geo_index_s = None
        geo_idx_file = arm_dir / "diagnosis/geo_index/geo_index_receipt.json"
        if geo_idx_file.is_file():
            geo_index_s = load_json(geo_idx_file)["seconds"]

        for seq in range(1, summary["logical_admitted"] + 1):
            rdir = arm_dir / f"{seq:02d}"
            diag_file = arm_dir / f"diagnosis/{seq:02d}" / ("diagnosis.json" if backend == "online" else "geo_diagnosis.json")
            diag = load_json(diag_file) if diag_file.is_file() else None
            if diag:
                total_pre_released += len(diag.get("released_neighbors", []))
            res_file = rdir / "result.json"
            if not res_file.is_file():
                req_details.append({"seq": seq, "status": "clipped_before_result", "pre_released": len(diag["released_neighbors"]) if diag else 0})
                continue
            rec = load_json(res_file)
            if "retry" in rec["passes"]:
                retries += 1
            final_pass = rec["passes"][-1]
            phys = load_json(rdir / final_pass / "receipt.json")
            hold_deltas = {}
            setup_deltas = {}
            for c in ("FF", "TT", "SS"):
                if c in phys.get("views", {}):
                    hold_deltas[c] = phys["views"][c]["hold_wns_ps"] - ref_views[c]["hold_wns_ps"]
                    setup_deltas[c] = phys["views"][c]["setup_wns_ps"] - ref_views[c]["setup_wns_ps"]
            d = {
                "seq": seq,
                "actions": rec["actions"],
                "passes": rec["passes"],
                "failures": rec["failures"],
                "pre_released_count": len(diag["released_neighbors"]) if diag else 0,
                "pre_released_nets": diag["released_neighbors"] if diag else [],
                "diag_seconds": diag["seconds"] if diag else 0.0,
                "elapsed_seconds": rec["elapsed_seconds"],
                "hold_deltas_ps": hold_deltas,
                "setup_deltas_ps": setup_deltas,
                "area": rec["endpoint"]["area"],
                "valid": rec["endpoint"]["valid"],
                "sec_pass": rec["endpoint"]["sec_pass"],
            }
            req_details.append(d)
            if seq == 3 and order == "forward":
                req3_compare[backend] = d
            if backend == "online" and seq == 4 and rec["endpoint"]["valid"]:
                online_best_fingerprints[order] = {
                    "actions": rec["actions"],
                    "area": rec["endpoint"]["area"],
                    "odb_sha": sha256(Path(phys["artifacts"]["odb"]["path"])),
                    "def_sha": sha256(Path(phys["artifacts"]["def"]["path"])),
                    "v_sha": sha256(Path(phys["artifacts"]["v"]["path"])),
                    "spef_dateless_sha": spef_dateless_sha(Path(phys["artifacts"]["spef"]["path"])),
                    "sec_receipt": load_json(rdir / final_pass / "sec/receipt.json"),
                }

        diag_tools = sum(Path(t["log"]).name in ("preview.log", "geo_bbox.log") for t in tools)
        arm_row = {
            "order": order,
            "cell": cell,
            "backend": backend,
            "stop_reason": summary["stop_reason"],
            "logical_finished": summary["logical_finished"],
            "logical_admitted": summary["logical_admitted"],
            "first_target_seconds": summary["window"]["time_to_target_seconds"],
            "area_saved_um2": summary["window"]["area_saved"],
            "route_tools": summary["route_tools"],
            "unlocked_drc_tools": summary["unlocked_drc_tools"],
            "sta_tools": summary["sta_tools"],
            "sec_tools": summary["sec_tools"],
            "diag_tools": diag_tools,
            "completed_retries": retries,
            "geo_index_seconds": geo_index_s,
            "total_pre_released_nets": total_pre_released,
            "requests": req_details,
        }
        arms.append(arm_row)
        print(f"{order:7s} | {backend:10s} | fin={arm_row['logical_finished']}/{arm_row['logical_admitted']} | "
              f"first={str(round(arm_row['first_target_seconds'],2)) if arm_row['first_target_seconds'] else 'None':>6s} | "
              f"area={arm_row['area_saved_um2']:8.4f} | route={arm_row['route_tools']} retries={retries} sec={arm_row['sec_tools']} pre_rel={total_pre_released}")

    # Cross-check Request 3 identical actions across all 3 backends
    print("\n=== Forward Request 3 Direct Causal Comparison (Same 3-Gate Proposal) ===")
    r3_actions = {b: req3_compare[b]["actions"] for b in ("geo_m1_k1", "geo_m1_r0", "online")}
    same_r3_actions = len({tuple(v) for v in r3_actions.values()}) == 1
    print("Same actions across all 3 backends:", same_r3_actions)
    for b in ("geo_m1_k1", "geo_m1_r0", "online"):
        r = req3_compare[b]
        hd = r["hold_deltas_ps"]
        print(f"  {b:10s}: passes={r['passes']} pre_rel={r['pre_released_count']:2d} diag={r['diag_seconds']:5.2f}s elapsed={r['elapsed_seconds']:6.2f}s "
              f"dHold(FF/TT/SS)={hd['FF']:+.6f}/{hd['TT']:+.6f}/{hd['SS']:+.6f} ps | fails={r['failures']}")

    # Cross-order reproducibility check for online best endpoint
    fwd_fp, rev_fp = online_best_fingerprints["forward"], online_best_fingerprints["reverse"]
    cross_order_exact = (
        fwd_fp["actions"] == rev_fp["actions"]
        and fwd_fp["odb_sha"] == rev_fp["odb_sha"]
        and fwd_fp["def_sha"] == rev_fp["def_sha"]
        and fwd_fp["v_sha"] == rev_fp["v_sha"]
        and fwd_fp["spef_dateless_sha"] == rev_fp["spef_dateless_sha"]
    )
    print("\nOnline best 6-gate cross-order exact match (ODB/DEF/V/dateless-SPEF):", cross_order_exact)
    print("Online SEC proven/unproven:", fwd_fp["sec_receipt"]["proven"], fwd_fp["sec_receipt"]["unproven"])

    payload = {
        "raw_root": str(RAW_ROOT),
        "arms": arms,
        "forward_req3_same_actions": same_r3_actions,
        "forward_req3_comparison": req3_compare,
        "online_best_cross_order_exact": cross_order_exact,
        "online_best_fingerprints": online_best_fingerprints,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("Wrote", OUT_JSON, "sha256=", sha256(OUT_JSON))


if __name__ == "__main__":
    main()
