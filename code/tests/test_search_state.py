"""0a gate (step 3): G2 event contract + G3 checkpoint/restore consistency.

These tests are the executable form of
``project_docs/planning/FAECO_V2_IMPL_CONTRACT_20260923.md`` §2 (which state each
event updates) and §3 (what a checkpoint must contain and how it must restore).
"""

import json
import unittest

from rseco.failures import FailureType
from rseco.feedback import ADAPTIVE_CONFIG, LEGACY_CONFIG, FailureFeedbackState
from rseco.refinement import RefinementWeights
from rseco.search_state import (
    SCHEMA_VERSION,
    CheckpointError,
    SearchState,
    StateConsistencyError,
    split_attribution,
)

INITIAL = "module top();\nendmodule\n"


def make_state(**kwargs) -> SearchState:
    kwargs.setdefault("run_config", {"strategies": ["G", "B"], "seed": 1, "enable_feedback": True})
    return SearchState(initial_netlist_text=INITIAL, current_netlist_text=INITIAL, **kwargs)


def simulate(state: SearchState, *, start_round: int, rounds: int, accept_every: int = 3):
    """Deterministic round driver, shared by the resume-equivalence test."""
    pattern = [
        {FailureType.TIMING_GAIN_INSUFFICIENT},
        {FailureType.PATCH_TOO_LARGE, FailureType.TIMING_GAIN_INSUFFICIENT},
        {FailureType.EQUIVALENCE},
    ]
    for offset in range(rounds):
        state.begin_round()
        index = start_round + offset
        failures = pattern[index % len(pattern)]
        state.record_rejection(candidate_hash=f"cand-{index}", failures=failures, runtime_s=0.0)
        if (index + 1) % accept_every == 0:
            state.accept_patch(
                f"p{index}",
                state.current_netlist_text + f"// patch {index}\n",
                wns=-0.5 + 0.01 * index,
                tns=-1.0 + 0.02 * index,
                min_slack=-0.4 + 0.01 * index,
                critical_endpoints=[f"ep{index}"],
                critical_instances=[f"inst{index}"],
                cone_gates=[f"g{index}"],
            )
    return state


