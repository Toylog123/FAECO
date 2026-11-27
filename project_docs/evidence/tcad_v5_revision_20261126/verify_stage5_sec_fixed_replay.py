#!/usr/bin/env python3
"""Compare the three 40 ns Stage 5 arms before and after the SEC process-group fix."""

import argparse
from collections import Counter
from contextlib import ExitStack
from hashlib import file_digest, sha256
import json
import math
from pathlib import Path, PurePosixPath
import re
from types import ModuleType


V1_ROOT = PurePosixPath("/var/tmp/faeco_v6_stage5_online_20261127_v1")
V2_ROOT = PurePosixPath("/var/tmp/faeco_v6_stage5_online_sec_fixed_20261127_v1")
QUALIFICATION = PurePosixPath("/var/tmp/faeco_v6_stage5_rebuilt_20261127_v2/qualification")
V1_TOOLS = PurePosixPath("/var/tmp/faeco_v6_stage5_online_tools_20261127")
V2_TOOLS = PurePosixPath("/var/tmp/faeco_v6_stage5_sec_fixed_tools_20261127")
V1_INPUTS = Path("/var/tmp/faeco_v6_stage5_input_20261127_v4")
V2_INPUTS = Path("/var/tmp/faeco_v6_stage5_input_20261127_sec_fixed_v1")
ARMS = ("single_boxed", "fixed_boxed", "faeco_boxed")
CUTOFF_ARCHIVE_SHA = "60a6583339f527ccf444d53ee4a0be745da02d5a35d5dd867852f8729e4ff4ed"
FIXED_ARCHIVES = {
    "V5_STAGE5_SEC_FIXED_COMMON.zip": "665d7fffa00fa2b5a858aff5e1da2a4da29f7180e600799c3c29a589b72120db",
    "V5_STAGE5_SEC_FIXED_SINGLE_BOXED.zip": "91af7083b475f2dea8e6e8f201102bfbf7c974130471b66a1cec3d95f19395a6",
    "V5_STAGE5_SEC_FIXED_FIXED_BOXED.zip": "e66ece78348ed9cdd16a9fd89f724173243a07fc3955a664eb4da3e959fb90f2",
    "V5_STAGE5_SEC_FIXED_FAECO_BOXED.zip": "5f6a0e1a54c61ff622e861f0ec3e4fef966f172bf1068dc3ada8290508b4d852",
}
VERIFIER_SHA = "4d1d711db8c7a923ac7799e8222f82bd9862882f6e6dbb8774bbb9596f54c606"
PROVE = "prove_ibex.py"
PROVE_PATH = f"project/project_docs/evidence/tcad_ibex_20261123/{PROVE}"
LAUNCH_CORE = ("replay_stage5_online.py", "replay_stage5_fixed_first.py")
STATE = "stage5_progress.json"
ALIASES = "replay/PHYSICAL_ALIASES.json"
CELL = re.compile(rb"(?m)^\s*(sky130_fd_sc_hd__\w+)[ \t]+(\\?\S+)[ \t]+\(")
PROOF = b"4559 are proven and 0 are unproven"


def published_verifier(evidence):
    path = evidence / "verify_stage5_isolated_online.py"
    source = path.read_bytes().replace(b"\r\n", b"\n")
    if sha256(source).hexdigest() != VERIFIER_SHA:
        raise ValueError("published Stage 5 verifier digest changed")
    audit = ModuleType("published_stage5_audit")
    audit.__file__ = str(path)
    exec(compile(source, str(path), "exec"), vars(audit))
    return audit


def pinned_bundle(audit, stack, path, expected):
    with path.open("rb") as stream:
        audit.require(file_digest(stream, "sha256").hexdigest() == expected, (path, "ZIP digest"))
    return audit.indexed_bundle(stack, path)


def runtime_reader(audit, root, bundles):
    mappings = [(root, PurePosixPath("replay")), (QUALIFICATION, PurePosixPath("reference")),
                (V1_TOOLS, PurePosixPath("launcher")), (V2_TOOLS, PurePosixPath("launcher"))]
    if bundles:
        return lambda path: audit.mapped_member(path, mappings, bundles)
    return lambda path: Path(path).read_bytes()


