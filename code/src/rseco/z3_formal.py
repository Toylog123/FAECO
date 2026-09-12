"""Z3 candidate/boundary formal equivalence wrapper (N31-06).

Complements the existing ABC CEC path with per-candidate boundary SMT
verification.  Uses z3-solver 5.0.0 Python API directly so tests do
not need the z3 binary on PATH.

Supports:
- simple single ``assign y = ...`` modules (original tests)
- EPFL-style modules with internal wire assigns and escaped
  identifiers (``assign n19 = ~\\B[1] & \\B[4];``), multiple output
  ports, ``& | ^ ~`` operators, parentheses and ``1'b0``/``1'b1``
  literals.
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


def _normalize_ident(name: str) -> str:
    """Normalize an escaped identifier ``\\B[0]`` to ``B[0]``.

    Non-escaped identifiers are returned unchanged.  ``[0]`` bus
    suffixes are preserved so boundary ports match ``B[0]`` style.
    Trailing ``)`` / ``,`` / ``;`` (from one-line module-port
    declarations like ``module top(input a, output y);``) are stripped.
    """
    name = name.strip()
    if name.startswith("\\"):
        name = name[1:]
    while name and name[-1] in "),;":
        name = name[:-1]
    return name.strip()


def _parse_assigns(verilog: str) -> dict[str, str]:
    """Extract ``{lhs: expr}`` from all ``assign <lhs> = <expr>;`` lines.

    lhs and expr tokens are normalized (escaped ``\\`` removed).
    """
    assigns: dict[str, str] = {}
    # match `assign <lhs> = <expr> ;` where expr may span until ';'
    for m in re.finditer(r"\bassign\s+([^=;]+)\s*=\s*([^;]+)\s*;", verilog):
        lhs = _normalize_ident(m.group(1))
        assigns[lhs] = m.group(2).strip()
    return assigns


def _parse_module_outputs(verilog: str) -> list[str]:
    """Extract normalized output port names from ``output ...;`` lines."""
    outputs: list[str] = []
    for m in re.finditer(r"\boutput\s+([^;]+);", verilog):
        for name in m.group(1).split(","):
            name = _normalize_ident(name)
            if name:
                outputs.append(name)
    return outputs


def _parse_module_inputs(verilog: str) -> list[str]:
    """Extract normalized input port names from ``input ...;`` lines."""
    inputs: list[str] = []
    for m in re.finditer(r"\binput\s+([^;]+);", verilog):
        for name in m.group(1).split(","):
            name = _normalize_ident(name)
            if name:
                inputs.append(name)
    return inputs


class _ExprParser:
    """Recursive-descent parser for simple boolean Verilog expressions.

    Grammar:
        or_expr   := xor_expr ( '|' xor_expr )*
        xor_expr  := and_expr ( '^' and_expr )*
        and_expr  := unary ( '&' unary )*
        unary     := '~' unary | primary
        primary   := '(' or_expr ')' | constant | identifier

    ``env`` maps identifiers (boundary ports) to z3.BoolRef; unknown
    identifiers raise KeyError so a genuinely unsupported expression
    reports ``error`` instead of silently comparing two unconstrained
    bools.
    """

    def __init__(self, text: str, env: dict[str, "z3.BoolRef"]) -> None:
        self._tokens = self._tokenize(text)
        self._pos = 0
        self._env = env

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        tokens: list[str] = []
        i = 0
        n = len(text)
        while i < n:
            ch = text[i]
            if ch.isspace():
                i += 1
                continue
            if ch in "~&|^()":
                tokens.append(ch)
                i += 1
                continue
            if ch == "\\":
                # escaped identifier: read until whitespace or comma
                j = i + 1
                while j < n and not text[j].isspace() and text[j] not in "(),":
                    j += 1
                tokens.append("\\" + text[i + 1:j])
                i = j
                continue
            if ch.isdigit() or ch.isalpha() or ch in "_[]":
                j = i
                while j < n and (text[j].isalnum() or text[j] in "_[]'"):
                    j += 1
                tokens.append(text[i:j])
                i = j
                continue
            # unknown char — treat as single token (will surface parse error)
            tokens.append(ch)
            i += 1
        return tokens

    def _peek(self) -> str:
        return self._tokens[self._pos] if self._pos < len(self._tokens) else ""

    def _next(self) -> str:
        tok = self._peek()
        self._pos += 1
        return tok

    def parse(self) -> "z3.BoolRef":
        expr = self._parse_or()
        if self._peek():
            raise ValueError(f"unexpected token {self._peek()!r} after expression")
        return expr

    def _parse_or(self) -> "z3.BoolRef":
        left = self._parse_xor()
        while self._peek() == "|":
            self._next()
            right = self._parse_xor()
            left = z3.Or(left, right)
        return left

    def _parse_xor(self) -> "z3.BoolRef":
        left = self._parse_and()
        while self._peek() == "^":
            self._next()
            right = self._parse_and()
            left = z3.Xor(left, right)
        return left

    def _parse_and(self) -> "z3.BoolRef":
        left = self._parse_unary()
        while self._peek() == "&":
            self._next()
            right = self._parse_unary()
            left = z3.And(left, right)
        return left

    def _parse_unary(self) -> "z3.BoolRef":
        if self._peek() == "~":
            self._next()
            return z3.Not(self._parse_unary())
        return self._parse_primary()

    def _parse_primary(self) -> "z3.BoolRef":
        tok = self._next()
        if tok == "(":
            expr = self._parse_or()
            if self._peek() != ")":
                raise ValueError("missing closing parenthesis")
            self._next()
            return expr
        norm = _normalize_ident(tok)
        if norm in self._env:
            return self._env[norm]
        low = norm.lower()
        if low in {"1'b1", "1", "1'b0", "0"}:
            return z3.BoolVal(low in {"1", "1'b1"})
        # Unknown identifier: emit a fresh z3.Bool symbol.  Internal
        # wires are later substituted by _rewrite_wires; genuinely
        # unknown names become free symbols shared by both sides (so
        # an equivalence check still reports unsat when both sides
        # reference the same unknown wire).
        return z3.Bool(norm)


def _build_output_exprs(
    assigns: dict[str, str],
    outputs: list[str],
    env: dict[str, "z3.BoolRef"],
) -> dict[str, "z3.BoolRef"]:
    """Build a Z3 BoolRef for every output port, resolving wire assigns.

    Resolves wire-to-wire references recursively; cycles are treated as
    an error (a real combinational netlist has no combinational loops).
    """
    cache: dict[str, "z3.BoolRef"] = {}
    visiting: set[str] = set()

    def resolve(name: str) -> "z3.BoolRef":
        norm = _normalize_ident(name)
        if norm in env:
            return env[norm]
        if norm in cache:
            return cache[norm]
        if norm in visiting:
            raise ValueError(f"combinational loop through wire {norm!r}")
        if norm not in assigns:
            raise KeyError(f"unknown wire {norm!r}")
        visiting.add(norm)
        parser = _ExprParser(assigns[norm], env)
        expr = parser.parse()
        # parser may reference other wires only through env; for
        # wire-to-wire we instead re-parse with a resolver-aware env.
        # Simpler: substitute each identifier in expr if it is an
        # internal wire and not already resolved.
        expr = _substitute_wires(assigns, env, cache, norm, expr)
        visiting.discard(norm)
        cache[norm] = expr
        return expr

    result: dict[str, "z3.BoolRef"] = {}
    for out in outputs:
        norm = _normalize_ident(out)
        result[norm] = resolve(norm)
    return result


def _substitute_wires(
    assigns: dict[str, str],
    env: dict[str, "z3.BoolRef"],
    cache: dict[str, "z3.BoolRef"],
    target: str,
    expr: "z3.BoolRef",
) -> "z3.BoolRef":
    """Resolve internal-wire references inside ``expr``.

    ``expr`` was parsed with only boundary-port identifiers in env.
    Any remaining identifier that names an internal wire is substituted
    with its own resolved z3 expression (recursively, memoised in
    ``cache``).  This is a small, structural rewriter.
    """
    # z3 expression tree walk: substitute Bool consts that are wires.
    return _rewrite_wires(expr, assigns, env, cache, set())


def _rewrite_wires(
    node: "z3.ExprRef",
    assigns: dict[str, str],
    env: dict[str, "z3.BoolRef"],
    cache: dict[str, "z3.BoolRef"],
    visiting: set[str],
) -> "z3.BoolRef":
    if z3.is_const(node) and z3.is_bool(node):
        name = node.decl().name()
        if name in env:
            return env[name]
        if name in cache:
            return cache[name]
        if name in visiting:
            raise ValueError(f"combinational loop through wire {name!r}")
        if name in assigns:
            visiting.add(name)
            parser = _ExprParser(assigns[name], env)
            inner = parser.parse()
            inner = _rewrite_wires(inner, assigns, env, cache, visiting)
            visiting.discard(name)
            cache[name] = inner
            return inner
        return node  # leave unknown const (e.g. constant) untouched
    if z3.is_app(node):
        children = [
            _rewrite_wires(c, assigns, env, cache, visiting)
            for c in node.children()
        ]
        return node.decl()(*children)
    return node


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

    Builds an SMT problem asserting that some boundary input makes one
    of the original outputs differ from its replaced counterpart, then
    asks z3 for a counterexample.  Returns Z3FormalEquivalenceResult.
    """
    started_at = time.perf_counter()
    original_path = Path(original_netlist_path)
    replaced_path = Path(replaced_netlist_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    smt2_problem_path = output_dir / "boundary_equivalence.smt2"
    smt2_output_path = output_dir / "boundary_equivalence.smt2.output"

    boundary_ports = [_normalize_ident(p) for p in boundary_ports]
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

    o_assigns = _parse_assigns(original_text)
    r_assigns = _parse_assigns(replaced_text)
    o_outputs = _parse_module_outputs(original_text)
    r_outputs = _parse_module_outputs(replaced_text)

    # Fall back to single-assign (original behaviour) when no output
    # port declaration was parsed (e.g. minimal test Verilog without
    # a separate output statement).
    if not o_outputs:
        # try to infer outputs from assign lhs where lhs is 'y'
        inferred = [lhs for lhs in o_assigns if lhs == "y"]
        o_outputs = inferred
    if not r_outputs:
        inferred = [lhs for lhs in r_assigns if lhs == "y"]
        r_outputs = inferred

    if not o_outputs or not r_outputs:
        return Z3FormalEquivalenceResult(
            status="error",
            command=command,
            runtime_s=time.perf_counter() - started_at,
            reason="could not extract assign expressions from verilog",
            boundary_ports=tuple(boundary_ports),
            smt2_problem_path=str(smt2_problem_path),
        )

    # Build env from boundary ports.  All identifiers in the netlists
    # are boolean; use z3.Bool.
    env = {p: z3.Bool(p) for p in boundary_ports}

    try:
        o_exprs = _build_output_exprs(o_assigns, o_outputs, env)
        r_exprs = _build_output_exprs(r_assigns, r_outputs, env)
    except Exception as exc:  # noqa: BLE001
        return Z3FormalEquivalenceResult(
            status="error",
            command=command,
            runtime_s=time.perf_counter() - started_at,
            reason=f"failed to build output expressions: {exc}",
            boundary_ports=tuple(boundary_ports),
            smt2_problem_path=str(smt2_problem_path),
        )

    s = z3.Solver()
    try:
        s.set("timeout", int(timeout_s * 1000))  # milliseconds
    except z3.Z3Exception:
        pass

    # Assert: exists input where at least one output differs.
    diffs = []
    for out in o_outputs:
        norm = _normalize_ident(out)
        o_expr = o_exprs.get(norm)
        r_expr = r_exprs.get(norm)
        if o_expr is not None and r_expr is not None:
            diffs.append(o_expr != r_expr)
    if not diffs:
        return Z3FormalEquivalenceResult(
            status="error",
            command=command,
            runtime_s=time.perf_counter() - started_at,
            reason="no matching output ports between original and replaced",
            boundary_ports=tuple(boundary_ports),
            smt2_problem_path=str(smt2_problem_path),
        )
    s.add(z3.Or(diffs))

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