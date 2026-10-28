# 交接入口 — r27黑白灰完整工作稿已交付（2026-10-19/LOG258）

当前状态（2026-10-19/LOG258）：r27完整中文主文/补充黑白灰工作稿已交付；main1d3b94f4/9d0394e8为10页7图6表8554CJK/14refs，补9886b68a/27ac11ab为9页5图12表9632CJK。内置模型两示意图+7量化图、双遍编译/DeviceGray19页严格灰度/根全页视觉/各3PDF同步均完成，FINAL_DELIVERY10701c76。科学正文仅图路径和两色词变化；AI原生RGB细差/字体提示/序列化微差明记。无新EDA/production/HEAD改动，四partial/D正式28/56raw3/8/OI051与HEADf761两门锁保持，不提交。

r23历史完成状态（2026-10-18/LOG149）：r23中文只读全审完成，Major Revision，20意见/22路线图（8 must_fix、14 should_fix）；报告`paper/zh/review_rounds/r23_20261018/REVIEW_REPORT.md`及root crosscheck/最终SHA回执齐。五席十阶段及机械合成PASS≠科学全部通过，模型家族/provider身份未知，不称独立专家验证。Integration既有目标保留，本轮仅无正式criteria绑定。正文/图件/代码/HEADf761不变，无新EDA。D producer56已完成但accepted28/raw3，56+8post两门齐前不提交。下一轮按路线图与现有证据修订，不能重复证明A8/b17或跨族补旧科学结论。

A8限定修订已接受（LOG120）：proof/双语句表、EN包含布局/38页视觉、当前PDF与四metadata同步获独立+根472b441b接受；OI050此门closed，ZH173ae809…/ENc2783046…为A8当轮身份；当前ZH以顶部本轮状态与CURRENT_STATUS为准，EN未本轮更新，未完成其它科学/作者投稿门。D诊断caption v2已根接受，仍仅预览。

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
- **每轮另留一份 `handoff_YYYYMMDD.md`**（同日多轮追加轮次后缀；当轮完整交接：做了什么、当前状态、如何验收、待办、不要做什么）。最近一份：`handoff_20261019_r27.md`（配色统一）；上一轮`handoff_20261018_r26.md`（完整论文/示意图）；上一轮`handoff_20261018_r25.md`（中文稿压缩/主线）；上一轮`handoff_20261018_r24.md`（修订交付）；上一轮`handoff_20261018_r23.md`（中文只读审稿）；上一轮`handoff_20261018_r22.md`（10-18继续推进）；`handoff_20261016_r22.md`（r22恢复推进）；`handoff_20261014_r22.md`保留暂停原件，`handoff_20261014.md`为r21。
- `skill_snapshots/`：项目技能快照（`skills/` 不可用时的回退）。
- `checklists/`：交接推送检查清单等。
- `guides/`：操作指南（git 工作流、构建流程等，按需建立）。

当前双稿入口：主文TeX paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex 与补充TeX paper/zh/manuscript/FAECO_补充材料.tex；在manuscript目录显式选目标分别LuaLaTeX双遍；当前PDF均在paper/zh/build/。完整身份/边界见CURRENT_STATUS与r27 FINAL_DELIVERY；重建须接DeviceGray导出/QA，见当前round的DELIVERY_AND_REPRODUCE.md。
