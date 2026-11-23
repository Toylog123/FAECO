"""Recompute Ibex comparison counts and check the selected routed proof inputs."""

import argparse
from hashlib import file_digest
import json
import math
from pathlib import Path


VIEWS = ("FF", "TT", "SS")
ARMS = ("single", "fixed", "faeco")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify_file(record):
    path = Path(record["path"])
    with path.open("rb") as stream:
        sha = file_digest(stream, "sha256").hexdigest()
    if sha != record["sha256"] or path.stat().st_size != record["bytes"]:
        raise ValueError(f"evidence identity mismatch: {path}")


def verify_endpoint(root, receipt, control, config):
    if receipt["failures"] or receipt["drc_violations"] != 0:
        raise ValueError(f"selected endpoint failed a joint gate: {receipt['endpoint_id']}")
    for artifact in receipt["artifacts"].values():
        verify_file(artifact)
    if receipt["control_sdc"] != config["bindings"]["control"]["sdc"]:
        raise ValueError("candidate SDC is not the frozen CONTROL SDC")
    sec = read(root / receipt["endpoint_id"] / "sec/receipt.json")
    if not sec["passed"] or sec["proven"] <= 0 or sec["unproven"] != 0:
        raise ValueError("selected endpoint has no valid, non-empty SEC")
    for key, expected in (("gold", config["bindings"]["control"]["v"]), ("gate", receipt["artifacts"]["v"])):
        if sec[key] != expected:
            raise ValueError(f"SEC {key} does not bind the exact routed endpoint")
    verify_file(sec["log"])
    tolerance = config["numerical_tolerance_ps"]
    view_deltas = {}
    for view in VIEWS:
        baseline, candidate = control["views"][view], receipt["views"][view]
        setup = candidate["setup_wns_ps"] - baseline["setup_wns_ps"]
        hold = candidate["hold_wns_ps"] - baseline["hold_wns_ps"]
        if setup < -config["setup_budget_ps_per_view"] - tolerance:
            raise ValueError(f"{view}: selected endpoint exceeds setup budget")
        if hold < -tolerance or candidate["hold_wns_ps"] < 0.0:
            raise ValueError(f"{view}: selected endpoint violates the hold gate")
        for kind, old in baseline["electrical"].items():
            if candidate["electrical"][kind].keys() - old.keys():
                raise ValueError(f"{view}: selected endpoint adds an electrical violation")
        view_deltas[view] = {"setup_ps": setup, "hold_ps": hold}
    return {"sec": [sec["proven"], sec["unproven"]], "view_deltas_ps": view_deltas}


def attempt_ledger(trials, trace):
    return [
        {
            "endpoint": trial["endpoint_id"],
            "actions": trial["actions"],
            "accepted": step["accepted"],
            "area_saved": trial.get("area_saved"),
            "seconds": trial["wall_seconds"],
            "drc": trial.get("drc_violations"),
            "passed_drt": trial.get("routed_to_completion", False),
            "passed_rcx": trial.get("extracted_to_completion", False),
            "failures": trial["failures"],
            "views_ps": {
                view: {key: values[key] for key in
                       ("setup_wns_ps", "hold_wns_ps", "setup_tns_ps", "hold_tns_ps")}
                for view, values in trial["views"].items()
            },
        }
        for trial, step in zip(trials, trace, strict=True)
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_output", type=Path)
    args = parser.parse_args()
    root = args.raw_output
    config = read(root / "config.json")
    data = read(root / "results.json")
    if data["status"] != "matched" or data["scope"] != config["scope"]:
        raise ValueError("no complete, matched comparison receipt")
    for value in config["bindings"]["control"].values():
        verify_file(value)
    verified = {"control_area": data["control"]["endpoint"]["area"], "arms": {}}
    verified["noop"] = verify_endpoint(root, data["shared_noop"], data["control"], config)
    equal_wall = data["equal_wall_prefixes"]
    trial_sets = {
        arm: [read(root / name / "receipt.json") for name in data["results"][arm]["attempts"]]
        for arm in ARMS
    }
    common_seconds = min(sum(trial["wall_seconds"] for trial in trials) for trials in trial_sets.values())
    if not math.isclose(common_seconds, data["equal_wall_prefix_limit_seconds"], abs_tol=1e-9):
        raise ValueError("common wall prefix budget mismatch")
    verified["common_wall_seconds"] = common_seconds
    for arm in ARMS:
        result = data["results"][arm]
        trials = trial_sets[arm]
        counts = {
            "route_attempts": sum("DRT_RCX" in trial["operations"] for trial in trials),
            "drt_completions": sum(trial.get("routed_to_completion", False) for trial in trials),
            "rcx_completions": sum(trial.get("extracted_to_completion", False) for trial in trials),
            "view_sta_attempts": sum(f"STA_{view}" in trial["operations"] for trial in trials for view in VIEWS),
            "sec_attempts": sum("SEC" in trial["operations"] for trial in trials),
        }
        if (len(trials) != config["budget_attempts_per_arm"]
                or any(count != result[key] for key, count in counts.items())):
            raise ValueError(f"{arm}: count mismatch")
        selected = result["selected"]
        saved = verified["control_area"] - selected["area"]
        if not math.isclose(saved, result["area_saved"], abs_tol=1e-9):
            raise ValueError(f"{arm}: area mismatch")
        elapsed, completed, common_area = 0.0, 0, verified["control_area"]
        for trace, trial in zip(result["trace"], trials, strict=True):
            elapsed += trial["wall_seconds"]
            if elapsed > common_seconds:
                break
            completed += 1
            if trace["accepted"]:
                common_area = trial["endpoint"]["area"]
        common_saved = verified["control_area"] - common_area
        if (completed != equal_wall[arm]["completed_attempts"]
                or not math.isclose(common_saved, equal_wall[arm]["area_saved"], abs_tol=1e-9)):
            raise ValueError(f"{arm}: common wall result mismatch")
        summary = {
            **counts,
            "selected": selected["endpoint_id"],
            "area_saved": saved,
            "common_wall_area_saved": common_saved,
            "common_wall_attempts": completed,
            "attempts": attempt_ledger(trials, result["trace"]),
        }
        if selected["endpoint_id"] != "control":
            selected_trial = next(trial for trial in trials if trial["endpoint_id"] == selected["endpoint_id"])
            summary.update(verify_endpoint(root, selected_trial, data["control"], config))
        verified["arms"][arm] = summary
    print(json.dumps(verified, indent=2))


if __name__ == "__main__":
    main()
