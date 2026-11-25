#!/usr/bin/env python3
"""Retry only the TT capture-leaf neighborhood of two rejected UART ODBs."""

from argparse import ArgumentParser
from collections import defaultdict
import math
import os
from pathlib import Path
import re
from statistics import median
from unittest.mock import patch

from run_hold_reentry_rescue import comparison, is_hold_only, phase, preview, read, seed_args, verify


CASES = ("uart_04", "uart_05")
ROUTE_LIMIT = 75.0
GEOMETRY = preview.geometry
RAW = GEOMETRY.raw_seconds
WIRE_STATUS = re.compile(r"\+ (?:ROUTED|FIXED) ")


def points(text):
    coordinates = []
    for _, body in GEOMETRY.ROUTE.findall(text):
        previous = None
        for pair in GEOMETRY.POINT.findall(body.partition(" RECT ")[0]):
            point = tuple(previous[index] if item == "*" else int(item) for index, item in enumerate(pair))
            coordinates.append(point)
            previous = point
    return coordinates


def inside(anchors, box):
    x0, y0, x1, y1 = box
    return bool(anchors) and all(x0 <= x <= x1 and y0 <= y <= y1 for x, y in anchors)


def actual_tracks(path):
    lines = defaultdict(set)
    for row in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"TRACKS ([XY]) (-?\d+) DO (\d+) STEP (\d+) LAYER (.+?) ;", row)
        if not match:
            continue
        axis, origin, count, step, layers = match.groups()
        for layer in layers.split():
            lines[(axis, layer)].update(int(origin) + offset * int(step) for offset in range(int(count)))
    return {key: median([b - a for a, b in zip(items, items[1:])]) for key, all_tracks in lines.items()
            if len(items := sorted(all_tracks)) > 1}


def pin_nets(wires):
    index = {}
    for net, record in wires.items():
        for instance, pin in re.findall(r"\( (\S+) (\S+) \)", record.partition(" + ")[0]):
            if instance != "PIN":
                key = (comparison.canonical_odb_name(instance), pin)
                if key in index:
                    raise ValueError(f"multiple nets own {key}")
                index[key] = net
    return index


def locate(case):
    start = RAW()
    rejected = case["fresh_direct"]
    if not is_hold_only(rejected["failures"]) or "TT:hold_regression" not in rejected["failures"]:
        raise ValueError("scoped input must be freshly rejected on TT hold")
    physical = read(verify(rejected["physical"]))
    base_def = verify(physical["artifacts"]["def"])
    tt_report = Path(physical["operations"]["STA_TT"]["log"])
    text = tt_report.read_text(encoding="utf-8")
    if comparison.parse_sta(text)["hold_wns_ps"] != physical["views"]["TT"]["hold_wns_ps"]:
        raise ValueError("TT report does not bind the source terminal")
    minimum = []
    for candidate in re.split(r"(?m)(?=^Startpoint: )", text):
        if "Path Type: min" in candidate:
            slack = re.search(rf"(?m)^\s*({comparison.NUMBER})\s+slack \(", candidate)
            minimum.append((float(slack[1]), candidate))
    slack, path = min(minimum)
    if abs(slack - physical["views"]["TT"]["hold_wns_ps"]) > 0.006:
        raise ValueError("rounded TT path report does not match the bound minimum")
    launch = re.search(r"(?m)^Startpoint: (\S+)", path)[1]
    capture = re.search(r"(?m)^Endpoint: (\S+)", path)[1]
    if capture != launch or f"{capture}/CLK" not in path.split("data arrival time", 1)[1]:
        raise ValueError("expected the preregistered registered feedback capture clock")
    wires = comparison.def_section(base_def, "NETS")
    pins = pin_nets(wires)
    leaf = pins[(capture, "CLK")]
    if "+ USE CLOCK" not in wires[leaf]:
        raise ValueError("capture CLK must bind a clock leaf in the routed DEF")
    arr = path.split("data arrival time", 1)[0]
    feedback = {pins[tuple(pin.rsplit("/", 1))] for pin in re.findall(r"[\^v] (\S+/\S+)\s+\(", arr)
                if not pin.endswith("/CLK")}
    feeder = pins[(capture, "D")]
    components = comparison.def_section(base_def, "COMPONENTS")
    coords = re.search(r"\+ PLACED \( (-?\d+) (-?\d+) \)", components[capture])
    x, y = map(int, coords.groups())
    units = int(re.search(r"(?m)^UNITS DISTANCE MICRONS (\d+)", base_def.read_text(encoding="utf-8"))[1])
    tracks = actual_tracks(base_def)
    layers = {layer for layer, *_ in GEOMETRY.segments(wires[leaf])}
    margin = math.ceil(3 * max(tracks[axis, layer] for layer in layers for axis in ("X", "Y")))
    xx, yy = zip(*points(wires[leaf]))
    bounds = (min(xx) - margin, min(yy) - margin, max(xx) + margin, max(yy) + margin)
    sink = (max(bounds[0], x - units), max(bounds[1], y - units), min(bounds[2], x + units), min(bounds[3], y + units))
    included = {net for net in feedback if "+ USE SIGNAL" in wires[net] and inside(points(wires[net]), sink)}
    if feeder not in included:
        raise ValueError("the D feeder is outside the declared local window")
    result = {"label": case["proposal"]["label"], "tt_report": comparison.bind(tt_report),
              "source_odb": physical["artifacts"]["odb"], "source_def": physical["artifacts"]["def"],
              "launch": launch, "capture": capture, "shared_leaf": leaf, "capture_origin_dbu": [x, y],
              "old_hold_wns_ps": physical["views"]["TT"]["hold_wns_ps"], "physical_pitch_halo_dbu": margin,
              "clock_window_dbu": bounds, "signal_window_dbu": sink, "feedback_nets": sorted(feedback),
              "allowed_nets": sorted(included | {leaf}), "optional_clear": feeder}
    result["selection_raw_seconds"] = RAW() - start
    return result


