"""Cross frozen AES ODB and SPEF artifacts to attribute relative hold changes."""

from argparse import ArgumentParser
from hashlib import file_digest
from itertools import product
from pathlib import Path
import json
import os
import re
import subprocess
import time


EXPECTED = {
    ("02", "SS"): ("key[35]", "u0.w[2][3]$_DFF_P_", "_19304_/Y"),
    ("05", "FF"): ("sa03_sr[5]$_DFF_P_", "text_out[29]$_DFF_P_", "_17769_/X"),
    ("05", "TT"): ("sa03_sr[5]$_DFF_P_", "text_out[29]$_DFF_P_", "_17769_/X"),
}
TIMEOUT_SECONDS = 90
RECEIPT_TOLERANCE_PS = 0.000001


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def verify(binding):
    path = Path(binding["path"]).resolve(strict=True)
    with path.open("rb") as stream:
        sha = file_digest(stream, "sha256").hexdigest()
    if sha != binding["sha256"] or path.stat().st_size != binding["bytes"]:
        raise ValueError(f"changed input artifact {path}")
    return path


def render(lib, sdc, odb, spef):
    return f"""if {{[catch {{
    read_liberty {{{lib}}}
    read_db {{{odb}}}
    read_sdc {{{sdc}}}
    if {{[llength [all_clocks]] == 0}} {{ error "No clocks in saved SDC" }}
    read_spef {{{spef}}}
    puts "AES_HOLD_PS [expr {{1e12 * [sta::worst_slack_cmd min]}}]"
    puts "AES_HOLD_TNS_PS [expr {{1e12 * [sta::total_negative_slack_cmd min]}}]"
    puts AES_ANNOTATION_BEGIN
    report_parasitic_annotation -report_unannotated
    puts AES_ANNOTATION_END
    puts AES_PATH_BEGIN
    report_checks -path_delay min -group_path_count 1 -endpoint_path_count 1 \\
        -digits 9 -no_line_splits -format full_clock_expanded \\
        -fields {{capacitance slew fanout input_pin net}}
    puts AES_PATH_END
}} problem]}} {{
    puts stderr "AES_PROBE_ERROR $problem"
    exit 2
}}
puts AES_PROBE_COMPLETE
exit
"""


def field(log, pattern):
    match = re.search(pattern, log, flags=re.MULTILINE)
    if not match:
        raise ValueError(f"missing field {pattern}")
    return match[1]


def block(log, label):
    return log.split(f"{label}_BEGIN\n")[1].split(f"{label}_END")[0]


def parse(log, expected, matched_reference):
    if "AES_PROBE_COMPLETE" not in log or re.search(
        r"(?mi)^\s*(?:\[ERROR\s|Error:)|(?:net|pin).*not found|no paths found", log
    ):
        raise ValueError("STA reported an error or missing path")
    hold = float(field(log, r"^AES_HOLD_PS (\S+)"))
    tns = float(field(log, r"^AES_HOLD_TNS_PS (\S+)"))
    annotations = block(log, "AES_ANNOTATION")
    if "Found 0 partially unannotated drivers." not in annotations:
        raise ValueError("unexpected partial SPEF annotation")
    paths = re.split(r"(?m)(?=^Startpoint: )", block(log, "AES_PATH"))
    clock_path, = [path for path in paths if "\nPath Group: clk\n" in path]
    startpoint = field(clock_path, r"^Startpoint: (\S+)")
    endpoint = field(clock_path, r"^Endpoint: (\S+)")
    if (startpoint, endpoint) != expected[:2] or expected[2] not in clock_path:
        raise ValueError(f"changed minimum-path identity {startpoint} -> {endpoint}")
    path_slack_ps = 1000.0 * float(field(clock_path, r"^\s*(\S+)\s+slack \("))
    if abs(path_slack_ps - hold) > 0.001:
        raise ValueError("expanded minimum path does not account for hold WNS")
    if matched_reference is not None:
        for name, value in {"hold_wns_ps": hold, "hold_tns_ps": tns}.items():
            if abs(value - matched_reference[name]) > RECEIPT_TOLERANCE_PS:
                raise ValueError(f"matched row disagrees with original {name}")
    return {
        "hold_wns_ps": hold,
        "hold_tns_ps": tns,
        "unannotated_drivers": annotations,
        "startpoint": startpoint,
        "endpoint": endpoint,
        "matched_path_slack_ps": path_slack_ps,
        "matched_path": clock_path,
        "matched_original_receipt": matched_reference is not None,
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("original_matrix", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root = args.original_matrix.resolve(strict=True)
    out = args.output.resolve()
    out.mkdir(parents=True)
    cfg = read_json(root / "config.json")["bindings"]
    control = cfg["control"]
    tool = verify(cfg["tools"]["openroad"])
    sdc = verify(control["sdc"])
    manifest = {"source": str(root), "openroad": cfg["tools"]["openroad"], "sdc": control["sdc"],
                "worker_affinity": sorted(os.sched_getaffinity(0)),
                "timeout_seconds_per_read": TIMEOUT_SECONDS, "cases": {}}
    results = {}
    jobs = []
    for (slot, corner), expected in EXPECTED.items():
        ctrl_path = root / "control/receipt.json"
        edit_path = root / f"screened/fixed/{slot}_physical/receipt.json"
        edit = read_json(edit_path)
        if edit["control_sdc"] != control["sdc"]:
            raise ValueError(f"candidate {slot} does not bind CONTROL SDC")
        library, = cfg["used_libraries"][corner]
        lib = verify(library)
        by_origin = {"C": control, "E": edit["artifacts"]}
        refs = {"C": read_json(ctrl_path)["views"][corner], "E": edit["views"][corner]}
        for odb_origin, rc_origin in product("CE", repeat=2):
            name = f"{slot}_{corner}_{odb_origin}{rc_origin}"
            odb_binding = by_origin[odb_origin]["odb"]
            spef_binding = by_origin[rc_origin]["spef"]
            odb, spef = verify(odb_binding), verify(spef_binding)
            matched = odb_origin == rc_origin
            manifest["cases"][name] = {
                "lib": library, "odb": odb_binding, "spef": spef_binding,
                "expected_path": expected, "matched_reference": refs[odb_origin] if matched else None,
                "reference_receipt": str(ctrl_path if odb_origin == "C" else edit_path) if matched else None,
            }
            jobs.append((name, lib, odb, spef, expected, refs[odb_origin] if matched else None))
    save_json(out / "inputs.json", manifest)
    for name, lib, odb, spef, expected, reference in jobs:
        script = out / f"{name}.tcl"
        script.write_text(render(lib, sdc, odb, spef), encoding="utf-8")
        log = script.with_suffix(".log")
        start = time.monotonic()
        with log.open("w", encoding="utf-8") as stream:
            subprocess.run([tool, "-no_init", "-no_splash", "-threads", "1", "-exit", script],
                           cwd=out, stdout=stream, stderr=subprocess.STDOUT,
                           timeout=TIMEOUT_SECONDS, check=True)
        case = parse(log.read_text(encoding="utf-8"), expected, reference)
        case["wall_seconds"] = time.monotonic() - start
        control_case = results.get(f"{name[:-2]}CC", case)
        if case["unannotated_drivers"] != control_case["unannotated_drivers"]:
            raise ValueError(f"changed SPEF annotation in {name}")
        results[name] = case
        save_json(out / "results.json", results)
        print(name, case["hold_wns_ps"], case["hold_tns_ps"], flush=True)


if __name__ == "__main__":
    main()
