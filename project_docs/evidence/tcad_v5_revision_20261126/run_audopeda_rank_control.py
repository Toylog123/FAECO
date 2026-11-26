#!/usr/bin/env python3
"""Repeat the frozen Stage 5 fixed-three arm with the AuDoPEDA instance ordering."""

import argparse
from functools import partial
import math
from pathlib import Path
from struct import pack, unpack

from measure_stage5_resources import prepare, stage
from run_asap7_aes_rank_aligned import install


PROBE_SHA256 = "d6ac3dc328028ce34b0ad7740072d71dbd93606b163a7cf2518997b891495d47"
BASELINE_SHA256 = "f49a41ea18be55720ee474bd3813bea3dd07d25c88952c0d7c39d7624815740b"
PATCH_SHA256 = "b56acd68d698190c3be8d748ebd55f5912a5c06576d16ea877a6428670b5eefd"
PATCH_SOURCE = ("https://github.com/ABKGroup/AuDoPEDA/blob/"
                "d396422e27496b6836ecbc7229edff33f642525c/diffs/pwr/OpenROAD_pwr.patch#L308-L328")
RANK_RULE = "Frozen TT total instance power times setup headroom; descending power, headroom, source area ties"
STRATEGY = stage.STRATEGIES["fixed_boxed"]
SENSITIVITY = stage.qualified.matrix.sensitivity


def float32(value):
    return unpack("!f", pack("!f", value))[0]


def render_rank_tcl(libraries, control, pool):
    script = SENSITIVITY.render_rank_tcl(libraries, control, pool)
    anchor = '    foreach pin [get_pins -quiet -of_objects $cell -filter "direction==output"] {'
    if script.count(anchor) != 1:
        raise ValueError("shared Stage 5 rank Tcl output-pin block changed")
    instance_power = """    set dbinst [[ord::get_db_block] findInst $name]
    set master [$dbinst getMaster]
    set fields [sta::instance_power [lindex $cell 0] [sta::cmd_scene]]
    if {[llength $fields] != 4} { error "Expected internal/switching/leakage/total W for $name" }
    puts "AUDO_FEATURE $name [$master getName] [$master getArea] $fields"
"""
    return script.replace(anchor, instance_power + anchor, 1)


def parse_rank(pool, text, expected_wns_ps, probe):
    if expected_wns_ps <= 0 or text.splitlines().count(SENSITIVITY.RANK_COMPLETE) != 1:
        raise ValueError("projected ordering requires the frozen timing-closed TT reference and completed STA")
    # OpenROAD reports the same output-pin slack used by the native Stage 5 ranker.
    native = SENSITIVITY.rank_actions(pool, text, expected_wns_ps)
    if native["ordered_action_ids"] != probe["original_rank"]:
        raise ValueError("fresh original TT ordering differs from the pinned comparison")

    actions = {action.instance: action for action in pool}
    features = {}
    for line in text.splitlines():
        if not line.startswith("AUDO_FEATURE "):
            continue
        _, name, master, area, *power = line.split()
        if name not in actions or len(power) != 4:
            raise ValueError(f"invalid AuDoPEDA feature row: {line}")
        action = actions[name]
        action_id = action.action_id
        if action_id in features or master != action.source_cell or int(area) <= 0:
            raise ValueError(f"duplicate instance, incorrect master, or invalid source area: {name}")

        pins = native["rows"][action_id]["pins_setup_slack_ps"]
        if len(pins) != 1 or not 10 < (slack_ps := next(iter(pins.values()))) < 1e8:
            raise ValueError(f"{name} is outside the frozen finite single-output data-net projection")
        internal, switching, leakage, total = map(float, power)
        if not all(math.isfinite(value) and value >= 0 for value in (internal, switching, leakage, total)):
            raise ValueError(f"invalid OpenSTA instance power: {name}")
        if not math.isclose(internal + switching + leakage, total, rel_tol=2e-6, abs_tol=1e-15):
            raise ValueError(f"inconsistent OpenSTA instance power components: {name}")

        # The author's WNS floor is 0 on a timing-closed design. Their comparator
        # uses seconds and single-precision multiplication.
        headroom = float32(slack_ps * 1e-12)
        watts = float32(total)
        features[action_id] = {
            "instance": name, "source": master, "target": action.target_cell,
            "power_w": watts, "headroom_s": headroom, "area_dbu2": int(area),
            "score": float32(watts * headroom),
        }
    order = sorted(features, key=lambda key: tuple(-features[key][field] for field in
                   ("score", "power_w", "headroom_s", "area_dbu2")) + (key,))
    if features != probe["features"] or order != probe["projected_rank"]:
        raise ValueError("fresh power/headroom feature tuples or their ordering differ from the pinned projection")
    return {
        "control_setup_wns_ps": expected_wns_ps, "rows": features, "ordered_action_ids": order,
        "original_ordered_action_ids": native["ordered_action_ids"], "rule": RANK_RULE,
    }


