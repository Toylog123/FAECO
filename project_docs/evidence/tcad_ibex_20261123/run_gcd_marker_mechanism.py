#!/usr/bin/env python3
"""Compare fixed-proposal ordinary and live-marker protected routing on SKY130HD GCD."""

from argparse import ArgumentParser
import json
import os
from pathlib import Path
import re
from types import SimpleNamespace

from probe_aes_selective_repair import read, verify
from run_aes_cold_online import ColdOnlineComparison, diagnostic_tcl
from run_aes_incident_priority_matched_v2 import CorrectedComparison, comparison, process_ledger
from run_aes_protected_online import LIMIT_SECONDS
from run_screened_matrix import bind_runtime, raw_seconds
import run_setup_budget_sweep as sweep


PROTOCOL_ORDER = ("ordinary", "online", "online", "ordinary")
ZERO_TIMEOUT_SECONDS = 240.0
FIXED_RANKS = (13, 14, 15)


def fixed_proposal(pool):
    if len(pool) != 18 or len({action.action_id for action in pool}) != 18:
        raise ValueError("expected the 18 frozen and distinct GCD candidates")
    return tuple(sorted(pool[rank - 1].action_id for rank in FIXED_RANKS))


def run_fixed_proposal(method, name, reference, evaluate, actions, cap, policy, assess):
    if name != method or cap < 1:
        raise ValueError("expected one fixed-proposal dispatch in this arm")
    endpoint = evaluate(actions)
    accepted = assess(reference, endpoint, policy).feasible and endpoint.area < reference.area - 1e-9
    return {"selected": endpoint if accepted else reference, "trace": [{"accepted": accepted}]}


