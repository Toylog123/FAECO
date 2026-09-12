# Handoff Index

项目交接入口。**接手者按以下顺序阅读**，即可无口头交接重建上下文：

1. `../AGENTS.md` — 协作契约与规则
2. `README.md` — 本文件（阅读顺序）
3. `START_HERE.md` — 当前工作区与立即工作
4. `status_logs/CURRENT_STATUS.md` — 最近一轮状态
5. `TASK_BOARD.md` — 任务看板：每步任务与证据门
6. `CURRENT_RUN_HANDOFF.md` — 本轮详细交接
7. `NEXT_AGENT_PROMPT.md` — 给下一位 agent 的提示词
8. `../baselines/` — 具名基线（先读 `BASELINE_INDEX.csv`）
9. `../evidence/` — 按需查证证据
10. `../../docs/environment.md` — 环境与依赖清单（复现环境）

## 规则

- **每轮结束必须更新**本索引指向的文件，保证接手者可随时直接上手。
- `skill_snapshots/`：项目技能快照（`skills/` 不可用时的回退）。
- `checklists/`：交接推送检查清单等。
- `guides/`：操作指南（git 工作流、构建流程等，按需建立）。
