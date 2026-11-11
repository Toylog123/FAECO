"""Run OpenROAD resizer (repair_timing -setup) using the same flow as routed_sta.

Instead of duplicating the subprocess machinery, we simply:
1. Render the routed_sta flow Tcl
2. Insert `repair_timing -setup` after CTS
3. Feed it through the existing `run_routed_sta` pipeline
"""
from __future__ import annotations

import json
from pathlib import Path

from config import BASE_MAPPED, CIRCUITS, DENSITY, PERIOD, ROOT, UTILS
from rseco.routed_sta import run_routed_sta, render_flow_tcl

# Marker where we insert repair_timing
_CTS_MARKER = "pin_access"
_RESIZER_BLOCK = """\
# ---- FAECO-P P1: OpenROAD resizer ----
# Runs after setRC.tcl/set_routing_layers, before routing.
# Legalising the resizer's new cells is necessary for DRT to find pins.
repair_timing -setup
detailed_placement
# s713: repair_timing can promote tie nets (one_/zero_) to POWER type,
# which TritonRoute then refuses to route. Demote them back to SIGNAL.
set block [ord::get_db_block]
foreach nname {one_ zero_} {
  set net [$block findNet $nname]
  if {$net ne "NULL"} { $net setSigType SIGNAL }
}
# ----------------------------------------
pin_access"""


def run_resizer_one(circuit: str, *, util: float = 0.35) -> dict:
    """Run resizer + routing + STA on one circuit."""
    import os as _os
    dirname = _os.environ.get("RESIZER_DIR", "arms/Resizer")
    out_dir = ROOT / dirname / circuit
    out_dir.mkdir(parents=True, exist_ok=True)

    # Already done?
    result_path = out_dir / "result.json"
    if result_path.exists():
        try:
            d = json.loads(result_path.read_text(encoding="utf-8"))
            if d.get("wns") is not None:
                print(f"  [{circuit}] cached wns={d['wns']:.4f}")
                return d
        except Exception:
            pass

    # Optional replacement input (Hybrid arm: feed a previously produced netlist
    # instead of the W1 mapped.v). RESIZER_INPUT_DIR looks for <c>.v, then <c>/FAECO-P.v.
    input_dir = _os.environ.get("RESIZER_INPUT_DIR", "").strip()
    if input_dir:
        cand = [ROOT / input_dir / f"{circuit}.v", ROOT / input_dir / circuit / "FAECO-P.v"]
        mapped_src = next((c for c in cand if c.is_file()), cand[-1])
    else:
        mapped_src = BASE_MAPPED / circuit / "mapped.v"
    if not mapped_src.exists():
        return {"error": f"mapped.v not found: {mapped_src}", "wns": None}

    # Trick: render the flow Tcl, patch in repair_timing, then monkeypatch
    # render_flow_tcl temporarily so run_routed_sta picks up our version.
    from rseco.placed_sta import DEFAULT_PLATFORM
    from rseco.routed_sta import DEFAULT_ORFS

    original_flow = render_flow_tcl(
        netlist_path=str(mapped_src.resolve()),
        output_dir=str(out_dir.resolve()),
        top_module=circuit,
        period=PERIOD,
        util=util,
        density=DENSITY,
        clock_port="CK",
        platform=DEFAULT_PLATFORM,
        orfs=DEFAULT_ORFS,
    )
    patched_flow = original_flow.replace(_CTS_MARKER, _RESIZER_BLOCK)

    # Save patched Tcl for the flow
    flow_tcl = out_dir / "resizer_flow.tcl"
    flow_tcl.write_text(patched_flow, encoding="utf-8")

    # Manually run the patched flow + STA (mimic run_routed_sta internals)
    import re
    import subprocess
    from rseco.placed_sta import DEFAULT_PLATFORM
    from rseco.routed_sta import (
        DEFAULT_OPENROAD, DEFAULT_ORFS, DEFAULT_STA,
        ROUTED_STA_TCL, _WNS_MAX_RE, _WNS_MIN_RE, _TNS_RE, _DRC_RE,
    )
    from rseco.opensta import _to_sta_path

    # 1. Flow
    argv = ["wsl.exe", "-d", "Ubuntu", "--", DEFAULT_OPENROAD]
    argv.extend(["-no_init", "-exit", _to_sta_path(flow_tcl)])
    flow_raw, flow_rc = _run_sub(argv, timeout_s=1800.0)
    (out_dir / "resizer_flow.log").write_text(flow_raw, encoding="utf-8")
    if flow_rc != 0:
        return {"error": f"flow returncode={flow_rc}", "wns": None}

    routed_v = out_dir / "routed.v"
    routed_spef = out_dir / "routed.spef"
    if not routed_v.is_file() or not routed_spef.is_file():
        return {"error": "routed.v or routed.spef not produced", "wns": None}

    # 2. STA
    sta_tcl = ROUTED_STA_TCL.replace("__PLATFORM__", DEFAULT_PLATFORM)
    sta_tcl = sta_tcl.replace("__NETLIST__", _to_sta_path(routed_v))
    sta_tcl = sta_tcl.replace("__SPEF__", _to_sta_path(routed_spef))
    sta_tcl = sta_tcl.replace("__TOP__", circuit)
    sta_tcl = sta_tcl.replace("__PERIOD__", str(PERIOD))
    sta_tcl = sta_tcl.replace("__CLK_PORT__", "CK")
    sta_tcl_path = out_dir / "resizer_sta.tcl"
    sta_tcl_path.write_text(sta_tcl, encoding="utf-8")

    argv_sta = ["wsl.exe", "-d", "Ubuntu", "--", DEFAULT_STA]
    argv_sta.extend(["-no_splash", "-exit", _to_sta_path(sta_tcl_path)])
    sta_raw, sta_rc = _run_sub(argv_sta, timeout_s=300.0)
    (out_dir / "resizer_sta.log").write_text(sta_raw, encoding="utf-8")
    if sta_rc != 0:
        return {"error": f"sta returncode={sta_rc}", "wns": None}

    wns = None
    m = _WNS_MAX_RE.search(sta_raw)
    if m:
        wns = float(m.group(1)) * 1e9
    tns = None
    m = _TNS_RE.search(sta_raw)
    if m:
        tns = float(m.group(1))
    min_slack = None
    m = _WNS_MIN_RE.search(sta_raw)
    if m:
        min_slack = float(m.group(1)) * 1e9

    drc_rpt = out_dir / "drc.rpt"
    drc_violations = 0
    if drc_rpt.is_file():
        drc_violations = len(_DRC_RE.findall(drc_rpt.read_text(encoding="utf-8", errors="replace")))

    result = {
        "wns": wns,
        "tns": tns,
        "min_slack": min_slack,
        "drc_violations": drc_violations,
        "error": None,
    }
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"  [{circuit}] wns={wns:.4f} tns={tns} drc={drc_violations}")
    return result


def _run_sub(argv: list[str], *, timeout_s: float) -> tuple[str, int | None]:
    """Run a subprocess, returning (stdout+stderr, returncode)."""
    import subprocess
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


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("circuits", nargs="*", default=None)
    p.add_argument("--util", type=float, default=0.35)
    args = p.parse_args()

    circuits = args.circuits or CIRCUITS
    results = {}
    for c in circuits:
        r = run_resizer_one(c, util=args.util)
        results[c] = r
        if r.get("error"):
            print(f"  [{c}] ERROR: {r['error']}")

    import os as _os2
    summary_path = ROOT / _os2.environ.get("RESIZER_DIR", "arms/Resizer") / "summary.json"
    summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSummary: {summary_path}")


if __name__ == "__main__":
    main()