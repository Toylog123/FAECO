"""Prepare a new self-contained checker; syntax only, never execute its audit."""
from pathlib import Path
import ast,difflib,hashlib,json,shutil
R=Path.cwd();O=Path(__file__).resolve().parent
old=R/'project_docs/evidence/r22_D_revalidation_20261018/independent_completed_review/checker_v2.py'
before=old.read_text(encoding='utf-8');new=before
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(old)=='59e51ed56d72fafc3b2dd611bf62028e4491991d6d07ca8bebc4b31ddd9e4250'
helper=(O/'classification_helper_v3.py').read_text(encoding='utf-8')
new=new.replace('\ndef main():','\n'+helper+'\ndef main():',1)
oldselection="""    assert actual_completed_at_start == selected_keys, 'Need a fresh root audit for the exact completed set at start'
    assert len(manifest['jobs']) == 56 and 0 < len(selected_keys) <= 56
"""
newselection="""    manifest_keys = {j['key'] for j in manifest['jobs']}
    assert len(manifest_keys) == len(manifest['jobs']) == 56
    assert 0 < len(selected_keys) <= 56 and selected_keys <= manifest_keys
    assert selected_keys <= actual_completed_at_start, 'A selected immutable completion is missing'
    assert len(selected_audit['jobs']) == len({j['key'] for j in selected_audit['jobs']}) == len(selected_keys)
    assert {j['key'] for j in selected_audit['jobs']} == selected_keys
    extra_completed_at_start_not_reviewed = sorted(actual_completed_at_start - selected_keys)
"""
assert new.count(oldselection)==1;new=new.replace(oldselection,newselection)
start=new.index('        linked = {}; cache = 0; rejected = 0\n')
end=new.index('        observed = []; valid = []; best = best_valid = 0.0\n',start)
new=new[:start]+"""        linked, cache, rejected, classification, inferred_dedup = classify_trials(
            trials, by_seq, text(p / 'mapped.v'), state['current_netlist_hash'], ledger['call_log'])
"""+new[end:]
oldrow="""        row = {'key':job['key'], **recomputed, 'baseline_actual_STA_runs':1, 'pre_STA_rejected_trial_records':rejected,
"""
newrow="""        row = {'key':job['key'], **recomputed, 'baseline_actual_STA_runs':1, 'pre_STA_rejected_trial_records':rejected,
               'nonlaunch_record_classification':classification, 'tested_hash_dedup_inference':inferred_dedup,
               'legacy_n_cache_replays_is_compatibility_sum_not_pure_STA_reuse':True,
"""
assert new.count(oldrow)==1;new=new.replace(oldrow,newrow)
needle="        print('VERIFIED', job['key'],"
assert new.count(needle)==1;new=new.replace(needle,"        totals.update(classification)\n"+needle)
new=new.replace("'r22-D-frozen-completed-independent-raw-review-v2'","'r22-D-frozen-subset-independent-raw-review-v3'")
oldend="""               'new_completions_after_review_start_not_reviewed': sorted({j['key'] for j in manifest['jobs'] if (Path(j['output_dir']) / 'completion.json').is_file()} - selected_keys),
               'full_56_registered_keys_reviewed':len(jobs)==56,
"""
newend="""               'extra_completed_at_start_not_reviewed':extra_completed_at_start_not_reviewed,
               'extra_completed_at_end_not_reviewed': sorted({j['key'] for j in manifest['jobs'] if (Path(j['output_dir']) / 'completion.json').is_file()} - selected_keys),
               'full_56_registered_keys_reviewed':selected_keys==manifest_keys,
               'subset_contract':'Exact registered keys from immutable supplied root receipt; every selected completion SHA must match, later/extra completions are explicitly excluded.',
               'cache_accounting_contract':'n_cache_replays is preserved legacy compatibility sum: actual STA cache reuse + tested-hash dedup without replay + cached pre-STA rejection. The separated counters are authoritative for interpretation.',
"""
assert new.count(oldend)==1;new=new.replace(oldend,newend)
new=new.replace("'Candidate k excludes baseline STA, cache reuse and pre-STA rejects; baseline 1 per job checked separately.'","'Candidate k excludes baseline STA, measured cache reuse, tested-hash dedup and pre-STA rejects; baseline 1 per job checked separately. Legacy cache count is not pure STA reuse.'")
ast.parse(new)
target=O/'checker_v3.py'
with target.open('x',encoding='utf-8',newline='\n') as f:f.write(new)
(O/'checker_v2_to_v3.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),new.splitlines(True),fromfile='checker_v2.py',tofile='checker_v3.py')),encoding='utf-8')
shutil.copy2(R/'scratch/diagnose_D_duplicate_1018.log',O/'DIAGNOSIS_RUN.log')
details=json.loads((O/'DUPLICATE_DETAILS.json').read_text(encoding='utf-8'))
with (O/'FIRST_FAILURE_s641_FOUR.json').open('x',encoding='utf-8') as f:json.dump([d for d in details if d['job']=='D/fixed/s641'],f,indent=2);f.write('\n')
value={'status':'prepared AST syntax checked; not executed; root review required before run','ancestor':old.relative_to(R).as_posix(),'ancestor_sha256':sha(old),'checker_v3_sha256':sha(target),'helper_sha256':sha(O/'classification_helper_v3.py'),'minimaldiff_sha256':sha(O/'checker_v2_to_v3.diff'),'diagnosis_sha256':sha(O/'DIAGNOSIS.json'),'explicit_contract_changes':['Frozen immutable registered subset accepted; extras excluded at both start and end; full56 iff exact registered set','Cache count split by launch reuse, tested-hash no-replay dedup and cached pre-STA rejection; preserved old aggregate','Raw missing base is never filled; exact commit-chain plus cache formula inference recorded; ambiguous records fail closed'],'new_EDA_runs':0,'old_source_or_checker_mutations':0}
with (O/'V3_PREPARATION_RECEIPT.json').open('x',encoding='utf-8') as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps(value,indent=2))
