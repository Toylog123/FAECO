#!/usr/bin/env python3
"""Evaluate checkpoint rescue only after a fresh full route reproduces a hold-only rejection."""

from argparse import ArgumentParser
from dataclasses import asdict
import math
import os
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

import probe_gcd_local_hold_preview as preview
import probe_gcd_local_route_reentry as phase
from probe_gcd_route_checkpoint_restart import run_split


HOLDOUT = Path(__file__).resolve().parents[1] / "tcad_holdout_20261123"
sys.path.insert(0, str(HOLDOUT))
from run_uart_online import UartComparison
from run_uart_rejection_dedup import seed_args


comparison, read, verify = phase.comparison, phase.read, phase.verify
HOLD_ONLY = {f"{corner}:hold_regression" for corner in comparison.CORNERS}
LIMIT = 100.0
EPS = 1e-7
UART_INDICES = (1, 4, 5)


def is_hold_only(reasons):
    return bool(reasons) and set(reasons) <= HOLD_ONLY


def evidence(label, logical_ref, physical_ref, best, **scope):
    logical, physical = (read(verify(item)) for item in (logical_ref, physical_ref))
    if (logical["actions"] != physical["actions"] or not is_hold_only(logical["failures"])
            or physical["area_saved"] <= best + EPS or logical["endpoint"]["valid"]
            or not physical["routed_to_completion"] or not physical["extracted_to_completion"]
            or physical["drc_violations"] or set(physical["views"]) != set(comparison.CORNERS)):
        raise ValueError(f"not an admissible physical hold-only target: {label}")
    return {"label": label, "actions": physical["actions"], "historical_reasons": logical["failures"],
            "potential_area_um2": physical["area_saved"], "historical_logical": logical_ref,
            "historical_physical": physical_ref, **scope}


def gcd_plan(old):
    archived = read(old / "results.json")
    protocol = read(verify(archived["protocol"]))
    scores = read(verify(protocol["score"]))
    inputs = read(verify(scores["protocol"]))
    config_path = verify(inputs["seed"])
    root = config_path.parent
    best, qualified = 0.0, []
    unique = {}
    for method in ("fixed", "faeco"):
        for index in range(1, 7):
            logical = root / f"screened/{method}/{index:02d}.json"
            physical = logical.with_name(f"{index:02d}_physical") / "receipt.json"
            row, routed = read(logical), read(physical)
            if row["endpoint"]["valid"] and row["endpoint"]["sec_pass"] and not row["failures"]:
                best = max(best, routed["area_saved"])
                qualified.append(comparison.bind(logical))
            elif is_hold_only(row["failures"]):
                unique.setdefault(tuple(row["actions"]), (logical, physical, routed["area_saved"]))
    targets = [evidence("gcd_triple", comparison.bind(log), comparison.bind(phy), best)
               for log, phy, area in unique.values() if area > best + EPS]
    if len(targets) != 1 or not math.isclose(best, 15.0144, abs_tol=EPS, rel_tol=0):
        raise ValueError("the GCD historical hold-only frontier changed")
    return {"design": "gcd", "historical_best_um2": best, "source": comparison.bind(config_path),
            "reference": inputs["reference"], "pool": inputs["pool"], "qualified": qualified,
            "targets": targets, "feature_source": protocol["score"], "prior_run": comparison.bind(old / "results.json")}


def uart_plan(root, dedup, reserved, probe):
    config = root / "protocol.json"
    proto = read(config)
    root_audit = root / "independent_verification.json"
    audit = read(root_audit)
    if verify(audit["producer_protocol"]) != config or len(audit["verified_cells"]) != 6:
        raise ValueError("the selected UART ledger was not audited")
    best = max(item["best"]["area_saved"] for item in audit["verified_cells"])
    bindings = [comparison.bind(root_audit)]
    for path in (dedup, reserved):
        verified = path / "independent_verification.json"
        row = read(verified)
        source = read(verify(row["protocol"]))
        if any(proto[k] != source[k] for k in ("seed", "reference", "gate", "ordered_pool")):
            raise ValueError("the UART follow-up audit has a different physical contract")
        best = max(best, *(arm["best"]["area_saved"] for arm in row["arms"]))
        bindings.append(comparison.bind(verified))
    directed = probe / "targeted_verification.json"
    row = read(directed)
    if row["proof_count"] != [567, 0] or row["candidate"]["failures"]:
        raise ValueError("UART directed endpoint was not qualified")
    best = max(best, read(verify(row["candidate"]["physical_receipt"]))["area_saved"])
    bindings.append(comparison.bind(directed))
    if not math.isclose(best, 0.23328, abs_tol=EPS, rel_tol=0):
        raise ValueError("the highest audited admissible UART endpoint changed")
    unique = set()
    for cell in audit["verified_cells"]:
        arm = root / f"cell_{cell['cell']:02d}" / cell["method"]
        for request in cell["requests"]:
            if not request["logical_finished"]:
                continue
            row = read(arm / f"{request['id']:02d}/result.json")
            if is_hold_only(row["failures"]) and read(verify(row["physical_receipt"]))["area_saved"] > best + EPS:
                unique.add(tuple(row["actions"]))
    targets = []
    for index in UART_INDICES:
        path = root / f"cell_02/fixed_online/{index:02d}/result.json"
        physical = read(path)["physical_receipt"]
        scope = verify(physical).with_name("routing_scope.json")
        targets.append(evidence(f"uart_{index:02d}", comparison.bind(path), physical, best,
                                historical_scope=comparison.bind(scope)))
    if unique != {tuple(target["actions"]) for target in targets}:
        raise ValueError("candidate list is incomplete for the audited UART pool")
    return {"design": "uart", "source": comparison.bind(verify(proto["seed"])), "reference": proto["reference"],
            "historical_best_um2": best, "historical_online_protocol": comparison.bind(config),
            "qualified": bindings, "targets": targets}


