"""Wrong-object CEC counterexamples; processes controlled at the tool boundary."""
from pathlib import Path
import json,re,subprocess
import pytest
from rseco import yosys_abc as ya,verilog_modules as vm

IDENTITY='.model ztop\n.inputs A\n.outputs Y\n.names A Y\n1 1\n.end\n'
INVERTER=IDENTITY.replace('1 1','0 1')
DUMMY=IDENTITY.replace('ztop','dummy')
HIERARCHY='.model helper\n.inputs A\n.outputs Y\n.names A Y\n1 1\n.end\n.model ztop\n.inputs A\n.outputs Y\n.subckt helper A=A Y=Y\n.end\n'

@pytest.mark.parametrize('output,rc,wanted',[
 ('networks are equivalent',7,'error'),
 ('warning: the design has 2 root-level modules. the first one (dummy) will be used.\nnetworks are equivalent',0,'error'),
 ('networks are not equivalent\nnetworks are equivalent',0,'fail'),
 ('networks are equivalent',0,'pass'),('networks are not equivalent',0,'fail'),
])
def test_abc_success_needs_clean_exit_and_unambiguous_object(output,rc,wanted):
    assert ya._abc_status_from_output(output,rc)==wanted

@pytest.mark.parametrize('text,requested,wanted',[
 (IDENTITY,None,'ztop'),(HIERARCHY,None,'ztop'),
 (DUMMY+INVERTER,None,None),(INVERTER+DUMMY,None,None),
 (DUMMY+INVERTER,'ztop','ztop'),(IDENTITY,'missing',None),
])
def test_selects_actual_blif_root_without_first_model_guess(text,requested,wanted):
    if wanted is None:
        with pytest.raises(ValueError):vm.select_blif_top_module(text,requested)
    else:assert vm.select_blif_top_module(text,requested)==wanted

def tools(monkeypatch,*,baseline_multi=False):
    monkeypatch.setattr(ya,'_resolve_yosys_and_abc',lambda **kw:ya._ToolSet(yosys_argv=['fake-yosys'],abc_argv=['fake-abc']))
    def process(argv,**kw):
        script=argv[-1]
        if argv[0]=='fake-yosys':
            path=Path(re.search(r'write_blif\s+([^;\s]+)',script)[1]);top=re.search(r'hierarchy -check -top\s+(\w+)',script)[1]
            path.write_text(IDENTITY.replace('ztop',top),encoding='utf-8')
            return subprocess.CompletedProcess(argv,0,'normalized','')
        assert argv[0]=='fake-abc'
        if 'write_blif ' in script:
            path=Path(re.search(r'write_blif\s+([^;\s]+)',script)[1]);path.write_text(DUMMY+INVERTER if baseline_multi else IDENTITY)
            return subprocess.CompletedProcess(argv,0,'n : i/o = 1/ 1 lat = 0 and = 0 lev = 0','')
        return subprocess.CompletedProcess(argv,0,'Networks are equivalent','')
    monkeypatch.setattr(subprocess,'run',process)

@pytest.mark.parametrize('text',[DUMMY+INVERTER,INVERTER+DUMMY])
def test_mapped_boundary_rejects_independent_roots_in_either_order(tmp_path,monkeypatch,text):
    tools(monkeypatch);original=tmp_path/'original.v';original.write_text('module ztop(input A,output Y);assign Y=A;endmodule\n')
    mapped=tmp_path/'mapped.blif';mapped.write_text(text)
    result=ya.check_mapped_blif_equivalence(original,mapped,artifact_dir=tmp_path/'proof')
    assert result.status!='pass'

def test_mapped_boundary_preserves_reachable_helper_and_receipt(tmp_path,monkeypatch):
    tools(monkeypatch);original=tmp_path/'original.v';original.write_text('module ztop(input A,output Y);assign Y=A;endmodule\n')
    mapped=tmp_path/'mapped.blif';mapped.write_text(HIERARCHY)
    result=ya.check_mapped_blif_equivalence(original,mapped,artifact_dir=tmp_path/'proof')
    assert result.status=='pass'
    receipts=list((tmp_path/'proof').glob('revised.normalized.blif.normalize/attempt*/receipt.json'))
    assert len(receipts)==1
    receipt=json.loads(receipts[0].read_text());assert receipt['selected_top_module']=='ztop'
    assert receipt['input_format']=='blif' and receipt['input_drift']==[]

def test_explicit_mapped_top_must_exist(tmp_path,monkeypatch):
    tools(monkeypatch);original=tmp_path/'original.v';original.write_text('module ztop(input A,output Y);assign Y=A;endmodule\n')
    mapped=tmp_path/'mapped.blif';mapped.write_text(IDENTITY)
    result=ya.check_mapped_blif_equivalence(original,mapped,artifact_dir=tmp_path/'proof',mapped_top_module='missing')
    assert result.status!='pass'

def test_baseline_backcheck_does_not_accept_multiroot_generated_output(tmp_path,monkeypatch):
    tools(monkeypatch,baseline_multi=True);original=tmp_path/'original.v';original.write_text('module ztop(input A,output Y);assign Y=A;endmodule\n')
    result=ya.run_yosys_abc_resynthesis_baseline(original,output_dir=tmp_path/'baseline')
    assert result.status!='success'
