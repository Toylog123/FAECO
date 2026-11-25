#!/usr/bin/env python3
"""Transfer the frozen UART hold-geometry diagnostic to historical SKY130HD GCD."""

from argparse import ArgumentParser
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
import sys
from unittest.mock import patch

HOLDOUT = Path(__file__).resolve().parents[1] / "tcad_holdout_20261123"
sys.path.insert(0, str(HOLDOUT))

import probe_uart_hold_geometry as geometry

comparison, read, verify = geometry.comparison, geometry.read, geometry.verify
METHODS = ("fixed", "faeco")
KNOWN_PAIR = {"rejected": "screened/fixed/04_physical/receipt.json",
              "passed": "screened/faeco/05_physical/receipt.json"}


def freeze_scores(seed, output):
    source = seed / "config.json"
    config = read(source)
    if (config["pdk"], config["top"], config["route_guide_source"], config["single_pin_access"]) != (
        "sky130hd", "gcd", "embedded in frozen CONTROL ODB", True,
    ):
        raise ValueError("expected the GCD original embedded-guide pair and one pin access")
    assets = config["bindings"]
    pool_path = seed / "screened_pool_used.json"
    rows = read(pool_path)
    if len(rows) != 18 or rows != read(verify(config["screen_inputs"]["pool"])):
        raise ValueError("the original frozen 18 candidate pool changed")
    verify(config["screen_inputs"]["receipt"])
    verify(assets["original_sdc"])
    pool = [comparison.PhysicalAction(**row) for row in rows]
    reference = seed / "control/receipt.json"
    views = read(reference)["views"]
    protocol = {
        "seed": comparison.bind(source), "pool": comparison.bind(pool_path), "reference": comparison.bind(reference),
        "clock": "CLOCK_MONOTONIC_RAW", "corner_order": geometry.CORNERS, "geometry_track_radius": geometry.TRACK_RADIUS,
        "min_paths_per_group": geometry.PATH_COUNT, "hold_tolerance_ps": config["numerical_tolerance_ps"],
        "absolute_hold_ps": config["hold_threshold_ps"], "known_equal_area_pair": KNOWN_PAIR,
        "driver": comparison.bind(Path(__file__).resolve()),
        "geometry_source": comparison.bind(Path(geometry.__file__).resolve()),
        "incident_source": comparison.bind(Path(geometry.build_incident_priority.__code__.co_filename).resolve()),
        "sta_source": assets["tools"]["opensta"], "reference_path_stage": "frozen only",
    }
    output.mkdir(parents=True)
    protocol_path = output / "protocol.json"
    comparison.save(protocol_path, protocol)

    paths, calls = None, []
    original_paths, original_process = geometry.hold_paths, comparison.run_process

    def frozen_paths(bound_assets, artifacts, expected, out, kinds):
        # UART's shared scorer also requests paths at an accepted prefix. GCD
        # evaluates the frozen-state score only and needs no second STA batch.
        nonlocal paths
        if artifacts != assets["control"] or expected != views:
            raise ValueError("the transfer cannot query a post-candidate prefix")
        if paths is None:
            paths = original_paths(bound_assets, artifacts, expected, out, kinds)
        return paths

    def metered_process(argv, logfile, timeout, *, env=None):
        start = geometry.raw_seconds()
        result = original_process(argv, logfile, timeout, env=env)
        stop = geometry.raw_seconds()
        calls.append({"command": [str(part) for part in argv], "start_raw": start, "stop_raw": stop, **asdict(result)})
        comparison.save(output / "sta_operations.json", calls)
        return result

    start = geometry.raw_seconds()
    prefix = {"artifacts": assets["control"], "views": views}
    with geometry.bind_runtime("gcd", verify(assets["flow"]["fastroute.tcl"])), \
            patch.object(geometry, "hold_paths", frozen_paths), patch.object(comparison, "run_process", metered_process):
        features = geometry.measure_geometry(output, assets["control"], assets, pool, views, prefix)
    features["stages"].pop("accepted_prefix")
    for net in features["per_net"].values():
        net.pop("accepted_prefix")
    elapsed = geometry.raw_seconds() - start
    if len(calls) != len(geometry.CORNERS) or any(call["returncode"] != 0 for call in calls):
        raise ValueError("expected exactly one completed STA for each frozen view")
    comparison.save(output / "scores.json", {"protocol": comparison.bind(protocol_path), "features": features,
                                              "sta_operations": comparison.bind(output / "sta_operations.json"),
                                              "elapsed_raw_seconds": elapsed, "sta_calls": len(calls)})
    print(f"Frozen geometry scored for 18 actions in {elapsed:.3f} RAW s using {len(calls)} STA calls", flush=True)


