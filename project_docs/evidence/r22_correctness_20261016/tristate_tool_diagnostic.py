"""Registered dirty-tree tool diagnostic; no optimization or timing runs."""
from pathlib import Path
import importlib.util
import subprocess

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('sec_controls', HERE/'sec_model_controls.py')
controls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controls)
batch = controls.batch

def main():
    out = HERE/'tristate_tool_diagnostic'
    if out.exists():
        raise RuntimeError('Never overwrite diagnostic evidence')
    out.mkdir()
    cases = list(controls.CASES[-3:])
    positive = controls.tri_gold.replace('TE_B', 'TE').replace("TE ? 1'bz : ~A", "TE ? ~A : 1'bz")
    good = controls.tri_good.replace('einvn_1', 'einvp_1').replace('TE_B', 'TE')
    bad = controls.tri_bad.replace('einvn_1', 'einvp_1').replace('TE_B', 'TE')
    cases += [('positive_enable_full_semantics',positive,good,'pass'),
              ('positive_enable_inverted',positive,bad,'fail')]
    source = batch.source_manifest()
    lib_sha = batch.sha(batch.LIB)
    receipt = {'diagnostic_only':True, 'timing_runs':0,
               'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=batch.ROOT,text=True).strip(),
               'source_status':subprocess.check_output(['git','status','--porcelain','--','code'],cwd=batch.ROOT,text=True),
               'source_manifest':source, 'liberty_sha256':lib_sha,
               'script_sha256':batch.sha(Path(__file__)),
               'configuration':[dict(name=n,gold=g,gate=c,expected=e) for n,g,c,e in cases],
               'status':'registered','results':[]}
    target=out/'diagnostic.json'
    batch.save(target,receipt)
    for name,gold,gate,expected in cases:
        if batch.source_manifest()!=source or batch.sha(batch.LIB)!=lib_sha:
            raise RuntimeError('Source/input drift')
        try:
            result=batch.final_sec(gold,gate,'top',out/name)
        except ValueError as exc:
            result={'status':'input_error','error':str(exc)}
        receipt['results'].append(dict(name=name,expected=expected,result=result,
                                      matches=result['status']==expected))
        batch.save(target,receipt)
        print(name,expected,result['status'],flush=True)
    receipt['source_stable']=batch.source_manifest()==source and batch.sha(batch.LIB)==lib_sha
    receipt['status']='completed'
    receipt['passed']=receipt['source_stable'] and all(r['matches'] for r in receipt['results'])
    batch.save(target,receipt)
    return 0 if receipt['passed'] else 1

if __name__=='__main__':
    raise SystemExit(main())
