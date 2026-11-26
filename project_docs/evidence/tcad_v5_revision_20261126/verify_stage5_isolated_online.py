#!/usr/bin/env python3
"""Read-only audit of the V5 processor online trace and an isolated replay."""

import argparse
from contextlib import ExitStack
from hashlib import file_digest, sha256
import json
import math
from pathlib import Path, PurePosixPath
import re
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent
OLD_STATE = "V5_STEP5_10K_TIMING_CLOSED_TC40NS_MMMC_DRV_VERIFIED.json"
OLD_SHA = "af4f0fb7fa91ec8ef48f4072938c5774f2a68850765502db8f654c36c3f0c98f"
ARCHIVE_SHA = "eec4d4bdc4911ec42aa31cb874c0fb9a1ebfa4a11508a19573858f9137d3237f"
ONLINE_ARCHIVES = {
    "V5_STAGE5_ISOLATED_ONLINE_COMMON.zip": "8d41ca26aa2e6552ac851546722ffb257db2b79c4b1153c7dbeedb03b2c5e860",
    "V5_STAGE5_ISOLATED_ONLINE_SINGLE_BOXED.zip": "e94b27dcec4501785e0959913578550f504ab2a6e7f74b2ce81f721b8c360d86",
    "V5_STAGE5_ISOLATED_ONLINE_FIXED_BOXED.zip": "87bbd4657cae6226dc0de88eed5f9e5e0d36a8fc179867306abdae34291e0f1d",
    "V5_STAGE5_ISOLATED_ONLINE_FAECO_BOXED.zip": "042e626fb3b2cf49ca022df25860af341ebdd570946ba85c585a66e547bb88b7",
}
OLD_HOME = PurePosixPath("/home/toylog")
OLD_STAGE = OLD_HOME / "faeco_v5_step5_riscv32i_tc40ns_mmmc_drv_20261127_v1"
CORNER_METRICS = {"IBEX_SETUP_PS": "setup_wns_ps", "IBEX_HOLD_PS": "hold_wns_ps",
                  "IBEX_TNS_PS": "setup_tns_ps", "IBEX_HOLD_TNS_PS": "hold_tns_ps"}
PHYSICAL_ARTIFACTS = ("odb", "def", "v", "spef")
POLICY = ("ordered_pool", "gate", "top", "pdk", "batch_size", "route_threads", "affinity",
          "box_halo_rows", "single_pin_access", "absolute_hold_ps", "hold_tolerance_ps",
          "wall_window_seconds_including_screen", "clock", "strategies", "rank_charge_policy")


def require(ok, label):
    if not ok:
        raise ValueError(label)


def bound(read, item):
    content = read(item["path"])
    require(len(content) == item["bytes"] and sha256(content).hexdigest() == item["sha256"], item["path"])
    return content


def read_trial(read, evidence_dir, request, point):
    """Read a completed trial, including rejects, against the progress ledger."""
    target = evidence_dir / f"{request['id']:02d}"
    result = json.loads(read(str(target / "result.json")))
    phys = json.loads(bound(read, result["physical_receipt"]))
    require(result["actions"] == phys["actions"] == request["actions"]
            and result["failures"] == request["failures"]
            and len(result["passes"]) == request["physical_passes"]
            and result["endpoint"] == point["endpoint"]
            and PurePosixPath(result["physical_receipt"]["path"]).parent.parent == target
            and PurePosixPath(result["physical_receipt"]["path"]).parent.name == result["passes"][-1],
            (target, "trial/raw progress disagreement"))
    trial = {"passes": result["passes"], "gate": phys["failures"], "views": phys["views"],
             "routed": phys["routed_to_completion"], "extracted": phys["extracted_to_completion"],
             "drc": phys["drc_violations"], "area": phys["area_saved"], "artifacts": phys["artifacts"]}
    if result["passes"] == ["initial", "retry"]:
        assessment = json.loads(read(str(target / "initial" / "assessment.json")))
        require(PurePosixPath(assessment["physical_receipt"]["path"]) == target / "initial" / "receipt.json",
                (target, "initial pass physical receipt binding"))
        initial = json.loads(bound(read, assessment["physical_receipt"]))
        require(initial["actions"] == request["actions"], (target, "initial pass actions"))
        unlocked = assessment["unlocked"]
        if unlocked is not None:
            bound(read, unlocked["report"])
        trial["initial_retry"] = {
            "failures": assessment["failures"], "pin_access_starts": assessment["pin_access_starts"],
            "views": initial["views"], "physical_drc_markers": initial["drc_violations"],
            "unlocked": None if unlocked is None else [unlocked["drc_markers"], unlocked["marker_types"]],
        }
    return trial


