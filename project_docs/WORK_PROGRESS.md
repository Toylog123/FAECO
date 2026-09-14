# Work Progress

本文件按**倒序**记录每一轮工作（最新在上）。完整正序日志见 `LOGS.md`。

## 2026-09-14 交接整理收尾

- **做了什么**：核查交接文档体系，发现并补齐三处缺口：上轮交接文档变更未提交（本轮 commit+push）、`NEXT_AGENT_PROMPT.md` 为空模板（已补全：目标=D-01~D-03 落地 + T20、约束、证据门）、`.codex-handoff.json` 时间戳过期（已刷新，read_order 补入决策简报）；核查 versions/v1/ 为模板占位（与待 D-01 决策一致）。
- **关键结果**：pytest 264 passed + 4 skipped（环境验证通过）；全套交接文档提交推送，仓库随时可无口头交接。
- **下一步**：不变——用户拍板 D-01~D-03 → 执行决策 → T20 投稿件打包。

## 2026-09-12（下午）决策简报 + 交接收尾

- **做了什么**：为 OPEN_ISSUES 中三项待决策事项（versions/v1 冻结、机制图、DOI/DRC）核实最新事实并编写决策简报 `agent_handoff/DECISION_BRIEF_20260912.md`；刷新 OPEN_ISSUES（OI-001 降级：主稿无 DOI 占位符；OI-006 重定义：当前 9 页稿仅 3 图，原拆分问题已消失；新增 OI-007 hold limitation 记录）与 TASK_BOARD（U26-06/U26-08 关闭、U26-07 部分完成、新增 D-01~D-03 决策项与 T20 投稿打包任务）；重建全套交接文档。
- **关键结果**：三项决策均有明确建议（轻量冻结 / 维持 3 图 / 维持如实声明+按需 rebuttal），用户拍板后下一轮即可执行。
- **下一步**：用户读简报做 D-01~D-03 决策 → 执行（tag+manifest / 无动作 / 关闭对应 OI）→ T20 投稿件打包。

## 2026-09-12 框架架构迁移 + 环境重建 + 旧副本清理

- **做了什么**：robocopy 全量复制仓库（316,765 文件 / 117.7 GB / 0 失败）至 `D:\BaiduSyncdisk\01_Papers\03_FAECO`，git 历史与远程保留；按 99_项目模板重组织（code/、project_docs/、data/raw/benchmarks/、scratch/、顶层契约）；路径修复（pyproject、12+ 硬编码脚本、19+12 测试锚点）；交接文档重建。随后 `.venv` 用 Python 3.11.9 重建并装依赖；C 盘 3 个 git worktree 删除（分支先推送固化、未提交文档抢救归档）；旧目录全删。
- **关键结果**：pytest 264 passed + 4 skipped 全绿；check_project.sh PASS；live 文件旧路径残扫 0；main 与 origin 同步（35fd558 → f5b6380）。
- **映射全记录**：`migration/MIGRATION_20260912.md`。

## 2026-09-11 第 18 轮审稿修订 + 全文一致性审计

- **第 18 轮**（3d984c6）：接手中断会话的未提交修订（SEC 口径细分、b17 预算披露、benchmark 纳入规则、tab:configs、SPEF 公式、F6 降强），修正幽灵引用/重复段落/配置表事实错误；排版债清零（0 Overfull，9 页）。
- **一致性审计**（d329f19）：修复 8 处正文与实验产物的矛盾（策略分布、b21 +2.75、3363 次 STA、b06 声明、b18/b19 归属、SEC 计数 5 处口径、随机种子、pcpi_mul +0.07）；审计记录 `review_history/paper_audit/consistency_audit_20260911.md`。

## 2026-09-08 ~ 09-09 实验补齐与结果汇总（摘要）

b17 phase-2 重跑（+0.38 ns / 104 STA / SEC 12812+1 unproven）；joint-depth 消融；hold-mode ITC-99（诚实 limitation）；multi-iter ablation 与 --no-early-stop 修复；`experiments/RESULTS.md` + `results.json` 顶层汇总。详见 `LOGS.md`。

（2026-08-11 ~ 08-13 的 17 轮命名版审稿史、2026-08-26 unified-loop 主实验、更早 N31 系列见 `LOGS.md` 与 `review_history/paper_audit/`。）
