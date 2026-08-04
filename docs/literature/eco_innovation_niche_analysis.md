# FAECO 相关领域对标与创新性分析

更新时间：2026-08-04

文档性质：基于本地文献库（25 篇 A 级核验）+ Crossref 多轮检索（2026-08-04）的竞争格局分析。结论用于指导论文定位与实验设计，不替代逐篇精读。

## 1. 检索方法

1. 本地核验：docs/literature/literature_matrix.md（Timing ECO / Functional ECO / Buffering & Gate Sizing / ML 四组，25 篇 A 级 + 1 篇 B 级）。
2. 在线检索：Crossref API 共 9 组关键词 + OpenAlex API 共 3 组关键词，覆盖"timing ECO + 自适应修复""resynthesis + 失败反馈""验证反馈驱动 cut refinement""ECO fixability + 策略选择""B&G + remapping 组合"等角度。

补充发现（OpenAlex 2026-08-04）：

- TSTL-GNN: Graph-Based Two-Stage Transfer Learning for Timing ECO Analysis Acceleration（Electronics 2024, DOI 10.3390/electronics13152897）：用 GNN + 两阶段迁移学习加速时序 ECO 分析——但它是"分析加速"（预测 ECO 影响），不是"策略选择/失败反馈"，与 FAECO 生态位不同。
- A Survey of Machine Learning Approaches in Logic Synthesis（ACM TODAES 2025, DOI 10.1145/3785362）：ML 用于逻辑综合的综述，可用于定位 FAECO 在学习式方法中的边界（FAECO 不用 GNN/RL，用可解释规则）。

## 2. 最接近的已有工作（审稿人会对标的对象）

| 方向 | 代表作 | 与 FAECO 的关系 |
|---|---|---|
| B&G 联合优化 | AiTO 2024（GNN+RL 联合 sizing+buffering, DOI 10.1016/j.vlsi.2024.102211）、RL-Sizer 2021 | 联合 B&G 求解，无逻辑重写 R、无失败反馈 |
| remapping 补 B&G | Ho et al. TCAD 2010（spare-cell B&G + tech remapping 两阶段, DOI 10.1109/TCAD.2010.2043573）、CPA-Remap ICCD 2025（DOI 10.1109/ICCD65941.2025.00063） | 最接近"多手段组合"，但切换是固定两阶段，非失败反馈驱动 |
| 重综合辅助局部替换 | TRECO TCAD 2012（模板驱动迭代 remapping, DOI 10.1109/TCAD.2012.2201480） | 与 FAECO 外环最接近，但面向工业 spare-cell 约束 |
| 功能 ECO 失败回退 | SAT proof minimization + interpolation 2010、multi-error rectification DAC 2011（DOI 10.1145/2024724.2024758） | 有"失败后换方法"思想，但 functional 非 timing，且无策略学习 |
| 可修复性判断 | Bezier fixability identification TCAD 2012 | 多特征判断"能不能修"，不是"选哪个策略" |

## 3. 未检索到直接先例的生态位

1. **验证失败（F1-F5）驱动 cut 权重调整**：等价失败/边界失败/patch 过大/时序不足/验证超时结构化为反馈信号反向调整 cut 搜索空间——未搜到 ECO 领域先例（形式化验证领域有 CEGAR，但非 ECO）。
2. **跨策略自适应切换 + 跨电路经验复用**：按实例特征预测 R/G/B 策略——未搜到；近两年 RL 工作（AiTO、IR-aware ECO MLCAD 2024, DOI 10.1145/3670474.3685945）学习 cell 级动作，不是策略级选择。

## 4. 创新性评估

整体定位：**中上，且生态位空缺**。核心组合"验证反馈驱动的跨策略自适应时序 ECO"无直接先例。

三点风险与应对：

1. "组合已有技术"质疑：用消融实验证明每个反馈分支/策略各自贡献 + 决策层效率对比（同 WNS 下比 STA 调用数）。
2. "failure-aware 标签"先例：2012 fixability、CEGAR 均有影子，需 in-text 明确区分。
3. 2024-2025 新对照：CPA-Remap（ICCD 2025）、IR-aware RL ECO（MLCAD 2024）、AiTO（Integration 2024）必须引用并对齐。

## 5. 结论

创新性有真实支撑，但组合型工作的创新必须靠"决策层效率对比 + 反馈消融"两类实验落地，否则容易被审稿人打回为"拼盘"。这两类实验也是当前实现最缺的部分。
