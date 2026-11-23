#!/usr/bin/env python3
"""Rank legal modest edits, screen with frozen TT SPEF, and optionally route the Ibex pilot."""

from dataclasses import asdict, replace
import json
from pathlib import Path
import re
import sys
import time

import compare_ibex as comparison
import run_setup_budget_sweep as sweep
import setup_budget as policy


PILOT_INSTANCES = ("place2749", "place2755")
SHORTLIST_LIMIT = 32
SCREEN_TARGET = 18
MIN_MATRIX_POOL = 16


def elapsed_clock():
    return time.clock_gettime(time.CLOCK_MONOTONIC_RAW)


class RawTime:
    monotonic = staticmethod(elapsed_clock)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def qualified_options(index, libraries, masters, instances, legacy):
    in_all_views = set.intersection(*(set(comparison.liberty_areas(libraries[c])) for c in comparison.CORNERS))
    area = comparison.liberty_areas(libraries["TT"])
    legal = {action.instance: action for action in legacy}
    choices = {}
    for action in comparison.generate_compatible_candidates(index, libraries["TT"], one_per_instance=False,
                                                              deprioritize_zero_drive=True):
        raw = action.instance.removeprefix("\\")
        aligned = instances.get(raw)
        eligible = None if aligned is None else legal.get(aligned[0])
        target = masters.get(action.target_cell)
        if eligible is None or target is None or action.target_cell not in in_all_views:
            continue
        source = masters[action.source_cell]
        if source[:4] != target[:4] or int(target[4]) >= int(source[4]):
            continue
        action = replace(action, instance=eligible.instance)
        previous = choices.get(eligible.instance)
        if previous is None or (-area[action.target_cell], action.target_cell) < (-area[previous.target_cell], previous.target_cell):
            choices[eligible.instance] = action
    if set(choices) != {row.instance for row in legacy}:
        raise comparison.TrialFailure("different compatible instance coverage")
    return choices


FANOUT = r"""
foreach item [[ord::get_db_block] getInsts] {
    set count 0
    foreach term [$item getITerms] {
        if {[[$term getMTerm] getIoType] ne "OUTPUT"} { continue }
        set net [$term getNet]
        if {$net eq "NULL"} { continue }
        set sinks 0
        foreach pin [$net getITerms] {
            if {[[$pin getMTerm] getIoType] in {INPUT INOUT}} { incr sinks }
        }
        foreach port [$net getBTerms] {
            if {[$port getIoType] in {OUTPUT INOUT}} { incr sinks }
        }
        set count [expr {max($count,$sinks)}]
    }
    puts "SCREEN_FANOUT\t[$item getName]\t$count"
}
puts SCREEN_FANOUT_COMPLETE
exit
"""


def probe(args, control, libraries, action, directory):
    directory.mkdir()
    sta = comparison.render_sta(libraries["TT"], control["v"], control["sdc"], control["spef"],
                                report_setup_endpoints=True)
    db = f"read_db {comparison.tcl(control['odb'])}"
    if action:
        db += f"""
set inst [[ord::get_db_block] findInst {comparison.tcl(action.instance)}]
set target [[ord::get_db] findMaster {comparison.tcl(action.target_cell)}]
if {{$inst eq "NULL" || $target eq "NULL" || [[$inst getMaster] getName] ne {comparison.tcl(action.source_cell)}}} {{
    error "frozen-screen source/target mismatch"
}}
if {{![$inst swapMaster $target] || [[$inst getMaster] getName] ne {comparison.tcl(action.target_cell)}}} {{
    error "frozen-screen master replacement failed"
}}
"""
    original = f"read_verilog {comparison.tcl(control['v'])}\nlink_design {comparison.TOP}"
    if sta.count(original) != 1:
        raise comparison.TrialFailure("could not substitute frozen ODB for STA")
    sta = sta.replace(original, db)
    sta = sta.replace("report_parasitic_annotation", "puts SCREEN_ANN_BEGIN\nreport_parasitic_annotation -report_unannotated\nputs SCREEN_ANN_END")
    script = directory / "tt.tcl"
    script.write_text(sta, encoding="utf-8")
    op = comparison.run_process([args.openroad, "-threads", "1", "-exit", script], directory / "tt.log", args.sta_timeout)
    output = comparison.checked_output(op, "IBEX_STA_COMPLETE")
    result = comparison.parse_sta(output)
    annotation = output.split("SCREEN_ANN_BEGIN\n", 1)[1].split("SCREEN_ANN_END", 1)[0]
    if "Found 0 partially unannotated drivers." not in annotation:
        raise comparison.TrialFailure("fixed SPEF has partial annotation")
    return result, annotation, asdict(op)


