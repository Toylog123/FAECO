#!/usr/bin/env python3
"""Use an independently qualified holdout in the four-arm wall-clock matrix."""

from dataclasses import asdict
from contextlib import contextmanager
import math
import os
from pathlib import Path
import re
from types import SimpleNamespace

import run_wallclock_matrix as matrix
from run_wallclock_matrix import comparison, read, verify
from run_aes_cold_online import ColdOnlineComparison
from run_aes_incident_priority_matched_v2 import process_ledger
import run_setup_budget_sweep as sweep
from run_screened_matrix import bind_runtime, bind_screen_inputs, raw_seconds, screened_actions
import screen_sky130_candidates as screening


CONFIRMED_STRATEGIES = ("fixed_online", "single_sensitivity", "faeco_dedup")


@contextmanager
def strategy_scope(confirmed_only):
    original = matrix.FORWARD
    if confirmed_only:
        matrix.FORWARD = CONFIRMED_STRATEGIES
    try:
        yield
    finally:
        matrix.FORWARD = original


def budget_basis(semantics, saved_sdc, preregistered_ps):
    units = {"ns": 1000.0, "ps": 1.0}
    multiplier = units.get(semantics.get("sdc_time_unit"))
    if multiplier is None:
        raise ValueError("qualification did not bind the exported SDC time unit")
    if re.search(r"(?m)^create_generated_clock\b", saved_sdc):
        raise ValueError("budget selection needs an explicit generated-clock policy")
    clocks = {}
    for line in saved_sdc.splitlines():
        if not line.startswith("create_clock ") or "[get_ports " not in line:
            continue
        name = re.search(r"-name\s+\{?(\S+?)\}?\s", line)
        period = re.search(rf"-period\s+({comparison.NUMBER})(?=\s|$)", line)
        if name is None or period is None or name[1] in clocks:
            raise ValueError(f"ambiguous physical clock in qualified CONTROL SDC: {line}")
        clocks[name[1]] = float(period[1]) * multiplier
    if not clocks or any(not math.isfinite(value) or value <= 0 for value in clocks.values()):
        raise ValueError("qualified CONTROL SDC does not identify positive real-clock periods")
    smallest = min(clocks.values())
    if len(clocks) == 1:
        if not math.isclose(semantics["period_ps"], smallest, rel_tol=0, abs_tol=1e-6):
            raise ValueError("source-qualification period changed in the saved CONTROL SDC")
    else:
        if preregistered_ps is None:
            raise ValueError("multiple real clocks require an explicit preregistered shortest-clock budget")
        pinned_clocks = semantics.get("clock_periods_ps", {})
        if pinned_clocks.keys() != clocks.keys() or any(
            not math.isclose(period, pinned_clocks[name], rel_tol=0, abs_tol=1e-6)
            for name, period in clocks.items()
        ):
            raise ValueError("multiclock source qualification differs from saved physical clocks")
    if preregistered_ps is not None and not math.isclose(preregistered_ps, smallest, rel_tol=0, abs_tol=1e-6):
        raise ValueError("preregistered period differs from the shortest real CONTROL clock")
    return {"real_clock_periods_ps": clocks, "period_ps": smallest, "target_setup_budget_pct": 1.0,
            "absolute_wns_loss_budget_ps": sweep.policy.setup_budget_ps(smallest, 1.0)}


def prepare_binding(args):
    qualified = read(args.views_json)
    control = {ext: args.control_dir / f"6_final.{ext}" for ext in comparison.CONTROL_FILES}
    libraries = comparison.load_views(qualified)
    assets = {
        "control": {kind: comparison.bind(path) for kind, path in control.items()},
        "control_drc": comparison.bind(args.control_drc),
        "original_sdc": comparison.bind(args.original_sdc),
        "qualification_receipt": comparison.bind(args.views_json),
        "source_libraries": {corner: [comparison.bind(path) for path in paths] for corner, paths in libraries.items()},
        "tools": {"openroad": comparison.bind(args.openroad), "opensta": comparison.bind(args.sta),
                  "sec": comparison.bind(args.sec)},
        "routing_config": comparison.bind(args.routing_config),
        "helper_sources": [comparison.bind(path) for path in args.helper_source],
    }
    if any(not data["bytes"] for data in assets["control"].values()) or args.control_drc.read_text().strip():
        raise ValueError("qualification requires nonempty CONTROL and an empty DRT report")
    saved = control["sdc"].read_text(encoding="utf-8")
    if not re.search(r"(?m)^set_propagated_clock\b", saved):
        raise ValueError("qualified CONTROL SDC does not propagate the routed clock")
    comparison.qualify_binding(qualified, assets)
    declared_top = qualified.get("top", args.top)
    if declared_top != args.top:
        raise ValueError("requested design top disagrees with P0 qualification")
    exported = control["v"].read_text(encoding="utf-8")
    if not re.search(rf"(?m)^module\s+{re.escape(args.top)}\s+\(", exported):
        raise ValueError("requested top is absent from the qualified routed netlist")
    clock = budget_basis(qualified["source_sdc_semantics"], saved, args.shortest_clock_period_ps)
    return qualified, assets, clock


