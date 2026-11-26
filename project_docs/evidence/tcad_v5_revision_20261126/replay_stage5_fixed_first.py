#!/usr/bin/env python3
"""Replay just the frozen Stage 5 fixed strategy's first accepted candidate."""

import argparse
from dataclasses import asdict
import math
from pathlib import Path
import re
import sys
from zipfile import ZipFile


LINEAGE = "c4ede33ddcb4400184a115f4718fe8adeabd6935"
EVIDENCE_RELATIVE = Path("project_docs/evidence/tcad_v5_revision_20261126")
ROOT = Path("/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO")
REPLAY_TIMEOUT_S = 450
POLICY_FIELDS = (
    "top", "pdk", "ordered_pool", "batch_size", "area_target_pct", "clock", "gate",
    "absolute_hold_ps", "hold_tolerance_ps", "route_threads", "affinity", "single_pin_access",
    "endpoint_checks", "strategies", "selection", "box_halo_rows",
    "wall_window_seconds_including_screen", "rank_charge_policy",
)


def frozen_first(evidence):
    """Load the hash-bound dispatch without following the old WSL paths."""
    import json

    sys.path.insert(0, str(evidence))
    import verify_review_evidence as review

    state_path = evidence / review.NAMES[5]
    state_data = state_path.read_bytes()
    review.check_bytes(state_data, review.SHA256[5], state_path.name)
    state = json.loads(state_data)
    archive_path = evidence / review.ARCHIVE
    review.check_bytes(archive_path.read_bytes(), review.ARCHIVE_SHA, archive_path.name)
    arm = state["arms"]["fixed_boxed"]
    point = arm["accepted_checkpoints"][0]
    with ZipFile(archive_path) as archive:
        protocol = json.loads(review.original(archive, state["protocol"]))
        progress = json.loads(review.original(archive, arm["progress"]))
        receipt = json.loads(review.original(archive, point["receipt"]))
        physical = json.loads(review.original(archive, point["physical"]))
        proof = json.loads(review.original(archive, point["sec"]))
        drc = json.loads(review.original(archive, point["drc"]))
    first = progress["logical_requests"][0]
    actions = sorted(state["rank_order"][:protocol["batch_size"]])
    review.require(
        state["status"] == "finished"
        and state["screened_pool_size"] == 18
        and len(set(state["rank_order"])) == 18
        and progress["method"] == "fixed"
        and first["id"] == 1
        and point["gates"] == protocol["batch_size"] == len(actions) == 3
        and actions == first["actions"] == point["actions"] == receipt["actions"] == physical["actions"]
        and progress["checkpoints"][0]["accepted"] is True
        and progress["checkpoints"][0]["endpoint"] == receipt["endpoint"]
        and not first["failures"] and not receipt["failures"] and not physical["failures"]
        and receipt["physical_receipt"] == point["physical"]
        and physical["routed_to_completion"] and physical["extracted_to_completion"]
        and physical["drc_violations"] == drc["drc_markers"] == 0
        and proof["passed"] and proof["proven"] == point["sec_proven"] == 4559
        and proof["unproven"] == point["sec_unproven"] == 0
        and proof["gate"] == physical["artifacts"]["v"],
        "historical first dispatch, acceptance and bound physical evidence disagree",
    )
    return {"state": state, "state_file": state_path, "archive_file": archive_path,
            "protocol": protocol, "point": point, "physical": physical, "actions": actions}


def fingerprints(sources):
    return {key: (item["bytes"], item["sha256"]) for key, item in sources.items()}


def check_policy(current, frozen):
    fields = [key for key in POLICY_FIELDS if current[key] != frozen[key]]
    if fingerprints(current["sources"]) != fingerprints(frozen["sources"]):
        fields.append("sources")
    if fields:
        raise ValueError(f"fresh Stage 5 protocol changed: {', '.join(fields)}")


def rebuilt_control(stage, rebuilt, frozen):
    state = frozen["state"]
    if rebuilt == Path(state["qualification"]["path"]).parents[1]:
        raise ValueError("the historical Stage 5 root is not a rebuilt input")
    qualification = rebuilt / "qualification/CONTROL.json"
    control = stage.read(qualification)
    build_path = stage.verify(control["build_receipt"])
    build = stage.read(build_path)
    protocol_path = stage.verify(build["protocol"])
    protocol = stage.read(protocol_path)
    if (build_path != rebuilt / "build_receipt.json" or protocol_path != rebuilt / "build_protocol.json"
            or build["status"] != "finished" or build["operation"]["returncode"] != 0
            or protocol["clock_period_ps"] != 40000.0 or protocol["design"] != "sky130hd/riscv32i"
            or control["flow_variant"] != "tc40ns_mmmc_drv"
            or control["top"] != "riscv" or control["status"] != "hold_qualified"
            or control["failures"] or not control["strictly_timing_closed"]
            or control["control_output_paths"] != build["control_output_paths"]):
        raise ValueError("input does not bind a qualified, rebuilt 40 ns Stage 5 reference")
    for item in control["control_output_paths"].values():
        if not stage.verify(item).is_relative_to(rebuilt):
            raise ValueError("rebuilt physical artifact is outside the rebuilt root")
    return control


