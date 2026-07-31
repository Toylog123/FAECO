# Paper Audit

用于审计学长 RSECO 旧稿是否具备投稿条件。

计划产物：

- `claim_evidence_matrix.md`：论文声明与证据对应关系。
- `legacy_source_locator.md`：旧稿 claim、公式、图表和表格的 PDF 页级出处。
- `legacy_table2_recalculation.md`：表2正文、Avg 行和逐 case 数据的独立复算。
- `pre_submission_review.md`：预投稿审稿意见。
- `formula_figure_audit.md`：公式、符号和图表完整性审计。
- `revision_roadmap.md`：投稿前修改路线。
- `method_rewrite_readiness.md`：方法要素的实现证据、可写边界和重写门槛。

当前状态：

| 文件 | 状态 | 说明 |
|---|---|---|
| `claim_evidence_matrix.md` | 已完成页级校订一轮 | 核心 claim 已链接到 PDF 页码并标记证据边界 |
| `legacy_source_locator.md` | 已创建 | 已记录 16 页 PDF/DOCX 核验、公式编号、图表和数值冲突 |
| `legacy_table2_recalculation.md` | 已创建 | 已确认四套汇总数字不一致，旧均值不可作为 FAECO 主证据 |
| `pre_submission_review.md` | 已更新 | 已给出 P0/P1/P2 问题清单，并纳入编号与数值一致性风险 |
| `formula_figure_audit.md` | 已完成页级校订一轮 | 已覆盖公式 (1)-(20)、图1-9、表1-5 和已确认问题 |
| `revision_roadmap.md` | 已创建 | 已按旧稿硬伤、formal/ABC、failure recovery、timing 和写作阶段拆分完成标准 |
| `method_rewrite_readiness.md` | 已按 Stage B 完成状态重映射 (2026-07-31) | 18 项方法要素中 METH-02 ready（Yosys formal runner 接入）、METH-15 ready（Stage B 8-case runtime 写回）、METH-17 partial（Stage B 8-case 跑通但 CEC/ISCS85/sequential 三项限制）；其余维持原状态 |
