# r23 中文稿修改路线图

结论：Major Revision。以下按不可变来源顺序列出，编号表示引用关系，不表示执行优先级。审稿未修改论文。

**绑定边界**：机器路线图绑定只读的逐段LaTeX围栏投影 `inputs/review_projection.md`（122块），投影仅规范化行尾，原文逐字节片段映射见 `inputs/PROJECTION_RECEIPT.json`。原始TeX SHA为 c750ff9cad382ff3fdf3c067980016a0ebcc7be7c2fff2a198c5f5396767918b。此投影用于定位，不能直接当作LaTeX自动补丁授权；实际修订前须核对原稿映射并建立作者裁决sidecar。本轮不代填作者选择。

| 引用 | 来源 | 严重性/信心 | 修订项 | 门槛 | 范围 |
|---|---|---|---|---|---|
| R1 / REV-01 | EIC:W1,R1:W1,DA:M1 | major / 5 | 隔离割机制与排序的独立收益 | must_fix | re_analysis |
| R2 / REV-02 | EIC:W2 | major / 4 | 与强相关方法建立算法层面的差异 | must_fix | section |
| S1 / REV-03 | EIC:W3 | minor / 5 | 摘要和结论绑定正确实验族 | should_fix | sentence |
| S2 / REV-04 | EIC:W4 | minor / 5 | 分开候选检查与最终全网表SEC | should_fix | sentence |
| R3 / REV-05 | R1:W2,DA:M3 | major / 5 | 闭合主要历史结果的版本与输入身份 | must_fix | re_analysis |
| R4 / REV-06 | R1:W3,R2:W1,DA:M2 | major / 4 | 定义覆盖割的构造目标和步骤 | must_fix | section |
| R5 / REV-07 | R1:W3,R2:W1,DA:M2 | major / 4 | 定义割边界到实际动作的实例化 | must_fix | section |
| R6 / REV-08 | R1:W3,R2:W1,DA:M2 | major / 4 | 定义融合排序的唯一顺序 | must_fix | section |
| R7 / REV-09 | R1:W4 | major / 5 | 同步b17最终证明状态和效果绑定 | must_fix | re_analysis |
| R8 / REV-10 | R2:W2 | major / 4 | 说明并验证顺序等价保证的初态与状态域 | must_fix | re_analysis |
| S3 / REV-11 | R2:W3 | minor / 5 | 纠正功能ECO的等价目标 | should_fix | sentence |
| S4 / REV-12 | R2:W3 | minor / 5 | 纠正Kravets工作的技术定位 | should_fix | sentence |
| S5 / REV-13 | R2:W4 | minor / 5 | 修正Pan2024引用的技术归属 | should_fix | sentence |
| S6 / REV-14 | R2:W5 | minor / 4 | 分开Dao2018失败分支和后续动作 | should_fix | sentence |
| S7 / REV-15 | R2:W6 | minor / 5 | 修正功能补丁的阶段分类 | should_fix | sentence |
| S8 / REV-16 | R2:W7 | minor / 5 | 区分逻辑深度代理与真实时序关键度 | should_fix | section |
| S9 / REV-17 | R2:W7 | minor / 5 | 解释锥规模常数项对割目标的作用 | should_fix | section |
| S10 / REV-18 | R2:W7 | minor / 5 | 说明扇出与电气负载的代理关系 | should_fix | sentence |
| S11 / REV-19 | R3:W1 | minor / 5 | 报告接受候选的网表代价 | should_fix | re_analysis |
| S12 / REV-20 | R3:W1 | minor / 5 | 明确额外工程指标的评价状态 | should_fix | section |
| S13 / REV-21 | R3:W2 | minor / 5 | 补齐简化SPEF的模型定义 | should_fix | section |
| S14 / REV-22 | R3:W2 | minor / 5 | 补齐物理后验运行条件 | should_fix | section |

## 逐项要求

### R1 — REV-01：隔离割机制与排序的独立收益

