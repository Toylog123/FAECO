"""Static complete-cell area audit of the s382 pre-Resizer denominator. No EDA."""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import copy, hashlib, json, re, sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
from structure_reader import Reader
from liberty_signature_reader import parse_cells
LIB=ROOT/'data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'
TAP='sky130_fd_sc_hd__tapvpwrvgnd_1'
PINNED_LIB='ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
canonical_sha=lambda obj:hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def def_components(text):
    blocks=list(re.finditer(r'(?m)^COMPONENTS\s+(\d+)\s*;([\s\S]*?)^END COMPONENTS\s*$',text))
    assert len(blocks)==1,'Missing/duplicate COMPONENTS section'
    block=blocks[0];body=block.group(2);result={};pos=0
    records=list(re.finditer(r'\s*-\s+(\S+)\s+(\S+)([\s\S]*?);',body))
    for record in records:
        assert not body[pos:record.start()].strip(),'Unparsed component text'
        name,master=record.group(1),record.group(2)
        assert name not in result,'Duplicate DEF component'
        assert re.fullmatch(r'[A-Za-z0-9_/$]+',name),'Unsupported DEF identifier'
        result[name]=master;pos=record.end()
    assert not body[pos:].strip(),'Unparsed component tail'
    assert len(result)==int(block.group(1)),'Component count mismatch'
    nets=list(re.finditer(r'(?m)^NETS\s+\d+\s*;([\s\S]*?)^END NETS\s*$',text))
    assert len(nets)==1,'Missing/duplicate regular NETS section'
    connections=re.findall(r'\(\s*(\S+)\s+(\S+)\s*\)',nets[0].group(1))
    taps={n for n,m in result.items() if m==TAP}
    assert not any(n in taps for n,pin in connections),'Physical tap has regular signal connection'
    return result


def parse_modules(text):
    # Reader checks every statement inside each complete module, not a cell regex subset.
    cleaned=re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S)
    modules={};pos=0
    for match in re.finditer(r'\bmodule\b[\s\S]*?\bendmodule\b',cleaned):
        assert not cleaned[pos:match.start()].strip(),'Unsupported text outside module'
        design,_=Reader(match.group()).parse()
        assert design['module'] not in modules,'Duplicate module'
        modules[design['module']]=design;pos=match.end()
    assert not cleaned[pos:].strip() and modules,'Unparsed module tail'
    return modules


def elaborate_leaf_masters(modules,top,library):
    result={}
    def visit(module,prefix,active):
        assert module not in active,'Recursive hierarchy'
        for name,inst in modules[module]['instances'].items():
            full=prefix+name;master=inst['cell']
            if master in modules:
                assert set(inst['pins'])==set(modules[master]['ports']),'Module port mismatch'
                visit(master,full+'/',active+(module,))
            else:
                assert master in library,'Unresolved hierarchical leaf'
                assert full not in result,'Duplicate hierarchical instance'
                result[full]=master
    visit(top,'',())
    return result


