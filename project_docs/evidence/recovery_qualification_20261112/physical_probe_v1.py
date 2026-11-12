"""Bounded s382 qualification probe; archived recipes, never rewrites input data."""
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'code/src'))
from rseco.opensta import _to_sta_path
from rseco.routed_sta import ROUTED_STA_TCL

HERE = Path(__file__).resolve().parent
PLATFORM = '/home/toylog/OpenROAD-flow-scripts/flow/platforms/sky130hd'
ORFS = _to_sta_path(ROOT / 'data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629')
OPENROAD = '/home/toylog/faeco_eda/or26Q3/bin/openroad'
RECIPE = ROOT / 'experiments/20261112_resizer_recovery/arms/RECOVERED_V2/s382/summary.json'
SPEF = ROOT / 'experiments/20261115_p1_resizer_vs_faeco/arms/Resizer/s382/routed.spef'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(argv, logfile, timeout):
    start = time.monotonic()
    with logfile.open('wb') as log:
        try:
            p = subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            rc = 124
    return dict(argv=argv, returncode=rc, elapsed_s=time.monotonic()-start)

def main(arm):
    assert arm in {'CONTROL', 'RECOVERY_V2', 'NATIVE'}
    out = HERE / 'phase1' / arm
    if out.exists():
        raise SystemExit('Refusing to overwrite existing arm')
    out.mkdir(parents=True)
    odb = HERE / 'phase0/reentry.odb'
    base = HERE / 'phase0/manifest.json'
    assert json.loads(base.read_text())['pass_sta_reentry']
    manifest = dict(arm=arm, input_sha256={str(p.relative_to(ROOT)):sha(p) for p in [odb,base,SPEF,RECIPE,Path(__file__)]},
                    native_parasitics='original extracted SPEF at entry',clock='propagated for native; ideal/propagated separate final measurements',
                    route_iterations=15, per_route_timeout_s=900, per_sta_timeout_s=300)
    def save():
        (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    changes=''
    if arm=='RECOVERY_V2':
        for ev in json.loads(RECIPE.read_text())['applied']:
            assert re.fullmatch(r'\w+',ev['instance'])
            assert re.fullmatch(r'\w+',ev['old_cell'])
            changes += f"replace_cell {ev['instance']} {ev['old_cell']}\n"
    elif arm=='NATIVE':
        changes='repair_timing -recover_power 100\n'
    tcl=f'''read_liberty {PLATFORM}/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_db {_to_sta_path(odb)}
create_clock -name clk -period 0.5 [get_ports CK]
set_propagated_clock [all_clocks]
source {ORFS}/setRC.tcl
read_spef {_to_sta_path(SPEF)}
{changes}
detailed_placement
check_placement -verbose
set_routing_layers -signal met1-met5 -clock met3-met5
pin_access
global_route
detailed_route -output_drc {_to_sta_path(out/'drc.rpt')} -verbose 0 -droute_end_iter 15
check_placement -verbose
write_verilog {_to_sta_path(out/'routed.v')}
write_def {_to_sta_path(out/'routed.def')}
write_db {_to_sta_path(out/'routed.odb')}
define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file {ORFS}/rcx/rcx_patterns.rules
write_spef {_to_sta_path(out/'routed.spef')}
puts "PHYSICAL_PROBE_OK"
exit
'''
    (out/'flow.tcl').write_text(tcl,encoding='utf-8')
    manifest['tcl_sha256']=sha(out/'flow.tcl')
    save()
    print(f'{arm}: start physical pipeline',flush=True)
    manifest['flow']=run(['wsl.exe','-d','Ubuntu','--',OPENROAD,'-no_init','-exit',_to_sta_path(out/'flow.tcl')],out/'flow.log',900)
    save()
    if manifest['flow']['returncode'] or 'PHYSICAL_PROBE_OK' not in (out/'flow.log').read_text(errors='replace'):
        print(f'{arm}: flow failed; inspect log',flush=True)
        return 1
    drc=out/'drc.rpt'
    manifest['drc_count']=len(re.findall(r'^violation type:',drc.read_text(),re.M)) if drc.exists() else None
    for clock in ['ideal','propagated']:
        text=ROUTED_STA_TCL
        for key,value in [('PLATFORM',PLATFORM),('NETLIST',_to_sta_path(out/'routed.v')),('SPEF',_to_sta_path(out/'routed.spef')),('TOP','s382'),('PERIOD','0.5'),('CLK_PORT','CK')]:
            text=text.replace('__'+key+'__',value)
        if clock=='propagated':
            text=text.replace('read_spef $SPEF','read_spef $SPEF\nset_propagated_clock [all_clocks]')
        text+='\nreport_check_types -max_slew -max_capacitance -violators -digits 6\nreport_worst_slack -min -digits 6\nreport_tns -digits 6\n'
        script=out/f'{clock}.tcl'
        script.write_text(text,encoding='utf-8')
        manifest[clock]=run(['wsl.exe','-d','Ubuntu','--','/usr/local/bin/sta','-no_splash','-exit',_to_sta_path(script)],out/f'{clock}.log',300)
        raw=(out/f'{clock}.log').read_text(errors='replace')
        for name,pattern in [('setup_ns',r'ROUTED_WNS_MAX\s+([-+\d.eE]+)'),('hold_ns',r'ROUTED_WNS_MIN\s+([-+\d.eE]+)')]:
            m=re.search(pattern,raw)
            manifest[clock][name]=float(m.group(1))*1e9 if m else None
        manifest[clock]['tns_reports_ns']=re.findall(r'^tns max\s+([-+\d.eE]+)',raw,re.M)
        manifest[clock]['drv_status']='pending raw report review'
        save()
    manifest['functional_equivalence']='pending'
    save()
    print(json.dumps(manifest,indent=2),flush=True)
    return 0

if __name__=='__main__':
    raise SystemExit(main(sys.argv[1]))
