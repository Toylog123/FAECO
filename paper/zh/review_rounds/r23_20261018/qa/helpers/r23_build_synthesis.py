from pathlib import Path
import re,json,hashlib,datetime,shutil
r=Path('paper/zh/review_rounds/r23_20261018');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prov=json.loads((r/'PANEL_PROVENANCE.json').read_text(encoding='utf-8'))
assert json.loads((r/'qa/provenance_validate_canonical/RECEIPT.json').read_text())['returncode']==0
roles=[('EIC','eic'),('R1','methodology'),('R2','domain'),('R3','perspective'),('DA','da')]
findings={}; reports=[]
def anchor(raw):
    kind,loc=raw.split(':',1);kind=kind.strip();loc=loc.strip()
    if kind=='absence':
        base,rest=loc.split(' — expected ',1);expect,checked=rest.split('; checked ',1)
        return {'anchor_type':kind,'locator':base,'absence_scope':expect,'check_performed':checked}
    a={'anchor_type':kind,'locator':loc}
    if kind=='text':
        quotes=re.findall('“([^”]+)”',loc)
        a['quote']=quotes[0] if quotes else loc
    return a
for seat,role in roles:
    text=(r/f'seats/{role}_phase2.md').read_text(encoding='utf-8')
    ws=[];ss=[]
    if role!='da':
        for m in re.finditer(r'^### (W\d+): ([^\n]+)\n(.*?)(?=^### |\Z)',text,re.M|re.S):
            ident,title,body=m.groups();sev=re.search(r'\*\*Severity\*\*: (\w+)',body).group(1).lower()
            anc=anchor(re.search(r'\*\*Evidence Anchor\*\*: (.+)',body).group(1))
            cm=re.search(r'\*\*Confidence\*\*: (\d)([^\n]*)',body);confidence=int(cm.group(1));basis=cm.group(2).strip(' —，-')
            f={'description':title,'severity':sev,'type':'evidence' if seat=='EIC' else 'methodology' if seat=='R1' else 'theory' if seat=='R2' else 'writing','evidence_anchor':anc,'confidence':confidence,'competence_basis':basis,'source':f'{seat}:{ident}','raw_body':body.strip()}
            findings[f['source']]=f;ws.append({k:v for k,v in f.items() if k not in ['raw_body','source']})
        for m in re.finditer(r'^### (S\d+): ([^\n]+)\n(.*?)(?=^### |\Z)',text,re.M|re.S):
            _,title,body=m.groups();am=re.search(r'\*\*Evidence Anchor\*\*: (.+)',body)
            ss.append({'description':title,'evidence_anchor':anchor(am.group(1))})
    else:
        for line in text.splitlines():
            if not re.match(r'^\| M\d+ \|',line):continue
            cells=[x.strip() for x in line.strip('|').split('|')];ident,dim,desc,anc,cm,_,_=cells
            confidence=int(cm[0]);basis=cm[1:].strip(' —')
            f={'description':desc,'severity':'major','type':'evidence','evidence_anchor':anchor(anc),'confidence':confidence,'competence_basis':basis,'source':f'DA:{ident}','raw_body':line}
            findings[f['source']]=f;ws.append({k:v for k,v in f.items() if k not in ['raw_body','source']})
        ss=[{'description':'明确保留EMA无额外收益、S零严格WNS改善及物理退化，不据此虚构fatal。','evidence_anchor':{'anchor_type':'table','locator':'§4.4、§4.5表13、§4.6表14'}}]
    judgements=[]
    for dim,score in re.findall(r'^### (D\d): [^\n]+\n\s*score: (\w+)',text,re.M):
        assessed=score!='not_assessed'
        judgements.append({'criterion_id':dim,'criterion_source':'reviewer/reviewer_full/v2#'+dim,'judgement_scale':'sprint_contract','judgement':score,'evidence_anchors':[w['evidence_anchor'] for w in ws] if assessed else [],'rationale':f'原席完整理由及触发见seats/{role}_phase2.md#{dim}','uncertainty_or_scope_limit':'criteria_binding_unavailable；NOT_CALIBRATED；按席位职责，仅评价被分配维度。','decision_bearing':assessed,'decision_bearing_reason':'按原契约角色范围判断。' if assessed else '非本席评价维度。'})
    assert len(judgements)==6
    reports.append({'reviewer_id':seat,'role':role,'criterion_judgements':judgements,'strengths':ss,'weaknesses':ws,'questions':[]})
