"""Replay SKY130 s713/s832 with one physical snapshot and four timing views."""
import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / name) for name in (
    "code/src", "code/scripts", "project_docs/evidence/timing_budget_20261113",
)]
from recover_area import load_liberty_areas
from rseco.budgeted_recovery import BudgetPolicy, Endpoint, assess
from rseco.opensta import _to_sta_path
from rseco.physical_budget_adapter import (
    DEFAULT_LIBERTY, adaptive_batch_recovery, compute_mapped_area,
    generate_compatible_candidates, parse_sta_log, render_physical_flow_tcl,
    render_propagated_sta_tcl,
)
from rseco.placed_sta import DEFAULT_OPENROAD, DEFAULT_PLATFORM
from rseco.routed_sta import DEFAULT_ORFS, DEFAULT_STA
import run_r22_cut_ablation as sec
from structure_reader import Reader

OUT = ROOT / "scratch/sky130_joint_constraints_20261123"
START = ROOT / "experiments/20261115_p1_resizer_vs_faeco/arms/Resizer"
HISTORIC = {"s713": "RUN_008", "s832": "RUN_009"}
LIB_ROOT = "/home/toylog/faeco_eda/build26/OpenROAD-src/test/sky130hd"
LIBS = {
    mode: f"{LIB_ROOT}/sky130_fd_sc_hd__{corner}.lib"
    for mode, corner in (
        ("TT", "tt_025C_1v80"), ("SS", "ss_n40C_1v40"),
        ("FF", "ff_n40C_1v95"), ("IO_OCV", "tt_025C_1v80"),
    )
}
IO_OCV = """
foreach p [all_inputs] {
    if {[get_name $p] ne "CK"} {
        set_input_delay 0.10 -clock clk $p
        set_input_transition 0.05 $p
    }
}
set_output_delay 0.10 -clock clk [all_outputs]
set_load 0.01 [all_outputs]
set_timing_derate -early 0.90
set_timing_derate -late 1.10
"""
POLICY = BudgetPolicy.from_ps(10)
MAX_EVALS, BATCH_SIZE, THREADS = 10, 3, 4
TAP = "sky130_fd_sc_hd__tapvpwrvgnd_1"
ERROR = re.compile(r"^\s*(?:\[ERROR|Error:|Error\s+[^\n]*\.tcl)", re.M)


def save(path, payload):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(directory, names):
    return {name: digest(directory / name) for name in names if (directory / name).is_file()}


def wsl(*argv):
    return ["wsl.exe", "-d", "Ubuntu", "--", *argv]


def run_tool(argv, log, timeout):
    with log.open("wb") as stream:
        try:
            return subprocess.run(
                wsl("timeout", "--kill-after=5s", f"{timeout}s", *argv),
                stdout=stream, stderr=subprocess.STDOUT, timeout=timeout + 20,
            ).returncode
        except subprocess.TimeoutExpired:
            return 124


def measure(circuit, source, out):
    out.mkdir(exist_ok=True)
    result = {}
    for mode, lib in LIBS.items():
        tcl = render_propagated_sta_tcl(
            netlist_path=source / "routed.v", spef_path=source / "routed.spef",
            top_module=circuit, period=0.5, clk_port="CK",
            extra_sta_tcl=IO_OCV if mode == "IO_OCV" else "",
        ).replace(
            "read_liberty $PLATFORM/lib/sky130_fd_sc_hd__tt_025C_1v80.lib",
            f"read_liberty {lib}",
        ).replace("report_tns\n", "report_tns -digits 6\n")
        tcl += (
            "\nreport_checks -path_delay min -format full_clock_expanded -digits 6"
            "\nputs JOINT_STA_COMPLETE\nexit\n"
        )
        tcl_file, log = out / f"{mode}.tcl", out / f"{mode}.log"
        tcl_file.write_text(tcl, encoding="utf-8")
        rc = run_tool([DEFAULT_STA, "-no_splash", "-exit", _to_sta_path(tcl_file)], log, 60)
        text = log.read_text(encoding="utf-8", errors="replace")
        values = parse_sta_log(text)
        valid = rc == 0 and "JOINT_STA_COMPLETE" in text and not ERROR.search(text)
        valid = valid and all(value is not None and math.isfinite(value) for value in values.values())
        result[mode] = {"returncode": rc, "valid": valid, **values}
    return result


