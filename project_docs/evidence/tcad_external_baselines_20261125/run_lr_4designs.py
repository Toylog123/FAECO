#!/usr/bin/env python3
"""Run classical 5-iteration frozen-SPEF Lagrangian Relaxation (LR, Chen/Chu TCAD'99 & Flach TCAD'14 paradigm)
on all 4 TCAD large designs (sky130hd/aes, sky130hd/riscv32i, asap7/uart, asap7/aes), using the EXACT same
18-action frozen pool, 1% clock setup budget, protected local routing + 1.0*H_row boxed pre-DRT DRC,
FF/TT/SS multi-corner STA, independent whole-block DRC, antenna, and Yosys SEC signoff gate."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

REPO = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
EVIDENCE = REPO / "project_docs/evidence"
for sub in (
    "tcad_ibex_20261123",
    "tcad_holdout_20261123",
    "tcad_wallclock_schedule_20261125",
    "tcad_boxed_drc_20261126",
):
    p = str(EVIDENCE / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

import boxed_drc
import compare_ibex as cmp
from run_aes_cold_online import ColdOnlineComparison
from run_aes_protected_online import process_ledger
from run_qualified_wallclock import QualifiedWallclockComparison
from run_screened_matrix import bind_runtime, raw_seconds
from run_uart_online import UartComparison
from run_uart_rejection_dedup import seed_args

OUT_ROOT = Path("/home/toylog/faeco_tcad_lr_4designs_20261126_v1")
OUT_JSON = EVIDENCE / "tcad_external_baselines_20261125/LR_4DESIGNS_VERIFIED.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def run_lr_solve(runner, pdk: str, budget_ps: float, ref_tt_wns_ps: float, out_dir: Path) -> dict:
    """Run 5-iteration subgradient Lagrangian Relaxation on frozen TT SPEF over runner.pool."""
    out_dir.mkdir(parents=True, exist_ok=True)
    tt_libs = runner.eval.libraries["TT"]
    ctrl = runner.eval.control
    setrc = runner.flow["setRC.tcl"]

    # Build Tcl candidate tuples: {action_id odb_inst src tgt area_saving}
    cand_lines = []
    for a in runner.pool:
        inst_odb = cmp.canonical_odb_name(a.instance)
        cand_lines.append(
            f"  {{{{{a.action_id}}} {{{inst_odb}}} {{{a.source_cell}}} {{{a.target_cell}}} {a.estimated_area_saving:.6f}}}"
        )
    cand_block = "\n".join(cand_lines)

    lr_tcl = out_dir / "lr_solve.tcl"
    lr_log = out_dir / "lr_solve.log"
    lines = [f"read_liberty {cmp.tcl(lib)}" for lib in tt_libs]
    lines += [
        f"read_db {cmp.tcl(ctrl['odb'])}",
        f"read_sdc {cmp.tcl(ctrl['sdc'])}",
        f"source {cmp.tcl(setrc)}",
        f"read_spef {cmp.tcl(ctrl['spef'])}",
        "set blk [ord::get_db_block]",
        "set db [ord::get_db]",
        "set base_wns_raw [sta::worst_slack_cmd max]",
        "set base_hold_raw [sta::worst_slack_cmd min]",
        'puts "LR_BASE_RAW wns=$base_wns_raw hold=$base_hold_raw"',
        # OpenSTA Tcl worst_slack_cmd returns SI seconds (e.g. 1e-12 = 1 ps); verify explicitly vs ref_tt_wns_ps
        "set scale_ps 1.0e12",
        f"set ref_tt_ps {ref_tt_wns_ps:.6f}",
        "set base_wns_ps [expr {$base_wns_raw * $scale_ps}]",
        "if { abs($base_wns_ps - $ref_tt_ps) > 1.0 } {",
        "  if { abs($base_wns_raw * 1000.0 - $ref_tt_ps) <= 1.0 } { set scale_ps 1000.0 } elseif { abs($base_wns_raw - $ref_tt_ps) <= 1.0 } { set scale_ps 1.0 } else { error \"LR unit mismatch: raw=$base_wns_raw ref=$ref_tt_ps\" }",
        "}",
        "set base_wns_ps [expr {$base_wns_raw * $scale_ps}]",
        "set base_hold_ps [expr {$base_hold_raw * $scale_ps}]",
        f"set budget_ps {budget_ps:.6f}",
        "set target_wns_ps [expr {$base_wns_ps - $budget_ps}]",
        'puts "LR_CALIBRATED scale_ps=$scale_ps base_wns_ps=$base_wns_ps base_hold_ps=$base_hold_ps target_wns_ps=$target_wns_ps"',
        "set cands {",
        cand_block,
        "}",
        "array set lam {}",
        "array set active {}",
        "foreach item $cands {",
        "  lassign $item aid inst src tgt sav",
        "  set lam($inst) 1.0",
        "  set active($inst) 0",
        "}",
        "for {set iter 1} {$iter <= 5} {incr iter} {",
        "  foreach item $cands {",
        "    lassign $item aid inst src tgt sav",
        "    set db_inst [$blk findInst $inst]",
        '    if {$db_inst eq "NULL"} { continue }',
        "    set sta_cell [get_cells -quiet $inst]",
        '    if {$sta_cell eq ""} { continue }',
        "    set slk_ps 1.0e9",
        '    foreach p [get_pins -quiet -of_objects $sta_cell -filter "direction==output"] {',
        "      set s [get_property $p slack_max]",
        '      if {$s ne "" && $s ne "INF"} {',
        "        set sp [expr {$s * $scale_ps}]",
        "        if {$sp < $slk_ps} { set slk_ps $sp }",
        "      }",
        "    }",
        "    set norm [expr {max(10.0, abs($base_wns_ps))}]",
        "    set viol [expr {($target_wns_ps - $slk_ps) / $norm}]",
        "    set factor [expr {exp(min(3.0, max(-2.0, 2.0 * $viol)))}]",
        "    set lam($inst) [expr {max(0.05, min(1000.0, $lam($inst) * $factor))}]",
        "    if {$active($inst) == 0} {",
        "      set tgt_m [$db findMaster $tgt]",
        "      set src_m [$db findMaster $src]",
        '      if {$tgt_m eq "NULL" || $src_m eq "NULL"} { continue }',
        "      if {![$db_inst swapMaster $tgt_m]} { continue }",
        "      set nw_ps [expr {[sta::worst_slack_cmd max] * $scale_ps}]",
        "      set nh_ps [expr {[sta::worst_slack_cmd min] * $scale_ps}]",
        "      set dwns [expr {max(0.0, $base_wns_ps - $nw_ps)}]",
        "      set lag_gain [expr {$sav - $lam($inst) * 0.01 * $dwns}]",
        "      if {$lag_gain > 0.0 && $nw_ps >= $target_wns_ps && $nh_ps >= ($base_hold_ps - 0.001)} {",
        "        set active($inst) 1",
        "      } else {",
        "        $db_inst swapMaster $src_m",
        "      }",
        "    } else {",
        "      set cw_ps [expr {[sta::worst_slack_cmd max] * $scale_ps}]",
        "      set ch_ps [expr {[sta::worst_slack_cmd min] * $scale_ps}]",
        "      if {$cw_ps < $target_wns_ps || $ch_ps < ($base_hold_ps - 0.001)} {",
        "        set src_m [$db findMaster $src]",
        "        $db_inst swapMaster $src_m",
        "        set active($inst) 0",
        "      }",
        "    }",
        "  }",
        '  puts "LR_ITER $iter wns_ps=[expr {[sta::worst_slack_cmd max]*$scale_ps}] hold_ps=[expr {[sta::worst_slack_cmd min]*$scale_ps}]"',
        "}",
        "foreach item $cands {",
        "  lassign $item aid inst src tgt sav",
        "  if {$active($inst) == 1} {",
        '    puts "LR_COMMIT $aid"',
        "  }",
        "}",
        'puts "LR_FINAL wns_ps=[expr {[sta::worst_slack_cmd max]*$scale_ps}] hold_ps=[expr {[sta::worst_slack_cmd min]*$scale_ps}]"',
        "puts LR_SOLVE_DONE",
        "exit",
    ]
    lr_tcl.write_text("\n".join(lines) + "\n", encoding="utf-8")

    t0 = raw_seconds()
    res = cmp.run_process([runner.tools["openroad"], "-no_init", "-no_splash", "-threads", "1", "-exit", lr_tcl], lr_log, 180.0)
    dt = raw_seconds() - t0
    txt = cmp.checked_output(res, "LR_SOLVE_DONE")
    committed = [
        line.split(None, 1)[1].strip()
        for line in txt.splitlines()
        if line.startswith("LR_COMMIT ")
    ]
    m_fin = re.search(r"LR_FINAL wns_ps=([+-]?\S+) hold_ps=([+-]?\S+)", txt)
    by_id = {a.action_id: a for a in runner.pool}
    nominal_area = sum(by_id[aid].estimated_area_saving for aid in committed)
    return {
        "solve_seconds": dt,
        "committed_actions": sorted(committed),
        "committed_count": len(committed),
        "nominal_area_saved_um2": nominal_area,
        "frozen_final_tt_wns_ps": float(m_fin.group(1)) if m_fin else None,
        "frozen_final_tt_hold_ps": float(m_fin.group(2)) if m_fin else None,
        "log": str(lr_log),
    }


def make_boxed_runner(kind: str, run_dir: Path):
    if kind == "sky130hd_aes":
        class AesBoxed(ColdOnlineComparison):
            def diagnose(self, actions, directory):
                return boxed_drc.diagnose_boxed(self, actions, directory, halo_rows=1.0)

        runner = AesBoxed(Path("/home/toylog/faeco_tcad_sky_holdout_20261123/aes_matrix_v1"), run_dir)
        runner.use_preview = True
        return runner, "sky130hd", runner.gate.wns_ps, runner.eval.ref_views["TT"]["setup_wns_ps"], 113.363

    if kind == "asap7_uart":
        proto = json.loads(Path("/home/toylog/faeco_tcad_uart_wallclock_20261125_v1/protocol.json").read_text())
        seed_path = Path(proto["seed"]["path"])
        seed = json.loads(seed_path.read_text())
        args = seed_args(seed, proto)
        args.max_evals = 1

        class UartBoxed(UartComparison):
            def diagnose(self, actions, directory):
                return boxed_drc.diagnose_boxed(self, actions, directory, halo_rows=1.0)

        run_dir.mkdir(parents=True, exist_ok=True)
        with bind_runtime("uart", Path(seed["bindings"]["flow"]["fastroute.tcl"]["path"])):
            runner = UartBoxed(args, seed_path.parent, run_dir, proto["screen_input"], proto["charged_screening_seconds_per_arm"])
        runner.use_preview = True
        return runner, "asap7", runner.gate.wns_ps, runner.eval.ref_views["TT"]["setup_wns_ps"], proto["charged_screening_seconds_per_arm"]

    if kind in ("sky130hd_riscv32i", "asap7_aes"):
        proto_path = (
            Path("/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i/matrix_rank_aligned_v1/protocol.json")
            if kind == "sky130hd_riscv32i"
            else Path("/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/matrix_boxed_drc_20261126_v1/protocol.json")
        )
        proto = json.loads(proto_path.read_text())
        seed_path = Path(proto["seed"]["path"])
        seed = json.loads(seed_path.read_text())
        pdk = proto["pdk"]
        top = proto["top"]
        orfs = Path(seed["bindings"]["flow"]["setRC.tcl"]["path"]).parents[2]
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

        class QualBoxed(QualifiedWallclockComparison):
            def diagnose(self, actions, directory):
                return boxed_drc.diagnose_boxed(self, actions, directory, halo_rows=1.0)

        with bind_runtime(top, Path(seed["bindings"]["flow"]["fastroute.tcl"]["path"])):
            runner = QualBoxed(args, seed_path.parent, run_dir, proto["screen_input"], proto["charged_screening_seconds_per_arm"])
        runner.use_preview = True
        return runner, pdk, runner.gate.wns_ps, runner.eval.ref_views["TT"]["setup_wns_ps"], proto["charged_screening_seconds_per_arm"]

    raise ValueError(kind)


def main() -> int:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    summary = json.loads(OUT_JSON.read_text()) if OUT_JSON.is_file() else {"designs": {}}
    for kind in ("sky130hd_aes", "sky130hd_riscv32i", "asap7_uart", "asap7_aes"):
        if kind in summary["designs"] and "--force" not in sys.argv:
            print(f"=== Skipping already-completed {kind} ===", flush=True)
            continue
        print(f"\n=== Running Classical 5-Iter Frozen-SPEF LR on {kind} ===", flush=True)
        run_dir = OUT_ROOT / kind
        if run_dir.exists():
            import shutil
            shutil.rmtree(run_dir)
        runner, pdk, budget_ps, ref_tt_wns_ps, screen_s = make_boxed_runner(kind, run_dir)
        pool_ceiling = sum(a.estimated_area_saving for a in runner.pool)
        base_area = runner.eval.ref_area

        with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
            lr = run_lr_solve(runner, pdk, budget_ps, ref_tt_wns_ps, run_dir / "lr_solve")
            print(
                f"  [{kind}] LR solved in {lr['solve_seconds']:.2f}s -> committed={lr['committed_count']}/{len(runner.pool)} "
                f"(nominal={lr['nominal_area_saved_um2']:.6f} um2, frozen_TT_WNS={lr['frozen_final_tt_wns_ps']:.3f} ps)",
                flush=True,
            )
            phys_dir = run_dir / "physical"
            t0 = raw_seconds()
            with process_ledger(run_dir / "subprocesses.json", raw_seconds() + 600.0):
                ep, rec = runner.attempt(tuple(lr["committed_actions"]), phys_dir)
            phys_s = raw_seconds() - t0

        final_pass = rec["passes"][-1]
        phys_receipt = json.loads((phys_dir / final_pass / "receipt.json").read_text())
        ref_views = runner.eval.ref_views
        views_delta = {}
        for c in ("FF", "TT", "SS"):
            if c in phys_receipt.get("views", {}):
                views_delta[c] = {
                    "d_setup_wns_ps": phys_receipt["views"][c]["setup_wns_ps"] - ref_views[c]["setup_wns_ps"],
                    "d_setup_tns_ps": phys_receipt["views"][c]["setup_tns_ps"] - ref_views[c]["setup_tns_ps"],
                    "d_hold_wns_ps": phys_receipt["views"][c]["hold_wns_ps"] - ref_views[c]["hold_wns_ps"],
                    "abs_hold_wns_ps": phys_receipt["views"][c]["hold_wns_ps"],
                }
        unlocked_path = phys_dir / final_pass / "unlocked_drc/audit.json"
        unlocked_drc = json.loads(unlocked_path.read_text())["drc_markers"] if unlocked_path.is_file() else None
        passed = bool(ep.valid and ep.sec_pass and not rec["failures"])
        qualified_area = (base_area - ep.area) if passed else 0.0

        row = {
            "design": kind,
            "pdk": pdk,
            "top": runner.top,
            "base_area_um2": base_area,
            "pool_size": len(runner.pool),
            "pool_ceiling_um2": pool_ceiling,
            "wns_budget_ps": budget_ps,
            "charged_screening_s": screen_s,
            "lr_solve": lr,
            "physical_passes": rec["passes"],
            "physical_seconds": phys_s,
            "total_seconds_incl_screen": screen_s + lr["solve_seconds"] + phys_s,
            "unlocked_drc_markers": unlocked_drc,
            "views_delta_ps": views_delta,
            "failures": rec["failures"],
            "passed_all_gates": passed,
            "qualified_area_saved_um2": qualified_area,
            "qualified_pool_capture_pct": 100.0 * qualified_area / pool_ceiling if pool_ceiling else 0.0,
            "endpoint_area_um2": ep.area,
        }
        summary["designs"][kind] = row
        OUT_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(
            f"  [{kind}] PHYSICAL: passes={rec['passes']} elapsed={phys_s:.2f}s | passed={passed} | "
            f"qual_area={qualified_area:.6f} um2 | unlocked_drc={unlocked_drc} | fails={rec['failures']}",
            flush=True,
        )

    print("\nWrote", OUT_JSON, "sha256=", sha256(OUT_JSON), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
