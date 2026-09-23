"""Tests for the 0a equivalence gate comparator (``compare_0a_equivalence``).

The comparator is the acceptance instrument for the 0a state-architecture
migration, so it must (a) call a difference a difference, (b) separate decision
items from bookkeeping items, and (c) ignore per-run provenance paths that
legitimately differ between two run directories.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "code" / "scripts" / "compare_0a_equivalence.py"

sys.path.insert(0, str(SCRIPT.parent))
from compare_0a_equivalence import compare  # noqa: E402


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
                    "sta_provenance": {"output_dir": "/some/run/specific/path"},
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


def _write(tmp_path: Path, name: str, product: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(product), encoding="utf-8")
    return path


def test_identical_products_pass_every_item(tmp_path: Path) -> None:
    ref = _write(tmp_path, "ref.json", _product())
    cand = _write(tmp_path, "cand.json", _product())
    result = compare(ref, cand)

    assert result["full_match"] is True
    assert result["decision_match"] is True
    assert result["n_match"] == result["n_items"]


def test_provenance_paths_do_not_count_as_differences(tmp_path: Path) -> None:
    """Two runs write different ``output_dir`` values; that is not a behaviour diff."""
    left = _product()
    right = _product()
    right["state"]["accepted_patches"][0]["sta_provenance"] = {
        "output_dir": "/a/completely/different/run/directory"
    }
    ref = _write(tmp_path, "ref.json", left)
    cand = _write(tmp_path, "cand.json", right)

    result = compare(ref, cand)
    assert result["full_match"] is True


def test_sta_counter_difference_is_bookkeeping_not_decision(tmp_path: Path) -> None:
    """E6 counters moved between revisions; that must not fail the decision core."""
    right = _product()
    right["n_candidate_sta_runs"] = 86
    right["state"]["budget"].update({"sta_runs": 53, "formal_runs": 106,
                                     "sta_used": 53, "formal_used": 106})
    ref = _write(tmp_path, "ref.json", _product())
    cand = _write(tmp_path, "cand.json", right)

    result = compare(ref, cand)
    assert result["decision_match"] is True
    assert result["full_match"] is False
    assert set(result["bookkeeping_mismatches"]) == {
        "E6.n_candidate_sta_runs", "E6.sta_runs", "E6.sta_used",
        "E6.formal_runs", "E6.formal_used",
    }
    assert result["core_mismatches"] == []


def test_decision_difference_is_reported_as_core_mismatch(tmp_path: Path) -> None:
    right = _product(wns=-1.21, actions_history=[])
    ref = _write(tmp_path, "ref.json", _product())
    cand = _write(tmp_path, "cand.json", right)

    result = compare(ref, cand)
    assert result["decision_match"] is False
    assert "E5.wns" in result["core_mismatches"]
    assert "E2.feedback_sequence" in result["core_mismatches"]


def test_candidate_order_difference_is_bookkeeping(tmp_path: Path) -> None:
    right = _product()
    right["state"]["tested_candidate_hashes"] = ["aaa", "bbb", "ccc", "ddd"]
    ref = _write(tmp_path, "ref.json", _product())
    cand = _write(tmp_path, "cand.json", right)

    result = compare(ref, cand)
    assert result["decision_match"] is True
    assert "E1.candidate_order" in result["bookkeeping_mismatches"]


def test_cli_exit_code_reflects_decision_gate(tmp_path: Path) -> None:
    ref = _write(tmp_path, "ref.json", _product())
    same = _write(tmp_path, "same.json", _product())
    worse = _write(tmp_path, "worse.json", _product(wns=-1.21))

    passing = subprocess.run(
        [sys.executable, str(SCRIPT), "--reference", str(ref), "--candidate", str(same)],
        capture_output=True, text=True,
    )
    assert passing.returncode == 0
    assert "full gate (E1-E6)     : PASS" in passing.stdout

    failing = subprocess.run(
        [sys.executable, str(SCRIPT), "--reference", str(ref), "--candidate", str(worse)],
        capture_output=True, text=True,
    )
    assert failing.returncode == 1
    assert "decision core" in failing.stdout


def test_cli_writes_machine_readable_report(tmp_path: Path) -> None:
    ref = _write(tmp_path, "ref.json", _product())
    cand = _write(tmp_path, "cand.json", _product())
    out = tmp_path / "report.json"

    subprocess.run(
        [sys.executable, str(SCRIPT), "--reference", str(ref),
         "--candidate", str(cand), "--json-out", str(out)],
        capture_output=True, text=True, check=True,
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert isinstance(payload, list) and len(payload) == 1
    assert payload[0]["full_match"] is True
