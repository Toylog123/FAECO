"""Independent static historical review; no EDA, git, or original-file mutation."""
from pathlib import Path
import hashlib, itertools, json, re, sys, time

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
S=OUT.parent
P=ROOT/'project_docs/evidence/r22_spef_audit_20261016'
SEEN={}
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while block:=f.read(1024*1024):h.update(block)
    return h.hexdigest()
def read(p):
    p=p.resolve(); key=p.relative_to(ROOT).as_posix(); digest=sha(p)
    if key in SEEN:assert SEEN[key]['sha256']==digest,key
    SEEN[key]={'sha256':digest,'bytes':p.stat().st_size}
    return p.read_text(encoding='utf-8-sig')
def load(p):return json.loads(read(p))
def save(name,obj):
    with (OUT/name).open('x',encoding='utf-8',newline='') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')

TOKEN=re.compile(r"\s*(~\^|\^~|1'[bB][01]|[!~'&*|+^()]|[01]|[A-Za-z_$][\w$]*)")
def parse(expr):
    tokens=[];pos=0
    while pos<len(expr):
        if not expr[pos:].strip():break
        m=TOKEN.match(expr,pos)
        if not m:raise ValueError('unsupported token: '+expr[pos:])
        tokens.append(m[1]);pos=m.end()
    i=0;prec={'|':0,'+':0,'^':1,'~^':1,'^~':1,'&':2,'*':2}
    def atom():
        nonlocal i
        if i>=len(tokens):raise ValueError('missing operand')
        t=tokens[i];i+=1
        if t in ('!','~'):node=('not',atom())
        elif t=='(':
            node=binary(0)
            if i>=len(tokens) or tokens[i]!=')':raise ValueError('missing close parenthesis')
            i+=1
        elif re.fullmatch(r"1'[bB][01]|[01]|[A-Za-z_$][\w$]*",t):node=('leaf',t)
        else:raise ValueError('bad operand: '+t)
        while i<len(tokens) and tokens[i]=="'":i+=1;node=('not',node)
        return node
    def binary(level):
        nonlocal i
        left=atom()
        while i<len(tokens) and prec.get(tokens[i],-1)>=level:
            op=tokens[i];i+=1;left=(op,left,binary(prec[op]+1))
        return left
    tree=binary(0)
    if i!=len(tokens):raise ValueError('unconsumed tokens')
    return tree
def evaluate(tree,env):
    op=tree[0]
    if op=='leaf':return int(tree[1][-1]) if tree[1] in ('0','1',"1'b0","1'b1","1'B0","1'B1") else env[tree[1]]
    if op=='not':return (~evaluate(tree[1],env))&1
    a,b=evaluate(tree[1],env),evaluate(tree[2],env)
    if op in ('&','*'):return a&b
    if op in ('|','+'):return a|b
    if op=='^':return a^b
    if op in ('~^','^~'):return (~(a^b))&1
    raise ValueError(op)