def fixed_reader(audit, root, bundles, old_bundles):
    read = runtime_reader(audit, root, bundles)
    if not bundles:
        return read
    try:
        aliases = json.loads(audit.indexed_member(bundles, ALIASES))
    except KeyError:
        aliases = {}
    for path, item in aliases.items():
        runtime = PurePosixPath(path)
        member = PurePosixPath(item["member"])
        audit.require(runtime.is_relative_to(root) and ".." not in runtime.parts
                      and runtime.suffix in (".odb", ".def", ".v") and runtime.suffix == member.suffix,
                      (path, "physical alias scope"))
        audit.require(item["archive"] in old_bundles, (path, "physical alias must refer to a pinned old ZIP"))
        _, index = old_bundles[item["archive"]]
        audit.require(item["member"] in index and fingerprint(item) == fingerprint(index[item["member"]]),
                      (path, "physical alias does not match old member index"))
        own_member = (PurePosixPath("replay") / runtime.relative_to(root)).as_posix()
        audit.require(all(own_member not in index for _, index in bundles), (path, "duplicate raw physical member"))

    def read_aliased(path):
        if path in aliases:
            item = aliases[path]
            return audit.indexed_member([old_bundles[item["archive"]]], item["member"])
        try:
            return read(path)
        except KeyError:
            name = PurePosixPath(path)
            if name.parent == V2_TOOLS and name.name in LAUNCH_CORE:
                return audit.indexed_member(old_bundles.values(), f"launcher/{name.name}")
            raise

    return read_aliased


def live_extra_member(member):
    paths = {
        "inputs/original_FILES.sha256": V1_INPUTS / "FILES.sha256",
        "inputs/fixed_FILES.sha256": V2_INPUTS / "FILES.sha256",
        f"inputs/original_{PROVE}": V1_INPUTS / PROVE_PATH,
        f"inputs/fixed_{PROVE}": V2_INPUTS / PROVE_PATH,
    }
    return paths.get(member, Path(str(V2_TOOLS / PurePosixPath(member).name))).read_bytes()


def bound_json(audit, read, item):
    return json.loads(audit.bound(read, item))


def fingerprint(binding):
    return {key: binding[key] for key in ("bytes", "sha256")}


def source_delta(audit, old_protocol, new_protocol, cutoff_bundle):
    old, new = (protocol["sources"] for protocol in (old_protocol, new_protocol))
    audit.require(old.keys() == new.keys(), "Stage 5 runtime source inventory differs")
    changes = [key for key in old if fingerprint(old[key]) != fingerprint(new[key])]
    audit.require(changes == [PROVE] and old[PROVE]["path"] == new[PROVE]["path"],
                  ("unexpected Stage 5 runtime source delta", changes))
    for label, binding in (("original", old[PROVE]), ("fixed", new[PROVE])):
        raw = audit.indexed_member([cutoff_bundle], f"source/{label}_prove_ibex.py")
        audit.require(fingerprint(binding) == {"bytes": len(raw), "sha256": sha256(raw).hexdigest()},
                      (label, "prover source does not match cutoff fixture"))
    return {"unchanged_runtime_source_bindings": len(old) - 1,
            "changed_runtime_source": PROVE, "old": fingerprint(old[PROVE]), "new": fingerprint(new[PROVE])}


