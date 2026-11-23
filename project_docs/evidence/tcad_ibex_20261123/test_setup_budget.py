import json
from pathlib import Path

import pytest

from setup_budget import (
    SETUP_BUDGET_PCT_GRID,
    original_period_ps,
    setup_budget_ps,
    setup_gate_failures,
    setup_threshold_ps,
    setup_tns_budget_ps,
    tns_gate_failures,
)


EVIDENCE = Path(__file__).resolve().parent


@pytest.mark.parametrize(
    ("process", "receipt_name", "sdc_name", "period_ps"),
    [
        ("asap7", "CONTROL.json", "ORFS_SOURCE_CONSTRAINT.sdc", 1000.0),
        ("sky130", "REPAIRED_CONTROL.json", "original.sdc", 10000.0),
    ],
)
def test_original_period_uses_qualified_source_sdc(process, receipt_name, sdc_name, period_ps):
    folder = EVIDENCE / f"{process}_control"
    qualification = json.loads((folder / receipt_name).read_text(encoding="utf-8"))
    assert original_period_ps(qualification, folder / sdc_name) == period_ps


def test_period_rejects_source_drift(tmp_path):
    folder = EVIDENCE / "asap7_control"
    qualification = json.loads((folder / "CONTROL.json").read_text(encoding="utf-8"))
    source = (folder / "ORFS_SOURCE_CONSTRAINT.sdc").read_text(encoding="utf-8")
    changed = tmp_path / "changed.sdc"
    changed.write_text(source.replace("set clk_period 1000", "set clk_period 2000"), encoding="utf-8")
    with pytest.raises(ValueError, match="original SDC"):
        original_period_ps(qualification, changed)


def test_period_rejects_mismatched_ps_conversion():
    folder = EVIDENCE / "sky130_control"
    qualification = json.loads((folder / "REPAIRED_CONTROL.json").read_text(encoding="utf-8"))
    qualification["source_sdc_semantics"]["period_ps"] = 10.0
    with pytest.raises(ValueError, match="period_ps"):
        original_period_ps(qualification, folder / "original.sdc")


@pytest.mark.parametrize(
    ("period_ps", "expected"),
    [(1000, [0, 1, 2.5, 5, 10]), (10000, [0, 10, 25, 50, 100])],
)
def test_sweep_uses_fraction_of_original_period(period_ps, expected):
    assert [setup_budget_ps(period_ps, pct) for pct in SETUP_BUDGET_PCT_GRID] == expected


@pytest.mark.parametrize(("period_ps", "budget_pct"), [(0, 0.1), (float("inf"), 0.1), (1000, -0.1), (1000, float("nan"))])
def test_invalid_scaling_inputs_raise(period_ps, budget_pct):
    with pytest.raises(ValueError):
        setup_budget_ps(period_ps, budget_pct)


def test_rejects_observed_asap7_ff_sign_crossing_even_with_enough_relative_budget():
    reference_ps, candidate_ps, allowed_loss_ps = 0.38036240827332874, -4.379829832109492, 5.0
    assert setup_threshold_ps(reference_ps, allowed_loss_ps) == 0.0
    assert setup_gate_failures("FF", reference_ps, candidate_ps, allowed_loss_ps) == ["FF:setup_floor"]


def test_actual_asap7_tt_remains_eligible_with_enough_relative_budget():
    reference_ps, candidate_ps = -382.748166, -384.797415
    assert setup_threshold_ps(reference_ps, 2.5) == pytest.approx(-385.248166)
    assert not setup_gate_failures("TT", reference_ps, candidate_ps, 2.5)
    assert setup_gate_failures("TT", reference_ps, candidate_ps, 1.0) == ["TT:setup_budget"]


def test_clean_setup_floor_has_no_negative_tolerance():
    assert not setup_gate_failures("FF", 0.0, 0.0, 0.0)
    assert setup_gate_failures("FF", 0.0, -0.00001, 0.0) == ["FF:setup_floor"]


def test_zero_budget_keeps_relative_numeric_tolerance():
    assert not setup_gate_failures("SS", -100.0, -100.0009, 0.0)
    assert setup_gate_failures("SS", -100.0, -100.0011, 0.0) == ["SS:setup_budget"]


def test_positive_baseline_can_fail_relative_budget_without_crossing_zero():
    assert setup_threshold_ps(100.0, 10.0) == 90.0
    assert setup_gate_failures("FF", 100.0, 89.0, 10.0) == ["FF:setup_budget"]


def test_opt_out_of_positive_wns_floor_retains_relative_budget():
    assert setup_threshold_ps(0.38, 5.0, protect_clean=False) == pytest.approx(-4.62)
    assert not setup_gate_failures("FF", 0.38, -4.38, 5.0, protect_clean=False)
    assert setup_gate_failures("FF", 0.38, -4.38, 2.5, protect_clean=False) == ["FF:setup_budget"]


def test_tns_budget_uses_ten_times_wns_for_a_clean_view():
    assert setup_tns_budget_ps(1000.0, 0.5, 0.0) == 50.0


def test_tns_budget_scales_with_original_tns_when_larger():
    assert setup_tns_budget_ps(1000.0, 0.5, -449949.7379129025) == pytest.approx(2249.7486895645125)


def test_zero_percent_means_zero_tns_loss_budget():
    assert setup_tns_budget_ps(10000.0, 0.0, -1628197.1966236597) == 0.0


def test_tns_gate_checks_signed_loss_with_relative_tolerance():
    assert not tns_gate_failures("SS", -1000.0, -1050.0005, 50.0)
    assert tns_gate_failures("SS", -1000.0, -1050.0015, 50.0) == ["SS:setup_tns_budget"]
    assert not tns_gate_failures("SS", -1000.0, -900.0, 0.0)


@pytest.mark.parametrize(("arm", "name"), [("single", "single/05"), ("faeco", "faeco/03")])
def test_historical_asap7_endpoints_pass_half_percent_with_relative_only_setup(arm, name):
    baseline = json.loads((EVIDENCE / "ASAP7_P1_RESULTS.json").read_text(encoding="utf-8"))
    verified = json.loads((EVIDENCE / "ASAP7_P1_VERIFIED.json").read_text(encoding="utf-8"))
    endpoint = next(row for row in verified["arms"][arm]["attempts"] if row["endpoint"] == name)
    limit_ps = setup_budget_ps(1000.0, 0.5)
    for view, original in baseline["control"]["views"].items():
        candidate = endpoint["views_ps"][view]
        assert not setup_gate_failures(view, original["setup_wns_ps"], candidate["setup_wns_ps"],
                                       limit_ps, protect_clean=False)
        tns_limit = setup_tns_budget_ps(1000.0, 0.5, original["setup_tns_ps"])
        assert not tns_gate_failures(view, original["setup_tns_ps"], candidate["setup_tns_ps"], tns_limit)
    ff_ref = baseline["control"]["views"]["FF"]["setup_wns_ps"]
    ff_candidate = endpoint["views_ps"]["FF"]["setup_wns_ps"]
    assert setup_gate_failures("FF", ff_ref, ff_candidate, limit_ps) == ["FF:setup_floor"]