class G2EventContractTest(unittest.TestCase):
    def test_feedback_off_freezes_parameters_but_still_records(self):
        """Contract §2.3 ruling 1: only the feedback -> parameters edge is closed."""
        state = make_state(enable_feedback=False, feedback_config=ADAPTIVE_CONFIG)
        weights_before = state.refinement_weights
        feedback_before = state.failure_feedback

        for round_index in range(20):
            state.begin_round()
            state.record_rejection(
                candidate_hash=f"c{round_index}",
                failures={FailureType.TIMING_GAIN_INSUFFICIENT, FailureType.VERIFICATION_TOO_EXPENSIVE},
            )

        self.assertEqual(state.refinement_weights, weights_before)
        self.assertEqual(state.failure_feedback, feedback_before)
        self.assertEqual(state.cone_limit, 1000)
        # ... but classification, logging and de-duplication all still happened
        self.assertEqual(len(state.failure_history), 20)
        self.assertEqual(len(state.tested_candidate_hashes), 20)
        self.assertEqual(state.round_id, 20)

    def test_reject_never_touches_the_netlist(self):
        state = make_state()
        for round_index in range(5):
            state.begin_round()
            state.record_rejection(candidate_hash=f"c{round_index}", failures={FailureType.PATCH_TOO_LARGE})
        self.assertEqual(state.netlist_epoch, 0)
        self.assertEqual(state.accepted_patches, [])
        self.assertEqual(state.current_netlist_text, INITIAL)
        self.assertIsNone(state.current_wns)

    def test_accept_does_not_advance_the_ema(self):
        """Contract §2.3 ruling 3."""
        state = make_state(feedback_config=ADAPTIVE_CONFIG)
        state.begin_round()
        state.record_rejection(candidate_hash="c0", failures={FailureType.TIMING_GAIN_INSUFFICIENT})
        feedback_before = state.failure_feedback
        state.accept_patch("p1", INITIAL + "// a\n", wns=-0.3)
        self.assertEqual(state.failure_feedback, feedback_before)

    def test_rollback_restores_decision_state_atomically(self):
        """The weights/EMA/cone limit must go back with the netlist, not stay ahead."""
        state = make_state(feedback_config=LEGACY_CONFIG)
        state.begin_round()
        state.record_rejection(candidate_hash="c0", failures={FailureType.TIMING_GAIN_INSUFFICIENT})
        weights_at_accept = state.refinement_weights
        feedback_at_accept = state.failure_feedback
        cone_at_accept = state.cone_limit
        self.assertEqual(weights_at_accept.critical_coverage_reward, 2.0)

        state.accept_patch("p1", INITIAL + "// a\n", wns=-0.3)

        state.begin_round()
        state.record_rejection(candidate_hash="c1", failures={FailureType.TIMING_GAIN_INSUFFICIENT})
        self.assertEqual(state.refinement_weights.critical_coverage_reward, 3.0)

        self.assertTrue(state.rollback())
        self.assertEqual(state.refinement_weights, weights_at_accept)
        self.assertEqual(state.failure_feedback, feedback_at_accept)
        self.assertEqual(state.cone_limit, cone_at_accept)
        self.assertEqual(state.current_netlist_text, INITIAL)
        self.assertEqual(state.netlist_epoch, 0)
        self.assertIsNone(state.current_wns)

    def test_rollback_keeps_audit_and_budget_state(self):
        """Contract §2.3 ruling 2: undo the decision, keep the memory."""
        state = make_state()
        state.begin_round()
        state.record_rejection(candidate_hash="c0", failures={FailureType.PATCH_TOO_LARGE})
        state.reserve_budget("sta")
        state.accept_patch("p1", INITIAL + "// a\n", wns=-0.3)

        tested_before = set(state.tested_candidate_hashes)
        budget_before = dict(state.budget)
        history_len_before = len(state.failure_history)

        self.assertTrue(state.rollback())

        self.assertEqual(state.tested_candidate_hashes, tested_before)
        self.assertEqual(state.budget, budget_before)
        self.assertEqual(state.budget_used("sta"), 1)
        self.assertEqual(len(state.failure_history), history_len_before)

    def test_rollback_flags_invalidated_events(self):
        state = make_state()
        state.begin_round()
        state.accept_patch("p1", INITIAL + "// a\n", wns=-0.3)
        state.begin_round()
        state.record_rejection(candidate_hash="c-after", failures={FailureType.PATCH_TOO_LARGE})
        self.assertTrue(state.rollback())
        flagged = [event for event in state.failure_history if event.get("invalidated_by_rollback")]
        self.assertTrue(flagged)
        self.assertIn("c-after", {event.get("candidate_hash") for event in flagged})

    def test_rollback_on_empty_stack_is_a_clean_no_op(self):
        state = make_state()
        snapshot = json.dumps(state.to_dict(), sort_keys=True, default=str)
        self.assertFalse(state.rollback())
        self.assertFalse(state.rollback())
        self.assertEqual(json.dumps(state.to_dict(), sort_keys=True, default=str), snapshot)

    def test_rollback_refuses_a_broken_chain(self):
        """The snapshot must still describe the netlist the reconstruction produces."""
        state = make_state()
        simulate(state, start_round=0, rounds=6)
        self.assertEqual(len(state.accepted_patches), 2)
        state.accepted_patches[0]["netlist_text"] = "module tampered();\nendmodule\n"
        with self.assertRaises(StateConsistencyError):
            state.rollback()

    def test_invariants_hold_throughout(self):
        state = make_state()
        state.check_invariants()
        simulate(state, start_round=0, rounds=9)
        state.check_invariants()
        self.assertEqual(state.netlist_epoch, len(state.accepted_patches))
        self.assertGreaterEqual(state.round_id, state.netlist_epoch)

    def test_replay_matches_current_netlist(self):
        state = make_state()
        simulate(state, start_round=0, rounds=9)
        replayed = SearchState.replay(state.initial_netlist_text, state.accepted_patches)
        self.assertEqual(SearchState.hash_text(replayed), state.current_netlist_hash)

    def test_replay_rejects_a_non_contiguous_log(self):
        state = make_state()
        simulate(state, start_round=0, rounds=12)
        self.assertGreaterEqual(len(state.accepted_patches), 3)
        state.accepted_patches[1]["netlist_text"] = "module other();\nendmodule\n"
        with self.assertRaises(CheckpointError):
            SearchState.replay(state.initial_netlist_text, state.accepted_patches)


