#!/usr/bin/env python3
"""Measure resource use and downstream checkpoint reads for two frozen Stage 5 arms."""

import argparse
from dataclasses import asdict
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import run_v5_step5_10k_timing_closed as stage
from verify_review_evidence import SHA256


ARMS = {"fixed_boxed": "fixed", "faeco_boxed": "faeco"}
POLL_SECONDS = 0.05
ARM_TIMEOUT_SECONDS = 735.0
STRICT_ZERO_SHA = "3d0e3908188856627ac8e90a5556b9e033d9d425587eb24851c5911f81939edf"


def prepare(frozen, output):
    output.mkdir()
    state_path = frozen / "stage5_progress.json"
    if stage.cmp.sha(state_path) != SHA256[5]:
        raise ValueError("Stage 5 source receipt differs from the published comparison")
    state = stage.read(state_path)
    control = stage.read(stage.verify(state["qualification"]))
    protocol = stage.read(stage.verify(state["protocol"]))
    prepared = stage.verify(protocol["screen_install"])
    zero = frozen / "strict_zero.json"
    if stage.cmp.sha(zero) != STRICT_ZERO_SHA:
        raise ValueError("strict zero receipt changed")
    for source, name in ((prepared, "search_inputs.json"), (zero, "strict_zero.json")):
        shutil.copyfile(source, output / name)

    args = stage.candidate_args(frozen, control, stage.VARIANTS["tc40ns_mmmc_drv"])
    runner = stage.prepare_search(output, args)
    comparable = runner.config | {"screen_install": protocol["screen_install"]}
    if comparable != protocol:
        raise ValueError("live preparation disagrees with the frozen Stage 5 protocol")
    reference = stage.strict_zero(output, runner)
    if asdict(reference) != state["reference"] or len(state["rank_order"]) != stage.POOL_SIZE:
        raise ValueError("strict zero or rank order differs from the frozen Stage 5 comparison")
    return runner, reference, state


def scope_snapshot(scope):
    cpu = dict(line.split() for line in (scope / "cpu.stat").read_text().splitlines())
    return {
        "raw": stage.raw_seconds(),
        "cpu_usec": {key: int(cpu[key]) for key in ("usage_usec", "user_usec", "system_usec")},
        "memory_peak_bytes": int((scope / "memory.peak").read_text()),
    }


def worker(args):
    scope_name = Path("/proc/self/cgroup").read_text().strip().removeprefix("0::/")
    scope = Path("/sys/fs/cgroup") / scope_name
    if scope.name != args.scope_unit or str(os.getpid()) not in (scope / "cgroup.procs").read_text().split():
        raise ValueError("worker is outside the expected accounting scope")
    initial = scope_snapshot(scope)
    stage.cmp.save(args.output / "scope.json", {"path": str(scope), "initial": initial})
    with (
        stage.bind_runtime(stage.TOP, stage.ROUTING),
        stage.qualified.qualified_ranking(),
        stage.qualified.qualified_process_clock(),
    ):
        runner, reference, state = prepare(args.frozen, args.output / "stage")
        runner.output = args.output / "arm"
        runner.output.mkdir()
        runner.eval.args.out = runner.output
        start = scope_snapshot(scope)
        summary, reuse = stage.run_aligned_strategy(
            runner, stage.STRATEGIES[args.arm], reference, {"order": state["rank_order"]},
            stage.qualified.matrix.run_strategy,
        )
        search_return = scope_snapshot(scope)
        arm_root = runner.output / summary["method"]
        progress = stage.read(arm_root / "progress.json")
        requests = {f"{row['id']:02d}": row for row in progress["logical_requests"]}
        commits = [stage.checked_commit(reference, row, requests, runner.eval)
                   for row in progress["checkpoints"] if row["accepted"]]
        after_audit = scope_snapshot(scope)
        stage.cmp.save(args.output / "producer.json", {
            "frozen_state": stage.cmp.bind(args.frozen / "stage5_progress.json"),
            "scope": str(scope), "initial": initial, "before_search": start,
            "search_return": search_return, "after_checkpoint_audit": after_audit,
            "search_cpu_usec": {key: search_return["cpu_usec"][key] - start["cpu_usec"][key]
                                for key in start["cpu_usec"]},
            "scope_peak_memory_bytes": after_audit["memory_peak_bytes"],
            "screen_charge_s": runner.screen, "summary": stage.cmp.bind(arm_root / "summary.json"),
            "progress": stage.cmp.bind(arm_root / "progress.json"),
            "tool_ledger": stage.cmp.bind(arm_root / "subprocesses.json"),
            "commits": commits, "exact_setup_only_dedup_hits": reuse,
        })


