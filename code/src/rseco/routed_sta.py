"""Routed-tier (post-route, extracted-SPEF) timing evaluation via OpenROAD.

WHY THIS MODULE EXISTS
======================
The mechanism's inner loop judges candidates on the *ideal* netlist, and the
r30/r103 evidence says that tier systematically overstates or understates
different candidate kinds (buffer insertion is punished because the ideal
netlist has no interconnect at all).  :mod:`rseco.placed_sta` added the placed
tier, which is the cheap supervised signal.  But the paper's endpoint numbers
(post-route WNS after full placement+CTS+routing+RCX) need a *routed* reading:
a candidate that looks better on placement parasitics can be neutralised or
reversed once real metal is routed.

This module is the endpoint measuring instrument only -- it is deliberately
NOT wired into the inner loop (too expensive: minutes per candidate versus
seconds for the placed tier).

CONVENTION (mirrors ``experiments/20261102_layout_stability_n8``)
================================================================
1. Full flow from the netlist: floorplan -> place -> CTS -> global route ->
   detailed route, with the platform ``pdn.tcl`` and the project's ORFS
   snapshot ``setRC.tcl``.
2. ``extract_parasitics`` with the ORFS ``rcx_patterns.rules`` -> SPEF.
3. A *separate* STA pass on the routed netlist + SPEF (ideal clock, no
   ``set_propagated_clock``), which is exactly the r103 ``_sta_p.tcl``
   convention.  Keeping the STA pass separate matters: the flow propagates the
   clock for CTS/route, and reporting timing inside that session would confound
   the routed reading with a clock-model change.

Caveats (same family as r30/r103):
* ``extract_parasitics`` with RCX rules is closer to sign-off than the placed
  tier's ``estimate_parasitics -placement``, but it is still not a foundry
  sign-off extraction.
* Each evaluation re-runs placement, so placement dispersion is part of the
  measurement by design (r103: single-arm across-layout spread median 0.055 ns).
* DRC violations are reported (count of ``violation type:`` records) but do not
  invalidate the reading; callers must treat non-zero DRC as a caveat.

COST
====
Tens of seconds to minutes per netlist depending on size; use it for endpoints,
not for candidate screening.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .opensta import _to_sta_path
from .placed_sta import DEFAULT_OPENROAD, DEFAULT_PLATFORM

#: Standalone OpenSTA on WSL: the endpoint STA pass runs here, not in the
#: routing session (OpenROAD STA mode needs LEF and fails with ORD-2010).
DEFAULT_STA = "/usr/local/bin/sta"

#: Project-local ORFS snapshot: setRC.tcl + rcx rules live here (the WSL
#: platform directory only carries lef/lib/pdn.tcl).
DEFAULT_ORFS = "/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629"

ROUTED_FLOW_TCL = """\\
set PLATFORM "__PLATFORM__"
set ORFS     "__ORFS__"
set NETLIST  "__NETLIST__"
set OUTDIR   "__OUTDIR__"
set TOP      __TOP__
set PERIOD   __PERIOD__
set UTIL     __UTIL__
set DENSITY  __DENSITY__
set CLK_PORT __CLK_PORT__
set DROUTE_ITER __DROUTE_ITER__

read_liberty $PLATFORM/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_lef $PLATFORM/lef/sky130_fd_sc_hd.tlef
read_lef $PLATFORM/lef/sky130_fd_sc_hd_merged.lef
read_verilog $NETLIST
link_design $TOP
create_clock -name clk -period $PERIOD [get_ports $CLK_PORT]

initialize_floorplan -utilization $UTIL -aspect_ratio 1.0 -core_space 2.0 -site unithd
make_tracks
place_pins -hor_layers met3 -ver_layers met2
source $PLATFORM/pdn.tcl
tapcell -distance 14 -tapcell_master sky130_fd_sc_hd__tapvpwrvgnd_1
global_placement -density $DENSITY
detailed_placement
clock_tree_synthesis -buf_list {sky130_fd_sc_hd__clkbuf_4 sky130_fd_sc_hd__clkbuf_8} -root_buf sky130_fd_sc_hd__clkbuf_16
repair_clock_nets
detailed_placement
write_def $OUTDIR/cts.def
set_propagated_clock [all_clocks]

