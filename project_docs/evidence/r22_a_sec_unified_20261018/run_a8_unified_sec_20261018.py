"""Fresh, serial SEC of the eight exact A pairs; no mapping, STA or search."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,subprocess,sys,time,re
ROOT=Path.cwd().resolve()
sys.path.insert(0,str(ROOT/'code/scripts'))
import run_r22_d_revalidation as d
from rseco.logic_rewrite import parse_liberty_cells
from rseco.real_wns import validate_cell_input_connections,two_state_sec_unsupported_reason
BASE=ROOT/'project_docs/evidence/r22_a_sec_unified_20261018'
PROPOSAL=ROOT/'paper/zh/review_rounds/r22_20261016/proof_metadata_correction_02/A8_INPUT_PROPOSAL.json'
DROOT=ROOT/'experiments/20261018_r22_D_revalidate_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2)
def tools():
    rows=[]
    for argv in [['wsl.exe','-d','Ubuntu','--','/usr/bin/yosys','-V'],['wsl.exe','-d','Ubuntu','--','sha256sum','/usr/bin/yosys']]:
        p=subprocess.run(argv,capture_output=True,timeout=30)
        assert p.returncode==0
        rows.append({'argv':argv,'returncode':p.returncode,'stdout':p.stdout.decode('utf-8',errors='replace'),'stderr':p.stderr.decode('utf-8',errors='replace'),
                     'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()})
    return rows
def guard(manifest):
    d.validate_manifest(load(DROOT/'manifest.json'),DROOT)
    assert manifest['source_pin']==d.executable_pin()
    assert sha(PROPOSAL)==manifest['proposal_sha256'] and sha(Path(__file__))==manifest['runner_sha256']
    assert sha(d.LIB)==manifest['liberty_sha256']
    for row in manifest['cases']:
        for role in ['baseline','accepted_final']:
            entry=row[role];p=ROOT/entry['path'];assert sha(p)==entry['sha256'] and p.stat().st_size==entry['bytes']
            snapshot=BASE/'source_snapshots'/row['circuit']/(role+'.v');assert snapshot.read_bytes()==p.read_bytes()

args=argparse.ArgumentParser();args.add_argument('mode',choices=['register','run']);mode=args.parse_args().mode
if mode=='register':
    assert not BASE.exists();proposal=load(PROPOSAL)
    assert proposal['read_sources_sha_before_after_stable'] and proposal['new_sta_runs']==0 and not proposal['external_prover_started']
    d.validate_manifest(load(DROOT/'manifest.json'),DROOT)
    assert proposal['source_pin_from_locked_D_manifest']==d.executable_pin()
    cells=parse_liberty_cells(d.LIB.read_text(encoding='utf-8'))
    assert len(proposal['cases'])==8
    for row in proposal['cases']:
        texts=[]
        for role,decoded_key in [('baseline','baseline_decoded_utf8_sha256'),('accepted_final','final_decoded_utf8_sha256')]:
            p=ROOT/row[role]['path'];assert sha(p)==row[role]['sha256']
            text=p.read_text(encoding='utf-8-sig');assert hashlib.sha256(text.encode('utf-8')).hexdigest()==row[decoded_key]
            validate_cell_input_connections(text,cells)
            assert two_state_sec_unsupported_reason(text,cells) is None
            texts.append(text)
        d.common.sec_designs(*texts,row['circuit'])
    tool_pin=tools();BASE.mkdir()
    for row in proposal['cases']:
        p=BASE/'source_snapshots'/row['circuit'];p.mkdir(parents=True)
        for role in ['baseline','accepted_final']:
            with (p/(role+'.v')).open('xb') as f:f.write((ROOT/row[role]['path']).read_bytes())
    (BASE/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    manifest={'schema':'r22-A8-unified-exact-object-SEC-v1','registered_utc':datetime.now(timezone.utc).isoformat(),
      'family':'A exact retained baseline-to-accepted pairs, fresh uniform SEC only','source_pin':d.executable_pin(),
      'proposal_sha256':sha(PROPOSAL),'runner_sha256':sha(Path(__file__)),'liberty':str(d.LIB.relative_to(ROOT)),'liberty_sha256':sha(d.LIB),
      'cases':proposal['cases'],'tool_pin':tool_pin,'parallelism':1,'per_proof_timeout_s':180,'batch_timeout_s':1800,
      'sta_runs':0,'mapping_runs':0,'candidate_search_runs':0,'external_prover_started_at_registration':False,
      'timing_scope':'common.final_sec runtime_s: elapsed external prover invocation and log emission; excludes model/input preparation; D STA runs concurrently; no cross-method performance inference',
      'pass_gate':'Exact inputs/source/lib/tools stable; explicit correct top; statuspass/rc0; actual SEC log nonzero proven/zero unproven; no unsupported; stop on failure; independent audit pending'}
    save(BASE/'manifest.json',manifest);guard(manifest)
    print(json.dumps({'registered':True,'manifest':str(BASE/'manifest.json'),'manifest_sha256':sha(BASE/'manifest.json'),'cases':8,'sta_runs':0,'external_prover_started':False}),flush=True)
else:
    manifest=load(BASE/'manifest.json');guard(manifest);assert tools()==manifest['tool_pin']
    assert not (BASE/'RUN_INVOCATION.json').exists()
    save(BASE/'RUN_INVOCATION.json',{'actual_utc':datetime.now(timezone.utc).isoformat(),'argv':sys.argv,'manifest_sha256':sha(BASE/'manifest.json'),'source_head':manifest['source_pin']['head'],'serial_proofs':8,'STA_runs':0,'outer_wrapper_timeout_s':1800})
    started=time.monotonic();rows=[]
    try:
        for row in manifest['cases']:
            guard(manifest);c=row['circuit'];out=BASE/'proofs'/c;assert not out.exists()
            initial=(ROOT/row['baseline']['path']).read_text(encoding='utf-8-sig');final=(ROOT/row['accepted_final']['path']).read_text(encoding='utf-8-sig')
            result=d.common.final_sec(initial,final,c,out)
            guard(manifest);log=(out/'sec.log').read_text(encoding='utf-8')
            counts=re.findall(r'Of those cells (\d+) are proven and (\d+) are unproven',log)
            assert result['status']=='pass' and result['returncode']==0 and len(counts)==1 and int(counts[0][0])>0 and int(counts[0][1])==0
            assert 'Equivalence successfully proven!' in log and 'No SAT model available' not in log
            assert re.search(r'Top module:\s+\\equiv\b',log)
            assert (out/'initial_raw.v').read_text(encoding='utf-8')==initial and (out/'final_raw.v').read_text(encoding='utf-8')==final
            record={'circuit':c,'proven':int(counts[0][0]),'unproven':int(counts[0][1]),'runtime_s':result['runtime_s'],'status':result['status'],'returncode':result['returncode'],
               'baseline_original_sha256':row['baseline']['sha256'],'final_original_sha256':row['accepted_final']['sha256'],
               'artifact_sha256':{p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()}}
            save(out/'completion.json',record);rows.append(record)
            print(json.dumps(record),flush=True)
        guard(manifest);tool_after=tools();assert tool_after==manifest['tool_pin']
        save(BASE/'TOOLS_AFTER.json',tool_after)
        save(BASE/'RUN_RECEIPT.json',{'status':'all_8_SEC_passed_independent_review_pending','returncode':0,'runtime_s':time.monotonic()-started,'rows':rows,
          'source_and_inputs_stable':True,'tool_identity_stable':True,'STA_runs':0,'manifest_sha256':sha(BASE/'manifest.json')})
    except Exception as error:
        save(BASE/'FAILURE.json',{'error':repr(error),'runtime_s':time.monotonic()-started,'completed_cases':[r['circuit'] for r in rows],'source_and_inputs_revalidation_required':True})
        raise
