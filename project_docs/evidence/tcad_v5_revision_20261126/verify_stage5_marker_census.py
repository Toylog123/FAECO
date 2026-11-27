#!/usr/bin/env python3
"""Count initial and post-route markers in the already published processor traces."""

from contextlib import ExitStack
import json
from pathlib import PurePosixPath
import re

from verify_stage5_isolated_online import ROOT, bound, indexed_bundle, mapped_member, require


RUN = PurePosixPath("/var/tmp/faeco_v6_stage5_online_20261127_v1")
ARCHIVE_PREFIX = "V5_STAGE5_ISOLATED_ONLINE_"


def markers(raw):
    """Keep each marker body so duplicate events can be counted by exact action set."""
    blocks = re.split(r"(?m)^\s*(?=violation type:)", raw.decode())
    return [" ".join(block.split()) for block in blocks if block.startswith("violation type:")]


def inspect(read):
    state = json.loads(read(RUN / "stage5_progress.json"))
    protocol = json.loads(bound(read, state["protocol"]))
    require(state["status"] == "finished" and len(state["arms"]) == 3, "incomplete frozen trace")
    by_id = {item["action_id"]: item for item in protocol["ordered_pool"]}
    rows = []
    for label, arm in state["arms"].items():
        progress_path = PurePosixPath(arm["progress"]["path"])
        trace = json.loads(bound(read, arm["progress"]))
        for request in trace["logical_requests"]:
            number = f"{request['id']:02d}"
            method = progress_path.parent
            action_set = sorted((by_id[key]["instance"], by_id[key]["source_cell"], by_id[key]["target_cell"])
                                for key in request["actions"])
            require(len(action_set) == len({row[0] for row in action_set}), (label, number, "duplicate instance"))
            preflight_path = method / "diagnosis" / number / "diagnosis.json"
            preflight = json.loads(read(preflight_path))
            require(preflight["actions"] == request["actions"] and preflight["failure"] is None,
                    (label, number, "preflight did not bind request"))
            initial_markers = markers(bound(read, preflight["report"]))
            raw_count = sum(len(markers(read(preflight_path.parent / f"box_{index}.rpt")))
                            for index in range(preflight["box_meta"]["merged_boxes"]))
            require(len(initial_markers) == preflight["marker_count"] and raw_count == preflight["raw_marker_count"],
                    (label, number, "preflight marker count"))
            row = {"arm": label, "request": request["id"], "actions": action_set,
                   "preflight": {"receipt": str(preflight_path), "raw_markers": raw_count,
                                 "markers": initial_markers, "released_neighbors": preflight["released_neighbors"]}}
            for key, phase in (("first_independent_drc", "initial"), ("retry_independent_drc", "retry")):
                audit_path = method / number / phase / "unlocked_drc/audit.json"
                try:
                    audit = json.loads(read(audit_path))
                except KeyError:
                    row[key] = None
                else:
                    found = markers(bound(read, audit["report"]))
                    require(len(found) == audit["drc_markers"], (label, number, phase, "raw marker count"))
                    row[key] = {"receipt": str(audit_path), "markers": found}
            rows.append(row)
    first = [row for row in rows if row["first_independent_drc"] is not None]
    positive = {(tuple(map(tuple, row["actions"])), marker)
                for row in first for marker in row["first_independent_drc"]["markers"]}
    counts = {
        "preflight_requests": len(rows),
        "preflight_unique_action_sets": len({tuple(map(tuple, row["actions"])) for row in rows}),
        "preflight_nonzero": sum(bool(row["preflight"]["markers"]) for row in rows),
        "first_drc_available": len(first),
        "first_drc_nonzero": sum(bool(row["first_independent_drc"]["markers"]) for row in first),
        "first_drc_positive_action_sets": len({actions for actions, _ in positive}),
        "first_drc_action_marker_pairs": len(positive),
        "first_drc_distinct_marker_bodies": len({marker for _, marker in positive}),
        "retry_drc_available": sum(row["retry_independent_drc"] is not None for row in rows),
        "retry_drc_nonzero": sum(bool(row["retry_independent_drc"]["markers"])
                                 for row in rows if row["retry_independent_drc"] is not None),
    }
    return {"run": str(RUN), "counts": counts, "requests": rows}


def main():
    names = ("COMMON", "SINGLE_BOXED", "FIXED_BOXED", "FAECO_BOXED")
    with ExitStack() as stack:
        bundles = [indexed_bundle(stack, ROOT / f"{ARCHIVE_PREFIX}{name}.zip") for name in names]
        data = inspect(lambda path: mapped_member(path, [(RUN, PurePosixPath("replay"))], bundles))
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