def checks(state, read, *, historical_archive=False, only_arm=None, live_trials=False,
           verify_accept_artifacts=False):
    record = lambda item: json.loads(bound(read, item))
    protocol = record(state["protocol"])
    control = record(state["qualification"])
    require(control["strictly_timing_closed"] and not control["failures"], "reference failed")
    period, budget = protocol["period_basis"]["period_ps"], protocol["gate"]["budget_ps"]
    require(len(protocol["ordered_pool"]) == state["screened_pool_size"] == 18
            and state.get("clock_period_ps", period) == period == 40000
            and state.get("setup_budget_ps", budget) == budget == 400
            and protocol["period_basis"]["absolute_wns_loss_budget_ps"] == budget
            and protocol["wall_window_seconds_including_screen"] == 720, "wrong Stage 5 scope")
    arms = {}
    for label, arm in state["arms"].items():
        if only_arm is not None and label != only_arm:
            continue
        progress, summary, tools = [record(arm[k]) for k in ("progress", "summary", "tool_ledger")]
        requests, points = progress["logical_requests"], progress["checkpoints"]
        start, deadline, charge = progress["start_raw"], progress["deadline_raw"], arm["charged_screening_s"]
        require(charge == protocol["charged_screening_seconds_per_arm"]
                and math.isclose(deadline - start + charge, 720, rel_tol=0, abs_tol=1e-7), (label, "deadline"))
        require(len(requests) == summary["logical_admitted"] == arm["logical_admitted"]
                and len(points) == summary["logical_finished"] == arm["logical_finished"], (label, "counts"))
        require([row["id"] for row in requests] == list(range(1, len(requests) + 1))
                and all(start <= row["admitted_raw"] < deadline for row in requests), (label, "admission"))
        require(progress["stop_reason"] == summary["stop_reason"] and
                (len(requests) == len(points) or len(requests) == len(points) + 1), (label, "stop"))
        for row in tools:
            require(start <= row["start_raw"] < deadline
                    and math.isclose(row["effective_timeout_seconds"],
                                     min(deadline - row["start_raw"], row["configured_timeout_seconds"]),
                                     rel_tol=0, abs_tol=1e-7), (label, "tool deadline"))
        accepted, seen, integral, last_t, gain = {}, iter(arm["accepted_checkpoints"]), 0.0, 0.0, 0.0
        sec_logs, trials = 0, {}
        for index, (request, point) in enumerate(zip(requests, points), start=1):
            require(request["admitted_raw"] <= request["finished_raw"] < deadline
                    and math.isclose(point["elapsed_seconds"], charge + request["finished_raw"] - start,
                                     rel_tol=0, abs_tol=1e-7), (label, index, "completion"))
            if live_trials:
                evidence_dir = PurePosixPath(arm["progress"]["path"]).parent
                trials[index] = read_trial(read, evidence_dir, request, point)
            if not point["accepted"]:
                continue
            item = next(seen)
            result, phys, drc, sec = [record(item[k]) for k in ("receipt", "physical", "drc", "sec")]
            require(request["actions"] == item["actions"] == result["actions"] == phys["actions"]
                    and item["physical"] == result["physical_receipt"] and not result["failures"]
                    and point["endpoint"] == result["endpoint"], (label, index, "acceptance binding"))
            require(phys["routed_to_completion"] and phys["extracted_to_completion"]
                    and phys["drc_violations"] == drc["drc_markers"] == 0 and not bound(read, drc["report"])
                    and re.findall(rb"(?m)^AES_SELECTIVE_ANTENNA (\d+)$",
                                   read(phys["operations"]["DRT_RCX"]["log"])) == [b"0"],
                    (label, index, "physical gate"))
            require(sec["passed"] and sec["proven"] == 4559 and sec["unproven"] == 0
                    and sec["gold"] == control["control_output_paths"]["v"] and sec["gate"] == phys["artifacts"]["v"],
                    (label, index, "SEC binding"))
            try:
                proof = bound(read, sec["log"])
            except KeyError:
                if not historical_archive:
                    raise
            else:
                require(b"4559 are proven and 0 are unproven" in proof, (label, index, "SEC log"))
                sec_logs += 1
            for corner, timing in phys["views"].items():
                raw = read(phys["operations"][f"STA_{corner}"]["log"]).decode()
                require("IBEX_STA_COMPLETE" in raw and all(
                    [float(x) for x in re.findall(rf"(?m)^{marker} (\S+)\s*$", raw)] == [timing[key]]
                    for marker, key in CORNER_METRICS.items()), (label, index, corner, "raw STA"))
                require(not any(timing["electrical"].values())
                        and timing["setup_wns_ps"] >= protocol["gate"]["setup_floor_ps_by_view"][corner] - 0.001
                        and timing["setup_tns_ps"] == timing["hold_tns_ps"] == 0
                        and timing["hold_wns_ps"] >= control["views"][corner]["hold_wns_ps"] - 0.001,
                        (label, index, corner, "timing gate"))
            t, value = item["elapsed_s"], item["area_saved_um2"]
            require(last_t <= t == point["elapsed_seconds"] <= 720 and value > gain, (label, index, "AUC"))
            integral += (t - last_t) * gain
            last_t, gain = t, value
            if verify_accept_artifacts:
                for key in PHYSICAL_ARTIFACTS:
                    bound(read, phys["artifacts"][key])
            accepted[index] = {"area": value, "timing": phys["views"],
                               "physical": {k: phys["artifacts"][k]["sha256"] for k in PHYSICAL_ARTIFACTS}}
        require(next(seen, None) is None and gain == arm["qualified_area_saved_um2"], (label, "terminal"))
        auc = (integral + (720 - last_t) * gain) / 720
        require(math.isclose(auc, arm["anytime_auc_um2"], rel_tol=0, abs_tol=1e-9), (label, "AUC accounting"))
        if len(requests) > len(points):
            require(progress["stop_reason"] == "end_to_end_wall_cap", (label, "unfinished request"))
        arms[label] = {"requests": requests, "completed": len(points), "accepted": accepted, "raw_trials": trials,
                       "stop": progress["stop_reason"], "area": gain, "auc": auc, "raw_sec_logs": sec_logs,
                       "raw_accepted_physical_count": len(accepted) * len(PHYSICAL_ARTIFACTS)
                       if verify_accept_artifacts else 0,
                       "last_tool": [PurePosixPath(tools[-1]["log"]).name, tools[-1]["timeout_bound"],
                                     tools[-1]["returncode"], tools[-1]["effective_timeout_seconds"]]}
    return protocol, arms


