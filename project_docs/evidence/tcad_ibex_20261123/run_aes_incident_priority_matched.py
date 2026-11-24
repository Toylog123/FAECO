#!/usr/bin/env python3
"""Run fixed and incident-capacitance FAECO under the same strict AES wall window."""

from argparse import ArgumentParser
from dataclasses import asdict
from pathlib import Path
import math

import compare_ibex as comparison
import incident_cap_priority
import run_setup_budget_sweep as sweep
from probe_aes_selective_repair import read
from run_aes_protected_online import LIMIT_SECONDS, MAX_REQUESTS, OnlineProtection, WallWindowEnded, process_ledger
from run_screened_matrix import RELATIVE_HOLD_REASONS, bind_runtime, raw_seconds


METHODS = ("fixed", "faeco")


class IncidentPriorityComparison(OnlineProtection):
    def prepare_pair(self, preflight):
        reference = self.transfer_preflight(preflight)
        self.config.update({
            "methods": list(METHODS),
            "incident_priority_method": "faeco",
            "incident_priority_trigger": "first completed request rejected with a relative hold reason",
            "incident_priority_scope": "once, only unvisited actions after the trigger",
            "priority_cost": "measure from original DEF/SPEF within FAECO's strict raw wall window",
            "physical_cache": "disabled, including between arms and preflight",
        })
        for module in (Path(__file__).resolve(), Path(incident_cap_priority.__file__).resolve()):
            self.config["driver_sources"][module.name] = comparison.bind(module)
            (self.output / "producer_sources" / module.name).write_bytes(module.read_bytes())
        comparison.save(self.output / "config.json", self.config)
        return reference

    def arm(self, method, reference):
        out = self.output / method
        out.mkdir()
        begun = raw_seconds()
        deadline = begun + LIMIT_SECONDS - self.screen
        checkpoints = []
        requests = []
        best = reference
        first_defer = None
        priorities = None
        priority_span = None

        def write_progress(stopped):
            comparison.save(out / "progress.json", {
                "method": method, "start_raw": begun, "deadline_raw": deadline,
                "stop_reason": stopped, "logical_requests": requests, "checkpoints": checkpoints,
                "priority_preparation": priority_span, "first_relative_hold_defer": first_defer,
            })

        def evaluate(actions):
            nonlocal best
            admitted = raw_seconds()
            if admitted >= deadline:
                raise WallWindowEnded()
            sequence = len(requests) + 1
            requests.append({"id": sequence, "actions": list(actions), "admitted_raw": admitted})
            write_progress(None)
            print(f"{method} request {sequence} edits={len(actions)}", flush=True)
            endpoint, record = self.attempt(actions, out / f"{sequence:02d}")
            accepted = comparison.assess(reference, endpoint, self.policy).feasible and endpoint.area < best.area - 1e-9
            finished = raw_seconds()
            if finished >= deadline:
                requests[-1]["finished_after_cap"] = True
                raise WallWindowEnded()
            if accepted:
                best = endpoint
            requests[-1].update(failures=record["failures"], physical_passes=len(record["passes"]), finished_raw=finished)
            checkpoints.append({"elapsed_seconds": self.screen + (finished - begun),
                                "accepted": accepted, "endpoint": asdict(endpoint)})
            write_progress(None)
            print(f"{method} {sequence} result {record['failures'] or 'passed gates'}", flush=True)
            return endpoint

        def defer(actions):
            nonlocal first_defer
            latest = requests[-1]
            if tuple(latest["actions"]) != actions:
                raise ValueError("scheduler hold-event identity mismatch")
            reasons = sorted(RELATIVE_HOLD_REASONS.intersection(latest["failures"]))
            if reasons and first_defer is None:
                first_defer = {"request_id": latest["id"], "actions": latest["actions"], "reasons": reasons}
                write_progress(None)
            return bool(reasons)

        if method == "faeco":
            preparation_start = raw_seconds()
            control = self.eval.control
            ranking = incident_cap_priority.build_incident_priority(control["def"], control["spef"], self.pool)
            preparation_end = raw_seconds()
            priority_span = {"start_raw": preparation_start, "stop_raw": preparation_end,
                             "seconds": preparation_end - preparation_start}
            priorities = {key: row["priority"] for key, row in ranking["actions"].items()}
            comparison.save(out / "incident_priority.json", {
                **ranking, "control_def": comparison.bind(control["def"]),
                "control_spef": comparison.bind(control["spef"]), "preparation": priority_span,
            })
        write_progress(None)
        stop = "logical_cap_or_pool_exhausted"
        with process_ledger(out / "subprocesses.json", deadline):
            try:
                result = comparison.run_method(
                    method, reference, self.pool, evaluate, MAX_REQUESTS, self.batch, policy=self.policy,
                    defer_split_for=defer if method == "faeco" else None, priority_after_defer=priorities,
                )
                if result["selected"] != best or len(result["trace"]) != len(checkpoints):
                    raise ValueError("external checkpoints disagree with scheduler")
            except WallWindowEnded:
                stop = "end_to_end_wall_cap"
        ended = raw_seconds()
        write_progress(stop)
        timeline = sweep.summarize_wall_window(reference, checkpoints, wall_limit_seconds=LIMIT_SECONDS,
                                               target_area_pct=self.target)
        tools = read(out / "subprocesses.json") if (out / "subprocesses.json").exists() else []
        summary = {"method": method, "stop_reason": stop, "search_raw_seconds": ended - begun,
                   "stop_raw": ended, "logical_admitted": len(requests), "logical_finished": len(checkpoints),
                   "route_tools": sum(Path(row["log"]).name == "route.log" for row in tools),
                   "unlocked_drc_tools": sum(Path(row["log"]).name == "audit.log" for row in tools),
                   "sta_tools": sum(Path(row["log"]).name.startswith("sta_") for row in tools),
                   "sec_tools": sum(Path(row["log"]).name == "sec.log" for row in tools),
                   "tool_seconds": math.fsum(row.get("wall_seconds", 0) for row in tools),
                   "priority_preparation": priority_span, "first_relative_hold_defer": first_defer,
                   "window": timeline}
        comparison.save(out / "summary.json", summary)
        return summary


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("old_matrix", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("preflight", type=Path)
    args = parser.parse_args()
    runner = IncidentPriorityComparison(args.old_matrix.resolve(strict=True), args.output.resolve())
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        reference = runner.prepare_pair(args.preflight.resolve(strict=True))
        results = {}
        for method in METHODS:
            results[method] = runner.arm(method, reference)
            comparison.save(runner.output / "results.json", results)


if __name__ == "__main__":
    main()
