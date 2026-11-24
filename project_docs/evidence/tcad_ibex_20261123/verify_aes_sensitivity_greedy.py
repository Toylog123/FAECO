#!/usr/bin/env python3
"""Replay the AES tuned-greedy schedule and audit the charged ranking STA."""

from argparse import ArgumentParser
import math
from pathlib import Path
import re

import verify_aes_greedy_matched as matched
from run_aes_sensitivity_greedy import render_rank_tcl


comparison, cold = matched.comparison, matched.cold
read, verify, check = matched.read, matched.verify, matched.check
RULE = "frozen TT output-pin setup margin with uncapped weighting: >5 ps first, area*(0.1+max(margin_ps,0)/200)"
RANK_LOG = Path("sensitivity/sta_rank.log")


def verify_protocol(root):
    path = root / "matched_protocol.json"
    plan = read(path)
    settings = {**matched.PLAN_SETTINGS, "single_sensitivity_rule": RULE, "single_sensitivity_timeout_seconds": 40.0}
    check(plan.keys() == settings.keys() | {"driver", "parent_driver", "matrix", "preflight"}
          and all(plan[key] == value for key, value in settings.items()), "mismatched sensitivity plan")
    for field, file in (("driver", "run_aes_sensitivity_greedy.py"), ("parent_driver", "run_aes_greedy_matched.py")):
        check(verify(plan[field]) == Path(__file__).with_name(file).resolve(), "unexpected producer")
    verify(plan["matrix"])
    verify(plan["preflight"])
    return plan, comparison.bind(path)


def verify_manifest(cell, order, method, plan, binding):
    manifest = read(cell / "config.json")
    scheduler = "single_sensitivity" if method == "single" else method
    check(manifest["methods"] == manifest["diagnostic_methods"] == [method]
          and manifest["matched_order"] == order and manifest["scheduler"] == scheduler
          and manifest["single_sensitivity_rule"] == RULE,
          f"incorrect scheduler or diagnostic backend for {order}/{method}")
    check(manifest["matrix"] == plan["matrix"] and manifest["matched_protocol"] == binding
          and manifest["measurement_clock"] == "CLOCK_MONOTONIC_RAW" and manifest["batch_size"] == 3
          and read(cell / "transferred_preflight.json")["preflight_result"] == plan["preflight"],
          "common policy, preflight, or inputs changed")
    for field in ("driver", "parent_driver"):
        name = Path(plan[field]["path"]).name
        check(manifest["driver_sources"][name] == plan[field]
              and comparison.bind(cell / "producer_sources" / name)["sha256"] == plan[field]["sha256"],
              "the frozen producer differs from the arm copy")
    cold.verify_protocol(cell, {**manifest, "methods": list(cold.METHODS), "diagnostic_methods": list(cold.ONLINE)})
    return manifest


def validate_ranking(arm, assets, views, pool, tool=None):
    sensitivity = arm / "sensitivity"
    receipt = read(sensitivity / "ranking.json")
    log, script = verify(receipt["log"]), verify(receipt["script"])
    check(log == arm / RANK_LOG and script == sensitivity / "rank.tcl" and receipt["view"] == "TT"
          and receipt["threads"] == 1 and receipt["rule"] == RULE, "rank evidence points outside its arm")
    control = {name: assets["control"][name] for name in ("odb", "sdc", "spef")}
    libraries = assets["used_libraries"]["TT"]
    check(receipt["control"] == control and receipt["libraries"] == libraries
          and script.read_text(encoding="utf-8") == render_rank_tcl([verify(lib) for lib in libraries],
                                                                  {key: verify(asset) for key, asset in control.items()}, pool),
          "ranking did not read the original frozen TT inputs")
    text = log.read_text(encoding="utf-8")
    check("AES_TT_RANK_COMPLETE" in text.splitlines(), "ranking STA lacks completion evidence")
    span = receipt["preparation"]
    check(span["seconds"] == span["stop_raw"] - span["start_raw"] > 0, "invalid rank preparation span")
    if tool is not None:
        commands = [str(verify(assets["tools"]["openroad"])), "-no_init", "-no_splash", "-threads", "1", "-exit", str(script)]
        check(tool["command"] == commands and tool["returncode"] == 0 and tool["configured_timeout_seconds"] == 40.0
              and tool["wall_seconds"] == receipt["tool_wall_seconds"], "missing, failed, or uncharged ranking STA")
        progress = read(arm / "progress.json")
        check(progress["start_raw"] <= span["start_raw"] <= tool["start_raw"] <= tool["stop_raw"] <= span["stop_raw"]
              <= progress["logical_requests"][0]["admitted_raw"], "rank preparation was outside its wall window")

    wns = views["TT"]["setup_wns_ps"]
    observed = re.findall(r"(?m)^RANK_WNS_PS (\S+)$", text)
    check(len(observed) == 1 and abs(float(observed[0]) - wns) <= 0.001
          and receipt["control_setup_wns_ps"] == wns, "rank query WNS does not match the reference")
    pins = {action.instance: {} for action in pool}
    for instance, pin, slack in re.findall(r"(?m)^RANK_PIN (\S+) (\S+) (\S+)$", text):
        check(instance in pins and pin not in pins[instance] and math.isfinite(float(slack)), "invalid raw pin identity")
        pins[instance][pin] = float(slack)
    check(all(pins.values()) and len(pins) == len(pool) == 18, "rank query did not cover the common pool")
    ranked, historical = [], []
    for action in pool:
        output_pins = pins[action.instance]
        min_slack = min(output_pins.values())
        margin = min_slack - wns
        area = action.estimated_area_saving
        identity = action.action_id
        score = area * (0.1 + max(margin, 0) / 200)
        old_score = area * (0.1 + min(max(margin, 0), 200) / 200)
        expected = {"instance": action.instance, "pins_setup_slack_ps": output_pins, "min_output_setup_slack_ps": min_slack,
                    "margin_ps": margin, "area": area, "off_critical": margin > 5, "score": score, "historical_score": old_score}
        check(expected == receipt["rows"][identity], f"ranking score does not reconstruct for {identity}")
        ranked.append((margin <= 5, -score, -area, identity))
        historical.append((margin <= 5, -old_score, -area, identity))
    order, old_order = ([row[-1] for row in sorted(score)] for score in (ranked, historical))
    check(order == receipt["ordered_action_ids"] and old_order == receipt["historical_ordered_action_ids"]
          and receipt["historical_saturated_count"] == sum(min(slacks.values()) - wns >= 200 for slacks in pins.values())
          and set(receipt["rows"]) == set(order), "single-gate order or saturation recount differs")
    action_index = {action.action_id: action for action in pool}
    return [action_index[identity] for identity in order], receipt