def spef_without_date(read, item):
    raw = bound(read, item)
    normalized, count = re.subn(rb"(?m)^\*DATE .*", b"*DATE", raw)
    require(count == 1, ("expected one SPEF DATE line", item["path"]))
    return sha256(normalized).hexdigest()


def compare_trial_physical(old, new, read_old, read_new):
    """Compare rejected and accepted raw physical receipts without path noise."""
    left, right = old["artifacts"], new["artifacts"]
    keys = sorted(left.keys() | right.keys())
    artifacts = {key: key in left and key in right and left[key]["sha256"] == right[key]["sha256"]
                 and left[key]["bytes"] == right[key]["bytes"] for key in keys}
    normalized = None
    if "spef" in left and "spef" in right:
        normalized = artifacts["spef"] or (
            spef_without_date(read_old, left["spef"]) == spef_without_date(read_new, right["spef"])
        )
    comparison = {"gate_metrics_and_passes_equal": all(old[k] == new[k] for k in old if k not in (
        "artifacts", "initial_retry")), "bound_byte_hashes_equal": artifacts, "spef_normalized_equal": normalized}
    if "initial_retry" in old or "initial_retry" in new:
        comparison["retry_initial_gate_and_views_equal"] = old.get("initial_retry") == new.get("initial_retry")
    return comparison


