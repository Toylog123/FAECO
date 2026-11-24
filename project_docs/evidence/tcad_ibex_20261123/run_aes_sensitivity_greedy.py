#!/usr/bin/env python3
"""Compare frozen TT slack-ranked single-gate greedy with FAECO on AES."""

from argparse import ArgumentParser
import math
from pathlib import Path
import re

from run_aes_cold_online import ColdOnlineComparison
import run_aes_greedy_matched as matched
from run_aes_greedy_matched import ordered_methods, run_online_arm
from run_aes_incident_priority_matched_v2 import comparison
from run_aes_protected_online import LIMIT_SECONDS, MAX_REQUESTS
from run_screened_matrix import bind_runtime, raw_seconds


RANK_TIMEOUT_SECONDS = 40.0
RANK_COMPLETE = "AES_TT_RANK_COMPLETE"
RANK_RULE = "frozen TT output-pin setup margin with uncapped weighting: >5 ps first, area*(0.1+max(margin_ps,0)/200)"


def rank_actions(pool, text, expected_wns_ps):
    instances = {action.instance for action in pool}
    if len(instances) != len(pool):
        raise ValueError("the common candidate pool must have distinct instances")
    reported_wns = re.findall(r"(?m)^RANK_WNS_PS (\S+)$", text)
    if len(reported_wns) != 1 or not math.isclose(float(reported_wns[0]), expected_wns_ps, abs_tol=1e-3, rel_tol=0):
        raise ValueError("ranking STA did not recover frozen CONTROL TT setup WNS")
    pin_slacks = {instance: {} for instance in instances}
    for instance, pin, slack in re.findall(r"(?m)^RANK_PIN (\S+) (\S+) (\S+)$", text):
        value = float(slack)
        if instance not in pin_slacks or pin in pin_slacks[instance] or not math.isfinite(value):
            raise ValueError(f"unexpected, ambiguous, or untimed ranking pin {instance}/{pin}")
        pin_slacks[instance][pin] = value
    if any(not pins for pins in pin_slacks.values()):
        raise ValueError(f"missing ranking pin coverage: {sorted(name for name, pins in pin_slacks.items() if not pins)}")

    rows = {}
    for action in pool:
        pins = pin_slacks[action.instance]
        slack_ps = min(pins.values())
        margin_ps = slack_ps - expected_wns_ps
        area = action.estimated_area_saving
        nonnegative_margin = max(margin_ps, 0.0)
        rows[action.action_id] = {"instance": action.instance, "pins_setup_slack_ps": pins,
                                  "min_output_setup_slack_ps": slack_ps, "margin_ps": margin_ps,
                                  "area": area, "off_critical": margin_ps > 5.0,
                                  "score": area * (0.1 + nonnegative_margin / 200.0),
                                  "historical_score": area * (0.1 + min(nonnegative_margin, 200.0) / 200.0)}

    def order(score):
        return sorted(rows, key=lambda key: (-rows[key]["off_critical"], -rows[key][score], -rows[key]["area"], key))

    return {"control_setup_wns_ps": expected_wns_ps, "rows": rows, "ordered_action_ids": order("score"),
            "historical_ordered_action_ids": order("historical_score"),
            "historical_saturated_count": sum(row["margin_ps"] >= 200.0 for row in rows.values())}


def render_rank_tcl(libraries, control, pool):
    names = [action.instance for action in pool]
    if any(not re.fullmatch(r"[A-Za-z0-9_.$/]+", name) for name in names):
        raise ValueError("candidate instance requires Tcl quoting beyond the frozen AES scope")
    instances = " ".join(f"{{{name}}}" for name in names)
    return f"""{comparison.read_db(libraries, control['odb'])}
read_sdc {comparison.tcl(control['sdc'])}
if {{[llength [all_clocks]] == 0}} {{ error "No clocks in saved SDC" }}
read_spef {comparison.tcl(control['spef'])}
set_cmd_units -time ns
puts "RANK_WNS_PS [expr {{1e12 * [sta::worst_slack_cmd max]}}]"
foreach name [list {instances}] {{
    set cell [get_cells -quiet $name]
    if {{[llength $cell] != 1 || [get_full_name $cell] ne $name}} {{ error "Wrong candidate instance: $name" }}
    foreach pin [get_pins -quiet -of_objects $cell -filter "direction==output"] {{
        puts "RANK_PIN $name [get_name $pin] [expr {{1e3 * [get_property $pin slack_max]}}]"
    }}
}}
puts {RANK_COMPLETE}
exit
"""


