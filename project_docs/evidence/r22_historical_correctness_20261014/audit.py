"""Read-only historical namespace and SEC-binding audit; never launches EDA."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'code/src'))
from rseco.verilog_modules import module_spans, target_module_text
from rseco.real_wns import build_boundary_closure_checker
from rseco.gate_sizing import parse_mapped_netlist

SOURCES = {}


def register(path, role):
    path = Path(path)
    key = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
    if key not in SOURCES:
        SOURCES[key] = {'exists': path.is_file(), 'roles': []}
        if path.is_file():
            data = path.read_bytes()
            SOURCES[key].update(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
    if role not in SOURCES[key]['roles']:
        SOURCES[key]['roles'].append(role)
    return key


def read(path, role):
    register(path, role)
    return Path(path).read_text(encoding='utf-8-sig')


def load(path, role):
    text = read(path, role).lstrip()
    value, end = json.JSONDecoder().raw_decode(text)
    if text[end:].strip():
        SOURCES[register(path, role)]['trailing_text'] = text[end:].strip()[:100]
    return value


def text_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def nonblank_lines(text):
    # strip_to_single_module adds an empty line after the original header.
    # Retain every nonempty line byte-for-byte; do not normalize helper logic.
    return '\n'.join(line for line in text.splitlines() if line.strip())


def resolve_recorded(path):
    norm = str(path).replace('\\', '/')
    if '/experiments/' in norm:
        return ROOT / ('experiments/' + norm.split('/experiments/', 1)[1])
    if norm.startswith('experiments/'):
        return ROOT / norm
    if '/benchmarks/' in norm:
        return ROOT / ('data/raw/benchmarks/' + norm.split('/benchmarks/', 1)[1])
    return ROOT / norm


def module_dict(text):
    return {m.name: m.text for m in module_spans(text)}


def signatures(text):
    return {c.instance: (c.cell_type, c.pins) for c in parse_mapped_netlist(text)}


def without_wires(text):
    text = re.sub(r'(?m)^\s*wire\b[^;]*;', '', text)
    return re.sub(r'\s+', '', text)


def structure(initial, final, circuit):
    before, after = module_dict(initial), module_dict(final)
    changed = []
    for name in sorted((set(before) | set(after)) - {circuit}):
        if before.get(name) != after.get(name):
            left, right = before.get(name, ''), after.get(name, '')
            changed.append({'module': name,
                            'kind': 'wire_declarations_only' if without_wires(left) == without_wires(right) else 'logic_or_interface_changed',
                            'before_hash': text_hash(left), 'after_hash': text_hash(right),
                            'added_instances': sorted(set(signatures(right))-set(signatures(left))),
                            'added_wire_names': sorted(set(re.findall(r'\bwire\s+(\w+)\s*;', right))-set(re.findall(r'\bwire\s+(\w+)\s*;', left)))})
    left, right = before[circuit], after[circuit]
    f2 = build_boundary_closure_checker()(left, right)
    base_f2 = build_boundary_closure_checker()(left, left)
    gate_delta = signatures(left), signatures(right)
    return {'initial_modules': list(before), 'final_modules': list(after),
            'helpers_changed': changed,
            'baseline_target_f2': {'status': base_f2.status, 'reason': base_f2.reason},
            'final_target_f2': {'status': f2.status, 'reason': f2.reason},
            'added_top_instances': sorted(set(gate_delta[1])-set(gate_delta[0])),
            'changed_original_top_instances': sorted(g for g in gate_delta[0] if gate_delta[0][g] != gate_delta[1].get(g)),
            'initial_text_hash': text_hash(initial), 'final_text_hash': text_hash(final),
            'initial_top_hash': text_hash(left), 'final_top_hash': text_hash(right)}


def sec_binding(folder, circuit, initial, final):
    script = folder/'verify.ys'
    log = folder/'verify.log'
    answer = {'script': register(script, 'SEC exact script'), 'log': register(log, 'SEC exact log'),
              'present': script.is_file() and log.is_file(), 'bound': False}
    if not answer['present']:
        return answer
    recipe, transcript = read(script, 'SEC exact script'), read(log, 'SEC exact log')
    reads = re.findall(r'^read_verilog\s+([^\n]+)', recipe, re.M)
    gate_path = resolve_recorded(reads[-1].strip().strip('"'))
    gold_path = resolve_recorded(reads[-2].strip().strip('"'))
    answer.update(gold_file=register(gold_path, 'SEC declared gold'), gate_file=register(gate_path, 'SEC declared gate'),
                  log_proved='Equivalence successfully proven!' in transcript,
                  log_unproven_counts=re.findall(r'(\d+) are proven and (\d+) are unproven', transcript))
    if gold_path.is_file() and gate_path.is_file():
        gold, gate = read(gold_path, 'SEC declared gold'), read(gate_path, 'SEC declared gate')
        answer.update(gold_top_hash=text_hash(target_module_text(gold, circuit)),
                      gate_top_hash=text_hash(target_module_text(gate, circuit)),
                      gold_equals_initial_top=target_module_text(gold,circuit)==target_module_text(initial,circuit),
                      gold_equals_initial_top_ignoring_blank_lines=nonblank_lines(target_module_text(gold,circuit))==nonblank_lines(target_module_text(initial,circuit)),
                      gate_equals_actual_final_top=target_module_text(gate,circuit)==target_module_text(final,circuit))
        answer['bound'] = answer['gold_equals_initial_top_ignoring_blank_lines'] and answer['gate_equals_actual_final_top'] and answer['log_proved']
    return answer


def classification(row):
    structural = row['structure']
    harmful = any(h['kind'] == 'logic_or_interface_changed' for h in structural['helpers_changed'])
    issue = structural['final_target_f2']['reason']
    if harmful or ('declared-undriven' in issue and structural['baseline_target_f2']['status']=='pass'):
        return 'invalid', 'actual helper logic/interface changed or new target-module undriven consumed net'
    proof = row.get('sec', {})
    if proof.get('bound'):
        if structural['final_target_f2']['status'] == 'pass':
            return 'valid', 'actual final target bound to successful archived SEC; no harmful namespace change'
        if 'undeclared-consumed' in issue and all(h['kind']=='wire_declarations_only' for h in structural['helpers_changed']):
            return 'valid', 'archived SEC binds final function; helper delta is only unused wire declarations; strict declaration gate nonconforming'
    return 'unidentified', 'no successful independent SEC bound to actual final; structural pass alone is not a proof'


def main():
    for name in ('code/src/rseco/netlist.py','code/src/rseco/real_wns.py','code/src/rseco/verilog_modules.py',
                 'project_docs/evidence/PAPER_EVIDENCE_MANIFEST.md',
                 'paper/zh/figures/data/plot_specs/r21_source_manifest.json',
                 'paper/zh/review_rounds/r21_20261014/sta_ledger_audit.json',
                 'project_docs/evidence/r22_historical_audit_20261014/inputs_manifest.json',
                 'project_docs/evidence/r22_historical_audit_20261014/C_configuration_and_counts.json'):
        register(ROOT/name, 'reused evidence anchor / audit implementation dependency')
    r21=load(ROOT/'paper/zh/figures/data/plot_specs/r21_source_manifest.json','r21 source crosswalk')
    explicit=load(ROOT/'experiments/20260807_real_pr_iscas8/pre_layout_audit_summary.json','A-prime explicit netlist crosswalk')
    pairs={(r['circuit'],r['variant']):ROOT/r['netlist'] for r in explicit['records']}
    circuits=('s27','s382','s420','s641','s713','s820','s832','s953')
    rows=[]
    for c in circuits:
        run=ROOT/'experiments/20260805_tcad_sprint1_iscas89'/c/c
        result=load(run/'outerloop_result.json','A exact result')
        ledger=load(run/'eval_trials.json','A accepted metadata')
        accepted=[t for t in ledger['trials'] if t.get('accepted') is True]
        initial=read(pairs[c,'baseline'],'A-prime explicit baseline')
        final=read(pairs[c,'fixed'],'A-prime explicit accepted candidate counterpart')
        row={'family':'A','circuit':c,'run':str(run.relative_to(ROOT)),
             'accepted_actions':[{k:t.get(k) for k in ('instance','kind','to_type','wns','tns')} for t in accepted],
             'final_source':str(pairs[c,'fixed'].relative_to(ROOT)),
             'structure':structure(initial,final,c),
             'sec':sec_binding(ROOT/'experiments/20260814_iscas89_sec'/c,c,initial,final)}
        actual=signatures(target_module_text(final,c)); old=signatures(target_module_text(initial,c))
        typed={}
        for t in accepted:
            if t['kind']=='JOINT':
                typed.update(item.split(':',1) for item in t['to_type'].split(','))
            elif t['kind'] in ('R','G'):
                typed[t['instance']]=t['to_type']
        row['explicit_counterpart_matches_accepted_types']=all(g in actual and actual[g][0]==typ for g,typ in typed.items())
        row['counterpart_changed_cells_match_accepted_scope']=set(row['structure']['changed_original_top_instances'])==set(typed)
        row['classification'],row['classification_reason']=classification(row)
        rows.append(row)
    print('A8 audited',flush=True)
    aggregation=load(ROOT/'experiments/20260826_aggregation/summary.json','B authoritative instance crosswalk')
    for suite,records in aggregation.items():
        for entry in records:
            c=entry['circuit']
            if c=='picorv32_regs':
                rows.append({'family':'B','suite':suite,'circuit':c,'classification':'unidentified',
                             'classification_reason':'no setup/accepted final; SEC not applicable; no final-pair proof fabricated'})
                continue
            if c=='b17':
                proof=load(ROOT/'experiments/20260908_phase2_b17_resume/sec/sec_result.json','B b17 dedicated SEC hash receipt')
                final_path=resolve_recorded(proof['mapped']); gold_path=resolve_recorded(proof['itc_golden'])
                final=read(final_path,'b17 explicit accepted final from SEC receipt')
                initial=read(gold_path,'b17 explicit SEC gold')
                full_initial=read(ROOT/'experiments/20260908_phase2_b17_resume/b17/mapped.v','b17 mapped baseline')
                row={'family':'B','suite':suite,'circuit':c,'final_source':str(final_path.relative_to(ROOT)),
                     'structure':structure(full_initial,final,c),
                     'sec':{'bound':False,'hash_final_matches':SOURCES[register(final_path,'B final')]['sha256']==proof['mapped_sha256'],
                            'hash_gold_matches':SOURCES[register(gold_path,'B gold')]['sha256']==proof['itc_sha256'],
                            'result':proof['result'],'equiv_unproven':proof['equiv_unproven'],'equiv_proven':proof['equiv_proven']},
                     'classification':'unidentified','classification_reason':'dedicated SEC receipt matches actual final but1 unproven point; no complete proof'}
                rows.append(row);continue
            base=ROOT/('experiments/20260826_'+('picorv32_hetero' if suite=='picorv32' else suite+'_main'))/c
            run=base/c if (base/c/'outerloop_result.json').is_file() else base
            result=load(run/'outerloop_result.json','B authoritative result and committed state')
            initial=read(run/'mapped.v','B mapped baseline')
            final=result['state']['current_netlist_text']
            accepted=result['state'].get('accepted_patches',[])
            row={'family':'B','suite':suite,'circuit':c,'run':str(run.relative_to(ROOT)),
                 'final_source':'outerloop_result.json state.current_netlist_text',
                 'state_final_hash_matches':text_hash(final)==result['state']['current_netlist_hash'],
                 'accepted_patch_count':len(accepted),'structure':structure(initial,final,c),
                 'sec':sec_binding(ROOT/'experiments/20260826_sec'/c,c,initial,final)}
            if accepted:
                meta=accepted[-1].get('metadata',{}).get('sta_provenance') or {}
                if meta.get('output_dir'):
                    candidate=resolve_recorded(meta['output_dir'])/'mapped.v'
                    row['last_committed_source']=register(candidate,'B actual selected candidate from provenance')
                    row['last_committed_file_matches_state']=candidate.is_file() and read(candidate,'B actual selected candidate')==final
            row['classification'],row['classification_reason']=classification(row)
            rows.append(row)
    print('B30 audited',flush=True)
    # Exact byte/top identity can reuse a proof for the same A candidate, without mixing WNS/configs.
    for a in [r for r in rows if r['family']=='A']:
        counterparts=[b for b in rows if b['family']=='B' and b['circuit']==a['circuit'] and b.get('sec',{}).get('bound')
                      and b['structure']['initial_top_hash']==a['structure']['initial_top_hash']
                      and b['structure']['final_top_hash']==a['structure']['final_top_hash']]
        if counterparts:
            a['alternative_identical_pair_sec']={'family':'B','circuit':a['circuit'],'bound':True,
                                               'gold_top_hash':a['structure']['initial_top_hash'],'gate_top_hash':a['structure']['final_top_hash']}
            a['classification']='valid'
            a['classification_reason']='A own SEC gate is unbound, but B archived SEC proves exact same initial/final top pair'
    for directory,label in (('20260924_threearm','D'),('20260924_l2_k1','D_k1')):
        for file in sorted((ROOT/'experiments'/directory).glob('*/s*/outerloop_result.json')):
            result=load(file,'D exact result and committed state')
            run=file.parent;c=result['circuit'];initial=read(run/'mapped.v','D exact mapped baseline')
            final=result['state']['current_netlist_text']
            row={'family':label,'arm':run.parent.name,'circuit':c,'run':str(run.relative_to(ROOT)),
                 'final_source':'outerloop_result.json state.current_netlist_text',
                 'state_final_hash_matches':text_hash(final)==result['state']['current_netlist_hash'],
                 'accepted_patch_count':len(result['state'].get('accepted_patches',[])),
                 'structure':structure(initial,final,c),'sec':{'bound':False,'reason':'no SEC proof referenced by this run result'},
                 'reported_baseline_wns':result['baseline_wns'],'reported_final_wns':result['wns']}
            row['classification'],row['classification_reason']=classification(row)
            identical=[b for b in rows if b['family']=='B' and b['circuit']==c and b.get('sec',{}).get('bound')
                       and b['structure']['initial_top_hash']==row['structure']['initial_top_hash']
                       and b['structure']['final_top_hash']==row['structure']['final_top_hash']]
            if identical and row['classification']!='invalid':
                row['alternative_identical_pair_sec']={'family':'B','circuit':c,'bound':True}
                row['classification']='valid'
                row['classification_reason']='exact initial/final pair equals independently proven B pair; no harmful helper difference'
            rows.append(row)
        print(label+' audited',flush=True)
    old_c=load(ROOT/'project_docs/evidence/r22_historical_audit_20261014/C_configuration_and_counts.json','C previously audited explicit artifact crosswalk')
    selected=[r for r in old_c['runs'] if r['circuit'] in ('s27','s382')]
    for item in selected:
        row={'family':'C_representative','arm':item['arm'],'circuit':item['circuit']}
        paths=item.get('inputs',{})
        if paths.get('mapped.v',{}).get('exists') and paths.get('mapped_hybrid.v',{}).get('exists'):
            initial=read(ROOT/paths['mapped.v']['path'],'C crosswalk declared baseline')
            final=read(ROOT/paths['mapped_hybrid.v']['path'],'C crosswalk declared final output')
            row.update(structure=structure(initial,final,item['circuit']),sec={'bound':False,'reason':'no independent SEC bound in recovered C schema'})
            row['classification'],row['classification_reason']=classification(row)
            row['final_binding']='artifact output role from recovered crosswalk; execution revision/final hash was not captured'
        else:
            row.update(classification='unidentified',classification_reason='canonical result/final artifacts absent; sibling not substituted')
        rows.append(row)
    summaries={family:dict(Counter(r['classification'] for r in rows if r['family']==family)) for family in sorted({r['family'] for r in rows})}
    result={'schema':'r22-historical-correctness-v1','generated_at_utc':datetime.now(timezone.utc).isoformat(),
            'eda_executed':False,'paper_or_production_modified':False,'classifications':summaries,'runs':rows,
            'classification_limit':'valid means archived actual final pair is bound to complete SEC with no harmful namespace defect; unknown does not imply invalid. Declaration-only helper differences are separately reported.',
            'runtime_hash_limit':'Most old SEC scripts/logs do not capture runtime input hashes; file/script bindings and current archive hashes are evidence, not reconstructed runtime receipts.'}
    (OUT/'correctness_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for path,entry in SOURCES.items():
        if path in r21:
            entry['r21_expected_sha256']=r21[path]
            entry['r21_sha256_matches']=entry.get('sha256')==r21[path]
    (OUT/'input_hashes.json').write_text(json.dumps({'sources':SOURCES},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summaries,ensure_ascii=False),flush=True)


if __name__=='__main__':
    main()