def score_control(runner, pool, out, *, probe):
    start = stage.raw_seconds()
    out.mkdir(parents=True)
    control, libraries = runner.eval.control, runner.eval.libraries["TT"]
    script, log = out / "rank.tcl", out / "sta_rank.log"
    script.write_text(render_rank_tcl(libraries, control, pool), encoding="utf-8")
    operation = stage.cmp.run_process(
        [runner.tools["openroad"], "-no_init", "-no_splash", "-threads", "1", "-exit", script],
        log, SENSITIVITY.RANK_TIMEOUT_SECONDS,
    )
    text = stage.cmp.checked_output(operation, SENSITIVITY.RANK_COMPLETE)
    rank = parse_rank(pool, text, runner.eval.ref_views["TT"]["setup_wns_ps"], probe)
    stop = stage.raw_seconds()
    receipt = {
        **rank, "view": "TT", "threads": 1, "power_activity": "OpenSTA default activity",
        "control": {key: stage.cmp.bind(control[key]) for key in ("odb", "sdc", "spef")},
        "libraries": [stage.cmp.bind(path) for path in libraries], "script": stage.cmp.bind(script),
        "log": stage.cmp.bind(log), "source_ordering": {"patch": PATCH_SOURCE, "sha256": PATCH_SHA256},
        "preparation": {"start_raw": start, "stop_raw": stop, "seconds": stop - start},
        "tool_wall_seconds": operation.wall_seconds,
    }
    stage.cmp.save(out / "ranking.json", receipt)
    return receipt


def bind_comparison(args, runner, state, probe):
    action_identity = {action.action_id: (action.instance, action.source_cell, action.target_cell)
                       for action in runner.pool}
    probe_identity = {key: (row["instance"], row["source"], row["target"])
                      for key, row in probe["features"].items()}
    order = probe["projected_rank"]
    if (len(action_identity) != stage.POOL_SIZE or action_identity != probe_identity
            or set(order) != set(action_identity) or len(order) != len(action_identity)
            or state["rank_order"] != probe["original_rank"]
            or runner.batch != 3 or set(order[:runner.batch]) == set(state["rank_order"][:runner.batch])):
        raise ValueError("projected ordering does not preserve the frozen actions and change the first group")

    producer_path = args.baseline / "producer.json"
    producer_binding = stage.cmp.bind(producer_path)
    if producer_binding["sha256"] != BASELINE_SHA256:
        raise ValueError("the matched V4 fixed-arm receipt changed")
    producer = stage.read(producer_path)
    summary_path = stage.verify(producer["summary"])
    summary = stage.read(summary_path)
    rank_path = summary_path.parent / "sensitivity/ranking.json"
    if (stage.verify(producer["frozen_state"]) != args.frozen / "stage5_progress.json"
            or producer["screen_charge_s"] != runner.screen
            or summary["method"] != "fixed" or summary["stop_reason"] != "logical_cap_or_pool_exhausted"
            or stage.read(rank_path)["ordered_action_ids"] != state["rank_order"]):
        raise ValueError("the fixed-three reference does not match the prepared rank-only arm")
    for key in ("progress", "tool_ledger"):
        stage.verify(producer[key])
    return {
        "producer": producer_binding, "summary": producer["summary"], "progress": producer["progress"],
        "tool_ledger": producer["tool_ledger"], "ranking": stage.cmp.bind(rank_path),
        "time_average_um2": stage.comparable_auc(
            [(item["elapsed_s"], item["area_saved_um2"]) for item in producer["commits"]]),
    }