def compare(old, new, read_old, read_new):
    old_rows, new_rows = old["requests"], new["requests"]
    action_prefix, same = 0, []
    for i, (left, right) in enumerate(zip(old_rows, new_rows), start=1):
        if left["actions"] != right["actions"]:
            break
        action_prefix = i
        if i > min(old["completed"], new["completed"]):
            break
        earlier, fresh = old["accepted"].get(i), new["accepted"].get(i)
        status = {"id": i, "gate_and_retry_equal": (left["failures"], left["physical_passes"])
                  == (right["failures"], right["physical_passes"]),
                  "accepted_equal": (earlier is None) == (fresh is None)}
        if earlier is not None and fresh is not None:
            status.update({"timing_equal": earlier["timing"] == fresh["timing"],
                           "area_equal": earlier["area"] == fresh["area"],
                           "physical_bytes_equal": {key: earlier["physical"][key] == fresh["physical"][key]
                                                    for key in earlier["physical"]}})
        if i in old["raw_trials"] and i in new["raw_trials"]:
            status["raw_trial"] = compare_trial_physical(
                old["raw_trials"][i], new["raw_trials"][i], read_old, read_new,
            )
        same.append(status)
    return {"matched_action_prefix": action_prefix, "completed_overlap": same,
            "historical_tail": [len(old_rows), old["completed"], old["stop"], old["last_tool"]],
            "fresh_tail": [len(new_rows), new["completed"], new["stop"], new["last_tool"]],
            "historical_area_auc": [old["area"], old["auc"]],
            "fresh_area_auc": [new["area"], new["auc"]],
            "fresh_accepted_physical_members_verified": new["raw_accepted_physical_count"]}


