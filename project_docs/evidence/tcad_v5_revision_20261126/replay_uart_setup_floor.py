#!/usr/bin/env python3
"""Replay the six R3-1 STA reports on byte-pinned routed inputs."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path, PurePosixPath
import sys
from zipfile import ZipFile

from verify_review_evidence import (
    COLLECTED_ROOT, REVIEW_FLOOR, REVIEW_HASHES, REVIEW_ORIGINALS,
    check_bytes, check_review_floor, original, require,
)

EVIDENCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVIDENCE / "tcad_ibex_20261123"))
import compare_ibex as cmp


def relative(binding):
    return PurePosixPath(binding["path"]).relative_to(COLLECTED_ROOT).as_posix()


def replay_inputs(protocol, physical):
    control = json.loads((EVIDENCE / "tcad_holdout_20261123/UART_CONTROL_VERIFIED.json").read_bytes())
    control_inputs = {item["path"]: item for item in control["input_bindings"]}
    control_odb = str(PurePosixPath(protocol["reference"]["v"]["path"]).with_suffix(".odb"))
    endpoints = {
        "reference": (control_inputs[control_odb], protocol["reference"]["spef"]),
        "candidate": (physical["artifacts"]["odb"], protocol["candidate"]["spef"]),
    }
    tool = control_inputs[str(cmp.OPENROAD)]
    require(tool["sha256"] == cmp.OPENROAD_SHA, "unexpected OpenROAD binding")
    bindings = [tool, *(item for pair in endpoints.values() for item in pair),
                *(item for corner in cmp.CORNERS for item in protocol["libraries"][corner])]
    return tool, endpoints, {relative(item): item for item in bindings}


def run(archive, floor, protocol, args, tool, endpoints, bindings):
    root = args.inputs_root.resolve(strict=True)
    inputs = {name: (root / name).resolve(strict=True) for name in bindings}
    for name, path in inputs.items():
        require(path.is_relative_to(root), f"input resolves outside the supplied root: {name}")
        binding = cmp.bind(path)
        require(binding["sha256"] == bindings[name]["sha256"] and binding["bytes"] == bindings[name]["bytes"],
                f"input bytes differ: {name}")

    output = args.output.resolve()
    output.mkdir(parents=True)
    sdc = output / "uart_470p5ps.sdc"
    sdc.write_bytes(original(archive, protocol["analyzed_sdc"]))
    executable = inputs[relative(tool)]
    runs = {}
    for mode, (odb_binding, spef_binding) in endpoints.items():
        odb = inputs[relative(odb_binding)]
        spef = inputs[relative(spef_binding)]
        verilog = odb.with_suffix(".v")
        routed_stanza = f"read_verilog {cmp.tcl(verilog)}\nlink_design {cmp.TOP}"
        target = output / mode
        target.mkdir()
        runs[mode] = {}
        for corner, liberty_bindings in protocol["libraries"].items():
            libraries = [inputs[relative(item)] for item in liberty_bindings]
            tcl = cmp.render_sta(libraries, verilog, sdc, spef, report_setup_endpoints=True)
            require(tcl.count(routed_stanza) == 1, "unexpected STA template")
            script = target / f"sta_{corner}.odb.tcl"
            script.write_text(tcl.replace(routed_stanza, f"read_db {cmp.tcl(odb)}"), encoding="utf-8")
            log = target / f"sta_{corner}.log"
            result = cmp.run_process([executable, "-no_init", "-no_splash", "-threads", "1", "-exit", script],
                                     log, 15.0)
            report = cmp.checked_output(result, "IBEX_STA_COMPLETE")
            view = cmp.parse_sta(report)
            require(view == floor["views"][mode][corner], f"timing data differ: {mode}/{corner}")
            for local, item in zip([*libraries, odb, spef, sdc],
                                   [*liberty_bindings, odb_binding, spef_binding, protocol["analyzed_sdc"]]):
                report = report.replace(str(local), item["path"])
            historical = original(archive, floor["sta_logs"][mode][corner]).decode()
            header = f"IBEX_STA_ROUTED_ODB {odb_binding['path']}\n"
            require(historical.startswith(header), f"unexpected routed database: {mode}/{corner}")
            require(report == historical.removeprefix(header), f"raw STA report differs: {mode}/{corner}")
            runs[mode][corner] = {"operation": asdict(result), "log": cmp.bind(log),
                                  "tcl": cmp.bind(script), "view": view, "report_matches": True}

    cmp.save(output / "REPLAY_VERIFIED.json", {
        "input_bindings": bindings, "inputs_root": str(root), "analyzed_sdc": cmp.bind(sdc),
        "source_review": REVIEW_HASHES[REVIEW_FLOOR], "source_archive": REVIEW_HASHES[REVIEW_ORIGINALS],
        "reference_qualified": floor["reference_qualified"], "relative_reasons": floor["relative_reasons"],
        "absolute_reasons": floor["absolute_reasons"], "reports": runs,
    })
    print("6 fresh STA reports match the archived reports and parsed timing data")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list-inputs", action="store_true", help="print the input paths relative to the input root")
    parser.add_argument("--inputs-root", type=Path)
    parser.add_argument("--output", type=Path, help="new output directory")
    args = parser.parse_args()
    if not args.list_inputs and (args.inputs_root is None or args.output is None):
        parser.error("provide --list-inputs or both --inputs-root and --output")
    evidence = EVIDENCE / "tcad_v5_revision_20261126"
    floor_bytes = (evidence / REVIEW_FLOOR).read_bytes()
    check_bytes(floor_bytes, REVIEW_HASHES[REVIEW_FLOOR], REVIEW_FLOOR)
    floor = json.loads(floor_bytes)
    require(cmp.sha(evidence / REVIEW_ORIGINALS) == REVIEW_HASHES[REVIEW_ORIGINALS], "review archive SHA mismatch")
    with ZipFile(evidence / REVIEW_ORIGINALS) as archive:
        protocol = json.loads(original(archive, floor["protocol"]))
        physical = json.loads(original(archive, protocol["candidate"]["physical"]))
        tool, endpoints, bindings = replay_inputs(protocol, physical)
        if args.list_inputs:
            print("\n".join(bindings))
            return
        check_review_floor(archive, floor)
        run(archive, floor, protocol, args, tool, endpoints, bindings)


if __name__ == "__main__":
    main()
