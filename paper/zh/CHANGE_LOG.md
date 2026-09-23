# 论文修改记录

> 记录**每次修改论文**（内容 / 数字 / 术语 / 结构），便于回溯与防重复修改。
> 审稿轮次间的完整归档见 `paper/zh/review_rounds/`。

## 修改记录

| 日期 | 修改内容 | 原因 / 依据 | 关联（审稿轮次 / 证据 / 提交） |
|------|----------|-------------|-------------------------------|
| 2026-09-23 | §3.3 式(2) 补归一化分母与指示函数门控；表 2 符号表、图 2 注、§3.3 首段统一 $\lambda_c$ 表述（"不直接进入式(2)"→"以深度折扣形式进入"）；§3.4 正文与表 `tab:failures` 中 F1 补扇出权重 $\lambda_f$、F6 删未实现的尺寸惩罚 $\lambda_s$（共 8 处） | 代码—论文对照审计：`refinement.py:refine_weights` 与 `cut.py:166–199` 为实际实现，论文表述存在漏写（F1）/多写（F6）/不完整（λ_c）三处不一致。F1 主实验实测触发 138 次，属实质遗漏，非纯表述问题 | `consistency_audit` 续：`project_docs/review_history/paper_audit/code_paper_feedback_audit_20260923.md`；OI-008；LOG-20260923-03 |
| YYYY-MM-DD | 修改了… | 因… | r1 / 证据包路径 / commit |

## 规则

1. **每次修改论文后**：登记一行（修改内容、原因、关联）。
2. 修改数字必须同步证据交叉表（`project_docs/evidence/CROSSWALK_TEMPLATE.md`）。
3. 术语变更同步 `paper/GLOSSARY.md`（先改表再改正文）。
4. 审稿轮次间：完整归档到 `review_rounds/r<N>/`，本表记录概要。