def finish(runner, reference, summary, reuse):
    arm = runner.output / summary["method"]
    progress = stage.read(arm / "progress.json")
    requests = {f"{row['id']:02d}": row for row in progress["logical_requests"]}
    accepted = [stage.checked_commit(reference, row, requests, runner.eval)
                for row in progress["checkpoints"] if row["accepted"]]
    if (summary["method"] != "fixed" or reuse or len(accepted) > summary["logical_finished"]
            or any(not 0 < row["elapsed_s"] <= stage.LIMIT_S for row in accepted)):
        raise ValueError("fixed-three comparison changed its dispatch or acceptance contract")
    return {
        "accepted_checkpoints": accepted, "stop_reason": summary["stop_reason"],
        "logical_admitted": summary["logical_admitted"], "logical_finished": summary["logical_finished"],
        "qualified_area_um2": accepted[-1]["area_saved_um2"] if accepted else 0.0,
        "time_average_um2": stage.comparable_auc([(row["elapsed_s"], row["area_saved_um2"]) for row in accepted]),
        "summary": stage.cmp.bind(arm / "summary.json"), "progress": stage.cmp.bind(arm / "progress.json"),
        "rank": stage.cmp.bind(arm / "sensitivity/ranking.json"),
        "tool_ledger": stage.cmp.bind(arm / "subprocesses.json"),
        "stage_costs": stage.qualified.matrix.audit_tools(stage.read(arm / "subprocesses.json")),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frozen", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--probe", type=Path, required=True, help="pinned RANK_PROBE.json")
    parser.add_argument("--baseline", type=Path, required=True, help="source V4 fixed-arm result directory")
    parser.add_argument("--prepare-only", action="store_true", help="verify frozen inputs without calling EDA")
    args = parser.parse_args()
    args.frozen = args.frozen.resolve(strict=True)
    args.baseline = args.baseline.resolve(strict=True)
    args.probe = args.probe.resolve(strict=True)
    args.output = args.output.resolve()
    if any(args.output.is_relative_to(root) for root in (args.frozen, args.baseline, args.probe.parent)):
        parser.error("use a fresh output directory outside the frozen evidence roots")
    probe_binding = stage.cmp.bind(args.probe)
    if probe_binding["sha256"] != PROBE_SHA256:
        raise ValueError("the independently repeated rank probe changed")
    probe = stage.read(args.probe)

    args.output.mkdir(parents=True)
    with (
        stage.bind_runtime(stage.TOP, stage.ROUTING),
        stage.qualified.qualified_ranking(),
        stage.qualified.qualified_process_clock(),
    ):
        runner, reference, state = prepare(args.frozen, args.output / "stage")
        baseline = bind_comparison(args, runner, state, probe)
        protocol = {
            "driver": stage.cmp.bind(Path(__file__)),
            "scope": "AuDoPEDA instance ordering projected to the frozen Stage 5 downsizing pool",
            "source_ordering": {"patch": PATCH_SOURCE, "sha256": PATCH_SHA256},
            "frozen_state": stage.cmp.bind(args.frozen / "stage5_progress.json"),
            "frozen_protocol": state["protocol"], "rank_probe": probe_binding, "baseline": baseline,
            "batch_width": runner.batch, "screen_charge_s": runner.screen, "wall_limit_s": stage.LIMIT_S,
            "original_rank": probe["original_rank"], "projected_rank": probe["projected_rank"],
            "candidate_pool": runner.config["ordered_pool"],
        }
        protocol_path = args.output / "protocol.json"
        stage.cmp.save(protocol_path, protocol)
        if args.prepare_only:
            replay_tcl = render_rank_tcl(runner.eval.libraries["TT"], runner.eval.control, runner.pool)
            if replay_tcl != (args.probe.parent / "rank.tcl").read_text(encoding="utf-8"):
                raise ValueError("the fresh rank Tcl differs from the repeated probe")
            expected_wns = runner.eval.ref_views["TT"]["setup_wns_ps"]
            for name in ("tt_1.log", "tt_2.log"):
                parse_rank(runner.pool, (args.probe.parent / name).read_text(encoding="utf-8"),
                           expected_wns, probe)
            print("Frozen protocol and both prior rank logs verified; no new STA or candidate evaluations")
            return

        runner.output = args.output / "arm"
        runner.output.mkdir()
        runner.eval.args.out = runner.output
        print(f"Stage 5 projected fixed-three from {runner.output}", flush=True)
        with install(SENSITIVITY, "score_control", partial(score_control, probe=probe)):
            summary, reuse = stage.run_aligned_strategy(
                runner, STRATEGY, reference, {"order": probe["projected_rank"]}, stage.qualified.matrix.run_strategy,
            )
        result = finish(runner, reference, summary, reuse)
        stage.cmp.save(args.output / "VERIFIED.json", {"protocol": stage.cmp.bind(protocol_path), **result})
        print(f"Projected arm: {result['stop_reason']}; qualified area {result['qualified_area_um2']:.4f} um^2")


if __name__ == "__main__":
    main()