def run_qualified_screen(args, qualified, output):
    screen_args = SimpleNamespace(**(vars(args) | {"out": output / "screen", "pilot": False}))
    with bind_runtime(args.top, args.routing_config):
        return screening.run_screen(screen_args, qualified)


class QualifiedWallclockComparison(ColdOnlineComparison):
    """Bind the generic prepared seed to the existing protected online backend."""

    def __init__(self, args, seed, output, screen_bindings, screen_seconds):
        cfg = read(seed / "config.json")
        assets = cfg["bindings"]
        self.matrix, self.output, self.top = seed, output, args.top
        if (cfg["top"], cfg["pdk"], cfg["route_guide_source"]) != (
            self.top, args.pdk, "embedded in frozen CONTROL ODB",
        ):
            raise ValueError("seed must use the qualified holdout with embedded guides")
        self.tools = {key: verify(value) for key, value in assets["tools"].items()}
        self.flow = {key: verify(value) for key, value in assets["flow"].items()}
        control = {key: verify(value) for key, value in assets["control"].items()}
        libraries = {corner: [verify(value) for value in inputs] for corner, inputs in assets["used_libraries"].items()}
        reference = seed / "control/receipt.json"
        baseline = read(reference)
        if baseline["status"] != "passed":
            raise ValueError("qualified holdout did not pass fresh seed validation")
        masters = comparison.logical_masters(control["v"], comparison.liberty_areas(libraries["TT"]))
        seed_args = SimpleNamespace(**(vars(args) | {"out": seed}))
        evaluator = comparison.Evaluator(seed_args, control, libraries, masters, baseline["views"], (), cfg["scope"])
        self.pool = screened_actions(seed_args, evaluator)
        runtime = SimpleNamespace(**(vars(args) | {"out": output}))
        self.eval = comparison.Evaluator(runtime, control, libraries, masters, baseline["views"], self.pool, cfg["scope"])
        self.gate = sweep.budget_gate(self.eval, 1.0, False)
        self.policy = comparison.BudgetPolicy.from_ps(self.gate.wns_ps, tolerance_ns=comparison.PS_TOLERANCE / 1000)
        text = control["def"].read_text(encoding="utf-8")
        self.header = "\n".join(re.findall(r"(?m)^(?:VERSION|DIVIDERCHAR|BUSBITCHARS|DESIGN|UNITS) .+?;$", text))
        if len(self.header.splitlines()) != 5:
            raise ValueError("unexpected CONTROL DEF header")
        self.nets = comparison.def_section(control["def"], "NETS")
        self.screen, self.target, self.batch = screen_seconds, matrix.TARGETS_PCT[0], args.batch_size
        self.use_preview = False
        self.initial_hint = set()
        self.config = {
            "top": self.top, "pdk": args.pdk, "seed": comparison.bind(seed / "config.json"),
            "reference": comparison.bind(reference), "qualified_start": assets["qualification_receipt"],
            "screen_input": screen_bindings, "charged_screening_seconds_per_arm": screen_seconds,
            "ordered_pool": [asdict(item) for item in self.pool], "batch_size": self.batch,
            "area_target_pct": self.target, "clock": "CLOCK_MONOTONIC_RAW",
            "gate": sweep.gate_summary(self.gate, self.eval.ref_views), "absolute_hold_ps": 0.0,
            "hold_tolerance_ps": comparison.PS_TOLERANCE, "route_threads": args.threads,
            "affinity": sorted(os.sched_getaffinity(0)), "single_pin_access": args.single_pin_access,
            "endpoint_checks": "DRT, RCX, FF/TT/SS STA, protected geometry, independent whole-block DRC, antenna, SEC",
            "sources": {path.name: comparison.bind(path) for path in (
                Path(__file__).resolve(), *args.helper_source,
                *(matrix.EVIDENCE / "tcad_ibex_20261123" / filename for filename in (
                    "audit_aes_unlocked_drc.py", "probe_aes_selective_repair.py", "prove_ibex.py", "setup_budget.py",
                )),
                *(Path(method.__code__.co_filename) for method in (
                    self.qualify_zero, self.attempt, self.diagnose, self.physical, self.direct_nets,
                    sweep.budget_gate, process_ledger,
                )),
            )},
        }
        matrix.sensitivity.render_rank_tcl(self.eval.libraries["TT"], self.eval.control, self.pool)

    def qualify_zero(self):
        target = self.output / "preflight"
        target.mkdir()
        with process_ledger(target / "subprocesses.json", raw_seconds() + 450):
            reference, record = self.attempt((), target / "zero")
        if not reference.valid or not reference.sec_pass:
            raise comparison.TrialFailure(f"{self.top} frozen zero did not qualify: {record['failures']}")
        print(f"{self.top} strict zero passed", flush=True)
        return reference