source $ORFS/setRC.tcl
set_routing_layers -signal met1-met5 -clock met3-met5
# Some mapped netlists carry tie nets (one_/zero_) that OpenDB classifies as
# POWER; TritonRoute refuses those (DRT-0305). Demote them to SIGNAL so the same
# signoff flow can measure every arm.
set block [ord::get_db_block]
foreach nname {one_ zero_} {
  set net [$block findNet $nname]
  if {$net ne "NULL"} { $net setSigType SIGNAL }
}
pin_access
global_route
detailed_route -output_drc $OUTDIR/drc.rpt -verbose 0 -droute_end_iter $DROUTE_ITER
write_def $OUTDIR/routed.def
write_verilog $OUTDIR/routed.v

define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file $ORFS/rcx/rcx_patterns.rules
write_spef $OUTDIR/routed.spef
puts "ROUTED_FLOW_OK"
"""

#: Endpoint STA convention of the r103 family: ideal clock + routed SPEF.

def render_flow_tcl_skip_clock_tree(**kwargs) -> str:
    """Render the routing flow for a netlist that ALREADY contains a clock tree.

    Post-CTS exports carry the clock buffers as ordinary gates; running
    ``clock_tree_synthesis`` on top of that crashes OpenROAD (probe on s641:
    returncode 139 with CTS, 0 without).  This variant keeps everything else
    byte-identical to :func:`render_flow_tcl`, so the only difference between a
    pre-CTS and a post-CTS measurement is the input netlist.
    """
    tcl = render_flow_tcl(**kwargs)
    cts = (
        "clock_tree_synthesis -buf_list {sky130_fd_sc_hd__clkbuf_4 sky130_fd_sc_hd__clkbuf_8}"
        " -root_buf sky130_fd_sc_hd__clkbuf_16\nrepair_clock_nets\ndetailed_placement\n"
        "write_def $OUTDIR/cts.def\n"
    )
    if cts not in tcl:  # pragma: no cover - template drift guard
        raise RuntimeError("CTS block drifted; update render_flow_tcl_skip_clock_tree")
    return tcl.replace(
        cts,
        "# clock tree already present in the input netlist (post-CTS export)\n"
        "detailed_placement\n"
        "write_def $OUTDIR/cts.def\n",
    )


ROUTED_STA_TCL = """\\
set PLATFORM "__PLATFORM__"
set NETLIST  "__NETLIST__"
set SPEF     "__SPEF__"
set TOP      __TOP__
set PERIOD   __PERIOD__
set CLK_PORT __CLK_PORT__

read_liberty $PLATFORM/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog $NETLIST
link_design $TOP
create_clock -name clk -period $PERIOD [get_ports $CLK_PORT]
read_spef $SPEF

