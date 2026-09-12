# 2026-07-14 本周课题汇报规划

## 1. 汇报定位

这次汇报建议定位为：**课题接手后的方向确认与执行规划汇报**。

不要把它讲成“已经完成算法和实验”的成果汇报。当前最有价值的是把以下几件事讲清楚：

1. 学长 RSECO 工作的基础是什么。
2. 原代码和原数据不可用后，为什么不能简单复现旧论文。
3. 新课题如何继承旧工作的技术主线。
4. 新方法 FAECO 的核心创新点是什么。
5. 后续实验和工程计划如何保证可复现、可发表。

一句话目标：

> 本次汇报要让老师认可：我们不是盲目重做，也不是脱离原课题另起炉灶，而是在 RSECO 的问题定义上，提出一个更可复现、更容易落地的新工作 FAECO。

## 2. 建议汇报时长

推荐按 **15-20 分钟** 准备，PPT 控制在 **12-15 页**。

如果只有 10 分钟，删掉文献和长期路线细节，保留问题、方法、计划。

如果有 30 分钟，可以增加旧稿实验表分析、文献分类和 benchmark flow 细节。

## 3. 核心叙事线

汇报不要按“我整理了哪些文件”讲，而要按论文逻辑讲：

```text
ECO 后期时序修复很难
-> 学长 RSECO 提供了重综合辅助局部替换思路
-> 但旧代码/数据不可用，且旧方法存在可复现性和失败恢复问题
-> 新工作 FAECO 保留重综合辅助 patch replacement
-> 重点解决 cut 失败后的验证反馈和自适应恢复
-> 通过公开 benchmark flow 建立可复现实验
-> 先做组合逻辑 cone，再扩展到 sequential path cone
```

核心关键词：

- 时序 ECO
- 重综合辅助
- 等价 patch 替换
- 验证反馈
- failure-aware cut refinement
- 可复现 benchmark flow
- 中文工程类论文

## 4. PPT 结构建议

### Slide 1：标题页

标题建议：

**基于验证反馈的重综合辅助时序 ECO 框架：课题接手与研究计划**

副标题：

**FAECO: Failure-Aware ECO**

要讲：

- 本次汇报是阶段性规划，不是最终实验结果。
- 目标是明确接手旧工作的后续路线。

### Slide 2：课题背景：为什么需要 Timing ECO

要点：

- 芯片设计后期重新跑完整流程代价高。
- 时序违例需要尽量局部修复。
- 传统 timing ECO 主要依赖 buffering 和 gate sizing。
- 严重逻辑级数违例时，B&G 往往不够。

建议图：

```text
APR 后发现 timing violation
-> 局部 ECO 修复
-> 避免全流程重跑
```

注意：

- 不要讲太宽，不要展开 post-mask spare cell。
- 聚焦 pre-mask / late-stage timing ECO。

### Slide 3：学长 RSECO 工作基础

要点：

- RSECO 使用重综合网表辅助原网表修复。
- 通过等价点搜索和关键路径感知切割，移植新网表中的局部 patch。
- 旧稿已有完整论文结构和工业案例。

可以用一张流程图：

```text
原始 APR 网表 + 新约束
        |
    出现违例
        |
RTL 重综合 -> 新网表
        |
等价点搜索 + min-cut
        |
局部 patch 替换
```

要讲清楚：

- 我们不是否定旧工作。
- 旧工作是新课题的问题定义和技术来源。

### Slide 4：当前接手遇到的问题

要点：

| 问题 | 影响 |
|---|---|
| 原代码不可用或质量不可控 | 不能直接复现实验 |
| 原工业数据不可公开 | 投稿可复现性不足 |
| 旧方法对 cut 失败恢复讲得不够系统 | 创新点需要重新凝练 |
| 公式、baseline、实验设置需要重新审计 | 投稿前需要补证据 |

这一页要讲得直接一点：

> 因此后续不是简单整理旧稿，而是基于旧思路重构一个可复现的新工作。

### Slide 5：新工作定位：FAECO

标题：

**FAECO：Failure-Aware ECO**

定位：

> 在重综合辅助时序 ECO 框架中，将 patch 替换失败结果转化为 cut refinement 的反馈信号。

核心问题：

> 当 min-cut 产生的 patch boundary 无法通过等价验证、patch 过大或时序收益不足时，如何根据失败原因自动调整搜索方向？

