#!/usr/bin/env python3
"""Compare fresh protected ECO routing with and without a bound DRC diagnosis."""

from argparse import ArgumentParser
from pathlib import Path
import re

from probe_aes_selective_repair import read, verify
from run_aes_incident_priority_matched_v2 import CorrectedComparison, comparison
import run_aes_protected_online as protection
from run_screened_matrix import bind_runtime, raw_seconds


METHODS = ("retry_1", "guided_1", "guided_2", "retry_2")


def diagnostic_hint(sources, matrix, sdc, actions, edited, incident, nets):
    """Bind the marker report to this candidate and route before opening neighbor nets."""
    request, routed, audit_inputs, audit = (
        read(verify(sources[key])) for key in ("request", "physical", "audit_inputs", "audit_summary")
    )
    if (request["actions"] != list(actions) or routed["actions"] != list(actions)
            or request["direct_signal_nets"] != sorted(incident)):
        raise ValueError("diagnostic packet refers to a different candidate")
    if (audit_inputs["matrix_config"] != matrix or not routed["routed_to_completion"]
            or routed["control_sdc"] != sdc
            or any(audit_inputs[f"input_{kind}"] != routed["artifacts"][kind] for kind in ("odb", "def"))):
        raise ValueError("diagnostic packet describes a different physical input")
    for item in (matrix, sdc, audit_inputs["input_odb"], audit_inputs["input_def"], audit["normalized_geometry"]):
        verify(item)
    report = verify(audit["report"])
    count = len(re.findall(r"(?m)^violation type: ", report.read_text(encoding="utf-8")))
    if count != audit["drc_markers"]:
        raise ValueError("diagnostic marker count does not match the restored report")
    neighbors, evidence = protection.drc_neighbor_evidence((report,), incident, edited, nets)
    return (neighbors if len(evidence) == count else set()), evidence


class DiagnosticRepairComparison(CorrectedComparison):
    def prepare_case(self, preflight, request, physical, audit_dir):
        reference = super().prepare_pair(preflight)
        self.initial_hint = set()
        self.actions = tuple(read(request)["actions"])
        if not self.actions or self.actions != tuple(sorted(set(self.actions))) or not set(self.actions) <= self.eval.actions.keys():
            raise ValueError("expected a canonical request from the frozen candidate pool")
        self.sources = {key: comparison.bind(path) for key, path in {
            "request": request, "physical": physical, "audit_inputs": audit_dir / "inputs.json",
            "audit_summary": audit_dir / "audit.json",
        }.items()}
        source = Path(__file__).resolve()
        self.config["driver_sources"][source.name] = comparison.bind(source)
        (self.output / "producer_sources" / source.name).write_bytes(source.read_bytes())
        self.config.update({"methods": list(METHODS), "case_actions": list(self.actions), "logical_requests_per_arm": 1,
                            "diagnostic_sources": self.sources, "physical_cache": "disabled for every arm",
                            "guidance_policy": "use only a bound complete independent DRC with actionable neighbors for every marker"})
        comparison.save(self.output / "config.json", self.config)
        return reference

    def prepare_guidance(self, directory):
        start = raw_seconds()
        edited, incident = self.direct_nets(self.actions)
        neighbors, evidence = diagnostic_hint(self.sources, self.config["matrix"], comparison.bind(self.eval.control["sdc"]),
                                              self.actions, edited, incident, self.nets)
        count = read(verify(self.sources["audit_summary"]))["drc_markers"]
        stop = raw_seconds()
        comparison.save(directory / "hint.json", {"actions": list(self.actions), "incident_nets": sorted(incident),
            "released_neighbors": sorted(neighbors), "marker_evidence": evidence, "marker_count": count,
            "status": "guided" if neighbors else "no_complete_guidance",
            "preparation": {"start_raw": start, "stop_raw": stop, "seconds": stop - start}})
        self.initial_hint = neighbors

    def attempt(self, actions, directory):
        if not self.initial_hint:
            return super().attempt(actions, directory)
        original = protection.drc_neighbor_evidence

        def new_neighbors(reports, incident, edited, nets):
            return original(reports, incident | self.initial_hint, edited, nets)

        try:
            protection.drc_neighbor_evidence = new_neighbors
            return super().attempt(actions, directory)
        finally:
            protection.drc_neighbor_evidence = original

    def physical(self, actions, directory, incident, released):
        return super().physical(actions, directory, incident, released | self.initial_hint)

    def arm(self, method, reference):
        original = comparison.run_method

        def one_candidate(method_name, reference, pool, evaluate, cap, batch, *, policy, **kwargs):
            if method_name != method or cap < 1:
                raise ValueError("expected one exact-candidate trial in this arm")
            if method.startswith("guided_"):
                self.prepare_guidance(self.output / method)
            endpoint = evaluate(self.actions)
            accepted = comparison.assess(reference, endpoint, policy).feasible and endpoint.area < reference.area - 1e-9
            return {"selected": endpoint if accepted else reference, "trace": [{"accepted": accepted}]}

        try:
            comparison.run_method = one_candidate
            return super().arm(method, reference)
        finally:
            comparison.run_method = original
            self.initial_hint = set()


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("matrix", "preflight", "request", "physical", "audit_dir", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    runner = DiagnosticRepairComparison(args.matrix.resolve(strict=True), args.output.resolve())
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        reference = runner.prepare_case(*(path.resolve(strict=True) for path in
                                          (args.preflight, args.request, args.physical, args.audit_dir)))
        results = {}
        for method in METHODS:
            results[method] = runner.arm(method, reference)
            comparison.save(runner.output / "results.json", results)


if __name__ == "__main__":
    main()
