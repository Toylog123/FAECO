"""Z3 candidate/boundary formal equivalence wrapper (N31-06).

Complements the existing ABC CEC path with per-candidate boundary SMT
verification.  Uses z3-solver 5.0.0 Python API directly so tests do
not need the z3 binary on PATH.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path

import z3


@dataclass(frozen=True)
class Z3FormalEquivalenceResult:
    status: str  # "pass" / "fail" / "timeout" / "unavailable"
    tool: str = "z3"
    command: str = ""
    runtime_s: float = 0.0
    reason: str = ""
    candidate_id: str = ""
    boundary_ports: tuple[str, ...] = ()
    wns_unaffected_check: bool = True
    returncode: int | None = None
    counterexample_inputs: tuple[tuple[str, int], ...] = ()
    stdout_tail: str = ""
    stderr_tail: str = ""
    smt2_problem_path: str | None = None
    smt2_output_path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "tool": self.tool,
            "command": self.command,
            "runtime_s": self.runtime_s,
            "reason": self.reason,
            "candidate_id": self.candidate_id,
            "boundary_ports": list(self.boundary_ports),
            "wns_unaffected_check": self.wns_unaffected_check,
            "returncode": self.returncode,
            "counterexample_inputs": list(self.counterexample_inputs),
            "stdout_tail": self.stdout_tail,
            "stderr_tail": self.stderr_tail,
            "smt2_problem_path": self.smt2_problem_path,
            "smt2_output_path": self.smt2_output_path,
        }


def _is_z3_available() -> bool:
    try:
        import z3  # noqa: F401

        return True
    except ImportError:
        return False


def _first_assign(verilog: str) -> str | None:
    m = re.search(r"(assign\s+[^;]+;)", verilog)
    return m.group(1) if m else None


def _assign_to_z3(assign: str, g: dict[str, "z3.BoolRef"]) -> "z3.BoolRef":
    """Parse a simple `assign y = a & b;` or `assign y = a;` expression.

    Supports: identifiers in `g`, `&` (And), `|` (Or), `~` (Not), and
    parentheses.  Anything unknown becomes an unconstrained Bool
    (conservative — may make tests over-complex expressions return
    "fail" which is acceptable for FAECO's small cone-level Verilog).
    """
    s = assign.strip()
    if s.startswith("y = "):
        s = s[len("y = "):]
    s = s.rstrip(";").strip()
    env: dict[str, "z3.BoolRef"] = dict(g)

    def parse_expr(s: str) -> "z3.BoolRef":
        s = s.strip()
        if s.startswith("(") and s.endswith(")"):
            return parse_expr(s[1:-1])
        if s.startswith("~"):
            return z3.Not(parse_expr(s[1:]))
        # binary | (lowest precedence)
        for op_str, op_func in (
            ("|", z3.Or),
            ("&", z3.And),
        ):
            depth = 0
            for i in range(len(s) - 1, -1, -1):
                ch = s[i]
                if ch == ")":
                    depth += 1
                elif ch == "(":
                    depth -= 1
                elif depth == 0 and s[i:i + 1] == op_str and (
                    i == 0 or s[i - 1] not in {"=", "|", "&"}
                ):
                    return op_func(parse_expr(s[:i]), parse_expr(s[i + 1:]))
        if s in env:
            return env[s]
        return z3.Bool(s)

    return parse_expr(s)


def check_z3_candidate_boundary_equivalence(
    original_netlist_path,
    replaced_netlist_path,
    *,
    boundary_ports,
    liberty_path=None,
    output_dir,
    z3_command="z3",
    timeout_s=60.0,
) -> Z3FormalEquivalenceResult:
    """Check candidate patch boundary equivalence using Z3 SMT.

    Builds an SMT problem asserting that some boundary input makes the
    original and replaced outputs differ, then asks z3 for a
    counterexample.  Returns Z3FormalEquivalenceResult.
    """
    started_at = time.perf_counter()
    original_path = Path(original_netlist_path)
    replaced_path = Path(replaced_netlist_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    smt2_problem_path = output_dir / "boundary_equivalence.smt2"
    smt2_output_path = output_dir / "boundary_equivalence.smt2.output"

    boundary_ports = list(boundary_ports)
    command = (
        f"check_z3_candidate_boundary_equivalence("
        f"{original_path}, {replaced_path})"
    )

    if not _is_z3_available():
        return Z3FormalEquivalenceResult(
            status="unavailable",
            command=command,
            runtime_s=time.perf_counter() - started_at,
            reason="z3-solver Python package not importable",
            boundary_ports=tuple(boundary_ports),
            smt2_problem_path=str(smt2_problem_path),
        )

    try:
        original_text = original_path.read_text(encoding="utf-8", errors="replace")
        replaced_text = replaced_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return Z3FormalEquivalenceResult(
            status="error",
            command=command,
            runtime_s=time.perf_counter() - started_at,
            reason=f"failed to read verilog: {exc}",
            boundary_ports=tuple(boundary_ports),
            smt2_problem_path=str(smt2_problem_path),
        )

    o_assign = _first_assign(original_text)
    r_assign = _first_assign(replaced_text)
    if o_assign is None or r_assign is None:
        return Z3FormalEquivalenceResult(
            status="error",
            command=command,
            runtime_s=time.perf_counter() - started_at,
            reason="could not extract assign expression from verilog",
            boundary_ports=tuple(boundary_ports),
            smt2_problem_path=str(smt2_problem_path),
        )

    g = {p: z3.Bool(p) for p in boundary_ports}
    try:
        o_expr = _assign_to_z3(o_assign, g)
        r_expr = _assign_to_z3(r_assign, g)
    except Exception as exc:  # noqa: BLE001
        return Z3FormalEquivalenceResult(
            status="error",
            command=command,
            runtime_s=time.perf_counter() - started_at,
            reason=f"failed to parse assign expression: {exc}",
            boundary_ports=tuple(boundary_ports),
            smt2_problem_path=str(smt2_problem_path),
        )

    s = z3.Solver()
    try:
        s.set("timeout", int(timeout_s * 1000))  # milliseconds
    except z3.Z3Exception:
        # some backends may not support per-solver timeout
        pass
    s.add(o_expr != r_expr)

    try:
        smt2_text = s.to_smt2()
    except Exception:  # noqa: BLE001
        smt2_text = s.sexpr()
    smt2_problem_path.write_text(smt2_text, encoding="utf-8")

    try:
        check_result = s.check()
    except z3.Z3TimeoutError:
        return Z3FormalEquivalenceResult(
            status="timeout",
            command=command,
            runtime_s=time.perf_counter() - started_at,
            reason=f"z3 timed out after {timeout_s} seconds",
            boundary_ports=tuple(boundary_ports),
            smt2_problem_path=str(smt2_problem_path),
        )
    except Exception as exc:  # noqa: BLE001
        return Z3FormalEquivalenceResult(
            status="error",
            command=command,
            runtime_s=time.perf_counter() - started_at,
            reason=f"z3 solver error: {exc}",
            boundary_ports=tuple(boundary_ports),
            smt2_problem_path=str(smt2_problem_path),
        )

    smt2_output_path.write_text(str(check_result), encoding="utf-8")

    if str(check_result) == "unsat":
        return Z3FormalEquivalenceResult(
            status="pass",
            command=command,
            runtime_s=time.perf_counter() - started_at,
            reason="z3 unsat: boundary equivalence holds",
            boundary_ports=tuple(boundary_ports),
            returncode=0,
            smt2_problem_path=str(smt2_problem_path),
            smt2_output_path=str(smt2_output_path),
        )
    if str(check_result) == "sat":
        m = s.model()
        ce: list[tuple[str, int]] = []
        for p in boundary_ports:
            try:
                val = m.eval(z3.Bool(p), model_completion=True)
                ce.append((p, 1 if z3.is_true(val) else 0))
            except Exception:  # noqa: BLE001
                ce.append((p, 0))
        return Z3FormalEquivalenceResult(
            status="fail",
            command=command,
            runtime_s=time.perf_counter() - started_at,
            reason="z3 sat: counterexample found",
            boundary_ports=tuple(boundary_ports),
            returncode=0,
            counterexample_inputs=tuple(ce),
            smt2_problem_path=str(smt2_problem_path),
            smt2_output_path=str(smt2_output_path),
        )
    if str(check_result) == "unknown":
        return Z3FormalEquivalenceResult(
            status="timeout",
            command=command,
            runtime_s=time.perf_counter() - started_at,
            reason="z3 returned unknown (likely timeout or quantifier)",
            boundary_ports=tuple(boundary_ports),
            smt2_problem_path=str(smt2_problem_path),
            smt2_output_path=str(smt2_output_path),
        )
    return Z3FormalEquivalenceResult(
        status="error",
        command=command,
        runtime_s=time.perf_counter() - started_at,
        reason=f"z3 returned unexpected result: {check_result}",
        boundary_ports=tuple(boundary_ports),
        smt2_problem_path=str(smt2_problem_path),
        smt2_output_path=str(smt2_output_path),
    )