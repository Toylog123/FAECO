#!/usr/bin/env python3
"""Replay two screened AES batches with fixed, previously routed wires."""

from argparse import ArgumentParser
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
import json
import os
import re

import compare_ibex as comparison
import run_setup_budget_sweep as sweep
from run_screened_matrix import bind_runtime


CASES = ("02", "05")
ROUTING_TYPE = re.compile(r"(\+\s+)(ROUTED|FIXED)(\s+)")


def read(path):
    return json.loads(path.read_bytes())


def verify(item):
    path = Path(item["path"])
    if comparison.bind(path) != item:
        raise ValueError(f"frozen binding changed: {path}")
    return path


def normalize_net(entry):
    connectors, _, routing = entry.partition(" + ")
    terminal = re.compile(r"\( [^()]+ \)")
    if terminal.sub("", connectors).strip():
        raise ValueError(f"unrecognized DEF connection syntax: {connectors}")
    # DEF import can reorder connection tuples. Compare the full remaining
    # suffix, changing only the initial ROUTED/FIXED wire flag.
    return sorted(terminal.findall(connectors)), ROUTING_TYPE.sub(
        r"\g<1>ROUTED\g<3>", "+ " + routing, count=1,
    )


@contextmanager
def selective_route(mode, touched_by_case, released_neighbors, frozen):
    source_render = comparison.render_route
    header, baseline_nets = frozen

    def render(args, libraries, control, out, actions):
        expected_touched = touched_by_case[out.name]
        existing = {name: entry for name, entry in baseline_nets.items() if ROUTING_TYPE.search(entry)}
        fixed = {
            name: entry for name, entry in existing.items()
            if name not in expected_touched and (mode != "clock-only" or "+ USE CLOCK" in entry)
        }
        if not {"clk", "clknet_0_clk"} <= fixed.keys():
            raise ValueError("the fixed list must contain the clock root")
        patch = out / "fixed_wires.def"
        entries = [
            f"- {name} {ROUTING_TYPE.sub(r'\g<1>FIXED\g<3>', entry, count=1)} ;"
            for name, entry in fixed.items()
        ]
        patch.write_text(
            header + f"\nNETS {len(fixed)} ;\n" + "\n".join(entries) + "\nEND NETS\nEND DESIGN\n",
            encoding="utf-8",
        )
        comparison.save(out / "routing_scope.json", {
            "mode": mode, "fixed_nets": sorted(fixed), "expected_touched_nets": sorted(expected_touched),
            "fixed_wire_patch": comparison.bind(patch), "released_neighbors": sorted(released_neighbors),
        })
        text = source_render(args, libraries, control, out, actions)
        # The pinned DEF reader applies NETS in floorplan mode to the old block.
        # Incremental mode accepts this file but skips the NETS callback.
        readback = comparison.tcl(out / "pre_drt.def")
        lock_wires = f"""read_def -floorplan_initialize {comparison.tcl(patch)}
write_def {readback}
set fp [open {readback} r]
set snapshot [read $fp]
close $fp
set first [string first "\\nNETS " $snapshot]
set last [string first "\\nEND NETS" $snapshot]
set observed [regexp -all {{[+] FIXED }} [string range $snapshot $first $last]]
if {{$first < 0 || $last < $first || $observed != {len(fixed)}}} {{
    error "Expected {len(fixed)} encoded fixed nets, read back $observed"
}}
puts "AES_SELECTIVE_FIXED_READBACK $observed"
unset snapshot
"""
        text = text.replace("read_sdc ", lock_wires + "read_sdc ", 1)
        extra = " ".join(comparison.tcl(net) for net in sorted(released_neighbors))
        if extra:
            text = text.replace("set cleared 0", f"""foreach name [list {extra}] {{
    set net [[ord::get_db_block] findNet $name]
    if {{$net eq "NULL" || [$net getSigType] ne "SIGNAL"}} {{
        error "Released neighbor must be an existing data net: $name"
    }}
    dict set nets $name $net
}}
set cleared 0""", 1)
        before_write = f"""set antenna [check_antennas -report_file {comparison.tcl(out / 'antenna.rpt')}]
puts "AES_SELECTIVE_ANTENNA $antenna"
drt::check_drc -output_file {comparison.tcl(out / 'full_drc.rpt')}
puts AES_SELECTIVE_FULL_DRC_COMPLETE
"""
        return text.replace("set ::env(REPORTS_DIR)", before_write + "set ::env(REPORTS_DIR)", 1)

    try:
        comparison.render_route = render
        yield
    finally:
        comparison.render_route = source_render


