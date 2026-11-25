#!/usr/bin/env python3
"""Physically test a post-hoc UART proposal at the fixed-batch area gain."""

from argparse import ArgumentParser
from pathlib import Path

from run_uart_rejection_dedup import comparison, read, seed_args, verify
from run_uart_online import UartComparison
from run_aes_incident_priority_matched_v2 import process_ledger
from run_screened_matrix import bind_runtime, raw_seconds


ADDITION = "_0886_"
BASE_INSTANCES = ("_0814_", "_1027_")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("dedup_run", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = args.dedup_run.resolve(strict=True) / "protocol.json"
    previous = read(source)
    audited = source.with_name("independent_verification.json")
    confirmed = read(audited)
    if verify(confirmed["protocol"]) != source or len(confirmed["arms"]) != 4:
        raise ValueError("expected the complete audited UART comparison")
    seed_path = verify(previous["seed"])
    seed = read(seed_path)
    runtime = seed_args(seed, previous)
    out = args.output.resolve()
    out.mkdir(parents=True)
    with bind_runtime("uart", verify(seed["bindings"]["flow"]["fastroute.tcl"])):
        runner = UartComparison(runtime, seed_path.parent, out, previous["screen_input"],
                                previous["charged_screening_seconds_per_arm"])
        pool = {comparison.canonical_odb_name(action.instance): action for action in runner.pool}
        prefix = sorted(pool[name].action_id for name in BASE_INSTANCES)
        if any(prefix not in [point["actions"] for point in row["accepted"]] for row in confirmed["arms"]):
            raise ValueError("the common two-gate prefix was not accepted in all four arms")
        proposal = tuple(sorted((*prefix, pool[ADDITION].action_id)))
        predicted = sum(pool[name].estimated_area_saving for name in (*BASE_INSTANCES, ADDITION))
        protocol = {**runner.config, "source_protocol": comparison.bind(source),
                    "source_verification": comparison.bind(audited), "proposal": proposal,
                    "estimated_area_gain": predicted, "maximum_logical_requests": 1,
                    "scope": "post-hoc fixed-area candidate; no automatic scheduling or matched runtime claim",
                    "driver": comparison.bind(Path(__file__).resolve())}
        comparison.save(out / "protocol.json", protocol)
        reference = runner.qualify_zero()
        runner.use_preview = True
        started = raw_seconds()
        wall_limit = previous["wall_window_seconds_including_screen"]
        with process_ledger(out / "subprocesses.json", started + wall_limit - runner.screen):
            endpoint, result = runner.attempt(proposal, out / "trial")
        comparison.save(out / "summary.json", {
            "trial": comparison.bind(out / "trial/result.json"), "estimated_area_gain": predicted,
            "physical_area_gain": reference.area - endpoint.area, "qualified": endpoint.valid and endpoint.sec_pass,
            "failures": result["failures"], "evaluation_with_screen_raw_seconds": raw_seconds() - started + runner.screen,
        })
        print(proposal, reference.area - endpoint.area, result["failures"], flush=True)


if __name__ == "__main__":
    main()
