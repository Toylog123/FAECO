"""Read retained matrix input bytes and actual Liberty types, without EDA."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'code/src'))
from rseco.logic_rewrite import parse_liberty_cells
SOURCES = {}


def read(path, role):
    path = Path(path)
    path = path if path.is_absolute() else ROOT / path
    key = path.relative_to(ROOT).as_posix()
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    source = SOURCES.setdefault(key, {'sha256': sha, 'bytes': len(raw), 'roles': []})
    assert source['sha256'] == sha
    if role not in source['roles']:
        source['roles'].append(role)
    return raw.decode('utf-8-sig')


LIB_PATH = ('data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/'
            'da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib')
lib = parse_liberty_cells(read(LIB_PATH, 'actual Liberty tristate output semantics'))
tri = {name: cell.three_state_functions for name, cell in lib.items() if cell.three_state_functions}
assert len(tri) == 13
read('code/src/rseco/logic_rewrite.py', 'parser dependency at audit time')
preview_path = 'project_docs/evidence/r22_rerun_design_20261016/manifest_preview.json'
preview = json.loads(read(preview_path, 'explicit D56 retained input crosswalk'))
proofs_path = 'project_docs/evidence/r22_b_model_audit_20261016/audit.json'
proofs = json.loads(read(proofs_path, 'B2 accepted raw proof pairs and input hashes'))
rows = []


def inspect(group, path, circuit, expected_sha=None, **metadata):
    path = Path(path)
    path = path if path.is_absolute() else ROOT / path
    key = path.relative_to(ROOT).as_posix()
    row = {'group': group, 'circuit': circuit, 'path': key, **metadata}
    if not path.is_file():
        row.update(status='unknown_no_retained_mapped_input', exists=False)
    else:
        text = read(path, f'{group} actual retained mapped/raw input')
        types = Counter(re.findall(r'\b(sky130_fd_sc_hd__\w+)\s+(?:\\[^\s]+|[\w$]+)\s*\(', text))
        row.update(exists=True, sha256=SOURCES[key]['sha256'], source_type_counts=dict(sorted(types.items())),
                   used_tristate_types=sorted(set(types) & set(tri)),
                   unknown_library_types=sorted(set(types) - set(lib)))
        if expected_sha:
            row.update(expected_sha256=expected_sha, expected_sha_matches=expected_sha==row['sha256'])
            assert row['expected_sha_matches'], row
        row['status'] = ('actual_tristate_cells_used' if row['used_tristate_types'] else
                         'no_tristate_cell_in_actual_retained_input')
    rows.append(row)
    return row


for item in preview['D_runs']:
    inspect('D56_retained', item['baseline_input']['path'], item['circuit'],
            item['baseline_input']['sha256'], family=item['family'], arm=item['arm'])
for item in preview['shared_mapped_inputs']:
    inspect('shared_canonical8_prospective', item['canonical_input_to_stage'], item['circuit'], item['sha256'],
            limit='This audit does not stage or designate a C-prime input; explicit input registration must bind these bytes first.')
for item in proofs['proof_pairs']:
    for side in ('gold', 'gate'):
        inspect('B2_actual_raw_pairs', item[f'{side}_path'], item['top_module'], item[f'{side}_sha256'], side=side)
circuits = tuple(item['circuit'] for item in preview['shared_mapped_inputs'])
for name in circuits:
    old = ROOT / 'experiments/20261014_r22_cut_ablation/inputs' / name / 'mapped.v'
    if old.is_file():
        receipt = old.with_name('input.json')
        expected = json.loads(read(receipt, 'old C-prime retained mapped input receipt'))['mapped_sha256']
        inspect('Cprime_v1_retained', old, name, expected)
    inspect('Cprime_v2_prospective', ROOT / 'experiments/20261016_r22_cut_ablation_v2/inputs' / name / 'mapped.v', name)
changes = [name for name, info in SOURCES.items()
           if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != info['sha256']]
summary = {}
for group in sorted({row['group'] for row in rows}):
    subset = [row for row in rows if row['group'] == group]
    summary[group] = {'records': len(subset), 'existing_files': sum(row['exists'] for row in subset),
                      'tri_used_records': sum(bool(row.get('used_tristate_types')) for row in subset),
                      'missing_inputs_unknown': [row['circuit'] for row in subset if not row['exists']],
                      'distinct_existing_hashes': len({row['sha256'] for row in subset if row['exists']})}
payload = {'schema': 'r22-tristate-matrix-scope-check-v1',
           'generated_at_utc': datetime.now(timezone.utc).isoformat(),
           'eda_executed': False, 'production_or_tests_modified': False,
           'actual_library_tristate_types': tri, 'summary': summary, 'inputs': rows,
           'sources': SOURCES, 'source_changes_during_audit': changes,
           'limit': 'Only retained actual inputs are classified. C-prime v2 has no staged mapped files; RTL manifests and other-family mapped files do not certify its future mapped inputs. All future gold/gate must be checked again.'}
out = ROOT / 'project_docs/evidence/r22_correctness_20261016/TRISTATE_MATRIX_SCOPE_CHECK.json'
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'summary': summary, 'source_changes_during_audit': changes}, indent=2))
