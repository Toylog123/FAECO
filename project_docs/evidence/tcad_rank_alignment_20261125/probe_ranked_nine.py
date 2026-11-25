#!/usr/bin/env python3
"""Replay the recorded RISC-V sensitivity ranking and evaluate exactly its first nine edits."""

from argparse import ArgumentParser
import json
from pathlib import Path
import os
import sys
from types import SimpleNamespace


EVIDENCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVIDENCE / "tcad_wallclock_schedule_20261125"))

from run_qualified_wallclock import (  # noqa: E402
    QualifiedWallclockComparison, bind_runtime, comparison, prepare_binding,
    process_ledger, qualified_process_clock, rank_qualified_actions, raw_seconds,
    read, verify,
)
from run_aes_protected_online import WallWindowEnded  # noqa: E402


RUN_SHA = "a768316f012f7386c2c1d31e43829b9490c0da82174ab884dc3b6634ea5f2dae"
RANK_SHA = "200b402d5af592a794c05984524d6429a8ef8f61397bd2cfac8d4aa9f5a58bf0"
RAW_LIMIT = 720.0


def runtime_args(seed, protocol, output):
    assets = seed["bindings"]
    tools = {key: verify(ref) for key, ref in assets["tools"].items()}
    flow = {key: verify(ref) for key, ref in assets["flow"].items()}
    control = {key: verify(ref) for key, ref in assets["control"].items()}
    if (seed["pdk"], seed["top"], seed["methods_route_threads"], seed["route_drt_iters"],
        seed["route_timeout_seconds"], seed["sta_timeout_seconds_per_view"], seed["sec_timeout_seconds"],
        seed["route_mode"], seed["single_pin_access"], seed["report_setup_endpoints"],
        seed["original_clock_period_ps"]) != ("sky130hd", "riscv", 4, 64, 240, 180, 210, "local", True, True, 6000):
        raise ValueError("the saved RISC-V v2 physical recipe differs from the registered probe")
    return SimpleNamespace(
        top=seed["top"], pdk=seed["pdk"], out=output, control_dir=control["odb"].parent,
        control_drc=verify(assets["control_drc"]), original_sdc=verify(assets["original_sdc"]),
        views_json=verify(assets["qualification_receipt"]), openroad=tools["openroad"],
        sta=tools["opensta"], sec=tools["sec"], orfs=flow["setRC.tcl"].parents[2],
        routing_config=flow["fastroute.tcl"], helper_source=[], shortest_clock_period_ps=None,
        clock_period_ps=seed["original_clock_period_ps"], max_evals=1, batch_size=protocol["batch_size"],
        threads=seed["methods_route_threads"], route_mode=seed["route_mode"], route_guide=None,
        embedded_guides=True, single_pin_access=True, zero_reextract=False,
        report_setup_endpoints=True, droute_iters=seed["route_drt_iters"],
        route_timeout=seed["route_timeout_seconds"], sta_timeout=seed["sta_timeout_seconds_per_view"],
        sec_timeout=seed["sec_timeout_seconds"], screen_pool=verify(protocol["screen_input"]["pool"]),
        screen_receipt=verify(protocol["screen_input"]["receipt"]),
    )


def bind_probe(source, output):
    protocol_path = source / "protocol.json"
    verification = source / "independent_verification.json"
    if comparison.sha(protocol_path) != RUN_SHA or verify(read(verification)["protocol"]) != protocol_path:
        raise ValueError("expected the fully validated RISC-V v2 protocol")
    protocol = read(protocol_path)
    for ref in protocol["sources"].values():
        verify(ref)
    if sorted(os.sched_getaffinity(0)) != protocol["affinity"] or protocol["affinity"] != list(range(6)):
        raise ValueError("the RISC-V v2 probe must use the original CPU 0–5 group")
    arms = read(verification)["arms"]
    if len(arms) != 6 or read(verification)["verified_prefix"] != 6:
        raise ValueError("expected all six verified v2 arms")
    strong = next(row for row in arms if row["direction"] == "forward" and row["strategy"] == "single_sensitivity")
    source_arm = source / f"cell_{strong['cell']:02d}" / "single"
    ranking_path = source_arm / "sensitivity/ranking.json"
    if comparison.sha(ranking_path) != RANK_SHA:
        raise ValueError("the archived forward sensitivity ranking changed")
    ranking = read(ranking_path)
    rank_log = verify(ranking["log"])
    verify(ranking["script"])
    seed_path = verify(protocol["seed"])
    seed = read(seed_path)
    args = runtime_args(seed, protocol, output)
    qualified, bindings, clock = prepare_binding(args)
    if clock != protocol["period_basis"] or qualified["status"] != "hold_qualified":
        raise ValueError("the original P0 clock or qualification changed")
    for name, ref in ranking["control"].items():
        if ref != bindings["control"][name]:
            raise ValueError(f"ranking does not use the frozen {name}")
    if ranking["libraries"] != seed["bindings"]["used_libraries"]["TT"]:
        raise ValueError("ranking does not use the saved TT Liberty")
    zero_path = source / "preflight/zero/result.json"
    zero = read(zero_path)
    zero_physical = read(verify(zero["physical_receipt"]))
    if zero["actions"] or zero["failures"] or not zero["endpoint"]["valid"] or not zero["endpoint"]["sec_pass"]:
        raise ValueError("the shared strict zero was not accepted")
    if zero["endpoint"]["scope_id"] != seed["scope"] or zero_physical["control_sdc"] != bindings["control"]["sdc"]:
        raise ValueError("shared zero does not use the frozen scope and constraints")
    runner = QualifiedWallclockComparison(args, seed_path.parent, output, protocol["screen_input"],
                                          protocol["charged_screening_seconds_per_arm"])
    if runner.config["gate"] != protocol["gate"] or runner.config["ordered_pool"] != protocol["ordered_pool"]:
        raise ValueError("probe does not reproduce the original pool and acceptance envelope")
    replayed = rank_qualified_actions(runner.pool, rank_log.read_text(), runner.eval.ref_views["TT"]["setup_wns_ps"])
    for key, value in replayed.items():
        if value != ranking[key]:
            raise ValueError(f"archived ranking is not reproducible: {key}")
    order = ranking["ordered_action_ids"][:9]
    prefix = tuple(sorted(order))
    if len(set(order)) != 9 or any(tuple(sorted(order[:k])) not in {tuple(row["actions"]) for row in strong["accepted"]}
                                  for k in (3, 6, 7)):
        raise ValueError("nine-action tuple does not extend the recorded sensitivity path")
    _, incident = runner.direct_nets(prefix)
    return runner, prefix, {
        "probe": comparison.bind(Path(__file__)), "source_protocol": comparison.bind(protocol_path),
        "source_verification": comparison.bind(verification), "forward_ranking": comparison.bind(ranking_path),
        "rank_script": ranking["script"], "rank_log": ranking["log"], "source_shared_zero": comparison.bind(zero_path),
        "shared_zero_physical": zero["physical_receipt"], "reference_area_um2": zero["endpoint"]["area"],
        "physical_recipe": runner.config, "ranked_action_ids": order, "cumulative_actions": prefix,
        "direct_signal_nets": sorted(incident), "raw_candidate_limit_seconds": RAW_LIMIT,
        "stage_limits_seconds": {"DRT_RCX": args.route_timeout, "STA_per_view": args.sta_timeout, "SEC": args.sec_timeout},
        "scope": "single fixed cumulative probe from frozen CONTROL; prior ranking, screening and shared zero reused",
        "diagnostic_sec": "prove the exact routed netlist of a completed DRT/RCX result when a rejection bypassed ordinary SEC",
    }