def window_def(target, source, allowed):
    source_text = source.read_text(encoding="utf-8")
    header = "\n".join(re.findall(r"(?m)^(?:VERSION|DIVIDERCHAR|BUSBITCHARS|DESIGN|UNITS) .+?;$", source_text))
    wires = comparison.def_section(source, "NETS")
    if len(header.splitlines()) != 5 or not set(allowed) <= wires.keys():
        raise ValueError("unexpected source DEF or requested window")
    entries = [f"- {name} {WIRE_STATUS.sub('+ ROUTED ' if name in allowed else '+ FIXED ', row, count=1)} ;"
               for name, row in wires.items()]
    target.write_text(header + f"\nNETS {len(entries)} ;\n" + "\n".join(entries) + "\nEND NETS\nEND DESIGN\n", encoding="utf-8")


def deck_for(out, locator, baseline, mode):
    fmt = comparison.tcl
    template = verify(baseline["original_deck"])
    old = template.parent
    text = template.read_text(encoding="utf-8").replace(str(old), str(out))
    before, tail = text.split("set restore_start [clock microseconds]", 1)
    _, tail = tail.split("puts RESUME_BEFORE_DRT\n", 1)
    if "-no_pin_access" not in tail:
        raise ValueError("original restart deck does not preserve pin access")
    odb = verify(locator["source_odb"])
    original_read = f"read_db {fmt(out / 'checkpoint.odb')}"
    if before.count(original_read) != 1:
        raise ValueError("restart source read is not singular")
    before = before.replace(original_read, f"read_db {fmt(odb)}", 1)
    originals = re.findall(r"(?m)^IBEX_TOUCHED_NET (.+)$", verify(baseline["source_touched_log"]).read_text(encoding="utf-8"))
    if not originals:
        raise ValueError("missing earlier applied action-net identities")
    retained = "\n".join(f"puts {fmt('IBEX_TOUCHED_NET ' + net)}" for net in originals)
    patch = out / "capture_scope.def"
    window_def(patch, verify(locator["source_def"]), locator["allowed_nets"])
    stage = f"""
{retained}
write_guides {fmt(out / 'original.guide')}
read_def -floorplan_initialize {fmt(patch)}
write_def {fmt(out / 'bounded_start.def')}
write_guides {fmt(out / 'bounded.guide')}
if {{![design_is_routed] || ![grt::have_routes]}} {{error "Capture-window load lost routes or guides"}}
"""
    if mode == "clear_capture_d":
        stage += f"""
set net [[ord::get_db_block] findNet {fmt(locator['optional_clear'])}]
if {{$net eq "NULL" || [$net getWire] eq "NULL"}} {{error "Capture feeder lost its original route"}}
odb::dbWire_destroy [$net getWire]
puts {fmt('CLEAR_CAPTURE_D ' + locator['optional_clear'])}
"""
    final_copy = f"""
write_def {fmt(out / 'protected_endpoint.def')}
set fd [open {fmt(out / 'protected_endpoint.def')} r]
set snapshot [read $fd]
close $fd
set first [string first "\\nNETS " $snapshot]
set last [string first "\\nEND NETS" $snapshot]
if {{$first < 0 || $last <= $first}} {{error "Missing protected endpoint NETS"}}
set section [string range $snapshot $first [expr {{$last - 1}}]]
set normalized [string map {{"+ FIXED " "+ ROUTED "}} $section]
set fd [open {fmt(out / 'final_status_only.def')} w]
foreach line [split $snapshot "\\n"] {{
    if {{[regexp {{^(VERSION|DIVIDERCHAR|BUSBITCHARS|DESIGN|UNITS) }} $line]}} {{puts $fd $line}}
    if {{[string match "DIEAREA *" $line]}} {{break}}
}}
puts $fd $normalized
puts $fd "END NETS\\nEND DESIGN"
close $fd
read_def -floorplan_initialize {fmt(out / 'final_status_only.def')}
if {{![design_is_routed]}} {{error "Status normalization lost the final route"}}
puts CAPTURE_WINDOW_FULL_CHECKPOINT
"""
    if tail.count("puts IBEX_DRT_COMPLETE\n") != 1:
        raise ValueError("unexpected final DRT marker")
    return before + stage + tail.replace("puts IBEX_DRT_COMPLETE\n", final_copy + "puts IBEX_DRT_COMPLETE\n", 1)


