"""Bounded actual OpenSTA annotation falsification; no paper gain estimates."""
from pathlib import Path
import sys, subprocess, json, hashlib, time
sys.path.insert(0,str(Path('code/src').resolve()))
from rseco.spef import parse_mapped_verilog,build_spef
from rseco.opensta import LIB_SEQ,_to_sta_path,_sta_failure_reason,run_opensta_sequential

out=Path('project_docs/evidence/r22_spef_topology_repair_20261018/actual_tool_binding')
out.mkdir(exist_ok=False)
sources=[Path('code/src/rseco/spef.py'),Path('code/src/rseco/opensta.py'),LIB_SEQ]
def pins():return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
before=pins();lib=LIB_SEQ.read_text(encoding='utf-8')
(out/'PRE_REGISTER.json').write_text(json.dumps({'scope':'Micro correctness controls; not a benchmark gain or physical validation','sources':before,'timeout_each_s':30,'serial':True,'unit_lengths_um':[40,4000],'controls':['ordinary','escaped_literal_vs_bus_bit','missing_pin']},indent=2),encoding='utf-8')
rows=[]
for escaped in [False,True]:
    name='escaped' if escaped else 'ordinary'
    d=out/name;d.mkdir()
    bus='q[0]' if escaped else 'qvec'
    literal='\\q[0] ' if escaped else 'qlit'
    wires='wire [0:0] q; wire \\q[0] ;' if escaped else 'wire qvec, qlit;'
    net=d/'mapped.v'
    net.write_text(f'module top(input CK,A,output Z); {wires}\n'
        f'sky130_fd_sc_hd__dfxtp_1 f0 (.CLK(CK),.D(A),.Q({bus}));\n'
        f'sky130_fd_sc_hd__buf_1 b0 (.A({bus}),.X({literal}));\n'
        f'sky130_fd_sc_hd__dfxtp_1 f1 (.CLK(CK),.D({literal}),.Q(Z));\nendmodule\n',encoding='utf-8')
    topology=parse_mapped_verilog(net,liberty_text=lib,top_module='top')
    for length in [40,4000]:
        case=d/str(length);case.mkdir()
        spef=case/'net.spef';spef.write_text(build_spef(topology,unit_len_um=length),encoding='utf-8')
        result=run_opensta_sequential(netlist_path=net.resolve(),period=5,output_dir=case/'measurement',top_module='top',spef_path=spef.resolve(),timeout_s=30)
        tcl=(case/'measurement/sta.tcl').read_text(encoding='utf-8').replace('report_checks -path_delay max\n','report_parasitic_annotation -report_unannotated\nreport_checks -path_delay max\n',1)
        (case/'annotation.tcl').write_text(tcl,encoding='utf-8')
        argv=['wsl.exe','-d','Ubuntu','--','/usr/local/bin/sta','-no_splash','-exit',_to_sta_path((case/'annotation.tcl').resolve())]
        p=subprocess.run(argv,capture_output=True,timeout=30)
        (case/'annotation.stdout.bin').write_bytes(p.stdout);(case/'annotation.stderr.bin').write_bytes(p.stderr)
        raw=p.stdout.decode('utf-8',errors='replace')+'\n'+p.stderr.decode('utf-8',errors='replace')
        (case/'annotation.log').write_text(raw,encoding='utf-8')
        rows.append({'case':name,'length_um':length,'result':result,'annotation_argv':argv,'annotation_returncode':p.returncode,'annotation_error':_sta_failure_reason(raw,p.returncode)})
    bad=d/'missing_pin.spef';bad.write_text((d/'40/net.spef').read_text(encoding='utf-8').replace('b0:A','b0:ABSENT'),encoding='utf-8')
    result=run_opensta_sequential(netlist_path=net.resolve(),period=5,output_dir=d/'missing_pin_measurement',top_module='top',spef_path=bad.resolve(),timeout_s=30)
    rows.append({'case':name+'_missing_pin','result':result})
after=pins()
receipt={'scope':'actual OpenSTA micro annotation controls only','source_before':before,'source_after':after,'source_stable':before==after,'cases':rows,
         'artifacts':{str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}}
(out/'RESULT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps({'source_stable':before==after,'cases':rows},ensure_ascii=False))
assert before==after
