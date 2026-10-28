"""Fresh read-only A8 artifact review. Stdlib only, no EDA or Git process.

Run from repository root with --output NEW_DIRECTORY after producer completion.
This script is a new review, not recovery of any earlier execution script.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, math, re, sys, time

BASE=Path('project_docs/evidence/r22_a_sec_unified_20261018')
CASES=['s27','s382','s420','s641','s713','s820','s832','s953']
READ={}
def sha(data):return hashlib.sha256(data).hexdigest()
def raw(path):
    p=Path(path);b=p.read_bytes();name=str(p.resolve());entry={'bytes':len(b),'sha256':sha(b)}
    if name in READ:assert READ[name]==entry,('read drift',name)
    READ[name]=entry;return b
def text(path):return raw(path).decode('utf-8-sig').replace('\r\n','\n').replace('\r','\n')
def load(path):return json.loads(text(path))
def save(path,obj):
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
def modules(source):
    found=re.findall(r'(?ms)^\s*module\s+(\w+)\b(.*?^\s*endmodule\b)',source)
    result={name:('module '+name+body).strip() for name,body in found}
    assert len(result)==len(found) and result
    return result
def wsl(path):
    s=str(Path(path).resolve()).replace('\\','/');return '/mnt/'+s[0].lower()+s[2:]
def head():
    value=text('.git/HEAD').strip()
    if not value.startswith('ref: '):return value
    ref=value[5:];p=Path('.git')/ref
    if p.is_file():return text(p).strip()
    for line in text('.git/packed-refs').splitlines():
        if line.endswith(' '+ref):return line.split()[0]
    raise AssertionError('missing HEAD ref')
def group_body(source,start):
    """Brace match while excluding quoted text; no project Liberty parser."""
    opening=source.index('{',start);depth=0;quoted=False;escaped=False
    for i in range(opening,len(source)):
        char=source[i]
        if quoted:
            if escaped:escaped=False
            elif char=='\\':escaped=True
            elif char=='"':quoted=False
        elif char=='"':quoted=True
        elif char=='{':depth+=1
        elif char=='}':
            depth-=1
            if depth==0:return source[opening+1:i]
    raise AssertionError('unbalanced Liberty block')
def attrs(source,name):return re.findall(r'\b'+re.escape(name)+r'\s*:\s*"([^"]*)"\s*;',source)
def expression(source):return re.sub(r'\s+','',source).replace("1'b0",'0').replace("1'b1",'1')
def check_models(liberty,generated,used):
    generated_modules=modules(generated);assert set(generated_modules)==set(used)
    checked=[]
    for name in sorted(used):
        hits=list(re.finditer(r'\bcell\s*\(\s*"'+re.escape(name)+r'"\s*\)\s*\{',liberty));assert len(hits)==1,name
        cell=group_body(liberty,hits[0].start());model=generated_modules[name]
        assert not attrs(cell,'three_state'),('unsupported tri-state',name)
        lib_pins={}
        for match in re.finditer(r'(?m)^\s*pin\s*\(\s*"([^"]+)"\s*\)\s*\{',cell):
            body=group_body(cell,match.start());direction=attrs(body,'direction')
            assert len(direction)==1,(name,match.group(1))
            lib_pins[match.group(1)]={'direction':direction[0],'functions':attrs(body,'function')}
        ports={'input':set(),'output':set()}
        for direction in ports:
            for declaration in re.findall(r'\b'+direction+r'\s+([^;]+);',model):ports[direction].update(s.strip() for s in declaration.split(','))
            assert ports[direction]=={p for p,v in lib_pins.items() if v['direction']==direction},(name,direction)
        assignments=dict(re.findall(r'\bassign\s+(\w+)\s*=\s*(.*?);',model))
        assert set(assignments)==ports['output'],name
        for pin in ports['output']:
            functions=lib_pins[pin]['functions'];assert len(functions)==1,(name,pin)
            assert expression(assignments[pin])==expression(functions[0]),(name,pin,assignments[pin],functions[0])
        ff=list(re.finditer(r'\bff\s*\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)\s*\{',cell))
        if ff:
            # Actual A8 uses this one simple positive-edge FF; fail on other semantics.
            assert name=='sky130_fd_sc_hd__dfxtp_1' and len(ff)==1
            body=group_body(cell,ff[0].start());state=ff[0].group(1)
            assert attrs(body,'clocked_on')==['CLK'] and attrs(body,'next_state')==['D']
            assert not attrs(body,'clear') and not attrs(body,'preset')
            assert re.search(r'\breg\s+'+state+r'\s*;',model)
            assert re.search(r'always\s*@\(posedge\s+CLK\)\s+'+state+r'\s*<=\s*D\s*;',model)
        else:assert 'always' not in model and not re.search(r'\blatch\s*\(',cell)
        checked.append({'cell':name,'inputs':sorted(ports['input']),'outputs':sorted(ports['output']),'Liberty_expression_text_and_simple_ff_binding':True})
    return checked

def historical_s820_comparison():
    old=Path('experiments/20260826_sec/s820');new=BASE/'proofs/s820'
    oldscript=text(old/'verify.ys');newscript=text(new/'sec.ys')
    oldlog=text(old/'verify.log');newlog=text(new/'sec.log')
    old_commands=[s.strip() for s in oldscript.splitlines() if s.strip() and not s.startswith('#')]
    new_commands=[s.strip() for s in newscript.splitlines() if s.strip()]
    assert old_commands.index('flatten gold')<old_commands.index('equiv_make gold gate equiv')
    assert old_commands.index('flatten gate')<old_commands.index('equiv_make gold gate equiv')
    assert new_commands.index('equiv_make gold gate equiv')<new_commands.index('flatten')
    assert 'prep -top equiv' in old_commands and 'equiv_status' in old_commands and 'equiv_status -assert' not in old_commands
    assert 'hierarchy -top equiv' in new_commands and 'equiv_status -assert' in new_commands
    def counts(log):
        found=[(int(a),int(b)) for a,b in re.findall(r'Of those cells (\d+) are proven and (\d+) are unproven',log)]
        assert len(found)==1 and found[0][0]>0 and found[0][1]==0
        return list(found[0])
    def nonempty(module):return '\n'.join(s.strip() for s in module.splitlines() if s.strip())
    old_initial=text('experiments/20260826_iscas89_main/s820/s820/case/original/original.v')
    old_final=text(old/'final.v')
    new_initial=text(new/'initial_raw.v');new_final=text(new/'final_raw.v')
    assert nonempty(modules(old_initial)['s820'])==nonempty(modules(new_initial)['s820'])
    assert nonempty(modules(old_final)['s820'])==nonempty(modules(new_final)['s820'])
    retained_model_path=Path('data/raw/benchmarks/raw/skywater_cells_models/sky130_cells_v2.v')
    old_df=modules(text(retained_model_path))['sky130_fd_sc_hd__dfxtp_1']
    new_df=modules(text(new/'cells.v'))['sky130_fd_sc_hd__dfxtp_1']
    assert 'output reg Q;' in old_df and re.search(r'always\s*@\(posedge CLK\)\s*Q\s*<=\s*D',old_df)
    assert 'reg IQ;' in new_df and 'assign Q = IQ;' in new_df
    assert 'sky130_cells_v2.v' in oldscript and 'sky130_cells_v2.v' in oldlog
    selected=lambda log:[{'line':i+1,'text':s} for i,s in enumerate(log.splitlines()) if 'Executing EQUIV_MAKE' in s or 'Executing FLATTEN' in s or 'Executing EQUIV_STATUS' in s or re.search(r'Found \d+ (?:unproven )?\$equiv cells',s) or 'Trying to prove $equiv' in s or 'Of those cells' in s]
    return {'old_proven_unproven':counts(oldlog),'new_proven_unproven':counts(newlog),
            'actual_old_and_new_s820_top_modules_same_ignoring_blank_lines':True,
            'old_scope_commands':old_commands,'new_scope_commands':new_commands,
            'old_actual_log_lines':selected(oldlog),'new_actual_log_lines':selected(newlog),
            'old_current_retained_model_path':str(retained_model_path),'old_current_retained_dfxtp_module':old_df,'new_actual_dfxtp_module':new_df,
            'explanation':'Different equivalence-cell construction: old flattens both sides before equiv_make; new matches hierarchy before flattening. Old retained FF model drives output Q state directly; new pinned Liberty FF has internal IQ then Q assignment. Actual unproven cell identities and structural matches differ. $equiv totals are properties of these proof constructions, not a shared set of comparison points or evidence of proof strength.',
            'limits':'Exact identities of the two additional final cells cannot be recovered without retained RTLIL or a new EDA run; no such run is performed. Current retained old model bytes are not certified contemporaneous old model receipt. Input top comparison does not prove identical whole helper/model setup.'}

def main():
    started=time.monotonic();parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True);args=parser.parse_args()
    assert (BASE/'RUN_RECEIPT.json').is_file(),'producer not complete'
    wrapper=text(BASE/'RUN_WRAPPER.log');assert re.search(r'\[run\].*退出码 0',wrapper),'wrapper not successfully finished'
    out=Path(args.output);out.mkdir(exist_ok=False)
    manifest=load(BASE/'manifest.json');manifest_sha=sha(raw(BASE/'manifest.json'))
    assert manifest_sha.startswith('2cdedb1d')
    assert [r['circuit'] for r in manifest['cases']]==CASES
    assert len(manifest['source_pin']['files'])==45 and head()==manifest['source_pin']['head']
    for name,digest in manifest['source_pin']['files'].items():assert sha(raw(name))==digest,name
    assert sha(raw(BASE/'run_a8_unified_sec_20261018.py'))==manifest['runner_sha256']
    proposal_path=Path('paper/zh/review_rounds/r22_20261016/proof_metadata_correction_02/A8_INPUT_PROPOSAL.json')
    assert sha(raw(proposal_path))==manifest['proposal_sha256']
    proposal=load(proposal_path);assert proposal['cases']==manifest['cases']
    assert proposal['source_pin_from_locked_D_manifest']==manifest['source_pin']
    liberty=text(manifest['liberty']);assert sha(raw(manifest['liberty']))==manifest['liberty_sha256']
    tools_after=load(BASE/'TOOLS_AFTER.json');assert tools_after==manifest['tool_pin']
    for tool in tools_after:
        assert tool['returncode']==0
        assert sha(tool['stdout'].encode())==tool['stdout_sha256']
        assert sha(tool['stderr'].encode())==tool['stderr_sha256']
    assert tools_after[0]['argv']==['wsl.exe','-d','Ubuntu','--','/usr/bin/yosys','-V']
    assert tools_after[0]['stdout'].strip()=='Yosys 0.33 (git sha1 2584903a060)'
    assert tools_after[1]['argv']==['wsl.exe','-d','Ubuntu','--','sha256sum','/usr/bin/yosys']
    binary_sha=tools_after[1]['stdout'].split()[0]
    assert sha(raw(Path(r'\\wsl.localhost\Ubuntu\usr\bin\yosys')))==binary_sha
    batch=load(BASE/'RUN_RECEIPT.json');invocation=load(BASE/'RUN_INVOCATION.json')
    assert batch['returncode']==0 and batch['source_and_inputs_stable'] and batch['tool_identity_stable']
    assert batch['manifest_sha256']==invocation['manifest_sha256']==manifest_sha
    assert invocation['source_head']==manifest['source_pin']['head'] and invocation['serial_proofs']==8
    assert batch['STA_runs']==0 and manifest['sta_runs']==manifest['mapping_runs']==manifest['candidate_search_runs']==0
    assert manifest['parallelism']==1 and manifest['per_proof_timeout_s']==180 and manifest['batch_timeout_s']==1800
    assert len(batch['rows'])==8
    batch_rows={r['circuit']:r for r in batch['rows']}
    wrapper_rows={r['circuit']:r for r in (json.loads(s) for s in wrapper.splitlines() if s.startswith('{'))}
    assert set(wrapper_rows)==set(CASES)
    rows=[]
    for row in manifest['cases']:
        c=row['circuit'];p=BASE/'proofs'/c
        assert row['baseline']['path']==f'experiments/20260805_tcad_sprint1_iscas89/{c}/{c}/mapped.v'
        assert row['accepted_final']['path']==f'experiments/20260807_real_pr_iscas8/{c}/fixed/mapped.v'
        decoded=[];raw_difference={}
        for role,decoded_key,raw_name in [('baseline','baseline_decoded_utf8_sha256','initial_raw.v'),('accepted_final','final_decoded_utf8_sha256','final_raw.v')]:
            source=raw(row[role]['path']);assert sha(source)==row[role]['sha256'] and len(source)==row[role]['bytes']
            assert raw(BASE/'source_snapshots'/c/(role+'.v'))==source
            normalized=text(row[role]['path']);assert sha(normalized.encode())==row[decoded_key]
            assert text(p/raw_name)==normalized
            raw_difference[role]=raw(p/raw_name)!=source
            decoded.append(normalized)
        if c=='s713':assert row['accepted_final']['sha256']=='3c982ac08503110ad5d6c64ed76197da7d4c1fc6acc0cc032a8825d6db43a695'
        before,after=map(modules,decoded);assert sorted(before)==sorted(after)==sorted(row['declared_modules'])
        helpers={name:value for name,value in before.items() if name!=c}
        assert helpers=={name:value for name,value in after.items() if name!=c}
        assert modules(text(p/'gold.v'))=={c:before[c]}
        assert modules(text(p/'gate.v'))=={c:after[c]}
        assert modules(text(p/'helpers.v'))==helpers
        used=set(re.findall(r'\b(sky130_fd_sc_hd__\w+)\s+\w+\s*\(', '\n'.join(decoded)))
        assert used==set(row['used_sky_models'])
        models_checked=check_models(liberty,text(p/'cells.v'),used)
        completion=load(p/'completion.json');result=load(p/'result.json');log=text(p/'sec.log');script=text(p/'sec.ys')
        assert completion==batch_rows[c]==wrapper_rows[c]
        names={f.relative_to(p).as_posix() for f in p.rglob('*') if f.is_file()}-{'completion.json'}
        assert names==set(completion['artifact_sha256'])
        for name,digest in completion['artifact_sha256'].items():assert sha(raw(p/name))==digest,(c,name)
        assert completion['baseline_original_sha256']==row['baseline']['sha256'] and completion['final_original_sha256']==row['accepted_final']['sha256']
        assert result['initial_sha256']==sha(raw(p/'initial_raw.v')) and result['final_sha256']==sha(raw(p/'final_raw.v'))
        assert result['shared_helpers_sha256']==sha(raw(p/'helpers.v'))
        assert result['status']==completion['status']=='pass' and result['returncode']==completion['returncode']==0
        runtime=result['runtime_s'];assert isinstance(runtime,(int,float)) and math.isfinite(runtime) and 0<runtime<=180
        assert runtime==completion['runtime_s']
        assert result['command']==['wsl.exe','-d','Ubuntu','--','/usr/bin/yosys',wsl(p/'sec.ys')]
        commands=[s.strip() for s in script.splitlines() if s.strip()]
        expected=[f'read_verilog "{wsl(p/"cells.v")}"',f'read_verilog "{wsl(p/"helpers.v")}"',f'read_verilog "{wsl(p/"gold.v")}"',f'rename {c} gold',f'read_verilog "{wsl(p/"gate.v")}"',f'rename {c} gate','proc','memory','equiv_make gold gate equiv','hierarchy -top equiv','flatten','opt_clean','equiv_simple','equiv_induct -seq 10','equiv_status -assert']
        assert commands==expected,c
        actual_counts=[(int(a),int(b)) for a,b in re.findall(r'Of those cells (\d+) are proven and (\d+) are unproven',log)]
        assert len(actual_counts)==1 and actual_counts[0][0]>0 and actual_counts[0][1]==0
        assert [completion['proven'],completion['unproven']]==list(actual_counts[0])
        assert re.search(r'Top module:\s+\\equiv\b',log) and 'Equivalence successfully proven!' in log
        assert 'No SAT model available' not in log and not re.search(r'(?m)^ERROR:',log)
        assert 'Yosys 0.33 (git sha1 2584903a060)' in log
        r={'circuit':c,'actual_proven':actual_counts[0][0],'actual_unproven':0,'runtime_s_original':runtime,
           'baseline_original_sha256':row['baseline']['sha256'],'final_original_sha256':row['accepted_final']['sha256'],
           'original_and_snapshot_bytes_equal':True,'decoded_original_and_prover_raw_text_equal':True,
           'raw_serialization_bytes_differ_from_original':raw_difference,'Liberty_models_checked':models_checked,
           'gold_gate_helper_exact_decoded_modules_match':True,'explicit_top_and_success_log':True,
           'result_sha256':sha(raw(p/'result.json')),'completion_sha256':sha(raw(p/'completion.json'))}
        rows.append(r);print('VERIFIED original A',c,actual_counts[0],'runtime original',repr(runtime),flush=True)
    history=historical_s820_comparison()
    save(out/'S820_HISTORICAL_COMPARISON.json',history)
    assert head()==manifest['source_pin']['head']
    before=dict(READ);after={}
    for name,entry in before.items():
        b=Path(name).read_bytes();after[name]={'bytes':len(b),'sha256':sha(b)};assert after[name]==entry,('source/artifact drift',name)
    save(out/'SOURCE_BEFORE.json',before);save(out/'SOURCE_AFTER.json',after)
    report={'schema':'r22-A8-independent-exact-object-review-v1','client_date':'2026-10-18','actual_utc':datetime.now(timezone.utc).isoformat(),'argv':sys.argv,'cwd':str(Path.cwd()),'checker_sha256':sha(Path(__file__).read_bytes()),
            'runtime_s':time.monotonic()-started,'manifest_sha256':manifest_sha,'source_HEAD':manifest['source_pin']['head'],'current_runtime_sources':45,
            'all_read_sources_stable':True,'read_source_count':len(before),'actual_tool_binary_sha256':binary_sha,'actual_tool_binary_rehashed_through_read_only_UNC':True,
            'decision':'Eight registered original A pairs accepted within uniform Boolean SEC domain; root acceptance pending',
            'proof_count':8,'rows':rows,'s820_historical_comparison':history,'no_new_EDA_simulation_test_source_or_Git_command':True,
            'timing_scope':manifest['timing_scope'],
            'limitations':['Fresh uniform A8 batch, separate from historical A6/A2 and from A-prime; no historical proof rewrite.',
                           'Original source snapshots preserve bytes; prover raw serialization may differ due to universal-newline decode and Windows text write. Decoded input text is checked separately.',
                           'Model check compares actual used-cell ports/output expression text and the actual simple dfxtp clock/state semantics to the pinned Liberty, without simulation or EDA.',
                           'Runtime is preserved from producer result/completion/wrapper rows, not remeasured or estimated from CPU log time; concurrent D STA excludes cross-method performance inference.',
                           'No four-state, physical timing, RC calibration or other experiment-family validation.']}
    save(out/'RESULT.json',report);print('RESULT_SHA256',sha((out/'RESULT.json').read_bytes()),'stable sources',len(before),flush=True)

if __name__=='__main__':main()
