from pathlib import Path
import sys,json,importlib.util
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'code/scripts'),str(ROOT/'code/src')]
import run_r22_d_revalidation as d
import run_outerloop_real_wns as cli
before=d.executable_pin()
manifest=d.build_manifest(ROOT/'scratch/d56_cli_probe')
rows=[]
for job in manifest['jobs']:
    sys.argv=job['command'][4:]
    actual=vars(cli.parse_args())
    expected=job['expected_run_config']['resolved_args']
    mismatches=[]
    for name,want in expected.items():
        got=actual.get(name)
        if name in {'output_dir','iscas89_dir','source_file','priority_table'} and want is not None:
            want=str(Path(str(want).replace('\\','/')).resolve())
            got=str(Path(str(got).replace('\\','/')).resolve())
        if got!=want:
            mismatches.append(dict(name=name,expected=want,actual=got))
    rows.append(dict(key=job['key'],mismatches=mismatches))
out=ROOT/'project_docs/evidence/r22_correctness_20261016/D56_ACTUAL_CLI_PREFLIGHT.json'
record=dict(eda_executed=False,source_pin=before,source_stable=before==d.executable_pin(),jobs=rows,
            script_sha256=d.sha(Path(__file__)),passed=not any(r['mismatches'] for r in rows))
with out.open('x',encoding='utf-8') as f:json.dump(record,f,ensure_ascii=False,indent=2,default=str)
print(len(rows),'jobs;',sum(bool(r['mismatches']) for r in rows),'mismatches')
raise SystemExit(0 if record['passed'] and record['source_stable'] else 1)
