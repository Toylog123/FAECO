"""Check that the two schedulers are audited against distinct opening sizes."""

from types import SimpleNamespace
import unittest

from verify_aes_greedy_matched import verify_opening


class GreedyAuditTest(unittest.TestCase):
    def test_opening_matches_scheduler_not_backend(self):
        pool = [SimpleNamespace(action_id=action) for action in ("c", "a", "b")]
        single = [{"actions": ["c"]}]
        batch = [{"actions": ["a", "b", "c"]}]

        verify_opening("single", single, pool, 3)
        verify_opening("faeco", batch, pool, 3)
        with self.assertRaisesRegex(ValueError, "opening proposal"):
            verify_opening("single", batch, pool, 3)
        with self.assertRaisesRegex(ValueError, "opening proposal"):
            verify_opening("faeco", single, pool, 3)


if __name__ == "__main__":
    unittest.main()
