from pathlib import Path

import pytest

from run_holdout_screened import expected_holdout_sdc


def test_holdout_io_ratio_round_trip_preserves_sdc_expressions():
    source = (Path(__file__).parent / "sky130_control" / "original.sdc").read_text(encoding="utf-8")
    source = source.replace("set clk_period 10.0\n", "set clk_period 1.1\n", 1)
    ratio = float("0.22") / 1.1
    spec = expected_holdout_sdc(source, pinned=(1.1, ratio, "core_clock", "clk_i", 1.095), time_unit="ns")
    assert spec["period_ps"] == 1100
    assert spec["io_delay_ps"] == pytest.approx(220)
    with pytest.raises(RuntimeError, match="I/O fraction"):
        expected_holdout_sdc(source.replace("set clk_io_pct 0.2", "set clk_io_pct 0.22"),
                             pinned=(1.1, ratio, "core_clock", "clk_i", 1.095), time_unit="ns")
