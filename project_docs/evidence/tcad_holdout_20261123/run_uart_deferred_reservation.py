#!/usr/bin/env python3
"""Compare an optional last-slot hold-deferred candidate against two UART baselines."""

from argparse import ArgumentParser
from pathlib import Path

from run_uart_online import UartComparison, comparison, read, verify
from run_uart_rejection_dedup import run_variant, seed_args
from run_screened_matrix import bind_runtime


ORDER = ("dedup", "reserved", "fixed_online", "fixed_online", "reserved", "dedup")
RULE = "on the last physical slot: untested hold-deferred singleton, ordered by area, incident-cap priority, input rank"


def enable_reservation(search):
    def dispatch(*args, **kwargs):
        return search(*args, **kwargs, reserve_deferred_singleton=True)

    return dispatch


def run_reserved(runner, reference):
    native = comparison.adaptive_batch_recovery
    reserved_search = enable_reservation(native)
    observations = []

    def record(*args, **kwargs):
        result = reserved_search(*args, **kwargs)
        observations.extend({"physical_request": index, "action": row["reserved_deferred_singleton"],
                             "actions": row["actions"]}
                            for index, row in enumerate(result["trace"], 1)
                            if "reserved_deferred_singleton" in row)
        return result

    comparison.adaptive_batch_recovery = record
    try:
        summary, skipped = run_variant(runner, reference)
    finally:
        comparison.adaptive_batch_recovery = native
    comparison.save(runner.output / "reservation.json", observations)
    return summary, skipped


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("source_run", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = args.source_run.resolve(strict=True) / "protocol.json"
    previous = read(source)
    previous_audit = source.with_name("independent_verification.json")
    audited = read(previous_audit)
    if verify(audited["protocol"]) != source or len(audited["arms"]) != 4:
        raise ValueError("expected the complete audited UART rejection-reuse experiment")
    seed_path = verify(previous["seed"])
    seed = read(seed_path)
    runtime = seed_args(seed, previous)
    out = args.output.resolve()
    out.mkdir(parents=True)
    results = []
    with bind_runtime("uart", verify(seed["bindings"]["flow"]["fastroute.tcl"])):
        runner = UartComparison(runtime, seed_path.parent, out, previous["screen_input"],
                                previous["charged_screening_seconds_per_arm"])
        runner.config.update({"source_protocol": comparison.bind(source),
                              "source_verification": comparison.bind(previous_audit), "order": ORDER,
                              "reservation_rule": RULE, "fixed_area_reference_um2": 0.23328})
        module_paths = (Path(__file__).resolve(), Path(run_variant.__code__.co_filename).resolve(),
                        Path(comparison.adaptive_batch_recovery.__code__.co_filename).resolve())
        for path in module_paths:
            runner.config["sources"][path.name] = comparison.bind(path)
        comparison.save(out / "protocol.json", runner.config)
        reference = runner.qualify_zero()
        for index, entry in enumerate(ORDER, 1):
            runner.output = out / f"cell_{index:02d}"
            runner.output.mkdir()
            print(f"UART last-slot cell {index}: {entry}", flush=True)
            if entry == "fixed_online":
                summary, skipped = runner.arm(entry, reference), 0
            elif entry == "reserved":
                summary, skipped = run_reserved(runner, reference)
            else:
                summary, skipped = run_variant(runner, reference)
            results.append({"cell": index, "variant": entry, "method": summary["method"],
                            "reused_rejections": skipped, "result": summary})
            comparison.save(out / "results.json", results)
            print(entry, summary["window"]["area_saved"], summary["window"]["time_to_target_seconds"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
