"""Yosys technology mapping against a Liberty timing model.

Stage B: read Verilog → hierarchy -check -top → proc → flatten → opt →
techmap → opt → ``abc -liberty <lib>`` → clean → write_verilog/BLIF.

The wrapper records the full command sequence, runtime, stdout/stderr tail,
and the mapped Verilog/BLIF/log paths. It does not modify the original
Verilog input.
"""

from __future__ import annotations

import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .toolchain import resolve_tool_command


@dataclass(frozen=True)
class TechnologyMappingResult:
    status: str  # "success" / "error" / "timeout" / "unavailable"
    tool: str
    command: str
    runtime_s: float
    reason: str
    mapped_verilog_path: str | None = None
    mapped_blif_path: str | None = None
    log_path: str | None = None
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
            "mapped_verilog_path": self.mapped_verilog_path,
            "mapped_blif_path": self.mapped_blif_path,
            "log_path": self.log_path,
            "returncode": self.returncode,
            "stdout_tail": self.stdout_tail,
            "stderr_tail": self.stderr_tail,
        }


_LIBERTY_CELL_RE = re.compile(r"cell\s*\(\s*([^)\s]+)\s*\)")


def _resolve_yosys(*, yosys_command: str) -> list[str] | None:
    if yosys_command == "yosys":
        tool = resolve_tool_command("yosys", ["yosys"], env_var="FAECO_YOSYS")
    else:
        # Allow callers to pass arbitrary command lines (used by tests).
        tool = resolve_tool_command(
            "yosys", [yosys_command], env_var=None
        )
    if tool is None:
        return None
    return tool.argv


def _yosys_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def _tail(text: str, *, max_lines: int = 20) -> str:
    return "\n".join(text.splitlines()[-max_lines:])


def _extract_liberty_cells(liberty_path: Path) -> set[str]:
    if not liberty_path.exists():
        return set()
    text = liberty_path.read_text(encoding="utf-8", errors="replace")
    return set(_LIBERTY_CELL_RE.findall(text))


def _detect_unmapped_cells(stdout: str, stderr: str, liberty_cells: set[str]) -> set[str]:
    if not liberty_cells:
        return set()
    pattern = re.compile(
        r"(?:Cell|Module|cell)\s+`?([A-Za-z_][\w]*)`?\s+(?:is\s+)?(?:not\s+(?:found|defined)|undefined)",
        re.IGNORECASE,
    )
    candidates: set[str] = set()
    candidates.update(pattern.findall(stdout))
    candidates.update(pattern.findall(stderr))
    return {c for c in candidates if c and c not in liberty_cells}


