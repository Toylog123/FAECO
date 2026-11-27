#!/usr/bin/env python3
"""Observe tool processes across the arms of a private Stage 5 replay."""

import argparse
import json
import os
from pathlib import Path
import time


POLL_SECONDS = 0.20
POST_EXIT_SECONDS = 10.0


def read_json(path):
    try:
        return json.loads(path.read_bytes())
    except FileNotFoundError:
        return None


def process_rows(namespace, run_root, worker):
    rows = {}
    arms_prefix = f"{run_root}/arms/"
    for proc in Path("/proc").iterdir():
        if not proc.name.isdecimal() or int(proc.name) == worker:
            continue
        try:
            if os.readlink(proc / "ns/mnt") != namespace:
                continue
            stat = (proc / "stat").read_text().rsplit(") ", 1)[1].split()
            if stat[0] == "Z":
                continue
            argv = (proc / "cmdline").read_bytes().rstrip(b"\0").decode(errors="replace").split("\0")
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        matching = [item.split("/", 1)[0] for arg in argv if (item := arg.removeprefix(arms_prefix)) != arg]
        rows[(int(proc.name), int(stat[19]))] = {
            "pid": int(proc.name), "start_ticks": int(stat[19]), "ppid": int(stat[1]),
            "pgid": int(stat[2]), "sid": int(stat[3]), "arms": sorted(set(matching)), "argv": argv,
        }
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_root", type=Path)
    parser.add_argument("event_log", type=Path)
    parser.add_argument("--max-seconds", type=float, default=3050.0)
    args = parser.parse_args()
    root = args.run_root.resolve()
    end = time.monotonic() + args.max_seconds
    with args.event_log.open("x", encoding="utf-8", buffering=1) as log:
        def emit(event, **value):
            log.write(json.dumps({"event": event, "raw_s": time.clock_gettime(time.CLOCK_MONOTONIC_RAW),
                                  **value}) + "\n")

        seed = None
        while seed is None and time.monotonic() < end:
            seed = read_json(root / "replay_protocol.json")
            if seed is None:
                time.sleep(POLL_SECONDS)
        if seed is None:
            raise TimeoutError("no Stage 5 replay protocol appeared")
        worker, namespace = seed["pid"], seed["namespace"]["mnt"]
        emit("observer_start", worker=worker, namespace=namespace, interval_s=POLL_SECONDS,
             observer_affinity=sorted(os.sched_getaffinity(0)))
        previous, previous_phase = {}, None
        samples, after_exit, max_gap = 0, None, 0.0
        previous_sample = time.monotonic()
        while time.monotonic() < end:
            now = time.monotonic()
            max_gap = max(max_gap, now - previous_sample)
            previous_sample = now
            state = read_json(root / "stage5_progress.json") or {}
            arm = (state.get("active_arm") or {}).get("name")
            completed = tuple(state.get("arms", ()))
            phase = (state.get("status"), arm, completed)
            current = process_rows(namespace, root, worker)
            if phase != previous_phase:
                emit("phase", status=phase[0], arm=arm, completed=completed, processes=list(current.values()))
                previous_phase = phase
            started = [current[key] for key in current.keys() - previous.keys()]
            ended = [previous[key] for key in previous.keys() - current.keys()]
            if started or ended:
                emit("process_change", arm=arm, started=started, ended=ended)
            previous = current
            samples += 1
            if not Path(f"/proc/{worker}").exists():
                if after_exit is None:
                    after_exit = now
                    emit("worker_exit", status=phase[0], processes=list(current.values()))
                elif now - after_exit >= POST_EXIT_SECONDS:
                    emit("observer_finished", status=phase[0], samples=samples, max_gap_s=max_gap,
                         processes=list(current.values()))
                    return
            time.sleep(POLL_SECONDS)
        emit("observer_timeout", samples=samples, max_gap_s=max_gap, processes=list(previous.values()))
        raise TimeoutError("observer reached its limit before the worker exit tail completed")


if __name__ == "__main__":
    main()