def verify_single_cutoff(capture, old_state, new_state, old_arm, new_arm, old_read, new_read):
    """Verify the physical trial whose proof wrapper ran out of the single arm's wall budget."""
    require(old_arm["completed"] >= 8 and new_arm["completed"] == 7
            and len(new_arm["requests"]) == 8 and 8 in old_arm["accepted"]
            and old_arm["requests"][7]["actions"] == new_arm["requests"][7]["actions"],
            "single #8 cutoff request mismatch")
    old, new = capture["historical"], capture["replay"]
    normalized = {}
    proof_marker = b"4559 are proven and 0 are unproven"
    proof_found = {}
    for name, item, state, read in (("historical", old, old_state, old_read),
                                    ("replay", new, new_state, new_read)):
        arm = state["arms"]["single_boxed"]
        candidate = PurePosixPath(arm["progress"]["path"]).parent / "08" / "initial"
        files = [*item["artifacts"].values(), item["drc"], item["script"], item["log"], item["wrapper_log"]]
        require(all(PurePosixPath(file["path"]).is_relative_to(candidate) for file in files),
                (name, "cutoff candidate binding"))
        normalized[name] = spef_without_date(read, item["artifacts"]["spef"])
        require(normalized[name] == item["spef_without_date_sha256"], (name, "cutoff SPEF digest"))
        require(set(item["timing"]) == {"FF", "TT", "SS"}, (name, "cutoff MMMC views"))
        for corner, view in item["timing"].items():
            require(PurePosixPath(view["file"]["path"]) == candidate / f"sta_{corner}.log",
                    (name, corner, "cutoff STA log path"))
            log = bound(read, view["file"])
            metrics = re.findall(rb"(?m)^IBEX_(?:SETUP_PS|HOLD_PS|TNS_PS|HOLD_TNS_PS) [^\r\n]+", log)
            require([line.decode() for line in metrics] == view["metrics"] and b"IBEX_STA_COMPLETE" in log,
                    (name, corner, "cutoff STA metrics"))
        require(not bound(read, item["drc"]), (name, "cutoff direct DRC"))
        bound(read, item["script"])
        bound(read, item["wrapper_log"])
        proof_found[name] = proof_marker in bound(read, item["log"])
        receipt = str(candidate / "sec" / "receipt.json")
        try:
            raw_receipt = read(receipt)
        except (FileNotFoundError, KeyError):
            require(not item["receipt"] and name == "replay", (name, "cutoff SEC receipt missing"))
        else:
            posted = json.loads(raw_receipt)
            require(item["receipt"] and name == "historical" and posted["passed"]
                    and all(item["log"][key] == value for key, value in posted["log"].items()),
                    (name, "cutoff SEC receipt"))
    for key in PHYSICAL_ARTIFACTS:
        require(old["artifacts"][key]["sha256"] == old_arm["accepted"][8]["physical"][key],
                (key, "historical cutoff artifact differs from accepted #8"))
        if key != "spef":
            bound(new_read, new["artifacts"][key])
            require(old["artifacts"][key]["sha256"] == new["artifacts"][key]["sha256"]
                    and old["artifacts"][key]["bytes"] == new["artifacts"][key]["bytes"],
                    (key, "cutoff physical artifact differs"))
    require(normalized["historical"] == normalized["replay"]
            and all(old["timing"][key]["metrics"] == new["timing"][key]["metrics"] for key in old["timing"])
            and all(proof_found.values()), "cutoff SPEF, timing or proof-log difference")
    single = json.loads(bound(new_read, new_state["arms"]["single_boxed"]["tool_ledger"]))[-1]
    require(single == capture["single_last_tool"] and single["log"] == new["wrapper_log"]["path"]
            and single["timeout_bound"] == "wall" and single["returncode"] is None,
            "cutoff proof wrapper ledger")
    fixed = json.loads(bound(new_read, new_state["arms"]["fixed_boxed"]["tool_ledger"]))[0]
    require(fixed == capture["fixed_first_tool"] and fixed["log"] == capture["fixed_rank_log"]["path"]
            and fixed["start_raw"] > single["stop_raw"] and fixed["returncode"] == 0,
            "following rank ledger")
    bound(new_read, capture["fixed_rank_log"])
    return {"fresh_physical_members_verified": len(PHYSICAL_ARTIFACTS),
            "spef_without_date_sha256": normalized["replay"], "three_sta_corners_equal": True,
            "direct_drc_markers": 0, "proof_marker_present_in_both_raw_logs": True,
            "fresh_wrapper_returncode": single["returncode"], "fresh_sec_receipt_present": False,
            "fresh_checkpoint_accepted": False,
            "captured_fresh_proof_log_mtime_minus_fixed_rank_log_mtime_s":
                (new["log"]["mtime_ns"] - capture["fixed_rank_log"]["mtime_ns"]) / 1_000_000_000}


def indexed_bundle(stack, path):
    expected = ONLINE_ARCHIVES.get(path.name)
    if expected is not None:
        with path.open("rb") as stream:
            require(file_digest(stream, "sha256").hexdigest() == expected, (path, "published archive bytes changed"))
    zipped = stack.enter_context(ZipFile(path))
    names = zipped.namelist()
    index = json.loads(zipped.read("ORIGINALS.json"))
    require(len(names) == len(set(names)) == len(index) + 1
            and set(names) == set(index) | {"ORIGINALS.json"}, (path, "member index mismatch"))
    return zipped, index


def indexed_member(bundles, member):
    matches = []
    for zipped, index in bundles:
        if member in index:
            payload, item = zipped.read(member), index[member]
            require(len(payload) == item["bytes"] and sha256(payload).hexdigest() == item["sha256"],
                    (member, "ZIP digest mismatch"))
            matches.append(payload)
    if not matches:
        raise KeyError(member)
    require(all(data == matches[0] for data in matches[1:]), (member, "conflicting copies in bundles"))
    return matches[0]


def mapped_member(path, maps, bundles):
    absolute = PurePosixPath(path)
    matches = []
    for root, member_prefix in maps:
        if absolute.is_relative_to(root):
            member = (member_prefix / absolute.relative_to(root)).as_posix()
            try:
                matches.append(indexed_member(bundles, member))
            except KeyError:
                continue
    if not matches:
        raise KeyError(path)
    require(all(data == matches[0] for data in matches[1:]), (path, "conflicting copies in bundles"))
    return matches[0]


