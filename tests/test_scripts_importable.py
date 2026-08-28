"""Scripts must be importable without manual PYTHONPATH setup."""

from __future__ import annotations


def test_scripts_modules_importable() -> None:
    from run_sequential_timing_check import _to_wsl, run_opensta, run_yosys_mapping
    from run_outerloop_real_wns import main

    assert callable(run_opensta)
    assert callable(run_yosys_mapping)
    assert callable(main)


def test_to_wsl_handles_any_drive_letter(tmp_path) -> None:
    from pathlib import Path

    from run_sequential_timing_check import _to_wsl

    assert _to_wsl(Path("D:/work/bench/a.v")).startswith("/mnt/d/work/bench/a.v")
    assert _to_wsl(Path("C:/Users/tester/case.v")).startswith("/mnt/c/Users/tester/case.v")
    non_ascii = _to_wsl(Path("C:/Users/佟亚龙/project/case.v"))
    assert non_ascii.startswith("/mnt/c/Users/佟亚龙/project/case.v")
