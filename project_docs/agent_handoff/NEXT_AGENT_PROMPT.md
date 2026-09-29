# NEXT AGENT PROMPT

> 给下一位 agent 的完整提示词。**每轮结束前更新**。最后更新：2026-09-29。

你是本仓库的新任执行者。请先按顺序阅读：

1. `AGENTS.md`（协作契约与规则）
2. `project_docs/agent_handoff/README.md`（阅读顺序）
3. `project_docs/agent_handoff/START_HERE.md`（当前状态与立即工作）
4. **`project_docs/agent_handoff/handoff_20260929.md`（本轮完整交接，最重要）**
5. `project_docs/agent_handoff/CURRENT_RUN_HANDOFF.md`（只读最上一节）
6. `project_docs/agent_handoff/TASK_BOARD.md`
7. `project_docs/OPEN_ISSUES.md`（未决问题必须知晓并如实告知用户）
8. `project_docs/evidence/PAPER_EVIDENCE_MANIFEST.md`（**动 `.tex` 前的强制门槛**，含逐数字绑定）
9. `project_docs/agent_handoff/DECISION_BRIEF_20260912.md`（三项待用户拍板的决策）

**当前状态（一句话）**：论文已进入**内容冻结**，**9 页 / 0 Error / 0 Overfull / 0 Underfull**，tag `faeco-paper-final-20260929`（提交 `a8142b6`）。用户已明确要求**停止论文内容修改**。

**本轮目标（按优先级）：**

1. 把用户对 **D-01（versions/v1 冻结方案）/ D-02（机制图处置）/ D-03（DOI/DRC 处置）** 的决策落地（执行清单见 `DECISION_BRIEF_20260912.md` 末尾），随后进入 **T20 投稿件打包**（目标期刊模板 + cover letter + 补充材料清单）。
2. 非论文事项：**1-C**（`planning/FAECO_V2_TECH_DESIGN_20260923.md` §12）未落地；`experiments/RESULTS.md` 待与论文新口径对齐（尤其 §4.2 族 A / 族 A\* 的 revision 声明）。
3. 若审稿意见返回：以 `project_docs/review_history/paper_audit/consistency_audit_20260911.md` 为数字基线，**并先读 `PAPER_EVIDENCE_MANIFEST.md`**，只处理新意见；**新增内容修改须先取得用户同意**。

**约束 / 不要做：**

- ❌ **不要继续修改论文内容**（用户指令）。任何新的内容改动须先问用户。
- ❌ 不要用 PDF 字节 SHA256 断言"内容一致"——用内容指纹 `pdftotext -layout <pdf> - | sha256sum`。
- ❌ 不要跨实验族拼数字。铁律 **`same claim ⇒ same revision + same config family`**；族 A（效率优先，revision 未完整钉定）与族 B（统一跨测试集）**严禁混用**。
- ❌ 不要缩字体/行距/砍内容来压页——**版面异常先查 `\FloatBarrier`**（双栏下会退化为 `\clearpage`）。
- `experiments/` 证据目录严禁删除；`paper/zh/figures/fig_iscas89.pdf` 是编译依赖，亦禁删。
- 未跑测试不修改 `code/src/rseco/`。
- 环境异常：pytest 报 import 错误先 `.venv\Scripts\python.exe -m pip install -e .`。

**完成标准（证据门）：**

- [ ] D-01~D-03 决策按简报执行完毕（或用户改选其他选项，按对应分支执行）；对应 OI 状态更新。
- [ ] 论文重新编译后仍为 **9 页 / 0 Error / 0 Overfull / 0 Underfull**，双副本 SHA256 一致，内容指纹记录进 `PAPER_EVIDENCE_MANIFEST.md` §6。
- [ ] T20 投稿包产出并经用户确认。
- [ ] 全套交接文档同步更新（`WORK_PROGRESS.md`、`status_logs/CURRENT_STATUS.md`、`TASK_BOARD.md`、`CURRENT_RUN_HANDOFF.md`、`START_HERE.md`、本文件、`LOGS.md`）并 commit。
