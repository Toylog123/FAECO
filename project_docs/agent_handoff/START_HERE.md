# START HERE

接手者入口。**阅读顺序见根目录 `README.md` 与 `.codex-handoff.json` 的 read_order**。本文件描述"当前"状态，需每轮更新。

## 当前工作区

- 项目：FAECO — 面向预布局门级时序 ECO 的失效驱动候选搜索
- 仓库：`D:\BaiduSyncdisk\01_Papers\03_FAECO`
- 分支：main（remote: https://github.com/Toylog123/FAECO.git；迁移提交 38051c6 待推送——github 间歇不可达，网络恢复后 push）
- 当前 HEAD：d329f19（一致性审计，迁移前最后提交；迁移以单次语义提交落盘）
- 活跃基线：尚未建立（见 `../baselines/`，冻结方案待用户决策 = OPEN_ISSUES OI-003）
- 主稿件：`paper/zh/manuscript/FAECO_面向预布局门级时序ECO的失效驱动候选搜索.tex`（9 页）
- 实验入口：`experiments/INVENTORY.md`（总索引）、`experiments/RESULTS.md`（顶层汇总）

**版本定义**：代码/论文版本由具名基线决定；工作树名、运行目录名不定义版本。

## 立即工作

1. 迁移后首跑验证：`python -m pytest code/tests -q`（264 项）+ `bash code/scripts/check_project.sh`；若 import 失败先 `pip install -e .`（`.venv` 旧绝对路径已失效）。
2. 处理 OPEN_ISSUES 中等待用户决策的三项：OI-003（versions/v1 冻结）、OI-006（机制图拆分）、OI-001/002（投稿前 DOI / DRC）。
3. 如有新审稿意见：走第 19 轮流程（改动前先数字对账，规则见 `../../GLOSSARY.md` 关键口径）。

## 不要做什么

- 不要删除旧目录 `D:\BaiduSyncdisk\03_FAECO`（迁移源归档，用户处置，OI-005）。
- 不要改写 `experiments/` 历史产物（含其中记录的旧绝对路径——证据记录）。
- 不要把旧轮次的数据拼进新结论；论文数字只认 `experiments/20260826_aggregation/summary.json` 及对应产物。
- 不要在未跑测试的情况下修改 `code/src/rseco/`。

## 证据边界

- 论文主结果 = 20260826 统一批量口径（含 b17 phase-2 180 s 预算例外，唯一例外已披露）；§4.2 效率优先与 §4.4 消融是不同配置的独立实验，数字不互混。
- "WNS 严格改善"不等同于 timing closure；0.5 ns 为 stress-test 约束口径。
- SEC：30 实例中 29 个产生网表修改、28/29 完全证明；b17 剩 1 个未证明点（Liberty 同函数）单独报告；无 DRC signoff（如实声明）。
- P&R 验证为 OpenROAD 布局 + 全局布线寄生**估计**，非流片实测。
