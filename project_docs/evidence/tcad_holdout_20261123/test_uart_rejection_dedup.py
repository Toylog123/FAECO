"""Test the evidence gate for same-arm setup rejection reuse."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from run_uart_rejection_dedup import comparison, setup_only_rejection


class SetupRejectionTest(unittest.TestCase):
    def test_only_complete_setup_rejections_are_reused(self):
        cases = [(["FF:setup_budget"], True), (["SS:setup_tns_budget", "TT:setup_budget"], True),
                 (["FF:setup_budget", "SS:hold_regression"], False), (["FF:setup_budget", "unlocked_drc"], False),
                 (["route"], False), ([], False)]
        for reasons, reusable in cases:
            with self.subTest(reasons=reasons), TemporaryDirectory() as directory:
                root = Path(directory)
                initial = root / "initial"
                initial.mkdir()
                endpoint = comparison.Endpoint("e", 1.0, -0.05, -0.1, 0.01, "same-scope",
                                               str(initial), False, False)
                data = initial / "receipt.json"
                comparison.save(data, {"views": {corner: {} for corner in comparison.CORNERS}})
                result = root / "result.json"
                comparison.save(result, {"actions": ["a"], "scope_id": "same-scope", "failures": reasons,
                                         "physical_receipt": comparison.bind(data)})
                comparison.save(initial / "assessment.json", {"unlocked": {"drc_markers": 0}, "failures": reasons})
                recorded = setup_only_rejection(endpoint, ("a",))
                self.assertEqual(recorded, comparison.bind(result) if reusable else None)
                if reusable:
                    with self.assertRaisesRegex(ValueError, "cumulative action and scope"):
                        setup_only_rejection(endpoint, ("b",))
