"""Export a gate-level netlist from the resizer's placed design.

Why this exists
---------------
P1 (``experiments/20261115_p1_resizer_vs_faeco``) and its Hybrid arm both closed
the "beat / complement resizer by better decisions" question.  The one direction
never measured is the mirror composition: **resizer first, our ECO after it**.

To measure that we need the resizer's design as a *netlist* our flow can read.
``write_verilog`` on a routed design carries physical-only cells and (with CTS
done) a clock tree that our flow would build a second time.  So this exporter
runs a *post-placement, pre-CTS* variant of the standard flow:

    floorplan -> place_pins -> pdn -> tapcell -> global_placement
    -> detailed_placement -> repair_timing -setup -> detailed_placement
    -> write_verilog -remove_cells {tapcell}  -> exit

The exported netlist therefore contains the resizer's sizing/buffering but no
clock tree, which keeps re-entry through the standard flow well defined.
This deviation from the archived P1 resizer arm (which repaired after CTS) is
recorded in PREREGISTRATION.md §7 A1 and reported as the "re-entry gap".
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code" / "src"))

from rseco.opensta import _to_sta_path  # noqa: E402
from rseco.placed_sta import DEFAULT_PLATFORM  # noqa: E402
from rseco.routed_sta import DEFAULT_OPENROAD, DEFAULT_ORFS  # noqa: E402

HERE = Path(__file__).resolve().parent
BASE_MAPPED = ROOT / "experiments/20261016_r22_cut_ablation_v3/W1"
PERIOD = 0.5
DENSITY = 0.55
UTIL = 0.35

TAPCELL_MASTER = "sky130_fd_sc_hd__tapvpwrvgnd_1"

# Optional CTS stage: with ``--when post-cts`` the resizer runs where the P1 arm
# ran it (after clock tree synthesis), so the exported netlist carries the same
# quality of repair.  The clock tree it also carries is rebuilt by our standard
# flow; that confound hits R' and RF equally, which is what the H2 comparison
# uses.
CTS_BLOCK = """\
clock_tree_synthesis -buf_list {sky130_fd_sc_hd__clkbuf_4 sky130_fd_sc_hd__clkbuf_8} -root_buf sky130_fd_sc_hd__clkbuf_16
repair_clock_nets
detailed_placement
"""

EXPORT_TCL = """\
set PLATFORM "__PLATFORM__"
set ORFS     "__ORFS__"
set NETLIST  "__NETLIST__"
set OUTDIR   "__OUTDIR__"
set TOP      __TOP__
set PERIOD   __PERIOD__
set UTIL     __UTIL__
set DENSITY  __DENSITY__

read_liberty $PLATFORM/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_lef $PLATFORM/lef/sky130_fd_sc_hd.tlef
read_lef $PLATFORM/lef/sky130_fd_sc_hd_merged.lef
read_verilog $NETLIST
link_design $TOP
create_clock -name clk -period $PERIOD [get_ports CK]

initialize_floorplan -utilization $UTIL -aspect_ratio 1.0 -core_space 2.0 -site unithd
make_tracks
place_pins -hor_layers met3 -ver_layers met2
source $PLATFORM/pdn.tcl
tapcell -distance 14 -tapcell_master __TAPCELL__
global_placement -density $DENSITY
detailed_placement
__CTS__
source $ORFS/setRC.tcl
repair_timing -setup
detailed_placement
set block [ord::get_db_block]
foreach nname {one_ zero_} {
  set net [$block findNet $nname]
  if {$net ne "NULL"} { $net setSigType SIGNAL }
}
# Export a gate-level netlist our own flow can re-read.  Physical-only cells are
# dropped so the design is a pure logical netlist again.
write_verilog -remove_cells {__TAPCELL__} $OUTDIR/resized_gate.v
puts "EXPORT_OK"
exit
"""


def _run_sub(argv: list[str], timeout_s: float) -> tuple[str, int]:
    env = dict(os.environ)
    env["MSYS_NO_PATHCONV"] = "1"
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout_s, env=env)
        return (p.stdout or "") + (p.stderr or ""), p.returncode
    except subprocess.TimeoutExpired as exc:
        return f"timeout after {timeout_s}s: {exc}", 124


def export_one(circuit: str, *, out_root: Path | None = None, when: str = "pre-cts") -> dict:
    """Export the resizer endpoint as a gate-level netlist.

    when="pre-cts"  -> repair on the placed design with an ideal clock
    when="post-cts" -> repair after clock tree synthesis (same position as the
                       P1 resizer arm), exported netlist still carries the clock
                       tree; our standard flow rebuilds it for R' and RF alike.
    """
    out_dir = (out_root or HERE / "exports") / (circuit if when == "pre-cts" else f"{circuit}_postcts")
    out_dir.mkdir(parents=True, exist_ok=True)
    result_path = out_dir / "export.json"
    if result_path.exists():
        try:
            d = json.loads(result_path.read_text(encoding="utf-8"))
            if d.get("ok") and d.get("when") == when:
                print(f"  [{circuit}/{when}] export cached: {d['netlist']}")
                return d
        except Exception:
            pass

    mapped = BASE_MAPPED / circuit / "mapped.v"
    if not mapped.is_file():
        return {"ok": False, "error": f"mapped.v missing: {mapped}"}

    tcl = (
        EXPORT_TCL.replace("__PLATFORM__", DEFAULT_PLATFORM)
        .replace("__ORFS__", DEFAULT_ORFS)
        .replace("__NETLIST__", _to_sta_path(mapped.resolve()))
        .replace("__OUTDIR__", _to_sta_path(out_dir.resolve()))
        .replace("__TOP__", circuit)
        .replace("__PERIOD__", str(PERIOD))
        .replace("__UTIL__", str(UTIL))
        .replace("__DENSITY__", str(DENSITY))
        .replace("__TAPCELL__", TAPCELL_MASTER)
        .replace("__CTS__", CTS_BLOCK if when == "post-cts" else "")
    )
    tcl_path = out_dir / "export.tcl"
    tcl_path.write_text(tcl, encoding="utf-8")

    argv = ["wsl.exe", "-d", "Ubuntu", "--", DEFAULT_OPENROAD, "-no_init", "-exit",
            _to_sta_path(tcl_path)]
    raw, rc = _run_sub(argv, timeout_s=1800.0)
    (out_dir / "export.log").write_text(raw, encoding="utf-8")

    netlist = out_dir / "resized_gate.v"
    ok = rc == 0 and "EXPORT_OK" in raw and netlist.is_file() and netlist.stat().st_size > 0
    result = {
        "ok": ok,
        "circuit": circuit,
        "when": when,
        "returncode": rc,
        "netlist": str(netlist.relative_to(ROOT)) if ok else None,
        "bytes": netlist.stat().st_size if netlist.is_file() else 0,
        "error": None if ok else f"export failed (rc={rc})",
    }
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  [{circuit}/{when}] export ok={ok} bytes={result['bytes']}")
    return result


def main(argv: list[str]) -> int:
    when = "pre-cts"
    if argv and argv[0] in ("pre-cts", "post-cts"):
        when = argv.pop(0)
    circuits = argv or ["s382", "s641", "s832"]
    print(f"exporting resizer netlists ({when}) for: {' '.join(circuits)}")
    all_ok = True
    for c in circuits:
        r = export_one(c, when=when)
        all_ok &= bool(r.get("ok"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))