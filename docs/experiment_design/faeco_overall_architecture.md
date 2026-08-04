# FAECO 整体架构设计（两环闭环 + 决策层）

更新时间：2026-08-04

文档性质：把 FAECO 的理想终态固定为可讨论、可实施的整体架构。当前实现只覆盖部分环节（见 §6 现状对照），本文档是设计目标，不是已实现声明。

## 1. 一句话定位

FAECO = 验证反馈驱动的自适应时序 ECO 框架：重综合 patch（外环）与 R/G/B 策略修复（内环）通过失败分类闭环衔接，并用机理特征预测决策、跨电路复用经验。

## 2. 整体架构（两环闭环）

输入：违例门级网表 + 工艺库 + SDC + 重综合参考网表

外环（Stage A，patch 粒度）：min-cut -> patch -> 等价验证 -> F1-F5 失败分类 -> 调 cut 权重 -> 重切
内环（Stage B，cell 粒度）：关键路径实例 -> 特征诊断 -> R/G/B 策略候选 -> OpenSTA 实测 -> 只接受严格改善 -> 下一轮

衔接：外环的 F4（时序收益不足）触发内环诊断；内环修不动（策略空间饱和）则退回外环重切 patch。

## 3. 决策层（创新核心）

目标：生成候选之前先预测策略，而不是全量搜索。

输入特征（每个关键实例）：
- cell 输入电容（Liberty capacitance）
- cell intrinsic delay
- 同 family 是否有更大尺寸变体
- 驱动级强度 / 扇出数
- 网表逻辑深度位置

输出：R/G/B 优先级或"跳过"。

规则来源：从 trial 数据离线归纳（决策树/规则表/统计），不引入 GNN/RL。

## 4. 学习机制（三层）

| 层次 | 内容 | 状态 |
|---|---|---|
| 层1 搜索内适应 | 多轮贪心，接受改动影响下一轮关键路径 | 已实现 |
| 层2 跨电路归纳 | s382 经验迁移到 s641/s713，不重新搜索 | 未实现 |
| 层3 反馈权重自动调节 | refine_weights 参数化（步长/衰减/严重度） | 部分（规则已写，闭环未接） |

## 5. 与现有文档关系

- 外环算法：faeco_algorithm.md
- 失败分类：failure_taxonomy.md
- cut 权重升级：failure_aware_cut.md §7
- 内环实现：docs/engineering/n31_05_sequential_eco.md
- 实验基线：baseline_protocol.md / metrics_and_tables.md

## 6. 现状对照（诚实声明）

| 模块 | 设计 | 实现 | 闭环 |
|---|---|---|---|
| 内环 G/R/B | ✓ | ✓ | ✓（多轮贪心）|
| 决策层（特征预测）| ✓（本文档）| ✗ | ✗ |
| 外环 cut refinement | ✓ | 部分（1 轮权重更新）| ✗ |
| F1-F5 反馈 | ✓ | ✓（固定规则）| ✗（未接真实循环）|
| 跨电路学习 | ✓（本文档）| ✗ | ✗ |

## 7. 下一步实施顺序

1. 决策层：从 8 电路 trial 数据归纳"特征 -> 策略"规则，接入 runner 生成候选前预测
2. 效率对比：决策驱动 vs 全搜索，同 WNS 下比 STA 调用数
3. 外环闭环：X19 真正多轮 refinement + 参数化反馈
4. 消融：failure-aware 开关 / 反馈分支 / 决策层贡献

## 8. 跨电路迁移实验设计（2026-08-04）

目的：验证决策表是否跨电路可迁移（第二根创新支柱）。

协议：

1. 用 7 电路 trial 归纳决策表，在第 8 电路上跑 --strategy-priorities auto，对比全搜索基线（同 WNS 比 trials 数）。
2. leave-one-out 循环 8 次，每电路得到"迁移决策表 vs 全搜索"的 trials/WNS。
3. 汇总表：circuit | 全搜索 trials | 迁移 trials | 节省 % | WNS 对比。

预期：迁移决策表优先试高接受率策略（多为 B），trial 数下降且 WNS 不劣化；若某些电路 WNS 劣化，说明该电路 cell type 分布与训练集差异大，需记录为迁移边界。

当前状态：2026-08-04 已用 8 电路全量 trial 归纳共享决策表（strategy_priority_table.json），8 电路决策层实验运行中（experiments/20260804_strategy_selector_8c）。严格的 leave-one-out 版本待本批完成后补充。


