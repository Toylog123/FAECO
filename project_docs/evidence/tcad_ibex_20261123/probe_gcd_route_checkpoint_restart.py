#!/usr/bin/env python3
"""Run the GCD re-entry benchmark with a clean router process after the checkpoint."""

from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

import probe_gcd_local_route_reentry as benchmark


comparison = benchmark.comparison
ORIGINAL_PROCESS = comparison.run_process
ORIGINAL_SAVE = comparison.save


def run_split(argv, logfile, timeout, *, env=None):
    deck = Path(argv[-1])
    if deck.name != "route.tcl":
        return ORIGINAL_PROCESS(argv, logfile, timeout, env=env)
    body = deck.read_text(encoding="utf-8")
    if benchmark.STEPS[0] not in body:
        return ORIGINAL_PROCESS(argv, logfile, timeout, env=env)
    start = benchmark.geometry.raw_seconds()
    out = deck.parent
    checkpoint, unlock_and_finish = body.split("set checkpoint_fd", 1)
    checkpoint += """
puts "RESUME_CHECKPOINT_SAVE_US [expr {[clock microseconds] - $restore_start}]"
puts RESUME_CHECKPOINT_WRITTEN
exit
"""
    global_header = body[:body.index("read_db ")]
    tool_setup = body[body.index("read_sdc "):body.index("\nset inst ")]
    restart = f"{global_header}read_db {comparison.tcl(out / 'checkpoint.odb')}\n{tool_setup}\n"
    restart += "set restore_start [clock microseconds]\nset checkpoint_fd" + unlock_and_finish
    restart = restart.replace('if {![design_is_routed]} {error "Unrouted nets after resumed DRT"}',
                              f'if {{![design_is_routed]}} {{write_def {comparison.tcl(out / "failed.def")}; error "Unrouted nets after resumed DRT"}}')
    logs, receipts = [], []
    for name, stage in (("checkpoint", checkpoint), ("restart", restart)):
        file, log = out / f"{name}.tcl", out / f"{name}.log"
        file.write_text(stage, encoding="utf-8")
        limit = max(0.1, timeout - (benchmark.geometry.raw_seconds() - start))
        process = ORIGINAL_PROCESS([*argv[:-1], file], log, limit, env=env)
        logs.append(log.read_bytes())
        receipts.append({"stage": name, "tcl": comparison.bind(file), "result": asdict(process)})
        if process.returncode != 0:
            break
    logfile.write_bytes(b"\n".join(logs))
    comparison.save(out / "split_launches.json", {"charged_stages": receipts})
    return comparison.ProcessResult(process.returncode, benchmark.geometry.raw_seconds() - start, timeout, str(logfile))


def save_split_protocol(path, data):
    if path.name == "protocol.json" and "same_process_resume" in data:
        data = {**data, "same_process_resume": False, "restart_starts_from_checkpoint_odb": True,
                "restart_source": comparison.bind(Path(__file__).resolve())}
    return ORIGINAL_SAVE(path, data)


if __name__ == "__main__":
    with patch.object(comparison, "run_process", run_split), patch.object(comparison, "save", save_split_protocol):
        benchmark.main()
