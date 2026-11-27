# project_docs 入口

> **2026-11-27 第七轮主稿入口**见 [CANON](CANON.md)、[逐条复核](../paper/zh/review_rounds/r20261127_r7_editorial/R7_REVIEW_MAP.md)、[补充材料](../paper/zh/manuscript/FAECO_R7_补充材料.pdf) 与 [公开复算](evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md)。此前阶段仍可通过 [11 月 25 日交接](HANDOFF_2026-11-25.md) 追溯。

<details>
<summary>2026-11-13 过渡期入口（历史）</summary>

> **2026-11-13 当前入口：可调时序预算机制。** 优先读 `project_docs/evidence/timing_budget_20261113/REPORT.md` 与 `project_docs/CANON.md`。保留Resizer前端；默认允许WNS最多损失10ps，TNS辅助、hold保持原门。s382既有端点在该预算下已补SEC101/0：回收Resizer净新增面积28.90625%（总面积−4.399524%，WNS−3.098077ps，TNS−0.231982231ns）。这是已有物理端点重筛，不是新搜索算法收益。新 `code/src/rseco/budgeted_recovery.py` 实现纯策略/有界组合搜索，在线物理评估器、完整IO约束、强基线/跨设计尚待建立；下方strict政策与旧状态均保留历史。


> **2026-11-13 最新续跑**：见 `project_docs/evidence/strict_area_search_20261113/REPORT.md`。新增9组合+2同面积variant全部未过严格门，两排序所有预算前缀均保留原096安全端点（面积−0.594530321%）。完整网表/Liberty另枚举62个静态兼容降面积替换，旧清单只覆盖10；剩余51个遗漏目标本轮未测。静态候选不是收益，自有机制优势/完整约束仍open。
> **2026-11-13 接手优先级**：先读 `evidence/recovery_repair_20261113/REPORT.md`、`CANON.md` 与 `FAECO_ROADMAP.md`。当前目标是自己的机制在时序不下降条件下优化面积；41个物理候选中唯一接受的s382单动作基线节省0.594530321%，联合机制尚无优势证据。下方现行文件数及2026-11-09状态已过期，保留作溯源。

> **历史表述：本目录只有 6 个现行文件，其余全为历史。** 历史不是删掉了，是归档了——见 `ARCHIVE_INDEX.md`。

</details>

## 必读（按序）

当前补充入口：[SKY130 逐端点对齐与联合评测](evidence/sky130_joint_constraints_20261123/REPORT.md) · [中文 v3 修订稿](../paper/zh/FAECO_v3_后布局可调预算面积回收.pdf)。

0. **接手先读 [现行交接](HANDOFF_2026-11-25.md)**，其中包含现状、复现、自检和后续工作。
1. **[CANON](CANON.md)** 给出唯一现行口径、证据数字和待决项。
2. **`PROJECT_MAP.md`** —— 目录职责、版本三层对应、数据资产归属、6 条结构性坑。
3. **`LOGS.md`**（事实流水，只追加）/ **`OPEN_ISSUES.md`**（未决容器）。

`ARCHIVE_INDEX.md` 记录所有归档去向，含「这份为什么不见了」。

<details>
<summary>2026-11-09 实测 r116（历史）</summary>

论文已到 **r116**：主稿 **11 页 / 17 `\bibitem` / 7 图 / 5 表**（`.tex` SHA 前缀 `d5bbc9bd`、PDF `47c5964c`），
补充 **15 页 / 22 表 / 5 图**（`c9c73242`、`04df3914`），英文 **26 页**（`327987d2`，**自 r96 起未同口径**，见 CANON §8 P12）。
主稿与补充 `.tex` 均**纯 LF**、三副本逐字节一致、两篇质量门 GATE PASS（`Undefined: 5` 是字体替身，非缺失引用）。

判据门槛 `Δ_WNS > 0` **不是**"低于判定带 5 倍"的缺陷：r102 反事实已证它只是候选集 argmax 的实现细节，
把判定带塞进接受规则反而把累积从 8/8 打到 4/8（CANON §5）。

