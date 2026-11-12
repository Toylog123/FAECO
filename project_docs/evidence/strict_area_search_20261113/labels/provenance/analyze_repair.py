"""Read-only, fail-closed audit of the preregistered physical repair singleton sweep.

Only SUMMARY.partial.json (incomplete sweep) or SUMMARY.json (all jobs finished)
is written. No EDA tools, candidate mutations, or run-plan changes occur here.
"""
import copy
from decimal import Decimal
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "code/scripts"))
sys.path.insert(0, str(ROOT / "code/src"))
from recover_area import load_liberty_areas
from run_sequential_timing_check import LIB
from rseco.opensta import _to_sta_path

spec = importlib.util.spec_from_file_location("repair_structure", HERE / "structure_reader.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
TAP = "sky130_fd_sc_hd__tapvpwrvgnd_1"
ERROR = re.compile(r"(?im)^.*(?:Error:|\[ERROR|invalid command name|wrong # args|failed to).*$")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def readlog(path, marker):
    raw = path.read_text(encoding="utf-8", errors="replace").replace("\x00", "")
    require(marker in raw, f"Missing {marker}: {path}")
    require(not ERROR.search(raw), f"Error diagnostic: {path}")
    return raw


def metrics(raw):
    values = {}
    for key, token in (("setup_ns", "ROUTED_WNS_MAX"), ("hold_ns", "ROUTED_WNS_MIN")):
        matches = re.findall(token + r"\s+([-+\d.eE]+)", raw)
        require(len(matches) == 1, f"Nonunique/missing {token}")
        values[key] = float(matches[0]) * 1e9
    tns = re.findall(r"(?m)^tns max\s+([-+\d.eE]+)", raw)
    require(tns and len(tns[-1].split(".")[-1]) >= 9, "TNS9 unavailable")
    values["tns_ns"] = float(tns[-1])
    require(all(math.isfinite(v) for v in values.values()), "Nonfinite timing metric")
    return values


def structure(path):
    return reader.Reader(path.read_text(encoding="utf-8")).parse()[0]


def area(design, areas):
    total = Decimal(0)
    taps = []
    for name, cell in design["instances"].items():
        if cell["cell"] == TAP:
            require(not cell["pins"], "Connected tap cannot be excluded")
            taps.append(name)
        else:
            require(cell["cell"] in areas, f"Unknown area cell {cell['cell']} at {name}")
            total += Decimal(str(areas[cell["cell"]]))
    return float(total), sorted(taps)


def baseline(label, areas):
    directory = HERE / "inputs" / label
    diagnostic = HERE / "pathdiag"
    archive = json.loads((diagnostic / "archive_sha256.json").read_text())
    manifest = json.loads((diagnostic / "manifest.json").read_text())
    job = manifest["arms"][label]
    require(job["run"]["returncode"] == 0, "Diagnostic STA failed")
    for key, value in job["inputs"].items():
        require(sha(ROOT / key) == value, "Diagnostic input hash mismatch")
    for suffix in ("log", "tcl"):
        path = diagnostic / f"{label}.{suffix}"
        require(sha(path) == archive[path.name], "Diagnostic archive hash mismatch")
    raw = readlog(diagnostic / f"{label}.log", "PATHDIAG_TNS9_END")
    require("PATHDIAG_DONE" in raw and "ROUTED_STA_OK" in raw, "Incomplete baseline diagnostics")
    design = structure(directory / "routed.v")
    total, taps = area(design, areas)
    return dict(metrics=metrics(raw), area=total, taps=taps, structure=design,
                hashes={str(p.relative_to(HERE)): sha(p) for p in [directory / "routed.v", directory / "routed.spef", diagnostic / f"{label}.log", diagnostic / f"{label}.tcl"]})


def audit_arm(arm, restored, control, recovered, recipe, areas, tol, batch):
    directory = HERE / "runs" / arm
    result = {"arm": arm, "restored": restored, "status": "pending", "functional_equivalence": "not checked"}
    if arm not in batch:
        return result
    result["batch"] = batch[arm]
    try:
        require(batch[arm]["returncode"] == 0, "Batch subprocess failed")
        manifest = json.loads((directory / "manifest.json").read_text())
        require(manifest["restored_instances"] == restored, "Manifest restore-set mismatch")
        for key, value in manifest["input_sha256"].items():
            require(sha(ROOT / key) == value, f"Input SHA drift: {key}")
        require(sha(directory / "flow.tcl") == manifest["tcl_sha256"], "Flow Tcl hash mismatch")
        require(manifest["flow"]["returncode"] == 0, "Flow failure")
        readlog(directory / "flow.log", "PHYSICAL_PROBE_OK")
        report = (directory / "drc.rpt").read_text()
        require(not report.strip() and manifest["drc_count"] == 0, "Nonempty/missing DRC report or count mismatch")
        design = structure(directory / "routed.v")
        expected = copy.deepcopy(control["structure"])
        for change in recipe:
            inst = change["instance"]
            require(expected["instances"][inst]["cell"] == change["new_cell"], "Recipe input cell mismatch")
            if inst not in restored:
                expected["instances"][inst]["cell"] = change["old_cell"]
        require(design == expected, "Final netlist is not exact recipe-minus-restored structure")
        total, taps = area(design, areas)
        require(taps == control["taps"], "Physical tap set drift")
        result["structure_check"] = {"exact_recipe_minus_restored": True,
                                     "all_instances": len(design["instances"]),
                                     "functional_instances": len(design["instances"]) - len(taps),
                                     "pin_bindings": sum(len(c["pins"]) for c in design["instances"].values()),
                                     "excluded_empty_pin_taps": len(taps), "all_functional_cells_have_liberty_area": True}
        result["supported_rule_drc_zero"] = True
        result["area"] = total
        result["area_saved"] = control["area"] - total
        result["area_saved_pct"] = result["area_saved"] / control["area"] * 100
        result["original_saving_retained_pct"] = result["area_saved"] / (control["area"] - recovered["area"]) * 100
        result["metrics"] = {}
        for clock in ("ideal", "propagated"):
            require(manifest[clock]["returncode"] == 0, "STA failure")
            script = (directory / f"{clock}.tcl").read_text()
            for name in ("routed.v", "routed.spef"):
                require(_to_sta_path(directory / name) in script, "STA does not bind this physical endpoint")
            require("report_check_types -max_slew -max_capacitance -violators -digits 9" in script, "DRV report missing")
            require("report_worst_slack -min -digits 9" in script, "DRV end boundary missing")
            require(("set_propagated_clock [all_clocks]" in script) == (clock == "propagated"), "Wrong clock mode")
            raw = readlog(directory / f"{clock}.log", "ROUTED_STA_OK")
            drv = re.search(r"ROUTED_STA_OK([\s\S]*?)worst slack min", raw)
            require(drv and "VIOLATED" not in drv.group(1), "Missing or violated DRV segment")
            require("Startpoint:" in raw and "Endpoint:" in raw, "Detailed paths absent")
            result["metrics"][clock] = metrics(raw)
            require(result["metrics"][clock]["setup_ns"] == manifest[clock]["setup_ns"], "Manifest WNS mismatch")
            require(result["metrics"][clock]["hold_ns"] == manifest[clock]["hold_ns"], "Manifest hold mismatch")
            require(result["metrics"][clock]["tns_ns"] == float(manifest[clock]["tns_reports_ns"][-1]), "Manifest TNS mismatch")
        measured = result["metrics"]["propagated"]
        result["configured_slew_cap_report_no_violations"] = True
        result["deltas_ns"] = {key: measured[key] - control["metrics"][key] for key in measured}
        result["deficits_after_tolerance_ns"] = {key: max(0.0, -delta - tol) for key, delta in result["deltas_ns"].items()}
        result["absolute_hold_feasible"] = measured["hold_ns"] >= 0
        result["primary_numeric_pass"] = all(delta >= -tol for delta in result["deltas_ns"].values()) and result["absolute_hold_feasible"] and result["area_saved"] > 0
        result["diagnostic_budget_pass"] = {str(b): result["deltas_ns"]["setup_ns"] >= -b-tol and result["deltas_ns"]["tns_ns"] >= -tol and result["deltas_ns"]["hold_ns"] >= -tol and result["absolute_hold_feasible"] and result["area_saved"] > 0 for b in (0, .002, .005, .010)}
        result["output_sha256"] = {p.name: sha(p) for p in sorted(directory.iterdir()) if p.is_file()}
        result["status"] = "validated_numeric_candidate_pending_SEC" if result["primary_numeric_pass"] else "validated_primary_fail"
    except (ValueError, KeyError, OSError, TypeError) as exc:
        result["status"] = "invalid_or_missing_evidence"
        result["reason"] = str(exc)
    return result


def main():
    plan = json.loads((HERE / "PLAN.json").read_text())
    batch_data = json.loads((HERE / "BATCH_RECEIPT.json").read_text())
    batch = {job["arm"]: job for job in batch_data["jobs"]}
    require(batch_data["driver_sha256"] == sha(HERE / "physical_probe.py"), "Batch driver changed")
    require(batch_data["plan_sha256"] == sha(HERE / "PLAN.json"), "Batch plan changed")
    for name, info in json.loads((HERE / "inputs/MANIFEST.json").read_text()).items():
        require(sha(HERE / "inputs" / name) == info["sha256"], "Frozen input mismatch")
    areas = load_liberty_areas(LIB)
    control, recovered = baseline("CONTROL", areas), baseline("RECOVERY_V2", areas)
    recipe = json.loads((HERE / "inputs/recipe.json").read_text())["applied"]
    require(len(recipe) == 13 and len(plan["singletons"]) == 13, "Expected exactly 13 singleton recipes")
    require(all(len(v) == 1 for v in plan["singletons"].values()) and
            sorted(v[0] for v in plan["singletons"].values()) == sorted(r["instance"] for r in recipe),
            "Singleton plan does not exhaust every archived action exactly once")
    rows = [audit_arm(arm, restored, control, recovered, recipe, areas, plan["tolerance_ns"], batch) for arm, restored in plan["singletons"].items()]
    complete = all(row["status"] != "pending" for row in rows)
    summary = {"scope": "all13 single compensation cases; propagated strict WNS/TNS/hold non-worsening and hold>=0; SEC pending", "all13_finished": complete,
               "analyzer_sha256": sha(Path(__file__)), "reader_sha256": sha(HERE / "structure_reader.py"), "liberty_sha256": sha(LIB),
               "plan_sha256": sha(HERE / "PLAN.json"), "batch_receipt_sha256": sha(HERE / "BATCH_RECEIPT.json"),
               "baseline": {k: v for k, v in control.items() if k not in ("structure", "taps")},
               "original_recovery": {k: v for k, v in recovered.items() if k not in ("structure", "taps")},
               "rows": rows, "primary_candidates_pending_SEC": [r["arm"] for r in rows if r.get("primary_numeric_pass")],
               "limitations": ["No new EDA or SEC executed by analyzer.", "DRC limited to supported installed-flow rules; known skipped LEF58 rules remain.", "DRV acceptance only configured max-slew/cap reports; complete timing constraint coverage is not established.", "Known negative setup path VIOLATED labels are not mistaken for DRV violations."]}
    target = HERE / ("SUMMARY.json" if complete else "SUMMARY.partial.json")
    target.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"all13_finished": complete, "counts": {status: sum(r["status"] == status for r in rows) for status in sorted({r["status"] for r in rows})}, "primary_candidates_pending_SEC": summary["primary_candidates_pending_SEC"]}))


if __name__ == "__main__":
    main()
