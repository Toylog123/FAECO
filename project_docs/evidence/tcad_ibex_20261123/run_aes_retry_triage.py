#!/usr/bin/env python3
"""Evaluate hold-guided deferral of a DRC retry on the AES development case."""

from argparse import ArgumentParser
from pathlib import Path

import run_aes_incident_priority_matched as matched
from probe_aes_selective_repair import read
from run_aes_incident_priority_matched_v2 import CorrectedComparison, comparison
from run_aes_protected_online import drc_neighbor_evidence
from run_screened_matrix import RELATIVE_HOLD_REASONS, bind_runtime


DEFERRED_RETRY = "preliminary_hold_retry_deferred"
DRC_REASONS = frozenset(("drc", "full_drc", "unlocked_drc"))


class RetryTriageComparison(CorrectedComparison):
    def prepare_development(self, preflight, baseline):
        reference = super().prepare_pair(preflight)
        unchanged = self.config.keys() - {"driver_pid", "driver_sources"}
        previous = read(baseline / "config.json")
        if any(previous[key] != self.config[key] for key in unchanged):
            raise ValueError("V2/V3 inputs, physical gates or wall budget differ")
        evidence = baseline / "independent_verification.json"
        if set(read(evidence)["arms"]) != set(matched.METHODS):
            raise ValueError("V2 must have a completed independent audit")
        source = Path(__file__).resolve()
        self.config["driver_sources"][source.name] = comparison.bind(source)
        (self.output / "producer_sources" / source.name).write_bytes(source.read_bytes())
        self.config.update({
            "methods": ["faeco"], "development_case": "AES",
            "defer_marker_retry_reason": DEFERRED_RETRY,
            "defer_marker_retry_policy": "defer a legal marker retry after a preliminary relative-hold miss in any view",
            "baseline_v2": {name: comparison.bind(baseline / name)
                            for name in ("config.json", "results.json", evidence.name)},
        })
        comparison.save(self.output / "config.json", self.config)
        return reference

    def physical(self, actions, directory, incident, released):
        endpoint, receipt, failures, reports = super().physical(actions, directory, incident, released)
        hold_reasons = sorted(RELATIVE_HOLD_REASONS.intersection(failures))
        unrelated = {reason for reason in set(failures) - DRC_REASONS if not reason.startswith(("FF:", "TT:", "SS:"))}
        if directory.name != "initial" or not actions or not reports or not hold_reasons or unrelated:
            return endpoint, receipt, failures, reports
        if DRC_REASONS.isdisjoint(failures):
            return endpoint, receipt, failures, reports

        edited = {comparison.canonical_odb_name(self.eval.actions[key].instance) for key in actions}
        neighbors, markers = drc_neighbor_evidence(reports, incident, edited, self.nets)
        if not neighbors:
            return endpoint, receipt, failures, reports

        comparison.save(directory.parent / "deferred_retry.json", {
            "reason": DEFERRED_RETRY, "preliminary_assessment": comparison.bind(directory / "assessment.json"),
            "preliminary_relative_hold_reasons": hold_reasons, "reported_retry_neighbors": sorted(neighbors),
            "marker_evidence": markers, "actions": list(actions),
        })
        # The preliminary report documents the original hold values. Only legal layouts
        # give a final timing rejection, so use a distinct reason to defer this request.
        return endpoint, receipt, failures + [DEFERRED_RETRY], []

    def arm(self, method, reference):
        if method != "faeco":
            raise ValueError("the AES development contrast runs one FAECO arm")
        source = matched.RELATIVE_HOLD_REASONS
        try:
            matched.RELATIVE_HOLD_REASONS = source | {DEFERRED_RETRY}
            return super().arm(method, reference)
        finally:
            matched.RELATIVE_HOLD_REASONS = source


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("old_matrix", type=Path)
    parser.add_argument("baseline_v2", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("preflight", type=Path)
    args = parser.parse_args()
    runner = RetryTriageComparison(args.old_matrix.resolve(strict=True), args.output.resolve())
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        reference = runner.prepare_development(args.preflight.resolve(strict=True), args.baseline_v2.resolve(strict=True))
        result = runner.arm("faeco", reference)
        comparison.save(runner.output / "results.json", {"faeco": result})


if __name__ == "__main__":
    main()
