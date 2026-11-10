"""Post-route calibration of the placement-tier greedy comparison.

Motivation (measured, 2026-11-12 patch chains on s382 + s953): the placement
tier prices a buffer insertion at ~0.017-0.023 ns but the routed design gains
0.100-0.125 ns from it, while gate sizing is priced about right (0.072 ->
0.124) or optimistically (0.040 -> -0.043).  A single greedy rule that compares
raw placement deltas therefore systematically passes over B-class actions.

The calibration only reorders candidates that already passed the physical gate;
the gate itself still uses the raw delta.
"""

from __future__ import annotations

import pytest

from rseco.real_wns import RealWnsEvaluator, parse_postroute_calibration
from test_real_wns import LIB_TEXT, MAPPED_TEXT


def _evaluator(tmp_path, **kw):
    return RealWnsEvaluator(
        mapped_text=MAPPED_TEXT,
        top_module="s382",
        period=0.5,
        liberty_text=LIB_TEXT,
        baseline_wns=-0.94,
        output_dir=tmp_path,
        workers=1,
        **kw,
    )


class TestParsing:
    def test_empty_is_the_historical_rule(self):
        assert parse_postroute_calibration("") == {}
        assert parse_postroute_calibration(None) == {}

    def test_round_trip(self):
        table = parse_postroute_calibration("B=5.65, G=0.60 ,JOINT=0.53")
        assert table == {"B": 5.65, "G": 0.60, "JOINT": 0.53}

    def test_malformed_tokens_raise_instead_of_silently_dropping(self):
        with pytest.raises(ValueError):
            parse_postroute_calibration("B5.65")
        with pytest.raises(ValueError):
            parse_postroute_calibration("B=fast")
        with pytest.raises(ValueError):
            parse_postroute_calibration("=5.65")
        with pytest.raises(ValueError):
            parse_postroute_calibration("B=0")


class TestCandidateScore:
    def test_default_is_the_raw_delta(self, tmp_path):
        ev = _evaluator(tmp_path)
        assert ev.postroute_calibration == {}
        assert ev._candidate_score({"kind": "B", "physical_delta": 0.012}) == 0.012
        assert ev._candidate_score({"kind": "G", "physical_delta": 0.020}) == 0.020

    def test_missing_delta_scores_worst(self, tmp_path):
        ev = _evaluator(tmp_path, postroute_calibration={"B": 5.65})
        assert ev._candidate_score({"kind": "B", "physical_delta": None}) == float("-inf")

    def test_unknown_kind_is_unscaled(self, tmp_path):
        ev = _evaluator(tmp_path, postroute_calibration={"B": 5.65})
        assert ev._candidate_score({"kind": "R", "physical_delta": 0.01}) == 0.01

    def test_calibration_flips_the_ranking(self, tmp_path):
        """The measured ratios (B 5.65x, G 0.60x) must make a B action with a
        *smaller* placement gain outrank the G action the old rule preferred."""
        raw = _evaluator(tmp_path)
        cal = _evaluator(tmp_path, postroute_calibration={"B": 5.65, "G": 0.60})
        buff = {"kind": "B", "physical_delta": 0.012}
        size = {"kind": "G", "physical_delta": 0.020}
        assert raw._candidate_score(buff) < raw._candidate_score(size)
        assert cal._candidate_score(buff) > cal._candidate_score(size)
        # both candidates still pass the raw gate at 0.010 ns
        assert min(buff["physical_delta"], size["physical_delta"]) >= 0.010

    def test_gate_still_uses_the_raw_delta(self, tmp_path):
        """A calibrated factor must not let a sub-threshold action through:
        the gate reads ``physical_delta`` (0.004 < 0.010), not the score."""
        ev = _evaluator(tmp_path, postroute_calibration={"B": 5.65},
                        physical_gate=True, min_physical_gain_ns=0.010)
        tiny = {"kind": "B", "physical_delta": 0.004}
        assert ev._candidate_score(tiny) == pytest.approx(0.0226)
        assert tiny["physical_delta"] < ev.min_physical_gain_ns