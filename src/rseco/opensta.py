"""OpenSTA pre-layout timing runner for Stage B.

Drives ``sta`` from Windows via WSL2, emitting a Tcl script that reads the
Liberty model, the mapped Verilog and the SDC, then reports worst negative
slack / total negative slack / worst slack / status. The runner records the
full command sequence, runtime, stdout/stderr tail, and the report / log
paths. It does not modify the input netlist, Liberty or SDC.
"""

from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .toolchain import resolve_tool_command

LIB_SEQ = (
    Path(__file__).resolve().parents[2]
    / "benchmarks"
    / "raw"
    / "openroad_flow_scripts_sky130hd"
    / "da8f092a02a8e75658cc3100691aabff05f35629"
    / "lib"
    / "sky130_fd_sc_hd__tt_025C_1v80.lib"
)


@dataclass(frozen=True)
class StaResult:
    status: str  # "success" / "error" / "timeout" / "unavailable"
    tool: str
    command: str
    runtime_s: float
    reason: str
    wns: float | None = None
    tns: float | None = None
    slack: float | None = None
    slack_status: str = "UNKNOWN"
    report_path: str | None = None
    script_path: str | None = None
    log_path: str | None = None
    liberty_path: str | None = None
    netlist_path: str | None = None
    sdc_path: str | None = None
    tool_version: str | None = None
    returncode: int | None = None
    stdout_tail: str = ""
    stderr_tail: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "tool": self.tool,
            "command": self.command,
            "runtime_s": self.runtime_s,
            "reason": self.reason,
            "wns": self.wns,
            "tns": self.tns,
            "slack": self.slack,
            "slack_status": self.slack_status,
            "report_path": self.report_path,
            "script_path": self.script_path,
            "log_path": self.log_path,
            "liberty_path": self.liberty_path,
            "netlist_path": self.netlist_path,
            "sdc_path": self.sdc_path,
            "tool_version": self.tool_version,
            "returncode": self.returncode,
            "stdout_tail": self.stdout_tail,
            "stderr_tail": self.stderr_tail,
        }


_WNS_RE = re.compile(r"wns\s+(?:max|min)\s+(-?\d+\.\d+)")
_TNS_RE = re.compile(r"tns\s+(?:max|min)\s+(-?\d+\.\d+)")
_SLACK_MET_RE = re.compile(r"Path slack \(MET\):\s+(-?\d+\.\d+)")
_SLACK_VIOL_RE = re.compile(r"Path slack \(VIOLATED\):\s+(-?\d+\.\d+)")
_WORST_SLACK_RE = re.compile(
    r"worst\s+slack\s+(max|min)\s+(-?\d+\.\d+|inf|INF|-?inf|-?INF)"
)
_NO_PATHS_RE = re.compile(r"No paths found", re.IGNORECASE)
_VERSION_RE = re.compile(r"OpenSTA\s+(\S+)")


def _parse_numeric_token(token: str) -> float | None:
    t = token.strip().lower()
    if t in {"inf", "-inf"}:
        return None
    return float(token)


def parse_sta_report(report: str) -> dict[str, object]:
    """Parse key metrics from an OpenSTA report string.

    Recognises both the legacy ``wns max X`` / ``tns max X`` format and the
    OpenSTA 3.1 ``worst slack max INF`` format. When ``No paths found``
    appears (purely combinational circuits), WNS/TNS/slack are reported as
    None and status is ``MET`` to reflect the absence of violations.
    """
    wns = _WNS_RE.search(report)
    tns = _TNS_RE.search(report)
    slack_met = _SLACK_MET_RE.search(report)
    slack_viol = _SLACK_VIOL_RE.search(report)
    worst = _WORST_SLACK_RE.search(report)
    no_paths = bool(_NO_PATHS_RE.search(report))
    version = _VERSION_RE.search(report)

    if slack_met:
        slack_value = float(slack_met.group(1))
        slack_status = "MET"
    elif slack_viol:
        slack_value = float(slack_viol.group(1))
        slack_status = "VIOLATED"
    elif worst:
        slack_value = _parse_numeric_token(worst.group(2))
        slack_status = "MET"
    elif no_paths:
        slack_value = None
        slack_status = "MET"
    else:
        slack_value = None
        slack_status = "UNKNOWN"

    return {
        "wns": float(wns.group(1)) if wns else None,
        "tns": float(tns.group(1)) if tns else None,
        "slack": slack_value,
        "slack_status": slack_status,
        "tool_version": version.group(1) if version else None,
    }


def _resolve_sta(*, sta_command: str) -> list[str] | None:
    if sta_command in {"sta", "/usr/local/bin/sta"}:
        tool = resolve_tool_command(
            "opensta", ["sta", "/usr/local/bin/sta"],
            env_var="FAECO_OPENSTA",
        )
    else:
        tool = resolve_tool_command("opensta", [sta_command], env_var=None)
    if tool is None:
        return None
    return tool.argv


