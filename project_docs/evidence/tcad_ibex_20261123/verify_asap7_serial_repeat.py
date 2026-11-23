#!/usr/bin/env python3
"""Verify the two serial ASAP7 pairs from retained receipts, without running EDA."""

import argparse
from collections import deque
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from pathlib import Path
import re

from verify_setup_protocol import (
    Audit, CORNERS, count_physical, check_bindings, digest, equal, near, need, read,
)


ORDERS = {"reverse": ["faeco", "single"], "original": ["single", "faeco"]}
CAP, BATCH, BUDGET_PCT, TARGET_PCT = 6, 3, 1.0, 0.01
STAGES = ("DRT_RCX", *(f"STA_{view}" for view in CORNERS), "SEC")


def previous_bindings(audit):
    current = audit.config
    binding = current["previous_run"]
    check_bindings(binding)
    result_path = Path(binding["path"])
    old = read(result_path.with_name("config.json"))
    result = read(result_path)
    equal(result["status"], "matched", "historical primary status")
    equal(result["scope"], old["scope"], "historical primary scope")
    for key in ("pdk", "top", "budget_attempts_per_arm", "batch_size", "methods_route_threads",
                "route_mode", "route_drt_iters", "route_guide_source", "route_timeout_seconds",
                "sta_timeout_seconds_per_view", "sec_timeout_seconds", "numerical_tolerance_ps",
                "hold_threshold_ps", "hold_nonregression_per_view", "same_area_acceptance", "report_setup_endpoints",
                "original_clock_period_ps", "primary_budget_pct", "primary_mode",
                "primary_target_area_pct", "setup_tns_loss_budget", "no_op_preflight_setup_budget_ps"):
        equal(current[key], old[key], f"frozen CFG {key}")
    for key, source in old["bindings"].items():
        active = audit.assets[key]
        if key == "used_libraries":
            for view in CORNERS:
                equal([row["sha256"] for row in active[view]], [row["sha256"] for row in source[view]],
                      f"staged Liberty content {view}")
        elif key == "driver_source":
            equal({name: active[name] for name in source}, source, "previous driver bindings")
        else:
            equal(active, source, f"frozen input {key}")
    equal(audit.ref_views, result["control"]["views"], "frozen CONTROL view results")
    equal(digest(audit.root / "pool.json"), digest(result_path.with_name("pool.json")), "candidate pool digest")
    return result


def verify_dispatch(ranked, rows, method):
    pending, committed = deque(), []
    offset = 0
    for index, row in enumerate(rows, start=1):
        if not pending:
            width = BATCH if method == "faeco" and index < CAP else 1
            chunk = ranked[offset:offset + width]
            need(bool(chunk), f"candidate pool exhausted at dispatch {index}")
            pending.append(chunk)
            offset += len(chunk)
        chunk = pending.popleft()
        equal(row["actions"], sorted(committed + chunk), f"{method} dispatch order {index}")
        if row["accepted"]:
            committed.extend(chunk)
        elif method == "faeco" and len(chunk) > 1:
            split = len(chunk) // 2
            pending.extendleft((chunk[split:], chunk[:split]))


def parse_utc(raw):
    instant = datetime.fromisoformat(raw)
    equal(instant.tzinfo, timezone.utc, "arm clock in UTC")
    return instant


