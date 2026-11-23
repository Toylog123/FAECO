#!/usr/bin/env python3
"""Audit frozen-SPEF screening and retained physical Ibex pilot outcomes."""

import argparse
from dataclasses import asdict, replace
import json
import math
from pathlib import Path

import compare_ibex as comparison
from verify_screened_matrix import MatrixAudit
from verify_setup_protocol import check_bindings, complete, digest, equal, near, need, process, read


PILOT = ("place2749", "place2755")
CLOCK = "CLOCK_MONOTONIC_RAW"


def commands(source, command):
    return [line for line in source if line.startswith(command + " ")]


def load_probe(audit, directory, control, operation, action=None):
    source = (directory / "tt.tcl").read_text().splitlines()
    for cmd, role in (("read_db", "odb"), ("read_sdc", "sdc"), ("read_spef", "spef")):
        equal(commands(source, cmd), [f"{cmd} {comparison.tcl(control[role]['path'])}"], f"frozen {role} {directory}")
    equal(commands(source, "read_liberty"),
          [f"read_liberty {comparison.tcl(item['path'])}" for item in audit.libs["TT"]],
          f"frozen TT models {directory}")
    need(not any(row.startswith(("detailed_route ", "global_route", "extract_parasitics ", "write_")) for row in source),
         f"unexpected physical operation {directory}")
    swaps = [line for line in source if "swapMaster" in line]
    if action:
        equal(len(swaps), 1, f"single fixed-SPEF edit {directory}")
        need(any(line.endswith(f"findInst {comparison.tcl(action['instance'])}]") for line in source),
             f"fixed-SPEF edited instance {directory}")
        need(any(line.endswith(f"findMaster {comparison.tcl(action['target_cell'])}]") for line in source),
             f"fixed-SPEF target {directory}")
        need(any(f"getName] ne {comparison.tcl(action['source_cell'])}" in line for line in source),
             f"fixed-SPEF source master {directory}")
    else:
        equal(swaps, [], f"zero-edit fixed-SPEF baseline {directory}")
    text = process(operation, directory / "tt.log", audit.config["sta_timeout_seconds_per_view"])
    need(complete(operation, text, "IBEX_STA_COMPLETE"), f"raw fixed-SPEF STA {directory}")
    annotation = text.split("SCREEN_ANN_BEGIN\n", 1)[1].split("SCREEN_ANN_END", 1)[0]
    need("Found 0 partially unannotated drivers." in annotation, f"partial frozen annotation {directory}")
    return comparison.parse_sta(text), annotation


def rebuild_pool(root, audit):
    inventory = (root / "inventory.log").read_text()
    fanout_log = (root / "fanout.log").read_text().splitlines()
    need("IBEX_INVENTORY_COMPLETE" in inventory.splitlines()
         and "SCREEN_FANOUT_COMPLETE" in fanout_log, "raw screened inventory and fanout")
    for name in ("inventory", "fanout"):
        deck = (root / f"{name}.tcl").read_text().splitlines()
        equal(commands(deck, "read_db"), [f"read_db {comparison.tcl(audit.control['odb']['path'])}"],
              f"frozen {name} ODB")
    fanout = {fields[1]: int(fields[2]) for line in fanout_log if line.startswith("SCREEN_FANOUT\t")
              for fields in [line.split("\t")]}
    masters, instances = comparison.parse_inventory(inventory)
    aligned, mismatches = comparison.align_db_instances(audit.masters, instances)
    equal(mismatches, [], "frozen inventory master check")
    libraries = {corner: [Path(item["path"]) for item in group] for corner, group in audit.libs.items()}
    legacy = comparison.select_pool(root / "index.v", libraries, masters, aligned)
    equal([asdict(row) for row in legacy], audit.pool, "screen and prior eligible legacy pool")
    eligible = {comparison.canonical_odb_name(row.instance): row.instance for row in legacy}
    by_name = {row.instance: [] for row in legacy}
    all_views = set.intersection(*(set(comparison.liberty_areas(libs)) for libs in libraries.values()))
    for act in comparison.generate_compatible_candidates(root / "index.v", libraries["TT"]):
        instance = eligible.get(act.instance.removeprefix("\\"))
        if instance not in by_name or act.target_cell not in all_views:
            continue
        source, target = masters[act.source_cell], masters.get(act.target_cell)
        if target is not None and target[:4] == source[:4] and int(target[4]) < int(source[4]):
            by_name[instance].append(replace(act, instance=instance))
    closest = {
        name: min(acts, key=lambda row: (-audit.areas[row.target_cell], row.target_cell))
        for name, acts in by_name.items()
    }
    ranked = sorted(
        (row for name, row in closest.items() if fanout[name] > 0),
        key=lambda row: (fanout[row.instance], -row.estimated_area_saving, row.action_id),
    )
    return [asdict(row) for row in ranked], {k: asdict(v) for k, v in closest.items()}, fanout


