from pathlib import Path
import hashlib,json,subprocess,sys
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'code/src'),str(R/'code/scripts')]
import run_r22_cut_ablation as common
from rseco.refinement import RefinementWeights
from dataclasses import asdict
OUT=R/'project_docs/evidence/r22_cprime_v3_20261016/region_design_review'
OUT.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
assert head=='3ea0f757f5e9bab4a2df75c458b0c665eabcb258'
sources=common.source_manifest()
backend=R/'project_docs/evidence/r22_rerun_design_20261016/C_RECONSTRUCTION_ADAPTER/backend.py'
sources[backend.relative_to(R).as_posix()]=sha(backend)
sources['code/scripts/run_hybrid_repair.py']=sha(R/'code/scripts/run_hybrid_repair.py')
inputs={common.LIB.relative_to(R).as_posix():sha(common.LIB)}
for circuit in ['s27','s382','s420','s641']:
 for name in ['mapped.v','sta.log','outerloop_result.json','completion.json']:
  p=R/'experiments/20261016_r22_cut_ablation_v3/W0'/circuit/name
  inputs[p.relative_to(R).as_posix()]=sha(p)
contract={'schema':'r22-region-design-static-contract-v1','declared_utc':datetime.now(timezone.utc).isoformat(),
 'head':head,'scope':['s27','s382','s420','s641'],'state':'W0 initial mapped only; actual baseline critical parsed from archived sta.log',
 'eda_authorized':False,'new_experiment_registered':False,'production_or_registered_parameters_to_modify':[],
 'configured_weights':asdict(RefinementWeights()),
 'uniform_weights':{**asdict(RefinementWeights()),**{k:0. for k in ['boundary_penalty','size_penalty','critical_coverage_reward','verification_cost_penalty','equivalence_stability_reward']}},
 'generator':{'function':'constrained_weighted_cut_candidates','k':5,'min_critical_coverage':1,
  'hard_anchors':[],'window_size':'len(actual cone.gates)','allow_singleton':False,
  'beam_width':40,'max_region_evaluations':320,'wall_timeout_s':None,
  'r_available':'not a generator parameter; do not filter no-R G/B gates',
  'default_resolution':'k5; beam=max(8,k*8,32)=40; evaluation=max(256,k*64)=320; no tuning/scans'},
 'frozen_candidate_union':'canonical union of configured and uniform generator outputs plus output-driver singleton and full critical-path cover; retain all controls/nulls with origins',
 'ranking':{'primary':'sum build_weighted_cut_graph node_costs on identical canonical union; ties canonical_cut_hash',
  'configured':'five default1 weights, actual R availability across full cone',
  'uniform':'five zeros -> node costs1; actual R availability same',
  'scope':'Isolate five node cost terms over shared regions. Not replay of constrained generator full region_score. Physical/position/boundary region heuristics influence generator proposal union only, not primary ranking.'},
 'eligibility':'Connected, actual closed boundary, >=1 baseline critical cone gate, and >=1 distinct actual RGB edit passing current static domain/F1/F2. Singleton/fullcover always inventoried; failure does not silently disappear.',
 'actions':{'reuse_backend':'frozen C_RECONSTRUCTION_ADAPTER.ActualBackend snapshot/candidates/apply/validate only; never measure/sec',
  'strategies':['R','G','B'],'enable_buffer':True,'buf_types':['sky130_fd_sc_hd__buf_1','sky130_fd_sc_hd__buf_2'],
  'max_instances_per_region':8,'instance_order':'baseline critical first, then cone order',
  'witness_limit_per_kind_per_instance':3,'candidate_order':'unchanged backend order; first up to3 for each R/G/B',
  'remaining_candidates':'counts recorded, untested not assumed invalid',
  'gates_scope':'all modified original instances inside region; new B helper expected',
  'proof_scope':'F1/F2+two_state domain only; independent SEC/F3/F5/STA/acceptance not established'},
 'static_controls':['source direct root retained while legal upstream region boundary may exist',
  'zero-input source and multi-output secondary consumers closed',
  'no-R does not remove supported G/B edit opportunities',
  'singleton/full-cover control retained, duplicate hashes keep all origins',
  'same union exact hash set under both rankings; deterministic tie; no silent action pool change',
  'null if <2 eligible region identities, <2 distinct witness action sets, or no observable rank effect; preserve all four circuits',
  'toy checks are implementation support only, never timing benefit'],
 'watchdog_s':360,'source_sha256':sources,'input_sha256':inputs}