def capsule_evidence(audit, member, delta, launch):
    manifests = []
    manifest_digests = {}
    for tag, version in (("original", "old"), ("fixed", "new")):
        raw = member(f"inputs/{tag}_FILES.sha256")
        manifest_digests[tag] = sha256(raw).hexdigest()
        entries = re.findall(rb"(?m)^([a-f0-9]{64})  (.+)$", raw)
        manifest = {name.decode(): digest.decode() for digest, name in entries}
        audit.require(len(entries) == len(manifest) == len(raw.splitlines()) == 25656,
                      (tag, "capsule digest inventory"))
        source = member(f"inputs/{tag}_{PROVE}")
        audit.require(fingerprint(delta[version]) == {"sha256": sha256(source).hexdigest(), "bytes": len(source)}
                      and manifest[PROVE_PATH] == delta[version]["sha256"], (tag, "prover/capsule binding"))
        manifests.append(manifest)
    old, new = manifests
    audit.require(old.keys() == new.keys() and [name for name in old if old[name] != new[name]] == [PROVE_PATH],
                  "capsule inventories differ beyond the prover")
    live = json.loads(member("launcher/namespace_live.json"))
    mounts = live["readonly_mounts"]
    audit.require(live["worker_pid"] == launch["pid"] and live["worker_namespace"] == launch["namespace"]
                  and live["worker_affinity"] == launch["affinity"] and live["old_root_hidden"] is True
                  and live["proof_sha256"] == delta["new"]["sha256"]
                  and set(mounts) == {"/home/toylog", "/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO", "/usr/local/bin"}
                  and all("ro" in line.split(" - ", 1)[0].split()[5].split(",") for line in mounts.values())
                  and all(live["observer_namespace"][kind] != launch["namespace"][kind]
                          for kind in ("user", "mnt", "net")), "process namespace/source observation mismatch")
    outer = member("launcher/replay_stage5_sec_fixed.py")
    negative = member("launcher/unpatched_rejection.log")
    audit.require(all(delta[version]["sha256"].encode() in outer for version in ("old", "new"))
                  and b"ValueError: expected the fixed prover at the frozen prover's original path" in negative,
                  "fixed launcher source/negative control evidence")
    return {"source_inventory_files": len(old), "sole_changed_input": PROVE_PATH,
            "manifest_sha256": manifest_digests, "fixed_launcher_sha256": sha256(outer).hexdigest(),
            "private_readonly_input_mounts": sorted(mounts), "old_live_root_hidden": True}


def prover_role(row):
    argv = row["argv"]
    if not argv:
        return None
    if argv[0] == "/usr/bin/timeout" and argv[-1].endswith("/sec/prove.ys"):
        return str(PurePosixPath(argv[-1]).parent), "timeout"
    if len(argv) > 1 and argv[1].endswith("/sec_native.py"):
        return argv[-1], "wrapper"
    if argv[-1].endswith("/sec/prove.ys") and any(arg.endswith("/libexec/yosys") for arg in argv):
        return str(PurePosixPath(argv[-1]).parent), "yosys"
    return None


def observer_evidence(audit, raw, launch, *, only_arm=None):
    events = [json.loads(line) for line in raw.splitlines()]
    start, finish = events[0], events[-1]
    audit.require(start["event"] == "observer_start" and start["worker"] == launch["pid"]
                  and start["namespace"] == launch["namespace"]["mnt"]
                  and all(left["raw_s"] <= right["raw_s"] for left, right in zip(events, events[1:])),
                  "process observer identity or chronology")
    phase = [event for event in events if event["event"] == "phase"]
    observed_arms = [event["arm"] for event in phase if event["arm"] is not None]
    if only_arm is None:
        audit.require(finish["event"] == "observer_finished" and finish["status"] == "finished"
                      and observed_arms == list(ARMS) and phase[-1]["completed"] == list(ARMS),
                      "process observer did not cover the completed replay")
    else:
        audit.require(only_arm in observed_arms and only_arm in phase[-1]["completed"],
                      (only_arm, "process observer has not sampled the arm transition"))
    active = {}
    overlapping, proof_groups = [], {}
    for event in events:
        if event["event"] == "phase":
            active = {(row["pid"], row["start_ticks"]): row for row in event["processes"]}
        elif event["event"] == "process_change":
            for row in event["ended"]:
                active.pop((row["pid"], row["start_ticks"]), None)
            for row in event["started"]:
                active[(row["pid"], row["start_ticks"])] = row
        else:
            continue
        tool_arms = {arm for row in active.values() for arm in row["arms"]}
        if len(tool_arms) > 1:
            overlapping.append({"raw_s": event["raw_s"], "arms": sorted(tool_arms)})
        for row in active.values():
            prover = prover_role(row)
            if prover is None:
                continue
            key, role = prover
            if role == "timeout":
                audit.require("--foreground" in row["argv"], (key, "observer found legacy timeout"))
            proof_groups.setdefault(key, {}).setdefault(role, set()).add((row["sid"], row["pgid"]))
    complete = {key: roles for key, roles in proof_groups.items() if len(roles) == 3}
    audit.require(bool(complete), "observer did not sample a complete prover process group")
    different = sum(len(set().union(*roles.values())) != 1 for roles in complete.values())
    proof_stages = Counter()
    for key in complete:
        parts = PurePosixPath(key).parts
        stage = next((part for part in parts if part in ARMS), "preflight")
        proof_stages[stage] += 1
    return {"samples": finish.get("samples"), "requested_interval_s": start["interval_s"],
            "max_sample_gap_s": finish.get("max_gap_s"), "sampled_proving_process_triples": len(complete),
            "sampled_proving_process_triples_by_stage": dict(proof_stages),
            "sampled_proving_process_triples_in_distinct_groups": different,
            "simultaneously_active_arms_observations": overlapping,
            "observed_through_raw_s": finish["raw_s"], "observed_arm_phases": observed_arms,
            "processes_at_observer_finish": finish["processes"] if finish["event"] == "observer_finished" else None}


