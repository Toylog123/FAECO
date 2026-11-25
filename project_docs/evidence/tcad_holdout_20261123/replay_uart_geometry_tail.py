#!/usr/bin/env python3
"""Read the original UART frontier and compare the last-slot rankings offline."""

from argparse import ArgumentParser
from pathlib import Path

from probe_uart_hold_geometry import CORNERS, auc, comparison, read, scores, verify


def decision(arm, features, geometry_result, pool):
    requests = [row for row in arm["requests"] if row["logical_finished"]]
    history = arm["physical_identities"][:5]
    if len(requests) != 6 or len(arm["reservation"]) != 1 or arm["reservation"][0]["physical_request"] != 6:
        raise ValueError("expected a full physical arm with only a last-slot reservation")
    accepted = [row for row in arm["accepted"] if row["request_id"] < requests[-1]["id"]]
    current = set(accepted[-1]["actions"])
    # The original reserved arm used legal batches followed by atomic splits;
    # subtract the already accepted set to recover the individual proposal.
    committed, deferred, tested = set(), set(), set()
    for request, physical in zip(requests[:5], history, strict=True):
        actions = set(physical["actions"])
        new = actions - committed
        if len(new) == 1:
            tested.update(new)
        elif physical["failures"] and all(reason.endswith(":hold_regression") for reason in physical["failures"]):
            deferred.update(new)
        if any(row["request_id"] == request["id"] for row in accepted):
            committed = actions
    if committed != current:
        raise ValueError("replayed earlier commits do not match the accepted prefix")
    seen = {frozenset(item["actions"]) for item in history}
    eligible = [key for key in pool if key in deferred - (current | tested) and frozenset(current | {key}) not in seen]
    entries = []
    for action in eligible:
        cumulative = sorted(current | {action})
        modeled = scores(features, cumulative, "accepted_prefix")
        matches = [row for row in geometry_result["unique_rows"] if row["actions"] == cumulative]
        original = features["actions"][action]
        entries.append({"action": action, "area": original["estimated_save"], "priority": original["priority"],
                        "risk_by_corner": {corner: modeled[corner]["clock"] for corner in CORNERS},
                        "risk": max(modeled[corner]["clock"] for corner in CORNERS),
                        "measured": [{"passes_all": not row["failures"], "failures": row["failures"],
                                      "area": row["area"], "sources": row["sources"]} for row in matches]})
    frozen_order = lambda row: pool.index(row["action"])
    historical = min(entries, key=lambda row: (-row["area"], -row["priority"], frozen_order(row)))
    observed = arm["reservation"][0]["action"]
    if historical["action"] != observed:
        raise ValueError("the published last-slot order did not replay")
    ranked = sorted(entries, key=lambda row: (-row["area"], row["risk"], -row["priority"], frozen_order(row)))
    return {"cell": arm["cell"], "prefix": sorted(current), "area_then_capacitance": observed,
            "area_then_clock_risk": ranked[0]["action"], "ranked": ranked}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("geometry_run", type=Path)
    args = parser.parse_args()
    root = args.geometry_run.resolve(strict=True)
    scores_ref, result_ref = (comparison.bind(root / name) for name in ("scores.json", "results.json"))
    bundle, result = read(verify(scores_ref)), read(verify(result_ref))
    if result["score_receipt"] != scores_ref or not result["eligible"]:
        raise ValueError("the frozen development score did not pass its own eligibility gate")
    protocol = read(verify(bundle["protocol"]))
    audit = read(verify(protocol["audits"]["reservation"]))
    seed = read(verify(protocol["source_protocols"]["reservation"]))
    pool = [comparison.PhysicalAction(**row).action_id for row in seed["ordered_pool"]]
    two = [decision(arm, bundle["features"], result, pool) for arm in audit["arms"] if arm["variant"] == "reserved"]
    if len(two) != 2 or two[0]["ranked"] != two[1]["ranked"] or two[0]["prefix"] != protocol["prefix_actions"]:
        raise ValueError("the two historical frontier results do not match the scored prefix")
    formal = [row for row in result["unique_rows"] if any(y["source"][0] != "targeted" for y in row["sources"])]
    widths = {n: {key: auc([row for row in formal if len(row["actions"]) == n], "SS", key, "SS")
                  for key in ("clock", "incident_pf")}
              for n in sorted({len(row["actions"]) for row in formal})}
    comparison.save(root / "frontier.json", {"scores": scores_ref, "results": result_ref,
                                            "choices": two, "ss_by_candidate_width": widths,
                                            "driver": comparison.bind(Path(__file__).resolve()), "new_physical_evaluations": 0})
    print(f"replayed last-slot winner: {two[0]['area_then_clock_risk']}", flush=True)


if __name__ == "__main__":
    main()