def main():
    start=time.monotonic();assert not (OUT/'REVIEW.json').exists()
    read(Path(__file__))
    rows=[]
    # Independent expected functions, including deliberately inequivalent pairs.
    controls=[('!A',lambda a,b:1-a),('~A',lambda a,b:1-a),("A'",lambda a,b:1-a),
        ("!(A&B)",lambda a,b:1-(a&b)),('!A&B',lambda a,b:(1-a)&b),
        ('A^B',lambda a,b:a^b),('A~^B',lambda a,b:1-(a^b)),('A^~B',lambda a,b:1-(a^b)),
        ("1'b0 | (A*B)",lambda a,b:a&b),("(A+B)'",lambda a,b:1-(a|b)),
        ('!!A',lambda a,b:a),('~(A^B)',lambda a,b:1-(a^b))]
    for expr,oracle in controls:
        actual=[evaluate(parse(expr),{'A':a,'B':b}) for a,b in itertools.product((0,1),repeat=2)]
        expected=[oracle(a,b) for a,b in itertools.product((0,1),repeat=2)]
        assert actual==expected,(expr,actual,expected);rows.append({'expression':expr,'actual':actual,'expected':expected,'pass':True})
    for bad in ['!A&B','!(A&B)','A^B']:
        expected=[evaluate(parse(x),{'A':a,'B':b}) for x in [bad] for a,b in itertools.product((0,1),repeat=2)]
        opposite=[evaluate(parse(x),{'A':a,'B':b}) for x in [{'!A&B':'!(A&B)','!(A&B)':'!A&B','A^B':'A~^B'}[bad]] for a,b in itertools.product((0,1),repeat=2)]
        assert expected!=opposite
    save('EVALUATOR_CONTROLS.json',{'positive':rows,'negative_distinctions':3,'independent_parser':True,'production_expression_parser_used':False})
    old=load(S/'audit.json');models=load(S/'old_CEC_model_checks.json');sources=load(S/'source_before.json');after=load(S/'source_after.json')
    spef=load(P/'audit.json');oldchecks=load(S/'static_checks.json');bindings=load(S/'candidate_bindings.json');runs=load(S/'accepted_chains_and_pairs.json')
    mismatches=[];checked=0
    for label,manifest in [('S',sources),('SPEF',{x['path']:x for x in spef['files']})]:
        for name,meta in manifest.items():
            p=ROOT/name; actual=sha(p) if p.exists() else None
            SEEN[name]={'sha256':actual,'bytes':p.stat().st_size if p.exists() else None}
            if actual!=meta['sha256']:mismatches.append({'family':label,'path':name,'expected':meta['sha256'],'actual':actual,'roles':meta.get('roles')})
            checked+=1
        print('source verified',label,checked,flush=True)
    assert sources==after,'original S before/after differs'
    recomputed={};counts={};issues=[]
    for path,checks in models.items():
        body=read(ROOT/path);per={}
        for cell,row in checks.items():
            functions=row['liberty_outputs'];entry={'old_issues':row['issues'],'checks':[]}
            if row['status']=='reused_prior_exact_sequential_model_check':entry['status']='old_exact_sequential_reuse_not_new_proof'
            elif not functions:entry['status']='unknown_actual_outputs'
            else:
                # All old expressions also rebound to their retained actual bytes.
                for pin,got in row['model_assignments'].items():assert re.search(r'assign\s+'+re.escape(pin)+r'\s*=\s*'+re.escape(got)+r'\s*;',body)
                status='match'
                for pin,wanted in functions.items():
                    got=row['model_assignments'].get(pin)
                    if got is None:entry['checks'].append({'pin':pin,'missing':True});status='mismatch';continue
                    try:
                        wanted_ast,got_ast=parse(wanted),parse(got)
                        names=sorted(set(re.findall(r'[A-Za-z_$][\w$]*',wanted+' '+got))-{'b0','b1','B0','B1'})
                        assert len(names)<=12
                        bad=[]
                        for bits in itertools.product((0,1),repeat=len(names)):
                            env=dict(zip(names,bits))
                            if evaluate(wanted_ast,env)!=evaluate(got_ast,env):bad.append(env)
                        entry['checks'].append({'pin':pin,'variables':names,'rows':2**len(names),'mismatches':bad})
                        if bad:status='mismatch'
                    except Exception as e:entry['checks'].append({'pin':pin,'unknown':repr(e)});status='unknown'
                entry['status']=status
            counts[entry['status']]=counts.get(entry['status'],0)+1
            if entry['status'] in ['mismatch','unknown','unknown_actual_outputs']:issues.append({'path':path,'cell':cell,**entry})
            per[cell]=entry
        recomputed[path]=per
    save('MODEL_RECHECK.json',{'counts':counts,'file_count':len(models),'checks':recomputed,'issues':issues,'scope':'binary Boolean combinational truth tables only; no new SEC or sequential proof','actual_Liberty_fields_reused_from_old_audit':True})
    sys.path.insert(0,str(ROOT/'code/src'))
    from rseco.spef import MappedNet,MappedNetlist,build_spef
    net=MappedNet('n',(('u','SUM'),('v','A')))
    tiny=MappedNetlist('top',nets={'n':net},instances=[('sky130_fd_sc_hd__ha_1','u'),('sky130_fd_sc_hd__buf_1','v')])
    result=build_spef(tiny,unit_len_um=1)
    assert net.driver() is None and '*I u:SUM I' in result
    save('SPEF_MINIMAL_PROBE.json',{'input':{'name':'n','pins':list(net.pins),'unit_len_um':1},'driver_actual':net.driver(),'actual_spef':result,'expected':'u:SUM O with a u:SUM -> v:A resistor branch','EDA_executed':False})
    phys=[]
    for family in spef['physical_ledgers']:
        rr=family['candidate_records']; hashes=set();units={}; warnings=[]
        for item in rr:
            hashes.add(item['netlist']['sha256'])
            key=json.dumps(item['SPEF']['newline_normalized_exact_generator_match_unit_um'],sort_keys=True);units[key]=units.get(key,0)+1
            if item['physical_tcl'].get('read_spef_before_report_checks') is False:warnings.append(item['candidate_directory'])
        phys.append({'folder':family['folder'],'F6_records':family['physical_failure_count'],'candidate_records':len(rr),'unique_candidate_sha_count':len(hashes),'unique_candidate_shas':sorted(hashes),'retained_spef_generator_matches':units,'read_spef_after_first_report_count':len(warnings),'period_ns':family['baseline_tcl']['period_ns']})
    scans=[]
    for family in spef['scan_families']:
        for unit in family['units']:
            modes=unit['modes'];warnings=modes['repaired_spef']['log']['warnings_errors']
            scans.append({'path':unit['path'],'period_ns':unit['summary']['period_ns'],'unit_len_um':unit['summary']['unit_len_um'],'shared_baseline_spef':unit['shared_baseline_SPEF'],'baseline_path':modes['baseline_ideal']['tcl']['read_verilog_resolved'],'repaired_path':modes['repaired_ideal']['tcl']['read_verilog_resolved'],'repaired_spef_warnings':warnings,'ideal_delta':unit['summary']['ideal_delta'],'spef_delta':unit['summary']['spef_delta']})
    snapshot=dict(SEEN);save('SOURCE_BEFORE.json',snapshot)
    final={name:{'sha256':sha(ROOT/name),'bytes':(ROOT/name).stat().st_size} for name in snapshot}
    drift=[n for n in snapshot if snapshot[n]!=final[n]];assert not drift,drift
    save('SOURCE_AFTER.json',final)
    report={'date':'2026-10-18','EDA_executed':False,'git_executed':False,'old_S_sources_count':len(sources),'old_SPEF_sources_count':len(spef['files']),'old_sources_checked':checked,'old_sha_mismatches':mismatches,'new_review_sources_stable':True,'model_recheck_counts':counts,'model_recheck_issue_count':len(issues),'old_258_defect_file_count_valid':False,'S_totals_retained':old['totals'],'S_s27_first':bindings[0],'S_paired_endpoints':old['paired_endpoints'],'physical_ledger_summary':phys,'scans':scans,'runtime_seconds':time.monotonic()-start,'limits':['Static closure is not functional equivalence.','Actual Liberty output fields reused from prior audit; expression evaluator independent from production and prior evaluator.','Retained byte SHA is not historical runtime byte identity.','Physical timing values quoted from old reports, not remeasured.','No production, figure, manuscript or old audit changed.']}
    save('REVIEW.json',report)
    print(json.dumps({'model_counts':counts,'issues':len(issues),'source_mismatches':mismatches,'stable':True,'runtime_seconds':report['runtime_seconds']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
