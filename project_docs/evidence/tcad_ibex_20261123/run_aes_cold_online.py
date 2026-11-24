#!/usr/bin/env python3
"""Evaluate live diagnostics for protected post-route AES area recovery."""

from argparse import ArgumentParser
from pathlib import Path
import re

from run_aes_diagnostic_repair import DiagnosticRepairComparison
from run_aes_incident_priority_matched_v2 import CorrectedComparison, comparison
from run_aes_protected_online import drc_neighbor_evidence
from run_screened_matrix import bind_runtime, raw_seconds


METHODS = ("fixed", "fixed_online", "faeco")
PREVIEW_LIMIT = 60.0
PREVIEW_COMPLETE = "FAECO_PRE_DRT_DRC_COMPLETE"
CLEAR_EVENT = 'puts "IBEX_CLEARED_SIGNAL_WIRES $cleared"\n'


def diagnostic_tcl(route_script, report):
    """Use the original swap/clear prefix on ROUTED CONTROL and exit after DRC."""
    if route_script.count(CLEAR_EVENT) != 1:
        raise ValueError("expected one direct wire clearing boundary in the route script")
    prefix = route_script.split(CLEAR_EVENT, 1)[0] + CLEAR_EVENT
    return f"{prefix}drt::check_drc -output_file {comparison.tcl(report)}\nputs {PREVIEW_COMPLETE}\nexit\n"


class ColdOnlineComparison(DiagnosticRepairComparison):
    def prepare_online(self, preflight):
        reference = self.prepare_pair(preflight)
        self.initial_hint = set()
        source = Path(__file__).resolve()
        parent = Path(DiagnosticRepairComparison.attempt.__code__.co_filename).resolve()
        for module in (source, parent):
            self.config["driver_sources"][module.name] = comparison.bind(module)
            (self.output / "producer_sources" / module.name).write_bytes(module.read_bytes())
        self.config.update({"methods": list(METHODS), "diagnostic_methods": list(METHODS[1:]),
                            "diagnostic_strategy": "fresh pre-DRT local swap and erase on frozen ROUTED control",
                            "diagnostic_timeout_seconds": PREVIEW_LIMIT, "diagnostic_threads": 1,
                            "physical_cache": "disabled, no candidate-specific diagnostic input"})
        comparison.save(self.output / "config.json", self.config)
        return reference

    def diagnose(self, actions, directory):
        start = raw_seconds()
        directory.mkdir(parents=True)
        edited, incident = self.direct_nets(actions)
        _, edits = self.eval.expected_masters(actions)
        report, script = directory / "full_drc.rpt", directory / "preview.tcl"
        complete = comparison.render_route(self.eval.args, self.eval.libraries["TT"], self.eval.control, directory, edits)
        script.write_text(diagnostic_tcl(complete, report), encoding="utf-8")
        result = comparison.run_process([self.tools["openroad"], "-no_init", "-no_splash", "-threads", "1", "-exit", script],
                                        directory / "preview.log", PREVIEW_LIMIT)
        count, neighbors, evidence, failure = None, set(), [], None
        try:
            log = comparison.checked_output(result, PREVIEW_COMPLETE)
            touched = set(re.findall(r"(?m)^IBEX_TOUCHED_NET (.+)$", log))
            cleared = re.findall(r"(?m)^IBEX_CLEARED_SIGNAL_WIRES (\d+)$", log)
            expected_cleared = sum("+ ROUTED " in self.nets[net] or "+ FIXED " in self.nets[net] for net in incident)
            if touched != incident or cleared != [str(expected_cleared)] or not report.is_file():
                raise comparison.TrialFailure("preview did not clear the expected direct wires or report DRC")
            text = report.read_text(encoding="utf-8")
            count = len(re.findall(r"(?m)^violation type: ", text))
            if not count and text.strip():
                raise comparison.TrialFailure("unrecognized preview DRC report")
            neighbors, evidence = drc_neighbor_evidence((report,), incident, edited, self.nets)
            if len(evidence) != count:
                neighbors = set()
        except comparison.TrialFailure as error:
            failure = str(error)
        stop = raw_seconds()
        comparison.save(directory / "diagnosis.json", {"actions": list(actions), "incident_nets": sorted(incident),
            "released_neighbors": sorted(neighbors), "marker_evidence": evidence, "marker_count": count,
            "status": "unavailable" if failure else "guided" if neighbors else "no_complete_guidance", "failure": failure,
            "report": comparison.bind(report) if report.is_file() else None, "script": comparison.bind(script),
            "start_raw": start, "stop_raw": stop, "seconds": stop - start})
        return neighbors

    def attempt(self, actions, directory):
        if self.use_preview:
            self.initial_hint = self.diagnose(actions, directory.parent / "diagnosis" / directory.name)
        try:
            return super().attempt(actions, directory)
        finally:
            self.initial_hint = set()

    def arm(self, method, reference):
        self.use_preview = method in METHODS[1:]
        original = comparison.run_method

        def dispatch(name, *args, **kwargs):
            return original("fixed" if name == "fixed_online" else name, *args, **kwargs)

        try:
            comparison.run_method = dispatch
            return CorrectedComparison.arm(self, method, reference)
        finally:
            comparison.run_method = original
            self.use_preview = False


def main():
    parser = ArgumentParser(description=__doc__)
    for name in ("matrix", "preflight", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    runner = ColdOnlineComparison(args.matrix.resolve(strict=True), args.output.resolve())
    with bind_runtime(runner.top, runner.flow["fastroute.tcl"]):
        reference = runner.prepare_online(args.preflight.resolve(strict=True))
        results = {}
        for method in METHODS:
            results[method] = runner.arm(method, reference)
            comparison.save(runner.output / "results.json", results)


if __name__ == "__main__":
    main()
