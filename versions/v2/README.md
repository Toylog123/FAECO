# 版本 v2 — `v2026-09-30-submission-ready`（投稿格式适配冻结）

- 基线 ID：`v2026-09-30-submission-ready`
- 冻结日期：2026-09-30
- git tag：`v2026-09-30-submission-ready`（annotated tag，指向包含本 README 与 `MANIFEST.sha256` 的提交）
- 方案：**D-01=A 轻量冻结**（同 v1；tag + SHA-256 manifest，不复制原始输出）
- **派生来源**：自 v1（`v2026-09-29-submission-ready`）派生。改动 = **论文中英摘要两段**（用户 OI-020 授权：中文压至 295 字、去"本文"句式；英文压至 149 词，JCAD 格式适配），其余正文、全部数字、实验族归属、代码、测试、证据**零改动**。详见 `paper/zh/CHANGE_LOG.md` 2026-09-30 行与 `PAPER_EVIDENCE_MANIFEST.md` §6。

## 与 v1 的差异

| 项 | v1（superseded） | v2（active） |
|---|---|---|
| 论文 tag | `faeco-paper-final-20260929`（a8142b6） | `faeco-paper-final-20260930`（本基线内） |
| PDF 字节 SHA256 | `9af41d77…` | `df82292f…` |
| 内容指纹（poppler 25.07） | `7adf0279…` | `43becd39…` |
| 摘要 | 约 460 字 / 约 250 词，含"本文提出" | **295 字 / 149 词，无第一人称** |

## manifest 覆盖范围（四元绑定，与 v1 相同口径）

论文 `.tex` + 双副本 `.pdf`；`code/src`、`code/tests` 全部源文件（不含构建产物）；`experiments/RESULTS.md`、`experiments/results.json`、`20260826_aggregation/summary.json`（论文主数字源）、`ablation_summary.json`、`20260826_sec/summary.csv`。

**验证方法**（仓库根目录）：`sha256sum -c versions/v2/MANIFEST.sha256` —— 117 条全部 OK 即冻结未动。

## 跟踪状态说明

同 v1：manifest 117 条中 114 条同时被 git 跟踪；3 条证据汇总文件（`20260826_aggregation/summary.json`、`ablation_summary.json`、`20260826_sec/summary.csv`）未被 git 跟踪（OI-022，用户拍板维持现状），manifest 为其唯一完整性锁。