def audit_routing(directory, baseline_nets, output=None):
    scope = read(directory / "routing_scope.json")
    logfile = (directory / "route.log").read_text(encoding="utf-8")
    observed_touch = set(re.findall(r"(?m)^IBEX_TOUCHED_NET (.+)$", logfile))
    routed_nets = comparison.def_section(directory / "routed.def", "NETS")
    pre_drt_nets = comparison.def_section(directory / "pre_drt.def", "NETS")
    if baseline_nets.keys() != routed_nets.keys() or baseline_nets.keys() != pre_drt_nets.keys():
        raise ValueError("the route net identities differ from frozen CONTROL")
    changed = {
        net for net in baseline_nets
        if normalize_net(baseline_nets[net]) != normalize_net(routed_nets[net])
    }
    fixed = set(scope["fixed_nets"])
    failures = []
    expected_fixed_readback = {net for net, entry in pre_drt_nets.items() if "+ FIXED " in entry}
    if expected_fixed_readback != fixed or any(
        normalize_net(base) != normalize_net(pre_drt_nets[net]) for net, base in baseline_nets.items()
    ):
        failures.append("unexpected_pre_drt_geometry")
    if observed_touch != set(scope["expected_touched_nets"]):
        failures.append("unexpected_touched_nets")
    if changed & fixed:
        failures.append("protected_geometry_changed")
    report = directory / "full_drc.rpt"
    if (not report.is_file() or report.read_text(encoding="utf-8").strip()
            or "AES_SELECTIVE_FULL_DRC_COMPLETE" not in logfile):
        failures.append("full_drc")
    if not re.search(r"(?m)^AES_SELECTIVE_ANTENNA (0|0\.0)\s*$", logfile):
        failures.append("antenna")
    comparison.save(output or directory / "routing_audit.json", {
        "changed_nets_ignoring_route_type": sorted(changed),
        "changed_protected_nets": sorted(changed & fixed),
        "changed_untouched_nets": sorted(changed - observed_touch),
        "observed_touched_nets": sorted(observed_touch),
        "changed_released_neighbors": sorted(changed & set(scope.get("released_neighbors", ()))),
        "fixed_nets_count": len(fixed),
        "full_drc": comparison.bind(report) if report.is_file() else None,
        "failures": failures,
    })
    return failures


def audit_timing(evaluator, receipt, gate, noop):
    failures = []
    if set(receipt["views"]) != set(comparison.CORNERS):
        return ["incomplete_sta_views"]
    for corner, base in evaluator.ref_views.items():
        trial = receipt["views"][corner]
        if noop:
            for metric in ("setup_wns_ps", "setup_tns_ps", "hold_wns_ps", "hold_tns_ps"):
                if abs(base[metric] - trial[metric]) > comparison.PS_TOLERANCE:
                    failures.append(f"{corner}:zero_edit_{metric}_changed")
            continue
        failures.extend(sweep.policy.setup_gate_failures(
            corner, base["setup_wns_ps"], trial["setup_wns_ps"], gate.wns_ps,
            comparison.PS_TOLERANCE, protect_clean=gate.protect_clean,
        ))
        failures.extend(sweep.policy.tns_gate_failures(
            corner, base["setup_tns_ps"], trial["setup_tns_ps"], gate.tns_ps_by_view[corner],
            comparison.PS_TOLERANCE,
        ))
    return failures