def _to_sta_path(path: Path) -> str:
    """Convert a Windows / POSIX path to a path OpenSTA can read.

    OpenSTA running inside WSL2 expects Linux-style paths. For Windows
    paths under D:\\, this maps ``D:\\foo\\bar`` -> ``/mnt/d/foo/bar``.
    """
    text = str(path)
    match = re.match(r"^([A-Za-z]):[\\/](.*)$", text)
    if match:
        drive = match.group(1).lower()
        rest = match.group(2).replace("\\", "/")
        return f"/mnt/{drive}/{rest}"
    return text.replace("\\", "/")


def _tail(text: str, *, max_lines: int = 20) -> str:
    return "\n".join(text.splitlines()[-max_lines:])


def build_pre_layout_sta_script(
    *,
    liberty_path: Path,
    netlist_path: Path,
    sdc_path: Path,
    top_module: str = "top",
) -> str:
    """Build a Tcl command file for OpenSTA pre-layout STA."""
    lib = _to_sta_path(liberty_path)
    net = _to_sta_path(netlist_path)
    sdc = _to_sta_path(sdc_path)
    return (
        "# FAECO pre-layout STA script\n"
        f"read_liberty {lib}\n"
        f"read_verilog {net}\n"
        f"link_design {top_module}\n"
        f"source {sdc}\n"
        "report_checks -path_delay max\n"
        "report_checks -path_delay min\n"
        "report_worst_slack -max\n"
        "report_worst_slack -min\n"
        "exit\n"
    )



_SEQ_SLACK_RE = re.compile(r"(-?\d+\.\d+)\s+slack \(([A-Z]+)\)")
_SEQ_WNS_RE = re.compile(r"worst slack max\s+(-?\d+\.\d+)")
_SEQ_MIN_SLACK_RE = re.compile(r"worst slack min\s+(-?\d+\.\d+)")
_SEQ_TNS_RE = re.compile(r"tns\s+max\s+(-?\d+\.\d+)")


