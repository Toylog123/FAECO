# Current Run Handoff

> 最近一轮在最上，历史轮次原样保留在下。**新接手者只需读最上一节**。

## 2026-09-29（晚）决策轮 — D-01~D-03 落地 + RESULTS.md 对齐 + T20 启动

**本轮性质**：决策执行 + 文档对齐 + 投稿准备，**未动论文内容、未动代码**。

1. **四项用户拍板**：D-01=A 轻量冻结 / D-02=A 维持 3 图 / D-03=A（DOI 投稿时补、DRC 如实声明）/ T20 目标期刊 = **JCAD（计算机辅助设计与图形学学报）**。
2. **D-01 落地**：tag `v2026-09-29-submission-ready`（`d84061a`）+ `versions/v1/MANIFEST.sha256`（117 条，`sha256sum -c` 全 OK）+ `BASELINE_INDEX.csv` 首个 active 行；已 push（3 个本地论文 tag 一并上 origin）。**附带发现**：`20260826_aggregation/summary.json`（论文主数字源）等 3 个证据汇总文件此前未被 git 跟踪，现由 manifest 锁定（OI-022 待用户定是否 `git add`）。
3. **RESULTS.md 对齐**（rev. 2026-09-29）：实查修正 3 处 headline 错误——ISCAS89 中位 +0.14→**+0.10**、ITC-99 中位 +0.21→**+0.18** 且 success 19/19→**18/19 严格改善**、PicoRV32 中位 +0.05→**+0.60**；§3 b06 补 TNS 辅助接受事实（WNS 持平、TNS −3.97→−3.92、`--tns-aware` 批次、不计入严格统计 = 论文 §4.1 口径）。依据：`20260826_aggregation/summary.json` 复算 + b06 `outerloop_result.json` 实读。
4. **T20 投稿包**（`paper/zh/submission/`）：`JCAD_REQUIREMENTS_20260929.md`（要求核实报告，✔/⚠ 标注 + 官网来源）、官方《投稿模板（2026）.doc》副本、`T20_SUBMISSION_PACKAGE.md`（检查单 + 4 个决策点）、cover letter 草稿、补充材料清单（S1=OI-008 事件名映射为投稿前必办）、`draft_email_to_jcad.md`（询问 LaTeX PDF 可否评审）。**核心事实：JCAD 无官方 LaTeX 模板，投稿须 Word(.doc)+PDF、公式 MathType、2026 起另要求英文长摘要（3 页，修改阶段）与 AIGC 披露。**
5. **1-C 评估完毕**：代码语义已在 `search_state.py` 落地并过 0a 等价门；§12.2 论文文本已备、§12.4 前置 gate（OI-013/OI-014/3-A）全清。剩余唯一动作 = 插入 `.tex`，**属内容修改，与冻结令冲突** → 默认留修稿轮（OI-018），待用户拍板。

**待用户拍板**（`OPEN_ISSUES.md` OI-018~OI-022）：1-C 插入时机 / Word 转排路径 / 摘要改写授权 / AIGC 披露口径 / 3 个证据文件 git add。

**不要做**：论文内容修改仍冻结（含摘要）；未拍板不发询问邮件、不启动 Word 转排、不插入 1-C 小节。

---

## 2026-09-29 — 论文终稿收敛 + 仓库收敛 + 版面收尾

**详细交接见 [`handoff_20260929.md`](handoff_20260929.md)**（本轮主文档）。要点：

1. **论文内容冻结**。终稿审稿轮三批修改全部落地：评审 15 项中优先 7 项（`681841a`）、评审第二轮 10 项（`0ea80b6`）、必改 4 项（`a8142b6`）。**用户明确要求此后停止内容修改。**
2. **版面回到 9 页**（0 Error / 0 Overfull / 0 Underfull）。根因是 `placeins` 的 `\FloatBarrier` 在**双栏下遇待排浮动体退化为 `\clearpage`**；删掉 §3.4 表 3 之后那一处多余屏障即恢复 9 页（第 5 页 = 图 2 + 正文 + 表 3；第 9 页 = §5 + 全部 19 条参考文献）。
3. **仓库收敛**：删 81 个历史 `.tex`（3.0 MB，`eaec1f4`→`ff6ed96`）与 82 个历史 PDF（119.4 MB，`973b325`→`3a8d1a7`）；删前均先固化进 git，可回滚。`paper/` 下现只有**唯一主稿**。
4. **发布冻结**：tag `faeco-paper-final-20260929`（`a8142b6`）；PDF 字节 SHA256 `9af41d77…`；**内容指纹 `7adf0279…`**（判内容一致看这个，不看字节 SHA）。
5. **机械终检全过**：`??` = 0、无未定义引用、29 个 label 无重复、19 条 bibitem ↔ 19 个 cite 一一对应。遗留 6 个未被引用的 label（无可见影响，按"停止内容修改"未动）。

