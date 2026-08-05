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
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .buffer_insertion import buffer_candidates, build_net_fanout, insert_buffer
from .gate_sizing import (
    apply_sizing,
    build_available_sizes,
    larger_size_candidates,
    parse_mapped_netlist,
)
from .logic_rewrite import apply_rewrite, equivalence_candidates, parse_liberty_cells
from .opensta import run_opensta_sequential
from .strategy_selector import exploration_order


#: report_checks line: ``   0.36    0.69 v _079_/X (sky130_fd_sc_hd__or3_1)``
_INSTANCE_LINE_RE = re.compile(
    r"^\s+\d+\.\d+\s+\d+\.\d+\s+[v^]\s+(\w+)/\w+\s+\((sky130_fd_sc_hd__\w+)\)",
    re.M,
)
_ENDPOINT_RE = re.compile(r"^Endpoint:\s+([\w\\]+)", re.M)


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
        adaptive: bool = False,
        hold_mode: bool = False,
        baseline_min_slack: float | None = None,
        hold_uncertainty: float = 0.8,
        early_stop: bool = False,
        joint_k: int = 0,
        joint_mix: bool = False,
        clock_port: str = "CK",
        physical_gate: bool = False,
        min_physical_gain_ns: float = 0.010,
        physical_fanout_penalty: float = 1.0,
        physical_depth_penalty: float = 1.0,
        physical_unit_len_um: float = 40.0,
    ) -> None:
        self.mapped_text = mapped_text
        self.top_module = top_module
        self.period = period
        self.lib = parse_liberty_cells(liberty_text)
        self.available = build_available_sizes(liberty_text)
        self.baseline_wns = baseline_wns
        self.baseline_tns: float | None = None
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
        self.adaptive = bool(adaptive)
        if self.adaptive:
            from .adaptive_selector import AdaptiveStrategySelector
            self.adaptive_sel = AdaptiveStrategySelector()
        else:
            self.adaptive_sel = None
        self.early_stop = early_stop
        self.joint_k = max(0, joint_k)
        self.joint_mix = bool(joint_mix)
        self.clock_port = clock_port
        self.physical_gate = bool(physical_gate)
        self.min_physical_gain_ns = min_physical_gain_ns
        self.physical_fanout_penalty = physical_fanout_penalty
        self.physical_depth_penalty = physical_depth_penalty
        self.physical_unit_len_um = physical_unit_len_um
        self.trials: list[dict] = []
        self.call_log: list[dict] = []
        self._call_counter = 0

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
        # decision layer: reorder candidates by the per-cell-type strategy
        # priority table (fallback R,G,B); with --adaptive, use the online
        # UCB-based selector that updates from measured trials instead.
        if self.adaptive:
            order = self.adaptive_sel.priority_order(cell.cell_type)
        else:
            order = self.priority_table.get(cell.cell_type, ("R", "G", "B"))
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

    def _eval_one(self, job: tuple) -> dict:
        inst, cell_type, new_type, pin_map, kind, text, cand_dir, top_module, index = job
        if kind == "JOINT":
            candidate_text = self._apply_joint(text, pin_map)
        else:
            candidate_text = self._apply(text, inst, kind, new_type, pin_map)
        sub = cand_dir / ("%03d_" % index + inst + "_" + kind)
        sub.mkdir(parents=True, exist_ok=True)
        (sub / "mapped.v").write_text(candidate_text, encoding="utf-8")
        res = run_opensta_sequential(
            netlist_path=sub / "mapped.v",
            period=self.period,
            output_dir=sub,
            top_module=top_module,
            hold_uncertainty=self.hold_uncertainty if self.hold_mode else 0.0,
            min_path=self.hold_mode,
            clock_port=self.clock_port,
        )
        # Inner-loop physical gate (review shortboard): an ideal-net gain
        # must clear a minimum threshold before a parasitic-aware SPEF run is
        # even attempted; the candidate is only returned when the SPEF run
        # also improves WNS.  This turns the SPEF check from a post-hoc
        # autopsy into a per-candidate acceptance signal.
        if self.physical_gate and not self.hold_mode:
            ideal_wns = res.get("wns")
            if ideal_wns is not None and ideal_wns > self.baseline_wns + self.min_physical_gain_ns:
                try:
                    from .spef import build_spef, parse_mapped_verilog, write_spef
                    nl = parse_mapped_verilog(sub / "mapped.v")
                    spef = write_spef(
                        sub / "physical.spef",
                        nl,
                        unit_len_um=self.physical_unit_len_um,
                        fanout_penalty=self.physical_fanout_penalty,
                        depth_penalty=self.physical_depth_penalty,
                    )
                    phys = run_opensta_sequential(
                        netlist_path=sub / "mapped.v",
                        period=self.period,
                        output_dir=sub / "physical",
                        top_module=top_module,
                        clock_port=self.clock_port,
                        spef_path=spef,
                    )
                    phys_wns = phys.get("wns")
                    if phys_wns is None or phys_wns <= self.baseline_wns:
                        # physical load failure: the ideal gain does not
                        # survive parasitic RC (F6 signal for the outer loop)
                        res = {**res, "wns": self.baseline_wns,
                               "physical_failure": True,
                               "physical_wns": phys_wns}
                    else:
                        # parasitic-aware gain survives: report the SPEF WNS
                        res = {**res, "wns": phys_wns,
                               "physical_wns": phys_wns}
                except Exception as exc:
                    res = {**res, "physical_gate_error": str(exc)}
        return {
            "instance": inst,
            "kind": kind,
            "from_type": cell_type,
            "to_type": new_type,
            "wns": res.get("wns"),
            "tns": res.get("tns"),
            "min_slack": res.get("min_slack"),
            "min_slack_status": res.get("min_slack_status"),
            "slack": res.get("slack"),
            "slack_status": res.get("slack_status"),
            "physical_failure": res.get("physical_failure", False),
            "physical_wns": res.get("physical_wns"),
            "physical_gate_error": res.get("physical_gate_error"),
        }

    # -- main entry ---------------------------------------------------------

    def __call__(self, patch, weights) -> dict:
        """Evaluate one outer-loop patch candidate with real STA."""
        gates = list(getattr(patch, "gates", []) or [])
        patch_id = getattr(patch, "patch_id", str(patch))
        iteration = len(self.call_log) + 1
        self._call_counter += 1
        cand_dir = self.output_dir / ("iter%03d_cand%03d" % (iteration, self._call_counter))
        cand_dir.mkdir(parents=True, exist_ok=True)

        cells = parse_mapped_netlist(self.mapped_text)
        by_inst = {c.instance: c for c in cells}
        in_patch = [g for g in gates if g in by_inst]
        # order: critical-path instances first, then remaining cut gates
        ordered = [i for i in self.critical_instances if i in in_patch]
        ordered += [g for g in in_patch if g not in ordered]
        # fall back to critical instances when the cut has no real cells
        if not ordered:
            ordered = [i for i in self.critical_instances if i in by_inst]
        actionable = ordered[: self.max_instances]
        if not actionable:
            self.call_log.append(
                {"iteration": iteration, "patch_id": patch_id, "gates": gates,
                 "wns": self.baseline_wns, "improved": False, "reason": "no actionable gates"}
            )
            return {"wns": self.baseline_wns, "improved": False}

        jobs: list[tuple] = []
        job_index = 0
        for inst in actionable:
            for new_type, pin_map, kind in self._candidates_for(cells, inst):
                jobs.append((inst, by_inst[inst].cell_type, new_type, pin_map, kind,
                             self.mapped_text, cand_dir, self.top_module, job_index))
                job_index += 1

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
                jobs.append(("JOINT", "joint", "joint", joint_change, "JOINT",
                             self.mapped_text, cand_dir, self.top_module, job_index))
                job_index += 1

        results: list[dict] = []
        best_wns = self.baseline_wns
        best_tns = self.baseline_tns
        best_min = self.baseline_min_slack
        best: dict | None = None

        def _accept_result(r: dict) -> bool:
            nonlocal best_wns, best_tns, best_min, best
            wns = r["wns"]
            tns = r.get("tns")
            min_slack = r.get("min_slack")
            if wns is None:
                return False
            if self.hold_mode:
                # Hold-repair mode: accept a candidate that strictly improves
                # worst min slack (hold) without degrading setup WNS below
                # the baseline.  This lets buffer insertion act as the
                # hold-fixing strategy while setup remains safe.
                if min_slack is not None and best_min is not None and min_slack > best_min:
                    if wns >= self.baseline_wns or wns > best_wns:
                        best_wns = wns
                        best_tns = tns
                        best_min = min_slack
                        best = r
                        return True
                return False
            if wns > best_wns or (
                self.tns_aware
                and wns == best_wns
                and tns is not None
                and best_tns is not None
                and tns > best_tns
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
                results = [f.result() for f in futures]
            for r in results:
                _accept_result(r)
        else:
            # serial: evaluate in priority order; with early_stop, stop at
            # the first candidate that strictly improves WNS (decision-layer
            # value: fewer STA calls for the same result).
            for j in jobs:
                r = self._eval_one(j)
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
        improved = (
            best_min > self.baseline_min_slack
            if self.hold_mode
            else best_wns > self.baseline_wns
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
                "weights": {
                    k: getattr(weights, k)
                    for k in ("boundary_penalty", "size_penalty",
                              "critical_coverage_reward", "equivalence_stability_reward")
                    if hasattr(weights, k)
                },
            }
        )
        return {"wns": best_wns, "min_slack": best_min, "improved": improved}

    def write_trials(self, path: str | Path) -> None:
        payload: dict = {"call_log": self.call_log, "trials": self.trials}
        if self.adaptive:
            payload["adaptive_snapshot"] = self.adaptive_sel.snapshot()
        Path(path).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\\n",
            encoding="utf-8",
        )
