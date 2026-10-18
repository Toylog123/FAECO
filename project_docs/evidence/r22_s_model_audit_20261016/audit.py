"""Bounded static S-object/model audit. No STA/Yosys/ABC/Git subprocesses."""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
import ast, hashlib, itertools, json, re, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE=ROOT/'experiments/20260928_s_l1_ablation'
CIRCUITS=['s27','s382','s420','s641','s713','s820','s832','s953']
SOURCES={};OBJECTS={};TEXTS={};BLOCKED=[]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def tsha(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
def rel(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def rd(path,role='actual evidence'):
    path=Path(path);path=path if path.is_absolute() else ROOT/path
    data=path.read_bytes();name=rel(path);digest=hashlib.sha256(data).hexdigest()
    if name in SOURCES:assert SOURCES[name]['sha256']==digest,name
    else:SOURCES[name]={'sha256':digest,'bytes':len(data),'roles':[]}
    if role not in SOURCES[name]['roles']:SOURCES[name]['roles'].append(role)
    return data.decode('utf-8-sig').replace('\r\n','\n')
def load(p,role='actual evidence'):return json.loads(rd(p,role))
def save(name,obj):
    with (OUT/name).open('x',encoding='utf-8',newline='') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
def forbid(*args,**kwargs):
    BLOCKED.append(str(args)[:300]);raise RuntimeError('External process prohibited in static audit')
def obj(text,source,field=None,role='object'):
    digest=tsha(text);TEXTS[digest]=text
    row=OBJECTS.setdefault(digest,{'utf8_LF_text_sha256':digest,'bindings':[]})
    binding={'path':rel(source),'json_field':field,'role':role}
    if binding not in row['bindings']:row['bindings'].append(binding)
    return digest
def mapped_path(value):
    value=str(value).replace('\\','/')
    if '/experiments/' in value:return ROOT/('experiments/'+value.split('/experiments/',1)[1])
    return ROOT/value
def expr_value(expression,env):
    expression=re.sub(r"1'[bBhH]([01])",r'\1',expression.strip())
    tree=ast.parse(expression,mode='eval')
    def ev(node):
        if isinstance(node,ast.Expression):return ev(node.body)
        if isinstance(node,ast.Name):return env[node.id]
        if isinstance(node,ast.Constant) and node.value in (0,1):return int(node.value)
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.Invert):return 1-ev(node.operand)
        if isinstance(node,ast.BinOp):
            a,b=ev(node.left),ev(node.right)
            if isinstance(node.op,ast.BitAnd):return a&b
            if isinstance(node.op,ast.BitOr):return a|b
            if isinstance(node.op,ast.BitXor):return a^b
        raise ValueError('Unsupported 1-bit model expression '+expression)
    return ev(tree)&1

def main():
    started=time.monotonic()
    # Fail before any audit output is overwritten.
    assert not (OUT/'audit.json').exists(),'New audit directory required'
    frozen=load('experiments/20261016_r22_cut_ablation_v3/manifest.json','current production pin')
    for name,digest in frozen['source_manifest'].items():rd(name,'current production source');assert SOURCES[name]['sha256']==digest
    rd(__file__,'this static auditor')
    rd('docs/EXPERIENCE.md','prior experience (context only)')
    claimmap=load('paper/zh/review_rounds/r22_20261016/CLAIM_REPLACEMENT_MAP.json','frozen C13 scope')
    assert next(c for c in claimmap['claims'] if c['id']=='C13')['original_family']=='S-independent'
    oldaudit=load('project_docs/evidence/r22_b_model_audit_20261016/audit.json','reuse prior actual-library model audit')
    sys.path[:0]=[str(ROOT/'code/src'),str(ROOT/'code/scripts')]
    from rseco.logic_rewrite import parse_liberty_cells
    from rseco.gate_sizing import parse_mapped_netlist
    from rseco.verilog_modules import module_spans
    from rseco.real_wns import (validate_cell_input_connections,two_state_sec_unsupported_reason,
        build_boundary_closure_checker,liberty_expression_to_verilog,write_liberty_cell_models)
    from rseco.structure_resynthesis import canonical_netlist_hash
    import run_r22_cut_ablation as common
    for name in ['run','Popen','check_call','check_output','call']:setattr(subprocess,name,forbid)
    liberty=rd(common.LIB,'actual Liberty');assert sha(common.LIB)==frozen['lib_sha256'];cells=parse_liberty_cells(liberty)
    modelpath=ROOT/'data/raw/benchmarks/raw/skywater_cells_models/sky130_cells_v2.v'
    modeltext=rd(modelpath,'retained old model selected by S/CEC logs')
    modelmods={m.name:m.text.strip() for m in module_spans(modeltext)}
    aggregate=load(BASE/'aggregation/summarize_s_l1.json');paired=load(BASE/'aggregation/s_ablation_summary_l1.json')
    runs=[];candidates=[];window_dirs={};model_files={};alltypes=set()
    # Discover retained local proof/window objects by the actual module ID,
    # not directory names alone. Multiple matches remain explicit.
    for c in CIRCUITS:
        folder=BASE/'on'/c/'case/results/structure_resynth';index=defaultdict(list)
        for path in sorted(folder.glob('round*/*/window.v')):
            body=rd(path,'original extracted window')
            match=re.search(r'\bmodule\s+win_([A-Za-z0-9_]+)\s*\(',body)
            if match:index[match.group(1)].append(path.parent)
        window_dirs[c]=index
        for arm in ['off','on']:
            base=BASE/arm/c;rp=base/'outerloop_result.json';lp=base/'eval_trials.json'
            result=load(rp,'actual run state/accepted chain');ledger=load(lp,'actual per-candidate ledger');config=load(base/'run_config.json','actual runtime argv/head')
            initial=rd(base/'mapped.v','actual initial full mapped');ih=obj(initial,base/'mapped.v',role='initial')
            original=rd(base/'case/original/original.v','case wrapper/original counterpart; not assumed identical')
            obj(original,base/'case/original/original.v',role='case original')
            final=result['state']['current_netlist_text'];fh=obj(final,rp,'state.current_netlist_text','accepted final')
            commits=[];current=ih;byhash={ih:{'text_sha256':ih,'wns':result['baseline_wns'],'role':'initial'}}
            for i,p in enumerate(result['state']['accepted_patches']):
                text=p.get('netlist_text');entry={'index':i,'declared':{k:p.get(k) for k in ['patch_id','base_netlist_hash','candidate_hash','netlist_hash','wns']}}
                if text is None:entry['binding']='unknown/missing netlist_text';commits.append(entry);continue
                h=obj(text,rp,f'state.accepted_patches[{i}].netlist_text','accepted commit')
                entry.update(text_sha256=h,base_chain_match=p.get('base_netlist_hash')==current,
                    candidate_hash_match=p.get('candidate_hash')==h,netlist_hash_match=p.get('netlist_hash')==h)
                metadata=p.get('metadata',{});provenance=metadata.get('sta_provenance') or {}
                rawdir=provenance.get('output_dir')
                if rawdir:
                    rawfile=mapped_path(rawdir)/'mapped.v'
                    if rawfile.exists():
                        rawtext=rd(rawfile,'exact committed candidate raw');obj(rawtext,rawfile,role='commit raw')
                        entry.update(raw_path=rel(rawfile),raw_decoded_full_text_equal=rawtext==text,raw_sha256=sha(rawfile))
                byhash[h]={'text_sha256':h,'wns':p.get('wns'),'role':'accepted commit','commit_index':i}
                current=h;commits.append(entry)
            row={'arm':arm,'circuit':c,'run_path':rel(base),'initial_text_sha256':ih,'final_text_sha256':fh,
                'state_final_hash_match':result['state']['current_netlist_hash']==fh,'chain_ends_at_final':current==fh,
                'baseline_wns':result['baseline_wns'],'final_wns':result['wns_history'][-1],
                'runtime_head_declared':config.get('git_head'),'config_path':rel(base/'run_config.json'),
                'S_stats':config.get('structure_resynth_stats'),'commits':commits,'candidate_count':0}
            if arm=='on':
                for number,t in enumerate(ledger['trials']):
                    if t.get('kind')!='S':continue
                    h=obj(t['candidate_netlist_text'],lp,f'trials[{number}].candidate_netlist_text','S full host candidate')
                    metadata=t['resynth'];parts=t['patch_id'].split('::');wid=parts[1];variant=parts[2]
                    d={'circuit':c,'trial_index':number,'patch_id':t['patch_id'],'call_index':t['iteration'],
                        'candidate_text_sha256':h,'declared_candidate_hash':t.get('candidate_hash'),
                        'candidate_hash_match':h==t.get('candidate_hash'),'base_text_sha256':t.get('base_netlist_hash'),
                        'base_binding':byhash.get(t.get('base_netlist_hash')),'accepted':t.get('accepted'),
                        'wns':t['wns'],'metadata':metadata,'local_proof_options':[]}
                    # iteration is the evaluator call index, not the round directory.
                    sd=base/'eval'/f"iter{t['iteration']:03d}_s{t['iteration']:03d}"
                    if (sd/'mapped.v').exists():
                        body=rd(sd/'mapped.v','S actual measured raw');obj(body,sd/'mapped.v',role='S measured raw')
                        log=rd(sd/'sta.log','S actual old STA report');tcl=rd(sd/'sta.tcl','S actual old STA Tcl')
                        values=re.findall(r'worst slack max\s+(-?\d+(?:\.\d+)?)',log)
                        d['sta_binding']={'mapped_path':rel(sd/'mapped.v'),'raw_sha256':sha(sd/'mapped.v'),
                            'full_decoded_text_equal':body==t['candidate_netlist_text'],
                            'log_path':rel(sd/'sta.log'),'tcl_path':rel(sd/'sta.tcl'),
                            'reported_wns_values':[float(x) for x in values],
                            'wns_match':bool(values) and float(values[-1])==t['wns'],
                            'read_verilog_lines':re.findall(r'^read_verilog.*$',tcl,re.M)}
                    for folder in index.get(wid,[]):
                        vd=folder/variant;mv=vd/'win_mapped.v'
                        if not mv.exists():continue
                        mapped=rd(mv,'mapped local S window')
                        canon=canonical_netlist_hash(mapped)
                        if canon!=metadata['canonical_hash']:continue
                        before=rd(folder/'window.v','original local S window')
                        option={'path':rel(vd),'round_directory':folder.parent.name,'window_id':wid,'variant':variant,
                            'window_before_text_sha256':obj(before,folder/'window.v',role='local before'),
                            'window_mapped_text_sha256':obj(mapped,mv,role='local mapped'),'canonical_hash_match':True,
                            'files':{},'old_cec_runtime_input_sha256':'unknown/not recorded'}
                        for name in ['window.v','window.blif','win_abc.blif','win_mapped.blif','abc.log','abc_cec.log',
                                     'cec_left.blif','cec_right.blif','cec_left_cells.v','cec_right_cells.v','window_cells.v','ltp.log','techmap.log']:
                            path=vd/name
                            if path.exists():
                                body=rd(path,'retained local CEC/resynthesis/LTP artifact');option['files'][name]={'path':rel(path),'sha256':sha(path)}
                                if name.endswith('_cells.v'):model_files[rel(path)]=body
                                if name=='abc_cec.log':option.update(cec_log_equivalent='Networks are equivalent' in body,cec_actual_command=body.splitlines()[0])
                                if name=='ltp.log':option.update(ltp_retained_levels=[int(x) for x in re.findall(r'\(length=(\d+)\)',body)],ltp_retained_input_lines=[x for x in body.splitlines() if x.startswith('-- Running command')])
                        d['local_proof_options'].append(option)
                    d['old_local_binding_status']='identified_by_window_module_id_variant_and_canonical_mapped_hash' if d['local_proof_options'] else 'unknown/no exact local counterpart'
                    candidates.append(d);row['candidate_count']+=1
            runs.append(row)
            print('[discover]',arm,c,'commits',len(commits),'S',row['candidate_count'],flush=True)
    save('source_before.json',SOURCES)
    initial_source=dict(SOURCES)
    static={};checker_cache={};model_checks={}
    def checker(top):
        if top not in checker_cache:checker_cache[top]=build_boundary_closure_checker(top_module=top,liberty_text=liberty)
        return checker_cache[top]
    def check_object(h):
        if h in static:return static[h]
        body=TEXTS[h];mods=module_spans(body);physical=[cell for mod in mods for cell in parse_mapped_netlist(mod.text)]
        used=sorted({g.cell_type for g in physical});alltypes.update(used)
        required=[]
        try:validate_cell_input_connections(body,cells)
        except Exception as e:required.append(str(e))
        closure=[]
        for mod in mods:
            result=checker(mod.name)(body,body)
            closure.append({'module':mod.name,'status':result.status,'reason':result.reason})
        item={'physical_cells':len(physical),'used_types':used,'unknown_types':sorted(set(used)-set(cells)),
            'required_inputs_pass':not required,'required_input_errors':required,
            'module_closure':closure,'all_module_closure_pass':all(r['status']=='pass' for r in closure),
            'two_state_unsupported_reason':two_state_sec_unsupported_reason(body,cells),
            'used_multioutput_types':{n:cells[n].output_functions for n in used if n in cells and len(cells[n].output_functions)>1},
            'used_sequential_types':{n:{'kind':cells[n].sequential_kind,'next_state':cells[n].next_state,'clocked_on':cells[n].clocked_on,'clear':cells[n].clear,'preset':cells[n].preset,'outputs':cells[n].output_functions} for n in used if n in cells and cells[n].sequential_kind},
            'used_three_state_types':{n:cells[n].three_state_functions for n in used if n in cells and cells[n].three_state_functions}}
        static[h]=item;return item
    for i,h in enumerate(TEXTS,1):
        check_object(h)
        if i%20==0:print('[static]',i,'/',len(TEXTS),flush=True)
    # Independent bounded 1-bit evaluator controls: never executes a model.
    assert [expr_value('~A',{'A':x}) for x in [0,1]]==[1,0]
    assert [expr_value('(A&B)|(~A&C)',{'A':a,'B':b,'C':c}) for a,b,c in itertools.product([0,1],repeat=3)]==[c if not a else b for a,b,c in itertools.product([0,1],repeat=3)]
    for path,body in model_files.items():
        filtered={m.name:m.text.strip() for m in module_spans(body)}
        checks={}
        for name,block in filtered.items():
            cell=cells.get(name);assignments=dict(re.findall(r'assign\s+(\w+)\s*=\s*([^;]+);',block));issues=[]
            row={'retained_full_model_body_equal':modelmods.get(name)==block,'liberty_outputs':cell.output_functions if cell else None,
                'model_assignments':assignments,'issues':issues}
            if cell is None:issues.append('unknown_actual_Liberty_cell')
            elif cell.three_state_functions:issues.append('three_state_not_proven_by_old_function_only_model')
            elif cell.sequential_kind:
                prior=oldaudit['model_checks'].get(name,{})
                if prior.get('status')=='sequential_semantics_match' and prior.get('model_block','').strip()==block:
                    row['status']='reused_prior_exact_sequential_model_check'
                else:issues.append('sequential_semantics_unknown_requires_fresh_review')
            else:
                for pin,function in cell.output_functions.items():
                    if pin not in assignments:issues.append('missing_output_function:'+pin);continue
                    try:
                        wanted=liberty_expression_to_verilog(function);got=assignments[pin]
                        mismatches=[]
                        for values in itertools.product([0,1],repeat=len(cell.input_pins)):
                            env=dict(zip(cell.input_pins,values))
                            if expr_value(wanted,env)!=expr_value(got,env):mismatches.append(env)
                        if mismatches:issues.append('truth_table_mismatch:'+pin);row['mismatch_rows']=mismatches
                    except Exception as e:issues.append('unsupported_model_expression:'+str(e))
                row['status']='all_actual_output_truth_tables_match' if not issues else 'not_established'
            row.setdefault('status','not_established' if issues else 'all_actual_output_truth_tables_match')
            checks[name]=row
        model_checks[path]=checks
    # Fresh static model output is a plan artifact, not a new formal proof.
    write_liberty_cell_models(liberty,OUT/'actual_used_models_preflight.v',used_cells=alltypes)
    summary={};pairs=[];plans=[]
    for c in CIRCUITS:
        cr=[r for r in runs if r['circuit']==c];sr=[r for r in candidates if r['circuit']==c]
        on=next(r for r in cr if r['arm']=='on');off=next(r for r in cr if r['arm']=='off')
        pairs.append({'circuit':c,'on_final_text_sha256':on['final_text_sha256'],'off_final_text_sha256':off['final_text_sha256'],
            'final_full_text_equal':on['final_text_sha256']==off['final_text_sha256'],
            'endpoint_wns_equal':on['final_wns']==off['final_wns'],'on_final_all_module_closure_pass':static[on['final_text_sha256']]['all_module_closure_pass'],
            'off_final_all_module_closure_pass':static[off['final_text_sha256']]['all_module_closure_pass']})
        summary[c]={'S_records':len(sr),'depth_metadata_reduced':sum(s['metadata']['depth_after_sky130']<s['metadata']['depth_before_sky130'] for s in sr),
            'accepted':sum(bool(s['accepted']) for s in sr),'base_bound':sum(s['base_binding'] is not None for s in sr),
            'base_all_module_closure_pass':sum(bool(s['base_binding']) and static[s['base_text_sha256']]['all_module_closure_pass'] for s in sr),
            'candidate_all_module_closure_pass':sum(static[s['candidate_text_sha256']]['all_module_closure_pass'] for s in sr),
            'candidate_required_inputs_pass':sum(static[s['candidate_text_sha256']]['required_inputs_pass'] for s in sr),
            'candidate_two_state_supported':sum(static[s['candidate_text_sha256']]['two_state_unsupported_reason'] is None for s in sr),
            'candidate_exact_STA_bound':sum(s.get('sta_binding',{}).get('full_decoded_text_equal') is True and s['sta_binding']['wns_match'] for s in sr)}
        for s in sr:
            base=s['base_binding'];delta=None if base is None else s['wns']-base['wns'];s['relative_current_base_delta_ns']=delta
            for opt in s['local_proof_options']:
                paths=[opt['files'][name]['path'] for name in ['cec_left_cells.v','cec_right_cells.v'] if name in opt['files']]
                opt['actual_old_model_defects']={p:[name for name,v in model_checks[p].items() if v['issues']] for p in paths}
                mappedlevels=opt.get('ltp_retained_levels',[])
                opt['after_depth_log_matches_metadata']=bool(mappedlevels) and max(mappedlevels)==s['metadata']['depth_after_sky130']
            plans.append({'id':c+':'+s['patch_id'],'local_before_mapped_pairs':[
                {'gold':rel(ROOT/o['path']).rsplit('/',1)[0]+'/window.v','gate':o['files'].get('win_mapped.v',{}).get('path',o['path']+'/win_mapped.v'),
                 'pre_resynthesis_blif':o['files'].get('win_abc.blif',{}).get('path'),'old_post_cec_log':o['files'].get('abc_cec.log',{}).get('path')} for o in s['local_proof_options']],
                'host_base_text_sha256':s['base_text_sha256'],'host_candidate_text_sha256':s['candidate_text_sha256'],
                'actual_raw_candidate':s.get('sta_binding',{}).get('mapped_path'),
                'base_structurally_eligible':bool(base) and static[s['base_text_sha256']]['all_module_closure_pass'],
                'candidate_structurally_eligible':static[s['candidate_text_sha256']]['all_module_closure_pass'],
                'action':'Do not execute now. Fresh local actual-model CEC + distinct pre/post receipts and both LTP snapshots; whole-host SEC only with legal exact base and required-input/domain gates. Invalid base requires corrected same-family S on/off rerun, not a renamed proof.'})
    def digest_counts(field):return sum(v[field] for v in summary.values())
    totals={k:digest_counts(k) for k in next(iter(summary.values()))}
    totals.update(wns_positive=sum(s['relative_current_base_delta_ns'] is not None and s['relative_current_base_delta_ns']>1e-9 for s in candidates),
        wns_zero=sum(s['relative_current_base_delta_ns'] is not None and abs(s['relative_current_base_delta_ns'])<=1e-9 for s in candidates),
        wns_negative=sum(s['relative_current_base_delta_ns'] is not None and s['relative_current_base_delta_ns']<-1e-9 for s in candidates))
    save('object_registry.json',OBJECTS);save('static_checks.json',static);save('candidate_bindings.json',candidates)
    save('accepted_chains_and_pairs.json',{'runs':runs,'pairs':pairs});save('old_CEC_model_checks.json',model_checks);save('fresh_proof_plan.json',plans)
    after={p:{'sha256':sha(ROOT/p),'bytes':(ROOT/p).stat().st_size,'roles':v['roles']} for p,v in initial_source.items()}
    save('source_after.json',after);changes=[p for p in initial_source if initial_source[p]!=after[p]]
    assert not changes,changes;assert not BLOCKED,BLOCKED
    audit={'schema':'r22-S-static-object-model-audit-v1','created_utc':datetime.now(timezone.utc).isoformat(),
        'head_from_frozen_production_manifest':frozen['git_head'],'production_source_pin':frozen['source_manifest'],
        'eda_executed':False,'git_invoked':False,'external_process_calls':0,'source_stable':True,
        'source_files':len(SOURCES),'unique_text_objects':len(OBJECTS),'S_records':len(candidates),'paired_runs':len(pairs),
        'totals':totals,'per_circuit':summary,'paired_endpoints':pairs,'old_CEC_filtered_model_files':len(model_checks),
        'old_CEC_model_defect_files':{p:{n:v['issues'] for n,v in checks.items() if v['issues']} for p,checks in model_checks.items() if any(v['issues'] for v in checks.values())},
        'old_full_model_path':rel(modelpath),'old_full_model_sha256':sha(modelpath),'actual_liberty_sha256':sha(common.LIB),
        'runtime_s':time.monotonic()-started,'limits':['Static closure is not functional SEC.','Old logs identify paths, not runtime input SHA; retained SHA is not fabricated runtime identity.',
            'CEC_PRE/POST and before/after LTP reuse output paths in retained producer; only retained actual command is credited.',
            'Defective host bases do not imply every S candidate is itself invalid.','No repaired/replayed candidate or new timing result was created.']}
    save('audit.json',audit)
    save('artifact_receipt.json',{'source_before_sha256':sha(OUT/'source_before.json'),'source_after_sha256':sha(OUT/'source_after.json'),
        'files':{p.name:sha(p) for p in OUT.iterdir() if p.is_file()},'eda_executed':False})
    print(json.dumps({'totals':totals,'per_circuit':summary,'model_defect_files':len(audit['old_CEC_model_defect_files']),'source_stable':True,'runtime_s':audit['runtime_s']},ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
