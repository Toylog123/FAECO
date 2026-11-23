from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from compare_ibex import CORNERS, Endpoint, PhysicalAction, bind
from run_setup_budget_sweep import TrialCache, budget_gate, run_sweep, summarize_wall_window


class FixtureEvaluator:
    def __init__(self, out, *, ff_droop=0.0, ss_tns_loss=0.0, proof_pass=True):
        self.args = SimpleNamespace(
            out=out, clock_period_ps=1000.0, budget_pcts=(0.0, 0.5, 1.0),
            primary_budget_pct=1.0, wall_limit_seconds=100, target_area_pct=1.0,
            max_evals=2, batch_size=1,
        )
        self.ref_views = {
            corner: {"setup_wns_ps": slack, "setup_tns_ps": -100.0}
            for corner, slack in zip(CORNERS, (0.38, -382.75, -1085.19), strict=True)
        }
        self.reference = Endpoint("control", 100, -0.38275, 0, 0, "test", str(out), True, True)
        self.ff_droop = ff_droop
        self.ss_tns_loss = ss_tns_loss
        self.proof_pass = proof_pass
        self.measured = []
        self.measurement_paths = []
        self.proven = []

    def evaluate(self, actions, out, *, envelope_only):
        if not envelope_only:
            raise ValueError("Fixture requires a physical-only evaluation")
        self.measured.append(actions)
        self.measurement_paths.append(out)
        out.mkdir()
        candidate = out / "routed.v"
        candidate.write_text("fixture", encoding="utf-8")
        views = {
            corner: {**self.ref_views[corner]} for corner in CORNERS
        }
        views["FF"]["setup_wns_ps"] -= self.ff_droop
        views["TT"]["setup_wns_ps"] -= 2
        views["SS"]["setup_tns_ps"] -= self.ss_tns_loss
        endpoint = Endpoint(
            str(out.relative_to(self.args.out)),
            100 - len(actions), -0.38475, 0, 0, "test", str(out), True, False,
        )
        record = {
            "endpoint_id": out.name, "views": views, "failures": [], "wall_seconds": 10.0,
            "artifacts": {"v": bind(candidate)}, "routed_to_completion": True,
            "extracted_to_completion": True, "operations": {
                "DRT_RCX": {}, **{f"STA_{corner}": {} for corner in CORNERS},
            },
        }
        return endpoint, record

    def proof(self, candidate, out, operations):
        if candidate.parent != out:
            raise ValueError("SEC proof must use the cached endpoint")
        self.proven.append(candidate)
        operations["SEC"] = {"wall_seconds": 3.0}
        return self.proof_pass


