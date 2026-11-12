"""Validate local history copies; historical source paths are identifiers only."""
import copy
import json
from decimal import Decimal
from pathlib import Path

import analyze_repair as audit
import selection

HERE = Path(__file__).resolve().parent
EXTRAS = ('_052_', '_054_', '_055_', '_079_', '_093_', '_098_', '_102_', '_111_', '_113_')
SEED = 'FORWARD__096_'


def local(name):
    path = (HERE / name).resolve()
    audit.require(path.is_relative_to(HERE), 'Path escapes local package')
    return path


def read(name):
    return json.loads(local(name).read_text(encoding='utf-8'))


def check_hash(name, expected):
    audit.require(audit.sha(local(name)) == expected, 'SHA mismatch: ' + name)


def endpoint(directory):
    files = dict(zip(selection.ROLES, ('routed.v', 'routed.spef', 'routed.odb', 'routed.def', 'manifest.json')))
    return {role: {'path': directory + '/' + name, 'sha256': audit.sha(local(directory + '/' + name))}
            for role, name in files.items()}


def point(row, directory):
    valid = row['status'].startswith('validated_')
    return {'candidate_id': row['arm'], 'evidence_kind': 'actual', 'area': row.get('area'),
            'metrics': row.get('metrics', {}).get('propagated', {}),
            'checks': {key: valid for key in selection.CHECKS},
            'endpoint': endpoint(directory) if valid else {}, 'sec_status': 'pending'}


def history():
    """Read and verify only this package plus current code/library dependencies."""
    copies = read('COPY_MANIFEST.json')
    mapping = read('LOCAL_INPUT_MAP.json')
    for name, info in copies.items():
        check_hash(name, info['sha256'])
        audit.require(mapping[info['source'].replace('\\', '/')] == name, 'Copy mapping mismatch')
    for source, name in mapping.items():
        audit.require(name in copies, 'Mapped path is not a registered copy')
        local(name)
    for name, info in read('inputs/MANIFEST.json').items():
        check_hash('inputs/' + name, info['sha256'])
        audit.require(mapping[info['source'].replace('\\', '/')] == 'inputs/' + name,
                      'Original input alias mismatch')
    areas = audit.load_liberty_areas(audit.LIB)
    control = audit.baseline('CONTROL', areas)
    recovered = audit.baseline('RECOVERY_V2', areas)
    recipe = read('inputs/recipe.json')['applied']
    actions = sorted(r['instance'] for r in recipe)
    audit.require(len(actions) == len(set(actions)) == 13, 'Recipe is not original 13')
    summary = read('labels/provenance/FORWARD_SUMMARY.json')
    prior_plan = read('labels/provenance/FORWARD_PLAN.json')
    check_hash('labels/provenance/FORWARD_PLAN.json', summary['plan_sha256'])
    audit.require(summary['status'] == 'all13_finished' and len(summary['rows']) == 13,
                  'Historical singleton sweep incomplete')
    rows = {r['arm']: r for r in summary['rows']}
    audit.require(set(rows) == {'FORWARD_' + a for a in actions}, 'Historical action set mismatch')
    observations = {}
    for action in actions:
        arm = 'FORWARD_' + action
        row = rows[arm]
        directory = 'labels/singletons/' + arm
        audit.require(row['status'].startswith('validated_'), 'Invalid historical singleton')
        expected_restored = sorted(set(actions) - {action})
        audit.require(prior_plan['singletons'][arm] == row['restored'] == expected_restored,
                      'Prior action/restored identity mismatch')
        for name, digest in row['output_sha256'].items():
            check_hash(directory + '/' + name, digest)
        design = audit.structure(local(directory + '/routed.v'))
        expected = copy.deepcopy(control['structure'])
        for change in recipe:
            audit.require(expected['instances'][change['instance']]['cell'] == change['new_cell'], 'Recipe baseline mismatch')
            if change['instance'] == action:
                expected['instances'][action]['cell'] = change['old_cell']
        audit.require(design == expected, 'Prior singleton full structure mismatch')
        total, taps = audit.area(design, areas)
        audit.require(total == row['area'] and taps == control['taps'], 'Prior complete area mismatch')
        measured = audit.metrics(audit.readlog(local(directory + '/propagated.log'), 'ROUTED_STA_OK'))
        audit.require(measured == row['metrics']['propagated'], 'Prior raw metric mismatch')
        observations[action] = measured
    acceptance = read('labels/provenance/FORWARD_ACCEPTANCE.json')
    for name, key in (('FORWARD_SUMMARY.json', 'forward_summary_sha256'), ('run_repair_sec.py', 'sec_driver_sha256')):
        check_hash('labels/provenance/' + name, acceptance[key])
    check_hash('labels/seed_proof/receipt.json', acceptance['sec_receipt_sha256'])
    proof = read('labels/seed_proof/receipt.json')
    audit.require(acceptance['arm'] == SEED and acceptance['status'] == 'accepted_local_conservative_baseline', 'Wrong seed acceptance')
    audit.require(proof['status'] == 'pass' and proof['sources_unchanged'] is True and proof['pair'] == ['CONTROL', SEED], 'Seed proof failed/identity mismatch')
    audit.require(acceptance['checks']['equiv_proven'] == 101 and acceptance['checks']['equiv_unproven'] == 0,
                  'Seed proof counts mismatch')
    for name, digest in proof['proof_sha256'].items():
        check_hash('labels/seed_proof/proof/' + name, digest)
    for role, info in proof['inputs'].items():
        check_hash(mapping[info['path'].replace('\\', '/')], info['original_sha256'])
        check_hash('labels/seed_proof/' + role + '_normalized.v', info['normalized_sha256'])
    seed = point(rows[SEED], 'labels/singletons/' + SEED)
    seed.update(sec_status='pass', acceptance={'path': 'labels/provenance/FORWARD_ACCEPTANCE.json',
                'sha256': audit.sha(local('labels/provenance/FORWARD_ACCEPTANCE.json'))},
                proof={'path': 'labels/seed_proof/receipt.json', 'sha256': acceptance['sec_receipt_sha256']})
    audit.require(seed['area'] == acceptance['area'] and seed['metrics'] == acceptance['metrics'], 'Seed acceptance metrics mismatch')
    audit.require(seed['endpoint']['netlist']['sha256'] == acceptance['netlist_sha256'] and
                  seed['endpoint']['spef']['sha256'] == acceptance['spef_sha256'], 'Seed physical endpoint mismatch')
    audit.require(selection.judge_actual(seed, control)['feasible'], 'Seed is not strict feasible')
    return areas, control, recovered, recipe, seed, observations


def proposal(data):
    areas, control, recovered, recipe, seed, observations = data
    actions = {r['instance'] for r in recipe}
    candidates = []
    restored = {}
    for extra in EXTRAS:
        ident = 'PAIR_096_' + extra.strip('_')
        design = copy.deepcopy(control['structure'])
        for change in recipe:
            if change['instance'] in ('_096_', extra):
                design['instances'][change['instance']]['cell'] = change['old_cell']
        total, _ = audit.area(design, areas)
        saving = float(Decimal(str(control['area'])) - Decimal(str(total)))
        audit.require(saving > selection.judge_actual(seed, control)['area_saved'], 'Pair must improve logical area')
        candidates.append({'candidate_id': ident, 'extra_action': extra, 'area': total, 'area_saved': saving})
        restored[ident] = sorted(actions - {'_096_', extra})
    return dict(selection.freeze_orders(candidates, control, seed, observations), singletons=restored)