def map_verilog_to_liberty(
    input_verilog: str | Path,
    liberty_path: str | Path,
    *,
    top_module: str,
    output_dir: str | Path,
    yosys_command: str = "yosys",
    timeout_s: float = 60.0,
) -> TechnologyMappingResult:
    """Run Yosys technology mapping against a Liberty timing model.

    The mapped Verilog, mapped BLIF and full Yosys log are written under
    ``output_dir``. The original ``input_verilog`` is read but never modified.
    """
    started_at = time.perf_counter()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    input_verilog = Path(input_verilog)
    liberty_path = Path(liberty_path)
    mapped_v = output_dir / "mapped.v"
    mapped_blif = output_dir / "mapped.blif"
    log_path = output_dir / "tech_mapping.log"

    yosys_argv = _resolve_yosys(yosys_command=yosys_command)
    if yosys_argv is None:
        return TechnologyMappingResult(
            status="unavailable",
            tool="yosys",
            command=yosys_command,
            runtime_s=time.perf_counter() - started_at,
            reason=f"Yosys command not found: {yosys_command}",
            mapped_verilog_path=str(mapped_v),
            mapped_blif_path=str(mapped_blif),
            log_path=str(log_path),
        )

    script = "; ".join(
        [
            f"read_verilog {_yosys_path(input_verilog)}",
            f"hierarchy -check -top {top_module}",
            "proc",
            "flatten",
            "opt",
            f"synth -top {top_module} -noabc",
            f"abc -liberty {_yosys_path(liberty_path)}",
            "clean",
            f"write_verilog -noattr {_yosys_path(mapped_v)}",
            f"write_blif {_yosys_path(mapped_blif)}",
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
        return TechnologyMappingResult(
            status="timeout",
            tool="yosys",
            command=" ".join(command),
            runtime_s=time.perf_counter() - started_at,
            reason=f"Yosys technology mapping timed out after {timeout_s} seconds",
            mapped_verilog_path=str(mapped_v),
            mapped_blif_path=str(mapped_blif),
            log_path=str(log_path),
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

    if not mapped_v.exists() or not mapped_blif.exists():
        return TechnologyMappingResult(
            status="error",
            tool="yosys",
            command=" ".join(command),
            runtime_s=time.perf_counter() - started_at,
            reason="Yosys did not produce mapped Verilog or BLIF",
            mapped_verilog_path=str(mapped_v) if mapped_v.exists() else None,
            mapped_blif_path=str(mapped_blif) if mapped_blif.exists() else None,
            log_path=str(log_path),
            returncode=completed.returncode,
            stdout_tail=_tail(completed.stdout),
            stderr_tail=_tail(completed.stderr),
        )

    try:
        mapped_v_text = mapped_v.read_text(encoding="utf-8", errors="replace")
        mapped_blif_text = mapped_blif.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return TechnologyMappingResult(
            status="error",
            tool="yosys",
            command=" ".join(command),
            runtime_s=time.perf_counter() - started_at,
            reason=f"Failed to read mapped artifacts: {exc}",
            mapped_verilog_path=str(mapped_v),
            mapped_blif_path=str(mapped_blif),
            log_path=str(log_path),
            returncode=completed.returncode,
            stdout_tail=_tail(completed.stdout),
            stderr_tail=_tail(completed.stderr),
        )

    if not mapped_v_text.strip() or not mapped_blif_text.strip():
        return TechnologyMappingResult(
            status="error",
            tool="yosys",
            command=" ".join(command),
            runtime_s=time.perf_counter() - started_at,
            reason="Mapped Verilog or BLIF is empty",
            mapped_verilog_path=str(mapped_v),
            mapped_blif_path=str(mapped_blif),
            log_path=str(log_path),
            returncode=completed.returncode,
            stdout_tail=_tail(completed.stdout),
            stderr_tail=_tail(completed.stderr),
        )

    liberty_cells = _extract_liberty_cells(liberty_path)
    unmapped = _detect_unmapped_cells(completed.stdout, completed.stderr, liberty_cells)
    if unmapped:
        return TechnologyMappingResult(
            status="error",
            tool="yosys",
            command=" ".join(command),
            runtime_s=time.perf_counter() - started_at,
            reason=(
                f"Mapped cells not found in Liberty: {', '.join(sorted(unmapped))}"
            ),
            mapped_verilog_path=str(mapped_v),
            mapped_blif_path=str(mapped_blif),
            log_path=str(log_path),
            returncode=completed.returncode,
            stdout_tail=_tail(completed.stdout),
            stderr_tail=_tail(completed.stderr),
        )

    if completed.returncode != 0:
        return TechnologyMappingResult(
            status="error",
            tool="yosys",
            command=" ".join(command),
            runtime_s=time.perf_counter() - started_at,
            reason=(
                f"Yosys returned non-zero exit code {completed.returncode}"
            ),
            mapped_verilog_path=str(mapped_v),
            mapped_blif_path=str(mapped_blif),
            log_path=str(log_path),
            returncode=completed.returncode,
            stdout_tail=_tail(completed.stdout),
            stderr_tail=_tail(completed.stderr),
        )

    return TechnologyMappingResult(
        status="success",
        tool="yosys",
        command=" ".join(command),
        runtime_s=time.perf_counter() - started_at,
        reason="Yosys technology mapping against Liberty completed and passed validation",
        mapped_verilog_path=str(mapped_v),
        mapped_blif_path=str(mapped_blif),
        log_path=str(log_path),
        returncode=completed.returncode,
        stdout_tail=_tail(completed.stdout),
        stderr_tail=_tail(completed.stderr),
    )