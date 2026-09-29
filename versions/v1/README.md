# 版本 v1 — `v2026-09-29-submission-ready`（投稿就绪冻结）

- 基线 ID：`v2026-09-29-submission-ready`
- 冻结日期：2026-09-29
- git tag：`v2026-09-29-submission-ready`（annotated tag，指向包含本 README 与 `MANIFEST.sha256` 的提交）
- 方案：**D-01=A 轻量冻结**（tag + SHA-256 manifest，不复制 116 GB 实验原始输出）。用户 2026-09-29 拍板，选项与依据见 `project_docs/agent_handoff/DECISION_BRIEF_20260912.md`
- 变更摘要：论文内容冻结（9 页 / 0 Error / 0 Overfull / 0 Underfull）；实验主基线冻结（`faeco-exp-rev1`）。

## 关联冻结物

| 对象 | 锚点 |
|---|---|
| 本基线 | tag `v2026-09-29-submission-ready`（即本目录所在提交） |
| 论文发布 | tag `faeco-paper-final-20260929` = `a8142b6`；PDF 字节 SHA256 `9af41d77…`（双副本一致）；内容指纹 `7adf0279…` |
| 实验代码 revision | tag `faeco-exp-rev1` = `87d01ba` |
| 数字→实验族绑定 | `project_docs/evidence/PAPER_EVIDENCE_MANIFEST.md` |

## manifest 覆盖范围（四元绑定）

| 要素 | 文件 |
|---|---|
| 论文 | 主稿 `.tex` + 双副本 `.pdf`（字节 SHA256 `9af41d77…`，两份一致） |
| 源码 + 测试 | `code/src`、`code/tests` 全部 `.py/.md/.sh/.bat/.json/.txt/.toml/.cfg`（**不含** `__pycache__`、`egg-info` 等构建产物） |
| 实验权威汇总 | `experiments/RESULTS.md`、`experiments/results.json`、`experiments/20260826_aggregation/summary.json`（论文主数字源）、`experiments/20260826_aggregation/ablation_summary.json`、`experiments/20260826_sec/summary.csv` |

**验证方法**（仓库根目录）：`sha256sum -c versions/v1/MANIFEST.sha256` —— 117 条全部 OK 即冻结未动。

## 跟踪状态说明（2026-09-29 复核实测）

- manifest 117 条中 **114 条**同时被 git 跟踪（tag 与 manifest 双重锁定）。
- **3 条未被 git 跟踪**（被 `.gitignore` 排除），manifest 是其唯一完整性锁：
  - `experiments/20260826_aggregation/summary.json`（**论文主数字权威源**）
  - `experiments/20260826_aggregation/ablation_summary.json`
  - `experiments/20260826_sec/summary.csv`
  建议（待用户确认后执行）将这 3 个 KB 级文件纳入 git 跟踪，使其获得版本历史。
- 注意：`DECISION_BRIEF_20260912.md` 曾写"git 已跟踪聚合 summary"，实测不属实（2026-09-29 复核），以本 README 为准。

## 与模板版完整体的关系

本版本采用轻量方案：**历史由 git 承载**（tag 锁定全树），`versions/v1/` 只存 manifest + 本 README（KB 级），不复制 `code/`+`project/`+`experiments/`+`docs/` 完整体。若将来期刊要求证据打包，再按 D-01=B 方案补齐（见决策简报）。
