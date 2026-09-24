"""Tests for the multi-circuit equivalence sweep (``compare_equivalence_sweep``).

A phase gate such as the legacy regression asks one question over a whole
benchmark set: do *all* circuits pass the six equivalence items?  These tests
pin the three ways the aggregate verdict can go wrong — a decision difference
on one circuit, a bookkeeping-only difference, and a circuit whose product is
missing — plus the exit-code contract that a CI gate depends on.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "code" / "scripts" / "compare_equivalence_sweep.py"

sys.path.insert(0, str(SCRIPT.parent))
from compare_equivalence_sweep import run_sweep  # noqa: E402


def _product(**overrides):
    """A minimal, self-consistent product with every gate item populated."""
    product = {
        "baseline_wns": -0.98,
        "baseline_min_slack": 0.42,
        "wns": -0.83,
        "min_slack": 0.42,
        "tns": -11.83,
        "n_candidate_sta_runs": 22,
        "stop_reason": "max_iterations",
        "final_patch_id": "patch_x",
        "init_weights": {"boundary_penalty": 1.0, "max_cone_gates": 1000},
        "weights": {"boundary_penalty": 1.0, "max_cone_gates": 1000},
        "actions_history": [["increase_boundary_penalty"]],
        "history": [{"iteration": 1, "status": "accepted", "wns": -0.9}],
        "state": {
            "tested_candidate_hashes": ["aaa", "bbb"],
            "current_cone_gates": ["_001_"],
            "current_netlist_hash": "deadbeef",
            "accepted_patches": [
                {
                    "base_netlist_hash": "b0",
                    "candidate_hash": "c1",
                    "netlist_hash": "n1",
                    "patch_id": "patch_x",
                    "sta_provenance": {"output_dir": "/run/specific/path"},
                }
            ],
            "budget": {
                "max_patches": 8,
                "sta_runs": 22,
                "sta_used": 22,
                "formal_runs": 44,
                "formal_used": 44,
                "iterations_used": 8,
            },
        },
    }
    product.update(overrides)
    return product


def _write_product(root: Path, side: str, circuit: str, product: dict) -> None:
    d = root / side / circuit
    d.mkdir(parents=True, exist_ok=True)
    (d / "outerloop_result.json").write_text(
        json.dumps(product), encoding="utf-8")


def test_all_identical_circuits_pass(tmp_path: Path) -> None:
    circuits = ["s27", "s382", "s420"]
    for c in circuits:
        _write_product(tmp_path, "codex", c, _product())
        _write_product(tmp_path, "main", c, _product())

    report = run_sweep(tmp_path, "codex", "main", circuits)
    assert report["n_decision_pass"] == 3
    assert report["n_full_pass"] == 3
    assert report["all_decision_pass"] is True
    assert report["all_full_pass"] is True


def test_one_decision_difference_fails_the_sweep(tmp_path: Path) -> None:
    circuits = ["s27", "s382"]
    for c in circuits:
        _write_product(tmp_path, "codex", c, _product())
    _write_product(tmp_path, "main", "s27", _product())
    _write_product(tmp_path, "main", "s382", _product(wns=-1.21))

    report = run_sweep(tmp_path, "codex", "main", circuits)
    assert report["all_decision_pass"] is False
    assert report["n_decision_pass"] == 1
    status = {c["circuit"]: c["status"] for c in report["per_circuit"]}
    assert status == {"s27": "OK", "s382": "DECISION_DIFF"}


def test_bookkeeping_only_difference_keeps_decision_gate_green(tmp_path: Path) -> None:
    circuits = ["s27"]
    bump = _product()
    bump["n_candidate_sta_runs"] = 86
    bump["state"]["budget"].update({"sta_runs": 53, "sta_used": 53})
    _write_product(tmp_path, "codex", "s27", _product())
    _write_product(tmp_path, "main", "s27", bump)

    report = run_sweep(tmp_path, "codex", "main", circuits)
    assert report["all_decision_pass"] is True
    assert report["all_full_pass"] is False
    assert report["per_circuit"][0]["status"] == "BOOKKEEPING_DIFF"


def test_missing_product_is_reported_not_ignored(tmp_path: Path) -> None:
    """A circuit that never ran must not be silently dropped from the verdict."""
    circuits = ["s27", "s382"]
    _write_product(tmp_path, "codex", "s27", _product())
    _write_product(tmp_path, "main", "s27", _product())
    _write_product(tmp_path, "codex", "s382", _product())
    # main/s382 deliberately absent

    report = run_sweep(tmp_path, "codex", "main", circuits)
    assert report["n_runnable"] == 1
    assert report["all_decision_pass"] is False
    missing = [c for c in report["per_circuit"] if c["status"] == "MISSING"]
    assert missing and missing[0]["circuit"] == "s382"
    assert "main/s382" in missing[0]["missing"]


def test_cli_exit_code_and_json_report(tmp_path: Path) -> None:
    circuits = ["s27", "s382"]
    for c in circuits:
        _write_product(tmp_path, "codex", c, _product())
        _write_product(tmp_path, "main", c, _product())
    out = tmp_path / "sweep.json"

    passing = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path),
         "--circuits", ",".join(circuits), "--json-out", str(out)],
        capture_output=True, text=True,
    )
    assert passing.returncode == 0
    assert "SWEEP GATE    : PASS" in passing.stdout
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["all_full_pass"] is True
    assert payload["n_circuits"] == 2


def test_cli_require_full_flags_bookkeeping_drift(tmp_path: Path) -> None:
    bump = _product()
    bump["n_candidate_sta_runs"] = 86
    bump["state"]["budget"].update({"sta_runs": 53, "sta_used": 53})
    _write_product(tmp_path, "codex", "s27", _product())
    _write_product(tmp_path, "main", "s27", bump)

    lenient = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path),
         "--circuits", "s27"],
        capture_output=True, text=True,
    )
    assert lenient.returncode == 0

    strict = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path),
         "--circuits", "s27", "--require-full"],
        capture_output=True, text=True,
    )
    assert strict.returncode == 1
    assert "SWEEP GATE    : FAIL" in strict.stdout