要点：

- 不沿用 RSECO 名称，避免变成“复刻旧系统”。
- 继承 RSECO 的问题和基本流程。
- 新贡献集中在 failure-aware refinement 和可复现 flow。

### Slide 6：FAECO 总体框架

建议画流程：

```text
Benchmark / Design
    |
Original netlist
    |
Resynthesis
    |
Candidate patch extraction
    |
Equivalence verification
    |
Failure classification
    |
Weight refinement
    |
Timing-aware ranking
    |
Patched netlist + metrics
```

要强调：

- 验证不是最后一步，而是反馈信号来源。
- cut 失败后不直接放弃，而是进入 refinement。

### Slide 7：失败类型定义

这是本次汇报最重要的一页之一。

| 类型 | 含义 | 调整方向 |
|---|---|---|
| F1 等价失败 | 替换后功能不等价 | 移动或扩大 cut boundary |
| F2 边界不闭合 | patch 输入输出无法稳定对应 | 避免复杂 fanout/reconvergence |
| F3 patch 过大 | 修改规模过大 | 压缩非关键区域 |
| F4 时序收益不足 | WNS/TNS 或逻辑级数改善不明显 | 强化关键路径覆盖 |
| F5 验证代价过高 | SAT/验证时间过长 | 限制 cone size 或分层验证 |

要讲：

- 这不是简单“调参”。
- 每种失败都对应一种工程现象和反馈策略。

### Slide 8：Timing-Aware Patch Ranking

第一版不做 GNN/RL，使用确定性 scoring：

```text
score = alpha * timing_gain
      - beta  * patch_size
      - gamma * boundary_complexity
      - delta * verification_cost
      + eta   * equivalence_confidence
```

要点：

- 工程可解释。
- 适合中文工程类论文。
- 后续可扩展成学习式 ranking，但不是第一阶段目标。

### Slide 9：实验设计：从组合逻辑到时序路径

要正面回应“只做组合逻辑是否真实”的问题。

建议表述：

> 第一阶段在 combinational benchmark 上验证 patch replacement 和 failure-aware refinement 的机制；第二阶段在 sequential benchmark 中抽取 reg-to-reg path 的组合逻辑 cone，将方法迁移到更真实的 timing ECO 场景。

表格：

| 阶段 | 数据 | 目的 |
|---|---|---|
| Stage A | ISCAS/EPFL combinational | 验证核心算法机制 |
| Stage B | ITC/ISCAS sequential path cone | 验证接近真实时序路径 |
| Stage C | 可恢复工业案例 | 作为 case study |

### Slide 10：评价指标与 Baseline

工程类论文必须强调指标。

指标：

- WNS / TNS
- 违例路径数量
- logic level / Max-LL
- patch size / change ratio
- runtime
- equivalence pass rate
- recovery success rate

baseline：

- fixed min-cut
- random cut
- size-only cut
- critical-path-only cut
- ABC resyn / rewrite / refactor
- ABC if / map

### Slide 11：当前项目状态

要点：

已完成：

- 主线确定为 FAECO。
- 原始材料已归纳。
- 工程目录已整理。
- 长期路线图、任务表、风险表已建立。
- benchmark flow、failure-aware cut、patch ranking 已有设计草案。

当前阶段：

- Phase 1：论文证据审计。

下一步：

- claim-evidence matrix。
- 旧稿预投稿审计。
- benchmark flow 细化。

### Slide 12：长期计划

按阶段讲：

| 阶段 | 目标 |
|---|---|
| Phase 1 | 旧稿 claim 和证据审计 |
| Phase 2 | benchmark flow 定稿 |
| Phase 3 | 最小算法原型 |
| Phase 4 | combinational 实验 |
| Phase 5 | sequential cone 扩展 |
| Phase 6 | 中文论文初稿 |

要讲：

- 当前不是直接开写论文，也不是直接写代码。
- 先确定证据和实验定义，再实现。

### Slide 13：本周计划

建议本周完成：

1. 完成旧稿 claim-evidence matrix。
2. 完成旧稿预投稿审计初版。
3. 选定第一批 benchmark。
4. 明确 benchmark case schema。
5. 准备下一次汇报中的技术细节页。

### Slide 14：需要老师确认的问题

这一页很重要，要主动请老师给反馈。

建议提问：

