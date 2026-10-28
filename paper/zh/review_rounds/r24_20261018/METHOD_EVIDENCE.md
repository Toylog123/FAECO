# r24 方法与参数证据（只读取证）

本包仅读取既有代码、冻结 ZIP、日志与配置；没有运行 EDA、修改生产源、主稿、图或 HEAD。JSON 保存逐文件 SHA、行号、A8 状态映射与算例输入/输出。六门例是人工指定网表上的静态算法演算，绝不是计时、STA、SEC 或科学效果实验。新计算不改变任何历史证据身份。

## 1. 先区分实际执行分支

当前 HEAD 为 `f761ee1996a83fc4f0f3de0999b74d85a8237858`；C′v3 科学运行 pin 为 `3ea0f757f5e9bab4a2df75c458b0c665eabcb258`。C′原始运行字节在 `project_docs/evidence/r22_cprime_v3_20261016/source_snapshot/runtime_inputs.zip`（SHA `620a0eb9809dd08720fd4fdf4bdb85781668ff161a9b061936e7447ade442d7f`）。本报告检查了 ZIP 内源，不以当前源码替代历史身份。以下括号中 `ZIP:` 表示该 ZIP 的 entry 和一基行号。

主稿的方法叙述混合了三个实现：

| 分支 | 边界生成与顺序 | 可据此说明的范围 |
|---|---|---|
| C′ `weighted_st` | 每个子锥至多 cover 一项、weighted 一项；cover 先插入，规范区域 hash 去重；不按节点和重新排序 | 当前可审计 C′机制；不是连续融合分数 |
| `legacy` 且 constrained | bounded connected beam，完整 region_score 含位置/物理等额外项；覆盖候选补到队首；最多 k 个 beam 候选另加 cover | 不能称精确 k-best；不是 C′加权 s-t 解 |
| `weighted_cut_candidates` | weighted、fixed、random、size-only、critical-only 等；字典序 cover优先→节点和→weighted优先→method | 函数确有 λc>1 的 cover 调度条件，但实调用 `critical_first_default=True` 已使其首轮优先 |

定位：`code/src/rseco/flow.py:356–421`；`cut.py:266–324,326–464`；`candidate_policy.py:1–64`。C′ ZIP 中 candidate_policy SHA `e84072c25ba2b98dcdb0f842443e472227809c9662a73d698d18d3732af4d718`、cut SHA `44f6af84c6c6b7cf7943d3a02481addf2105d6017062ab63c8e2a2d8639dc755`、flow SHA `2ebe04c3eb70d53090663b99b09ee2a8da5fa51607c6f53ba7a5417e8220054d`。

**可直接替换的机制表述**：在冻结 C′运行器中，加权节点割与报告关键实例覆盖区域分别给出候选修改区域；full 配置先调度覆盖区域，再调度加权区域，同一区域合并来源。区域内再按实例和策略次序枚举具体动作。该实现采用分层确定性调度，没有把割代价、覆盖率和策略优先级合成一个共同的实数分数。

## 2. 覆盖区域、路径来源、λc 与边界

真实来源为 OpenSTA 报告。baseline runner 先解析日志中的实例，然后取首个 Endpoint 的 D 输入作为目标锥根（ZIP `code/scripts/run_outerloop_real_wns.py:323–326`）。`parse_critical_instances` 扫描**整份日志**中的 `_INSTANCE_LINE_RE` 匹配，跳过含 `/` 的层级名字，按首次出现去重；并没有切分成路径集合（ZIP `real_wns.py:929–938`）。同时 STA 脚本报告最差路径和 `report_checks -path_delay max -slack_max 0 -endpoint_count 100000`（`opensta.py:330–336`）。因此 `critical_instances` 实际为报告中出现的实例有序并集，不能仅根据 docstring 写成“唯一最差路径”或逐路径 set-cover。

令有序列表为 P，当前锥门集合为 C，覆盖区域是 `Cc=[g for g in P if g in C]`。full/cover 分支调用时显式传 `r_available=None`，故不删除仍可能被 G/B 修改的 R−门。P∩C 为空则不生成 cover。每子锥只生成这一项，没有逐路径命中最优化、覆盖率阈值或额外 cover 个数参数（`candidate_policy.py:38–43`；`cut.py:624–644`）。如锥门数超过 `max_cone_gates`，按深度分子锥，按子锥次序拼接；总池截前 `max_candidates_per_iteration`，C′值8（`flow.py:363–377,674`）。

