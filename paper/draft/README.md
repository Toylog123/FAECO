# Paper Draft Index

更新时间：2026-07-31

本目录是 FAECO 论文草稿和章节草案，按论文主体顺序组织。所有内容均为 Draft 1，未经用户最终审定；禁止作为论文主表事实性表述。

## 章节初稿

| 章节 | 文件 | 对应长期任务 | 状态 |
|---|---|---|---|
| Introduction | `introduction.md` | PM25 | Draft 1 (2026-07-31) |
| Related Work | `related_work.md` | L01 | Draft 1 (2026-07-31) |
| Method (符号表与骨架) | `method_symbol_table.md` | N05 | Draft 1 (2026-07-31) |
| Method (正文) | `method.md` | PM27 | Draft 1 (2026-07-31) |
| Experiments | `experiments.md` | PM28 | Draft 1 (2026-07-31) |
| Conclusion | `conclusion.md` | PM29 | Draft 1 (2026-07-31) |

## 章节一致性

- 5 个章节初稿共享以下基础：
  - `docs/mainline.md` 主线定义（FAECO 名称、研究定位）
  - `docs/literature/literature_matrix.md` 25A/1B 文献证据（用于 related_work.md 和结论边界）
  - `docs/paper_audit/method_rewrite_readiness.md` 18 项方法要素审计（用于 method_symbol_table.md）
  - `experiments/20260718_minimal_combinational_batch_demo/` + `experiments/20260731_epfl_8case_stage_b/` 真实实验产物（用于 experiments.md 和 conclusion.md）

## 章节修订顺序

1. **PM27 Method 章节正文**：已完成 Draft 1（`method.md`）。等待 method_symbol_table 符号表获用户审定后与 `method.md` 同步修订符号。
2. **L01 Related Work 迁入**：当用户审定 `related_work.md` 后迁入 `paper/submission/related_work.md`，并按论文主风格重组。
3. **PM25-29 迁入**：所有章节初稿获用户审定后迁入 `paper/submission/`。
4. **figures/ 占位**：已建立（`paper/figures/README.md`），等 method chapter 获批后渲染图 1-5。
5. **tables/ 占位**：已建立（`paper/tables/README.md`），表 1-6 已在 `experiments/` 落盘 markdown。

## 当前 limitation（章节初稿中明确标注）

- L31-01 / R31-01：SKY130 Liberty 不含 `clkinv_1` cell → CEC unavailable
- L31-02：8 case 全 combinational → STA slack=null / slack_status=MET (INF)
- L31-04 / X19：failure_recovery 仍是 single-iteration proxy
- L31-03：Z3 candidate/boundary formal 未接入

## 与其他文档的边界

- `docs/paper_audit/pre_submission_review.md` —— 旧稿预投稿审计结论
- `docs/paper_audit/revision_roadmap.md` —— RR02-RR10 论文修订路线
- `docs/paper_audit/claim_evidence_matrix.md` —— 旧稿 16 页 claim × 证据对应
- `docs/paper_audit/formula_figure_audit.md` —— 公式、图表完整性审计

这些文档与本目录的章节初稿共同构成论文撰写的事实基础。任何对 B 级证据 [F08-B] 和 [B06] 的引用须保留禁止声明，禁止引用其算法细节与数字。