def deltas(ref, metrics):
    return {
        mode: {key: 1000 * (row[key] - ref[mode][key]) for key in ("setup_ns", "hold_ns", "tns_ns")}
        for mode, row in metrics.items() if row["valid"]
    }


def reasons(ref, metrics, saving, physical_ok, *, io_floor=True):
    if not physical_ok:
        return ["physical_or_identity_failure"]
    findings = [] if saving > 1e-9 else ["no_area_gain"]
    for mode, row in metrics.items():
        if not row["valid"]:
            findings.append(f"{mode}:sta_failure")
            continue
        if row["setup_ns"] < ref[mode]["setup_ns"] - POLICY.wns_budget_ns - POLICY.tolerance_ns:
            findings.append(f"{mode}:setup_budget")
        if row["hold_ns"] < ref[mode]["hold_ns"] - POLICY.tolerance_ns:
            findings.append(f"{mode}:hold_regression")
        if row["hold_ns"] < 0 and (mode != "IO_OCV" or io_floor):
            findings.append(f"{mode}:negative_hold")
    return findings


def instances(text):
    return Reader(text).parse()[0]["instances"]


def masters(path):
    return {key: row["cell"] for key, row in instances(path.read_text(encoding="utf-8")).items()}


def route_tcl(circuit, source, out, actions, components):
    replacements = []
    for action in actions:
        instance = action.instance.removeprefix("\\")
        if components.get(instance) != action.source_cell:
            raise ValueError(f"DEF and netlist disagree on {instance}")
        replacements.append((instance, action.target_cell))
    marker = f"read_db {_to_sta_path(out / 'unused.odb')}"
    tcl = render_physical_flow_tcl(
        odb_path=out / "unused.odb", spef_path=source / "routed.spef", out_dir=out,
        top_module=circuit, period=0.5, clk_port="CK", droute_iter=15,
        replacements=replacements,
    )
    if tcl.count(marker) != 1:
        raise ValueError("expected one database read in the reused Tcl")
    read_def = (
        f"read_lef {DEFAULT_PLATFORM}/lef/sky130_fd_sc_hd.tlef\n"
        f"read_lef {DEFAULT_PLATFORM}/lef/sky130_fd_sc_hd_merged.lef\n"
        f"read_def {_to_sta_path(source / 'routed.def')}"
    )
    return tcl.replace(marker, read_def)


def project_taps(path):
    raw = path.read_text(encoding="utf-8")
    taps = {key: row for key, row in instances(raw).items() if row["cell"] == TAP}
    if any(row["pins"] for row in taps.values()):
        raise ValueError("connected tap")
    text, count = re.subn(
        rf"(?m)^[ \t]*{TAP}[ \t]+[A-Za-z_$][A-Za-z0-9_$]*[ \t]*\([ \t]*\)[ \t]*;[ \t]*\n?",
        "", raw,
    )
    if count != len(taps):
        raise ValueError("tap projection count mismatch")
    return text, taps