# sta::worst_slack_cmd returns SECONDS; report_tns reports NANOseconds.
puts "ROUTED_WNS_MAX [sta::worst_slack_cmd max]"
puts "ROUTED_WNS_MIN [sta::worst_slack_cmd min]"
puts "ROUTED_TNS_BEGIN"
report_tns
puts "ROUTED_TNS_END"
puts "ROUTED_STA_OK"
"""

_WNS_MAX_RE = re.compile(r"ROUTED_WNS_MAX\s+(-?[0-9.eE+-]+)")
_WNS_MIN_RE = re.compile(r"ROUTED_WNS_MIN\s+(-?[0-9.eE+-]+)")
_TNS_RE = re.compile(r"ROUTED_TNS_BEGIN\s*\n\s*tns\s+max\s+(-?[0-9.]+)")
_ERROR_RE = re.compile(r"^(?:\[ERROR|Error:)", re.MULTILINE)
_DRC_RE = re.compile(r"^violation type:", re.MULTILINE)


def _argv(command: str | None) -> list[str]:
    if command:
        return command.split()
    return ["wsl.exe", "-d", "Ubuntu", "--", DEFAULT_OPENROAD]


def _sta_argv(command: str | None) -> list[str]:
    """Standalone OpenSTA argv.

    The endpoint STA pass must NOT be run inside the routing session: that
    session has propagated clocks and no need for LEF re-reading, whereas the
    r103 convention (and the ideal-tier instrument) is ``sta`` on
    netlist + SPEF + create_clock.  OpenROAD in STA mode fails here with
    ORD-2010 (no technology read), so the pass uses ``sta``.
    """
    if command:
        return command.split()
    return ["wsl.exe", "-d", "Ubuntu", "--", DEFAULT_STA]


def _run(argv: list[str], *, timeout_s: float) -> tuple[str, int | None]:
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return type(exc).__name__ + ": " + str(exc), None
    return (proc.stdout or "") + (proc.stderr or ""), proc.returncode


def render_flow_tcl(
    *,
    netlist_path,
    output_dir,
    top_module: str,
    period: float,
    util: float,
    density: float,
    clock_port: str,
    platform: str,
    orfs: str,
    droute_end_iter: int = 15,
) -> str:
    return (
        ROUTED_FLOW_TCL
        .replace("__PLATFORM__", platform)
        .replace("__ORFS__", orfs)
        .replace("__NETLIST__", _to_sta_path(Path(netlist_path)))
        .replace("__OUTDIR__", _to_sta_path(Path(output_dir)))
        .replace("__TOP__", str(top_module))
        .replace("__PERIOD__", repr(float(period)))
        .replace("__UTIL__", repr(float(util)))
        .replace("__DENSITY__", repr(float(density)))
        .replace("__CLK_PORT__", str(clock_port))
        .replace("__DROUTE_ITER__", str(int(droute_end_iter)))
    )


def render_sta_tcl(
    *,
    netlist_path,
    spef_path,
    top_module: str,
    period: float,
    clock_port: str,
    platform: str,
) -> str:
    return (
        ROUTED_STA_TCL
        .replace("__PLATFORM__", platform)
        .replace("__NETLIST__", _to_sta_path(Path(netlist_path)))
        .replace("__SPEF__", _to_sta_path(Path(spef_path)))
        .replace("__TOP__", str(top_module))
        .replace("__PERIOD__", repr(float(period)))
        .replace("__CLK_PORT__", str(clock_port))
    )


def run_routed_sta(
    *,
    netlist_path,
    output_dir,
    top_module: str,
    period: float = 0.5,
    clock_port: str = "CK",
    util: float = 0.35,
    density: float = 0.55,
    platform: str = DEFAULT_PLATFORM,
    orfs: str = DEFAULT_ORFS,
    openroad_command: str | None = None,
    sta_command: str | None = None,
    droute_end_iter: int = 15,
    skip_clock_tree: bool = False,
    flow_timeout_s: float = 1800.0,
    sta_timeout_s: float = 300.0,
) -> dict:
    """Route one netlist and report post-route setup timing in ns.

    Returns ``wns`` (ns), ``tns`` (ns), ``min_slack`` (ns), ``drc_violations``
    (int or None), ``slack``/``slack_status`` aliases and ``error`` (None on
    success).  Timing values are ``None`` whenever any stage fails, so callers
    fail closed.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    argv = _argv(openroad_command)

    flow_tcl = output_dir / "route_flow.tcl"
    renderer = render_flow_tcl_skip_clock_tree if skip_clock_tree else render_flow_tcl
    flow_tcl.write_text(
        renderer(
            netlist_path=netlist_path,
            output_dir=output_dir,
            top_module=top_module,
            period=period,
            util=util,
            density=density,
            clock_port=clock_port,
            platform=platform,
            orfs=orfs,
            droute_end_iter=droute_end_iter,
        ),
        encoding="utf-8",
    )
    flow_raw, flow_rc = _run(
        [*argv, "-no_init", "-exit", _to_sta_path(flow_tcl)], timeout_s=flow_timeout_s
    )
    (output_dir / "route_flow.log").write_text(flow_raw, encoding="utf-8")
    if flow_rc != 0:
        return _failure(flow_raw, f"route flow returncode={flow_rc}")
    if _ERROR_RE.search(flow_raw) or "ROUTED_FLOW_OK" not in flow_raw:
        return _failure(flow_raw, _first_error(flow_raw, "missing ROUTED_FLOW_OK"))

    routed_v = output_dir / "routed.v"
    routed_spef = output_dir / "routed.spef"
    if not routed_v.is_file() or not routed_spef.is_file():
        return _failure(flow_raw, "routed.v or routed.spef not written")

    drc_path = output_dir / "drc.rpt"
    drc_violations = None
    if drc_path.is_file():
        drc_violations = len(_DRC_RE.findall(drc_path.read_text(encoding="utf-8", errors="replace")))

    reading = sta_routed(
        routed_netlist=routed_v,
        spef_path=routed_spef,
        output_dir=output_dir,
        top_module=top_module,
        period=period,
        clock_port=clock_port,
        platform=platform,
        sta_command=sta_command,
        timeout_s=sta_timeout_s,
    )
    if reading["error"] is not None:
        return reading
    reading["drc_violations"] = drc_violations
    return reading


