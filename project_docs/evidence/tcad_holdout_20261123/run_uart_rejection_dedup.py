#!/usr/bin/env python3
"""Replay UART FAECO with and without exact completed setup-rejection reuse."""

from argparse import ArgumentParser
from inspect import signature
from pathlib import Path
from types import SimpleNamespace

from run_uart_online import UartComparison, comparison, read, verify
from run_aes_greedy_matched import run_online_arm
from run_screened_matrix import bind_runtime, raw_seconds


ORDER = ("original", "dedup", "dedup", "original")
SETUP_REASONS = {f"{corner}:{kind}" for corner in comparison.CORNERS
                 for kind in ("setup_budget", "setup_tns_budget")}


def setup_only_rejection(endpoint, actions):
    final = Path(endpoint.evidence_id)
    result = read(final.parent / "result.json")
    failures = set(result["failures"])
    if result["actions"] != list(actions) or result["scope_id"] != endpoint.scope_id:
        raise ValueError("result does not bind the measured cumulative action and scope")
    if not failures or not failures <= SETUP_REASONS:
        return None
    receipt = verify(result["physical_receipt"])
    assessment = read(final / "assessment.json")
    if receipt != final / "receipt.json" or set(read(receipt)["views"]) != set(comparison.CORNERS):
        raise ValueError("setup rejection did not complete all three physical timing views")
    if assessment["unlocked"]["drc_markers"] or set(assessment["failures"]) != failures:
        raise ValueError("setup rejection did not originate from the clean measured endpoint")
    return comparison.bind(final.parent / "result.json")


def run_variant(runner, reference):
    measured = {}
    skipped = []
    original = comparison.run_method

    def dispatch(method, base, pool, evaluate, cap, width, **kwargs):
        if method != "faeco":
            raise ValueError("only the FAECO scheduler is varied in this experiment")

        def evaluate_and_remember(actions):
            endpoint = evaluate(actions)
            receipt = setup_only_rejection(endpoint, actions)
            if receipt is not None:
                measured[actions] = receipt
            return endpoint

        def known_rejection(actions):
            if actions not in measured:
                return False
            skipped.append({"actions": list(actions), "rejected_receipt": measured[actions],
                            "skipped_raw": raw_seconds()})
            return True

        return comparison.adaptive_batch_recovery(
            base, pool, evaluate_and_remember, kwargs["policy"], max_evaluations=cap, batch_size=width,
            defer_split_for=kwargs["defer_split_for"], priority_after_defer=kwargs["priority_after_defer"],
            known_split_rejection=known_rejection,
        )

    comparison.run_method = dispatch
    try:
        summary = run_online_arm(runner, "faeco", reference)
    finally:
        comparison.run_method = original
    comparison.save(runner.output / "reused_rejections.json", skipped)
    return summary, len(skipped)


def seed_args(seed, protocol):
    assets = seed["bindings"]
    control = {name: verify(item) for name, item in assets["control"].items()}
    tools = {name: verify(item) for name, item in assets["tools"].items()}
    return SimpleNamespace(
        pdk="asap7", out=None, threads=seed["methods_route_threads"],
        clock_period_ps=read(verify(assets["qualification_receipt"]))["source_sdc_semantics"]["period_ps"],
        openroad=tools["openroad"], sta=tools["opensta"], sec=tools["sec"],
        orfs=verify(assets["flow"]["setRC.tcl"]).parents[2], route_mode="local",
        droute_iters=seed["route_drt_iters"], embedded_guides=True, route_guide=None,
        zero_reextract=False, single_pin_access=True, route_timeout=seed["route_timeout_seconds"],
        sta_timeout=seed["sta_timeout_seconds_per_view"], sec_timeout=seed["sec_timeout_seconds"],
        report_setup_endpoints=True, control_dir=control["odb"].parent,
        control_drc=verify(assets["control_drc"]), max_evals=protocol["logical_dispatch_cap"],
        batch_size=protocol["batch_size"], screen_pool=verify(protocol["screen_input"]["pool"]),
    )


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("source_run", type=Path)
    parser.add_argument("output", type=Path)
    ns = parser.parse_args()
    if "known_split_rejection" not in signature(comparison.adaptive_batch_recovery).parameters:
        parser.error("the opt-in scheduler change is not available on this checkout")
    source = ns.source_run.resolve(strict=True) / "protocol.json"
    previous = read(source)
    seed_path = verify(previous["seed"])
    seed = read(seed_path)
    args = seed_args(seed, previous)
    output = ns.output.resolve()
    output.mkdir(parents=True)
    results = []
    with bind_runtime("uart", verify(seed["bindings"]["flow"]["fastroute.tcl"])):
        runner = UartComparison(args, seed_path.parent, output, previous["screen_input"],
                                previous["charged_screening_seconds_per_arm"])
        runner.config.update({"source_protocol": comparison.bind(source), "order": ORDER,
                              "variant": "same-arm completed setup-only rejections reused without physical dispatch"})
        driver = Path(__file__).resolve()
        scheduler = Path(comparison.adaptive_batch_recovery.__code__.co_filename).resolve()
        for ref in (driver, scheduler):
            runner.config["sources"][ref.name] = comparison.bind(ref)
        comparison.save(output / "protocol.json", runner.config)
        reference = runner.qualify_zero()
        for index, variant in enumerate(ORDER, 1):
            runner.output = output / f"cell_{index:02d}"
            runner.output.mkdir()
            print(f"UART rejection reuse cell {index}: {variant}", flush=True)
            summary, skipped = (run_variant(runner, reference) if variant == "dedup"
                                else (run_online_arm(runner, "faeco", reference), 0))
            results.append({"cell": index, "variant": variant, "method": "faeco",
                            "reused_rejections": skipped, "result": summary})
            comparison.save(output / "results.json", results)
            print(summary["window"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
