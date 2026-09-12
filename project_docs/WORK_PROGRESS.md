# Work Progress

本文件按**倒序**记录每一轮工作（最新在上）。完整正序日志见 `LOGS.md`。

## 2026-09-12 框架架构迁移（99_项目模板 → 01_Papers/03_FAECO）

- **做了什么**：全量复制仓库（robocopy 316,765 文件 / 117.7 GB / 0 失败，git 历史与远程保留）；按模板重组织（code/、project_docs/、data/raw/benchmarks/、scratch/、顶层契约文件）；路径修复（pyproject、9 个硬编码脚本、5 处 benchmarks 引用）；重写 README；填写环境/术语/经验/未决/状态/交接文档。
- **关键结果**：映射全记录 `migration/MIGRATION_20260912.md`；证据门 = pytest 264 项全绿 + check_project.sh 通过 + 旧路径残扫清零。
- **提交**：本轮迁移单次语义提交。
- **下一步**：用户决策 OPEN_ISSUES OI-003（versions/v1 冻结方案）、OI-006（机制图拆分）。

## 2026-09-11 第 18 轮审稿修订 + 全文一致性审计

- **做了什么**：接手中断会话的第 18 轮未提交修订（SEC 口径细分、b17 预算披露、benchmark 纳入规则、tab:configs、SPEF 公式、F6 降强），修正其引入的幽灵引用/重复段落/配置表事实错误；随后全文数字对账，修复 8 处正文与实验产物的矛盾。
- **关键结果**：论文 9 页、0 Error / 0 Overfull / 0 未定义引用；审计记录 `review_history/paper_audit/consistency_audit_20260911.md`；工作日志 LOG-20260911-01/02。
- **提交**：3d984c6（第 18 轮）、7d42152（旧名 PDF 清理）、d329f19（一致性审计），均已推送。

## 2026-09-08 ~ 09-09 实验补齐与结果汇总（摘要）

- b17 phase-2 重跑（+0.38 ns / 104 STA / SEC 12812+1 unproven）；joint-depth 消融（depth4 +0.43）；hold-mode ITC-99（诚实 limitation）；multi-iter ablation 与 --no-early-stop 修复；`experiments/RESULTS.md` + `results.json` 顶层汇总。
- 详见 `LOGS.md` 2026-09-08/09 段（LOG-20260908-01..15、LOG-20260909-01）。

（2026-08-11 ~ 08-13 的 17 轮命名版审稿史、2026-08-26 unified-loop 主实验、更早 N31 系列见 `LOGS.md` 与 `review_history/paper_audit/`。）
