#!/usr/bin/env python3
"""Compare fresh GCD DRT with reusing the unlocked cutoff layout in one tool process."""

from argparse import ArgumentParser
from dataclasses import asdict
from hashlib import sha256
import math
import os
from pathlib import Path
import re
from types import SimpleNamespace
from unittest.mock import patch

from probe_gcd_local_hold_preview import audit_timing, comparison, geometry, normalize_net, read, render_preview, sweep, verify


ORDER = (
    (("direct", "r091"), ("resume", "r091"), ("direct", "r093"), ("resume", "r093")),
    (("resume", "r093"), ("direct", "r093"), ("resume", "r091"), ("direct", "r091")),
)
FIXED_COUNT = 452
PA = "[INFO DRT-0165] Start pin access."
STEPS = ("RESUME_BEFORE_DRT", "RESUME_AFTER_DRT")


def resume_renderer(evaluator, actions, out, features, with_pa):
    tcl = comparison.tcl
    source, scope = render_preview(evaluator, actions, out, "local", features)
    if len(scope["fixed"]) != FIXED_COUNT:
        raise ValueError("checkpoint did not use the measured 452-net scope")
    comparison.save(out / "resume_scope.json", scope)
    head, ending = source.split("puts IBEX_DRT_COMPLETE\n", 1)
    ending = ending.replace("set preview_rcx_start", "set finish_rcx_start", 1).replace("$preview_rcx_start", "$finish_rcx_start", 1)
    head = head.replace(str(out / "drc.rpt"), str(out / "checkpoint_drc.rpt"))
    head = head.replace('puts "IBEX_DRT_VIOLATIONS', 'puts "CHECKPOINT_DRT_VIOLATIONS', 1)
    no_pa = "" if with_pa else " -no_pin_access"
    unlock = f"""
set restore_start [clock microseconds]
write_db {tcl(out / 'checkpoint.odb')}
write_def {tcl(out / 'checkpoint.def')}
write_guides {tcl(out / 'checkpoint.guide')}
set checkpoint_fd [open {tcl(out / 'checkpoint.def')} r]
set snapshot [read $checkpoint_fd]
close $checkpoint_fd
set first [string first "\\nNETS " $snapshot]
set last [string first "\\nEND NETS" $snapshot]
if {{$first < 0 || $last <= $first}} {{error "Missing checkpoint DEF NETS section"}}
set section [string range $snapshot $first [expr {{$last - 1}}]]
set unlocked_count [regsub -all {{\+ FIXED }} $section {{+ ROUTED }} unlocked]
if {{$unlocked_count != {FIXED_COUNT}}} {{error "Wrong number of fixed paths for resume: $unlocked_count"}}
set patch_fd [open {tcl(out / 'unlock.def')} w]
set header 0
foreach line [split $snapshot "\\n"] {{
    if {{[regexp {{^(VERSION|DIVIDERCHAR|BUSBITCHARS|DESIGN|UNITS) }} $line]}} {{
        puts $patch_fd $line
        incr header
    }}
    if {{[string match "DIEAREA *" $line]}} {{break}}
}}
if {{$header != 5}} {{close $patch_fd; error "Invalid checkpoint DEF header"}}
puts $patch_fd $unlocked
puts $patch_fd "END NETS\\nEND DESIGN"
close $patch_fd
read_def -floorplan_initialize {tcl(out / 'unlock.def')}
write_def {tcl(out / 'unlocked.def')}
if {{![grt::have_routes] || ![design_is_routed]}} {{error "Checkpoint lost guides or wires on unlock"}}
write_guides {tcl(out / 'unlocked.guide')}
puts "RESUME_SAVE_UNLOCK_US [expr {{[clock microseconds] - $restore_start}}]"
puts {STEPS[0]}
set resume_start [clock microseconds]
detailed_route -output_drc {tcl(out / 'drc.rpt')} -verbose 1 -droute_end_iter 64{no_pa}
puts "RESUME_FINISH_DRT_US [expr {{[clock microseconds] - $resume_start}}]"
puts {STEPS[1]}
puts "IBEX_DRT_VIOLATIONS [detailed_route_num_drvs]"
if {{![design_is_routed]}} {{error "Unrouted nets after resumed DRT"}}
check_placement -verbose
puts IBEX_DRT_COMPLETE
"""
    return head + unlock + ending