def process_rss(scope):
    try:
        pids = (scope / "cgroup.procs").read_text().split()
    except FileNotFoundError:
        return 0, 0
    values = []
    for pid in pids:
        try:
            status = Path(f"/proc/{pid}/status").read_text()
        except (FileNotFoundError, ProcessLookupError):
            continue
        for line in status.splitlines():
            if line.startswith("VmRSS:"):
                values.append(int(line.split()[1]))
                break
    return sum(values), len(values)


def observe_checkpoints(progress_path, scope_root, seen):
    try:
        progress = stage.read(progress_path)
    except FileNotFoundError:
        return None
    observed = stage.raw_seconds()
    for row in progress["checkpoints"]:
        endpoint = row["endpoint"]["evidence_id"]
        if not row["accepted"] or endpoint in seen:
            continue
        path = Path(endpoint).resolve(strict=True)
        if not path.is_relative_to(scope_root):
            raise ValueError("observer found a checkpoint outside the new arm")
        evidence = stage.read(path / "receipt.json")
        for artifact in ("odb", "def", "v", "spef"):
            stage.verify(evidence["artifacts"][artifact])
        seen[endpoint] = {
            "endpoint": endpoint, "accepted_accounted_seconds": row["elapsed_seconds"],
            "accepted_progress_observed_raw": observed, "artifacts_read_and_verified_raw": stage.raw_seconds(),
        }
    return observed if progress["stop_reason"] is not None else None


def observe(args):
    args.output.mkdir(parents=True)
    unit = f"faeco-v4-{os.getpid()}-{ARMS[args.arm]}.scope"
    command = [
        "systemd-run", "--user", "--scope", "--quiet", "--unit", unit,
        "-p", "CPUAccounting=yes", "-p", "MemoryAccounting=yes",
        "taskset", "-c", "0-5", sys.executable, "-B", str(Path(__file__).resolve()),
        args.arm, str(args.frozen), str(args.output), "--scope-unit", unit,
    ]
    scope = None
    samples = 0
    peak_rss = {"rss_kib": 0, "processes": 0, "raw": None}
    checkpoints = {}
    stopped = None
    progress = args.output / "arm" / ARMS[args.arm] / "progress.json"
    launched = stage.raw_seconds()
    with (args.output / "console.log").open("wb") as console:
        process = subprocess.Popen(command, stdout=console, stderr=subprocess.STDOUT)
        try:
            while process.poll() is None:
                now = stage.raw_seconds()
                if now - launched >= ARM_TIMEOUT_SECONDS:
                    raise TimeoutError(f"{args.arm} outer scope did not return")
                if scope is None and (args.output / "scope.json").is_file():
                    scope = Path(stage.read(args.output / "scope.json")["path"])
                    if scope.name != unit:
                        raise ValueError("refusing to read another job's scope")
                if scope is not None:
                    rss, count = process_rss(scope)
                    samples += int(count > 0)
                    if rss > peak_rss["rss_kib"]:
                        peak_rss = {"rss_kib": rss, "processes": count, "raw": now}
                observed = observe_checkpoints(progress, args.output / "arm", checkpoints)
                if stopped is None:
                    stopped = observed
                time.sleep(POLL_SECONDS)
        finally:
            if process.poll() is None:
                subprocess.run(["systemctl", "--user", "stop", unit], timeout=10, check=True)
                process.wait(timeout=10)
    returned = stage.raw_seconds()
    observed = observe_checkpoints(progress, args.output / "arm", checkpoints)
    if stopped is None:
        stopped = observed
    stage.cmp.save(args.output / "observer.json", {
        "command": command, "launch_raw": launched, "scope_return_observed_raw": returned,
        "returncode": process.returncode, "poll_interval_seconds": POLL_SECONDS,
        "sample_count": samples, "sampled_sum_rss_peak": peak_rss,
        "stopped_progress_observed_raw": stopped, "checkpoints": list(checkpoints.values()),
    })
    if process.returncode != 0:
        raise SystemExit(process.returncode)
    if not checkpoints or stopped is None or samples == 0:
        raise ValueError("no observed accepted checkpoint, stop record, or resource sample")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arm", choices=ARMS)
    parser.add_argument("frozen", type=Path)
    parser.add_argument("output", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--prepare-only", action="store_true")
    mode.add_argument("--scope-unit")
    args = parser.parse_args()
    args.frozen = args.frozen.resolve(strict=True)
    args.output = args.output.resolve()
    if args.output.is_relative_to(args.frozen):
        parser.error("use a new output root outside the frozen experiment")
    if args.prepare_only:
        with stage.bind_runtime(stage.TOP, stage.ROUTING):
            runner, _, _ = prepare(args.frozen, args.output)
        print(f"{len(runner.pool)} frozen actions; screen charge {runner.screen:.6f} s")
    elif args.scope_unit:
        worker(args)
    else:
        observe(args)


if __name__ == "__main__":
    main()