- **Source**: EIC:W1,R1:W1,DA:M1；SC-01
- **Severity / Confidence**: major / 5；稿件直接说明历史运行器未使用两类割，并承认其独立贡献仍需检验
- **Evidence Anchor**: absence: §4.4、图5及表9–11
- **Obligation / Cost scope**: must_fix；re_analysis:源稿L508,589
- **Consequence**: evidence_gap_remains
- **Suggested action**: 在同一冻结运行器、输入、接受谓词和新STA预算下比较边界与排序；候选生成对照允许候选池变化，纯排序对照固定候选池。逐实例报告收益—成本曲线、实际测量和多种子。优先审查已验收C′72证据，再决定剩余工作，不能把C′改名为历史C/D。
- **Acceptance criteria**: 能从图表追踪每个对照的版本、输入、开关与预算；权重零收益及不利结果保留；历史1.07 ns不用于证明割机制。

### R2 — REV-02：与强相关方法建立算法层面的差异

- **Source**: EIC:W2；SC-02
- **Severity / Confidence**: major / 4；可直接核查稿内比较内容；未据此断言引用文献实际上已覆盖本文贡献
- **Evidence Anchor**: absence: §2及表1–2
- **Obligation / Cost scope**: must_fix；section:源稿L156,195
- **Consequence**: claim_scope_unsupported
- **Suggested action**: 以原始文献逐项比较候选空间、组合粒度、排序信号和验证预算；对相容可运行强基线实施统一比较，对不相容方法说明具体接口/目标障碍。
- **Acceptance criteria**: 逐项差异有原文支持，新增部件与已有部件明确；商用/需训练的概括不能代替逐项分析。

### S1 — REV-03：摘要和结论绑定正确实验族

- **Source**: EIC:W3；SC-03
- **Severity / Confidence**: minor / 5；摘要与结果配置说明之间可直接逐段核对
- **Evidence Anchor**: text: 中文摘要，源码第94行“固定权重、20 轮迭代下”；§4.4，源码第512行“加权割和覆盖割各自的贡献仍需同一运行器下的独立对照检验”
- **Obligation / Cost scope**: should_fix；sentence:源稿L94,102,692,694
- **Consequence**: interpretive_ambiguity_remains
- **Suggested action**: 就地标明1.07/0.16 ns属于未用两类割的历史策略枚举；主机制效率用实际同族对照支撑。增加实验族—研究问题—图表对应表。
- **Acceptance criteria**: 摘要、结论、实验设置和图题对同一数字的版本/机制身份一致。

### S2 — REV-04：分开候选检查与最终全网表SEC

- **Source**: EIC:W4；SC-04
- **Severity / Confidence**: minor / 5；摘要语法与方法正文、图1的检查对象和时机可直接对照
- **Evidence Anchor**: text: 中文摘要，源码第94行“候选按轮提交，依次经函数与结构检查、时序分析与最终等价性检查”；§3.2，源码第281行“独立顺序 SEC 在生成最终修复网表后执行”
- **Obligation / Cost scope**: should_fix；sentence:源稿L94,102,264,281
- **Consequence**: interpretive_ambiguity_remains
- **Suggested action**: 摘要分别说明候选的局部检查/STA及搜索结束后的最终独立全网表SEC，保持中英文摘要一致。
- **Acceptance criteria**: 读者不会理解成每个候选都执行最终SEC；证明完成状态与当前绑定证据一致。

### R3 — REV-05：闭合主要历史结果的版本与输入身份

- **Source**: R1:W2,DA:M3；SC-05
- **Severity / Confidence**: major / 5；复现身份与配置追踪
- **Evidence Anchor**: text: 实验设置L402“代码 revision 未完整钉定”；同段“同配置重跑在部分电路出现结果漂移”；策略表注L546“各臂完整命令未全部归档”
- **Obligation / Cost scope**: must_fix；re_analysis:源稿L398,419,546,546,692,694
- **Consequence**: method_reproducibility_unresolved
- **Suggested action**: 逐族绑定代码、参数、输入、库、约束、种子及输出；先分析已知漂移。无法恢复旧身份时保留历史观察，另外呈现当前冻结族重验，不能以当前源码替代旧数字身份。
- **Acceptance criteria**: 每个主要数字可追踪同一族的代码/输入/设定/输出；漂移有归因，未恢复项持续登记。

### R4 — REV-06：定义覆盖割的构造目标和步骤

