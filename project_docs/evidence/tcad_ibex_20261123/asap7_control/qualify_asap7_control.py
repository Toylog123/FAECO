
"""Qualify a completed ORFS ASAP7 Ibex CONTROL against the pinned RTL source SDC."""
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import subprocess
import time


WORK = Path("/home/toylog/faeco_tcad_ibex_20261123/control_asap7")
FLOW = Path("/home/toylog/faeco_eda/orfs/flow")
SLACK_PATTERN = r"[+-]?(?:\d+\.?\d*|\.\d+)(?:[Ee][+-]?\d+)?"
STA = Path("/usr/local/bin/sta")
TOP = "ibex_core"
VIEWS = ("FF", "TT", "SS")
LIBS = (
    "AO_RVT_{view}_nldm_211120.lib.gz",
    "INVBUF_RVT_{view}_nldm_220122.lib.gz",
    "OA_RVT_{view}_nldm_211120.lib.gz",
    "SIMPLE_RVT_{view}_nldm_211120.lib.gz",
    "SEQ_RVT_{view}_nldm_220123.lib",
)


def file_ref(path):
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path.read_bytes()).hexdigest()}


def take_scalar(text, pattern, message):
    found = re.findall(pattern, text, re.MULTILINE)
    if len(found) != 1:
        raise RuntimeError(f"{message}: expected one result, got {found}")
    return found[0]


def read_text(path):
    return path.read_text(encoding="utf-8")


def expected_sdc(text, *, pinned=(1000.0, 0.2, "core_clock", "clk_i", 161.775), time_unit="ps"):
    period = float(take_scalar(text, rf"^set clk_period\s+({SLACK_PATTERN})$", "source period"))
    fraction = float(take_scalar(text, rf"^set clk_io_pct\s+({SLACK_PATTERN})$", "source I/O fraction"))
    clock = take_scalar(text, r"^set clk_name\s+([a-zA-Z_0-9]+)$", "source core clock")
    port = take_scalar(text, r"^set clk_port_name\s+([a-zA-Z_0-9]+)$", "source clock port")
    latency = float(take_scalar(text, rf"^set_clock_latency\s+({SLACK_PATTERN})\s+\[get_clocks \$clk_io_name\]$", "source virtual latency"))
    for line in (
        "set clk_io_name vclk_$clk_name",
        "create_clock -name $clk_name -period $clk_period $clk_port",
        "create_clock -name $clk_io_name -period $clk_period",
        "set non_clock_inputs [all_inputs -no_clocks]",
        "set_input_delay [expr $clk_period * $clk_io_pct] -clock $clk_io_name $non_clock_inputs",
        "set_output_delay [expr $clk_period * $clk_io_pct] -clock $clk_io_name [all_outputs]",
    ):
        if line not in text.splitlines():
            raise RuntimeError(f"source SDC expression mismatch: {line}")
    core_latency = float(take_scalar(text, rf"^set_clock_latency\s+({SLACK_PATTERN})\s+\[get_clocks \$clk_name\]$", "source core latency"))
    if (period, fraction, clock, port, latency) != pinned or core_latency != latency:
        raise RuntimeError("source SDC numbers do not match preregistered base variant")
    ps_scale = {"ps": 1.0, "ns": 1000.0}[time_unit]
    return {"sdc_time_unit": time_unit, "period_sdc_units": period, "io_delay_sdc_units": period * fraction,
            "virtual_latency_sdc_units": latency, "source_core_latency_sdc_units": core_latency,
            "period_ps": period * ps_scale, "io_delay_ps": period * fraction * ps_scale,
            "virtual_latency_ps": latency * ps_scale, "core_clock": clock,
            "clock_port": port, "virtual_clock": f"vclk_{clock}"}