加权图以每门 in→out 容量 cost(v)、依赖/源汇容量10^9，Edmonds–Karp求残量可达割；源接“无内部驱动输入”的门，汇接目标输出驱动（`cut.py:149–263,691–713,726–820`）。实际 cost 带下界 `max(0.05, formula)`，主稿公式应补此截断。`depth`是从锥输入起算的最长**逻辑层数**；`s(v)`包含门自身的传递扇入门数；fanout 是**锥内消费输入连接计数**，未包含引脚电容、线载或锥外负载（`cut.py:466–536`）。它们是代理，不能称真实STA关键度/电气负载。

λc=`critical_coverage_reward`在C′只进入 cost 分母，且仅 R+门获得深度折扣。它**不改变C′cover-first的次序**。无R候选也仅去掉分母折扣和扇出项，绝不是禁止该门被weighted选中；代码注释里的“hard equivalence constraint”比实现强。`0.01 λv nC`在同一锥是门共享常数，加到每条分裂边后通过割门数及深度分母影响总割代价，不能解释成逐候选实测验证时间。

对区域 S：输入是被选门输入中驱动不在S的信号，按首次遇到去重；输出包含被选门产生的锥接口输出、及被锥内S外门消费的输出；其余被选输出为内部网（`cut.py:657–670,822–866`）。外部consumer通过 `cone.interface_outputs()` 并入；多输出不能只留目标网。

## 3. 从区域到 R/G/B/JOINT：实际枚举规则

先在当前 mapped top 中取区域内存在的实例，按 critical_instances 中的出现次序，再追加其余区域门，截取 `max_instances`（C′=8）。这里截的是实例数，并非 STA 数（ZIP `real_wns.py:2451–2459`；当前 `2451–2459`）。每实例的 R 是 Liberty 真值/引脚置换等价匹配，排除同family及不保多输出角色的目标；G 是同family所有更大整数size；B 是对符合门槛的输入引脚分别插 buf_1/buf_2、只重接该sink的pin，名称由net/instance/pin决定（`real_wns.py:1440–1492`；`logic_rewrite.py:238–278`；`gate_sizing.py:156–174`；`buffer_insertion.py:36–69`）。

注意B的实际阈值口径：`_candidates_for`调用 `build_net_fanout(cells)` 时未传output_pins，故此计数表包含驱动输出pin；仅候选目标cell的输出pin在 `buffer_candidates` 中排除。不能把目前 `len(fanout[net])>=2`直接写成“至少2个负载sink”。这是静态实现事实，不是本轮新发现的物理收益或修复授权。

单实例动作先按 `(strategy_rank,new_type_string)` 排序，再由 `exploration_order`把G/R整组移到B前，组内保持原顺序（`real_wns.py:1469–1480`；`strategy_selector.py:53–69`）。策略表fallback是R,G,B。C′未传priority-table且关闭adaptive/proxy排序，因此按job_index执行，即“实例顺序→每实例R/G→B”，再追加JOINT；G的最终次序是字符串次序，不应仅根据 larger_size_candidates 的数值排序推定。

C′参数 `joint_k=2,joint_mix=False,joint_enumerate_depth=0`：遍历actionable实例，选各自第一项G，找到两个后只追加**一个**联合动作；不足两个则不追加。**不是**枚举所有两门组合；B不进入JOINT（`real_wns.py:2554–2608`）。另一路 `joint_enumerate_depth>0`才滑窗枚举子集，每实例取第一个R否则第一个G，最多50项；本轮C′未开。joint_mix=True的当前实现实际只接受R，没有注释所称无R→G fallback，应据代码写，不外推本轮。

两级身份要分开：区域按 sorted unique gates/inputs/outputs +空action的SHA去重（`cut.py:78–87,candidate_policy.py:52–63`）；外循环去重还包含当前base hash及patch_id（`flow.py:708–716`）。具体候选缓存键是SHA(base_fulltext_hash+candidate_fulltext_hash+analysis_config_hash)，命中不等实际新STA；不同区域可能产生同一候选全文并复用缓存（ZIP `real_wns.py:1623–1650`）。应分别记区域、动作全文、实际STA，不能把每个evaluation当独有候选。C′每轮8是区域上限，**不是8个R/G/B动作上限**。

