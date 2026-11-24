#!/usr/bin/env python3
"""Run matched post-route Ibex recovery policies against one immutable CONTROL."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code/src"))
from rseco.budgeted_recovery import BudgetPolicy, Endpoint, assess
from rseco.logic_rewrite import parse_generic_liberty_catalog
from rseco.physical_budget_adapter import (
    PhysicalAction,
    adaptive_batch_recovery,
    generate_compatible_candidates,
)


TOP = "ibex_core"
CORNERS = ("FF", "TT", "SS")
METHODS = ("single", "fixed", "faeco")
POLICY = BudgetPolicy.from_ps(10.0)
PS_TOLERANCE = POLICY.tolerance_ns * 1000.0
CONTROL_FILES = ("odb", "def", "v", "sdc", "spef")
ORFS = Path("/home/toylog/faeco_eda/orfs/flow")
OPENROAD = Path("/home/toylog/rseco_timing/vendor/OpenROAD-b511b6a/bazel-bin/openroad")
OPENROAD_SHA = "2d9662715130538b50e93b614c33099a5e183eef0cc31b642099daea8d203e19"
STA = Path("/usr/local/bin/sta")
NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
ERROR = re.compile(r"(?im)^\s*(?:Error:|Error .*\.tcl|\[ERROR\b)")


class TrialFailure(RuntimeError):
    """An attempted operation failed and its raw log is retained."""


@dataclass(frozen=True)
class ProcessResult:
    returncode: int | None
    wall_seconds: float
    timeout_seconds: float
    log: str


def sha(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def bind(path: Path) -> dict:
    return {"path": str(path.resolve()), "sha256": sha(path), "bytes": path.stat().st_size}


def save(path: Path, value: object) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(path)


def tcl(value: str | Path) -> str:
    """Quote a single Tcl word, including escaped, hierarchical instance names."""
    escaped = re.sub(r'([\\$\[\]"])', r"\\\1", str(value))
    return '"' + escaped.replace("\r", "\\r").replace("\n", "\\n") + '"'


def run_process(argv, logfile: Path, timeout: float, *, env=None) -> ProcessResult:
    start = time.monotonic()
    with logfile.open("wb") as log:
        proc = subprocess.Popen(
            argv, stdout=log, stderr=subprocess.STDOUT, cwd=logfile.parent,
            env=env, start_new_session=True,
        )
        try:
            returncode = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            returncode = None
    return ProcessResult(returncode, time.monotonic() - start, timeout, str(logfile))


def checked_output(result: ProcessResult, completion: str | None = None) -> str:
    output = Path(result.log).read_text(encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise TrialFailure(f"command rc={result.returncode}, log={result.log}")
    if ERROR.search(output):
        raise TrialFailure(f"tool reported an error, log={result.log}")
    if completion is not None and completion not in output.splitlines():
        raise TrialFailure(f"missing completion marker, log={result.log}")
    return output


def load_views(qualification: dict) -> dict[str, list[Path]]:
    result = {}
    for corner in CORNERS:
        paths = qualification.get("library_paths", {}).get(corner)
        if paths is None:
            paths = qualification["views"][corner].get("library_paths")
        if not isinstance(paths, list) or not paths:
            raise ValueError(f"missing library_paths for {corner}")
        result[corner] = [Path(path).resolve() for path in paths]
    return result


def qualify_binding(qualification: dict, assets: dict) -> None:
    if qualification.get("status") != "hold_qualified" or not qualification.get("all_views_nonnegative_hold"):
        raise TrialFailure("P0 receipt does not certify nonnegative hold in all views")
    if qualification.get("detailed_route_drc_count") != 0:
        raise TrialFailure("P0 receipt does not certify DRC 0")
    if qualification.get("source_sdc_semantics", {}).get("source_io_matches_all_nonclock_inputs_and_outputs") is not True:
        raise TrialFailure("P0 receipt does not certify original IO coverage")
    for ext, artifact in assets["control"].items():
        if qualification["control_output_paths"][ext]["sha256"] != artifact["sha256"]:
            raise TrialFailure(f"CONTROL {ext} hash disagrees with P0 receipt")
    source_hash = qualification.get("source_sdc", {}).get("sha256")
    if source_hash is None:
        original = assets["original_sdc"]
        source_hash = qualification.get("producer", {}).get("sha256_pre", {}).get(original["path"])
    if source_hash != assets["original_sdc"]["sha256"]:
        raise TrialFailure("source SDC hash disagrees with P0 receipt")
    for corner, entries in assets["source_libraries"].items():
        qualified = qualification["view_liberty_groups"][corner]
        if [item["sha256"] for item in entries] != [item["sha256"] for item in qualified]:
            raise TrialFailure(f"{corner} libraries disagree with P0 receipt")
    if assets["tools"]["opensta"]["sha256"] != qualification["sta_binary"]["sha256"]:
        raise TrialFailure("OpenSTA binary disagrees with P0 receipt")
    if assets["tools"]["openroad"]["sha256"] != OPENROAD_SHA:
        raise TrialFailure("OpenROAD binary disagrees with the pinned P0 producer")
    if not any(item["sha256"] == assets["control_drc"]["sha256"] and item["path"] == assets["control_drc"]["path"]
               for item in qualification["raw_reports"]):
        raise TrialFailure("CONTROL DRC report is absent from P0 receipt")


def materialize_views(paths, out: Path) -> dict[str, list[Path]]:
    out.mkdir()
    result = {}
    for corner, libraries in paths.items():
        staged = out / corner
        staged.mkdir()
        result[corner] = []
        for source in libraries:
            if source.suffix == ".gz":
                dest = staged / source.stem
                with gzip.open(source, "rb") as reader, dest.open("xb") as writer:
                    shutil.copyfileobj(reader, writer)
            else:
                dest = source.resolve()
            result[corner].append(dest)
    return result


def render_sta(libraries, netlist: Path, sdc: Path, spef: Path, *, report_setup_endpoints=False) -> str:
    reads = "\n".join(f"read_liberty {tcl(path)}" for path in libraries)
    setup_inventory = """
