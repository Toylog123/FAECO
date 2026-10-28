# r22 Evidence Closure — Implementation and Experiment Plan

> 用户在剩余项汇报后授权“继续推进”；恢复核心证据补足，旧r21不新EDA/消融暂缓仅为历史。按AGENTS先独立设计评审、TDD、反驳测试，之后正式运行。

**Goal:** 以同一已钉定运行器补足候选来源、代价及排序的可辨识证据，完成历史配置/计数审计，再将验证后的结果同步中文母稿、配图及英文投稿稿。

**Architecture:** 新显式实验策略与旧默认路径隔离。加权s–t路径只由真实最小割Cw与明确覆盖集合Cc构造，不混入旧固定/随机/尺寸候选；按规范哈希去重。旧legacy路径保持默认行为作为强当前基线。所有对照共享实际R/G/B/JOINT、输入映射、验证、冷缓存、串行评估、相同提交与真实STA预算。

**Tech Stack:** Python3.11、pytest、Yosys0.67+146、WSL OpenSTA3.1；SKY130 HD、8个ISCAS89、matplotlib/LuaLaTeX。本轮起点46ede94，基线测试538 passed/4 skipped/156 subtests（113s，真实运行）。复用当前干净适用工作副本，不另建不必要worktree；所有改动可由已提交起点回滚。

## 预锁定矩阵与科学判据

新族C′，不与历史C/D拼接。每电路相同0.5ns、20轮、真实STA预约500、k=8、joint_k=2、R/G/B、buffer开启、strict WNS、feedback关闭、S/TOPOLOGY关闭、workers=1、全新缓存。cover-first明确为两源调度策略，不称未经验证的归一化融合score。

| 臂 | 路径 | Cw代价 | 来源 | 顺序 |
|---|---|---|---|---|
| W0 | weighted_st | 式(2)五项默认1 | Cw | cost |
| W1 | weighted_st | 式(2)五项默认1 | Cw+Cc | cover-first |
| U0 | weighted_st | 五项全0（等代价） | Cw | cost |
| U1 | weighted_st | 五项全0（等代价） | Cw+Cc | cover-first |
| C | weighted_st | 默认1（Cw不执行） | Cc | cover |
| UR1/2/3 | weighted_st | 五项默认1 | 与W1相同池 | seeded边界排序 |
| L | legacy | 原默认 | 原约束区域+cover | 原调度 |

共9臂×8电路=72运行，优先2电路反驳pilot；pilot不替代全集，结果不可用于调臂。原4–5h只是旧预算假设，由首运行实测并记录；正式batch最多2个电路运行并发、每臂workers1，避免资源竞争。单run有合理硬timeout；全batch监测、失败不静默跳过。

- 主读数：相同真实k预算下的有效累计最优改善B_valid(k)，最终WNS、接受次数与独立最终SEC。
- B_valid仅计通过功能/结构/接受门的可提交候选，排除正WNS但硬门失败的虚假收益；另保留所有已测候选B_observed作诊断。
- 次读数：首次有效改善的真实STA序号、新STA/评估记录/cache/墙钟时间、来源重叠、候选身份与类型、每轮pool trace。
- 最强反证：W1是否胜过C仅覆盖；若加权与等权实际候选完全一致，不将零差异包装为代价贡献；随机优势及任何负收益按同口径展示。
- 2×2估计cost与cover条件效应，不用历史D随机范围作为本族噪声阈值；本族3种子仅描述顺序敏感性，不声称统计显著或理论最优。
- 若机制无效，先按实现/设定/环境/数据归因，不立即用弱化声明替代设计；修复若改变实验对象必须重钉revision并重跑完整受影响矩阵。

## Task 1 · 历史审计（独立并行）

- [ ] 复用r21账本规则，恢复C逐臂输入/命令/flags/revision分级证据，审计b17旧报告。文件：`code/scripts/python/audit_historical_evidence_r22.py`、`project_docs/evidence/r22_historical_audit_20261014/`。
- [ ] 确定/推断/缺失明确分级；不由重复记录猜测缓存，不由剩余文件数猜测调用数。
- [ ] 可复用表同步补充材料；无法恢复字段以不可识别结案，不伪造值。

## Task 2 · 核心控制与TDD（主线）

- [ ] 新测试先失败：source关闭不泄漏cover、等代价控制真实生效、同哈希来源去重、无TOPOLOGY、默认兼容、缓存不增新STA、B_valid不纳入硬失败。
- [ ] 新模块 `code/src/rseco/candidate_policy.py`：validated policy、真实Cw构造与Cc、去重及来源trace。
- [ ] `flow.py`接入新显式policy，保留legacy，记录每轮来源/pool/config，修正真实测量曲线并保留旧评估字段的兼容语义。
- [ ] `real_wns.py`公开五项初始权重、path/source/cost选择；真实STA launch事件与cache命中区别；explicit topology switch。
- [ ] `run_outerloop_real_wns.py` CLI与resolved_args/result完整透传；不推测缺失参数。
- [ ] 跑专属失败→通过；全code/tests回归；实查runner --help与dry config。

## Task 3 · 前置反驳门与正式矩阵

- [ ] 12项静态门按独立设计评审执行：来源开关、默认兼容、同池hash、受控R门控、预算/cache、硬门/提交、未知配置fail-closed、schema。
- [ ] 2电路pilot使用同一矩阵配置，验证映射/基线/实际STA/候选类型/SEC一致；来源控制若未生效不启动大batch。
- [ ] 执行前commit并锁源码SHA/输入/工具版本/完整命令；注册新族实验。不复用可能污染的旧cache或输出。
- [ ] 批跑72，记录每run超时、退出码、进度与实际耗时；崩溃按日志定位，已完成配置仅验证manifest后幂等复用。
- [ ] 聚合各臂全部电路、预算曲线与反例；独立证据复核后改论文与图，不跨族归因。

## Task 4 · 稿件与投稿产物

- [ ] 中文母稿新增新族方法/结果与真实配置说明，按结果归因同步论断与图表；重编、逐页渲染、来源交叉表、作者版同步。
- [ ] 官方Integration指南核实后制作英文elsarticle稿、highlights/cover letter/披露草稿；作者承诺或尚无事实字段不代替签署。
- [ ] Word按实际投稿用途评估；如仍需，修复原硬编码管线，确保反读一致，不重复旧v6输出。
- [ ] 最终版式/代码/证据/记录自检、独立复审、commit+push；不以图件通过等同科学问题闭合。
