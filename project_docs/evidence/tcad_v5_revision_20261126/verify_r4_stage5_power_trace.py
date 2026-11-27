#!/usr/bin/env python3
"""Verify the R4 TT trace and extract the same-run terminal timing offline."""

from hashlib import sha256
import json
from pathlib import PurePosixPath
from zipfile import ZipFile

from generate_stage5_table12 import REBUILT, REBUILT_SHA
from replay_r4_stage5_power_trace import EVIDENCE, OR_SHA256, PASS, WARNING, identity, power_body
from verify_stage5_sec_fixed_replay import V2_ROOT


TRACE_ARCHIVE = "R4_STAGE5_POWER_TRACE_ORIGINALS.zip"
TRACE_SHA256 = "8a8892c2f15692c45e9baf653ea3e2b0793b3979dbdc490330af7ff99a7c8a85"
TIMING_KEYS = ("setup_wns_ps", "hold_wns_ps", "setup_tns_ps", "hold_tns_ps")
CORNERS = ("FF", "TT", "SS")


def verified_bytes(archive, member, expected):
    raw = archive.read(member)
    if len(raw) != expected["bytes"] or sha256(raw).hexdigest() != expected["sha256"]:
        raise ValueError(f"Unbound member: {member}")
    return raw


def replay_member(binding):
    return (PurePosixPath("replay") / PurePosixPath(binding["path"]).relative_to(
        PurePosixPath(V2_ROOT))).as_posix()


def trace_case(trace, previous, label, case, baseline, expected_inputs):
    original_raw = verified_bytes(previous, replay_member(baseline["raw_report"]), baseline["raw_report"])
    original_tcl = verified_bytes(previous, replay_member(baseline["tcl"]), baseline["tcl"])
    traced_raw = verified_bytes(trace, f"{label}/power.json", case["traced_report"])
    traced_tcl = verified_bytes(trace, f"{label}/trace.tcl", case["tcl"])
    log = verified_bytes(trace, f"{label}/trace.log", case["log"])
    if case["input_bindings"] != expected_inputs or case["returncode"] or log.strip() != b"PWR_OK":
        raise ValueError(f"Unexpected replay acceptance or input: {label}")
    original_lines = original_tcl.decode().splitlines()
    traced_lines = traced_tcl.decode().splitlines()
    if (traced_lines[:4] != original_lines[:4] or traced_lines[4] != "sta::set_debug power_activity 1"
            or traced_lines[5].split(" > ", 1)[0] != original_lines[4].split(" > ", 1)[0]
            or traced_lines[6:] != original_lines[5:]):
        raise ValueError(f"Unexpected change in measurement script: {label}")
    old_status, old_body = power_body(original_raw.decode())
    status, body = power_body(traced_raw.decode())
    if old_body != body or WARNING not in status or WARNING not in old_status:
        raise ValueError(f"Archived power numbers or diagnostic changed: {label}")
    trace_rows = [{"pass": int(number), "displayed_max_relative_activity_update": change, "pin": pin}
                  for number, change, pin in PASS.findall(status)]
    if [row["pass"] for row in trace_rows] != list(range(1, 51)) or trace_rows != case["passes"]:
        raise ValueError(f"Activity trace is incomplete or unbound: {label}")
    return trace_rows[-1]


def show(label, timing, last):
    fields = [[timing[corner][key] for corner in CORNERS] for key in TIMING_KEYS]
    print(f"{label}: FF/TT/SS")
    for key, values in zip(TIMING_KEYS, fields, strict=True):
        print(f"  {key} = " + " / ".join(f"{value:.6f}" for value in values))
    print(f"  50 passes; last activity delta = {last['displayed_max_relative_activity_update']} at {last['pin']}")


def main():
    table_path = EVIDENCE / "V5_STAGE5_TABLE12.json"
    table = json.loads(table_path.read_bytes())
    archive_path = EVIDENCE / TRACE_ARCHIVE
    if identity(archive_path)["sha256"] != TRACE_SHA256:
        raise ValueError("Power trace archive digest mismatch")
    rebuilt_path = EVIDENCE / REBUILT
    if identity(rebuilt_path)["sha256"] != REBUILT_SHA:
        raise ValueError("Rebuilt reference archive digest mismatch")
    with ZipFile(archive_path) as trace, ZipFile(rebuilt_path) as rebuilt:
        results = json.loads(trace.read("results.json"))
        if (results["openroad"]["sha256"] != OR_SHA256
                or results["table12"]["sha256"] != identity(table_path)["sha256"]):
            raise ValueError("Power trace OpenROAD or Table 12 identity mismatch")
        reference = json.loads(verified_bytes(rebuilt, "rebuild/CONTROL.json", table["reference_qualification"]))
        cases = {"reference": (table["reference_tt_power"], None)}
        cases.update({label: (arm["tt_power_measurement"], arm["accepted_trace"][-1]["physical_receipt"])
                      for label, arm in table["arms"].items()})
        members = ["results.json"] + [f"{label}/{name}" for label in cases
                                     for name in ("power.json", "trace.tcl", "trace.log")]
        if sorted(trace.namelist()) != sorted(members):
            raise ValueError("Power trace archive member set mismatch")
        one_liberty, = table["tt_power_policy"]["liberty"]
        sdc = table["tt_power_policy"]["sdc"]
        if results["cases"].keys() != cases.keys():
            raise ValueError("Power trace case set mismatch")
        for label, (baseline, terminal) in cases.items():
            suffix = label.upper() if terminal else "COMMON"
            path = EVIDENCE / f"V5_STAGE5_SEC_FIXED_{suffix}.zip"
            if identity(path)["sha256"] != table["fixed_archives"][path.name]:
                raise ValueError(f"Stage 5 archive digest mismatch: {suffix}")
            with ZipFile(path) as previous:
                endpoint = (json.loads(verified_bytes(previous, replay_member(terminal), terminal))
                            if terminal else reference)
                files = endpoint["artifacts"] if terminal else endpoint["control_output_paths"]
                expected_inputs = [one_liberty, files["odb"], sdc, files["spef"]]
                last = trace_case(trace, previous, label, results["cases"][label], baseline, expected_inputs)
                show(label, endpoint["views"], last)


if __name__ == "__main__":
    main()