def main():
    copies=load(HERE/'SOURCE_COPIES.json')
    for name,info in copies.items():
        assert sha(HERE/name)==info['sha256']==sha(ROOT/info['source']),(name,'source or copy drift')
    assert sha(LIB)==PINNED_LIB
    toolchain=load(HERE/'inputs/TOOLCHAIN_PRECHECK.json')
    platform_libs=[t for t in toolchain['tools'] if t['path'].endswith('/lib/sky130_fd_sc_hd__tt_025C_1v80.lib')]
    assert len(platform_libs)==1 and platform_libs[0]['sha256']==PINNED_LIB
    parent_copies=load(HERE/'inputs/PARENT_COPY_MANIFEST.json')
    for alias,parent_path in [('CONTROL.v','inputs/CONTROL/routed.v'),('FINAL.v','runs/RESTORE__074_/routed.v'),
                              ('FINAL.def','runs/RESTORE__074_/routed.def'),('FINAL.manifest.json','runs/RESTORE__074_/manifest.json')]:
        assert sha(HERE/'inputs'/alias)==parent_copies[parent_path]['sha256']
    text=(HERE/'inputs/resizer_flow.tcl').read_text()
    lines=text.splitlines();commands=[(i+1,line.strip()) for i,line in enumerate(lines) if line.strip() and not line.lstrip().startswith('#') and line.strip()!='\\']
    def locate(exact):
        hits=[n for n,c in commands if c==exact];assert len(hits)==1,exact
        return hits[0]
    cts_line=locate('write_def $OUTDIR/cts.def');repair_line=locate('repair_timing -setup')
    clock_repair_line=locate('repair_clock_nets');route_line=locate('write_def $OUTDIR/routed.def')
    assert clock_repair_line<cts_line<repair_line<route_line
    between=[c for n,c in commands if cts_line<n<repair_line]
    assert between==['set_propagated_clock [all_clocks]','source $ORFS/setRC.tcl','set_routing_layers -signal met1-met5 -clock met3-met5']
    rc_lines=[s.strip() for s in (HERE/'inputs/setRC.tcl').read_text().splitlines() if s.strip() and not s.lstrip().startswith('#')]
    assert all(s.startswith(('set_layer_rc ','set_wire_rc ')) for s in rc_lines),'setRC contains unreviewed mutation'
    after=[c for n,c in commands if repair_line<n<=route_line]
    assert after==['detailed_placement','pin_access','global_route','detailed_route -output_drc $OUTDIR/drc.rpt -verbose 0 -droute_end_iter $DROUTE_ITER','write_def $OUTDIR/routed.def']
    cts=def_components((HERE/'inputs/cts.def').read_text())
    routed=def_components((HERE/'inputs/resizer_routed.def').read_text())
    final_def=def_components((HERE/'inputs/FINAL.def').read_text())
    design_r,_=Reader((HERE/'inputs/resizer_routed.v').read_text()).parse()
    control,_=Reader((HERE/'inputs/CONTROL.v').read_text()).parse()
    final,_=Reader((HERE/'inputs/FINAL.v').read_text()).parse()
    masters=lambda d:{n:i['cell'] for n,i in d['instances'].items()}
    assert masters(design_r)==routed and design_r==control,'AR DEF/V/CONTROL mismatch'
    assert masters(final)==final_def,'AF DEF/V mismatch'
    for design in [design_r,control,final]:
        assert all(not x['pins'] for x in design['instances'].values() if x['cell']==TAP)
    modules=parse_modules((HERE/'inputs/mapped.v').read_text())
    families={re.sub(r'_\d+$','',m) for d in [cts,routed,final_def] for m in d.values() if m!=TAP}
    families|={re.sub(r'_\d+$','',i['cell']) for d in modules.values() for i in d['instances'].values() if i['cell'] not in modules}
    cells,_=parse_cells(LIB.read_text(),families)
    synthesis=elaborate_leaf_masters(modules,'s382',cells)
    def area(inv):
        unknown={m for m in inv.values() if m not in cells and m!=TAP}
        assert not unknown,unknown
        return sum((cells[m]['area'] for m in inv.values() if m!=TAP),Decimal(0))
    def inventory(inv):
        return {'all_instances':len(inv),'functional_instances':sum(m!=TAP for m in inv.values()),
                'area':str(area(inv)),'master_counts':dict(sorted(Counter(inv.values()).items())),
                'instance_master':dict(sorted(inv.items())),'excluded_tap_ids':sorted(n for n,m in inv.items() if m==TAP)}
    def delta(before,after):
        added=[{'instance':n,'master':m,'area':str(cells[m]['area'])} for n,m in sorted(after.items()) if n not in before and m!=TAP]
        removed=[{'instance':n,'master':m,'area':str(cells[m]['area'])} for n,m in sorted(before.items()) if n not in after and m!=TAP]
        changed=[{'instance':n,'from':m,'to':after[n],'area_delta':str(cells[after[n]]['area']-cells[m]['area'])} for n,m in sorted(before.items()) if n in after and m!=after[n]]
        by_master=[]
        for master in sorted(set(before.values())|set(after.values())):
            if master==TAP:continue
            a=list(before.values()).count(master);b=list(after.values()).count(master)
            if a!=b:by_master.append({'master':master,'before':a,'after':b,'count_delta':b-a,'unit_area':str(cells[master]['area']),'net_area_delta':str((b-a)*cells[master]['area'])})
        signed=sum((Decimal(x['area']) for x in added),Decimal(0))-sum((Decimal(x['area']) for x in removed),Decimal(0))+sum((Decimal(x['area_delta']) for x in changed),Decimal(0))
        assert signed==area(after)-area(before)==sum((Decimal(x['net_area_delta']) for x in by_master),Decimal(0))
        return {'added':added,'removed':removed,'changed':changed,'by_master':by_master,'net_area_delta':str(signed)}
    assert {n for n,m in cts.items() if m==TAP}=={n for n,m in routed.items() if m==TAP}=={n for n,m in final_def.items() if m==TAP}
    recipe=load(HERE/'inputs/recipe.json')['applied'];expected=copy.deepcopy(control)
    for change in recipe:
        assert expected['instances'][change['instance']]['cell']==change['new_cell']
        if change['instance']!='_074_':expected['instances'][change['instance']]['cell']=change['old_cell']
    assert final==expected,'AF is not exact recipe minus 074'
    fm=load(HERE/'inputs/FINAL.manifest.json');assert fm['restored_instances']==['_074_']
    A0,AR,AF=area(cts),area(routed),area(final_def);denominator=AR-A0;numerator=AR-AF
    assert denominator>0 and numerator>=0
    log=(HERE/'inputs/resizer_flow.log').read_text(errors='replace').replace('\x00','')
    assert 'ROUTED_FLOW_OK' in log and '[INFO RSZ-0040] Inserted 8 buffers.' in log
    assert not re.search(r'(?im)^.*(?:\[ERROR|Error:|invalid command name|wrong # args).*$',log)
    log_events=[line for line in log.splitlines() if 'RSZ-0040' in line or 'RSZ-0051' in line or 'CTS-0018' in line]
    bad='VERSION 5.8 ;\nCOMPONENTS 2 ;\n - a x ;\n - a x ;\nEND COMPONENTS\nNETS 0 ;\nEND NETS\n'
    try:def_components(bad)
    except AssertionError:duplicate_rejected=True
    else:raise AssertionError('Duplicate component accepted')
    for name,info in copies.items():assert sha(HERE/name)==info['sha256']==sha(ROOT/info['source'])
    receipt={'status':'pass_static_s382_stage_specific_area_accounting','new_EDA':0,
             'scope':'Liberty-known functional mapped-cell area; excludes exact unchanged physical taps, not die/core area',
             'auditor_sha256':sha(Path(__file__)),'source_copies_sha256':sha(HERE/'SOURCE_COPIES.json'),'source_copies':copies,
             'liberty':{'path':str(LIB.relative_to(ROOT)).replace('\\','/'),'sha256':sha(LIB)},
             'archived_platform_library_binding':platform_libs[0],
             'stage_check':{'clock_repair_line':clock_repair_line,'A0_cts_def_line':cts_line,'repair_timing_line':repair_line,'AR_routed_def_line':route_line,'commands_A0_to_repair':between,'commands_after_repair_to_AR':after,
                            'interpretation':'A0 already includes placement, CTS and repair_clock_nets. AR includes repair_timing followed by legalization/routing. Endpoint master changes are measured; no transient edit ledger is reconstructed.'},
             'synthesis_hierarchy':{'modules':sorted(modules),'top':'s382','inventory':inventory(synthesis)},
             'A0':inventory(cts),'AR':inventory(routed),'AF':inventory(final_def),
             'synthesis_to_A0':delta(synthesis,cts),'A0_to_AR':delta(cts,routed),'AR_to_AF':delta(routed,final_def),
             'metrics':{'AR_minus_A0':str(denominator),'AR_minus_AF':str(numerator),'recovery_of_Resizer_net_added_area_percent':str(numerator/denominator*100),'total_AR_area_reduction_percent':str(numerator/AR*100)},
             'identity_checks':{'AR_DEF_full_instances_equal_AR_Verilog':True,'AR_canonical_equals_CONTROL':True,'AF_DEF_full_instances_equal_AF_Verilog':True,'AF_exact_recipe_minus_074':True,'unchanged_tap_sets':True,'original_sources_unchanged':True},
             'selfchecks':{'duplicate_DEF_instances_rejected':duplicate_rejected},'resizer_log_events':log_events,
             'limitations':['s382 only; does not correct the other 13 archived baseline denominators.',
                            'Net added area between pinned stages is not gross cumulative area of every transient Resizer event.',
                            'A0 is a DEF inventory, not a newly measured timing endpoint; no STA/EDA/SEC is run.',
                            'The ratio is area accounting and does not establish timing acceptance, formal equivalence, algorithm novelty, or full IO constraints.']}
    (HERE/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':receipt['status'],'areas':{'synthesis':str(area(synthesis)),'A0':str(A0),'AR':str(AR),'AF':str(AF)},'metrics':receipt['metrics'],'A0_AR_added':len(receipt['A0_to_AR']['added']),'A0_AR_changed':len(receipt['A0_to_AR']['changed']),'AR_AF_changed':len(receipt['AR_to_AF']['changed'])},indent=2))


if __name__=='__main__':main()
