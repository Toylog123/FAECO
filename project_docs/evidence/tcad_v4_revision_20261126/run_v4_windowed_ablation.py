#!/usr/bin/env python3
"""V4 Stage B Experiment 1:
Same-window (1.0 x H_row boxed DRC) fair baselines & scheduling component ablation.

Part 1 — SKY130HD AES (720 RAW s, 113.363 s screen charge, CPU 0-5 exclusive):
  1. single_sens_boxed      : Sensitivity-ranked single-gate (b=1) + 1.0*H_row boxed DRC
  2. fixed_boxed            : Fixed micro-batch (b=3, no defer, no cap rerank) + 1.0*H_row boxed DRC
  3. faeco_defer_only_boxed : Adaptive micro-batch (b=3 + Hold defer ONLY, no cap rerank) + 1.0*H_row boxed DRC
  (Pairs directly with already-verified faeco_boxed_drc = 98.8448 um2, 9 gates, forward & reverse)

Part 2 — ASAP7 AES (7 nm holdout, 720 RAW s, 156.268 s screen charge, live TT sensitivity rank):
  4. fixed_boxed            : Fixed micro-batch (b=3, sensitivity rank, no defer) + 1.0*H_row boxed DRC
  (Pairs directly with already-verified single_boxed_drc = 0.30618 um2 and faeco_boxed_drc = 0.61236 um2)
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

REPO = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
EVIDENCE = REPO / "project_docs/evidence"
for sub in (
    "tcad_ibex_20261123",
    "tcad_wallclock_schedule_20261125",
    "tcad_asap7_aes_holdout_20261125",
    "tcad_boxed_drc_20261126",
):
    p = str(EVIDENCE / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

import boxed_drc
import compare_ibex as comparison
import run_aes_sensitivity_greedy as sens_aes
import run_qualified_wallclock as qualified
import run_wallclock_matrix as wmatrix
from run_aes_cold_online import ColdOnlineComparison
from run_aes_incident_priority_matched_v2 import CorrectedComparison, process_ledger
from run_aes_protected_online import OnlineProtection
from run_asap7_aes_rank_aligned import install, run_aligned_strategy
from run_screened_matrix import bind_runtime, raw_seconds

OUT_ROOT = Path("/home/toylog/faeco_v4_windowed_ablation_20261126_v1")
OUT_JSON = EVIDENCE / "tcad_v4_revision_20261126/WINDOWED_ABLATION_VERIFIED.json"

SKY_MATRIX = Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_matrix_v1")


def get_or_create_sky_preflight() -> Path:
    pf_dir = OUT_ROOT / "shared_preflight"
    pf_res = pf_dir / "preflight/result.json"
    if pf_res.is_file() and (pf_dir / "config.json").is_file():
        return pf_res
    if pf_dir.exists():
        shutil.rmtree(pf_dir)
    pf_runner = OnlineProtection(SKY_MATRIX, pf_dir)
    with bind_runtime(pf_runner.top, pf_runner.flow["fastroute.tcl"]):
        pf_runner.preflight()
    return pf_res.resolve(strict=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_anytime_auc(checkpoints: list[dict], ref_area: float, limit_s: float = 720.0) -> float:
    best = 0.0
    pts = [(0.0, 0.0)]
    for cp in sorted(checkpoints, key=lambda c: c["elapsed_seconds"]):
        t = float(cp["elapsed_seconds"])
        if t > limit_s:
            continue
        if cp.get("accepted"):
            ep = cp["endpoint"]
            saved = ref_area - float(ep["area"])
            if saved > best:
                best = saved
                pts.append((t, best))
    pts.append((limit_s, best))
    area_time = 0.0
    for (t0, v0), (t1, _) in zip(pts, pts[1:]):
        area_time += max(0.0, t1 - t0) * v0
    return area_time / limit_s


class SkyBoxedAblationRunner(ColdOnlineComparison):
    """Boxed 1.0*H_row runner supporting single_sens_boxed, fixed_boxed, and faeco_defer_only_boxed."""

    def __init__(self, matrix: Path, output: Path, mode: str):
        super().__init__(matrix, output)
        self.ablation_mode = mode

    def diagnose(self, actions, directory):
        return boxed_drc.diagnose_boxed(self, actions, directory, halo_rows=1.0)

    def run_ablation_arm(self, reference):
        self.use_preview = True
        orig_run_method = comparison.run_method
        mode = self.ablation_mode

        if mode == "single_sens_boxed":
            def dispatch(name, ref, actions, *args, **kwargs):
                ranking = sens_aes.score_control(self, actions, self.output / "single" / "sensitivity")
                by_id = {a.action_id: a for a in actions}
                ranked = [by_id[aid] for aid in ranking["ordered_action_ids"]]
                return orig_run_method("single", ref, ranked, *args, **kwargs)
            arm_name = "single"
        elif mode == "fixed_boxed":
            def dispatch(name, ref, actions, *args, **kwargs):
                return orig_run_method("fixed", ref, actions, *args, **kwargs)
            arm_name = "fixed_online"
        elif mode == "faeco_defer_only_boxed":
            def dispatch(name, ref, actions, *args, **kwargs):
                # Keep Hold deferral (defer_split_for), DISABLE incident-cap re-ranking!
                kwargs["priority_after_defer"] = None
                return orig_run_method("faeco", ref, actions, *args, **kwargs)
            arm_name = "faeco"
        else:
            raise ValueError(mode)

        try:
            comparison.run_method = dispatch
            return CorrectedComparison.arm(self, arm_name, reference)
        finally:
            comparison.run_method = orig_run_method
            self.use_preview = False


def run_sky130hd_arm(mode: str, sky_preflight: Path) -> dict:
    arm_dir = OUT_ROOT / "sky130hd_aes" / mode
    if arm_dir.exists():
        shutil.rmtree(arm_dir)
    runner = SkyBoxedAblationRunner(SKY_MATRIX, arm_dir, mode)
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        reference = runner.prepare_online(sky_preflight)
        summary = runner.run_ablation_arm(reference)

    arm_sub = {"single_sens_boxed": "single", "fixed_boxed": "fixed_online", "faeco_defer_only_boxed": "faeco"}[mode]
    prog = json.loads((arm_dir / arm_sub / "progress.json").read_text())
    cps = prog["checkpoints"]
    ref_area = runner.eval.ref_area
    auc = compute_anytime_auc(cps, ref_area, 720.0)

    # Extract best accepted checkpoint details
    best_cp = None
    best_saved = 0.0
    for cp in cps:
        if cp.get("accepted"):
            s = ref_area - cp["endpoint"]["area"]
            if s > best_saved:
                best_saved = s
                best_cp = cp

    # Read diag stats
    diag_dir = arm_dir / arm_sub / "diagnosis"
    diag_secs = []
    if diag_dir.is_dir():
        for dj in sorted(diag_dir.glob("*/diagnosis.json")):
            dd = json.loads(dj.read_text())
            diag_secs.append(dd["seconds"])

    # Read final receipt views if accepted
    best_views = {}
    best_drc = None
    best_sec = None
    best_gates = 0
    if best_cp is not None:
        # Find matching request id
        ep_id = best_cp["endpoint"]["endpoint_id"]
        for rdir in sorted((arm_dir / arm_sub).glob("[0-9][0-9]")):
            for pass_name in ("retry", "initial"):
                rp = rdir / pass_name / "receipt.json"
                if rp.is_file():
                    rec = json.loads(rp.read_text())
                    if abs(rec.get("area", -1) - best_cp["endpoint"]["area"]) < 1e-6:
                        best_views = {
                            c: {
                                "d_setup_wns_ps": rec["views"][c]["setup_wns_ps"] - runner.eval.ref_views[c]["setup_wns_ps"],
                                "d_hold_wns_ps": rec["views"][c]["hold_wns_ps"] - runner.eval.ref_views[c]["hold_wns_ps"],
                            }
                            for c in ("FF", "TT", "SS")
                            if c in rec.get("views", {})
                        }
                        ud = rdir / pass_name / "unlocked_drc/audit.json"
                        if ud.is_file():
                            best_drc = json.loads(ud.read_text()).get("drc_markers")
                        break
        # Count gates from logical_requests matching area
        for req in prog["logical_requests"]:
            if req.get("failures") == []:
                best_gates = max(best_gates, len(req["actions"]))
        best_sec = bool(best_cp["endpoint"].get("sec_pass"))

    max_setup_loss = max((max(0.0, -v["d_setup_wns_ps"]) for v in best_views.values()), default=0.0)
    return {
        "design": "sky130hd_aes",
        "mode": mode,
        "diagnosis": "boxed_1.0_Hrow",
        "base_area_um2": ref_area,
        "pool_ceiling_um2": sum(a.estimated_area_saving for a in runner.pool),
        "qualified_area_saved_um2": best_saved,
        "qualified_gates": best_gates,
        "area_saved_pct": 100.0 * best_saved / ref_area,
        "pool_capture_pct": 100.0 * best_saved / sum(a.estimated_area_saving for a in runner.pool),
        "anytime_auc_um2": auc,
        "max_setup_loss_ps": max_setup_loss,
        "setup_budget_util_pct": 100.0 * max_setup_loss / runner.gate.wns_ps if runner.gate.wns_ps else 0.0,
        "first_target_s": summary["window"]["time_to_target_seconds"],
        "logical_finished": summary["logical_finished"],
        "logical_admitted": summary["logical_admitted"],
        "diag_calls": len(diag_secs),
        "diag_mean_s": (sum(diag_secs) / len(diag_secs)) if diag_secs else None,
        "first_relative_hold_defer": prog.get("first_relative_hold_defer"),
        "unlocked_drc_markers": best_drc,
        "sec_pass": best_sec,
        "views_delta_ps": best_views,
        "checkpoints": [
            {
                "elapsed_s": cp["elapsed_seconds"],
                "accepted": cp["accepted"],
                "area_saved_um2": ref_area - cp["endpoint"]["area"],
            }
            for cp in cps
        ],
        "run_dir": str(arm_dir),
    }


def run_asap7_aes_fixed_boxed() -> dict:
    """Run fixed_online + 1.0*H_row boxed DRC + live TT sensitivity rank on 7nm asap7/aes."""
    proto_path = Path("/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/matrix_boxed_drc_20261126_v1/protocol.json")
    proto = json.loads(proto_path.read_text())
    seed_path = Path(proto["seed"]["path"])
    seed = json.loads(seed_path.read_text())
    pdk, top = proto["pdk"], proto["top"]
    orfs = Path(seed["bindings"]["flow"]["setRC.tcl"]["path"]).parents[2]
    run_dir = OUT_ROOT / "asap7_aes" / "fixed_boxed"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    args = SimpleNamespace(
        pdk=pdk, top=top, out=run_dir, threads=proto["route_threads"],
        clock_period_ps=proto["period_basis"]["period_ps"],
        openroad=Path(seed["bindings"]["tools"]["openroad"]["path"]),
        sta=Path(seed["bindings"]["tools"]["opensta"]["path"]),
        sec=Path(seed["bindings"]["tools"]["sec"]["path"]),
        orfs=orfs, route_mode="local", droute_iters=seed["route_drt_iters"],
        embedded_guides=True, route_guide=None, zero_reextract=False,
        single_pin_access=True, route_timeout=240.0,
        sta_timeout=seed["sta_timeout_seconds_per_view"],
        sec_timeout=seed["sec_timeout_seconds"],
        report_setup_endpoints=True, batch_size=3, max_evals=1, helper_source=[],
        screen_pool=Path(proto["screen_input"]["pool"]["path"]),
        screen_receipt=Path(proto["screen_input"]["receipt"]["path"]),
    )

    class Asap7FixedBoxed(qualified.QualifiedWallclockComparison):
        def diagnose(self, actions, directory):
            return boxed_drc.diagnose_boxed(self, actions, directory, halo_rows=1.0)

    expected_box = {"order": None}
    with (
        bind_runtime(top, Path(seed["bindings"]["flow"]["fastroute.tcl"]["path"])),
        qualified.qualified_ranking(),
        qualified.qualified_process_clock(),
    ):
        runner = Asap7FixedBoxed(args, seed_path.parent, run_dir, proto["screen_input"], proto["charged_screening_seconds_per_arm"])
        ref = runner.qualify_zero()
        arm_out = run_dir / "cell_01"
        arm_out.mkdir(parents=True)
        runner.output = arm_out
        summary_ret = run_aligned_strategy(runner, "fixed_online", ref, expected_box, wmatrix.run_strategy)
        summary = summary_ret[0] if isinstance(summary_ret, tuple) else summary_ret

    prog = json.loads((arm_out / "fixed" / "progress.json").read_text())
    cps = prog["checkpoints"]
    ref_area = runner.eval.ref_area
    auc = compute_anytime_auc(cps, ref_area, 720.0)
    best_saved = max((ref_area - cp["endpoint"]["area"] for cp in cps if cp.get("accepted")), default=0.0)
    best_gates = max((len(req["actions"]) for req in prog["logical_requests"] if req.get("failures") == []), default=0)
    diag_secs = [json.loads(dj.read_text())["seconds"] for dj in sorted((arm_out / "fixed" / "diagnosis").glob("*/diagnosis.json"))]

    return {
        "design": "asap7_aes",
        "mode": "fixed_boxed",
        "diagnosis": "boxed_1.0_Hrow",
        "base_area_um2": ref_area,
        "pool_ceiling_um2": sum(a.estimated_area_saving for a in runner.pool),
        "qualified_area_saved_um2": best_saved,
        "qualified_gates": best_gates,
        "area_saved_pct": 100.0 * best_saved / ref_area,
        "pool_capture_pct": 100.0 * best_saved / sum(a.estimated_area_saving for a in runner.pool),
        "anytime_auc_um2": auc,
        "first_target_s": summary["window"]["time_to_target_seconds"],
        "logical_finished": summary["logical_finished"],
        "logical_admitted": summary["logical_admitted"],
        "diag_calls": len(diag_secs),
        "diag_mean_s": (sum(diag_secs) / len(diag_secs)) if diag_secs else None,
        "checkpoints": [
            {
                "elapsed_s": cp["elapsed_seconds"],
                "accepted": cp["accepted"],
                "area_saved_um2": ref_area - cp["endpoint"]["area"],
            }
            for cp in cps
        ],
        "run_dir": str(run_dir),
    }


def main() -> int:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    results = json.loads(OUT_JSON.read_text()) if OUT_JSON.is_file() else {"arms": {}}

    sky_preflight = get_or_create_sky_preflight()
    for mode in ("single_sens_boxed", "fixed_boxed", "faeco_defer_only_boxed"):
        key = f"sky130hd_aes::{mode}"
        if key in results["arms"] and "--force" not in sys.argv:
            print(f"Skipping existing {key}", flush=True)
            continue
        print(f"\n=== Running {key} ===", flush=True)
        row = run_sky130hd_arm(mode, sky_preflight)
        results["arms"][key] = row
        OUT_JSON.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        print(
            f"DONE {key}: saved={row['qualified_area_saved_um2']:.4f} um2 ({row['qualified_gates']} gates), "
            f"AUC={row['anytime_auc_um2']:.3f}, finished={row['logical_finished']}/{row['logical_admitted']}",
            flush=True,
        )

    key_a7 = "asap7_aes::fixed_boxed"
    if key_a7 not in results["arms"] or "--force" in sys.argv:
        print(f"\n=== Running {key_a7} ===", flush=True)
        row_a7 = run_asap7_aes_fixed_boxed()
        results["arms"][key_a7] = row_a7
        OUT_JSON.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        print(
            f"DONE {key_a7}: saved={row_a7['qualified_area_saved_um2']:.6f} um2 ({row_a7['qualified_gates']} gates), "
            f"AUC={row_a7['anytime_auc_um2']:.4f}, finished={row_a7['logical_finished']}/{row_a7['logical_admitted']}",
            flush=True,
        )

    print("Wrote:", OUT_JSON, "sha256=", sha256(OUT_JSON), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
