#!/usr/bin/env python3
"""Trace the frozen 40 ns TT power runs at the compiled 50-pass ceiling."""

import argparse
from hashlib import file_digest
import json
from pathlib import Path
import re
import subprocess
from time import monotonic


EVIDENCE = Path(__file__).resolve().parent
OR_BINARY = Path("/home/toylog/.cache/bazel/_bazel_toylog/c540bbdc4bbb635360729b4d7a91c803"
                 "/execroot/_main/bazel-out/k8-opt/bin/openroad_unstamped")
OR_SHA256 = "2d9662715130538b50e93b614c33099a5e183eef0cc31b642099daea8d203e19"
DEBUG = "sta::set_debug power_activity 1"
WARNING = "[WARNING STA-2402] power activity propagation through registers did not converge after 50 passes."
PASS = re.compile(r"(?m)^.*?Pass (\d+) change (\S+)(?: (\S*))?\s*$")


def sha256_for(path):
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def identity(path):
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_for(path)}


def bind(item):
    path = Path(item["path"])
    if identity(path) != item:
        raise ValueError(f"Frozen input identity mismatch: {path}")
    return path


def power_body(raw):
    prefix, body = raw.split("{", 1)
    return prefix, "{" + body


def trace_run(root, label, baseline, physical, liberty, sdc):
    original_tcl = bind(baseline["tcl"])
    original_report = bind(baseline["raw_report"])
    odb, spef = (bind(physical[key]) for key in ("odb", "spef"))
    inputs = [liberty, odb, sdc, spef]
    identities = [identity(path) for path in inputs]
    expected = [f"{command} {json.dumps(str(path))}"
                for command, path in zip(("read_liberty", "read_db", "read_sdc", "read_spef"), inputs, strict=True)]
    expected += [f"report_power -digits 9 -format json > {json.dumps(str(original_report))}",
                 "puts PWR_OK", "exit"]
    script = original_tcl.read_text(encoding="utf-8").splitlines()
    if script != expected:
        raise ValueError(f"Unexpected original script commands: {original_tcl}")
    case = root / label
    case.mkdir()
    report = case / "power.json"
    tcl = case / "trace.tcl"
    tcl.write_text("\n".join([*script[:4], DEBUG,
                              f"report_power -digits 9 -format json > {json.dumps(str(report))}",
                              *script[5:]]) + "\n", encoding="utf-8")
    log = case / "trace.log"
    command = ["timeout", "--kill-after=2s", "90s", "taskset", "-c", "0-5", str(OR_BINARY),
               "-no_init", "-no_splash", "-threads", "1", "-exit", str(tcl)]
    started = monotonic()
    with log.open("wb") as stream:
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, check=False)
    elapsed = monotonic() - started
    log_text = log.read_text(encoding="utf-8")
    if result.returncode or "PWR_OK" not in log_text.splitlines():
        raise RuntimeError(f"Tool failed ({result.returncode}): {log}")
    raw_prefix, raw_body = power_body(original_report.read_text(encoding="utf-8"))
    prefix, body = power_body(report.read_text(encoding="utf-8"))
    if raw_body != body or WARNING not in raw_prefix or WARNING not in (prefix + log_text):
        raise ValueError(f"Archived and traced power results differ: {report}")
    matches = PASS.findall(prefix + "\n" + log_text)
    if [int(number) for number, *_ in matches] != list(range(1, 51)):
        raise ValueError(f"Incomplete debug trace: {tcl}")
    if identities != [identity(path) for path in inputs]:
        raise ValueError(f"Input bytes changed while reading {tcl}")
    return {"input_bindings": identities, "command": command, "returncode": result.returncode,
            "seconds": elapsed, "tcl": identity(tcl), "log": identity(log),
            "traced_report": identity(report), "archived_report": baseline["raw_report"],
            "archived_tcl": baseline["tcl"], "power_body_byte_match": True,
            "activity_warning": WARNING, "passes": [
                {"pass": int(number), "displayed_max_relative_activity_update": change, "pin": pin}
                for number, change, pin in matches]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workdir", type=Path, help="Fresh absolute output directory")
    args = parser.parse_args()
    if not args.workdir.is_absolute() or sha256_for(OR_BINARY) != OR_SHA256:
        raise ValueError("Invalid output path or pinned OpenROAD digest")
    table_path = EVIDENCE / "V5_STAGE5_TABLE12.json"
    table = json.loads(table_path.read_bytes())
    control = json.loads(bind(table["reference_qualification"]).read_bytes())
    one_liberty, = table["tt_power_policy"]["liberty"]
    liberty = bind(one_liberty)
    sdc = bind(table["tt_power_policy"]["sdc"])
    root = args.workdir
    root.mkdir()
    started = monotonic()
    readback = {"reference": trace_run(root, "reference", table["reference_tt_power"],
                                       control["control_output_paths"], liberty, sdc)}
    for label, arm in table["arms"].items():
        terminal = arm["accepted_trace"][-1]
        physical = json.loads(bind(terminal["physical_receipt"]).read_bytes())
        readback[label] = trace_run(root, label, arm["tt_power_measurement"], physical["artifacts"], liberty, sdc)
    result = {"openroad": identity(OR_BINARY), "table12": identity(table_path), "cases": readback,
              "elapsed_seconds": monotonic() - started}
    (root / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for label, case in readback.items():
        print(f"{label}: {case['seconds']:.3f}s; 50 passes; {case['passes'][-1]}")


if __name__ == "__main__":
    main()
