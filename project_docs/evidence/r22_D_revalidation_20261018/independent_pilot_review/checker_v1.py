"""Independent D14 raw-artifact check, stdlib only; never starts EDA or Git.

Run at repository root with --output NEW_DIRECTORY. All read inputs are SHA/size
snapshotted and rechecked; outputs are exclusive. This is D14, not D56 acceptance.
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

def main():
    begin = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True); args = parser.parse_args()
    # Do not create any evidence output before the whole pilot is actually finished.
    assert (EVIDENCE / 'PILOT_RUN_RECEIPT.json').is_file(), 'pilot still running'
    manifest = load(EXPERIMENT / 'manifest.json')
    assert sha(raw(EXPERIMENT / 'manifest.json')) == EXPECTED_MANIFEST
    jobs = [j for j in manifest['jobs'] if j['circuit'] in ['s27', 's382']]
    assert len(manifest['jobs']) == 56 and len(jobs) == 14
    assert len({j['key'] for j in jobs}) == 14
    assert all((Path(j['output_dir']) / 'completion.json').is_file() for j in jobs)
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
    root_path = EVIDENCE / 'ROOT_COMPLETION_AUDIT_14.json'
    root = load(root_path) if root_path.is_file() else None
    if root: assert root['verified_completed'] == 14 and root['all_frozen_completed_verified']
    root_jobs = {j['key']: j for j in root['jobs']} if root else {}
    rows = []; totals = collections.Counter()
    frozen = {j['key']: sha(raw(Path(j['output_dir']) / 'completion.json')) for j in jobs}
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
        linked = {}; cache = 0; rejected = 0
        for t in trials:
            is_cache = t.get('skipped_duplicate') is True or (t.get('sta_executed') is False and t.get('cached_from_seq') is not None)
            if is_cache:
                cache += 1; assert t['sta_executed'] is False and t.get('sta_launch_seq') is None
                origin = by_seq[t['cached_from_seq']]; assert origin['candidate_hash'] == t['candidate_hash'] and origin['base_netlist_hash'] == t['base_netlist_hash']
            elif t.get('sta_executed') is True:
                seq = t['sta_launch_seq']; assert seq not in linked and seq in by_seq; linked[seq] = t
            else:
                rejected += 1; assert not t.get('sta_launch_seq')
        assert len(linked) == len(events)
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
               'sec_proven':counts[0][0], 'sec_unproven':0, 'baseline_wns':bw, 'final_wns':result['wns'],
               'final_state_sha256':state['current_netlist_hash'], 'completion_sha256':frozen[job['key']],
               'accepted_commits':len(state['accepted_patches'])}
        rows.append(row); totals.update({'jobs':1,'candidate_evaluation_records':len(trials),'candidate_ideal_STA_launches':len(events),'baseline_STA_runs':1,'cache_replays':cache,'pre_STA_rejected_trial_records':rejected,'SEC_passes':1})
        print('VERIFIED', job['key'], 'candidate STA',len(events),'cache',cache,'pre-reject',rejected,'SEC',counts[0],flush=True)
    assert head() == EXPECTED_HEAD
    before = dict(READ); after = {}
    for name, value in before.items():
        data = Path(name).read_bytes(); after[name] = {'sha256':sha(data),'bytes':len(data)}
        assert value == after[name], ('source/artifact drift',name)
    write(out / 'SOURCE_BEFORE.json', before); write(out / 'SOURCE_AFTER.json', after)
    receipt = {'schema':'r22-D14-independent-raw-review-v1','client_date':'2026-10-18','actual_utc':datetime.now(timezone.utc).isoformat(),
               'argv':sys.argv,'checker_sha256':sha(Path(__file__).read_bytes()),'runtime_s':time.monotonic()-begin,
               'source_HEAD':EXPECTED_HEAD,'source_files_current_matched':45,'manifest_sha256':EXPECTED_MANIFEST,
               'all_read_artifacts_stable':True,'read_artifact_count':len(before),'completion_set_frozen_at_start':frozen,
               'totals':dict(totals),'rows':rows,'root_cross_receipt_available_at_start':bool(root),'decision':'D14 pilot raw evidence accepted; no D56 extrapolation',
               'limitations':['Only s27/s382 14 registered jobs, not the remaining 42 or full D56.',
                              'Candidate k excludes baseline STA, cache reuse and pre-STA rejects; baseline 1 per job checked separately.',
                              'Ideal-net STA timing only; no physical RC calibration claim.',
                              'No new EDA, source mutation, test run or Git command; HEAD read directly from Git metadata.',
                              'No independent semantic reconstruction of Liberty-to-Boolean cell models; frozen source and retained SEC models are hash bound.',
                              'Other historical scientific domains and four-state support remain outside this review.']}
    write(out / 'RESULT.json',receipt)
    print('FINAL',json.dumps(dict(totals)), 'read stable',len(before),'RESULT_SHA256',sha((out/'RESULT.json').read_bytes()),flush=True)

if __name__ == '__main__': main()