def audit_screen(root, prior):
    cfg = read(root / "screen_receipt.json")
    check_bindings(cfg)
    equal(cfg["clock"], CLOCK, "screen clock")
    equal(cfg["top"], prior.config["top"], "screened top")
    equal(cfg["control"], prior.control, "fixed screen CONTROL identity")
    equal(cfg["control_sha256"], {name: prior.control[name]["sha256"] for name in ("odb", "spef", "sdc")},
          "fixed screen CONTROL SHA")
    expected_pool, closest, fanout = rebuild_pool(root, prior)
    baseline, annotation = load_probe(prior, root / "control_TT", cfg["control"], cfg["baseline"])
    equal(baseline, prior.ref_views["TT"], "screen baseline exact prior TT metrics")
    near(cfg["period_ps"], prior.period, "screen period")
    wns = prior.period / 100
    tns = max(10 * wns, abs(baseline["setup_tns_ps"]) / 100)
    near(cfg["budgets_ps"]["wns"], wns, "frozen TT WNS budget")
    near(cfg["budgets_ps"]["tns"], tns, "frozen TT TNS budget")

    def verify_probe(row):
        action = row["action"]
        directory = root / row["label"]
        equal(read(directory / "receipt.json"), row, f"fixed-SPEF receipt {directory}")
        equal(row["fanout"], fanout[action["instance"]], f"raw fanout {directory}")
        views, annotated = load_probe(prior, directory, cfg["control"], row["operation"], action)
        equal(row["metrics"], views, f"raw frozen TT {directory}")
        failures = prior.common_gates(dict.fromkeys(comparison.CORNERS, views))
        failures = [r for r in failures if r.startswith("TT:") and r != "TT:hold_regression"]
        if views["setup_wns_ps"] < baseline["setup_wns_ps"] - wns - prior.tol:
            failures.append("TT:setup_budget")
        if views["setup_tns_ps"] < baseline["setup_tns_ps"] - tns - prior.tol:
            failures.append("TT:setup_tns_budget")
        if annotated != annotation:
            failures.append("changed_annotation")
        equal(row["failures"], failures, f"screen gates {directory}")

    rows, received = cfg["rows"], read(root / "screen_pool.json")
    equal(len(rows), cfg["screened"], "attempt count")
    need(len(rows) <= 32, "bounded fixed-SPEF shortlist")
    equal([row["action"] for row in rows], expected_pool[:len(rows)], "ordered nearest smaller candidates")
    for i, row in enumerate(rows, 1):
        equal(row["label"], f"screen_{i:02d}", "fixed-SPEF attempt order")
        verify_probe(row)
    passed = [row for row in rows if not row["failures"]]
    equal([row["action"] for row in passed], received, "all successful screened edits in order")
    equal((len(passed), cfg["passed"]), (18, 18), "frozen pass count")
    need(not rows[-1]["failures"], "screen stops on the 18th accepted edit")
    equal(digest(root / "screen_pool.json"), cfg["pool_sha256"], "frozen screened pool hash")
    lower = cfg["baseline"]["wall_seconds"] + sum(row["operation"]["wall_seconds"] for row in rows)
    need(math.isfinite(cfg["wall_seconds"]) and cfg["wall_seconds"] >= lower, "screen raw clock includes TT tools")
    plan = read(root / "pilot_receipt.json")
    check_bindings(plan)
    equal(plan["screen"]["sha256"], digest(root / "screen_receipt.json"), "pilot plan binds fixed screen")
    cases = plan["cases"]
    equal(len(cases), 4, "four fixed pilot cases")
    equal(cases[2:], passed[:2], "first two low-load passing edits")
    for instance, row in zip(PILOT, cases[:2], strict=True):
        equal(row["label"], f"pilot_{instance}", "the two prespecified reconvergent control instances")
        equal(row["action"], closest[instance], f"nearest compatible driver {instance}")
        verify_probe(row)
    return cases, {"attempts": len(rows), "passed": len(passed), "screen_seconds": cfg["wall_seconds"],
                   "pool_sha256": cfg["pool_sha256"], "screen_receipt_sha256": digest(root / "screen_receipt.json")}