class CandidateIdentityTest(unittest.TestCase):
    def test_candidate_key_includes_the_base_netlist(self):
        """The gap the contract requires fixed: same cut, different epoch = new candidate."""
        state = make_state()
        cut_hash = state.candidate_hash(gates=["g1", "g2"], action_hash="sizing")
        self.assertTrue(state.mark_candidate_tested(cut_hash))
        self.assertFalse(state.mark_candidate_tested(cut_hash), "same epoch must de-duplicate")

        state.begin_round()
        state.accept_patch("p1", INITIAL + "// a\n", wns=-0.3)
        self.assertTrue(
            state.mark_candidate_tested(cut_hash),
            "the same cut on a new base netlist is a different candidate",
        )

    def test_stale_candidate_is_logged_without_touching_the_ema(self):
        state = make_state(feedback_config=ADAPTIVE_CONFIG)
        weights_before = state.refinement_weights
        feedback_before = state.failure_feedback
        tested_before = set(state.tested_candidate_hashes)

        state.record_stale_candidate(candidate_hash="c-stale", epoch_at_generation=0)

        self.assertEqual(state.refinement_weights, weights_before)
        self.assertEqual(state.failure_feedback, feedback_before)
        self.assertEqual(state.tested_candidate_hashes, tested_before)
        self.assertEqual(len(state.failure_history), 1)
        self.assertEqual(state.failure_history[0]["stage_tags"], ["W_STALE_CANDIDATE"])


class G4AttributionLayerTest(unittest.TestCase):
    def test_tool_layer_failures_never_move_weights(self):
        """Contract §4.1: W_* is tool failure, not method failure."""
        state = make_state(feedback_config=ADAPTIVE_CONFIG)
        weights_before = state.refinement_weights
        feedback_before = state.failure_feedback

        for round_index in range(20):
            state.begin_round()
            state.record_rejection(
                candidate_hash=f"w{round_index}",
                failures=set(),
                stage_tags=["W_ABC_TIMEOUT", "W_GRAFT_ERROR"],
            )

        self.assertEqual(state.refinement_weights, weights_before)
        self.assertEqual(state.failure_feedback, feedback_before)
        self.assertEqual(state.cone_limit, 1000)
        self.assertEqual(len(state.failure_history), 20)

    def test_short_circuit_records_no_double_attribution(self):
        """A W_*-rejected candidate never also produces an F1-F6 entry (§4.3 ruling 1)."""
        state = make_state()
        state.begin_round()
        state.record_rejection(
            candidate_hash="c0", failures=set(), stage_tags=["W_EXTRACT_INVARIANT"]
        )
        event = state.failure_history[-1]
        self.assertEqual(event["failures"], [])
        self.assertEqual(event["stage_tags"], ["W_EXTRACT_INVARIANT"])

    def test_f3_s_and_cec2_tags_are_classified(self):
        attributable, tags = split_attribution(
            {FailureType.PATCH_TOO_LARGE}, stage_tags=["S_TECHMAP_MISMATCH"]
        )
        self.assertEqual(attributable, {FailureType.PATCH_TOO_LARGE})
        self.assertEqual(tags, ["S_TECHMAP_MISMATCH"])

    def test_unknown_stage_tag_is_rejected(self):
        with self.assertRaises(ValueError):
            split_attribution(set(), stage_tags=["W_INVENTED_TAG"])