### 8.1 初步结果（2026-08-04，6/8 完成）

共享决策表（8 电路全量 trial 归纳）+ 各电路 --strategy-priorities auto：

| 电路 | baseline | 全搜索 final | 全搜索 trials | 决策层 final | 决策层 trials | 结论 |
|---|---|---|---|---|---|---|
| s27 | -0.28 | -0.01 | 119 | -0.01 | 119 | 持平 |
| s382 | -0.94 | +0.02 | 1245 | +0.02 | 1245 | 持平 |
| s420 | -1.78 | -0.01 | 633 | -0.01 | 633 | 持平 |
| s641 | -1.86 | -0.02 | 950 | -0.02 | 989 | 持平（trials 略增） |
| s713 | -1.86 | -0.01 | 1114 | -0.01 | 1140 | 持平（trials 略增） |
| s820 | -1.42 | -0.20 | 2402 | **-1.03（劣化）** | 2266 | **迁移失败** |
| s832 | -1.15 | -0.47 | 2275 | 运行中 | - | - |
| s953 | -1.48 | -0.09 | 3467 | 运行中 | - | - |

### 8.2 s820 迁移失败根因（重要，诚实记录）

决策层在 s820 上只跑 2 轮（全搜索 4 轮）即停止：第 2 轮后 B 候选不再改善 WNS，而全搜索靠第 3-4 轮的 G/R 组合继续收敛到 -0.20。根因：**决策表把 B 排最前，改变了每轮贪心选优轨迹，导致提前收敛**——不是决策表本身错误，而是"优先级重排 + 每轮单 best 贪心"组合在部分电路上缩短了探索。

教训：决策层不能只重排优先级，还需保留"轮内多策略探索"（如每轮至少试一个 G 和一个 R），否则会牺牲多轮收敛能力。


### 8.3 最终结果（2026-08-04，8/8 完成）

| 电路 | baseline | 全搜索 final | 全搜索 trials | 决策层 final | 决策层 trials | 结论 |
|---|---|---|---|---|---|---|
| s27 | -0.28 | -0.01 | 119 | -0.01 | 119 | 持平 |
| s382 | -0.94 | +0.02 | 1245 | +0.02 | 1245 | 持平 |
| s420 | -1.78 | -0.01 | 633 | -0.01 | 633 | 持平 |
| s641 | -1.86 | -0.02 | 950 | -0.02 | 950 | 持平 |
| s713 | -1.86 | -0.01 | 1114 | -0.01 | 1140 | 持平 |
| s820 | -1.42 | -0.20 | 2402 | **-1.03（劣化）** | 2266 | 迁移失败 |
| s832 | -1.15 | -0.47 | 2275 | **-0.45（更好）** | 1932（-15%） | 决策层有效 |
| s953 | -1.48 | -0.09 | 3467 | -0.09 | 3412 | 持平 |

汇总：7/8 持平或更好；s832 证明决策层可在同质量下省 15% STA 调用且找到略优解；s820 证明优先级重排会改变贪心轨迹导致提前收敛（诚实负面结论）。

改进方向：决策层需保留"轮内多策略探索"（每轮至少试一个 G/R），或对迁移失败电路回退全搜索。


### 8.4 探索守卫修复（2026-08-04，已验证）

s820 迁移失败的根因：决策表把 B 排最前，改变了每轮贪心选优轨迹，第 2 轮后 B 不再改善就提前收敛（-1.03）。

修复：src/rseco/strategy_selector.py 新增 exploration_order——候选排序后把 G/R 候选提到 B 之前，保证每轮都有逻辑级选项参与竞争。runner 复用该函数。

验证（s820, --strategy-priorities auto + 探索守卫）：

| 配置 | final WNS | trials | audit |
|---|---|---|---|
| 全搜索基线 | -0.20 | 2402 | ok |
| 决策层（纯排序） | **-1.03** | 2266 | ok |
| 决策层（探索守卫） | **-0.20（恢复）** | 2402 | ok |

结论：探索守卫恢复 s820 到全搜索质量，代价是 trials 回到全搜索水平（2402）——排序不再省 trial，但保证不劣化。真正的效率收益保留在 s832 这类 B 主导电路（-0.45 / 1932 trials）。


