#!/usr/bin/env python3
"""Audit retained Ibex protocol artefacts without running any EDA tools."""

from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import gzip
from hashlib import file_digest, sha256
import json
import math
from pathlib import Path
import re
import shlex

from asap7_control.qualify_asap7_control import expected_sdc
from compare_ibex import (
    CORNERS, ERROR, canonical_odb_name, changed_geometry, liberty_areas, logical_masters,
    parse_inventory, parse_sta, tcl,
)


METHODS = ("single", "fixed", "faeco")
METRICS = ("setup_wns_ps", "setup_tns_ps", "hold_wns_ps", "hold_tns_ps")
COUNT_KEYS = ("route_attempts", "drt_completions", "rcx_completions", "view_sta_attempts", "sec_attempts")


def need(ok, detail):
    if not ok:
        raise ValueError(detail)


def equal(actual, expected, detail):
    need(actual == expected, detail)


def near(actual, expected, detail):
    need(math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-8), detail)


def read(path):
    return json.loads(path.read_bytes())


@lru_cache(maxsize=None)
def digest(path):
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def check_bindings(value):
    if isinstance(value, dict) and {"path", "bytes", "sha256"} <= value.keys():
        path = Path(value["path"])
        equal(path.stat().st_size, value["bytes"], f"byte count {path}")
        equal(digest(path), value["sha256"], f"SHA-256 {path}")
    elif isinstance(value, dict):
        for item in value.values():
            check_bindings(item)
    elif isinstance(value, list):
        for item in value:
            check_bindings(item)


def process(op, log, timeout):
    equal(Path(op["log"]), log, f"operation log {log}")
    near(op["timeout_seconds"], timeout, f"operation timeout {log}")
    need(math.isfinite(op["wall_seconds"]) and op["wall_seconds"] > 0, f"operation time {log}")
    return log.read_text(errors="replace")


def complete(op, text, marker):
    return op["returncode"] == 0 and not ERROR.search(text) and marker in text.splitlines()


def count_physical(record, proof=None):
    ops = record["operations"]
    return {
        "route_attempts": int("DRT_RCX" in ops),
        "drt_completions": int(record.get("routed_to_completion", False)),
        "rcx_completions": int(record.get("extracted_to_completion", False)),
        "view_sta_attempts": sum(f"STA_{view}" in ops for view in CORNERS),
        "sec_attempts": int("SEC" in (proof["operations"] if proof is not None else ops)),
    }


