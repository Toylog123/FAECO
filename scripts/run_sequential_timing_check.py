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
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from rseco.netlist_audit import audit_netlist
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


def _find_oss_cad_root() -> Path | None:
    """Locate the OSS-CAD Suite root (native Windows Yosys 0.67).

    Review shortboard defect 4: the FAECO toolchain is unified on the
    OSS-CAD Suite nightly (Yosys 0.67+), replacing both the 32-bit Windows
    Yosys 0.9 and the WSL Ubuntu 0.33 package.  The suite ships its runtime
    DLLs under lib/, so PATH must include both bin/ and lib/.
    """
    explicit = os.environ.get("YOSYSHQ_ROOT")
    if explicit and Path(explicit).exists():
        return Path(explicit)
    candidates = [
        Path(r"C:\oss-cad-suite-build\oss-cad-suite"),
        Path.home() / "oss-cad-suite",
    ]
    for cand in candidates:
        if (cand / "bin" / "yosys.exe").exists():
            return cand
    return None


def _yosys_env() -> dict | None:
    """Environment for the native OSS-CAD Yosys; None falls back to os.environ."""
    root = _find_oss_cad_root()
    if root is None:
        return None
    env = dict(os.environ)
    env["YOSYSHQ_ROOT"] = str(root)
    env["SSL_CERT_FILE"] = str(root / "etc" / "cacert.pem")
    env["PATH"] = str(root / "bin") + os.pathsep + str(root / "lib") + os.pathsep + env.get("PATH", "")
    return env


def _to_wsl(path: Path) -> str:
    """Windows path -> WSL /mnt/d path (absolute).

    Resolve first so relative paths become absolute before the
    drive-letter rewrite; otherwise WSL cannot find them.
    """
    p = path.resolve()
    return str(p).replace("\\", "/").replace("D:/", "/mnt/d/", 1)