def audit_final_sdc(text, spec):
    num = SLACK_PATTERN
    # Exported SDC uses braces and one command per line. Validate both bound
    # clocks, the explicit propagation and every expanded min/max I/O delay.
    clock = spec["core_clock"]
    virt = spec["virtual_clock"]
    clocks = {name: (float(period), target.strip()) for name, period, target in re.findall(
        rf"^create_clock\s+-name\s+(\S+)\s+-period\s+({num})([^\r\n]*)$", text, re.M
    )}
    if set(clocks) != {clock, virt}:
        raise RuntimeError(f"unexpected exported clocks: {clocks}")
    expected_target = f"[get_ports {{{spec['clock_port']}}}]"
    if clocks[clock] != (spec["period_sdc_units"], expected_target) or clocks[virt] != (spec["period_sdc_units"], ""):
        raise RuntimeError(f"exported core or virtual clock mismatch: {clocks}")
    propagated = take_scalar(text, r"^set_propagated_clock\s+\[get_clocks\s+\{([^}]+)\}\]\s*$", "propagated core clock")
    if propagated != clock:
        raise RuntimeError(f"expected propagated {clock}, got {propagated}")
    latencies = [
        (float(value), name) for value, name in re.findall(
            rf"^set_clock_latency\s+({num})\s+\[get_clocks\s+\{{([^}}]+)\}}\]\s*$", text, re.M
        )
    ]
    if latencies != [(spec["virtual_latency_sdc_units"], virt)]:
        raise RuntimeError(f"unexpected virtual/physical clock latency: {latencies}")
    expanded = {"input": set(), "output": set()}
    statements = [l for l in text.splitlines() if l.startswith(("set_input_delay", "set_output_delay"))]
    for line in statements:
        match = re.fullmatch(
            rf"set_(input|output)_delay\s+({num})\s+-clock\s+\[get_clocks\s+\{{([^}}]+)\}}\]"
            r"(?P<other>.*?)\s+\[get_ports\s+\{([^}]+)\}\]\s*",
            line,
        )
        if not match:
            raise RuntimeError(f"unrecognized SDC delay syntax: {line}")
        sense, delay, target, flags, port = match.groups()
        if float(delay) != spec["io_delay_sdc_units"] or target != virt or set(flags.split()) - {"-add_delay"}:
            raise RuntimeError(f"delay semantics differ from original SDC: {line}")
        if port in expanded[sense]:
            raise RuntimeError(f"duplicate expanded {sense} delay: {port}")
        expanded[sense].add(port)
    if not all(expanded.values()):
        raise RuntimeError("exported SDC has no data inputs or no data outputs")
    extra = [line for line in text.splitlines() if line.startswith("set_") and not line.startswith(
        ("set_input_delay", "set_output_delay", "set_clock_latency", "set_propagated_clock")
    )]
    return expanded, extra


def produce_tcl(artifact, view_libs):
    script = [f"read_liberty {{{library}}}" for library in view_libs]
    script += [
        f"read_verilog {{{artifact}.v}}",
        f"link_design {TOP}",
        f"read_sdc {{{artifact}.sdc}}",
        f"read_spef {{{artifact}.spef}}",
        'puts "IBEX_SETUP_SECONDS [sta::worst_slack_cmd max]"',
        'puts "IBEX_HOLD_SECONDS [sta::worst_slack_cmd min]"',
        'puts "IBEX_SETUP_TNS_SECONDS [sta::total_negative_slack_cmd max]"',
        'puts "IBEX_HOLD_TNS_SECONDS [sta::total_negative_slack_cmd min]"',
        'foreach port [all_inputs -no_clocks] { puts "IBEX_DATA_INPUT [get_name $port]" }',
        'foreach port [all_outputs] { puts "IBEX_OUTPUT [get_name $port]" }',
        "report_units",
        "report_clock_properties [all_clocks]",
        "check_setup -verbose",
        "report_check_types -max_slew -max_capacitance -violators",
        "report_checks -path_delay min -format full_clock_expanded -digits 6",
        "report_checks -path_delay max -format full_clock_expanded -digits 6",
        'puts "IBEX_CONTROL_STA_COMPLETE"',
        "exit",
    ]
    return "\n".join(script) + "\n"


