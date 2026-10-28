# project_docs 入口

> **本目录只有 5 个现行文件，其余全为历史。** 历史不是删掉了，是归档了——见 `ARCHIVE_INDEX.md`。

## 必读（按序，读完这三个就够）

1. **`CANON.md`** —— 唯一现行口径：论文定版、8 条声称的强度裁决、冻结数字、待决项、已否决路线。
2. **`PROJECT_MAP.md`** —— 目录职责、版本三层对应、数据资产归属、6 条结构性坑。
3. **`LOGS.md`**（事实流水，只追加）/ **`OPEN_ISSUES.md`**（未决容器）。

`ARCHIVE_INDEX.md` 记录所有归档去向，含「这份为什么不见了」。

## 一句话现状

论文 **r28（2026-10-19）交付后一字未动**：主稿 **10 页**、补充 **9 页**、CJK **8554**、`\bibitem` **14**、**7 图 6 表**。
`.tex` SHA256 前缀 `f0f4d5e0`、主稿 PDF `e71feb3d`（双副本一致）。
扩面族 1393 候选 × 三档物理标签**尚未进论文**（三份 `.tex` 里 0 命中）。
最大问题：判据门槛 `Δ_WNS > 0` **低于自己的判定带 0.049752 ns 约 5 倍**。

## 论文入口

- 主稿：`../paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex`
- 补充：`../paper/zh/manuscript/FAECO_补充材料.tex`
- PDF：`../paper/zh/build/`（两处副本 SHA 须一致）
- 编译：`cd paper/zh/manuscript/`，**显式选目标** `lualatex -interaction=nonstopmode <n>.tex` ×2，再 `cp` 到 `paper/zh/`
- 质量门：`paper/zh/scripts/checks/latex_quality_gate.py` —— Errors / Overfull / Underfull 全 0
- **`.tex` 必须纯 CRLF**，并断言 `count(b"\r\r\n")==0`（r13 事故：`\r\r\n` ⇒ 83 Errors）

## 目录

| 目录 / 文件 | 角色 | 状态 |
|---|---|---|
| `CANON.md` | 唯一口径 | **现行** |
| `PROJECT_MAP.md` | 目录 / 版本 / 数据地图 | **现行** |
| `ARCHIVE_INDEX.md` | 归档去向 | **现行** |
| `LOGS.md` | 事实流水（只追加） | **现行** |
| `OPEN_ISSUES.md` | 未决容器 | **现行** |
| `WORK_PROGRESS.md` | 进度（倒序） | 活跃 |
| `agent_handoff/` | 逐轮交接（41 份） | **只读最近一份** + 其 README |
| `evidence/` | 论文数字唯一来源（426 MB） | **禁动** |
| `reports/` | 实验报告 | 历史（CANON §5 引用其结论） |
| `review_history/` | 审稿历史 | 历史 |
| `design_specs/` | 设计规格 | 约束 `code/` |
| `planning/` | 仅存 V2 三份 + README | 半活 |
| `baselines/` | 具名基线 | 活跃（`active` = v19 / r28） |
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