def qualified_union(paths, matrix, control_v):
    """Bind two accepted routes and reject overlap before launching DRT."""
    actions = []
    routed_nets = set()
    neighbors = set()
    bound_inputs = []
    for path in paths:
        path = path.resolve(strict=True)
        inputs = path.with_name("inputs.json")
        if read(inputs)["matrix"] != comparison.bind(matrix):
            raise ValueError("union components must use the same frozen matrix")
        accept, = read(path).values()
        if accept["failures"] or accept["unlocked_drc"]["drc_markers"] or not accept.get("sec"):
            raise ValueError("union requires a qualified, SEC-proven endpoint")
        receipt_path = verify(accept["physical_receipt"])
        receipt = read(receipt_path)
        scope_path = receipt_path.with_name("routing_scope.json")
        scope = read(scope_path)
        audit_path = verify(accept["physical_route_preflight"])
        audit = read(audit_path)
        trial_nets = set(scope["expected_touched_nets"])
        if trial_nets != set(audit["observed_touched_nets"]) or audit["failures"]:
            raise ValueError("union component has an inconsistent allowed routing scope")
        proof_path = verify(accept["sec"]["log"]).parent / "sec/receipt.json"
        proof = read(proof_path)
        if (not proof["passed"] or proof["proven"] <= 0 or proof["unproven"] != 0
                or verify(proof["gold"]) != control_v or proof["gate"] != receipt["artifacts"]["v"]):
            raise ValueError("union proof does not bind the frozen control and routed candidate")
        verify(proof["gate"])
        if set(actions).intersection(receipt["actions"]) or routed_nets & trial_nets:
            raise ValueError("union components share edits or allowed route nets")
        actions.extend(receipt["actions"])
        routed_nets.update(trial_nets)
        neighbors.update(scope["released_neighbors"])
        bound_inputs.extend((path, inputs, receipt_path, scope_path, audit_path, proof_path))
    return tuple(actions), routed_nets, neighbors, bound_inputs


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("matrix", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("--mode", choices=("fixed-untouched", "clock-only"), default="fixed-untouched")
    p.add_argument("--route-timeout", type=int, default=240)
    p.add_argument("--case", choices=("zero", *CASES), action="append",
                   help="run only the selected case, default is zero, 02, 05")
    p.add_argument("--release-neighbor", action="append", default=[],
                   help="add one existing data net to the clear-and-reroute set for a single nonzero case")
    p.add_argument("--omit-instance", action="append", default=[],
                   help="exclude a named original edit from a single nonzero case")
    p.add_argument("--add-singleton-slot",
                   help="append the one action from a specified screened/fixed matrix slot")
    p.add_argument("--qualifying-union", type=Path, nargs=2,
                   help="combine two disjoint qualified routes using their accepted routing scopes")
    ns = p.parse_args()
    source = ns.matrix.resolve(strict=True)
    out = ns.out.resolve()
    matrix = read(source / "config.json")
    bindings = matrix["bindings"]
    if matrix["top"] != "aes_cipher_top" or matrix["pdk"] != "sky130hd":
        raise ValueError("expected the original SKY130 AES matrix")
    control = {key: verify(item) for key, item in bindings["control"].items()}
    tools = {key: verify(item) for key, item in bindings["tools"].items()}
    flow = {key: verify(item) for key, item in bindings["flow"].items()}
    libraries = {corner: [verify(item) for item in items] for corner, items in bindings["used_libraries"].items()}
    verify(bindings["original_sdc"])
    orig_control = source / "control/receipt.json"
    edits = source / "screened_pool_used.json"
    pool = [comparison.PhysicalAction(**row) for row in read(edits)]
    prior = {label: source / f"screened/fixed/{label}.json" for label in CASES}
    case_actions = {label: tuple(read(path)["actions"]) for label, path in prior.items()}
    old_physical = {label: Path(read(path)["physical_receipt"]) for label, path in prior.items()}
    old_layout = {label: path.with_name("layout_changes.json") for label, path in old_physical.items()}
    touched = {label: set(read(path)["touched_nets"]) for label, path in old_layout.items()}
    touched["zero"] = set()
    baseline_text = control["def"].read_text(encoding="utf-8")
    header = "\n".join(re.findall(r"(?m)^(?:VERSION|DIVIDERCHAR|BUSBITCHARS|DESIGN|UNITS) .+?;$", baseline_text))
    if len(header.splitlines()) != 5:
        raise ValueError("unexpected frozen DEF header")
    baseline_nets = comparison.def_section(control["def"], "NETS")
    case_order = ns.case or ["zero", *CASES]
    omitted = set(map(comparison.canonical_odb_name, ns.omit_instance))
    donor_inputs = []
    released = set(ns.release_neighbor)
    if ns.qualifying_union:
        if (len(case_order) != 1 or case_order[0] == "zero" or omitted or ns.add_singleton_slot or released
                or ns.mode != "fixed-untouched"):
            raise ValueError("qualifying union is a single nonzero, all-untouched-fixed case")
        selected = case_order[0]
        case_actions[selected], touched[selected], released, donor_inputs = qualified_union(
            ns.qualifying_union, source / "config.json", control["v"],
        )
        instances = {action.action_id: comparison.canonical_odb_name(action.instance) for action in pool}
        if len({instances[key] for key in case_actions[selected]}) != len(case_actions[selected]):
            raise ValueError("union contains overlapping same-instance edits")
    if omitted or ns.add_singleton_slot is not None:
        if len(case_order) != 1 or case_order[0] == "zero":
            raise ValueError("edit the original batch of one nonzero case")
        selected = case_order[0]
        identities = {
            action.action_id: comparison.canonical_odb_name(action.instance)
            for action in pool
        }
        if not omitted < {identities[key] for key in case_actions[selected]}:
            raise ValueError("omissions must leave at least one edit in the original batch")
        case_actions[selected] = tuple(key for key in case_actions[selected] if identities[key] not in omitted)
        if ns.add_singleton_slot is not None:
            if not re.fullmatch(r"\d{2}", ns.add_singleton_slot):
                raise ValueError("donor slot must have a two-digit matrix identifier")
            raw_donor = source / f"screened/fixed/{ns.add_singleton_slot}.json"
            donor = read(raw_donor)
            donor_action, = donor["actions"]
            if identities[donor_action] in {identities[key] for key in case_actions[selected]}:
                raise ValueError("donor singleton must change a different instance")
            donor_layout = Path(donor["physical_receipt"]).with_name("layout_changes.json")
            donor_inputs.extend((raw_donor, Path(donor["physical_receipt"]), donor_layout))
            case_actions[selected] += (donor_action,)
            touched[selected].update(read(donor_layout)["touched_nets"])
        remaining = {identities[key] for key in case_actions[selected]}
        incident = {
            net for net, entry in baseline_nets.items()
            if remaining.intersection(re.findall(r"\( (\S+) \S+ \)", entry.partition(" + ")[0]))
        }
        if not incident or not incident <= touched[selected]:
            raise ValueError("edit incidence disagrees with the audited matrix trials")
        touched[selected] = incident
    if released:
        if len(case_order) != 1 or case_order[0] == "zero":
            raise ValueError("run one nonzero case to test a specific neighbor relaxation")
        for net in released:
            if net not in baseline_nets or "+ USE SIGNAL" not in baseline_nets[net]:
                raise ValueError(f"released neighbor must be a CONTROL data net: {net}")
        touched[case_order[0]].update(released)
    args = SimpleNamespace(
        pdk="sky130hd", out=out, threads=matrix["methods_route_threads"],
        clock_period_ps=matrix["original_clock_period_ps"], openroad=tools["openroad"], sta=tools["opensta"],
        sec=tools["sec"], orfs=flow["setRC.tcl"].parents[2], route_mode=matrix["route_mode"],
        droute_iters=matrix["route_drt_iters"], embedded_guides=True, route_guide=None, zero_reextract=False,
        route_timeout=ns.route_timeout, sta_timeout=matrix["sta_timeout_seconds_per_view"],
        sec_timeout=matrix["sec_timeout_seconds"], report_setup_endpoints=matrix["report_setup_endpoints"],
    )
    target = matrix["primary_target_area_pct"]
    out.mkdir(parents=True)
    comparison.save(out / "inputs.json", {
        "matrix_config": comparison.bind(source / "config.json"),
        "reference_view_receipt": comparison.bind(orig_control), "used_pool": comparison.bind(edits),
        "prior_trials": {str(path): comparison.bind(path)
                         for path in (*prior.values(), *old_physical.values(), *old_layout.values(), *donor_inputs)},
        "driver": comparison.bind(Path(__file__).resolve()), "mode": ns.mode,
        "threads": args.threads, "affinity": sorted(os.sched_getaffinity(0)),
        "stage_timeouts_seconds": {"route_drc_rcx": args.route_timeout, "sta_per_view": args.sta_timeout,
                                  "sec": args.sec_timeout},
        "case_order": case_order, "actions": case_actions, "omitted_instances": sorted(omitted),
        "donor_singleton_slot": ns.add_singleton_slot,
        "qualifying_union": [str(path) for path in ns.qualifying_union] if ns.qualifying_union else None,
        "released_neighbors": sorted(released),
        "target_area_pct": target, "candidate_sec": "deferred until status-normalized full DRC",
    })
    results = {}
    with bind_runtime(matrix["top"], flow["fastroute.tcl"]), selective_route(
        ns.mode, touched, released, (header, baseline_nets),
    ):
        evaluator = comparison.Evaluator(
            args, control, libraries, comparison.logical_masters(control["v"], comparison.liberty_areas(libraries["TT"])),
            read(orig_control)["views"], pool, f"{matrix['scope']}:{ns.mode}",
        )
        gate = sweep.budget_gate(evaluator, matrix["primary_budget_pct"], False)
        for label in case_order:
            directory = out / label
            print(f"AES {ns.mode} {label} starting", flush=True)
            _, receipt = evaluator.evaluate(case_actions.get(label, ()), directory, noop=(label == "zero"),
                                            envelope_only=(label != "zero"))
            failures = list(receipt["failures"])
            if receipt.get("artifacts"):
                failures.extend(audit_routing(directory, baseline_nets))
            failures.extend(audit_timing(evaluator, receipt, gate, label == "zero"))
            area_pct = 100.0 * receipt.get("area_saved", 0.0) / evaluator.ref_area
            if label != "zero" and area_pct < target:
                failures.append("area_target")
            results[label] = {
                "receipt": comparison.bind(directory / "receipt.json"),
                "area_recovered_pct": area_pct, "failures": failures,
                "sec_deferred": label != "zero",
                "sec_pass": label == "zero" and not failures and receipt["endpoint"]["sec_pass"],
            }
            comparison.save(out / "results.json", results)
            print(f"AES {ns.mode} {label} completed {failures}", flush=True)
    return 0 if "zero" not in results or results["zero"]["sec_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
