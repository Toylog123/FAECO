"""Yosys-normalized BLIF plus ABC wrappers for Stage A experiments."""

from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .toolchain import resolve_tool_command, requested_tool_command


FORMAL_SCOPE = "gate_level_full_netlist_all_primary_outputs"
RESYN2_BUILTIN_SEQUENCE = [
    "balance",
    "rewrite",
    "refactor",
    "balance",
    "rewrite",
    "rewrite -z",
    "balance",
    "refactor -z",
    "rewrite -z",
    "balance",
]


@dataclass(frozen=True)
class YosysAbcEquivalenceResult:
    status: str
    method: str
    tool: str
    command: str
    outputs: list[str]
    runtime_s: float
    reason: str
    scope: str = FORMAL_SCOPE
    normalized_original: str | None = None
    normalized_revised: str | None = None
    log_path: str | None = None
    returncode: int | None = None
    stdout_tail: str = ""
    stderr_tail: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "method": self.method,
            "tool": self.tool,
            "command": self.command,
            "outputs": self.outputs,
            "runtime_s": self.runtime_s,
            "reason": self.reason,
            "scope": self.scope,
            "normalized_original": self.normalized_original,
            "normalized_revised": self.normalized_revised,
            "log_path": self.log_path,
            "returncode": self.returncode,
            "stdout_tail": self.stdout_tail,
            "stderr_tail": self.stderr_tail,
        }


@dataclass(frozen=True)
class YosysAbcBaselineResult:
    method: str
    status: str
    tool: str
    command: str
    runtime_s: float
    reason: str
    output_netlist: str | None = None
    normalized_original: str | None = None
    log_path: str | None = None
    verification_log_path: str | None = None
    verification_status: str | None = None
    stats: dict[str, dict[str, int]] | None = None
    returncode: int | None = None
    stdout_tail: str = ""
    stderr_tail: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "method": self.method,
            "status": self.status,
            "tool": self.tool,
            "command": self.command,
            "runtime_s": self.runtime_s,
            "reason": self.reason,
            "output_netlist": self.output_netlist,
            "normalized_original": self.normalized_original,
            "log_path": self.log_path,
            "verification_log_path": self.verification_log_path,
            "verification_status": self.verification_status,
            "stats": self.stats,
            "returncode": self.returncode,
            "stdout_tail": self.stdout_tail,
            "stderr_tail": self.stderr_tail,
        }