def check_window(out, loc, mode):
    original = verify(loc["source_def"])
    files = (original, out / "bounded_start.def", out / "protected_endpoint.def", out / "routed.def")
    before, start, protected, normalized = (comparison.def_section(path, "NETS") for path in files)
    if any(nets.keys() != before.keys() for nets in (start, protected, normalized)):
        raise ValueError("NETS identities changed")
    allowed = set(loc["allowed_nets"])
    locked = {name for name, entry in before.items() if name not in allowed and WIRE_STATUS.search(entry)}
    if {name for name, entry in start.items() if "+ FIXED " in entry} != locked or any(
            phase.normalize_net(before[name]) != phase.normalize_net(start[name]) for name in before):
        raise ValueError("window flags changed geometry or did not bind the exact lockset")
    if any("+ FIXED " not in protected[name] for name in locked):
        raise ValueError("one or more locked nets were released during DRT")
    for kind in ("COMPONENTS", "SPECIALNETS"):
        actual = comparison.def_section(original, kind)
        if any(comparison.def_section(path, kind) != actual for path in files[1:]):
            raise ValueError(f"the capture window changed {kind}")
    if (out / "original.guide").read_bytes() != (out / "bounded.guide").read_bytes():
        raise ValueError("the capture window changed embedded guides")
    changed = []
    for name, entry in before.items():
        old, updated, final = map(phase.normalize_net, (entry, protected[name], normalized[name]))
        if old[0] != updated[0] or updated != final or "+ FIXED " in normalized[name]:
            raise ValueError(f"connectivity or status-only final normalization failed for {name}")
        if old != updated:
            area = loc["clock_window_dbu" if name == loc["shared_leaf"] else "signal_window_dbu"]
            if name not in allowed or not inside(points(protected[name]), area):
                raise ValueError(f"route escaped its permitted capture window: {name}")
            changed.append(name)
    log = (out / "route.log").read_text(encoding="utf-8")
    expected_clear = [loc["optional_clear"]] if mode == "clear_capture_d" else []
    if phase.PA in log or re.findall(r"(?m)^CLEAR_CAPTURE_D (.+)$", log) != expected_clear:
        raise ValueError("unexpected PA or cleared route scope")
    return {"changed_nets": sorted(changed), "protected_net_count": len(locked), "cleared": expected_clear,
            "protected_def": comparison.bind(files[2]), "normalized_def": comparison.bind(files[3])}