def gcd_evaluator(plan, matrix, out, libraries, control, tools, fast):
    runtime = SimpleNamespace(out=out, orfs=fast.parents[2], pdk=matrix["pdk"], route_mode="local",
                              droute_iters=64, embedded_guides=True, single_pin_access=True, zero_reextract=False,
                              report_setup_endpoints=True, threads=matrix["methods_route_threads"], clock_period_ps=matrix["original_clock_period_ps"],
                              openroad=tools["openroad"], sta=tools["opensta"], sec=tools["sec"],
                              route_timeout=LIMIT, sta_timeout=20.0, sec_timeout=30.0)
    masters = comparison.logical_masters(control["v"], comparison.liberty_areas(libraries["TT"]))
    reference = read(verify(plan["reference"]))["views"]
    pool = [comparison.PhysicalAction(**row) for row in read(verify(plan["pool"]))]
    return comparison.Evaluator(runtime, control, libraries, masters, reference, pool, matrix["scope"])


def reroute_scope(plan, candidate, evaluator, runner):
    if plan["design"] == "gcd":
        features = read(verify(plan["feature_source"]))["features"]
        return preview.edit_scope(features, evaluator.control["def"], candidate["actions"])
    saved = read(verify(candidate["historical_scope"]))
    _, nets = runner.direct_nets(candidate["actions"])
    released = set(saved["released_neighbors"])
    fixed = {net: runner.nets[net] for net in saved["fixed_nets"]}
    if nets | released != set(saved["expected_touched_nets"]) or fixed.keys() & (nets | released):
        raise ValueError("the original UART net window does not match the proposed actions")
    return nets, set(), released, fixed


def fresh_direct(candidate, evaluator, runner, out):
    actions = tuple(candidate["actions"])
    if runner is None:
        return phase.run_cell(evaluator, out, actions, "direct", {})
    start = preview.geometry.raw_seconds()
    runner.use_preview = True
    _, logical = runner.attempt(actions, out)
    actual = read(verify(logical["physical_receipt"]))
    if logical["actions"] != candidate["actions"] or actual["actions"] != candidate["actions"]:
        raise ValueError("the fresh full route did not apply the selected UART actions")
    elapsed = preview.geometry.raw_seconds() - start
    return {"mode": "direct_original_online", "actions": candidate["actions"], "failures": logical["failures"],
            "views": actual["views"], "physical": logical["physical_receipt"], "logical": comparison.bind(out / "result.json"),
            "elapsed_raw_seconds": elapsed, "conditional_sec_seconds": elapsed}


def rescue(plan, candidate, evaluator, runner, out):
    start = preview.geometry.raw_seconds()
    same_scope = reroute_scope(plan, candidate, evaluator, runner)
    with patch.object(preview, "edit_scope", return_value=same_scope), \
         patch.object(phase, "FIXED_COUNT", len(same_scope[-1])), patch.object(comparison, "run_process", run_split), \
         patch.object(evaluator.args, "route_timeout", LIMIT):
        result = phase.run_cell(evaluator, out, tuple(candidate["actions"]), "resume", {})
    elapsed = preview.geometry.raw_seconds() - start
    result["trigger_additional_raw_seconds"] = elapsed - (result["elapsed_raw_seconds"] - result["conditional_sec_seconds"])
    result["all_diagnostic_checks_raw_seconds"] = elapsed
    complete = read(verify(result["physical"]))
    if not result["failures"] and not math.isclose(complete["area_saved"], candidate["potential_area_um2"], abs_tol=EPS, rel_tol=0):
        raise ValueError("rescue altered the target area independently of the bound actions")
    result["qualified_area_um2"] = complete["area_saved"] if not result["failures"] else None
    return result


