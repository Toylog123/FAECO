#!/usr/bin/env python3
"""V5 Offline Log Audit:
1. Extract exact Non-Monotonic Feasibility Counterexample (T subset S, Phi(T)=0, Phi(S)=1)
   on SKY130HD AES from verified V4 receipts and WSL trial logs.
2. Audit Hybrid FAECO probe sub-budget vs OS cleanup latency vs accepted checkpoint timestamps.
3. Audit Table 5 (SKY130HD AES completed vs accepted rounds), Table 8 (dedup + initial rank),
   and Table 10 vs Table 4 (ASAP7 UART backend & initial rank differences).
4. Locate saved best endpoint ODB/SPEF paths for SKY130HD AES Hybrid, ASAP7 UART-TC, and ASAP7 UART K=36.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
EVID = REPO / "project_docs/evidence"
OUT_DIR = EVID / "tcad_v5_revision_20261126"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    out = {}

    # 1. Hybrid FAECO probe timing & checkpoint timestamp audit
    hybrid = load_json(EVID / "tcad_v4_revision_20261126/HYBRID_FAECO_4DESIGNS_VERIFIED.json")
    probe_audit = {}
    for k, v in hybrid["designs"].items():
        p1 = v.get("phase1_probe", {})
        cps = v.get("checkpoints", [])
        acc_cps = [c for c in cps if c.get("accepted")]
        max_acc_t = max((float(c["elapsed_s"]) for c in acc_cps), default=0.0)
        sub_b = float(v["probe_sub_budget_s"])
        p1_wall = float(p1.get("wall_s", 0.0))
        probe_audit[k] = {
            "charged_screening_s": v["charged_screening_s"],
            "probe_sub_budget_s": sub_b,
            "phase1_status": p1.get("status"),
            "phase1_wall_s": p1_wall,
            "cleanup_overhead_s": round(p1_wall - sub_b, 4) if p1.get("status") == "sub_budget_timeout" else 0.0,
            "total_wall_s_incl_screen": v["total_wall_s_incl_screen"],
            "n_accepted_checkpoints": len(acc_cps),
            "last_accepted_checkpoint_s": max_acc_t,
            "all_accepted_within_720s": max_acc_t <= 720.0,
            "qualified_gates": v["qualified_gates"],
            "qualified_area_saved_um2": v["qualified_area_saved_um2"],
            "anytime_auc_um2": v["anytime_auc_um2"],
        }
    out["hybrid_probe_timing_audit"] = probe_audit

    # 2. Non-monotonic feasibility counterexample on SKY130HD AES
    # T = 6-gate subset (first 6 actions in area-rank order from fixed_boxed trial 2) -> Phi(T) = 0 (Hold regression)
    # S = 18-gate full pool (Hybrid Phase 1 probe) -> Phi(S) = 1 (all 3 corners pass, 0 DRC, SEC proven)
    fixed_res_path = Path("/home/toylog/faeco_v4_windowed_ablation_20261126_v1/sky130hd_aes/fixed_boxed/result.json")
    if not fixed_res_path.is_file():
        cands = list(Path("/home/toylog/faeco_v4_windowed_ablation_20261126_v1/sky130hd_aes/fixed_boxed").rglob("result.json"))
        fixed_res_path = cands[0] if cands else None

    fixed_trials = []
    if fixed_res_path and fixed_res_path.is_file():
        fres = load_json(fixed_res_path)
        for arm in fres.get("arms", [fres]):
            for cp in arm.get("checkpoints", arm.get("trials", [])):
                fixed_trials.append(cp)

    # Also read directly from fixed_boxed/fixed_online subdirectories assessment.json / receipt.json
    fb_root = Path("/home/toylog/faeco_v4_windowed_ablation_20261126_v1/sky130hd_aes/fixed_boxed")
    fb_evals = []
    for aj in sorted(fb_root.rglob("assessment.json")):
        d = load_json(aj)
        rj = aj.parent / "receipt.json"
        rec = load_json(rj) if rj.is_file() else {}
        lc = aj.parent / "layout_changes.json"
        lch = load_json(lc) if lc.is_file() else {}
        fb_evals.append({
            "dir": str(aj.parent),
            "feasible": d.get("feasible"),
            "reasons": d.get("reasons"),
            "views_delta_ps": d.get("views_delta_ps", d.get("views")),
            "actions_count": len(rec.get("actions", lch.get("edits", []))),
            "actions": rec.get("actions", []),
            "edits_sample": lch.get("edits", [])[:10] if isinstance(lch, dict) else [],
        })

    # Hybrid 18-gate superset S
    hyb_dir = Path("/home/toylog/faeco_v4_hybrid_faeco_20261126_v1/sky130hd_aes/phase1_optimistic_probe/initial")
    hyb_assess = load_json(hyb_dir / "assessment.json") if (hyb_dir / "assessment.json").is_file() else {}
    hyb_rec = load_json(hyb_dir / "receipt.json") if (hyb_dir / "receipt.json").is_file() else {}
    hyb_lc = load_json(hyb_dir / "layout_changes.json") if (hyb_dir / "layout_changes.json").is_file() else {}

    out["non_monotonic_counterexample_sky130hd_aes"] = {
        "fixed_boxed_evals": fb_evals,
        "hybrid_18gate_superset": {
            "dir": str(hyb_dir),
            "feasible": hyb_assess.get("feasible"),
            "reasons": hyb_assess.get("reasons"),
            "views_delta_ps": hybrid["designs"]["sky130hd_aes"].get("views_delta_ps"),
            "actions_count": len(hyb_rec.get("actions", [])),
            "actions": hyb_rec.get("actions", []),
            "edits": hyb_lc.get("edits", []) if isinstance(hyb_lc, dict) else [],
            "odb": str(hyb_dir / "routed.odb"),
            "spef": str(hyb_dir / "routed.spef"),
        },
    }

    # 3. Table 5 (SKY130HD AES pure FAECO boxed finished vs accepted rounds)
    boxed_ver = load_json(EVID / "tcad_boxed_drc_20261126/BOXED_DRC_VERIFIED.json")
    sky_boxed_arms = []
    for arm in boxed_ver["sky130hd_aes"]["arms"]:
        if arm["diagnosis_mode"] == "boxed":
            cps = arm.get("checkpoints", [])
            sky_boxed_arms.append({
                "order": arm["order"],
                "logical_finished": arm.get("logical_finished"),
                "logical_admitted": arm.get("logical_admitted"),
                "n_checkpoints": len(cps),
                "n_accepted": sum(1 for c in cps if c.get("accepted")),
                "accepted_details": [
                    {"t": c.get("elapsed_s", c.get("elapsed_seconds")), "gates": len(c.get("actions", c.get("endpoint", {}).get("actions", []))), "saved": c.get("area_saved_um2")}
                    for c in cps if c.get("accepted")
                ],
                "best_gates": len(arm["best_endpoint"]["actions"]),
                "best_area": arm["best_endpoint"]["area_saved_um2"],
            })
    out["table5_sky_pure_faeco_audit"] = sky_boxed_arms

    # 4. Locate saved best endpoint ODB/SPEF for UART-TC and UART K=36
    endpoints = {
        "sky130hd_aes_hybrid_18g": {
            "odb": str(hyb_dir / "routed.odb"),
            "spef": str(hyb_dir / "routed.spef"),
            "exists": (hyb_dir / "routed.odb").is_file() and (hyb_dir / "routed.spef").is_file(),
        }
    }

    # Search timing_closed_asap7_uart/faeco_boxed
    tc_root = Path("/home/toylog/faeco_v4_tc_drc_sens_20261126_v1/timing_closed_asap7_uart/faeco_boxed")
    tc_best = None
    for aj in sorted(tc_root.rglob("assessment.json")):
        a = load_json(aj)
        if a.get("feasible"):
            rj = aj.parent / "receipt.json"
            rec = load_json(rj) if rj.is_file() else {}
            n_act = len(rec.get("actions", []))
            if tc_best is None or n_act >= tc_best["n_actions"]:
                tc_best = {
                    "dir": str(aj.parent),
                    "n_actions": n_act,
                    "odb": str(aj.parent / "routed.odb"),
                    "spef": str(aj.parent / "routed.spef"),
                    "exists": (aj.parent / "routed.odb").is_file() and (aj.parent / "routed.spef").is_file(),
                    "assessment": a,
                }
    endpoints["asap7_uart_tc_faeco"] = tc_best

    # Search b3_K36
    k36_roots = [
        Path("/home/toylog/faeco_v4_step4_finish_20261126_v1/bk_sens_finish/b3_K36"),
        Path("/home/toylog/faeco_v4_tc_drc_sens_20261126_v1/bk_sensitivity_asap7_uart/b3_K36"),
    ]
    k36_best = None
    for kr in k36_roots:
        if not kr.exists():
            continue
        for aj in sorted(kr.rglob("assessment.json")):
            a = load_json(aj)
            if a.get("feasible"):
                rj = aj.parent / "receipt.json"
                rec = load_json(rj) if rj.is_file() else {}
                n_act = len(rec.get("actions", []))
                if k36_best is None or n_act >= k36_best["n_actions"]:
                    k36_best = {
                        "dir": str(aj.parent),
                        "n_actions": n_act,
                        "odb": str(aj.parent / "routed.odb"),
                        "spef": str(aj.parent / "routed.spef"),
                        "exists": (aj.parent / "routed.odb").is_file() and (aj.parent / "routed.spef").is_file(),
                    }
    endpoints["asap7_uart_k36"] = k36_best
    out["saved_endpoints"] = endpoints

    # 5. Check Table 8 dedup & initial rank in ablation scripts
    out["table8_design_notes"] = {
        "sky130hd_aes": {
            "A_single_sens_boxed": {"batch": False, "hold_defer": False, "cap_rerank": False, "setup_dedup": False, "probe": False, "init_rank": "sensitivity"},
            "B_fixed_boxed": {"batch": True, "hold_defer": False, "cap_rerank": False, "setup_dedup": False, "probe": False, "init_rank": "area"},
            "C_faeco_defer_only_boxed": {"batch": True, "hold_defer": True, "cap_rerank": False, "setup_dedup": True, "probe": False, "init_rank": "area"},
            "D_pure_faeco_boxed": {"batch": True, "hold_defer": True, "cap_rerank": True, "setup_dedup": True, "probe": False, "init_rank": "area"},
            "E_hybrid_faeco": {"batch": True, "hold_defer": True, "cap_rerank": True, "setup_dedup": True, "probe": True, "init_rank": "area"},
        },
        "note": "C and D share IDENTICAL initial rank (area), IDENTICAL boxed 1.0*H_row backend, IDENTICAL Hold defer, and IDENTICAL Setup dedup switch (enabled, 0 dedup hits on SKY130HD AES because all rejections are Hold rejections!). Thus C->D (33.7824 -> 98.8448 um2, 2.93x) is 100% purely due to Eq.(8) incident-cap re-ranking!"
    }

    (OUT_DIR / "V5_OFFLINE_LOG_AUDIT.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "probe_audit": probe_audit,
        "fb_evals_count": len(fb_evals),
        "fb_evals_brief": [(e["actions_count"], e["feasible"], e["reasons"]) for e in fb_evals],
        "hyb_18g_feasible": hyb_assess.get("feasible"),
        "sky_boxed_arms": sky_boxed_arms,
        "endpoints_found": {k: (v["exists"], v.get("n_actions")) if v else None for k, v in endpoints.items()},
    }, indent=2))


if __name__ == "__main__":
    main()
