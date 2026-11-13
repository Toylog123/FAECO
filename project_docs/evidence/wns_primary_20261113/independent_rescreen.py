"""Read-only historical reclassification; prints a receipt, runs no EDA."""
from pathlib import Path
from decimal import Decimal
from collections import defaultdict
import copy, hashlib, json, math, re, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E = HERE.parent
sys.path.insert(0, str(HERE))
from structure_reader import Reader
sys.path.insert(0, str(E/'strict_area_search_20261113/space_audit'))
from audit_space import parse_cells, LIB
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
structure = lambda p: Reader(p.read_text(encoding='utf-8')).parse()[0]
canonical_sha = lambda d: hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':')).encode()).hexdigest()
ERR = re.compile(r'(?im)^.*(?:Error:|\[ERROR|invalid command name|wrong # args|failed to).*$')
TOL = 1e-6


def readlog(path, marker):
    raw = path.read_text(encoding='utf-8',errors='replace').replace('\x00','')
    assert marker in raw and not ERR.search(raw), path
    return raw


def metrics(raw):
    result = {}
    for key, token in [('setup_ns','ROUTED_WNS_MAX'),('hold_ns','ROUTED_WNS_MIN')]:
        v = re.findall(token+r'\s+([-+\d.eE]+)',raw)
        assert len(v)==1, token
        result[key] = float(v[0])*1e9
    values = re.findall(r'^tns max\s+([-+\d.eE]+)',raw,re.M)
    assert values and len(values[-1].split('.')[-1])>=9
    result['tns_ns']=float(values[-1])
    assert all(math.isfinite(v) for v in result.values())
    return result