**下一手要做**：① 用户对 D-01/D-02/D-03 拍板（见 `DECISION_BRIEF_20260912.md`）→ 落地执行清单 → T20 投稿件打包；② 1-C（技术设计 §12）未落地；③ `experiments/RESULTS.md` 待与论文新口径对齐（**均非论文内容修改**）。

---

# 历史轮次：2026-09-12 交接收尾（**以下内容为历史快照，勿作为当前状态**）

## 1. 项目概览

FAECO：面向预布局门级时序 ECO 的失效驱动候选搜索（中文论文 + Python 工程 + 公开 benchmark 实验）。
工作区：`D:\BaiduSyncdisk\01_Papers\03_FAECO`（**唯一副本**，旧副本与 C 盘 worktree 已清理）；分支 main（与 origin 同步，HEAD f5b6380）；活跃基线待 D-01 决策后建立。

## 2. 本轮（2026-09-12 全天）做了什么

1. **上午**：robocopy 全量迁移仓库（316,765 文件 / 117.7 GB / 0 失败）→ 按 99_项目模板重组织（code/、project_docs/、data/raw/benchmarks/、scratch/、顶层契约）→ 路径修复（pyproject / 12+ 硬编码脚本 / 31 个测试文件锚点 / .gitignore / README / .codex-handoff）→ pytest 264 全绿（35fd558）。
2. **中午**：`.venv` 重建 + 依赖安装（再次 264 全绿）；C 盘 3 个 git worktree 删除（3 条 codex 分支先推送固化，2 份未提交 phase2 文档抢救至 `../archive/phase0_worktree_salvage_20260912/`）；旧目录全删（f5b6380）。
3. **下午**：三项待决策事项编写决策简报（`DECISION_BRIEF_20260912.md`，含事实核实——主稿无 DOI 占位符、当前 9 页稿仅 3 图）；刷新 OPEN_ISSUES / TASK_BOARD / 全套交接文档。

## 3. 证据门（本轮验收，全部通过）

- [x] git 历史完整、main 与 origin 同步、3 条 codex 分支固化
- [x] pytest 264 passed + 4 skipped（迁移前后基线一致）
- [x] check_project.sh PASS；live 文件旧绝对路径残扫 0
- [x] 论文未动（9 页审计闭环状态保持）

## 4. 下一步（下一次接手者）

1. **先读** `README.md` → `START_HERE.md` → `DECISION_BRIEF_20260912.md` → `../OPEN_ISSUES.md`。
2. 用户对 D-01（versions/v1 冻结，建议轻量 tag+manifest）、D-02（机制图，建议维持 3 图）、D-03（DOI/DRC，建议维持如实声明）拍板后执行简报末尾的执行清单。
3. 之后进入 T20：投稿件打包（目标期刊模板 + cover letter + 补充材料清单）。
4. 环境：如 pytest 报 import 错误，先 `.venv\Scripts\python.exe -m pip install -e .`。

## 5. 不要做

- `experiments/` 证据严禁删除（OI-004 的 cleanup-candidates 档位须用户逐项确认）。
- 论文改动前先跑测试 + 数字对账；新审稿意见走第 19 轮流程，以 `../review_history/paper_audit/consistency_audit_20260911.md` 为数字基线。
- 旧目录空壳 `D:\BaiduSyncdisk\03_FAECO` 由用户手动删除。

## 6. 增量：2026-09-14 交接整理

- 补齐上轮交接缺口：未提交的交接文档 + `DECISION_BRIEF_20260912.md` 统一 commit+push；`NEXT_AGENT_PROMPT.md` 空模板补全（阅读顺序 / 本轮目标 / 约束 / 证据门）；`.codex-handoff.json` 刷新（timestamp + read_order 补决策简报）。
- versions/v1/ 核查为模板占位（待 D-01 决策后冻结，无动作）。
- 环境复验：pytest 264 passed + 4 skipped。项目状态与第 2~4 节描述一致，无其他变更。
