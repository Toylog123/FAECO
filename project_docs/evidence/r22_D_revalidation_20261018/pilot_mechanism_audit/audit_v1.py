"""Read-only completed-pilot mechanism audit. No production imports/tool runs."""
from pathlib import Path
import argparse, collections, hashlib, json, time

parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', type=Path, required=True)
args = parser.parse_args()
ROOT = Path(__file__).resolve().parents[4]
OUT = args.output_dir.resolve()
OUT.mkdir(exist_ok=False, parents=True)
manifest = {}
def read(path):
    path = ROOT / path
    raw = path.read_bytes()
    manifest[path.relative_to(ROOT).as_posix()] = {
        'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
    return raw.decode('utf-8-sig')
def load(path):
    return json.loads(read(path))
def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()

started = time.time()
base = Path('experiments/20261018_r22_D_revalidate_v1')
registration = load(base / 'manifest.json')
root_audit = load('project_docs/evidence/r22_D_revalidation_20261018/ROOT_COMPLETION_AUDIT_07.json')
source_match = {}
for path, expected in registration['source_pin']['files'].items():
    read(path)
    source_match[path] = manifest[path]['sha256'] == expected
assert all(source_match.values())
run_facts, pairs = {}, []
for circuit in ['s27', 's382']:
    objects = {}
    for arm in ['fixed', 'adaptive']:
        directory = base / 'D' / arm / circuit
        config = load(directory / 'run_config.json')
        result = load(directory / 'outerloop_result.json')
        ledger = load(directory / 'eval_trials.json')
        completion = load(directory / 'completion.json')
        key = f'D/{arm}/{circuit}'
        assert manifest[(directory / 'completion.json').as_posix()]['sha256'] == root_audit['completion_set_frozen_at_start'][key]
        weights = result['weights_trace']
        changed = [w for w in weights if any(v != weights[0][k] for k, v in w.items() if k != 'round_id')]
        actions = collections.Counter(a for row in result['actions_history'] for a in row)
        fact = {
            'enable_feedback': config['enable_feedback'],
            'feedback_config_name': config['feedback_config_name'],
            'feedback_config': config['feedback_config'],
            'resolved_args': config['resolved_args'],
            'first_changed_weights': changed[0] if changed else None,
            'weights_trace': weights, 'final_weights': result['weights'],
            'actions_counts': dict(actions), 'actions_history': result['actions_history'],
            'failure_ema_trace': result['failure_ema_trace'],
            'history': result['history'], 'pool_trace': result['candidate_pool_trace'],
            'evaluator_call_count': len(ledger['call_log']),
            'evaluator_call_weights': [row.get('weights') for row in ledger['call_log']],
            'candidate_record_count': len(ledger['trials']),
            'n_new_sta_runs': result['n_new_sta_runs'],
            'n_cache_replays': result['n_cache_replays'],
            'baseline_wns': result['baseline_wns'], 'final_wns': result['wns'],
            'final_netlist_hash': result['state']['current_netlist_hash'],
            'no_new_candidate_failures': sum(row.get('type') == 'no_new_candidate' for row in result['state']['failure_history']),
            'call_log_gates_and_actionable': [{'patch_id': row['patch_id'], 'gates': row.get('gates'), 'actionable': row.get('actionable')} for row in ledger['call_log']],
        }
        run_facts[key] = fact
        objects[arm] = (result, ledger)
    fixed, adaptive = objects['fixed'][0], objects['adaptive'][0]
    ft, at = objects['fixed'][1]['trials'], objects['adaptive'][1]['trials']
    round_pairs = []
    seen_by_base = collections.defaultdict(set)
    for f, a in zip(fixed['candidate_pool_trace'], adaptive['candidate_pool_trace']):
        seen = seen_by_base[a['base_netlist_hash']]
        round_pairs.append({
            'round': a['round'], 'same_base': f['base_netlist_hash'] == a['base_netlist_hash'],
            'same_critical_instances': f['critical_instances'] == a['critical_instances'],
            'same_r_available': f['r_available'] == a['r_available'],
            'pool_order_same': f['pool_hashes'] == a['pool_hashes'],
            'pool_set_same': set(f['pool_hashes']) == set(a['pool_hashes']),
            'dispatch_order_same': f['dispatch_hashes'] == a['dispatch_hashes'],
            'dispatch_set_same': set(f['dispatch_hashes']) == set(a['dispatch_hashes']),
            'adaptive_dispatch_not_offered_before_same_base': sorted(set(a['dispatch_hashes']) - seen),
            'fixed_pool': f['pool_hashes'], 'adaptive_pool': a['pool_hashes'],
            'fixed_dispatch': f['dispatch_hashes'], 'adaptive_dispatch': a['dispatch_hashes'],
        })
        seen.update(a['dispatch_hashes'])
    # Check every repeated occurrence of the same base, not just each last round.
    cross = []
    for f in fixed['candidate_pool_trace']:
        for a in adaptive['candidate_pool_trace']:
            if f['base_netlist_hash'] == a['base_netlist_hash']:
                cross.append({'fixed_round': f['round'], 'adaptive_round': a['round'],
                              'base': f['base_netlist_hash'],
                              'pool_order_same': f['pool_hashes'] == a['pool_hashes'],
                              'pool_set_same': set(f['pool_hashes']) == set(a['pool_hashes']),
                              'dispatch_order_same': f['dispatch_hashes'] == a['dispatch_hashes'],
                              'dispatch_set_same': set(f['dispatch_hashes']) == set(a['dispatch_hashes'])})
    sequence_keys = ['candidate_hash', 'base_netlist_hash', 'kind', 'instance', 'patch_id', 'accepted', 'committed', 'sta_executed']
    equality = {key: [t.get(key) for t in ft] == [t.get(key) for t in at] for key in sequence_keys}
    pairs.append({'circuit': circuit, 'round_pairs': round_pairs, 'all_same_base_cross_pairs': cross,
                  'trial_sequence_equal_fields': equality,
                  'candidate_hash_sequence_sha_fixed': digest([t.get('candidate_hash') for t in ft]),
                  'candidate_hash_sequence_sha_adaptive': digest([t.get('candidate_hash') for t in at]),
                  'fixed_calls': len(objects['fixed'][1]['call_log']),
                  'adaptive_calls': len(objects['adaptive'][1]['call_log'])})

# Hash all sources actually read once more, after this read-only analysis.
for path, identity in manifest.items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == identity['sha256'], path
report = {'scope': 'Only D/fixed and D/adaptive s27/s382 completed pilot. No EDA, production imports, code/HEAD changes, old D replacement or all-eight inference.',
          'source_head_from_registered_manifest': registration['source_pin']['head'],
          'source_matches_registered_pin': source_match,
          'frozen_completions_match_root_07': True,
          'read_sha_before_after_stable': True, 'runs': run_facts, 'paired': pairs,
          'elapsed_s': time.time() - started}
(OUT / 'MECHANISM_AUDIT.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(OUT / 'READ_SHA_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'head': report['source_head_from_registered_manifest'], 'read_files': len(manifest),
                  'source_files_match': len(source_match),
                  'pairs': [{'circuit': p['circuit'], 'round_pairs': len(p['round_pairs']),
                             'all_same_base_cross_pairs': len(p['all_same_base_cross_pairs']),
                             'changed_pool_rounds': [r['round'] for r in p['round_pairs'] if not r['pool_order_same']],
                             'trial_sequence_equal_fields': p['trial_sequence_equal_fields']} for p in pairs]}, indent=2))
