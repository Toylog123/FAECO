#!/usr/bin/env python3
"""Replay the frozen standard 16-action UART native proposal in the protected backend."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "code/src"))

import run_v5_step2_dedup_and_native_protected as stage2


PROPOSAL = (stage2.OUT_ROOT / "native_protected/asap7_uart/native_std/extract/native_diffs.txt")
PROPOSAL_SHA = "269d62f05c711c9177d5ad07ebca53b0d33668f110c5ba2ed9cc397dcd24d44c"
AREA_LINE = re.compile(r"(?m)^([ \t]*area[ \t]*:[ \t]*[-+0-9.eE]+)[ \t]*$")
LIMIT = 720.0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir()
    root = args.output.resolve()
    cmp = stage2.cmp
    original = PROPOSAL.read_bytes()
    if hashlib.sha256(original).hexdigest() != PROPOSAL_SHA:
        raise ValueError("Unexpected native proposal bytes")
    diffs = [tuple(line.split("\t")) for line in original.decode().splitlines()]
    if len(diffs) != 16 or len({name for name, _, _ in diffs}) != 16:
        raise ValueError("Expected sixteen distinct frozen native moves")
    if {(src, dst) for _, src, dst in diffs} != {("BUFx3_ASAP7_75t_R", "HB3xp67_ASAP7_75t_R")}:
        raise ValueError("Expected the frozen matched-footprint native moves")
    (root / "native_diffs.txt").write_bytes(original)
    runner, pdk, setup_budget, _, _ = stage2.lr_mod.make_boxed_runner("asap7_uart", root / "runner")
    if pdk != "asap7" or not math.isclose(setup_budget, 2.7) or runner.eval.args.route_timeout != 240.0:
        raise ValueError("Expected the frozen 270 ps protected-run policy")
    if runner.eval.args.clock_period_ps != 270.0 or runner.eval.args.threads != 4:
        raise ValueError("Expected the original clock and route thread count")

    with stage2.bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        raw_input_bindings = {name: cmp.bind(path) for name, path in runner.eval.control.items()}
        library_hashes = {str(p): cmp.bind(p) for paths in runner.eval.libraries.values() for p in paths}
        old_areas, old_reference = runner.eval.areas, runner.eval.ref_area
        areas, normalized = {}, []
        for path in runner.eval.libraries["TT"]:
            original_lib = path.read_text(encoding="utf-8")
            amended, edits = AREA_LINE.subn(r"\1;", original_lib)
            areas.update(cmp.parse_generic_liberty_catalog(amended)[1])
            if edits:
                normalized.append({"input": cmp.bind(path), "edits": edits,
                                   "in_memory_sha256": hashlib.sha256(amended.encode()).hexdigest()})
        if (len(old_areas), len(areas), sum(row["edits"] for row in normalized)) != (160, 202, 42):
            raise ValueError("Unexpected frozen Liberty area-key counts")
        if any(areas[key] != value for key, value in old_areas.items()):
            raise ValueError("Normalization modified a previously indexed area")
        ref_masters = cmp.logical_masters(runner.eval.control["v"], areas)
        missing, mismatched = stage2.bind_native_resizes(diffs, ref_masters)
        conflicts = stage2.protected_net_conflicts(diffs, runner.nets)
        if missing or mismatched or conflicts:
            raise ValueError(f"Cannot bind all native actions to ordinary signal nets: {missing}, {mismatched}, {conflicts}")
        runner.eval.areas = areas
        runner.eval.ref_masters = ref_masters
        runner.eval.ref_area = math.fsum(areas[master] for master in ref_masters.values())
        if not math.isclose(runner.eval.ref_area, 101.89962, abs_tol=1e-10):
            raise ValueError("Unexpected normalized frozen reference area")
        ids = []
        for pos, (instance, source, target) in enumerate(diffs):
            action_id = f"native_{pos:04d}_{instance}"
            area_delta = areas[source] - areas[target]
            if area_delta != 0.0:
                raise ValueError("Expected true equal-area swaps")
            runner.eval.actions[action_id] = cmp.PhysicalAction(
                action_id=action_id, instance=instance, source_cell=source, target_cell=target,
                estimated_area_saving=area_delta, category="native_recover_power")
            ids.append(action_id)
        actions = tuple(sorted(ids))
        _, incident = runner.direct_nets(actions)
        if len(incident) != 32:
            raise ValueError("Unexpected frozen incident signal-net count")
        pre_run = {
            "proposal": cmp.bind(PROPOSAL), "proposal_mode": "native_std",
            "actions": actions, "incident_signal_nets": sorted(incident), "declared_area_delta_um2": 0.0,
            "normalized_liberty_inputs": normalized, "old_reference_area_um2": old_reference,
            "complete_reference_area_um2": runner.eval.ref_area, "control_inputs": raw_input_bindings,
            "liberty_inputs": library_hashes, "runner_protocol": cmp.bind(root / "runner/protocol.json"),
            "route_timeout_seconds": runner.eval.args.route_timeout,
            "sta_timeout_seconds_per_view": runner.eval.args.sta_timeout,
            "sec_timeout_seconds": runner.eval.args.sec_timeout, "candidate_window_seconds": LIMIT,
            "setup_budget_ps_per_view": setup_budget,
        }
        cmp.save(root / "replay_protocol.json", pre_run)
        print("Bound all 16 frozen native edits and 32 incident SIGNAL nets", flush=True)
        with stage2.qualified.qualified_process_clock():
            runner.use_preview = False
            reference = runner.qualify_zero()
            runner.use_preview = True
            print("Strict zero preflight passed; dispatching the sole 16-action proposal", flush=True)
            start = stage2.raw_seconds()
            result = {"start_raw": start, "reference": cmp.bind(root / "runner/preflight/zero/result.json")}
            try:
                with stage2.process_ledger(root / "candidate_subprocesses.json", start + LIMIT):
                    endpoint, assessment = runner.attempt(actions, root / "runner/protected_eval")
                result.update({
                    "assessment": cmp.bind(root / "runner/protected_eval/result.json"),
                    "raw_net_area_recovery_um2": reference.area - endpoint.area,
                    "qualified_area_recovery_um2": reference.area - endpoint.area if
                      (cmp.assess(reference, endpoint, runner.policy).feasible
                       and endpoint.area < reference.area - 1e-9 and endpoint.sec_pass
                       and not assessment["failures"]) else 0.0,
                    "failures": assessment["failures"],
                    "physical": assessment["physical_receipt"],
                    "passes": assessment["passes"],
                })
            except stage2.WallWindowEnded:
                result["failures"] = ["outer_window_timeout"]
            result["candidate_seconds"] = stage2.raw_seconds() - start
        if (raw_input_bindings != {name: cmp.bind(path) for name, path in runner.eval.control.items()}
                or library_hashes != {str(p): cmp.bind(p) for paths in runner.eval.libraries.values() for p in paths}):
            raise ValueError("A frozen input changed")
        cmp.save(root / "result.json", result)
        print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