def score_labels(output, audit_path):
    score_path = output / "scores.json"
    bundle = read(score_path)
    protocol = read(verify(bundle["protocol"]))
    if (verify(protocol["geometry_source"]) != Path(geometry.__file__).resolve()
            or verify(protocol["driver"]) != Path(__file__).resolve()
            or protocol["known_equal_area_pair"] != KNOWN_PAIR):
        raise ValueError("the frozen predictor or comparison identity changed")
    verify(protocol["incident_source"])
    verify(bundle["sta_operations"])
    config_path = verify(protocol["seed"])
    seed = config_path.parent
    config = read(config_path)
    audit = read(audit_path)
    if (audit["top"] != "gcd" or audit["config_sha256"] != protocol["seed"]["sha256"]
            or audit["results_sha256"] != comparison.sha(seed / "results.json") or audit["cache_hits"] != 0
            or audit["screened_pool_sha256"] != config["screen_inputs"]["pool"]["sha256"]
            or audit["screened_receipt_sha256"] != config["screen_inputs"]["receipt"]["sha256"]
            or any(audit["arms"]["screened"][method]["attempts_inside_wall"] != 6 for method in METHODS)):
        raise ValueError("historical label source is not the audited same-backend GCD pair")
    reference = read(verify(protocol["reference"]))["views"]
    unique, pair = {}, {}
    for method in METHODS:
        for request in range(1, 7):
            path = seed / f"screened/{method}/{request:02d}_physical/receipt.json"
            row = read(path)
            if (not row["routed_to_completion"] or not row["extracted_to_completion"]
                    or row["control_sdc"] != config["bindings"]["control"]["sdc"]
                    or set(row["views"]) != set(geometry.CORNERS) or row["drc_violations"] != 0):
                raise ValueError(f"missing original measured physical endpoint at {path}")
            spef = verify(row["artifacts"]["spef"])
            fingerprint = [comparison.bind(verify(row["artifacts"][key]))["sha256"] for key in ("odb", "def", "v")]
            fingerprint.append(sha256(b"".join(line for line in spef.read_bytes().splitlines(keepends=True)
                                               if not line.startswith(b"*DATE "))).hexdigest())
            actions = row["actions"]
            key = tuple(actions), tuple(fingerprint)
            labels = {}
            for view in geometry.CORNERS:
                floor = max(protocol["absolute_hold_ps"], reference[view]["hold_wns_ps"] - protocol["hold_tolerance_ps"])
                labels[view] = row["views"][view]["hold_wns_ps"] < floor
                if labels[view] != any(reason in row["failures"] for reason in (f"{view}:hold_regression", f"{view}:negative_hold")):
                    raise ValueError(f"historical hold label disagrees with measured WNS at {path} {view}")
            result = {"actions": actions, "fingerprint": fingerprint, "hold_reject": labels,
                      "hold_wns_ps": {view: item["hold_wns_ps"] for view, item in row["views"].items()},
                      "failures": row["failures"], "area_saved_um2": row["area_saved"],
                      "frozen_score": geometry.scores(bundle["features"], actions, "frozen")}
            if key in unique and result != {k: v for k, v in unique[key].items() if k != "sources"}:
                raise ValueError(f"the same physical artifact has differing labels at {path}")
            item = unique.setdefault(key, result | {"sources": []})
            item["sources"].append(comparison.bind(path))
            for name, relative in KNOWN_PAIR.items():
                if path == seed / relative:
                    pair[name] = item
    records = list(unique.values())
    metrics = {view: {feature: geometry.auc(records, view, feature, view) for feature in geometry.FEATURES}
               for view in geometry.CORNERS}
    result = {"audit": comparison.bind(audit_path), "score_receipt": comparison.bind(score_path),
              "original_results": comparison.bind(seed / "results.json"), "physical_occurrences": 12,
              "unique_physical_count": len(records), "unique_action_tuples": len({tuple(item["actions"]) for item in records}),
              "metrics": metrics, "known_equal_area_pair": pair, "rows": records,
              "routing_or_candidate_sta_calls": 0}
    comparison.save(output / "results.json", result)
    for view in ("TT", "SS"):
        print(f"{view}: clock {metrics[view]['clock']} and incident_pf {metrics[view]['incident_pf']}", flush=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("score", "evaluate"))
    parser.add_argument("output", type=Path)
    parser.add_argument("--seed", type=Path)
    parser.add_argument("--audit", type=Path, default=Path(__file__).with_name("GCD_INCIDENT_CAP_PAIR_VERIFIED.json"))
    args = parser.parse_args()
    output = args.output.resolve()
    if args.phase == "score":
        if args.seed is None:
            parser.error("score requires --seed")
        freeze_scores(args.seed.resolve(strict=True), output)
    else:
        score_labels(output.resolve(strict=True), args.audit.resolve(strict=True))


if __name__ == "__main__":
    main()