- **Source**: R1:W3,R2:W1,DA:M2；SC-06
- **Severity / Confidence**: major / 4；算法可重建性检查
- **Evidence Anchor**: absence: 方法的多源候选边界与融合排序
- **Obligation / Cost scope**: must_fix；section:源稿L291,320,267,281,387,389
- **Consequence**: method_reproducibility_unresolved
- **Suggested action**: 定义关键路径集合来源、覆盖对象、覆盖判定、割生成规则和数量上限；补可执行伪代码。
- **Acceptance criteria**: 不查外部口头约定即可复建覆盖割；六门算例列出输入与输出边界。

### R5 — REV-07：定义割边界到实际动作的实例化

- **Source**: R1:W3,R2:W1,DA:M2；SC-07
- **Severity / Confidence**: major / 4；算法可重建性检查
- **Evidence Anchor**: absence: 方法的多源候选边界与融合排序
- **Obligation / Cost scope**: must_fix；section:源稿L264,300,306,320
- **Consequence**: method_reproducibility_unresolved
- **Suggested action**: 说明边界到R/G/B/JOINT的映射、合法组合、候选枚举上限和去重；算例给出实际动作。
- **Acceptance criteria**: 同一输入能确定候选身份，JOINT组合范围和去重可验证。

### R6 — REV-08：定义融合排序的唯一顺序

- **Source**: R1:W3,R2:W1,DA:M2；SC-08
- **Severity / Confidence**: major / 4；算法可重建性检查
- **Evidence Anchor**: absence: 方法的多源候选边界与融合排序
- **Obligation / Cost scope**: must_fix；section:源稿L264,320
- **Consequence**: method_reproducibility_unresolved
- **Suggested action**: 给出割代价、覆盖与策略优先级的精确计算、字典序/加权方式、并列处理与停止规则；展示最终次序。
- **Acceptance criteria**: 同一候选池产生确定可核查的次序，能明确区分基线排序和所提排序。

### R7 — REV-09：同步b17最终证明状态和效果绑定

- **Source**: R1:W4；SC-09
- **Severity / Confidence**: major / 5；验证状态与效果指标对应
- **Evidence Anchor**: text: 跨测试集评估L497“另有 1 个等价点未完成证明”
- **Obligation / Cost scope**: must_fix；re_analysis:源稿L435,439,491,497
- **Consequence**: evidence_gap_remains
- **Suggested action**: 先复用已恢复的b17原始候选新证明，确认其与正文时序端点一一对应，再更新证明计数、均值口径与表注；不能把新模型证明点数冒充历史旧日志。
- **Acceptance criteria**: 绑定新证据的12879/0与旧12812+1清楚区分；0.38 ns端点身份经核对后才合并。

### R8 — REV-10：说明并验证顺序等价保证的初态与状态域

- **Source**: R2:W2；SC-10
- **Severity / Confidence**: major / 4；已核对稿件所列流程与Yosys 0.33官方文档、同版本源码；未读取实际证明脚本或日志。
- **Evidence Anchor**: text: §4.2及表8注，母稿L445与L477，“独立顺序等价检查完全证明了这8对基线与最终修复网表”，“equiv\_induct -seq 10”。
- **Obligation / Cost scope**: must_fix；re_analysis:源稿L218,220,371,383,445,477
- **Consequence**: claim_scope_unsupported
- **Suggested action**: 展示实际模型准备、寄存器对应、输入/复位与X/undef假设；分开equiv_simple与归纳证明点。若恒等状态映射建立保持性，给出实际下一状态/输出证据；若靠复位同步，补基例。
- **Acceptance criteria**: 已建立所称保证需要的状态关系和基例；不以删除“完全”替代补证，不据此推断网表已不等价。

### S3 — REV-11：纠正功能ECO的等价目标

- **Source**: R2:W3；SC-11
- **Severity / Confidence**: minor / 5；已查Wu2010作者PDF的摘要、§II和Cheng2016官方PDF的研究目标。
- **Evidence Anchor**: text: §2.1，母稿L161，“再通过 SAT 证明筛选与原逻辑功能等价的补丁”。
- **Obligation / Cost scope**: should_fix；sentence:源稿L159,161
- **Consequence**: interpretive_ambiguity_remains
- **Suggested action**: 区分与修订后规格等价及保持原基线功能；按Wu原文说明FRAIG识别共享部分和补丁修正差异。
- **Acceptance criteria**: 修复功能不再被写成只与旧错误函数等价；与本文功能保持型时序修改清楚区分。

