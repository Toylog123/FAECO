"""Static independent proof/endpoint readback. No EDA or proof execution."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import sys
from decimal import Decimal

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'code/src'))
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))
spec = importlib.util.spec_from_file_location('reader', HERE / 'structure_reader.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)

def main():
    folder = HERE / 'sec/CONTROL_vs_RESTORE__074__models_v2'
    receipt = load(folder / 'receipt.json')
    plan = load(HERE / 'PLAN.json')
    assert receipt['plan_sha256'] == sha(HERE / 'PLAN.json')
    assert receipt['driver_sha256'] == sha(HERE / 'run_budget_sec.py')
    assert receipt['checker_sha256'] == sha(HERE / 'structure_reader.py')
    assert receipt['sec_source_sha256'] == sha(ROOT / 'code/scripts/run_r22_cut_ablation.py')
    for name, digest in plan['source_sha256'].items():
        assert sha(HERE / name) == digest, name
    assert receipt['status'] == 'pass' and receipt['sources_unchanged'] is True
    assert receipt['result']['returncode'] == 0
    proof = folder / 'proof'
    assert {p.name for p in proof.iterdir() if p.is_file()} == set(receipt['proof_sha256'])
    for name, digest in receipt['proof_sha256'].items():
        assert sha(proof / name) == digest, name
    assert load(proof / 'result.json') == receipt['result']
    log = (proof / 'sec.log').read_text(encoding='utf8').replace('\x00', '')
    assert re.findall(r'Of those cells (\d+) are proven and (\d+) are unproven', log) == [('101', '0')]
    assert 'Equivalence successfully proven!' in log
    assert not re.search(r'(?im)^\s*(?:ERROR|FATAL):', log)
    script = (proof / 'sec.ys').read_text()
    for command in ('equiv_make gold gate equiv', 'hierarchy -top equiv', 'equiv_simple', 'equiv_induct -seq 10', 'equiv_status -assert'):
        assert command in script.splitlines()
    from rseco.logic_rewrite import parse_liberty_cells
    lib = ROOT / receipt['liberty_path']
    assert sha(lib) == receipt['liberty_sha256']
    cells = parse_liberty_cells(lib.read_text(encoding='utf8'))
    used, counts, sources = set(), {}, {}
    tap = 'sky130_fd_sc_hd__tapvpwrvgnd_1'
    for side, rawname in [('gold', 'initial_raw.v'), ('gate', 'final_raw.v')]:
        entry = receipt['inputs'][side]
        path = ROOT / entry['path']
        assert sha(path) == entry['original_sha256']
        assert sha(path.parent / 'manifest.json') == entry['physical_manifest_sha256']
        original, ports = reader.Reader(path.read_text()).parse()
        removed = sorted(n for n, v in original['instances'].items() if v['cell'] == tap)
        assert removed == entry['removed_ids'] and len(removed) == 3026
        assert all(not original['instances'][n]['pins'] for n in removed)
        projected = dict(original, instances={n: v for n, v in original['instances'].items() if v['cell'] != tap})
        normalized = folder / (side + '_normalized.v')
        assert sha(normalized) == entry['normalized_sha256']
        for candidate in (normalized, proof / rawname, proof / (side + '.v')):
            structure, actual_ports = reader.Reader(candidate.read_text()).parse()
            assert (structure, actual_ports) == (projected, ports), candidate
        used.update(v['cell'] for v in projected['instances'].values())
        count = {'all_instances': len(projected['instances']), 'sequential_instances': sum(bool(cells[v['cell']].sequential_kind) for v in projected['instances'].values())}
        assert count == {'all_instances': 102, 'sequential_instances': 21}
        assert count == receipt['cell_counts'][side]
        counts[side] = count
        sources[side] = {'original_sha256': sha(path), 'normalized_sha256': sha(normalized), 'removed_count': len(removed)}
    assert sorted(used) == receipt['all_used_cells']
    model_names = re.findall(r'^module\s+(\w+)\s*\(', (proof / 'cells.v').read_text(), re.M)
    assert len(model_names) == len(set(model_names)) and set(model_names) == used
    # Rebuild models using the same audited production emitter, without tools.
    from rseco.real_wns import write_liberty_cell_models
    rebuilt = HERE / 'sec/independently_rebuilt_cells.v'
    write_liberty_cell_models(lib.read_text(encoding='utf8'), rebuilt, used_cells=used)
    assert sha(rebuilt) == sha(proof / 'cells.v')
    rescreen = load(HERE / 'RESCREEN.json')
    selected = rescreen['selected_pending_SEC']
    assert selected['arm'] == 'RESTORE__074_'
    for name, digest in selected['hashes'].items():
        assert sha(HERE / 'runs/RESTORE__074_' / name) == digest, name
    area = load(HERE / 'area_baseline_audit/RECEIPT.json')
    added = Decimal(area['metrics']['AR_minus_A0'])
    saved = Decimal(area['metrics']['AR_minus_AF'])
    percentage = saved / added * 100
    assert percentage == Decimal(area['metrics']['recovery_of_Resizer_net_added_area_percent'])
    assert abs(float(saved) - selected['area_saved']) < 1e-9
    report = {'status': 'accepted_within_10ps_policy_and_archived_constraint_scope',
              'new_EDA': 0, 'new_SEC_by_reviewer': 0,
              'checker_sha256': sha(Path(__file__)), 'SEC_receipt_sha256': sha(folder / 'receipt.json'),
              'plan_sha256': sha(HERE / 'PLAN.json'), 'area_receipt_sha256': sha(HERE / 'area_baseline_audit/RECEIPT.json'),
              'source_audit_sha256': sha(HERE / 'INDEPENDENT_SOURCE_AUDIT.json'),
              'proof_sha256': receipt['proof_sha256'], 'inputs': sources, 'cell_counts': counts,
              'model_count': len(used), 'model_emitter_sha256': sha(ROOT / 'code/src/rseco/real_wns.py'),
              'liberty_sha256': sha(lib), 'rebuilt_models_sha256': sha(rebuilt),
              'proven_equiv_cells': 101, 'unproven_equiv_cells': 0,
              'selected': selected, 'area_added_recovery_percent': str(percentage),
              'limitations': ['Postmeasurement policy change; no online search gain demonstrated',
                              'Two-state SEC; constrained-path TT physical checks only; incomplete IO coverage',
                              'TNS regresses and absolute setup still violates; not timing closure',
                              's382 stage-specific mapped-cell denominator, not old14-design recovery claim']}
    (HERE / 'ACCEPTANCE.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({'status': report['status'], 'models': len(used), 'SEC': '101/0', 'receipt_sha256': sha(HERE / 'ACCEPTANCE.json')}))

if __name__ == '__main__':
    main()
