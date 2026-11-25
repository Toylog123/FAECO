#!/usr/bin/env python3
"""Charge GCD route previews and complete physical trials on the same frozen pair."""

from argparse import ArgumentParser
from dataclasses import asdict
import math
import os
from pathlib import Path
import re
from types import SimpleNamespace

from probe_gcd_hold_geometry_transfer import comparison, geometry, read, verify
from probe_aes_selective_repair import ROUTING_TYPE, audit_timing, normalize_net
import run_setup_budget_sweep as sweep


CORNERS = ("TT", "SS")
ORDER = (("r091", "r093"), ("r093", "r091"))
MODES = ("grt", "local", "full")
LOCAL_ITERS = 2
NEIGHBORS = 20
HALO_TRACKS = 3
ROUTE_TIMEOUT = {"grt": 30.0, "local": 35.0, "full": 60.0}


def edit_scope(features, frozen_def, actions):
    inputs = comparison.def_section(frozen_def, "NETS")
    wires = {name: geometry.segments(record) for name, record in inputs.items() if ROUTING_TYPE.search(record)}
    steps = geometry.track_steps(frozen_def)
    layer_number = {name: index for index, name in enumerate(("li1", "met1", "met2", "met3", "met4", "met5"))}
    direct = {net for action in actions for net in features["actions"][action]["incident_nets"]}
    clocks = {net for view in CORNERS for path in features["stages"]["frozen"][view]["paths"] for net in path["clock"]}
    if not (direct | clocks) <= wires.keys() or any("+ USE SIGNAL" not in inputs[net] for net in direct):
        raise ValueError("direct or clock scope does not bind the original placed design")

    def bounds(wire):
        _, axis, fixed, low, high = wire
        return (low, high, fixed, fixed) if axis == 0 else (fixed, fixed, low, high)

    def nearby(net):
        distance = math.inf
        for victim in wires[net]:
            v_layer, v_axis = victim[:2]
            x0, x1, y0, y1 = bounds(victim)
            for source in active:
                s_layer, s_axis = source[:2]
                if abs(layer_number[v_layer] - layer_number[s_layer]) > 1:
                    continue
                a0, a1, b0, b1 = bounds(source)
                gap = max(0, x0 - a1, a0 - x1) + max(0, y0 - b1, b0 - y1)
                pitch = max(steps[v_layer, v_axis], steps[s_layer, s_axis])
                distance = min(distance, gap / pitch)
        return distance

    active = [segment for net in direct for segment in wires[net]]
    candidates = sorted((nearby(net), net) for net in wires.keys() - direct - clocks if "+ USE SIGNAL" in inputs[net])
    neighbors = {net for distance, net in candidates[:NEIGHBORS] if distance <= HALO_TRACKS}
    allowed = direct | clocks | neighbors
    fixed = {net: inputs[net] for net in wires.keys() - allowed}
    return direct, clocks, neighbors, fixed


def fixed_patch(out, frozen_def, fixed):
    header = "\n".join(re.findall(r"(?m)^(?:VERSION|DIVIDERCHAR|BUSBITCHARS|DESIGN|UNITS) .+?;$",
                                  frozen_def.read_text(encoding="utf-8")))
    if len(header.splitlines()) != 5 or not fixed:
        raise ValueError("cannot generate a fixed-net DEF fragment")
    entries = [f"- {net} {ROUTING_TYPE.sub(r'\g<1>FIXED\g<3>', text, count=1)} ;" for net, text in sorted(fixed.items())]
    patch = out / "fixed_wires.def"
    patch.write_text(header + f"\nNETS {len(fixed)} ;\n" + "\n".join(entries) + "\nEND NETS\nEND DESIGN\n", encoding="utf-8")
    return patch