### S4 — REV-12：纠正Kravets工作的技术定位

- **Source**: R2:W3；SC-12
- **Severity / Confidence**: minor / 5；已查Wu2010作者PDF的摘要、§II和Cheng2016官方PDF的研究目标。
- **Evidence Anchor**: text: §2.1，母稿L161，“再通过 SAT 证明筛选与原逻辑功能等价的补丁”。
- **Obligation / Cost scope**: should_fix；sentence:源稿L159,159
- **Consequence**: reader_traceability_reduced
- **Suggested action**: 按IBM官方摘要把符号采样定位于规格修正点与功能补丁搜索，不能直接作为WNS导向时序重映射证据。
- **Acceptance criteria**: 论述与实际取得的摘要证据相符，未取得全文的覆盖边界明确。

### S5 — REV-13：修正Pan2024引用的技术归属

- **Source**: R2:W4；SC-13
- **Severity / Confidence**: minor / 5；已查Pan等作者arXiv全文的摘要、§II-C、§III及SAT-sweeping实验定位。
- **Evidence Anchor**: text: §2.1，母稿L163，“后续工作进一步将资源代价纳入补丁生成”。
- **Obligation / Cost scope**: should_fix；sentence:源稿L163,163,704,717
- **Consequence**: reader_traceability_reduced
- **Suggested action**: 将Pan2024移至STP仿真/SAT-sweeping与等价节点识别的实际论述；资源感知补丁陈述只引用支持该内容的原文。
- **Acceptance criteria**: 每条引文支撑相邻技术陈述，不把仿真论文归为补丁生成。

### S6 — REV-14：分开Dao2018失败分支和后续动作

- **Source**: R2:W5；SC-14
- **Severity / Confidence**: minor / 4；已查Dao2018作者PDF的§3.2–3.6；未声称穷尽功能ECO文献。
- **Evidence Anchor**: text: §2.1，母稿L165，“代表性流程通常需要扩大搜索窗口或增加补丁规模重新枚举”。
- **Obligation / Cost scope**: should_fix；sentence:源稿L165,165
- **Consequence**: reader_traceability_reduced
- **Suggested action**: 区分不可修复、超时与不等价，按原文指出具体回退分支；不能笼统写成验证失败后扩窗。
- **Acceptance criteria**: 扩窗/规模增长论述有对应原文算法分支；无法支持的泛化被纠正。

### S7 — REV-15：修正功能补丁的阶段分类

- **Source**: R2:W6；SC-15
- **Severity / Confidence**: minor / 5；Cheng2016官方全文§I明确将场景设为placement frozen之后的metal-only ECO。
- **Evidence Anchor**: text: §2.2，母稿L172，“逻辑补丁构造则多在综合后、布局前执行功能修复”。
- **Obligation / Cost scope**: should_fix；sentence:源稿L172,195
- **Consequence**: interpretive_ambiguity_remains
- **Suggested action**: 分别按问题目标、设计阶段、备用单元与物理信息分类，保留Cheng metal-only布局冻结后场景。
- **Acceptance criteria**: 不再把逻辑补丁构造整体视为布局前，也不以无覆盖依据的频率词定位。

### S8 — REV-16：区分逻辑深度代理与真实时序关键度

- **Source**: R2:W7；SC-16
- **Severity / Confidence**: minor / 5；依据稿件自身数学定义核对，未猜测实现细节。
- **Evidence Anchor**: equation: 式（2）及§3.4、表4，母稿L306–342。
- **Obligation / Cost scope**: should_fix；section:源稿L306,342
- **Consequence**: interpretive_ambiguity_remains
- **Suggested action**: 说明depth是逻辑层数，覆盖割是否另用真实STA路径；以算例展示深度项如何影响选择。
- **Acceptance criteria**: 深度折扣不自行被称为关键路径覆盖保证；确定性效果有对照证据。

### S9 — REV-17：解释锥规模常数项对割目标的作用