class SetupBudgetSweepTest(unittest.TestCase):
    def test_cached_route_only_invokes_sec_once_when_a_policy_qualifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            evaluator = FixtureEvaluator(Path(tmp))
            cache = TrialCache(evaluator)
            ep, charged = cache.request(("a",), budget_gate(evaluator, 0.0, True))
            self.assertFalse(ep.valid)
            self.assertEqual(charged["wall_seconds"], 10.0)
            self.assertEqual(evaluator.proven, [])
            ep, charged = cache.request(("a",), budget_gate(evaluator, 0.5, True))
            self.assertTrue(ep.valid)
            self.assertTrue(ep.sec_pass)
            self.assertEqual(charged["wall_seconds"], 13.0)
            ep, charged = cache.request(("a",), budget_gate(evaluator, 1.0, True))
            self.assertTrue(ep.valid)
            self.assertEqual(charged["wall_seconds"], 13.0)
            self.assertEqual(evaluator.measured, [("a",)])
            self.assertEqual(len(evaluator.proven), 1)

    def test_clean_corner_crossing_zero_skips_sec_even_within_relative_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            evaluator = FixtureEvaluator(Path(tmp), ff_droop=0.4)
            cache = TrialCache(evaluator)
            ep, receipt = cache.request(("a",), budget_gate(evaluator, 0.5, True))
            self.assertFalse(ep.valid)
            self.assertIn("FF:setup_floor", receipt["failures"])
            self.assertEqual(evaluator.proven, [])
            ep, receipt = cache.request(("a",), budget_gate(evaluator, 0.5, False))
            self.assertTrue(ep.valid)
            self.assertEqual(evaluator.measured, [("a",)])

    def test_tns_deterioration_can_prevent_sec_under_a_passing_wns_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            evaluator = FixtureEvaluator(Path(tmp), ss_tns_loss=51)
            cache = TrialCache(evaluator)
            ep, receipt = cache.request(("a",), budget_gate(evaluator, 0.5, False))
            self.assertFalse(ep.valid)
            self.assertEqual(receipt["failures"], ["SS:setup_tns_budget"])
            self.assertEqual(evaluator.proven, [])

    def test_failed_proof_is_cached_but_never_committed(self):
        with tempfile.TemporaryDirectory() as tmp:
            evaluator = FixtureEvaluator(Path(tmp), proof_pass=False)
            cache = TrialCache(evaluator)
            for pct in (0.5, 1.0):
                ep, receipt = cache.request(("a",), budget_gate(evaluator, pct, True))
                self.assertFalse(ep.valid)
                self.assertFalse(ep.sec_pass)
                self.assertIn("sec", receipt["failures"])
            self.assertEqual(len(evaluator.proven), 1)

    def test_primary_has_fresh_arms_and_diagnostics_share_first_measurement(self):
        with tempfile.TemporaryDirectory() as tmp:
            evaluator = FixtureEvaluator(Path(tmp))
            pool = [
                PhysicalAction(name, name, "old", "new", 1.0)
                for name in ("a", "b")
            ]
            preflight = {"operations": {}}
            passed, output = run_sweep(
                evaluator.args, evaluator, evaluator.reference, pool, preflight, preflight,
            )
            self.assertTrue(passed)
            strict = output["budgets"]["0"]["modes"]["protect"]["results"]
            relaxed = output["budgets"]["0.5"]["modes"]["tradeoff"]["results"]
            primary = output["primary"]["results"]
            for method in ("single", "fixed", "faeco"):
                self.assertEqual(strict[method]["evaluations_used"], 2)
                self.assertEqual(relaxed[method]["evaluations_used"], 2)
                self.assertEqual(strict[method]["trace"][1]["actions"], ["b"])
                self.assertEqual(relaxed[method]["trace"][1]["actions"], ["a", "b"])
                self.assertEqual(relaxed[method]["area_saved"], 2)
                self.assertEqual(primary[method]["operations"]["route_attempts"], 2)
                self.assertEqual(primary[method]["operations"]["sec_attempts"], 2)
                self.assertEqual(primary[method]["wall_window"]["area_saved"], 2)
                self.assertIsNotNone(primary[method]["wall_window"]["time_to_target_seconds"])
            self.assertEqual(evaluator.measured, [("a",), ("a", "b")] * 3 + [("b",)])
            self.assertEqual(len(set(evaluator.measurement_paths)), 7)
            self.assertEqual(output["physical_operations"]["logical_requests"], 42)
            self.assertEqual(output["physical_operations"]["physical_cache_hits"], 35)
            self.assertEqual(output["physical_operations"]["sec_attempts"], 6)

    def test_fixed_wall_checkpoint_never_claims_late_area(self):
        reference = Endpoint("control", 100, 0, 0, 0, "test", "control", True, True)
        checkpoints = [
            {"elapsed_seconds": 8, "accepted": True, "endpoint": {"area": 99}},
            {"elapsed_seconds": 12, "accepted": True, "endpoint": {"area": 96}},
        ]
        summary = summarize_wall_window(reference, checkpoints, wall_limit_seconds=10, target_area_pct=2)
        self.assertEqual(summary["completed_attempts"], 1)
        self.assertEqual(summary["area_saved"], 1)
        self.assertIsNone(summary["time_to_target_seconds"])


if __name__ == "__main__":
    unittest.main()