def main():
    repair=E/'recovery_repair_20261113'; strict=E/'strict_area_search_20261113'
    sources=[(repair,'SUMMARY.json','inputs/recipe.json'),
             (repair,'COMBINATION_SUMMARY.json','inputs/recipe.json'),
             (repair,'FORWARD_SUMMARY.json','inputs/recipe.json'),
             (repair,'JOINT_SUMMARY.json','JOINT_RECIPE.json'),
             (strict,'SEARCH_SUMMARY.json','inputs/recipe.json'),
             (strict,'VARIANT_SUMMARY.json','VARIANT_RECIPE.json')]
    control=structure(repair/'inputs/CONTROL/routed.v')
    ref=metrics(readlog(repair/'pathdiag/CONTROL.log','PATHDIAG_TNS9_END'))
    families={re.sub(r'_\d+$','',x['cell']) for x in control['instances'].values()}
    cells,_=parse_cells(LIB.read_text(),families)
    def area(design):
        value=Decimal(0)
        for name,entry in design['instances'].items():
            if entry['cell']=='sky130_fd_sc_hd__tapvpwrvgnd_1':
                assert not entry['pins']
            else:
                assert entry['cell'] in cells,(name,entry['cell'])
                value+=cells[entry['cell']]['area']
        return value
    base_area=area(control)
    rows=[]; bindings={}; logical=defaultdict(list); physical=defaultdict(list)
    for package, summary_name, recipe_name in sources:
        path=package/summary_name; bindings[str(path.relative_to(ROOT))]=sha(path)
        recipe_path=package/recipe_name;bindings[str(recipe_path.relative_to(ROOT))]=sha(recipe_path)
        recipe=load(recipe_path)['applied']
        for archived in load(path)['rows']:
            arm=archived['arm']; folder=package/'runs'/arm
            assert archived['status'].startswith('validated_'),(path,arm)
            for name,h in archived['output_sha256'].items():assert sha(folder/name)==h,(arm,name)
            manifest=load(folder/'manifest.json')
            for name,h in manifest['input_sha256'].items():assert sha(ROOT/name)==h,(arm,name)
            assert manifest['restored_instances']==archived['restored']
            assert manifest['flow']['returncode']==0
            readlog(folder/'flow.log','PHYSICAL_PROBE_OK')
            assert not (folder/'drc.rpt').read_text().strip() and manifest['drc_count']==0
            assert sha(folder/'flow.tcl')==manifest['tcl_sha256']
            design=structure(folder/'routed.v');expected=copy.deepcopy(control)
            for change in recipe:
                assert expected['instances'][change['instance']]['cell']==change['new_cell']
                if change['instance'] not in archived['restored']:
                    expected['instances'][change['instance']]['cell']=change['old_cell']
            assert expected==design,(arm,'full structural mismatch')
            total=area(design);assert float(total)==archived['area']
            for clock in ['ideal','propagated']:
                assert manifest[clock]['returncode']==0
                raw=readlog(folder/(clock+'.log'),'ROUTED_STA_OK')
                measured=metrics(raw);assert measured==archived['metrics'][clock]
                script=(folder/(clock+'.tcl')).read_text()
                for name in ['routed.v','routed.spef']:
                    assert str(folder/name).replace('\\','/').replace('D:','/mnt/d') in script
                assert ('set_propagated_clock [all_clocks]' in script)==(clock=='propagated')
                assert 'report_check_types -max_slew -max_capacitance -violators -digits 9' in script
                drv=re.search(r'ROUTED_STA_OK([\s\S]*?)worst slack min',raw)
                assert drv and 'VIOLATED' not in drv.group(1)
            delta={k:measured[k]-ref[k] for k in ref}
            saving=base_area-total
            eligible=saving>0 and measured['hold_ns']>=0 and delta['setup_ns']>=-TOL and delta['hold_ns']>=-TOL
            old_gate=eligible and delta['tns_ns']>=-TOL
            assert old_gate==archived['primary_numeric_pass']
            info={'source':package.name,'summary':summary_name,'arm':arm,'area':str(total),'area_saved':str(saving),
                  'area_saved_pct':str(saving/base_area*100),'metrics':measured,'deltas_ns':delta,
                  'wns_primary_numeric_pass':eligible,'old_strict_pass':old_gate,
                  'endpoint':str(folder.relative_to(ROOT)).replace('\\','/'),
                  'full_structure_sha256':canonical_sha(design),'output_sha256':archived['output_sha256']}
            rows.append(info)
            logical[info['full_structure_sha256']].append(arm)
            physical[(sha(folder/'routed.v'),sha(folder/'routed.spef'))].append(arm)
    assert len(rows)==52
    ranked=sorted([r for r in rows if r['wns_primary_numeric_pass']],
                  key=lambda r:(-Decimal(r['area_saved']),-r['metrics']['tns_ns'],-r['metrics']['setup_ns'],-r['metrics']['hold_ns'],r['arm']))
    selected=ranked[0]
    root_result=load(HERE/'RESCREEN.json')
    assert selected['arm']==root_result['selected_pending_SEC']['arm'] and len(ranked)==root_result['eligible_count']
    assert [r['arm'] for r in ranked]==[r['arm'] for r in root_result['ranked_eligible']]
    for name,info in load(HERE/'COPY_MANIFEST.json').items():
        assert sha(HERE/name)==info['sha256']==sha(ROOT/info['source']),name
    assert structure(HERE/'inputs/CONTROL/routed.v')==control
    copied=HERE/'runs'/selected['arm']
    selected_design=structure(copied/'routed.v')
    assert selected_design==structure(ROOT/selected['endpoint']/'routed.v')
    actual_changes=[{'instance':n,'source':entry['cell'],'target':selected_design['instances'][n]['cell']}
                    for n,entry in control['instances'].items() if entry['cell']!=selected_design['instances'][n]['cell']]
    receipt={'status':'numerically_eligible_for_SEC_not_final_acceptance','new_EDA':0,'new_SEC':0,
             'reviewer_sha256':sha(Path(__file__)),'policy_sha256':sha(HERE/'PREREGISTRATION.md'),
             'root_rescreen_sha256':sha(HERE/'RESCREEN.json'),'liberty_sha256':sha(LIB),
             'source_sha256':bindings,'control':{'area':str(base_area),'metrics':ref},
             'count':len(rows),'eligible_count':len(ranked),'ranked_eligible':ranked,
             'selected':selected,'selected_actual_changes':actual_changes,
             'unique_full_logical_structures':len(logical),'duplicate_logical_groups':[v for v in logical.values() if len(v)>1],
             'unique_netlist_spef_hash_pairs':len(physical),'duplicate_physical_groups':[v for v in physical.values() if len(v)>1],
             'source_local_copies_identical':True,
             'limitations':['Post-measurement user-directed objective change; old strict failures preserved.',
                            'TNS has no veto under the new policy and its loss is explicitly reported.',
                            'Clock-only constraint/IO and supported-rule DRC/DRV limitations remain.',
                            '52 measured endpoints are not 52 independent circuits or necessarily unique netlists.']}
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':
    main()
