"""Scripts must be importable without manual PYTHONPATH setup."""

from __future__ import annotations


def test_scripts_modules_importable() -> None:
    from run_sequential_timing_check import run_opensta, run_yosys_mapping
    from run_outerloop_real_wns import main

    assert callable(run_opensta)
    assert callable(run_yosys_mapping)
    assert callable(main)