def audit(root, prefix):
    defaults = matched.verify_protocol, matched.verify_manifest, matched.audit_cell
    original_read, original_inputs = cold.read, matched.verify_pair_inputs
    orig_audit_cell = matched.audit_cell

    def audit_cell(cell, method, manifest, entry, assets):
        arm = cell / method
        subprocess_path = arm / "subprocesses.json"
        tools = read(subprocess_path)
        stage = [tool for tool in tools if Path(tool["log"]) == arm / RANK_LOG]
        check(len(stage) == int(method == "single") and (not stage or stage[0] == tools[0]),
              "bad number or order of rank tools")
        if method != "single":
            check(not (arm / "sensitivity").exists(), "FAECO unexpectedly used greedy ranking artifacts")
            return orig_audit_cell(cell, method, manifest, entry, assets)
        frozen, views, nets, pool, reference = original_inputs(cell, manifest)
        ordered, receipt = validate_ranking(arm, assets, views, pool, stage[0])

        # Only the cold per-request DRC audit excludes the already-audited
        # ranking stage. The ordinary timing and operation replays see all tools.
        def candidate_receipts(path):
            return tools[1:] if Path(path) == subprocess_path else original_read(path)

        def ranked_inputs(_cell, _manifest):
            return frozen, views, nets, ordered, reference

        cold.read, matched.verify_pair_inputs = candidate_receipts, ranked_inputs
        try:
            checked, folded = orig_audit_cell(cell, method, manifest, entry, assets)
        finally:
            cold.read, matched.verify_pair_inputs = original_read, original_inputs
        checked["ranking_receipt"] = comparison.bind(arm / "sensitivity/ranking.json")
        folded["sensitivity_ranking_seconds"] = receipt["preparation"]["seconds"]
        folded["sensitivity_sta_seconds"] = receipt["tool_wall_seconds"]
        folded["candidate_sta_tools"] = folded["sta_tools"] - 1
        folded["historical_saturated_count"] = receipt["historical_saturated_count"]
        return checked, folded

    matched.verify_protocol, matched.verify_manifest, matched.audit_cell = verify_protocol, verify_manifest, audit_cell
    matched.STAGES[RANK_LOG.name] = "control_rank_sta"
    try:
        report = matched.audit(root, prefix)
    finally:
        matched.verify_protocol, matched.verify_manifest, matched.audit_cell = defaults
        del matched.STAGES[RANK_LOG.name]
    return {**report, "common_audit_source": report["audit_source"], "audit_source": comparison.bind(Path(__file__).resolve())}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--prefix", type=int, choices=range(1, 5))
    mode.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    root = args.run.resolve(strict=True)
    if args.preflight_only:
        manifest = read(root / "config.json")
        _, views, _, pool, _ = matched.verify_pair_inputs(root, manifest)
        assets = read(verify(manifest["matrix"]))["bindings"]
        ordered, ranking = validate_ranking(root, assets, views, pool)
        comparison.save(root / "independent_preflight.json", {
            "checked_action_count": len(ordered), "ranking": comparison.bind(root / "sensitivity/ranking.json"),
            "historically_saturated_count": ranking["historical_saturated_count"],
            "historical_order_is_original": ranking["historical_ordered_action_ids"] == [action.action_id for action in pool],
            "uncapped_order_is_original": [action.action_id for action in ordered] == [action.action_id for action in pool],
        })
        print(f"reconstructed original and uncapped order for {len(ordered)} actions", flush=True)
        return
    stem = f"independent_verification_prefix_{args.prefix}" if args.prefix else "independent_verification"
    comparison.save(root / f"{stem}.json", audit(root, args.prefix))


if __name__ == "__main__":
    main()
