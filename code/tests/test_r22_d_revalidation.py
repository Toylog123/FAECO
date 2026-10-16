"""D recovery transactions use subprocess stubs; no EDA is launched."""

import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/run_r22_d_revalidation.py"


def prepared(monkeypatch, tmp_path):
    assert SCRIPT.is_file(), "D same-family recovery driver is missing"
    spec = importlib.util.spec_from_file_location("r22_d_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "git_identity", lambda: {"head": "a" * 40, "source_tree_clean": True})
    monkeypatch.setattr(module, "source_manifest", lambda: {"code/source.py": "pinned"})
    output = tmp_path / "D_new"
    return module, output, module.build_manifest(output)


def stub_tools(monkeypatch, module, manifest, *, returncode=0, sec_status="pass", mismatch=False):
    calls = []
    jobs = {tuple(job["command"]): job for job in manifest["jobs"]}

    def runner(command, **kwargs):
        assert command[2] == "3900" and kwargs["timeout"] == 3930
        job = jobs[tuple(command[3:])]
        out = Path(job["output_dir"])
        calls.append(job["key"])
        if returncode:
            return SimpleNamespace(returncode=returncode)
        initial = (out / "mapped.v").read_text(encoding="utf-8")
        current_hash = hashlib.sha256(initial.encode()).hexdigest()
        result = {"n_new_sta_runs": 1, "n_candidate_sta_runs": 1, "n_candidate_evaluation_records": 1,
                  "state": {"budget": {"sta_used": 2 if mismatch else 1},
                            "current_netlist_text": initial, "current_netlist_hash": current_hash,
                            "accepted_patches": []},
                  "baseline_wns": -0.3, "wns": -0.3, "stop_reason": "stagnation",
                  "cut_search_policy": "legacy", "enable_topology": True}
        module.save(out / "outerloop_result.json", result)
        module.save(out / "run_config.json", {**job["expected_run_config"], "git_head": manifest["source_pin"]["head"]})
        module.save(out / "eval_trials.json", {"trials": [{"sta_executed": True, "sta_launch_seq": 1, "wns": -0.3}],
                    "sta_launch_events": [{"kind": "candidate_ideal", "seq": 1, "status": "completed", "wns": -0.3}]})
        return SimpleNamespace(returncode=0)

    def sec(initial, final, circuit, out):
        out.mkdir()
        (out / "initial_raw.v").write_text(initial, encoding="utf-8")
        (out / "final_raw.v").write_text(final, encoding="utf-8")
        for name in ("cells.v", "helpers.v", "gold.v", "gate.v", "sec.log", "sec.ys"):
            (out / name).write_text("stub proof", encoding="utf-8")
        result = {"status": sec_status, "returncode": 0 if sec_status == "pass" else 1,
                  "initial_sha256": module.sha(out / "initial_raw.v"), "final_sha256": module.sha(out / "final_raw.v")}
        module.save(out / "result.json", result)
        return result

    monkeypatch.setattr(module.subprocess, "run", runner)
    monkeypatch.setattr(module, "final_sec", sec)
    return calls


def test_matrix_preserves_d_commands_and_has_no_cprime_policy(monkeypatch, tmp_path):
    m, output, manifest = prepared(monkeypatch, tmp_path)
    assert len(manifest["jobs"]) == 56
    assert len(m.common.ARMS) == 9
    for job in manifest["jobs"]:
        command = job["command"]
        expected_width = "8" if job["family"] == "D" else "1"
        assert command[command.index("--candidates-per-iteration") + 1] == expected_width
        assert command[command.index("--cut-search-policy") + 1] == "legacy"
        assert command[command.index("--joint-k") + 1] == "2"
        assert "--skip-mapping" in command and "--enable-buffer" in command
        assert "--disable-topology" not in command and "--tns-aware" not in command
        assert "--structure-resynth" not in command
        if job["arm"] == "adaptive":
            assert "--feedback-ema" in command and job["expected_run_config"]["feedback_config"]["rho"] == 0.5
        else:
            assert "--no-feedback" in command
        assert Path(job["output_dir"]).is_relative_to(output)


def test_dry_run_registers_only_and_never_calls_tools(monkeypatch, tmp_path):
    m, output, _ = prepared(monkeypatch, tmp_path)
    monkeypatch.setattr(m.subprocess, "run", lambda *a, **k: pytest.fail("dry-run started a tool"))
    assert m.main(["--output-dir", str(output), "--circuits", "s27,s382", "--dry-run"]) == 0
    assert [p.name for p in output.iterdir()] == ["manifest.json"]


@pytest.mark.parametrize("drift", ["source", "preview", "liberty", "historical_config", "input"])
def test_drift_is_rejected_before_any_launch(monkeypatch, tmp_path, drift):
    m, output, manifest = prepared(monkeypatch, tmp_path)
    if drift == "source":
        monkeypatch.setattr(m, "source_manifest", lambda: {"changed": "source"})
    else:
        paths = {"preview": m.PREVIEW, "liberty": m.LIB,
                 "historical_config": m.ROOT / manifest["jobs"][0]["historical_config"],
                 "input": m.ROOT / manifest["jobs"][0]["baseline"]["path"]}
        old_sha = m.sha
        monkeypatch.setattr(m, "sha", lambda path: "changed" if Path(path) == paths[drift] else old_sha(path))
    with pytest.raises(RuntimeError, match="changed|drift|pin"):
        m.validate_manifest(manifest, output)
    assert not output.exists()


def test_ema_configuration_drift_is_not_silently_used(monkeypatch, tmp_path):
    m, _, _ = prepared(monkeypatch, tmp_path)
    monkeypatch.setattr(m, "current_feedback_config", lambda: {"rho": 0.9})
    with pytest.raises(RuntimeError, match="EMA|feedback"):
        m.build_manifest(tmp_path / "other")


def test_formal_execution_refuses_dirty_registered_source(monkeypatch, tmp_path):
    m, output, manifest = prepared(monkeypatch, tmp_path)
    manifest["source_pin"]["source_tree_clean"] = False
    with pytest.raises(RuntimeError, match="dirty|frozen|clean"):
        m.execute_run(manifest["jobs"][0], output, manifest)


def test_failed_runner_receipt_prevents_overwrite_or_retry(monkeypatch, tmp_path):
    m, output, manifest = prepared(monkeypatch, tmp_path)
    calls = stub_tools(monkeypatch, m, manifest, returncode=7)
    job = manifest["jobs"][0]
    with pytest.raises(RuntimeError, match="Runner|runner"):
        m.execute_run(job, output, manifest)
    run = Path(job["output_dir"])
    assert json.loads((run / "failure.json").read_text(encoding="utf-8"))["returncode"] == 7
    assert not (run / "completion.json").exists()
    with pytest.raises(RuntimeError, match="Incomplete|incomplete"):
        m.execute_run(job, output, manifest)
    assert len(calls) == 1


def test_sec_failure_never_creates_completion(monkeypatch, tmp_path):
    m, output, manifest = prepared(monkeypatch, tmp_path)
    stub_tools(monkeypatch, m, manifest, sec_status="fail")
    job = manifest["jobs"][0]
    with pytest.raises(RuntimeError, match="SEC"):
        m.execute_run(job, output, manifest)
    run = Path(job["output_dir"])
    assert json.loads((run / "failure.json").read_text(encoding="utf-8"))["sec_status"] == "fail"
    assert not (run / "completion.json").exists()


def test_launch_reservation_mismatch_has_failure_receipt(monkeypatch, tmp_path):
    m, output, manifest = prepared(monkeypatch, tmp_path)
    stub_tools(monkeypatch, m, manifest, mismatch=True)
    job = manifest["jobs"][0]
    with pytest.raises(RuntimeError, match="reservation"):
        m.execute_run(job, output, manifest)
    assert (Path(job["output_dir"]) / "failure.json").is_file()


def test_complete_run_resume_rechecks_all_artifact_receipts(monkeypatch, tmp_path):
    m, output, manifest = prepared(monkeypatch, tmp_path)
    calls = stub_tools(monkeypatch, m, manifest)
    job = manifest["jobs"][0]
    complete = m.execute_run(job, output, manifest)
    assert complete["status"] == "complete" and complete["sec_status"] == "pass"
    assert m.execute_run(job, output, manifest) == complete
    assert len(calls) == 1
    (Path(job["output_dir"]) / "final_sec/cells.v").write_text("tampered")
    with pytest.raises(RuntimeError, match="receipt|hash"):
        m.execute_run(job, output, manifest)
    assert len(calls) == 1


def test_unregistered_directory_is_never_overwritten(monkeypatch, tmp_path):
    m, output, manifest = prepared(monkeypatch, tmp_path)
    job = manifest["jobs"][0]
    run = Path(job["output_dir"])
    run.mkdir(parents=True)
    sentinel = run / "mapped.v"
    sentinel.write_text("foreign input")
    with pytest.raises(RuntimeError, match="Incomplete|unregistered"):
        m.execute_run(job, output, manifest)
    assert sentinel.read_text() == "foreign input"
    assert sorted(p.name for p in run.iterdir()) == ["mapped.v"]


def test_seven_arms_are_serial_within_one_circuit(monkeypatch, tmp_path):
    m, output, manifest = prepared(monkeypatch, tmp_path)
    seen = []
    monkeypatch.setattr(m, "execute_run", lambda job, *a, **k: seen.append(job["key"]) or job["key"])
    result = m.execute_circuit("s27", output, manifest)
    assert result == seen and len(seen) == 7
    assert [key.split("/")[0] for key in seen] == ["D"] * 5 + ["D_k1"] * 2


def test_preview_cannot_relabel_fixed_and_random_controls(monkeypatch, tmp_path):
    import copy
    m, _, _ = prepared(monkeypatch, tmp_path)
    read = m._read_json
    preview = copy.deepcopy(read(m.PREVIEW))
    for row in preview["D_runs"]:
        if row["family"] == "D" and row["circuit"] == "s27" and row["arm"] in {"fixed", "random_s1"}:
            row["arm"] = "random_s1" if row["arm"] == "fixed" else "fixed"
    monkeypatch.setattr(m, "_read_json", lambda path: preview if Path(path) == m.PREVIEW else read(path))
    with pytest.raises(RuntimeError, match="random|Random|control"):
        m.build_manifest(tmp_path / "relabeled")


def test_outer_timeout_keeps_failure_receipt_and_no_completion(monkeypatch, tmp_path):
    m, output, manifest = prepared(monkeypatch, tmp_path)
    def timeout(*args, **kwargs):
        raise m.subprocess.TimeoutExpired(args[0], 3930)
    monkeypatch.setattr(m.subprocess, "run", timeout)
    job = manifest["jobs"][0]
    with pytest.raises(RuntimeError, match="timed out"):
        m.execute_run(job, output, manifest)
    run = Path(job["output_dir"])
    assert json.loads((run / "failure.json").read_text(encoding="utf-8"))["returncode"] == 124
    assert not (run / "completion.json").exists()


def test_source_change_during_runner_prevents_sec_and_completion(monkeypatch, tmp_path):
    m, output, manifest = prepared(monkeypatch, tmp_path)
    stub_tools(monkeypatch, m, manifest)
    runner = m.subprocess.run
    def changed(*args, **kwargs):
        result = runner(*args, **kwargs)
        monkeypatch.setattr(m, "source_manifest", lambda: {"changed": "during-run"})
        return result
    monkeypatch.setattr(m.subprocess, "run", changed)
    monkeypatch.setattr(m, "final_sec", lambda *a: pytest.fail("SEC launched after source drift"))
    job = manifest["jobs"][0]
    with pytest.raises(RuntimeError, match="Source pin changed"):
        m.execute_run(job, output, manifest)
    assert (Path(job["output_dir"]) / "failure.json").exists()


def test_actual_feedback_config_change_rejected_before_sec(monkeypatch, tmp_path):
    m, output, manifest = prepared(monkeypatch, tmp_path)
    stub_tools(monkeypatch, m, manifest)
    job = next(job for job in manifest["jobs"] if job["arm"] == "adaptive")
    runner = m.subprocess.run
    def changed(*args, **kwargs):
        result = runner(*args, **kwargs)
        file = Path(job["output_dir"]) / "run_config.json"
        cfg = json.loads(file.read_text(encoding="utf-8"))
        cfg["feedback_config"]["rho"] = 0.9
        m.save(file, cfg)
        return result
    monkeypatch.setattr(m.subprocess, "run", changed)
    with pytest.raises(RuntimeError, match="feedback_config"):
        m.execute_run(job, output, manifest)
    assert not (Path(job["output_dir"]) / "completion.json").exists()


def test_batch_parallelism_is_capped_at_two_circuits(monkeypatch, tmp_path):
    import threading
    import time
    m, output, manifest = prepared(monkeypatch, tmp_path)
    output.mkdir()
    lock = threading.Lock()
    active = maximum = 0
    def circuit(name, *args):
        nonlocal active, maximum
        with lock:
            active += 1
            maximum = max(maximum, active)
        time.sleep(0.02)
        with lock:
            active -= 1
        return []
    monkeypatch.setattr(m, "execute_circuit", circuit)
    assert m.run_batch(["s27", "s382", "s420", "s641"], output, manifest) == 0
    assert maximum == 2


@pytest.mark.parametrize("tamper", ["model", "sec_result", "receipt"])
def test_resume_rejects_tampering_when_validator_returns_false(monkeypatch, tmp_path, tamper):
    m, output, manifest = prepared(monkeypatch, tmp_path)
    calls = stub_tools(monkeypatch, m, manifest)
    job = manifest["jobs"][0]
    m.execute_run(job, output, manifest)
    run = Path(job["output_dir"])
    if tamper == "model":
        (run / "final_sec/cells.v").write_text("tampered model", encoding="utf-8")
    elif tamper == "sec_result":
        file = run / "final_sec/result.json"
        value = m._read_json(file)
        value["status"] = "fail"
        m.save(file, value)
    else:
        file = run / "completion.json"
        value = m._read_json(file)
        value["evidence_receipt"]["final_sec/cells.v"] = "tampered receipt"
        m.save(file, value)
    validate = m.validate_completion
    def boolean_validator(*args):
        try:
            return validate(*args)
        except RuntimeError:
            return False
    assert boolean_validator(run, m._read_json(run / "completion.json"), (run / "mapped.v").read_text(encoding="utf-8")) is False
    monkeypatch.setattr(m, "validate_completion", boolean_validator)
    with pytest.raises(RuntimeError, match="SEC|receipt|validation"):
        m.execute_run(job, output, manifest)
    assert len(calls) == 1


def test_false_completion_validation_cannot_create_completion(monkeypatch, tmp_path):
    m, output, manifest = prepared(monkeypatch, tmp_path)
    stub_tools(monkeypatch, m, manifest)
    monkeypatch.setattr(m, "validate_completion", lambda *args: False)
    job = manifest["jobs"][0]
    with pytest.raises(RuntimeError, match="SEC|receipt|validation"):
        m.execute_run(job, output, manifest)
    run = Path(job["output_dir"])
    assert not (run / "completion.json").exists()
    assert (run / "failure.json").exists()
