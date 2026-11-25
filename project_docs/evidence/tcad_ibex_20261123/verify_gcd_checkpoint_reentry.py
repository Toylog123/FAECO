#!/usr/bin/env python3
"""Audit checkpoint continuity even on re-entry trials without a final endpoint."""

from argparse import ArgumentParser
from pathlib import Path
import re

from probe_gcd_local_route_reentry import PA, STEPS, comparison, normalize_net, read, verify
from probe_gcd_incremental_hold_rc import spef


def snapshot_audit(root, frozen):
    before, after = (root / name for name in ("checkpoint.def", "unlocked.def"))
    old, new = (comparison.def_section(path, "NETS") for path in (before, after))
    fixed = sorted(net for net, entry in old.items() if "+ FIXED " in entry)
    intended = read(root / "resume_scope.json")["fixed"]
    if sorted(intended) != fixed or any(normalize_net(old[net]) != normalize_net(frozen[net]) for net in fixed):
        raise ValueError(f"{root}: the checkpoint violated the nominal protection scope")
    if old.keys() != new.keys() or any(
            "+ FIXED " in new[net] or normalize_net(old[net]) != normalize_net(new[net]) for net in old):
        raise ValueError(f"{root}: status re-encoding changed the checkpoint nets")
    for kind in ("COMPONENTS", "SPECIALNETS"):
        if comparison.def_section(before, kind) != comparison.def_section(after, kind):
            raise ValueError(f"{root}: lost {kind} on unlock")
    match_guides = (root / "checkpoint.guide").read_bytes() == (root / "unlocked.guide").read_bytes()
    if not match_guides:
        raise ValueError(f"{root}: guide retrieval changed")
    log = root / "route.log"
    first, rest = log.read_text(encoding="utf-8").split(STEPS[0], 1)
    fixed_marker = re.findall(r"(?m)^CHECKPOINT_DRT_VIOLATIONS (\d+)$", first)
    if len(fixed_marker) != 1:
        raise ValueError(f"{root}: missing original checkpoint violation count")
    resume = re.findall(r"\[INFO DRT-0627\] Found (\d+) DRC marker\(s\) in the database; resuming detailed routing from iteration (\d+)", rest)
    if len(resume) != 1 or int(resume[0][0]) != int(fixed_marker[0]):
        raise ValueError(f"{root}: router did not report resuming the saved markers")
    return {"route_log": comparison.bind(log), "checkpoint_odb": comparison.bind(root / "checkpoint.odb"),
            "checkpoint_def": comparison.bind(before), "released_def": comparison.bind(after), "released_nets": len(fixed),
            "all_nets": len(old), "same_guides": match_guides, "pa_on_first_stage": first.count(PA),
            "pa_on_resumed_stage": rest.count(PA), "markers": int(resume[0][0]), "restart_iter": int(resume[0][1]),
            "resumed_drt_finished": STEPS[1] in rest, "final_route_rejected_as_unrouted": "Unrouted nets after resumed DRT" in rest,
            "stage_microseconds": {name: int(us) for name, us in re.findall(r"(?m)^((?:PREVIEW|RESUME)_\w+)_US (\d+)$", first + rest)}}


def audit_measurement(run):
    path = run / "results.json"
    results = read(path)
    protocol = read(verify(results["protocol"]))
    verify(protocol["driver"])
    before = read(verify(protocol["seed"]))["bindings"]["control"]["def"]
    frozen = comparison.def_section(verify(before), "NETS")
    audit = {}
    for name, trial in results["cases"].items():
        if trial["mode"] == "direct":
            continue
        row = read(verify(trial["physical"]))
        folder = Path(trial["physical"]["path"]).parent
        status = snapshot_audit(folder, frozen)
        if status["pa_on_first_stage"] != 1 or status["pa_on_resumed_stage"] != int(not protocol["resume_skips_pin_access"]):
            raise ValueError(f"{name}: unexpected PA invocation count")
        status["route_process"] = row["operations"]["DRT_RCX"]
        status["full_original_timing_available"] = len(trial["views"]) == 3
        status["preflight_failures"] = trial["failures"]
        audit[name] = status
    completed_endpoints = {}
    for name, trial in results["cases"].items():
        if trial["mode"] != "resume" or not trial["views"]:
            continue
        paired = results["cases"][name.replace("_resume_", "_direct_", 1)]
        completed_endpoints[name] = route_deltas(paired, trial)
    return {"result": comparison.bind(path), "same_process": protocol["same_process_resume"], "cases": audit,
            "completed_endpoint_deltas": completed_endpoints}


def route_deltas(direct, resumed):
    physical = [read(verify(row["physical"])) for row in (direct, resumed)]
    args = [row["artifacts"] for row in physical]
    layouts = [comparison.def_section(verify(row["def"]), "NETS") for row in args]
    if layouts[0].keys() != layouts[1].keys():
        raise ValueError("final net identities differ")
    differences = [name for name, old in layouts[0].items() if normalize_net(old) != normalize_net(layouts[1][name])]
    clocks = [name for name in differences if "+ USE CLOCK" in layouts[0][name]]
    parasitics = [spef(verify(row["spef"]))[1] for row in args]
    tracked = sorted(set(clocks) | {"clk", "clknet_0_clk"})
    cap_reference = {name: [float(item[name][2]) * 1000 for item in parasitics] for name in tracked}
    return {"same_functional_netlist": args[0]["v"]["sha256"] == args[1]["v"]["sha256"],
            "changed_nets": sorted(differences), "changed_clock_nets": sorted(clocks),
            "clock_c_fF_direct_resume": cap_reference,
            "hold_delta_ps": {corner: resumed["views"][corner]["hold_wns_ps"] - direct["views"][corner]["hold_wns_ps"]
                              for corner in comparison.CORNERS}}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("runs", type=Path, nargs="+")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    comparison.save(args.output, {"driver": comparison.bind(Path(__file__).resolve()),
                                  "audits": [audit_measurement(root.resolve(strict=True)) for root in args.runs]})


if __name__ == "__main__":
    main()