def run_probe(runner, actions, output, registration):
    runner.use_preview = True
    started = raw_seconds()
    ledger = output / "subprocesses.json"
    result = {"protocol": comparison.bind(registration), "status": "incomplete", "diagnostic_SEC": None}
    try:
        with qualified_process_clock(), process_ledger(ledger, started + RAW_LIMIT):
            endpoint, record = runner.attempt(actions, output / "trial")
            physical = read(verify(record["physical_receipt"]))
            qualified = endpoint.valid and endpoint.sec_pass
            result.update(status="qualified" if qualified else "rejected", logical=comparison.bind(output / "trial/result.json"),
                          physical=record["physical_receipt"], failures=record["failures"],
                          released_neighbors=read(output / "trial/retry_decision.json")["released_neighbors"]
                          if (output / "trial/retry_decision.json").exists() else [],
                          physical_area_saved_um2=physical.get("area_saved"),
                          qualified_area_saved_um2=physical.get("area_saved") if qualified else None,
                          physical_evaluation_raw_seconds=raw_seconds() - started)
            netlist = physical.get("artifacts", {}).get("v")
            if (record["failures"] and not record["proof_operations"] and netlist
                    and physical.get("routed_to_completion") and physical.get("extracted_to_completion")):
                diagnostic = output / "diagnostic_sec"
                diagnostic.mkdir()
                candidate = verify(netlist)
                operations = {}
                passed = runner.eval.proof(candidate, diagnostic, operations)
                proof_path = diagnostic / "sec/receipt.json"
                proof = read(proof_path) if proof_path.exists() else {}
                if passed and (not proof.get("passed") or proof.get("proven", 0) <= 0 or proof.get("unproven") != 0
                               or proof.get("gate") != physical["artifacts"]["v"]
                               or proof.get("gold") != comparison.bind(runner.eval.control["v"])):
                    raise ValueError("diagnostic equivalence proof does not bind the exact routed netlists")
                result["diagnostic_SEC"] = {"passed": passed, "operations": operations,
                                            "proof": comparison.bind(proof_path) if proof_path.exists() else None}
    except WallWindowEnded:
        result["window_exhausted"] = True
    finally:
        result["elapsed_raw_seconds"] = raw_seconds() - started
        result["subprocesses"] = comparison.bind(ledger) if ledger.exists() else None
        comparison.save(output / "results.json", result)
    print(result["status"], result.get("failures"), output / "results.json", flush=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="original matrix_qualified_v2 run")
    parser.add_argument("output", type=Path)
    parser.add_argument("--prepare", action="store_true", help="write the input-bound manifest without tools")
    ns = parser.parse_args()
    source, output = ns.source.resolve(strict=True), ns.output.resolve()
    if output.is_relative_to(source):
        parser.error("probe outputs must be separate from the frozen matrix")
    registration = output / "preregistration.json"
    with bind_runtime("riscv", None):
        runner, actions, manifest = bind_probe(source, output)
    if ns.prepare:
        output.mkdir(parents=True, exist_ok=True)
        if registration.exists():
            raise ValueError("probe already has a preregistration")
        comparison.save(registration, manifest)
        print(f"preregistered {len(actions)} actions and {len(manifest['direct_signal_nets'])} direct nets: {registration}", flush=True)
        return
    if read(registration) != json.loads(json.dumps(manifest)):
        raise ValueError("probe inputs differ from preregistration")
    if (output / "trial").exists() or (output / "results.json").exists():
        raise ValueError("probe output already contains an attempted trial")
    with bind_runtime("riscv", runner.flow["fastroute.tcl"]):
        run_probe(runner, actions, output, registration)


if __name__ == "__main__":
    main()