class Audit:
    def __init__(self, root):
        self.root = root
        self.config = read(root / "config.json")
        self.assets = self.config["bindings"]
        self.scope = sha256(json.dumps(self.assets, sort_keys=True).encode()).hexdigest()
        equal(self.config["scope"], self.scope, "configuration scope")
        check_bindings(self.assets)
        self.control = self.assets["control"]
        self.libs = self.assets["used_libraries"]
        self.areas = liberty_areas(Path(item["path"]) for item in self.libs["TT"])
        self.masters = logical_masters(Path(self.control["v"]["path"]), self.areas)
        self.area = math.fsum(self.areas[master] for master in self.masters.values())
        self.ref = read(root / "control/receipt.json")
        equal(self.ref["status"], "passed", "control status")
        self.verify_sta(root / "control", self.ref, self.control)
        self.ref_views = self.ref["views"]
        self.endpoint(self.ref["endpoint"], root / "control", self.area, self.ref_views, True, True)
        qualification = read(Path(self.assets["qualification_receipt"]["path"]))
        self.tol = self.config["numerical_tolerance_ps"]
        self.period = self.config["original_clock_period_ps"]
        source = qualification["source_sdc_semantics"]
        original = Path(self.assets["original_sdc"]["path"]).read_text()
        derived = expected_sdc(original, pinned=(
            source["period_sdc_units"], source["io_delay_sdc_units"] / source["period_sdc_units"],
            source["core_clock"], source["clock_port"], source["virtual_latency_sdc_units"],
        ), time_unit=source["sdc_time_unit"])
        equal(derived["period_ps"], self.period, "original source SDC period in ps")
        equal(source["period_ps"], self.period, "P0 qualified SDC period in ps")
        for view in CORNERS:
            need(self.ref_views[view]["hold_wns_ps"] >= 0, f"negative baseline hold {view}")
            for metric in METRICS:
                need(abs(self.ref_views[view][metric] - qualification["views"][view][metric]) <= self.tol,
                     f"P0 mismatch {view} {metric}")
        self.pool = read(root / "pool.json")
        self.actions = {action["action_id"]: action for action in self.pool}
        equal(len(self.actions), self.ref["pool_instances"], "pool action cardinality")
        equal(len({action["instance"] for action in self.pool}), len(self.pool), "pool instance uniqueness")
        inventory = self.ref["operations"]["ODB_INVENTORY"]
        source = process(inventory, root / "control/inventory.log", self.config["sta_timeout_seconds_per_view"])
        need(complete(inventory, source, "IBEX_INVENTORY_COMPLETE"), "control ODB inventory")
        commands = (root / "control/inventory.tcl").read_text().splitlines()
        equal([line for line in commands if line.startswith("read_db ")],
              [f"read_db {tcl(self.control['odb']['path'])}"], "control inventory ODB binding")
        _, instances = parse_inventory(source)
        normalized = {canonical_odb_name(name): attrs[0] for name, attrs in instances.items()}
        for action in self.pool:
            name = canonical_odb_name(action["instance"])
            equal(self.masters[name], action["source_cell"], f"pool source netlist {name}")
            equal(normalized[name], action["source_cell"], f"pool source ODB {name}")
            need(self.areas[action["target_cell"]] < self.areas[action["source_cell"]], f"pool area {name}")
        self.physical = {}
        self.proofs = {}
        self.cache = {}
        self.logical_paths = set()
        self.request_count = self.cache_hits = 0
        self.anomalies = []

    def endpoint(self, record, directory, area, views, valid, sec):
        equal(record["endpoint_id"], str(directory.relative_to(self.root)), f"endpoint identity {directory}")
        equal(Path(record["evidence_id"]), directory, f"endpoint artefact {directory}")
        equal(record["scope_id"], self.scope, f"endpoint scope {directory}")
        equal((record["valid"], record["sec_pass"]), (valid, sec), f"endpoint gates {directory}")
        near(record["area"], area, f"endpoint area {directory}")
        for field, metric in zip(("wns_ns", "tns_ns", "hold_wns_ns"), METRICS[:3], strict=True):
            near(record[field], views["TT"][metric] / 1000, f"endpoint {field} {directory}")

    def verify_sta(self, directory, record, artifacts):
        measured = {}
        for view in CORNERS:
            op = record["operations"].get(f"STA_{view}")
            if op is None:
                break
            text = process(op, directory / f"sta_{view}.log", self.config["sta_timeout_seconds_per_view"])
            commands = (directory / f"sta_{view}.tcl").read_text().splitlines()
            for cmd, asset in (("read_verilog", artifacts["v"]), ("read_spef", artifacts["spef"]),
                               ("read_sdc", self.control["sdc"])):
                equal([line for line in commands if line.startswith(cmd + " ")],
                      [f"{cmd} {tcl(asset['path'])}"], f"STA input {cmd} {directory} {view}")
            equal([line for line in commands if line.startswith("read_liberty ")],
                  [f"read_liberty {tcl(item['path'])}" for item in self.libs[view]], f"STA Liberty {directory} {view}")
            if complete(op, text, "IBEX_STA_COMPLETE"):
                measured[view] = parse_sta(text)
                need("setup_negative_endpoints" in measured[view], f"setup endpoint inventory {directory} {view}")
        # The physical driver publishes views atomically only after all three succeed.
        published = measured if set(measured) == set(CORNERS) else {}
        equal(record["views"], published, f"raw STA values {directory}")
        return published

    def common_gates(self, views):
        reasons = []
        for view in CORNERS:
            base, trial = self.ref_views[view], views[view]
            if trial["hold_wns_ps"] < 0:
                reasons.append(f"{view}:negative_hold")
            if trial["hold_wns_ps"] < base["hold_wns_ps"] - self.tol:
                reasons.append(f"{view}:hold_regression")
            if trial["ports"] != base["ports"]:
                reasons.append(f"{view}:port_identity")
            for kind in base["electrical"]:
                if trial["electrical"][kind].keys() - base["electrical"][kind].keys():
                    reasons.append(f"{view}:new_{kind.lower()}_violations")
        return reasons

    def setup_gates(self, views, pct, protect):
        reasons = []
        budget = self.period * (pct / 100)
        for view in CORNERS:
            base, trial = self.ref_views[view], views[view]
            if trial["setup_wns_ps"] < base["setup_wns_ps"] - budget - self.tol:
                reasons.append(f"{view}:setup_budget")
            if protect and base["setup_wns_ps"] >= 0 > trial["setup_wns_ps"]:
                reasons.append(f"{view}:setup_floor")
            tns_budget = max(10 * budget, abs(base["setup_tns_ps"]) * (pct / 100))
            if trial["setup_tns_ps"] < base["setup_tns_ps"] - tns_budget - self.tol:
                reasons.append(f"{view}:setup_tns_budget")
        return reasons

    def view_metrics(self, views):
        result = {}
        for view in CORNERS:
            ref, trial = self.ref_views[view], views[view]
            before, after = set(ref["setup_negative_endpoints"]), set(trial["setup_negative_endpoints"])
            result[view] = {
                **{metric: trial[metric] for metric in METRICS},
                **{f"delta_{metric}": trial[metric] - ref[metric] for metric in METRICS},
                "control_negative": len(before), "candidate_negative": len(after), "new_negative": len(after - before),
            }
        return result

    def proof(self, directory, operations, candidate, *, passed):
        op = operations.get("SEC")
        receipt = directory / "sec/receipt.json"
        if op is None:
            need(not passed and not receipt.exists(), f"SEC operation absent {directory}")
            return None
        log = process(op, directory / "sec.log", self.config["sec_timeout_seconds"])
        if not receipt.exists():
            need(not passed and op["returncode"] != 0, f"SEC receipt absent {directory}")
            return None
        raw = read(receipt)
        check_bindings(raw)
        for role, artifact in (("gold", self.control["v"]), ("gate", candidate)):
            bound = {**artifact, "path": str(Path(artifact["path"]).resolve())}
            equal(raw[role], bound, f"SEC {role} identity {directory}")
        equal(raw["liberties"], self.libs["TT"], f"SEC TT models {directory}")
        for src, loaded in zip(raw["liberties"], raw["loaded_liberties"], strict=True):
            if src["path"].endswith(".gz"):
                with gzip.open(src["path"], "rb") as stream:
                    equal(file_digest(stream, "sha256").hexdigest(), loaded["sha256"], f"SEC expanded Liberty {directory}")
            else:
                equal(src, loaded, f"SEC loaded Liberty {directory}")
        script_path, log_path = directory / "sec/prove.ys", directory / "sec/prove.log"
        equal(Path(raw["script"]["path"]), script_path, f"proof script path {directory}")
        equal(Path(raw["log"]["path"]), log_path, f"proof log path {directory}")
        script = script_path.read_text().splitlines()
        equal([line for line in script if line.startswith("read_verilog ")],
              [f'read_verilog "{raw[key]["path"]}"' for key in ("gold", "gate")], f"proof inputs {directory}")
        reads = [line.split(' "', 1)[-1] for line in script if line.startswith("read_liberty ")]
        equal(reads, [f'{lib["path"]}"' for lib in raw["loaded_liberties"]] * 2, f"proof model usage {directory}")
        need("equiv_status -assert" in script, f"SEC assertion absent {directory}")
        matches = re.findall(r"(\d+) are proven and (\d+) are unproven", log_path.read_text(errors="replace"))
        counts = tuple(map(int, matches[-1])) if matches else (0, None)
        equal(counts, (raw["proven"], raw["unproven"]), f"SEC raw proof count {directory}")
        outcome = raw["returncode"] == op["returncode"] == 0 and counts[0] > 0 and counts[1] == 0
        equal(raw["passed"], outcome, f"SEC process verifier {directory}")
        equal(passed, outcome, f"SEC linked outcome {directory}")
        need(f"SEC proven={counts[0]} unproven={counts[1]} rc={raw['returncode']}" in log, f"SEC launcher log {directory}")
        return counts[0] if outcome else None

    def verify_physical(self, path, actions, *, noop=False):
        if path in self.physical:
            return self.physical[path]
        directory, record = path.parent, read(path)
        equal(record["actions"], list(actions), f"physical action tuple {path}")
        equal(record["endpoint_id"], str(directory.relative_to(self.root)), f"physical endpoint ID {path}")
        equal(record["control_sdc"], self.control["sdc"], f"original propagated SDC {path}")
        ops = record["operations"]
        frozen = noop and "RCX_REEXTRACT" in ops
        route = ops["RCX_REEXTRACT" if frozen else "DRT_RCX"]
        text = process(route, directory / "route.log", self.config["route_timeout_seconds"])
        lines = text.splitlines()
        equal("IBEX_DRT_COMPLETE" in lines, record["routed_to_completion"], f"DRT completion {path}")
        equal("IBEX_RCX_COMPLETE" in lines, record["extracted_to_completion"], f"RCX completion {path}")
        equal("IBEX_REUSED_FROZEN_DRT" in lines, frozen, f"frozen route marker {path}")
        commands = (directory / "route.tcl").read_text().splitlines()
        for command, asset in (("read_db", self.control["odb"]), ("read_sdc", self.control["sdc"])):
            equal([line for line in commands if line.startswith(command + " ")],
                  [f"{command} {tcl(asset['path'])}"], f"route input {command} {path}")
        flow = self.assets["flow"]
        equal(sorted(str(Path(shlex.split(line)[1]).resolve()) for line in commands if line.startswith("source ")),
              sorted(asset["path"] for name, asset in flow.items() if name.endswith(".tcl")),
              f"routing settings and extraction Tcl {path}")
        extraction = [shlex.split(line) for line in commands if line.startswith("extract_parasitics ")]
        need(len(extraction) == 1 and len(extraction[0]) == 3 and extraction[0][1] == "-ext_model_file",
             f"extraction invocation {path}")
        equal(str(Path(extraction[0][2]).resolve()), flow["rcx_patterns.rules"]["path"], f"extraction model binding {path}")
        equal(sum(line.startswith("detailed_route ") for line in commands), int(not frozen), f"routing invocation {path}")
        equal([line for line in commands if line.startswith("read_liberty ")],
              [f"read_liberty {tcl(item['path'])}" for item in self.libs["TT"]], f"routing TT Liberty {path}")
        if "route_guide" in self.assets and not frozen:
            guides = [shlex.split(line) for line in commands if line.startswith("read_guides ")]
            need(len(guides) == 1 and len(guides[0]) == 2, f"external route guide invocation {path}")
            equal(str(Path(guides[0][1]).resolve()), self.assets["route_guide"]["path"], f"external route guide {path}")
        if self.config["route_guide_source"] == "embedded in frozen CONTROL ODB" and not frozen:
            need(any("grt::have_routes" in line for line in commands), f"embedded route guide {path}")
        expected = self.masters.copy()
        for aid in actions:
            action = self.actions[aid]
            name = canonical_odb_name(action["instance"])
            equal(expected[name], action["source_cell"], f"unique edited source {name} {path}")
            expected[name] = action["target_cell"]
        artifacts = record.get("artifacts", {})
        views = self.verify_sta(directory, record, artifacts)
        failures = []
        if artifacts:
            need(complete(route, text, "IBEX_ROUTE_COMPLETE"), f"raw routing rc/marker {path}")
            need(record["extracted_to_completion"] and (record["routed_to_completion"] or frozen),
                 f"missing completed DRT/RCX evidence {path}")
            check_bindings(artifacts)
            for ext in ("odb", "def", "v", "spef"):
                equal(Path(artifacts[ext]["path"]), directory / f"routed.{ext}", f"routed {ext} binding {path}")
                need(artifacts[ext]["bytes"] > 0, f"empty routed {ext} {path}")
            equal(Path(artifacts["drc"]["path"]), directory / "drc.rpt", f"DRC binding {path}")
            marks = re.findall(r"(?m)^IBEX_DRT_VIOLATIONS (\d+)\s*$", text)
            equal(marks, [str(record["drc_violations"])], f"raw DRC count {path}")
            if int(marks[0]) or (directory / "drc.rpt").read_text().strip():
                failures.append("drc")
            touched = set(re.findall(r"(?m)^IBEX_TOUCHED_NET (.+)$", text))
            actual = logical_masters(directory / "routed.v", self.areas)
            layout = changed_geometry(Path(self.control["def"]["path"]), directory / "routed.def", touched)
            equal(read(directory / "layout_changes.json"), layout, f"DEF geometry evidence {path}")
            if layout["changed_component_placement"]:
                failures.append("component_placement_changed")
            if actions and not touched:
                failures.append("no_edited_signal_nets")
            if actual != expected:
                differences = {name: {"expected": expected.get(name), "actual": actual.get(name)}
                               for name in expected.keys() | actual.keys() if expected.get(name) != actual.get(name)}
                equal(record.get("instance_mismatches"), differences, f"netlist master discrepancy {path}")
                failures.append("netlist_master_identity")
            area = math.fsum(self.areas[master] for master in actual.values())
            near(record["area_saved"], self.area - area, f"candidate area delta {path}")
            if not noop and self.area - area <= 1e-9:
                failures.append("no_area_gain")
        elif views:
            raise ValueError(f"missing STA candidate artefacts {path}")
        if views:
            metrics = self.view_metrics(views)
            equal(record["setup_endpoint_counts"], {
                view: {key: row[key] for key in ("control_negative", "candidate_negative", "new_negative")}
                for view, row in metrics.items()
            }, f"new setup endpoint calculation {path}")
            failures.extend(self.common_gates(views))
            if noop:
                allowance = self.config["no_op_preflight_setup_budget_ps"]
                failures.extend(f"{view}:setup_budget" for view in CORNERS if
                                views[view]["setup_wns_ps"] < self.ref_views[view]["setup_wns_ps"] - allowance - self.tol)
            equal(sorted(record["failures"]), sorted(failures), f"physical gates {path}")
        else:
            need(bool(record["failures"]) and set(failures) <= set(record["failures"]), f"unexplained physical reject {path}")
            need(not all((complete(route, text, "IBEX_ROUTE_COMPLETE"),
                          set(f"STA_{view}" for view in CORNERS) <= ops.keys(),
                          all(ops.get(f"STA_{view}", {}).get("returncode") == 0 for view in CORNERS))),
                 f"incomplete STA despite successful operations {path}")
        self.endpoint(record["endpoint"], directory, area if views else self.area, views or self.ref_views,
                      bool(views and not failures), noop)
        near(max(record["wall_seconds"], sum(op["wall_seconds"] for op in ops.values())),
             record["wall_seconds"], f"physical wall below tool times {path}")
        if not noop:
            need("SEC" not in ops, f"candidate measured before timing policy claimed SEC {path}")
            self.physical[path] = record
        else:
            self.noop_proven = self.proof(directory, ops, artifacts["v"], passed=True)
            need(self.noop_proven, "qualified shared no-op SEC")
        return record

    def request(self, path, actions, pct, protect, primary):
        need(path not in self.logical_paths, f"duplicate logical receipt {path}")
        self.logical_paths.add(path)
        raw = read(path)
        equal(raw["actions"], list(actions), f"logical actions {path}")
        key = tuple(actions)
        expected_cache = not primary and key in self.cache
        equal(raw["from_physical_cache"], expected_cache, f"exact tuple cache flag {path}")
        self.request_count += 1
        self.cache_hits += int(expected_cache)
        physical_path = Path(raw["physical_receipt"])
        if expected_cache:
            equal(physical_path, self.cache[key], f"first exact-tuple receipt {path}")
        else:
            need(physical_path not in self.physical, f"shared fresh measurement {path}")
            destination = (path.parent / f"{path.stem}_physical" if primary else
                           self.root / "physical" / f"{len(self.physical) + 1:04d}")
            equal(physical_path, destination / "receipt.json", f"fresh measurement location {path}")
        physical = self.verify_physical(physical_path, key)
        views = physical["views"]
        if not primary or (physical["routed_to_completion"] and physical["extracted_to_completion"] and views):
            self.cache.setdefault(key, physical_path)
        failures = list(physical["failures"])
        if views:
            failures.extend(self.setup_gates(views, pct, protect))
        passed, seconds = False, physical["wall_seconds"]
        if not failures:
            proof_path = physical_path.with_name("deferred_proof.json")
            equal(raw["deferred_proof_receipt"], str(proof_path), f"conditional SEC binding {path}")
            if physical_path not in self.proofs:
                proof = read(proof_path)
                equal(proof["endpoint_id"], physical["endpoint_id"], f"deferred proof endpoint {path}")
                equal(proof["candidate"], physical["artifacts"]["v"], f"deferred proof netlist {path}")
                proven = self.proof(physical_path.parent, proof["operations"], proof["candidate"], passed=proof["sec_pass"])
                if "SEC" in proof["operations"]:
                    near(proof["wall_seconds"], proof["operations"]["SEC"]["wall_seconds"], f"SEC wall {path}")
                self.proofs[physical_path] = (proof, proven)
            proof, _ = self.proofs[physical_path]
            passed = proof["sec_pass"]
            equal(not proof["failures"], passed, f"deferred SEC reasons {path}")
            failures.extend(proof["failures"])
            seconds += proof["wall_seconds"]
        else:
            equal(raw["deferred_proof_receipt"], None, f"proof on pre-SEC rejected candidate {path}")
        equal(raw["failures"], failures, f"independent logical gates {path}")
        near(raw["wall_seconds"], seconds, f"charged seconds {path}")
        equal(raw["endpoint"], {**physical["endpoint"], "valid": passed, "sec_pass": passed}, f"logical endpoint {path}")
        for metric in ("setup_wns_ps", "setup_tns_ps"):
            equal(raw[metric], {view: values[metric] for view, values in views.items()}, f"logical {metric} {path}")
        return raw

    def totals(self, paths):
        counts = Counter({key: 0 for key in COUNT_KEYS})
        seconds = 0.0
        for path in paths:
            physical, (proof, _) = self.physical[path], self.proofs.get(path, (None, None))
            counts.update(count_physical(physical, proof))
            seconds += physical["wall_seconds"] + (proof["wall_seconds"] if proof else 0)
        return dict(counts, measured_endpoints=len(paths),
                    distinct_action_tuples=len({tuple(self.physical[path]["actions"]) for path in paths}),
                    actual_evaluation_seconds=seconds)

    def gate_summary(self, record, pct, protect):
        budget = self.period * (pct / 100)
        near(record["budget_ps"], budget, "reported WNS budget")
        equal(record["protect_clean_setup_views"], protect, "policy floor mode")
        for view, ref in self.ref_views.items():
            floor = ref["setup_wns_ps"] - budget
            if protect and ref["setup_wns_ps"] >= 0:
                floor = max(0, floor)
            near(record["setup_floor_ps_by_view"][view], floor, f"nominal WNS floor {view}")
            near(record["setup_tns_budget_ps_by_view"][view],
                 max(10 * budget, abs(ref["setup_tns_ps"]) * (pct / 100)), f"TNS budget {view}")

    def prefix(self, checkpoints, limit):
        selected, count = self.ref["endpoint"], 0
        for elapsed, accepted, ep in checkpoints:
            if elapsed > limit:
                break
            count += 1
            if accepted:
                selected = ep
        return {"completed_attempts": count, "selected": selected, "area_saved": self.area - selected["area"]}

    def verify_order(self, directory, trace):
        method = directory.name
        batch_size = 1 if method == "single" else self.config["batch_size"]
        cap = len(trace)
        ranked = [action["action_id"] for action in self.pool]
        queue, deferred, committed = [], [], []
        defer_reasons = set(self.config.get("split_deferral_reasons", ()))
        offset = 0
        for idx, receipt in enumerate(trace):
            if not queue:
                if offset < len(ranked):
                    count = min(batch_size, len(ranked) - offset) if cap - idx > 1 else 1
                    queue.append(ranked[offset:offset + count])
                    offset += count
                else:
                    need(bool(deferred), f"trace exceeds candidate pool {directory} {idx + 1}")
                    queue.extend(deferred.pop(0))
            chunk = queue.pop(0)
            equal(receipt["actions"], sorted(committed + chunk), f"scheduled action order {directory} {idx + 1}")
            defer = False
            if receipt["accepted"]:
                committed.extend(chunk)
            elif method == "faeco" and len(chunk) > 1 and idx + 1 < cap:
                mid = len(chunk) // 2
                children = [chunk[:mid], chunk[mid:]]
                if offset < len(ranked) and defer_reasons:
                    failure = read(directory / f"{idx + 1:02d}.json")["failures"]
                    defer = not defer_reasons.isdisjoint(failure)
                if defer:
                    deferred.append(children)
                else:
                    queue[0:0] = children
            equal(receipt.get("split_deferred", False), defer, f"split deferral {directory} {idx + 1}")

    def arm(self, directory, result, pct, protect, *, primary):
        equal(read(directory / "summary.json"), result, f"arm summary binding {directory}")
        count = self.config["budget_attempts_per_arm"]
        equal(result["evaluations_used"], count, f"candidate cap {directory}")
        equal(len(result["trace"]), count, f"trace cardinality {directory}")
        self.verify_order(directory, result["trace"])
        paths = [directory / f"{idx:02d}.json" for idx in range(1, count + 1)]
        equal(result["attempt_receipts"], [str(path) for path in paths], f"logical receipt manifest {directory}")
        committed, best = set(), self.ref["endpoint"]
        times, operations_before, proofs_before = [], set(self.physical), set(self.proofs)
        reject_reasons = Counter()
        proposed_widths = []
        for index, (path, trace) in enumerate(zip(paths, result["trace"], strict=True)):
            actions = trace["actions"]
            need(actions == sorted(set(actions)) and committed <= set(actions), f"cumulative action tuple {path}")
            growth = len(set(actions) - committed)
            proposed_widths.append(growth)
            equal(trace["batch_len"], growth, f"trace proposal cardinality {path}")
            if directory.name == "single":
                equal(growth, 1, f"singleton scheduling slot {path}")
            else:
                need(0 < growth <= self.config["batch_size"], f"batch size {path}")
                if index == count - 1 and growth != 1:
                    self.anomalies.append(f"{path.relative_to(self.root)} final slot contains {growth} edits")
            attempt = self.request(path, actions, pct, protect, primary)
            reject_reasons.update(attempt["failures"])
            ep = attempt["endpoint"]
            for key in ("area", "wns_ns", "hold_wns_ns"):
                equal(trace[key], ep[key], f"receipt-to-trace {key} {path}")
            equal(trace["feasible"], ep["valid"], f"trace feasibility {path}")
            accepted = ep["valid"] and ep["area"] < best["area"] - 1e-9
            equal(trace["accepted"], accepted, f"trace acceptance {path}")
            if accepted:
                best, committed = ep, set(actions)
            if primary:
                checkpoint = result["checkpoints"][index]
                equal((checkpoint["endpoint"], checkpoint["accepted"]), (ep, accepted), f"wall checkpoint {path}")
                elapsed = checkpoint["elapsed_seconds"]
                need(math.isfinite(elapsed) and elapsed >= (times[-1][0] if times else 0) + attempt["wall_seconds"] - 1e-8,
                     f"wall checkpoint precedes charged tool work {path}")
            else:
                elapsed = (times[-1][0] if times else 0) + attempt["wall_seconds"]
            times.append((elapsed, accepted, ep))
        equal(result["selected"], best, f"selected endpoint {directory}")
        equal(sorted(result["committed"]), sorted(committed), f"committed edits {directory}")
        near(result["area_saved"], self.area - best["area"], f"selected area delta {directory}")
        created = [path for path in self.physical if path not in operations_before]
        totals = self.totals(created)
        for key, value in totals.items():
            near(result["operations"][key], value, f"arm physical counts {key} {directory}")
        proof_on_cached = [str(path) for path in self.proofs if path in operations_before and path not in proofs_before]
        if not primary:
            near(result["charged_evaluation_seconds"], times[-1][0], f"arm charged seconds {directory}")
            return times, proof_on_cached
        equal(len(result["checkpoints"]), count, f"checkpoint cardinality {directory}")
        need(math.isfinite(result["wall_seconds"]) and result["wall_seconds"] >= times[-1][0], f"arm wall {directory}")
        equal(totals["route_attempts"], count, f"primary real DRT/RCX calls {directory}")
        limit = self.config["primary_wall_limit_seconds"]
        target_pct = self.config["primary_target_area_pct"]
        target = self.area * target_pct / 100
        first = next((elapsed for elapsed, accepted, ep in times
                      if accepted and self.area - ep["area"] >= target - 1e-9), None)
        within = first if first is not None and first <= limit else None
        prefix = self.prefix(times, limit)
        wall = result["wall_window"]
        for field in ("completed_attempts", "selected", "area_saved"):
            equal(wall[field], prefix[field], f"wall-window prefix {field} {directory}")
        equal(wall["time_to_target_seconds"], within, f"first target inside window {directory}")
        equal(wall["target_reached_in_window"], within is not None, f"target censoring {directory}")
        near(wall["wall_limit_seconds"], limit, f"wall limit {directory}")
        near(wall["target_area_pct"], target_pct, f"area percent target {directory}")
        near(wall["target_area_saved"], target, f"area target {directory}")
        near(wall["area_saved_pct"], 100 * prefix["area_saved"] / self.area, f"wall-window area percent {directory}")
        return {
            "within_candidate_cap": self.outcome(best),
            "within_wall_window": self.outcome(prefix["selected"]),
            "first_target_within_candidate_cap_seconds": first,
            "first_target_within_wall_window_seconds": within,
            "completed_attempts_inside_window": prefix["completed_attempts"],
            "wall_seconds": result["wall_seconds"],
            "physical_operations": totals,
            "proposed_chunk_sizes": proposed_widths,
            "accepted_trials": sum(accepted for _, accepted, _ in times),
            "rejected_trial_gate_counts": dict(reject_reasons),
        }

    def outcome(self, ep):
        directory = Path(ep["evidence_id"])
        views = self.ref_views if ep == self.ref["endpoint"] else self.physical[directory / "receipt.json"]["views"]
        _, proven = self.proofs.get(directory / "receipt.json", (None, None))
        return {
            "endpoint": ep["endpoint_id"], "area": ep["area"], "area_saved": self.area - ep["area"],
            "area_saved_pct": 100 * (self.area - ep["area"]) / self.area,
            "views": self.view_metrics(views), "sec_proven": proven,
        }

    def duplicate_primary(self, paths):
        groups = {}
        for path in paths:
            groups.setdefault(tuple(self.physical[path]["actions"]), []).append(self.physical[path])
        duplicates = []
        for actions, records in groups.items():
            if len(records) == 1:
                continue
            elapsed = [row["operations"]["DRT_RCX"]["wall_seconds"] for row in records]
            duplicates.append({
                "actions": actions,
                "endpoints": [row["endpoint_id"] for row in records],
                "same_artifact_hash": {
                    ext: all(ext in row.get("artifacts", {}) for row in records)
                    and len({row["artifacts"][ext]["sha256"] for row in records}) == 1
                    for ext in ("v", "def", "odb", "spef")
                },
                "same_all_view_slacks": all(row["views"] for row in records) and all(
                    len({row["views"][view][metric] for row in records}) == 1
                    for view in CORNERS for metric in METRICS
                ),
                "drt_rcx_wall_seconds": elapsed,
                "drt_rcx_wall_range_seconds": max(elapsed) - min(elapsed),
            })
        return duplicates

    def run(self, *, partial):
        result_path = self.root / "results.json"
        final = result_path.is_file()
        need(final or partial, f"final results unavailable {self.root}")
        result = read(result_path if final else self.root / "sweep_progress.json")
        noop = self.verify_physical(self.root / "noop/receipt.json", (), noop=True)
        if final:
            equal(result["status"], "matched", "completed result status")
            equal(result["scope"], self.scope, "result input scope")
            equal(result["control"], self.ref, "embedded control receipt")
            equal(result["shared_noop"], noop, "embedded no-op receipt")
            equal(result["control_operations"], count_physical(self.ref), "baseline operation counts")
            equal(result["shared_noop_operations"], count_physical(noop), "no-op operation counts")
            equal(result["clock_period_ps"], self.period, "result period")
        equal(self.config["methods_in_run_order"], list(METHODS), "arm order")
        equal(self.config["budget_attempts_per_arm"], 6, "protocol candidate cap")
        equal(self.config["setup_budget_percent_of_clock"], [0, 0.5, 1], "protocol budget grid")
        equal(self.config["primary_budget_pct"], 1, "protocol primary budget")
        equal(self.config["primary_mode"], "tradeoff", "protocol primary mode")
        equal(self.config["primary_target_area_pct"], 0.01, "protocol area target")
        equal(self.config["primary_wall_limit_seconds"], {"asap7": 1200, "sky130hd": 720}[self.config["pdk"]], "protocol wall cap")
        primary = result["primary"]
        self.gate_summary(primary, 1, False)
        equal(primary["mode"], "tradeoff", "result primary mode")
        equal(primary["budget_pct"], 1, "result primary budget")
        primary_data = {}
        for method in METHODS:
            if method in primary["results"]:
                primary_data[method] = self.arm(self.root / "primary_tradeoff_1pct" / method,
                                                primary["results"][method], 1, False, primary=True)
            else:
                need(not final, f"missing primary arm {method}")
        primary_paths = list(self.physical)
        primary_counts = self.totals(primary_paths)
        equal(primary_counts["route_attempts"], 6 * len(primary_data), "fresh primary physical count")
        equal(self.cache_hits, 0, "primary cache reads")
        primary_requests = self.request_count
        diagnostics = {}
        diagnostic_outcomes = {}
        diagnostic_new_proofs_on_cached = []
        for pct in self.config["setup_budget_percent_of_clock"]:
            key = f"{pct:g}"
            budget = result["budgets"].get(key)
            if budget is None:
                need(not final, f"missing diagnostic budget {key}")
                continue
            equal(budget["budget_pct"], pct, f"diagnostic percent {key}")
            diagnostics[key] = {}
            for mode, protect in (("protect", True), ("tradeoff", False)):
                value = budget["modes"].get(mode)
                if value is None:
                    need(not final, f"missing diagnostic mode {key} {mode}")
                    continue
                self.gate_summary(value, pct, protect)
                arms = {}
                for method in METHODS:
                    if method not in value["results"]:
                        need(not final, f"missing diagnostic arm {key} {mode} {method}")
                        continue
                    directory = self.root / f"budget_{key}pct" / mode / method
                    arm = value["results"][method]
                    times, delayed = self.arm(directory, arm, pct, protect, primary=False)
                    diagnostic_new_proofs_on_cached += delayed
                    arms[method] = times
                if "equal_charged_prefix_limit_seconds" not in value:
                    need(not final, f"missing diagnostic prefix {key} {mode}")
                    continue
                limit = min(times[-1][0] for times in arms.values())
                near(value["equal_charged_prefix_limit_seconds"], limit, f"diagnostic common time {key} {mode}")
                comparison = {}
                for method, times in arms.items():
                    prefix = self.prefix(times, limit)
                    equal(value["equal_charged_prefixes"][method], prefix, f"diagnostic first prefix {key} {mode} {method}")
                    selected = value["results"][method]["selected"]
                    for ep in (prefix["selected"], selected):
                        if ep["endpoint_id"] != "control" and ep["endpoint_id"] not in diagnostic_outcomes:
                            diagnostic_outcomes[ep["endpoint_id"]] = self.outcome(ep)
                    comparison[method] = {
                        "charged_evaluation_seconds": times[-1][0],
                        "area_saved_pct_at_candidate_cap": 100 * value["results"][method]["area_saved"] / self.area,
                        "area_saved_pct_at_equal_charged_prefix": 100 * prefix["area_saved"] / self.area,
                        "endpoint_at_candidate_cap": selected["endpoint_id"],
                        "endpoint_at_equal_charged_prefix": prefix["selected"]["endpoint_id"],
                        "evaluations_in_prefix": prefix["completed_attempts"],
                    }
                diagnostics[key][mode] = {"common_charged_seconds": limit, "arms": comparison}
        totals = self.totals(list(self.physical))
        totals.update(logical_requests=self.request_count, physical_cache_hits=self.cache_hits)
        for key, value in totals.items():
            near(result["physical_operations"][key], value, f"overall count {key}")
        if final:
            equal(self.request_count, 126, "all primary and diagnostic logical requests")
            logical = set(self.root.glob("primary_tradeoff_1pct/*/[0-9][0-9].json"))
            logical.update(self.root.glob("budget_*pct/*/*/[0-9][0-9].json"))
            equal(logical, self.logical_paths, "unaccounted logical receipts")
            on_disk = set(self.root.glob("primary_tradeoff_1pct/*/*_physical/receipt.json"))
            on_disk.update(self.root.glob("physical/*/receipt.json"))
            equal(on_disk, set(self.physical), "unaccounted physical receipts")
            proof_on_disk = {path.with_name("receipt.json") for path in self.root.rglob("deferred_proof.json")}
            equal(proof_on_disk, set(self.proofs), "unaccounted deferred proofs")
        if self.config.get("tns_gate") is False:
            self.anomalies.append("Legacy config.tns_gate=false contradicts setup_tns_loss_budget. The auditor verified the TNS gate on each logical request.")
        if diagnostic_new_proofs_on_cached:
            self.anomalies.append("Arm operations attribute SEC to the physical measurement that created the endpoint. Later proofs on cache hits are included in overall operations.")
        return {
            "pdk": self.config["pdk"], "complete": final, "scope": self.scope,
            "config_sha256": digest(self.root / "config.json"),
            "results_sha256": digest(result_path) if final else None,
            "candidate_pool_sha256": digest(self.root / "pool.json"),
            "original_sdc_sha256": self.assets["original_sdc"]["sha256"],
            "control_sdc_sha256": self.control["sdc"]["sha256"],
            "clock_period_ps": self.period,
            "control": self.outcome(self.ref["endpoint"]),
            "shared_noop_operations": count_physical(noop),
            "shared_noop_sec_proven": self.noop_proven,
            "primary_requests": primary_requests, "primary_wall_limit_seconds": primary["wall_limit_seconds"],
            "primary_target_area_pct": primary["target_area_pct"],
            "primary_operations": primary_counts, "primary": primary_data,
            "primary_duplicate_tuples": self.duplicate_primary(primary_paths),
            "diagnostic_requests": self.request_count - primary_requests,
            "diagnostic_proofs_on_already_measured_endpoints": diagnostic_new_proofs_on_cached,
            "diagnostic_endpoint_metrics": diagnostic_outcomes,
            "diagnostics": diagnostics, "physical_operations": totals, "anomalies": self.anomalies,
        }


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--partial", action="store_true", help="allow an atomically published live snapshot")
    args.add_argument("roots", type=Path, nargs="+")
    ns = args.parse_args()
    print(json.dumps({"audit": [Audit(root.resolve()).run(partial=ns.partial) for root in ns.roots]},
                     indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
