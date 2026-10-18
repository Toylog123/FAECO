"""Evidence-only C greedy reconstruction. No mapping, C-prime, or outerloop.

The CLI previews by default. Execution requires a separately reviewed frozen
pin; the supplied reconstruction preview deliberately cannot authorize it.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
import hashlib
import json
import math
from pathlib import Path
import random
import re
import subprocess
import sys
import threading
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "code/src"))
sys.path.insert(0, str(ROOT / "code/scripts"))
sys.path.insert(0, str(HERE))
from run_hybrid_repair import _accepts


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def save(path, value):
    with Path(path).open("x", encoding="utf-8", newline="") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write(path, text):
    with Path(path).open("x", encoding="utf-8", newline="") as stream:
        stream.write(text)


def write_bytes(path, value):
    with Path(path).open("xb") as stream:
        stream.write(value if isinstance(value, bytes) else (value or "").encode("utf-8"))


class PinDrift(RuntimeError):
    pass


class BudgetExhausted(RuntimeError):
    pass


class StaFailure(RuntimeError):
    pass


class PinGuard:
    def __init__(self, files):
        self.files = {Path(path): expected for path, expected in files.items()}

    def __call__(self):
        for path, expected in self.files.items():
            if not path.is_file() or sha(path) != expected:
                raise PinDrift("Frozen source/input/library changed: " + str(path))


@dataclass(frozen=True)
class Action:
    instance: str
    kind: str
    target: str
    pin_map: dict = field(default_factory=dict)
    pin: str = ""
    new_net: str = ""


@dataclass(frozen=True)
class Config:
    rounds: int = 20
    period: float = 0.5
    workers: int = 2
    only_strategy: str | None = None
    enable_buffer: bool = True
    buf_types: tuple = ("sky130_fd_sc_hd__buf_1", "sky130_fd_sc_hd__buf_2")
    random_order: bool = False
    seed: int = 20260806
    tns_aware: bool = False
    joint_pairs: int = 0
    sta_budget: int = 0
    wall_timeout_s: float = 3600
    clock_port: str = "CK"
    strategy_priorities: str = ""

    def __post_init__(self):
        if (self.rounds < 1 or self.workers not in (1, 2) or self.sta_budget < 0
                or self.joint_pairs < 0 or self.period <= 0 or self.wall_timeout_s <= 0):
            raise ValueError("Invalid bounded reconstruction configuration")
        if self.only_strategy not in (None, "R", "G", "B") or self.strategy_priorities:
            raise ValueError("Only the explicitly declared empty-priority recipes are supported")


def run_schedule(initial, config, backend, output, *, guard=None,
                 process_runner=None, retained_input=None):
    """Native historical pass/instance/JOINT order; injectable tool boundaries.

    Simulated backends produce qa_complete, never a scientific completion.
    Every external STA retry goes through invoke; helper calls are not counts.
    """
    if guard is None and not backend.simulated:
        raise RuntimeError("Live execution requires a frozen source/input guard")
    guard = guard or (lambda: None)
    guard()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    write(output / "initial.v", initial)
    if retained_input is not None:
        with (output / "retained_mapped.v").open("xb") as stream:
            stream.write(Path(retained_input).read_bytes())
        guard()
    save(output / "config.json", asdict(config))
    write(output / "events.jsonl", "")
    mutex = threading.RLock()
    immutable_files = {path: sha(path) for path in (output / "initial.v", output / "config.json")}
    if retained_input is not None:
        immutable_files[output / "retained_mapped.v"] = sha(output / "retained_mapped.v")
    counts = {name: 0 for name in (
        "candidate_proposals", "candidate_evaluations", "precheck_rejects", "budget_rejects",
        "sta_reservations", "sta_launches", "failed_launch_attempts", "candidate_sta_launches",
        "joint_sta_launches", "baseline_sta_launches", "refresh_sta_launches", "final_sta_launches",
        "candidate_reservations", "cache_hits", "commits", "sec_calls")}
    sequence = 0
    deadline = time.monotonic() + config.wall_timeout_s
    runner = process_runner or subprocess.run
    trials, commits, passes = [], [], []

    def remember(*paths):
        with mutex:
            for path in paths:
                digest = sha(path)
                if path in immutable_files and immutable_files[path] != digest:
                    raise PinDrift("Previously checked evidence changed: " + str(path))
                immutable_files[path] = digest

    def verify_evidence():
        for path, expected in immutable_files.items():
            if not path.is_file() or sha(path) != expected:
                raise PinDrift("Previously checked trial/input artifact changed: " + str(path))

    def event(kind, **fields):
        nonlocal sequence
        with mutex:
            sequence += 1
            row = {"seq": sequence, "kind": kind, **fields}
            with (output / "events.jsonl").open("a", encoding="utf-8", newline="") as stream:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")

    def remaining():
        return None if not config.sta_budget else max(0, config.sta_budget - counts["candidate_reservations"])

    def measure(text, directory, role):
        directory.mkdir()
        write(directory / "mapped.v", text)
        expected = sha(directory / "mapped.v")
        attempt = 0
        expected_tcl = None
        expected_lib = None
        last_argv = None

        def sta_path(token):
            # The reused legacy Tcl writer emits one literal absolute path.
            # Do not invent a Tcl evaluator or accept substitutions/multi-input
            # syntax that this adapter cannot bind to exact archived bytes.
            token = token.strip()
            if token.startswith("{") and token.endswith("}"):
                token = token[1:-1]
            elif token.startswith('"') and token.endswith('"'):
                token = token[1:-1]
            elif any(char.isspace() for char in token):
                raise PinDrift("Unsupported unquoted STA path")
            if any(char in token for char in ('$','[',']',';','\\','"','{','}')):
                raise PinDrift("Unsupported dynamic/escaped STA path")
            mounted = re.fullmatch(r"/mnt/([a-zA-Z])/(.*)", token)
            if mounted:
                token = mounted.group(1).upper() + ":/" + mounted.group(2)
            path = Path(token)
            if not path.is_absolute():
                raise PinDrift("STA input path is not absolute")
            return path.resolve()

        def input_snapshot(argv):
            nonlocal expected_tcl, expected_lib
            if sha(directory / "mapped.v") != expected:
                raise PinDrift("STA input changed before invocation")
            tcl_path = directory / "sta.tcl"
            if not tcl_path.is_file():
                raise StaFailure("STA helper did not emit a Tcl input")
            tcl_bytes = tcl_path.read_bytes()
            tcl_digest = hashlib.sha256(tcl_bytes).hexdigest()
            if expected_tcl is not None and tcl_digest != expected_tcl:
                raise PinDrift("STA Tcl changed between attempts")
            lines = re.findall(r"^read_verilog[ \t]+(.+?)[ \t\r]*$",
                               tcl_bytes.decode("utf-8"), re.M)
            if len(lines) != 1:
                raise PinDrift("Expected exactly one supported full-netlist read_verilog")
            actual_path = sta_path(lines[0])
            if actual_path != (directory / "mapped.v").resolve():
                raise PinDrift("STA Tcl does not read the evaluated mapped input")
            if not backend.simulated and sta_path(str(argv[-1])) != tcl_path.resolve():
                raise PinDrift("Actual STA command does not execute the captured Tcl")
            actual_bytes = actual_path.read_bytes()
            actual_digest = hashlib.sha256(actual_bytes).hexdigest()
            if actual_digest != expected:
                raise PinDrift("Actual read_verilog bytes changed before invocation")
            library = {}
            lib_lines = re.findall(r"^read_liberty[ \t]+(.+?)[ \t\r]*$",
                                   tcl_bytes.decode("utf-8"), re.M)
            if not backend.simulated or lib_lines:
                import run_r22_cut_ablation as common
                if len(lib_lines) != 1:
                    raise PinDrift("Expected exactly one registered read_liberty input")
                lib_path = sta_path(lib_lines[0])
                if lib_path != common.LIB.resolve():
                    raise PinDrift("STA Tcl does not read the registered Liberty")
                lib_digest = sha(lib_path)
                if expected_lib is not None and lib_digest != expected_lib:
                    raise PinDrift("Actual read_liberty bytes changed across invocation")
                expected_lib = lib_digest
                library = {"read_liberty_token": lib_lines[0],
                    "resolved_read_liberty_path": str(lib_path),
                    "read_liberty_sha256": lib_digest, "read_liberty_bytes": lib_path.stat().st_size}
            expected_tcl = tcl_digest
            return tcl_bytes, actual_bytes, {"tcl_sha256": tcl_digest,
                "read_verilog_token": lines[0], "resolved_read_verilog_path": str(actual_path),
                "read_verilog_sha256": actual_digest, "read_verilog_bytes": len(actual_bytes), **library}

        def invoke(argv, **kwargs):
            nonlocal attempt, last_argv
            guard()
            # In particular this must precede every retry's runner call.
            tcl_bytes, input_bytes, snapshot = input_snapshot(argv)
            last_argv = argv
            with mutex:
                if time.monotonic() >= deadline:
                    raise BudgetExhausted("Run wall deadline exhausted before STA")
                if role in ("candidate", "joint") and remaining() == 0:
                    raise BudgetExhausted("Actual candidate STA launch budget exhausted")
                attempt += 1
                attempt_dir = directory / ("attempt_%03d" % attempt)
                attempt_dir.mkdir()
                counts["sta_reservations"] += 1
                if role in ("candidate", "joint"):
                    counts["candidate_reservations"] += 1
                event("sta_reserved", role=role, attempt=attempt, directory=str(attempt_dir))
            kwargs["timeout"] = max(0.001, min(float(kwargs.get("timeout", 900)), deadline - time.monotonic()))
            save(attempt_dir / "command.json", {"argv": list(argv), "timeout_s": kwargs["timeout"],
                "input_sha256": expected, "tcl_sha256": snapshot["tcl_sha256"], "role": role})
            write_bytes(attempt_dir / "sta.tcl", tcl_bytes)
            write_bytes(attempt_dir / "read_verilog_input.v", input_bytes)
            save(attempt_dir / "input_snapshot.json", snapshot)
            started = time.monotonic()
            observed, rc = False, None
            outcome = "not_started"
            try:
                guard()
                if sha(directory / "mapped.v") != expected or sha(directory / "sta.tcl") != expected_tcl:
                    raise PinDrift("STA input/Tcl changed immediately before runner call")
                event("sta_invocation_attempt", role=role, directory=str(attempt_dir), command=list(argv))
                proc = runner(argv, **kwargs)
                observed, rc = True, proc.returncode
                outcome = "returned"
                write_bytes(attempt_dir / "stdout.log", proc.stdout)
                write_bytes(attempt_dir / "stderr.log", proc.stderr)
                if rc:
                    raise StaFailure("STA returned nonzero: " + str(rc))
                return proc
            except subprocess.TimeoutExpired as error:
                observed = True  # run() raises this after the process was started.
                outcome = "timeout"
                write_bytes(attempt_dir / "stdout.log", error.stdout)
                write_bytes(attempt_dir / "stderr.log", error.stderr)
                write(attempt_dir / "timeout.txt", str(error))
                raise
            finally:
                with mutex:
                    if observed:
                        counts["sta_launches"] += 1
                        counts[role + "_sta_launches"] += 1
                    else:
                        counts["failed_launch_attempts"] += 1
                    save(attempt_dir / "invocation.json", {"process_observed": observed,
                        "simulated": backend.simulated, "returncode": rc, "outcome": outcome,
                        "runtime_s": time.monotonic() - started})
                    event("sta_invocation_finished", role=role, process_observed=observed,
                          returncode=rc, simulated=backend.simulated, directory=str(attempt_dir))
                guard()
                # The last invocation may have no retry. Check exact Tcl and
                # both actual read inputs after success/failure/timeout alike.
                input_snapshot(argv)

        guard()
        try:
            result = backend.measure(text, directory, role, invoke, config)
        except (StaFailure, BudgetExhausted, subprocess.TimeoutExpired, OSError) as error:
            result = {"wns": None, "tns": None, "error": str(error), "critical": []}
        guard()
        if attempt:
            input_snapshot(last_argv)
        if sha(directory / "mapped.v") != expected:
            raise PinDrift("STA mapped bytes changed")
        if attempt == 0 and "error" not in result:
            raise RuntimeError("STA helper returned without a recorded invocation")
        if result.get("wns") is not None and not math.isfinite(result["wns"]):
            result = {**result, "wns": None, "error": "nonfinite WNS"}
        save(directory / "measurement.json", result)
        remember(*(path for path in directory.rglob("*") if path.is_file()))
        return result

    def precheck(base, candidate):
        guard()
        result = backend.validate(base, candidate)
        guard()
        if not isinstance(result, dict) or result.get("status") != "pass":
            raise ValueError("Candidate F1/F2/domain rejected: " + str(result))

    precheck(initial, initial)
    baseline = measure(initial, output / "baseline", "baseline")
    if baseline.get("wns") is None:
        raise RuntimeError("No valid baseline STA; retained incomplete output")
    text, current = initial, baseline
    rng = random.Random(config.seed)
    stop_reason = "round_cap"

    def evaluate_group(base, actions_group, rnd, stage):
        prepared = []
        for actions in actions_group:
            number = len(trials)
            directory = output / ("trial_%06d" % number)
            directory.mkdir()
            action = asdict(actions[0]) if len(actions) == 1 else {
                "instance": "+".join(a.instance for a in actions), "kind": "JOINT",
                "target": "+".join(a.target for a in actions)}
            row = {"trial_id": number, "round": rnd, "stage": stage,
                   "action": action, "actions": [asdict(a) for a in actions],
                   "directory": str(directory), "base_sha256": text_sha(base)}
            trials.append(row)
            counts["candidate_proposals"] += 1
            counts["candidate_evaluations"] += 1
            write(directory / "base.v", base)
            remember(directory / "base.v")
            event("candidate_evaluation", trial_id=number, stage=stage, action=action)
            try:
                candidate = base
                for action_item in actions:
                    candidate = backend.apply(candidate, action_item)
                write(directory / "candidate.v", candidate)
                remember(directory / "candidate.v")
                row["candidate_sha256"] = text_sha(candidate)
                row["same_bytes_as_base"] = candidate == base
                precheck(base, candidate)
                row["status"] = "ready"
            except ValueError as error:
                row.update(status="precheck_reject", reason=str(error))
                counts["precheck_rejects"] += 1
                event("precheck_reject", trial_id=number, reason=str(error))
            save(directory / "proposal.json", row)
            remember(directory / "proposal.json")
            if row["status"] == "ready":
                prepared.append((row, candidate))
        limit = remaining()
        if limit is not None:
            for row, _ in prepared[limit:]:
                row.update(status="budget_reject", reason="No unreserved actual STA budget")
                counts["budget_rejects"] += 1
                event("budget_reject", trial_id=row["trial_id"])
            prepared = prepared[:limit]

        def evaluate(item):
            row, candidate = item
            row["metrics"] = measure(candidate, Path(row["directory"]) / "sta",
                                     "joint" if stage == "JOINT" else "candidate")
            row["status"] = "measured" if row["metrics"].get("wns") is not None else "sta_failed"
            if sha(Path(row["directory"]) / "candidate.v") != row["candidate_sha256"]:
                raise PinDrift("Candidate changed after evaluation")
            return row

        if config.workers > 1 and len(prepared) > 1:
            with ThreadPoolExecutor(max_workers=config.workers) as pool:
                futures = [pool.submit(evaluate, item) for item in prepared]
                evaluated = [future.result() for future in futures]  # submission order
        else:
            evaluated = [evaluate(item) for item in prepared]
        for row in trials:
            path = Path(row["directory"]) / "decision.json"
            if not path.exists():
                save(path, row)
                remember(path)
        return evaluated

    def commit(row):
        nonlocal text, current
        guard()
        candidate_path = Path(row["directory"]) / "candidate.v"
        if row["base_sha256"] != text_sha(text) or sha(candidate_path) != row["candidate_sha256"]:
            raise PinDrift("Commit is not bound to the evaluated current-base candidate")
        candidate = candidate_path.read_text(encoding="utf-8")
        precheck(text, candidate)
        entry = {"commit_id": len(commits), "trial_id": row["trial_id"], "action": row["action"],
                 "base_sha256": row["base_sha256"], "candidate_sha256": row["candidate_sha256"]}
        save(output / ("commit_%06d.json" % len(commits)), entry)
        remember(output / ("commit_%06d.json" % len(commits)))
        commits.append(entry)
        counts["commits"] += 1
        text, current = candidate, row["metrics"]
        event("commit", **entry)

    for rnd in range(1, config.rounds + 1):
        guard()
        snapshot = backend.snapshot(text)
        refresh = measure(text, output / ("pass_%03d_refresh" % rnd), "refresh")
        if refresh.get("wns") is None:
            raise RuntimeError("Critical-path refresh failed")
        critical = list(refresh.get("critical", []))
        if not critical:
            stop_reason = "no_critical_instances"
            break
        improved, best_by_inst = False, {}
        for inst in critical:
            if remaining() == 0:
                break
            actions = list(backend.candidates(snapshot, inst, config))
            if config.random_order:
                rng.shuffle(actions)
            rows = evaluate_group(text, [[action] for action in actions], rnd, "SINGLE")
            best, best_metrics = None, current
            for row in rows:
                value = row["metrics"]
                if _accepts(best_metrics["wns"], best_metrics.get("tns"),
                            value.get("wns"), value.get("tns"), config.tns_aware):
                    best, best_metrics = row, value
            if best is not None:
                commit(best)
                improved = True
                best_by_inst[inst] = Action(**best["actions"][0])
        # Historical JOINT re-applies accepted singles to the CURRENT text.
        # A repeated buffer may fail F1/F2; never silently rebase to pass start.
        names = sorted(best_by_inst)
        pairs = [(a, b) for i, a in enumerate(names) for b in names[i + 1:]][:config.joint_pairs]
        for a, b in pairs:
            if remaining() == 0:
                break
            rows = evaluate_group(text, [[best_by_inst[a], best_by_inst[b]]], rnd, "JOINT")
            if rows:
                row, value = rows[0], rows[0]["metrics"]
                if _accepts(current["wns"], current.get("tns"), value.get("wns"),
                            value.get("tns"), config.tns_aware):
                    commit(row)
                    improved = True
        passes.append({"round": rnd, "critical_order": critical, "improved": improved,
                       "refresh_metrics": refresh, "current_metrics": current})
        if not improved:
            stop_reason = "no_improvement"
            break
        if remaining() == 0:
            stop_reason = "candidate_sta_budget"
            break
    verify_evidence()
    final = measure(text, output / "final_sta", "final")
    write(output / "final.v", text)
    remember(output / "final.v")
    verify_evidence()
    guard()
    if deadline - time.monotonic() < 180:
        raise BudgetExhausted("Insufficient remaining wall time for independent final SEC")
    expected_proof = backend.prepare_sec(initial, text, output / "sec_preflight")
    save(output / "sec_preflight" / "binding.json", expected_proof)
    remember(*(path for path in (output / "sec_preflight").rglob("*") if path.is_file()))
    guard()
    counts["sec_calls"] += 1
    proof = backend.sec(initial, text, output / "final_sec")
    guard()
    verify_evidence()
    required = ("initial_raw.v", "final_raw.v", "gold.v", "gate.v", "cells.v", "helpers.v",
                "sec.ys", "sec.log", "result.json")
    proof_dir = output / "final_sec"
    proof_bound = all((proof_dir / name).is_file() for name in required)
    if proof_bound:
        saved = json.loads((proof_dir / "result.json").read_text(encoding="utf-8"))
        proof_bound = (saved == proof and saved.get("initial_sha256") == sha(proof_dir / "initial_raw.v")
            and saved.get("final_sha256") == sha(proof_dir / "final_raw.v")
            and saved.get("shared_helpers_sha256") == sha(proof_dir / "helpers.v")
            and (proof_dir / "initial_raw.v").read_text(encoding="utf-8") == initial
            and (proof_dir / "final_raw.v").read_text(encoding="utf-8") == text
            and all((proof_dir / name).read_text(encoding="utf-8") == content
                    for name, content in expected_proof["splits"].items())
            and sha(Path(expected_proof["model_path"])) == expected_proof["model_sha256"]
            and sha(proof_dir / "cells.v") == expected_proof["model_sha256"])
    log = (proof_dir / "sec.log").read_text(encoding="utf-8") if (proof_dir / "sec.log").is_file() else ""
    proof_points = re.findall(r"Of those cells (\d+) are proven and (\d+) are unproven", log)
    nonempty_proof = (bool(proof_points) and all(int(proven) > 0 and int(unproven) == 0
                         for proven, unproven in proof_points)
                     and "Equivalence successfully proven!" in log
                     and re.search(r"No\s+SAT\s+model\s+available", log, re.I) is None)
    passed = (proof_bound and proof.get("status") == "pass" and proof.get("returncode") == 0
              and nonempty_proof
              and final.get("wns") is not None and counts["failed_launch_attempts"] == 0
              and counts["sta_reservations"] == counts["sta_launches"])
    result = {"schema": "r22-C-reconstruction-run-v1", "simulated": backend.simulated,
        "status": ("qa_complete" if backend.simulated else "complete") if passed else "failed",
        "stop_reason": stop_reason, "initial_sha256": text_sha(initial), "final_sha256": text_sha(text),
        "final_text": text, "baseline": baseline, "final_metrics": final, "counts": counts,
        "trials": trials, "commits": commits, "passes": passes,
        "sec_status": proof.get("status"), "sec_bound": proof_bound,
        "sec_nonempty_supported_proof": nonempty_proof, "sec_proof_points": proof_points}
    event("run_finished", status=result["status"], counts=counts)
    save(output / "run_result.json", result)
    guard()
    verify_evidence()
    result["evidence_receipt"] = {p.relative_to(output).as_posix(): sha(p)
        for p in sorted(output.rglob("*")) if p.is_file()}
    save(output / "completion.json", result)
    return result


def source_manifest():
    import run_r22_cut_ablation as common
    files = {ROOT / p for p in common.source_manifest()}
    files.add(ROOT / "code/scripts/run_hybrid_repair.py")
    files.update(p for p in HERE.iterdir() if p.suffix in {".py", ".json", ".md"})
    files.update(HERE.parent / p for p in ("README.md", "manifest_preview.json",
                                        "C_RECOVERY_EXTENSION.md", "C_RECOVERY_EXTENSION.json"))
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(files)}


def run_frozen(pin, arm, circuit, output):
    """Future explicit entry point; never turns the preview into a registration."""
    if not pin.get("execution_ready") or pin.get("family") != "C-reconstruction-r22":
        raise RuntimeError("A preview cannot execute; supply a separately registered frozen pin")
    import run_r22_cut_ablation as common
    from backend import ActualBackend
    preview = json.loads((HERE / "recipe_preview.json").read_text(encoding="utf-8"))
    recipe = next((row for row in preview["runs"] if row["arm"] == arm and row["circuit"] == circuit), None)
    if recipe is None or pin.get("source_manifest") != source_manifest() or pin.get("lib_sha256") != sha(common.LIB):
        raise RuntimeError("Unregistered recipe/source/library")
    if pin.get("mapped_inputs") != preview["mapped_inputs"]:
        raise RuntimeError("Mapped input registration differs from reviewed preview")
    def clean_head():
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all", "--",
            "code", HERE.relative_to(ROOT).as_posix()], cwd=ROOT, text=True)
        if head != pin.get("git_head") or dirty:
            raise PinDrift("Live execution requires the clean registered HEAD and adapter")
    clean_head()
    files = {ROOT / path: digest for path, digest in pin["source_manifest"].items()}
    files[common.LIB] = pin["lib_sha256"]
    for row in pin["mapped_inputs"].values():
        files[ROOT / row["path"]] = row["sha256"]
    guard = PinGuard(files)
    guard()
    source = ROOT / pin["mapped_inputs"][circuit]["path"]
    result = run_schedule(source.read_text(encoding="utf-8"), Config(**recipe["new_reconstruction_values"]),
        ActualBackend(circuit), output, guard=guard, retained_input=source)
    guard()
    clean_head()
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-pin", type=Path)
    parser.add_argument("--arm")
    parser.add_argument("--circuit")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.execute_pin:
        if not all((args.arm, args.circuit, args.output_dir)):
            parser.error("Execution needs arm/circuit/new output-dir")
        result = run_frozen(json.loads(args.execute_pin.read_text(encoding="utf-8")), args.arm, args.circuit, args.output_dir)
        print(json.dumps({key: result[key] for key in ("status", "counts", "sec_status")}))
        return 0 if result["status"] == "complete" else 1
    preview = json.loads((HERE / "recipe_preview.json").read_text(encoding="utf-8"))
    print(json.dumps({"execution_ready": False, "runs": len(preview["runs"]),
                     "formal_source_pin": None, "family": preview["family"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
