"""No-tool minimal reproduction of current generated physical STA Tcl order."""
from pathlib import Path
from unittest.mock import patch
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'code/src'))
import rseco.opensta as sta
source=ROOT/'code/src/rseco/opensta.py'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
def forbid(*args,**kwargs):raise AssertionError('External invocation prohibited')
folder=OUT/'opensta_order_probe'
assert not folder.exists()
with patch.object(sta,'_resolve_sta',return_value=None),patch.object(sta.subprocess,'run',forbid):
    result=sta.run_opensta_sequential(netlist_path=OUT/'not_executed_mapped.v',period=0.5,output_dir=folder,top_module='top',spef_path=OUT/'not_executed.spef')
tcl=(folder/'sta.tcl').read_text()
assert tcl.index('report_checks')<tcl.index('read_spef')<tcl.index('report_worst_slack')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
with (OUT/'OPENSTA_ORDER_PROBE.json').open('x',encoding='utf-8') as f:
    json.dump({'production_source_sha256':digest,'generated_tcl':tcl,'return_value':result,'external_process_calls':0,'source_stable':True,'confirmed':'first path report is ideal; worst-slack report follows parasitic annotation'},f,indent=2)
print('Confirmed generated mixed-report order; external process calls 0.')