assert len(findings)==20
(r/'FINDING_INVENTORY.json').write_text(json.dumps(findings,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Immutable source order. Duplicates retain every cited seat's exact metadata;
# only the leading source drives severity/confidence. Silence is not a vote.
# config: sources,title,scope,lines,action,acceptance,consequence,obligation
configs=[
(['EIC:W1','R1:W1','DA:M1'],'隔离割机制与排序的独立收益','re_analysis',(508,589),'在同一冻结运行器、输入、接受谓词和新STA预算下比较边界与排序；候选生成对照允许候选池变化，纯排序对照固定候选池。逐实例报告收益—成本曲线、实际测量和多种子。优先审查已验收C′72证据，再决定剩余工作，不能把C′改名为历史C/D。','能从图表追踪每个对照的版本、输入、开关与预算；权重零收益及不利结果保留；历史1.07 ns不用于证明割机制。','evidence_gap_remains','must_fix'),
(['EIC:W2'],'与强相关方法建立算法层面的差异','section',(156,195),'以原始文献逐项比较候选空间、组合粒度、排序信号和验证预算；对相容可运行强基线实施统一比较，对不相容方法说明具体接口/目标障碍。','逐项差异有原文支持，新增部件与已有部件明确；商用/需训练的概括不能代替逐项分析。','claim_scope_unsupported','must_fix'),
(['EIC:W3'],'摘要和结论绑定正确实验族','sentence',(94,102,692,694),'就地标明1.07/0.16 ns属于未用两类割的历史策略枚举；主机制效率用实际同族对照支撑。增加实验族—研究问题—图表对应表。','摘要、结论、实验设置和图题对同一数字的版本/机制身份一致。','interpretive_ambiguity_remains','should_fix'),
(['EIC:W4'],'分开候选检查与最终全网表SEC','sentence',(94,102,264,281),'摘要分别说明候选的局部检查/STA及搜索结束后的最终独立全网表SEC，保持中英文摘要一致。','读者不会理解成每个候选都执行最终SEC；证明完成状态与当前绑定证据一致。','interpretive_ambiguity_remains','should_fix'),
(['R1:W2','DA:M3'],'闭合主要历史结果的版本与输入身份','re_analysis',(398,419,546,546,692,694),'逐族绑定代码、参数、输入、库、约束、种子及输出；先分析已知漂移。无法恢复旧身份时保留历史观察，另外呈现当前冻结族重验，不能以当前源码替代旧数字身份。','每个主要数字可追踪同一族的代码/输入/设定/输出；漂移有归因，未恢复项持续登记。','method_reproducibility_unresolved','must_fix'),
(['R1:W3','R2:W1','DA:M2'],'定义覆盖割的构造目标和步骤','section',(291,320,267,281,387,389),'定义关键路径集合来源、覆盖对象、覆盖判定、割生成规则和数量上限；补可执行伪代码。','不查外部口头约定即可复建覆盖割；六门算例列出输入与输出边界。','method_reproducibility_unresolved','must_fix'),
(['R1:W3','R2:W1','DA:M2'],'定义割边界到实际动作的实例化','section',(264,300,306,320),'说明边界到R/G/B/JOINT的映射、合法组合、候选枚举上限和去重；算例给出实际动作。','同一输入能确定候选身份，JOINT组合范围和去重可验证。','method_reproducibility_unresolved','must_fix'),
(['R1:W3','R2:W1','DA:M2'],'定义融合排序的唯一顺序','section',(264,320),'给出割代价、覆盖与策略优先级的精确计算、字典序/加权方式、并列处理与停止规则；展示最终次序。','同一候选池产生确定可核查的次序，能明确区分基线排序和所提排序。','method_reproducibility_unresolved','must_fix'),
(['R1:W4'],'同步b17最终证明状态和效果绑定','re_analysis',(435,439,491,497),'先复用已恢复的b17原始候选新证明，确认其与正文时序端点一一对应，再更新证明计数、均值口径与表注；不能把新模型证明点数冒充历史旧日志。','绑定新证据的12879/0与旧12812+1清楚区分；0.38 ns端点身份经核对后才合并。','evidence_gap_remains','must_fix'),
(['R2:W2'],'说明并验证顺序等价保证的初态与状态域','re_analysis',(218,220,371,383,445,477),'展示实际模型准备、寄存器对应、输入/复位与X/undef假设；分开equiv_simple与归纳证明点。若恒等状态映射建立保持性，给出实际下一状态/输出证据；若靠复位同步，补基例。','已建立所称保证需要的状态关系和基例；不以删除“完全”替代补证，不据此推断网表已不等价。','claim_scope_unsupported','must_fix'),
(['R2:W3'],'纠正功能ECO的等价目标','sentence',(159,161),'区分与修订后规格等价及保持原基线功能；按Wu原文说明FRAIG识别共享部分和补丁修正差异。','修复功能不再被写成只与旧错误函数等价；与本文功能保持型时序修改清楚区分。','interpretive_ambiguity_remains','should_fix'),
(['R2:W3'],'纠正Kravets工作的技术定位','sentence',(159,159),'按IBM官方摘要把符号采样定位于规格修正点与功能补丁搜索，不能直接作为WNS导向时序重映射证据。','论述与实际取得的摘要证据相符，未取得全文的覆盖边界明确。','reader_traceability_reduced','should_fix'),
(['R2:W4'],'修正Pan2024引用的技术归属','sentence',(163,163,704,717),'将Pan2024移至STP仿真/SAT-sweeping与等价节点识别的实际论述；资源感知补丁陈述只引用支持该内容的原文。','每条引文支撑相邻技术陈述，不把仿真论文归为补丁生成。','reader_traceability_reduced','should_fix'),
(['R2:W5'],'分开Dao2018失败分支和后续动作','sentence',(165,165),'区分不可修复、超时与不等价，按原文指出具体回退分支；不能笼统写成验证失败后扩窗。','扩窗/规模增长论述有对应原文算法分支；无法支持的泛化被纠正。','reader_traceability_reduced','should_fix'),
(['R2:W6'],'修正功能补丁的阶段分类','sentence',(172,195),'分别按问题目标、设计阶段、备用单元与物理信息分类，保留Cheng metal-only布局冻结后场景。','不再把逻辑补丁构造整体视为布局前，也不以无覆盖依据的频率词定位。','interpretive_ambiguity_remains','should_fix'),
(['R2:W7'],'区分逻辑深度代理与真实时序关键度','section',(306,342),'说明depth是逻辑层数，覆盖割是否另用真实STA路径；以算例展示深度项如何影响选择。','深度折扣不自行被称为关键路径覆盖保证；确定性效果有对照证据。','interpretive_ambiguity_remains','should_fix'),
(['R2:W7'],'解释锥规模常数项对割目标的作用','section',(306,342),'说明同一锥nC是节点共享常数，如何通过割节点数量和深度分母影响目标；区别实际验证工作量。','公式解释与其数学作用一致，减少验证代价的效果有实际对照。','interpretive_ambiguity_remains','should_fix'),
(['R2:W7'],'说明扇出与电气负载的代理关系','sentence',(306,342),'将fanout明确表述为负载代理，并交代未直接包含负载引脚电容及线载。','不把fanout数直接当作实际电容或已测负载风险。','interpretive_ambiguity_remains','should_fix'),
(['R3:W1'],'报告接受候选的网表代价','re_analysis',(218,220,371,419,435,439),'对绑定基线/最终网表列逐实例单元数、缓冲变化和同库单元面积；不能取得的项目标未评。','实际网表规模/面积能与WNS端点对应；候选锥尺寸不冒充网表代价。','reporting_requirement_unmet','should_fix'),
(['R3:W1'],'明确额外工程指标的评价状态','section',(371,419),'说明面积、功耗、hold、最大电容和转换时间是约束、观察量还是未评项目；已有检查给限值与违例数，无结果不写通过。','读者知道候选进入下一阶段仍需哪些检查；不强制扩展成完整PPA签核论文。','interpretive_ambiguity_remains','should_fix'),
(['R3:W2'],'补齐简化SPEF的模型定义','section',(624,624),'给出u(e)逐边计算规则、单位RC数值/单位及负载扫描范围，区分模型设定和物理提取。','40 μm/unit与实际RC可重建；不能用新配置覆盖历史条件。','method_reproducibility_unresolved','should_fix'),
(['R3:W2'],'补齐物理后验运行条件','section',(612,648),'列分析角、利用率、关键I/O约束和基线/候选是否同设置；历史缺项明确登记。','每例物理比较对应可核查配置；仍限定于布局和全局布线寄生估计。','reader_traceability_reduced','should_fix'),
]
mapping=json.loads((r/'inputs/PROJECTION_RECEIPT.json').read_text(encoding='utf-8'))['mapping'];items=[]
ordinal={}
for n,(sources,title,scope,ls,action,criterion,consequence,obligation) in enumerate(configs,1):
    f=findings[sources[0]];refs=[]
    for key in sources:
        seat,ident=key.split(':');ordn=int(ident[1:]);pair=(seat,ordn);sub=ordinal.get(pair,0);ordinal[pair]=sub+1
        refs.append({'seat':seat,'channel':'finding','ordinal':ordn,'subclaim_ordinal':sub})
    blocks=[]
    for b in mapping:
        if any(b['tex_first_line']<=ls[j+1] and b['tex_last_line']>=ls[j] for j in range(0,len(ls),2)):blocks.append({'block_id':b['block_id'],'allowed_operations':['replace_block','insert_after']})
    assert blocks
    item={'id':f'REV-{n:02d}','source_refs':refs,'sub_claim_ids':[f'SC-{n:02d}'],'description':title,'reviewer':','.join(sources),'obligation_class':obligation,'severity':f['severity'],'evidence_anchor':f['evidence_anchor'],'confidence':f['confidence'],'competence_basis':f['competence_basis'],'cost_scope':{'kind':scope,'locator':'源稿L'+','.join(map(str,ls))},'consequence_if_unaddressed':{'code':consequence,'target':{'kind':'manuscript','locator':title}},'target_section':'源稿L'+','.join(map(str,ls)),'suggested_action':action,'consensus_level':'SINGLE-VERIFIER','verification_criteria':criterion,'proposed_targets':blocks}
    # SINGLE-VERIFIER is the schema's non-consensus code; retain explicit corroboration below.
    if len(sources)>1:
        item['corroborating_sources']=[{'reviewer':key,**{k:findings[key][k] for k in ['severity','evidence_anchor','confidence','competence_basis']}} for key in sources[1:]]
    items.append(item)
counts={key:sum(i['obligation_class']==key for i in items) for key in ['must_fix','should_fix','consider']}
roadmap={'schema_version':'revision-roadmap/1.0','revision_round':23,'base_draft_sha256':sha(r/'inputs/review_projection.md'),'block_manifest_sha256':sha(r/'inputs/review_projection.block-manifest.json'),'items':items,'total_items':len(items),'obligation_counts':counts,'editorial_decision':'Major Revision','consensus_summary':'核心归因缺口EIC+R1两席，算法定义R1+R2两席，均为2/4 corroborated findings；DA另外提出相应Major。其余席未提不是反对。S负结果保留获四非DA席肯定。非共识条目用schema SINGLE-VERIFIER代码并保留corroborating_sources，不宣称3/4或4/4缺陷共识。','dissenting_opinions':['没有可确认的互不相容修复意见；不同职责导致的沉默不构成异议。证明范围补证并不等于发现实际网表错误。']}
(r/'REVISION_ROADMAP.json').write_text(json.dumps(roadmap,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
carrier=json.loads((r/'PANEL_CARRIER.json').read_text(encoding='utf-8'))
package={'editorial_decision':'Major Revision','reviewer_reports':reports,'consensus':'CONSENSUS-4','consensus_scope':'仅指四个非DA席均肯定保留S候选零严格WNS收益的报告方式，不表示缺陷四席共识；具体缺陷按roadmap来源判断。','revision_roadmap':roadmap,'calibration_status':'NOT_CALIBRATED','review_panel_provenance':carrier}
(r/'REVIEW_PACKAGE.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# r23 中文稿修改路线图','', '结论：Major Revision。以下按不可变来源顺序列出，编号表示引用关系，不表示执行优先级。审稿未修改论文。', '', '**绑定边界**：机器路线图绑定只读的逐段LaTeX围栏投影 `inputs/review_projection.md`（122块），原文逐字节映射见 `inputs/PROJECTION_RECEIPT.json`。原始TeX SHA为 '+sha(r/'inputs/manuscript.tex')+'。此投影用于定位，不能直接当作LaTeX自动补丁授权；实际修订前须核对原稿映射并建立作者裁决sidecar。本轮不代填作者选择。', '', '| 引用 | 来源 | 严重性/信心 | 修订项 | 门槛 | 范围 |','|---|---|---|---|---|---|']
nr=ns=0
for it in items:
    if it['obligation_class']=='must_fix':nr+=1;ref=f'R{nr}'
    else:ns+=1;ref=f'S{ns}'
    itref=it['id']; lines.append(f"| {ref} / {itref} | {it['reviewer']} | {it['severity']} / {it['confidence']} | {it['description']} | {it['obligation_class']} | {it['cost_scope']['kind']} |")
lines+=['','## 逐项要求','']
nr=ns=0
for it in items:
    if it['obligation_class']=='must_fix':nr+=1;ref=f'R{nr}'
    else:ns+=1;ref=f'S{ns}'
    lines+=[f"### {ref} — {it['id']}：{it['description']}",'',f"- **Source**: {it['reviewer']}；{it['sub_claim_ids'][0]}",f"- **Severity / Confidence**: {it['severity']} / {it['confidence']}；{it['competence_basis']}",f"- **Evidence Anchor**: {it['evidence_anchor']['anchor_type']}: {it['evidence_anchor']['locator']}",f"- **Obligation / Cost scope**: {it['obligation_class']}；{it['cost_scope']['kind']}:{it['cost_scope']['locator']}",f"- **Consequence**: {it['consequence_if_unaddressed']['code']}",f"- **Suggested action**: {it['suggested_action']}",f"- **Acceptance criteria**: {it['verification_criteria']}",'']
(r/'REVISION_ROADMAP.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'findings':len(findings),'roadmap_items':len(items),'obligation_counts':counts,'axes':prov['axes']},ensure_ascii=False))