def score_control(runner, pool, out):
    start = raw_seconds()
    out.mkdir(parents=True)
    control, libraries = runner.eval.control, runner.eval.libraries["TT"]
    script, log = out / "rank.tcl", out / "sta_rank.log"
    script.write_text(render_rank_tcl(libraries, control, pool), encoding="utf-8")
    operation = comparison.run_process([runner.tools["openroad"], "-no_init", "-no_splash", "-threads", "1", "-exit", script],
                                       log, RANK_TIMEOUT_SECONDS)
    output = comparison.checked_output(operation, RANK_COMPLETE)
    ranking = rank_actions(pool, output, runner.eval.ref_views["TT"]["setup_wns_ps"])
    stop = raw_seconds()
    receipt = {**ranking, "rule": RANK_RULE, "view": "TT", "threads": 1,
               "control": {key: comparison.bind(control[key]) for key in ("odb", "sdc", "spef")},
               "libraries": [comparison.bind(path) for path in libraries],
               "script": comparison.bind(script), "log": comparison.bind(log),
               "preparation": {"start_raw": start, "stop_raw": stop, "seconds": stop - start},
               "tool_wall_seconds": operation.wall_seconds}
    comparison.save(out / "ranking.json", receipt)
    return receipt


class SensitivityComparison(ColdOnlineComparison):
    def run_arm(self, method, reference):
        if method != "single":
            return run_online_arm(self, method, reference)
        original = comparison.run_method

        def dispatch(name, ref, actions, *args, **kwargs):
            # This callback is inside the ordinary arm clock and subprocess ledger.
            ranking = score_control(self, actions, self.output / method / "sensitivity")
            pool = {action.action_id: action for action in actions}
            ranked = [pool[action_id] for action_id in ranking["ordered_action_ids"]]
            return original(name, ref, ranked, *args, **kwargs)

        try:
            comparison.run_method = dispatch
            return run_online_arm(self, method, reference)
        finally:
            comparison.run_method = original


def run_cell(matrix, preflight, output, order, method, protocol):
    runner = SensitivityComparison(matrix, output)
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        reference = runner.prepare_online(preflight)
        for name in ("driver", "parent_driver"):
            source = Path(protocol[name]["path"])
            runner.config["driver_sources"][source.name] = protocol[name]
            (output / "producer_sources" / source.name).write_bytes(source.read_bytes())
        scheduler = "single_sensitivity" if method == "single" else method
        runner.config.update({"methods": [method], "diagnostic_methods": [method], "matched_order": order,
                              "matched_protocol": protocol["binding"], "scheduler": scheduler,
                              "single_sensitivity_rule": RANK_RULE,
                              "single_sensitivity_cost": "one fresh single-thread TT CONTROL STA inside the raw wall window"})
        comparison.save(output / "config.json", runner.config)
        summary = runner.run_arm(method, reference)
    comparison.save(output / "result.json", summary)
    return summary


def main():
    parser = ArgumentParser(description=__doc__)
    for field in ("matrix", "preflight", "output"):
        parser.add_argument(field, type=Path)
    parser.add_argument("--preflight-only", action="store_true", help="verify the inputs and query CONTROL TT; no candidate evaluates")
    args = parser.parse_args()
    matrix, preflight = (item.resolve(strict=True) for item in (args.matrix, args.preflight))
    out = args.output.resolve()
    if args.preflight_only:
        runner = SensitivityComparison(matrix, out)
        with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
            runner.prepare_online(preflight)
            receipt = score_control(runner, runner.pool, out / "sensitivity")
        print(f"{len(receipt['rows'])} instances scored in {receipt['preparation']['seconds']:.3f} RAW s")
        return

    out.mkdir(parents=True)
    orders = ordered_methods()
    manifest = out / "matched_protocol.json"
    plan = {"driver": comparison.bind(Path(__file__).resolve()),
            "parent_driver": comparison.bind(Path(matched.__file__).resolve()),
            "matrix": comparison.bind(matrix / "config.json"),
            "preflight": comparison.bind(preflight), "orders": orders, "area_target_pct": 0.01,
            "wall_limit_seconds_including_screen": LIMIT_SECONDS, "maximum_requests_per_cell": MAX_REQUESTS,
            "execution": "serial, fresh physical work per cell; both schedulers use current-candidate pre-DRT diagnosis",
            "single_sensitivity_rule": RANK_RULE, "single_sensitivity_timeout_seconds": RANK_TIMEOUT_SECONDS}
    comparison.save(manifest, plan)
    protocol = {**plan, "binding": comparison.bind(manifest)}
    outcomes = []
    for order, methods in orders.items():
        for method in methods:
            started = raw_seconds()
            cell = out / order / method
            print(f"{order}/{method}: fresh online diagnostic backend", flush=True)
            summary = run_cell(matrix, preflight, cell, order, method, protocol)
            stopped = raw_seconds()
            outcomes.append({"order": order, "cell": method, "method": method, "outer_start_raw": started,
                             "outer_stop_raw": stopped, "manifest": comparison.bind(cell / "config.json"),
                             "summary": comparison.bind(cell / method / "summary.json"), "result": summary})
            comparison.save(out / "results.json", outcomes)
            window = summary["window"]
            print(f"{order}/{method}: first={window['time_to_target_seconds']}; area={window['area_saved']}", flush=True)


if __name__ == "__main__":
    main()
