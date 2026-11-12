"""Pinned s382 SEC adapter for a root-selected, completed repair arm.

Default is read-only preflight. Explicit --execute proves only the all-nine selected endpoint.
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
PRIOR_ADAPTER_PATH = "labels/provenance/run_repair_sec.py"
PRIOR_ADAPTER_SHA256 = "056e9394c2926450ea2cd2bd7676e401ba911e9a413b60de3d0735f7d05aae07"
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


import analyze_repair as audit
import local_data as data
import run_search
import selection

PLAN_SHA256 = "2efbac2bfaf603fd2814e1e1ba00e0c6254dc7e5aeaf1c314f3fe169b5fcf45e"


def check_selection_header(summary, plan):
    audit.require(summary.get('status') == 'all9_finished', 'All nine must finish before SEC')
    audit.require(summary.get('actual_new_cost') == {'charged_verifications':9,'completed_routes':9,'completed_sta':18},
                  'Incomplete actual measurement accounting')
    jobs = summary.get('jobs', [])
    audit.require([j['arm'] for j in jobs] == plan['measurement_order'] and
                  all(j.get('returncode') == 0 and j.get('status') == 'complete' for j in jobs), 'Incomplete or invalid jobs')
    selected = summary.get('selected', {})
    arm = selected.get('candidate_id')
    audit.require(arm != plan['seed']['candidate_id'], 'Seed selected: reuse accepted seed proof; duplicate SEC prohibited')
    audit.require(arm in plan['singletons'] and selected.get('evidence_kind') == 'actual' and
                  selected.get('sec_status') == 'pending' and summary.get('next_sec') == 'selected_exact_endpoint_pending_SEC',
                  'Not a registered actual selected endpoint awaiting SEC')
    return arm


def prepare():
    audit.require(sec.sha(HERE/'PLAN.json') == PLAN_SHA256, 'Wrong frozen search plan')
    audit.require(sec.sha(HERE/PRIOR_ADAPTER_PATH) == PRIOR_ADAPTER_SHA256, 'Copied proof adapter drift')
    plan, dataset = run_search.preflight()
    summary = data.read('SEARCH_SUMMARY.json')
    arm = check_selection_header(summary, plan)
    audit.require(summary['plan_sha256'] == PLAN_SHA256 and
                  summary['runner_sha256'] == sec.sha(HERE/'run_search.py') and
                  summary['driver_sha256'] == sec.sha(HERE/'physical_probe.py'), 'Search execution identity mismatch')
    audit.require(sec.sha(HERE/'SEARCH_RECEIPT.json') == sec.sha(HERE/'SEARCH_SUMMARY.json'), 'Final receipt/summary differ')
    areas, control, recovered, recipe, seed, _ = dataset
    batch = {j['arm']:j for j in summary['jobs']}
    rows = []; points = {}
    for name in plan['measurement_order']:
        row = audit.audit_arm(name, plan['singletons'][name], control, recovered, recipe, areas, selection.TOL, batch)
        audit.require(row['status'].startswith('validated_'), 'Actual arm audit failed: '+name)
        rows.append(row)
        points[name] = data.point(row, 'runs/'+name)
    audit.require(rows == summary['rows'] and points == summary['points'], 'Raw endpoints disagree with final summary')
    replay = selection.replay(plan['orders'], points, control, seed)
    audit.require(replay == summary['traces'] and replay['area_first'][-1]['selected'] == summary['selected'],
                  'Selected endpoint is not the complete-pool audited optimum')
    audit.require(selection.judge_actual(summary['selected'], control)['feasible'], 'Selected endpoint fails strict actual gate')
    bindings = {'PLAN.json':PLAN_SHA256, 'SEARCH_SUMMARY.json':sec.sha(HERE/'SEARCH_SUMMARY.json'),
                'SEARCH_RECEIPT.json':sec.sha(HERE/'SEARCH_RECEIPT.json'),
                'inputs/CONTROL/routed.v':sec.sha(HERE/'inputs/CONTROL/routed.v'),
                'inputs/CONTROL/manifest.json':sec.sha(HERE/'inputs/CONTROL/manifest.json')}
    bindings.update({ref['path']:ref['sha256'] for ref in summary['selected']['endpoint'].values()})
    for path, expected in ((Path(sec.__file__), SEC_SOURCE_SHA256), (HERE/'structure_reader.py', READER_SHA256), (sec.LIB, LIBERTY_SHA256)):
        audit.require(sec.sha(path) == expected, 'Proof dependency drift: '+str(path))
    audit.require(not (HERE/'sec'/('CONTROL_vs_'+arm+'_models_v2')).exists(), 'Proof output exists; refuse overwrite/repeat')
    return arm, plan['singletons'][arm], bindings


def verify_bindings(bindings):
    for name, expected in bindings.items():
        data.check_hash(name, expected)


def prove_selected(arm, registered_restored, bindings):
    verify_bindings(bindings)
    plan_path = HERE/'PLAN.json'
    registration_category = 'singletons'
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
               "prover": "/usr/bin/yosys in WSL Ubuntu; same pinned final_sec engine",
               "expected_counts": "102 total functional instances, including 21 FFs (not 102+21)",
               "liberty_path": str(sec.LIB.relative_to(ROOT)), "liberty_sha256": sec.sha(sec.LIB),
               "sec_source_sha256": sec.sha(Path(sec.__file__)), "driver_sha256": sec.sha(Path(__file__)),
               "checker_sha256": sec.sha(HERE / "structure_reader.py"),
               "all_used_cells": sorted(used), "cell_counts": cell_counts,
               "adapter": "replace incomplete legacy used_cells with complete Reader enumeration; no instance renaming",
               "timeout_s": 180, "status": "registered_before_prover"}
    receipt["selection_binding_sha256"] = bindings
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
    verify_bindings(bindings)
    sec.write_liberty_cell_models = complete_models
    try:
        result = sec.final_sec(texts["gold"], texts["gate"], "s382", out / "proof")
    finally:
        sec.write_liberty_cell_models = legacy_writer
    receipt["result"] = result
    receipt["status"] = result["status"]
    receipt["proof_sha256"] = {p.name: sec.sha(p) for p in sorted((out / "proof").iterdir()) if p.is_file()}
    receipt["selection_binding_unchanged"] = all(sec.sha(data.local(name)) == value for name, value in bindings.items())
    receipt["sources_unchanged"] = all(sec.sha(ROOT / value["path"]) == value["original_sha256"] for value in sources.values())
    sec.save(out / "receipt.json", receipt)
    print(json.dumps({"pair": arm, "status": receipt["status"], "sources_unchanged": receipt["sources_unchanged"]}), flush=True)
    return 0 if receipt["status"] == "pass" and receipt["sources_unchanged"] and receipt["selection_binding_unchanged"] else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true', help='Prove the exact all-nine selected endpoint; default validates only.')
    args = parser.parse_args()
    arm, restored, bindings = prepare()
    print(json.dumps({'preflight':'pass','arm':arm,'summary_sha256':bindings['SEARCH_SUMMARY.json'],'execute':args.execute}), flush=True)
    raise SystemExit(prove_selected(arm, restored, bindings) if args.execute else 0)