def run_cases(plan, evaluator, runner, out):
    results = []
    for proposal in plan["targets"]:
        root = out / proposal["label"]
        root.mkdir()
        direct = fresh_direct(proposal, evaluator, runner, root / "direct")
        physical = read(verify(direct["physical"]))
        record = {"proposal": proposal, "fresh_direct": direct, "rescue": None, "confirmation": None}
        if (is_hold_only(direct["failures"]) and physical["drc_violations"] == 0 and
                physical["routed_to_completion"] and physical["extracted_to_completion"] and
                set(direct["views"]) == set(comparison.CORNERS)):
            attempt = rescue(plan, proposal, evaluator, runner, root / "restore")
            record["rescue"] = attempt
            area = attempt["qualified_area_um2"]
            if area is not None and area > plan["historical_best_um2"] + EPS:
                confirm = rescue(plan, proposal, evaluator, runner, root / "confirmation")
                record["confirmation"] = {"new_run": confirm,
                                          "equivalence": phase.physical_equivalence(attempt, confirm)}
        results.append(record)
        comparison.save(out / "progress.json", results)
        retried = record["rescue"]
        print(proposal["label"], "direct", direct["failures"], "rescue", None if retried is None else
              (retried["failures"], round(retried["trigger_additional_raw_seconds"], 3), retried["qualified_area_um2"]), flush=True)
    frontier = max(plan["historical_best_um2"], *(row["rescue"]["qualified_area_um2"] or 0.0
                    for row in results if row["rescue"] is not None), 0.0)
    added = math.fsum(row["rescue"]["trigger_additional_raw_seconds"] for row in results if row["rescue"] is not None)
    return {"cases": results, "historical_best_um2": plan["historical_best_um2"], "best_with_reentry_um2": frontier,
            "gain_over_best_um2": frontier - plan["historical_best_um2"], "rescue_triggered": sum(row["rescue"] is not None for row in results),
            "rescue_qualified": sum(row["rescue"] is not None and row["rescue"]["qualified_area_um2"] is not None for row in results),
            "paid_additional_seconds": added}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("design", choices=("gcd", "uart"))
    parser.add_argument("output", type=Path)
    parser.add_argument("--source", nargs="+", type=Path, required=True)
    args = parser.parse_args()
    roots = [root.resolve(strict=True) for root in args.source]
    if len(roots) != (1 if args.design == "gcd" else 4):
        parser.error("give GCD preview or UART online/dedup/reservation/directed roots in that order")
    plan = gcd_plan(roots[0]) if args.design == "gcd" else uart_plan(*roots)
    seed = verify(plan["source"])
    matrix = read(seed)
    assets = matrix["bindings"]
    tools = {name: verify(ref) for name, ref in assets["tools"].items()}
    flow = {name: verify(ref) for name, ref in assets["flow"].items()}
    control = {name: verify(ref) for name, ref in assets["control"].items()}
    libraries = {corner: [verify(ref) for ref in refs] for corner, refs in assets["used_libraries"].items()}
    out = args.output.resolve()
    out.mkdir()
    with preview.geometry.bind_runtime(args.design, flow["fastroute.tcl"]):
        runner = None
        if args.design == "gcd":
            affinity = matrix["cpu_affinity"]
            evaluator = gcd_evaluator(plan, matrix, out, libraries, control, tools, flow["setRC.tcl"])
            setup = phase.sweep.gate_summary(phase.sweep.budget_gate(evaluator, 1.0, False), evaluator.ref_views)
        else:
            source = read(verify(plan["historical_online_protocol"]))
            affinity = source["affinity"]
            runtime = seed_args(matrix, source)
            runner = UartComparison(runtime, seed.parent, out, source["screen_input"], source["charged_screening_seconds_per_arm"])
            evaluator = runner.eval
            setup = source["gate"]
            if runner.config["gate"] != setup:
                raise ValueError("UART gate changed from the historically audited online experiment")
        if sorted(os.sched_getaffinity(0)) != affinity:
            raise ValueError("the experiment must use the original design CPU set")
        protocol = out / "rescue_protocol.json"
        comparison.save(protocol, {**plan, "driver": comparison.bind(Path(__file__).resolve()),
                                   "reentry_core": comparison.bind(Path(phase.__file__).resolve()),
                                   "split_driver": comparison.bind(Path(run_split.__code__.co_filename).resolve()),
                                   "gate_setup": setup, "hold_ps": preview.hold_floor(evaluator.ref_views, comparison.PS_TOLERANCE, 0.0),
                                   "rescue_route_timeout": LIMIT, "affinity": affinity, "threads": evaluator.args.threads,
                                   "trigger": "fresh same-candidate full route rejects only on relative hold"})
        # The original direct attempt retains its configuration, including route timeout.
        # A separately metered rescue policy limits the two process-lifetimes jointly.
        result = run_cases(plan, evaluator, runner, out)
    comparison.save(out / "results.json", {"protocol": comparison.bind(protocol), **result})


if __name__ == "__main__":
    main()