def render_preview(evaluator, actions, out, mode, features):
    control = evaluator.control
    _, edits = evaluator.expected_masters(actions)
    tcl = comparison.tcl
    source = comparison.render_route(evaluator.args, evaluator.libraries["TT"], control, out, edits)
    if mode == "local":
        direct, clocks, neighbors, fixed = edit_scope(features, control["def"], actions)
        patch = fixed_patch(out, control["def"], fixed)
        head, tail = source.split("read_sdc ", 1)
        source = head + f"read_def -floorplan_initialize {tcl(patch)}\nwrite_def {tcl(out / 'pre.def')}\nread_sdc " + tail
        source = source.replace("-droute_end_iter 64", f"-droute_end_iter {LOCAL_ITERS}", 1)
        source = source.replace("detailed_route -output_drc", 'set preview_route_start [clock microseconds]\ndetailed_route -output_drc', 1)
        source = source.replace('puts "IBEX_DRT_VIOLATIONS', 'puts "PREVIEW_DRT_US [expr {[clock microseconds] - $preview_route_start}]"\nputs "IBEX_DRT_VIOLATIONS', 1)
        source = source.replace("define_process_corner", "set preview_rcx_start [clock microseconds]\ndefine_process_corner", 1)
        source = source.replace("puts IBEX_RCX_COMPLETE", 'puts "PREVIEW_RCX_US [expr {[clock microseconds] - $preview_rcx_start}]"\nputs IBEX_RCX_COMPLETE', 1)
        return source, {"direct": sorted(direct), "min_path_clock": sorted(clocks), "neighbors": sorted(neighbors), "fixed": sorted(fixed)}

    head, body = source.split('if {![grt::have_routes]}', 1)
    enable = f"read_spef {tcl(control['spef'])}\nset preview_route_start [clock microseconds]\nglobal_route -start_incremental\n"
    if edits:
        head = head.replace("\nset inst [", "\n" + enable + "set inst [", 1)
    else:
        head += enable
    writes = "set ::env(REPORTS_DIR)" + body.split("set ::env(REPORTS_DIR)", 1)[1].split("define_process_corner", 1)[0]
    result = head + f"""global_route -end_incremental
puts "PREVIEW_GRT_US [expr {{[clock microseconds] - $preview_route_start}}]"
if {{![grt::have_routes]}} {{error "No updated GRT routes"}}
write_guides {tcl(out / 'after.guide')}
{writes}
set preview_rcx_start [clock microseconds]
estimate_parasitics -global_routing -spef_file {tcl(out / 'routed.spef')}
puts "PREVIEW_ESTIMATE_US [expr {{[clock microseconds] - $preview_rcx_start}}]"
puts IBEX_ROUTE_COMPLETE
exit
"""
    return result, {}


def hold_floor(views, tolerance, absolute):
    return {corner: max(absolute, views[corner]["hold_wns_ps"] - tolerance) for corner in CORNERS}


def physical_view(evaluator, out, corner):
    tcl, log = out / f"sta_{corner}.tcl", out / f"sta_{corner}.log"
    tcl.write_text(comparison.render_sta(evaluator.libraries[corner], out / "routed.v", evaluator.control["sdc"],
                                         out / "routed.spef"), encoding="utf-8")
    process = comparison.run_process([evaluator.args.sta, "-exit", tcl], log, 20.0)
    output = comparison.checked_output(process, "IBEX_STA_COMPLETE")
    view = comparison.parse_sta(output)
    if view["ports"] != evaluator.ref_views[corner]["ports"]:
        raise ValueError(f"preview changed original {corner} port scope")
    view["unannotated"] = {label: int(count) for count, label in
                            re.findall(r"(?m)^Found (\d+) ((?:partially )?unannotated drivers)\.$", output)}
    return view, asdict(process)