def run_screen(args, qualification):
    begin = elapsed_clock()
    args.out.mkdir(parents=True)
    control = {ext: args.control_dir / f"6_final.{ext}" for ext in comparison.CONTROL_FILES}
    libraries = comparison.materialize_views(comparison.load_views(qualification), args.out / "libraries")
    asset_paths = [*control.values(), args.views_json, args.original_sdc,
                   args.openroad, Path(__file__), *[f for group in libraries.values() for f in group]]
    assets = [comparison.bind(path) for path in asset_paths]
    for ext, path in control.items():
        if comparison.bind(path)["sha256"] != qualification["control_output_paths"][ext]["sha256"]:
            raise comparison.TrialFailure(f"CONTROL {ext} differs from qualification")
    if qualification["source_sdc_semantics"]["source_io_matches_all_nonclock_inputs_and_outputs"] is not True:
        raise comparison.TrialFailure("source I/O is not qualified")
    index = args.out / "index.v"
    area = comparison.liberty_areas(libraries["TT"])
    ref_masters = comparison.logical_masters(control["v"], area)
    index.write_text("".join(f"{master} \\{name} ();\n" for name, master in ref_masters.items()), encoding="utf-8")
    script = args.out / "inventory.tcl"
    script.write_text(comparison.render_inventory(libraries["TT"], control["odb"]), encoding="utf-8")
    op = comparison.run_process([args.openroad, "-threads", "1", "-exit", script], args.out / "inventory.log", args.sta_timeout)
    masters, raw_instances = comparison.parse_inventory(comparison.checked_output(op, "IBEX_INVENTORY_COMPLETE"))
    instances, mismatches = comparison.align_db_instances(ref_masters, raw_instances)
    if mismatches:
        raise comparison.TrialFailure("frozen ODB and V masters differ")
    legacy = comparison.select_pool(index, libraries, masters, instances)
    options = qualified_options(index, libraries, masters, instances, legacy)
    fanout_tcl = args.out / "fanout.tcl"
    fanout_tcl.write_text(comparison.read_db(libraries["TT"], control["odb"]) + "\n" + FANOUT, encoding="utf-8")
    op = comparison.run_process([args.openroad, "-threads", "1", "-exit", fanout_tcl], args.out / "fanout.log", args.sta_timeout)
    output = comparison.checked_output(op, "SCREEN_FANOUT_COMPLETE")
    fanout = {line.split("\t")[1]: int(line.split("\t")[2]) for line in output.splitlines() if line.startswith("SCREEN_FANOUT\t")}
    ranked = sorted((a for a in options.values() if fanout[a.instance] > 0),
                    key=lambda a: (fanout[a.instance], -a.estimated_area_saving, a.action_id))
    baseline, annotation, base_time = probe(args, control, libraries, None, args.out / "control_TT")
    for field in ("setup_wns_ps", "setup_tns_ps", "hold_wns_ps", "hold_tns_ps"):
        if abs(baseline[field] - qualification["views"]["TT"][field]) > comparison.PS_TOLERANCE:
            raise comparison.TrialFailure(f"TT baseline does not replay the qualified {field}")
    wns = policy.setup_budget_ps(args.clock_period_ps, 1)
    tns = policy.setup_tns_budget_ps(args.clock_period_ps, 1, baseline["setup_tns_ps"])

    def test(action, label):
        metrics, actual_annotation, operation = probe(args, control, libraries, action, args.out / label)
        failures = comparison.joint_failures({c: baseline for c in comparison.CORNERS},
                                              {c: metrics for c in comparison.CORNERS}, check_setup=False)
        failures = [f for f in failures if f.startswith("TT:") and f != "TT:hold_regression"]
        failures += policy.setup_gate_failures("TT", baseline["setup_wns_ps"], metrics["setup_wns_ps"], wns,
                                              comparison.PS_TOLERANCE, protect_clean=False)
        failures += policy.tns_gate_failures("TT", baseline["setup_tns_ps"], metrics["setup_tns_ps"], tns,
                                            comparison.PS_TOLERANCE)
        if actual_annotation != annotation:
            failures.append("changed_annotation")
        row = {"action": asdict(action), "fanout": fanout[action.instance], "metrics": metrics,
               "failures": failures, "operation": operation, "label": label}
        comparison.save(args.out / label / "receipt.json", row)
        print(label, action.action_id, "fanout", fanout[action.instance], failures, flush=True)
        return row

    rows, passed = [], []
    for index, action in enumerate(ranked[:SHORTLIST_LIMIT], 1):
        row = test(action, f"screen_{index:02d}")
        rows.append(row)
        if not row["failures"]:
            passed.append(action)
            if len(passed) == SCREEN_TARGET:
                break
    comparison.save(args.out / "screen_pool.json", [asdict(a) for a in passed])
    receipt = {"clock": "CLOCK_MONOTONIC_RAW", "wall_seconds": elapsed_clock() - begin,
               "pool_sha256": comparison.bind(args.out / "screen_pool.json")["sha256"],
               "top": comparison.TOP, "control": {k: comparison.bind(v) for k, v in control.items()},
               "control_sha256": {k: comparison.bind(control[k])["sha256"] for k in ("odb", "spef", "sdc")},
               "period_ps": args.clock_period_ps, "budgets_ps": {"wns": wns, "tns": tns}, "baseline": base_time,
               "screened": len(rows), "passed": len(passed), "rows": rows, "input_bindings": assets}
    comparison.save(args.out / "screen_receipt.json", receipt)
    if args.pilot:
        if len(passed) < 2:
            raise comparison.TrialFailure("screen yielded fewer than two physical pilot controls")
        high = [test(options[name], f"pilot_{name}") for name in PILOT_INSTANCES]
        comparison.save(args.out / "pilot_receipt.json", {"screen": comparison.bind(args.out / "screen_receipt.json"),
                        "cases": high + [row for row in rows if not row["failures"]][:2]})
    elif len(passed) < MIN_MATRIX_POOL:
        raise comparison.TrialFailure(f"only {len(passed)} candidates passed the frozen screen")
    if any(comparison.bind(Path(item["path"])) != item for item in assets):
        raise comparison.TrialFailure("screening inputs changed while running")
    return 0