def single_cutoff_cleanup(audit, raw, read, state):
    single = state["arms"]["single_boxed"]
    wrapper = bound_json(audit, read, single["tool_ledger"])[-1]
    log = PurePosixPath(wrapper["log"])
    if log.name != "sec.log" or wrapper["returncode"] is not None or wrapper["timeout_bound"] != "wall":
        return None
    directory = str(log.parent / "sec")
    ends = {}
    for line in raw.splitlines():
        event = json.loads(line)
        for row in event.get("ended", ()):
            candidate = prover_role(row)
            if candidate is None or candidate[0] != directory:
                continue
            ends[candidate[1]] = {key: row[key] for key in ("pid", "sid", "pgid")}
            ends[candidate[1]]["observed_gone_raw_s"] = event["raw_s"]
    audit.require(set(ends) == {"wrapper", "timeout", "yosys"}, "single cutoff lacks three observed process exits")
    all_gone = max(row["observed_gone_raw_s"] for row in ends.values())
    deadline = bound_json(audit, read, single["progress"])["deadline_raw"]
    fixed = state["arms"].get("fixed_boxed")
    following = None
    if fixed is not None:
        following = bound_json(audit, read, fixed["tool_ledger"])[0]
    elif (state.get("active_arm") or {}).get("name") == "fixed_boxed":
        record = maybe_read(read, PurePosixPath(state["active_arm"]["path"]) / "fixed" / "subprocesses.json")
        if record:
            rows = json.loads(record)
            following = rows[0] if rows else None
    return {"candidate_sec_directory": directory, "observed_process_exits": ends,
            "time_after_deadline_s": all_gone - deadline, "time_after_wrapper_stop_s": all_gone - wrapper["stop_raw"],
            "observed_before_next_rank_start_s": following["start_raw"] - all_gone if following else None}


def sec_command(audit, read, sec, *, foreground):
    expected = ["/usr/bin/timeout", "--kill-after=10s", "180s", "/usr/local/bin/yosys", "-Q", "-s",
                sec["script"]["path"]]
    if foreground:
        expected.insert(1, "--foreground")
    audit.require(sec["command"] == expected, (sec["script"]["path"], "SEC command does not match version"))
    audit.bound(read, sec["script"])


