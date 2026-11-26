#!/usr/bin/env python3
"""Independent forensic verifier for paired local-windowed (1.0*H_row) boxed-DRC comparisons
on 7nm ASAP7 AES (6 arms) and 130nm SKY130HD AES (4 arms)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ASAP7_ROOT = Path("/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/matrix_boxed_drc_20261126_v1")
SKY_ROOT = Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_boxed_drc_20261126_v1")
OUT_JSON = Path(__file__).resolve().parent / "BOXED_DRC_VERIFIED.json"


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


def verify_asap7() -> dict:
    proto = load_json(ASAP7_ROOT / "protocol.json")
    ref_views = load_json(Path(proto["reference"]["path"]))["views"]
    zero_res = load_json(ASAP7_ROOT / "preflight/zero/result.json")
    base_area = zero_res["endpoint"]["area"]
    screen_s = proto["charged_screening_seconds_per_arm"]

    arms = []
    best_by_strat = {}
    diag_by_strat = {}

    for cell_idx in range(1, 7):
        cdir = ASAP7_ROOT / f"cell_{cell_idx:02d}"
        arm = load_json(cdir / "arm.json")
        strat = arm["strategy"]
        direction = arm["direction"]
        method_folder = "single" if strat.startswith("single_") else "faeco"
        mdir = cdir / method_folder
        prog = load_json(mdir / "progress.json")
        res = arm["result"]
        win = res["window"]

        best_cp_idx = None
        best_area = base_area
        t_0p20412 = None
        t_0p61236 = None
        checkpoints_clean = []
        for idx, cp in enumerate(prog["checkpoints"], 1):
            saved = base_area - cp["endpoint"]["area"]
            checkpoints_clean.append({
                "seq": idx,
                "elapsed_s": cp["elapsed_seconds"],
                "accepted": cp["accepted"],
                "area_saved_um2": saved,
            })
            if cp["accepted"]:
                if saved >= 0.20412 - 1e-6 and t_0p20412 is None:
                    t_0p20412 = cp["elapsed_seconds"]
                if saved >= 0.61236 - 1e-6 and t_0p61236 is None:
                    t_0p61236 = cp["elapsed_seconds"]
                if cp["endpoint"]["area"] < best_area:
                    best_area = cp["endpoint"]["area"]
                    best_cp_idx = idx

        diag_rows = []
        for dp in sorted((mdir / "diagnosis").glob("*/diagnosis.json")):
            dj = load_json(dp)
            diag_rows.append({
                "seq": dp.parent.name,
                "mode": dj.get("diagnosis_mode", "full"),
                "seconds": dj["seconds"],
                "marker_count": dj.get("marker_count"),
                "released_count": len(dj.get("released_neighbors", [])),
                "box_meta": dj.get("box_meta"),
                "status": dj.get("status"),
            })
        diag_by_strat.setdefault(strat, []).extend(diag_rows)

        best_rec = load_json(mdir / f"{best_cp_idx:02d}/result.json")
        final_pass = best_rec["passes"][-1]
        phys = load_json(mdir / f"{best_cp_idx:02d}/{final_pass}/receipt.json")
        unlocked = load_json(mdir / f"{best_cp_idx:02d}/{final_pass}/unlocked_drc/audit.json")
        sec_rec = load_json(mdir / f"{best_cp_idx:02d}/{final_pass}/sec/receipt.json")
        assert unlocked["drc_markers"] == 0, f"non-zero unlocked DRC in asap7 {strat}"
        assert sec_rec["passed"] and sec_rec["unproven"] == 0, f"SEC failed in asap7 {strat}"

        fp = {
            "actions": best_rec["actions"],
            "num_gates": len(best_rec["actions"]),
            "area": best_rec["endpoint"]["area"],
            "area_saved_um2": base_area - best_rec["endpoint"]["area"],
            "area_saved_pct": 100.0 * (base_area - best_rec["endpoint"]["area"]) / base_area,
            "odb_path": phys["artifacts"]["odb"]["path"],
            "spef_path": phys["artifacts"]["spef"]["path"],
            "odb_sha": sha256(Path(phys["artifacts"]["odb"]["path"])),
            "def_sha": sha256(Path(phys["artifacts"]["def"]["path"])),
            "v_sha": sha256(Path(phys["artifacts"]["v"]["path"])),
            "spef_dateless_sha": spef_dateless_sha(Path(phys["artifacts"]["spef"]["path"])),
            "unlocked_drc_markers": unlocked["drc_markers"],
            "sec_proven": sec_rec["proven"],
            "sec_unproven": sec_rec["unproven"],
            "views_delta_ps": {
                c: {
                    "d_setup_wns_ps": phys["views"][c]["setup_wns_ps"] - ref_views[c]["setup_wns_ps"],
                    "d_setup_tns_ps": phys["views"][c]["setup_tns_ps"] - ref_views[c]["setup_tns_ps"],
                    "d_hold_wns_ps": phys["views"][c]["hold_wns_ps"] - ref_views[c]["hold_wns_ps"],
                    "abs_hold_wns_ps": phys["views"][c]["hold_wns_ps"],
                }
                for c in ("FF", "TT", "SS")
            },
        }
        best_by_strat.setdefault(strat, {})[direction] = fp

        mean_diag_s = sum(d["seconds"] for d in diag_rows) / len(diag_rows) if diag_rows else 0.0
        total_diag_s = sum(d["seconds"] for d in diag_rows)
        row = {
            "cell": cell_idx,
            "direction": direction,
            "strategy": strat,
            "logical_finished": res["logical_finished"],
            "logical_admitted": res["logical_admitted"],
            "area_saved_um2": win["area_saved"],
            "area_saved_pct": 100.0 * win["area_saved"] / base_area,
            "first_0p01pct_s": win["time_to_target_seconds"],
            "t_0p20412_s": t_0p20412,
            "t_0p61236_s": t_0p61236,
            "diag_calls": len(diag_rows),
            "diag_total_s": total_diag_s,
            "diag_mean_s": mean_diag_s,
            "diag_rows": diag_rows,
            "checkpoints": checkpoints_clean,
            "stage_costs": arm["stage_costs"],
            "best_endpoint": fp,
        }
        arms.append(row)
        print(
            f"[ASAP7] cell_{cell_idx:02d} {direction:7s} {strat:17s} | fin={row['logical_finished']}/{row['logical_admitted']} | "
            f"area={row['area_saved_um2']:.6f} ({fp['num_gates']}g, {row['area_saved_pct']:.4f}%) | "
            f"t_0.01%={row['first_0p01pct_s']:.2f}s | t_0.612={str(round(t_0p61236,2)) if t_0p61236 else 'None':>6s} | "
            f"diag={len(diag_rows)}x mean={mean_diag_s:.2f}s tot={total_diag_s:.2f}s | SEC={fp['sec_proven']}/{fp['sec_unproven']}",
            flush=True,
        )

    cross_order_exact = {}
    for strat, by_dir in best_by_strat.items():
        f, r = by_dir["forward"], by_dir["reverse"]
        cross_order_exact[strat] = (
            f["actions"] == r["actions"]
            and f["odb_sha"] == r["odb_sha"]
            and f["def_sha"] == r["def_sha"]
            and f["v_sha"] == r["v_sha"]
            and f["spef_dateless_sha"] == r["spef_dateless_sha"]
        )
    print("[ASAP7] Cross-order exact match:", cross_order_exact, flush=True)
    return {
        "raw_root": str(ASAP7_ROOT),
        "base_area_um2": base_area,
        "charged_screening_s": screen_s,
        "arms": arms,
        "cross_order_exact": cross_order_exact,
    }


def verify_sky130hd() -> dict:
    results = load_json(SKY_ROOT / "results.json")
    assert len(results) == 4, f"expected 4 sky130hd arms, got {len(results)}"
    arms = []
    best_by_mode = {}
    diag_neighbors_by_mode = {}

    for entry in results:
        order = entry["order"]
        cell = entry["cell"]
        mode = entry["diagnosis_mode"]
        method = entry["method"]
        cdir = SKY_ROOT / order / cell
        mdir = cdir / method
        summary = load_json(mdir / "summary.json")
        prog = load_json(mdir / "progress.json")
        cfg = load_json(cdir / "config.json")
        ref_views = load_json(Path(cfg["control_sta"]["path"]))["views"]
        zero_area = load_json(cdir / "transferred_preflight.json")["strict_zero"]["endpoint"]["area"]

        best_cp_idx = None
        best_area = zero_area
        t_67 = None
        t_98 = None
        checkpoints_clean = []
        for idx, cp in enumerate(prog["checkpoints"], 1):
            saved = zero_area - cp["endpoint"]["area"]
            checkpoints_clean.append({
                "seq": idx,
                "elapsed_s": cp["elapsed_seconds"],
                "accepted": cp["accepted"],
                "area_saved_um2": saved,
            })
            if cp["accepted"]:
                if saved >= 67.5 - 1e-3 and t_67 is None:
                    t_67 = cp["elapsed_seconds"]
                if saved >= 98.8 - 1e-3 and t_98 is None:
                    t_98 = cp["elapsed_seconds"]
                if cp["endpoint"]["area"] < best_area:
                    best_area = cp["endpoint"]["area"]
                    best_cp_idx = idx

        diag_rows = []
        nbr_map = {}
        retries = 0
        for seq in range(1, summary["logical_admitted"] + 1):
            dp = mdir / f"diagnosis/{seq:02d}/diagnosis.json"
            if dp.is_file():
                dj = load_json(dp)
                diag_rows.append({
                    "seq": f"{seq:02d}",
                    "mode": dj.get("diagnosis_mode", "full"),
                    "seconds": dj["seconds"],
                    "marker_count": dj.get("marker_count"),
                    "raw_marker_count": dj.get("raw_marker_count"),
                    "released_neighbors": dj.get("released_neighbors", []),
                    "box_meta": dj.get("box_meta"),
                    "actions": dj.get("actions", []),
                })
                nbr_map[tuple(dj["actions"])] = {
                    "marker_count": dj.get("marker_count"),
                    "released_neighbors": dj.get("released_neighbors", []),
                }
            rf = mdir / f"{seq:02d}/result.json"
            if rf.is_file():
                rec = load_json(rf)
                if "retry" in rec["passes"]:
                    retries += 1
        diag_neighbors_by_mode.setdefault(mode, []).append(nbr_map)

        best_rec = load_json(mdir / f"{best_cp_idx:02d}/result.json")
        final_pass = best_rec["passes"][-1]
        phys = load_json(mdir / f"{best_cp_idx:02d}/{final_pass}/receipt.json")
        unlocked = load_json(mdir / f"{best_cp_idx:02d}/{final_pass}/unlocked_drc/audit.json")
        sec_rec = load_json(mdir / f"{best_cp_idx:02d}/{final_pass}/sec/receipt.json")
        assert unlocked["drc_markers"] == 0, f"non-zero unlocked DRC in sky {mode}"
        assert sec_rec["passed"] and sec_rec["unproven"] == 0, f"SEC failed in sky {mode}"

        fp = {
            "actions": best_rec["actions"],
            "num_gates": len(best_rec["actions"]),
            "area": best_rec["endpoint"]["area"],
            "area_saved_um2": zero_area - best_rec["endpoint"]["area"],
            "area_saved_pct": 100.0 * (zero_area - best_rec["endpoint"]["area"]) / zero_area,
            "odb_path": phys["artifacts"]["odb"]["path"],
            "spef_path": phys["artifacts"]["spef"]["path"],
            "odb_sha": sha256(Path(phys["artifacts"]["odb"]["path"])),
            "def_sha": sha256(Path(phys["artifacts"]["def"]["path"])),
            "v_sha": sha256(Path(phys["artifacts"]["v"]["path"])),
            "spef_dateless_sha": spef_dateless_sha(Path(phys["artifacts"]["spef"]["path"])),
            "unlocked_drc_markers": unlocked["drc_markers"],
            "sec_proven": sec_rec["proven"],
            "sec_unproven": sec_rec["unproven"],
            "views_delta_ps": {
                c: {
                    "d_setup_wns_ps": phys["views"][c]["setup_wns_ps"] - ref_views[c]["setup_wns_ps"],
                    "d_setup_tns_ps": phys["views"][c]["setup_tns_ps"] - ref_views[c]["setup_tns_ps"],
                    "d_hold_wns_ps": phys["views"][c]["hold_wns_ps"] - ref_views[c]["hold_wns_ps"],
                    "abs_hold_wns_ps": phys["views"][c]["hold_wns_ps"],
                }
                for c in ("FF", "TT", "SS")
            },
        }
        best_by_mode.setdefault(mode, {})[order] = fp

        mean_diag_s = sum(d["seconds"] for d in diag_rows) / len(diag_rows) if diag_rows else 0.0
        total_diag_s = sum(d["seconds"] for d in diag_rows)
        row = {
            "order": order,
            "cell": cell,
            "diagnosis_mode": mode,
            "stop_reason": summary["stop_reason"],
            "logical_finished": summary["logical_finished"],
            "logical_admitted": summary["logical_admitted"],
            "first_0p01pct_s": summary["window"]["time_to_target_seconds"],
            "t_67p56_s": t_67,
            "t_98p84_s": t_98,
            "area_saved_um2": summary["window"]["area_saved"],
            "area_saved_pct": 100.0 * summary["window"]["area_saved"] / zero_area,
            "completed_retries": retries,
            "route_tools": summary["route_tools"],
            "sec_tools": summary["sec_tools"],
            "diag_calls": len(diag_rows),
            "diag_total_s": total_diag_s,
            "diag_mean_s": mean_diag_s,
            "diag_rows": diag_rows,
            "checkpoints": checkpoints_clean,
            "best_endpoint": fp,
        }
        arms.append(row)
        print(
            f"[SKY130] {order:7s} {cell:16s} | fin={row['logical_finished']}/{row['logical_admitted']} | "
            f"area={row['area_saved_um2']:8.4f} ({fp['num_gates']}g, {row['area_saved_pct']:.4f}%) | "
            f"t_0.01%={row['first_0p01pct_s']:.2f}s | t_67.56={str(round(t_67,2)) if t_67 else 'None':>6s} | "
            f"t_98.84={str(round(t_98,2)) if t_98 else 'None':>6s} | "
            f"diag={len(diag_rows)}x mean={mean_diag_s:.2f}s tot={total_diag_s:.2f}s retries={retries} | SEC={fp['sec_proven']}/{fp['sec_unproven']}",
            flush=True,
        )

    # Check exact neighbor/marker equivalence between full and boxed on all shared requests
    full_map = diag_neighbors_by_mode["full"][0]
    boxed_map = diag_neighbors_by_mode["boxed"][0]
    shared_keys = sorted(set(full_map) & set(boxed_map))
    exact_shared_diag = all(full_map[k] == boxed_map[k] for k in shared_keys)

    cross_order_exact = {}
    for mode, by_dir in best_by_mode.items():
        f, r = by_dir["forward"], by_dir["reverse"]
        cross_order_exact[mode] = (
            f["actions"] == r["actions"]
            and f["odb_sha"] == r["odb_sha"]
            and f["def_sha"] == r["def_sha"]
            and f["v_sha"] == r["v_sha"]
            and f["spef_dateless_sha"] == r["spef_dateless_sha"]
        )
    print(f"[SKY130] Shared requests full==boxed exact marker+neighbor match ({len(shared_keys)} reqs):", exact_shared_diag, flush=True)
    print("[SKY130] Cross-order exact match:", cross_order_exact, flush=True)
    return {
        "raw_root": str(SKY_ROOT),
        "arms": arms,
        "shared_requests_checked": len(shared_keys),
        "full_vs_boxed_exact_diag_match": exact_shared_diag,
        "cross_order_exact": cross_order_exact,
    }


def main() -> int:
    payload = {
        "asap7_aes": verify_asap7(),
        "sky130hd_aes": verify_sky130hd(),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("Wrote", OUT_JSON, "sha256=", sha256(OUT_JSON), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