def main():
    parser = comparison.create_parser(__doc__)
    parser.set_defaults(embedded_guides=True, max_evals=1, route_timeout=240.0, sec_timeout=210.0)
    parser.add_argument("--top", required=True)
    parser.add_argument("--routing-config", type=Path, help="native design or platform FastRoute Tcl")
    parser.add_argument("--shortest-clock-period-ps", type=float, help="preregistered minimum physical clock for multiclock")
    parser.add_argument("--helper-source", action="append", type=Path, default=[])
    parser.add_argument("--screen-pool", type=Path)
    parser.add_argument("--screen-receipt", type=Path)
    parser.add_argument("--screen-only", action="store_true", help="build the screened pool from qualified frozen SPEF")
    parser.add_argument("--screen-workers", type=int, default=1, help="parallel single-thread frozen-SPEF probes")
    parser.add_argument("--confirmed-only", action="store_true",
                        help="holdout compares fixed, sensitivity-single and current dedup in both orders")
    parser.add_argument("--validate-only", action="store_true", help="validate the qualifications and screen pins without tools")
    args = comparison.prepare_args(parser, parser.parse_args())
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", args.top):
        parser.error("top must be a Verilog identifier")
    if args.max_evals != 1 or args.batch_size != 3 or args.zero_reextract:
        parser.error("expected the uncapped protocol, width three, and a fresh shared DRT zero")
    if args.validate_only and (args.prepare_only or args.probe_only):
        parser.error("validate-only cannot be combined with tool-based preflight modes")
    if args.screen_workers < 1:
        parser.error("screen-workers must be positive")
    if args.screen_only:
        if any((args.screen_pool, args.screen_receipt, args.prepare_only, args.probe_only)):
            parser.error("screen-only takes qualified sources and produces its own pool and receipt")
    elif not args.screen_pool or not args.screen_receipt:
        parser.error("matrix and its validation phases need an existing pool and screening receipt")
    # The existing UART backend also uses one internal DRT pin access on ASAP7.
    args.single_pin_access = args.report_setup_endpoints = True
    args.routing_config = (args.routing_config or args.orfs / "platforms" / args.pdk / "fastroute.tcl").resolve(strict=True)
    if not args.screen_only:
        args.screen_pool = args.screen_pool.resolve(strict=True)
        args.screen_receipt = args.screen_receipt.resolve(strict=True)
    args.helper_source = [path.resolve(strict=True) for path in args.helper_source]
    output = args.out
    output.mkdir(parents=True)
    state = output / "status.json"
    try:
        qualified, assets, clock = prepare_binding(args)
        args.clock_period_ps = clock["period_ps"]
        bindings, seconds = ({}, None) if args.screen_only else bind_screen_inputs(args)
        if not args.screen_only and not 0 < seconds < matrix.LIMIT_SECONDS:
            raise ValueError("the qualified screening receipt consumes the wall window")
        with strategy_scope(args.confirmed_only):
            planned_order = matrix.ordering()
        comparison.save(output / "qualified_inputs.json", {
            "top": args.top, "pdk": args.pdk, "source": assets, "period_basis": clock,
            "screen_input": bindings, "charged_screening_seconds_per_arm": seconds,
            "driver": comparison.bind(Path(__file__)),
            "screening_source": comparison.bind(Path(screening.__file__)),
            "screen_workers": args.screen_workers if args.screen_only else None,
            "strategy_order": planned_order, "confirmed_only": args.confirmed_only,
        })
        if args.validate_only:
            comparison.save(state, {"status": "protocol_and_inputs_validated", "completed_arms": 0})
            return 0
        if args.screen_only:
            if run_qualified_screen(args, qualified, output):
                raise ValueError("qualified screening backend did not produce an eligible pool")
            comparison.save(state, {
                "status": "screened", "completed_arms": 0,
                "pool": comparison.bind(output / "screen/screen_pool.json"),
                "receipt": comparison.bind(output / "screen/screen_receipt.json"),
            })
            return 0
        seed_args = SimpleNamespace(**(vars(args) | {"out": output / "seed", "prepare_only": True, "probe_only": False}))
        with bind_runtime(args.top, args.routing_config), strategy_scope(args.confirmed_only):
            if comparison.run(seed_args, config_overrides={
                "budget_attempts_per_arm": None, "original_clock_period_ps": args.clock_period_ps,
                "setup_budget_ps_per_view": clock["absolute_wns_loss_budget_ps"], "tns_gate": True,
                "screen_inputs": bindings, "charged_screening_seconds": seconds,
            }, extra_sources=(Path(__file__).resolve(), *args.helper_source)):
                raise ValueError("frozen holdout failed seed validation")
            runner = QualifiedWallclockComparison(args, seed_args.out, output, bindings, seconds)
            runner.config["period_basis"] = clock
            runner.config["confirmed_only"] = args.confirmed_only
            matrix.preregister(runner, args.views_json, output)
            if args.prepare_only:
                comparison.save(state, {"status": "seed_validated", "completed_arms": 0})
                return 0
            reference = runner.qualify_zero()
            if args.probe_only:
                comparison.save(state, {"status": "shared_zero_qualified", "completed_arms": 0})
                return 0
            matrix.run_matrix(runner, reference, output, runner.config)
    except Exception as error:
        prior = read(state) if state.exists() else {}
        comparison.save(state, {**prior, "status": "failed", "error": str(error), "stop_raw": raw_seconds()})
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
