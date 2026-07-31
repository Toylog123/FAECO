# 主线定义：FAECO

更新时间：2026-07-07

暂定题目：**基于验证反馈的重综合辅助时序 ECO 框架**

暂定方法名：**FAECO**，即 **Failure-Aware ECO**。后续不沿用 RSECO 名称，避免让新工作看起来只是整理或复刻学长系统。

## 1. 研究定位

本项目不是简单复刻学长的旧代码，也不是完全另起炉灶做一个泛化的 AI ECO 系统。新的研究定位是：

> 在 RSECO 重综合辅助时序 ECO 思路基础上，面向中文工程类论文，建立一个可复现的公开实验流程，并重点研究等价 patch 切割失败后的自适应恢复机制。

## 2. 核心问题

学长 RSECO 的关键思想是：对时序约束变化后的 RTL 重新综合，得到一个时序更优的新网表；然后在新旧网表之间寻找等价局部子电路，将新网表中的时序友好 patch 移植回原始 APR 网表。

新的工作聚焦一个更窄、更容易做扎实的问题：

> 当 min-cut 产生的 patch boundary 无法通过等价验证、patch 过大或时序收益不足时，如何根据失败原因自动调整搜索方向，找到更可靠的替换 patch？

第一阶段先处理 timing path 上的组合逻辑 cone；第二阶段扩展到 sequential benchmark 中的局部组合逻辑 cone。论文中不声明直接修改寄存器结构，而是定位为“时序路径局部组合逻辑 ECO”。

## 3. 论文贡献草案

1. **算法贡献**：提出 failure-aware cut refinement，根据等价验证失败、patch size、关键路径覆盖不足和时序收益不足动态调整 cut weights。
2. **流程贡献**：构建公开 benchmark 上的 resynthesis-assisted timing ECO case generation flow，补足旧工作工业案例不可复现的问题。
3. **排序贡献**：提出 timing-aware patch ranking，在多个候选 patch 中平衡 WNS/TNS 改善、patch size、边界复杂度和验证成本。
4. **实验贡献**：在公开 benchmark 上对比 fixed min-cut、random cut、size-only cut、critical-path-only cut 和本文方法，并保留工程类指标体系。

## 4. 一句话论文故事

传统 timing ECO 的 buffering 和 gate sizing 难以修复严重逻辑级数违例；重综合能提供更优局部逻辑，但一次性切割容易出现等价失败、patch 过大或时序收益不足。本文提出 FAECO，通过验证反馈驱动的 cut refinement 和 timing-aware patch ranking，提高局部重综合 patch 的成功率和收益稳定性。

## 5. 第一阶段成功标准

第一阶段不要求做完完整工业级 ECO。成功标准是：

- 能在公开小型 combinational benchmark 上构造 timing ECO case；
- 能从原始网表和重综合网表中提取候选 cone / patch；
- 能对候选 patch 做等价验证；
- 能复现实验表：WNS/TNS 或替代时序指标、违例路径数量、patch size、逻辑级数变化、运行时间、等价验证成功率；
- 能展示 failure-aware refinement 相比固定权重切割更稳。

第二阶段成功标准：

- 能在 sequential benchmark 中抽取局部组合逻辑 cone；
- 能解释寄存器边界和时序路径的处理方式；
- 能把第一阶段方法迁移到更接近真实设计的路径级 ECO 场景。

## 6. 暂定工具链

第一版使用确定性方法，不引入 GNN/RL：

- Python 原型；
- Yosys / ABC 做综合、重综合和逻辑处理；
- Z3 或 ABC 做等价验证；
- OpenSTA 做时序指标；
- NetworkX 或自实现 max-flow/min-cut 做 cut refinement。

