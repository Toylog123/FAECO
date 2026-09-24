"""Tests for analyze_k1_discriminant.py (synthetic fixtures)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "code/scripts" / "analyze_k1_discriminant.py"

spec = importlib.util.spec_from_file_location("analyze_k1_discriminant", SCRIPT)
assert spec is not None and spec.loader is not None
ak = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ak)


def _write_run(root: Path, arm: str, circuit: str, *, curve, final_wns,
               k_first=None, rounds=None):
    out = root / arm / circuit
    out.mkdir(parents=True, exist_ok=True)
    (out / "outerloop_result.json").write_text(json.dumps({
        "success": True, "stop_reason": "max_iterations",
        "baseline_wns": -0.5, "wns": final_wns,
        "best_wns_curve": curve,
        "n_sta_to_first_improvement": k_first,
    }), encoding="utf-8")
    if rounds is not None:
        trials = [{"iteration": it, "sta_provenance": "opensta",
                   "base_netlist_hash": r["base"], "cut_hash": r["cut"],
                   "wns": -0.5}
                  for it, r in sorted(rounds.items())]
        (out / "eval_trials.json").write_text(json.dumps(
            {"trials": trials}), encoding="utf-8")


def test_round_identities_first_trial_per_iteration():
    trials = [
        {"iteration": 1, "sta_provenance": "x", "base_netlist_hash": "b1",
         "cut_hash": "c1"},
        {"iteration": 1, "sta_provenance": "x", "base_netlist_hash": "b1",
         "cut_hash": "c1"},
        {"iteration": 2, "sta_provenance": "x", "base_netlist_hash": "b2",
         "cut_hash": "c2"},
        # no sta_provenance key at all -> pre-STA placeholder, not a
        # decision point (same canonical filter as flow.py's B(k))
        {"iteration": 3, "base_netlist_hash": "zz", "cut_hash": "zz"},
    ]
    rounds = ak._round_identities(trials)
    assert set(rounds) == {1, 2}
    assert rounds[2] == {"base_netlist_hash": "b2", "cut_hash": "c2"}


def test_compare_identities_counts_changes_and_divergence():
    fixed = {1: {"base_netlist_hash": "B", "cut_hash": "c1"},
             2: {"base_netlist_hash": "B", "cut_hash": "c2"},
             3: {"base_netlist_hash": "B", "cut_hash": "c3"},
             4: {"base_netlist_hash": "B", "cut_hash": "c4"}}
    # adaptive: same netlist state rounds 1-3 (cut differs at 2), diverges at 4
    adaptive = {1: {"base_netlist_hash": "B", "cut_hash": "c1"},
                2: {"base_netlist_hash": "B", "cut_hash": "c9"},
                3: {"base_netlist_hash": "B", "cut_hash": "c3"},
                4: {"base_netlist_hash": "X", "cut_hash": "c4"}}
    out = ak.compare_identities(fixed, adaptive)
    assert out["same_decision_rounds"] == 2
    assert out["identity_changed_rounds"] == 1
    assert out["trajectory_divergence_round"] == 4
    assert out["comparable_rounds_before_divergence"] == 3


def test_classify_pre_locked_lexicographic():
    f = {"final_dwns": 0.1, "max_bk": 0.1, "k_first": 5, "n_sta": 100}
    assert ak.classify(f, {**f, "final_dwns": 0.2}) == "better"
    assert ak.classify(f, {**f, "final_dwns": 0.05}) == "worse"
    assert ak.classify(f, {**f, "max_bk": 0.2}) == "better"
    assert ak.classify(f, {**f, "k_first": 3}) == "better"
    assert ak.classify(f, {**f, "n_sta": 90}) == "better"
    assert ak.classify(f, dict(f)) == "equal"
    assert ak.classify(f, {**f, "n_sta": 120}) == "worse"
    # k_first None counts as +inf (never improved); fixed arm is the one
    # that never improved here -> adaptive (improved at 5) is better
    assert ak.classify({**f, "k_first": None}, f) == "better"
    assert ak.classify(f, {**f, "k_first": None}) == "worse"


def test_adjudicate_majority_rules():
    # directional verdict requires a strict majority of all circuits
    rows = [{"classification": "better"}] * 5 + \
           [{"classification": "worse"}] * 2 + [{"classification": "equal"}]
    assert ak.adjudicate(rows)["verdict"] == "EMA_POSITIVE_BUDGET_SENSITIVE"
    rows = [{"classification": "equal"}] * 6 + [{"classification": "worse"}] * 2
    assert ak.adjudicate(rows)["verdict"] == "EMA_NO_INDEPENDENT_BENEFIT"
    rows = [{"classification": "worse"}] * 5 + \
           [{"classification": "better"}] * 2 + [{"classification": "equal"}]
    assert ak.adjudicate(rows)["verdict"] == "EMA_NEGATIVE"


def test_main_end_to_end(tmp_path):
    for circuit, better in (("s27", True), ("s382", False)):
        f_wns = -0.4  # fixed dWNS = +0.10
        # better: adaptive improves more (-0.35 -> +0.15); else less
        a_wns = -0.35 if better else -0.45
        # round 2: same netlist state, EMA picked a different cut on the
        # "better" circuit; same cut on the other one
        fixed_rounds = {1: {"base": "B1", "cut": "c1"},
                        2: {"base": "B1", "cut": "c2"}}
        adaptive_rounds = {1: {"base": "B1", "cut": "c1"},
                           2: {"base": "B1", "cut": "cX" if better else "c2"}}
        _write_run(tmp_path, "fixed", circuit, curve=[0.0, 0.1],
                   final_wns=f_wns, k_first=5, rounds=fixed_rounds)
        _write_run(tmp_path, "adaptive", circuit, curve=[0.0, 0.15],
                   final_wns=a_wns, k_first=3, rounds=adaptive_rounds)
    out = tmp_path / "verdict.json"
    import sys
    old = sys.argv
    sys.argv = ["x", "--root", str(tmp_path), "--json-out", str(out)]
    try:
        rc = ak.main()
    finally:
        sys.argv = old
    assert rc == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["verdict"]["n_circuits"] == 2
    assert data["rows"][0]["identity_comparison"][
        "identity_changed_rounds"] == 1
