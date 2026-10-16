"""Same-family D40 + k1 D16 revalidation using retained mapped inputs.

Register all 56 transactions with --dry-run, then select the two-circuit pilot
or remaining circuits with --circuits.  This does not change C-prime policies.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code/scripts"))
sys.path.insert(0, str(ROOT / "code/src"))
import run_r22_cut_ablation as common
from run_r22_cut_ablation import LIB, BASH, sha, save, source_manifest, final_sec, evidence_receipt, validate_completion
from rseco.feedback import ADAPTIVE_CONFIG
from rseco.sta_ledger import summarize_sta_ledger

PREVIEW = ROOT / "project_docs/evidence/r22_rerun_design_20261016/manifest_preview.json"
CIRCUITS = tuple(common.CIRCUITS)
ARMS = {"D": ("fixed", "adaptive", "random_s1", "random_s2", "random_s3"),
        "D_k1": ("fixed", "adaptive")}
SCHEMA = "r22-d-same-family-revalidation-v1"


def current_feedback_config():
    return asdict(ADAPTIVE_CONFIG)


def git_identity():
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, timeout=15).strip()
    status = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all", "--", "code"],
                                     cwd=ROOT, text=True, timeout=15)
    return {"head": head, "source_tree_clean": not bool(status.strip())}


def executable_pin():
    sources = dict(source_manifest())
    sources[Path(__file__).resolve().relative_to(ROOT).as_posix()] = sha(Path(__file__).resolve())
    return {**git_identity(), "files": sources}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def save_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def _relative(path):
    path = (ROOT / str(path).replace("\\", "/")).resolve()
    if not path.is_relative_to(ROOT):
        raise RuntimeError(f"Historical input outside repository: {path}")
    return path.relative_to(ROOT).as_posix()


def _read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _job(row, output):
    family, arm, circuit = row["family"], row["arm"], row["circuit"]
    if family not in ARMS or arm not in ARMS[family] or circuit not in CIRCUITS:
        raise RuntimeError("Unknown historical D matrix member")
    config_path = _relative(Path(row["historical_run"]) / "run_config.json")
    config = _read_json(ROOT / config_path)
    old = config["resolved_args"]
    if config["argv"] != row["historical_argv"] or old != row["historical_resolved_args"]:
        raise RuntimeError("Historical configuration changed from recovered preview")
    expected = {"circuit": circuit, "period": 0.5, "max_iterations": 20, "sta_budget": 500,
                "candidates_per_iteration": 8 if family == "D" else 1, "workers": 1,
                "joint_k": 2, "joint_enumerate_depth": 0, "strategies": "R,G,B",
                "enable_buffer": True, "early_stop": True, "tns_aware": False,
                "physical_gate": False, "proxy_ranking": False, "adaptive": False}
    if any(old.get(key) != value for key, value in expected.items()) or row.get("topology_enabled") is not True:
        raise RuntimeError("Recovered D scheduler/configuration contract is inconsistent")
    feedback = current_feedback_config() if arm == "adaptive" else None
    if config["feedback_config"] != feedback or config["enable_feedback"] != (arm == "adaptive"):
        raise RuntimeError("EMA feedback configuration changed from actual historical configuration")
    random_arm = arm.startswith("random_s")
    if (config["random_order"] != random_arm
            or config["seed"] != (int(arm[-1]) if random_arm else None)
            or old["no_feedback"] != (arm != "adaptive")):
        raise RuntimeError("Recovered fixed/random/EMA control identity is inconsistent")
    baseline = _relative(row["baseline_input"]["path"])
    if baseline != _relative(Path(row["historical_run"]) / "mapped.v") or sha(ROOT / baseline) != row["baseline_input"]["sha256"]:
        raise RuntimeError("Retained mapped input changed from recovered preview")
    out = output / family / arm / circuit
    argv = list(config["argv"])

    def option(flag, value):
        if flag in argv:
            argv[argv.index(flag) + 1] = str(value)
        else:
            argv.extend([flag, str(value)])

    option("--output-dir", out.parent)
    option("--iscas89-dir", ROOT / "data/raw/benchmarks/raw/iscas89")
    option("--cut-search-policy", "legacy")
    for flag, key in (("max-instances", "max_instances"), ("joint-enumerate-depth", "joint_enumerate_depth"),
                      ("strategies", "strategies"), ("clock-port", "clock_port"), ("epsilon", "epsilon"),
                      ("required-metrics", "required_metrics"), ("init-boundary-penalty", "init_boundary_penalty"),
                      ("init-size-penalty", "init_size_penalty"), ("init-critical-coverage-reward", "init_critical_coverage_reward")):
        option("--" + flag, old[key])
    argv.extend([flag for flag in ("--skip-mapping", "--no-proxy-ranking") if flag not in argv])
    if "--disable-topology" in argv or "--structure-resynth" in argv:
        raise RuntimeError("Recovered D command changed topology/S policy")
    command = [sys.executable, "-u", "-X", "utf8", str(common.RUNNER), *argv[1:]]
    resolved = {**old, "output_dir": str(out.parent), "iscas89_dir": str(ROOT / "data/raw/benchmarks/raw/iscas89"),
                "skip_mapping": True, "cut_search_policy": "legacy", "disable_topology": False,
                "structure_resynth": False}
    expected_config = {"argv": command[4:], "resolved_args": resolved,
                       **{key: config[key] for key in ("enable_feedback", "feedback_config_name", "feedback_config",
                                                      "random_order", "seed", "adaptive_ucb_decision_layer")}}
    return {"key": f"{family}/{arm}/{circuit}", "family": family, "arm": arm, "circuit": circuit,
            "historical_config": config_path, "historical_git_head": config["git_head"],
            "baseline": {"path": baseline, "sha256": row["baseline_input"]["sha256"]},
            "output_dir": str(out), "command": command, "expected_run_config": expected_config}


def build_manifest(output):
    output = Path(output).resolve()
    for archive in (ROOT / "experiments/20260924_threearm", ROOT / "experiments/20260924_l2_k1"):
        if output.is_relative_to(archive) or archive.is_relative_to(output):
            raise RuntimeError("New output must not overlap historical D archives")
    pin = executable_pin()
    preview = _read_json(PREVIEW)
    rows = preview["D_runs"]
    jobs = [_job(row, output) for row in rows]
    keys = {job["key"] for job in jobs}
    expected_keys = {f"{family}/{arm}/{c}" for family, arms in ARMS.items() for arm in arms for c in CIRCUITS}
    if len(jobs) != 56 or keys != expected_keys:
        raise RuntimeError("D matrix must contain exactly 40+16 unique registered runs")
    provenance = {PREVIEW.relative_to(ROOT).as_posix(): sha(PREVIEW)}
    for job in jobs:
        for name in (job["historical_config"], job["baseline"]["path"], f"data/raw/benchmarks/raw/iscas89/{job['circuit']}.v"):
            provenance[name] = sha(ROOT / name)
    for c in CIRCUITS:
        if len({job["baseline"]["sha256"] for job in jobs if job["circuit"] == c}) != 1:
            raise RuntimeError("D arms do not share identical mapped starting bytes")
    if executable_pin() != pin:
        raise RuntimeError("Source pin changed during registration")
    return {"schema": SCHEMA, "family": "historical-D-corrected-same-scheduler", "output_dir": str(output),
            "circuits": list(CIRCUITS), "source_pin": pin, "lib_sha256": sha(LIB), "liberty": _relative(LIB),
            "provenance": provenance, "jobs": jobs, "parallel_circuits": 2,
            "runner_timeout_s": 3900, "outer_timeout_s": 3930, "eda_executed_at_registration": False,
            "historical_limit": "Recorded historical HEAD/argv do not reconstruct unrecorded dirty runtime source; new runs use the new frozen corrected pin."}


def validate_manifest(manifest, output, *, require_clean=True):
    output = Path(output).resolve()
    if manifest.get("schema") != SCHEMA or manifest.get("output_dir") != str(output):
        raise RuntimeError("Registered manifest schema/output changed")
    if require_clean and not manifest["source_pin"]["source_tree_clean"]:
        raise RuntimeError("Registration is dirty; register a fresh output after the clean production commit")
    if executable_pin() != manifest["source_pin"]:
        raise RuntimeError("Source pin changed or executable source tree is no longer frozen")
    if sha(LIB) != manifest["lib_sha256"] or _relative(LIB) != manifest["liberty"]:
        raise RuntimeError("Library pin changed")
    for name, expected in manifest["provenance"].items():
        if _relative(name) != name or sha(ROOT / name) != expected:
            raise RuntimeError(f"Provenance/input changed: {name}")
    fresh = build_manifest(output)
    if fresh != manifest:
        raise RuntimeError("Registered commands/configuration/source pin changed")


def _stop(stop):
    if stop is not None and stop.is_set():
        raise RuntimeError("Batch stopped; no new D transaction or SEC will launch")


def _run_outputs(job, out, manifest):
    result = _read_json(out / "outerloop_result.json")
    config = _read_json(out / "run_config.json")
    expected = job["expected_run_config"]
    for key, value in expected.items():
        if key == "resolved_args":
            for arg, arg_value in value.items():
                actual = config[key].get(arg)
                if arg in {"output_dir", "iscas89_dir", "source_file", "priority_table"} and arg_value is not None:
                    actual = str(Path(str(actual).replace("\\", "/")).resolve())
                    arg_value = str(Path(str(arg_value).replace("\\", "/")).resolve())
                if actual != arg_value:
                    raise RuntimeError(f"Actual run configuration differs: {arg}")
        elif config.get(key) != value:
            raise RuntimeError(f"Actual run configuration differs: {key}")
    if config.get("git_head") != manifest["source_pin"]["head"]:
        raise RuntimeError("Runner recorded a different source HEAD")
    if result.get("cut_search_policy") != "legacy" or result.get("enable_topology") is not True:
        raise RuntimeError("Actual result changed D legacy/topology policy")
    state = result["state"]
    if hashlib.sha256(state["current_netlist_text"].encode("utf-8")).hexdigest() != state["current_netlist_hash"]:
        raise RuntimeError("Actual committed final state hash mismatch")
    ledger = _read_json(out / "eval_trials.json")
    if "sta_launch_events" not in ledger:
        raise RuntimeError("Missing actual STA launch event ledger")
    counts = summarize_sta_ledger(ledger["trials"], result["baseline_wns"], ledger["sta_launch_events"])
    n = counts["n_new_sta_runs"]
    if n != result["n_new_sta_runs"] or n != state["budget"].get("sta_used", 0):
        raise RuntimeError("Actual STA launch/reservation mismatch")
    if counts["n_candidate_evaluation_records"] != result["n_candidate_sta_runs"] or counts["n_candidate_evaluation_records"] != result["n_candidate_evaluation_records"]:
        raise RuntimeError("Candidate record count differs from saved ledger")
    seq = [event["seq"] for event in ledger["sta_launch_events"] if event.get("kind") == "candidate_ideal"]
    if sorted(seq) != list(range(1, n + 1)):
        raise RuntimeError("Actual candidate launch sequences are incomplete")
    counts["accepted_commits"] = len(state.get("accepted_patches", []))
    return result, counts


def _extra_receipt(out):
    names = ("preregistered.json", "runner.log", "final_sec/gold.v", "final_sec/gate.v")
    return {name: sha(out / name) for name in names}


def execute_run(job, output, manifest, stop=None):
    _stop(stop)
    validate_manifest(manifest, output)
    if job not in manifest["jobs"]:
        raise RuntimeError("Unregistered D job")
    out = Path(job["output_dir"])
    initial_path = ROOT / job["baseline"]["path"]
    initial = initial_path.read_text(encoding="utf-8")
    registration = {"manifest_sha256": fingerprint(manifest), "job": job}
    if out.exists():
        if not (out / "preregistered.json").is_file() or not (out / "completion.json").is_file():
            raise RuntimeError(f"Incomplete/unregistered prior run; do not overwrite: {out}")
        done = _read_json(out / "completion.json")
        if _read_json(out / "preregistered.json") != registration or done.get("registration_sha256") != fingerprint(registration):
            raise RuntimeError("Existing run registration/configuration changed")
        if done.get("status") != "complete" or done.get("returncode") != 0 or done.get("sec_returncode") != 0:
            raise RuntimeError("Existing run is incomplete")
        if not validate_completion(out, done, initial):
            raise RuntimeError("Independent SEC receipt validation returned false")
        result, counts = _run_outputs(job, out, manifest)
        if (done.get("accounting") != counts or done.get("result_sha256") != sha(out / "outerloop_result.json")
                or done.get("extra_receipt") != _extra_receipt(out)):
            raise RuntimeError("Completed run accounting/artifact receipt hash mismatch")
        validate_manifest(manifest, output)
        return done
    out.mkdir(parents=True)
    started = time.monotonic()
    failure = {"key": job["key"], "status": "failed", "returncode": None, "sec_status": "not_run"}
    try:
        save_new(out / "preregistered.json", registration)
        with (out / "mapped.v").open("xb") as handle:
            handle.write(initial_path.read_bytes())
        if sha(out / "mapped.v") != job["baseline"]["sha256"]:
            raise RuntimeError("Frozen mapped copy hash mismatch")
        _stop(stop)
        validate_manifest(manifest, output)
        print(f"LAUNCH {job['key']}", flush=True)
        with (out / "runner.log").open("x", encoding="utf-8") as log:
            proc = subprocess.run([str(BASH), str(ROOT / "code/scripts/run_with_timeout.sh"), "3900", *job["command"]],
                                  cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=3930)
        failure["returncode"] = proc.returncode
        if proc.returncode != 0:
            raise RuntimeError(f"Runner exit {proc.returncode}; inspect runner.log")
        validate_manifest(manifest, output)
        if sha(out / "mapped.v") != job["baseline"]["sha256"]:
            raise RuntimeError("Runner changed the frozen mapped baseline")
        result, counts = _run_outputs(job, out, manifest)
        _stop(stop)
        sec = final_sec(initial, result["state"]["current_netlist_text"], job["circuit"], out / "final_sec")
        failure.update(sec_status=sec["status"], sec_returncode=sec.get("returncode"))
        if sec["status"] != "pass" or sec.get("returncode") != 0:
            raise RuntimeError("Independent final SEC did not pass")
        validate_manifest(manifest, output)
        done = {"key": job["key"], "family": job["family"], "arm": job["arm"], "circuit": job["circuit"],
                "status": "complete", "returncode": proc.returncode, "sec_status": sec["status"],
                "sec_returncode": sec["returncode"], "registration_sha256": fingerprint(registration),
                "accounting": counts, "result_sha256": sha(out / "outerloop_result.json"),
                "baseline_wns": result["baseline_wns"], "final_wns": result["wns"],
                "runtime_s": time.monotonic() - started, "evidence_receipt": evidence_receipt(out),
                "extra_receipt": _extra_receipt(out)}
        if not validate_completion(out, done, initial):
            raise RuntimeError("Independent SEC receipt validation returned false")
        save_new(out / "completion.json", done)
        print(f"COMPLETE {job['key']}", flush=True)
        return done
    except Exception as error:
        if stop is not None:
            stop.set()
        if isinstance(error, subprocess.TimeoutExpired):
            failure["returncode"] = 124
        failure.update(error=str(error), runtime_s=time.monotonic() - started,
                       artifacts={path.relative_to(out).as_posix(): sha(path) for path in sorted(out.rglob("*")) if path.is_file()})
        save_new(out / "failure.json", failure)
        raise RuntimeError(f"{job['key']}: {error}") from error


def execute_circuit(circuit, output, manifest, stop=None):
    try:
        return [execute_run(job, output, manifest, stop) for job in manifest["jobs"] if job["circuit"] == circuit]
    except Exception:
        if stop is not None:
            stop.set()
        raise


def run_batch(circuits, output, manifest):
    stop = threading.Event()
    completed, failed = [], []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(execute_circuit, c, output, manifest, stop): c for c in circuits}
        for future in as_completed(futures):
            try:
                completed.extend(future.result())
            except Exception as error:
                stop.set()
                failed.append({"circuit": futures[future], "error": str(error)})
                for pending in futures:
                    if pending is not future:
                        pending.cancel()
            # Summary is a derived index; per-run complete receipts are authoritative.
            save(Path(output) / "batch_summary.json", {"selected_circuits": circuits, "complete": completed, "failures": failed})
    return 1 if failed else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--circuits", default="s27,s382")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    circuits = args.circuits.split(",")
    if not circuits or len(set(circuits)) != len(circuits) or any(c not in CIRCUITS for c in circuits):
        parser.error("Use distinct registered D circuits")
    output = args.output_dir.resolve()
    manifest_path = output / "manifest.json"
    if manifest_path.exists():
        manifest = _read_json(manifest_path)
        validate_manifest(manifest, output, require_clean=not args.dry_run)
    elif args.dry_run:
        if output.exists() and any(output.iterdir()):
            raise RuntimeError("Unregistered nonempty output directory; do not overwrite")
        manifest = build_manifest(output)
        save_new(manifest_path, manifest)
    else:
        raise RuntimeError("Register a fresh manifest with --dry-run before formal execution")
    if args.dry_run:
        print(f"Registered D56; selected {7 * len(circuits)} runs; no mapping/STA/SEC executed", flush=True)
        return 0
    validate_manifest(manifest, output)
    return run_batch(circuits, output, manifest)


if __name__ == "__main__":
    raise SystemExit(main())