def verify_arm(audit, directory, summary):
    equal(read(directory / "summary.json"), summary, f"bound arm summary {directory}")
    rows = summary["checkpoints"]
    equal(summary["evaluations"], len(rows), f"evaluation count {directory}")
    need(1 <= len(rows) <= CAP, f"evaluation limit {directory}")
    target = audit.area * TARGET_PCT / 100
    near(summary["target_area_saved"], target, f"area target {directory}")
    start, end = summary["start_monotonic"], summary["end_monotonic"]
    duration = summary["elapsed_seconds"]
    near(duration, end - start, f"monotonic elapsed time {directory}")
    need(math.isfinite(duration) and duration > 0, f"wall duration {directory}")
    start_utc, end_utc = map(parse_utc, (summary["start_utc"], summary["end_utc"]))
    need(start_utc <= end_utc, f"UTC duration {directory}")

    best, first, elapsed = audit.ref["endpoint"], None, 0.0
    physical_paths = []
    stage_seconds = dict.fromkeys(STAGES, 0.0)
    for idx, row in enumerate(rows, start=1):
        need(first is None, f"physical work after first target {directory}:{idx}")
        step = audit.request(directory / f"{idx:02d}.json", row["actions"], BUDGET_PCT, False, True)
        equal({**step, "elapsed_seconds": row["elapsed_seconds"], "accepted": row["accepted"]}, row,
              f"checkpoint receipt {directory}:{idx}")
        path = Path(step["physical_receipt"])
        physical_paths.append(path)
        physical = audit.physical[path]
        need(physical["routed_to_completion"] and physical["extracted_to_completion"], f"physical completion {path}")
        equal(set(physical["views"]), set(CORNERS), f"complete corner results {path}")
        operations = dict(physical["operations"])
        if path in audit.proofs:
            operations.update(audit.proofs[path][0]["operations"])
        for name, op in operations.items():
            stage_seconds[name] += op["wall_seconds"]
        check_route_threads(operations["DRT_RCX"])

        endpoint = step["endpoint"]
        accepted = endpoint["valid"] and endpoint["sec_pass"] and endpoint["area"] < best["area"] - 1e-9
        equal(row["accepted"], accepted, f"verified acceptance {directory}:{idx}")
        instant = row["elapsed_seconds"]
        need(elapsed + step["wall_seconds"] <= instant + 1e-8 and instant <= duration + 1e-8,
             f"checkpoint clock bounds {directory}:{idx}")
        elapsed = instant
        if accepted:
            best = endpoint
            if audit.area - best["area"] >= target - 1e-9:
                first = instant

    verify_dispatch([action["action_id"] for action in audit.pool], rows, directory.name)
    equal(best, summary["selected"], f"selected endpoint {directory}")
    near(summary["area_saved"], audit.area - best["area"], f"area saved {directory}")
    equal(summary["target_reached_seconds"], first, f"first target time {directory}")
    need(first is not None or len(rows) == CAP, f"premature stop {directory}")
    return {
        "target_seconds": first, "arm_wall_seconds": duration,
        "start_utc": summary["start_utc"], "end_utc": summary["end_utc"],
        "evaluations": len(rows), "stage_seconds": stage_seconds,
        "overhead_seconds": elapsed - sum(stage_seconds.values()), "operations": audit.totals(physical_paths),
        "outcome": audit.outcome(best),
    }


def check_route_threads(op):
    with Path(op["log"]).open(errors="replace") as stream:
        match = next((m for line in stream if (m := re.search(r"Using (\d+) thread\(s\)", line))), None)
    need(match is not None and match[1] == "4", f"OpenROAD thread evidence {op['log']}")


def spef_without_date(path):
    normalized, excluded = sha256(), 0
    with path.open("rb") as stream:
        for line in stream:
            if line.startswith(b"*DATE "):
                excluded += 1
            else:
                normalized.update(line)
    equal(excluded, 1, f"one SPEF header DATE in {path}")
    return normalized.hexdigest()


def endpoint_signature(physical):
    artifacts = physical["artifacts"]
    return {
        "actions": physical["actions"], "area": physical["endpoint"]["area"],
        "views": physical["views"], "artifact_digests": {
            **{kind: artifacts[kind]["sha256"] for kind in ("odb", "def", "v")},
            "spef_without_date": spef_without_date(Path(artifacts["spef"]["path"])),
        },
    }


def at_target(audit, summary):
    if summary["target_reached_seconds"] is None:
        return None
    return endpoint_signature(audit.physical[Path(summary["selected"]["evidence_id"]) / "receipt.json"])


def paired_difference(arms):
    single, faeco = arms["single"], arms["faeco"]
    if single["target_seconds"] is None or faeco["target_seconds"] is None:
        return None
    return {
        "single_minus_faeco_seconds": single["target_seconds"] - faeco["target_seconds"],
        "stage_delta_seconds": {key: single["stage_seconds"][key] - faeco["stage_seconds"][key] for key in STAGES},
        "overhead_delta_seconds": single["overhead_seconds"] - faeco["overhead_seconds"],
    }


