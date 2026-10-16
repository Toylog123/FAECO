"""Register exact historical A proof objects, then reuse the independent SEC runner.

--dry-run only reads archives and hashes sources/Liberty; it never invokes EDA.
Register into a fresh directory after the production commit before formal use.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "code/src"))
from rseco.verilog_modules import module_spans, target_module_text

CIRCUITS = ("s382", "s420", "s641", "s713", "s832", "s953")
AUDIT_DIR = "project_docs/evidence/r22_historical_correctness_20261014"
CROSSWALK = "experiments/20260807_real_pr_iscas8/pre_layout_audit_summary.json"
LIBRARY = "data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
PROOF_SCRIPTS = ("code/scripts/run_r22_cut_ablation.py", "code/scripts/run_sequential_timing_check.py",
                 "code/scripts/run_with_timeout.sh", "code/scripts/python/prove_historical_a_r22.py")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def relative_path(root, path):
    path = Path(str(path).replace("\\", "/"))
    absolute = (root / path).resolve()
    if not absolute.is_relative_to(root.resolve()):
        raise ValueError(f"Input outside repository: {path}")
    return absolute.relative_to(root.resolve()).as_posix()


def git_identity(root):
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                          capture_output=True, text=True, timeout=15).stdout.strip()
    status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--", "code"],
                            cwd=root, check=True, capture_output=True, text=True, timeout=15).stdout
    return {"head": head, "source_tree_clean": not bool(status.strip())}


def source_pin(root):
    sources = sorted((root / "code/src/rseco").glob("*.py")) + [root / name for name in PROOF_SCRIPTS]
    if not sources:
        raise ValueError("Missing proof sources")
    return {**git_identity(root), "files": {relative_path(root, path): sha(path) for path in sources}}


def build_manifest(root=ROOT, *, circuits=CIRCUITS, liberty=None):
    root = Path(root).resolve()
    files, trailers = {}, {}

    def register(path, role):
        name = relative_path(root, path)
        file = root / name
        if name not in files:
            files[name] = {"path": name, "sha256": sha(file), "bytes": file.stat().st_size, "roles": []}
        if role not in files[name]["roles"]:
            files[name]["roles"].append(role)
        return {key: files[name][key] for key in ("path", "sha256", "bytes")}

    def read(path, role):
        item = register(path, role)
        return (root / item["path"]).read_text(encoding="utf-8-sig")

    def load(path, role):
        text = read(path, role).lstrip()
        value, end = json.JSONDecoder().raw_decode(text)
        trailer = text[end:].strip()
        if trailer:
            if trailer != r"\n":
                raise ValueError(f"Unexpected trailing JSON content: {path}")
            trailers[relative_path(root, path)] = trailer
        return value

    audit = load(f"{AUDIT_DIR}/correctness_audit.json", "prior classification and exact text hashes")
    register(f"{AUDIT_DIR}/audit.py", "archived binding audit implementation; not executed")
    crosswalk = load(CROSSWALK, "explicit A-prime baseline/fixed artifact crosswalk")
    library = register(liberty or root / LIBRARY, "actual Liberty for regenerated SEC models")
    cases = []
    for circuit in circuits:
        if circuit not in CIRCUITS:
            raise ValueError(f"Unregistered A recovery circuit: {circuit}")
        rows = [row for row in audit["runs"] if row["family"] == "A" and row["circuit"] == circuit]
        if len(rows) != 1 or rows[0]["classification"] != "unidentified":
            raise ValueError(f"Ambiguous/mismatched A audit row: {circuit}")
        row = rows[0]
        pair = {}
        for variant in ("baseline", "fixed"):
            matches = [item for item in crosswalk["records"] if item["circuit"] == circuit and item["variant"] == variant]
            if len(matches) != 1:
                raise ValueError(f"Ambiguous counterpart crosswalk: {circuit}/{variant}")
            pair[variant] = matches[0]["netlist"]
        if relative_path(root, pair["fixed"]) != relative_path(root, row["final_source"]):
            raise ValueError(f"Final counterpart differs from archived audit: {circuit}")
        run = relative_path(root, row["run"])
        result = load(f"{run}/outerloop_result.json", "original A result (no final runtime hash inferred)")
        if result.get("circuit") != circuit or result.get("success") is not True:
            raise ValueError(f"Original result does not identify successful A run: {circuit}")
        ledger = load(f"{run}/eval_trials.json", "original A accepted action ledger")
        accepted = [item for item in ledger["trials"] if item.get("accepted") is True]
        keys = ("instance", "kind", "to_type")
        if not accepted or [{k: t.get(k) for k in keys} for t in accepted] != [{k: t.get(k) for k in keys} for t in row["accepted_actions"]]:
            raise ValueError(f"Accepted ledger cannot identify the counterpart: {circuit}")
        initial = read(pair["baseline"], "A-prime counterpart baseline; distinct from original when normalized")
        final = read(pair["fixed"], "accepted counterpart (new SEC gate)")
        gold_path = f"{run}/mapped.v"
        original = read(gold_path, "actual original A mapped baseline (new SEC gold)")
        for label, text in (("initial", initial), ("final", final)):
            if text_sha(text) != row["structure"][f"{label}_text_hash"] or text_sha(target_module_text(text, circuit)) != row["structure"][f"{label}_top_hash"]:
                raise ValueError(f"Input text/hash differs from archived A audit: {circuit}/{label}")
        typed = {}
        for action in accepted:
            if action["kind"] == "JOINT":
                typed.update(item.split(":", 1) for item in action["to_type"].split(","))
            elif action["kind"] in ("R", "G"):
                typed[action["instance"]] = action["to_type"]
            else:
                raise ValueError(f"Unidentifiable accepted action kind: {action['kind']}")
        reconstructed = initial
        for instance, cell in typed.items():
            if not re.fullmatch(r"sky130_fd_sc_hd__\w+", cell):
                raise ValueError("Unknown accepted library cell")
            pattern = r"\bsky130_fd_sc_hd__\w+(?=\s+" + re.escape(instance) + r"\s*\()"
            reconstructed, count = re.subn(pattern, cell, reconstructed)
            if count != 1:
                raise ValueError(f"Accepted physical instance missing/duplicate: {instance}")
        if reconstructed != final:
            raise ValueError(f"Final artifact is not exact accepted type-only counterpart: {circuit}")
        helpers = [{m.name: m.text for m in module_spans(text) if m.name != circuit} for text in (original, final)]
        if helpers[0] != helpers[1]:
            raise ValueError(f"Original/counterpart helpers differ: {circuit}")
        old_sec = dict(row["sec"])
        for role in ("script", "log", "gold_file", "gate_file"):
            register(old_sec[role], f"old SEC {role}; not new proof evidence")
        cases.append({"circuit": circuit, "status": "pending_sec", "gold": register(gold_path, "new proof gold"),
                      "gate": register(pair["fixed"], "new proof gate"),
                      "counterpart_baseline": register(pair["baseline"], "crosswalk witness"),
                      "accepted_actions": accepted, "old_sec": old_sec,
                      "binding": {"accepted_type_only_reconstruction_exact": True,
                                  "original_equals_counterpart_baseline": original == initial,
                                  "baseline_difference_requires_main_proof": original != initial,
                                  "runtime_final_hash_recovered": False}})
    return {"schema": "r22-historical-a-sec-recovery-v1", "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "eda_executed": False, "source_pin": source_pin(root), "liberty": library,
            "files": files, "json_trailers": trailers, "cases": cases,
            "proof_method": "reuse run_r22_cut_ablation.final_sec; equiv_simple + equiv_induct -seq 10 + equiv_status -assert",
            "binding_limit": "Current archived artifacts and accepted metadata; not reconstructed historical runtime input hashes."}


def validate_manifest(manifest, root=ROOT):
    root = Path(root)
    if manifest.get("schema") != "r22-historical-a-sec-recovery-v1":
        raise ValueError("Unknown manifest schema")
    if not manifest["source_pin"]["source_tree_clean"]:
        raise ValueError("Provisional dirty registration: register again after the production commit")
    if source_pin(root) != manifest["source_pin"]:
        raise ValueError("Source pin changed or source tree is no longer frozen")
    for name, item in manifest["files"].items():
        if relative_path(root, name) != name or sha(root / name) != item["sha256"]:
            raise ValueError(f"Input hash changed: {name}")
    fresh = build_manifest(root, circuits=tuple(case["circuit"] for case in manifest["cases"]), liberty=root / manifest["liberty"]["path"])
    if any(fresh[key] != manifest[key] for key in ("files", "cases", "liberty", "json_trailers")):
        raise ValueError("Input binding changed from registration")


def load_prover(root=ROOT):
    sys.path.insert(0, str(root / "code/scripts"))
    spec = importlib.util.spec_from_file_location("r22_a_independent_sec", root / "code/scripts/run_r22_cut_ablation.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.final_sec, module.LIB


def save_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def run_case(manifest, case, root, output):
    root, output = Path(root), Path(output)
    if output.exists():
        raise ValueError(f"Refusing to overwrite proof directory: {output}")
    output.mkdir(parents=True)
    receipt = {"circuit": case["circuit"], "status": "blocked", "proof_started": False, "proof_returncode": None,
               "source_pin": manifest["source_pin"], "gold": case["gold"], "gate": case["gate"], "liberty": manifest["liberty"]}
    try:
        validate_manifest(manifest, root)
        prover, library = load_prover(root)
        if relative_path(root, library) != manifest["liberty"]["path"] or sha(library) != manifest["liberty"]["sha256"]:
            raise ValueError("SEC prover Liberty differs from registration")
        initial = (root / case["gold"]["path"]).read_text(encoding="utf-8-sig")
        final = (root / case["gate"]["path"]).read_text(encoding="utf-8-sig")
        receipt["proof_started"] = True
        result = prover(initial, final, case["circuit"], output)
        receipt.update(status=result["status"], proof_returncode=result.get("returncode"), proof_result=result)
        validate_manifest(manifest, root)
        if result["status"] == "pass":
            if result.get("returncode") != 0:
                raise ValueError("SEC pass has nonzero/absent process exit code")
            for name, expected in (("initial_raw.v", initial), ("final_raw.v", final)):
                if (output / name).read_text(encoding="utf-8-sig") != expected:
                    raise ValueError("SEC raw objects differ from registered pair")
            if result.get("initial_sha256") != sha(output / "initial_raw.v") or result.get("final_sha256") != sha(output / "final_raw.v"):
                raise ValueError("SEC result hashes do not bind actual raw inputs")
            if not all((output / name).is_file() for name in ("cells.v", "sec.ys", "sec.log", "result.json", "gold.v", "gate.v", "helpers.v")):
                raise ValueError("SEC pass lacks complete model/script/log receipt")
    except Exception as error:
        receipt.update(status="blocked", error=str(error))
    receipt["artifacts"] = {path.name: sha(path) for path in sorted(output.iterdir()) if path.is_file()}
    save_new(output / "receipt.json", receipt)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    if args.dry_run:
        manifest = build_manifest()
        save_new(args.manifest, manifest)
        print(json.dumps({"cases": len(manifest["cases"]), "eda_executed": False,
                          "source_tree_clean": manifest["source_pin"]["source_tree_clean"], "manifest": str(args.manifest)}))
        return 0
    if args.output_dir is None:
        parser.error("--output-dir is required for formal SEC")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    for case in manifest["cases"]:
        receipt = run_case(manifest, case, ROOT, args.output_dir / case["circuit"])
        print(json.dumps({"circuit": case["circuit"], "status": receipt["status"], "proof_returncode": receipt["proof_returncode"]}))
        if receipt["status"] != "pass":
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
