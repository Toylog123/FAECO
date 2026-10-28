"""Failure injection only: current public CEC API, no EDA or production mutation."""
from pathlib import Path
import subprocess,sys,hashlib,json,traceback,datetime
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path.cwd().resolve();sys.path.insert(0,str(ROOT/'code/src'))
from rseco import yosys_abc as module
OUT=ROOT/'project_docs/evidence/r22_oi049_timeout_bytes_20261018/red_v2'
OUT.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((ROOT/'experiments/20261018_r22_D_revalidate_v1/manifest.json').read_text(encoding='utf-8'))
before={p:sha(ROOT/p) for p in manifest['source_pin']['files']}
assert before==manifest['source_pin']['files']
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert head==manifest['source_pin']['head']
# Obtain a real TimeoutExpired from Python text-mode subprocess, no EDA executable.
child=[sys.executable,'-c',"import sys,time;print('ready',flush=True);time.sleep(.1);sys.stdout.buffer.write(b'partial output\\n');sys.stdout.flush();sys.stderr.buffer.write(b'partial error\\n');sys.stderr.flush();time.sleep(5)"]
process=subprocess.Popen(child,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
ready=process.stdout.readline()
assert ready=='ready\n'
try:
    process.communicate(timeout=.5)
except subprocess.TimeoutExpired as exc:
    actual=exc
else:
    raise AssertionError('Timeout stimulus did not occur')
finally:
    process.kill();process.communicate(timeout=10)
assert isinstance(actual.stdout,bytes) and actual.stdout
assert isinstance(actual.stderr,bytes) and actual.stderr
(OUT/'partial_stdout.bin').write_bytes(actual.stdout)
(OUT/'partial_stderr.bin').write_bytes(actual.stderr)
source=OUT/'original.v';source.write_text('module top(input a, output y); assign y=a; endmodule\n',encoding='utf-8')
tools=SimpleNamespace(yosys_argv=['MOCK_NO_EDA'],abc_argv=['MOCK_NO_EDA'])
def normalize(src,dest,**kwargs):
    dest.write_text('.model top\n.inputs a\n.outputs y\n.names a y\n1 1\n.end\n',encoding='utf-8')
    return SimpleNamespace(returncode=0,stdout='',stderr='',command=['MOCK_NORMALIZATION_NO_EDA'])
rows=[]
for name,error in [('str_control',subprocess.TimeoutExpired(['mock'],.5,output='partial output\n',stderr='partial error\n')),('actual_bytes_partial',actual),('empty_control',subprocess.TimeoutExpired(['mock'],.5))]:
    case=OUT/name;case.mkdir()
    with patch.object(module,'_resolve_yosys_and_abc',return_value=tools),patch.object(module,'_normalize_to_blif',side_effect=normalize),patch.object(module.subprocess,'run',side_effect=error) as mocked:
        try:
            result=module.check_yosys_abc_equivalence(source,source,outputs=['y'],artifact_dir=case,top_module='top',timeout_s=.5)
            row={'case':name,'returned':result.to_dict(),'exception':None}
        except Exception as failure:
            trace=traceback.format_exc();(case/'traceback.txt').write_text(trace,encoding='utf-8')
            row={'case':name,'returned':None,'exception':type(failure).__name__,'exception_message':str(failure)}
        row['mocked_CEC_calls']=mocked.call_count
        assert mocked.call_count==1
        rows.append(row)
assert rows[0]['returned']['status']=='timeout'
assert rows[1]['exception']=='TypeError' and rows[1]['returned'] is None
assert rows[2]['returned']['status']=='timeout'
after={p:sha(ROOT/p) for p in manifest['source_pin']['files']}
assert after==before
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_head':head,'source_before':before,'source_after':after,'all45_source_unchanged':True,'actual_non_EDA_timeout_child_argv':child,'actual_partial_stdout_type':type(actual.stdout).__name__,'actual_partial_stderr_type':type(actual.stderr).__name__,'rows':rows,'decision':'OI049 reproduced in public CEC timeout presentation; not a proof false-pass; production frozen, no fix applied.','scope':'Normalization and CEC mocked; no new EDA/STA/SEC scientific measurement. Real Python child used only to generate TimeoutExpired byte streams.'}
(OUT/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
(OUT/'RESULT.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rows':rows,'all45_source_unchanged':True,'result_sha256':sha(OUT/'RESULT.json')}))
