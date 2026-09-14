# NEXT AGENT PROMPT

> 给下一位 agent 的完整提示词。**每轮结束前更新**。

你是本仓库的新任执行者。请先按顺序阅读：

1. `AGENTS.md`
2. `project_docs/agent_handoff/README.md`
3. `project_docs/agent_handoff/START_HERE.md`
4. `project_docs/agent_handoff/status_logs/CURRENT_STATUS.md`
5. `project_docs/agent_handoff/DECISION_BRIEF_20260912.md`（三项待用户拍板的决策，含建议项）
6. `project_docs/agent_handoff/TASK_BOARD.md`
7. `project_docs/agent_handoff/CURRENT_RUN_HANDOFF.md`
8. `project_docs/OPEN_ISSUES.md`（未决问题必须知晓并如实告知用户）
9. `project_docs/baselines/BASELINE_INDEX.csv`（当前仅模板行——真实基线待 D-01 建立后登记）

**本轮目标：** 把用户对 D-01（versions/v1 冻结方案）/ D-02（机制图处置）/ D-03（DOI/DRC 处置）的决策落地（执行清单见 DECISION_BRIEF_20260912.md 末尾），随后进入 T20 投稿件打包（目标期刊模板 + cover letter + 补充材料清单）。

**约束 / 不要做：**

- `experiments/` 证据目录严禁删除；历史产物内旧绝对路径不改写（OI-004 cleanup-candidates 档位须用户逐项确认）。
- 论文数字只认 `experiments/20260826_aggregation/summary.json` 及对应产物；改动前先跑测试 + 数字对账（`docs/GLOSSARY.md` 关键口径）。
- 未跑测试不修改 `code/src/rseco/`。
- 审稿返回走第 19 轮：以 `project_docs/review_history/paper_audit/consistency_audit_20260911.md` 为数字基线，仅处理新意见。
- 旧目录空壳 `D:\BaiduSyncdisk\03_FAECO` 由用户手动删除（会话句柄释放后）。
- 环境异常时：pytest 报 import 错误先 `.venv\Scripts\python.exe -m pip install -e .`。

**完成标准（证据门）：**

- [ ] D-01~D-03 决策按简报执行完毕（或用户改选其他选项，按对应分支执行）；对应 OI 状态更新。
- [ ] 若 D-01=A：`git tag v2026-09-12-submission-ready && git push --tags` + manifest 落 `versions/v1/`，BASELINE_INDEX.csv 登记真实条目。
- [ ] T20 投稿包产出并经用户确认。
- [ ] 全套交接文档同步更新（`WORK_PROGRESS.md`、`status_logs/CURRENT_STATUS.md`、`TASK_BOARD.md`、`CURRENT_RUN_HANDOFF.md`、本文件、`LOGS.md`）并 commit + push。