with (OUT/'CONTRACT.json').open('x',encoding='utf-8') as f:json.dump(contract,f,indent=2)
md='''# 最小区域对照设计 contract（先登记静态规则，非实验注册）

本contract在census运行前冻结；仅四个已验收电路s27/s382/s420/s641的W0初始mapped与实际baseline critical。无EDA，不改production、当前C′注册参数或HEAD，不启动新正式实验。

复用现有constrained_weighted_cut_candidates，显式解析当前默认k5、beam40、最多320区域、window=全锥、min critical coverage1、无hard anchor、allow_singleton=false、无内部wall阈值；统一外层360s。configured为RefinementWeights默认五项1/physical1/maxcone1000，uniform只将五项置0，physical1保持。函数是bounded-beam生成器，不是精确k-best全枚举；不得因census无差异改变这些值或λ。

分别生成configured/uniform池，**只取一次规范hash union**，补入root singleton和full critical cover并保留origins。该union随后为两个排序共同使用的同一可行集；不能以原两池差异冒充纯排序。主排序明确选sum(actual nodecost)，uniform为门数，tie=canonical hash；这不是原constrained内部完整region_score复刻，也不混用它的position/physical等额外目标。原region_score只用于生成候选union，必须单独记录生成来源和偏置，后续正式设计需另评审。

静态eligibility逐项记录connected、所有真实dependency与外部consumer/multi-output闭合、critical覆盖、是否存在实际RGB可编辑witness。函数生成时不使用R_available筛区域；R可用性仅进入节点成本门控，不得删除仍可G/B的门。root singleton和full-cover无论是否eligible都保留记录，若同hash则合并origins。

动作静态复用已冻结ActualBackend的snapshot/candidates/apply/validate，不调用measure/sec。实例按baseline critical→剩余cone顺序，至多8；每实例每种R/G/B按原顺序最多尝试3个，buffer1/2。此界限是存在性witness搜索，不是完整候选穷尽；未找到不能宣称不可编辑。通过只称“确切候选全文已实例化并通过当前domain/F1/F2静态门”；不声称独立SEC、F3/F5、真实STA或可提交。保存action/candidate hash和失败原因；比较排名变化时同时比较静态witness集合，防止不同region实际机会相同。

反驳优先：先查同union不变量及无动作/仅一区域null；真实source direct-root依赖必须保留；多输出secondary consumer必须出现在区域边界；零输入source合法闭合；无R仍G/B不被删除。actual四例没有某结构时标未覆盖，独立小fixture只检验实现边界，不能升级为actual收益。两排名top1或全序均相同、或不同region却同witness集合，均是合法负诊断，不排除该电路、不调参。

若actual静态可行域没有多个候选或排序不可辨识，停在该诊断；若有，只能说明后续配对pilot有辨别机会，仍须设计审查、全部当前72验收、提交后fresh source pin、正式预算与真实SEC/STA正负控。新区域机制与当前separator机制分开，不补写当前矩阵为有效。详细参数、事前source/input SHA见CONTRACT.json。
'''
with (OUT/'CONTRACT.md').open('x',encoding='utf-8') as f:f.write(md)
print(json.dumps({'contract_sha256':sha(OUT/'CONTRACT.json'),'contract_md_sha256':sha(OUT/'CONTRACT.md'),
 'head':head,'sources':len(sources),'inputs':len(inputs),'eda':False},indent=2))
