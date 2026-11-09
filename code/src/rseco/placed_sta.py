"""Placement-tier (post-CTS, pre-route) timing evaluation via OpenROAD.

WHY THIS MODULE EXISTS
======================
The inner-loop physical gate in :mod:`rseco.real_wns` used a synthesised
fanout-wireload SPEF (:mod:`rseco.spef`) as its notion of "physics".  That
model is structurally incapable of rewarding buffer insertion: it prices a
net's wire length as a monotone function of its fanout count with a 40 um
floor per net, so splitting a fanout-N net into (1, N-1) always *adds* wire
length (40 + 40*sqrt(N-1) > 40*sqrt(N) for every N >= 2).  Measured on s382
(period 0.5): 110/110 buffer candidates rejected, physical delta in
[-0.14, 0.00] ns.  The gate was therefore not measuring parasitics at all --
it was measuring "did the patch add a cell".

This module replaces that backend with the PLACED tier that the r30 physical
label family validated: a real OpenROAD floorplan -> global placement ->
detailed placement -> CTS flow, followed by ``estimate_parasitics -placement``
and setup timing.  It is *not* sign-off RC extraction (see the caveat below)
but it is derived from actual placement, so isolating a large load across a
buffer is a physically meaningful move.

WHAT IT IS NOT
==============
* Not routing.  ``-placement`` estimates RC from Steiner trees over the placed
  netlist with a single per-unit-length RC pair; the routed tier uses
  per-layer RC over the global-routing topology.  The two models differ, so a
  "routed - placed" difference mixes the stage change with the model change and
  must not be reported as a pure routing penalty.
* Not sign-off extraction (RCX).  The r30 family states the same caveat.
* ``set_wire_rc`` is MANDATORY: without it ``estimate_parasitics -placement`` is
  inert and the reading degenerates to the ideal netlist (measured: 83/83
  candidates identical to the last digit; OpenROAD warns RSZ-0018).

DETERMINISM / PAIRING
=====================
Every candidate -- including the baseline -- goes through the identical flow
with identical parameters, so candidate-vs-baseline is paired by construction.
What the flow does NOT remove is placement dispersion: a one-cell change
re-runs global placement and moves cells, which is precisely the physical
effect the acceptance criterion is supposed to see (measured separately in
``experiments/20261102_layout_stability_n8``: single-arm across-layout spread
median 0.055 ns, up to 0.11 ns).

COST
====
~8 s per candidate on the ISCAS89 designs (vs ~0.05 s for ideal OpenSTA), so
this backend is roughly two orders of magnitude more expensive per evaluation.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .opensta import _to_sta_path

DEFAULT_PLATFORM = "/home/toylog/OpenROAD-flow-scripts/flow/platforms/sky130hd"
DEFAULT_OPENROAD = "/home/toylog/faeco_eda/or26Q3/bin/openroad"

#: Placed-tier timing flow, rendered per call (values substituted, not passed
#: through the environment: arbitrary Windows env vars are not reliably
#: forwarded into the WSL process).
PLACED_TCL = """\
set PLATFORM "__PLATFORM__"
set NETLIST  "__NETLIST__"
set OUTDIR   "__OUTDIR__"
set TOP      __TOP__
set PERIOD   __PERIOD__
set UTIL     __UTIL__
set DENSITY  __DENSITY__
set CLK_PORT __CLK_PORT__

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

# mandatory, otherwise -placement parasitics are inert (RSZ-0018)
set_wire_rc -layer met2 -signal
set_wire_rc -layer met4 -clock
estimate_parasitics -placement