def audit_physical(root, screen_root, prior, cases):
    pilot = MatrixAudit(root)
    final = read(root / "results.json")
    equal(final["status"], "matched", "pilot completed")
    equal(final["scope"], pilot.scope, "pilot frozen scope")
    equal(final["clock"], CLOCK, "pilot clock")
    equal(pilot.control, prior.control, "pilot frozen CONTROL")
    equal(final["control"], pilot.ref, "pilot reference binding")
    equal(pilot.ref_views, prior.ref_views, "pilot and prior three-view CONTROL metrics")
    equal(pilot.config["pilot_source"]["sha256"], digest(screen_root / "pilot_receipt.json"), "pilot plan identity")
    noop = pilot.verify_physical(root / "noop" / "receipt.json", (), noop=True)
    equal(final["shared_noop"], noop, "pilot shared no-edit preflight")
    pilot.gate_summary(final["gate"], 1.0, False)
    observed = []
    for i, (case, result) in enumerate(zip(cases, final["cases"], strict=True), 1):
        plan = case["action"]
        pilot.actions[plan["action_id"]] = plan
        directory = root / f"case_{i:02d}"
        path = directory / "receipt.json"
        equal(result["screen"], case, f"pilot keeps the preregistered action {directory}")
        measured = pilot.verify_physical(path, [plan["action_id"]])
        views = measured["views"]
        need(set(views) == set(comparison.CORNERS), f"three pilot STA views {directory}")
        logical = result["physical"]
        equal(logical["actions"], [plan["action_id"]], f"physical edit {directory}")
        equal(logical["physical_receipt"], str(path), f"physical receipt binding {directory}")
        equal(logical["from_physical_cache"], False, f"physical pilot is fresh {directory}")
        failures = measured["failures"] + pilot.setup_gates(views, 1.0, False)
        seconds, passed, proven = measured["wall_seconds"], False, None
        if failures:
            equal(logical["deferred_proof_receipt"], None, f"no SEC on a pre-SEC reject {directory}")
            need(not (directory / "sec").exists(), f"unexpected SEC attempt {directory}")
        else:
            receipt = directory / "deferred_proof.json"
            equal(logical["deferred_proof_receipt"], str(receipt), f"SEC binding {directory}")
            evidence = read(receipt)
            equal(evidence["endpoint_id"], measured["endpoint_id"], f"SEC source endpoint {directory}")
            equal(evidence["candidate"], measured["artifacts"]["v"], f"SEC exact candidate netlist {directory}")
            passed = evidence["sec_pass"]
            proven = pilot.proof(directory, evidence["operations"], evidence["candidate"], passed=passed)
            pilot.proofs[path] = evidence, proven
            seconds += evidence["wall_seconds"]
            failures.extend(evidence["failures"])
        equal(logical["failures"], failures, f"physical reasons {directory}")
        equal(result["endpoint"], {**measured["endpoint"], "valid": passed, "sec_pass": passed},
              f"pilot accepted endpoint {directory}")
        equal(logical["endpoint"], result["endpoint"], f"linked pilot endpoint {directory}")
        near(logical["wall_seconds"], seconds, f"physical pilot wall {directory}")
        for key in ("setup_wns_ps", "setup_tns_ps"):
            equal(logical[key], {name: row[key] for name, row in views.items()}, f"pilot raw {key} {directory}")
        sample = {
            "action": plan, "fanout": case["fanout"], "screen_pass": not case["failures"],
            "screen_tt_delta_ps": {key: case["metrics"][key] - prior.ref_views["TT"][key] for key in (
                "setup_wns_ps", "setup_tns_ps", "hold_wns_ps",
            )},
            "physical_delta_by_view": pilot.view_metrics(views), "area_saved": measured["area_saved"],
            "accepted": passed, "failures": failures, "sec_proven": proven, "wall_seconds": seconds,
        }
        if i <= 2:
            old_path = prior.root / "primary_tradeoff_1pct" / "single" / f"{(1, 5)[i - 1]:02d}_physical" / "receipt.json"
            old_actions = read(old_path)["actions"]
            equal(len(old_actions), 1, f"prior exact controlled edit {directory}")
            old = prior.verify_physical(old_path, old_actions)
            old_action = prior.actions[old_actions[0]]
            equal(old_action["instance"], plan["instance"], f"same high-load control instance {directory}")
            need(old_action["target_cell"].endswith("__buf_1"), f"expected aggressive prior action {directory}")
            sample["prior_aggressive"] = {
                "action": old_action, "physical_delta_by_view": prior.view_metrics(old["views"]),
                "area_saved": old["area_saved"],
            }
        observed.append(sample)
    totals = pilot.totals(list(pilot.physical))
    for key, value in totals.items():
        near(final["operations"][key], value, f"pilot count {key}")
    equal(final["operations"]["physical_cache_hits"], 0, "pilot physical cache hits")
    equal(final["operations"]["logical_requests"], 4, "all four pilot attempts")
    return {"cases": observed, "operations": totals, "results_sha256": digest(root / "results.json"),
            "config_sha256": digest(root / "config.json"), "target_area_saved": final["target_area_saved"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("screen", type=Path)
    parser.add_argument("prior", type=Path)
    parser.add_argument("--pilot", type=Path)
    args = parser.parse_args()
    screen = args.screen.resolve(strict=True)
    prior = MatrixAudit(args.prior.resolve(strict=True))
    cases, summary = audit_screen(screen, prior)
    result = {"screen": summary}
    if args.pilot is not None:
        result["physical_pilot"] = audit_physical(args.pilot.resolve(strict=True), screen, prior, cases)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
