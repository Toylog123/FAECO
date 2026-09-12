"""Tool command resolution helpers for external EDA wrappers."""

from __future__ import annotations

import os
import shlex
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ToolCommand:
    display: str
    argv: list[str]
    path: str | None
    source: str


def resolve_tool_command(
    tool_id: str,
    candidates: list[str],
    *,
    env_var: str | None = None,
) -> ToolCommand | None:
    """Resolve an external tool, preferring an explicit env command when present."""
    explicit = os.environ.get(env_var) if env_var else None
    if explicit:
        command = _command_from_spec(explicit, source=f"env:{env_var}")
        if command is not None:
            return command

    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return ToolCommand(
                display=candidate,
                argv=[resolved],
                path=resolved,
                source="path",
            )
        command = _command_from_spec(candidate, source="candidate")
        if command is not None:
            return command
    return None


def requested_tool_command(tool_id: str, default_command: str, *, env_var: str | None = None) -> str:
    explicit = os.environ.get(env_var) if env_var else None
    return explicit or default_command


def _command_from_spec(command_spec: str, *, source: str) -> ToolCommand | None:
    parts = [_strip_quotes(part) for part in shlex.split(command_spec, posix=False)]
    parts = [part for part in parts if part]
    if not parts:
        return None

    executable = parts[0]
    resolved = _resolve_executable(executable)
    if resolved is None:
        return None
    return ToolCommand(
        display=command_spec,
        argv=[resolved, *parts[1:]],
        path=resolved,
        source=source,
    )


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _resolve_executable(executable: str) -> str | None:
    path = Path(executable)
    if path.exists():
        return str(path.resolve())
    return shutil.which(executable)