def verify(root):
    audit = Audit(root)
    cfg = audit.config
    result = read(root / "results.json")
    equal(result["status"], "matched", "complete serial run")
    equal(result["scope"], audit.scope, "bound serial scope")
    equal(result["control"], audit.ref, "bound serial CONTROL")
    equal(list(cfg["orders"].items()), list(ORDERS.items()), "declared serial pairs")
    equal(cfg["methods_in_run_order"], ["faeco", "single", "single", "faeco"], "declared dispatch order")
    equal(list(result["orders"].items()), list(ORDERS.items()), "measured serial pairs")
    equal(list(result["pairs"]), list(ORDERS), "pair chronology")
    for key, value in {"pdk": "asap7", "cpu_affinity": list(range(6)), "methods_route_threads": 4,
                       "budget_attempts_per_arm": CAP, "batch_size": BATCH, "original_clock_period_ps": 1000.0,
                       "primary_mode": "tradeoff", "primary_budget_pct": BUDGET_PCT,
                       "primary_target_area_pct": TARGET_PCT, "cached_physical_trials": False}.items():
        equal(cfg[key], value, f"serial configuration {key}")
    equal(result["target_area_pct"], TARGET_PCT, "target percentage")
    audit.gate_summary(result["gate"], BUDGET_PCT, False)
    prior = previous_bindings(audit)
    noop = audit.verify_physical(root / "noop" / "receipt.json", (), noop=True)
    check_route_threads(noop["operations"]["DRT_RCX"])
    equal(result["shared_noop"], noop, "bound shared preflight")
    equal(result["shared_noop_operations"], count_physical(noop), "separate preflight counts")

    verified, signatures, last = {}, [], None
    for pair, order in ORDERS.items():
        arms = result["pairs"][pair]
        equal(list(arms), order, f"pair method order {pair}")
        summaries, endpoints = {}, []
        for method in order:
            row = arms[method]
            if last is not None:
                need(last["end_monotonic"] <= row["start_monotonic"] and
                     parse_utc(last["end_utc"]) <= parse_utc(row["start_utc"]),
                     f"non-overlap {pair}/{method}")
            summaries[method] = verify_arm(audit, root / pair / method, row)
            endpoints.append(at_target(audit, row))
            last = row
        verified[pair] = {
            "order": order, "arms": summaries, "difference": paired_difference(summaries),
            "same_target_endpoint": endpoints[0] is not None and endpoints[0] == endpoints[1],
        }
        signatures.extend(endpoints)

    equal(set(root.glob("*/*/[0-9][0-9].json")), audit.logical_paths, "all logical receipts accounted for")
    equal(set(root.glob("*/*/*_physical/receipt.json")), set(audit.physical), "all physical receipts accounted for")
    equal({p.with_name("receipt.json") for p in root.glob("*/*/*_physical/deferred_proof.json")}, set(audit.proofs),
          "all deferred SEC receipts accounted for")
    totals = audit.totals(list(audit.physical))
    totals.update(logical_requests=audit.request_count, physical_cache_hits=audit.cache_hits)
    for key, value in totals.items():
        near(result["physical_operations"][key], value, f"total recorded operations {key}")
    equal(audit.cache_hits, 0, "no physical cache reuse")
    prior_signatures = {method: prior_target(prior, method, audit) for method in ("single", "faeco")}
    same_target = signatures[0] is not None and all(row == signatures[0] for row in signatures)
    return {
        "config_sha256": digest(root / "config.json"), "results_sha256": digest(root / "results.json"),
        "previous_results_sha256": cfg["previous_run"]["sha256"], "scope": audit.scope,
        "pool_sha256": digest(root / "pool.json"), "original_sdc_sha256": audit.assets["original_sdc"]["sha256"],
        "target_area_saved": audit.area * TARGET_PCT / 100, "shared_noop_seconds": noop["wall_seconds"],
        "shared_noop_sec_proven": audit.noop_proven, "operations": totals, "pairs": verified,
        "same_target_endpoint_all_arms": same_target,
        "same_target_endpoint_as_previous": same_target and all(row == signatures[0] for row in prior_signatures.values()),
        "common_target_digest": signatures[0]["artifact_digests"] if same_target else None,
    }


def prior_target(prior, method, audit):
    source = prior["primary"]["results"][method]
    target = audit.area * TARGET_PCT / 100
    for row in source["checkpoints"]:
        endpoint = row["endpoint"]
        if row["accepted"] and endpoint["sec_pass"] and audit.area - endpoint["area"] >= target - 1e-9:
            physical = read(Path(endpoint["evidence_id"]) / "receipt.json")
            check_bindings(physical["artifacts"])
            return endpoint_signature(physical)
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="retained serial run root")
    print(json.dumps(verify(parser.parse_args().root.resolve()), indent=2, allow_nan=False))