def independent_physical(evaluator, artifacts, out):
    out.mkdir()
    tcl = comparison.tcl
    odb = verify(artifacts["odb"])
    source = out / "audit.tcl"
    final = out / "readback.def"
    report = out / "drc.rpt"
    antenna = out / "antenna.rpt"
    source.write_text(f"""read_db {tcl(odb)}
if {{![design_is_routed]}} {{error "Unexpected unrouted final state"}}
write_def {tcl(final)}
drt::check_drc -output_file {tcl(report)}
puts "RESUME_INDEPENDENT_ANTENNA [check_antennas -report_file {tcl(antenna)}]"
puts RESUME_INDEPENDENT_COMPLETE
exit
""", encoding="utf-8")
    process = comparison.run_process([evaluator.args.openroad, "-no_init", "-no_splash", "-threads", "4", "-exit", source],
                                     out / "audit.log", 45)
    result = {"operation": asdict(process), "failures": []}
    try:
        output = comparison.checked_output(process, "RESUME_INDEPENDENT_COMPLETE")
        layouts = [comparison.def_section(path, "NETS") for path in (verify(artifacts["def"]), final)]
        if (layouts[0] != layouts[1]) or any("+ FIXED " in entry for entry in layouts[1].values()):
            raise ValueError("final geometry or unlock flags changed at independent readback")
        markers = report.read_text(encoding="utf-8")
        kinds = re.findall(r"(?m)^violation type:\s*(.+)$", markers)
        if markers.strip() and not kinds:
            raise ValueError("independent DRC report format changed")
        observed = re.findall(r"(?m)^RESUME_INDEPENDENT_ANTENNA (\d+)(?:\.0+)?$", output)
        if len(observed) != 1:
            raise ValueError("missing independent antenna count")
        result.update(drc=len(kinds), antenna=int(observed[0]), drc_report=comparison.bind(report),
                      def_readback=comparison.bind(final), antenna_report=comparison.bind(antenna))
        if kinds:
            result["failures"].append("independent_drc")
        if result["antenna"]:
            result["failures"].append("antenna")
    except (comparison.TrialFailure, OSError, ValueError) as error:
        result["failures"].append(str(error))
    comparison.save(out / "audit.json", result)
    return result


def verify_checkpoint(evaluator, out, text, with_pa):
    # Use all of the checkpoint readbacks, including geometry outside the route window.
    before, checkpoint, unlock, final = [comparison.def_section(path, "NETS") for path in
                                         (evaluator.control["def"], out / "checkpoint.def", out / "unlocked.def", out / "routed.def")]
    fixed = set(read(out / "resume_scope.json")["fixed"])
    if {net for net, entry in checkpoint.items() if "+ FIXED " in entry} != fixed or any(
            normalize_net(checkpoint[net]) != normalize_net(before[net]) for net in fixed):
        raise ValueError("the checkpoint lost its frozen wires")
    if checkpoint.keys() != unlock.keys() or any(
            "+ FIXED " in unlock[net] or normalize_net(checkpoint[net]) != normalize_net(unlock[net]) for net in checkpoint):
        raise ValueError("unlock changed geometry or did not release every wire")
    for kind in ("COMPONENTS", "SPECIALNETS"):
        if comparison.def_section(out / "checkpoint.def", kind) != comparison.def_section(out / "unlocked.def", kind):
            raise ValueError(f"unlock changed {kind}")
    if (out / "checkpoint.guide").read_bytes() != (out / "unlocked.guide").read_bytes():
        raise ValueError("unlock changed embedded guides")
    first, second = text.split(STEPS[0], 1)
    if first.count(PA) != 1 or second.count(PA) != int(with_pa) or STEPS[1] not in second:
        raise ValueError("pin-access pass count or second-stage completion is not as specified")
    return {"saved_odb": comparison.bind(out / "checkpoint.odb"), "saved_def": comparison.bind(out / "checkpoint.def"),
            "unlocked_def": comparison.bind(out / "unlocked.def"), "guide": comparison.bind(out / "unlocked.guide"),
            "fixed_count": len(fixed), "first_pass_pin_access": first.count(PA), "second_pass_pin_access": second.count(PA),
            "checkpoint_drc": int(re.search(r"(?m)^CHECKPOINT_DRT_VIOLATIONS (\d+)$", first)[1]),
            "changed_nets_after_resume": sorted(net for net in final if normalize_net(final[net]) != normalize_net(unlock[net]))}