git：HEAD `faa533a`、工作区 clean、**30 条提交未 push**。基线 `active` 仍是 v19 / r28，
`versions/v19/MANIFEST.sha256` 当前实测 **139 OK / 9 FAILED**（r95 起的文本改动 + r108/r113 代码改动造成的预期漂移），
**r95–r116 尚未冻结成 v20**。

测试：全量 `pytest code/tests` 需把 OSS-CAD 的 `bin` 与 `lib` 放在 PATH 最前（原因见 `PROJECT_MAP.md` §7），
否则 5 个依赖真实 yosys 的用例会因 DLL 串位假红。

</details>

## 论文入口

- 活跃中文工作稿为 [后布局 v3 源码](../paper/zh/manuscript/FAECO_v3_后布局可调预算面积回收.tex) 与 [15 页 PDF](../paper/zh/FAECO_v3_后布局可调预算面积回收.pdf)。
- 历史预布局主稿及补充材料保留在 `../paper/zh/manuscript/`。
- 编译：`cd paper/zh/manuscript/`，**显式选目标** `lualatex -interaction=nonstopmode <n>.tex` ×2，再 `cp` 到 `paper/zh/`
- 质量门：`paper/zh/scripts/checks/latex_quality_gate.py` —— Errors / Overfull / Underfull 全 0
- **行尾**：`.tex` 与 `OPEN_ISSUES.md` **纯 LF**、`LOGS.md` **纯 CRLF**、`.sh` 由 `.gitattributes` 强制 LF；
  任何被跟踪文本文件都**不得含 `\r\r\n`**（`code/scripts/fix_crcrlf.py` 自查；r13 事故即 `\r\r\n` ⇒ 83 Errors）
- 英文工作稿暂冻。现行稿件路径和指纹见 [交接配置](../.codex-handoff.json)。

## 目录

| 目录 / 文件 | 角色 | 状态 |
|---|---|---|
| `HANDOFF_2026-11-25.md` | 交接入口（现状 / 复现 / 自检 / 后续规划） | **现行** |
| `HANDOFF_2026-11-23.md`、`HANDOFF_2026-11-09.md` | 交接快照 | 历史 |
| `CANON.md` | 唯一口径 | **现行** |
| `PROJECT_MAP.md` | 目录 / 版本 / 数据地图 | **现行** |
| `ARCHIVE_INDEX.md` | 归档去向 | **现行** |
| `LOGS.md` | 事实流水（只追加） | **现行** |
| `OPEN_ISSUES.md` | 未决容器 | **现行** |
| `WORK_PROGRESS.md` | 进度（倒序） | **停用**（停在 r93 / 2026-10-28，头有横幅） |
| `agent_handoff/` | 逐轮交接（41 份） | **停用**（全部止于 r30，只作溯源） |
| `evidence/` | 论文数字唯一来源（426 MB） | **禁动** |
| `reports/` | 实验报告 | 历史（CANON §5 引用其结论） |
| `review_history/` | 审稿历史 | 历史 |
| `design_specs/` | 设计规格 | 约束 `code/` |
| `planning/` | 仅存 V2 三份 + README | 半活 |
| `baselines/` | 具名基线 | 见交接与版本规范 |
| `archive/` | 退役 | 历史 |
| `migration/`、`worktrees/` | 迁移记录、工作树 | 历史 |

## 已停用（头部有横幅，打开即见）

`mainline.md`、`roadmap.md`、`milestones.md`、`long_term_task_plan.md`、`risk_register.md`、`RECORDS.md`、`decision_log.md`、`future_task_backlog.md`、`ARCHIVE_POLICY.md`、`FILE_ORGANIZATION.md`

## 历史去哪了

| 内容 | 位置 |
|---|---|
| 逐轮事实 | `LOGS.md` |
| 已完结轮次方案（13 份 + 7 月旧方案 2 份） | `archive/2026-10-28_superseded/planning_done/` |
| 被取代的状态/存储报告（4 份） | `archive/2026-10-28_superseded/reports/` |
| 互斥方案（2 份） | `archive/2026-10-28_superseded/plans/` |

---

分工：面向实现的技术文档在根 `docs/`；这里只放过程与治理。
