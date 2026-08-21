"""Real OpenSTA WNS evaluator bridging the outer refinement loop to timing.

N31-05 failure-aware hybrid repair, real-STA leg.  The outer loop
(flow.run_multi_iteration_case) produces cut-based patch candidates over the
analysis netlist; ``RealWnsEvaluator`` turns one candidate into a real,
measured repair:

  1. map the cut gates (analysis netlist instance names) onto the real
     SKY130 mapped netlist;
  2. for each actionable instance generate strategy candidates
     R (functionally-equivalent lower-delay cell), G (larger drive size)
     and optionally B (buffer insertion on a fanout pin);
  3. evaluate every candidate with real OpenSTA (pre-layout, ideal nets);
  4. accept only candidates that strictly improve the baseline WNS.

This is the failure-aware core of the hybrid repair: candidates that hurt
timing (e.g. over-sized G cells in the ideal-net regime) are measured and
rejected instead of assumed good.  The evaluator is pure with respect to
the input netlist text (every candidate is derived from the same baseline),
so candidate STA runs are independent and can be parallelized.
"""

from __future__ import annotations

import json
import re
import hashlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .buffer_insertion import buffer_candidates, build_net_fanout, insert_buffer
from .gate_sizing import (
    apply_sizing,
    build_available_sizes,
    larger_size_candidates,
    parse_mapped_netlist,
)
from .logic_rewrite import apply_rewrite, equivalence_candidates, parse_liberty_cells, canonical_function
from .opensta import run_opensta_sequential
from .proxy_ranking import ProxyWeights, rank_real_candidates
from .strategy_selector import exploration_order
from .failures import AcceptanceEvidence
from .yosys_abc import YosysAbcEquivalenceResult
from .replacement import (
    extract_combinational_window, generate_topology_replacement,
    stitch_topology_replacement, check_local_functional_equivalence,
    parse_verilog_netlist_from_text,
)
import itertools
import hashlib
import time
import threading
from collections import Counter


#: report_checks line: ``   0.36    0.69 v _079_/X (sky130_fd_sc_hd__or3_1)``
_INSTANCE_LINE_RE = re.compile(
    r"^\s+\d+\.\d+\s+\d+\.\d+\s+[v^]\s+(\w+)/\w+\s+\((sky130_fd_sc_hd__\w+)\)",
    re.M,
)
_ENDPOINT_RE = re.compile(r"^Endpoint:\s+([\w\\]+)", re.M)


def _checker_passed(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, dict):
        return value.get("status") == "pass"
    return getattr(value, "status", None) == "pass"


def _checker_details(value) -> dict:
    """Preserve structured checker status/method/reason in failure evidence."""
    if isinstance(value, dict):
        status = value.get("status")
        method = value.get("method")
        reason = value.get("reason")
    else:
        status = getattr(value, "status", None)
        method = getattr(value, "method", None)
        reason = getattr(value, "reason", None)
    details = {"status": status, "method": method, "reason": reason}
    if isinstance(reason, str):
        try:
            parsed = json.loads(reason)
        except (TypeError, ValueError):
            parsed = None
        if isinstance(parsed, dict):
            details.update(parsed)
    return {key: value for key, value in details.items() if value is not None}


def _physical_sta_provenance(output_dir: str | Path, metrics: dict | None,
                             rc_config: dict, rc_config_hash: str) -> dict:
    directory = Path(output_dir)
    report = directory / "sta.log"
    text = report.read_text(encoding="utf-8", errors="replace") if report.exists() else ""
    path = parse_critical_instances(text) if text else []
    endpoint = parse_worst_endpoint(text) if text else None
    return {
        "tool": "OpenSTA",
        "status": (metrics or {}).get("status", "unknown"),
        "report_path": str(report),
        "output_dir": str(directory),
        "config": dict(rc_config),
        "rc_config_hash": rc_config_hash,
        "wns": (metrics or {}).get("wns"),
        "tns": (metrics or {}).get("tns"),
        "hold_min_slack": (metrics or {}).get("min_slack"),
        "endpoint": endpoint,
        "path": path,
    }


def _normalise_failure_events(events, *, candidate_hash: str, cut_hash: str | None = None):
    """Return the canonical, auditable representation used by trials/state.

    Evaluator backends historically returned small ad-hoc dictionaries.  The
    outer loop may still accept those adapters, but production records must
    have a non-empty candidate/cut identity and a stable event id so a trial
    cannot be counted twice or silently lose checker evidence.
    """
    normalized = []
    for raw in events or []:
        event = dict(raw)
        event["candidate_hash"] = event.get("candidate_hash") or candidate_hash
        event["cut_hash"] = event.get("cut_hash") or cut_hash or event["candidate_hash"]
        event.setdefault("endpoint", None)
        event.setdefault("path", [])
        event.setdefault("net", None)
        event.setdefault("action_scope", [])
        event.setdefault("threshold", None)
        event.setdefault("observed_value", None)
        event.setdefault("severity", "hard")
        event.setdefault("runtime_s", 0.0)
        event.setdefault("evidence", {})
        if not event.get("event_id"):
            event["event_id"] = hashlib.sha256(json.dumps({
                key: event.get(key) for key in (
                    "type", "candidate_hash", "cut_hash", "endpoint", "path",
                    "net", "action_scope", "threshold", "observed_value", "evidence",
                )
            }, sort_keys=True, default=str).encode("utf-8")).hexdigest()
        normalized.append(event)
    return normalized


def build_real_equivalence_checker(liberty_text: str):
    """Build a per-candidate Liberty-function checker for R/G/B actions.

    R candidates are checked by canonical Liberty Boolean functions, G keeps
    the same function family, and B permits only added buffer/identity cells.
    Unknown cells or malformed netlists fail closed with a structured result.
    """
    lib = parse_liberty_cells(liberty_text)

    def check(original_text: str, candidate_text: str):
        from .equivalence import EquivalenceResult
        try:
            before = parse_mapped_netlist(original_text)
            after = parse_mapped_netlist(candidate_text)
            old = {c.instance: c for c in before}
            new = {c.instance: c for c in after}
            if not set(old).issubset(new):
                return EquivalenceResult("fail", "liberty_local_function", "an existing instance disappeared")
            added = set(new) - set(old)
            buffer_edges: dict[str, set[str]] = {}
            for inst in added:
                cell = lib.get(new[inst].cell_type)
                if cell is None or cell.family not in {"buf", "bufbuf", "clkbuf"}:
                    return EquivalenceResult("fail", "liberty_local_function", f"added non-buffer cell at {inst}")
                pins = new[inst].pins
                input_net = pins.get("A") or pins.get("I")
                output_net = pins.get(cell.output_pin) or pins.get("X") or pins.get("Y")
                if input_net and output_net:
                    buffer_edges.setdefault(input_net, set()).add(output_net)

            def connected_through_buffers(source_net: str, target_net: str) -> bool:
                if source_net == target_net:
                    return True
                pending = [source_net]
                seen = {source_net}
                while pending:
                    current = pending.pop()
                    for successor in buffer_edges.get(current, ()):
                        if successor == target_net:
                            return True
                        if successor not in seen:
                            seen.add(successor)
                            pending.append(successor)
                return False

            for inst, source in old.items():
                target = new[inst]
                if source.cell_type == target.cell_type and source.pins != target.pins:
                    if any(not connected_through_buffers(source.pins.get(pin, ""), target.pins.get(pin, ""))
                           for pin in set(source.pins) | set(target.pins)):
                        return EquivalenceResult(
                            "fail", "liberty_local_function",
                            f"pin-to-net connection changed at {inst}: {source.pins} -> {target.pins}",
                        )
                if source.cell_type == target.cell_type:
                    continue
                src_lib, dst_lib = lib.get(source.cell_type), lib.get(target.cell_type)
                if src_lib is None or dst_lib is None or not src_lib.function or not dst_lib.function:
                    return EquivalenceResult("fail", "liberty_local_function", f"unknown/non-combinational cell at {inst}")
                if canonical_function(src_lib.function) != canonical_function(dst_lib.function):
                    return EquivalenceResult("fail", "liberty_local_function", f"Boolean function changed at {inst}")
                src_output = src_lib.output_pin
                dst_output = dst_lib.output_pin
                if src_output and dst_output and source.pins.get(src_output) != target.pins.get(dst_output):
                    return EquivalenceResult("fail", "liberty_local_function", f"output net changed at {inst}")
                if Counter(source.pins.values()) != Counter(target.pins.values()):
                    return EquivalenceResult("fail", "liberty_local_function", f"pin-to-net multiset changed at {inst}")
            for inst in added:
                cell = lib.get(new[inst].cell_type)
                if cell is None or cell.family not in {"buf", "bufbuf", "clkbuf"}:
                    return EquivalenceResult("fail", "liberty_local_function", f"added non-buffer cell at {inst}")
        except Exception as exc:
            return EquivalenceResult("fail", "liberty_local_function", f"checker failed closed: {exc}")
        return EquivalenceResult("pass", "liberty_local_function", "Liberty functions preserved")

    return check


def build_full_netlist_sec_checker(
    *,
    top_module: str,
    liberty_text: str | None = None,
    liberty_cells_v: str | Path | None = None,
    artifact_dir: str | Path,
    yosys_command: str = "wsl.exe -e yosys",
    abc_command: str = "wsl.exe -e yosys-abc",
    timeout_s: float = 60.0,
):
    """Build the production text-in/text-out full-netlist SEC backend.

    The callback owns temporary Verilog checkpoints and delegates normalization
    plus ABC CEC to the existing Yosys/ABC backend.  Tool unavailability,
    malformed text, and timeout are returned as structured non-pass results so
    strict topology callers fail closed without substituting the local checker.
    """
    from .equivalence import EquivalenceResult
    from .yosys_abc import check_yosys_abc_equivalence

    artifact_root = Path(artifact_dir)
    artifact_root.mkdir(parents=True, exist_ok=True)

    def check(original_text: str, candidate_text: str):
        try:
            outputs = list(parse_verilog_netlist_from_text(original_text).outputs)
        except Exception as exc:
            return EquivalenceResult(
                "fail", "full_netlist_sec", f"SEC input parse failed closed: {exc}"
            )
        digest = hashlib.sha256((top_module + "\0" + original_text + "\0" + candidate_text).encode()).hexdigest()[:16]
        trial_dir = artifact_root / f"trial-{digest}"
        trial_dir.mkdir(parents=True, exist_ok=True)
        original = trial_dir / f"{top_module}.gold.v"
        revised = trial_dir / f"{top_module}.gate.v"
        original.write_text(original_text, encoding="utf-8")
        revised.write_text(candidate_text, encoding="utf-8")
        cells_path = trial_dir / "cells.v"
        if liberty_text is not None:
            used_cells = set(re.findall(
                r"\b(sky130_fd_sc_hd__\w+)\s+\w+\s*\(",
                original_text + "\n" + candidate_text,
            ))
            try:
                write_liberty_cell_models(liberty_text, cells_path, used_cells=used_cells)
            except ValueError as exc:
                return YosysAbcEquivalenceResult(
                    status="fail", method="yosys_liberty_model_generation",
                    tool="Liberty-to-Verilog", command="materialize_cells_v",
                    outputs=list(outputs), runtime_s=0.0,
                    reason=str(exc),
                )
        elif liberty_cells_v is not None:
            cells_path = Path(liberty_cells_v)
        else:
            cells_path = None
        result = check_yosys_abc_equivalence(
            original, revised, outputs=outputs,
            artifact_dir=trial_dir / "yosys-abc",
            yosys_command=yosys_command,
            abc_command=abc_command,
            timeout_s=timeout_s,
            liberty_cells_v=cells_path,
            top_module=top_module,
        )
        return result

    return check