def run_cell(evaluator, out, keys, mode, features):
    start = geometry.raw_seconds()
    resumed = mode != "direct"
    with_pa = mode == "resume_with_pa"
    if resumed:
        def render(args, libs, control, destination, edit_rows):
            with patch.object(comparison, "render_route", original):
                return resume_renderer(evaluator, keys, destination, features, with_pa)

        original = comparison.render_route
        with patch.object(comparison, "render_route", render):
            _, row = evaluator.evaluate(keys, out, envelope_only=True)
    else:
        _, row = evaluator.evaluate(keys, out, envelope_only=True)
    gate = sweep.budget_gate(evaluator, 1.0, False)
    old_failures = list(dict.fromkeys(row["failures"] + audit_timing(evaluator, row, gate, False)))
    result = {"actions": keys, "mode": mode, "old_failures": old_failures, "views": row["views"],
              "physical": comparison.bind(out / "receipt.json"), "failures": old_failures.copy()}
    if "artifacts" in row:
        text = (out / "route.log").read_text(encoding="utf-8")
        if resumed:
            try:
                result["checkpoint"] = verify_checkpoint(evaluator, out, text, with_pa)
            except (OSError, ValueError) as error:
                result["failures"].append(f"checkpoint: {error}")
        elif text.count(PA) != 1:
            result["failures"].append("direct_pin_access_count")
        result["route_markers_us"] = {key: int(value) for key, value in re.findall(
            r"(?m)^((?:PREVIEW|RESUME)_\w+)_US (\d+)$", text)}
        result["route_log_times"] = [float(n) for n in re.findall(r"Runtime: ([0-9.]+)s", text)]
        physical = independent_physical(evaluator, row["artifacts"], out / "independent")
        result["independent"] = physical
        result["failures"].extend(physical["failures"])
    result["before_sec_seconds"] = geometry.raw_seconds() - start
    result["sec"] = None
    if "artifacts" in row and "netlist_master_identity" not in old_failures:
        operations = {}
        passed = evaluator.proof(verify(row["artifacts"]["v"]), out, operations)
        proof = read(out / "sec/receipt.json") if (out / "sec/receipt.json").is_file() else {}
        if (not passed or not proof.get("passed") or not proof.get("proven") or proof.get("unproven") != 0
                or proof.get("gold") != comparison.bind(evaluator.control["v"]) or proof.get("gate") != row["artifacts"]["v"]):
            result["failures"].append("sec")
        result["sec"] = {"operations": operations, "proven": proof.get("proven"), "unproven": proof.get("unproven")}
    result["elapsed_raw_seconds"] = geometry.raw_seconds() - start
    qualified_before_proof = not set(result["failures"]) - {"sec"}
    result["conditional_sec_seconds"] = result["elapsed_raw_seconds"] if qualified_before_proof else result["before_sec_seconds"]
    comparison.save(out / "trial.json", result)
    return result


def physical_equivalence(a, b):
    old, new = [read(verify(trial["physical"])) for trial in (a, b)]
    fields = ("odb", "def", "v", "spef")
    if not all(all(field in item.get("artifacts", {}) for field in fields) for item in (old, new)):
        return None

    def spef(trial):
        path = verify(trial["artifacts"]["spef"])
        return sha256(b"".join(line for line in path.read_bytes().splitlines(keepends=True) if not line.startswith(b"*DATE "))).digest()

    return {**{key: old["artifacts"][key]["sha256"] == new["artifacts"][key]["sha256"] for key in fields if key != "spef"},
            "spef_without_date": spef(old) == spef(new), "views": old["views"] == new["views"]}


