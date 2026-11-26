#!/usr/bin/env python3
"""V5 Stage 2 (resumable, pinned CPU 0-5):
Part A: Setup Deduplication Independent Ablation on asap7/uart
  - Compares dedup=OFF (known_split_rejection=None) vs dedup=ON under identical
    1.0*H_row boxed DRC backend, 18-action pool, area initial rank, 720 s wall-clock.
Part B: OpenROAD Native `repair_timing -recover_power` Mounted on FAECO's
  1.0*H_row Protected Local-Reroute Backend across all 4 designs
  (sky130hd_aes, sky130hd_riscv32i, asap7_uart, asap7_aes) for both standard and
  `-allow_setup_violations` modes -> cleanly decouples native sizing selection from
  unguarded full-block rerouting!
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import mkdtemp

REPO = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
EVID = REPO / "project_docs/evidence"
for sub in (
    "tcad_ibex_20261123",
    "tcad_holdout_20261123",
    "tcad_wallclock_schedule_20261125",
    "tcad_asap7_aes_holdout_20261125",
    "tcad_boxed_drc_20261126",
    "tcad_external_baselines_20261125",
):
    p = str(EVID / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

import compare_ibex as cmp
import incident_cap_priority
import run_lr_4designs as lr_mod
import run_qualified_wallclock as qualified
from run_aes_incident_priority_matched_v2 import WallWindowEnded, process_ledger
from run_screened_matrix import RELATIVE_HOLD_REASONS, bind_runtime, raw_seconds

OR_BIN = "/home/toylog/.cache/bazel/_bazel_toylog/c540bbdc4bbb635360729b4d7a91c803/execroot/_main/bazel-out/k8-opt/bin/openroad_unstamped"
OUT_ROOT = Path("/home/toylog/faeco_v5_step2_dedup_native_20261126_v1")
OUT_JSON = EVID / "tcad_v5_revision_20261126/V5_STEP2_DEDUP_NATIVE_VERIFIED.json"
LIMIT_S = 720.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_auc(cps: list[dict], limit_s: float = 720.0) -> float:
    best = 0.0
    pts = [(0.0, 0.0)]
    for c in sorted(cps, key=lambda x: x["elapsed_s"]):
        if c["elapsed_s"] <= limit_s and c["accepted"] and c["area_saved_um2"] > best:
            best = float(c["area_saved_um2"])
            pts.append((float(c["elapsed_s"]), best))
    pts.append((limit_s, best))
    return sum(max(0.0, t1 - t0) * v0 for (t0, v0), (t1, _) in zip(pts, pts[1:])) / limit_s


def run_uart_dedup_ablation(existing: dict, force: bool) -> dict:
    out = dict(existing)
    for mode, use_dedup in (("dedup_off", False), ("dedup_on", True)):
        if mode in out and not force:
            print(f"[Stage 2A] Skipping existing {mode}", flush=True)
            continue
        rdir = OUT_ROOT / "uart_dedup" / mode
        if rdir.exists():
            shutil.rmtree(rdir)
        runner, pdk, budget_ps, _, screen_s = lr_mod.make_boxed_runner("asap7_uart", rdir)
        if not hasattr(runner, "initial_hint"):
            runner.initial_hint = set()
        ref_area = runner.eval.ref_area
        pool = list(runner.pool)
        pool_ceiling = sum(a.estimated_area_saving for a in pool)

        with (
            bind_runtime(runner.top, runner.flow["fastroute.tcl"]),
            qualified.qualified_ranking(),
            qualified.qualified_process_clock(),
        ):
            runner.use_preview = False
            reference = runner.qualify_zero()
            runner.use_preview = True

            begun = raw_seconds()
            deadline = begun + (LIMIT_S - screen_s)
            reqs = []
            cps = []
            best_ep = reference
            best_saved = 0.0
            best_gates = 0
            known_rej: set[tuple[str, ...]] = set()
            dedup_hits = 0

            def eval_fn(actions):
                nonlocal best_ep, best_saved, best_gates
                now = raw_seconds()
                if now >= deadline:
                    raise WallWindowEnded()
                seq = len(reqs) + 1
                reqs.append({"id": seq, "actions": list(actions)})
                ep, rec = runner.attempt(actions, rdir / "trials" / f"{seq:02d}")
                fin = raw_seconds()
                if fin >= deadline:
                    raise WallWindowEnded()
                acc = cmp.assess(reference, ep, runner.policy).feasible and ep.area < best_ep.area - 1e-9 and ep.sec_pass
                reqs[-1].update(failures=rec["failures"], accepted=acc)
                if not acc:
                    # Only record pure-setup complete-measurement rejections (excluding timeouts/DRC/hold)
                    fails = set(rec["failures"])
                    if fails and fails.issubset({"FF:setup_budget", "TT:setup_budget", "SS:setup_budget", "FF:tns_budget", "TT:tns_budget", "SS:tns_budget"}):
                        known_rej.add(tuple(sorted(actions)))
                else:
                    best_ep = ep
                    best_saved = ref_area - ep.area
                    best_gates = len(actions)
                cps.append({"elapsed_s": screen_s + (fin - begun), "accepted": acc, "area_saved_um2": (ref_area - ep.area) if acc else 0.0, "failures": rec["failures"]})
                return ep

            def defer_fn(actions):
                return bool(RELATIVE_HOLD_REASONS.intersection(reqs[-1].get("failures", [])))

            def known_fn(trial):
                nonlocal dedup_hits
                if tuple(sorted(trial)) in known_rej:
                    dedup_hits += 1
                    return True
                return False

            with process_ledger(rdir / "subprocesses.json", deadline):
                try:
                    rcap = incident_cap_priority.build_incident_priority(runner.eval.control["def"], runner.eval.control["spef"], pool)
                    prios = {k: row["priority"] for k, row in rcap["actions"].items()}
                    cmp.adaptive_batch_recovery(
                        reference, pool, eval_fn, runner.policy,
                        max_evaluations=None, batch_size=3,
                        defer_split_for=defer_fn,
                        priority_after_defer=prios,
                        known_split_rejection=(known_fn if use_dedup else None),
                    )
                except WallWindowEnded:
                    pass

            total_wall = screen_s + (raw_seconds() - begun)
            auc = compute_auc(cps, LIMIT_S)
            out[mode] = {
                "use_dedup": use_dedup,
                "qualified_area_saved_um2": best_saved,
                "qualified_gates": best_gates,
                "area_saved_pct": 100.0 * best_saved / ref_area,
                "pool_capture_pct": 100.0 * best_saved / pool_ceiling,
                "anytime_auc_um2": auc,
                "logical_finished": len(cps),
                "dedup_hits": dedup_hits,
                "total_wall_s_incl_screen": total_wall,
                "checkpoints": cps,
            }
            print(f"  [Stage 2A/{mode}] saved={best_saved:.6f} um2 ({best_gates}/18), AUC={auc:.4f}, evals={len(cps)}, dedup_hits={dedup_hits}, wall={total_wall:.1f}s", flush=True)
    return out


def extract_native_resizes(runner, extra_flags: str, out_dir: Path) -> tuple[list[tuple[str, str, str]], float]:
    """Run OpenROAD native `repair_timing -recover_power 100` in-memory on frozen control ODB/SPEF
    and extract the exact list of (inst_odb, old_master, new_master) resized cells."""
    out_dir.mkdir(parents=True, exist_ok=True)
    diff_txt = out_dir / "native_diffs.txt"
    tcl = out_dir / "extract_native.tcl"
    tt_libs = runner.eval.libraries["TT"]
    ctrl = runner.eval.control
    lines = [f"read_liberty {cmp.tcl(lib)}" for lib in tt_libs]
    lines += [
        f"read_db {cmp.tcl(ctrl['odb'])}",
        f"read_sdc {cmp.tcl(ctrl['sdc'])}",
        f"read_spef {cmp.tcl(ctrl['spef'])}",
        f"source {cmp.tcl(runner.flow['setRC.tcl'])}",
        "set blk [ord::get_db_block]",
        "array set before_m {}",
        "foreach inst [$blk getInsts] {",
        "  if { ![$inst isFixed] } { set before_m([$inst getName]) [[$inst getMaster] getName] }",
        "}",
        "remove_fillers",
        f"repair_timing -recover_power 100 {extra_flags}",
        f"set f [open {cmp.tcl(diff_txt)} w]",
        "foreach inst [$blk getInsts] {",
        "  set nm [$inst getName]",
        "  if { [info exists before_m($nm)] } {",
        "    set am [[$inst getMaster] getName]",
        "    if { $am ne $before_m($nm) } {",
        "      puts $f \"$nm\\t$before_m($nm)\\t$am\"",
        "    }",
        "  }",
        "}",
        "close $f",
        "puts NATIVE_EXTRACT_OK",
        "exit",
    ]
    tcl.write_text("\n".join(lines) + "\n", encoding="utf-8")
    t0 = raw_seconds()
    r = subprocess.run([OR_BIN, "-no_init", "-no_splash", "-threads", "1", "-exit", str(tcl)],
                       capture_output=True, text=True, timeout=300)
    dt = raw_seconds() - t0
    assert r.returncode == 0, f"native extract failed: {r.stderr[-400:]}"
    diffs = []
    for ln in diff_txt.read_text(encoding="utf-8").splitlines():
        parts = ln.strip().split("\t")
        if len(parts) == 3:
            diffs.append((parts[0], parts[1], parts[2]))
    return diffs, dt


def bind_native_resizes(diffs, ref_masters):
    # Keep raw OpenDB names for findInst; the frozen netlist uses canonical keys.
    canonical, _ = cmp.align_db_instances({}, {inst: (old, new) for inst, old, new in diffs})
    missing = sorted(name for name in canonical if name not in ref_masters)
    mismatched = sorted(name for name, (_, (old, _)) in canonical.items()
                        if name in ref_masters and ref_masters[name] != old)
    return missing, mismatched


def protected_net_conflicts(diffs, nets):
    by_name = {cmp.canonical_odb_name(inst): inst for inst, _, _ in diffs}
    conflicts = {}
    for net, entry in nets.items():
        if "+ USE SIGNAL" in entry:
            continue
        terminals = entry.partition(" + ")[0]
        for name in re.findall(r"\( (\S+) \S+ \)", terminals):
            raw = by_name.get(cmp.canonical_odb_name(name))
            if raw is not None:
                conflicts.setdefault(raw, []).append(net)
    return {inst: sorted(nets) for inst, nets in sorted(conflicts.items())}


def run_native_on_protected_backend(existing: dict, force: bool, checkpoint, designs=None,
                                    route_timeout=None, key_suffix="", project_signal_only=False) -> dict:
    out = dict(existing)
    designs = designs or ("sky130hd_aes", "sky130hd_riscv32i", "asap7_uart", "asap7_aes")
    for kind in designs:
        for mode_label, flags in (("native_std", ""), ("native_allow_setup", "-allow_setup_violations")):
            key = f"{kind}::{mode_label}{key_suffix}"
            if key in out and not force:
                print(f"[Stage 2B] Skipping existing {key}", flush=True)
                continue
            attempts = OUT_ROOT / "native_protected" / kind / (mode_label + key_suffix)
            attempts.mkdir(parents=True, exist_ok=True)
            rdir = Path(mkdtemp(prefix="attempt_", dir=attempts))
            runner_root = rdir / "runner"
            runner, pdk, budget_ps, _, _ = lr_mod.make_boxed_runner(kind, runner_root)
            if not hasattr(runner, "initial_hint"):
                runner.initial_hint = set()
            # qualify_zero() creates <runner.output>/preflight with a non-recursive mkdir
            Path(runner.output).mkdir(parents=True, exist_ok=True)
            if route_timeout is not None:
                for holder in (getattr(runner, "args", None), getattr(getattr(runner, "eval", None), "args", None)):
                    if holder is not None and hasattr(holder, "route_timeout"):
                        holder.route_timeout = float(route_timeout)
            diffs, ext_s = extract_native_resizes(runner, flags, rdir / "extract")
            proposal_count = len(diffs)
            proposal = cmp.bind(rdir / "extract/native_diffs.txt")
            print(f"  [Stage 2B/{key}] native proposed {len(diffs)} resizes in {ext_s:.2f}s", flush=True)
            if not diffs:
                out[key] = {
                    "design": kind, "mode": mode_label, "native_proposed_count": 0,
                    "extract_s": round(ext_s, 3), "qualified_area_saved_um2": 0.0,
                    "status": "zero_native_edits", "failures": ["zero_edits"],
                    "raw_directory": str(rdir),
                }
                checkpoint(out)
                continue

            missing, mismatched = bind_native_resizes(diffs, runner.eval.ref_masters)
            if mismatched:
                raise ValueError(f"native proposals do not bind frozen source masters: {mismatched[:10]}")
            if missing:
                out[key] = {
                    "design": kind, "mode": mode_label,
                    "native_proposed_count": len(diffs),
                    "extract_s": round(ext_s, 3),
                    "status": "not_in_action_space",
                    "not_in_action_space_count": len(missing),
                    "not_in_action_space_examples": missing[:10],
                    "qualified_area_saved_um2": 0.0,
                    "failures": ["not_in_action_space"],
                    "raw_directory": str(rdir),
                    "proposal": proposal,
                }
                checkpoint(out)
                print(f"  [Stage 2B/{key}] status=not_in_action_space ({len(missing)}/{len(diffs)} "
                      f"instances outside the frozen netlist, e.g. {missing[:3]})", flush=True)
                continue

            conflicts = protected_net_conflicts(diffs, runner.nets)
            if conflicts and not project_signal_only:
                out[key] = {
                    "design": kind, "mode": mode_label, "native_proposed_count": proposal_count,
                    "status": "unsupported_protected_scope", "failures": ["non_signal_incident_nets"],
                    "protected_net_conflicts": conflicts, "qualified_area_saved_um2": 0.0,
                    "extract_s": round(ext_s, 3), "raw_directory": str(rdir), "proposal": proposal,
                }
                print(f"  [Stage 2B/{key}] status=unsupported_protected_scope {conflicts}", flush=True)
                checkpoint(out)
                continue
            if project_signal_only:
                if not conflicts:
                    raise ValueError(f"projected arm {key} must remove a protected non-signal action")
                diffs = [row for row in diffs if row[0] not in conflicts]
                if not diffs:
                    raise ValueError(f"projected arm {key} has no eligible actions")

            # Register native resizes as PhysicalAction objects and run through FAECO's 1.0*H_row protected backend!
            areas = cmp.liberty_areas(runner.eval.libraries["TT"])
            unknown = sorted({cell for _, old, new in diffs for cell in (old, new) if cell not in areas})
            if unknown:
                raise ValueError(f"native resize masters lack TT Liberty area: {unknown[:10]}")
            nat_ids = []
            for idx, (inst_odb, old_m, new_m) in enumerate(diffs):
                aid = f"native_{idx:04d}_{inst_odb}"
                sav = areas[old_m] - areas[new_m]
                pa = cmp.PhysicalAction(
                    action_id=aid, instance=inst_odb,
                    source_cell=old_m, target_cell=new_m,
                    estimated_area_saving=sav, category="native_recover_power",
                )
                runner.eval.actions[aid] = pa
                nat_ids.append(aid)
            nat_tuple = tuple(sorted(nat_ids))

            with (
                bind_runtime(runner.top, runner.flow["fastroute.tcl"]),
                qualified.qualified_process_clock(),
            ):
                if kind == "sky130hd_aes":
                    pf_res = Path("/home/toylog/faeco_v4_hybrid_faeco_20261126_v1/sky_shared_preflight/preflight/result.json")
                    reference = runner.prepare_online(pf_res.resolve(strict=True))
                else:
                    runner.use_preview = False
                    reference = runner.qualify_zero()
                    runner.use_preview = True

                t0 = raw_seconds()
                deadline = t0 + (float(route_timeout) + 240.0 if route_timeout else 600.0)
                status = "evaluated"
                fails = []
                saved = 0.0
                sec_ok = False
                views_delta = {}
                evaluation = None
                try:
                    with process_ledger(rdir / "subprocesses.json", deadline):
                        ep, rec = runner.attempt(nat_tuple, runner_root / "protected_eval")
                        fails = list(rec["failures"])
                        gate_ok = cmp.assess(reference, ep, runner.policy).feasible and ep.area < reference.area - 1e-9 and ep.sec_pass
                        if gate_ok and not fails:
                            status = "qualified_pass"
                            saved = runner.eval.ref_area - ep.area
                            sec_ok = True
                        else:
                            status = "rejected"
                        last_p = rec["passes"][-1]
                        evaluation = cmp.bind(runner_root / "protected_eval" / "result.json")
                        rp = runner_root / "protected_eval" / last_p / "receipt.json"
                        if rp.is_file():
                            rd = json.loads(rp.read_text())
                            views_delta = {
                                c: {
                                    "d_setup_wns_ps": rd["views"][c]["setup_wns_ps"] - runner.eval.ref_views[c]["setup_wns_ps"],
                                    "d_hold_wns_ps": rd["views"][c]["hold_wns_ps"] - runner.eval.ref_views[c]["hold_wns_ps"],
                                    "d_setup_tns_ps": rd["views"][c]["setup_tns_ps"] - runner.eval.ref_views[c]["setup_tns_ps"],
                                    "d_hold_tns_ps": rd["views"][c]["hold_tns_ps"] - runner.eval.ref_views[c]["hold_tns_ps"],
                                }
                                for c in ("FF", "TT", "SS") if c in rd.get("views", {})
                            }
                except WallWindowEnded:
                    status = "outer_window_timeout"
                    fails = ["outer_window_timeout"]

                eval_s = raw_seconds() - t0
                operations = rdir / "subprocesses.json"
                timed_out = None
                if operations.is_file():
                    timed_out = next((row for row in json.loads(operations.read_text())
                                      if "returncode" in row and row["returncode"] is None), None)
                    if timed_out and status == "rejected":
                        status = "evaluation_timeout"
                diagnosis = runner_root / "diagnosis/protected_eval/diagnosis.json"
                out[key] = {
                    "design": kind, "mode": mode_label,
                    "native_proposed_count": proposal_count,
                    "protected_attempted_count": len(diffs),
                    "signal_only_projection": project_signal_only,
                    "protected_net_conflicts": conflicts,
                    "extract_s": round(ext_s, 3),
                    "protected_eval_s": round(eval_s, 3),
                    "status": status,
                    "qualified_area_saved_um2": saved,
                    "sec_pass": sec_ok,
                    "failures": fails,
                    "views_delta_ps": views_delta,
                    "raw_directory": str(rdir),
                    "proposal": proposal,
                    "evaluation": evaluation,
                    "diagnosis": cmp.bind(diagnosis) if diagnosis.is_file() else None,
                    "subprocess_ledger": cmp.bind(operations) if operations.is_file() else None,
                    "boxed_backend": cmp.bind(Path(lr_mod.boxed_drc.__file__)),
                    "timeout_operation": timed_out,
                    "route_timeout_seconds": runner.eval.args.route_timeout,
                    "outer_window_seconds": deadline - t0,
                }
                checkpoint(out)
                print(f"  [Stage 2B/{key}] status={status} saved={saved:.6f} um2 eval={eval_s:.1f}s fails={fails[:5]}", flush=True)
    return out


def main() -> int:
    force = "--force" in sys.argv
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(OUT_JSON.read_text()) if OUT_JSON.is_file() else {"uart_dedup_ablation": {}, "native_on_protected_backend": {}}

    data["uart_dedup_ablation"] = run_uart_dedup_ablation(data.get("uart_dedup_ablation", {}), force)
    cmp.save(OUT_JSON, data)

    def checkpoint(native):
        data["native_on_protected_backend"] = native
        cmp.save(OUT_JSON, data)

    native = run_native_on_protected_backend(data.get("native_on_protected_backend", {}), force, checkpoint)
    # Second pass: the two SKY130HD designs get a 600 s per-trial route budget so the failure mode is
    # attributable to physics rather than to the default 240 s cap shared by every FAECO arm.
    native = run_native_on_protected_backend(
        native, force, checkpoint, designs=("sky130hd_aes", "sky130hd_riscv32i"),
        route_timeout=600.0, key_suffix="::rt600s",
    )
    run_native_on_protected_backend(
        native, force, checkpoint, designs=("sky130hd_aes",), route_timeout=600.0,
        key_suffix="::rt600s::signal_only", project_signal_only=True,
    )

    print("DONE Stage 2 ->", OUT_JSON, "sha256=", sha256(OUT_JSON), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
