"""Parasitic-aware (SPEF) verification of FAECO ECO repairs.

Re-runs OpenSTA on baseline vs repaired mapped netlists under two modes:
  * ideal-net (the paper nominal pre-layout STA);
  * SPEF-annotated (fanout-driven estimated wire RC via src/rseco/spef.py).

Answers the paper key physical-awareness question: does the repair that
improves ideal-net WNS still improve WNS once wire load is present?
"""
import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rseco.spef import parse_mapped_verilog, write_spef
from rseco.opensta import _sta_failure_reason, _output_text

LIB = Path(r"data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib").resolve()


def to_wsl(p: Path) -> str:
    rp = str(p.resolve())
    if rp.startswith("D:\\"):
        return "/mnt/d/" + rp[3:].replace("\\", "/")
    return rp.replace("\\", "/")


def _artifact(path: Path) -> dict:
    path = Path(path)
    result = {"path": str(path.resolve()), "exists": path.is_file()}
    if path.is_file():
        raw = path.read_bytes()
        result.update(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
    return result


def _save_json(path: Path, value) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def run_sta(mapped: Path, period: float, out: Path, spef: Path | None, top: str,
            *, clock_port: str = "CK", rc_model: dict | None = None) -> dict:
    out.mkdir(parents=True, exist_ok=False)
    rc_model = dict(rc_model or {"unit_len_um": 40.0, "fanout_penalty": 1.0, "depth_penalty": 1.0})
    inputs = {"netlist": _artifact(mapped), "liberty": _artifact(LIB),
              "spef": _artifact(spef) if spef is not None else None}
    lines = [
        f"read_liberty {to_wsl(LIB)}",
        f"read_verilog {to_wsl(mapped)}",
        f"link_design {top}",
    ]
    if spef is not None:
        lines.append(f"read_spef {to_wsl(spef)}")
    lines += [
        f"create_clock -name clk -period {period} [get_ports {clock_port}]",
        "report_checks -path_delay max",
        "report_worst_slack -max",
        "report_worst_slack -min",
    ]
    tcl = out / "sta.tcl"
    tcl.write_text("\n".join(lines), encoding="utf-8")
    # WSL auto-translates the inherited Windows PATH into /mnt/... entries;
    # non-existent entries (e.g. E:\APP\...) make wsl.exe print
    # "Failed to translate" and can break the VM exec. Pass a minimal PATH
    # that only contains System32 (enough to resolve wsl.exe itself).
    clean_env = os.environ.copy()
    clean_env["PATH"] = r"C:\Windows\System32;C:\Windows"
    command = ["wsl.exe", "-d", "Ubuntu", "--", "/usr/local/bin/sta", "-no_splash", "-exit", to_wsl(tcl)]
    error = None
    returncode = None
    try:
        if not all(row is None or row["exists"] for row in inputs.values()):
            raise FileNotFoundError("A required netlist/Liberty/SPEF input is missing")
        proc = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=600, env=clean_env)
        returncode = proc.returncode
        log = proc.stdout + proc.stderr
        error = _sta_failure_reason(log, returncode)
    except (OSError, subprocess.TimeoutExpired) as exc:
        log = _output_text(getattr(exc, "stdout", None)) + _output_text(getattr(exc, "stderr", None))
        log += "\n" + type(exc).__name__ + ": " + str(exc) + "\n"
        error = str(exc)
    log_path = out / "sta.log"
    log_path.write_text(log, encoding="utf-8")
    after = {"netlist": _artifact(mapped), "liberty": _artifact(LIB),
             "spef": _artifact(spef) if spef is not None else None}
    if after != inputs:
        error = "Measurement input changed during the STA process"
    slack = re.search(r"(-?\d+\.\d+)\s+slack \(([A-Z]+)\)", log)
    wns = re.search(r"worst slack max\s+(-?\d+\.\d+)", log)
    slack_value = float(slack.group(1)) if slack else None
    wns_value = float(wns.group(1)) if wns else None
    if error is None and not (slack_value is not None and wns_value is not None
                              and math.isfinite(slack_value) and math.isfinite(wns_value)):
        error = "OpenSTA did not produce finite recognized path slack and worst slack"
    valid = error is None
    receipt = {
        **inputs, "inputs_after": after, "tcl": _artifact(tcl), "log": _artifact(log_path),
        "rc_model": rc_model,
        "rc_model_sha256": hashlib.sha256(json.dumps(rc_model, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "top": top, "clock_port": clock_port, "period_ns": period, "argv": command,
        "timeout_s": 600, "returncode": returncode, "valid": valid, "error": error,
    }
    receipt_path = out / "measurement_receipt.json"
    _save_json(receipt_path, receipt)
    return {"rc": returncode, "slack": slack_value if valid else None,
            "status": slack.group(2) if valid else None, "wns": wns_value if valid else None,
            "valid": valid, "error": error, "measurement_receipt_path": str(receipt_path),
            "measurement_receipt_sha256": _artifact(receipt_path)["sha256"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True, type=Path)
    ap.add_argument("--repaired", required=True, type=Path)
    ap.add_argument("--period", required=True, type=float)
    ap.add_argument("--output-dir", required=True, type=Path)
    ap.add_argument("--top", default=None)
    ap.add_argument("--clock-port", default="CK")
    ap.add_argument("--unit-len-um", type=float, default=40.0)
    args = ap.parse_args()
    out = args.output_dir
    try:
        out.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print(f"Output directory already exists; refusing to overwrite: {out}", file=sys.stderr)
        return 2
    rc_model = {"unit_len_um": args.unit_len_um, "fanout_penalty": 1.0, "depth_penalty": 1.0}
    try:
        if not math.isfinite(args.period) or args.period <= 0 or not math.isfinite(args.unit_len_um) or args.unit_len_um <= 0:
            raise ValueError("Period and unit wire length must be finite and positive")
        original_inputs = {"baseline": _artifact(args.baseline), "repaired": _artifact(args.repaired),
                           "liberty": _artifact(LIB)}
        liberty_text = LIB.read_text(encoding="utf-8")
        baseline_nl = parse_mapped_verilog(args.baseline, liberty_text=liberty_text, top_module=args.top)
        top = baseline_nl.module_name
        repaired_nl = parse_mapped_verilog(args.repaired, liberty_text=liberty_text, top_module=top)
        baseline_spef = write_spef(out / "baseline.spef", baseline_nl, **rc_model)
        repaired_spef = write_spef(out / "repaired.spef", repaired_nl, **rc_model)
        rows = {}
        for side, mapped, spef in [("baseline", args.baseline, baseline_spef),
                                  ("repaired", args.repaired, repaired_spef)]:
            for mode, annotation in [("ideal", None), ("spef", spef)]:
                name = side + "_" + mode
                rows[name] = run_sta(mapped, args.period, out / name, annotation, top,
                                     clock_port=args.clock_port, rc_model=rc_model)
        final_inputs = {"baseline": _artifact(args.baseline), "repaired": _artifact(args.repaired),
                        "liberty": _artifact(LIB)}
        if original_inputs != final_inputs:
            raise ValueError("Comparison input changed while generating or measuring its sides")
    except (OSError, ValueError) as exc:
        _save_json(out / "failure.json", {"valid": False, "error_type": type(exc).__name__, "error": str(exc),
                    "baseline": _artifact(args.baseline), "repaired": _artifact(args.repaired),
                    "liberty": _artifact(LIB), "rc_model": rc_model})
        print(f"Parasitic comparison failed: {exc}", file=sys.stderr)
        return 1
    b_i = rows["baseline_ideal"]["wns"]
    r_i = rows["repaired_ideal"]["wns"]
    b_s = rows["baseline_spef"]["wns"]
    r_s = rows["repaired_spef"]["wns"]
    summary = {
        "circuit": top,
        "period_ns": args.period,
        "clock_port": args.clock_port,
        "unit_len_um": args.unit_len_um,
        "rc_model": rc_model,
        "original_inputs": original_inputs,
        "inputs_after": final_inputs,
        "valid": all(row["valid"] for row in rows.values()),
        "rows": rows,
        "ideal_delta": round(r_i - b_i, 4) if (b_i is not None and r_i is not None) else None,
        "spef_delta": round(r_s - b_s, 4) if (b_s is not None and r_s is not None) else None,
    }
    _save_json(out / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
