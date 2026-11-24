#!/usr/bin/env python3
"""Evaluate screened AES online with the same protected routing in each arm."""

from argparse import ArgumentParser
from contextlib import contextmanager
from dataclasses import asdict, replace
from pathlib import Path
from types import SimpleNamespace
import math
import os
import re

import compare_ibex as comparison
import run_setup_budget_sweep as sweep
from audit_aes_unlocked_drc import audit
from probe_aes_selective_repair import audit_routing, audit_timing, read, selective_route, verify
from run_holdout_screened import expected_holdout_sdc
from run_screened_matrix import CLOCK_NAME, RELATIVE_HOLD_REASONS, bind_runtime, raw_seconds


METHODS = ("single", "fixed", "faeco")
LIMIT_SECONDS = 720.0
MAX_REQUESTS = 6
PROTECT_PA = r"(?m)^\[INFO DRT-0165\] Start pin access\."


class WallWindowEnded(Exception):
    """The next complete evaluation cannot be admitted inside the wall window."""


@contextmanager
def process_ledger(path, deadline):
    source = comparison.run_process
    rows = []

    def invoke(argv, logfile, timeout, *, env=None):
        start = raw_seconds()
        remaining = deadline - start
        if remaining <= 0:
            raise WallWindowEnded()
        effective = min(timeout, remaining)
        row = {"command": [str(x) for x in argv], "start_raw": start,
               "effective_timeout_seconds": effective, "configured_timeout_seconds": timeout,
               "log": str(logfile)}
        rows.append(row)
        comparison.save(path, rows)
        result = source(argv, logfile, effective, env=env)
        row.update(asdict(result), stop_raw=raw_seconds())
        comparison.save(path, rows)
        if raw_seconds() > deadline:
            raise WallWindowEnded()
        return result

    try:
        comparison.run_process = invoke
        yield
    finally:
        comparison.run_process = source


def def_name(name):
    return name.replace(r"\[", "[").replace(r"\]", "]")


def drc_neighbor_evidence(reports, incident, edited, original_nets):
    """Extract only original wired signal neighbors on a marker tied to this edit."""
    original_aliases = {}
    for name, entry in original_nets.items():
        alias = def_name(name)
        if alias in original_aliases:
            raise ValueError(f"ambiguous original DEF net name {alias}")
        original_aliases[alias] = name
    incident_aliases = {def_name(net) for net in incident}
    selected = set()
    evidence = []
    for path in reports:
        text = path.read_text(encoding="utf-8")
        for block in re.split(r"(?m)(?=^violation type: )", text):
            source = re.search(r"(?m)^\s*srcs:\s*(.+)$", block)
            if not source:
                continue
            raw_nets = re.findall(r"\bnet:(\S+)", source[1])
            raw_instances = re.findall(r"\binst:(\S+)", source[1])
            if (not incident_aliases.intersection(map(def_name, raw_nets))
                    and not edited.intersection(map(comparison.canonical_odb_name, raw_instances))):
                continue
            neighbors = {
                original_aliases[def_name(name)]
                for name in raw_nets
                if def_name(name) in original_aliases and def_name(name) not in incident_aliases
                and "+ USE SIGNAL" in original_nets[original_aliases[def_name(name)]]
                and "+ ROUTED " in original_nets[original_aliases[def_name(name)]]
            }
            selected.update(neighbors)
            if neighbors:
                evidence.append({"report": str(path), "marker": block.strip(), "neighbors": sorted(neighbors)})
    return selected, evidence


