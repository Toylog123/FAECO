import importlib.util,json,hashlib
from pathlib import Path
from types import SimpleNamespace
import pytest
R=Path(__file__).resolve().parents[2]
P=R/'project_docs/evidence/r22_cprime_v3_20261016/prepare_inputs.py'
def load():
    spec=importlib.util.spec_from_file_location('prep',P); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
@pytest.fixture
def setup(tmp_path):
    root=tmp_path/'repo'; root.mkdir(); (root/'code').mkdir(); s=root/'code/s.py';s.write_text('source');lib=root/'cells.lib';lib.write_text('library')
    for c in ('s27','s382'):
        p=root/'data/raw/benchmarks/raw/iscas89'/f'{c}.v';p.parent.mkdir(parents=True,exist_ok=True);p.write_text('RTL '+c)
    out=tmp_path/'output';out.mkdir();calls=[]
    def mapper(src,dst):calls.append(src.stem);(dst/'mapped.v').write_text('MAPPED '+src.stem);return []
    common=SimpleNamespace(ROOT=root,LIB=lib,CIRCUITS=('s27','s382'),source_manifest=lambda:{'code/s.py':sha(s)},run_yosys_mapping=mapper)
    manifest={'family':'C-prime-r22','circuits':['s27','s382'],'git_head':'abc','source_manifest':common.source_manifest(),'lib_sha256':sha(lib),'inputs':{c:sha(root/'data/raw/benchmarks/raw/iscas89'/f'{c}.v') for c in common.CIRCUITS}}
    (out/'manifest.json').write_text(json.dumps(manifest));clean=[]
    checker=lambda text,circuit,liberty:{'used_types':['toy'],'two_state_sec_unsupported_reason':None,'f2_identity_status':'pass'}
    return common,out,calls,s,clean,checker

def prepare(t,**kw):
    c,o,_,_,clean,checker=t
    return load().prepare(o,common=c,code_state_checker=lambda h:clean.append(h),static_checker=checker,**kw)
def test_dry_run_never_launches_or_writes(setup,monkeypatch):
    m=load();monkeypatch.setattr(m.subprocess,'run',lambda *a,**k:pytest.fail('external process'))
    c,o,calls,_,clean,checker=setup;result=m.prepare(o,common=c,dry_run=True,code_state_checker=lambda _:pytest.fail('git'),static_checker=checker)
    assert result['status']=='dry_run' and calls==[] and clean==[] and sorted(p.name for p in o.iterdir())==['manifest.json']
def test_maps_once_and_revalidates_receipts(setup):
    result=prepare(setup);c,o,calls,s,clean,checker=setup
    assert calls==['s27','s382'] and result['status']=='prepared'
    r=json.loads((o/'inputs/s27/input.json').read_text());assert r=={'source_manifest':c.source_manifest(),'source_sha256':sha(c.ROOT/'data/raw/benchmarks/raw/iscas89/s27.v'),'mapped_sha256':sha(o/'inputs/s27/mapped.v')}
    before=(o/'preflight.json').read_bytes();prepare(setup);assert calls==['s27','s382'] and (o/'preflight.json').read_bytes()==before
@pytest.mark.parametrize('change',['source','lib','other_rtl','manifest_head'])
def test_pin_drift_rejected_before_mapping(setup,change):
    c,o,calls,s,clean,checker=setup
    if change=='source':s.write_text('changed')
    elif change=='lib':c.LIB.write_text('changed')
    elif change=='other_rtl':(c.ROOT/'data/raw/benchmarks/raw/iscas89/s382.v').write_text('changed')
    else:
        def reject(h):raise RuntimeError('HEAD differs')
        with pytest.raises(RuntimeError):load().prepare(o,['s27'],common=c,code_state_checker=reject,static_checker=checker)
        assert not calls;return
    with pytest.raises(RuntimeError):prepare(setup,circuits=['s27'])
    assert not calls
@pytest.mark.parametrize('artifact',['mapped.v','map.ys','input.json'])
def test_orphan_or_incomplete_prior_run_never_overwritten(setup,artifact):
    c,o,calls,s,clean,checker=setup;p=o/'inputs/s27';p.mkdir(parents=True);(p/artifact).write_text('{}')
    with pytest.raises((RuntimeError,ValueError,KeyError)):prepare(setup)
    assert not calls and (p/artifact).read_text()=='{}'
