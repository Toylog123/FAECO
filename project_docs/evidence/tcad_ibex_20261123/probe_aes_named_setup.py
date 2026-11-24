#!/usr/bin/env python3
"""Measure one exact AES setup endpoint on control and repaired artifacts."""

from argparse import ArgumentParser
from pathlib import Path
import re

import compare_ibex as comparison
from probe_aes_selective_repair import read, verify


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("endpoint", nargs="?", help="defaults to the only new SS negative setup endpoint")
    args = parser.parse_args()
    control = read(args.matrix)["bindings"]
    candidate = read(args.candidate)
    if candidate["control_sdc"] != control["control"]["sdc"]:
        raise ValueError("candidate does not bind frozen SDC")
    if args.endpoint is None:
        starting_views = read(args.matrix.parent / "control/receipt.json")["views"]
        args.endpoint, = sorted(set(candidate["views"]["SS"]["setup_negative_endpoints"])
                               - set(starting_views["SS"]["setup_negative_endpoints"]))
    out = args.output.resolve()
    out.mkdir(parents=True)
    tool = verify(control["tools"]["openroad"])
    lib, = [verify(item) for item in control["used_libraries"]["SS"]]
    sdc = verify(control["control"]["sdc"])
    pairs = {"control": control["control"], "candidate": candidate["artifacts"]}
    comparison.save(out / "inputs.json", {
        "matrix": comparison.bind(args.matrix.resolve()), "physical_receipt": comparison.bind(args.candidate.resolve()),
        "driver": comparison.bind(Path(__file__).resolve()), "endpoint": args.endpoint, "cases": pairs,
    })
    result = {}
    for name, assets in pairs.items():
        odb, spef = (verify(assets[key]) for key in ("odb", "spef"))
        script = out / f"{name}.tcl"
        script.write_text(
            f"""read_liberty {comparison.tcl(lib)}
read_db {comparison.tcl(odb)}
read_sdc {comparison.tcl(sdc)}
read_spef {comparison.tcl(spef)}
set endpoint {comparison.tcl(args.endpoint)}
set pins [list]
foreach pin [get_pins -hierarchical *] {{
    if {{[get_full_name $pin] eq $endpoint}} {{ lappend pins $pin }}
}}
if {{[llength $pins] != 1}} {{ error "Could not bind the unique setup endpoint" }}
set paths [find_timing_paths -path_delay max -to $pins -group_path_count 1 -endpoint_path_count 1]
if {{[llength $paths] != 1}} {{ error "Could not bind the unique setup path" }}
puts "AES_EXACT_SETUP_SLACK_PS [expr {{1000.0 * [get_property [lindex $paths 0] slack]}}]"
report_checks -path_delay max -to $pins -group_path_count 1 -endpoint_path_count 1 -digits 9
puts AES_EXACT_SETUP_COMPLETE
exit
""", encoding="utf-8",
        )
        log = out / f"{name}.log"
        code = comparison.run_process([tool, "-no_init", "-no_splash", "-threads", "1", "-exit", script],
                                      log, 45)
        text = comparison.checked_output(code, "AES_EXACT_SETUP_COMPLETE")
        slack = re.search(r"(?m)^AES_EXACT_SETUP_SLACK_PS (\S+)$", text)
        if not slack:
            raise ValueError(f"missing setup slack for {name}")
        result[name] = {"slack_ps": float(slack[1]), "log": comparison.bind(log)}
    comparison.save(out / "results.json", result)
    print(result, flush=True)


if __name__ == "__main__":
    main()
