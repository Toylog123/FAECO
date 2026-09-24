"""Tests for compare_threearm.py (synthetic fixtures, no real runs)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "code/scripts" / "compare_threearm.py"

spec = importlib.util.spec_from_file_location("compare_threearm", SCRIPT)
assert spec is not None and spec.loader is not None
ct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ct)


def _write_run(root: Path, arm: str, circuit: str, *, curve: list[float],
               final_wns: float, baseline: float = -0.5,
               k_first: int | None = None, seed: int | None = None) -> None:
    out = root / arm / circuit
    out.mkdir(parents=True, exist_ok=True)
    data = {
        "success": True,
        "stop_reason": "sta_budget",
        "baseline_wns": baseline,
        "wns": final_wns,
        "best_wns_curve": curve,
        "n_sta_to_first_improvement": k_first,
        "wns_gain_per_100_sta": 0.1,
        "enable_feedback": arm == "adaptive",
        "random_order": arm.startswith("random"),
        "seed": seed,
    }
    (out / "outerloop_result.json").write_text(
        json.dumps(data), encoding="utf-8")


def _populate(root: Path, curves: dict[str, list[float]]) -> None:
    """adaptive/fixed/random_s1..3 for circuits keyed '<circuit>_<armSuffix>'."""
    for circuit, curve in curves.items():
        # deterministic final wns so paired diffs are checkable
        _write_run(root, "fixed", circuit, curve=curve, final_wns=-0.4,
                   k_first=10)
        _write_run(root, "adaptive", circuit, curve=curve, final_wns=-0.45,
                   k_first=5)
        for i, arm in enumerate(ct.RANDOM_ARMS, start=1):
            _write_run(root, arm, circuit, curve=curve, final_wns=-0.42,
                       k_first=8, seed=i)


def test_load_run_missing_and_incomplete(tmp_path):
    assert ct.load_run(tmp_path, "fixed", "s27") is None
    _write_run(tmp_path, "fixed", "s27", curve=[], final_wns=-0.4)
    # a run without any real-STA curve cannot be paired
    assert ct.load_run(tmp_path, "fixed", "s27") is None
    _write_run(tmp_path, "fixed", "s27", curve=[0.0, 0.1], final_wns=-0.4)
    run = ct.load_run(tmp_path, "fixed", "s27")
    assert run is not None
    assert run["n_sta"] == 2
    assert run["final_dwns"] == 0.1  # final -0.4 - baseline -0.5 (WNS->0 better)


def test_paired_diffs_direction_consistency(tmp_path):
    _populate(tmp_path, {"s27": [0.0, 0.1]})
    runs = ct.load_all(tmp_path, circuits=("s27",))
    assert len(runs) == 5
    rows, summary = ct.paired_diffs(runs, ("s27",), "final_dwns")
    # adaptive -0.45 vs fixed -0.4 with baseline -0.5 -> +0.05 vs +0.1
    assert rows[0]["diff_vs_fixed"] == -0.05
    assert summary["n_pairs_vs_fixed"] == 1
    assert summary["adaptive_worse_vs_fixed"] == 1


def test_paired_diffs_missing_side_is_none_not_imputed(tmp_path):
    _write_run(tmp_path, "adaptive", "s27", curve=[0.0], final_wns=-0.45)
    runs = ct.load_all(tmp_path, circuits=("s27",))
    rows, summary = ct.paired_diffs(runs, ("s27",), "final_dwns")
    assert rows[0]["diff_vs_fixed"] is None
    assert summary["n_pairs_vs_fixed"] == 0


def test_adjudicate_ema_faster(tmp_path):
    # adaptive B(k) not worse at equal k and earlier first improvement on
    # both circuits -> EMA_FASTER_TO_FIRST_IMPROVEMENT
    _populate(tmp_path, {"s27": [0.0, 0.2], "s382": [0.0, 0.3]})
    runs = ct.load_all(tmp_path, circuits=("s27", "s382"))
    verdict = ct.adjudicate(tmp_path, runs, ("s27", "s382"))
    assert verdict["verdict"] == "EMA_FASTER_TO_FIRST_IMPROVEMENT"
    assert verdict["counts"]["k_first_lower"] == 2


def test_adjudicate_no_independent_contribution(tmp_path):
    # adaptive strictly worse B(k) at equal k and later first improvement
    for circuit in ("s27", "s382"):
        _write_run(tmp_path, "fixed", circuit, curve=[0.0, 0.2],
                   final_wns=-0.4, k_first=2)
        _write_run(tmp_path, "adaptive", circuit, curve=[0.0, 0.1],
                   final_wns=-0.41, k_first=9)
        for i, arm in enumerate(ct.RANDOM_ARMS, start=1):
            _write_run(tmp_path, arm, circuit, curve=[0.0, 0.1],
                       final_wns=-0.42, k_first=8, seed=i)
    runs = ct.load_all(tmp_path, circuits=("s27", "s382"))
    verdict = ct.adjudicate(tmp_path, runs, ("s27", "s382"))
    assert verdict["verdict"] == "NO_INDEPENDENT_CONTRIBUTION"


def test_adjudicate_insufficient_data(tmp_path):
    runs = ct.load_all(tmp_path, circuits=("s27",))
    verdict = ct.adjudicate(tmp_path, runs, ("s27",))
    assert verdict["verdict"] == "INSUFFICIENT_DATA"


def test_export_curves_shape(tmp_path):
    _populate(tmp_path, {"s27": [0.0, 0.1]})
    runs = ct.load_all(tmp_path, circuits=("s27",))
    curves = ct.export_curves(tmp_path, runs, ("s27",))
    assert curves["adaptive"]["s27"] == [0.0, 0.1]
    assert "fixed" in curves and len(curves["fixed"]) == 1


def test_main_cli_writes_json(tmp_path, capsys):
    _populate(tmp_path, {"s27": [0.0, 0.1]})
    out = tmp_path / "report.json"
    rc = ct.main.__wrapped__() if hasattr(ct.main, "__wrapped__") else None
    # invoke via argv to exercise the real entry point
    sys_argv = ["compare_threearm.py", "--root", str(tmp_path),
                "--circuits", "s27", "--json-out", str(out), "--quiet"]
    old = sys.argv
    sys.argv = sys_argv
    try:
        rc = ct.main()
    finally:
        sys.argv = old
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["adjudication"]["verdict"] == "EMA_FASTER_TO_FIRST_IMPROVEMENT"
    assert "fixed/s27" in data["runs"]
    assert capsys.readouterr().out == ""  # --quiet suppresses the table