```text
for subcone in split_if_needed(current_target_cone):
    pool = []
    append cover = ordered_intersection(report_instances, subcone.gates), if nonempty
    append one weighted_node_split_min_cut, if nonempty
    merge equal canonical_region_hash, preserving first occurrence and origins
concatenate subcone pools; keep first 8; optional seeded shuffle only for UR arms
for region in dispatch:
    skip repeated (base_hash, region/patch identity)
    instances = (report-order intersection + remaining region-order)[:8]
    jobs = all per-instance R/G/B in actual ordering
    append one first-two-G joint job when available
    for job in jobs:                         # workers=1, early_stop=True
        apply to same current base; validate; use exact cache or launch STA
        stop at first improving job; commit and rebuild next round from new base
stop on registered STA/formal/wall/iteration/patch/no-new-candidate/timing conditions
```

C′命令证据 `code/scripts/run_r22_cut_ablation.py:42–61`：20轮、20patch、500candidate STA预算、3600s、8区域/轮、8实例、workers1、RGB+buffer、joint2、关闭反馈/proxy/topology、early-stop；W0/W1与U0/U1分别weighted/full及configured/uniform，C只cover，UR1–3随机区域序。不同arm不应统称同一融合排序。

| arm | cut_search_policy | cut_sources | 五节点权重 | 额外顺序 |
|---|---|---|---|---|
| W0 | weighted_st | weighted | 全1 | 一次weighted区域 |
| W1 | weighted_st | full | 全1 | cover先、weighted后 |
| U0 | weighted_st | weighted | 全0（cost=1） | 一次uniform节点割 |
| U1 | weighted_st | full | 全0（cost=1） | cover先、uniform割后 |
| C | weighted_st | cover | 全1，未构造weighted图 | 一次cover区域 |
| UR1/2/3 | weighted_st | full | 全1 | 对截前8的区域列表shuffle，seed1/2/3；不shuffle单实例动作列表 |
| L | legacy | full | 全1 | constrained connected-beam区域池及cover补前，随后截前8 |

上述全部arm经同一个 `run_outerloop_real_wns.py` 调用 `RealWnsEvaluator`，真实候选STA，最终另行whole-netlist SEC。L与W1改变**区域生成方式、候选池与截断输入**，不是仅改顺序；二者实际STA差额不能归为纯排序收益。W0与W1改变是否加入cover，U0与U1同理。W1与UR1–3是同生成规则的区域调度对照，但early-stop后基准可能分叉，不能称分叉后每轮仍有相同候选池。实际同base诊断须以candidate_pool_trace中的base_netlist_hash配对。

## 4. 图2的可复算六门例

图2依赖 `g1→g4,g2→g4,g2→g5,g3→g5,g4→g6,g5→g6`来自 `paper/zh/figures/data/scripts/review_r21_figures.py:116–119`，R−标于g3/g6（126）。该图本来没有实际cell、输入、数值cost、区域或动作结果，故不能称既有运行轨迹。

可采用JSON随附的**人工静态例**补足：g1(a)→n1、g2(b)→n2、g3(c,c)→n3、g4(n1,n2)→n4、g5(n2,n3)→n5、g6(n4,n5)→n6。指定报告实例列表[g1,g4,g6]，全1权重，真实固定Liberty的类型为clkinv_1/clkinv_1/nor2_1/and2_1/or2_1/nor2_1，故R+恰为[g1,g2,g4,g5]。这是为说明算法人工选择的cell，未声称真实STA给出了该关键路径。

| 门 | depth | s(v) | 锥内fanout | cost（6位小数） |
|---|---:|---:|---:|---:|
| g1 | 1 | 1 | 1 | 1.258158 |
| g2 | 1 | 1 | 2 | 1.333158 |
| g3 | 1 | 1 | 1 | 1.577544 |
| g4 | 2 | 3 | 1 | 0.990737 |
| g5 | 2 | 3 | 1 | 0.990737 |
| g6 | 3 | 6 | 0 | 1.941579 |

S2=57，Cw={g6}、输入[n4,n5]、输出[n6]，cost=1.941579；Cc=[g1,g4,g6]、输入[a,n2,n5]、输出[n6]、内部[n1,n4]，节点和4.190474。full仍先Cc后Cw，不能画成按节点和升序。g6虽然R−仍可G/B且可被weighted选中。JSON同时保存实际Liberty匹配菜单、单实例动作witness、JOINT witness的候选全文SHA；均只实例化，不声称新STA/SEC通过、时序改善或能被提交。

