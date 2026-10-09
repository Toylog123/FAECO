# 归档：被取代的 Word 转排稿（勿投稿）

本目录存放**已被取代**的 JCAD Word 转排稿，仅供追溯，**不得作为投稿件**。

**当前有效稿**：`../FAECO_投稿Word转排_20261009c.docx` + `../FAECO_投稿Word转排_20261009c_Word导出.pdf`（来源 tag `v2026-10-09-text-review`）。

| 归档文件 | 作废原因 |
|---|---|
| `FAECO_投稿Word转排_20260930.docx` / `…_Word导出.pdf` | 参考文献 [1]–[19] **未按正文首次引用顺序编号**（P0，18/19 条错位）；已在 v4 修复 |
| `FAECO_投稿Word转排_20261009.docx` / `…_Word导出.pdf` | 参考文献已修（v4），但摘要仍为**技术术语密集版**（R/G/B/JOINT、F1--F6 等）；已在 v5 改写为面向大同行的概念化摘要 |
| `FAECO_投稿Word转排_20261009b.docx` / `…_Word导出.pdf` | ⚠ **文件名标注为 v5 稿，但摘要实为 v4 版**——v5 轮重建时只改了 `postprocess.py` 的输出路径，**漏改其硬编码的 `zh_abs` / `en_abs` / 中英文关键词**（转排管线缺陷，非 `.tex` 问题）。已由 v6（`…20261009c`）修正并重建：摘要同步为 v6 版（按 r7 审稿方向重加 R/G/B/JOINT 等术语），关键词"门级局部重构"→"局部门级修改"、英文 `local restructuring`→`gate-level local modification` |

审计依据：`../../REFERENCE_AUDIT_20261009.md`（文献）、`paper/zh/CHANGE_LOG.md` 2026-10-09 三行（文献修复 + v5 摘要改写 + v6 文字专项审稿）、`paper/zh/review_rounds/r7_20261009/response.md` 文末"执行记录"。

> **教训（写入交接）**：任何被转排管线**硬编码**的段落（`postprocess.py` 的 `zh_abs`/`en_abs`/关键词/标题/作者行）在 `.tex` 改写后**必须同步**，否则 Word 稿会静默保留旧文本；`preprocess.py` 的 `N_BIB` 守卫只覆盖参考文献条数。