1. 中文论文目标是否合适？
2. FAECO 这个新方法名和方向是否认可？
3. 第一阶段先做 combinational cone，第二阶段扩展 sequential path cone 是否可接受？
4. 是否需要继续尝试联系学长获取旧代码/实验日志？
5. benchmark 是否优先 ISCAS/EPFL/ITC？
6. 论文贡献是否应把 failure-aware cut 放在第一位？

## 5. 本周准备日程

假设本周五汇报，可按下面推进。

| 日期 | 任务 | 产物 |
|---|---|---|
| 7/14 | 梳理汇报逻辑，确定 PPT 结构 | 本规划文档 |
| 7/15 | 做旧稿 claim-evidence matrix 初版 | `docs/paper_audit/claim_evidence_matrix.md` |
| 7/16 | 做 benchmark flow 细化和图示 | `case_schema.md` 草案 + PPT 图 |
| 7/17 | 完成 PPT 初稿和讲稿 | 12-15 页 PPT |
| 7/18 | 自查、压缩、准备答问 | 最终汇报版 |

如果汇报更早：

- 保留 Slide 1-11；
- Slide 12-14 用口头说明。

## 6. 汇报前必须准备的材料

必备：

- `docs/mainline.md`
- `docs/project_management/roadmap.md`
- `docs/materials/rseco_legacy_paper_summary.md`
- `docs/experiment_design/failure_aware_cut.md`
- `docs/experiment_design/benchmark_flow.md`
- `docs/experiment_design/patch_ranking.md`

建议补齐：

- `docs/paper_audit/claim_evidence_matrix.md`
- `docs/experiment_design/case_schema.md`
- `docs/experiment_design/baseline_protocol.md`

## 7. 可能被问到的问题与回答

### Q1：为什么不继续复现学长 RSECO？

答：

旧代码和旧数据不可用或质量不可控，直接复现风险很高。我们保留 RSECO 的问题定义和重综合辅助思想，但将新工作定位为 FAECO，重点解决旧工作没有系统展开的 failure-aware cut refinement 和公开可复现实验问题。

### Q2：只做组合逻辑是不是不够真实？

答：

第一阶段只在组合逻辑 cone 上验证算法机制；第二阶段会从 sequential benchmark 中抽取 reg-to-reg timing path 的组合逻辑 cone。这样既保证方法可控，也能逐步贴近真实 timing ECO 场景。

### Q3：创新点到底是什么？

答：

不是简单使用 min-cut，而是把 ECO patch 替换中的失败结果结构化为反馈信号，包括等价失败、边界不闭合、patch 过大、时序收益不足和验证代价过高，并用这些信号驱动下一轮 cut weight refinement。

### Q4：为什么不用 GNN/RL？

答：

第一篇中文工程类论文优先保证可解释、可复现和可落地。确定性 scoring 更容易解释和验证。后续如果需要，可以把 ranking 特征扩展到学习式模型。

### Q5：没有商业 B&G baseline 怎么办？

答：

第一阶段使用开源 baseline，包括 fixed min-cut、random cut、size-only cut、critical-path-only cut，以及 ABC resyn/rewrite/refactor/if/map。若后续能接入 OpenROAD/OpenSTA flow，再补更接近工业工具的比较。

### Q6：这个工作能发吗？

答：

如果只是整理旧稿，风险较高；但现在的路线是新方法 + 可复现 benchmark flow + 工程指标实验。中文工程类论文的可行性较高，关键是尽快完成 claim-evidence matrix 和第一轮公开 benchmark 实验。

## 8. 汇报时不要过度承诺

不要说：

- 已经完成算法。
- 已经证明方法有效。
- 可以达到学长旧稿的所有指标。
- 直接能投。

可以说：

- 已经完成方向重构和项目管理。
- 已经明确新方法 FAECO 的问题定义。
- 已经建立实验和工程路线。
- 下一阶段会用公开 benchmark 验证可行性。

## 9. 汇报结论页建议

最后一页可以这样收：

> 本阶段完成了对 RSECO 旧工作的接手分析，并将后续研究重构为 FAECO：一个基于验证反馈的重综合辅助时序 ECO 框架。下一步将围绕旧稿 claim-evidence 审计、公开 benchmark flow 和 failure-aware cut refinement 原型展开，目标是形成一篇可复现、可投稿的中文工程类论文。