def check_yosys_abc_equivalence(
    original_netlist_path: str | Path,
    revised_netlist_path: str | Path,
    *,
    outputs: list[str],
    artifact_dir: str | Path,
    yosys_command: str = "yosys",
    abc_command: str = "yosys-abc",
    timeout_s: float = 60.0,
) -> YosysAbcEquivalenceResult:
    """Normalize Verilog to BLIF with Yosys, then run full-netlist ABC CEC."""
    started_at = time.perf_counter()
    artifact_dir = Path(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    original_blif = artifact_dir / "original.normalized.blif"
    revised_blif = artifact_dir / "revised.normalized.blif"
    log_path = artifact_dir / "abc_cec.log"

    tools = _resolve_yosys_and_abc(yosys_command=yosys_command, abc_command=abc_command)
    if isinstance(tools, _UnavailableTools):
        return YosysAbcEquivalenceResult(
            status="unavailable",
            method="yosys_blif_abc_cec",
            tool="yosys+abc",
            command=tools.requested_command,
            outputs=list(outputs),
            runtime_s=time.perf_counter() - started_at,
            reason=tools.reason,
        )

    normalize_original = _normalize_to_blif(
        Path(original_netlist_path),
        original_blif,
        yosys_argv=tools.yosys_argv,
        timeout_s=timeout_s,
    )
    if normalize_original.returncode != 0 or not original_blif.exists():
        return _formal_error(
            started_at,
            outputs,
            normalize_original,
            reason="Yosys failed to normalize original netlist to BLIF",
            normalized_original=str(original_blif) if original_blif.exists() else None,
            normalized_revised=str(revised_blif) if revised_blif.exists() else None,
        )
    normalize_revised = _normalize_to_blif(
        Path(revised_netlist_path),
        revised_blif,
        yosys_argv=tools.yosys_argv,
        timeout_s=timeout_s,
    )
    if normalize_revised.returncode != 0 or not revised_blif.exists():
        return _formal_error(
            started_at,
            outputs,
            normalize_revised,
            reason="Yosys failed to normalize revised netlist to BLIF",
            normalized_original=str(original_blif),
            normalized_revised=str(revised_blif) if revised_blif.exists() else None,
        )

    script = f"cec {_abc_path(original_blif)} {_abc_path(revised_blif)}"
    command = [*tools.abc_argv, "-s", "-c", script]
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
        return YosysAbcEquivalenceResult(
            status="timeout",
            method="yosys_blif_abc_cec",
            tool="yosys+abc",
            command=" ".join(command),
            outputs=list(outputs),
            runtime_s=time.perf_counter() - started_at,
            reason=f"Yosys/ABC full-netlist cec timed out after {timeout_s} seconds",
            normalized_original=str(original_blif),
            normalized_revised=str(revised_blif),
            log_path=str(log_path),
            stdout_tail=_tail(exc.stdout or ""),
            stderr_tail=_tail(exc.stderr or ""),
        )

    _write_log(log_path, completed)
    combined_output = f"{completed.stdout}\n{completed.stderr}".lower()
    status = _abc_status_from_output(combined_output, completed.returncode)
    return YosysAbcEquivalenceResult(
        status=status,
        method="yosys_blif_abc_cec",
        tool="yosys+abc",
        command=" ".join(command),
        outputs=list(outputs),
        runtime_s=time.perf_counter() - started_at,
        reason=_formal_reason(status, completed.returncode),
        normalized_original=str(original_blif),
        normalized_revised=str(revised_blif),
        log_path=str(log_path),
        returncode=completed.returncode,
        stdout_tail=_tail(completed.stdout),
        stderr_tail=_tail(completed.stderr),
    )


def run_yosys_abc_resynthesis_baseline(
    original_netlist_path: str | Path,
    *,
    output_dir: str | Path,
    yosys_command: str = "yosys",
    abc_command: str = "yosys-abc",
    timeout_s: float = 60.0,
) -> YosysAbcBaselineResult:
    """Normalize to BLIF, run explicit ABC resyn2 sequence, stats, and CEC backcheck."""
    started_at = time.perf_counter()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    original_blif = output_dir / "original.normalized.blif"
    optimized_blif = output_dir / "abc_rewrite_refactor_resyn.blif"
    log_path = output_dir / "abc_baseline.log"
    verification_log_path = output_dir / "abc_baseline_cec.log"

    tools = _resolve_yosys_and_abc(yosys_command=yosys_command, abc_command=abc_command)
    if isinstance(tools, _UnavailableTools):
        return YosysAbcBaselineResult(
            method="yosys_blif_abc_rewrite_refactor_resyn",
            status="unavailable",
            tool="yosys+abc",
            command=tools.requested_command,
            runtime_s=time.perf_counter() - started_at,
            reason=tools.reason,
        )

    normalized = _normalize_to_blif(
        Path(original_netlist_path),
        original_blif,
        yosys_argv=tools.yosys_argv,
        timeout_s=timeout_s,
    )
    if normalized.returncode != 0 or not original_blif.exists():
        return YosysAbcBaselineResult(
            method="yosys_blif_abc_rewrite_refactor_resyn",
            status="error",
            tool="yosys+abc",
            command=" ".join(normalized.command),
            runtime_s=time.perf_counter() - started_at,
            reason="Yosys failed to normalize original netlist to BLIF",
            normalized_original=str(original_blif) if original_blif.exists() else None,
            returncode=normalized.returncode,
            stdout_tail=_tail(normalized.stdout),
            stderr_tail=_tail(normalized.stderr),
        )

    script = "; ".join(
        [
            f"read_blif {_abc_path(original_blif)}",
            "strash",
            *RESYN2_BUILTIN_SEQUENCE,
            "print_stats",
            f"write_blif {_abc_path(optimized_blif)}",
        ]
    )
    command = [*tools.abc_argv, "-s", "-c", script]
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
        return YosysAbcBaselineResult(
            method="yosys_blif_abc_rewrite_refactor_resyn",
            status="timeout",
            tool="yosys+abc",
            command=" ".join(command),
            runtime_s=time.perf_counter() - started_at,
            reason=f"Yosys/ABC resynthesis timed out after {timeout_s} seconds",
            normalized_original=str(original_blif),
            output_netlist=str(optimized_blif),
            log_path=str(log_path),
            stdout_tail=_tail(exc.stdout or ""),
            stderr_tail=_tail(exc.stderr or ""),
        )

    _write_log(log_path, completed)
    stats = _parse_abc_stats(completed.stdout)
    if completed.returncode != 0 or not optimized_blif.exists():
        return YosysAbcBaselineResult(
            method="yosys_blif_abc_rewrite_refactor_resyn",
            status="error",
            tool="yosys+abc",
            command=" ".join(command),
            runtime_s=time.perf_counter() - started_at,
            reason=f"Yosys/ABC resynthesis did not generate optimized BLIF; returncode={completed.returncode}",
            normalized_original=str(original_blif),
            output_netlist=str(optimized_blif) if optimized_blif.exists() else None,
            log_path=str(log_path),
            stats=stats,
            returncode=completed.returncode,
            stdout_tail=_tail(completed.stdout),
            stderr_tail=_tail(completed.stderr),
        )

    verification = _run_abc_cec(
        original_blif,
        optimized_blif,
        abc_argv=tools.abc_argv,
        log_path=verification_log_path,
        timeout_s=timeout_s,
    )
    status = "success" if verification.status == "pass" else "error"
    reason = "Yosys-normalized ABC resynthesis generated BLIF and passed ABC cec backcheck" if status == "success" else (
        f"Yosys-normalized ABC resynthesis verification status={verification.status}"
    )
    return YosysAbcBaselineResult(
        method="yosys_blif_abc_rewrite_refactor_resyn",
        status=status,
        tool="yosys+abc",
        command=" ".join(command),
        runtime_s=time.perf_counter() - started_at,
        reason=reason,
        output_netlist=str(optimized_blif),
        normalized_original=str(original_blif),
        log_path=str(log_path),
        verification_log_path=str(verification_log_path),
        verification_status=verification.status,
        stats=stats,
        returncode=completed.returncode,
        stdout_tail=_tail(completed.stdout),
        stderr_tail=_tail(completed.stderr),
    )


@dataclass(frozen=True)
class _ToolSet:
    yosys_argv: list[str]
    abc_argv: list[str]


@dataclass(frozen=True)
class _UnavailableTools:
    requested_command: str
    reason: str


@dataclass(frozen=True)
class _CommandOutput:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class _CecOutput:
    status: str
    returncode: int | None
    stdout: str
    stderr: str


def _resolve_yosys_and_abc(*, yosys_command: str, abc_command: str) -> _ToolSet | _UnavailableTools:
    requested_yosys = requested_tool_command("yosys", yosys_command, env_var="FAECO_YOSYS") if yosys_command == "yosys" else yosys_command
    requested_abc = requested_tool_command("abc", abc_command, env_var="FAECO_ABC") if abc_command == "yosys-abc" else abc_command
    yosys = resolve_tool_command("yosys", [yosys_command], env_var="FAECO_YOSYS" if yosys_command == "yosys" else None)
    abc_candidates = [abc_command]
    if abc_command == "yosys-abc":
        abc_candidates = ["yosys-abc", "abc"]
    abc = resolve_tool_command("abc", abc_candidates, env_var="FAECO_ABC" if abc_command == "yosys-abc" else None)
    if yosys is None:
        return _UnavailableTools(requested_command=f"{requested_yosys} + {requested_abc}", reason=f"Yosys command not found: {requested_yosys}")
    if abc is None:
        return _UnavailableTools(requested_command=f"{requested_yosys} + {requested_abc}", reason=f"ABC command not found: {requested_abc}")
    return _ToolSet(yosys_argv=yosys.argv, abc_argv=abc.argv)


def _normalize_to_blif(
    netlist_path: Path,
    output_blif: Path,
    *,
    yosys_argv: list[str],
    timeout_s: float,
) -> _CommandOutput:
    output_blif.parent.mkdir(parents=True, exist_ok=True)
    yosys_input_path = _prepare_yosys_input(netlist_path, output_blif)
    script = "; ".join(
        [
            f"read_verilog {_yosys_path(yosys_input_path)}",
            "proc",
            "flatten",
            "opt",
            "simplemap",
            "clean",
            f"write_blif {_yosys_path(output_blif)}",
        ]
    )
    command = [*yosys_argv, "-q", "-p", script]
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
        return _CommandOutput(command=command, returncode=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
    except subprocess.TimeoutExpired as exc:
        return _CommandOutput(command=command, returncode=124, stdout=exc.stdout or "", stderr=exc.stderr or "")


def _prepare_yosys_input(netlist_path: Path, output_blif: Path) -> Path:
    try:
        data = netlist_path.read_bytes()
    except OSError:
        return netlist_path
    if not data.startswith(b"\xef\xbb\xbf"):
        return netlist_path
    sanitized_path = output_blif.with_name(_sanitized_verilog_name(output_blif))
    sanitized_path.write_bytes(data[3:])
    return sanitized_path


def _sanitized_verilog_name(output_blif: Path) -> str:
    suffix = ".normalized.blif"
    if output_blif.name.endswith(suffix):
        return output_blif.name[: -len(suffix)] + ".sanitized.v"
    return output_blif.stem + ".sanitized.v"


def _run_abc_cec(
    left_blif: Path,
    right_blif: Path,
    *,
    abc_argv: list[str],
    log_path: Path,
    timeout_s: float,
) -> _CecOutput:
    script = f"cec {_abc_path(left_blif)} {_abc_path(right_blif)}"
    command = [*abc_argv, "-s", "-c", script]
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
        _write_text_log(log_path, command, exc.stdout or "", exc.stderr or "")
        return _CecOutput(status="timeout", returncode=None, stdout=exc.stdout or "", stderr=exc.stderr or "")
    _write_log(log_path, completed)
    status = _abc_status_from_output(f"{completed.stdout}\n{completed.stderr}".lower(), completed.returncode)
    return _CecOutput(status=status, returncode=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)


def check_mapped_blif_equivalence(
    original_netlist_path: str | Path,
    mapped_blif_path: str | Path,
    *,
    artifact_dir: str | Path,
    yosys_command: str = "yosys",
    abc_command: str = "yosys-abc",
    timeout_s: float = 60.0,
) -> YosysAbcEquivalenceResult:
    """Normalize original Verilog to BLIF, then CEC against an already-mapped BLIF.

    Stage B batch 3: after Yosys ``abc -liberty`` tech-mapping produces a
    mapped BLIF, this function skips Yosys normalisation on the right-hand
    side (because the mapped BLIF is already gate-level BLIF) and runs
    ABC ``cec`` directly against the normalized reference BLIF.
    """
    started_at = time.perf_counter()
    artifact_dir = Path(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    original_blif = artifact_dir / "original.normalized.blif"
    log_path = artifact_dir / "abc_cec.log"

    tools = _resolve_yosys_and_abc(yosys_command=yosys_command, abc_command=abc_command)
    if isinstance(tools, _UnavailableTools):
        return YosysAbcEquivalenceResult(
            status="unavailable",
            method="yosys_blif_abc_cec_mapped",
            tool="yosys+abc",
            command=tools.requested_command,
            outputs=[],
            runtime_s=time.perf_counter() - started_at,
            reason=tools.reason,
            normalized_original=None,
            normalized_revised=str(mapped_blif_path),
        )

    normalize_original = _normalize_to_blif(
        Path(original_netlist_path),
        original_blif,
        yosys_argv=tools.yosys_argv,
        timeout_s=timeout_s,
    )
    if normalize_original.returncode != 0 or not original_blif.exists():
        return _formal_error(
            started_at,
            [],
            normalize_original,
            reason="Yosys failed to normalize original netlist to BLIF",
            normalized_original=str(original_blif) if original_blif.exists() else None,
            normalized_revised=str(mapped_blif_path),
        )

    mapped_blif = Path(mapped_blif_path)
    if not mapped_blif.exists():
        return YosysAbcEquivalenceResult(
            status="error",
            method="yosys_blif_abc_cec_mapped",
            tool="yosys+abc",
            command=" ".join(normalize_original.command),
            outputs=[],
            runtime_s=time.perf_counter() - started_at,
            reason=f"Mapped BLIF not found: {mapped_blif}",
            normalized_original=str(original_blif),
            normalized_revised=str(mapped_blif),
        )

    verification = _run_abc_cec(
        original_blif,
        mapped_blif,
        abc_argv=tools.abc_argv,
        log_path=log_path,
        timeout_s=timeout_s,
    )
    status = verification.status
    reason_map = {
        "pass": "Yosys-normalized original-vs-mapped ABC cec reported equivalent networks",
        "fail": "Yosys-normalized original-vs-mapped ABC cec reported non-equivalent networks",
        "timeout": f"Yosys-normalized original-vs-mapped ABC cec timed out after {timeout_s} seconds",
        "error": f"Yosys-normalized original-vs-mapped ABC cec did not produce a recognized equivalence result; returncode={verification.returncode}",
    }
    return YosysAbcEquivalenceResult(
        status=status,
        method="yosys_blif_abc_cec_mapped",
        tool="yosys+abc",
        command=" ".join(normalize_original.command),
        outputs=[],
        runtime_s=time.perf_counter() - started_at,
        reason=reason_map.get(status, verification.stdout[:200]),
        normalized_original=str(original_blif),
        normalized_revised=str(mapped_blif),
        log_path=str(log_path),
        returncode=verification.returncode,
        stdout_tail=_tail(verification.stdout),
        stderr_tail=_tail(verification.stderr),
    )


def _formal_error(
    started_at: float,
    outputs: list[str],
    command_output: _CommandOutput,
    *,
    reason: str,
    normalized_original: str | None,
    normalized_revised: str | None,
) -> YosysAbcEquivalenceResult:
    return YosysAbcEquivalenceResult(
        status="error",
        method="yosys_blif_abc_cec",
        tool="yosys+abc",
        command=" ".join(command_output.command),
        outputs=list(outputs),
        runtime_s=time.perf_counter() - started_at,
        reason=reason,
        normalized_original=normalized_original,
        normalized_revised=normalized_revised,
        returncode=command_output.returncode,
        stdout_tail=_tail(command_output.stdout),
        stderr_tail=_tail(command_output.stderr),
    )


def _abc_status_from_output(output: str, returncode: int) -> str:
    if "networks are equivalent" in output or "circuits are equivalent" in output:
        return "pass"
    if "networks are not equivalent" in output or "circuits are not equivalent" in output:
        return "fail"
    if returncode != 0:
        return "error"
    return "error"


def _formal_reason(status: str, returncode: int) -> str:
    reasons = {
        "pass": "Yosys-normalized full-netlist ABC cec reported equivalent networks",
        "fail": "Yosys-normalized full-netlist ABC cec reported non-equivalent networks",
        "error": f"Yosys-normalized full-netlist ABC cec did not produce a recognized equivalence result; returncode={returncode}",
    }
    return reasons[status]


def _parse_abc_stats(output: str) -> dict[str, dict[str, int]]:
    rows = []
    pattern = re.compile(
        r"i/o\s*=\s*(?P<inputs>\d+)\s*/\s*(?P<outputs>\d+)\s+lat\s*=\s*(?P<lat>\d+)\s+and\s*=\s*(?P<and>\d+)\s+lev\s*=\s*(?P<lev>\d+)"
    )
    for line in output.splitlines():
        match = pattern.search(line)
        if match:
            rows.append({key: int(value) for key, value in match.groupdict().items()})
    if not rows:
        return {}
    if len(rows) == 1:
        return {"after": rows[-1]}
    return {"before": rows[0], "after": rows[-1]}


def _write_log(path: Path, completed: subprocess.CompletedProcess[str]) -> None:
    _write_text_log(path, completed.args if isinstance(completed.args, list) else [str(completed.args)], completed.stdout, completed.stderr)


def _write_text_log(path: Path, command: list[str], stdout: str, stderr: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "command: " + " ".join(command) + "\n\nstdout:\n" + stdout + "\n\nstderr:\n" + stderr + "\n",
        encoding="utf-8",
    )


def _yosys_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def _abc_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def _tail(text: str, *, max_lines: int = 20) -> str:
    return "\n".join(text.splitlines()[-max_lines:])