def strict_zero(audit, read, state, *, foreground):
    preflight = bound_json(audit, read, state["strict_zero"])
    reference = state["reference"]
    result = bound_json(audit, read, preflight["record"])
    physical, sec, drc = [bound_json(audit, read, preflight["raw"][name]) for name in ("physical", "sec", "audit")]
    control = bound_json(audit, read, state["qualification"])
    audit.require(result["endpoint"] == reference and reference["valid"] and reference["sec_pass"]
                  and preflight["scope"] == reference["scope_id"]
                  and not result["actions"] and not result["failures"]
                  and result["physical_receipt"] == preflight["raw"]["physical"]
                  and not physical["actions"] and physical["failures"] == ["no_area_gain"]
                  and sec["gate"] == physical["artifacts"]["v"] and sec["passed"]
                  and sec["gold"] == control["control_output_paths"]["v"]
                  and fingerprint(sec["gold"]) == fingerprint(sec["gate"])
                  and sec["proven"] == 4559 and sec["unproven"] == 0
                  and PROOF in audit.bound(read, sec["log"])
                  and drc["drc_markers"] == 0 and not audit.bound(read, drc["report"]),
                  "strict-zero endpoint / proof / DRC binding")
    sec_command(audit, read, sec, foreground=foreground)


def accepted_path(audit, read, state, label, arm, protocol, *, foreground):
    """Bind each committed endpoint to its ordered request and realized substitutions."""
    accepted = []
    previous_id, previous_actions = None, set()
    pool = {item["action_id"]: item for item in protocol["ordered_pool"]}
    for committed, (request_id, accepted_record) in zip(state["arms"][label]["accepted_checkpoints"],
                                                        arm["accepted"].items(), strict=True):
        request = arm["requests"][request_id - 1]
        actions = request["actions"]
        audit.require(len(actions) == len(set(actions)) and all(action in pool for action in actions)
                      and actions == committed["actions"] and len(actions) == committed["gates"],
                      (label, request_id, "accepted action inventory"))
        trial = bound_json(audit, read, committed["physical"])
        result = bound_json(audit, read, committed["receipt"])
        endpoint = result["endpoint"]
        reference = state["reference"]
        audit.require(endpoint["valid"] and endpoint["sec_pass"] and endpoint["scope_id"] == reference["scope_id"]
                      and math.isclose(reference["area"] - endpoint["area"], committed["area_saved_um2"],
                                       rel_tol=0, abs_tol=1e-9), (label, request_id, "accepted scope or area"))
        physical = trial["artifacts"]
        netlist = audit.bound(read, physical["v"])
        mapped_cells = {instance.lstrip(b"\\").decode(): cell.decode() for cell, instance in CELL.findall(netlist)}
        audit.require(all(mapped_cells.get(pool[action]["instance"]) == pool[action]["target_cell"]
                          for action in actions), (label, request_id, "accepted substitution missing from netlist"))
        sec = bound_json(audit, read, committed["sec"])
        sec_command(audit, read, sec, foreground=foreground)
        earlier = arm["requests"][(previous_id or 0):request_id - 1]
        accepted.append({"request_id": request_id, "previous_accepted_request_id": previous_id,
                         "intervening_rejected_requests": [{key: row[key] for key in ("id", "actions", "failures")}
                                                           for row in earlier],
                         "actions": actions, "retained_actions": sorted(previous_actions & set(actions)),
                         "added_actions": sorted(set(actions) - previous_actions),
                         "removed_actions": sorted(previous_actions - set(actions)),
                         "area_saved_um2": accepted_record["area"], "elapsed_s": committed["elapsed_s"],
                         "sec_foreground": foreground})
        previous_id, previous_actions = request_id, set(actions)
    return accepted


def maybe_read(read, path):
    try:
        return read(str(path))
    except (FileNotFoundError, KeyError):
        return None


