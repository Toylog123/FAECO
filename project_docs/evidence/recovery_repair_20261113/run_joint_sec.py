"""Pinned s382 SEC adapter for a root-selected, completed repair arm.

Preparation alone runs no proof. Invoke with a registered arm only after selection.
This proves two-state logical equivalence, not physical or timing feasibility.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "code/scripts"))
sys.path.insert(0, str(ROOT / "code/src"))
import run_r22_cut_ablation as sec

spec = importlib.util.spec_from_file_location("structure_check", HERE / "structure_reader.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
TAP = "sky130_fd_sc_hd__tapvpwrvgnd_1"
PRIOR_ADAPTER_PATH = "project_docs/evidence/recovery_qualification_20261112/run_pilot_sec.py"
PRIOR_ADAPTER_SHA256 = "f7b6a52eabb5263985ce20d5c12befe0b2a48f6d28e8d29dd852b0a0c8f7440b"
SEC_SOURCE_SHA256 = "046b383f50ec540f295ab9a008e5d1c394c2fb92740c5dd8be0391861378ceea"
READER_SHA256 = "db708d1360e74efca225c9b2b251802aed7958ceec9feb2fc256b3b42cf9def7"
LIBERTY_SHA256 = "ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9"


def project(path):
    text = path.read_text(encoding="utf-8")
    parsed, ports = checker.Reader(text).parse()
    removed = sorted(name for name, inst in parsed["instances"].items() if inst["cell"] == TAP)
    if not all(not parsed["instances"][name]["pins"] for name in removed):
        raise ValueError("Connected physical tap cannot be removed")
    matched = []

    def drop(match):
        name = match.group(1)
        if name not in removed:
            raise ValueError("Removal is not in parsed tap set")
        matched.append(name)
        return ""

    projected = re.sub(r"(?m)^[ \t]*" + TAP + r"[ \t]+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(\s*\)\s*;[ \t]*\r?\n?", drop, text)
    if sorted(matched) != removed:
        raise ValueError("Removal spans do not exactly cover parsed tap set")
    expected = dict(parsed, instances={name: inst for name, inst in parsed["instances"].items() if name not in removed})
    actual, actual_ports = checker.Reader(projected).parse()
    if actual != expected or ports != actual_ports:
        raise ValueError("Projection changed non-tap logical structure")
    return projected, removed


def main(arm):
    if not re.fullmatch(r"[A-Z0-9_]+", arm):
        raise ValueError("Invalid arm identifier")
    pinned_plans = {"JOINT_PLAN.json": "eff0bac1e359148aaf228703395ae9d20613f6ad0db6959fcc96e63183182622"}
    matches = []
    for name, expected in pinned_plans.items():
        candidate = HERE / name
        if sec.sha(candidate) != expected:
            raise ValueError(f"Registration plan changed: {candidate}")
        plan = json.loads(candidate.read_text(encoding="utf-8"))
        for category in ("singletons", "combinations"):
            if arm in plan.get(category, {}):
                matches.append((candidate, category, plan[category][arm]))
    if len(matches) != 1:
        raise ValueError("Arm must match exactly one pinned registration entry")
    plan_path, registration_category, registered_restored = matches[0]
    for path, expected in ((Path(sec.__file__), SEC_SOURCE_SHA256),
                           (HERE / "structure_reader.py", READER_SHA256),
                           (sec.LIB, LIBERTY_SHA256)):
        if sec.sha(path) != expected:
            raise ValueError(f"Pinned proof input changed: {path}")
    out = HERE / "sec" / ("CONTROL_vs_" + arm + "_models_v2")
    out.mkdir(parents=True, exist_ok=False)
    sources, removed, texts = {}, {}, {}
    for side, label in (("gold", "CONTROL"), ("gate", arm)):
        base = HERE / "inputs" / "CONTROL" if side == "gold" else HERE / "runs" / arm
        manifest = json.loads((base / "manifest.json").read_text())
        if manifest["flow"]["returncode"] != 0 or any(manifest[c]["returncode"] != 0 for c in ("ideal", "propagated")):
            raise ValueError("Final physical endpoint is not complete")
        if side == "gate" and manifest["restored_instances"] != registered_restored:
            raise ValueError("Physical manifest differs from registered restoration set")
        source = base / "routed.v"
        texts[side], removed[side] = project(source)
        normalized = out / (side + "_normalized.v")
        normalized.write_text(texts[side], encoding="utf-8", newline="\n")
        sources[side] = {"path": str(source.relative_to(ROOT)), "original_sha256": sec.sha(source),
                         "normalized_sha256": sec.sha(normalized), "removed_ids": removed[side],
                         "physical_manifest_sha256": sec.sha(base / "manifest.json")}
    if removed["gold"] != removed["gate"]:
        raise ValueError("Tap removal sets differ")
    parsed = {side: checker.Reader(text).parse()[0] for side, text in texts.items()}
    used = {inst["cell"] for design in parsed.values() for inst in design["instances"].values()}
    from rseco.logic_rewrite import parse_liberty_cells
    cells = parse_liberty_cells(sec.LIB.read_text(encoding="utf-8"))
    if not used <= set(cells):
        raise ValueError("Full parsed cell set is not covered by Liberty")
    cell_counts = {side: {"all_instances": len(design["instances"]),
                         "sequential_instances": sum(bool(cells[x["cell"]].sequential_kind) for x in design["instances"].values())}
                   for side, design in parsed.items()}
    if any(v != {"all_instances": 102, "sequential_instances": 21} for v in cell_counts.values()):
        raise ValueError("s382 expected 102 functional cells including 21 sequential cells")
    receipt = {"scope": "two-state sequential equivalence of explicitly projected final physical exports",
               "pair": ["CONTROL", arm], "inputs": sources,
               "plan_path": str(plan_path.relative_to(ROOT)), "plan_sha256": sec.sha(plan_path),
               "registration_category": registration_category, "registered_restored": registered_restored,
               "adapted_from": {"path": PRIOR_ADAPTER_PATH, "sha256": PRIOR_ADAPTER_SHA256},
               "copied_from_driver": {"path": "project_docs/evidence/recovery_repair_20261113/run_repair_sec.py", "sha256": "056e9394c2926450ea2cd2bd7676e401ba911e9a413b60de3d0735f7d05aae07"},
               "prover": "/usr/bin/yosys in WSL Ubuntu; same pinned final_sec engine",
               "expected_counts": "102 total functional instances, including 21 FFs (not 102+21)",
               "liberty_path": str(sec.LIB.relative_to(ROOT)), "liberty_sha256": sec.sha(sec.LIB),
               "sec_source_sha256": sec.sha(Path(sec.__file__)), "driver_sha256": sec.sha(Path(__file__)),
               "checker_sha256": sec.sha(HERE / "structure_reader.py"),
               "all_used_cells": sorted(used), "cell_counts": cell_counts,
               "adapter": "replace incomplete legacy used_cells with complete Reader enumeration; no instance renaming",
               "timeout_s": 180, "status": "registered_before_prover"}
    sec.save(out / "receipt.json", receipt)
    print(json.dumps({"pair": arm, "removed": len(removed["gold"]), "stage": "starting SEC"}), flush=True)
    legacy_writer = sec.write_liberty_cell_models
    def complete_models(liberty_text, output_path, *, used_cells=None, **kwargs):
        if used_cells is None or not set(used_cells) <= used:
            raise ValueError("Legacy model scanner returned unexpected cell types")
        if liberty_text != sec.LIB.read_text(encoding="utf-8") or sec.sha(sec.LIB) != receipt["liberty_sha256"]:
            raise ValueError("Liberty changed before model generation")
        receipt["legacy_scanner_omitted_cells"] = sorted(used - set(used_cells))
        return legacy_writer(liberty_text, output_path, used_cells=used, **kwargs)
    sec.write_liberty_cell_models = complete_models
    try:
        result = sec.final_sec(texts["gold"], texts["gate"], "s382", out / "proof")
    finally:
        sec.write_liberty_cell_models = legacy_writer
    receipt["result"] = result
    receipt["status"] = result["status"]
    receipt["proof_sha256"] = {p.name: sec.sha(p) for p in sorted((out / "proof").iterdir()) if p.is_file()}
    receipt["sources_unchanged"] = all(sec.sha(ROOT / value["path"]) == value["original_sha256"] for value in sources.values())
    sec.save(out / "receipt.json", receipt)
    print(json.dumps({"pair": arm, "status": receipt["status"], "sources_unchanged": receipt["sources_unchanged"]}), flush=True)
    return 0 if receipt["status"] == "pass" and receipt["sources_unchanged"] else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arm", help="Root-selected registered arm under runs/")
    args = parser.parse_args()
    raise SystemExit(main(args.arm))
