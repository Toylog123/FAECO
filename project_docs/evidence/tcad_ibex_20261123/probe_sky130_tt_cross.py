"""Read-only 2x2 SKY130 TT ODB/SPEF attribution. Run after timed ASAP7 arms."""

from argparse import ArgumentParser
from hashlib import file_digest
from math import fsum
from pathlib import Path
import json
import re
import subprocess
import time


PATHS = {
    "fifo_39": (
        "if_stage_i.instr_rdata_id_o[21]$_DFFE_PP_/Q",
        "place2749/X",
        "if_stage_i.gen_prefetch_buffer.prefetch_buffer_i.fifo_i.rdata_q[39]$_DFFE_PP_/DE",
    ),
    "rf_762": (
        "if_stage_i.instr_rdata_id_o[22]$_DFFE_PP_/Q",
        "place2755/X",
        "gen_regfile_ff.register_file_i.rf_reg[762]$_DFFE_PN0P_/D",
    ),
}

TCL_DIAGNOSTICS = r"""
puts "TT_PROBE_WNS_PS [expr {1e12 * [sta::worst_slack_cmd max]}]"
puts "TT_PROBE_TNS_PS [expr {1e12 * [sta::total_negative_slack_cmd max]}]"
puts TT_PROBE_ANNOTATION_BEGIN
report_parasitic_annotation -report_unannotated
puts TT_PROBE_ANNOTATION_END

set paths [find_timing_paths -path_delay max -slack_max 0 -group_path_count 100000 -endpoint_path_count 1]
if {[llength $paths] >= 100000} { error "TT PROBE capped path enumeration" }
set endpoint_slacks [dict create]
foreach path $paths {
    set name [get_full_name [get_property $path endpoint]]
    set slack [expr {1000.0 * [get_property $path slack]}]
    if {$slack < 0 && (![dict exists $endpoint_slacks $name] || $slack < [dict get $endpoint_slacks $name])} {
        dict set endpoint_slacks $name $slack
    }
}
dict for {name slack} $endpoint_slacks { puts "TT_PROBE_NEG\t$name\t$slack" }

proc find_exact_probe_pins {triples} {
    set sought_pins [dict create]
    dict for {label names} $triples {
        foreach name $names { dict set sought_pins $name 1 }
    }
    set found [dict create]
    foreach pin [get_pins -hierarchical *] {
        set name [get_full_name $pin]
        if {[dict exists $sought_pins $name]} {
            if {[dict exists $found $name]} { error "duplicate TT PROBE pin: $name" }
            dict set found $name $pin
        }
    }
    if {[dict size $found] != [dict size $sought_pins]} {
        error "one or more TT PROBE pins absent: $found"
    }
    return $found
}

set matched_pins [find_exact_probe_pins $triples]
dict for {label names} $triples {
    lassign $names from through to
    set from [dict get $matched_pins $from]
    set through [dict get $matched_pins $through]
    set to [dict get $matched_pins $to]
    puts "TT_PROBE_PATH_BEGIN $label"
    report_checks -path_delay max -group_path_count 1 -endpoint_path_count 1 \
        -from $from -through $through -to $to -digits 9 -no_line_splits \
        -format full_clock_expanded -fields {capacitance slew fanout input_pin net}
    puts "TT_PROBE_PATH_END $label"
}
puts TT_PROBE_COMPLETE
"""


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify_binding(binding):
    path = Path(binding["path"])
    with path.open("rb") as f:
        digest = file_digest(f, "sha256").hexdigest()
    if digest != binding["sha256"] or path.stat().st_size != binding["bytes"]:
        raise ValueError(f"changed input {path}")
    return path


def tcl_quote(value):
    return "{" + str(value) + "}"


def render(lib, sdc, odb, spef, groups):
    reads = [
        f"read_liberty {tcl_quote(lib)}",
        f"read_db {tcl_quote(odb)}",
        f"read_sdc {tcl_quote(sdc)}",
        f"read_spef {tcl_quote(spef)}",
        "set triples [dict create]",
    ]
    pairs = [
        f"dict set triples {label} [list {' '.join(map(tcl_quote, paths))}]"
        for label, paths in groups.items()
    ]
    routine = "\n".join(reads + pairs + [TCL_DIAGNOSTICS])
    return "if {[catch {\n" + routine + '\n} problem]} {\n    puts stderr "TT_PROBE_ERROR $problem"\n    exit 2\n}\nexit\n'


