"""Actual corrected models/edits, historical candidate generation and STA Tcl.

No production module globals are changed. The per-call legacy STA clone routes
its actual subprocess boundary (including retries) through the adapter's ledger.
"""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re
from types import FunctionType, SimpleNamespace

from rseco.buffer_insertion import buffer_candidates, build_net_fanout, insert_buffer
from rseco.gate_sizing import apply_sizing, build_available_sizes, larger_size_candidates, parse_mapped_netlist
from rseco.logic_rewrite import apply_rewrite, parse_liberty_cells
from rseco.real_wns import (build_real_equivalence_checker, build_boundary_closure_checker,
    two_state_sec_unsupported_reason, write_liberty_cell_models)
from rseco.verilog_modules import target_module_text, replace_target_module
import run_hybrid_repair as legacy
import run_r22_cut_ablation as common


class ActualBackend:
    simulated = False

    def __init__(self, circuit, *, liberty_text=None):
        self.circuit = circuit
        self.liberty = common.LIB.read_text(encoding="utf-8") if liberty_text is None else liberty_text
        self.cells = parse_liberty_cells(self.liberty)
        self.available = build_available_sizes(self.liberty)
        self.f1 = build_real_equivalence_checker(self.liberty, top_module=circuit)
        self.f2 = build_boundary_closure_checker(top_module=circuit, liberty_text=self.liberty)
        self.legacy = legacy

    def snapshot(self, text):
        return parse_mapped_netlist(target_module_text(text, self.circuit))

    def candidates(self, snapshot, instance, config):
        # Import the already loaded adapter module through the action's fields
        # rather than sharing mutable state with a production evaluator.
        from adapter import Action
        source = next((cell for cell in snapshot if cell.instance == instance), None)
        if source is None:
            return []
        out = []
        if config.only_strategy in (None, "R"):
            out.extend(Action(instance, "R", target, pin_map) for target, pin_map
                       in self.legacy._build_r_candidates(source.cell_type, self.cells))
        if config.only_strategy in (None, "G"):
            out.extend(Action(instance, "G", target) for target
                       in larger_size_candidates(source.cell_type, self.available))
        if config.enable_buffer and config.only_strategy in (None, "B"):
            # Retain the historical fanout enumeration, including its legacy
            # driver-inclusive count. Actual output roles cannot be B inputs.
            fanout = build_net_fanout(snapshot)
            cell = self.cells.get(source.cell_type)
            outputs = set(cell.output_functions) if cell else set()
            for pin, net, target, new_net in buffer_candidates(snapshot, instance, fanout,
                    buf_types=tuple(config.buf_types), output_pins=outputs):
                out.append(Action(instance, "B", target, pin=pin, new_net=new_net))
        return out

    def apply(self, text, action):
        top = target_module_text(text, self.circuit)
        matches = [cell for cell in parse_mapped_netlist(top) if cell.instance == action.instance]
        if len(matches) != 1:
            raise ValueError("Target instance is missing/duplicated in selected top")
        if action.kind == "B":
            changed = insert_buffer(text, action.instance, action.pin, action.target,
                                    action.new_net, top_module=self.circuit)
        elif action.kind in ("R", "G"):
            updated = (apply_rewrite(top, action.instance, action.target, action.pin_map)
                       if action.kind == "R" else apply_sizing(top, {action.instance: action.target}))
            actual = [cell for cell in parse_mapped_netlist(updated) if cell.instance == action.instance]
            if len(actual) != 1 or actual[0].cell_type != action.target:
                raise ValueError("Requested edit did not reach exactly its physical target")
            changed = replace_target_module(text, self.circuit, updated)
        else:
            raise ValueError("Unsupported strategy: " + action.kind)
        return changed

    def validate(self, base, candidate):
        for role, text in (("base", base), ("candidate", candidate)):
            reason = two_state_sec_unsupported_reason(text, self.cells)
            if reason:
                return {"status": "fail", "reason": role + ": " + reason}
        results = {"F1": self.f1(base, candidate), "F2": self.f2(base, candidate)}
        return {"status": "pass" if all(result.status == "pass" for result in results.values()) else "fail",
                "checks": {name: asdict(result) for name, result in results.items()}}

    def measure(self, text, directory, role, invoke, config):
        original = self.legacy.run_opensta
        namespace = {**original.__globals__, "subprocess": SimpleNamespace(run=invoke)}
        scoped = FunctionType(original.__code__, namespace, original.__name__, original.__defaults__, original.__closure__)
        scoped.__kwdefaults__ = original.__kwdefaults__
        result = scoped(Path(directory) / "mapped.v", config.period, Path(directory),
                        top_module=self.circuit, multi_path=role in ("baseline", "refresh"),
                        clock_port=config.clock_port)
        log = Path(directory) / "sta.log"
        result["critical"] = self.legacy._critical_instances_from_sta(log.read_text(encoding="utf-8")) if log.is_file() else []
        return result

    def prepare_sec(self, initial, final, directory):
        directory.mkdir()
        gold, gate, helpers = common.sec_designs(initial, final, self.circuit)
        splits = {"gold.v": gold, "gate.v": gate, "helpers.v": helpers}
        for name, text in splits.items():
            (directory / name).write_text(text, encoding="utf-8")
        masked = re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"', " ", initial + "\n" + final)
        used = set(re.findall(r"\b(sky130_fd_sc_hd__\w+)\s+[^\s(]+\s*\(", masked))
        model_path = directory / "model_preflight.v"
        write_liberty_cell_models(self.liberty, model_path, used_cells=used)
        return {"splits": splits, "model_path": str(model_path),
                "model_sha256": common.sha(model_path), "used_types": sorted(used),
                "liberty_text_utf8_sha256": hashlib.sha256(self.liberty.encode("utf-8")).hexdigest()}

    def sec(self, initial, final, directory):
        # RGB edits preserve helper definitions. common final_sec independently
        # verifies that equality before using its shared-helper proof path.
        return common.final_sec(initial, final, self.circuit, directory)