def run_trial(eval, out, case, profile, baseline, mode):
    started = RAW()
    def render(args, libs, control, destination, edits):
        return deck_for(destination, profile, baseline, mode)
    with patch.object(comparison, "render_route", render), patch.object(eval.args, "route_timeout", ROUTE_LIMIT):
        _, physical = eval.evaluate(tuple(case["proposal"]["actions"]), out, envelope_only=True)
    gate = phase.sweep.budget_gate(eval, 1.0, False)
    failures = list(dict.fromkeys(physical["failures"] + phase.audit_timing(eval, physical, gate, False)))
    result = {"mode": mode, "physical": comparison.bind(out / "receipt.json"), "failures": failures,
              "views": physical["views"], "sec": None}
    if "artifacts" in physical:
        try:
            result["scope_check"] = check_window(out, profile, mode)
        except (ValueError, OSError) as err:
            failures.append(str(err))
        audit = phase.independent_physical(eval, physical["artifacts"], out / "independent")
        result["independent"] = audit
        failures.extend(audit["failures"])
        before_sec = RAW()
        charges = {}
        passed = eval.proof(verify(physical["artifacts"]["v"]), out, charges)
        proof_path = out / "sec/receipt.json"
        proof = read(proof_path) if proof_path.is_file() else {}
        if (not passed or not proof.get("passed") or (proof.get("proven"), proof.get("unproven")) != (567, 0)
                or proof.get("gate") != physical["artifacts"]["v"] or proof.get("gold") != comparison.bind(eval.control["v"])):
            failures.append("sec")
        result["sec"] = {"proven": proof.get("proven"), "unproven": proof.get("unproven"), "operations": charges}
    else:
        before_sec = RAW()
    finished = RAW()
    result["all_checks_raw_seconds"] = finished - started
    result["paid_raw_seconds"] = (finished if not set(failures) - {"sec"} else before_sec) - started
    result["qualified_area_um2"] = physical.get("area_saved") if not failures else None
    comparison.save(out / "capture_window_result.json", result)
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("old_rescue", type=Path)
    parser.add_argument("full_unlock", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    old = args.old_rescue.resolve(strict=True) / "results.json"
    unlock = args.full_unlock.resolve(strict=True) / "results.json"
    prior, full = map(read, (old, unlock))
    source = read(verify(prior["protocol"]))
    if read(verify(full["protocol"]))["source"] != comparison.bind(old):
        raise ValueError("full-unlock receipts belong to a different cohort")
    chosen = {case["proposal"]["label"]: case for case in prior["cases"] if case["proposal"]["label"] in CASES}
    baseline = {case["label"]: case for case in full["cases"] if case["label"] in CASES}
    if tuple(chosen) != CASES or set(baseline) != set(CASES) or sorted(os.sched_getaffinity(0)) != source["affinity"]:
        raise ValueError("wrong case order or CPU affinity")
    profiles = {label: locate(case) for label, case in chosen.items()}
    for label, loc in profiles.items():
        if loc["source_odb"] != baseline[label]["source_rejected_odb"]:
            raise ValueError("the limited route is not paired on the original ODB")
    out = args.output.resolve()
    out.mkdir()
    protocol = out / "protocol.json"
    comparison.save(protocol, {"source": comparison.bind(old), "full_unlocked": comparison.bind(unlock),
                               "driver": comparison.bind(Path(__file__).resolve()), "profiles": profiles,
                               "case_order": CASES, "policy": "only shared TT capture leaf and contained same-path feedback wires",
                               "optional_step": "clear the local TT D feeder once, only if retaining its wire fails",
                               "route_timeout": ROUTE_LIMIT, "time_clock": "CLOCK_MONOTONIC_RAW", "affinity": source["affinity"]})
    seed = read(verify(source["source"]))
    online = read(verify(source["historical_online_protocol"]))
    assets = seed["bindings"]
    control = {key: verify(ref) for key, ref in assets["control"].items()}
    lib = {corner: [verify(ref) for ref in refs] for corner, refs in assets["used_libraries"].items()}
    runtime = seed_args(seed, online)
    runtime.out = out
    reference = read(verify(source["reference"]))["views"]
    rows = []
    with GEOMETRY.bind_runtime("uart", verify(assets["flow"]["fastroute.tcl"])):
        masters = comparison.logical_masters(control["v"], comparison.liberty_areas(lib["TT"]))
        pool = [comparison.PhysicalAction(**row) for row in online["ordered_pool"]]
        eval = comparison.Evaluator(runtime, control, lib, masters, reference, pool, seed["scope"])
        for label in CASES:
            dest = out / label
            dest.mkdir()
            case, loc, old_row = chosen[label], profiles[label], baseline[label]
            attempts = []
            for mode in ("keep_wires", "clear_capture_d"):
                trial = run_trial(eval, dest / mode, case, loc, old_row, mode)
                attempts.append(trial)
                print(label, mode, trial["failures"], round(trial["paid_raw_seconds"], 4), flush=True)
                if not trial["failures"]:
                    break
            paid = loc["selection_raw_seconds"] + sum(row["paid_raw_seconds"] for row in attempts)
            frontier = prior["best_with_reentry_um2"]
            gain = max(0, (attempts[-1]["qualified_area_um2"] or 0) - frontier)
            rows.append({"label": label, "attempts": attempts, "paid_with_scope_raw_seconds": paid,
                         "unlocked_raw_seconds": old_row["trigger_additional_raw_seconds"], "unlocked_failures": old_row["failures"],
                         "previous_frontier_um2": frontier, "net_gain_um2": gain})
            comparison.save(out / "progress.json", rows)
    comparison.save(out / "results.json", {"protocol": comparison.bind(protocol), "cases": rows,
                                             "distinct_net_gain_um2": max(row["net_gain_um2"] for row in rows)})


if __name__ == "__main__":
    main()