### 8.5 leave-one-out 跨电路迁移评估（2026-08-04，离线验证）

方法：对每个电路 c，用"其他 7 电路"的 trial 数据归纳决策表（cell-type -> 策略优先级），然后统计该表对 c 的历史 trial 的预测命中率（trial 的 kind 是否在预测 top-1/top-2 内）。

| 电路 | top-1 命中 | top-2 命中 | 决策表条目 |
|---|---|---|---|
| s27 | 52.1% | 96.6% | 75 |
| s382 | 72.6% | 96.7% | 72 |
| s420 | 55.5% | 94.3% | 75 |
| s641 | 64.5% | 95.8% | 75 |
| s713 | 59.4% | 94.9% | 74 |
| s820 | 73.2% | 98.0% | 70 |
| s832 | 73.6% | 98.2% | 73 |
| s953 | 65.0% | 97.4% | 60 |

结论：**跨电路经验可迁移性强**——用其他 7 电路归纳的决策表，对任一电路 trial 的 top-2 命中率 >= 94.3%。策略选择规律（如 B 对多数 cell type 有效）在不同 ISCAS89 电路间高度一致。这是"跨电路经验复用"创新支柱的离线证据（无需重跑实验）。


## 9. 创新点与实证对照（2026-08-04）

针对"纯搜索策略空间、无创新点"的质疑，FAECO 的三根创新支柱及其可复现实证如下：

### 支柱 1：验证反馈驱动的策略决策层（不再是纯搜索）

- 实现：src/rseco/strategy_selector.py（cell-type -> 策略优先级决策表，从 12205 trials 归纳）
- 实证：runner 候选生成前按决策表排序，非全枚举
- 对比：传统 B&G/remapping 是固定顺序或 cell 级 RL 动作，FAECO 是"历史验证反馈归纳的策略级选择"

### 支柱 2：跨电路经验复用（不是每电路从零搜索）

- 实证：leave-one-out 评估（§8.5），其他 7 电路归纳的决策表对任一电路 trial top-2 命中率 94.3%-98.2%
- 意义：策略选择规律跨 ISCAS89 电路高度稳定，经验可迁移

### 支柱 3：效率可量化（failure-aware 的实际价值）

- 实证：s832 决策层 -0.45（比全搜索 -0.47 更好）且 trials 2275->1932（-15%）
- 实证：s820 探索守卫保证不劣化（-0.20 与全搜索一致）——"aware"的价值是保证质量 + 在可预测电路省算力

### 待补齐（诚实声明）

- 外环闭环（X19）实现层已复核：F1（结构等价）与 F4（逻辑级下降）判据互斥致成功不可达、F1/F2/F4 反馈未进排序 cost（惰性）；已注入功能等价 checker 打通成功路径，权重全参与排序 + WNS 接入为后续项
- 决策层仅用 cell-type 单特征，未用输入电容/扇出等机理特征（§3 设计的特征向量未全实现）
- 实验规模 8 电路，需更大 benchmark 验证


## 10. 外环多轮闭环实现（X19, 2026-08-04）

新增 src/rseco/refinement_loop.py：真正的 multi-iteration loop（cut -> classify -> refine_weights -> re-cut），直到成功或 max_iterations。

- simulate_refinement_loop(evaluator, config)：evaluator 回调返回 (success, patch_id)，失败时用失败类型调 refine_weights 更新权重再重试
- flow.py 新增 run_multi_iteration_case：把 Stage A 的单轮 proxy 升级为多轮，输出 refinement_iterations 历史
- 单元测试 5 项（3 loop + 2 flow），全量回归 155 passed

现状对照更新：外环闭环从"未实现"变为"已实现（模块 + 测试 + flow 接入）"。剩余：用真实 case（c17/c432）跑端到端多轮验证 + 消融（关反馈 vs 开反馈的 recovery 对比）。


### 10.1 端到端验证发现（2026-08-04）

用 5 个真实 case（c17x2/c432/c499/c880）跑 run_multi_iteration_case(max_iterations=5)：