def run_preview(evaluator, mode, out, actions, features):
    out.mkdir()
    start = geometry.raw_seconds()
    source, scope = render_preview(evaluator, actions, out, mode, features)
    script, log = out / "route.tcl", out / "route.log"
    script.write_text(source, encoding="utf-8")
    comparison.save(out / "scope.json", scope)
    proc = comparison.run_process([evaluator.args.openroad, "-threads", str(evaluator.args.threads), "-exit", script],
                                  log, ROUTE_TIMEOUT[mode])
    data = {"actions": actions, "mode": mode, "route_process": asdict(proc), "scope": scope, "views": {}, "sta": {}, "error": None}
    try:
        output = comparison.checked_output(proc, "IBEX_ROUTE_COMPLETE")
        data["phase_microseconds"] = {name: int(cost) for name, cost in re.findall(r"(?m)^PREVIEW_(\w+)_US (\d+)$", output)}
        data["artifacts"] = {key: comparison.bind(out / f"routed.{key}") for key in ("odb", "def", "v", "spef")}
        expected, _ = evaluator.expected_masters(actions)
        if expected != comparison.logical_masters(out / "routed.v", evaluator.areas):
            raise ValueError("preview changed functional masters outside the specified swaps")
        data["layout"] = comparison.changed_geometry(evaluator.control["def"], out / "routed.def", set(scope.get("direct", ())))
        if mode == "local":
            before, pre, after = [comparison.def_section(path, "NETS") for path in
                                  (evaluator.control["def"], out / "pre.def", out / "routed.def")]
            observed_fixed = {name for name, row in pre.items() if "+ FIXED " in row}
            changed = [name for name in scope["fixed"] if normalize_net(before[name]) != normalize_net(after[name])]
            data["fixed_changed"] = changed
            if observed_fixed != set(scope["fixed"]) or changed or data["layout"]["changed_component_placement"]:
                raise ValueError("route escaped the frozen scope")
            data["preview_drc"] = int(re.search(r"(?m)^IBEX_DRT_VIOLATIONS (\d+)$", output)[1])
        for corner in CORNERS:
            data["views"][corner], data["sta"][corner] = physical_view(evaluator, out, corner)
    except (comparison.TrialFailure, OSError, ValueError) as err:
        data["error"] = str(err)
    data["elapsed_raw_seconds"] = geometry.raw_seconds() - start
    comparison.save(out / "preview.json", data)
    return data


def run_full(evaluator, out, actions):
    start = geometry.raw_seconds()
    _, row = evaluator.evaluate(actions, out, envelope_only=True)
    gate = sweep.budget_gate(evaluator, 1.0, False)
    failures = list(dict.fromkeys(row["failures"] + audit_timing(evaluator, row, gate, False)))
    proof = {}
    if not failures and not evaluator.proof(verify(row["artifacts"]["v"]), out, proof):
        failures.append("sec")
    data = {"actions": actions, "mode": "full", "views": row["views"], "failures": failures,
            "physical": comparison.bind(out / "receipt.json"), "proof": proof,
            "elapsed_raw_seconds": geometry.raw_seconds() - start}
    comparison.save(out / "full_gate.json", data)
    return data