def summary(cases):
    rows = []
    for index in (1, 2):
        result = {}
        for role in ("r091", "r093"):
            direct, resume = [cases[f"b{index}_{mode}_{role}"] for mode in ("direct", "resume")]
            result[role] = {"equivalence": physical_equivalence(direct, resume),
                            "same_original_gate": direct["old_failures"] == resume["old_failures"],
                            "same_acceptance": bool(direct["failures"]) == bool(resume["failures"]),
                            "drc_antenna_sec_clean": all(trial.get("independent", {}).get("drc") == 0
                                and trial["independent"]["antenna"] == 0 and (trial.get("sec") or {}).get("unproven") == 0
                                and (trial.get("sec") or {}).get("proven", 0) > 0 for trial in (direct, resume))}
        costs = {mode: {"all_checks": math.fsum(cases[f"b{index}_{mode}_{role}"]["elapsed_raw_seconds"] for role in result),
                        "conditional_sec": math.fsum(cases[f"b{index}_{mode}_{role}"]["conditional_sec_seconds"] for role in result)}
                 for mode in ("direct", "resume")}
        rows.append({"index": index, "costs_seconds": costs, "candidates": result,
                     "resume_minus_direct_seconds": {name: costs["resume"][name] - costs["direct"][name] for name in costs["direct"]}})
    return rows


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("historical_preview", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--pa-diagnostic", action="store_true", help="single block of resumed DRT with normal pin access")
    args = parser.parse_args()
    prior = args.historical_preview.resolve(strict=True) / "results.json"
    earlier = read(prior)
    prior_protocol = read(verify(earlier["protocol"]))
    seed = read(verify(prior_protocol["seed"]))
    scores = read(verify(prior_protocol["score"]))
    score_meta = read(verify(scores["protocol"]))
    assets = seed["bindings"]
    frozen = {name: verify(ref) for name, ref in assets["control"].items()}
    tools = {name: verify(ref) for name, ref in assets["tools"].items()}
    flow = {name: verify(ref) for name, ref in assets["flow"].items()}
    libraries = {corner: [verify(ref) for ref in refs] for corner, refs in assets["used_libraries"].items()}
    reference = read(verify(score_meta["reference"]))["views"]
    pool = [comparison.PhysicalAction(**item) for item in read(verify(score_meta["pool"]))]
    actions = {role: tuple(items) for role, items in prior_protocol["actions"].items()}
    if seed["top"] != "gcd" or sorted(os.sched_getaffinity(0)) != seed["cpu_affinity"]:
        raise ValueError("resume benchmark must use the original GCD CPU affinity")
    out = args.output.resolve()
    out.mkdir()
    runtime = SimpleNamespace(out=out, orfs=flow["setRC.tcl"].parents[2], pdk=seed["pdk"], route_mode="local",
                              droute_iters=64, embedded_guides=True, single_pin_access=True, zero_reextract=False,
                              report_setup_endpoints=True, threads=seed["methods_route_threads"], clock_period_ps=seed["original_clock_period_ps"],
                              openroad=tools["openroad"], sta=tools["opensta"], sec=tools["sec"],
                              route_timeout=100.0, sta_timeout=20.0, sec_timeout=30.0)
    sequence = ((('resume_with_pa', 'r091'), ('resume_with_pa', 'r093')),) if args.pa_diagnostic else ORDER
    manifest = out / "protocol.json"
    comparison.save(manifest, {"prior_preview": comparison.bind(prior), "seed": prior_protocol["seed"], "actions": actions, "order": sequence,
                               "gate_lower_hold_ps": prior_protocol["hold_floors_ps"], "driver": comparison.bind(Path(__file__).resolve()),
                               "source_preview": comparison.bind(Path(render_preview.__code__.co_filename).resolve()),
                               "same_process_resume": True, "resume_skips_pin_access": not args.pa_diagnostic,
                               "cpu_affinity": seed["cpu_affinity"], "route_timeout_seconds": runtime.route_timeout})
    cases = {}
    with geometry.bind_runtime("gcd", flow["fastroute.tcl"]):
        masters = comparison.logical_masters(frozen["v"], comparison.liberty_areas(libraries["TT"]))
        evaluator = comparison.Evaluator(runtime, frozen, libraries, masters, reference, pool, seed["scope"])
        for index, order in enumerate(sequence, 1):
            for mode, role in order:
                run = f"b{index}_{mode}_{role}"
                row = run_cell(evaluator, out / run, actions[role], mode, scores["features"])
                cases[run] = row
                comparison.save(out / "progress.json", cases)
                print(run, round(row["elapsed_raw_seconds"], 3), row["failures"],
                      {key: round(info["hold_wns_ps"], 6) for key, info in row["views"].items()}, flush=True)
    comparison.save(out / "results.json", {"protocol": comparison.bind(manifest), "cases": cases,
                                             "comparisons": summary(cases) if not args.pa_diagnostic else None})


if __name__ == "__main__":
    main()
