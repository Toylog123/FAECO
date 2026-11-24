#!/usr/bin/env python3
"""Recompute a screened matrix from its physical, gate, and timing receipts."""

import argparse
from collections import Counter
from pathlib import Path
import json
import math

import compare_ibex as comparison
from incident_cap_priority import build_incident_priority
from verify_setup_protocol import Audit, check_bindings, digest, equal, near, need, read


CLOCK = "CLOCK_MONOTONIC_RAW"
STA_STAGES = tuple(f"STA_{corner}" for corner in comparison.CORNERS)
RELATIVE_HOLD = {f"{corner}:hold_regression" for corner in comparison.CORNERS}


class MatrixAudit(Audit):
    def verify_sta(self, directory, record, artifacts):
        views = super().verify_sta(directory, record, artifacts)
        top = self.config["top"]
        for view in views:
            script = directory / f"sta_{view}.tcl"
            source = script.read_text().splitlines()
            equal([line for line in source if line.startswith("link_design ")], [f"link_design {top}"],
                  f"original STA top {directory} {view}")
            if self.config["pdk"] == "sky130hd":
                adapted = script.with_suffix(".odb.tcl").read_text().splitlines()
                index = next(i for i, line in enumerate(source) if line.startswith("read_verilog "))
                equal(adapted, [
                    *source[:index], f"read_db {{{artifacts['odb']['path']}}}", *source[index + 2:],
                ], f"actual ODB STA deck {directory} {view}")
                began = (directory / f"sta_{view}.log").read_text().splitlines()[0]
                equal(began, f"IBEX_STA_ROUTED_ODB {artifacts['odb']['path']}", f"actual ODB marker {directory} {view}")
        return views

    def proof(self, directory, operations, candidate, *, passed):
        count = super().proof(directory, operations, candidate, passed=passed)
        if count is not None:
            source = (directory / "sec/prove.ys").read_text().splitlines()
            equal([line for line in source if line.startswith("hierarchy -simcheck -top ")],
                  [f"hierarchy -simcheck -top {self.config['top']}"] * 2, f"SEC design top {directory}")
        return count

    def wall_window(self, actual, timeline, directory):
        cap = self.config["primary_wall_limit_seconds"]
        target_pct = self.config["primary_target_area_pct"]
        target = self.area * target_pct / 100
        first = next((elapsed for elapsed, accepted, ep in timeline
                      if accepted and self.area - ep["area"] >= target - 1e-9), None)
        prefix = self.prefix(timeline, cap)
        for key, value in prefix.items():
            equal(actual[key], value, f"wall-window {key} {directory}")
        in_window = first if first is not None and first <= cap else None
        equal(actual["time_to_target_seconds"], in_window, f"within-window target {directory}")
        equal(actual["target_reached_in_window"], in_window is not None, f"target censoring {directory}")
        near(actual["wall_limit_seconds"], cap, f"wall seconds ceiling {directory}")
        near(actual["target_area_pct"], target_pct, f"target percent {directory}")
        near(actual["target_area_saved"], target, f"target area {directory}")
        near(actual["area_saved_pct"], 100 * prefix["area_saved"] / self.area, f"prefix percentage {directory}")
        return first, prefix

    def matrix_arm(self, directory, arm, screen_seconds):
        equal(read(directory / "summary.json"), arm, f"arm summary binding {directory}")
        equal(arm["clock"], CLOCK, f"arm clock {directory}")
        near(arm["charged_screening_seconds"], screen_seconds, f"screen cost {directory}")
        ranking = self.config.get("incident_ranking") if directory.name == "faeco" else None
        ranking_seconds = ranking["raw_seconds"] if ranking else 0.0
        near(arm.get("charged_ranking_seconds", 0.0), ranking_seconds, f"ranking cost {directory}")
        front_end = screen_seconds + ranking_seconds
        count = self.config["budget_attempts_per_arm"]
        equal((arm["evaluations_used"], len(arm["trace"]), len(arm["checkpoints"]),
               len(arm["end_to_end_checkpoints"])), (count,) * 4, f"complete arm {directory}")
        self.verify_order(directory, arm["trace"])
        paths = [directory / f"{idx:02d}.json" for idx in range(1, count + 1)]
        equal(arm["attempt_receipts"], [str(path) for path in paths], f"attempt paths {directory}")
        best, committed = self.ref["endpoint"], set()
        search, end_to_end, measured = [], [], []
        stage = dict.fromkeys(("DRT_RCX", *STA_STAGES, "SEC"), 0.0)
        failures = Counter()
        hold_only = 0
        for path, trace, checkpoint, charged in zip(
                paths, arm["trace"], arm["checkpoints"], arm["end_to_end_checkpoints"], strict=True):
            actions = trace["actions"]
            need(actions == sorted(set(actions)) and committed <= set(actions), f"dispatch tuple {path}")
            equal(len(set(actions) - committed), trace["batch_len"], f"batch width {path}")
            attempt = self.request(path, actions, self.config["primary_budget_pct"], False, True)
            ep = attempt["endpoint"]
            physical_path = Path(attempt["physical_receipt"])
            measured.append(physical_path)
            physical = self.physical[physical_path]
            need(set(physical["views"]) == set(comparison.CORNERS), f"incomplete raw STA {path}")
            for key in ("area", "wns_ns", "hold_wns_ns"):
                equal(trace[key], ep[key], f"trace metric {key} {path}")
            equal(trace["feasible"], ep["valid"], f"trace feasibility {path}")
            accepted = ep["valid"] and ep["area"] < best["area"] - 1e-9
            equal(trace["accepted"], accepted, f"accepted trace {path}")
            equal((checkpoint["accepted"], checkpoint["endpoint"]), (accepted, ep), f"raw checkpoint {path}")
            equal((charged["accepted"], charged["endpoint"]), (accepted, ep), f"charged checkpoint {path}")
            elapsed = checkpoint["elapsed_seconds"]
            last = search[-1][0] if search else 0.0
            need(math.isfinite(elapsed) and elapsed + 1e-8 >= last + attempt["wall_seconds"],
                 f"checkpoint precedes counted work {path}")
            near(charged["elapsed_seconds"], elapsed + front_end, f"charged checkpoint time {path}")
            search.append((elapsed, accepted, ep))
            end_to_end.append((charged["elapsed_seconds"], accepted, ep))
            if accepted:
                best, committed = ep, set(actions)
            failures.update(attempt["failures"])
            hold_only += bool(attempt["failures"]) and set(attempt["failures"]) <= RELATIVE_HOLD
            proof, _ = self.proofs.get(physical_path, (None, None))
            for key, op in physical["operations"].items():
                stage[key] += op["wall_seconds"]
            if proof:
                stage["SEC"] += proof["operations"]["SEC"]["wall_seconds"]
        equal(arm["selected"], best, f"best endpoint {directory}")
        equal(sorted(arm["committed"]), sorted(committed), f"committed actions {directory}")
        near(arm["area_saved"], self.area - best["area"], f"selected gain {directory}")
        equal(dict(failures), arm["failures_by_exact_reason"], f"rejection reasons {directory}")
        equal(hold_only, arm["relative_hold_only_rejections"], f"relative-hold-only rejections {directory}")
        for key, seconds in stage.items():
            near(arm["tool_stage_seconds"][key], seconds, f"stage seconds {key} {directory}")
        for key, value in self.totals(measured).items():
            near(arm["operations"][key], value, f"operations {key} {directory}")
        near(arm["search_wall_seconds"], arm["wall_seconds"], f"search-only raw wall {directory}")
        need(math.isfinite(arm["search_wall_seconds"]) and arm["search_wall_seconds"] >= search[-1][0],
             f"arm duration precedes final checkpoint {directory}")
        near(arm["end_to_end_wall_seconds"], arm["search_wall_seconds"] + front_end, f"charged wall {directory}")
        search_target, _ = self.wall_window(arm["search_only_wall_window"], search, directory)
        e2e_target, prefix = self.wall_window(arm["wall_window"], end_to_end, directory)
        equal(arm["search_time_to_target_seconds"], search_target, f"search-first area time {directory}")
        equal(arm["end_to_end_time_to_target_seconds"], e2e_target, f"charged-first area time {directory}")
        return {
            "within_cap": self.outcome(best), "within_wall_window": self.outcome(prefix["selected"]),
            "attempts_inside_wall": prefix["completed_attempts"],
            "time_to_target_seconds": e2e_target, "search_time_to_target_seconds": search_target,
            "charged_screening_seconds": screen_seconds, "search_wall_seconds": arm["search_wall_seconds"],
            "charged_ranking_seconds": ranking_seconds,
            "stage_seconds": stage, "failure_reasons": dict(failures), "relative_hold_only_rejections": hold_only,
            "operations": arm["operations"],
        }

    def run_matrix(self):
        final = read(self.root / "results.json")
        equal(final["status"], "matched", "matrix status")
        equal(final["scope"], self.scope, "matrix scope")
        equal(final["control"], self.ref, "embedded control receipt")
        self.gate_summary(final["gate"], self.config["primary_budget_pct"], False)
        equal(self.config["clock"], CLOCK, "matrix clock")
        equal(self.config["tns_gate"], True, "TNS gate is enabled")
        need(self.config["clock_resolution_seconds"] > 0, "clock resolution")
        noop = self.verify_physical(self.root / "noop" / "receipt.json", (), noop=True)
        equal(noop, final["shared_noop"], "embedded no-op receipt")
        screen = self.config["screen_inputs"]
        check_bindings(screen)
        equal(final["screen_inputs"], screen, "screen bindings")
        receipt = read(Path(screen["receipt"]["path"]))
        equal(receipt["top"], self.config["top"], "screen design")
        equal(receipt["clock"], CLOCK, "screen clock")
        near(receipt["wall_seconds"], self.config["charged_screening_seconds"], "screen receipt seconds")
        equal(receipt["pool_sha256"], screen["pool"]["sha256"], "screened candidate ordering hash")
        for kind in ("odb", "spef", "sdc"):
            equal(receipt["control_sha256"][kind], self.control[kind]["sha256"], f"screen reference {kind}")
        pool = {"legacy": self.pool, "screened": read(Path(screen["pool"]["path"]))}
        ranking = self.config.get("incident_ranking")
        if ranking is not None:
            rebuilt = build_incident_priority(
                Path(self.control["def"]["path"]), Path(self.control["spef"]["path"]),
                [comparison.PhysicalAction(**row) for row in pool["screened"]],
            )
            equal({key: value for key, value in ranking.items() if key != "raw_seconds"}, rebuilt,
                  "ranking from original capacitance and topology")
            need(math.isfinite(ranking["raw_seconds"]) and ranking["raw_seconds"] >= 0, "ranking charge")
        equal(read(self.root / "screened_pool_used.json"), pool["screened"], "screened order consumed")
        equal((final["qualified_legacy_instances"], final["screened_instances"]),
              (len(pool["legacy"]), len(pool["screened"])), "pool sizes")
        expected_order = [(kind, method) for kind in self.config["pool_order"] for method in self.config["methods_in_run_order"]]
        equal([(row["pool"], row["method"]) for row in final["serial_arm_order"]], expected_order, "serial arms")
        previous_end = 0.0
        arms = {}
        for row in final["serial_arm_order"]:
            kind, method = row["pool"], row["method"]
            self.pool = pool[kind]
            self.actions = {item["action_id"]: item for item in self.pool}
            equal(len(self.actions), len(self.pool), f"unique {kind} edit IDs")
            charge = receipt["wall_seconds"] if kind == "screened" else 0.0
            current = final["arms"][kind][method]
            start, end = row["raw_start"], row["raw_end"]
            need(previous_end <= start <= end and end - start >= current["wall_seconds"],
                 f"serial raw-clock interval {kind}/{method}")
            previous_end = end
            arms.setdefault(kind, {})[method] = self.matrix_arm(self.root / kind / method, current, charge)
        counts = self.totals(list(self.physical))
        for key, value in counts.items():
            near(final["physical_operations"][key], value, f"all-arm count {key}")
        expected = len(expected_order) * self.config["budget_attempts_per_arm"]
        equal(self.cache_hits, 0, "no reused physical measurements")
        equal(self.request_count, expected, "all expected independent physical evaluations")
        equal(final["physical_operations"]["logical_requests"], self.request_count, "logical count")
        equal(final["physical_operations"]["physical_cache_hits"], 0, "cache evidence")
        observed = set(self.root.glob("*/*/*_physical/receipt.json"))
        equal(observed, set(self.physical), "unaccounted physical candidates")
        return {
            "top": self.config["top"], "clock": CLOCK, "config_sha256": digest(self.root / "config.json"),
            "results_sha256": digest(self.root / "results.json"), "screened_pool_sha256": screen["pool"]["sha256"],
            "screened_receipt_sha256": screen["receipt"]["sha256"], "control": self.outcome(self.ref["endpoint"]),
            "noop_sec_proven": self.noop_proven, "arms": arms, "total_operations": counts, "cache_hits": self.cache_hits,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    comparison.TOP = read(root / "config.json")["top"]
    print(json.dumps(MatrixAudit(root).run_matrix(), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
