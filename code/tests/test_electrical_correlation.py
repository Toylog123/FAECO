"""Tests for the phase 3-A correlation analysis.

The analysis decides whether electrical quantities enter the paper's eq. (2), so
its statistics must be beyond doubt: the AUC is rank-based and tie-aware, the
Spearman is rank-based, and both return ``None`` (not a fabricated 0.5/0.0) when
a class is empty.  A wrong sign here would silently invert the verdict.

The verdict tests are end-to-end against synthetic collections on disk, because
the rule that matters is the *guard*: a label that is near-degenerate must be
reported as unusable rather than producing a confident-looking AUC, and a single
lucky label must not be enough for a SIGNAL.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "code/scripts" / "analyze_electrical_correlation.py"


def _load():
    spec = importlib.util.spec_from_file_location("analyze_electrical_3a", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


MOD = _load()


class TestRanks:
    def test_average_ranks_share_ties(self):
        assert MOD._ranks([1.0, 2.0, 2.0, 4.0]) == [1.0, 2.5, 2.5, 4.0]

    def test_all_equal_share_the_middle(self):
        assert MOD._ranks([5.0, 5.0, 5.0]) == [2.0, 2.0, 2.0]


class TestSpearman:
    def test_monotone_increasing(self):
        assert MOD.spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)

    def test_monotone_decreasing(self):
        assert MOD.spearman([1, 2, 3, 4], [40, 30, 20, 10]) == pytest.approx(-1.0)

    def test_rank_not_value(self):
        # A strong monotone but non-linear relation is still 1.0.
        assert MOD.spearman([1, 2, 3, 4], [1, 8, 27, 64]) == pytest.approx(1.0)

    def test_constant_input_is_undefined(self):
        assert MOD.spearman([1, 1, 1, 1], [1, 2, 3, 4]) is None
        assert MOD.spearman([1, 2], [1, 2]) is None  # too few points


class TestAuc:
    def test_perfect_separation(self):
        assert MOD.auc([0.9, 0.8, 0.2, 0.1], [1, 1, 0, 0]) == pytest.approx(1.0)

    def test_perfectly_reversed(self):
        assert MOD.auc([0.1, 0.2, 0.8, 0.9], [1, 1, 0, 0]) == pytest.approx(0.0)

    def test_all_tied_scores_are_chance(self):
        assert MOD.auc([0.5, 0.5, 0.5, 0.5], [1, 1, 0, 0]) == pytest.approx(0.5)

    def test_tie_between_classes_counts_half(self):
        # Positives {0.9, 0.5} vs negatives {0.5, 0.1}: the tied (0.5, 0.5)
        # pair scores 0.5 and the other three pairs score 1.0 -> (3 + 0.5)/4.
        assert MOD.auc([0.5, 0.9, 0.5, 0.1], [1, 1, 0, 0]) == pytest.approx(0.875)

    def test_single_class_is_not_testable(self):
        assert MOD.auc([0.1, 0.2], [0, 0]) is None
        assert MOD.auc([0.1, 0.2], [1, 1]) is None

    def test_orient_reports_the_stronger_direction(self):
        assert MOD._orient(0.0) == pytest.approx(1.0)
        assert MOD._orient(0.2) == pytest.approx(0.8)
        assert MOD._orient(0.7) == pytest.approx(0.7)
        assert MOD._orient(None) is None


def _trial(*, d_slew=-0.05, f6=False, hard_fail=None, ideal_delta=0.1,
           physical_delta=None, kind="G", index=0) -> dict:
    events = []
    if f6:
        events.append({"type": "F6_physical_load_failure", "hard_gate": True})
    elif hard_fail:
        events.append({"type": "F4_timing_gain_insufficient", "hard_gate": True})
    return {
        "kind": kind,
        "instance": f"g{index}",
        "from_type": "sky130_fd_sc_hd__nor3b_1",
        "to_type": "sky130_fd_sc_hd__nor3b_2",
        "wns": -0.4,
        "electrical": {
            "captured": True,
            "worst": {
                "max_slew": {"pin": "g/Y", "limit": 1.5, "value": 0.5,
                             "slack": 1.0 + d_slew, "status": "MET"},
                "max_capacitance": {"pin": "g/Y", "limit": 0.05, "value": 0.02,
                                    "slack": 0.03, "status": "MET"},
                "max_fanout": None,
            },
            "n_violations": 0,
            "slack_delta_vs_baseline": {
                "max_slew": d_slew, "max_capacitance": -0.01, "max_fanout": None,
            },
            "critical_path": {
                "pins": 4, "max_slew": 0.5, "max_capacitance": 0.02,
                "total_capacitance": 0.05, "max_fanout": 3,
            },
            "baseline_available": True,
        },
        "failure_events": events,
        "acceptance_evidence": {
            "setup_wns": ideal_delta - 0.5, "metric_references": {"setup_wns": -0.5},
        },
        "physical_delta": physical_delta,
    }


class TestFeatureExtraction:
    def test_features_carry_deltas_and_path_profile(self):
        features = MOD.trial_features(_trial())
        assert features["d_slew_slack"] == -0.05
        assert features["d_cap_slack"] == -0.01
        assert features["d_fanout_slack"] is None  # unconstrained -> None, not 0
        assert features["worst_max_slew_slack"] == pytest.approx(0.95)
        assert features["cp_pins"] == 4
        assert features["cp_total_capacitance"] == 0.05
        assert features["drive_from"] == 1
        assert features["drive_to"] == 2
        assert features["drive_delta"] == 1

    def test_missing_record_yields_none(self):
        assert MOD.trial_features({"kind": "R"}) is None


class TestLabels:
    def test_f6_and_hard_fail_from_events(self):
        row = MOD.trial_row(_trial(f6=True), regime="phys", circuit="s27")
        assert row["f6"] == 1
        assert row["hard_fail"] == 1

    def test_no_events_is_zero_not_missing(self):
        row = MOD.trial_row(_trial(), regime="base", circuit="s27")
        assert row["f6"] == 0
        assert row["hard_fail"] == 0

    def test_no_ideal_gain_from_anchored_delta(self):
        losing = MOD.trial_row(_trial(ideal_delta=-0.1), regime="base", circuit="s27")
        winning = MOD.trial_row(_trial(ideal_delta=0.1), regime="base", circuit="s27")
        assert losing["no_ideal_gain"] == 1
        assert winning["no_ideal_gain"] == 0

    def test_no_physical_gain_is_undefined_without_a_physical_delta(self):
        row = MOD.trial_row(_trial(physical_delta=None), regime="base", circuit="s27")
        assert row["no_physical_gain"] is None

    def test_label_applicability_is_regime_aware(self):
        # F6 can only be emitted when the physical gate runs.
        assert MOD.label_applicable("f6", "phys") is True
        assert MOD.label_applicable("f6", "base") is False
        assert MOD.label_applicable("no_ideal_gain", "base") is True


class TestArmComparison:
    def _run(self, **overrides):
        run = {
            "result": {
                "success": True, "iterations": 3, "stop_reason": "early_stop",
                "wns_history": [-0.5, -0.4, -0.4],
                "state": {"accepted_patches": [
                    {"patch_id": "p1", "kind": "G", "instance": "g17",
                     "candidate_hash": "a" * 64},
                ]},
            },
            "trials": [{"kind": "G", "instance": "g17",
                        "from_type": "t1", "to_type": "t2", "wns": -0.4}],
        }
        run.update(overrides)
        return run

    def test_identical_arms_pass(self):
        assert MOD.compare_arms(self._run(), self._run()) == []

    def test_trajectory_mismatch_is_reported(self):
        other = self._run()
        other["result"] = dict(other["result"], wns_history=[-0.5, -0.4, -0.3])
        assert any("wns_history" in d for d in MOD.compare_arms(self._run(), other))

    def test_accepted_chain_mismatch_is_reported(self):
        other = self._run()
        other["result"] = dict(other["result"], state={"accepted_patches": []})
        assert any("accepted_patches" in d
                   for d in MOD.compare_arms(self._run(), other))

    def test_trial_sequence_mismatch_is_reported(self):
        other = self._run()
        other["trials"] = [{"kind": "R", "instance": "g1",
                            "from_type": "t1", "to_type": "t2", "wns": -0.4}]
        assert any("trial sequence" in d
                   for d in MOD.compare_arms(self._run(), other))


class TestBudgetReading:
    def test_reads_state_budget_sta_used(self):
        assert MOD._sta_used({"state": {"budget": {"sta_used": 42}}}) == 42

    def test_absent_budget_is_none_not_zero(self):
        assert MOD._sta_used({}) is None
        assert MOD._sta_used({"state": {}}) is None


class TestPairParsing:
    def test_parses_multiple_pairs(self):
        assert MOD.parse_pairs("phys:elec,base:cap") == [
            ("phys", "phys", "elec"), ("base", "base", "cap")]

    def test_rejects_malformed_pair(self):
        with pytest.raises(ValueError):
            MOD.parse_pairs("phys")
        with pytest.raises(ValueError):
            MOD.parse_pairs("phys:")


class TestVerdict:
    """End-to-end verdict checks: only usable labels and agreement may decide."""

    CIRCUIT = "s27"

    def _write_arm(self, root: Path, arm: str, trials: list[dict], *,
                   capture: bool, wns_history=None) -> None:
        base = root / arm / self.CIRCUIT
        base.mkdir(parents=True, exist_ok=True)
        (base / "eval_trials.json").write_text(
            json.dumps({"trials": trials}), encoding="utf-8")
        (base / "outerloop_result.json").write_text(json.dumps({
            "success": True, "iterations": 1, "stop_reason": "early_stop",
            "wns_history": wns_history or [-0.5, -0.4],
            "n_candidate_sta_runs": 12,
            "state": {"accepted_patches": [], "budget": {"sta_used": 12}},
        }), encoding="utf-8")
        (base / "run_config.json").write_text(json.dumps({
            "capture_electrical": capture,
            "resolved_args": {"sta_budget": 1600},
        }), encoding="utf-8")

    def _analyze(self, tmp_path: Path, trials: list[dict],
                 pairs=("phys", "phys", "elec")):
        control = [{k: v for k, v in t.items() if k != "electrical"}
                   for t in trials]
        self._write_arm(tmp_path, pairs[1], control, capture=False)
        self._write_arm(tmp_path, pairs[2], trials, capture=True)
        return MOD.analyze(tmp_path, [pairs], [self.CIRCUIT])

    def test_signal_when_two_labels_agree(self, tmp_path):
        # Failure exactly when the candidate raised electrical stress, and the
        # stress signal also shows in the ideal-gain and physical-gain labels.
        trials = []
        for i in range(40):
            failing = i >= 20
            trials.append(_trial(
                d_slew=(-0.2 - 0.01 * i) if failing else (0.2 + 0.01 * i),
                f6=failing,
                ideal_delta=-0.1 if failing else 0.1,
                physical_delta=-0.05 if failing else 0.05,
                index=i,
            ))
        report = self._analyze(tmp_path, trials)
        assert report["verdict"]["status"] == "SIGNAL"
        winner = report["verdict"]["winners"][0]
        assert winner["feature"] == "d_slew_slack"
        assert len(winner["labels"]) >= 2

    def test_single_separating_label_is_not_enough(self, tmp_path):
        # Only ``no_ideal_gain`` has usable classes; the F6 label is degenerate
        # (5/35) and the physical-gain label is constant.
        trials = []
        for i in range(40):
            failing = i >= 20
            trials.append(_trial(
                d_slew=(-0.2 - 0.01 * i) if failing else (0.2 + 0.01 * i),
                f6=(i < 5),                       # 5 positives -> unusable
                ideal_delta=-0.1 if failing else 0.1,
                physical_delta=0.05,              # constant -> unusable
                index=i,
            ))
        report = self._analyze(tmp_path, trials)
        assert report["labels"]["f6"]["usable"] is False
        assert report["labels"]["no_physical_gain"]["usable"] is False
        assert report["labels"]["no_ideal_gain"]["usable"] is True
        assert report["verdict"]["status"] == "NO SIGNAL"

    def test_all_labels_degenerate_is_untestable(self, tmp_path):
        trials = [
            _trial(d_slew=-0.01 * i, f6=(i < 5), ideal_delta=0.1,
                   physical_delta=None, index=i)
            for i in range(40)
        ]
        report = self._analyze(tmp_path, trials)
        assert report["verdict"]["status"] == "NO SIGNAL (untestable)"
        assert report["labels"]["f6"]["usable"] is False

    def test_non_separating_feature_is_no_signal(self, tmp_path):
        trials = []
        for i in range(40):
            alternating = bool(i % 2)
            trials.append(_trial(
                d_slew=-0.01 * i,
                f6=alternating,
                ideal_delta=-0.1 if alternating else 0.1,
                physical_delta=-0.05 if alternating else 0.05,
                index=i,
            ))
        report = self._analyze(tmp_path, trials)
        assert report["verdict"]["status"] == "NO SIGNAL"

    def test_arm_mismatch_invalidates_the_collection(self, tmp_path):
        trials = [_trial(d_slew=-0.1 * i, index=i) for i in range(30)]
        control = [{k: v for k, v in t.items() if k != "electrical"}
                   for t in trials]
        self._write_arm(tmp_path, "phys", control, capture=False,
                        wns_history=[-0.5, -0.3])
        self._write_arm(tmp_path, "elec", trials, capture=True,
                        wns_history=[-0.5, -0.4])
        report = MOD.analyze(tmp_path, [("phys", "phys", "elec")], [self.CIRCUIT])
        assert report["verdict"]["status"] == "INVALID COLLECTION"
        assert report["gate"]["passed"] is False

    def test_missing_run_invalidates_the_collection(self, tmp_path):
        trials = [_trial(d_slew=-0.1 * i, index=i) for i in range(30)]
        self._write_arm(tmp_path, "elec", trials, capture=True)
        report = MOD.analyze(tmp_path, [("phys", "phys", "elec")], [self.CIRCUIT])
        assert report["verdict"]["status"] == "INVALID COLLECTION"
        assert report["gate"]["missing"]