def sta_routed(
    *,
    routed_netlist,
    spef_path,
    output_dir,
    top_module: str,
    period: float = 0.5,
    clock_port: str = "CK",
    platform: str = DEFAULT_PLATFORM,
    sta_command: str | None = None,
    timeout_s: float = 300.0,
) -> dict:
    """Endpoint STA on an already-routed netlist + SPEF (ideal clock).

    Split out of :func:`run_routed_sta` so a reading can be repeated without
    paying for the routing flow again -- use this when auditing an archived
    routed netlist.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    sta_tcl = output_dir / "route_sta.tcl"
    sta_tcl.write_text(
        render_sta_tcl(
            netlist_path=routed_netlist,
            spef_path=spef_path,
            top_module=top_module,
            period=period,
            clock_port=clock_port,
            platform=platform,
        ),
        encoding="utf-8",
    )
    sta_raw, sta_rc = _run(
        [*_sta_argv(sta_command), "-no_splash", "-exit", _to_sta_path(sta_tcl)],
        timeout_s=timeout_s,
    )
    (output_dir / "route_sta.log").write_text(sta_raw, encoding="utf-8")
    if sta_rc != 0:
        return _failure(sta_raw, f"route sta returncode={sta_rc}")
    if _ERROR_RE.search(sta_raw) or "ROUTED_STA_OK" not in sta_raw:
        return _failure(sta_raw, _first_error(sta_raw, "missing ROUTED_STA_OK"))

    wns_max = _WNS_MAX_RE.search(sta_raw)
    if not wns_max:
        return _failure(sta_raw, "routed WNS not reported")
    wns_min = _WNS_MIN_RE.search(sta_raw)
    tns = _TNS_RE.search(sta_raw)
    setup_wns = float(wns_max.group(1)) * 1e9
    return {
        "wns": setup_wns,
        "tns": float(tns.group(1)) if tns else None,
        "min_slack": float(wns_min.group(1)) * 1e9 if wns_min else None,
        "slack": setup_wns,
        "slack_status": "MET" if setup_wns >= 0 else "VIOLATED",
        "drc_violations": None,
        "routed_netlist": str(routed_netlist),
        "spef": str(spef_path),
        "error": None,
    }


def _first_error(raw: str, fallback: str) -> str:
    hit = _ERROR_RE.search(raw)
    if not hit:
        return fallback
    return raw[hit.start():].splitlines()[0].strip()


def _failure(raw: str, error: str) -> dict:
    return {
        "wns": None,
        "tns": None,
        "min_slack": None,
        "slack": None,
        "slack_status": None,
        "drc_violations": None,
        "error": error,
        "raw_tail": "\n".join(raw.splitlines()[-20:]),
    }