- **Source**: R2:W7；SC-17
- **Severity / Confidence**: minor / 5；依据稿件自身数学定义核对，未猜测实现细节。
- **Evidence Anchor**: equation: 式（2）及§3.4、表4，母稿L306–342。
- **Obligation / Cost scope**: should_fix；section:源稿L306,342
- **Consequence**: interpretive_ambiguity_remains
- **Suggested action**: 说明同一锥nC是节点共享常数，如何通过割节点数量和深度分母影响目标；区别实际验证工作量。
- **Acceptance criteria**: 公式解释与其数学作用一致，减少验证代价的效果有实际对照。

### S10 — REV-18：说明扇出与电气负载的代理关系

- **Source**: R2:W7；SC-18
- **Severity / Confidence**: minor / 5；依据稿件自身数学定义核对，未猜测实现细节。
- **Evidence Anchor**: equation: 式（2）及§3.4、表4，母稿L306–342。
- **Obligation / Cost scope**: should_fix；sentence:源稿L306,342
- **Consequence**: interpretive_ambiguity_remains
- **Suggested action**: 将fanout明确表述为负载代理，并交代未直接包含负载引脚电容及线载。
- **Acceptance criteria**: 不把fanout数直接当作实际电容或已测负载风险。

### S11 — REV-19：报告接受候选的网表代价

- **Source**: R3:W1；SC-19
- **Severity / Confidence**: minor / 5；已逐段检查接受条件与结果指标，判断限于稿件所报告的信息。
- **Evidence Anchor**: absence: §3.1、§3.6及§4.1的目标与接受条件
- **Obligation / Cost scope**: should_fix；re_analysis:源稿L218,220,371,419,435,439
- **Consequence**: reporting_requirement_unmet
- **Suggested action**: 对绑定基线/最终网表列逐实例单元数、缓冲变化和同库单元面积；不能取得的项目标未评。
- **Acceptance criteria**: 实际网表规模/面积能与WNS端点对应；候选锥尺寸不冒充网表代价。

### S12 — REV-20：明确额外工程指标的评价状态

- **Source**: R3:W1；SC-20
- **Severity / Confidence**: minor / 5；已逐段检查接受条件与结果指标，判断限于稿件所报告的信息。
- **Evidence Anchor**: absence: §3.1、§3.6及§4.1的目标与接受条件
- **Obligation / Cost scope**: should_fix；section:源稿L371,419
- **Consequence**: interpretive_ambiguity_remains
- **Suggested action**: 说明面积、功耗、hold、最大电容和转换时间是约束、观察量还是未评项目；已有检查给限值与违例数，无结果不写通过。
- **Acceptance criteria**: 读者知道候选进入下一阶段仍需哪些检查；不强制扩展成完整PPA签核论文。

### S13 — REV-21：补齐简化SPEF的模型定义

- **Source**: R3:W2；SC-21
- **Severity / Confidence**: minor / 5；已核看物理段落、公式、表13及原始渲染页，判断限于模型与条件说明的充分性。
- **Evidence Anchor**: text: §4.5迭代式门控，PDF第10至11页，源稿第624行 "unit 表示一次扇出后沿拓扑/曼哈顿距离累加的相对单位长度"；表13注释，源稿第648行 "s27 采用 10\% 利用率布局规划"
- **Obligation / Cost scope**: should_fix；section:源稿L624,624
- **Consequence**: method_reproducibility_unresolved
- **Suggested action**: 给出u(e)逐边计算规则、单位RC数值/单位及负载扫描范围，区分模型设定和物理提取。
- **Acceptance criteria**: 40 μm/unit与实际RC可重建；不能用新配置覆盖历史条件。

### S14 — REV-22：补齐物理后验运行条件

- **Source**: R3:W2；SC-22
- **Severity / Confidence**: minor / 5；已核看物理段落、公式、表13及原始渲染页，判断限于模型与条件说明的充分性。
- **Evidence Anchor**: text: §4.5迭代式门控，PDF第10至11页，源稿第624行 "unit 表示一次扇出后沿拓扑/曼哈顿距离累加的相对单位长度"；表13注释，源稿第648行 "s27 采用 10\% 利用率布局规划"
- **Obligation / Cost scope**: should_fix；section:源稿L612,648
- **Consequence**: reader_traceability_reduced
- **Suggested action**: 列分析角、利用率、关键I/O约束和基线/候选是否同设置；历史缺项明确登记。
- **Acceptance criteria**: 每例物理比较对应可核查配置；仍限定于布局和全局布线寄生估计。

