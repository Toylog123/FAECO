# 版本 v4 — `v2026-10-09-reference-fix`（参考文献规范修复冻结）

- 基线 ID：`v2026-10-09-reference-fix`
- 冻结日期：2026-10-09
- git tag：`v2026-10-09-reference-fix`（annotated tag，指向包含本 README 与 `MANIFEST.sha256` 的提交）
- 方案：**D-01=A 轻量冻结**（同 v1/v2/v3）
- **派生来源**：自 v3（`v2026-09-30-submission-ready-r2`）派生。改动 = **T20 投稿检查单 #3 参考文献核对后的著录层修复**（用户 2026-10-09 拍板"方案 A"）：
  1. **P0 编号顺序**：`thebibliography` 由 19 条重排为 14 条、严格按正文首次引用顺序编号（原首处引用渲染为 `[1, 7, 9]`，18/19 条错位）；
  2. **P1**：会议文献 `[C]//` → `[C] //`（JCAD 规范模板）；期刊名 `Integration` → `Integration, the VLSI Journal`（规范一.3）；BUFFALO 题名补全（…`via group relative policy optimization`）；`liberty`（Liberty User Guide，v3 中 `[Z]` 且来源不可核）条目整体移出参考文献表；
  3. **5 条工具/技术文档类引用转正文页脚**（规范一.12）：`picorv32`、`yosys`、`opensta`、`sky130`（正文引用 2 处，含原 `liberty` 所指的 Liberty 文件句）→ 正文 5 处 `\footnote{\url{…}}`，参考文献由 19 条降为 **14 条**；
  4. **P2**：`kravets2019symbolic` 页码 `1-6` → `71:1-71:6`；DATE 会议名补 `& Exhibition`；RL-Sizer 出版者 ACM → IEEE、会议名 `58th ACM/IEEE Design Automation Conference`；`itc99` 题名标点；
  5. **补 DOI**：14 条全部补 DOI（用户 2026-10-09 拍板）。
  详见 `paper/zh/submission/REFERENCE_AUDIT_20261009.md`、`paper/zh/CHANGE_LOG.md` 2026-10-09 行。
  **零数字、零实验改动**——正文数字、公式、图表、结论均未变，仅参考文献著录层。

## 与 v3 的差异

| 项 | v3（superseded） | v4（active） |
|---|---|---|
| 论文 tag | `faeco-paper-final-20260930-r2` | `faeco-paper-final-20261009` |
| 参考文献条数 | 19（编号未按引用顺序） | **14（按引用顺序）** + 5 处正文页脚 |
| 论文 `.tex` SHA256 | `9879107455…` | `7a0cfed3…` |
| PDF 字节 SHA256 | `28647dc0…` | `dea21bb3…` |
| 内容指纹（poppler 25.07） | `70bbd610…` | `6ca972d5…` |
| 页码 / 质量门 | 9 页 / 0/0/0 | 9 页 / 0/0/0 |

## manifest 覆盖范围（与 v1/v2/v3 相同口径）

论文 `.tex` + 双副本 `.pdf`；`code/src`、`code/tests` 源文件（不含构建产物）；`experiments/RESULTS.md`、`results.json`、`20260826_aggregation/summary.json`（论文主数字源）、`ablation_summary.json`、`20260826_sec/summary.csv`。

**验证方法**（仓库根目录）：`sha256sum -c versions/v4/MANIFEST.sha256` —— 117 条全部 OK 即冻结未动。
