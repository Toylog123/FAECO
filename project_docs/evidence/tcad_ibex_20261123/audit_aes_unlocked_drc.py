#!/usr/bin/env python3
"""Check AES route geometry with all signal wires eligible for DRC markers."""

from argparse import ArgumentParser
from pathlib import Path
import json
import re

import compare_ibex as comparison
from probe_aes_selective_repair import normalize_net


def load(path):
    return json.loads(path.read_bytes())


def require_binding(binding):
    path = Path(binding["path"])
    if comparison.bind(path) != binding:
        raise ValueError(f"input changed: {path}")
    return path


def audit(matrix, out, candidate=None):
    cfg = load(matrix)["bindings"]
    tool = require_binding(cfg["tools"]["openroad"])
    src = load(candidate)["artifacts"] if candidate is not None else cfg["control"]
    odb = require_binding(src["odb"])
    geometry = require_binding(src["def"])
    original = geometry.read_text(encoding="utf-8")
    body_beg = original.index("\nNETS ")
    body_end = original.index("\nEND NETS", body_beg)
    net_section = original[body_beg:body_end]
    header = "\n".join(re.findall(r"(?m)^(?:VERSION|DIVIDERCHAR|BUSBITCHARS|DESIGN|UNITS) .+?;$", original))
    if len(header.splitlines()) != 5:
        raise ValueError("unexpected DEF header")
    unlocked_section, fixed_count = re.subn(r"\+ FIXED ", "+ ROUTED ", net_section)
    if bool(fixed_count) != (candidate is not None):
        raise ValueError("only candidate audits should contain FIXED signal wires")
    out = out.resolve()
    out.mkdir(parents=True)
    encoded = out / "normalized_nets.def"
    normalized = out / "normalized_geometry.def"
    report = out / "full_drc.rpt"
    unlock_tcl = ""
    if fixed_count:
        encoded.write_text(header + unlocked_section + "\nEND NETS\nEND DESIGN\n", encoding="utf-8")
        unlock_tcl = f"read_def -floorplan_initialize {comparison.tcl(encoded)}\n"
    provenance = {"matrix_config": comparison.bind(matrix.resolve()), "input_odb": src["odb"],
                  "input_def": src["def"], "original_fixed_wire_count": fixed_count,
                  "producer": comparison.bind(Path(__file__).resolve()), "timeout_seconds": 120}
    comparison.save(out / "inputs.json", provenance)
    script = out / "audit.tcl"
    script.write_text(
        f"""read_db {comparison.tcl(odb)}
{unlock_tcl}write_def {comparison.tcl(normalized)}
if {{![design_is_routed]}} {{ error "Unrouted signal nets" }}
drt::check_drc -output_file {comparison.tcl(report)}
puts AES_UNLOCKED_DRC_COMPLETE
exit
""", encoding="utf-8",
    )
    result = comparison.run_process([tool, "-no_init", "-no_splash", "-threads", "1", "-exit", script],
                                    out / "audit.log", 120)
    comparison.checked_output(result, "AES_UNLOCKED_DRC_COMPLETE")
    original_nets = comparison.def_section(geometry, "NETS")
    compared_nets = comparison.def_section(normalized, "NETS")
    if (any("+ FIXED " in entry for entry in compared_nets.values())
            or {net: normalize_net(entry) for net, entry in original_nets.items()}
            != {net: normalize_net(entry) for net, entry in compared_nets.items()}):
        raise ValueError("route status normalization changed NETS geometry")
    if (comparison.def_section(geometry, "COMPONENTS") != comparison.def_section(normalized, "COMPONENTS")
            or comparison.def_section(geometry, "SPECIALNETS") != comparison.def_section(normalized, "SPECIALNETS")):
        raise ValueError("route status normalization changed components or special nets")
    markers = report.read_text(encoding="utf-8")
    violations = re.findall(r"(?m)^violation type:\s*(.+)$", markers)
    if markers.strip() and not violations:
        raise ValueError("unknown DRC report format")
    summary = {"drc_markers": len(violations), "marker_types": sorted(set(violations)),
               "report": comparison.bind(report), "normalized_geometry": comparison.bind(normalized),
               "wall_seconds": result.wall_seconds}
    comparison.save(out / "audit.json", summary)
    return summary


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--candidate", type=Path, help="physical receipt from a FIXED-mode AES trial")
    ns = parser.parse_args()
    print(json.dumps(audit(ns.matrix, ns.out, ns.candidate)), flush=True)


if __name__ == "__main__":
    main()
