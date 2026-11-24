"""Verify candidate identity and fail-closed scope selection for DRC guidance."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import compare_ibex as comparison
from probe_aes_selective_repair import read
from run_aes_protected_online import OnlineProtection, drc_neighbor_evidence
from run_aes_diagnostic_repair import DiagnosticRepairComparison

if not os.environ.get("FAECO_AES_BEFORE_DIAGNOSTIC_BINDING"):
    from run_aes_diagnostic_repair import diagnostic_hint


class DiagnosticBindingTest(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.actions = ("edit=small",)
        self.nets = {"data": "+ USE SIGNAL + ROUTED met1", "near": "+ USE SIGNAL + ROUTED met1",
                     "clock": "+ USE CLOCK + ROUTED met1"}
        self.matrix = self.file("matrix.json", {})
        self.sdc = self.file("control.sdc", "frozen SDC")
        self.database = self.file("routed.odb", "routed database")
        self.geometry = self.file("routed.def", "routed geometry")
        self.report = self.file("full_drc.rpt", "violation type: Short\n srcs: inst:edit net:near net:clock\n")
        self.normalized = self.file("normalized.def", "restored geometry")
        self.sources = {
            "request": self.file("request.json", {"actions": self.actions, "direct_signal_nets": ["data"]}),
            "physical": self.file("receipt.json", {
                "actions": self.actions, "control_sdc": self.sdc, "routed_to_completion": True,
                "artifacts": {"odb": self.database, "def": self.geometry},
            }),
            "audit_inputs": self.file("inputs.json", {"input_odb": self.database, "input_def": self.geometry,
                                                     "matrix_config": self.matrix}),
            "audit_summary": self.file("audit.json", {"report": self.report, "drc_markers": 1,
                                                       "normalized_geometry": self.normalized}),
        }

    def file(self, name, body):
        path = self.root / name
        if isinstance(body, str):
            path.write_text(body, encoding="utf-8")
        else:
            comparison.save(path, body)
        return comparison.bind(path)

    def load(self, actions=None):
        actions = actions if actions is not None else self.actions
        if os.environ.get("FAECO_AES_BEFORE_DIAGNOSTIC_BINDING"):
            return drc_neighbor_evidence((Path(self.report["path"]),), {"data"}, {"edit"}, self.nets)[0]
        neighbors, _ = diagnostic_hint(self.sources, self.matrix, self.sdc, actions, {"edit"}, {"data"}, self.nets)
        return neighbors

    def test_only_wired_neighbor_signal_is_released(self):
        self.assertEqual(self.load(), {"near"})

    def test_rejects_a_report_from_another_candidate(self):
        with self.assertRaisesRegex(ValueError, "different candidate"):
            self.load(("other=small",))

    def test_rejects_an_audit_from_another_routed_geometry(self):
        foreign = self.file("foreign.def", "other geometry")
        self.sources["audit_inputs"] = self.file("inputs.json", {"input_odb": self.database, "input_def": foreign,
                                                               "matrix_config": self.matrix})
        with self.assertRaisesRegex(ValueError, "different physical input"):
            self.load()

    def test_falls_back_when_any_marker_has_no_actionable_neighbor(self):
        new_report = self.file("mixed.rpt", Path(self.report["path"]).read_text() +
                               "violation type: Short\n srcs: inst:other net:clock\n")
        self.sources["audit_summary"] = self.file("audit.json", {"report": new_report, "drc_markers": 2,
                                                                 "normalized_geometry": self.normalized})
        self.assertEqual(self.load(), set())


class GuidedRetryTest(unittest.TestCase):
    def test_retries_only_with_a_new_neighbor_and_keeps_the_initial_release(self):
        actions = ("edit=small",)
        runner = object.__new__(DiagnosticRepairComparison)
        runner.initial_hint = {"known"}
        runner.nets = {net: "+ USE SIGNAL + ROUTED met1" for net in ("direct", "known", "new")}
        runner.direct_nets = lambda _: ({"edit"}, {"direct"})
        runner.eval = SimpleNamespace(scope="frozen")
        endpoint = comparison.Endpoint("candidate", 90, 0, 0, 0.3, "frozen", "trial", False, False)
        invoked = []

        def physical(_, keys, directory, incident, released):
            self.assertEqual(keys, actions)
            self.assertEqual(incident, {"direct"})
            invoked.append(set(released))
            directory.mkdir()
            comparison.save(directory / "receipt.json", {})
            if directory.name == "retry":
                return endpoint, {}, ["FF:hold_regression"], []
            marker = directory / "full_drc.rpt"
            marker.write_text("violation type: Short\n srcs: inst:edit net:known net:new\n", encoding="utf-8")
            return endpoint, {}, ["full_drc"], [marker]

        with TemporaryDirectory() as scratch, patch.object(OnlineProtection, "physical", physical):
            candidate = Path(scratch) / "request"
            if os.environ.get("FAECO_AES_BEFORE_DIAGNOSTIC_BINDING"):
                _, record = OnlineProtection.attempt(runner, actions, candidate)
            else:
                _, record = runner.attempt(actions, candidate)
            self.assertEqual(record["passes"], ["initial", "retry"])
            self.assertEqual(invoked, [{"known"}, {"known", "new"}])
            self.assertEqual(read(candidate / "retry_decision.json")["released_neighbors"], ["new"])


if __name__ == "__main__":
    unittest.main()