def parse_log(log, groups, reference):
    if "TT_PROBE_COMPLETE" not in log or re.search(
        r"(?mi)^\s*(?:\[ERROR\s|Error:)|(?:net|pin).*not found|no paths found", log
    ):
        raise ValueError("STA reported an error or no constrained path")
    full = float(re.search(r"(?m)^TT_PROBE_TNS_PS (\S+)", log)[1])
    worst = float(re.search(r"(?m)^TT_PROBE_WNS_PS (\S+)", log)[1])
    slacks = {
        name: float(slack)
        for name, slack in re.findall(r"(?m)^TT_PROBE_NEG\t([^\t\n]+)\t(\S+)", log)
    }
    reconstructed = fsum(slacks.values())
    discrepancy = reconstructed - full
    if not slacks or abs(discrepancy) > 0.002 * len(slacks) or abs(min(slacks.values()) - worst) > 0.002:
        raise ValueError(f"endpoint inventory disagrees with scalar TNS/WNS: {discrepancy}")
    if reference:
        for key, actual in {"setup_wns_ps": worst, "setup_tns_ps": full}.items():
            if abs(reference[key] - actual) > 0.001:
                raise ValueError(f"{key} differs from original physical receipt")
        if set(slacks) != set(reference["setup_negative_endpoints"]):
            raise ValueError("endpoint inventory differs from original physical receipt")
    annotation = log.split("TT_PROBE_ANNOTATION_BEGIN\n")[1].split("TT_PROBE_ANNOTATION_END")[0]
    if "Found 0 partially unannotated drivers." not in annotation:
        raise ValueError("unexpected partial annotation")
    paths = {}
    for label, (_, through, to) in groups.items():
        block = log.split(f"TT_PROBE_PATH_BEGIN {label}\n")[1].split(f"TT_PROBE_PATH_END {label}")[0]
        if not all(name in block for name in (through, to, "slack (")):
            raise ValueError(f"target path missing in report {label}")
        paths[label] = block
    return {
        "wns_ps": worst,
        "tns_ps": full,
        "negative_slack_sum_error_ps": discrepancy,
        "negative_endpoint_slack_ps": slacks,
        "unannotated_drivers": annotation,
        "matched_paths": paths,
    }


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("run_directory", type=Path)
    p.add_argument("output_directory", type=Path)
    p.add_argument("--prepare-only", action="store_true")
    ns = p.parse_args()
    root = ns.run_directory.resolve(strict=True)
    out = ns.output_directory.resolve()
    out.mkdir(parents=True)
    cfg = load_json(root / "config.json")["bindings"]
    control = cfg["control"]
    lib, = [verify_binding(item) for item in cfg["used_libraries"]["TT"]]
    sdc = verify_binding(control["sdc"])
    openroad = verify_binding(cfg["tools"]["openroad"])
    cc = (verify_binding(control["odb"]), verify_binding(control["spef"]))
    input_bindings = {
        item["path"]: item
        for item in (cfg["used_libraries"]["TT"][0], cfg["tools"]["openroad"],
                     control["sdc"], control["odb"], control["spef"])
    }
    ctrl = load_json(root / "control/receipt.json")["views"]["TT"]
    cases = [("CC", *cc, PATHS, ctrl)]
    for slot, label in (("01", "fifo_39"), ("05", "rf_762")):
        groups = {label: PATHS[label]}
        receipt = load_json(root / f"primary_tradeoff_1pct/single/{slot}_physical/receipt.json")
        if receipt["control_sdc"] != control["sdc"]:
            raise ValueError(f"candidate {slot} does not bind CONTROL SDC")
        odb, spef = [verify_binding(receipt["artifacts"][kind]) for kind in ("odb", "spef")]
        for kind in ("odb", "spef"):
            item = receipt["artifacts"][kind]
            input_bindings[item["path"]] = item
        cases.extend([
            (f"{slot}_EE", odb, spef, groups, receipt["views"]["TT"]),
            (f"{slot}_EC", odb, cc[1], groups, None),
            (f"{slot}_CE", cc[0], spef, groups, None),
        ])
    (out / "inputs.json").write_text(json.dumps({
        "source_root": str(root),
        "verified_bindings": input_bindings,
        "cases": {name: {"odb": str(odb), "spef": str(spef), "matched_paths": groups}
                  for name, odb, spef, groups, _ in cases},
    }, indent=2) + "\n", encoding="utf-8")
    result = {}
    for name, odb, spef, groups, reference in cases:
        script = out / f"{name}.tcl"
        script.write_text(render(lib, sdc, odb, spef, groups), encoding="utf-8")
        if ns.prepare_only:
            continue
        log = script.with_suffix(".log")
        start = time.monotonic()
        with log.open("w", encoding="utf-8") as fd:
            subprocess.run(
                [openroad, "-no_init", "-no_splash", "-threads", "1", "-exit", script],
                cwd=out,
                stdout=fd,
                stderr=subprocess.STDOUT,
                timeout=90,
                check=True,
            )
        result[name] = parse_log(log.read_text(encoding="utf-8"), groups, reference)
        result[name]["inputs"] = {"odb": str(odb), "spef": str(spef), "lib": str(lib), "sdc": str(sdc)}
        result[name]["wall_seconds"] = time.monotonic() - start
        if result[name]["unannotated_drivers"] != result["CC"]["unannotated_drivers"]:
            raise ValueError(f"changed parasitic annotation in {name}")
        print(name, result[name]["wns_ps"], result[name]["tns_ps"], flush=True)
        (out / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