def write_liberty_cell_models(liberty_text: str, output_path: str | Path,
                              *, used_cells: set[str] | None = None) -> Path:
    """Materialize a deterministic, synthesizable Verilog model from Liberty."""
    cells = parse_liberty_cells(liberty_text)
    selected = sorted(used_cells if used_cells is not None else cells)
    missing = sorted(set(selected) - set(cells))
    if missing:
        raise ValueError("Liberty missing instantiated cells: " + ", ".join(missing))
    blocks: list[str] = ["// Generated from Liberty for symmetric Yosys/ABC SEC.\n"]
    for name in selected:
        cell = cells[name]
        output_pins = list(cell.output_functions) or ([cell.output_pin] if cell.output_pin else [])
        ports = list(dict.fromkeys([*cell.input_pins, *output_pins]))
        if not ports:
            continue
        lines = [f"module {name} ({', '.join(ports)});"]
        if cell.input_pins:
            lines.append("  input " + ", ".join(cell.input_pins) + ";")
        if output_pins:
            lines.append("  output " + ", ".join(output_pins) + ";")
        if cell.sequential_kind == "ff":
            if not (cell.next_state and cell.output_pin and cell.clocked_on):
                raise ValueError(f"unsupported sequential semantics for instantiated cell {name}")
            state = cell.state_var or cell.output_pin
            sequential_outputs = cell.output_functions or {cell.output_pin: state}
            edge = "negedge" if cell.clocked_on.startswith("!") else "posedge"
            clock = cell.clocked_on.lstrip("!").strip()
            lines.extend([
                "  reg " + state + ";",
                f"  always @({edge} {clock}) {state} <= {cell.next_state};",
            ])
            for pin, function in sequential_outputs.items():
                if function == state:
                    lines.append(f"  assign {pin} = {state};")
                elif cell.state_inv_var and function == cell.state_inv_var:
                    lines.append(f"  assign {pin} = ~{state};")
                else:
                    raise ValueError(f"unsupported sequential output mapping for {name}.{pin}: {function}")
        elif cell.sequential_kind == "latch":
            if not (cell.next_state and cell.output_pin and cell.latch_enable):
                raise ValueError(f"unsupported sequential semantics for instantiated cell {name}")
            state = cell.state_var or cell.output_pin
            lines.extend([
                "  reg " + state + ";",
                f"  always @* if ({cell.latch_enable}) {state} <= {cell.next_state};",
            ])
            for pin, function in cell.output_functions.items():
                if function == state:
                    lines.append(f"  assign {pin} = {state};")
                elif cell.state_inv_var and function == cell.state_inv_var:
                    lines.append(f"  assign {pin} = ~{state};")
                else:
                    raise ValueError(f"unsupported latch output mapping for {name}.{pin}: {function}")
        elif cell.function and cell.output_pin:
            expr = (cell.function.replace("*", "&").replace("+", "|"))
            lines.append(f"  assign {cell.output_pin} = {expr};")
        elif not cell.function:
            raise ValueError(f"unsupported sequential semantics for instantiated cell {name}")
        lines.append("endmodule\n")
        blocks.append("\n".join(lines))
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(blocks), encoding="utf-8")
    return path


def build_boundary_closure_checker():
    """Build a real module-boundary checker used as the strict F2 gate."""
    def _net_closure(netlist):
        constants = {"0", "1", "1'b0", "1'b1", "1'h0", "1'h1", "$false", "$true", "$undef"}
        drivers = Counter(netlist.resolve_alias(g.output) for g in netlist.gates)
        declared = set(netlist.inputs) | set(netlist.outputs) | set(netlist.wires)
        # Module-output loss/rewiring is the more specific boundary defect;
        # classify it before generic consumed-net/dangling checks.
        for output in netlist.outputs:
            resolved_output = netlist.resolve_alias(output)
            if drivers.get(resolved_output, 0) != 1:
                return {"kind": "rewired-module-output", "net": resolved_output,
                        "drivers": drivers.get(resolved_output, 0)}
        consumed = [net for gate in netlist.gates for net in gate.inputs]
        for net in consumed:
            resolved = netlist.resolve_alias(net)
            if resolved in constants:
                continue
            if resolved not in declared:
                return {"kind": "undeclared-consumed", "net": resolved}
            if resolved in netlist.inputs:
                continue
            if drivers.get(resolved, 0) == 0:
                return {"kind": "declared-undriven", "net": resolved}
            if drivers.get(resolved, 0) != 1:
                return {"kind": "multiple-driver", "net": resolved,
                        "drivers": drivers.get(resolved, 0)}
        consumers = {netlist.resolve_alias(net)
                     for gate in netlist.gates for net in gate.inputs}
        for gate in netlist.gates:
            output = netlist.resolve_alias(gate.output)
            if output in netlist.outputs or output in constants:
                continue
            if output not in consumers:
                return {"kind": "dangling-output", "net": output}
        return None

    def check(original_text: str, candidate_text: str):
        from .equivalence import EquivalenceResult
        pattern = re.compile(r"\bmodule\s+(\w+)\s*\((.*?)\)\s*;", re.S)
        left, right = pattern.search(original_text), pattern.search(candidate_text)
        if left is None or right is None:
            return EquivalenceResult("fail", "boundary_closure", "module header unavailable")
        left_ports = tuple(p.strip() for p in left.group(2).replace("\n", " ").split(",") if p.strip())
        right_ports = tuple(p.strip() for p in right.group(2).replace("\n", " ").split(",") if p.strip())
        if left.group(1) != right.group(1) or left_ports != right_ports:
            return EquivalenceResult("fail", "boundary_closure", "module boundary changed")
        try:
            before = parse_verilog_netlist_from_text(original_text)
            after = parse_verilog_netlist_from_text(candidate_text)
            if before.inputs != after.inputs or before.outputs != after.outputs:
                return EquivalenceResult("fail", "boundary_closure", "boundary input/output set changed")
            for label, netlist in (("baseline", before), ("candidate", after)):
                issue = _net_closure(netlist)
                if issue is not None:
                    return EquivalenceResult(
                        "fail", "boundary_closure",
                        json.dumps({"stage": "consumed_net_closure", "side": label, **issue}, sort_keys=True),
                    )
                drivers = Counter(netlist.resolve_alias(g.output) for g in netlist.gates)
                if any(drivers[input_name] for input_name in netlist.inputs):
                    return EquivalenceResult("fail", "boundary_closure",
                                             f"{label} input is driven")
        except Exception as exc:
            return EquivalenceResult("fail", "boundary_closure", f"boundary parse failed closed: {exc}")
        return EquivalenceResult("pass", "boundary_closure", "boundary inputs/outputs and driver closure preserved")
    return check


def parse_critical_instances(sta_text: str) -> list[str]:
    """Instance names on the worst timing path, in path order (deduped)."""
    insts: list[str] = []
    for m in _INSTANCE_LINE_RE.finditer(sta_text):
        inst = m.group(1)
        if "/" in inst:
            continue
        if inst not in insts:
            insts.append(inst)
    return insts


def parse_worst_endpoint(sta_text: str) -> str | None:
    """Endpoint DFF instance name (e.g. ``DFF_11`` from ``DFF_11/_0_``)."""
    m = _ENDPOINT_RE.search(sta_text)
    return (m.group(1).split("/")[0].strip("\\")) if m else None


def dff_d_input_net(mapped_text: str, dff_instance: str) -> str | None:
    """Net connected to ``.D`` of a named-port ``dff`` instance."""
    pat = re.compile(
        r"\b(?:dff|sky130_fd_sc_hd__\w+)\s+" + re.escape(dff_instance) + r"\s*\((.*?)\)\s*;", re.S
    )
    m = pat.search(mapped_text)
    if not m:
        return None
    for pin, net in re.findall(r"\.(\w+)\(\s*([^)]+?)\s*\)", m.group(1)):
        if pin == "D":
            return net.strip().strip("\\")
    return None


def build_r_available(
    liberty_text: str,
    instances: list[str],
    mapped_text: str,
) -> set[str]:
    """Return the subset of ``instances`` whose cell type has at least one
    logic-rewrite (R) equivalence candidate in the Liberty library.

    This is the hard-equivalence input to the joint bi-objective cut: gates
    without an R candidate get no critical discount and are skipped by the
    critical-path cover (review shortboard: merge F1/F4).  Uses the same
    candidate rule as ``RealWnsEvaluator._r_candidates`` (R requires a
    different-family equivalent cell in the library).
    """
    lib = parse_liberty_cells(liberty_text)
    cells = parse_mapped_netlist(mapped_text)
    by_inst = {c.instance: c for c in cells}
    r_ok: set[str] = set()
    for inst in instances:
        cell = by_inst.get(inst)
        if cell is None:
            continue
        ctype = cell.cell_type
        c = lib.get(ctype)
        if not c:
            continue
        has_r = any(
            lib.get(t) is not None and lib[t].family != c.family
            for t, _pm in equivalence_candidates(c, lib)
        )
        if has_r:
            r_ok.add(inst)
    return r_ok


def strip_to_single_module(verilog_text: str, top_module: str) -> str:
    """Keep only the ``top_module`` body from a multi-module netlist.

    Yosys writes the flop model as a separate ``module dff ...`` before the
    circuit module; the FAECO analysis parser takes the *first* module, so
    the flop model must be removed before building the case netlist.
    """
    pat = re.compile(
        r"\bmodule\s+" + re.escape(top_module) + r"\s*\((.*?)\)\s*;",
        re.S,
    )
    m = pat.search(verilog_text)
    if not m:
        return verilog_text
    start = m.start()
    module_header = m.group(0)
    rest = verilog_text[m.end():]
    # module body ends at the matching endmodule (last one in the file)
    end = rest.rfind("endmodule")
    if end == -1:
        return verilog_text
    body = rest[:end].rstrip()
    # drop any earlier module definitions (e.g. the ``module dff`` flop
    # model); keep only the leading comment block.
    prefix = verilog_text[:start]
    module_at = prefix.find("module")
    header = (prefix[:module_at] if module_at != -1 else prefix).rstrip() + "\n"
    return header + module_header + "\n" + body + "\nendmodule\n"