puts IBEX_SETUP_NEG_BEGIN
set paths [find_timing_paths -path_delay max -slack_max 0 -group_path_count 100000 -endpoint_path_count 1]
if {[llength $paths] >= 100000} { error "setup endpoint inventory hit the path report cap" }
foreach path $paths {
    if {[get_property $path slack] < 0} {
        puts "IBEX_SETUP_NEG [get_full_name [get_property $path endpoint]]"
    }
}
puts IBEX_SETUP_NEG_END
""" if report_setup_endpoints else ""
    return f"""{reads}
read_verilog {tcl(netlist)}
link_design {TOP}
read_sdc {tcl(sdc)}
if {{[llength [all_clocks]] == 0}} {{ error "No clocks in saved SDC" }}
read_spef {tcl(spef)}
puts "IBEX_SETUP_PS [expr {{1e12 * [sta::worst_slack_cmd max]}}]"
puts "IBEX_HOLD_PS [expr {{1e12 * [sta::worst_slack_cmd min]}}]"
puts "IBEX_TNS_PS [expr {{1e12 * [sta::total_negative_slack_cmd max]}}]"
puts "IBEX_HOLD_TNS_PS [expr {{1e12 * [sta::total_negative_slack_cmd min]}}]"
puts IBEX_MAX_SLEW_START
report_check_types -max_slew -violators -digits 9
puts IBEX_MAX_SLEW_END
puts IBEX_MAX_CAPACITANCE_START
report_check_types -max_capacitance -violators -digits 9
puts IBEX_MAX_CAPACITANCE_END
foreach port [all_inputs -no_clocks] {{ puts "IBEX_INPUT [get_name $port]" }}
foreach port [all_outputs] {{ puts "IBEX_OUTPUT [get_name $port]" }}
check_setup -verbose
report_parasitic_annotation
report_checks -path_delay max -group_path_count 1
report_checks -path_delay min -group_path_count 1
{setup_inventory}
puts IBEX_STA_COMPLETE
exit
"""


def violations(output: str, kind: str) -> dict[str, float]:
    match = re.search(rf"(?ms)^IBEX_{kind}_START\n(.*?)^IBEX_{kind}_END$", output)
    if not match:
        raise TrialFailure(f"missing electrical report {kind}")
    results = {}
    for line in match[1].splitlines():
        if "(VIOLATED)" not in line:
            continue
        item = re.fullmatch(rf"\s*(\S.*?)\s+{NUMBER}\s+{NUMBER}\s+({NUMBER})\s+\(VIOLATED\)\s*", line)
        if item is None:
            raise TrialFailure(f"unreadable {kind} violation row {line!r}")
        name = " ".join(item[1].split())
        if name in results:
            raise TrialFailure(f"ambiguous {kind} violation {name}")
        results[name] = float(item[2])
    return results


def parse_sta(output: str) -> dict:
    metrics = {}
    for label, key in (
        ("SETUP", "setup_wns_ps"), ("HOLD", "hold_wns_ps"),
        ("TNS", "setup_tns_ps"), ("HOLD_TNS", "hold_tns_ps"),
    ):
        found = re.findall(rf"(?m)^IBEX_{label}_PS\s+({NUMBER})\s*$", output)
        if len(found) != 1 or not math.isfinite(float(found[0])) or abs(float(found[0])) > 1e9:
            raise TrialFailure(f"invalid {key} marker")
        metrics[key] = float(found[0])
    if re.search(r"(?i)black.?box|not found", output):
        raise TrialFailure("unresolved STA object")
    metrics["electrical"] = {kind: violations(output, kind) for kind in ("MAX_SLEW", "MAX_CAPACITANCE")}
    metrics["ports"] = {
        side: sorted(re.findall(rf"(?m)^IBEX_{side} (\S+)$", output)) for side in ("INPUT", "OUTPUT")
    }
    if not all(metrics["ports"].values()):
        raise TrialFailure("missing actual I/O port evidence")
    if "IBEX_SETUP_NEG_BEGIN" in output:
        inventory = re.search(r"(?ms)^IBEX_SETUP_NEG_BEGIN\n(.*?)^IBEX_SETUP_NEG_END$", output)
        if not inventory:
            raise TrialFailure("incomplete setup violation endpoint inventory")
        endpoints = re.findall(r"(?m)^IBEX_SETUP_NEG (.+)$", inventory[1])
        metrics["setup_negative_endpoints"] = sorted(set(endpoints))
    return metrics


def describe_sta(args, libraries, netlist, sdc, spef, out, operations) -> dict:
    views = {}
    for corner in CORNERS:
        script = out / f"sta_{corner}.tcl"
        script.write_text(render_sta(
            libraries[corner], netlist, sdc, spef, report_setup_endpoints=args.report_setup_endpoints,
        ), encoding="utf-8")
        result = run_process([args.sta, "-exit", script], out / f"sta_{corner}.log", args.sta_timeout)
        operations[f"STA_{corner}"] = asdict(result)
        views[corner] = parse_sta(checked_output(result, "IBEX_STA_COMPLETE"))
        if args.report_setup_endpoints and "setup_negative_endpoints" not in views[corner]:
            raise TrialFailure("missing setup violation endpoint inventory")
    return views


def joint_failures(control: dict, candidate: dict, *, check_setup: bool = True) -> list[str]:
    reasons = []
    for corner in CORNERS:
        ref, trial = control[corner], candidate[corner]
        if check_setup and trial["setup_wns_ps"] < ref["setup_wns_ps"] - 10.0 - PS_TOLERANCE:
            reasons.append(f"{corner}:setup_budget")
        if trial["hold_wns_ps"] < 0:
            reasons.append(f"{corner}:negative_hold")
        if trial["hold_wns_ps"] < ref["hold_wns_ps"] - PS_TOLERANCE:
            reasons.append(f"{corner}:hold_regression")
        if "ports" in ref and trial["ports"] != ref["ports"]:
            reasons.append(f"{corner}:port_identity")
        for kind, ref_violations in ref.get("electrical", {}).items():
            if trial["electrical"][kind].keys() - ref_violations.keys():
                reasons.append(f"{corner}:new_{kind.lower()}_violations")
    return reasons


def read_db(libraries, odb: Path) -> str:
    return "\n".join([*(f"read_liberty {tcl(lib)}" for lib in libraries), f"read_db {tcl(odb)}"])


def render_inventory(libraries, odb: Path) -> str:
    return read_db(libraries, odb) + """
