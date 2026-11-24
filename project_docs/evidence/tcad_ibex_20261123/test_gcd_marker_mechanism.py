from types import SimpleNamespace
import unittest

from run_gcd_marker_mechanism import PROTOCOL_ORDER, fixed_proposal, run_fixed_proposal


class GcdMarkerMechanismTest(unittest.TestCase):
    def test_blocked_order_and_frozen_proposal(self):
        pool = [SimpleNamespace(action_id=f"action_{rank:02d}") for rank in range(1, 19)]
        self.assertEqual(PROTOCOL_ORDER, ("ordinary", "online", "online", "ordinary"))
        self.assertEqual(fixed_proposal(pool), ("action_13", "action_14", "action_15"))
        with self.assertRaises(ValueError):
            fixed_proposal(pool[:-1])

    def test_one_trial_returns_reference_for_rejection_or_no_gain(self):
        reference = SimpleNamespace(valid=True, area=100.0)
        for feasible, area, accepted in ((False, 99.0, False), (True, 100.0, False), (True, 99.0, True)):
            endpoint = SimpleNamespace(valid=feasible, area=area)
            calls = []

            def evaluate(actions):
                calls.append(actions)
                return endpoint

            def assess(_reference, trial, _policy):
                return SimpleNamespace(feasible=trial.valid)

            trace = run_fixed_proposal("ordinary", "ordinary", reference, evaluate, ("action_13",), 1, None, assess)
            self.assertEqual(calls, [("action_13",)])
            self.assertEqual(trace["selected"], endpoint if accepted else reference)
            self.assertEqual(trace["trace"], [{"accepted": accepted}])
