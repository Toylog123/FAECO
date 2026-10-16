"""Prepare fresh mapped inputs for a registered C-prime v3; never run STA.

Dry-run only reads hashes and statically checks any existing inputs. Execution
requires the manifest HEAD and a clean code tree. A failed/incomplete mapping
is retained for attribution and is never automatically overwritten/retried.
This preparation/static receipt is not an RTL-to-mapped equivalence proof.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import importlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code/scripts"))
sys.path.insert(0, str(ROOT / "code/src"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _save_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def _code_state(root, expected_head):
    def git(*args):
        result = subprocess.run(["git", *args], cwd=root, capture_output=True,
                                text=True, encoding="utf-8", errors="strict", timeout=30)
        if result.returncode:
            raise RuntimeError("Git identity check failed: " + result.stderr)
        return result.stdout.strip()
    if git("rev-parse", "HEAD") != expected_head:
        raise RuntimeError("HEAD differs from registered manifest")
    tool_path = Path(__file__).resolve().relative_to(root).as_posix()
    if git("status", "--porcelain", "--untracked-files=all", "--", "code", tool_path):
        raise RuntimeError("Execution requires a clean code tree and committed preparation tool")


def static_preflight(text, circuit, liberty_text):
    """Real validators/model metadata only; no external tool or proof invoked."""
    from rseco.logic_rewrite import parse_liberty_cells
    from rseco.real_wns import (validate_cell_input_connections,
        two_state_sec_unsupported_reason, build_boundary_closure_checker,
        _assert_unique_physical_instances)
    from rseco.verilog_modules import module_spans
    cells = parse_liberty_cells(liberty_text)
    modules = module_spans(text)
    if circuit not in {module.name for module in modules}:
        raise ValueError("Mapped top absent: " + circuit)
    for module in modules:
        _assert_unique_physical_instances(module.text)
    validate_cell_input_connections(text, cells)
    reason = two_state_sec_unsupported_reason(text, cells)
    if reason is not None:
        raise ValueError(reason)
    f2 = build_boundary_closure_checker(top_module=circuit, liberty_text=liberty_text)(text, text)
    if f2.status != "pass":
        raise ValueError("F2 identity preflight failed: " + str(f2))
    masked = re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"', " ", text)
    used = sorted(set(re.findall(r"\b(sky130_fd_sc_hd__\w+)\s+[^\s(]+\s*\(", masked)))
    if not used or any(name not in cells for name in used):
        raise ValueError("Mapped input lacks a known actual-Liberty model scope")
    models = {name: asdict(cells[name]) for name in used}
    model_sha = hashlib.sha256(json.dumps(models, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"used_types": used, "module_names": [module.name for module in modules],
            "required_input_check": "pass", "physical_instance_uniqueness": "pass",
            "two_state_sec_unsupported_reason": None, "f2_identity_status": f2.status,
            "model_scope": models, "model_scope_sha256": model_sha,
            "proof_status": "not_run; static preparation is not equivalence"}


def prepare(output, circuits=None, *, dry_run=False, common=None,
            code_state_checker=None, static_checker=None):
    common = common or importlib.import_module("run_r22_cut_ablation")
    checker = static_checker or static_preflight
    output = Path(output).resolve()
    if any(part in {"20261014_r22_cut_ablation", "20261016_r22_cut_ablation_v2"}
           for part in output.parts):
        raise RuntimeError("Old v1/v2 directories are immutable")
    manifest_path = output / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("Register the common manifest first; preparation does not register it")
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    if manifest.get("family") != "C-prime-r22":
        raise RuntimeError("Expected a registered common C-prime manifest")
    registered = manifest["circuits"]
    if (not registered or len(set(registered)) != len(registered)
            or any(c not in common.CIRCUITS for c in registered)
            or set(manifest["inputs"]) != set(registered)):
        raise RuntimeError("Manifest circuit/input registration is inconsistent")
    circuits = list(registered if circuits is None else circuits)
    if not circuits or len(set(circuits)) != len(circuits) or any(c not in registered for c in circuits):
        raise RuntimeError("Use distinct registered circuits")
    tool_sha = sha(__file__)
    code_check = code_state_checker or (lambda head: _code_state(common.ROOT, head))
    verified_artifacts = {}

    def verify():
        if manifest_path.read_bytes() != manifest_bytes:
            raise RuntimeError("Registered manifest changed")
        if common.source_manifest() != manifest["source_manifest"]:
            raise RuntimeError("Registered executable source changed")
        if sha(common.LIB) != manifest["lib_sha256"]:
            raise RuntimeError("Registered Liberty changed")
        for circuit in registered:
            if sha(common.ROOT / "data/raw/benchmarks/raw/iscas89" / (circuit + ".v")) != manifest["inputs"][circuit]:
                raise RuntimeError("Registered RTL changed: " + circuit)
        if sha(__file__) != tool_sha:
            raise RuntimeError("Preparation tool changed during execution")
        for circuit, artifacts in verified_artifacts.items():
            for name, expected_sha in artifacts.items():
                path = output / "inputs" / circuit / name
                if not path.is_file() or sha(path) != expected_sha:
                    raise RuntimeError("Previously checked input artifact changed: " + circuit + "/" + name)
        if not dry_run:
            code_check(manifest["git_head"])

    verify()
    preflight_path = output / "preflight.json"
    previous = json.loads(preflight_path.read_text(encoding="utf-8")) if preflight_path.exists() else None
    if previous is not None and previous.get("circuits") != circuits:
        raise RuntimeError("Existing preflight selection differs; do not overwrite or extend it")
    liberty_text = common.LIB.read_text(encoding="utf-8")
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    summary = {"schema": "r22-cprime-v3-prepared-inputs-v1", "status": "prepared",
               "circuits": circuits, "manifest_sha256": manifest_sha,
               "source_manifest": manifest["source_manifest"], "git_head": manifest["git_head"],
               "lib_sha256": manifest["lib_sha256"], "prepare_tool_sha256": tool_sha,
               "mapping_equivalence": "not_run", "sta_executed": False, "inputs": []}

    def inspect(circuit, create):
        baseline = output / "inputs" / circuit
        receipt_path = baseline / "input.json"
        mapped = baseline / "mapped.v"
        source = common.ROOT / "data/raw/benchmarks/raw/iscas89" / (circuit + ".v")
        if receipt_path.exists():
            try:
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                expected = {"source_manifest": manifest["source_manifest"],
                            "source_sha256": manifest["inputs"][circuit], "mapped_sha256": sha(mapped)}
                if receipt != expected:
                    raise RuntimeError("Mapped input/source receipt mismatch: " + circuit)
            except (OSError, KeyError, ValueError) as error:
                raise RuntimeError("Incomplete mapped input receipt: " + circuit) from error
        elif baseline.exists() and any(baseline.iterdir()):
            raise RuntimeError("Unregistered mapped input or partial mapping; do not overwrite: " + circuit)
        elif not create:
            return {"circuit": circuit, "status": "would_map", "source_sha256": manifest["inputs"][circuit]}
        else:
            verify()
            baseline.mkdir(parents=True, exist_ok=True)
            print("MAP " + circuit, flush=True)
            errors = common.run_yosys_mapping(source, baseline)
            verify()
            if errors or not mapped.is_file():
                raise RuntimeError("Mapping failed; retained for attribution: " + str(errors))
        mapped_sha = sha(mapped)
        text = mapped.read_text(encoding="utf-8")
        details = checker(text, circuit, liberty_text)
        if details.get("two_state_sec_unsupported_reason") is not None or details.get("f2_identity_status") != "pass":
            raise RuntimeError("Static preflight did not pass: " + circuit)
        verify()
        if sha(mapped) != mapped_sha:
            raise RuntimeError("Mapped input changed during static preflight: " + circuit)
        if not receipt_path.exists() and create:
            _save_new(receipt_path, {"source_manifest": manifest["source_manifest"],
                      "source_sha256": manifest["inputs"][circuit], "mapped_sha256": mapped_sha})
        artifacts = {name: sha(baseline / name) for name in
                     ("mapped.v", "map.ys", "map.log", "circuit_pre.v", "input.json") if (baseline / name).is_file()}
        verified_artifacts[circuit] = artifacts
        print("STATIC_DONE " + circuit + " mapped_sha256=" + mapped_sha, flush=True)
        return {"circuit": circuit, "source_sha256": manifest["inputs"][circuit],
                "mapped_sha256": mapped_sha, "artifacts_sha256": artifacts, **details}

    # Precheck the complete selection before launching the first mapping. A bad
    # later receipt must not allow an earlier unprepared case to be launched.
    preview_rows = [inspect(circuit, False) for circuit in circuits]
    if dry_run:
        verify()
        return {**summary, "status": "dry_run", "inputs": preview_rows,
                "external_processes_executed": False, "code_clean_check": "execution_only"}
    lock = output / ".prepare_inputs.lock"
    try:
        stream = lock.open("x", encoding="utf-8")
    except FileExistsError as error:
        raise RuntimeError("Prior/concurrent preparation lock exists; inspect before retry") from error
    try:
        with stream:
            stream.write(tool_sha + "\n")
        if previous is not None:
            summary["inputs"] = [inspect(circuit, False) for circuit in circuits]
            verify()
            if summary != previous:
                raise RuntimeError("Existing preflight receipt mismatch; do not overwrite")
        else:
            summary["inputs"] = [inspect(circuit, True) for circuit in circuits]
            verify()
            _save_new(preflight_path, summary)
        verify()
        return summary
    finally:
        lock.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--circuits", help="Comma-separated registered cases; default all registered")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    result = prepare(args.output_dir, None if args.circuits is None else args.circuits.split(","), dry_run=args.dry_run)
    print(json.dumps({"status": result["status"], "circuits": result["circuits"],
        "manifest_sha256": result["manifest_sha256"], "sta_executed": False,
        "preflight_path": str(args.output_dir.resolve() / "preflight.json"),
        "inputs": [{key: row[key] for key in ("circuit", "status", "mapped_sha256", "used_types")
                    if key in row} for row in result["inputs"]]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
