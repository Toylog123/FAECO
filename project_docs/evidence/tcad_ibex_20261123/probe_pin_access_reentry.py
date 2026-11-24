#!/usr/bin/env python3
"""Replay a new ECO from each saved pin-access state under an exact 2×2 design."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
COMPARISON_SOURCE = Path(__file__).with_name("compare_ibex.py").resolve()
PIN = "4f28ada3"
ORDER = ("AA", "BB", "AB", "BA")
CASES = {"gcd": (5, (13, 14, 15), (16,)), "ibex_core": (3, (7, 8, 9), (10, 11, 12))}


def read(path):
    return json.loads(Path(path).read_bytes())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def frozen_comparison():
    relative = COMPARISON_SOURCE.relative_to(ROOT).as_posix()
    source = subprocess.check_output(["git", "show", f"{PIN}:{relative}"], cwd=ROOT)
    module = ModuleType("compare_ibex")
    module.__file__ = str(COMPARISON_SOURCE)
    sys.modules[module.__name__] = module
    exec(compile(source, str(COMPARISON_SOURCE), "exec"), module.__dict__)
    return module, source


def route_renderer(base_renderer, mode, out):
    def render(args, libraries, control, destination, actions):
        require(args.embedded_guides and destination == out and bool(actions), "unexpected re-entry route command")
        source = base_renderer(args, libraries, control, destination, actions)
        marker = '\npin_access\nif {![grt::have_routes]}'
        require(source.count(marker) == 1, "original explicit pin-access command missing")
        return source.replace(marker, '\nif {![grt::have_routes]}', 1) if mode == "B" else source

    return render


def compare_results(left, right):
    return {key: left[key] == right[key] for key in (
        "odb_sha256", "def_sha256", "v_sha256", "drc_sha256", "spef_sha256_without_date",
        "layout", "views", "setup_endpoint_counts", "failures", "accepted", "sec",
        "area_saved_original",
    )}


def run(reference, out):
    comparison, comparison_source = frozen_comparison()
    from probe_duplicate_pin_access import spef_without_date
    from run_screened_matrix import CLOCK_NAME, bind_runtime, raw_seconds
    import run_setup_budget_sweep as sweep
    from verify_setup_protocol import check_bindings

    ab_config = read(reference / "config.json")
    ab_result = read(reference / "results.json")
    require(ab_result["status"] == "matched", "expected completed first-stage A/B")
    top = ab_config["top"]
    slot, prior_ranks, new_ranks = CASES[top]
    assets = ab_config["bindings"]
    require(assets["driver_source"]["compare_ibex.py"]["sha256"] == hashlib.sha256(comparison_source).hexdigest(),
            "historical comparison driver differs from selected Git snapshot")
    check_bindings({k: v for k, v in assets.items() if k != "driver_source"})
    sources = {k: v for k, v in assets["driver_source"].items() if k != "compare_ibex.py"}
    check_bindings(sources)
    check_bindings(ab_config["reference_bindings"])
    frozen = {name: Path(item["path"]) for name, item in assets["control"].items()}
    libs = {corner: [Path(item["path"]) for item in items] for corner, items in assets["used_libraries"].items()}
    pool = [comparison.PhysicalAction(**r) for r in read(ab_config["reference_bindings"][-1]["path"])]
    prior_actions = tuple(sorted(pool[rank - 1].action_id for rank in prior_ranks))
    new_actions = tuple(sorted(pool[rank - 1].action_id for rank in new_ranks))
    cumulative = tuple(sorted(prior_actions + new_actions))
    hist = Path(ab_config["reference_bindings"][0]["path"]).parent
    prior_historical = read(hist / "screened" / "faeco" / f"{slot:02d}.json")
    direct_path = hist / "screened" / "faeco" / f"{slot + 1:02d}.json"
    direct = read(direct_path)
    require(tuple(prior_historical["actions"]) == prior_actions and tuple(direct["actions"]) == cumulative,
            "ordered action tuples do not match original physical experiment")
    direct_physical = read(direct["physical_receipt"])
    direct_artifacts = direct_physical["artifacts"]
    direct_spef = spef_without_date(direct_artifacts["spef"]["path"])
    ab_root_paths = {"A": "01_explicit", "B": "02_automatic"}
    prior = {}
    for mode, directory in ab_root_paths.items():
        raw_path = reference / directory / "receipt.json"
        raw = read(raw_path)
        logical = read(reference / directory / "logical.json")
        sec = read(reference / directory / "sec" / "receipt.json")
        require(prior_actions == tuple(raw["actions"]) == tuple(logical["actions"]) and not logical["failures"]
                and logical["endpoint"]["valid"] and logical["endpoint"]["sec_pass"], "prior route is unqualified")
        require(sec["passed"] and sec["proven"] > 0 and sec["unproven"] == 0
                and sec["gold"] == assets["control"]["v"] and sec["gate"] == raw["artifacts"]["v"],
                "prior route SEC is unqualified")
        check_bindings(raw["artifacts"])
        prior[mode] = raw
    require(prior["A"]["views"] == prior["B"]["views"], "starting STA differs across A/B")
    for kind in ("def", "v", "drc"):
        require(prior["A"]["artifacts"][kind]["sha256"] == prior["B"]["artifacts"][kind]["sha256"],
                f"starting {kind} differs")
    require(spef_without_date(prior["A"]["artifacts"]["spef"]["path"]) ==
            spef_without_date(prior["B"]["artifacts"]["spef"]["path"]), "starting parasitics differ")

    routing = Path(assets["flow"]["fastroute.tcl"]["path"])
    flow = Path(assets["flow"]["setRC.tcl"]["path"]).parents[2]
    settings = SimpleNamespace(
        out=out, pdk=ab_config["pdk"], orfs=flow, clock_period_ps=ab_config["original_clock_period_ps"],
        openroad=Path(assets["tools"]["openroad"]["path"]), sta=Path(assets["tools"]["opensta"]["path"]),
        sec=Path(assets["tools"]["sec"]["path"]), threads=ab_config["methods_route_threads"],
        embedded_guides=True, zero_reextract=True, route_mode=ab_config["route_mode"], route_guide=None,
        droute_iters=ab_config["route_drt_iters"], route_timeout=ab_config["route_timeout_seconds"],
        sta_timeout=ab_config["sta_timeout_seconds_per_view"], sec_timeout=ab_config["sec_timeout_seconds"],
        report_setup_endpoints=ab_config["report_setup_endpoints"], control_drc=Path(assets["control_drc"]["path"]),
    )
    require(settings.pdk == "sky130hd" and settings.route_mode == "local", "expected SKY130 embedded-guide local route")
    out.mkdir()
    snapshot = out / "compare_ibex.frozen.py"
    snapshot.write_bytes(comparison_source)
    config = {
        "top": top, "clock": CLOCK_NAME, "cpu_affinity": sorted(os.sched_getaffinity(0)), "order": ORDER,
        "first_stage": prior_actions, "second_stage": new_actions, "cumulative": cumulative,
        "source": comparison.bind(Path(__file__).resolve()), "comparison_snapshot": comparison.bind(snapshot),
        "comparison_commit": PIN, "source_dependencies": sources,
        "control_and_tool_bindings": {k: v for k, v in assets.items() if k != "driver_source"},
        "starting_artifacts": {mode: row["artifacts"] for mode, row in prior.items()},
        "reference_ab": [comparison.bind(reference / kind) for kind in ("config.json", "results.json")],
        "direct_control_start": comparison.bind(direct_path),
        "active_gate": ab_result["gate"],
    }
    comparison.save(out / "config.json", config)
    scope = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    rows = {}
    renderer = comparison.render_route
    with bind_runtime(top, routing):
        areas = comparison.liberty_areas(libs["TT"])
        frozen_masters = comparison.logical_masters(frozen["v"], areas)
        original_area = ab_result["control"]["endpoint"]["area"]
        expected = frozen_masters.copy()
        for action in pool:
            if action.action_id in cumulative:
                name = comparison.canonical_odb_name(action.instance)
                require(expected[name] == action.source_cell, f"historical master mismatch: {name}")
                expected[name] = action.target_cell
        for index, arm in enumerate(ORDER, 1):
            before = prior[arm[0]]["artifacts"]
            trial_dir = out / f"{index:02d}_{arm}"
            source = {**frozen, "odb": Path(before["odb"]["path"]), "def": Path(before["def"]["path"])}
            masters = comparison.logical_masters(Path(before["v"]["path"]), areas)
            evaluator = comparison.Evaluator(settings, source, libs, masters, ab_result["control"]["views"], pool, scope)
            gate = sweep.budget_gate(evaluator, ab_config["primary_budget_pct"], False)
            require(sweep.gate_summary(gate, evaluator.ref_views) == ab_result["gate"], "original timing gates changed")

            # A new physical request is made on every arm. SEC uses source["v"], the original CONTROL.
            cache = sweep.TrialCache(evaluator) if index == 1 else cache
            cache.evaluator = evaluator
            print(f"START {arm} {trial_dir}", flush=True)
            start = raw_seconds()
            with patch.object(comparison, "render_route", route_renderer(renderer, arm[1], trial_dir)):
                endpoint, logical = cache.request(new_actions, gate, fresh_directory=trial_dir)
            charged_wall = raw_seconds() - start
            comparison.save(trial_dir / "logical.json", logical)
            physical = read(trial_dir / "receipt.json")
            require(physical["routed_to_completion"] and physical["extracted_to_completion"]
                    and len(physical["views"]) == 3, f"{arm} physically incomplete: {logical['failures']}")
            artifacts = physical["artifacts"]
            actual = comparison.logical_masters(Path(artifacts["v"]["path"]), areas)
            require(actual == expected, f"{arm} does not implement the exact cumulative edits")
            route_log = (trial_dir / "route.log").read_text()
            require(route_log.count("Start pin access.") == (2 if arm[1] == "A" else 1),
                    f"{arm} second-stage pin-access count mismatch")
            def_path = Path(artifacts["def"]["path"])
            start_def = Path(before["def"]["path"])
            incremental_layout = read(trial_dir / "layout_changes.json")
            comparison.save(trial_dir / "cumulative_layout_changes.json", comparison.changed_geometry(frozen["def"], def_path, set()))

            proof_path = trial_dir / "sec" / "receipt.json"
            diagnostic_seconds = None
            if not proof_path.exists():
                diagnostic = trial_dir / "diagnostic_proof"
                diagnostic.mkdir()
                proof_operations = {}
                evaluator.proof(Path(artifacts["v"]["path"]), diagnostic, proof_operations)
                proof_path = diagnostic / "sec" / "receipt.json"
                diagnostic_seconds = proof_operations["SEC"]["wall_seconds"]
            proof = read(proof_path)
            require(proof["gold"] == assets["control"]["v"] and proof["gate"] == artifacts["v"]
                    and proof["passed"] and proof["proven"] > 0 and proof["unproven"] == 0, "re-entry SEC failed")
            spef = spef_without_date(artifacts["spef"]["path"])
            rows[arm] = {
                "first_stage_mode": arm[0], "second_stage_mode": arm[1],
                "retained_input_odb_sha256": before["odb"]["sha256"], "start_geometry": comparison.bind(start_def),
                **{f"{key}_sha256": artifacts[key]["sha256"] for key in ("odb", "def", "v", "drc")},
                "spef_sha256_without_date": spef, "layout": incremental_layout, "views": physical["views"],
                "setup_endpoint_counts": physical["setup_endpoint_counts"], "drc_violations": physical["drc_violations"],
                "failures": logical["failures"], "accepted": endpoint.valid and endpoint.sec_pass,
                "sec": {"proven": proof["proven"], "unproven": proof["unproven"]}, "official_sec": diagnostic_seconds is None,
                "area_saved_original": original_area - endpoint.area, "area_saved_incremental": evaluator.ref_area - endpoint.area,
                "elapsed_raw_seconds": charged_wall, "diagnostic_sec_raw_seconds": diagnostic_seconds,
                "stage_raw_seconds": {key: op["wall_seconds"] for key, op in physical["operations"].items()},
                "original_frozen_cumulative": {
                    "def": artifacts["def"]["sha256"] == direct_artifacts["def"]["sha256"],
                    "v": artifacts["v"]["sha256"] == direct_artifacts["v"]["sha256"],
                    "spef": spef == direct_spef, "views": physical["views"] == direct_physical["views"],
                    "failures": logical["failures"] == direct["failures"],
                },
            }
            if diagnostic_seconds is None:
                rows[arm]["stage_raw_seconds"]["SEC"] = read(logical["deferred_proof_receipt"])["wall_seconds"]
            comparison.save(out / "progress.json", rows)
            print(f"FINISH {arm} {charged_wall:.3f}s {logical['failures'] or 'qualified'}", flush=True)
    check_bindings(config)
    comparison.save(out / "results.json", {
        "rows": rows, "comparisons": {f"{a}_{b}": compare_results(rows[a], rows[b])
                                      for a, b in (("AA", "BA"), ("AB", "BB"), ("AA", "BB"), ("AA", "AB"), ("BA", "BB"))},
        "aa_minus_bb_raw_seconds": rows["AA"]["elapsed_raw_seconds"] - rows["BB"]["elapsed_raw_seconds"],
        "original_frozen_cumulative_failures": direct["failures"], "physical_operations": cache.totals(),
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    run(args.reference.resolve(strict=True), args.output.resolve())


if __name__ == "__main__":
    main()
