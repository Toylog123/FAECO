import hashlib, json, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'code/src'))
from rseco.routed_sta import sta_routed
from rseco.opensta import _to_sta_path
OUT = ROOT / 'project_docs/evidence/recovery_qualification_20261112/phase0'
OUT.mkdir(parents=True, exist_ok=True)
SRC = ROOT / 'experiments/20261115_p1_resizer_vs_faeco/arms/Resizer/s382'
PLAT = '/home/toylog/OpenROAD-flow-scripts/flow/platforms/sky130hd'
TOOL = '/home/toylog/faeco_eda/or26Q3/bin/openroad'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
manifest = {'stage':'same-state reentry', 'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [SRC/'routed.def',SRC/'routed.v',SRC/'routed.spef',SRC/'result.json',Path(__file__)]}, 'period_ns':0.5, 'clock':'ideal', 'timeout_s':300}
tcl = f'''read_liberty {PLAT}/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_lef {PLAT}/lef/sky130_fd_sc_hd.tlef
read_lef {PLAT}/lef/sky130_fd_sc_hd_merged.lef
read_def {_to_sta_path(SRC/'routed.def')}
create_clock -name clk -period 0.5 [get_ports CK]
check_placement -verbose
write_verilog {_to_sta_path(OUT/'reentry.v')}
write_db {_to_sta_path(OUT/'reentry.odb')}
puts "REENTRY_OK"
exit
'''
(OUT/'reentry.tcl').write_text(tcl,encoding='utf-8')
manifest['tcl_sha256']=sha(OUT/'reentry.tcl')
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
argv=['wsl.exe','-d','Ubuntu','--',TOOL,'-no_init','-exit',_to_sta_path(OUT/'reentry.tcl')]
start=time.monotonic()
with (OUT/'reentry.log').open('wb') as log:
    p=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT,timeout=300)
manifest.update(returncode=p.returncode, elapsed_s=time.monotonic()-start,argv=argv)
if p.returncode: raise SystemExit(p.returncode)
print('DEF reentry complete, running standalone STA',flush=True)
result=sta_routed(routed_netlist=str(OUT/'reentry.v'),spef_path=str(SRC/'routed.spef'),output_dir=str(OUT/'sta'),top_module='s382',period=0.5,timeout_s=300)
old=json.loads((SRC/'result.json').read_text())
manifest['sta']=result
manifest['original']=old
manifest['wns_delta_ns']=None if result.get('wns') is None else result['wns']-old['wns']
manifest['hold_delta_ns']=None if result.get('min_slack') is None else result['min_slack']-old['min_slack']
manifest['pass_sta_reentry']=all(manifest[k] is not None and abs(manifest[k])<=1e-6 for k in ['wns_delta_ns','hold_delta_ns'])
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2),flush=True)