def end_of_arm(audit, read, state, label, arm):
    item = state["arms"][label]
    progress = bound_json(audit, read, item["progress"])
    tools = bound_json(audit, read, item["tool_ledger"])
    deadline = progress["deadline_raw"]
    pending = arm["requests"][arm["completed"]:]
    audit.require(all("finished_raw" not in request for request in pending), (label, "unfinished commit recorded"))
    timeout_rows = []
    for row in tools:
        audit.require(row["stop_raw"] >= row["start_raw"], (label, "tool time order"))
        if row["returncode"] is not None:
            continue
        log = PurePosixPath(row["log"])
        kind = row["timeout_bound"]
        audit.require(kind in ("stage", "wall"), (label, "unclassified timeout"))
        if kind == "wall":
            audit.require(math.isclose(row["effective_timeout_seconds"], deadline - row["start_raw"],
                                       rel_tol=0, abs_tol=1e-7)
                          and row["stop_raw"] >= deadline - 0.01, (label, "wall timeout accounting"))
        timeout = {"log": log.name, "timeout_bound": kind,
                   "effective_limit_s": row["effective_timeout_seconds"], "tool_stop_minus_deadline_s": (
                       row["stop_raw"] - deadline)}
        if log.name == "sec.log":
            proof_log = maybe_read(read, log.parent / "sec" / "prove.log")
            receipt = maybe_read(read, log.parent / "sec" / "receipt.json")
            timeout.update({"proof_log_present": proof_log is not None,
                            "proof_success_marker_present": proof_log is not None and PROOF in proof_log,
                            "sec_receipt_present_in_evidence": receipt is not None})
        timeout_rows.append(timeout)
    return {"admitted": len(arm["requests"]), "completed": arm["completed"],
            "screening_charge_s": item["charged_screening_s"],
            "time_for_rank_and_search_s": deadline - progress["start_raw"],
            "stop": arm["stop"], "pending_at_stop": [row["id"] for row in pending],
            "tool_timeouts": timeout_rows, "area_at_720s_um2": arm["area"], "auc_um2": arm["auc"]}


def completed_by_occurrence(arm):
    occurrences = Counter()
    for request in arm["requests"][:arm["completed"]]:
        actions = tuple(request["actions"])
        occurrences[actions] += 1
        yield (actions, occurrences[actions]), request


def shared_requests(audit, old, new, old_read, new_read):
    other = dict(completed_by_occurrence(new))
    pairs = []
    for identity, left in completed_by_occurrence(old):
        right = other.get(identity)
        if right is None:
            continue
        prior, fresh = left["id"], right["id"]
        rows = audit.compare_trial_physical(old["raw_trials"][prior], new["raw_trials"][fresh], old_read, new_read)
        pairs.append({"old_id": prior, "new_id": fresh, "action_occurrence": identity[1],
                      "gate_and_pass_count_equal": (left["failures"], left["physical_passes"])
                      == (right["failures"], right["physical_passes"]),
                      "accepted_equal": (prior in old["accepted"]) == (fresh in new["accepted"]), **rows})
    return pairs