class G3CheckpointTest(unittest.TestCase):
    def test_round_trip_preserves_every_field(self):
        state = simulate(make_state(feedback_config=ADAPTIVE_CONFIG), start_round=0, rounds=7)
        state.reserve_budget("sta")
        state.set_stop_reason("max_iterations")

        restored = SearchState.from_dict(json.loads(state.to_checkpoint_json()))

        self.assertEqual(restored.refinement_weights, state.refinement_weights)
        self.assertEqual(restored.failure_feedback, state.failure_feedback)
        self.assertEqual(restored.cone_limit, state.cone_limit)
        self.assertEqual(restored.netlist_epoch, state.netlist_epoch)
        self.assertEqual(restored.round_id, state.round_id)
        self.assertEqual(restored.current_netlist_text, state.current_netlist_text)
        self.assertEqual(restored.current_wns, state.current_wns)
        self.assertEqual(restored.critical_endpoints, state.critical_endpoints)
        self.assertEqual(restored.critical_instances, state.critical_instances)
        self.assertEqual(restored.current_cone_gates, state.current_cone_gates)
        self.assertEqual(restored.accepted_patches, state.accepted_patches)
        self.assertEqual(restored.failure_history, state.failure_history)
        self.assertEqual(restored.tested_candidate_hashes, state.tested_candidate_hashes)
        self.assertEqual(restored.budget, state.budget)
        self.assertEqual(restored.stop_reason, state.stop_reason)
        self.assertEqual(restored._snapshots, state._snapshots)

    def test_checkpoint_serialisation_is_byte_deterministic(self):
        state = simulate(make_state(), start_round=0, rounds=6)
        self.assertEqual(state.to_checkpoint_json(), state.to_checkpoint_json())

    def test_checkpoint_records_the_effective_configuration(self):
        """The OI-012 gap: enable_feedback / strategies / init_weights must be on the record."""
        state = make_state(enable_feedback=False, run_config={"strategies": ["G"], "seed": 7, "init_weights": None})
        payload = state.to_dict()
        self.assertEqual(payload["effective_config"]["enable_feedback"], False)
        self.assertEqual(payload["effective_config"]["strategies"], ["G"])
        self.assertEqual(payload["effective_config"]["seed"], 7)
        self.assertIn("feedback_config", payload)
        self.assertEqual(payload["schema_version"], SCHEMA_VERSION)

    def test_resume_equivalence(self):
        """R6: interrupting, checkpointing and resuming must change nothing."""
        uninterrupted = simulate(make_state(feedback_config=ADAPTIVE_CONFIG), start_round=0, rounds=9)

        partial = simulate(make_state(feedback_config=ADAPTIVE_CONFIG), start_round=0, rounds=4)
        resumed = SearchState.from_dict(partial.to_dict())
        simulate(resumed, start_round=4, rounds=5)

        self.assertEqual(resumed.refinement_weights, uninterrupted.refinement_weights)
        self.assertEqual(resumed.failure_feedback, uninterrupted.failure_feedback)
        self.assertEqual(resumed.cone_limit, uninterrupted.cone_limit)
        self.assertEqual(resumed.netlist_epoch, uninterrupted.netlist_epoch)
        self.assertEqual(resumed.round_id, uninterrupted.round_id)
        self.assertEqual(resumed.current_netlist_text, uninterrupted.current_netlist_text)
        self.assertEqual(resumed.current_wns, uninterrupted.current_wns)
        self.assertEqual(resumed.current_min_slack, uninterrupted.current_min_slack)
        self.assertEqual(
            [patch["patch_id"] for patch in resumed.accepted_patches],
            [patch["patch_id"] for patch in uninterrupted.accepted_patches],
        )
        self.assertEqual(
            [patch["netlist_hash"] for patch in resumed.accepted_patches],
            [patch["netlist_hash"] for patch in uninterrupted.accepted_patches],
        )
        self.assertEqual(resumed.tested_candidate_hashes, uninterrupted.tested_candidate_hashes)
        self.assertEqual(resumed.budget_used("sta"), uninterrupted.budget_used("sta"))

    def test_save_checkpoint_filename_carries_epoch_and_round(self):
        import tempfile
        from pathlib import Path

        state = simulate(make_state(), start_round=0, rounds=5)
        with tempfile.TemporaryDirectory() as tmp:
            path = state.save_checkpoint(Path(tmp))
            self.assertEqual(path.name, f"state_checkpoint_e{state.netlist_epoch:03d}_r{state.round_id:03d}.json")
            self.assertTrue(path.exists())

    def test_restore_refuses_a_config_mismatch(self):
        payload = simulate(make_state(), start_round=0, rounds=4).to_dict()
        payload["run_config"] = {"strategies": ["G"], "seed": 999}
        with self.assertRaises(CheckpointError):
            SearchState.from_dict(payload)

    def test_restore_refuses_an_unknown_schema(self):
        payload = simulate(make_state(), start_round=0, rounds=2).to_dict()
        payload["schema_version"] = 999
        with self.assertRaises(CheckpointError):
            SearchState.from_dict(payload)

    def test_restore_refuses_a_broken_patch_chain(self):
        payload = simulate(make_state(), start_round=0, rounds=5).to_dict()
        payload["accepted_patches"][0]["netlist_text"] = "module tampered();\nendmodule\n"
        with self.assertRaises(CheckpointError):
            SearchState.from_dict(payload)

    def test_restore_refuses_a_broken_epoch_invariant(self):
        payload = simulate(make_state(), start_round=0, rounds=5).to_dict()
        payload["netlist_epoch"] = 99
        with self.assertRaises(CheckpointError):
            SearchState.from_dict(payload)

    def test_restore_refuses_a_tampered_snapshot(self):
        payload = simulate(make_state(), start_round=0, rounds=9).to_dict()
        payload["snapshots"][1]["netlist_hash"] = "0" * 64
        with self.assertRaises(CheckpointError):
            SearchState.from_dict(payload)

    def test_restore_refuses_a_snapshot_count_mismatch(self):
        payload = simulate(make_state(), start_round=0, rounds=5).to_dict()
        payload["snapshots"] = payload["snapshots"][:-1]
        with self.assertRaises(CheckpointError):
            SearchState.from_dict(payload)


if __name__ == "__main__":
    unittest.main()