# sta::worst_slack_cmd returns SECONDS (e.g. -1.579e-9 for -1.579 ns);
# report_tns below reports NANOseconds.  The scaling happens in Python.
puts "PLACED_WNS_MAX [sta::worst_slack_cmd max]"
puts "PLACED_WNS_MIN [sta::worst_slack_cmd min]"
puts "PLACED_TNS_BEGIN"
report_tns
puts "PLACED_TNS_END"
write_def $OUTDIR/placed.def
puts "PLACED_OK"
"""

_WNS_MAX_RE = re.compile(r"PLACED_WNS_MAX\s+(-?[0-9.eE+-]+)")
_WNS_MIN_RE = re.compile(r"PLACED_WNS_MIN\s+(-?[0-9.eE+-]+)")
_TNS_RE = re.compile(r"PLACED_TNS_BEGIN\s*\n\s*tns\s+max\s+(-?[0-9.]+)")
_ERROR_RE = re.compile(r"^(?:\[ERROR|Error:)", re.MULTILINE)


def _openroad_argv(command: str | None) -> list[str]:
    if command:
        return command.split()
    return ["wsl.exe", "-d", "Ubuntu", "--", DEFAULT_OPENROAD]


def render_tcl(
    *,
    netlist_path,
    output_dir,
    top_module: str,
    period: float,
    util: float,
    density: float,
    clock_port: str,
    platform: str,
) -> str:
    """Render the placed-tier Tcl for one evaluation (also used by tests)."""
    return (
        PLACED_TCL
        .replace("__PLATFORM__", platform)
        .replace("__NETLIST__", _to_sta_path(Path(netlist_path)))
        .replace("__OUTDIR__", _to_sta_path(Path(output_dir)))
        .replace("__TOP__", str(top_module))
        .replace("__PERIOD__", repr(float(period)))
        .replace("__UTIL__", repr(float(util)))
        .replace("__DENSITY__", repr(float(density)))
        .replace("__CLK_PORT__", str(clock_port))
    )


def run_placed_sta(
    *,
    netlist_path,
    output_dir,
    top_module: str,
    period: float = 0.5,
    clock_port: str = "CK",
    util: float = 0.35,
    density: float = 0.55,
    platform: str = DEFAULT_PLATFORM,
    openroad_command: str | None = None,
    timeout_s: float = 300.0,
) -> dict:
    """Run the placed-tier flow on one netlist and return setup timing in ns.

    Returns a dict shaped like :func:`rseco.opensta.run_opensta_sequential`:
    ``wns`` (setup, ns), ``tns`` (ns), ``min_slack`` (hold, ns), plus
    ``slack``/``slack_status`` (aliases of the setup values, for callers that
    expect the OpenSTA record) and ``error`` (None on success).  Timing values
    are ``None`` when the run fails, so callers fail closed.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tcl_path = output_dir / "placed.tcl"
    tcl_path.write_text(
        render_tcl(
            netlist_path=netlist_path,
            output_dir=output_dir,
            top_module=top_module,
            period=period,
            util=util,
            density=density,
            clock_port=clock_port,
            platform=platform,
        ),
        encoding="utf-8",
    )

    argv = [*_openroad_argv(openroad_command), "-no_init", "-exit", _to_sta_path(tcl_path)]
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
        raw = type(exc).__name__ + ": " + str(exc)
        (output_dir / "placed.log").write_text(raw, encoding="utf-8")
        return _failure(raw=raw, error=raw)

    raw = (proc.stdout or "") + (proc.stderr or "")
    (output_dir / "placed.log").write_text(raw, encoding="utf-8")
    if proc.returncode != 0:
        return _failure(raw=raw, error=f"openroad returncode={proc.returncode}")
    if _ERROR_RE.search(raw) or "PLACED_OK" not in raw:
        diag = _ERROR_RE.search(raw)
        line = raw[diag.start():].splitlines()[0].strip() if diag else "missing PLACED_OK"
        return _failure(raw=raw, error=line)

    wns_max = _WNS_MAX_RE.search(raw)
    wns_min = _WNS_MIN_RE.search(raw)
    tns = _TNS_RE.search(raw)
    if not wns_max:
        return _failure(raw=raw, error="placed WNS not reported")
    setup_wns = float(wns_max.group(1)) * 1e9
    hold_slack = float(wns_min.group(1)) * 1e9 if wns_min else None
    return {
        "wns": setup_wns,
        "tns": float(tns.group(1)) if tns else None,
        "min_slack": hold_slack,
        "slack": setup_wns,
        "slack_status": "MET" if setup_wns >= 0 else "VIOLATED",
        "error": None,
    }


def _failure(*, raw: str, error: str) -> dict:
    return {
        "wns": None,
        "tns": None,
        "min_slack": None,
        "slack": None,
        "slack_status": None,
        "error": error,
        "raw_tail": "\n".join(raw.splitlines()[-20:]),
    }