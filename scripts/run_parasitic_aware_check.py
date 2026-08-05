"""Parasitic-aware (SPEF) verification of FAECO ECO repairs.

Re-runs OpenSTA on baseline vs repaired mapped netlists under two modes:
  * ideal-net (the paper nominal pre-layout STA);
  * SPEF-annotated (fanout-driven estimated wire RC via src/rseco/spef.py).

Answers the paper key physical-awareness question: does the repair that
improves ideal-net WNS still improve WNS once wire load is present?
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rseco.spef import parse_mapped_verilog, write_spef

LIB = Path(r"benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib").resolve()


def to_wsl(p: Path) -> str:
    rp = str(p.resolve())
    if rp.startswith("D:\\"):
        return "/mnt/d/" + rp[3:].replace("\\", "/")
    return rp.replace("\\", "/")


def run_sta(mapped: Path, period: float, out: Path, spef: Path | None, top: str) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    lines = [
        f"read_liberty {to_wsl(LIB)}",
        f"read_verilog {to_wsl(mapped)}",
        f"link_design {top}",
    ]
    if spef is not None:
        lines.append(f"read_spef {to_wsl(spef)}")
    lines += [
        f"create_clock -name clk -period {period} [get_ports CK]",
        "report_checks -path_delay max",
        "report_worst_slack -max",
        "report_worst_slack -min",
    ]
    tcl = out / "sta.tcl"
    tcl.write_text("\n".join(lines), encoding="utf-8")
    proc = subprocess.run(
        ["wsl.exe", "-d", "Ubuntu", "--", "/usr/local/bin/sta", "-no_splash", "-exit", to_wsl(tcl)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300,
    )
    log = proc.stdout + proc.stderr
    (out / "sta.log").write_text(log, encoding="utf-8")
    slack = re.search(r"(-?\d+\.\d+)\s+slack \(([A-Z]+)\)", log)
    wns = re.search(r"worst slack max\s+(-?\d+\.\d+)", log)
    return {
        "rc": proc.returncode,
        "slack": float(slack.group(1)) if slack else None,
        "status": slack.group(2) if slack else None,
        "wns": float(wns.group(1)) if wns else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True, type=Path)
    ap.add_argument("--repaired", required=True, type=Path)
    ap.add_argument("--period", required=True, type=float)
    ap.add_argument("--output-dir", required=True, type=Path)
    ap.add_argument("--top", default=None)
    ap.add_argument("--unit-len-um", type=float, default=40.0)
    args = ap.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    nl = parse_mapped_verilog(args.baseline)
    top = args.top or nl.module_name
    spef = write_spef(out / "estimated.spef", nl, unit_len_um=args.unit_len_um)

    rows = {
        "baseline_ideal": run_sta(args.baseline, args.period, out / "baseline_ideal", None, top),
        "baseline_spef": run_sta(args.baseline, args.period, out / "baseline_spef", spef, top),
        "repaired_ideal": run_sta(args.repaired, args.period, out / "repaired_ideal", None, top),
        "repaired_spef": run_sta(args.repaired, args.period, out / "repaired_spef", spef, top),
    }
    b_i = rows["baseline_ideal"]["wns"]
    r_i = rows["repaired_ideal"]["wns"]
    b_s = rows["baseline_spef"]["wns"]
    r_s = rows["repaired_spef"]["wns"]
    summary = {
        "circuit": top,
        "period_ns": args.period,
        "unit_len_um": args.unit_len_um,
        "rows": rows,
        "ideal_delta": round(r_i - b_i, 4) if (b_i is not None and r_i is not None) else None,
        "spef_delta": round(r_s - b_s, 4) if (b_s is not None and r_s is not None) else None,
    }
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
