"""Run sequential timing check: ISCAS89 circuit -> Yosys SKY130 mapping -> OpenSTA STA.

N31-05 sequential ECO foundation: verifies the full sequential timing
pipeline works with real reg-to-reg timing paths and controllable
timing violations:

  1. Yosys synth -top <c> (keeps DFF)
  2. dfflibmap -liberty <SKY130>  (maps DFF -> sky130_fd_sc_hd__dfxtp_1)
  3. abc -liberty <SKY130>        (maps combinational -> SKY130 cells)
  4. OpenSTA: read mapped + Liberty + create_clock -> report slack/wns/tns

Verified 2026-08-03 on ISCAS89 s27:
  - period 10ns -> slack 9.22 (MET)
  - period 1ns  -> slack 0.22 (MET)
  - period 0.5ns -> slack -0.28 (VIOLATED)  [real timing violation]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LIB = (
    ROOT
    / "benchmarks"
    / "raw"
    / "openroad_flow_scripts_sky130hd"
    / "da8f092a02a8e75658cc3100691aabff05f35629"
    / "lib"
    / "sky130_fd_sc_hd__tt_025C_1v80.lib"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--circuit", default="s27", help="ISCAS89 circuit id (default s27)")
    p.add_argument("--iscas89-dir", type=Path, default=ROOT / "benchmarks" / "raw" / "iscas89")
    p.add_argument("--period", type=float, default=10.0, help="Clock period (ns)")
    p.add_argument("--output-dir", type=Path, required=True)
    return p.parse_args()


def _to_wsl(path: Path) -> str:
    return str(path).replace("\\", "/").replace("D:/", "/mnt/d/", 1)


def run_yosys_mapping(circuit: Path, output: Path) -> list[str]:
    """Yosys: synth + dfflibmap + abc -liberty -> pure SKY130 cell netlist."""
    script = output / "map.ys"
    lib_posix = LIB.as_posix()
    top_name = circuit.stem
    src = circuit.read_text(encoding="utf-8", errors="replace")
    # Some ISCAS89 netlists (s820/s832/s953) instantiate a plain ``dff``
    # black box (``dff NAME(CK,D,Q)``) with no module definition.  Yosys
    # cannot resolve it, so emit a preprocessed copy that (1) rewrites the
    # instance to named ports and (2) appends a standard ``module dff``
    # definition that dfflibmap can later map to a SKY130 flop.
    pre = output / "circuit_pre.v"
    if re.search(r"\bdff\s+\w+\s*\(", src) and "module dff" not in src:
        def _fix_dff(m):
            name = m.group(1)
            args = [a.strip() for a in m.group(2).split(",")]
            if len(args) == 3:
                ck, q, d = args
                return "dff " + name + "(.CK(" + ck + "), .D(" + d + "), .Q(" + q + "))"
            return m.group(0)
        src = re.sub(r"\bdff\s+(\w+)\s*\(\s*([^;]+?)\s*\)", _fix_dff, src)
        src += "\nmodule dff(input CK, D, output Q);\n  reg Q;\n  always @(posedge CK) Q <= D;\nendmodule\n"
        pre.write_text(src, encoding="utf-8")
        circuit = pre
    script.write_text(
        "\n".join(
            [
                f"read_verilog {circuit.as_posix()}",
                "synth -top " + top_name,
                f"dfflibmap -liberty {lib_posix}",
                f"abc -liberty {lib_posix}",
                "clean",
                f"write_verilog -noattr {(output / 'mapped.v').as_posix()}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    proc = subprocess.run(
        ["yosys", str(script)], capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=300,
    )
    (output / "map.log").write_text(proc.stdout + proc.stderr, encoding="utf-8")
    return [l for l in (proc.stdout + proc.stderr).splitlines() if "ERROR" in l]


def run_opensta(mapped: Path, period: float, output: Path,
                top_module: str | None = None) -> dict[str, Any]:
    """OpenSTA via WSL2: read Liberty + mapped + create_clock -> report.

    ``top_module`` is the design module name to link.  If omitted, it is
    inferred from the first ``module <name>`` declaration in the mapped
    Verilog (NOT from the parent directory name, which breaks when the
    netlist lives under a subdirectory such as ``cand/``).
    """
    if top_module is None:
        text = mapped.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"\bmodule\s+(\w+)", text)
        top_module = m.group(1) if m else mapped.parent.name
    tcl = output / "sta.tcl"
    tcl.write_text(
        f"read_liberty {_to_wsl(LIB)}\n"
        f"read_verilog {_to_wsl(mapped)}\n"
        f"link_design {top_module}\n"
        f"create_clock -name clk -period {period} [get_ports CK]\n"
        "report_checks -path_delay max\n"
        "report_worst_slack -max\n"
        "report_worst_slack -min\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        ["wsl.exe", "-d", "Ubuntu", "--", "/usr/local/bin/sta",
         "-no_splash", "-exit", _to_wsl(tcl)],
        capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=180,
    )
    (output / "sta.log").write_text(proc.stdout + proc.stderr, encoding="utf-8")
    text = proc.stdout + proc.stderr
    # OpenSTA format: "-0.28   slack (VIOLATED)" (value left of 'slack')
    slack = re.search(r"(-?\d+\.\d+)\s+slack \(([A-Z]+)\)", text)
    wns = re.search(r"worst slack max\s+(-?\d+\.\d+)", text)
    return {
        "slack": float(slack.group(1)) if slack else None,
        "slack_status": slack.group(2) if slack else None,
        "wns": float(wns.group(1)) if wns else None,
    }


def main() -> int:
    args = parse_args()
    circuit = args.iscas89_dir / f"{args.circuit}.v"
    if not circuit.exists():
        print(f"circuit not found: {circuit}", file=sys.stderr)
        return 1
    out = args.output_dir / args.circuit
    out.mkdir(parents=True, exist_ok=True)

    errors = run_yosys_mapping(circuit, out)
    mapped = out / "mapped.v"
    if errors or not mapped.exists():
        print(f"{args.circuit}: mapping failed")
        return 1

    timing = run_opensta(mapped, args.period, out)
    result = {
        "circuit": args.circuit,
        "period_ns": args.period,
        "mapping_errors": len(errors),
        "timing": timing,
    }
    summary_path = out / "timing_check.json"
    summary_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(
        f"{args.circuit}: period={args.period}ns "
        f"slack={timing['slack']} ({timing['slack_status']}) wns={timing['wns']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())