def parse_map(text):
    root, delimiter, prefix = text.partition("=")
    root, prefix = PurePosixPath(root), PurePosixPath(prefix)
    if not delimiter or not root.is_absolute() or prefix.is_absolute() or ".." in prefix.parts:
        raise argparse.ArgumentTypeError("expected /absolute/runtime/root=relative/archive/prefix")
    return root, prefix


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=ROOT)
    parser.add_argument("--new-state", help="live file or original absolute Linux path in replay ZIPs")
    parser.add_argument("--arm", choices=("single_boxed", "fixed_boxed", "faeco_boxed"))
    parser.add_argument("--historical-live", action="store_true",
                        help="also read original host reject receipts, raw logs and matching SPEFs")
    parser.add_argument("--historical-zip", type=Path, action="append", default=[])
    parser.add_argument("--replay-zip", type=Path, action="append", default=[])
    parser.add_argument("--replay-map", type=parse_map, action="append", default=[],
                        help="map /absolute/runtime/root=relative/member/prefix in replay ZIPs")
    parser.add_argument("--single-cutoff", type=Path,
                        help="read the live single #8 cutoff capture; replay archives provide it internally")
    args = parser.parse_args()
    historical = (args.evidence / OLD_STATE).read_bytes()
    archive = args.evidence / "V5_REVIEW_ORIGINALS.zip"
    require(sha256(historical).hexdigest() == OLD_SHA and sha256(archive.read_bytes()).hexdigest() == ARCHIVE_SHA,
            "published artifacts changed")
    state = json.loads(historical)
    with ExitStack() as stack:
        zipped = stack.enter_context(ZipFile(archive))
        history_bundles = [indexed_bundle(stack, path) for path in args.historical_zip]
        history_full = args.historical_live or bool(history_bundles)
        history_map = [(OLD_STAGE, PurePosixPath("historical"))]

        def old_read(path):
            try:
                return zipped.read(PurePosixPath(path).relative_to(OLD_HOME).as_posix())
            except KeyError:
                if history_bundles:
                    try:
                        return mapped_member(path, history_map, history_bundles)
                    except KeyError:
                        pass
                if not args.historical_live:
                    raise
                return Path(path).read_bytes()
        policy, old = checks(state, old_read, historical_archive=not history_full,
                             only_arm=args.arm, live_trials=history_full)
        if args.new_state is None:
            print(json.dumps({key: {k: v for k, v in row.items() if k not in ("requests", "accepted", "raw_trials")}
                              | {"accepted_ids": list(row["accepted"])} for key, row in old.items()}, indent=2))
            return
        runtime_state = PurePosixPath(args.new_state)
        if args.replay_zip and not runtime_state.is_absolute():
            parser.error("--new-state is the original absolute runtime path when reading replay ZIPs")
        replay_bundles = [indexed_bundle(stack, path) for path in args.replay_zip]
        replay_maps = [(runtime_state.parent, PurePosixPath("replay")), *args.replay_map]

        def new_read(path):
            if replay_bundles:
                return mapped_member(path, replay_maps, replay_bundles)
            return Path(path).read_bytes()
        fresh = json.loads(new_read(args.new_state))
        new_policy, new = checks(fresh, new_read, only_arm=args.arm, live_trials=history_full,
                                 verify_accept_artifacts=True)
        source_fprints = lambda shape: {key: (item["bytes"], item["sha256"]) for key, item in shape["sources"].items()}
        require(bool(new), "no completed fresh arm matching --arm")
        require(all(policy[key] == new_policy[key] for key in POLICY) and state["rank_order"] == fresh["rank_order"]
                and source_fprints(policy) == source_fprints(new_policy),
                "policy, pool or rank differs from original")
        comparison = {key: compare(old[key], row, old_read, new_read) for key, row in new.items()}
        if "single_boxed" in new and (args.single_cutoff or replay_bundles):
            raw_capture = (args.single_cutoff.read_bytes() if args.single_cutoff else
                           indexed_member(replay_bundles, "launcher/single_08_cutoff.json"))
            comparison["single_boxed"]["eighth_request_cutoff"] = verify_single_cutoff(
                json.loads(raw_capture), state, fresh, old["single_boxed"], new["single_boxed"], old_read, new_read,
            )
        print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
