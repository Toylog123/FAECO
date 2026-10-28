"""Read/AST/hash only. Does not import or run production, probes or tests."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ast,hashlib,json,re,sys,time
BASE=Path('project_docs/evidence/r22_oi049_timeout_bytes_20261018')
READ={}
def sha(data):return hashlib.sha256(data).hexdigest()
def raw(path):
    p=Path(path);data=p.read_bytes();name=str(p.resolve());entry={'sha256':sha(data),'bytes':len(data)}
    if name in READ:assert READ[name]==entry,name
    READ[name]=entry;return data
def text(path):return raw(path).decode('utf-8-sig').replace('\r\n','\n')
def load(path):return json.loads(text(path))
def save(path,obj):
    with path.open('x',encoding='utf-8',newline='\n')as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
def head():
    value=text('.git/HEAD').strip()
    if not value.startswith('ref: '):return value
    ref=value[5:];p=Path('.git')/ref
    if p.is_file():return text(p).strip()
    return next(line.split()[0]for line in text('.git/packed-refs').splitlines()if line.endswith(' '+ref))
def main():
    started=time.monotonic();parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True);args=parser.parse_args()
    out=Path(args.output);out.mkdir(exist_ok=False)
    result=load(BASE/'red_v3/RESULT.json')
    assert sha(raw(BASE/'red_v3/RESULT.json'))=='bb5e332b4c2c9994c6546388557c68591d3d0a8c9b3277af1c78f28df42a1b27'
    manifest=load('experiments/20261018_r22_D_revalidate_v1/manifest.json')
    assert result['source_before']==result['source_after']==manifest['source_pin']['files'] and len(result['source_before'])==45
    assert result['source_head']==head()==manifest['source_pin']['head']
    for name,digest in result['source_before'].items():assert sha(raw(name))==digest,name
    for directory in ['red_v1','red_v2','red_v3']:
        for f in (BASE/directory).rglob('*'):
            if f.is_file():raw(f)
    for name in ['RED_V2_WRAPPER.log','RED_V3_WRAPPER.log']:raw(BASE/name)
    script=text(BASE/'red_v3/probe_oi049_timeout_bytes_20261018.py');tree=ast.parse(script)
    assert "output=b'partial output\\n',stderr=b'partial error\\n'"in script
    assert "patch.object(module,'_resolve_yosys_and_abc',return_value=tools)"in script
    assert "patch.object(module,'_normalize_to_blif',side_effect=normalize)"in script
    assert "patch.object(module.subprocess,'run',side_effect=error)"in script
    calls=[node for node in ast.walk(tree)if isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)and node.func.attr=='check_yosys_abc_equivalence']
    assert len(calls)==1 and "for name,error in [('str_control'"in script
    rows=result['rows'];assert [r['case']for r in rows]==['str_control','synthetic_bytes_partial','empty_control']
    assert all(r['mocked_CEC_calls']==1 for r in rows)
    assert rows[0]['returned']['status']==rows[2]['returned']['status']=='timeout'
    assert rows[0]['exception']is None and rows[2]['exception']is None
    assert rows[1]['returned']is None and rows[1]['exception']=='TypeError'
    assert rows[1]['exception_message']=='sequence item 0: expected str instance, bytes found'
    assert rows[0]['returned']['stdout_tail']=='partial output' and rows[0]['returned']['stderr_tail']=='partial error'
    assert rows[2]['returned']['stdout_tail']==rows[2]['returned']['stderr_tail']==''
    wrapper=text(BASE/'RED_V3_WRAPPER.log');wire=[json.loads(s)for s in wrapper.splitlines()if s.startswith('{')]
    assert len(wire)==1 and wire[0]['rows']==rows and wire[0]['result_sha256']==sha(raw(BASE/'red_v3/RESULT.json'))
    assert '退出码 0'in wrapper and '超时 60s'in wrapper
    source=text('code/src/rseco/yosys_abc.py');source_tree=ast.parse(source)
    functions={n.name:n for n in source_tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    snippets={name:{'lineno':functions[name].lineno,'end_lineno':functions[name].end_lineno,'source':ast.get_source_segment(source,functions[name])}for name in ['check_yosys_abc_equivalence','_tail','_write_text_log','_run_abc_cec']}
    assert '"\\n".join(text.splitlines()[-max_lines:])'in snippets['_tail']['source']
    assert 'stdout_tail=_tail(exc.stdout or "")'in snippets['check_yosys_abc_equivalence']['source']
    trace=text(BASE/'red_v3/synthetic_bytes_partial/traceback.txt')
    assert 'in check_yosys_abc_equivalence'in trace and 'in _tail'in trace and 'expected str instance, bytes found'in trace
    assert 'in _run_abc_cec'not in trace
    for number in re.findall(r'yosys_abc.py", line (\d+)',trace):assert int(number)<=len(source.splitlines())
    stdout=raw(BASE/'red_v3/partial_stdout.bin');stderr=raw(BASE/'red_v3/partial_stderr.bin')
    assert stdout==b'partial output\n' and stderr==b'partial error\n'
    folder=BASE/'red_v3/synthetic_bytes_partial'
    assert raw(folder/'abc_cec.log.stdout.bin')==stdout and raw(folder/'abc_cec.log.stderr.bin')==stderr
    for row in rows:
        directory=BASE/'red_v3'/row['case'];log=text(directory/'abc_cec.log')
        assert log.startswith('command: MOCK_NO_EDA -s -c cec ')
        for side in ['original','revised']:
            assert text(directory/(side+'.normalized.blif'))=='.model top\n.inputs a\n.outputs y\n.names a y\n1 1\n.end\n'
        if row['case']!='empty_control':assert 'partial output'in log and 'partial error'in log
    v1_script=text(BASE/'red_v1/probe_v1_setup_failed.py');v2_script=text(BASE/'red_v2/probe_v2_setup_failed.py')
    assert v1_script.index('assert isinstance(actual.stdout,bytes) and actual.stdout')<v1_script.index('module.check_yosys_abc_equivalence(')
    assert v2_script.index('assert isinstance(actual.stdout,bytes) and actual.stdout')<v2_script.index('module.check_yosys_abc_equivalence(')
    assert not (BASE/'red_v1/RESULT.json').exists() and not (BASE/'red_v2/RESULT.json').exists()
    v2log=text(BASE/'RED_V2_WRAPPER.log');assert 'AssertionError'in v2log and '退出码 1'in v2log
    v1note=text(BASE/'red_v1/SETUP_FAILURE.md');assert 'not an original redirected raw log'in v1note
    before=dict(READ);after={}
    for name,entry in before.items():
        data=Path(name).read_bytes();after[name]={'sha256':sha(data),'bytes':len(data)};assert after[name]==entry,name
    save(out/'READ_BEFORE.json',before);save(out/'READ_AFTER.json',after)
    report={'schema':'oi049-independent-readonly-review-v1','client_date':'2026-10-18','actual_utc':datetime.now(timezone.utc).isoformat(),'argv':sys.argv,'checker_sha256':sha(Path(__file__).read_bytes()),'runtime_s':time.monotonic()-started,'all_read_sources_stable':True,'read_source_count':len(before),'source_pin_45_files_current_match':True,'source_HEAD':result['source_head'],'current_yosys_abc_sha256':READ[str(Path('code/src/rseco/yosys_abc.py').resolve())]['sha256'],'observed_rows':rows,'source_snippets':snippets,
            'actual_reproduced_API':'check_yosys_abc_equivalence direct subprocess timeout presentation; shared _tail TypeError',
            'evidence_binding':'Three explicit mock CEC calls; str/empty return timeout, nonempty bytes raises TypeError after readable/raw logs are written; wrapper expects this reproduction and exits 0.',
            'old_attempts':'v1/v2 fail setup type/nonempty assumption before public API; v2 has raw redirected wrapper, v1 only transcribed tooltrace. Neither reports actual OS timeout stream type/value.',
            'wording_limit':'v1 SETUP_FAILURE says no partial stdout arrived, but the retained conjunction assertion failure alone cannot distinguish absent/empty bytes from another type; actual type/value remains unknown.',
            'limits':['No probe, pytest, simulation, EDA, tool timeout or Git command was rerun in this review.','No true OS/EDA timeout type or incidence is established.','Mapped _run_abc_cec path shares _tail-related static risk but was not invoked by this three-case probe.','No proof false-pass: controls return timeout and bytes raises an exception, with no successful equivalence verdict.','OI049 is injected-reproduced and remains open/unfixed until source freeze is lifted after D; no production change.'],'decision':'Accept narrowly scoped failure-injection attribution; OI049 remains open'}
    save(out/'RESULT.json',report);print('Verified 3 retained mock rows; source 45/current stable; read',len(before),'RESULT_SHA256',sha((out/'RESULT.json').read_bytes()),flush=True)
if __name__=='__main__':main()