def prior_single_cutoff(audit, old, new, old_read, new_read, new_state):
    request_id = 8
    if len(new["requests"]) < request_id:
        return {"old_id": request_id, "dispatched_in_new_run": False}
    matching = old["requests"][request_id - 1]["actions"] == new["requests"][request_id - 1]["actions"]
    outcome = {"old_id": request_id, "dispatched_in_new_run": True, "actions_equal_at_same_ordinal": matching,
               "completed_in_new_run": new["completed"] >= request_id}
    if not matching:
        return outcome
    previous = json.loads(old_read(str(V1_TOOLS / "single_08_cutoff.json")))["replay"]
    outcome["new_request_accepted"] = request_id in new["accepted"]
    if outcome["completed_in_new_run"]:
        current = new["raw_trials"][request_id]
    else:
        arm = new_state["arms"]["single_boxed"]
        candidate = PurePosixPath(arm["progress"]["path"]).parent / f"{request_id:02d}"
        last_tool = bound_json(audit, new_read, arm["tool_ledger"])[-1]
        last_log = PurePosixPath(last_tool["log"])
        if not last_log.is_relative_to(candidate):
            return outcome
        assessment_bytes = maybe_read(new_read, last_log.parent / "assessment.json")
        if assessment_bytes is None:
            return outcome
        assessment = json.loads(assessment_bytes)
        current = bound_json(audit, new_read, assessment["physical_receipt"])
        audit.require(current["actions"] == new["requests"][request_id - 1]["actions"],
                      "single cutoff physical receipt actions")
        outcome["new_physical_failures"] = assessment["failures"]
        if assessment["unlocked"] is not None:
            report = audit.bound(new_read, assessment["unlocked"]["report"])
            outcome["new_direct_drc_markers"] = assessment["unlocked"]["drc_markers"]
            outcome["direct_drc_reports_equal"] = report == audit.bound(old_read, previous["drc"])
        confirmed = 0
        for key in audit.PHYSICAL_ARTIFACTS:
            if key in current["artifacts"]:
                audit.bound(new_read, current["artifacts"][key])
                confirmed += 1
        outcome["new_uncommitted_physical_members_verified"] = confirmed
    outcome["physical_fingerprints_match"] = {
        key: (fingerprint(previous["artifacts"][key]) == fingerprint(current["artifacts"][key])
              if key in current["artifacts"] else None)
        for key in ("odb", "def", "v")
    }
    for key in ("odb", "def", "v"):
        audit.bound(old_read, previous["artifacts"][key])
    outcome["spef_without_date_equal"] = None
    if "spef" in current["artifacts"]:
        outcome["spef_without_date_equal"] = (
            audit.spef_without_date(old_read, previous["artifacts"]["spef"])
            == audit.spef_without_date(new_read, current["artifacts"]["spef"]))
    timing = {corner: {audit.CORNER_METRICS[marker]: float(value) for marker, value in
                       (line.split() for line in row["metrics"])} for corner, row in previous["timing"].items()}
    outcome["setup_hold_wns_tns_equal"] = None
    if timing.keys() == current["views"].keys():
        outcome["setup_hold_wns_tns_equal"] = all(
            all(current["views"][corner].get(key) == value for key, value in values.items())
            for corner, values in timing.items())
        if not outcome["completed_in_new_run"]:
            for corner, values in timing.items():
                raw = new_read(current["operations"][f"STA_{corner}"]["log"]).decode()
                audit.require("IBEX_STA_COMPLETE" in raw and all(
                    [float(x) for x in re.findall(rf"(?m)^{marker} (\S+)\s*$", raw)] == [current["views"][corner][key]]
                    for marker, key in audit.CORNER_METRICS.items()), (corner, "cutoff raw STA metrics"))
    return outcome


def matching_action_prefix(old, new):
    matched = 0
    for before, after in zip(old, new):
        if before["actions"] != after["actions"]:
            break
        matched += 1
    return matched