def prove(circuit, gold, gate, out):
    initial, initial_taps = project_taps(gold)
    final, final_taps = project_taps(gate)
    if initial_taps != final_taps:
        raise ValueError("tap instances changed")
    cells = {row["cell"] for text in (initial, final) for row in instances(text).values()}
    legacy = sec.write_liberty_cell_models

    def complete_models(liberty, output, **kwargs):
        kwargs["used_cells"] = cells
        return legacy(liberty, output, **kwargs)

    sec.write_liberty_cell_models = complete_models
    try:
        result = sec.final_sec(initial, final, circuit, out)
    finally:
        sec.write_liberty_cell_models = legacy
    log = out / "sec.log"
    counts = re.findall(r"(\d+) are proven and (\d+) are unproven", log.read_text(encoding="utf-8")) if log.is_file() else []
    proved, unproved = map(int, counts[-1]) if counts else (0, None)
    result.update(
        gold_routed_sha256=digest(gold), gate_routed_sha256=digest(gate),
        projected_taps=len(initial_taps), equiv_proven=proved, equiv_unproven=unproved,
        accepted=result["status"] == "pass" and result["returncode"] == 0 and proved > 0 and unproved == 0,
    )
    save(out / "receipt.json", result)
    return result


def run_circuit(circuit, out, reuse_from=None):
    source = START / circuit
    historic = ROOT / "scratch/tool_agnostic_iscas89" / circuit / "evals" / HISTORIC[circuit]
    required = ("routed.def", "routed.v", "routed.spef", "drc.rpt")
    input_hashes = identity(source, required)
    if len(input_hashes) != len(required) or (source / "drc.rpt").read_text().strip():
        raise ValueError(f"missing or non-clean CONTROL: {source}")
    before = masters(source / "routed.v")
    def_text = (source / "routed.def").read_text(encoding="utf-8")
    components_text = def_text.split("\nCOMPONENTS ", 1)[1].split("\nEND COMPONENTS", 1)[0]
    components = dict(re.findall(r"^\s*-\s+(\S+)\s+(\S+)", components_text, re.M))
    areas = load_liberty_areas()
    control_area = compute_mapped_area(source / "routed.v", areas)
    actions = generate_compatible_candidates(
        source / "routed.v", one_per_instance=True, deprioritize_zero_drive=True,
    )
    by_id = {a.action_id: a for a in actions}
    assets = [
        *dict.fromkeys(LIBS.values()),
        f"{DEFAULT_PLATFORM}/lib/sky130_fd_sc_hd__tt_025C_1v80.lib",
        f"{DEFAULT_PLATFORM}/lef/sky130_fd_sc_hd.tlef",
        f"{DEFAULT_PLATFORM}/lef/sky130_fd_sc_hd_merged.lef",
        f"{DEFAULT_ORFS}/setRC.tcl", f"{DEFAULT_ORFS}/rcx/rcx_patterns.rules",
    ]
    hashes = subprocess.check_output(wsl("sha256sum", *assets), text=True, timeout=30)
    save(out / "config.json", {
        "circuit": circuit,
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, timeout=15).strip(),
        "control": source.relative_to(ROOT).as_posix(), "control_sha256": input_hashes,
        "historic": historic.relative_to(ROOT).as_posix(),
        "historic_sha256": identity(historic, ("routed.v", "routed.spef", "flow.tcl")),
        "source_sha256": {path.relative_to(ROOT).as_posix(): digest(path) for path in (
            Path(__file__), DEFAULT_LIBERTY, sec.LIB,
            ROOT / "code/src/rseco/physical_budget_adapter.py",
            ROOT / "code/src/rseco/budgeted_recovery.py",
            ROOT / "code/scripts/run_r22_cut_ablation.py",
        )},
        "wsl_asset_sha256": dict(line.split("  ", 1)[::-1] for line in hashes.splitlines()),
        "scenario_liberty": LIBS, "period_ns": 0.5, "clock_port": "CK",
        "io_ocv_tcl": IO_OCV, "policy": asdict(POLICY), "max_evals": MAX_EVALS,
        "batch_size": BATCH_SIZE, "route_threads": THREADS, "droute_iterations": 15,
        "timeout_s": {"route": 180, "sta": 60, "sec": 180},
        "actions": [asdict(action) for action in actions],
    })
    reusable = {}
    if reuse_from is not None:
        previous_config = json.loads((reuse_from / "config.json").read_text(encoding="utf-8"))
        config = json.loads((out / "config.json").read_text(encoding="utf-8"))
        immutable = (
            "control_sha256", "wsl_asset_sha256", "scenario_liberty", "actions", "policy",
            "period_ns", "clock_port", "io_ocv_tcl", "route_threads", "droute_iterations",
        )
        if any(previous_config[key] != config[key] for key in immutable):
            raise ValueError("route replay configuration mismatch")
        for metrics in sorted(reuse_from.glob("*/metrics.json")):
            prior = json.loads(metrics.read_text(encoding="utf-8"))
            if prior.get("route_ok"):
                reusable[tuple(prior["action_ids"])] = (metrics.parent, prior["routed_sha256"])
    print(f"{circuit} config saved; {len(actions)} candidates", flush=True)
    ref = measure(circuit, source, out / "CONTROL")
    save(out / "CONTROL/metrics.json", ref)
    if not all(row["valid"] for row in ref.values()):
        raise RuntimeError("invalid CONTROL STA")
    print(f"{circuit} CONTROL IO hold {ref['IO_OCV']['hold_ns'] * 1000:.3f} ps", flush=True)
    old = measure(circuit, historic, out / "HISTORIC_TT")
    comparison = {
        "metrics": old, "deltas_ps_vs_current_control": deltas(ref, old),
        "area": compute_mapped_area(historic / "routed.v", areas),
        "reference_note": "Historical publication used a different measured CONTROL.",
    }
    save(out / "HISTORIC_TT/metrics.json", comparison)
    records = []

    def route(endpoint, ids):
        trial_start = time.monotonic()
        path = out / endpoint
        path.mkdir()
        edits = [by_id[key] for key in ids]
        tcl, log = path / "flow.tcl", path / "flow.log"
        reused_route = None
        if ids in reusable:
            prior_dir, expected_files = reusable[ids]
            if len(expected_files) != 5 or identity(prior_dir, expected_files) != expected_files:
                raise ValueError(f"route replay artifact identity mismatch: {prior_dir}")
            for name in (*expected_files, "flow.tcl", "flow.log"):
                shutil.copyfile(prior_dir / name, path / name)
            reused_route = prior_dir.relative_to(OUT).as_posix()
            rc = 0
        else:
            tcl.write_text(route_tcl(circuit, source, path, edits, components), encoding="utf-8")
            rc = run_tool([DEFAULT_OPENROAD, "-threads", str(THREADS), "-no_init", "-exit", _to_sta_path(tcl)], log, 180)
        text = log.read_text(encoding="utf-8", errors="replace")
        files = identity(path, ("routed.v", "routed.def", "routed.odb", "routed.spef", "drc.rpt"))
        drc_text = (path / "drc.rpt").read_text(encoding="utf-8", errors="replace") if "drc.rpt" in files else None
        drc = None if drc_text is None else len(re.findall(r"^\s*violation type:", drc_text, re.M))
        route_ok = rc == 0 and "PHYSICAL_PROBE_OK" in text and not ERROR.search(text)
        route_ok = route_ok and len(files) == 5 and drc == 0 and not drc_text.strip()
        changes = {}
        if route_ok:
            after = masters(path / "routed.v")
            want = before | {action.instance.removeprefix("\\"): action.target_cell for action in edits}
            changes = {key: [want.get(key), after.get(key)] for key in want.keys() | after.keys() if want.get(key) != after.get(key)}
        physical_ok = route_ok and not changes
        metrics = measure(circuit, path, path) if physical_ok else {}
        area = compute_mapped_area(path / "routed.v", areas) if "routed.v" in files else None
        saving = 0 if area is None else control_area - area
        row = {
            "endpoint": endpoint, "action_ids": list(ids), "route_returncode": rc,
            "route_ok": route_ok, "physical_ok": physical_ok, "drc_count": drc,
            "reused_route": reused_route,
            "unexpected_master_changes": changes, "area": area, "area_saved": saving,
            "metrics": metrics, "deltas_ps": deltas(ref, metrics), "routed_sha256": files,
            "strict_reasons": reasons(ref, metrics, saving, physical_ok),
            "relative_io_hold_reasons": reasons(ref, metrics, saving, physical_ok, io_floor=False),
            "elapsed_s": round(time.monotonic() - trial_start, 3),
        }
        save(path / "metrics.json", row)
        print(f"{circuit} {endpoint} save={saving:.4f} strict={row['strict_reasons']} relative={row['relative_io_hold_reasons']}", flush=True)
        return row

    elapsed_start = time.monotonic()
    null = route("NO_CHANGE", ())
    tt = ref["TT"]
    reference = Endpoint("CONTROL", control_area, tt["setup_ns"], tt["tns_ns"], tt["hold_ns"], circuit, str(source), True, True)

    def evaluate(ids):
        row = route(f"RUN_{len(records) + 1:03d}", ids)
        records.append(row)
        m = row["metrics"].get("TT", {})
        endpoint = Endpoint(
            row["endpoint"], row["area"] or reference.area, m.get("setup_ns") or 0.0,
            m.get("tns_ns") or 0.0, m.get("hold_ns") or 0.0, circuit,
            str(out / row["endpoint"]), not row["strict_reasons"], False,
        )
        if endpoint.valid and not assess(reference, endpoint, POLICY).feasible:
            raise AssertionError("joint gate and nominal gate disagree")
        return endpoint

    search = adaptive_batch_recovery(reference, actions, evaluate, POLICY, max_evaluations=MAX_EVALS, batch_size=BATCH_SIZE)
    if identity(source, required) != input_hashes:
        raise RuntimeError("CONTROL identity changed")
    proofs = {}

    def pick(reason_key):
        eligible = sorted((row for row in records if not row[reason_key]), key=lambda row: (-row["area_saved"], row["endpoint"]))
        for row in eligible:
            key = row["endpoint"]
            if key not in proofs:
                proofs[key] = prove(circuit, source / "routed.v", out / key / "routed.v", out / key / "SEC")
            if proofs[key]["accepted"]:
                return key
        return None

    strict = pick("strict_reasons")
    relative = pick("relative_io_hold_reasons")
    save(out / "summary.json", {
        "circuit": circuit, "control_area": control_area, "control_metrics": ref,
        "historic_endpoint": comparison, "no_change": null,
        "candidate_count": len(actions), "evaluations": records,
        "physical_route_count": sum(row["reused_route"] is None for row in [null, *records]),
        "reused_route_count": sum(row["reused_route"] is not None for row in [null, *records]),
        "search_committed": search["committed"],
        "search_selected_before_sec": search["selected"].endpoint_id,
        "selected_strict": strict, "selected_relative_io_hold_diagnostic": relative,
        "sec": proofs, "elapsed_search_and_sec_s": round(time.monotonic() - elapsed_start, 3),
        "strict_failure_histogram": dict(Counter(reason for row in records for reason in row["strict_reasons"])),
    })
    print(f"{circuit} DONE strict={strict} relative={relative}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("circuit", choices=tuple(HISTORIC))
    parser.add_argument("--retry", action="store_true", help="write to a new directory")
    parser.add_argument("--replay", action="store_true", help="reuse fingerprint-matched routes from _retry")
    args = parser.parse_args()
    if args.retry and args.replay:
        parser.error("--retry and --replay are mutually exclusive")
    suffix = "_retry" if args.retry else "_replay" if args.replay else ""
    output = OUT / f"{args.circuit}{suffix}"
    output.mkdir(parents=True, exist_ok=False)
    reuse_from = OUT / f"{args.circuit}_retry" if args.replay else None
    run_circuit(args.circuit, output, reuse_from)