foreach lib [[ord::get_db] getLibs] {
    foreach master [$lib getMasters] {
        set site [$master getSite]
        set site_name [expr {$site eq "NULL" ? "" : [$site getName]}]
        set pins {}
        foreach pin [$master getMTerms] {
            lappend pins "[$pin getName]:[$pin getIoType]:[$pin getSigType]"
        }
        puts "MASTER\t[$master getName]\t[$master getType]\t[$master getHeight]\t$site_name\t[join [lsort $pins] ,]\t[$master getWidth]"
    }
}
foreach inst [[ord::get_db_block] getInsts] {
    set clock 0
    foreach pin [$inst getITerms] {
        set net [$pin getNet]
        if {$net ne "NULL" && [$net getSigType] eq "CLOCK"} { set clock 1 }
    }
    puts "INSTANCE\t[$inst getName]\t[[$inst getMaster] getName]\t[$inst getPlacementStatus]\t$clock\t[$inst isDoNotTouch]"
}
puts IBEX_INVENTORY_COMPLETE
exit
"""


def parse_inventory(text: str) -> tuple[dict, dict]:
    masters, instances = {}, {}
    for line in text.splitlines():
        columns = line.split("\t")
        if columns[0] not in ("MASTER", "INSTANCE"):
            continue
        records = masters if columns[0] == "MASTER" else instances
        name, *row = columns[1:]
        if len(row) != (5 if columns[0] == "MASTER" else 4):
            raise TrialFailure(f"malformed {columns[0]} record {line!r}")
        if name in records and row != records[name]:
            raise TrialFailure(f"ambiguous database name {name}")
        records[name] = row
    if not masters or not instances:
        raise TrialFailure("empty master or instance inventory")
    return masters, instances


def liberty_areas(paths) -> dict[str, float]:
    result = {}
    for path in paths:
        _, areas, _ = parse_generic_liberty_catalog(path.read_text(encoding="utf-8"))
        result.update(areas)
    return result


def logical_masters(path: Path, areas: dict) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    ident = r"(?:\\\S+|[A-Za-z_$][\w$]*)"
    modules = {
        name.removeprefix("\\"): body
        for name, body in re.findall(rf"(?ms)^module\s+({ident})\s+(.*?)^endmodule\b", content)
    }
    known = {}

    def visit(module: str, prefix: str, parent_modules: set[str]) -> None:
        if module in parent_modules:
            raise TrialFailure(f"recursive exported hierarchy at {prefix}")
        for master, instance in re.findall(rf"(?m)^[ \t]*({ident})\s+({ident})\s*\(", modules[module]):
            master = master.removeprefix("\\")
            name = prefix + instance.removeprefix("\\")
            if master in modules:
                visit(master, name + "/", parent_modules | {module})
            elif master in areas:
                if name in known:
                    raise TrialFailure(f"ambiguous exported instance {name}")
                known[name] = master

    if TOP not in modules:
        raise TrialFailure(f"missing exported design top module {TOP}")
    visit(TOP, "", set())
    if not known:
        raise TrialFailure("no timed library masters in exported netlist")
    return known


def canonical_odb_name(name: str) -> str:
    return re.sub(r"\\(.)", r"\1", name)


def align_db_instances(ref_masters: dict, instances: dict) -> tuple[dict, list[str]]:
    canonical = {}
    for name, row in instances.items():
        normalized = canonical_odb_name(name)
        if normalized in canonical:
            raise TrialFailure(f"ambiguous canonical ODB path {normalized}")
        canonical[normalized] = (name, row)
    mismatches = [
        name for name, master in ref_masters.items() if name not in canonical or canonical[name][1][0] != master
    ]
    return canonical, mismatches


def select_pool(index, libraries, masters, instances) -> list[PhysicalAction]:
    in_all_views = set.intersection(*(set(liberty_areas(libraries[corner])) for corner in CORNERS))
    selected = {}
    for action in generate_compatible_candidates(
        index, libraries["TT"], one_per_instance=False, deprioritize_zero_drive=True,
    ):
        name = action.instance.removeprefix("\\")
        source = masters.get(action.source_cell)
        target = masters.get(action.target_cell)
        if source is None or target is None or source[:4] != target[:4] or not source[2]:
            continue
        if int(target[4]) >= int(source[4]):
            continue
        if not {action.source_cell, action.target_cell} <= in_all_views:
            continue
        raw_name, instance = instances[name]
        if instance[0] != action.source_cell:
            continue
        if instance[1:] != ["PLACED", "0", "0"] or name.startswith("clkload"):
            continue
        selected.setdefault(name, replace(action, instance=raw_name))
    return list(selected.values())


def run_method(
    method: str, reference: Endpoint, actions: list[PhysicalAction],
    evaluate: Callable[[tuple[str, ...]], Endpoint], budget: int, batch_size: int, *, policy: BudgetPolicy = POLICY,
    defer_split_for: Callable[[tuple[str, ...]], bool] | None = None,
) -> dict:
    if method == "faeco":
        return adaptive_batch_recovery(
            reference, actions, evaluate, policy, max_evaluations=budget, batch_size=batch_size,
            defer_split_for=defer_split_for,
        )
    if method not in ("single", "fixed"):
        raise ValueError(f"unknown method {method}")
    size = 1 if method == "single" else batch_size
    idx, trace, committed, best = 0, [], [], reference
    while idx < len(actions) and len(trace) < budget:
        chunk_size = size if budget - len(trace) >= 2 else 1
        chunk = actions[idx:idx + chunk_size]
        idx += len(chunk)
        chunk_ids = [action.action_id for action in chunk]
        trial = tuple(sorted((*committed, *chunk_ids)))
        ep = evaluate(trial)
        gate = assess(reference, ep, policy)
        accepted = gate.feasible and ep.area < best.area - 1e-9
        trace.append({
            "actions": list(trial), "batch_len": len(chunk), "feasible": gate.feasible,
            "accepted": accepted, "area": ep.area, "wns_ns": ep.wns_ns,
            "hold_wns_ns": ep.hold_wns_ns,
        })
        if accepted:
            committed.extend(chunk_ids)
            best = ep
    return {"selected": best, "committed": committed, "evaluations_used": len(trace), "trace": trace}


def render_route(args, libraries, control, out: Path, actions: list[PhysicalAction]) -> str:
    platform = args.orfs / f"platforms/{args.pdk}"
    signal, clock, top = {
        "sky130hd": ("met1", "met3", "met5"),
        "asap7": ("M2", "M4", "M7"),
    }[args.pdk]
    edits = []
    for action in actions:
        name = tcl(action.instance)
        edits.append(f"""