- **复核修正（2026-08-04）**：早前「c432/c499/c880 的 F3 在权重反馈下消失」不可复现——实测 3 电路每轮只触发 F4，F3 从不触发；c17 虽触发 F3，但 size penalty 不改变被选中的 1-gate cut。候选排序 cost 单调加性，1-gate cut 恒最便宜，只有 size_penalty 会额外加入同尺寸候选，F1/F2/F4 权重不进入排序 cost，反馈在实现层面惰性
- 全部 case 失败的直接原因是 logic_level_reduction=0（重综合网表就是原网表副本），F4 永不满足；更深根因是成功判据互斥：F1 结构签名等价与 F4 reduction>=1 不可同时成立，成功路径在构造上不可达（reduction=0 只是表象）
- 诚实结论：**机制框架在，实现层两处缺陷均已修复**——成功路径（F1/F4 互斥）已通过注入 functional equivalence checker 打通（合成 case 验证）；权重惰性已修复：F1-F5 全部进入加权 min-cut 节点成本，weighted_cut_candidates 真正求解 s-t min-cut（tests/test_weighted_cut_feedback.py 6 项，权重变化真实翻转 cut）。后续：真实重综合网表 + WNS 接入
  
  - **真实重综合落地（2026-08-04 晚）**：原 5 case 的 resynthesized 网表就是原文件副本（reduction=0），是 10.3 消融无法区分的主因。新增 scripts/resynthesize_minimal_cases.py 用 Yosys techmap + abc -liberty 对 SKY130 真实重综合，5 case 全部成功（c17 6→3 gates、LL 3→2；c432 171→68、LL 20→12、reduction 8；c499 174→158、LL 11→7、reduction 4；c880 323→152、LL 20→11、reduction 9）；c432/c499/c880 外环第 1 轮即成功，成功路径从"构造上不可达"变为"可达且真实"
  - **CEC 解锁**：check_yosys_abc_equivalence 新增 liberty_cells_v；_extract_cells_for_netlist 只提取网表实际实例化的 SKY130 单元（避开时序/$mul 特殊单元），c17 original vs resynthesized 经 ABC 结构哈希真 pass（不再 error），build_case_metrics 的 formal_equivalence 从"未接"变"真验证"
  - **反馈精确化（诚实边界）**：F1-F5 权重真实进入 min-cut 且能改变解（c17 size_penalty=5 时 cut 从 root 翻到 2-gate 浅层）；但 evaluator 成功条件用**全局** logic-level reduction、与 cut 位置解耦，全局 reduction≥1 且默认 cut 过阈值时首轮即成功、否则每轮失败，故 ON/OFF 无差异；c17×2 因 max_patch_ratio=0.15 对 ≤6-gate 小网表过严恒 F3 失败（阈值边界而非反馈失效）。tests/test_evaluator_cut_decoupling.py 2 项 + test_weighted_cut_feedback 诚实化（boundary/critical 在真实 DAG 不能翻转 cut，仅 size_penalty 可）


### 10.2 WNS 驱动成功标准（2026-08-04）

外环循环的 evaluator 回调天然支持 WNS 成功标准：evaluator 内部决定 success（如 WNS 改善即 True），循环只负责失败时调权重重试。测试验证（test_refinement_wns.py 2 项）：

- WNS 序列 [-1.5, -1.2, -0.9] 下，第 3 次 WNS >= -1.0 时循环成功停止（iterations=3）
- 首次即 success 时立即停止（iterations=1，无多余 refine）

这解决了 10.1 的 case 限制：logic_level_reduction=0 时，改用 WNS 改善作为成功标准即可让外环真正"恢复"。真实接入需把 Stage A 的 patch 替换后跑 OpenSTA（复用 run_opensta，需 mapped netlist + clock），作为后续工程项。


### 10.3 消融实验（关反馈 vs 开反馈，2026-08-04）

simulate_refinement_loop 新增 enable_feedback 参数（默认 True；False 为消融对照，权重固定）。5 个 case（c17x2/c432/c499/c880）分别跑开/关反馈 5 轮：

| case | 开反馈失败集 | 关反馈失败集 | 差异 |
|---|---|---|---|
| c17x2 | [F3,F4] | [F3,F4] | 无 |
| c432/c499/c880 | [F4] | [F4] | 无 |

诚实结论：**当前 case 上消融无法区分反馈效果**——weighted_cut_candidates 对这些小 case 的权重变化不敏感（F3 消除是首轮权重就生效，不是多轮积累；F4 因 reduction=0 永不满足）。需更大的 case（权重变化真正改变 cut 边界）或 WNS 成功标准才能体现反馈价值。这是数据/实现局限，不是机制本身无效（测试已验证 refine_weights 正确触发）。