## 5. 物理后验与SPEF必须分族

**原A物理后验**：读取 `experiments/20260807_real_pr_iscas8/<case>/{baseline,fixed}/pr.tcl` 16份。每例两侧脚本字节完全相同；s27 SHA `65c4b8e29da0716915953e40eed9feaa502efc5c91b6bc9c757bcca7267e8dc7`，其余七例均 `ddc4d9db7572b76ce67fbfa0b752d9a0b847f188181434e1e1d3da4e0def7784`。脚本第6行TT025C1v80、第12行CK周期0.5ns、第14行utilization s27=10%、其余=30%、aspect1.0/core_space2/siteunithd；第19行global_placement density0.7。place_pins横met3/纵met2；signal met1–met5/clock met3–met5，routing adjustment0.2；global_route后调用detailed_route，**所报时序寄生仍明确 `estimate_parasitics -global_routing`（第30行）**。没有input/output_delay、额外output_load、input_transition或uncertainty命令，故这些量是未显式约束，不可写为签核通过。PLATFORM内pdn.tcl被source，其运行时实际bytes未由本任务恢复，历史平台路径的内容SHA/工具binary/seed身份不能从当前同名路径追补。

**当前简化SPEF生成器**（`code/src/rseco/spef.py:277–301,314–322,335–358`）：

`L(e)=unit_len_um * max(1,sqrt(fanout(e))) * fanout_penalty * depth_penalty`；`R(e)=0.09 [Ω/μm] L(e)`；`C(e)=0.21 [fF/μm] L(e)/1000 [pF/fF]`。SPEF标 `R_UNIT OHM,C_UNIT PF,PIN_CAP NONE`，线电容集中在driver；总R均分为driver→sink星形支路。depth_penalty是统一乘数，并未逐网算逻辑深度；没有坐标或曼哈顿距离。两个penalty默认1。SKY130 li1代表参数之出处当前代码无校准引用，不能称提取RC。

**历史扫描**：s382 9点[0,5,10,20,40,80,120,160,200]，0.5ns；b18 10点[0,2,5,10,20,40,80,120,160,200]，13.15ns。配置由各u*/summary.json实读。所有19点两侧使用同一baseline estimated.spef；s382 repaired存在SLEEP缺pin告警。不得把当前已修的双侧SPEF实现补写成当时流程。

**历史F6门控**：复用 `project_docs/evidence/r22_spef_audit_20261016/review_20261018/{REPORT.md,REVIEW.json}` 的独立实查。s382_big的50条仅5个独有候选SHA，b18_light的6条仅1个；50/6不可写为50/6个独有候选。b18_light retained SPEF仅与unit=1μm当前估计全文归一匹配，不与40匹配；s382_big在1和40均不匹配，历史实际RC配方unknown。主稿将两族一并称40μm/unit不成立。56份历史gate Tcl首个report_checks在read_spef前，slack字段混入ideal；不据此直接否定后续worst-slack WNS，但不能声称全部物理字段同一来源。当前修复的QA不能转为历史科学效果复验。

## 6. A8的模型、初态关系及实际证明分解

实际 `proofs/<case>/sec.ys` 15行顺序为：两侧读取共同cells/helpers与gold/gate；proc、memory；equiv_make；hierarchy -top equiv；flatten；opt_clean；equiv_simple；equiv_induct -seq10；equiv_status -assert。没有reset序列、assume、setundef、显式init值或新状态映射求解。cells中的dfxtp_1使用 `reg IQ; always @(posedge CLK) IQ <= D; assign Q=IQ;`，无初始化/异步reset；helpers的dff仅把CK/D/Q连到dfxtp。实际二值模型不提供X/Z、真实三态、电源/时序违例、模拟物理时序保证。

| case | 原/末DFF实例数（逐CK/D/Q相同） | simple新增证明 | induct新增证明 | 最终proven/unproven |
|---|---:|---:|---:|---:|
| s27 | 3 | 2 | 0 | 11/0 |
| s382 | 21 | 2 | 0 | 90/0 |
| s420 | 16 | 2 | 0 | 79/0 |
| s641 | 19 | 1 | 0 | 124/0 |
| s713 | 19 | 1 | 0 | 126/0 |
| s820 | 5 | 1 | 0 | 139/0 |
| s832 | 5 | 1 | 0 | 146/0 |
| s953 | 29 | 2 | 0 | 228/0 |