def collect_view(view, artifact, view_libs, expected_ports, raw_output, *, reuse_existing=False, sta_binary=STA):
    tcl = raw_output / f"{view}.tcl"
    script = produce_tcl(artifact, view_libs)
    log = raw_output / f"{view}.log"
    command = ["/usr/bin/timeout", "--kill-after=5s", "120s", str(sta_binary), "-no_splash", "-exit", str(tcl)]
    elapsed = None
    if reuse_existing:
        if read_text(tcl) != script:
            raise RuntimeError(f"{view} existing Tcl differs from the canonical test")
        returncode = 0
    else:
        tcl.write_text(script, encoding="utf-8")
        start = time.monotonic()
        with log.open("wb") as stream:
            returncode = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, timeout=130).returncode
        elapsed = round(time.monotonic() - start, 3)
    text = read_text(log)
    if returncode or re.search(r"^\s*(?:\[ERROR|Error:|Error .*\.tcl)", text, re.M) or "IBEX_CONTROL_STA_COMPLETE" not in text:
        raise RuntimeError(f"{view} setup/hold STA failed, rc={returncode}; see {log}")
    if re.search(r"black box|not found|unannotated driver", text, re.I):
        raise RuntimeError(f"{view} contains unresolved netlist or missing timing data; see {log}")
    sta_ports = {
        "input": set(re.findall(r"^IBEX_DATA_INPUT (\S+)$", text, re.M)),
        "output": set(re.findall(r"^IBEX_OUTPUT (\S+)$", text, re.M)),
    }
    if sta_ports != expected_ports:
        mismatch = {key: {"missing_delays": sorted(sta_ports[key] - expected_ports[key]),
                          "extra_delays": sorted(expected_ports[key] - sta_ports[key])} for key in sta_ports}
        raise RuntimeError(f"{view} actual versus exported constrained ports differ: {mismatch}")
    values = {}
    for key, marker in (
        ("setup_wns_ps", "IBEX_SETUP_SECONDS"), ("hold_wns_ps", "IBEX_HOLD_SECONDS"),
        ("setup_tns_ps", "IBEX_SETUP_TNS_SECONDS"), ("hold_tns_ps", "IBEX_HOLD_TNS_SECONDS"),
    ):
        shown = float(take_scalar(text, rf"^{marker}\s+({SLACK_PATTERN})$", marker))
        if not math.isfinite(shown):
            raise RuntimeError(f"{view} non-finite {marker}")
        values[key] = shown * 1e12
    return {
        **values, "elapsed_seconds": elapsed, "returncode": returncode, "receipt_reuses_saved_success_log": reuse_existing,
        "command": command, "tcl": file_ref(tcl), "log": file_ref(log),
        "actual_port_counts": {key: len(value) for key, value in sta_ports.items()},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-output", required=True, type=Path)
    parser.add_argument("--reuse-existing-raw", action="store_true", help="Validate exact saved Tcl and previously completed logs without running new STA.")
    args = parser.parse_args()
    output = Path(__file__).resolve().parent
    raw_output = args.raw_output.resolve()
    if not raw_output.is_relative_to(WORK.resolve()):
        raise ValueError("raw output must be under the pinned CONTROL work home")
    result_dir = WORK / "results/asap7/ibex/base"
    logs = WORK / "logs/asap7/ibex/base"
    reports = WORK / "reports/asap7/ibex/base"
    artifacts = result_dir / "6_final"
    producer = WORK / "producer_receipt.json"
    record = json.loads(read_text(producer))
    if record["returncode"] or record["sha256_pre"] != record["sha256_post"]:
        raise RuntimeError("producer failed or source/tool pins changed while it ran")
    source_sdc = FLOW / "designs/asap7/ibex/constraint.sdc"
    sdc = result_dir / "6_final.sdc"
    spec = expected_sdc(read_text(source_sdc))
    ports, extra = audit_final_sdc(read_text(sdc), spec)
    drc_report = reports / "5_route_drc.rpt"
    drc = json.loads(read_text(logs / "5_2_route.json"))["detailedroute__route__drc_errors"]
    if drc != 0 or drc_report.stat().st_size != 0:
        raise RuntimeError(f"CONTROL detailed-route DRC gate failed: {drc}; check {drc_report}")

    platform = FLOW / "platforms/asap7/lib/NLDM"
    libraries = {view: [platform / ("asap7sc7p5t_" + lib.format(view=view)) for lib in LIBS] for view in VIEWS}
    physical = [result_dir / f"6_final.{ext}" for ext in ("odb", "def", "v", "sdc", "spef")]
    raw_logs = [WORK / "producer.log", producer, logs / "5_2_route.log", logs / "5_2_route.json", logs / "6_report.log",
                logs / "6_report.json", drc_report, reports / "6_finish.rpt"]
    inputs = physical + [source_sdc, STA] + [lib for group in libraries.values() for lib in group]
    before = [file_ref(path) for path in inputs]
    if not all(path.stat().st_size > 0 for path in physical):
        raise RuntimeError("empty final physical artifact")
    if not args.reuse_existing_raw:
        raw_output.mkdir(parents=False, exist_ok=False)
    views = {}
    for view, view_libs in libraries.items():
        views[view] = collect_view(view, artifacts, view_libs, ports, raw_output, reuse_existing=args.reuse_existing_raw)
        print(f"{view} setup WNS {views[view]['setup_wns_ps']:+.6f} ps; hold WNS {views[view]['hold_wns_ps']:+.6f} ps", flush=True)
    if [file_ref(path) for path in inputs] != before:
        raise RuntimeError("input pins drifted during the three-view replay")
    finish = json.loads(read_text(logs / "6_report.json"))
    sa = finish["finish__timing__setup__ws"]
    ho = finish["finish__timing__hold__ws"]
    match = abs(sa - views["FF"]["setup_wns_ps"]) <= 0.10 and abs(ho - views["FF"]["hold_wns_ps"]) <= 0.10
    diagnostic_dir = WORK / "qualification_ff_diagnostic"
    diagnostic = {}
    for mode in ("pinned_odb_spef", "pinned_verilog_lef_spef"):
        log = diagnostic_dir / f"{mode}.log"
        if log.is_file():
            text = read_text(log)
            if "IBEX_CONTROL_STA_COMPLETE" not in text:
                raise RuntimeError(f"incomplete supplemental FF diagnostic: {log}")
            diagnostic[mode] = {
                "setup_wns_ps": float(take_scalar(text, rf"^IBEX_SETUP_SECONDS\s+({SLACK_PATTERN})$", mode)) * 1e12,
                "hold_wns_ps": float(take_scalar(text, rf"^IBEX_HOLD_SECONDS\s+({SLACK_PATTERN})$", mode)) * 1e12,
                "log": file_ref(log), "tcl": file_ref(log.with_suffix(".tcl")),
            }
    failed_tech_probe = diagnostic_dir / "pinned_verilog_spef.log"
    if failed_tech_probe.is_file():
        diagnostic["earlier_verilog_no_tech_precondition_diagnostic"] = {
            "log": file_ref(failed_tech_probe), "tcl": file_ref(failed_tech_probe.with_suffix(".tcl")),
            "report": "ORD-2010, no technology was read; no setup/hold measurement.",
        }
    state = {
        "schema_version": 1, "design": "ORFS ASAP7 ibex / ibex_core",
        "status": "hold_qualified" if all(v["hold_wns_ps"] >= 0 for v in views.values()) else "hold_infeasible",
        "producer": record, "control_output_paths": {path.suffix.removeprefix("."): file_ref(path) for path in physical},
        "source_sdc_semantics": {**spec, "expanded_port_counts": {k: len(v) for k, v in ports.items()},
                                 "source_io_matches_all_nonclock_inputs_and_outputs": True,
                                 "propagated_after_cts": spec["core_clock"], "other_exported_set_commands": extra,
                                 "core_clock_latency_semantics": "original ideal latency is replaced by actual propagated clock tree, virtual latency is retained"},
        "detailed_route_drc_count": drc, "raw_reports": [file_ref(path) for path in raw_logs],
        "views": views, "library_paths": {view: [str(lib) for lib in group] for view, group in libraries.items()},
        "view_liberty_groups": {view: [file_ref(lib) for lib in group] for view, group in libraries.items()},
        "sta_binary": file_ref(STA),
        "sta_version": subprocess.check_output([str(STA), "-version"], text=True, timeout=10).strip(),
        "ff_matches_native_producer_0p10_ps": match,
        "ff_native_setup_difference_from_standalone_ps": sa - views["FF"]["setup_wns_ps"],
        "ff_native_is_a_separate_diagnostic": True, "ff_supplemental_readbacks": diagnostic,
        "native_finish_setup_wns_ps": sa, "native_finish_hold_wns_ps": ho,
        "native_finish_stdcell_area_um2": finish.get("finish__design__instance__area__stdcell"),
        "native_finish_stdcell_count": finish.get("finish__design__instance__count__stdcell"),
        "all_views_nonnegative_hold": all(v["hold_wns_ps"] >= 0 for v in views.values()),
        "corner_scope": "FF/TT/SS RVT Liberty and one common extracted OpenRCX SPEF, propagated clock and source-derived SDC.",
        "counts": {"qualification_sta": 3, "qualification_sta_repeated_for_this_receipt": 0 if args.reuse_existing_raw else 3,
                   "ff_supplemental_successful_readbacks": sum(key in diagnostic for key in ("pinned_odb_spef", "pinned_verilog_lef_spef")),
                   "candidate_routes": 0, "candidate_sta": 0, "candidate_sec": 0},
    }
    (output / "CONTROL.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