def replay(stage, rebuilt, output, frozen):
    from verify_review_evidence import check_raw_sta

    control = rebuilt_control(stage, rebuilt, frozen)
    variant = stage.VARIANTS["tc40ns_mmmc_drv"]
    args = stage.candidate_args(rebuilt, control, variant)
    output.mkdir(parents=True)
    stage.cmp.save(output / "replay_protocol.json", {
        "source_lineage": LINEAGE,
        "scope": "one original first fixed dispatch on a rebuilt reference",
        "source": stage.cmp.bind(Path(__file__)),
        "historical_state": stage.cmp.bind(frozen["state_file"]),
        "historical_archive": stage.cmp.bind(frozen["archive_file"]),
        "historical_protocol": frozen["state"]["protocol"],
        "rebuilt_qualification": stage.cmp.bind(args.views_json),
        "actions": frozen["actions"],
        "phase_timeout_s": REPLAY_TIMEOUT_S,
    })
    with (stage.bind_runtime(stage.TOP, stage.ROUTING), stage.qualified.qualified_ranking(),
          stage.qualified.qualified_process_clock()):
        runner = stage.prepare_search(output, args)
        stage.cmp.save(output / "search_protocol.json", runner.config)
        check_policy(runner.config, frozen["protocol"])
        reference = stage.strict_zero(output, runner)
        metrics = ("area", "wns_ns", "tns_ns", "hold_wns_ns")
        if any(not math.isclose(getattr(reference, key), frozen["state"]["reference"][key],
                                rel_tol=0.0, abs_tol=1e-9) for key in metrics):
            raise ValueError("fresh strict zero disagrees with the frozen physical reference")
        runner.output = output / "fixed_first"
        runner.output.mkdir()
        runner.eval.args.out = runner.output
        runner.use_preview = True
        ledger = runner.output / "subprocesses.json"
        with stage.process_ledger(ledger, stage.raw_seconds() + REPLAY_TIMEOUT_S):
            rank = stage.qualified.matrix.sensitivity.score_control(runner, runner.pool,
                                                                  runner.output / "sensitivity")
            if rank["ordered_action_ids"] != frozen["state"]["rank_order"]:
                raise ValueError("fresh TT sensitivity order differs before dispatch")
            actions = sorted(rank["ordered_action_ids"][:runner.batch])
            if actions != frozen["actions"]:
                raise ValueError("fresh fixed first dispatch is not the historical batch")
            endpoint, result = runner.attempt(actions, runner.output / "01")
        if (result["failures"] or not stage.cmp.assess(reference, endpoint, runner.policy).feasible
                or not endpoint.area < reference.area - 1e-9):
            raise ValueError(f"replayed candidate was not accepted: {result['failures']}")
        commit = stage.checked_commit(reference, {"endpoint": asdict(endpoint),
                                                    "elapsed_seconds": result["elapsed_seconds"]},
                                        {"01": {"actions": actions}}, runner.eval)
    physical = stage.read(stage.verify(commit["physical"]))
    drc = stage.read(stage.verify(commit["drc"]))
    log = Path(physical["operations"]["DRT_RCX"]["log"]).read_text(encoding="utf-8")
    if (not physical["routed_to_completion"] or not physical["extracted_to_completion"]
            or physical["drc_violations"] or stage.verify(drc["report"]).read_bytes()
            or re.findall(r"(?m)^AES_SELECTIVE_ANTENNA (\d+)$", log) != ["0"]
            or commit["sec_proven"] != frozen["point"]["sec_proven"]):
        raise ValueError("replayed raw physical checks or SEC size disagree")
    for corner, view in physical["views"].items():
        sta_log = Path(physical["operations"][f"STA_{corner}"]["log"])
        check_raw_sta(sta_log.read_text(encoding="utf-8"), view, f"rebuilt fixed first {corner}")
    old = frozen["physical"]
    artifact_match = {}
    for key, item in physical["artifacts"].items():
        stage.verify(item)
        historic = old["artifacts"].get(key)
        artifact_match[key] = historic is not None and (
            historic["sha256"], historic["bytes"]) == (item["sha256"], item["bytes"])
    stage.cmp.save(output / "replay_receipt.json", {
        "status": "accepted",
        "protocol": stage.cmp.bind(output / "replay_protocol.json"),
        "search_protocol": stage.cmp.bind(output / "search_protocol.json"),
        "strict_zero": stage.cmp.bind(output / "strict_zero.json"),
        "sensitivity": stage.cmp.bind(runner.output / "sensitivity/ranking.json"),
        "tool_ledger": stage.cmp.bind(ledger),
        "accepted_candidate": commit,
        "historical_candidate": frozen["point"],
        "comparison": {
            "ordered_pool_gate_sources_and_tt_rank_match": True,
            "area_matches": math.isclose(commit["area_saved_um2"], frozen["point"]["area_saved_um2"],
                                         rel_tol=0.0, abs_tol=1e-9),
            "timing_and_electrical_match": physical["views"] == old["views"],
            "artifact_byte_matches": artifact_match,
        },
    })
    print(f"Fixed first candidate accepted: {commit['area_saved_um2']:.4f} um2; SEC {commit['sec_proven']}/0",
          flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--rebuilt", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    evidence = args.repo_root.resolve(strict=True) / EVIDENCE_RELATIVE
    frozen = frozen_first(evidence)
    import run_v5_step5_10k_timing_closed as stage

    replay(stage, args.rebuilt.resolve(strict=True), args.output_root.resolve(), frozen)


if __name__ == "__main__":
    main()
