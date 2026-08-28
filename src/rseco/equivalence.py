"""Minimal structural equivalence checks for early FAECO experiments."""

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .netlist import Netlist
from .toolchain import resolve_tool_command, requested_tool_command


@dataclass(frozen=True)
class EquivalenceResult:
    status: str
    method: str
    reason: str


@dataclass(frozen=True)
class FormalEquivalenceResult:
    status: str
    method: str
    tool: str
    command: str
    outputs: list[str]
    runtime_s: float
    reason: str
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
            "returncode": self.returncode,
            "stdout_tail": self.stdout_tail,
            "stderr_tail": self.stderr_tail,
        }


def _signature_equal(left: Any, right: Any) -> bool:
    """Iterative structural equality for signatures (deep cones like b15)."""
    stack: list[tuple[Any, Any]] = [(left, right)]
    while stack:
        a, b = stack.pop()
        if a is b:
            continue
        if type(a) is not type(b):
            return False
        if isinstance(a, tuple):
            if len(a) != len(b):
                return False
            for x, y in zip(a, b):
                stack.append((x, y))
        elif a != b:
            return False
    return True


def check_structural_equivalence(
    left: Netlist,
    right: Netlist,
    *,
    outputs: list[str],
    other_outputs: list[str] | None = None,
) -> EquivalenceResult:
    right_outputs = other_outputs or outputs
    left_signatures = [_signal_signature(left, output) for output in outputs]
    right_signatures = [_signal_signature(right, output) for output in right_outputs]

    if len(left_signatures) == len(right_signatures) and all(
        _signature_equal(l, r)
        for l, r in zip(left_signatures, right_signatures)
    ):
        return EquivalenceResult(
            status="pass",
            method="structural_signature",
            reason="signatures match",
        )
    return EquivalenceResult(
        status="fail",
        method="structural_signature",
        reason="signatures differ",
    )


def check_abc_equivalence(
    original_netlist_path: str | Path,
    revised_netlist_path: str | Path,
    *,
    outputs: list[str],
    abc_command: str = "abc",
    timeout_s: float = 60.0,
) -> FormalEquivalenceResult:
    """Run ABC combinational equivalence checking when ABC is available."""
    started_at = time.perf_counter()
    requested_command = requested_tool_command("abc", abc_command, env_var="FAECO_ABC") if abc_command == "abc" else abc_command
    tool_command = resolve_tool_command("abc", [abc_command], env_var="FAECO_ABC" if abc_command == "abc" else None)
    if tool_command is None:
        return FormalEquivalenceResult(
            status="unavailable",
            method="abc_cec",
            tool="abc",
            command=requested_command,
            outputs=list(outputs),
            runtime_s=time.perf_counter() - started_at,
            reason=f"ABC command not found: {requested_command}",
        )

    script = f"cec {Path(original_netlist_path)} {Path(revised_netlist_path)}"
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
        return FormalEquivalenceResult(
            status="timeout",
            method="abc_cec",
            tool="abc",
            command=" ".join(command),
            outputs=list(outputs),
            runtime_s=time.perf_counter() - started_at,
            reason=f"ABC cec timed out after {timeout_s} seconds",
            stdout_tail=_tail(exc.stdout or ""),
            stderr_tail=_tail(exc.stderr or ""),
        )

    stdout_tail = _tail(completed.stdout)
    stderr_tail = _tail(completed.stderr)
    combined_output = f"{completed.stdout}\n{completed.stderr}".lower()
    status = _abc_status_from_output(combined_output, completed.returncode)
    return FormalEquivalenceResult(
        status=status,
        method="abc_cec",
        tool="abc",
        command=" ".join(command),
        outputs=list(outputs),
        runtime_s=time.perf_counter() - started_at,
        reason=_abc_reason(status, completed.returncode),
        returncode=completed.returncode,
        stdout_tail=stdout_tail,
        stderr_tail=stderr_tail,
    )


def _signal_signature(netlist: Netlist, signal: str) -> Any:
    """Structural fingerprint of the cone driving ``signal`` (iterative DFS).

    Matches the historical recursive formulation exactly: node ids are
    assigned in DFS pre-order and a re-encountered signal (shared DAG node
    or cycle) contributes a ``("ref", id)`` leaf instead of its full
    sub-signature.  The explicit stack avoids RecursionError on deep cones
    (e.g. ITC-99 b15).
    """
    output_to_gate = {gate.output: gate for gate in netlist.gates}
    encounter_ids: dict[str, int] = {}
    memo: dict[str, Any] = {}

    # Continuation-style iterative DFS mirroring the recursive formulation:
    # ids are assigned in DFS pre-order and a gate fanin tuple captures the
    # value visit() returned for each input at call time (full node on first
    # discovery, ("ref", id) on re-encounter).  A re-encounter never
    # overwrites the first-visit signature in ``memo``.
    collectors: list[tuple[str, list[Any]]] = []
    consumers: list[int] = []
    stack: list[tuple[str, Any]] = [("call", signal)]
    final: Any = None

    while stack:
        kind, payload = stack.pop()
        if kind == "call":
            current = payload
            if current in encounter_ids:
                stack.append(("return", ("ref", encounter_ids[current])))
            elif current in netlist.inputs:
                stack.append(("return", ("input", current)))
            else:
                gate = output_to_gate.get(current)
                if gate is None:
                    stack.append(("return", ("net", current)))
                else:
                    encounter_ids[current] = len(encounter_ids)
                    collector_id = len(collectors)
                    collectors.append((current, []))
                    stack.append(("collect", collector_id))
                    for input_signal in reversed(gate.inputs):
                        consumers.append(collector_id)
                        stack.append(("call", input_signal))
        elif kind == "collect":
            collector_id = payload
            current, children = collectors[collector_id]
            gate = output_to_gate[current]
            value = (
                "node",
                encounter_ids[current],
                gate.gate_type,
                tuple(children),
            )
            memo[current] = value
            stack.append(("return", value))
        else:
            value = payload
            if not consumers:
                final = value
            else:
                collector_id = consumers.pop()
                collectors[collector_id][1].append(value)
    return final

def _abc_status_from_output(output: str, returncode: int) -> str:
    if "networks are equivalent" in output or "circuits are equivalent" in output:
        return "pass"
    if "networks are not equivalent" in output or "circuits are not equivalent" in output:
        return "fail"
    if returncode != 0:
        return "error"
    return "error"


def _abc_reason(status: str, returncode: int) -> str:
    reasons = {
        "pass": "ABC cec reported equivalent networks",
        "fail": "ABC cec reported non-equivalent networks",
        "error": f"ABC cec did not produce a recognized equivalence result; returncode={returncode}",
    }
    return reasons[status]


def _tail(text: str, *, max_lines: int = 20) -> str:
    return "\n".join(text.splitlines()[-max_lines:])
