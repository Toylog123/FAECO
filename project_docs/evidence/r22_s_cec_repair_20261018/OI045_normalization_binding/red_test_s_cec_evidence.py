"""CEC stage preservation, exercising production normalization with fake processes."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import pytest
from rseco import structure_resynthesis as sr, yosys_abc as ya
from rseco.cut import CutBoundary

HOST='''module top(a,b,y);
input a,b; output y; wire n;
sky130_fd_sc_hd__inv_1 g1 (.A(a),.Y(n));
sky130_fd_sc_hd__and2_1 g2 (.A(n),.B(b),.X(y));
endmodule
'''
BOUNDARY=CutBoundary(method='m',boundary_inputs=['a'],boundary_outputs=['n'],internal_nets=[],gates=['g1'])
MODEL='module sky130_fd_sc_hd__inv_1(A,Y); input A; output Y; assign Y=~A; endmodule\n'
LIB='library(x) { cell (sky130_fd_sc_hd__inv_1) { area : 1; } }'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def factory(tmp_path,monkeypatch,statuses=('pass','fail'),normalize_fail=False,abc_timeout=False,timeout_bytes=False):
    lib=tmp_path/'cells.lib';lib.write_text(LIB)
    model=tmp_path/'cells.v';model.write_text(MODEL)
    monkeypatch.setattr(ya,'_resolve_yosys_and_abc',lambda **kw:ya._ToolSet(yosys_argv=['fake-yosys'],abc_argv=['fake-abc']))
    commands=[];statusiter=iter(statuses)
    def process(argv,**kwargs):
        commands.append(argv)
        if argv[0]=='fake-yosys':
            if normalize_fail:return subprocess.CompletedProcess(argv,1,'','bad normalize')
            m=re.search(r'write_blif\s+(?:"([^"]+)"|([^;\s]+))',argv[-1]);assert m,argv
            dst=Path(m.group(1) or m.group(2));dst.write_text('.model win\n.inputs a\n.outputs y\n.names a y\n0 1\n.end\n')
            return subprocess.CompletedProcess(argv,0,'normalized','')
        assert argv[0]=='fake-abc'
        if abc_timeout:raise subprocess.TimeoutExpired(argv,1,output=b'partial ABC \xff' if timeout_bytes else 'partial ABC',stderr=b'timed out' if timeout_bytes else 'timed out')
        status=next(statusiter)
        return subprocess.CompletedProcess(argv,0,'Networks are equivalent' if status=='pass' else 'Networks are NOT EQUIVALENT','')
    monkeypatch.setattr(subprocess,'run',process)
    tools=sr.default_resynth_tools(lib,cells_v=model)
    def variant(spec,name,out):
        p=Path(out)/'win_abc.blif';p.write_text('.model win\n.end\n')
        return sr.VariantResult(variant=name,status='ok',window_blif=str(p))
    def techmap(blif,out):
        p=Path(out)/'win_mapped.v';p.write_text('module win(w_1,w_2); input w_1; output w_2;\nsky130_fd_sc_hd__inv_1 m1 (.A(w_1),.Y(w_2));\nendmodule\n');return p
    tools.run_variant=variant;tools.techmap=techmap
    return tools,commands,model

def test_pre_pass_post_fail_retains_two_distinct_proofs(tmp_path,monkeypatch):
    tools,commands,model=factory(tmp_path,monkeypatch)
    outcome=sr.run_structure_resynthesis(HOST,BOUNDARY,tmp_path/'run',tools=tools,variants=('S0',))
    assert outcome.rejections[0]['label']==sr.LABEL_CEC_POST
    pre=tmp_path/'run/S0/cec_pre';post=tmp_path/'run/S0/cec_post'
    assert pre.is_dir() and post.is_dir(),'pre/post must not overwrite the same CEC files'
    a=json.loads((pre/'receipt.json').read_text());b=json.loads((post/'receipt.json').read_text())
    assert a['status']=='pass' and b['status']=='fail'
    assert 'Networks are equivalent' in (pre/'abc_cec.log').read_text()
    assert 'NOT EQUIVALENT' in (post/'abc_cec.log').read_text()
    for folder,receipt in [(pre,a),(post,b)]:
        assert receipt['inputs']['model']['sha256']==digest(model)
        for role in ['reference','candidate','model']:
            row=receipt['inputs'][role];assert digest(Path(row['snapshot']))==row['sha256']
        for name,row in receipt['artifacts'].items():assert digest(folder/name)==row['sha256']
        assert 'cec_left.blif' in receipt['artifacts'] and 'cec_right.blif' in receipt['artifacts'] and 'abc_cec.log' in receipt['artifacts']

def test_pre_fail_short_circuits_mapping_and_post(tmp_path,monkeypatch):
    tools,commands,_=factory(tmp_path,monkeypatch,statuses=('fail',))
    tools.techmap=lambda *a:pytest.fail('pre failure must not execute mapping')
    result=sr.run_structure_resynthesis(HOST,BOUNDARY,tmp_path/'run',tools=tools,variants=('S0',))
    assert result.rejections[0]['label']==sr.LABEL_F1_CEC_PRE
    folder=tmp_path/'run/S0';assert (folder/'cec_pre/receipt.json').exists();assert not (folder/'cec_post').exists()

def test_two_passes_preserve_candidate_semantics_and_proofs(tmp_path,monkeypatch):
    tools,_,_=factory(tmp_path,monkeypatch,statuses=('pass','pass'))
    result=sr.run_structure_resynthesis(HOST,BOUNDARY,tmp_path/'run',tools=tools,variants=('S0',))
    assert len(result.candidates)==1 and result.rejections==[]
    assert result.candidates[0].resynth_stats['cec_pre_map']=='pass'
    assert result.candidates[0].resynth_stats['cec_post_map']=='pass'
    for stage in ['cec_pre','cec_post']:
        receipt=json.loads((tmp_path/'run/S0'/stage/'receipt.json').read_text())
        assert receipt['status']=='pass' and receipt['input_drift']==[]

@pytest.mark.parametrize('mode',['normalize_failure','abc_timeout'])
def test_failed_stages_have_nonpass_receipts(tmp_path,monkeypatch,mode):
    tools,commands,_=factory(tmp_path,monkeypatch,normalize_fail=mode=='normalize_failure',abc_timeout=mode=='abc_timeout')
    reference=tmp_path/'ref.v';reference.write_text('module win(a,y); input a; output y;\nsky130_fd_sc_hd__inv_1 g (.A(a),.Y(y));\nendmodule\n')
    candidate=tmp_path/'gate.blif';candidate.write_text('.model win\n.end\n')
    folder=tmp_path/'proof';result=tools.cec(reference,candidate,folder)
    receipt=json.loads((folder/'receipt.json').read_text())
    assert receipt['status']==result.status!='pass'
    assert receipt['inputs']['reference']['sha256']==digest(reference)
    if mode=='abc_timeout':assert 'partial ABC' in (folder/'abc_cec.log').read_text()
    else:assert 'bad normalize' in (folder/'cec_left.normalize.log').read_text()

def test_existing_stage_is_rejected_without_clobbering_evidence(tmp_path,monkeypatch):
    tools,commands,_=factory(tmp_path,monkeypatch,statuses=('pass',))
    reference=tmp_path/'ref.v';reference.write_text('module win(a,y); input a; output y; assign y=~a; endmodule\n')
    candidate=tmp_path/'gate.blif';candidate.write_text('.model win\n.end\n')
    folder=tmp_path/'proof';folder.mkdir();sentinel=folder/'abc_cec.log';sentinel.write_text('original proof\n');before=digest(sentinel)
    with pytest.raises(FileExistsError):tools.cec(reference,candidate,folder)
    assert digest(sentinel)==before and commands==[]

def test_timeout_with_byte_output_retains_partial_evidence(tmp_path,monkeypatch):
    tools,_,_=factory(tmp_path,monkeypatch,abc_timeout=True,timeout_bytes=True)
    reference=tmp_path/'ref.v';reference.write_text('module win(a,y); input a; output y; assign y=~a; endmodule\n')
    candidate=tmp_path/'gate.blif';candidate.write_text('.model win\n.end\n')
    folder=tmp_path/'proof';result=tools.cec(reference,candidate,folder)
    assert result.status=='timeout'
    assert 'partial ABC' in (folder/'abc_cec.log').read_text(encoding='utf-8')
    assert (folder/'abc_cec.log.stdout.bin').read_bytes()==b'partial ABC \xff'
    assert (folder/'abc_cec.log.stderr.bin').read_bytes()==b'timed out'
    receipt=json.loads((folder/'receipt.json').read_text())
    assert receipt['status']=='timeout' and receipt['artifacts']['abc_cec.log']['sha256']==digest(folder/'abc_cec.log')

@pytest.mark.parametrize('target',['model_source','reference_source','normalized_blif'])
def test_input_drift_cannot_keep_a_passing_receipt(tmp_path,monkeypatch,target):
    tools,_,model=factory(tmp_path,monkeypatch,statuses=('pass',))
    reference=tmp_path/'ref.v';reference.write_text('module win(a,y); input a; output y; assign y=~a; endmodule\n')
    candidate=tmp_path/'gate.blif';candidate.write_text('.model win\n.end\n')
    process=subprocess.run
    folder=tmp_path/'proof'
    def mutate(argv,**kwargs):
        result=process(argv,**kwargs)
        if argv[0]=='fake-abc':
            victim={'model_source':model,'reference_source':reference,'normalized_blif':folder/'cec_left.blif'}[target]
            victim.write_bytes(victim.read_bytes()+b'\nchanged\n')
        return result
    monkeypatch.setattr(subprocess,'run',mutate)
    result=tools.cec(reference,candidate,folder);receipt=json.loads((folder/'receipt.json').read_text())
    assert result.status==receipt['status']=='unavailable'
    assert receipt['input_drift']

@pytest.mark.parametrize('target',['filtered_model','prepared_verilog'])
def test_actual_normalization_read_input_drift_rejects_before_cec(tmp_path,monkeypatch,target):
    tools,commands,_=factory(tmp_path,monkeypatch,statuses=('pass',))
    reference=tmp_path/'ref.v'
    reference.write_bytes(b'\xef\xbb\xbfmodule win(a,y); input a; output y;\nsky130_fd_sc_hd__inv_1 g (.A(a),.Y(y));\nendmodule\n')
    candidate=tmp_path/'gate.blif';candidate.write_text('.model win\n.end\n')
    process=subprocess.run;folder=tmp_path/'proof';mutations=[]
    def mutate(argv,**kwargs):
        if argv[0]=='fake-yosys' and not mutations:
            actual_reads=re.findall(r'read_verilog\s+(?:"([^"]+)"|([^;\s]+))',argv[-1])
            paths=[Path(a or b) for a,b in actual_reads]
            victim=paths[0] if target=='filtered_model' else paths[-1]
            before=digest(victim);victim.write_bytes(victim.read_bytes()+b'\n// drifted while consumed\n');mutations.append((before,digest(victim)))
        return process(argv,**kwargs)
    monkeypatch.setattr(subprocess,'run',mutate)
    result=tools.cec(reference,candidate,folder)
    assert result.status!='pass','actual read_verilog inputs must be pinned during normalization'
    assert len(mutations)==1 and all(a!=b for a,b in mutations)
    assert not any(cmd[0]=='fake-abc' for cmd in commands)
    receipt=json.loads((folder/'cec_left.blif.normalize.receipt.json').read_text())
    assert receipt['input_drift'] and receipt['returned_returncode']!=0
    assert (folder/'cec_left.normalize.log').exists()

def test_normalization_launch_error_keeps_log_and_receipt(tmp_path,monkeypatch):
    tools,_,_=factory(tmp_path,monkeypatch)
    reference=tmp_path/'ref.v';reference.write_text('module win(a,y); input a; output y; assign y=~a; endmodule\n')
    candidate=tmp_path/'gate.blif';candidate.write_text('.model win\n.end\n')
    def missing(*args,**kwargs):raise FileNotFoundError('controlled missing normalization executable')
    monkeypatch.setattr(subprocess,'run',missing)
    folder=tmp_path/'proof';result=tools.cec(reference,candidate,folder)
    assert result.status!='pass'
    assert 'FileNotFoundError' in (folder/'cec_left.normalize.log').read_text(encoding='utf-8')
    receipt=json.loads((folder/'cec_left.blif.normalize.receipt.json').read_text())
    assert receipt['exception_type']=='FileNotFoundError' and receipt['process_launched'] is False

def test_normalization_receipt_refuses_reuse_before_rewriting_filtered_model(tmp_path,monkeypatch):
    tools,commands,model=factory(tmp_path,monkeypatch)
    reference=tmp_path/'ref.v';reference.write_text('module win(a,y); input a; output y;\nsky130_fd_sc_hd__inv_1 g (.A(a),.Y(y));\nendmodule\n')
    output=tmp_path/'normalized.blif';receipt=tmp_path/'normalized.blif.normalize.receipt.json';receipt.write_text('old immutable receipt')
    filtered=tmp_path/'normalized_cells.v';filtered.write_text('old exact filtered model');before=digest(filtered)
    with pytest.raises(FileExistsError):ya._normalize_to_blif(reference,output,yosys_argv=['fake-yosys'],timeout_s=1,liberty_cells_v=model,top_module='win')
    assert receipt.read_text()=='old immutable receipt' and digest(filtered)==before and commands==[]