class GcdMarkerComparison(ColdOnlineComparison):
    def __init__(self, seed, output):
        self.matrix, self.output, self.top = seed, output, "gcd"
        cfg = read(seed / "config.json")
        if (cfg["top"], cfg["pdk"], cfg["route_guide_source"], cfg["single_pin_access"], cfg["route_mode"]) != (
            self.top, "sky130hd", "embedded in frozen CONTROL ODB", True, "local",
        ):
            raise ValueError("expected qualified GCD embedded-guide seed with a single pin access")
        assets = cfg["bindings"]
        self.tools = {key: verify(asset) for key, asset in assets["tools"].items()}
        self.flow = {key: verify(asset) for key, asset in assets["flow"].items()}
        control = {key: verify(asset) for key, asset in assets["control"].items()}
        libraries = {view: [verify(lib) for lib in files] for view, files in assets["used_libraries"].items()}
        original_sdc = verify(assets["original_sdc"])
        qualification = read(verify(assets["qualification_receipt"]))
        reference_file = seed / "control/receipt.json"
        reference = read(reference_file)
        semantics = qualification["source_sdc_semantics"]
        if (qualification["status"] != "hold_qualified" or qualification["detailed_route_drc_count"] != 0
                or reference["status"] != "passed" or qualification["source_sdc"] != assets["original_sdc"]
                or (semantics["period_ps"], semantics["io_delay_ps"], semantics["virtual_latency_ps"]) != (1100.0, 220.0, 290.0)
                or any(view["hold_wns_ps"] < 0 for view in reference["views"].values())):
            raise ValueError("GCD source, timing constraints, or original hold qualification differs")

        screen_path = verify(cfg["screen_inputs"]["pool"])
        screening = read(verify(cfg["screen_inputs"]["receipt"]))
        local_pool = seed / "screened_pool_used.json"
        self.screen = cfg["charged_screening_seconds"]
        if (read(local_pool) != read(screen_path) or screening["wall_seconds"] != self.screen
                or not 0 < self.screen < LIMIT_SECONDS
                or screening["pool_sha256"] != cfg["screen_inputs"]["pool"]["sha256"]
                or any(assets["control"][name]["sha256"] != digest
                       for name, digest in screening["control_sha256"].items())):
            raise ValueError("GCD pool or its common screening charge differs from its bound inputs")
        self.pool = [comparison.PhysicalAction(**row) for row in read(local_pool)]
        self.actions = fixed_proposal(self.pool)
        self.batch, self.target = cfg["batch_size"], cfg["primary_target_area_pct"]
        args = SimpleNamespace(
            pdk="sky130hd", out=output, threads=cfg["methods_route_threads"], clock_period_ps=semantics["period_ps"],
            openroad=self.tools["openroad"], sta=self.tools["opensta"], sec=self.tools["sec"],
            orfs=self.flow["setRC.tcl"].parents[2], route_mode="local", droute_iters=cfg["route_drt_iters"],
            embedded_guides=True, route_guide=None, zero_reextract=False, single_pin_access=True,
            route_timeout=cfg["route_timeout_seconds"], sta_timeout=cfg["sta_timeout_seconds_per_view"],
            sec_timeout=cfg["sec_timeout_seconds"], report_setup_endpoints=True,
        )
        if (args.threads, args.droute_iters, self.batch, self.target, cfg["primary_budget_pct"],
                cfg["primary_wall_limit_seconds"]) != (4, 64, 3, 0.01, 1.0, LIMIT_SECONDS):
            raise ValueError("GCD route, physical gate, or objective budgets changed")
        with bind_runtime(self.top, self.flow["fastroute.tcl"]):
            masters = comparison.logical_masters(control["v"], comparison.liberty_areas(libraries["TT"]))
        self.eval = comparison.Evaluator(args, control, libraries, masters, reference["views"], self.pool,
                                         cfg["scope"] + ":gcd_marker_mechanism")
        self.gate = sweep.budget_gate(self.eval, cfg["primary_budget_pct"], False)
        self.policy = comparison.BudgetPolicy.from_ps(self.gate.wns_ps, tolerance_ns=comparison.PS_TOLERANCE / 1000)
        self.header = "\n".join(re.findall(r"(?m)^(?:VERSION|DIVIDERCHAR|BUSBITCHARS|DESIGN|UNITS) .+?;$",
                                           control["def"].read_text(encoding="utf-8")))
        self.nets = comparison.def_section(control["def"], "NETS")
        if len(self.header.splitlines()) != 5 or any("+ USE CLOCK" not in self.nets.get(net, "")
                                                    for net in ("clk", "clknet_0_clk")):
            raise ValueError("protected-route clock identities or frozen GCD DEF header do not match")
        self.use_preview = False
        self.initial_hint = set()
        sources = {Path(__file__).resolve()}
        for entry in (bind_runtime, comparison.render_route, process_ledger, ColdOnlineComparison.diagnose,
                      ColdOnlineComparison.physical, ColdOnlineComparison.direct_nets, CorrectedComparison.arm):
            sources.add(Path(entry.__code__.co_filename).resolve())
        for name in ("run_aes_incident_priority_matched.py", "compare_ibex.py", "probe_aes_selective_repair.py",
                     "run_setup_budget_sweep.py", "audit_aes_unlocked_drc.py"):
            sources.add(Path(__file__).resolve().with_name(name))
        self.config = {"seed": comparison.bind(seed / "config.json"), "reference": comparison.bind(reference_file),
                       "original_sdc": comparison.bind(original_sdc), "pool": comparison.bind(local_pool),
                       "screen_inputs": cfg["screen_inputs"], "charged_screening_seconds": self.screen,
                       "protocol_order": PROTOCOL_ORDER, "fixed_ranks": FIXED_RANKS, "fixed_actions": self.actions,
                       "clock": "CLOCK_MONOTONIC_RAW", "wall_budget_seconds_including_screen": LIMIT_SECONDS,
                       "outer_zero_timeout_seconds": ZERO_TIMEOUT_SECONDS, "maximum_logical_requests_per_cell": 1,
                       "area_target_pct": self.target, "gate": sweep.gate_summary(self.gate, self.eval.ref_views),
                       "route_threads": args.threads, "diagnostic_threads": 1, "single_pin_access": True,
                       "affinity": sorted(os.sched_getaffinity(0)), "physical_cache": "disabled",
                       "sources": {path.name: comparison.bind(path) for path in sorted(sources)}}

    def static_check(self):
        edited, incident = self.direct_nets(self.actions)
        _, edits = self.eval.expected_masters(self.actions)
        base_tcl = comparison.render_route(self.eval.args, self.eval.libraries["TT"], self.eval.control, self.output, edits)
        preview = diagnostic_tcl(base_tcl, self.output / "full_drc.rpt")
        if (not incident or any("+ ROUTED " not in self.nets[net] for net in incident)
                or 'if {![grt::have_routes]}' not in base_tcl or "-droute_end_iter 64" not in base_tcl
                or "detailed_route " in preview or "drt::check_drc" not in preview):
            raise ValueError("the direct-net scope, guide, or live diagnostic boundary differs")
        return {"edited_instances": sorted(edited), "incident_nets": sorted(incident),
                "frozen_wired_nets": len(self.nets), "programs_launched": 0}

    def qualify_zero(self):
        location = self.output / "preflight"
        location.mkdir()
        with process_ledger(location / "subprocesses.json", raw_seconds() + ZERO_TIMEOUT_SECONDS):
            reference, trial = self.attempt((), location / "zero")
        if not reference.valid or not reference.sec_pass:
            raise comparison.TrialFailure(f"GCD protected zero failed: {trial['failures']}")
        return reference

    def run_cell(self, method, reference, output):
        self.output, self.use_preview = output, method == "online"
        original = comparison.run_method

        def dispatch(name, ref, _pool, evaluate, cap, _batch, *, policy, **_kwargs):
            return run_fixed_proposal(method, name, ref, evaluate, self.actions, cap, policy, comparison.assess)

        try:
            comparison.run_method = dispatch
            return CorrectedComparison.arm(self, method, reference)
        finally:
            comparison.run_method = original
            self.use_preview = False


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("seed", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--check-inputs", action="store_true", help="hash and inspect frozen inputs without launching EDA")
    args = parser.parse_args()
    seed, output = args.seed.resolve(strict=True), args.output.resolve()
    runner = GcdMarkerComparison(seed, output)
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        checked = runner.static_check()
        if args.check_inputs:
            print(json.dumps({"setup": runner.config["gate"], "actions": checked}, indent=2))
            return
        output.mkdir(parents=True)
        comparison.save(output / "protocol.json", runner.config | {"static_check": checked})
        reference = runner.qualify_zero()
        results = []
        for index, method in enumerate(PROTOCOL_ORDER, 1):
            cell = output / f"cell_{index:02d}"
            cell.mkdir()
            outer_start = raw_seconds()
            result = runner.run_cell(method, reference, cell)
            results.append({"cell": index, "method": method, "outer_start_raw": outer_start,
                            "outer_stop_raw": raw_seconds(), "result": result})
            comparison.save(output / "results.json", results)
            print(f"GCD cell {index} {method}: area={result['window']['area_saved']}", flush=True)


if __name__ == "__main__":
    main()