def run_pilot(args, evaluator, reference, pool, baseline, noop):
    original = read(args.pilot_receipt)
    rows = original["cases"]
    if len(rows) != 4:
        raise comparison.TrialFailure("pilot must identify two high and two low fanout cases")
    actions = [comparison.PhysicalAction(**row["action"]) for row in rows]
    for action in actions:
        evaluator.actions[action.action_id] = action
    cache = sweep.TrialCache(evaluator)
    gate = sweep.budget_gate(evaluator, 1.0, False)
    measured = []
    for sequence, action in enumerate(actions, 1):
        print("physical", sequence, action.action_id, flush=True)
        endpoint, receipt = cache.request((action.action_id,), gate, fresh_directory=args.out / f"case_{sequence:02d}")
        measured.append({"endpoint": asdict(endpoint), "physical": receipt, "screen": rows[sequence - 1]})
        comparison.save(args.out / "pilot_progress.json", measured)
    counts = cache.totals()
    return counts["drt_completions"] == counts["rcx_completions"] == 4 and counts["view_sta_attempts"] == 12, {
        "clock": "CLOCK_MONOTONIC_RAW", "gate": sweep.gate_summary(gate, evaluator.ref_views),
        "cases": measured, "operations": counts, "target_area_saved": reference.area * 0.0001,
    }


def main():
    parser = comparison.create_parser(description=__doc__)
    parser.add_argument("--top", default="ibex_core")
    phase = parser.add_mutually_exclusive_group()
    phase.add_argument("--pilot", action="store_true", help="add the two named Ibex frozen-SPEF probes")
    phase.add_argument("--pilot-receipt", type=Path, help="perform physical followthrough on the four frozen pilot cases")
    args = comparison.prepare_args(parser, parser.parse_args())
    comparison.TOP = args.top
    comparison.time = sweep.time = RawTime()
    try:
        cfg = read(args.views_json)
        args.clock_period_ps = policy.original_period_ps(cfg, args.original_sdc)
        if args.pilot_receipt:
            args.pilot_receipt = args.pilot_receipt.resolve(strict=True)
            return comparison.run(args, matched_runner=run_pilot, config_overrides={
                "clock": "CLOCK_MONOTONIC_RAW", "pilot_source": comparison.bind(args.pilot_receipt),
                "setup_budget_ps_per_view": None, "tns_gate": True,
                "original_clock_period_ps": args.clock_period_ps,
            }, extra_sources=(Path(__file__), Path(sweep.__file__), Path(policy.__file__)))
        return run_screen(args, cfg)
    except (comparison.TrialFailure, OSError, ValueError, KeyError) as err:
        print(str(err), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
