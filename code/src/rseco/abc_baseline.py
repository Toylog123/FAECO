"""ABC resynthesis baseline wrapper for Stage A experiments."""

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .toolchain import resolve_tool_command, requested_tool_command


@dataclass(frozen=True)
class AbcBaselineResult:
    method: str
    status: str
    tool: str
    command: str
    runtime_s: float
    reason: str
    output_netlist: str | None = None
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
            "returncode": self.returncode,
            "stdout_tail": self.stdout_tail,
            "stderr_tail": self.stderr_tail,
        }


def run_abc_resynthesis_baseline(
    original_netlist_path: str | Path,
    *,
    output_dir: str | Path,
    abc_command: str = "abc",
    timeout_s: float = 60.0,
) -> AbcBaselineResult:
    """Run ABC rewrite/refactor/resyn when ABC is available."""
    started_at = time.perf_counter()
    requested_command = requested_tool_command("abc", abc_command, env_var="FAECO_ABC") if abc_command == "abc" else abc_command
    tool_command = resolve_tool_command("abc", [abc_command], env_var="FAECO_ABC" if abc_command == "abc" else None)
    if tool_command is None:
        return AbcBaselineResult(
            method="abc_rewrite_refactor_resyn",
            status="unavailable",
            tool="abc",
            command=requested_command,
            runtime_s=time.perf_counter() - started_at,
            reason=f"ABC command not found: {requested_command}",
        )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_netlist = output_dir / "abc_rewrite_refactor_resyn.v"
    script = "; ".join(
        [
            f"read {Path(original_netlist_path)}",
            "strash",
            "rewrite",
            "refactor",
            "resyn2",
            f"write {output_netlist}",
        ]
    )
    command = [*tool_command.argv, "-c", script]
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
        return AbcBaselineResult(
            method="abc_rewrite_refactor_resyn",
            status="timeout",
            tool="abc",
            command=" ".join(command),
            runtime_s=time.perf_counter() - started_at,
            reason=f"ABC resynthesis timed out after {timeout_s} seconds",
            output_netlist=str(output_netlist),
            stdout_tail=_tail(exc.stdout or ""),
            stderr_tail=_tail(exc.stderr or ""),
        )

    status = "success" if completed.returncode == 0 and output_netlist.exists() else "error"
    reason = "ABC resynthesis baseline generated output netlist" if status == "success" else (
        f"ABC resynthesis did not generate output netlist; returncode={completed.returncode}"
    )
    return AbcBaselineResult(
        method="abc_rewrite_refactor_resyn",
        status=status,
        tool="abc",
        command=" ".join(command),
        runtime_s=time.perf_counter() - started_at,
        reason=reason,
        output_netlist=str(output_netlist) if output_netlist.exists() else None,
        returncode=completed.returncode,
        stdout_tail=_tail(completed.stdout),
        stderr_tail=_tail(completed.stderr),
    )


def _tail(text: str, *, max_lines: int = 20) -> str:
    return "\n".join(text.splitlines()[-max_lines:])
