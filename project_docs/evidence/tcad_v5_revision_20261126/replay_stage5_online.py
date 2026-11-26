#!/usr/bin/env python3
"""Replay all three frozen Stage 5 online arms on an isolated rebuilt reference."""

import argparse
from dataclasses import asdict
from hashlib import sha256
import math
import os
from pathlib import Path

import replay_stage5_fixed_first as first


FIRST_DRIVER_SHA = "98bab30663853096157cca2ce10775a5099ed9871ae5c20378a62eef90c5b321"


def replay(stage, rebuilt, output, frozen):
    control = first.rebuilt_control(stage, rebuilt, frozen)
    variant = stage.VARIANTS["tc40ns_mmmc_drv"]
    args = stage.candidate_args(rebuilt, control, variant)
    output.mkdir()
    stage.cmp.save(output / "replay_protocol.json", {
        "source_lineage": first.LINEAGE,
        "driver": stage.cmp.bind(Path(__file__)),
        "input_validator": stage.cmp.bind(Path(first.__file__)),
        "historical_state": stage.cmp.bind(frozen["state_file"]),
        "historical_archive": stage.cmp.bind(frozen["archive_file"]),
        "historical_protocol": frozen["state"]["protocol"],
        "rebuilt_qualification": stage.cmp.bind(args.views_json),
        "expected_rank": frozen["state"]["rank_order"],
        "ordered_arms": list(stage.STRATEGIES),
        "window_s": stage.LIMIT_S,
        "namespace": {kind: os.readlink(f"/proc/self/ns/{kind}") for kind in ("user", "mnt", "net")},
        "pid": os.getpid(),
        "affinity": sorted(os.sched_getaffinity(0)),
    })
    print(f"[isolated Stage 5] start fresh screen and strict zero in {output}", flush=True)
    with (stage.bind_runtime(stage.TOP, stage.ROUTING), stage.qualified.qualified_ranking(),
          stage.qualified.qualified_process_clock()):
        runner = stage.prepare_search(output, args)
        protocol = output / "search_protocol.json"
        stage.cmp.save(protocol, runner.config)
        first.check_policy(runner.config, frozen["protocol"])
        reference = stage.strict_zero(output, runner)
        metrics = ("area", "wns_ns", "tns_ns", "hold_wns_ns")
        if any(not math.isclose(getattr(reference, key), frozen["state"]["reference"][key],
                                rel_tol=0.0, abs_tol=1e-9) for key in metrics):
            raise ValueError("fresh strict zero differs from the published Stage 5 reference")
        power_dir = stage.next_attempt(output / "reference_power")
        ref_odb, ref_spef = (runner.eval.control[key] for key in ("odb", "spef"))
        ref_power = stage.measure_tt_power(ref_odb, ref_spef, args.control_dir / "6_final.sdc",
                                           stage.SKY_CORNER_LIBS["TT"], power_dir, "reference")
        power_path = output / "reference_power.json"
        stage.cmp.save(power_path, ref_power)
        state = {
            "status": "running",
            "replay_protocol": stage.cmp.bind(output / "replay_protocol.json"),
            "qualification": stage.cmp.bind(args.views_json),
            "protocol": stage.cmp.bind(protocol),
            "strict_zero": stage.cmp.bind(output / "strict_zero.json"),
            "reference": asdict(reference),
            "reference_power": stage.cmp.bind(power_path),
            "screened_pool_size": len(runner.pool),
            "rank_order": frozen["state"]["rank_order"],
            "arms": {},
        }
        progress = output / "stage5_progress.json"
        expected_rank = {"order": state["rank_order"]}
        for arm in stage.STRATEGIES:
            runner.output = stage.next_attempt(output / "arms" / arm)
            state["active_arm"] = {"name": arm, "path": str(runner.output)}
            stage.cmp.save(progress, state)
            state["arms"][arm] = stage.run_arm(runner, reference, arm, expected_rank, ref_power)
            state["active_arm"] = None
            stage.cmp.save(progress, state)
        state["status"] = "finished"
        stage.cmp.save(progress, state)
        print(f"[isolated Stage 5] completed {len(state['arms'])} arms; {progress}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuilt", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    if sha256(Path(first.__file__).read_bytes()).hexdigest() != FIRST_DRIVER_SHA:
        raise ValueError("the frozen qualification validator changed")
    evidence = first.ROOT / first.EVIDENCE_RELATIVE
    frozen = first.frozen_first(evidence)
    import run_v5_step5_10k_timing_closed as stage

    replay(stage, args.rebuilt.resolve(strict=True), args.output_root.resolve(), frozen)


if __name__ == "__main__":
    main()
