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

