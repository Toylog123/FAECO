# START HERE

接手者入口。**阅读顺序见 `README.md`**。本文件描述"当前"状态，需每轮更新。

## 当前工作区

- 项目：FAECO — 面向预布局门级时序 ECO 的结构化候选搜索与失效归因
- 仓库：`D:\BaiduSyncdisk\01_Papers\03_FAECO`（唯一工作副本）
- 分支：main，HEAD **`a8142b6`**；remote: https://github.com/Toylog123/FAECO.git
- 主稿件（**唯一 `.tex`，历史副本已清空**）：
  `paper/zh/manuscript/FAECO_面向预布局门级时序ECO的结构化候选搜索与失效归因.tex`
  **9 页 / 0 Error / 0 Overfull / 0 Underfull**；tag `faeco-paper-final-20260929`
- 实验入口：`experiments/INVENTORY.md`（目录总索引）、`experiments/RESULTS.md`（权威汇总，**待与论文新口径对齐**）
- 环境：`.venv`（Python 3.11.9）；测试 `python -m pytest code/tests -q` → 264 passed + 4 skipped

**版本定义**：代码/论文版本由具名基线（tag）决定；工作树名、运行目录名不定义版本。

## 立即工作

1. **读 `handoff_20260929.md`** —— 本轮（论文终稿收敛 + 仓库收敛 + 版面修复）的完整交接。
2. **等用户对 D-01 / D-02 / D-03 拍板**——见 `DECISION_BRIEF_20260912.md`；选定后按简报末尾执行清单落地，随后进入 T20 投稿件打包。
3. 论文侧：**内容修改已停止**（用户指令）。若审稿意见返回，以 `../review_history/paper_audit/consistency_audit_20260911.md` 为数字基线，**并先读 `../evidence/PAPER_EVIDENCE_MANIFEST.md`**。

## 不要做什么

- **不要继续修改论文内容**——用户已要求"做完 4 项必改即停止"。
- `experiments/` 证据目录严禁删除；`paper/zh/figures/fig_iscas89.pdf` 是编译依赖，亦禁删。
- 论文数字只认 `experiments/20260826_aggregation/summary.json` 及对应产物；改动前先跑测试 + 数字对账（`docs/GLOSSARY.md` 关键口径）。
- 未跑测试不修改 `code/src/rseco/`。
- 压页/版面异常**先查 `\FloatBarrier`**，不要缩字体、行距或砍内容。

## 证据边界

- 论文主结果 = 20260826 统一批量口径（族 B；b17 phase-2 180 s 预算例外已披露）；§4.2 效率优先子研究（族 A，**revision 未完整钉定**）与 §4.4 消融（族 C/D）、§4.6 S 能力边界（族 F）是**各自独立配置，数字严禁互混**。
- 铁律：**`same claim ⇒ same revision + same config family`**。
- §4.1 已声明：**以 WNS 严格改善为主要统计口径**；b06 的 TNS 辅助接受单独声明、不计入「严格 WNS 改善」统计。
- "WNS 严格改善"不等同于 timing closure；0.5 ns 为 stress-test 约束，非目标工作频率。
- SEC：30 实例 29 修改、28/29 完全证明；b17 剩 1 个未证明点（Liberty 同函数）单独报告。
- P&R 验证为 OpenROAD 布局 + 全局布线寄生**估计**；无 DRC signoff（如实声明）。

## 构建与验收（论文）

见 `handoff_20260929.md` §3：`cd paper/zh/manuscript` → `lualatex` ×2 → 质量门 → 双副本 `cp` + SHA256 核对 → 内容指纹（`pdftotext -layout … | sha256sum`）。
