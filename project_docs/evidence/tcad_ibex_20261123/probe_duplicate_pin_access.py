#!/usr/bin/env python3
"""Pair fresh, same-tuple evaluations with one or two embedded-guide pin-access passes."""

import hashlib
import os
from pathlib import Path
import re
import sys
from unittest.mock import patch

import compare_ibex as comparison
import run_setup_budget_sweep as sweep
from run_screened_matrix import CLOCK_NAME, bind_runtime, raw_seconds, read, screened_actions


ORDER = ("explicit", "automatic", "automatic", "explicit")
CASES = {"gcd": ("gcd", 5, (13, 14, 15)), "ibex_core": ("ibex", 3, (7, 8, 9))}


def require(condition, message):
    if not condition:
        raise comparison.TrialFailure(message)


def spef_without_date(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for line in stream:
            if not line.startswith(b"*DATE "):
                digest.update(line)
    return digest.hexdigest()


def route_deck(path, automatic, base_renderer):
    def render(args, libraries, control, out, actions):
        require(args.embedded_guides and actions and out == path, "unexpected routing evaluation")
        deck = base_renderer(args, libraries, control, out, actions)
        marker = '\npin_access\nif {![grt::have_routes]}'
        require(deck.count(marker) == 1, "expected exactly one explicit pre-DRT pin_access")
        return deck.replace(marker, '\nif {![grt::have_routes]}', 1) if automatic else deck

    return render


def run_trials(args, evaluator, reference, historical, matrix, selected, actions):
    evaluator.actions = {action.action_id: action for action in actions}
    rank_tuple = tuple(sorted(actions[rank - 1].action_id for rank in CASES[matrix["top"]][2]))
    require(selected["actions"] == list(rank_tuple), "frozen qualified tuple disagrees with planned ranks")
    gate = sweep.budget_gate(evaluator, matrix["primary_budget_pct"], False)
    gate_record = sweep.gate_summary(gate, evaluator.ref_views)
    require(gate_record == historical["gate"], "historical timing gates have changed")
    original = Path(selected["physical_receipt"])
    recorded = read(original)
    original_artifacts = recorded["artifacts"]
    original_spef = spef_without_date(original_artifacts["spef"]["path"])
    original_layout = read(original.parent / "layout_changes.json")
    original_proof = read(original.parent / "sec" / "receipt.json")
    renderer = comparison.render_route
    trials = sweep.TrialCache(evaluator)
    rows = []
    canonical_deck = None
    for seq, mode in enumerate(ORDER, 1):
        path = args.out / f"{seq:02d}_{mode}"
        print(f"START {mode} {seq}/{len(ORDER)} {path}", flush=True)
        start = raw_seconds()
        with patch.object(comparison, "render_route", route_deck(path, mode == "automatic", renderer)):
            endpoint, logical = trials.request(rank_tuple, gate, fresh_directory=path)
        elapsed = raw_seconds() - start
        physical = read(path / "receipt.json")
        deck = (path / "route.tcl").read_text().replace(str(path), "<trial>")
        if seq == 1:
            canonical_deck = deck
        expected_deck = canonical_deck if mode == "explicit" else canonical_deck.replace("\npin_access\n", "\n", 1)
        require(deck == expected_deck, "candidate Tcl changes more than the planned pin_access line")
        comparison.save(path / "logical.json", logical)
        stages = physical["operations"]
        route_log = (path / "route.log").read_text()
        stage_proof = read(Path(logical["deferred_proof_receipt"])) if logical["deferred_proof_receipt"] else None
        proof_path = path / "sec" / "receipt.json"
        proof = read(proof_path) if proof_path.exists() else None
        if proof and endpoint.sec_pass:
            require(proof["proven"] > 0 and proof["unproven"] == 0, "functional proof is empty or unresolved")
            require(proof["gold"] == matrix["bindings"]["control"]["v"], "functional proof gold changed")
            require(proof["gate"] == physical["artifacts"]["v"], "functional proof gate changed")
        artifacts = physical.get("artifacts", {})
        matches = {kind: artifacts.get(kind, {}).get("sha256") == original_artifacts[kind]["sha256"]
                   for kind in ("odb", "def", "v", "drc")}
        matches["spef_without_date"] = bool(artifacts) and spef_without_date(artifacts["spef"]["path"]) == original_spef
        matches["sta_views"] = physical["views"] == recorded["views"]
        matches["layout_changes"] = bool(artifacts) and read(path / "layout_changes.json") == original_layout
        matches["sec_points"] = bool(proof and proof["passed"]) and (proof["proven"], proof["unproven"]) == (
            original_proof["proven"], original_proof["unproven"])
        passes = len(re.findall(r"(?m)^\[INFO DRT-0165\] Start pin access\.$", route_log))
        row = {
            "mode": mode, "receipt": comparison.bind(path / "logical.json"),
            "physical_receipt": comparison.bind(path / "receipt.json"),
            "matches_historical": matches, "accepted": endpoint.valid and endpoint.sec_pass,
            "actual_pin_access_passes": passes, "expected_pin_access_passes": 2 if mode == "explicit" else 1,
            "area_saved": reference.area - endpoint.area,
            "search_raw_seconds": elapsed,
            "stage_raw_seconds": {**{key: value["wall_seconds"] for key, value in stages.items()},
                                  **({"SEC": stage_proof["wall_seconds"]} if stage_proof else {})},
        }
        rows.append(row)
        comparison.save(args.out / "progress.json", rows)
        print(f"FINISH {mode} {seq}/{len(ORDER)} {elapsed:.3f}s matches={matches}", flush=True)
    paired = [
        {"order": [a["mode"], b["mode"]],
         "explicit_minus_automatic_raw_seconds": (a["search_raw_seconds"] - b["search_raw_seconds"])
         * (1 if a["mode"] == "explicit" else -1)}
        for a, b in (rows[:2], rows[2:])
    ]
    return True, {
        "gate": gate_record, "trials": rows, "paired_observations": paired,
        "all_same_qualified_endpoints": all(r["accepted"] and all(r["matches_historical"].values())
                                            and r["actual_pin_access_passes"] == r["expected_pin_access_passes"]
                                            for r in rows),
        "operations": trials.totals(),
    }


def main():
    parser = comparison.create_parser(description=__doc__)
    parser.add_argument("--matrix", required=True, type=Path, help="fresh hold-aware reference directory")
    args = comparison.prepare_args(parser, parser.parse_args())
    try:
        matrix_dir = args.matrix.resolve(strict=True)
        matrix, historical = read(matrix_dir / "config.json"), read(matrix_dir / "results.json")
        require(matrix["top"] in CASES and historical["status"] == "matched", "invalid reference matrix")
        require(args.pdk == matrix["pdk"] == "sky130hd" and args.embedded_guides and args.zero_reextract
                and not args.prepare_only and not args.probe_only, "requires embedded-guide fresh candidate DRT")
        fields = ("threads", "route_mode", "droute_iters", "route_timeout", "sta_timeout", "sec_timeout",
                  "report_setup_endpoints")
        keys = ("methods_route_threads", "route_mode", "route_drt_iters", "route_timeout_seconds",
                "sta_timeout_seconds_per_view", "sec_timeout_seconds", "report_setup_endpoints")
        require(tuple(getattr(args, f) for f in fields) == tuple(matrix[k] for k in keys),
                "physical evaluator settings differ from the reference")
        design, slot, _ = CASES[matrix["top"]]
        routing = (args.orfs / "platforms/sky130hd/fastroute.tcl" if design == "gcd"
                   else args.orfs / f"designs/sky130hd/{design}/fastroute.tcl").resolve(strict=True)
        bindings = matrix["bindings"]
        for binding, path in (
            (bindings["qualification_receipt"], args.views_json), (bindings["original_sdc"], args.original_sdc),
            (bindings["control_drc"], args.control_drc), (bindings["tools"]["openroad"], args.openroad),
            (bindings["tools"]["opensta"], args.sta), (bindings["tools"]["sec"], args.sec),
            (bindings["flow"][routing.name], routing),
            *((item, args.control_dir / f"6_final.{ext}") for ext, item in bindings["control"].items()),
        ):
            require(comparison.bind(path) == binding, f"input differs from reference: {path}")
        source_path = matrix_dir / "screened" / "faeco" / f"{slot:02d}.json"
        selected = read(source_path)
        require(selected["endpoint"]["sec_pass"] and not selected["failures"], "reference tuple must be qualified")
        args.screen_pool = Path(matrix["screen_inputs"]["pool"]["path"])
        args.clock_period_ps = matrix["original_clock_period_ps"]
        original_path = Path(selected["physical_receipt"])
        input_paths = [
            matrix_dir / "config.json", matrix_dir / "results.json", source_path, original_path,
            original_path.parent / "layout_changes.json", original_path.parent / "sec" / "receipt.json",
            original_path.parent / "routed.spef", args.screen_pool,
        ]
        recorded_inputs = [comparison.bind(p) for p in input_paths]
        require(recorded_inputs[-1] == matrix["screen_inputs"]["pool"], "frozen candidate pool changed")
        source_dependencies = [Path(x["path"]) for x in bindings["driver_source"].values()]

        def matched(run_args, evaluator, reference, _legacy_pool, baseline, _noop):
            fresh_bindings = read(args.out / "config.json")["bindings"]
            for key in ("control", "original_sdc", "control_drc", "qualification_receipt",
                        "source_libraries", "flow", "tools"):
                require(fresh_bindings[key] == bindings[key], f"historical {key} binding changed")
            for corner in comparison.CORNERS:
                historical_libraries = bindings["used_libraries"][corner]
                fresh_libraries = fresh_bindings["used_libraries"][corner]
                require([x["sha256"] for x in fresh_libraries] == [x["sha256"] for x in historical_libraries],
                        f"staged library content changed in {corner}")
            require(baseline["views"] == historical["control"]["views"], "fresh CONTROL timing changed")
            result = run_trials(run_args, evaluator, reference, historical, matrix, selected,
                                screened_actions(run_args, evaluator))
            require([comparison.bind(p) for p in input_paths] == recorded_inputs, "reference inputs changed")
            return result

        sources = tuple(dict.fromkeys([Path(__file__).resolve(), *source_dependencies]))
        with bind_runtime(matrix["top"], routing):
            return comparison.run(args, matched_runner=matched, config_overrides={
                "clock": CLOCK_NAME, "cpu_affinity": sorted(os.sched_getaffinity(0)),
                "reference_bindings": recorded_inputs, "trial_order": ORDER,
                "primary_budget_pct": matrix["primary_budget_pct"], "original_clock_period_ps": args.clock_period_ps,
                "methods_in_run_order": ORDER, "tns_gate": True,
            }, extra_sources=sources)
    except (comparison.TrialFailure, OSError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