def test_source_drift_after_mapper_has_no_success_receipt(setup):
    c,o,calls,s,clean,checker=setup;original=c.run_yosys_mapping
    def mapper(src,dst):r=original(src,dst);s.write_text('changed');return r
    c.run_yosys_mapping=mapper
    with pytest.raises(RuntimeError):prepare(setup)
    assert calls==['s27'] and not (o/'inputs/s27/input.json').exists() and not (o/'preflight.json').exists()
def test_static_failure_keeps_mapping_without_success_receipt(setup):
    c,o,calls,s,clean,checker=setup
    def bad(*a):raise ValueError('missing required pin')
    with pytest.raises(ValueError):load().prepare(o,common=c,code_state_checker=lambda h:None,static_checker=bad)
    assert calls==['s27'] and (o/'inputs/s27/mapped.v').exists() and not (o/'inputs/s27/input.json').exists()
def test_mapping_error_rejected(setup):
    c,o,calls,s,clean,checker=setup;c.run_yosys_mapping=lambda *a:['ERROR test']
    with pytest.raises(RuntimeError):prepare(setup)
    assert not (o/'inputs/s27/input.json').exists()
def test_receipt_source_sha_tamper_rejected(setup):
    prepare(setup);c,o,calls,s,clean,checker=setup;p=o/'inputs/s27/input.json';r=json.loads(p.read_text());r['source_sha256']='wrong';p.write_text(json.dumps(r))
    with pytest.raises(RuntimeError):prepare(setup)
    assert calls==['s27','s382']
def test_preflight_mapped_tamper_rejected(setup):
    prepare(setup);c,o,calls,s,clean,checker=setup;(o/'inputs/s27/mapped.v').write_text('tampered')
    with pytest.raises(RuntimeError):prepare(setup)
    assert calls==['s27','s382']

def test_actual_static_gates_required_input_and_tristate():
    m=load()
    lib='''library(test) { cell ("sky130_fd_sc_hd__buf_1") { area : 1; pin("A") { direction : input; } pin("X") { direction : output; function : "A"; } } cell ("sky130_fd_sc_hd__ebufn_1") { area : 1; pin("A") { direction : input; } pin("TE_B") { direction : input; } pin("Z") { direction : output; function : "A"; three_state : "TE_B"; } } }'''
    good='module top(A,Y); input A; output Y; sky130_fd_sc_hd__buf_1 u(.A(A),.X(Y)); endmodule'
    assert m.static_preflight(good,'top',lib)['f2_identity_status']=='pass'
    with pytest.raises(ValueError,match='required input'):m.static_preflight(good.replace('.A(A),',''),'top',lib)
    tri=good.replace('buf_1 u(.A(A),.X(Y))','ebufn_1 u(.A(A),.TE_B(A),.Z(Y))')
    with pytest.raises(ValueError,match='three-state'):m.static_preflight(tri,'top',lib)

@pytest.mark.parametrize('artifact',['mapped.v','input.json','map.ys'])
def test_later_mapping_cannot_mutate_earlier_input(setup,artifact):
    c,o,calls,s,clean,checker=setup;original=c.run_yosys_mapping
    def mapper(src,dst):
        result=original(src,dst)
        (dst/'map.ys').write_text('commands')
        if src.stem=='s382':(o/'inputs/s27'/artifact).write_text('changed after s27 check')
        return result
    c.run_yosys_mapping=mapper
    with pytest.raises(RuntimeError,match='artifact|input'):
        prepare(setup)
    assert calls==['s27','s382'] and not (o/'preflight.json').exists()

def test_existing_preflight_tamper_rejected_without_mapping(setup):
    prepare(setup);c,o,calls,s,clean,checker=setup;p=o/'preflight.json';j=json.loads(p.read_text());j['inputs'][0]['used_types']=['tampered'];p.write_text(json.dumps(j))
    with pytest.raises(RuntimeError):prepare(setup)
    assert calls==['s27','s382']

def test_later_orphan_prevents_any_launch(setup):
    c,o,calls,s,clean,checker=setup;p=o/'inputs/s382';p.mkdir(parents=True);(p/'mapped.v').write_text('orphan')
    with pytest.raises(RuntimeError):prepare(setup)
    assert calls==[] and not (o/'inputs/s27').exists()
