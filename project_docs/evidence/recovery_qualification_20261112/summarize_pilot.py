"""Recompute pilot effects from complete named-cell netlists and endpoint receipts."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT/'code/scripts'))
from recover_area import load_liberty_areas
from check_phase0_structure import Reader, sha

areas = load_liberty_areas()
rows = []
for arm in ['CONTROL', 'RECOVERY_V2', 'NATIVE']:
    out = HERE/'phase1_v2'/arm
    manifest = json.loads((out/'manifest.json').read_text())
    structure, _ = Reader((out/'routed.v').read_text()).parse()
    included = {}
    omitted = {}
    for name, value in structure['instances'].items():
        cell=value['cell']
        if cell in areas:
            included[name]=areas[cell]
        elif cell=='sky130_fd_sc_hd__tapvpwrvgnd_1' and not value['pins']:
            omitted[name]=cell
        else:
            raise ValueError(f'Unknown connected cell or unsupported physical cell: {name} {cell}')
    row={'arm':arm,'liberty_known_instances':len(included),'standard_cell_area_um2':sum(included.values()),
         'excluded_unconnected_tap_instances':len(omitted),'drc_count':manifest['drc_count'],
         'flow_seconds':manifest['flow']['elapsed_s'],'ideal':manifest['ideal'],'propagated':manifest['propagated'],
         'output_sha256':{name:sha(out/name) for name in ['routed.v','routed.def','routed.spef','drc.rpt','flow.log','ideal.log','propagated.log','manifest.json']}}
    assert manifest['flow']['returncode']==0
    for clock in ['ideal','propagated']:
        assert manifest[clock]['returncode']==0
        raw=(out/f'{clock}.log').read_text(errors='replace')
        assert 'ROUTED_STA_OK' in raw and 'Error:' not in raw and '[ERROR' not in raw
    rows.append(row)
control=rows[0]
for row in rows:
    row['total_area_reduction_pct']=100*(control['standard_cell_area_um2']-row['standard_cell_area_um2'])/control['standard_cell_area_um2']
    row['strict_timing_nonworsening']={}
    for clock in ['ideal','propagated']:
        changes={k:row[clock][k]-control[clock][k] for k in ['setup_ns','hold_ns']}
        changes['tns_ns']=float(row[clock]['tns_reports_ns'][-1])-float(control[clock]['tns_reports_ns'][-1])
        row['strict_timing_nonworsening'][clock]={'deltas':changes,'pass':all(x>=-1e-6 for x in changes.values())}
report={'scope':'s382 feasibility only; known-liberty standard-cell area excluding unconnected physical tap cells',
        'status':'NON_PROMOTION','timing_tolerance_ns':1e-6,'drv_coverage':'raw reports empty; constraints coverage not established',
        'note':'All designs have negative setup slack; nonworsening is not timing closure. Native zero actions does not establish strongest-baseline superiority.',
        'rows':rows}
(HERE/'PILOT_SUMMARY.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
for row in rows:
    print(row['arm'],row['standard_cell_area_um2'],row['total_area_reduction_pct'],row['propagated']['setup_ns'],row['drc_count'],row['strict_timing_nonworsening']['propagated'])