class OnlineProtection:
    def __init__(self, matrix, output):
        self.matrix = matrix
        self.output = output
        config = read(matrix / "config.json")
        assets = config["bindings"]
        if (config["top"], config["pdk"], config["route_guide_source"]) != (
            "aes_cipher_top", "sky130hd", "embedded in frozen CONTROL ODB",
        ):
            raise ValueError("expected frozen AES matrix with embedded guides")
        control = {key: verify(item) for key, item in assets["control"].items()}
        source_sdc = verify(assets["original_sdc"])
        qualify = verify(assets["qualification_receipt"])
        self.tools = {key: verify(item) for key, item in assets["tools"].items()}
        self.flow = {key: verify(item) for key, item in assets["flow"].items()}
        libraries = {key: [verify(item) for item in values] for key, values in assets["used_libraries"].items()}
        pin = read(qualify)["source_sdc_semantics"]
        source_period = pin["period_sdc_units"]
        derived = expected_holdout_sdc(
            source_sdc.read_text(encoding="utf-8"),
            pinned=(source_period, pin["io_delay_sdc_units"] / source_period, pin["core_clock"],
                    pin["clock_port"], pin["virtual_latency_sdc_units"]),
            time_unit=pin["sdc_time_unit"],
        )
        period = derived["period_ps"]
        if period != config["original_clock_period_ps"] or config["numerical_tolerance_ps"] != comparison.PS_TOLERANCE:
            raise ValueError("frozen policy mismatch")
        self.screen = config["charged_screening_seconds"]
        self.target = config["primary_target_area_pct"]
        pool_path = matrix / "screened_pool_used.json"
        screen_pool, screen_receipt = (verify(config["screen_inputs"][key]) for key in ("pool", "receipt"))
        if read(pool_path) != read(screen_pool):
            raise ValueError("old screened matrix did not use the exact frozen ordered screen pool")
        screen_row = read(screen_receipt)
        if (screen_row["wall_seconds"] != self.screen
                or screen_row["pool_sha256"] != config["screen_inputs"]["pool"]["sha256"]
                or screen_row["control_sha256"] != {
                    key: assets["control"][key]["sha256"] for key in screen_row["control_sha256"]
                }):
            raise ValueError("screening cost or CONTROL binding mismatch")
        self.pool = [comparison.PhysicalAction(**row) for row in read(pool_path)]
        self.top = config["top"]
        self.reference_receipt = matrix / "control/receipt.json"
        args = SimpleNamespace(
            pdk="sky130hd", out=output, threads=config["methods_route_threads"],
            clock_period_ps=period, openroad=self.tools["openroad"], sta=self.tools["opensta"],
            sec=self.tools["sec"], orfs=self.flow["setRC.tcl"].parents[2],
            route_mode="local", droute_iters=config["route_drt_iters"],
            embedded_guides=True, route_guide=None, zero_reextract=False, single_pin_access=True,
            route_timeout=240.0, sta_timeout=config["sta_timeout_seconds_per_view"],
            sec_timeout=config["sec_timeout_seconds"], report_setup_endpoints=True,
        )
        with bind_runtime(self.top, self.flow["fastroute.tcl"]):
            masters = comparison.logical_masters(control["v"], comparison.liberty_areas(libraries["TT"]))
        self.eval = comparison.Evaluator(
            args, control, libraries, masters, read(self.reference_receipt)["views"], self.pool,
            config["scope"] + ":online_protection",
        )
        self.gate = sweep.budget_gate(self.eval, config["primary_budget_pct"], False)
        self.policy = comparison.BudgetPolicy.from_ps(self.gate.wns_ps, tolerance_ns=comparison.PS_TOLERANCE / 1000)
        self.header = "\n".join(re.findall(r"(?m)^(?:VERSION|DIVIDERCHAR|BUSBITCHARS|DESIGN|UNITS) .+?;$",
                                          control["def"].read_text(encoding="utf-8")))
        if len(self.header.splitlines()) != 5:
            raise ValueError("invalid frozen DEF header")
        self.nets = comparison.def_section(control["def"], "NETS")
        self.config = {
            "matrix": comparison.bind(matrix / "config.json"), "scope": self.eval.scope,
            "control_sta": comparison.bind(self.reference_receipt),
            "qualified_start": comparison.bind(qualify), "screened_pool": comparison.bind(pool_path),
            "historical_screen_receipt": comparison.bind(screen_receipt),
            "charged_screening_seconds_per_arm": self.screen, "measurement_clock": CLOCK_NAME,
            "wall_window_seconds_including_screen": LIMIT_SECONDS, "logical_dispatch_cap": MAX_REQUESTS,
            "methods": list(METHODS), "batch_size": config["batch_size"], "area_target_pct": self.target,
            "affinity": sorted(os.sched_getaffinity(0)), "route_threads": args.threads, "driver_pid": os.getpid(),
            "single_internal_pin_access": True, "direct_data_nets_only_initially": True,
            "maximum_neighbor_retries": 1,
            "retry_rule": "non-clock wired SIGNAL neighbors named on a DRC marker with an edited instance or incident net",
            "gate": sweep.gate_summary(self.gate, self.eval.ref_views),
            "absolute_hold_ps": 0.0, "relative_hold_tolerance_ps": comparison.PS_TOLERANCE,
        }
        self.batch = config["batch_size"]
        sources = [Path(__file__).resolve(), Path(comparison.__file__), Path(sweep.__file__),
                   Path(selective_route.__code__.co_filename), Path(audit.__code__.co_filename),
                   Path(bind_runtime.__code__.co_filename), Path(comparison.adaptive_batch_recovery.__code__.co_filename),
                   Path(expected_holdout_sdc.__code__.co_filename)]
        self.config["driver_sources"] = {p.name: comparison.bind(p) for p in sources}
        output.mkdir(parents=True)
        snapshots = output / "producer_sources"
        snapshots.mkdir()
        for path in sources:
            (snapshots / path.name).write_bytes(path.read_bytes())
        comparison.save(output / "config.json", self.config)
        comparison.save(output / "ordered_pool.json", [asdict(row) for row in self.pool])

    def direct_nets(self, actions):
        edited = {comparison.canonical_odb_name(self.eval.actions[key].instance) for key in actions}
        direct = {
            net for net, entry in self.nets.items()
            if edited.intersection(re.findall(r"\( (\S+) \S+ \)", entry.partition(" + ")[0]))
        }
        if (edited and not direct) or any("+ USE SIGNAL" not in self.nets[net] for net in direct):
            raise ValueError("direct edits must be linked solely to wired signal nets")
        return edited, direct

    def physical(self, actions, directory, incident, released):
        with selective_route("fixed-untouched", {directory.name: incident | released}, released,
                             (self.header, self.nets)):
            endpoint, row = self.eval.evaluate(actions, directory, envelope_only=True)
        failures = list(row["failures"])
        if not actions:
            failures = [reason for reason in failures if reason != "no_area_gain"]
        logfile = directory / "route.log"
        log = logfile.read_text(encoding="utf-8", errors="replace") if logfile.is_file() else ""
        pa_count = len(re.findall(PROTECT_PA, log))
        if pa_count != 1:
            failures.append("pin_access_count")
        if not row.get("routed_to_completion") or not row.get("extracted_to_completion"):
            return endpoint, row, failures, []
        failures.extend(audit_routing(directory, self.nets))
        unlocked = audit(self.matrix / "config.json", directory / "unlocked_drc", directory / "receipt.json")
        if unlocked["drc_markers"]:
            failures.append("unlocked_drc")
        failures.extend(audit_timing(self.eval, row, self.gate, not actions))
        reports = [directory / "drc.rpt", directory / "full_drc.rpt", directory / "unlocked_drc/full_drc.rpt"]
        comparison.save(directory / "assessment.json", {
            "failures": failures, "pin_access_starts": pa_count, "unlocked": unlocked,
            "physical_receipt": comparison.bind(directory / "receipt.json"),
        })
        return endpoint, row, failures, reports

    def attempt(self, actions, directory):
        directory.mkdir()
        start = raw_seconds()
        edited, incident = self.direct_nets(actions)
        comparison.save(directory / "request.json", {"actions": list(actions), "direct_signal_nets": sorted(incident)})
        endpoint, row, failures, reports = self.physical(actions, directory / "initial", incident, set())
        passes = ["initial"]
        drc_reasons = {"drc", "full_drc", "unlocked_drc"}
        # Hold/setup values from an illegal preliminary layout do not steer the retry decision.
        if actions and reports and drc_reasons.intersection(failures):
            unsafe = set(failures) - drc_reasons
            unrelated = {x for x in unsafe if not x.startswith(("FF:", "TT:", "SS:"))}
            if not unrelated:
                neighbors, proof = drc_neighbor_evidence(reports, incident, edited, self.nets)
                comparison.save(directory / "retry_decision.json",
                                {"released_neighbors": sorted(neighbors), "drc_marker_evidence": proof})
                if neighbors:
                    endpoint, row, failures, _ = self.physical(actions, directory / "retry", incident, neighbors)
                    passes.append("retry")
        final_dir = directory / passes[-1]
        proof_ops = {}
        if not failures:
            candidate = verify(row["artifacts"]["v"])
            if not actions and comparison.sha(candidate) != comparison.sha(self.eval.control["v"]):
                failures.append("zero_edit_netlist_changed")
            if not failures and not self.eval.proof(candidate, final_dir, proof_ops):
                failures.append("sec")
        if drc_reasons.intersection(failures):
            failures = [name for name in failures if name not in RELATIVE_HOLD_REASONS]
        ep = replace(endpoint, valid=not failures, sec_pass=not failures)
        record = {
            "actions": list(actions), "passes": passes, "scope_id": self.eval.scope,
            "physical_receipt": comparison.bind(final_dir / "receipt.json"), "failures": failures,
            "endpoint": asdict(ep), "proof_operations": proof_ops, "elapsed_seconds": raw_seconds() - start,
        }
        comparison.save(directory / "result.json", record)
        return ep, record

    def preflight(self):
        out = self.output / "preflight"
        out.mkdir()
        deadline = raw_seconds() + 1050
        with process_ledger(out / "subprocesses.json", deadline):
            zero, baseline = self.attempt((), out / "zero")
            comparison.save(out / "checkpoint.json", {"zero": baseline})
            if not zero.valid or not zero.sec_pass:
                raise ValueError(f"strict zero failed: {baseline['failures']}")
            first = tuple(sorted(action.action_id for action in self.pool[:self.batch]))
            _, challenge = self.attempt(first, out / "rank1_batch")
        comparison.save(out / "result.json", {"zero": baseline, "rank1_batch": challenge})
        print("preflight zero passed; rank1", challenge["failures"], flush=True)
        return zero

    def transfer_preflight(self, path):
        old_config = read(path.parent.parent / "config.json")
        current = {key: value for key, value in self.config.items() if key != "driver_pid"}
        supplied = {key: value for key, value in old_config.items() if key != "driver_pid"}
        if supplied != current:
            raise ValueError("preflight configuration does not bind the same protocol and inputs")
        result = read(path)
        zero = result["zero"]
        if zero["failures"] or not zero["endpoint"]["sec_pass"] or not result.get("rank1_batch"):
            raise ValueError("preflight has not completed with a strict accepted zero")
        receipt_path = verify(zero["physical_receipt"])
        verify(read(receipt_path)["artifacts"]["v"])
        summary = read(receipt_path.parent / "unlocked_drc/audit.json")
        if summary["drc_markers"]:
            raise ValueError("zero unlocked DRC report is not clean")
        verify(summary["report"])
        proof = read(receipt_path.parent / "sec/receipt.json")
        if (not proof["passed"] or proof["proven"] <= 0 or proof["unproven"] != 0
                or verify(proof["gate"]) != Path(read(receipt_path)["artifacts"]["v"]["path"])):
            raise ValueError("zero SEC receipt does not bind routed netlist")
        comparison.save(self.output / "transferred_preflight.json", {
            "preflight_result": comparison.bind(path), "strict_zero": zero,
            "unlocked_drc": summary, "sec": comparison.bind(receipt_path.parent / "sec/receipt.json"),
        })
        return comparison.Endpoint(**zero["endpoint"])

    def arm(self, method, reference):
        out = self.output / method
        out.mkdir()
        begun = raw_seconds()
        deadline = begun + LIMIT_SECONDS - self.screen
        checkpoints = []
        requests = []
        best = reference

        def write_progress(stopped):
            comparison.save(out / "progress.json", {
                "method": method, "start_raw": begun, "deadline_raw": deadline,
                "stop_reason": stopped, "logical_requests": requests, "checkpoints": checkpoints,
            })

        def evaluate(actions):
            nonlocal best
            if raw_seconds() >= deadline:
                raise WallWindowEnded()
            sequence = len(requests) + 1
            requests.append({"id": sequence, "actions": list(actions)})
            write_progress(None)
            print(f"{method} request {sequence} edits={len(actions)}", flush=True)
            ep, rec = self.attempt(actions, out / f"{sequence:02d}")
            if raw_seconds() >= deadline:
                requests[-1]["finished_after_cap"] = True
                raise WallWindowEnded()
            accepted = comparison.assess(reference, ep, self.policy).feasible and ep.area < best.area - 1e-9
            if accepted:
                best = ep
            requests[-1].update(failures=rec["failures"], physical_passes=len(rec["passes"]))
            checkpoints.append({"elapsed_seconds": self.screen + raw_seconds() - begun,
                                "accepted": accepted, "endpoint": asdict(ep)})
            write_progress(None)
            print(f"{method} {sequence} result {rec['failures'] or 'passed gates'}", flush=True)
            return ep

        def defer(actions):
            item = requests[-1]
            if tuple(item["actions"]) != actions:
                raise ValueError("scheduler hold-event identity mismatch")
            return not RELATIVE_HOLD_REASONS.isdisjoint(item["failures"])

        stop = "logical_cap_or_pool_exhausted"
        with process_ledger(out / "subprocesses.json", deadline):
            try:
                result = comparison.run_method(
                    method, reference, self.pool, evaluate, MAX_REQUESTS, self.batch, policy=self.policy,
                    defer_split_for=defer if method == "faeco" else None,
                )
                if result["selected"] != best or len(result["trace"]) != len(checkpoints):
                    raise ValueError("external checkpoints disagree with scheduler")
            except WallWindowEnded:
                stop = "end_to_end_wall_cap"
        write_progress(stop)
        timeline = sweep.summarize_wall_window(reference, checkpoints, wall_limit_seconds=LIMIT_SECONDS,
                                               target_area_pct=self.target)
        tools = read(out / "subprocesses.json")
        summary = {"method": method, "stop_reason": stop, "search_raw_seconds": raw_seconds() - begun,
                   "logical_admitted": len(requests), "logical_finished": len(checkpoints),
                   "route_tools": sum(Path(row["log"]).name == "route.log" for row in tools),
                   "unlocked_drc_tools": sum(Path(row["log"]).name == "audit.log" for row in tools),
                   "sta_tools": sum(Path(row["log"]).name.startswith("sta_") for row in tools),
                   "sec_tools": sum(Path(row["log"]).name == "sec.log" for row in tools),
                   "tool_seconds": math.fsum(row.get("wall_seconds", 0) for row in tools),
                   "window": timeline}
        comparison.save(out / "summary.json", summary)
        return summary


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("old_matrix", type=Path)
    p.add_argument("output", type=Path)
    phases = p.add_mutually_exclusive_group()
    phases.add_argument("--preflight-only", action="store_true")
    phases.add_argument("--verified-preflight", type=Path)
    args = p.parse_args()
    runner = OnlineProtection(args.old_matrix.resolve(strict=True), args.output.resolve())
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        reference = (runner.transfer_preflight(args.verified_preflight.resolve(strict=True))
                     if args.verified_preflight else runner.preflight())
        if args.preflight_only:
            return
        results = {}
        for method in METHODS:
            results[method] = runner.arm(method, reference)
            comparison.save(runner.output / "results.json", results)


if __name__ == "__main__":
    main()
