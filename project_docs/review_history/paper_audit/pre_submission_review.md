# RSECO 旧稿预投稿审计

更新时间：2026-07-19

结论先行：

> 旧稿不建议原样投稿。更可行的路线是保留其问题定义和重综合辅助思想，将新工作重构为 FAECO，并用公开 benchmark 与 failure-aware cut refinement 建立新的证据链。

## P0 问题：投稿前必须解决

| ID | 问题 | 影响 | 处理方案 |
|---|---|---|---|
| P0-01 | 原代码不可用或质量不可控 | 旧结果无法复现，审稿中难以回应实现细节 | 不依赖旧代码，重写最小可复现原型 |
| P0-02 | 原工业数据不可公开 | 实验可复现性不足，结果可信度受限 | 主实验使用来源和许可固定的 EPFL/ITC 等公开 benchmark；当前许可未声明的 ISCAS85 文件只作本地 smoke |
| P0-03 | 商业 B&G baseline 设置不透明 | “优于商业工具”的 claim 难以验证公平性 | 第一篇以开源 baseline 为主，商业结果降级为背景或补充 |
| P0-04 | 递归学习策略缺少充分消融 | “解决 ECO 算法失效”缺少直接证据 | 设计 failure-aware refinement 消融，统计 recovery success rate |
| P0-05 | 公式编号、交叉引用和实验数值存在一致性问题 | 原式(16)-(20)缓存编号未刷新、图6误引为图1、表2四套统计不一致，影响可读性和结果可信度 | 以 `legacy_source_locator.md`、`legacy_table2_recalculation.md` 为依据修正编号/引用，删除不可认证均值，并按 FAECO 口径重写公式 |
| P0-06 | 等价验证流程不够可复现 | patch 是否功能等价是核心正确性问题 | 明确 SAT/ABC/Z3 验证流程，记录 equivalence pass/fail |
| P0-07 | benchmark case 构造规则不明确 | 新旧网表、约束变化、目标 cone 的来源不清楚 | 定义 `case_schema.md` 和 case generation protocol |

## P1 问题：会影响论文质量

| ID | 问题 | 影响 | 处理方案 |
|---|---|---|---|
| P1-01 | 只做组合电路容易被质疑真实场景不足 | timing ECO 通常发生在 sequential design 中 | 第一阶段做 combinational cone，第二阶段做 reg-to-reg cone |
| P1-02 | 文献综述需要更新 | 已核验 25 篇 A 级全文和 1 条 B 级官方证据；DAC 2006 SAT Sweeping 已由归档全文升级为 A，BUFFALO 与两篇 ML timing 工作均已完成全文与边界核验 | 按 `core_paper_notes.md` 形成 Related Work 初稿；DAC 2018 维持 B 级使用边界并定期复核，不阻塞初稿 |
| P1-03 | 指标体系需重新定义 | WNS/TNS、Max-LL、patch size 口径需要可复现 | 建立 `metrics_and_tables.md` |
| P1-04 | runtime 和规模扩展性证据不足 | 工程类论文需要展示可运行性 | 记录分阶段 runtime：cut、verification、ranking、total |
| P1-05 | 参数设置缺少敏感性分析 | cut weight 和 ranking 权重可能被认为是经验调参 | 增加默认参数、参数范围和 ablation |
| P1-06 | 论文贡献表述容易显得像工程组合 | 创新性不足 | 把第一贡献固定为 failure-aware cut refinement |

## P2 问题：写作和呈现层面

| ID | 问题 | 影响 | 处理方案 |
|---|---|---|---|
| P2-01 | RSECO 名称容易让新工作被看作旧系统修补 | 新论文独立性不足 | 新方法名采用 FAECO |
| P2-02 | 摘要中过早给出旧工业数值 | 若新实验不一致，会造成叙事冲突 | 新摘要基于新实验结果重写 |
| P2-03 | 图表需要重新编号和统一风格 | 已确认图6误引、旧审计遗漏图9/表5，影响投稿格式和证据定位 | 先修复交叉引用，再在论文初稿阶段统一重画和编号 |
| P2-04 | 部分段落偏工程说明，贡献提炼不足 | 影响审稿人快速理解创新点 | 按“背景-缺口-方法-证据”重写 |

## 建议修改路线

| 阶段 | 动作 | 产物 |
|---|---|---|
| 1 | 旧稿 claim 审计 | `claim_evidence_matrix.md` |
| 2 | 公式图表审计 | `formula_figure_audit.md` |
| 3 | 公开 benchmark 与 case schema | `benchmark_selection.md`、`case_schema.md` |
| 4 | baseline 与指标定义 | `baseline_protocol.md`、`metrics_and_tables.md` |
| 5 | FAECO 算法重写 | `faeco_algorithm.md` |
| 6 | 最小原型和第一轮实验 | `src/`、`experiments/` |
| 7 | 中文论文重写 | `paper/draft/` |

## 投稿可行性判断

当前旧稿直接投稿风险较高。若完成以下条件，转为中文工程类论文的可行性较高：

1. FAECO 有清晰算法伪代码和失败反馈机制。
2. 至少一个公开 benchmark flow 可端到端复现。
3. 有 fixed min-cut、random cut、size-only、critical-path-only、ABC baseline 对比。
4. 有 recovery success rate、equivalence pass rate、patch size、runtime 等工程指标。
5. sequential cone 扩展至少有设计文档和一个 demo 或 case study。
