#!/usr/bin/env python3
"""Check whether sensitivity-ranked batch prefixes already have measured endpoints."""

from argparse import ArgumentParser
from pathlib import Path

from run_wallclock_matrix import comparison, read, verify


def replay(root, verification):
    report = read(verification)
    protocol_path = root / "protocol.json"
    if verify(report["protocol"]) != protocol_path:
        raise ValueError("verification bound another experiment")
    protocol = read(protocol_path)
    strong = next(row for row in report["arms"] if row["direction"] == "forward"
                  and row["strategy"] == "single_sensitivity")
    arm = root / f"cell_{strong['cell']:02d}" / "single"
    ranking = read(arm / "sensitivity/ranking.json")
    ordered = ranking["ordered_action_ids"]
    scope = read(verify(protocol["seed"]))["scope"]
    if set(ordered) != {row["action_id"] for row in protocol["ordered_pool"]}:
        raise ValueError("ranked candidate pool differs")
    known = {tuple(row["actions"]): row for row in strong["accepted"]}
    progress = read(arm / "progress.json")
    width = protocol["batch_size"]
    hits = []
    for stop in range(width, len(ordered) + 1, width):
        ids = tuple(sorted(ordered[:stop]))
        endpoint = known.get(ids)
        if endpoint is None:
            break
        identity = endpoint["identity"]["receipt"]
        payload = read(verify(identity))
        if tuple(payload["actions"]) != ids or payload["endpoint"]["scope_id"] != scope:
            raise ValueError("accepted endpoint is outside the frozen tuple or scope")
        request = progress["logical_requests"][endpoint["request_id"] - 1]
        hits.append({"ranked_actions": stop, "source_request": endpoint["request_id"],
                     "area_saved": endpoint["area_saved"], "actions": list(ids), "physical_receipt": identity,
                     "observed_request_raw_seconds": request["finished_raw"] - request["admitted_raw"]})
    return {"protocol": comparison.bind(protocol_path), "verification": comparison.bind(verification),
            "ranking": comparison.bind(arm / "sensitivity/ranking.json"), "exact_accepted_prefixes": hits,
            "first_prefix_without_accepted_measurement": len(hits) * width + width,
            "scope": "post-hoc exact cumulative action lookups, no new physical work or combined runtime"}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("verification", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = replay(args.run.resolve(strict=True), args.verification.resolve(strict=True))
    comparison.save(args.output, result)
    for point in result["exact_accepted_prefixes"]:
        print(point["ranked_actions"], point["area_saved"], point["observed_request_raw_seconds"])
    print("first unmeasured prefix:", result["first_prefix_without_accepted_measurement"])


if __name__ == "__main__":
    main()