set inst [[ord::get_db_block] findInst {name}]
if {{$inst eq "NULL" || [[$inst getMaster] getName] ne {tcl(action.source_cell)}}} {{
    error "source instance/master mismatch"
}}
set target [[ord::get_db] findMaster {tcl(action.target_cell)}]
if {{$target eq "NULL" || ![$inst swapMaster $target]}} {{
    error "could not swap the OpenDB master"
}}
set inst [[ord::get_db_block] findInst {name}]
if {{$inst eq "NULL" || [[$inst getMaster] getName] ne {tcl(action.target_cell)}}} {{
    error "target instance/master mismatch"
}}
""")
    replacements = "".join(edits)
    names = " ".join(tcl(action.instance) for action in actions)
    net_source = (
        f"""
set nets [dict create]
foreach name [list {names}] {{
    set inst [[ord::get_db_block] findInst $name]
    foreach pin [$inst getITerms] {{
        set net [$pin getNet]
        if {{$net ne "NULL" && [$net getSigType] ni {{POWER GROUND}}}} {{
            dict set nets [$net getName] $net
        }}
    }}
}}
"""
        if args.route_mode == "local"
        else """
set nets [dict create]
foreach net [[ord::get_db_block] getNets] {
    dict set nets [$net getName] $net
}
"""
    )
    source_grt = fastroute(args)
    if args.embedded_guides:
        grt = 'if {![grt::have_routes]} {error "No embedded route guides"}'
    elif args.route_mode == "local" and args.route_guide:
        grt = f"read_guides {tcl(args.route_guide)}"
    else:
        grt = "global_route" + (" -resistance_aware" if args.pdk == "asap7" else "")
    if args.zero_reextract and not actions:
        routing = f"""if {{![design_is_routed]}} {{ error "Frozen CONTROL contains unrouted nets" }}
file copy -- {tcl(args.control_drc)} {tcl(out / "drc.rpt")}
puts "IBEX_DRT_VIOLATIONS 0"
puts IBEX_REUSED_FROZEN_DRT"""
    else:
        routing = f"""pin_access
{grt}
detailed_route -output_drc {tcl(out / "drc.rpt")} -verbose 1 -droute_end_iter {args.droute_iters}
puts "IBEX_DRT_VIOLATIONS [detailed_route_num_drvs]"
if {{![design_is_routed]}} {{ error "Unrouted nets after DRT" }}
check_placement -verbose
puts IBEX_DRT_COMPLETE"""
    return f"""{read_db(libraries, control["odb"])}
