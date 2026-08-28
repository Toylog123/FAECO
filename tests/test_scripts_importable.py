"""Scripts must be importable without manual PYTHONPATH setup."""

from __future__ import annotations


def test_scripts_modules_importable() -> None:
    from run_sequential_timing_check import _to_wsl, run_opensta, run_yosys_mapping
    from run_outerloop_real_wns import main
    from verify_sentinel_sec import main as sec_main

    assert callable(run_opensta)
    assert callable(run_yosys_mapping)
    assert callable(main)
    assert callable(sec_main)


def test_to_wsl_handles_any_drive_letter(tmp_path) -> None:
    from pathlib import Path

    from run_sequential_timing_check import _to_wsl

    assert _to_wsl(Path("D:/work/bench/a.v")).startswith("/mnt/d/work/bench/a.v")
    assert _to_wsl(Path("C:/Users/tester/case.v")).startswith("/mnt/c/Users/tester/case.v")
    non_ascii = _to_wsl(Path("C:/Users/佟亚龙/project/case.v"))
    assert non_ascii.startswith("/mnt/c/Users/佟亚龙/project/case.v")


def test_sentinel_sec_loads_final_netlist(tmp_path) -> None:
    import json

    from verify_sentinel_sec import _load_evidences, _sha256

    run_dir = tmp_path / "s382"
    run_dir.mkdir()
    (run_dir / "mapped.v").write_text("module s382;\nendmodule\n", encoding="utf-8")
    (run_dir / "outerloop_result.json").write_text(
        json.dumps(
            {
                "state": {
                    "current_netlist_text": "module s382;\nwire x;\nendmodule\n"
                }
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "eval_trials.json").write_text(
        json.dumps(
            {
                "trials": [
                    {"accepted": True, "candidate_netlist_text": "X"},
                    {"accepted": False, "candidate_netlist_text": "Y"},
                ]
            }
        ),
        encoding="utf-8",
    )
    baseline, final = _load_evidences(run_dir)
    assert "wire x" in final
    assert len(_sha256(final)) == 64


def test_sentinel_sec_missing_run_raises(tmp_path) -> None:
    import pytest

    from verify_sentinel_sec import _load_evidences

    with pytest.raises(FileNotFoundError):
        _load_evidences(tmp_path / "nope")