def run_opensta_sequential(
    *,
    netlist_path,
    period,
    output_dir,
    top_module=None,
    multi_path=False,
    sta_command="wsl-sta",
    timeout_s=180.0,
    hold_uncertainty: float = 0.0,
    min_path: bool = False,
):
    """Run sequential pre-layout STA (create_clock on CK) via OpenSTA.

    Mirrors the verified ``scripts/run_sequential_timing_check.py`` flow so
    library callers (real-WNS outer-loop evaluator) can measure candidate
    netlists without depending on the script's import context.  Returns a
    dict with keys ``slack``, ``slack_status``, ``wns``, ``tns``,
    ``min_slack`` and ``min_slack_status`` (min slack comes from the
    ``report_worst_slack -min`` line; only present when the run reports it).

    ``sta_command`` defaults to ``wsl-sta`` (``wsl.exe -d Ubuntu --
    /usr/local/bin/sta``), matching the documented FAECO environment;
    pass an explicit command (e.g. ``python fake_sta.py``) in tests or on
    native-Linux setups.

    ``multi_path`` appends ``report_checks -slack_max 0 -endpoint_count
    100000`` so critical-path instances can be parsed from the report.

    ``hold_uncertainty`` (ns) injects ``set_clock_uncertainty -hold X`` to
    model a hold-violation scenario; ``min_path`` adds a min-path
    ``report_checks -slack_max 0`` so hold-critical instances can be parsed.
    """
    if top_module is None:
        raw = Path(netlist_path).read_text(encoding="utf-8", errors="replace")
        m = re.search(r"\bmodule\s+(\w+)", raw)
        top_module = m.group(1) if m else Path(netlist_path).parent.name
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tcl = output_dir / "sta.tcl"
    tcl_body = (
        "read_liberty " + _to_sta_path(LIB_SEQ) + "\n"
        "read_verilog " + _to_sta_path(Path(netlist_path)) + "\n"
        "link_design " + str(top_module) + "\n"
        "create_clock -name clk -period " + str(period) + " [get_ports CK]\n"
        "report_checks -path_delay max\n"
    )
    if hold_uncertainty and hold_uncertainty > 0:
        tcl_body += "set_clock_uncertainty -hold " + str(hold_uncertainty) + " [get_clocks clk]\n"
    if min_path:
        tcl_body += "report_checks -path_delay min -slack_max 0 -endpoint_count 100000\n"
    if multi_path:
        tcl_body += "report_checks -path_delay max -slack_max 0 -endpoint_count 100000\n"
    tcl_body += (
        'puts "TNS_BEGIN"\n'
        "report_tns\n"
        'puts "TNS_END"\n'
        "report_worst_slack -max\n"
        "report_worst_slack -min\n"
    )
    tcl.write_text(tcl_body, encoding="utf-8")
    if sta_command == "wsl-sta":
        sta_argv = ["wsl.exe", "-d", "Ubuntu", "--", "/usr/local/bin/sta"]
    else:
        sta_argv = _resolve_sta(sta_command=sta_command)
    if sta_argv is None:
        return {
            "slack": None,
            "slack_status": None,
            "wns": None,
            "tns": None,
            "min_slack": None,
            "min_slack_status": None,
            "error": "OpenSTA command not found: " + str(sta_command),
        }
    proc = subprocess.run(
        [*sta_argv, "-no_splash", "-exit", _to_sta_path(tcl)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_s,
    )
    (output_dir / "sta.log").write_text(proc.stdout + proc.stderr, encoding="utf-8")
    raw = proc.stdout + proc.stderr
    slack = _SEQ_SLACK_RE.search(raw)
    wns = _SEQ_WNS_RE.search(raw)
    tns = _SEQ_TNS_RE.search(raw)
    min_slack = _SEQ_MIN_SLACK_RE.search(raw)
    return {
        "slack": float(slack.group(1)) if slack else None,
        "slack_status": slack.group(2) if slack else None,
        "wns": float(wns.group(1)) if wns else None,
        "tns": float(tns.group(1)) if tns else None,
        "min_slack": float(min_slack.group(1)) if min_slack else None,
        "min_slack_status": (
            "MET" if float(min_slack.group(1)) >= 0 else "VIOLATED"
        ) if min_slack else None,
    }


def run_opensta_pre_layout(
    *,
    netlist_path: str | Path,
    liberty_path: str | Path,
    sdc_path: str | Path,
    output_dir: str | Path,
    sta_command: str = "sta",
    top_module: str = "top",
    timeout_s: float = 60.0,
) -> StaResult:
    """Run pre-layout STA via OpenSTA and parse slack / WNS / TNS from stdout."""
    started_at = time.perf_counter()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    netlist_path = Path(netlist_path)
    liberty_path = Path(liberty_path)
    sdc_path = Path(sdc_path)
    script_path = output_dir / "sta_script.tcl"
    log_path = output_dir / "sta.log"
    report_path = output_dir / "sta_report.txt"

    script_text = build_pre_layout_sta_script(
        liberty_path=liberty_path,
        netlist_path=netlist_path,
        sdc_path=sdc_path,
        top_module=top_module,
    )
    script_path.write_text(script_text, encoding="utf-8")

    sta_argv = _resolve_sta(sta_command=sta_command)
    if sta_argv is None:
        return StaResult(
            status="unavailable",
            tool="opensta",
            command=sta_command,
            runtime_s=time.perf_counter() - started_at,
            reason=f"OpenSTA command not found: {sta_command}",
            report_path=str(report_path),
            script_path=str(script_path),
            log_path=str(log_path),
            liberty_path=str(liberty_path),
            netlist_path=str(netlist_path),
            sdc_path=str(sdc_path),
        )

    command = [*sta_argv, "-no_splash", "-exit", _to_sta_path(script_path)]

    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired as exc:
        log_path.write_text(
            "command: " + " ".join(command) + "\n\n"
            "timeout after "
            + str(timeout_s)
            + " seconds\n\nstdout:\n"
            + (exc.stdout or "")
            + "\n\nstderr:\n"
            + (exc.stderr or "")
            + "\n",
            encoding="utf-8",
        )
        return StaResult(
            status="timeout",
            tool="opensta",
            command=" ".join(command),
            runtime_s=time.perf_counter() - started_at,
            reason=f"OpenSTA pre-layout STA timed out after {timeout_s} seconds",
            report_path=str(report_path),
            script_path=str(script_path),
            log_path=str(log_path),
            liberty_path=str(liberty_path),
            netlist_path=str(netlist_path),
            sdc_path=str(sdc_path),
            stdout_tail=_tail(exc.stdout or ""),
            stderr_tail=_tail(exc.stderr or ""),
        )

    log_path.write_text(
        "command: " + " ".join(command) + "\n\nstdout:\n"
        + completed.stdout
        + "\n\nstderr:\n"
        + completed.stderr
        + "\n",
        encoding="utf-8",
    )
    report_path.write_text(completed.stdout, encoding="utf-8")

    metrics = parse_sta_report(completed.stdout)
    status = "success" if metrics["slack_status"] in {"MET", "VIOLATED"} else (
        "error" if completed.returncode != 0 else "success"
    )
    reason_map = {
        "success": "OpenSTA pre-layout STA produced a recognized slack report",
        "error": (
            f"OpenSTA returncode={completed.returncode}; report did not contain "
            "recognized slack lines"
        ),
    }
    return StaResult(
        status=status,
        tool="opensta",
        command=" ".join(command),
        runtime_s=time.perf_counter() - started_at,
        reason=reason_map.get(status, "unknown"),
        wns=metrics["wns"],
        tns=metrics["tns"],
        slack=metrics["slack"],
        slack_status=str(metrics["slack_status"]),
        report_path=str(report_path),
        script_path=str(script_path),
        log_path=str(log_path),
        liberty_path=str(liberty_path),
        netlist_path=str(netlist_path),
        sdc_path=str(sdc_path),
        tool_version=str(metrics["tool_version"]) if metrics["tool_version"] else None,
        returncode=completed.returncode,
        stdout_tail=_tail(completed.stdout),
        stderr_tail=_tail(completed.stderr),
    )