class RealWnsEvaluator:
    """Measure a patch candidate with real OpenSTA and report WNS.

    The evaluator is passed to ``run_multi_iteration_case(wns_evaluator=...)``
    and called as ``(patch, weights)``; it returns a dict with ``wns`` and
    ``improved`` (strict improvement over the baseline WNS).
    """

    def __init__(
        self,
        *,
        mapped_text: str,
        top_module: str,
        period: float,
        liberty_text: str,
        baseline_wns: float,
        baseline_tns: float | None = None,
        output_dir: str | Path,
        critical_instances: list[str] | None = None,
        workers: int = 4,
        enable_buffer: bool = False,
        buf_types: tuple[str, ...] = (
            "sky130_fd_sc_hd__buf_1",
            "sky130_fd_sc_hd__buf_2",
        ),
        tns_aware: bool = False,
        max_instances: int = 8,
        priority_table: dict | None = None,
        proxy_ranking: bool = False,
        proxy_weights: ProxyWeights | None = None,
        adaptive: bool = False,
        hold_mode: bool = False,
        baseline_min_slack: float | None = None,
        hold_uncertainty: float = 0.8,
        early_stop: bool = False,
        joint_k: int = 0,
        joint_mix: bool = False,
        joint_enumerate_depth: int = 0,
        strategy_filter: tuple[str, ...] = ("R", "G", "B"),
        init_boundary_penalty: float = 1.0,
        init_size_penalty: float = 1.0,
        init_critical_coverage_reward: float = 1.0,
        clock_port: str = "CK",
        physical_gate: bool = False,
        min_physical_gain_ns: float = 0.010,
        physical_fanout_penalty: float = 1.0,
        physical_depth_penalty: float = 1.0,
        physical_unit_len_um: float = 40.0,
         equivalence_checker=None,
         topology_sec_checker=None,
         boundary_checker=None,
        strict_gates: bool = False,
        max_patch_ratio: float = 0.15,
        max_verification_time_s: float = 60.0,
        epsilon: float = 0.0,
        strict_budgets: bool = False,
        area_budget: float | None = None,
        max_transition_budget: float | None = None,
        max_capacitance_budget: float | None = None,
        max_fanout_budget: float | None = None,
         required_metrics: tuple[str, ...] | list[str] = ("setup_wns", "setup_tns"),
         available_metrics: tuple[str, ...] | list[str] = ("setup_wns", "setup_tns", "hold_min_slack"),
         metric_epsilons: dict[str, float] | None = None,
        allow_singleton: bool = False,
        enable_topology: bool = True,
    ) -> None:
        self.mapped_text = mapped_text
        self.top_module = top_module
        self.period = period
        self.lib = parse_liberty_cells(liberty_text)
        self.liberty_text = liberty_text
        self.available = build_available_sizes(liberty_text)
        self.baseline_wns = baseline_wns
        self.baseline_tns: float | None = baseline_tns
        self.hold_mode = bool(hold_mode)
        self.baseline_min_slack = baseline_min_slack
        self.hold_uncertainty = hold_uncertainty
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.critical_instances = list(critical_instances or [])
        self.workers = max(1, workers)
        self.enable_buffer = enable_buffer
        self.buf_types = buf_types
        self.tns_aware = tns_aware
        self.max_instances = max_instances
        self.priority_table = priority_table or {}
        self.proxy_ranking = bool(proxy_ranking)
        self.proxy_weights = proxy_weights or ProxyWeights()
        self.adaptive = bool(adaptive)
        if self.adaptive:
            from .adaptive_selector import AdaptiveStrategySelector
            self.adaptive_sel = AdaptiveStrategySelector()
        else:
            self.adaptive_sel = None
        self.early_stop = early_stop
        self.joint_k = max(0, joint_k)
        self.joint_mix = bool(joint_mix)
        self.joint_enumerate_depth = max(0, joint_enumerate_depth)
        self.strategy_filter = tuple(strategy_filter or ("R", "G", "B"))
        self.init_weights = {
            "boundary_penalty": float(init_boundary_penalty),
            "size_penalty": float(init_size_penalty),
            "critical_coverage_reward": float(init_critical_coverage_reward),
        }
        self.clock_port = clock_port
        self.physical_gate = bool(physical_gate)
        self.min_physical_gain_ns = min_physical_gain_ns
        self.physical_fanout_penalty = physical_fanout_penalty
        self.physical_depth_penalty = physical_depth_penalty
        self.physical_unit_len_um = physical_unit_len_um
        self.equivalence_checker = equivalence_checker
        self.topology_sec_checker = topology_sec_checker
        self.boundary_checker = boundary_checker
        self.strict_gates = bool(strict_gates)
        self.use_constrained_cuts = True
        self.refresh_cone = True
        self.max_patch_ratio = float(max_patch_ratio)
        self.max_verification_time_s = float(max_verification_time_s)
        self.epsilon = float(epsilon)
        self.metric_epsilons = {
            "patch_ratio": 0.0, "area": 0.0, "max_transition": 0.0,
            "max_capacitance": 0.0, "max_fanout": 0.0,
            **{str(k): float(v) for k, v in (metric_epsilons or {}).items()},
        }
        self.strict_budgets = bool(strict_budgets)
        self.area_budget = area_budget
        self.max_transition_budget = max_transition_budget
        self.max_capacitance_budget = max_capacitance_budget
        self.max_fanout_budget = max_fanout_budget
        required = set(str(metric) for metric in required_metrics)
        budget_metric = {
            "area_budget": "area", "max_transition_budget": "max_transition",
            "max_capacitance_budget": "max_capacitance", "max_fanout_budget": "max_fanout",
        }
        for option, metric in budget_metric.items():
            if getattr(self, option) is not None:
                required.add(metric)
        if self.hold_mode:
            required.add("hold_min_slack")
        self.hold_required = self.hold_mode or "hold_min_slack" in required
        self.required_metrics = tuple(sorted(required))
        self.available_metrics = frozenset(str(metric) for metric in available_metrics)
        self.allow_singleton = bool(allow_singleton)
        self.enable_topology = bool(enable_topology)
        self.trials: list[dict] = []
        self.call_log: list[dict] = []
        self._call_counter = 0
        self._physical_baseline_cache: dict[str, dict] = {}
        self._physical_baseline_lock = threading.Lock()
        self.tested_candidate_hashes: set[str] = set()
        self._sta_cache: dict[str, dict] = {}
        self._active_state = None

    def _metric_epsilon(self, metric: str) -> float:
        """Return a unit-specific non-timing tolerance."""
        return self.metric_epsilons.get(metric, 0.0)

    def _deadline_or_budget_event(self, state, kind: str, *, candidate_hash: str,
                                  cut_hash: str, action_scope: list[str]):
        """Reserve one tool call, fail closed before invocation."""
        if state is None:
            return None
        if state.deadline_expired():
            return {
                "type": "deadline_exhausted", "candidate_hash": candidate_hash,
                "cut_hash": cut_hash, "severity": "hard", "hard_gate": True,
                "action_scope": action_scope, "threshold": state.budget.get("wall_timeout_s"),
                "observed_value": "deadline", "runtime_s": 0.0,
                "evidence": {"stage": kind, "budget": "wall_timeout"},
            }
        if not state.reserve_budget(kind):
            return {
                "type": f"{kind}_budget_exhausted", "candidate_hash": candidate_hash,
                "cut_hash": cut_hash, "severity": "hard", "hard_gate": True,
                "action_scope": action_scope, "threshold": state.budget.get(f"{kind}_budget"),
                "observed_value": state.budget_used(kind), "runtime_s": 0.0,
                "evidence": {"stage": kind, "budget": kind, "reason": "reserved before tool"},
            }
        return None

    @staticmethod
    def _remaining_tool_timeout(state, default: float = 180.0) -> float:
        deadline = state.budget.get("_deadline_monotonic") if state is not None else None
        if deadline is None:
            return default
        return max(0.001, min(default, float(deadline) - time.perf_counter()))

    def _strategy_order(self, cell_type: str) -> tuple[str, ...]:
        if self.adaptive:
            return tuple(self.adaptive_sel.priority_order(cell_type))
        return tuple(self.priority_table.get(cell_type, ("R", "G", "B")))

    def accept_candidate(self, result: dict, *, state=None) -> None:
        """Commit an accepted candidate as the next STA baseline.

        The outer loop calls this only after :class:`SearchState` has recorded
        the candidate.  Consequently every subsequent candidate is generated
        from the committed ``G_r`` rather than the original netlist.
        """
        text = result.get("candidate_netlist_text")
        if not text:
            raise ValueError("accepted candidate has no netlist text")
        self.mapped_text = str(text)
        if result.get("wns") is not None:
            self.baseline_wns = float(result["wns"])
        if "tns" in result:
            self.baseline_tns = (float(result["tns"])
                                 if result["tns"] is not None else None)
        if "min_slack" in result:
            self.baseline_min_slack = (float(result["min_slack"])
                                       if result["min_slack"] is not None else None)
        if result.get("critical_instances") is not None:
            self.critical_instances = list(result["critical_instances"])
        if state is not None:
            self.critical_instances = list(getattr(state, "critical_instances", self.critical_instances))

    def r_available_for(self, instances: list[str]) -> set[str]:
        """Recompute R-action availability against the current committed G_r."""
        return build_r_available(self.liberty_text, list(instances), self.mapped_text)

    # -- candidate construction -------------------------------------------

    def _r_candidates(self, cell_type: str) -> list[tuple[str, dict]]:
        cell = self.lib.get(cell_type)
        if not cell:
            return []
        return [
            (t, pm)
            for t, pm in equivalence_candidates(cell, self.lib)
            if self.lib.get(t) is not None and self.lib[t].family != cell.family
        ]

    def _candidates_for(self, cells, inst: str) -> list[tuple[str, dict, str]]:
        cell = next((c for c in cells if c.instance == inst), None)
        if cell is None:
            return []
        cands: list[tuple[str, dict, str]] = []
        for new_type, pin_map in self._r_candidates(cell.cell_type):
            cands.append((new_type, pin_map, "R"))
        for new_type in larger_size_candidates(cell.cell_type, self.available):
            cands.append((new_type, {}, "G"))
        if self.enable_buffer:
            fanout = build_net_fanout(cells)
            lc = self.lib.get(cell.cell_type)
            output_pins = {lc.output_pin} if lc else None
            for pin, net, buf_type, new_net in buffer_candidates(
                cells, inst, fanout, buf_types=self.buf_types, output_pins=output_pins
            ):
                cands.append(("buf:" + buf_type + ":" + pin + ":" + new_net, {}, "B"))
        # strategy ablation filter (pure-R / pure-G / pure-B): keep only
        # the requested strategy kinds so the outer loop can measure the
        # standalone contribution of each repair strategy.
        if self.strategy_filter:
            cands = [c for c in cands if c[2] in self.strategy_filter]
        # decision layer: reorder candidates by the per-cell-type strategy
        # priority table (fallback R,G,B); with --adaptive, use the online
        # UCB-based selector that updates from measured trials instead.
        order = self._strategy_order(cell.cell_type)
        rank = {k: i for i, k in enumerate(order)}
        cands.sort(key=lambda c: (rank.get(c[2], len(order)), c[0]))
        return exploration_order(cands)

    def _apply(self, text: str, inst: str, kind: str, new_type: str, pin_map: dict) -> str:
        if kind == "R":
            return apply_rewrite(text, inst, new_type, pin_map)
        if kind == "B":
            _, buf_type, bpin, new_net = new_type.split(":")
            return insert_buffer(text, inst, bpin, buf_type, new_net)
        return apply_sizing(text, {inst: new_type})

    def _apply_joint(self, text: str, change) -> str:
        """Apply several instance -> new-type replacements in one shot.

        ``change`` maps instance -> (new_type, pin_map, kind).  R uses the
        logic rewrite (renames pins), G uses gate sizing; applying them one
        instance at a time keeps the joint candidate a single STA-evaluated
        repair combination (joint action space).
        """
        out = text
        for inst, (new_type, pin_map, kind) in change.items():
            if kind == "R":
                out = apply_rewrite(out, inst, new_type, pin_map)
            else:
                out = apply_sizing(out, {inst: new_type})
        return out

    def _joint_enumerate_combos(self, cells, allowed_instances=None) -> list[tuple[dict, str]]:
        """Joint repair de-humanization (TCAD sprint): enumerate multi-gate
        upsize/rewrite combinations along the critical path.

        For ``joint_enumerate_depth > 0``, take a sliding window of
        ``joint_enumerate_depth`` consecutive critical-path instances and
        enumerate every subset of size >= 2 within the window (bounded to
        avoid an exponential blowup).  Each combination is applied as a
        single STA-evaluated JOINT candidate -- fully automated, no manual
        selection of which gates to upsize together.
        """
        if self.joint_enumerate_depth <= 0:
            return []
        # critical_instances are already in path order; keep only those with
        # a real cell and a candidate.
        by_inst = {c.instance: c for c in cells}
        allowed = set(allowed_instances) if allowed_instances is not None else None
        ordered = [i for i in self.critical_instances
                   if i in by_inst and (allowed is None or i in allowed)][: self.max_instances]
        if len(ordered) < 2:
            return []
        window = min(self.joint_enumerate_depth, len(ordered))
        combos: list[tuple[dict, str]] = []
        max_combos = 50  # TCAD sprint: bounded enumeration
        # sliding window: for each start index, enumerate subsets of size
        # 2..window over the window slice
        for start in range(len(ordered) - window + 1):
            win = ordered[start:start + window]
            for r in range(2, window + 1):
                for subset in itertools.combinations(win, r):
                    change: dict[str, tuple[str, dict, str]] = {}
                    for inst in subset:
                        cands = self._candidates_for(cells, inst)
                        # prefer R (logic rewrite) then G (sizing) -- do not
                        # put buffer insertion inside a joint candidate
                        chosen = next((c for c in cands if c[2] == "R"),
                                      next((c for c in cands if c[2] == "G"), None))
                        if chosen is None:
                            break
                        change[inst] = (chosen[0], chosen[1], chosen[2])
                    if len(change) >= 2:
                        label = ",".join(f"{i}:{c[0]}" for i, c in sorted(change.items()))
                        combos.append((change, label))
                        if len(combos) >= max_combos:
                            return combos
        return combos

    def _proxy_row(
        self,
        *,
        instance: str,
        kind: str,
        from_type: str,
        to_type: str,
        critical_rank: int,
        critical_count: int,
        strategy_rank: int,
        patch_size: int,
        boundary_complexity: int,
        job: tuple,
    ) -> dict:
        return {
            "instance": instance,
            "kind": kind,
            "from_type": from_type,
            "to_type": to_type,
            "critical_rank": critical_rank,
            "critical_count": critical_count,
            "strategy_rank": strategy_rank,
            "patch_size": patch_size,
            "boundary_complexity": boundary_complexity,
            "job_index": int(job[-1]),
            "_job": job,
        }

    @staticmethod
    def _proxy_metadata(row: dict) -> dict:
        return {
            "proxy_rank": int(row["proxy_rank"]),
            "proxy_score": float(row["proxy_score"]),
            "proxy_features": dict(row["proxy_features"]),
        }

    def _eval_one(self, job: tuple) -> dict:
        (
            inst,
            cell_type,
            new_type,
            pin_map,
            kind,
            text,
            cand_dir,
            top_module,
            index,
            proxy_meta,
        ) = job
        started_at = time.perf_counter()
        topology_window = None
        if kind == "TOPOLOGY":
            topology_replacement, topology_window = pin_map
            candidate_text = stitch_topology_replacement(text, topology_replacement)
        elif kind == "JOINT":
            candidate_text = self._apply_joint(text, pin_map)
        else:
            candidate_text = self._apply(text, inst, kind, new_type, pin_map)
        sub = cand_dir / ("%03d_" % index + inst + "_" + kind)
        sub.mkdir(parents=True, exist_ok=True)
        (sub / "mapped.v").write_text(candidate_text, encoding="utf-8")
        candidate_hash = hashlib.sha256(candidate_text.encode("utf-8")).hexdigest()
        base_hash = hashlib.sha256(self.mapped_text.encode("utf-8")).hexdigest()
        analysis_config = {
            "period": self.period, "clock_port": self.clock_port,
            "sdc_config": {"period": self.period, "clock_port": self.clock_port,
                           "hold_mode": self.hold_mode,
                           "hold_uncertainty": self.hold_uncertainty},
            "hold_mode": self.hold_mode,
            "hold_uncertainty": self.hold_uncertainty,
            "physical_gate": self.physical_gate,
            "physical_unit_len_um": self.physical_unit_len_um,
            "physical_fanout_penalty": self.physical_fanout_penalty,
            "physical_depth_penalty": self.physical_depth_penalty,
            "liberty_hash": hashlib.sha256(self.liberty_text.encode("utf-8")).hexdigest(),
            "analysis_config": {"hold_mode": self.hold_mode,
                                "tns_aware": self.tns_aware,
                                "epsilon": self.epsilon},
            "rc_config": {"physical_gate": self.physical_gate,
                          "unit_len_um": self.physical_unit_len_um,
                          "fanout_penalty": self.physical_fanout_penalty,
                          "depth_penalty": self.physical_depth_penalty,
                          "min_physical_gain_ns": self.min_physical_gain_ns},
            "formal_config": {"strict_gates": self.strict_gates,
                              "checker": type(self.equivalence_checker).__name__ if self.equivalence_checker else None},
            "epsilon": self.epsilon,
        }
        config_hash = hashlib.sha256(json.dumps(analysis_config, sort_keys=True).encode()).hexdigest()
        cache_key = hashlib.sha256((base_hash + candidate_hash + config_hash).encode()).hexdigest()
        unavailable_gate_events = []
        if self.strict_gates and kind == "TOPOLOGY" and self.topology_sec_checker is None:
            unavailable_gate_events.append({
                "type": "F1_equivalence_failure", "candidate_hash": candidate_hash,
                "cut_hash": candidate_hash, "severity": "hard", "hard_gate": True,
                "evidence": {"stage": "full_netlist_sec", "status": "unavailable",
                             "reason": "topology SEC backend unavailable",
                             "formal_backend": "unavailable"},
            })
        elif self.strict_gates and kind != "TOPOLOGY" and self.equivalence_checker is None:
            unavailable_gate_events.append({
                "type": "F1_equivalence_failure", "candidate_hash": candidate_hash,
                "cut_hash": candidate_hash, "severity": "hard", "hard_gate": True,
                "evidence": {"reason": "per-candidate equivalence checker unavailable",
                             "formal_backend": "unavailable"},
            })
        if self.strict_gates and self.boundary_checker is None:
            unavailable_gate_events.append({
                "type": "F2_boundary_invalid", "candidate_hash": candidate_hash,
                "cut_hash": candidate_hash, "severity": "hard", "hard_gate": True,
                "evidence": {"reason": "boundary closure checker unavailable",
                             "boundary_backend": "unavailable"},
            })
        if unavailable_gate_events:
            failed = {
                "instance": inst, "kind": kind, "from_type": cell_type,
                "to_type": new_type, "wns": self.baseline_wns,
                "tns": self.baseline_tns, "min_slack": None,
                "physical_failure": False, "candidate_netlist_text": candidate_text,
                "candidate_hash": candidate_hash, "base_netlist_hash": base_hash,
                "cache_key": cache_key, "config_hash": config_hash,
                "failure_events": _normalise_failure_events(
                    unavailable_gate_events, candidate_hash=candidate_hash),
                "runtime_s": time.perf_counter() - started_at, **proxy_meta,
            }
            self._sta_cache[cache_key] = dict(failed)
            return failed
        if cache_key in self._sta_cache:
            cached = dict(self._sta_cache[cache_key])
            cached["skipped_duplicate"] = True
            return {**cached, **proxy_meta}
        if candidate_hash in self.tested_candidate_hashes and base_hash == getattr(self, "_last_base_hash", None):
            return {
                "instance": inst, "kind": kind, "from_type": cell_type,
                "to_type": new_type, "wns": self.baseline_wns,
                "tns": self.baseline_tns, "min_slack": None,
                "physical_failure": False, "candidate_netlist_text": candidate_text,
                "candidate_hash": candidate_hash, "runtime_s": 0.0,
                "skipped_duplicate": True, "cache_key": cache_key,
                "config_hash": config_hash, **proxy_meta,
            }
        state = self._active_state
        needs_formal = bool(self.strict_gates and
                            (self.equivalence_checker is not None or kind == "TOPOLOGY"))
        event = self._deadline_or_budget_event(
            state, "formal", candidate_hash=candidate_hash, cut_hash=candidate_hash,
            action_scope=[inst],
        ) if needs_formal else (self._deadline_or_budget_event(
            state, "local", candidate_hash=candidate_hash, cut_hash=candidate_hash,
            action_scope=[inst],
        ) if state is not None and kind == "TOPOLOGY" else None)
        if event is not None:
            failed = {"instance": inst, "kind": kind, "from_type": cell_type,
                      "to_type": new_type, "wns": self.baseline_wns,
                      "tns": self.baseline_tns, "min_slack": None,
                      "physical_failure": False, "candidate_netlist_text": candidate_text,
                      "candidate_hash": candidate_hash, "base_netlist_hash": base_hash,
                      "cache_key": cache_key, "config_hash": config_hash,
                      "failure_events": [event], "runtime_s": 0.0, **proxy_meta}
            self._sta_cache[cache_key] = dict(failed)
            return failed
        # All structural gates run before STA.  A topology candidate requires
        # local truth-table evidence plus a separate full-netlist SEC result;
        # the latter is never substituted by the local checker.
        if kind == "TOPOLOGY":
            sec_unavailable = False
            sec_status = None
            sec_details = {}
            try:
                local_check = check_local_functional_equivalence(topology_window, candidate_text)
                if local_check.status != "pass":
                    raise ValueError(f"local checker: {local_check.reason}")
                if self.strict_gates:
                    formal_event = self._deadline_or_budget_event(
                        state, "formal", candidate_hash=candidate_hash,
                        cut_hash=candidate_hash, action_scope=[inst],
                    )
                    if formal_event is not None:
                        failed = {"instance": inst, "kind": kind, "from_type": cell_type,
                                  "to_type": new_type, "wns": self.baseline_wns,
                                  "tns": self.baseline_tns, "min_slack": None,
                                  "physical_failure": False, "candidate_netlist_text": candidate_text,
                                  "candidate_hash": candidate_hash, "base_netlist_hash": base_hash,
                                  "cache_key": cache_key, "config_hash": config_hash,
                                  "failure_events": [formal_event], "runtime_s": 0.0, **proxy_meta}
                        self._sta_cache[cache_key] = dict(failed)
                        return failed
                    sec = self.topology_sec_checker(self.mapped_text, candidate_text)
                    sec_details = _checker_details(sec)
                    sec_status = sec_details.get("status")
                    sec_unavailable = sec_status == "unavailable"
                    if not _checker_passed(sec):
                        raise ValueError(f"full-netlist SEC: {sec}")
            except TimeoutError as exc:
                event = {"type": "F1_equivalence_failure", "candidate_hash": candidate_hash,
                         "cut_hash": candidate_hash, "severity": "hard", "hard_gate": True,
                         "runtime_s": 0.0, "evidence": {"stage": "full_netlist_sec",
                         "status": "timeout", "reason": str(exc)}}
                failed = {"instance": inst, "kind": kind, "from_type": cell_type,
                          "to_type": new_type, "wns": self.baseline_wns,
                          "tns": self.baseline_tns, "min_slack": None,
                          "physical_failure": False, "candidate_netlist_text": candidate_text,
                          "candidate_hash": candidate_hash, "base_netlist_hash": base_hash,
                          "cache_key": cache_key, "config_hash": config_hash,
                          "failure_events": [event], "runtime_s": 0.0, **proxy_meta}
                self._sta_cache[cache_key] = dict(failed)
                return failed
            except Exception as exc:
                event = {"type": "F1_equivalence_failure", "candidate_hash": candidate_hash,
                         "cut_hash": candidate_hash, "severity": "hard", "hard_gate": True,
                         "runtime_s": 0.0, "evidence": {"stage": "full_netlist_sec",
                         "status": sec_status or ("unavailable" if sec_unavailable else "fail"),
                         "reason": sec_details.get("reason", str(exc)), **sec_details}}
                failed = {"instance": inst, "kind": kind, "from_type": cell_type,
                          "to_type": new_type, "wns": self.baseline_wns,
                          "tns": self.baseline_tns, "min_slack": None,
                          "physical_failure": False, "candidate_netlist_text": candidate_text,
                          "candidate_hash": candidate_hash, "base_netlist_hash": base_hash,
                          "cache_key": cache_key, "config_hash": config_hash,
                          "failure_events": [event], "runtime_s": 0.0, **proxy_meta}
                self._sta_cache[cache_key] = dict(failed)
                return failed
            boundary_budget_event = self._deadline_or_budget_event(
                state, "formal", candidate_hash=candidate_hash,
                cut_hash=candidate_hash, action_scope=[inst],
            )
            if boundary_budget_event is not None:
                failed = {"instance": inst, "kind": kind, "from_type": cell_type,
                          "to_type": new_type, "wns": self.baseline_wns,
                          "tns": self.baseline_tns, "min_slack": None,
                          "physical_failure": False, "candidate_netlist_text": candidate_text,
                          "candidate_hash": candidate_hash, "base_netlist_hash": base_hash,
                          "cache_key": cache_key, "config_hash": config_hash,
                          "failure_events": [boundary_budget_event], "runtime_s": 0.0, **proxy_meta}
                self._sta_cache[cache_key] = dict(failed)
                return failed
            if self.boundary_checker is not None:
                boundary_result = None
                try:
                    boundary_result = self.boundary_checker(self.mapped_text, candidate_text)
                    boundary_ok = _checker_passed(boundary_result)
                except Exception as exc:
                    boundary_ok = False
                    boundary_result = {"status": "error", "reason": str(exc)}
            else:
                boundary_ok = False
                boundary_result = {"status": "unavailable", "reason": "boundary checker unavailable"}
            if not boundary_ok:
                    event = {"type": "F2_boundary_invalid", "candidate_hash": candidate_hash,
                             "cut_hash": candidate_hash, "severity": "hard", "hard_gate": True,
                             "runtime_s": 0.0, "evidence": {"stage": "boundary_closure",
                             **_checker_details(boundary_result)}}
                    failed = {"instance": inst, "kind": kind, "from_type": cell_type,
                              "to_type": new_type, "wns": self.baseline_wns,
                              "tns": self.baseline_tns, "min_slack": None,
                              "physical_failure": False, "candidate_netlist_text": candidate_text,
                              "candidate_hash": candidate_hash, "base_netlist_hash": base_hash,
                              "cache_key": cache_key, "config_hash": config_hash,
                              "failure_events": [event], "runtime_s": 0.0, **proxy_meta}
                    self._sta_cache[cache_key] = dict(failed)
                    return failed
        if self.strict_gates and kind != "TOPOLOGY":
            structural_events = []
            try:
                eq = self.equivalence_checker(self.mapped_text, candidate_text)
                if not _checker_passed(eq):
                    structural_events.append({
                        "type": "F1_equivalence_failure", "candidate_hash": candidate_hash,
                        "cut_hash": candidate_hash, "severity": "hard", "hard_gate": True,
                        "runtime_s": 0.0, "evidence": {"stage": "equivalence", "result": str(eq)},
                    })
            except Exception as exc:
                structural_events.append({
                    "type": "F1_equivalence_failure", "candidate_hash": candidate_hash,
                    "cut_hash": candidate_hash, "severity": "hard", "hard_gate": True,
                    "runtime_s": 0.0, "evidence": {"stage": "equivalence", "reason": str(exc)},
                })
            boundary_budget_event = self._deadline_or_budget_event(
                state, "formal", candidate_hash=candidate_hash,
                cut_hash=candidate_hash, action_scope=[inst],
            )
            boundary_result = None
            try:
                if boundary_budget_event is not None:
                    boundary_ok = False
                else:
                    boundary_result = (self.boundary_checker(self.mapped_text, candidate_text)
                                       if self.boundary_checker is not None else None)
                    boundary_ok = boundary_result is not None and _checker_passed(boundary_result)
            except Exception as exc:
                boundary_ok = False
                boundary_error = str(exc)
                boundary_result = {"status": "error", "reason": boundary_error}
            if boundary_budget_event is not None:
                structural_events.append(boundary_budget_event)
            if not boundary_ok and boundary_budget_event is None:
                structural_events.append({
                    "type": "F2_boundary_invalid", "candidate_hash": candidate_hash,
                    "cut_hash": candidate_hash, "severity": "hard", "hard_gate": True,
                    "runtime_s": 0.0,
                    "evidence": {"stage": "boundary_closure",
                                 **_checker_details(boundary_result or {
                                     "status": "unavailable",
                                     "reason": "checker unavailable or false",
                                 })},
                })
            if structural_events:
                failed = {"instance": inst, "kind": kind, "from_type": cell_type,
                          "to_type": new_type, "wns": self.baseline_wns,
                          "tns": self.baseline_tns, "min_slack": None,
                          "physical_failure": False, "candidate_netlist_text": candidate_text,
                          "candidate_hash": candidate_hash, "base_netlist_hash": base_hash,
                          "cache_key": cache_key, "config_hash": config_hash,
                          "failure_events": structural_events, "runtime_s": 0.0, **proxy_meta}
                self._sta_cache[cache_key] = dict(failed)
                return failed
        event = self._deadline_or_budget_event(
            state, "sta", candidate_hash=candidate_hash, cut_hash=candidate_hash,
            action_scope=[inst],
        )
        if event is not None:
            failed = {"instance": inst, "kind": kind, "from_type": cell_type,
                      "to_type": new_type, "wns": self.baseline_wns,
                      "tns": self.baseline_tns, "min_slack": None,
                      "physical_failure": False, "candidate_netlist_text": candidate_text,
                      "candidate_hash": candidate_hash, "base_netlist_hash": base_hash,
                      "cache_key": cache_key, "config_hash": config_hash,
                      "failure_events": [event], "runtime_s": 0.0, **proxy_meta}
            self._sta_cache[cache_key] = dict(failed)
            return failed
        self.tested_candidate_hashes.add(candidate_hash)
        self._last_base_hash = base_hash
        try:
            res = run_opensta_sequential(
                netlist_path=sub / "mapped.v",
                period=self.period,
                output_dir=sub,
                top_module=top_module,
                hold_uncertainty=self.hold_uncertainty if self.hold_mode else 0.0,
                min_path=self.hold_mode,
                clock_port=self.clock_port,
                multi_path=True,
                timeout_s=self._remaining_tool_timeout(state),
            )
        except TimeoutError as exc:
            res = {"wns": None, "tns": None, "error": str(exc), "timeout": True}
        except Exception as exc:
            res = {"wns": None, "tns": None, "error": str(exc)}
        critical_refresh = None
        critical_endpoint_refresh = None
        report = sub / "sta.log"
        critical_report = report
        if state is not None and state.deadline_expired():
            event = {
                "type": "deadline_exhausted", "candidate_hash": candidate_hash,
                "cut_hash": candidate_hash, "severity": "hard", "hard_gate": True,
                "runtime_s": time.perf_counter() - started_at,
                "evidence": {"stage": "sta", "reason": "deadline expired after ideal STA"},
            }
            return {"instance": inst, "kind": kind, "from_type": cell_type,
                    "to_type": new_type, "wns": self.baseline_wns,
                    "tns": self.baseline_tns, "min_slack": None,
                    "candidate_netlist_text": candidate_text,
                    "candidate_hash": candidate_hash, "failure_events": [event],
                    "runtime_s": time.perf_counter() - started_at, **proxy_meta}
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="replace")
            critical_refresh = parse_critical_instances(report_text)
            critical_endpoint_refresh = parse_worst_endpoint(report_text)
        # Physical mode is evaluated exclusively against a paired physical
        # baseline/candidate under one RC model.  Ideal STA is retained only
        # as an independent diagnostic, never as an acceptance prefilter.
        if self.physical_gate:
            rc_config = {
                "unit_len_um": self.physical_unit_len_um,
                "fanout_penalty": self.physical_fanout_penalty,
                "depth_penalty": self.physical_depth_penalty,
            }
            physical_config = {**rc_config,
                               "min_physical_gain_ns": self.min_physical_gain_ns}
            rc_config_hash = hashlib.sha256(
                json.dumps(physical_config, sort_keys=True).encode()
            ).hexdigest()
            try:
                    from .spef import build_spef, parse_mapped_verilog, write_spef
                    import hashlib as _hashlib
                    rc_config_hash = _hashlib.sha256(
                        json.dumps(physical_config, sort_keys=True).encode()
                    ).hexdigest()
                    baseline_hash = _hashlib.sha256(self.mapped_text.encode("utf-8")).hexdigest()
                    cache_key = baseline_hash + ":" + rc_config_hash
                    self._physical_baseline_lock.acquire()
                    physical_lock_held = True
                    baseline = self._physical_baseline_cache.get(cache_key)
                    if baseline is None:
                        base_dir = cand_dir / "physical_baseline"
                        base_dir.mkdir(parents=True, exist_ok=True)
                        (base_dir / "mapped.v").write_text(self.mapped_text, encoding="utf-8")
                        base_nl = parse_mapped_verilog(base_dir / "mapped.v")
                        base_spef = write_spef(base_dir / "physical.spef", base_nl, **rc_config)
                        budget_event = self._deadline_or_budget_event(
                            state, "sta", candidate_hash=candidate_hash,
                            cut_hash=candidate_hash, action_scope=[inst])
                        base_sta = None if budget_event else run_opensta_sequential(
                            netlist_path=base_dir / "mapped.v",
                            period=self.period, output_dir=base_dir,
                            top_module=top_module, clock_port=self.clock_port,
                            spef_path=base_spef,
                            hold_uncertainty=self.hold_uncertainty if self.hold_mode else 0.0,
                            min_path=self.hold_mode,
                            timeout_s=self._remaining_tool_timeout(state),
                        )
                        # Keep a physical baseline artifact alongside the
                        # candidate, and fail closed if it is incomplete.
                        baseline = {"wns": base_sta.get("wns") if base_sta else None,
                                    "tns": base_sta.get("tns") if base_sta else None,
                                    "min_slack": base_sta.get("min_slack") if base_sta else None,
                                    "budget_event": budget_event,
                                    "rc_config_hash": rc_config_hash,
                                    "provenance": _physical_sta_provenance(
                                        base_dir, base_sta, rc_config, rc_config_hash)}
                        self._physical_baseline_cache[cache_key] = baseline
                    self._physical_baseline_lock.release()
                    physical_lock_held = False
                    if baseline.get("budget_event"):
                        phys = {"wns": None, "tns": None, "min_slack": None,
                                "budget_event": baseline["budget_event"]}
                    else:
                        nl = parse_mapped_verilog(sub / "mapped.v")
                        spef = write_spef(sub / "physical.spef", nl, **rc_config)
                        budget_event = self._deadline_or_budget_event(
                            state, "sta", candidate_hash=candidate_hash,
                            cut_hash=candidate_hash, action_scope=[inst])
                        phys = {"wns": None, "tns": None, "min_slack": None,
                                "budget_event": budget_event} if budget_event else run_opensta_sequential(
                            netlist_path=sub / "mapped.v",
                            period=self.period,
                            output_dir=sub / "physical",
                            top_module=top_module,
                            clock_port=self.clock_port,
                            spef_path=spef,
                            hold_uncertainty=self.hold_uncertainty if self.hold_mode else 0.0,
                            min_path=self.hold_mode,
                            timeout_s=self._remaining_tool_timeout(state),
                        )
                    phys_wns = phys.get("wns")
                    phys_tns = phys.get("tns")
                    phys_min_slack = phys.get("min_slack")
                    baseline_provenance = baseline.get("provenance")
                    candidate_provenance = _physical_sta_provenance(
                        sub / "physical", phys, rc_config, rc_config_hash)
                    base_phys_wns = baseline.get("wns")
                    base_phys_tns = baseline.get("tns")
                    base_phys_min_slack = baseline.get("min_slack")
                    if baseline.get("budget_event") or phys.get("budget_event"):
                        res = {**res, "wns": self.baseline_wns,
                               "physical_failure": True,
                               "physical_status": "budget_exhausted",
                               "physical_wns": phys_wns, "physical_tns": phys_tns,
                               "physical_min_slack": phys_min_slack,
                               "physical_baseline": base_phys_wns,
                               "physical_candidate": phys_wns,
                               "physical_baseline_tns": base_phys_tns,
                               "physical_candidate_tns": phys_tns,
                               "physical_baseline_min_slack": base_phys_min_slack,
                               "physical_candidate_min_slack": phys_min_slack,
                               "physical_delta": None,
                               "physical_budget_event": baseline.get("budget_event") or phys.get("budget_event"),
                               "physical_baseline_provenance": baseline_provenance,
                               "physical_candidate_provenance": candidate_provenance,
                               "rc_config_hash": rc_config_hash}
                    elif (base_phys_wns is None or phys_wns is None
                          or base_phys_tns is None or phys_tns is None
                          or (self.hold_required and (base_phys_min_slack is None
                                                      or phys_min_slack is None))):
                        # physical load failure: the ideal gain does not
                        # have a complete paired physical measurement.
                        res = {**res, "wns": self.baseline_wns,
                               "physical_failure": True,
                               "physical_status": "paired_incomplete",
                               "physical_wns": phys_wns,
                               "physical_tns": phys_tns,
                               "physical_min_slack": phys_min_slack,
                               "physical_baseline": base_phys_wns,
                               "physical_candidate": phys_wns,
                               "physical_baseline_tns": base_phys_tns,
                               "physical_candidate_tns": phys_tns,
                               "physical_baseline_min_slack": base_phys_min_slack,
                               "physical_candidate_min_slack": phys_min_slack,
                               "physical_delta": None,
                               "physical_baseline_provenance": baseline_provenance,
                               "physical_candidate_provenance": candidate_provenance,
                               "rc_config_hash": rc_config_hash}
                    elif ((phys_wns < base_phys_wns - self.epsilon
                           if self.hold_mode else
                           phys_wns - base_phys_wns + 1e-12
                           < self.min_physical_gain_ns - self.epsilon)
                          or phys_tns < base_phys_tns - self.epsilon
                          or (self.hold_required and (
                              base_phys_min_slack is None or phys_min_slack is None
                              or phys_min_slack < base_phys_min_slack - self.epsilon))):
                        # physical load failure: candidate is compared to the
                        # paired current baseline under exactly one RC model.
                        res = {**res, "wns": self.baseline_wns,
                               "physical_failure": True,
                               "physical_status": "paired_rejected",
                               "physical_wns": phys_wns,
                               "physical_tns": phys_tns,
                               "physical_min_slack": phys_min_slack,
                               "physical_baseline": base_phys_wns,
                               "physical_candidate": phys_wns,
                               "physical_baseline_tns": base_phys_tns,
                               "physical_candidate_tns": phys_tns,
                               "physical_baseline_min_slack": base_phys_min_slack,
                               "physical_candidate_min_slack": phys_min_slack,
                               "physical_delta": phys_wns - base_phys_wns,
                               "physical_baseline_provenance": baseline_provenance,
                               "physical_candidate_provenance": candidate_provenance,
                               "rc_config_hash": rc_config_hash}
                    else:
                        # parasitic-aware gain survives: report the SPEF WNS
                        res = {**res, "wns": phys_wns, "tns": phys_tns,
                               "min_slack": phys_min_slack,
                               "physical_status": "paired_improved",
                               "physical_wns": phys_wns,
                               "physical_tns": phys_tns,
                               "physical_min_slack": phys_min_slack,
                               "physical_baseline": base_phys_wns,
                               "physical_candidate": phys_wns,
                               "physical_baseline_tns": base_phys_tns,
                               "physical_candidate_tns": phys_tns,
                               "physical_baseline_min_slack": base_phys_min_slack,
                               "physical_candidate_min_slack": phys_min_slack,
                               "physical_delta": phys_wns - base_phys_wns,
                               "physical_baseline_provenance": baseline_provenance,
                               "physical_candidate_provenance": candidate_provenance,
                               "rc_config_hash": rc_config_hash}
            except Exception as exc:
                    if locals().get("physical_lock_held"):
                        self._physical_baseline_lock.release()
                    res = {**res, "wns": self.baseline_wns,
                           "physical_failure": True,
                           "physical_status": "error",
                           "physical_baseline": (baseline.get("wns") if "baseline" in locals() else None),
                           "physical_candidate": None,
                           "physical_baseline_tns": (baseline.get("tns") if "baseline" in locals() else None),
                           "physical_candidate_tns": None,
                           "physical_delta": None,
                           "physical_baseline_provenance": (baseline.get("provenance") if "baseline" in locals() and baseline else None),
                           "physical_candidate_provenance": (_physical_sta_provenance(sub / "physical", phys, rc_config, rc_config_hash) if "phys" in locals() and phys else None),
                           "rc_config_hash": (rc_config_hash if "rc_config_hash" in locals() else None),
                           "physical_gate_error": str(exc)}
            if state is not None and state.deadline_expired():
                deadline_event = {
                    "type": "deadline_exhausted", "candidate_hash": candidate_hash,
                    "cut_hash": candidate_hash, "severity": "hard", "hard_gate": True,
                    "runtime_s": time.perf_counter() - started_at,
                    "evidence": {"stage": "physical_sta", "reason": "deadline expired after physical STA"},
                }
                res = {**res, "wns": self.baseline_wns, "tns": self.baseline_tns,
                       "min_slack": None, "physical_failure": False,
                       "physical_status": "budget_exhausted",
                       "physical_budget_event": deadline_event,
                       "physical_delta": None}
            if self.physical_gate:
                res["physical_config"] = {
                    "unit_len_um": self.physical_unit_len_um,
                    "fanout_penalty": self.physical_fanout_penalty,
                    "depth_penalty": self.physical_depth_penalty,
                    "min_physical_gain_ns": self.min_physical_gain_ns,
                }
            physical_report = sub / "physical" / "sta.log"
            if physical_report.exists():
                critical_report = physical_report
                physical_report_text = physical_report.read_text(
                    encoding="utf-8", errors="replace"
                )
                critical_refresh = parse_critical_instances(physical_report_text)
                critical_endpoint_refresh = parse_worst_endpoint(physical_report_text)
        failure_events = []
        if res.get("physical_budget_event"):
            failure_events.append(res["physical_budget_event"])
        if res.get("physical_failure"):
            failure_events.append({
                "type": "F6_physical_load_failure",
                "candidate_hash": candidate_hash,
                "cut_hash": candidate_hash,
                "endpoint": None,
                "path": [],
                "net": None,
                "action_scope": [inst],
                "threshold": {
                    "value": self.min_physical_gain_ns,
                    "unit": "ns",
                    "epsilon": self.epsilon,
                },
                "observed_value": res.get("physical_delta"),
                "severity": "soft",
                "runtime_s": time.perf_counter() - started_at,
                "evidence": {
                    "threshold": {
                        "value": self.min_physical_gain_ns,
                        "unit": "ns",
                        "epsilon": self.epsilon,
                    },
                    "actual_delta": res.get("physical_delta"),
                    "backend": "OpenSTA SPEF",
                    "physical_baseline": res.get("physical_baseline"),
                    "physical_candidate": res.get("physical_candidate"),
                    "paired_baseline": res.get("physical_baseline_provenance"),
                    "paired_candidate": res.get("physical_candidate_provenance"),
                    "rc_config_hash": res.get("rc_config_hash"),
                    "status": res.get("physical_status"),
                    "error": res.get("physical_gate_error"),
                },
            })
        # F3 is measured from the actual changed region and is a hard gate in
        # both compatibility and strict production modes.  It must never be
        # disabled merely because formal/boundary checkers are configured.
        if kind == "TOPOLOGY" and topology_window is not None:
            changed = len(topology_window.gates)
        elif kind == "JOINT":
            changed = len(pin_map)
        else:
            changed = 1
        gate_count = max(1, len(parse_mapped_netlist(self.mapped_text)))
        ratio = changed / gate_count
        if self.strict_gates and ratio > self.max_patch_ratio + self._metric_epsilon("patch_ratio"):
            failure_events.append({
                "type": "F3_patch_too_large", "candidate_hash": candidate_hash,
                "cut_hash": candidate_hash, "severity": "hard", "hard_gate": True,
                "runtime_s": 0.0,
                 "threshold": {"value": self.max_patch_ratio, "unit": "ratio",
                                "epsilon": self._metric_epsilon("patch_ratio")},
                 "observed_value": {"value": ratio, "unit": "ratio"},
                "evidence": {"modified_gate_count": changed, "gate_count": gate_count,
                             "action_scope": [inst]},
            })
        if time.perf_counter() - started_at > self.max_verification_time_s:
            failure_events.append({
                "type": "F5_verification_too_expensive", "candidate_hash": candidate_hash,
                "cut_hash": candidate_hash, "severity": "hard", "runtime_s": time.perf_counter() - started_at,
                "threshold": self.max_verification_time_s,
                "observed_value": time.perf_counter() - started_at,
                "evidence": {"tool": "OpenSTA"},
            })
        if res.get("error") or res.get("timeout"):
            failure_events.append({
                "type": "F5_verification_too_expensive", "candidate_hash": candidate_hash,
                "cut_hash": candidate_hash, "severity": "hard", "runtime_s": time.perf_counter() - started_at,
                "threshold": self.max_verification_time_s,
                "observed_value": time.perf_counter() - started_at,
                "evidence": {"tool": "OpenSTA", "error": res.get("error"),
                             "timeout": bool(res.get("timeout"))},
            })
        paired = self.physical_gate
        metric_values = {
            "setup_wns": res.get("physical_candidate") if paired else res.get("wns"),
            "setup_tns": res.get("physical_candidate_tns") if paired else res.get("tns"),
            "hold_min_slack": (res.get("physical_candidate_min_slack")
                               if paired else res.get("min_slack")),
            "area": res.get("area"),
            "max_transition": res.get("max_transition"),
            "max_capacitance": res.get("max_capacitance"),
            "max_fanout": res.get("max_fanout"),
        }
        metric_references = {
            "setup_wns": res.get("physical_baseline") if paired else self.baseline_wns,
            "setup_tns": res.get("physical_baseline_tns") if paired else self.baseline_tns,
            "hold_min_slack": (res.get("physical_baseline_min_slack")
                               if paired else self.baseline_min_slack),
        }
        unavailable_metrics = [metric for metric in self.required_metrics
                               if metric_values.get(metric) is None]
        unavailable = tuple(unavailable_metrics)
        violations: list[str] = []
        if (self.strict_budgets and metric_references["setup_tns"] is not None
                and metric_values["setup_tns"] is not None
                and metric_values["setup_tns"] < metric_references["setup_tns"] - self.epsilon):
            violations.append("setup_tns")
        if (self.strict_budgets and self.hold_required
                and metric_references["hold_min_slack"] is not None
                and metric_values["hold_min_slack"] is not None
                and metric_values["hold_min_slack"] < metric_references["hold_min_slack"] - self.epsilon):
            violations.append("hold_min_slack")
        if self.area_budget is not None and res.get("area") is not None and res["area"] > self.area_budget + self._metric_epsilon("area"):
            violations.append("area")
        if self.max_transition_budget is not None and res.get("max_transition") is not None and res["max_transition"] > self.max_transition_budget + self._metric_epsilon("max_transition"):
            violations.append("max_transition")
        if self.max_capacitance_budget is not None and res.get("max_capacitance") is not None and res["max_capacitance"] > self.max_capacitance_budget + self._metric_epsilon("max_capacitance"):
            violations.append("max_capacitance")
        if self.max_fanout_budget is not None and res.get("max_fanout") is not None and res["max_fanout"] > self.max_fanout_budget + self._metric_epsilon("max_fanout"):
            violations.append("max_fanout")
        evidence = AcceptanceEvidence(
            setup_wns=metric_values["setup_wns"], setup_tns=metric_values["setup_tns"],
            hold_min_slack=metric_values["hold_min_slack"], area=res.get("area"),
            max_transition=res.get("max_transition"),
            max_capacitance=res.get("max_capacitance"), max_fanout=res.get("max_fanout"),
            backend_provenance={"tool": "OpenSTA", "status": res.get("status", "unknown")},
            unavailable=unavailable if self.strict_budgets else (),
            violations=tuple(violations), epsilon=self.epsilon,
            epsilon_by_metric=dict(self.metric_epsilons),
        )
        if self.strict_budgets and (evidence.unavailable or evidence.violations):
            metric_budgets = {}
            budget_specs = {
                "area": self.area_budget,
                "max_transition": self.max_transition_budget,
                "max_capacitance": self.max_capacitance_budget,
                "max_fanout": self.max_fanout_budget,
            }
            metric_units = {
                "setup_wns": "ns", "setup_tns": "ns", "hold_min_slack": "ns",
                "area": "um^2", "max_transition": "ns",
                "max_capacitance": "pF", "max_fanout": "count",
            }
            metric_values_for_evidence = {
                "setup_wns": metric_values["setup_wns"],
                "setup_tns": metric_values["setup_tns"],
                "hold_min_slack": metric_values["hold_min_slack"],
                **metric_values,
            }
            for metric, budget in budget_specs.items():
                value = metric_values.get(metric)
                if budget is not None and value is not None and metric in violations:
                    metric_budgets[metric] = {
                        "value": value,
                        "budget": budget,
                        "epsilon": self._metric_epsilon(metric),
                        "unit": metric_units[metric],
                        "backend": "OpenSTA",
                    }
            for metric, reference in metric_references.items():
                value = metric_values_for_evidence.get(metric)
                if metric in violations and reference is not None and value is not None:
                    metric_budgets[metric] = {
                        "value": value,
                        "reference": reference,
                        "epsilon": self.epsilon,
                        "unit": metric_units[metric],
                        "backend": "OpenSTA",
                    }
            evidence_payload = evidence.to_dict()
            evidence_payload["metric_budgets"] = metric_budgets
            failure_events.append({
                "type": "acceptance_budget_unavailable" if evidence.unavailable else "acceptance_budget_violation",
                "candidate_hash": candidate_hash, "cut_hash": candidate_hash,
                "severity": "hard", "hard_gate": True, "runtime_s": time.perf_counter() - started_at,
                "threshold": {"unavailable": list(evidence.unavailable), "violations": list(evidence.violations)},
                "observed_value": evidence_payload, "evidence": evidence_payload,
            })
        evidence_payload = evidence.to_dict()
        evidence_payload["metric_references"] = metric_references
        if self.physical_gate:
            evidence_payload["paired_reference_source"] = "physical_baseline"
        result = {
            "instance": inst,
            "kind": kind,
            "from_type": cell_type,
            "to_type": new_type,
            "topology_metrics": ({
                "before": topology_replacement.before.to_dict(),
                "after": topology_replacement.after.to_dict(),
            } if kind == "TOPOLOGY" else None),
            "wns": res.get("wns"),
            "tns": res.get("tns"),
            "min_slack": res.get("min_slack"),
            "area": res.get("area"),
            "max_transition": res.get("max_transition"),
            "max_capacitance": res.get("max_capacitance"),
            "max_fanout": res.get("max_fanout"),
            "min_slack_status": res.get("min_slack_status"),
            "slack": res.get("slack"),
            "slack_status": res.get("slack_status"),
            "physical_failure": res.get("physical_failure", False),
            "physical_wns": res.get("physical_wns"),
            "physical_tns": res.get("physical_tns"),
            "physical_min_slack": res.get("physical_min_slack"),
            "physical_gate_error": res.get("physical_gate_error"),
            "physical_baseline": res.get("physical_baseline"),
            "physical_candidate": res.get("physical_candidate"),
            "physical_baseline_tns": res.get("physical_baseline_tns"),
            "physical_candidate_tns": res.get("physical_candidate_tns"),
            "physical_baseline_min_slack": res.get("physical_baseline_min_slack"),
            "physical_candidate_min_slack": res.get("physical_candidate_min_slack"),
            "physical_baseline_provenance": res.get("physical_baseline_provenance"),
            "physical_candidate_provenance": res.get("physical_candidate_provenance"),
            "physical_config": res.get("physical_config"),
            "physical_delta": res.get("physical_delta"),
            "physical_status": res.get("physical_status"),
            "rc_config_hash": res.get("rc_config_hash"),
            "failure_events": failure_events,
            "acceptance_evidence": evidence_payload,
            "critical_instances": critical_refresh,
            "critical_endpoints": ([critical_endpoint_refresh]
                                    if critical_endpoint_refresh else None),
            "sta_provenance": {
                "tool": "OpenSTA", "output_dir": str(critical_report.parent),
                "report_path": str(critical_report) if critical_report.exists() else None,
            },
            "candidate_netlist_text": candidate_text,
            "candidate_hash": candidate_hash,
            "base_netlist_hash": base_hash,
            "cache_key": cache_key,
            "config_hash": config_hash,
            "runtime_s": time.perf_counter() - started_at,
            **proxy_meta,
        }
        self._sta_cache[cache_key] = dict(result)
        return result

    # -- main entry ---------------------------------------------------------

    def __call__(self, patch, weights, *, state=None) -> dict:
        """Evaluate one outer-loop patch candidate with real STA."""
        self._active_state = state
        gates = list(getattr(patch, "gates", []) or [])
        patch_id = getattr(patch, "patch_id", str(patch))
        iteration = len(self.call_log) + 1
        self._call_counter += 1
        cand_dir = self.output_dir / ("iter%03d_cand%03d" % (iteration, self._call_counter))
        cand_dir.mkdir(parents=True, exist_ok=True)

        unavailable_required = sorted(set(self.required_metrics) - set(self.available_metrics))
        if self.strict_budgets and unavailable_required:
            base_hash = hashlib.sha256(self.mapped_text.encode("utf-8")).hexdigest()
            candidate_hash = hashlib.sha256(
                json.dumps({"base": base_hash, "patch": str(patch_id), "gates": sorted(gates)}, sort_keys=True).encode()
            ).hexdigest()
            event = {
                "type": "acceptance_budget_unavailable",
                "candidate_hash": candidate_hash, "cut_hash": candidate_hash,
                "endpoint": None, "path": [], "net": None,
                "action_scope": gates, "threshold": unavailable_required,
                "observed_value": "backend_preflight_unavailable", "severity": "hard",
                "runtime_s": 0.0,
                "evidence": {"required_metrics": list(self.required_metrics),
                             "available_metrics": sorted(self.available_metrics),
                             "backend": "OpenSTA sequential parser"},
            }
            event = _normalise_failure_events([event], candidate_hash=candidate_hash)[0]
            trial = {"patch_id": patch_id, "iteration": iteration,
                     "candidate_hash": candidate_hash, "cut_hash": candidate_hash,
                     "failure_events": [event], "accepted": False,
                     "wns": self.baseline_wns, "improved": False,
                     "reason": "required metric backend unavailable"}
            self.trials.append(trial)
            self.call_log.append({"iteration": iteration, "patch_id": patch_id,
                                  "gates": gates, "improved": False,
                                  "reason": trial["reason"], "failure_events": [event]})
            return {"wns": self.baseline_wns, "tns": self.baseline_tns,
                    "improved": False, "failure_events": [event],
                    "trial_failure_events": [event], "candidate_hash": candidate_hash}

        cells = parse_mapped_netlist(self.mapped_text)
        by_inst = {c.instance: c for c in cells}
        in_patch = [g for g in gates if g in by_inst]
        # order: critical-path instances first, then remaining cut gates
        ordered = [i for i in self.critical_instances if i in in_patch]
        ordered += [g for g in in_patch if g not in ordered]
        actionable = ordered[: self.max_instances]
        if not actionable:
            no_action_hash = hashlib.sha256(
                json.dumps({"gates": sorted(gates), "patch_id": patch_id}, sort_keys=True).encode()
            ).hexdigest()
            no_action_event = _normalise_failure_events([{
                     "type": "F2_boundary_invalid", "candidate_hash": no_action_hash,
                     "cut_hash": no_action_hash, "endpoint": None, "path": [],
                     "net": None, "action_scope": list(gates),
                     "threshold": 1, "observed_value": 0, "severity": "hard",
                     "runtime_s": 0.0,
                     "evidence": {"reason": "cut has no actionable mapped gate"},
                 }], candidate_hash=no_action_hash)[0]
            self.call_log.append(
                {"iteration": iteration, "patch_id": patch_id, "gates": gates,
                 "wns": self.baseline_wns, "improved": False,
                 "reason": "no actionable gates", "failure_events": [no_action_event]}
            )
            return {"wns": self.baseline_wns, "improved": False,
                    "failure_events": self.call_log[-1]["failure_events"]}

        candidate_rows: list[dict] = []
        job_index = 0
        boundary_complexity = (
            len(getattr(patch, "boundary_inputs", []) or [])
            + len(getattr(patch, "boundary_outputs", []) or [])
        )
        critical_count = max(1, len(self.critical_instances))
        for inst in actionable:
            critical_rank = (
                self.critical_instances.index(inst)
                if inst in self.critical_instances
                else critical_count - 1
            )
            order = self._strategy_order(by_inst[inst].cell_type)
            strategy_ranks = {kind: rank for rank, kind in enumerate(order)}
            for new_type, pin_map, kind in self._candidates_for(cells, inst):
                job = (
                    inst,
                    by_inst[inst].cell_type,
                    new_type,
                    pin_map,
                    kind,
                    self.mapped_text,
                    cand_dir,
                    self.top_module,
                    job_index,
                )
                candidate_rows.append(
                    self._proxy_row(
                        instance=inst,
                        kind=kind,
                        from_type=by_inst[inst].cell_type,
                        to_type=new_type,
                        critical_rank=critical_rank,
                        critical_count=critical_count,
                        strategy_rank=strategy_ranks.get(kind, len(order)),
                        patch_size=1,
                        boundary_complexity=boundary_complexity,
                        job=job,
                    )
                )
                job_index += 1

        # Topology candidate: extract exactly the cut region, generate a
        # multi-gate rewrite, and defer local truth-table equivalence to the
        # candidate evaluation before OpenSTA/acceptance.
        if self.enable_topology and len(actionable) >= 2:
            try:
                analysis_netlist = parse_verilog_netlist_from_text(self.mapped_text)
                window = extract_combinational_window(analysis_netlist, actionable)
                topology = generate_topology_replacement(window)
                job = (
                    "TOPOLOGY", "topology", topology.method,
                    (topology, window), "TOPOLOGY", self.mapped_text,
                    cand_dir, self.top_module, job_index,
                )
                candidate_rows.append(
                    self._proxy_row(
                        instance="TOPOLOGY", kind="TOPOLOGY", from_type="topology",
                        to_type=topology.method,
                        critical_rank=0, critical_count=critical_count,
                        strategy_rank=0, patch_size=len(topology.original_gates),
                        boundary_complexity=boundary_complexity, job=job,
                    )
                )
                job_index += 1
            except (ValueError, OSError):
                # No supported topology pattern in this region is an honest
                # no-candidate outcome, not a fallback to global critical gates.
                pass

        # joint repair: one candidate that changes the top-joint_k actionable
        # instances simultaneously.  Default (joint_mix=False) resizes with G;
        # joint_mix=True prefers R (rewrite) per instance and falls back to G,
        # building an R+G mixed action as a single STA-evaluated candidate.
        if self.joint_k > 0:
            joint_change: dict[str, tuple[str, dict, str]] = {}
            for inst in actionable:
                if inst in joint_change:
                    continue
                for new_type, _pm, kind in self._candidates_for(cells, inst):
                    if (self.joint_mix and kind == "R") or (
                        not self.joint_mix and kind == "G"
                    ):
                        joint_change[inst] = (new_type, _pm, kind)
                        break
                if len(joint_change) >= self.joint_k:
                    break
            if len(joint_change) >= 2:
                critical_rank = min(
                    (
                        self.critical_instances.index(inst)
                        for inst in joint_change
                        if inst in self.critical_instances
                    ),
                    default=critical_count - 1,
                )
                job = (
                    "JOINT",
                    "joint",
                    "joint",
                    joint_change,
                    "JOINT",
                    self.mapped_text,
                    cand_dir,
                    self.top_module,
                    job_index,
                )
                candidate_rows.append(
                    self._proxy_row(
                        instance="JOINT",
                        kind="JOINT",
                        from_type="joint",
                        to_type="joint",
                        critical_rank=critical_rank,
                        critical_count=critical_count,
                        strategy_rank=len(self._strategy_order(
                            by_inst[next(iter(joint_change))].cell_type
                        )) + 1,
                        patch_size=len(joint_change),
                        boundary_complexity=boundary_complexity,
                        job=job,
                    )
                )
                job_index += 1

        # Joint auto-enumeration (TCAD sprint 1, hard-4 fix): enumerate
        # multi-gate combinations along the critical path and let OpenSTA
        # pick the best -- no manual selection of the joint set.
        if self.joint_enumerate_depth > 0:
            for change, label in self._joint_enumerate_combos(cells, actionable):
                critical_rank = min(
                    (
                        self.critical_instances.index(inst)
                        for inst in change
                        if inst in self.critical_instances
                    ),
                    default=critical_count - 1,
                )
                job = (
                    "JOINT",
                    "joint",
                    label,
                    change,
                    "JOINT",
                    self.mapped_text,
                    cand_dir,
                    self.top_module,
                    job_index,
                )
                candidate_rows.append(
                    self._proxy_row(
                        instance="JOINT",
                        kind="JOINT",
                        from_type="joint",
                        to_type=label,
                        critical_rank=critical_rank,
                        critical_count=critical_count,
                        strategy_rank=len(self._strategy_order(
                            by_inst[next(iter(change))].cell_type
                        )) + 1,
                        patch_size=len(change),
                        boundary_complexity=boundary_complexity,
                        job=job,
                    )
                )
                job_index += 1

        ranked_rows = rank_real_candidates(
            candidate_rows,
            weights=self.proxy_weights,
        )
        if self.proxy_ranking:
            ordered_rows = ranked_rows
        else:
            ordered_rows = sorted(ranked_rows, key=lambda row: int(row["job_index"]))
        jobs = [
            tuple(row["_job"]) + (self._proxy_metadata(row),)
            for row in ordered_rows
        ]

        results: list[dict] = []
        best_wns = self.baseline_wns
        best_tns = self.baseline_tns
        best_min = self.baseline_min_slack
        best_physical_wns: float | None = None
        best: dict | None = None

        def _accept_result(r: dict) -> bool:
            nonlocal best_wns, best_tns, best_min, best_physical_wns, best
            wns = r["wns"]
            if any(e.get("severity") == "hard" or e.get("type") in {
                "F1_equivalence_failure", "F2_boundary_invalid",
                "F3_patch_too_large", "F5_verification_too_expensive",
            } for e in r.get("failure_events", [])):
                return False
            tns = r.get("tns")
            min_slack = r.get("min_slack")
            if wns is None:
                return False
            if self.physical_gate:
                physical_candidate = r.get("physical_candidate")
                physical_baseline = r.get("physical_baseline")
                physical_delta = r.get("physical_delta")
                physical_candidate_tns = r.get("physical_candidate_tns")
                physical_baseline_tns = r.get("physical_baseline_tns")
                physical_candidate_min_slack = r.get("physical_candidate_min_slack")
                physical_baseline_min_slack = r.get("physical_baseline_min_slack")
                if (r.get("physical_status") != "paired_improved"
                        or physical_candidate is None or physical_baseline is None
                        or physical_candidate_tns is None or physical_baseline_tns is None
                        or physical_candidate_tns < physical_baseline_tns - self.epsilon
                        or (self.hold_required
                            and (physical_baseline_min_slack is None
                                 or physical_candidate_min_slack is None
                                 or physical_candidate_min_slack < physical_baseline_min_slack - self.epsilon))
                        or (not self.hold_mode
                            and (physical_delta is None
                                 or physical_delta + 1e-12
                                 < self.min_physical_gain_ns - self.epsilon))
                        or (self.hold_mode
                            and (physical_baseline_min_slack is None
                                 or physical_candidate_min_slack is None
                                 or physical_candidate_min_slack <= physical_baseline_min_slack + self.epsilon))):
                    return False
                if best_physical_wns is None or physical_candidate > best_physical_wns + self.epsilon:
                    best_physical_wns = physical_candidate
                    best_wns = wns
                    best_tns = tns
                    best_min = physical_candidate_min_slack
                    best = r
                    return True
                return False
            if self.hold_mode:
                # Hold-repair mode: accept a candidate that strictly improves
                # worst min slack (hold) without degrading setup WNS below
                # the baseline.  This lets buffer insertion act as the
                # hold-fixing strategy while setup remains safe.
                if min_slack is not None and best_min is not None and min_slack > best_min + self.epsilon:
                    if (wns >= self.baseline_wns - self.epsilon
                            or wns > best_wns + self.epsilon):
                        best_wns = wns
                        best_tns = tns
                        best_min = min_slack
                        best = r
                        return True
                return False
            if wns > best_wns + self.epsilon or (
                self.tns_aware
                and abs(wns - best_wns) <= self.epsilon
                and tns is not None
                and best_tns is not None
                and tns > best_tns + self.epsilon
            ):
                best_wns = wns
                best_tns = tns
                best = r
                return True
            return False

        if self.workers > 1 and len(jobs) > 1:
            # parallel: evaluate all, keep deterministic full-search result
            with ThreadPoolExecutor(max_workers=self.workers) as ex:
                futures = [ex.submit(self._eval_one, j) for j in jobs]
                results = []
                for job, future in zip(jobs, futures):
                    result = dict(future.result())
                    result.update(job[-1])
                    result["failure_events"] = _normalise_failure_events(
                        result.get("failure_events"),
                        candidate_hash=result.get("candidate_hash") or hashlib.sha256(
                            result.get("candidate_netlist_text", "").encode("utf-8")
                        ).hexdigest(),
                    )
                    result["trial_failure_events"] = _normalise_failure_events(
                        result.get("trial_failure_events"),
                        candidate_hash=result.get("candidate_hash") or hashlib.sha256(
                            result.get("candidate_netlist_text", "").encode("utf-8")
                        ).hexdigest(),
                    )
                    results.append(result)
            for r in results:
                _accept_result(r)
        else:
            # serial: evaluate in priority order; with early_stop, stop at
            # the first candidate that strictly improves WNS (decision-layer
            # value: fewer STA calls for the same result).
            for j in jobs:
                r = dict(self._eval_one(j))
                r.update(j[-1])
                r["failure_events"] = _normalise_failure_events(
                    r.get("failure_events"),
                    candidate_hash=r.get("candidate_hash") or hashlib.sha256(
                        r.get("candidate_netlist_text", "").encode("utf-8")
                    ).hexdigest(),
                )
                r["trial_failure_events"] = _normalise_failure_events(
                    r.get("trial_failure_events"),
                    candidate_hash=r.get("candidate_hash") or hashlib.sha256(
                        r.get("candidate_netlist_text", "").encode("utf-8")
                    ).hexdigest(),
                )
                results.append(r)
                improved_now = _accept_result(r)
                if self.early_stop and improved_now:
                    break

        for r in results:
            trial = dict(r)
            trial["patch_id"] = patch_id
            trial["iteration"] = iteration
            trial["accepted"] = False
            self.trials.append(trial)
        if best is not None:
            self.trials[-len(results) + results.index(best)]["accepted"] = True
        # online decision layer v2: feed every measured trial back so the
        # per-cell-type strategy ordering adapts to this circuit in real time.
        if self.adaptive:
            from_type = ""
            for r in results:
                kind = r.get("kind", "")
                if not kind or kind == "JOINT":
                    continue
                if from_type == "":
                    inst = r.get("instance", "")
                    cell = by_inst.get(inst) if inst else None
                    from_type = cell.cell_type if cell else ""
                self.adaptive_sel.record(
                    from_type or r.get("from_type", ""), kind,
                    accepted=bool(r.get("accepted")),
                )

        # In hold-repair mode success is a strict worst-min-slack improvement
        # (setup WNS is only guarded, see _accept_result); in setup mode it is
        # the usual strict WNS improvement.
        if self.physical_gate:
            improved = bool(
                best is not None
                and best.get("physical_status") == "paired_improved"
                and (
                    (self.hold_mode
                     and best.get("physical_baseline_min_slack") is not None
                     and best.get("physical_candidate_min_slack") is not None
                     and best["physical_candidate_min_slack"]
                     > best["physical_baseline_min_slack"] + self.epsilon)
                    or (not self.hold_mode
                        and best.get("physical_delta") is not None
                        and best["physical_delta"] > self.epsilon)
                )
            )
        elif self.hold_mode:
            improved = best_min > self.baseline_min_slack + self.epsilon
        else:
            improved = (
                best_wns > self.baseline_wns + self.epsilon
                or (self.tns_aware and self.baseline_tns is not None
                    and abs(best_wns - self.baseline_wns) <= self.epsilon
                    and best_tns is not None
                    and best_tns > self.baseline_tns + self.epsilon)
            )
        self.call_log.append(
            {
                "iteration": iteration,
                "patch_id": patch_id,
                "gates": gates,
                "actionable": actionable,
                "n_trials": len(results),
                "best_wns": best_wns,
                "baseline_wns": self.baseline_wns,
                "best_min_slack": best_min,
                "baseline_min_slack": self.baseline_min_slack,
                "improved": improved,
                "accepted": best,
                "proxy_ranking": self.proxy_ranking,
                "proxy_weights": {
                    key: float(value)
                    for key, value in self.proxy_weights.__dict__.items()
                },
                "weights": {
                    k: getattr(weights, k)
                    for k in ("boundary_penalty", "size_penalty",
                              "critical_coverage_reward", "equivalence_stability_reward")
                    if hasattr(weights, k)
                },
                "epsilon": self.epsilon,
            }
        )
        selected_events = list(best.get("failure_events", [])) if best else [
            event for trial in results for event in trial.get("failure_events", [])
        ]
        trial_events = [
            event for trial in results for event in trial.get("failure_events", [])
        ]
        result = {"wns": best_wns, "tns": best_tns, "min_slack": best_min,
                  "improved": improved, "failure_events": selected_events,
                  "trial_failure_events": trial_events,
                  "physical_status": (best or (results[-1] if results else {})).get("physical_status"),
                  "physical_candidate": (best or (results[-1] if results else {})).get("physical_candidate"),
                  "physical_baseline": (best or (results[-1] if results else {})).get("physical_baseline"),
                  "physical_delta": (best or (results[-1] if results else {})).get("physical_delta"),
                  "physical_candidate_tns": (best or (results[-1] if results else {})).get("physical_candidate_tns"),
                  "physical_baseline_tns": (best or (results[-1] if results else {})).get("physical_baseline_tns"),
                  "physical_candidate_min_slack": (best or (results[-1] if results else {})).get("physical_candidate_min_slack"),
                  "physical_baseline_min_slack": (best or (results[-1] if results else {})).get("physical_baseline_min_slack"),
                  "physical_baseline_provenance": (best or (results[-1] if results else {})).get("physical_baseline_provenance"),
                  "physical_candidate_provenance": (best or (results[-1] if results else {})).get("physical_candidate_provenance"),
                  "physical_config": (best or (results[-1] if results else {})).get("physical_config")}
        if best is not None:
            result.update({k: best[k] for k in
                            ("candidate_netlist_text", "candidate_hash",
                             "runtime_s", "physical_baseline", "physical_candidate",
                             "physical_tns", "physical_min_slack", "physical_baseline_tns",
                             "physical_candidate_tns", "physical_baseline_min_slack",
                             "physical_candidate_min_slack", "physical_baseline_provenance",
                             "physical_candidate_provenance", "physical_delta", "physical_status", "rc_config_hash", "physical_config", "critical_instances",
                            "critical_endpoints", "sta_provenance", "acceptance_evidence",
                            "base_netlist_hash", "cache_key", "config_hash", "kind",
                            "topology_metrics") if k in best})
        return result

    def write_trials(self, path: str | Path) -> None:
        payload: dict = {"call_log": self.call_log, "trials": self.trials}
        if self.adaptive:
            payload["adaptive_snapshot"] = self.adaptive_sel.snapshot()
        Path(path).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
