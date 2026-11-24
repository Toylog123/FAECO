#!/usr/bin/env python3
"""Transfer the protected online recovery backend to qualified ASAP7 UART."""

from dataclasses import asdict
import os
from pathlib import Path
import re
import sys
from types import SimpleNamespace


IBEX = Path(__file__).resolve().parents[1] / "tcad_ibex_20261123"
sys.path.insert(0, str(IBEX))

import compare_ibex as comparison
import run_setup_budget_sweep as sweep
from probe_aes_selective_repair import read, verify
from run_aes_cold_online import ColdOnlineComparison
from run_aes_greedy_matched import run_online_arm
from run_aes_incident_priority_matched_v2 import process_ledger
from run_aes_protected_online import LIMIT_SECONDS, MAX_REQUESTS
from run_screened_matrix import bind_runtime, bind_screen_inputs, raw_seconds, screened_actions
from setup_budget import original_period_ps


ORDER = ("single", "fixed_online", "faeco", "faeco", "fixed_online", "single")


class UartComparison(ColdOnlineComparison):
    def __init__(self, args, seed, output, screen_bindings, screen_seconds):
        cfg = read(seed / "config.json")
        assets = cfg["bindings"]
        self.matrix, self.output = seed, output
        self.top = "uart"
        if (cfg["top"], cfg["pdk"], cfg["route_guide_source"]) != (
            self.top, "asap7", "embedded in frozen CONTROL ODB",
        ):
            raise ValueError("expected the qualified UART embedded-guide seed")
        self.tools = {name: verify(item) for name, item in assets["tools"].items()}
        self.flow = {name: verify(item) for name, item in assets["flow"].items()}
        control = {name: verify(item) for name, item in assets["control"].items()}
        libraries = {corner: [verify(item) for item in group] for corner, group in assets["used_libraries"].items()}
        ref = read(seed / "control/receipt.json")
        if ref["status"] != "passed":
            raise ValueError("fresh UART seed validation failed")
        masters = comparison.logical_masters(control["v"], comparison.liberty_areas(libraries["TT"]))
        seed_args = SimpleNamespace(**(vars(args) | {"out": seed}))
        evaluator = comparison.Evaluator(seed_args, control, libraries, masters, ref["views"], (), cfg["scope"])
        self.pool = screened_actions(seed_args, evaluator)
        if not 0 < screen_seconds < LIMIT_SECONDS:
            raise ValueError("UART screening cost leaves no comparison budget")
        runtime_args = SimpleNamespace(**(vars(args) | {"out": output}))
        self.eval = comparison.Evaluator(runtime_args, control, libraries, masters, ref["views"], self.pool, cfg["scope"])
        self.gate = sweep.budget_gate(self.eval, 1.0, False)
        self.policy = comparison.BudgetPolicy.from_ps(self.gate.wns_ps,
                                                       tolerance_ns=comparison.PS_TOLERANCE / 1000)
        self.header = "\n".join(re.findall(r"(?m)^(?:VERSION|DIVIDERCHAR|BUSBITCHARS|DESIGN|UNITS) .+?;$",
                                           control["def"].read_text(encoding="utf-8")))
        if len(self.header.splitlines()) != 5:
            raise ValueError("unexpected UART DEF header")
        self.nets = comparison.def_section(control["def"], "NETS")
        self.screen, self.target, self.batch = screen_seconds, 0.01, args.batch_size
        self.use_preview = False
        self.initial_hint = set()
        self.config = {
            "seed": comparison.bind(seed / "config.json"), "reference": comparison.bind(seed / "control/receipt.json"),
            "screen_input": screen_bindings, "charged_screening_seconds_per_arm": self.screen,
            "ordered_pool": [asdict(action) for action in self.pool], "order": ORDER,
            "wall_window_seconds_including_screen": LIMIT_SECONDS, "logical_dispatch_cap": MAX_REQUESTS,
            "area_target_pct": self.target, "batch_size": self.batch, "clock": "CLOCK_MONOTONIC_RAW",
            "gate": sweep.gate_summary(self.gate, self.eval.ref_views), "absolute_hold_ps": 0.0,
            "hold_tolerance_ps": comparison.PS_TOLERANCE, "route_threads": args.threads,
            "affinity": sorted(os.sched_getaffinity(0)), "single_pin_access": args.single_pin_access,
            "diagnostic": "candidate-specific live DRC on a copy of the frozen ROUTED CONTROL; all arms",
            "endpoint_checks": "DRT, RCX, all three STA views, protected geometry, independent DRC, antenna, SEC",
            "sources": {path.name: comparison.bind(path) for path in (
                Path(__file__).resolve(), Path(ColdOnlineComparison.diagnose.__code__.co_filename),
                Path(ColdOnlineComparison.physical.__code__.co_filename),
                Path(ColdOnlineComparison.direct_nets.__code__.co_filename),
                IBEX / "run_aes_incident_priority_matched.py", IBEX / "run_aes_greedy_matched.py",
                Path(process_ledger.__code__.co_filename), Path(__file__).with_name("holdout_tools.py"),
                IBEX / "probe_aes_selective_repair.py", IBEX / "audit_aes_unlocked_drc.py", IBEX / "prove_ibex.py",
            )},
        }
        comparison.save(output / "protocol.json", self.config)

    def qualify_zero(self):
        target = self.output / "preflight"
        target.mkdir()
        with process_ledger(target / "subprocesses.json", raw_seconds() + 450):
            reference, row = self.attempt((), target / "zero")
        if not reference.valid or not reference.sec_pass:
            raise comparison.TrialFailure(f"UART frozen zero did not qualify: {row['failures']}")
        print("UART strict zero passed", flush=True)
        return reference


def main():
    parser = comparison.create_parser(__doc__)
    parser.add_argument("--screen-pool", type=Path, required=True)
    parser.add_argument("--screen-receipt", type=Path, required=True)
    parser.add_argument("--zero-only", action="store_true")
    args = comparison.prepare_args(parser, parser.parse_args())
    if args.pdk != "asap7" or not args.embedded_guides or (args.max_evals, args.batch_size) != (MAX_REQUESTS, 3):
        parser.error("UART protocol requires ASAP7, embedded guides, six requests and batches of three")
    args.prepare_only = True
    args.single_pin_access = True
    args.report_setup_endpoints = True
    args.clock_period_ps = original_period_ps(read(args.views_json), args.original_sdc)
    args.screen_pool = args.screen_pool.resolve(strict=True)
    args.screen_receipt = args.screen_receipt.resolve(strict=True)
    bindings, seconds = bind_screen_inputs(SimpleNamespace(**vars(args), top="uart"))
    output = args.out
    output.mkdir(parents=True)
    args.out = seed = output / "seed"
    with bind_runtime("uart", comparison.fastroute(args)):
        if comparison.run(args, extra_sources=(Path(__file__).resolve(),)):
            return 2
        runner = UartComparison(args, seed, output, bindings, seconds)
        reference = runner.qualify_zero()
        if args.zero_only:
            return 0
        outcomes = []
        for order_index, method in enumerate(ORDER, 1):
            runner.output = output / f"cell_{order_index:02d}"
            runner.output.mkdir()
            print(f"UART cell {order_index}: {method}", flush=True)
            summary = (run_online_arm(runner, method, reference) if method == "single"
                       else runner.arm(method, reference))
            outcomes.append({"cell": order_index, "method": method, "result": summary})
            comparison.save(output / "results.json", outcomes)
            print(summary["window"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