def compare_cost(cases, reference, floors, zero):
    blocks = []
    for index in (1, 2):
        base = {key: cases[f"{index}_full_{key}"] for key in ORDER[0]}
        label = {key: {c: row["views"][c]["hold_wns_ps"] >= floors[c] for c in CORNERS} for key, row in base.items()}
        if label != {"r091": dict.fromkeys(CORNERS, False), "r093": dict.fromkeys(CORNERS, True)} or base["r093"]["failures"]:
            raise ValueError("fresh full physical pair does not reproduce the audited acceptance split")
        full_cost = math.fsum(row["elapsed_raw_seconds"] for row in base.values())
        modes = {}
        for mode in ("grt", "local"):
            scored, passed = {}, {}
            pre = {key: cases[f"{index}_{mode}_{key}"] for key in ORDER[0]}
            preview_cost = math.fsum(row["elapsed_raw_seconds"] for row in pre.values())
            zero_cost = zero["elapsed_raw_seconds"] if mode == "grt" else 0.0
            for key, row in pre.items():
                usable = not row["error"] and (mode != "grt" or not zero["error"])
                if usable:
                    scored[key] = {}
                    for corner in CORNERS:
                        view = row["views"][corner]
                        annotated = view["unannotated"]
                        if mode == "grt" and annotated != zero["views"][corner]["unannotated"]:
                            usable = False
                        if not annotated or annotated.get("partially unannotated drivers", 1) != 0:
                            usable = False
                        value = view["hold_wns_ps"]
                        if mode == "grt":
                            value += reference[corner]["hold_wns_ps"] - zero["views"][corner]["hold_wns_ps"]
                        scored[key][corner] = value
                passed[key] = {c: scored[key][c] >= floors[c] for c in CORNERS} if usable else None
            correct = passed == label
            projected = preview_cost + zero_cost + base["r093"]["elapsed_raw_seconds"]
            modes[mode] = {"adjusted_hold_wns_ps": scored, "prediction": passed, "correct_tt_ss": correct,
                           "preview_cost_seconds": preview_cost, "calibration_seconds": zero_cost,
                           "preview_pair_plus_pass_full_seconds": projected, "saving_seconds": full_cost - projected if correct else None,
                           "eligible": correct and projected < full_cost}
        blocks.append({"block": index, "full_label": label, "full_pair_seconds": full_cost, "modes": modes})
    return blocks


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("transfer", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    transfer = args.transfer.resolve(strict=True)
    # The label-free score receipt supplies the pool and reference timing-path geometry.
    score = read(transfer / "scores.json")
    bound = read(verify(score["protocol"]))
    seed = read(verify(bound["seed"]))
    feature = score["features"]
    assets = seed["bindings"]
    control = {key: verify(path) for key, path in assets["control"].items()}
    flow = {key: verify(path) for key, path in assets["flow"].items()}
    tools = {key: verify(path) for key, path in assets["tools"].items()}
    pool = [comparison.PhysicalAction(**row) for row in read(verify(bound["pool"]))]
    library = {corner: [verify(item) for item in view] for corner, view in assets["used_libraries"].items()}
    reference = read(verify(bound["reference"]))["views"]
    identities = {comparison.canonical_odb_name(action.instance): action.action_id for action in pool}
    actions = {f"r{tail}": tuple(sorted(identities[f"_{name}_"] for name in ("089", "090", tail))) for tail in ("091", "093")}
    if sorted(os.sched_getaffinity(0)) != seed["cpu_affinity"]:
        raise ValueError("use the original recorded CPU affinity")
    out = args.out.resolve()
    out.mkdir()
    runtime = SimpleNamespace(out=out, orfs=flow["setRC.tcl"].parents[2], pdk=seed["pdk"], route_mode="local",
                              droute_iters=64, embedded_guides=True, single_pin_access=True, zero_reextract=False,
                              report_setup_endpoints=True, threads=seed["methods_route_threads"], clock_period_ps=seed["original_clock_period_ps"],
                              openroad=tools["openroad"], sta=tools["opensta"], sec=tools["sec"],
                              route_timeout=ROUTE_TIMEOUT["full"], sta_timeout=20.0, sec_timeout=30.0)
    floors = hold_floor(reference, bound["hold_tolerance_ps"], bound["absolute_hold_ps"])
    comparison.save(out / "protocol.json", {"score": comparison.bind(transfer / "scores.json"), "seed": bound["seed"],
                                             "driver": comparison.bind(Path(__file__).resolve()), "actions": actions, "hold_floors_ps": floors,
                                             "modes": MODES, "order": ORDER, "local_iters": LOCAL_ITERS,
                                             "route_timeout_seconds": ROUTE_TIMEOUT, "affinity": seed["cpu_affinity"],
                                             "geometry_neighbor_limit": NEIGHBORS, "geometry_halo_tracks": HALO_TRACKS})
    with geometry.bind_runtime("gcd", flow["fastroute.tcl"]):
        masters = comparison.logical_masters(control["v"], comparison.liberty_areas(library["TT"]))
        evaluator = comparison.Evaluator(runtime, control, library, masters, reference, pool, seed["scope"])
        zero = run_preview(evaluator, "grt", out / "zero_grt", (), feature)
        cases = {}
        for index, order in enumerate(ORDER, 1):
            for mode in (MODES if index == 1 else MODES[::-1]):
                for key in order:
                    label = f"{index}_{mode}_{key}"
                    trial = out / label
                    data = run_full(evaluator, trial, actions[key]) if mode == "full" else run_preview(evaluator, mode, trial, actions[key], feature)
                    cases[label] = data
                    comparison.save(out / "progress.json", {"zero": zero, "cases": cases})
                    print(label, round(data["elapsed_raw_seconds"], 3), data.get("error") or data.get("failures"),
                          {c: v["hold_wns_ps"] for c, v in data["views"].items()}, flush=True)
        blocks = compare_cost(cases, reference, floors, zero)
    comparison.save(out / "results.json", {"protocol": comparison.bind(out / "protocol.json"),
                                             "comparisons": blocks, "zero": zero, "cases": cases,
                                             "eligible_modes": [mode for mode in ("grt", "local") if all(block["modes"][mode]["eligible"] for block in blocks)]})


if __name__ == "__main__":
    main()
