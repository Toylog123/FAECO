"""Check that the exact archived false-proof inputs are now refused."""
from pathlib import Path
import importlib.util
import json
import subprocess

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('controls',HERE/'sec_model_controls.py')
c=importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
b=c.batch

def main():
    out=HERE/'tristate_guard_verification'
    if out.exists():
        raise RuntimeError('Never overwrite evidence')
    out.mkdir()
    old=HERE/'tristate_z_diagnostic/diagnostic.json'
    cases=json.loads(old.read_text(encoding='utf-8'))['configuration']
    source=b.source_manifest()
    lib=b.sha(b.LIB)
    record={'status':'registered','purpose':'refusal verification, not four-state equivalence proof',
            'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=b.ROOT,text=True).strip(),
            'source_manifest':source,'liberty_sha256':lib,'historical_diagnostic_sha256':b.sha(old),
            'script_sha256':b.sha(Path(__file__)),'timing_runs':0,'results':[]}
    target=out/'verification.json'
    b.save(target,record)
    for case in cases:
        result=b.final_sec(case['gold'],case['gate'],'top',out/case['name'])
        record['results'].append(dict(name=case['name'],expected='unsupported',result=result,
                                     matches=result['status']=='unsupported' and result['command'] is None))
        b.save(target,record)
        print(case['name'],result['status'],flush=True)
    record.update(status='completed',source_stable=b.source_manifest()==source and b.sha(b.LIB)==lib)
    record['passed']=record['source_stable'] and all(r['matches'] for r in record['results'])
    b.save(target,record)
    return 0 if record['passed'] else 1

if __name__=='__main__':
    raise SystemExit(main())