每份log在进入induct时已明确 `No selected unproven $equiv cells found in equiv`。因此不能根据脚本含induct推断A8依赖弱归纳或只有10周期有效；simple新增数也不能当全部证明点数，其余由结构匹配/共享归并等已建立。精确日志行号与SHA见JSON。8对gold/gate已逐DFF实例静态比对CK/D/Q连接完全相同，完整映射保存在JSON；例如s27：DFF_0 CK/ G10→G5，DFF_1 CK/G11→G6，DFF_2 CK/G13→G7。

可清楚陈述的初态条件是**对应寄存器初值相同**，允许共同初值任意：关系R(q_gold,q_gate):所有同名DFF的IQ相等。它的基例由这一初态关系定义，不是独立随机初态等价，也不依赖运行reset同步。两侧相同输入/时钟下的映射组合逻辑等价及未改寄存器连接维持该关系，并保持对应输出一致。这是基于现有实际模型/匹配/日志的关系解释；本任务没有另跑SAT并生成新的“任意状态next-state miter”产物，不能声称已有一份额外独立的F_gold(q,x)=F_gate(q,x)量化证明文件。

r23 REV-10指出需解释初态/状态域仍有价值，但审查当时未读取实际脚本日志，不能把其风险假设升级为A8未成立。新统一A8证明与旧历史点集合不同（s820旧137/新139），仍引用新同批对象，不把点数差异解释成质量强弱。

## 7. 剩余unknown及修订边界

- 当前SPEF公式及代码完整性不恢复s382_big历史RC配方；已知错误历史连接不能靠改文字变成科学通过。
- A物理后验的运行时平台全文件/binary/seed身份未由此只读任务恢复；表述宜列实际保留Tcl条件并限定global-routing寄生估计。
- 六门例是人工静态演算；真实Liberty witness不等独立SEC、STA、F3/F5及接受验证。
- 本报告不启动D全56终验、raw归档或新EDA，不把producer56/accepted28混用。

## 8. 可复用的物理工具pilot及未执行的新配对命令

现有真实注入控制：`project_docs/evidence/r22_spef_topology_repair_20261018/actual_tool_binding/`。`probe_actual_spef_binding_20261018.py`、`RESULT.json`、`ROOT_ACCEPTANCE.json`及`independent_review/REVIEW.md`共同绑定tiny ordinary/escaped两种词法身份、40/4000μm、top/CK/5ns；四API+四annotation replay、两missing-pin负控。每份实际注入报告均零unannotated/零partially unannotated drivers，RC增加使WNS变差。它证明真实工具注入和失效拒绝，不是s382/b18科学收益pilot。此只读限定检索没有找到连接修正后s382/b18的已验收科学配对pilot。

当前修复版 `code/scripts/run_parasitic_aware_check.py` 可复用：基线/修复各自解析和生成SPEF，共用明确RC，并分别理想/寄生测量，总计四次STA、各次600秒内层timeout，输出目录存在即拒绝覆写。可预登记以下s382原scan那一对对象的新测量；这会是当前HEAD下的新实验，不恢复旧运行器身份。本任务**没有执行**：

```text
bash code/scripts/run_with_timeout.sh 2700 python code/scripts/run_parasitic_aware_check.py --baseline experiments/20260804_outerloop_decision/s382_beam1_early/s382/mapped.v --repaired experiments/20260804_outerloop_decision/s382_beam1_early/s382/eval/iter002_cand002/005__071__R/mapped.v --period 0.5 --top s382 --clock-port CK --unit-len-um 40 --output-dir experiments/20261018_r24_spef_pair_s382_u40
```

运行前仍需登记HEAD/当前脚本和生产源/Liberty/两输入bytes与解码SHA，检查支持域及同一精确对象的SEC状态；判读须实际检查四份measurement_receipt及两SPEF所有端点，不只比较summary delta。上面四STA不提供新的SEC证明。b18原scan的周期是13.15ns，且OI046的inout支持域仍open，不以更改周期或忽略inout绕过。若做新参数不能称s382_big旧RC已恢复。
