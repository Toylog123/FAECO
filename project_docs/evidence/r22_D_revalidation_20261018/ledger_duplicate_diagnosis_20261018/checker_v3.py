"""Independent frozen-completed D raw-artifact check, stdlib only; never starts EDA or Git.

Run at repository root with --output NEW_DIRECTORY. All read inputs are SHA/size
snapshotted and rechecked; outputs are exclusive. Acceptance is limited to the supplied frozen completion set; D56 only when all 56 registered keys are present.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, collections, hashlib, json, math, re, sys, time

EXPERIMENT = Path('experiments/20261018_r22_D_revalidate_v1')
EVIDENCE = Path('project_docs/evidence/r22_D_revalidation_20261018')
EXPECTED_HEAD = 'f761ee1996a83fc4f0f3de0999b74d85a8237858'
EXPECTED_MANIFEST = 'fd336745fd6bbb3039eaf5c043f67206a5567e74116b7787e093f89592a3ff4d'
READ = {}

def sha(raw): return hashlib.sha256(raw).hexdigest()
def key(path): return str(Path(path).resolve())
def raw(path):
    path = Path(path); data = path.read_bytes()
    item = {'sha256': sha(data), 'bytes': len(data)}
    name = key(path)
    if name in READ: assert READ[name] == item, ('drift during read', name)
    READ[name] = item
    return data
def text(path): return raw(path).decode('utf-8-sig').replace('\r\n', '\n')
def load(path): return json.loads(text(path))
def write(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')
def fingerprint(value): return sha(json.dumps(value, sort_keys=True, ensure_ascii=False).encode('utf-8'))
def near(a, b): assert math.isclose(a, b, rel_tol=0, abs_tol=1e-9), (a, b)
def wsl(path):
    s = str(Path(path).resolve()).replace('\\', '/')
    return '/mnt/' + s[0].lower() + s[2:]
def head():
    git = Path('.git')
    if git.is_file(): git = Path(text(git).strip().split('gitdir: ', 1)[1])
    value = text(git / 'HEAD').strip()
    if value.startswith('ref: '):
        ref = value[5:]
        if (git / ref).exists(): return text(git / ref).strip()
        for line in text(git / 'packed-refs').splitlines():
            if line.endswith(' ' + ref): return line.split()[0]
        raise AssertionError('HEAD ref not found')
    return value
def modules(source):
    matches = re.findall(r'(?ms)^\s*module\s+(\w+)\b(.*?^\s*endmodule\b)', source)
    result = {name: ('module ' + name + body).strip() for name, body in matches}
    assert len(result) == len(matches) and result
    return result
def sta(path, circuit, period, lib, netlist):
    tcl = text(path / 'sta.tcl'); log = text(path / 'sta.log')
    assert f'read_liberty {wsl(lib)}' in tcl
    assert f'read_verilog {wsl(netlist)}' in tcl
    assert f'link_design {circuit}\n' in tcl
    assert f'create_clock -name clk -period {period} [get_ports CK]' in tcl
    assert 'read_spef' not in tcl
    assert not re.search(r'(?mi)^Error\b|^Warning:\s+(?:1647|1652)\b', log), path
    ws = re.findall(r'(?m)^worst slack max\s+([-+0-9.eE]+)\s*$', log)
    ts = re.findall(r'(?m)^tns max\s+([-+0-9.eE]+)\s*$', log)
    assert len(ws) == len(ts) == 1, path
    raw(netlist)
    return float(ws[0]), float(ts[0])
def valid_trial(t):
    if t.get('accepted') is not True or t.get('committed') is not True or t.get('hard_gate') or t.get('physical_failure'): return False
    for name in ['failure_events', 'trial_failure_events']:
        events = t.get(name) or []
        if not isinstance(events, list) or any(not isinstance(e, dict) or e.get('hard_gate') or e.get('severity') == 'hard' for e in events): return False
    evidence = t.get('acceptance_evidence')
    return isinstance(evidence, dict) and evidence.get('passed') is not False and not evidence.get('violations') and not evidence.get('unavailable')

def classify_trials(trials, by_seq, initial_text, final_hash, call_log):
    """Separate measured reuse, identity dedup and rejected construction records.

    Missing base identity is reconstructed only for the exact tested-hash
    branch signature, from the explicit commit chain AND the cache-key digest.
    The raw trial is never changed. Every ambiguity raises an assertion.
    """
    counts = collections.Counter({name: 0 for name in (
        'actual_STA_cache_reuse_from_launch', 'tested_hash_dedup_without_replay',
        'cached_pre_STA_rejection', 'uncached_pre_STA_rejection')})
    linked = {}
    for index, trial in enumerate(trials):
        if trial.get('sta_executed') is True:
            seq = trial['sta_launch_seq']
            assert not trial.get('skipped_duplicate') and trial.get('cached_from_seq') is None
            assert isinstance(seq, int) and not isinstance(seq, bool) and seq in by_seq and seq not in linked
            linked[seq] = trial
    assert set(linked) == set(by_seq)
    call_by_iteration = {item['iteration']: item for item in call_log}
    assert len(call_by_iteration) == len(call_log)
    groups = collections.OrderedDict()
    for index, trial in enumerate(trials): groups.setdefault(trial['iteration'], []).append((index, trial))
    assert list(groups) == sorted(groups)
    base_by_index = {}; current = sha(initial_text.encode())
    for iteration, group in groups.items():
        assert iteration in call_by_iteration
        for index, trial in group:
            if 'base_netlist_hash' in trial: assert trial['base_netlist_hash'] == current
            base_by_index[index] = current
        commits = [trial for index, trial in group if trial.get('committed') is True]
        assert len(commits) <= 1
        if commits:
            assert commits[0].get('accepted') is True and commits[0].get('sta_executed') is True
            current = commits[0]['candidate_hash']
    assert current == final_hash
    prior_keys = collections.defaultdict(list); prior_measured = []; inferred = []
    def rejected(trial):
        assert trial.get('sta_executed') is False and trial.get('sta_launch_seq') is None
        assert trial.get('accepted') is False and trial.get('committed') is False
        events = trial.get('failure_events')
        assert isinstance(events, list) and events and all(isinstance(e, dict) for e in events)
        assert any(e.get('hard_gate') is True or e.get('severity') == 'hard' for e in events)
        assert not trial.get('sta_provenance')
        for event in events:
            if event.get('type') == 'sta_budget_exhausted':
                assert event.get('hard_gate') is True and event['observed_value'] == event['threshold']
                assert event['evidence']['stage'] == 'sta' and event['evidence']['reason'] == 'reserved before tool'
    for index, trial in enumerate(trials):
        candidate = trial['candidate_hash']; base = base_by_index[index]
        assert sha(trial['candidate_netlist_text'].encode()) == candidate
        assert re.fullmatch('[0-9a-f]{64}', trial['config_hash'])
        assert sha((base + candidate + trial['config_hash']).encode()) == trial['cache_key']
        skipped = trial.get('skipped_duplicate') is True
        cached_from = trial.get('cached_from_seq')
        if cached_from is not None:
            assert isinstance(cached_from, int) and not isinstance(cached_from, bool) and cached_from > 0
            assert trial.get('sta_executed') is False and trial.get('sta_launch_seq') is None
            assert cached_from in by_seq and cached_from in linked
            event = by_seq[cached_from]; origin = linked[cached_from]
            assert any(old is origin for old_index, old in prior_measured)
            assert event['candidate_hash'] == candidate and event['base_netlist_hash'] == trial['base_netlist_hash'] == base
            assert origin['cache_key'] == trial['cache_key'] and origin['config_hash'] == trial['config_hash']
            assert origin['wns'] == trial['wns'] and origin['tns'] == trial['tns']
            assert origin.get('sta_provenance') == trial.get('sta_provenance')
            counts['actual_STA_cache_reuse_from_launch'] += 1
        elif skipped and 'cached_from_seq' in trial:
            rejected(trial)
            origins = [(i, t) for i, t in prior_keys[trial['cache_key']]
                       if t.get('sta_executed') is False and not t.get('skipped_duplicate')]
            assert origins
            origin_index, origin = origins[0]; rejected(origin)
            assert origin['failure_events'] == trial['failure_events']
            assert origin['base_netlist_hash'] == trial['base_netlist_hash'] == base
            assert origin['candidate_hash'] == candidate and origin['config_hash'] == trial['config_hash']
            assert origin['wns'] == trial['wns'] and origin['tns'] == trial['tns']
            counts['cached_pre_STA_rejection'] += 1
        elif skipped:
            assert trial.get('sta_executed') is False and trial.get('sta_launch_seq') is None
            assert 'base_netlist_hash' not in trial and trial['runtime_s'] == 0.0
            assert trial.get('accepted') is False and trial.get('committed') is False
            assert not trial.get('failure_events') and not trial.get('trial_failure_events') and not trial.get('sta_provenance')
            near(trial['wns'], call_by_iteration[trial['iteration']]['baseline_wns'])
            origins = [(i, t) for i, t in prior_measured
                       if t['candidate_hash'] == candidate and t['config_hash'] == trial['config_hash']]
            assert origins
            # ROOT28's observed identity-dedup class is a previously measured
            # absolute netlist re-created under a later base, not same-key reuse.
            assert all(t['base_netlist_hash'] != base and t['cache_key'] != trial['cache_key'] for i, t in origins)
            inferred.append({'trial_index_0based': index, 'candidate_hash': candidate,
                             'base_hash_inferred_not_raw': base, 'cache_key': trial['cache_key'],
                             'base_binding': 'initial mapped text + ordered explicit committed trial chain + exact SHA256(base+candidate+config)',
                             'origin_measured_trial_indices': [i for i, t in origins],
                             'origin_STA_launch_sequences': [t['sta_launch_seq'] for i, t in origins]})
            counts['tested_hash_dedup_without_replay'] += 1
        elif trial.get('sta_executed') is True:
            prior_measured.append((index, trial))
        else:
            rejected(trial); counts['uncached_pre_STA_rejection'] += 1
        prior_keys[trial['cache_key']].append((index, trial))
    compatibility_cache_count = (counts['actual_STA_cache_reuse_from_launch']
                                 + counts['tested_hash_dedup_without_replay']
                                 + counts['cached_pre_STA_rejection'])
    assert len(linked) + compatibility_cache_count + counts['uncached_pre_STA_rejection'] == len(trials)
    return linked, compatibility_cache_count, counts['uncached_pre_STA_rejection'], dict(counts), inferred

def main():
    begin = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True); parser.add_argument('--audit', required=True); args = parser.parse_args()
    # Do not create any evidence output before the whole pilot is actually finished.
    assert (EVIDENCE / 'PILOT_RUN_RECEIPT.json').is_file(), 'pilot still running'
    manifest = load(EXPERIMENT / 'manifest.json')
    assert sha(raw(EXPERIMENT / 'manifest.json')) == EXPECTED_MANIFEST
    audit_path = Path(args.audit)
    selected_audit = load(audit_path)
    assert selected_audit['all_frozen_completed_verified'] is True
    assert selected_audit['manifest_sha256'] == EXPECTED_MANIFEST
    assert selected_audit['source_pin'] == manifest['source_pin']
    selected_keys = set(selected_audit['completion_set_frozen_at_start'])
    actual_completed_at_start = {j['key'] for j in manifest['jobs'] if (Path(j['output_dir']) / 'completion.json').is_file()}
    manifest_keys = {j['key'] for j in manifest['jobs']}
    assert len(manifest_keys) == len(manifest['jobs']) == 56
    assert 0 < len(selected_keys) <= 56 and selected_keys <= manifest_keys
    assert selected_keys <= actual_completed_at_start, 'A selected immutable completion is missing'
    assert len(selected_audit['jobs']) == len({j['key'] for j in selected_audit['jobs']}) == len(selected_keys)
    assert {j['key'] for j in selected_audit['jobs']} == selected_keys
    extra_completed_at_start_not_reviewed = sorted(actual_completed_at_start - selected_keys)
    jobs = [j for j in manifest['jobs'] if j['key'] in selected_keys]
    assert len(jobs) == len(selected_keys) == selected_audit['verified_completed']
    out = Path(args.output); out.mkdir(exist_ok=False)
    assert head() == EXPECTED_HEAD == manifest['source_pin']['head']
    assert len(manifest['source_pin']['files']) == 45
    for name, expected in manifest['source_pin']['files'].items(): assert sha(raw(name)) == expected, name
    lib = Path(manifest['liberty']); assert sha(raw(lib)) == manifest['lib_sha256']
    for name, expected in manifest['provenance'].items(): assert sha(raw(name)) == expected, name
    pilot = load(EVIDENCE / 'PILOT_RUN_RECEIPT.json')
    assert pilot['returncode'] == 0 and pilot['source_head'] == pilot['head_after'] == EXPECTED_HEAD
    assert pilot['manifest_sha256'] == EXPECTED_MANIFEST and pilot['selected_jobs'] == 14
    for stream in ['stdout', 'stderr']: assert sha(raw(EVIDENCE / f'pilot.{stream}.log')) == pilot[f'{stream}_sha256']
    root_path = audit_path
    root = selected_audit
    assert root['verified_completed'] == len(jobs) and root['all_frozen_completed_verified']
    root_jobs = {j['key']: j for j in root['jobs']} if root else {}
    rows = []; totals = collections.Counter()
    frozen = {j['key']: sha(raw(Path(j['output_dir']) / 'completion.json')) for j in jobs}
    assert frozen == selected_audit['completion_set_frozen_at_start'], 'Frozen completion SHA mismatch'
    for job in jobs:
        p = Path(job['output_dir']); c = job['circuit']
        done = load(p / 'completion.json'); config = load(p / 'run_config.json'); result = load(p / 'outerloop_result.json'); ledger = load(p / 'eval_trials.json')
        assert done['key'] == job['key'] and done['status'] == 'complete' and done['returncode'] == done['sec_returncode'] == 0 and done['sec_status'] == 'pass'
        assert config['git_head'] == EXPECTED_HEAD
        for name, value in job['expected_run_config'].items():
            if name == 'resolved_args':
                for arg, expected in value.items(): assert config[name][arg] == expected, (job['key'], arg)
            else: assert config[name] == value, (job['key'], name)
        assert config['resolved_args']['cut_sources'] == 'full' and config['resolved_args']['node_cost_mode'] == 'configured'
        assert not config['structure_resynth'] and not config['capture_electrical']
        assert config['resolved_args']['physical_gate'] is False
        assert result['cut_search_policy'] == 'legacy' and result['enable_topology'] is True
        registration = load(p / 'preregistered.json')
        assert registration == {'manifest_sha256': fingerprint(manifest), 'job': job}
        assert done['registration_sha256'] == fingerprint(registration)
        for name, expected in {**done['evidence_receipt'], **done['extra_receipt']}.items(): assert sha(raw(p / name)) == expected, (job['key'], name)
        assert done['result_sha256'] == sha(raw(p / 'outerloop_result.json'))
        assert sha(raw(p / 'mapped.v')) == job['baseline']['sha256'] == sha(raw(job['baseline']['path']))
        state = result['state']; final_text = state['current_netlist_text']
        assert sha(final_text.encode()) == state['current_netlist_hash']
        assert text(p / 'final_sec/final_raw.v') == final_text
        assert text(p / 'final_sec/initial_raw.v') == text(p / 'mapped.v')
        initial_modules = modules(text(p / 'final_sec/initial_raw.v')); final_modules = modules(final_text)
        assert modules(text(p / 'final_sec/gold.v')) == {c: initial_modules[c]}
        assert modules(text(p / 'final_sec/gate.v')) == {c: final_modules[c]}
        helpers = {n: s for n, s in initial_modules.items() if n != c}
        assert helpers == {n: s for n, s in final_modules.items() if n != c}
        if helpers: assert modules(text(p / 'final_sec/helpers.v')) == helpers
        else: assert not text(p / 'final_sec/helpers.v').strip()
        sec = load(p / 'final_sec/result.json'); ys = text(p / 'final_sec/sec.ys'); sl = text(p / 'final_sec/sec.log')
        assert sec['status'] == 'pass' and sec['returncode'] == 0
        assert sec['initial_sha256'] == sha(raw(p / 'final_sec/initial_raw.v'))
        assert sec['final_sha256'] == sha(raw(p / 'final_sec/final_raw.v'))
        assert sec['shared_helpers_sha256'] == sha(raw(p / 'final_sec/helpers.v'))
        for name in ['cells.v', 'helpers.v', 'gold.v', 'gate.v']: assert f'read_verilog "{wsl(p / "final_sec" / name)}"' in ys
        commands = [s.strip() for s in ys.splitlines() if s.strip()]
        order = [f'rename {c} gold', f'rename {c} gate', 'equiv_make gold gate equiv', 'hierarchy -top equiv', 'flatten', 'equiv_simple', 'equiv_induct -seq 10', 'equiv_status -assert']
        assert [commands.index(s) for s in order] == sorted(commands.index(s) for s in order)
        assert sec['command'][-1] == wsl(p / 'final_sec/sec.ys')
        counts = [(int(a), int(b)) for a, b in re.findall(r'Of those cells (\d+) are proven and (\d+) are unproven', sl)]
        assert len(counts) == 1 and counts[0][0] > 0 and counts[0][1] == 0 and 'Equivalence successfully proven!' in sl
        assert re.search(r'Top module:\s+\\equiv\b', sl)
        period = config['resolved_args']['period']
        bw, bt = sta(p, c, period, lib, p / 'mapped.v'); near(bw, result['baseline_wns'])
        trials = ledger['trials']; events = ledger['sta_launch_events']; assert all(e['kind'] == 'candidate_ideal' for e in events)
        by_seq = {e['seq']: e for e in events}; assert len(by_seq) == len(events) and sorted(by_seq) == list(range(1, len(events) + 1))
        linked, cache, rejected, classification, inferred_dedup = classify_trials(
            trials, by_seq, text(p / 'mapped.v'), state['current_netlist_hash'], ledger['call_log'])
        observed = []; valid = []; best = best_valid = 0.0
        for seq in sorted(by_seq):
            event = by_seq[seq]; t = linked[seq]
            assert event['status'] == 'completed' and not event['error'] and event['timeout'] is False
            assert event['candidate_hash'] == t['candidate_hash'] and event['base_netlist_hash'] == t['base_netlist_hash']
            candidate = Path(event['report_dir']); assert p.resolve() in candidate.resolve().parents
            assert sha(t['candidate_netlist_text'].encode()) == event['candidate_hash']
            assert text(candidate / 'mapped.v') == t['candidate_netlist_text']
            assert Path(t['sta_provenance']['report_path']) == candidate / 'sta.log'
            w, tn = sta(candidate, c, period, lib, candidate / 'mapped.v'); near(w, event['wns']); near(tn, event['tns'])
            best = max(best, w - bw)
            if valid_trial(t): best_valid = max(best_valid, w - bw)
            observed.append(best); valid.append(best_valid)
        ac = done['accounting']
        recomputed = {'n_new_sta_runs': len(events), 'n_candidate_evaluation_records': len(trials), 'n_cache_replays': cache,
                      'n_sta_to_first_improvement': next((i+1 for i,v in enumerate(observed) if v > 0), None),
                      'n_sta_to_first_valid_improvement': next((i+1 for i,v in enumerate(valid) if v > 0), None)}
        for name, value in recomputed.items(): assert ac[name] == result[name] == value, (job['key'], name)
        assert ac['best_wns_curve'] == result['best_wns_curve'] == observed
        assert ac['best_valid_wns_curve'] == result['best_valid_wns_curve'] == valid
        assert len(events) == state['budget']['sta_used']
        assert len(trials) == result['n_candidate_sta_runs']
        assert ac['accepted_commits'] == len(state['accepted_patches'])
        if state['accepted_patches']: assert state['accepted_patches'][-1]['netlist_hash'] == state['current_netlist_hash']
        near(result['wns'], state['current_wns']); near(result['wns'], done['final_wns']); near(result['baseline_wns'], done['baseline_wns'])
        if root:
            assert frozen[job['key']] == root_jobs[job['key']]['completion_sha256']
            for root_name, value in [('n_candidate_evaluation_records', len(trials)), ('n_new_candidate_sta_runs', len(events)), ('n_cache_replays', cache)]: assert root_jobs[job['key']][root_name] == value
        row = {'key':job['key'], **recomputed, 'baseline_actual_STA_runs':1, 'pre_STA_rejected_trial_records':rejected,
               'nonlaunch_record_classification':classification, 'tested_hash_dedup_inference':inferred_dedup,
               'legacy_n_cache_replays_is_compatibility_sum_not_pure_STA_reuse':True,
               'sec_proven':counts[0][0], 'sec_unproven':0, 'baseline_wns':bw, 'final_wns':result['wns'],
               'final_state_sha256':state['current_netlist_hash'], 'completion_sha256':frozen[job['key']],
               'accepted_commits':len(state['accepted_patches'])}
        rows.append(row); totals.update({'jobs':1,'candidate_evaluation_records':len(trials),'candidate_ideal_STA_launches':len(events),'baseline_STA_runs':1,'cache_replays':cache,'pre_STA_rejected_trial_records':rejected,'SEC_passes':1})
        totals.update(classification)
        print('VERIFIED', job['key'], 'candidate STA',len(events),'cache',cache,'pre-reject',rejected,'SEC',counts[0],flush=True)
    assert head() == EXPECTED_HEAD
    before = dict(READ); after = {}
    for name, value in before.items():
        data = Path(name).read_bytes(); after[name] = {'sha256':sha(data),'bytes':len(data)}
        assert value == after[name], ('source/artifact drift',name)
    write(out / 'SOURCE_BEFORE.json', before); write(out / 'SOURCE_AFTER.json', after)
    receipt = {'schema':'r22-D-frozen-subset-independent-raw-review-v3','client_date':'2026-10-18','actual_utc':datetime.now(timezone.utc).isoformat(),
               'argv':sys.argv,'checker_sha256':sha(Path(__file__).read_bytes()),'runtime_s':time.monotonic()-begin,
               'source_HEAD':EXPECTED_HEAD,'source_files_current_matched':45,'manifest_sha256':EXPECTED_MANIFEST,
               'all_read_artifacts_stable':True,'read_artifact_count':len(before),'completion_set_frozen_at_start':frozen,
               'totals':dict(totals),'rows':rows,'root_cross_receipt_available_at_start':True,'audit_path':str(audit_path),'audit_sha256':READ[key(audit_path)]['sha256'],
               'extra_completed_at_start_not_reviewed':extra_completed_at_start_not_reviewed,
               'extra_completed_at_end_not_reviewed': sorted({j['key'] for j in manifest['jobs'] if (Path(j['output_dir']) / 'completion.json').is_file()} - selected_keys),
               'full_56_registered_keys_reviewed':selected_keys==manifest_keys,
               'subset_contract':'Exact registered keys from immutable supplied root receipt; every selected completion SHA must match, later/extra completions are explicitly excluded.',
               'cache_accounting_contract':'n_cache_replays is preserved legacy compatibility sum: actual STA cache reuse + tested-hash dedup without replay + cached pre-STA rejection. The separated counters are authoritative for interpretation.',
               'decision':'Accepted only the supplied root-audit frozen completed set',
               'limitations':['Only the root-audit frozen completed set at review start is covered; full D56 only when all 56 registered keys are present.',
                              'Candidate k excludes baseline STA, measured cache reuse, tested-hash dedup and pre-STA rejects; baseline 1 per job checked separately. Legacy cache count is not pure STA reuse.',
                              'Ideal-net STA timing only; no physical RC calibration claim.',
                              'No new EDA, source mutation, test run or Git command; HEAD read directly from Git metadata.',
                              'No independent semantic reconstruction of Liberty-to-Boolean cell models; frozen source and retained SEC models are hash bound.',
                              'Other historical scientific domains and four-state support remain outside this review.']}
    write(out / 'RESULT.json',receipt)
    print('FINAL',json.dumps(dict(totals)), 'read stable',len(before),'RESULT_SHA256',sha((out/'RESULT.json').read_bytes()),flush=True)

if __name__ == '__main__': main()
