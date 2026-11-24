#!/usr/bin/env python3
"""Compare fixed AES batches with a targeted marker-informed three/six-edit plan."""

from argparse import ArgumentParser
from pathlib import Path

from probe_aes_selective_repair import read, verify
from run_aes_incident_priority_matched_v2 import CorrectedComparison, comparison
from run_aes_protected_online import drc_neighbor_evidence
from run_screened_matrix import bind_runtime, raw_seconds


METHODS = ("fixed", "repair")
SIX_RANKS = (4, 6, 12, 13, 16, 17)


def run_planned_repair(reference, proposals, evaluate, policy):
    """Validate complete alternatives and retain the smallest qualified endpoint."""
    selected, trace = reference, []
    for actions in proposals:
        endpoint = evaluate(actions)
        accepted = comparison.assess(reference, endpoint, policy).feasible and endpoint.area < selected.area - 1e-9
        if accepted:
            selected = endpoint
        trace.append({"actions": list(actions), "accepted": accepted})
    return {"selected": selected, "trace": trace}


class MarkerRepairComparison(CorrectedComparison):
    def prepare_repair(self, preflight, v2, v3, offline):
        reference = super().prepare_pair(preflight)
        self.hints = {}
        self.sources = {
            "three": (v2 / "fixed/02/request.json", v2 / "fixed/02/initial/unlocked_drc/full_drc.rpt"),
            "six": (v3 / "faeco/05/request.json", offline / "restored_checks/full_drc.rpt"),
        }
        self.source_runs = v2, v3, offline
        source = Path(__file__).resolve()
        self.config["driver_sources"][source.name] = comparison.bind(source)
        (self.output / "producer_sources" / source.name).write_bytes(source.read_bytes())
        self.config.update({
            "methods": list(METHODS),
            "development_case": "AES prior marker-informed exact six- and three-edit alternatives",
            "planned_hinted_passes": 1,
            "hint_inputs": {name: [str(path) for path in paths] for name, paths in self.sources.items()},
            "physical_cache": "disabled, including prior endpoint and preflight results",
        })
        comparison.save(self.output / "config.json", self.config)
        return reference

    def prepare_hints(self, pool):
        start = raw_seconds()
        v2, v3, offline = self.source_runs
        for root in (v2, v3):
            if read(root / "config.json")["matrix"] != self.config["matrix"]:
                raise ValueError("marker source uses another frozen matrix")
        v2_verified = read(v2 / "independent_verification.json")["arms"]["fixed"]
        v3_verified = read(v3 / "independent_verification.json")["arms"]["faeco"]
        if not v2_verified["window"]["target_reached_in_window"] or v3_verified["logical_admitted"] != 5:
            raise ValueError("marker sources do not describe the prior verified three and censored six")
        offline_inputs = read(offline / "offline_completion_inputs.json")
        old_six = read(verify(offline_inputs["original_routed_receipt"]))
        if verify(offline_inputs["original_routed_receipt"]) != v3 / "faeco/05/initial/receipt.json":
            raise ValueError("offline full-block audit does not bind the six edits")
        frozen_three = tuple(sorted(a.action_id for a in pool[3:6]))
        frozen_six = tuple(sorted(pool[rank - 1].action_id for rank in SIX_RANKS))
        hints, bindings = {}, {}
        for name, actions, expected_marker_count in (("three", frozen_three, 4), ("six", frozen_six, 8)):
            request_path, marker_path = self.sources[name]
            request = read(request_path)
            edited, incident = self.direct_nets(actions)
            if request["actions"] != list(actions) or request["direct_signal_nets"] != sorted(incident):
                raise ValueError(f"marker evidence and candidate do not match: {name}")
            audit_dir = marker_path.parent
            audit = read(audit_dir / "audit.json")
            if verify(audit["report"]) != marker_path or audit["drc_markers"] != expected_marker_count:
                raise ValueError(f"independent DRC marker record changed: {name}")
            if name == "six" and (old_six["actions"] != list(actions)
                    or audit["normalized_geometry"]["sha256"] != offline_inputs["original_pre_termination_normalized_def"]["sha256"]):
                raise ValueError("restored report does not describe the censored six layout")
            neighbors, evidence = drc_neighbor_evidence((marker_path,), incident, edited, self.nets)
            expected_count = 2 if name == "three" else 4
            if len(evidence) != expected_marker_count or len(neighbors) != expected_count:
                raise ValueError(f"marker evidence does not account for every protected neighbor: {name}")
            hints[name] = {"actions": actions, "incident_nets": sorted(incident),
                           "released_neighbors": sorted(neighbors), "marker_evidence": evidence}
            bindings[name] = {"request": comparison.bind(request_path), "marker_report": audit["report"]}
        stops = raw_seconds()
        proposals = (tuple(sorted(a.action_id for a in pool[:3])), frozen_three, frozen_six)
        comparison.save(self.output / "repair/marker_plan.json", {
            "actions": proposals, "hints": hints,
            "preparation": {"start_raw": start, "stop_raw": stops, "seconds": stops - start},
        })
        self.config["hint_sources"] = bindings
        comparison.save(self.output / "config.json", self.config)
        self.hints = {row["actions"]: set(row["released_neighbors"]) for row in hints.values()}
        return proposals

    def physical(self, actions, directory, incident, released):
        hinted = self.hints.get(actions)
        if hinted is None:
            return super().physical(actions, directory, incident, released)
        if directory.name != "initial" or released:
            raise ValueError("hinted candidate expects one fresh physical invocation")
        endpoint, receipted, failures, _ = super().physical(actions, directory, incident, hinted)
        return endpoint, receipted, failures, []

    def arm(self, method, reference):
        if method == "fixed":
            return super().arm(method, reference)
        if method != "repair":
            raise ValueError(method)
        original = comparison.run_method

        def planned(method_name, reference, pool, evaluate, cap, batch, *, policy, **kwargs):
            if method_name != "repair" or batch != 3 or cap < 3:
                raise ValueError("unexpected marker-schedule arguments")
            return run_planned_repair(reference, self.prepare_hints(pool), evaluate, policy)

        try:
            comparison.run_method = planned
            return super().arm(method, reference)
        finally:
            comparison.run_method = original
            self.hints = {}


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("matrix", "preflight", "v2", "v3", "offline", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    runner = MarkerRepairComparison(args.matrix.resolve(strict=True), args.output.resolve())
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        reference = runner.prepare_repair(*(path.resolve(strict=True) for path in
                                            (args.preflight, args.v2, args.v3, args.offline)))
        results = {}
        for method in METHODS:
            results[method] = runner.arm(method, reference)
            comparison.save(runner.output / "results.json", results)


if __name__ == "__main__":
    main()
