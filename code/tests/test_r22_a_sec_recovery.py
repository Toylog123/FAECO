"""The A recovery runner must bind actual artifacts before any SEC call."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/python/prove_historical_a_r22.py"


def _digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@pytest.fixture
def runner(monkeypatch):
    assert SCRIPT.is_file(), "A SEC recovery runner is missing"
    spec = importlib.util.spec_from_file_location("historical_a_sec_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "git_identity", lambda root: {"head": "a" * 40, "source_tree_clean": True})
    return module


@pytest.fixture
def archive(tmp_path):
    def write(path, value):
        file = tmp_path / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")
        return file

    baseline = "module s382(A,Y);\ninput A;\noutput Y;\nsky130_fd_sc_hd__buf_1 u (.A(A), .X(Y));\nendmodule"
    final = baseline.replace("__buf_1", "__buf_2")
    base = "experiments/counterpart/s382/baseline/mapped.v"
    fixed = "experiments/counterpart/s382/fixed/mapped.v"
    run = "experiments/original/s382"
    write(base, baseline)
    write(fixed, final)
    write(run + "/mapped.v", baseline)
    action = {"instance": "u", "kind": "G", "to_type": "sky130_fd_sc_hd__buf_2", "accepted": True}
    write(run + "/eval_trials.json", json.dumps({"trials": [action]}) + r"\n")
    write(run + "/outerloop_result.json", {"circuit": "s382", "success": True})
    for name in ("verify.ys", "verify.log", "old_gold.v"):
        write("experiments/old_sec/" + name, baseline)
    audit = {"runs": [{"family": "A", "circuit": "s382", "run": run, "final_source": fixed,
        "classification": "unidentified", "accepted_actions": [{k: v for k, v in action.items() if k != "accepted"}],
        "structure": {"initial_text_hash": _digest(baseline), "final_text_hash": _digest(final),
                      "initial_top_hash": _digest(baseline), "final_top_hash": _digest(final)},
        "sec": {"bound": False, "script": "experiments/old_sec/verify.ys", "log": "experiments/old_sec/verify.log",
                "gold_file": "experiments/old_sec/old_gold.v", "gate_file": run + "/mapped.v"}}]}
    write("project_docs/evidence/r22_historical_correctness_20261014/correctness_audit.json", audit)
    write("project_docs/evidence/r22_historical_correctness_20261014/audit.py", "# archived audit")
    write("experiments/20260807_real_pr_iscas8/pre_layout_audit_summary.json", {"records": [
        {"circuit": "s382", "variant": "baseline", "netlist": base},
        {"circuit": "s382", "variant": "fixed", "netlist": fixed}]})
    for name in ("code/scripts/run_r22_cut_ablation.py", "code/scripts/run_sequential_timing_check.py",
                 "code/scripts/run_with_timeout.sh", "code/scripts/python/prove_historical_a_r22.py", "code/src/rseco/real_wns.py"):
        write(name, "# pinned proof source\n")
    write("library.lib", "library(test) {}")
    return tmp_path


def _manifest(runner, archive):
    return runner.build_manifest(archive, circuits=("s382",), liberty=archive / "library.lib")


def test_actual_baseline_and_accepted_counterpart_are_bound(runner, archive):
    manifest = _manifest(runner, archive)
    case = manifest["cases"][0]
    assert case["gold"]["path"] == "experiments/original/s382/mapped.v"
    assert case["gate"]["path"] == "experiments/counterpart/s382/fixed/mapped.v"
    assert case["binding"]["accepted_type_only_reconstruction_exact"] is True
    assert case["old_sec"]["bound"] is False
    assert manifest["eda_executed"] is False
    assert manifest["json_trailers"] == {"experiments/original/s382/eval_trials.json": r"\n"}


@pytest.mark.parametrize("problem", ["missing_final", "unrelated_final", "duplicate_crosswalk", "unknown_accepted_kind"])
def test_ambiguous_or_unidentifiable_final_is_rejected(runner, archive, problem):
    if problem == "missing_final":
        (archive / "experiments/counterpart/s382/fixed/mapped.v").unlink()
    elif problem == "unrelated_final":
        (archive / "experiments/counterpart/s382/fixed/mapped.v").write_text("module s382(); endmodule")
    elif problem == "duplicate_crosswalk":
        path = archive / "experiments/20260807_real_pr_iscas8/pre_layout_audit_summary.json"
        value = json.loads(path.read_text())
        value["records"].append(value["records"][0])
        path.write_text(json.dumps(value))
    else:
        path = archive / "experiments/original/s382/eval_trials.json"
        path.write_text(json.dumps({"trials": [{"instance": "u", "kind": "B", "to_type": "x", "accepted": True}]}))
    with pytest.raises((ValueError, FileNotFoundError)):
        _manifest(runner, archive)


def test_source_pin_change_is_rejected_before_proof(runner, archive):
    manifest = _manifest(runner, archive)
    (archive / "code/src/rseco/real_wns.py").write_text("# changed model semantics\n")
    with pytest.raises(ValueError, match="[Ss]ource"):
        runner.validate_manifest(manifest, archive)


def test_dirty_registration_cannot_run_formal_sec(runner, archive, monkeypatch):
    monkeypatch.setattr(runner, "git_identity", lambda root: {"head": "a" * 40, "source_tree_clean": False})
    manifest = _manifest(runner, archive)
    with pytest.raises(ValueError, match="[Dd]irty|[Pp]rovisional|[Ff]rozen"):
        runner.validate_manifest(manifest, archive)


def test_input_change_is_rejected_before_proof(runner, archive):
    manifest = _manifest(runner, archive)
    (archive / manifest["cases"][0]["gate"]["path"]).write_text("changed")
    with pytest.raises(ValueError, match="[Ii]nput|[Hh]ash"):
        runner.validate_manifest(manifest, archive)


def test_receipt_records_prover_failure_instead_of_claiming_pass(runner, archive, tmp_path, monkeypatch):
    manifest = _manifest(runner, archive)
    calls = []
    def failed_proof(initial, final, circuit, output):
        calls.append((initial, final, circuit))
        return {"status": "fail", "returncode": 7}
    monkeypatch.setattr(runner, "load_prover", lambda root: (failed_proof, archive / "library.lib"))
    receipt = runner.run_case(manifest, manifest["cases"][0], archive, tmp_path / "proof")
    assert len(calls) == 1
    assert receipt["status"] == "fail"
    assert receipt["proof_returncode"] == 7
    assert (tmp_path / "proof/receipt.json").is_file()
