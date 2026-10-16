# 交接入口 — r22已恢复（2026-10-16）

用户明确“继续”，覆盖10-14暂停。最新完整七段交接：`CURRENT_RUN_HANDOFF.md` 与 `handoff_20261016_r22.md`。先读取当前修复/证据闭合任务，再按下方索引恢复上下文；旧暂停原件保留在 `handoff_20261014_r22.md`。

当前代码完整v5=835pass/166来源SHA稳定，正式9控制预期全符合（3正/3负/2unsupported/1input_error）；A6+B2真实新证明已补，B2在44d20bb绑定7/0孤立X identity及原bytes/模型/产物。OI038新缺证恢复、旧runtime身份不补造；B3/D/C、四态支持恢复与稿图仍待。proof/最终QA/docs准备阶段commit，记录员冻结写入；新C′v3尚未注册、无STA/pilot，v2仅注册禁执行。权威交接为 `agent_handoff/handoff_20261016_r22.md`（本目录是agent_handoff时用 `handoff_20261016_r22.md`）。

# Handoff Index

项目交接入口。**接手者按以下顺序阅读**，即可无口头交接重建上下文：

1. `../../AGENTS.md` — 协作契约与规则
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
- **每轮另留一份 `handoff_YYYYMMDD.md`**（同日多轮追加轮次后缀；当轮完整交接：做了什么、当前状态、如何验收、待办、不要做什么）。最近一份：`handoff_20261016_r22.md`（r22恢复推进）；`handoff_20261014_r22.md`保留暂停原件，`handoff_20261014.md`为r21。
- `skill_snapshots/`：项目技能快照（`skills/` 不可用时的回退）。
- `checklists/`：交接推送检查清单等。
- `guides/`：操作指南（git 工作流、构建流程等，按需建立）。