read_sdc {tcl(control["sdc"])}
if {{[llength [all_clocks]] == 0}} {{ error "No clocks in saved SDC" }}
source {tcl(platform / "setRC.tcl")}
set env(MIN_ROUTING_LAYER) {signal}
set env(MIN_CLK_ROUTING_LAYER) {clock}
set env(MAX_ROUTING_LAYER) {top}
set env(ROUTING_LAYER_ADJUSTMENT) 0.25
source {tcl(source_grt)}
{replacements}
check_placement -verbose
{net_source}
set cleared 0
dict for {{name net}} $nets {{
    if {{[$net getSigType] in {{POWER GROUND}}}} {{ continue }}
    puts "IBEX_TOUCHED_NET $name"
    set wire [$net getWire]
    if {{$wire ne "NULL"}} {{ odb::dbWire_destroy $wire; incr cleared }}
}}
puts "IBEX_CLEARED_SIGNAL_WIRES $cleared"
{routing}
set ::env(REPORTS_DIR) {tcl(out)}
source {tcl(args.orfs / "scripts/util.tcl")}
write_verilog {tcl(out / "routed.v")} -remove_cells [find_physical_only_masters]
write_def {tcl(out / "routed.def")}
write_db {tcl(out / "routed.odb")}
define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file {tcl(platform / "rcx_patterns.rules")}
write_spef {tcl(out / "routed.spef")}
puts IBEX_RCX_COMPLETE
puts IBEX_ROUTE_COMPLETE
exit
"""


def fastroute(args) -> Path:
    folder = "designs/sky130hd/ibex" if args.pdk == "sky130hd" else "platforms/asap7"
    return args.orfs / folder / "fastroute.tcl"


def def_section(path: Path, section: str) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"(?ms)^{section}\s+(\d+)\s*;\s*\n(.*?)^END {section}\b", text)
    if not match:
        raise TrialFailure(f"missing DEF {section} section in {path}")
    entries = re.findall(r"(?ms)^\s*-\s+(\S+)\s+(.*?)(?<!\\);\s*$", match[2])
    entries_by_name = {name: " ".join(value.split()) for name, value in entries}
    if len(entries_by_name) != int(match[1]):
        raise TrialFailure(f"DEF {section} entry count mismatch in {path}")
    return entries_by_name


def changed_geometry(control_def: Path, routed_def: Path, touched: set[str]) -> dict[str, list[str]]:
    control_nets, routed_nets = (def_section(path, "NETS") for path in (control_def, routed_def))
    changes = {name for name in control_nets.keys() | routed_nets.keys() if control_nets.get(name) != routed_nets.get(name)}
    control_inst, routed_inst = (def_section(path, "COMPONENTS") for path in (control_def, routed_def))
    # Exclude master name from comparison and require unchanged component placements and properties.
    components = {
        name for name in control_inst.keys() | routed_inst.keys()
        if control_inst.get(name, "").partition(" ")[2] != routed_inst.get(name, "").partition(" ")[2]
        or name not in control_inst or name not in routed_inst
    }
    return {
        "touched_nets": sorted(touched), "changed_nets": sorted(changes),
        "changed_untouched_nets": sorted(changes - touched), "changed_component_placement": sorted(components),
    }


def endpoint(label: str, area: float, views: dict, scope: str, out: Path, valid: bool, proof: bool) -> Endpoint:
    tt = views["TT"]
    return Endpoint(
        label, area, tt["setup_wns_ps"] / 1000.0, tt["setup_tns_ps"] / 1000.0,
        tt["hold_wns_ps"] / 1000.0, scope, str(out), valid, proof,
    )


class Evaluator:
    def __init__(self, args, control, libraries, ref_masters, ref_views, pool, scope):
        self.args = args
        self.control = control
        self.libraries = libraries
        self.ref_masters = ref_masters
        self.ref_views = ref_views
        self.actions = {action.action_id: action for action in pool}
        self.scope = scope
        self.areas = liberty_areas(libraries["TT"])
        self.ref_area = math.fsum(self.areas[cell] for cell in ref_masters.values())

    def expected_masters(self, action_ids: tuple[str, ...]) -> tuple[dict, list[PhysicalAction]]:
        expected = self.ref_masters.copy()
        edits = [self.actions[aid] for aid in action_ids]
        for action in edits:
            instance = canonical_odb_name(action.instance)
            if expected[instance] != action.source_cell:
                raise TrialFailure(f"candidate edits overlap at {instance}")
            expected[instance] = action.target_cell
        return expected, edits

    def proof(self, candidate: Path, out: Path, operations: dict) -> bool:
        sec = self.args.sec.resolve()
        command = [sys.executable, sec] if sec.suffix == ".py" else [sec]
        env = os.environ.copy()
        env["FAECO_SEC_LIBRARIES"] = json.dumps([str(path) for path in self.libraries["TT"]])
        env["FAECO_SEC_PDK"] = self.args.pdk
        result = run_process(
            [*command, self.control["v"], candidate, out / "sec"],
            out / "sec.log", self.args.sec_timeout, env=env,
        )
        operations["SEC"] = asdict(result)
        return result.returncode == 0

    def evaluate(
        self, action_ids: tuple[str, ...], out: Path, *, noop: bool = False, envelope_only: bool = False,
    ) -> tuple[Endpoint, dict]:
        if noop and envelope_only:
            raise ValueError("the no-op must be verified under its preflight policy")
        out.mkdir()
        start = time.monotonic()
        label = str(out.relative_to(self.args.out))
        record = {
            "endpoint_id": label, "actions": list(action_ids), "operations": {},
            "failures": [], "views": {}, "control_sdc": bind(self.control["sdc"]),
        }
        operations, failures = record["operations"], record["failures"]
        ep = endpoint(label, self.ref_area, self.ref_views, self.scope, out, False, False)
        save(out / "receipt.json", record)
        try:
            expected, edits = self.expected_masters(action_ids)
            script = out / "route.tcl"
            script.write_text(render_route(self.args, self.libraries["TT"], self.control, out, edits), encoding="utf-8")
            route = run_process(
                [self.args.openroad, "-threads", str(self.args.threads), "-exit", script],
                out / "route.log", self.args.route_timeout,
            )
            operation = "RCX_REEXTRACT" if noop and self.args.zero_reextract else "DRT_RCX"
            operations[operation] = asdict(route)
            route_log = Path(route.log).read_text(encoding="utf-8", errors="replace").splitlines()
            record["routed_to_completion"] = "IBEX_DRT_COMPLETE" in route_log
            record["extracted_to_completion"] = "IBEX_RCX_COMPLETE" in route_log
            output = checked_output(route, "IBEX_ROUTE_COMPLETE")
            drc_mark = re.findall(r"(?m)^IBEX_DRT_VIOLATIONS (\d+)\s*$", output)
            report = out / "drc.rpt"
            if len(drc_mark) != 1 or not report.is_file():
                raise TrialFailure("missing DRT DRC evidence")
            record["drc_violations"] = int(drc_mark[0])
            if record["drc_violations"] or report.read_text(encoding="utf-8").strip():
                failures.append("drc")
            artifacts = {ext: out / f"routed.{ext}" for ext in ("odb", "def", "v", "spef")}
            if any(not path.is_file() or not path.stat().st_size for path in artifacts.values()):
                raise TrialFailure("missing post-route artifact")
            record["artifacts"] = {**{ext: bind(path) for ext, path in artifacts.items()}, "drc": bind(report)}
            touched = set(re.findall(r"(?m)^IBEX_TOUCHED_NET (.+)$", output))
            layout = changed_geometry(self.control["def"], artifacts["def"], touched)
            save(out / "layout_changes.json", layout)
            if layout["changed_component_placement"]:
                failures.append("component_placement_changed")
            if action_ids and not touched:
                failures.append("no_edited_signal_nets")
            actual = logical_masters(artifacts["v"], self.areas)
            if actual != expected:
                mismatch = sorted(name for name in actual.keys() | expected.keys() if actual.get(name) != expected.get(name))
                record["instance_mismatches"] = {
                    name: {"expected": expected.get(name), "actual": actual.get(name)} for name in mismatch
                }
                failures.append("netlist_master_identity")
            area = math.fsum(self.areas[cell] for cell in actual.values())
            record["area_saved"] = self.ref_area - area
            if not noop and self.ref_area - area <= 1e-9:
                failures.append("no_area_gain")
            views = describe_sta(
                self.args, self.libraries, artifacts["v"], self.control["sdc"], artifacts["spef"],
                out, operations,
            )
            record["views"] = views
            if self.args.report_setup_endpoints:
                record["setup_endpoint_counts"] = {}
                for corner, view in views.items():
                    baseline = set(self.ref_views[corner]["setup_negative_endpoints"])
                    trial_endpoints = set(view["setup_negative_endpoints"])
                    record["setup_endpoint_counts"][corner] = {
                        "control_negative": len(baseline),
                        "candidate_negative": len(trial_endpoints),
                        "new_negative": len(trial_endpoints - baseline),
                    }
            if bind(self.control["sdc"]) != record["control_sdc"]:
                failures.append("changed_sdc")
            failures.extend(joint_failures(self.ref_views, views, check_setup=not envelope_only))
            proven = False
            if not failures and not envelope_only:
                proven = self.proof(artifacts["v"], out, operations)
                if not proven:
                    failures.append("sec")
            ep = endpoint(label, area, views, self.scope, out, not failures, proven)
        except (TrialFailure, OSError, ValueError) as error:
            failures.append(str(error))
        record["endpoint"] = asdict(ep)
        record["wall_seconds"] = time.monotonic() - start
        save(out / "receipt.json", record)
        return ep, record


def accepted_prefix(reference: Endpoint, result: dict, receipts: list[dict], common_limit: float) -> dict:
    selected = asdict(reference)
    elapsed = 0.0
    completed = 0
    for trace, receipt in zip(result["trace"], receipts, strict=True):
        elapsed += receipt["wall_seconds"]
        if elapsed > common_limit:
            break
        completed += 1
        if trace["accepted"]:
            selected = receipt["endpoint"]
    return {"completed_attempts": completed, "selected": selected, "area_saved": reference.area - selected["area"]}


def run_arm(args, evaluator: Evaluator, reference: Endpoint, pool, method: str) -> tuple[dict, list[dict]]:
    out = args.out / method
    out.mkdir()
    receipts = []

    def evaluate(action_ids: tuple[str, ...]) -> Endpoint:
        trial = out / f"{len(receipts) + 1:02d}"
        print(f"{method} attempt {len(receipts) + 1}/{args.max_evals} cumulative edits={len(action_ids)}", flush=True)
        ep, receipt = evaluator.evaluate(action_ids, trial)
        receipts.append(receipt)
        print(f"{method} {trial.name} {receipt['failures'] or 'passed gates'}", flush=True)
        return ep

    result = run_method(method, reference, pool, evaluate, args.max_evals, args.batch_size)
    result["selected"] = asdict(result["selected"])
    result["attempt_wall_seconds"] = sum(receipt["wall_seconds"] for receipt in receipts)
    result["route_attempts"] = sum("DRT_RCX" in receipt["operations"] for receipt in receipts)
    result["drt_completions"] = sum(receipt.get("routed_to_completion", False) for receipt in receipts)
    result["rcx_completions"] = sum(receipt.get("extracted_to_completion", False) for receipt in receipts)
    result["view_sta_attempts"] = sum(
        sum(f"STA_{corner}" in receipt["operations"] for corner in CORNERS) for receipt in receipts
    )
    result["sec_attempts"] = sum("SEC" in receipt["operations"] for receipt in receipts)
    result["area_saved"] = reference.area - result["selected"]["area"]
    result["attempts"] = [receipt["endpoint_id"] for receipt in receipts]
    save(out / "summary.json", result)
    return result, receipts


def run(args, *, matched_runner=None, config_overrides=None, extra_sources=()) -> int:
    control = {ext: args.control_dir / f"6_final.{ext}" for ext in CONTROL_FILES}
    assets = {
        "control": {ext: bind(path) for ext, path in control.items()},
        "original_sdc": bind(args.original_sdc), "control_drc": bind(args.control_drc),
    }
    if any(not item["bytes"] for item in assets["control"].values()):
        raise ValueError("one or more empty CONTROL artifacts")
    if args.control_drc.read_text(encoding="utf-8").strip():
        raise ValueError("CONTROL DRC report contains violations")
    if "set_propagated_clock" not in control["sdc"].read_text(encoding="utf-8"):
        raise ValueError("saved post-route SDC missing clock propagation")
    qualification = json.loads(args.views_json.read_text(encoding="utf-8"))
    assets["qualification_receipt"] = bind(args.views_json)
    src_views = load_views(qualification)
    assets["source_libraries"] = {corner: [bind(path) for path in libs] for corner, libs in src_views.items()}
    platform = args.orfs / f"platforms/{args.pdk}"
    assets["flow"] = {file.name: bind(file) for file in (
        platform / "setRC.tcl", fastroute(args), platform / "rcx_patterns.rules", args.orfs / "scripts/util.tcl",
    )}
    if args.route_guide is not None:
        assets["route_guide"] = bind(args.route_guide)
    assets["tools"] = {"openroad": bind(args.openroad), "opensta": bind(args.sta), "sec": bind(args.sec)}
    assets["driver_source"] = {
        path.name: bind(path)
        for path in (
            Path(__file__), ROOT / "code/src/rseco/budgeted_recovery.py",
            ROOT / "code/src/rseco/logic_rewrite.py", ROOT / "code/src/rseco/physical_budget_adapter.py",
            *extra_sources,
        )
    }
    qualify_binding(qualification, assets)
    args.out.mkdir(parents=True)
    staged_views = materialize_views(src_views, args.out / "libraries")
    assets["used_libraries"] = {corner: [bind(path) for path in libs] for corner, libs in staged_views.items()}
    scope = hashlib.sha256(json.dumps(assets, sort_keys=True).encode()).hexdigest()
    config = {
        "pdk": args.pdk, "top": TOP, "scope": scope, "bindings": assets,
        "methods_in_run_order": METHODS, "budget_attempts_per_arm": args.max_evals,
        "batch_size": args.batch_size, "methods_route_threads": args.threads,
        "route_mode": args.route_mode, "route_drt_iters": args.droute_iters,
        "route_guide_source": "embedded in frozen CONTROL ODB" if args.embedded_guides else "external",
        "route_timeout_seconds": args.route_timeout, "sta_timeout_seconds_per_view": args.sta_timeout,
        "sec_timeout_seconds": args.sec_timeout, "same_area_acceptance": False,
        "setup_budget_ps_per_view": 10.0, "numerical_tolerance_ps": PS_TOLERANCE,
        "hold_threshold_ps": 0.0, "hold_nonregression_per_view": True, "tns_gate": False,
        "report_setup_endpoints": args.report_setup_endpoints,
        "physical_area": "TT Liberty cell area sum of final routed functional netlist",
        "no_op_budget": ("one shared RCX re-extraction of frozen DRT" if args.zero_reextract else
                         "one shared preflight DRT/RCX, excluded from equal per-arm budget"),
        "no_op_preflight_setup_budget_ps": 10.0,
        "cached_physical_trials": False, "final_budget_slot": "singleton across all methods",
        "unrelated_route_changes": "report from routed DEF; common timing and electrical gates remain applicable",
    }
    if config_overrides:
        config.update(config_overrides)
    save(args.out / "config.json", config)
    baseline = args.out / "control"
    baseline.mkdir()
    reference_operations = {}
    baseline_record = {"operations": reference_operations}
    try:
        reference_views = describe_sta(args, staged_views, control["v"], control["sdc"], control["spef"],
                                       baseline, reference_operations)
        baseline_record["views"] = reference_views
        if any(reference_views[corner]["hold_wns_ps"] < 0.0 for corner in CORNERS):
            raise TrialFailure("original final CONTROL has negative hold")
        for corner, measured in reference_views.items():
            qualified = qualification["views"][corner]
            for metric in ("setup_wns_ps", "hold_wns_ps", "setup_tns_ps", "hold_tns_ps"):
                if abs(measured[metric] - qualified[metric]) > PS_TOLERANCE:
                    raise TrialFailure(f"{corner} live {metric} differs from pinned P0 receipt")
        inventory = baseline / "inventory.tcl"
        inventory.write_text(render_inventory(staged_views["TT"], control["odb"]), encoding="utf-8")
        result = run_process(
            [args.openroad, "-threads", str(args.threads), "-exit", inventory],
            baseline / "inventory.log", args.sta_timeout,
        )
        reference_operations["ODB_INVENTORY"] = asdict(result)
        masters, instances = parse_inventory(checked_output(result, "IBEX_INVENTORY_COMPLETE"))
        ref_masters = logical_masters(control["v"], liberty_areas(staged_views["TT"]))
        aligned, mismatches = align_db_instances(ref_masters, instances)
        if mismatches:
            baseline_record["netlist_odb_mismatch"] = mismatches
            raise TrialFailure("source ODB and final exported logical masters disagree")
        index = baseline / "flattened_instance_index.txt"
        index.write_text("".join(f"{master} \\{name} ();\n" for name, master in ref_masters.items()), encoding="utf-8")
        pool = select_pool(index, staged_views, masters, aligned)
        save(args.out / "pool.json", [asdict(a) for a in pool])
        baseline_record["pool_instances"] = len(pool)
        required = (args.max_evals - 1) * args.batch_size + 1
        if len(pool) < required:
            raise TrialFailure(f"only {len(pool)} eligible instances for matched schedule requiring {required}")
        evaluator = Evaluator(args, control, staged_views, ref_masters, reference_views, pool, scope)
        reference = endpoint("control", evaluator.ref_area, reference_views, scope, baseline, True, True)
        baseline_record["endpoint"] = asdict(reference)
    except (TrialFailure, OSError, ValueError) as error:
        baseline_record.update(failure=str(error), status="blocked")
        save(baseline / "receipt.json", baseline_record)
        print(str(error), file=sys.stderr)
        return 2
    baseline_record["status"] = "passed"
    save(baseline / "receipt.json", baseline_record)
    if args.prepare_only:
        return 0

    _, noop = evaluator.evaluate((), args.out / "noop", noop=True)
    if noop["failures"]:
        print(f"shared no-op did not qualify: {noop['failures']}", file=sys.stderr)
        return 2
    if args.probe_only:
        return 0
    if matched_runner is not None:
        phase_complete, payload = matched_runner(args, evaluator, reference, pool, baseline_record, noop)
    else:
        results, receipts = {}, {}
        for method in METHODS:
            results[method], receipts[method] = run_arm(args, evaluator, reference, pool, method)
        limit = min(result["attempt_wall_seconds"] for result in results.values())
        phase_complete = all(
            result["evaluations_used"] == args.max_evals == result["route_attempts"]
            for result in results.values()
        )
        payload = {
            "results": results, "equal_wall_prefix_limit_seconds": limit,
            "equal_wall_prefixes": {
                method: accepted_prefix(reference, results[method], receipts[method], limit) for method in METHODS
            },
        }
    source_bindings = [
        *assets["control"].values(), *assets["tools"].values(), *assets["flow"].values(),
        *assets["driver_source"].values(), assets["qualification_receipt"], assets["original_sdc"],
        *(entry for libraries in assets["source_libraries"].values() for entry in libraries),
    ]
    if "route_guide" in assets:
        source_bindings.append(assets["route_guide"])
    if any(bind(Path(entry["path"])) != entry for entry in source_bindings):
        raise TrialFailure("one or more frozen inputs changed during matched runs")
    save(args.out / "results.json", {
        **payload,
        "status": "matched" if phase_complete else "incomplete budget",
        "scope": scope, "control": baseline_record, "shared_noop": noop,
    })
    return 0 if phase_complete else 2


def create_parser(description=__doc__) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--pdk", choices=("sky130hd", "asap7"), required=True)
    parser.add_argument("--control-dir", type=Path, required=True)
    parser.add_argument("--original-sdc", type=Path, required=True)
    parser.add_argument("--control-drc", type=Path, required=True)
    parser.add_argument("--views-json", type=Path, required=True, help="P0 qualification receipt binding artifacts and views")
    parser.add_argument("--out", type=Path, required=True, help="must be a fresh directory")
    parser.add_argument("--sec", type=Path, required=True, help="SEC helper using gold.v gate.v output_dir")
    parser.add_argument("--orfs", type=Path, default=ORFS)
    parser.add_argument("--openroad", type=Path, default=OPENROAD)
    parser.add_argument("--sta", type=Path, default=STA)
    parser.add_argument("--max-evals", type=int, default=6)
    parser.add_argument("--batch-size", type=int, default=3)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--route-mode", choices=("local", "full"), default="local")
    parser.add_argument("--route-guide", type=Path, help="guide emitted by the CONTROL producer")
    parser.add_argument("--embedded-guides", action="store_true", help="retain the ODB guide metadata")
    parser.add_argument("--zero-reextract", action="store_true", help="no-op uses the frozen DRT")
    parser.add_argument("--droute-iters", type=int, default=64)
    parser.add_argument("--route-timeout", type=float, default=1500)
    parser.add_argument("--sta-timeout", type=float, default=180)
    parser.add_argument("--sec-timeout", type=float, default=600)
    parser.add_argument("--report-setup-endpoints", action="store_true")
    phases = parser.add_mutually_exclusive_group()
    phases.add_argument("--prepare-only", action="store_true", help="CONTROL and candidate pool only")
    phases.add_argument("--probe-only", action="store_true", help="CONTROL, pool and one shared no-op only")
    return parser


def prepare_args(parser, args):
    if args.embedded_guides and (args.route_mode != "local" or args.route_guide is not None):
        parser.error("embedded guides require local routing with no guide override")
    if args.zero_reextract and not args.embedded_guides:
        parser.error("zero re-extraction requires embedded guides")
    if args.route_mode == "local" and args.route_guide is None and not args.embedded_guides:
        args.route_guide = args.control_dir / "route.guide"
    for name in ("control_dir", "original_sdc", "control_drc", "views_json", "out", "sec", "orfs",
                 "openroad", "sta", "route_guide"):
        value = getattr(args, name)
        if value is not None:
            setattr(args, name, value.resolve())
    values = (args.max_evals, args.batch_size, args.threads, args.route_timeout, args.sta_timeout, args.sec_timeout)
    if any(not math.isfinite(value) or value <= 0 for value in values) or not 1 <= args.droute_iters <= 64:
        parser.error("budgets, stage timeouts and thread count must be positive, DRT iterations must be in [1, 64]")
    return args


def main() -> int:
    parser = create_parser()
    args = prepare_args(parser, parser.parse_args())
    try:
        return run(args)
    except (TrialFailure, OSError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
