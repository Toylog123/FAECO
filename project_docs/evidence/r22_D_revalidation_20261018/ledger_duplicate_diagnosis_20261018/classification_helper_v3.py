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
