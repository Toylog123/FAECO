# Failure-Aware Cut Refinement 设计草案

更新时间：2026-07-07

## 1. 目标

解决固定权重 min-cut 在重综合辅助 ECO 中容易出现的失败问题。本文不把失败视为简单的 pass/fail，而是将失败类型转化为下一轮 cut weight 的反馈信号。

## 2. 失败类型

| ID | 失败类型 | 定义 | 反馈动作 |
|---|---|---|---|
| F1 | 等价失败 | patch 替换后功能不等价 | 提高破坏等价边界附近的 cut cost，扩大或移动 cut boundary |
| F2 | 边界不闭合 | patch 输入输出无法与原网表稳定对应 | 惩罚高 fanout、多 reconvergent fanout 或映射不稳定边界 |
| F3 | patch 过大 | 功能正确但修改门数过多 | 提高远离关键路径区域的 cut cost，压缩 patch |
| F4 | 时序收益不足 | 功能正确但 WNS/TNS 或 logic level 改善不足 | 提高关键路径未覆盖节点的优先级，引导 cut 覆盖真正瓶颈 |
| F5 | 验证代价过高 | SAT/等价验证时间或 cone size 过大 | 限制 cone size，分层验证，惩罚过大边界 |

## 3. 算法流程

1. 根据关键路径、logic level 和 patch size 目标初始化边权。
2. 执行 min-cut 得到候选 patch boundary。
3. 进行 patch 替换和等价验证。
4. 计算 patch size、boundary complexity、timing gain 和 verification cost。
5. 判断失败类型。
6. 根据失败类型调整边权。
7. 迭代直到成功或达到最大轮数。

## 4. 权重反馈直觉

| 失败 | 权重调整方向 |
|---|---|
| F1 等价失败 | 边界向更稳定的等价点移动 |
| F2 边界不闭合 | 避免复杂 fanout/reconvergence 区域 |
| F3 patch 过大 | 压缩非关键区域 |
| F4 时序收益不足 | 增强关键路径覆盖 |
| F5 验证代价过高 | 限制 cone 和边界规模 |

## 5. 消融实验

| 实验 | 目的 |
|---|---|
| fixed min-cut vs failure-aware cut | 验证反馈机制是否提升成功率 |
| without F1 feedback | 验证等价失败反馈的重要性 |
| without F3 feedback | 验证 patch size 控制的重要性 |
| without F4 feedback | 验证 timing gain feedback 的重要性 |
| max iteration sensitivity | 分析迭代轮数对成功率和 runtime 的影响 |

## 6. 论文表述重点

创新点不是“使用 min-cut”，而是：

> 将 ECO patch 替换中的失败结果结构化为可反馈的 failure signals，并用这些 signals 反向调整 cut search space。

## 7. 权重升级方案（2026-08-04 设计修订）

### 7.1 现状诊断

原设计（§4）与实现（refinement.py）存在四个简化问题：

| 问题 | 现状 | 风险 |
|---|---|---|
| 特征未实算 | critical_path_distance / boundary_complexity / logic_level_gain 只有名词，cut.py 未计算 | 权重公式无真实输入 |
| 反馈幅度一刀切 | 所有失败固定 +1.0 | 无法区分严重度与失败部位 |
| 无衰减 | faeco_algorithm.md 写了 decay，refine_weights 未实现 | 后期振荡 |
| 与内环脱节 | F1-F5 只调 cut 权重，与 N31-05 的 R/G/B 无接口 | 两环不闭环 |

### 7.2 特征实算层（权重公式的真实输入）

每条 cut edge e 的权重输入改为以下可计算特征：

| 特征 | 定义 | 计算来源 |
|---|---|---|
| critical_distance(e) | e 的节点到关键路径的最短图距离 | STA report_checks + 网表图 |
| boundary_complexity(e) | 端点 fanout × reconvergence 计数 | 网表图分析 |
| logic_gain(e) | 重综合网表相对原网表在该节点的逻辑级数差 | 新旧网表对齐 |
| size_estimate(e) | 以 e 为界的最小 patch gate 数估计 | cone 遍历 |
| eq_stability(e) | 等价点映射置信度 | equivalence_map |

初始权重：

weight(e) = w_base
          + w_eq * (1 - eq_stability(e))
          + w_bc * boundary_complexity(e)
          + w_sz * size_estimate(e)
          - w_cr * gauss(critical_distance(e))
          - w_gain * logic_gain(e)

### 7.3 参数化反馈（替代固定 +1.0）

refine_weights 升级为带步长/衰减/严重度的反馈：

update(failure_f, boundary, metrics):
    magnitude = step[f] * severity[f] * decay(iteration)
    weight[f] = clip(weight[f] + magnitude, [lo[f], hi[f]])

| 参数 | 默认 | 说明 |
|---|---|---|
| step[f] | 0.5 | 每类失败独立步长 |
| severity[f] | F1=3, F2=2, F5=1.5, F3=1, F4=1 | 按失败优先级 |
| decay(iter) | 0.9^iter | 后期收敛 |
| lo/hi | [0.1, 20] | 权重上下界，防漂移 |

### 7.4 消融实验扩展

在 §5 基础上增加：

| 实验 | 目的 |
|---|---|
| step 敏感性（0.1/0.5/1.0） | 验证步长鲁棒性 |
| severity 开关（全部=1 vs 分级） | 验证严重度加权是否有用 |
| decay 开关 | 验证衰减是否减少振荡 |
| 特征消融（去掉 logic_gain / critical_distance） | 每个特征独立贡献 |

### 7.5 cut 在整体实验设计中的角色（与两环闭环的关系）

按 baseline_protocol §1：B01 fixed min-cut 是第一个必须对比的 baseline，证明 failure-aware refinement 优于固定切割；benchmark_flow §7 也把 fixed/random/size-only/critical-path-only 列为最重要消融。因此 cut 权重是 Stage A（外环）的核心机制，决定"切哪块逻辑"：

外环（Stage A）：min-cut -> patch -> 等价验证 -> F1-F5 -> 调权重 -> 重切
内环（Stage B）：关键路径实例 -> R/G/B 候选 -> OpenSTA 实测 -> 只接受改善
衔接点：F4（时序收益不足）触发内环诊断

升级顺序：先 §7.2 特征实算，再 §7.3 参数化反馈，最后跑 §7.4 消融。不引入 GNN/RL（8 电路数据量不足以支撑，且可解释性更利于工程类论文）。

### 7.6 一句话

cut 权重从"手写常数"升级为"可计算特征 + 参数化反馈 + 可消融"，是 FAECO 外环从工具变成方法的关键一步。
