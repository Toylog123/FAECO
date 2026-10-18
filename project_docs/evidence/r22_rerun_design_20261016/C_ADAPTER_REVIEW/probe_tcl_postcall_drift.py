"""Independent OI-042 probe. All processes/SEC are fakes; no EDA.

Run with a NEW --output-dir. Reads only the frozen C test/adapter files.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import sys

ROOT=Path(__file__).resolve().parents[4]
FOLDER=ROOT/'project_docs/evidence/r22_rerun_design_20261016/C_RECONSTRUCTION_ADAPTER'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();output=args.output_dir.resolve()
    if output.exists():raise RuntimeError('New output required; no overwrite/resume')
    spec=importlib.util.spec_from_file_location('c_independent_review_fixtures',FOLDER/'test_adapter.py')
    tests=importlib.util.module_from_spec(spec);sys.modules[spec.name]=tests;spec.loader.exec_module(tests)
    adapter=tests.module();backend=tests.FakeBackend(adapter,{'x':[1]});mutated=[]
    def process(argv,**kwargs):
        if not mutated and len(argv)>1 and json.loads(argv[1])['x']=='1':
            path=output/'trial_000000/sta/sta.tcl'
            path.write_text('read_verilog '+(output/'trial_000000/sta/mapped.v').as_posix()+
                            '\nread_liberty /wrong/library.lib\n',encoding='utf-8',newline='')
            mutated.append(str(path))
        return tests.fake_process(argv,**kwargs)
    result=adapter.run_schedule(tests.INITIAL,adapter.Config(rounds=1),backend,output,process_runner=process)
    captured=output/'trial_000000/sta/attempt_001/sta.tcl';current=output/'trial_000000/sta/sta.tcl'
    receipt={'issue':'OI-042','status':result['status'],'commits':result['counts']['commits'],
      'mutated_paths':mutated,'captured_tcl_sha256':adapter.sha(captured),
      'final_tcl_sha256':adapter.sha(current),'completion_exists':(output/'completion.json').is_file(),
      'input_drift_accepted':adapter.sha(captured)!=adapter.sha(current),'eda_executed':False}
    with (output/'independent_probe_receipt.json').open('x',encoding='utf-8') as stream:json.dump(receipt,stream,indent=2)
    print(json.dumps(receipt,indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