def compare_runs(audit, old_state, old_read, new_state, new_read, cutoff_bundle, *, only_arm=None):
    audit.require(old_state["status"] == "finished" and set(old_state["arms"]) == set(ARMS),
                  "old complete replay receipt required")
    labels = ARMS if only_arm is None else (only_arm,)
    audit.require((new_state["status"] == "finished" and set(new_state["arms"]) == set(ARMS))
                  or (only_arm in new_state["arms"]), "selected arms must publish final receipts before comparison")
    old_policy, old_arms = audit.checks(old_state, old_read, live_trials=True,
                                      verify_accept_artifacts=True, only_arm=only_arm)
    new_policy, new_arms = audit.checks(new_state, new_read, live_trials=True,
                                      verify_accept_artifacts=True, only_arm=only_arm)
    dynamic = {"charged_screening_seconds_per_arm", "reference", "screen_input", "screen_install", "seed", "sources"}
    audit.require({k: v for k, v in old_policy.items() if k not in dynamic}
                  == {k: v for k, v in new_policy.items() if k not in dynamic}
                  and old_state["rank_order"] == new_state["rank_order"]
                  and old_state["qualification"] == new_state["qualification"]
                  and {k: v for k, v in old_state["reference"].items() if k != "evidence_id"}
                  == {k: v for k, v in new_state["reference"].items() if k != "evidence_id"},
                  "qualification, strict-zero result, pool, rank or a search policy field changed")
    delta = source_delta(audit, old_policy, new_policy, cutoff_bundle)
    strict_zero(audit, old_read, old_state, foreground=False)
    strict_zero(audit, new_read, new_state, foreground=True)
    prior_launch = bound_json(audit, old_read, old_state["replay_protocol"])
    fresh_launch = bound_json(audit, new_read, new_state["replay_protocol"])
    for launch, read in ((prior_launch, old_read), (fresh_launch, new_read)):
        audit.require(launch["ordered_arms"] == list(ARMS) and launch["window_s"] == 720
                      and launch["expected_rank"] == old_state["rank_order"]
                      and launch["rebuilt_qualification"] == old_state["qualification"],
                      "launcher disagrees with three-arm Stage 5 receipt")
        for key in ("driver", "input_validator"):
            audit.bound(read, launch[key])
    launch_digests = {key: [fingerprint(item[key]) for item in (prior_launch, fresh_launch)]
                      for key in ("driver", "input_validator")}
    audit.require(all(old == new for old, new in launch_digests.values()), "core launchers changed")
    comparison = {}
    for label in labels:
        old, new = old_arms[label], new_arms[label]
        comparison[label] = {
            "old": end_of_arm(audit, old_read, old_state, label, old),
            "new": end_of_arm(audit, new_read, new_state, label, new),
            "matched_action_prefix": matching_action_prefix(old["requests"], new["requests"]),
            "shared_completed_requests": shared_requests(audit, old, new, old_read, new_read),
            "old_accepted_sequence": accepted_path(audit, old_read, old_state, label, old, old_policy,
                                                   foreground=False),
            "new_accepted_sequence": accepted_path(audit, new_read, new_state, label, new, new_policy,
                                                   foreground=True),
        }
    result = {"source_delta": delta, "launcher_sha256_and_bytes": launch_digests, "arms": comparison}
    if "single_boxed" in labels:
        result["prior_single_sec_cutoff_request"] = prior_single_cutoff(
            audit, old_arms["single_boxed"], new_arms["single_boxed"], old_read, new_read, new_state)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--fixed-root", type=PurePosixPath, default=V2_ROOT)
    parser.add_argument("--fixed-zip", type=Path, action="append", default=[],
                        help="indexed post-fix archives with replay/ and reference/ members")
    parser.add_argument("--arm", choices=ARMS, help="compare a published arm while the remaining arms run")
    args = parser.parse_args()
    audit = published_verifier(args.evidence)
    with ExitStack() as stack:
        old_bundles = {name: pinned_bundle(audit, stack, args.evidence / name, digest)
                       for name, digest in audit.ONLINE_ARCHIVES.items()}
        cutoff = pinned_bundle(audit, stack, args.evidence / "V5_STAGE5_SEC_CUTOFF_ORIGINALS.zip",
                               CUTOFF_ARCHIVE_SHA)
        fixed = [pinned_bundle(audit, stack, path, FIXED_ARCHIVES[path.name]) if path.name in FIXED_ARCHIVES
                 else audit.indexed_bundle(stack, path) for path in args.fixed_zip]
        old_read = runtime_reader(audit, V1_ROOT, old_bundles.values())
        new_read = fixed_reader(audit, args.fixed_root, fixed, old_bundles)
        old = json.loads(old_read(str(V1_ROOT / STATE)))
        new = json.loads(new_read(str(args.fixed_root / STATE)))
        verified = compare_runs(audit, old, old_read, new, new_read, cutoff, only_arm=args.arm)
        launch = bound_json(audit, new_read, new["replay_protocol"])
        member = (lambda name: audit.indexed_member(fixed, name)) if fixed else live_extra_member
        verified["capsule"] = capsule_evidence(audit, member, verified["source_delta"], launch)
        observations = member("launcher/observations.jsonl")
        verified["process_observer"] = observer_evidence(audit, observations, launch, only_arm=args.arm)
        if "single_boxed" in verified["arms"]:
            verified["single_sec_cutoff_process_cleanup"] = single_cutoff_cleanup(audit, observations, new_read, new)
        print(json.dumps(verified, indent=2))


if __name__ == "__main__":
    main()
