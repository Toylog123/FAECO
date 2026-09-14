# START HERE

接手者入口。**阅读顺序见根目录 `README.md` 与 `.codex-handoff.json` 的 read_order**。本文件描述"当前"状态，需每轮更新。

## 当前工作区

- 项目：FAECO — 面向预布局门级时序 ECO 的失效驱动候选搜索
- 仓库：`D:\BaiduSyncdisk\01_Papers\03_FAECO`（唯一工作副本；旧副本与 C 盘 worktree 已清理，见 LOG-20260912-02）
- 分支：main（与 origin/main 同步，HEAD f5b6380；remote: https://github.com/Toylog123/FAECO.git；另有 3 条 codex 历史分支已推送固化）
- 活跃基线：待用户 D-01 决策后建立（建议方案：tag `v2026-09-12-submission-ready` + manifest 入 `versions/v1/`）
- 主稿件：`paper/zh/manuscript/FAECO_面向预布局门级时序ECO的失效驱动候选搜索.tex`（9 页，18 轮审稿 + 一致性审计闭环，可投稿前状态）
- 实验入口：`experiments/INVENTORY.md`（122 目录总索引）、`experiments/RESULTS.md`（权威汇总）
- 环境：`.venv` 已就绪（Python 3.11.9 + 依赖）；测试 `python -m pytest code/tests -q` → 264 passed + 4 skipped

**版本定义**：代码/论文版本由具名基线决定；工作树名、运行目录名不定义版本。

## 立即工作

1. **等用户对 D-01 / D-02 / D-03 拍板**——先读 `DECISION_BRIEF_20260912.md`（每项有事实、选项、成本与建议），把简报呈给用户；选定后按简报末尾执行清单落地。
2. 之后进入 T20：投稿件打包（目标期刊模板 + cover letter + 补充材料清单）。
3. 审稿返回走第 19 轮：以 `../review_history/paper_audit/consistency_audit_20260911.md` 为数字基线，仅处理新意见。

## 不要做什么

- `experiments/` 证据目录严禁删除；历史产物内旧绝对路径不改写。
- 论文数字只认 `experiments/20260826_aggregation/summary.json` 及对应产物；改动前先跑测试 + 数字对账（`docs/GLOSSARY.md` 关键口径）。
- 未跑测试不修改 `code/src/rseco/`。
- 旧目录空壳 `D:\BaiduSyncdisk\03_FAECO` 由用户手动删除（本会话句柄释放后）。

## 证据边界

- 论文主结果 = 20260826 统一批量口径（b17 phase-2 180 s 预算例外已披露）；§4.2 效率优先与 §4.4 消融是独立配置，数字不互混。
- "WNS 严格改善"不等同于 timing closure；0.5 ns 为 stress-test 约束。
- SEC：30 实例 29 修改、28/29 完全证明；b17 剩 1 个未证明点（Liberty 同函数）单独报告。
- P&R 验证为 OpenROAD 布局 + 全局布线寄生**估计**；无 DRC signoff（如实声明，补跑需 Magic/KLayout，按需）。
