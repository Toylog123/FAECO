# 交接入口 — r23中文稿只读审稿（2026-10-18/LOG139）

当前执行（2026-10-18/LOG139）：用户新指令“审稿中文稿”，r23全稿只读审稿，输入2d76968c…/领域角色fcd0e2e2…与contract QA1a3651b0…已实际注册，五same-family新forknone席先盲标准再看稿，NOT_CALIBRATED/目标期刊未确认；最终报告未齐。HEAD/codef761不变，不改稿图/源或新EDA。D仅producer56/56完成（remaining106a6234…/monitor30098530…，active-failed空），正式accepted28/raw3，56+全部8包post两门未齐前仍锁不commit。本轮不启动D终验归档/修源。新交接handoff_20261018_r23.md，旧r22交接保原件。

A8限定修订已接受（LOG120）：proof/双语句表、EN包含布局/38页视觉、当前PDF与四metadata同步获独立+根472b441b接受；OI050此门closed，ZH173ae809…/ENc2783046…为当前工作稿，未完成其它科学/作者投稿门。D诊断caption v2已根接受，仍仅预览。

D计时环境（LOG110）：科学STA并发≤2电路；期间另有mock QA、7z压缩恢复、串行A8 SEC与TeX/Poppler，整机非独占benchmark。输入/结果/actualSTA计数不变，observed walltime不直接用于独占或跨方法速度因果。

按以下顺序读取，当前事实以CURRENT_RUN_HANDOFF与CURRENT_STATUS顶部为准，历史区不作为待办。

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
- **每轮另留一份 `handoff_YYYYMMDD.md`**（同日多轮追加轮次后缀；当轮完整交接：做了什么、当前状态、如何验收、待办、不要做什么）。最近一份：`handoff_20261018_r23.md`（中文只读审稿）；上一轮`handoff_20261018_r22.md`（10-18继续推进）；`handoff_20261016_r22.md`（r22恢复推进）；`handoff_20261014_r22.md`保留暂停原件，`handoff_20261014.md`为r21。
- `skill_snapshots/`：项目技能快照（`skills/` 不可用时的回退）。
- `checklists/`：交接推送检查清单等。
- `guides/`：操作指南（git 工作流、构建流程等，按需建立）。