def run_yosys_mapping(circuit: Path, output: Path,
                      yosys_cmd: list[str] | None = None) -> list[str]:
    """Yosys: synth + dfflibmap + abc -liberty -> pure SKY130 cell netlist.

    ``yosys_cmd`` selects the Yosys executable. Default is the native
    OSS-CAD Suite nightly Yosys 0.67 (the unified FAECO toolchain,
    review shortboard defect 4); pass
    ["wsl.exe", "-d", "Ubuntu", "--", "/usr/bin/yosys"] to fall back to
    the WSL2 Ubuntu 0.33 package. WSL mode translates map.ys paths via
    _to_wsl.
    """
    # unified FAECO toolchain: default to native OSS-CAD Yosys 0.67;
    # resolve the command *before* the WSL path translation check.
    # NOTE: Windows CreateProcess resolves a bare ``yosys`` name via the
    # *parent* PATH (the child env PATH is ignored for lookup), so when
    # OSS-CAD is installed we must pass the absolute exe path to make
    # sure the correct binary runs instead of a legacy PATH shim.
    if yosys_cmd is None:
        root = _find_oss_cad_root()
        yosys_cmd = [str(root / "bin" / "yosys.exe")] if root else ["yosys"]
    script = output / "map.ys"
    lib_posix = LIB.as_posix()
    script_posix = script.as_posix()
    mapped_posix = (output / "mapped.v").as_posix()
    use_wsl = bool(yosys_cmd and yosys_cmd[0].endswith("wsl.exe"))
    if use_wsl:
        lib_posix = _to_wsl(LIB)
        script_posix = _to_wsl(script)
        mapped_posix = _to_wsl(output / "mapped.v")
    top_name = circuit.stem
    src = circuit.read_text(encoding="utf-8", errors="replace")
    circuit_for_script = _to_wsl(circuit) if use_wsl else circuit.as_posix()
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
        circuit_for_script = _to_wsl(circuit) if use_wsl else circuit.as_posix()
    script.write_text(
        "\n".join(
            [
                f"read_verilog {circuit_for_script}",
                "synth -top " + top_name,
                f"dfflibmap -liberty {lib_posix}",
                f"abc -liberty {lib_posix}",
                "clean",
                f"write_verilog -noattr {mapped_posix}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    proc = subprocess.run(
        yosys_cmd + [script_posix], capture_output=True, text=True,
        env=None if use_wsl else _yosys_env(),
        encoding="utf-8", errors="replace", timeout=1500,
    )
    (output / "map.log").write_text(proc.stdout + proc.stderr, encoding="utf-8")
    mapped_file = output / "mapped.v"
    if mapped_file.exists():
        # OpenSTA 3.1.0's Verilog parser rejects `wire signed` declarations
        # (Yosys 0.67 write_verilog keeps the RTL signed attribute on leftover
        # internal nets).  For structural STA the signedness is irrelevant, so
        # normalize the declaration (bit widths unchanged).
        text = mapped_file.read_text(encoding="utf-8", errors="replace")
        if "wire signed" in text:
            mapped_file.write_text(text.replace("wire signed", "wire"), encoding="utf-8")
    return [l for l in (proc.stdout + proc.stderr).splitlines() if "ERROR" in l]


def _parse_tns(sta_text: str) -> float | None:
    """Extract TNS (sum of negative endpoint slacks) from the TNS_BEGIN/END section.

    OpenSTA report_tns prints a single line (e.g. "tns max -5.74");
    TNS is the total negative slack over all violating endpoints.  Returns
    None when the section is absent or contains no recognized tns line.
    """
    begin = sta_text.find("TNS_BEGIN")
    end = sta_text.find("TNS_END")
    if begin == -1 or end == -1 or end <= begin:
        return None
    section = sta_text[begin:end]
    m = re.search(r"tns\s+max\s+(-?\d+\.\d+)", section)
    if m:
        return round(float(m.group(1)), 3)
    vals = [
        float(mt[0])
        for mt in re.findall(r"(-?\d+\.\d+)\s+slack \(([A-Z]+)\)", section)
        if mt[1] == "VIOLATED"
    ]
    if not vals:
        return None
    return round(sum(vals), 3)


def run_opensta(mapped: Path, period: float, output: Path,
                top_module: str | None = None, multi_path: bool = False,
                hold_uncertainty: float = 0.0,
                clock_port: str = "CK") -> dict[str, Any]:
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
    tcl_body = (
        f"read_liberty {_to_wsl(LIB)}\n"
        f"read_verilog {_to_wsl(mapped)}\n"
        f"link_design {top_module}\n"
        f"create_clock -name clk -period {period} [get_ports {clock_port}]\n"
    )
    if hold_uncertainty and hold_uncertainty > 0:
        tcl_body += f"set_clock_uncertainty -hold {hold_uncertainty} [get_clocks clk]\n"
    tcl_body += "report_checks -path_delay max\n"
    if multi_path:
        # collect all violating-path instances for critical-instance parsing
        tcl_body += "report_checks -path_delay max -slack_max 0 -endpoint_count 100000\n"
    tcl_body += (
        'puts "TNS_BEGIN"\n'
        "report_tns\n"
        'puts "TNS_END"\n'
        "report_worst_slack -max\n"
        "report_worst_slack -min\n"
    )
    tcl.write_text(tcl_body, encoding="utf-8")
    proc = subprocess.run(
        ["wsl.exe", "-d", "Ubuntu", "--", "/usr/local/bin/sta",
         "-no_splash", "-exit", _to_wsl(tcl)],
        capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=900,
    )
    (output / "sta.log").write_text(proc.stdout + proc.stderr, encoding="utf-8")
    text = proc.stdout + proc.stderr
    # OpenSTA format: "-0.28   slack (VIOLATED)" (value left of 'slack')
    slack = re.search(r"(-?\d+\.\d+)\s+slack \(([A-Z]+)\)", text)
    wns = re.search(r"worst slack max\s+(-?\d+\.\d+)", text)
    min_slack = re.search(r"worst slack min\s+(-?\d+\.\d+)", text)
    tns = _parse_tns(text)
    return {
        "slack": float(slack.group(1)) if slack else None,
        "slack_status": slack.group(2) if slack else None,
        "wns": float(wns.group(1)) if wns else None,
        "min_slack": float(min_slack.group(1)) if min_slack else None,
        "tns": tns,
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
    mapped_text = mapped.read_text(encoding="utf-8", errors="replace")
    audit = audit_netlist(mapped_text, report=True)
    result = {
        "circuit": args.circuit,
        "period_ns": args.period,
        "mapping_errors": len(errors),
        "timing": timing,
        "netlist_audit": audit,
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
