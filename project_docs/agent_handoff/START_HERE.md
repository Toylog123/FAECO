# START HERE

接手者入口。**阅读顺序见 `README.md`**。本文件描述"当前"状态，需每轮更新。

## 当前工作区

- 项目：FAECO — 面向预布局门级时序 ECO 的结构化候选搜索与失效归因
- 仓库：`D:\BaiduSyncdisk\01_Papers\03_FAECO`（唯一工作副本）
- 分支：main，HEAD **`26f4f3b`**（+ 文档同步提交 `5bc0e7d`）；remote: https://github.com/Toylog123/FAECO.git
- 主稿件（唯一 `.tex`，**内容冻结 v3，修改已终止**）：
  `paper/zh/manuscript/FAECO_面向预布局门级时序ECO的结构化候选搜索与失效归因.tex`
  **9 页 / 0 Error / 0 Overfull / 0 Underfull**；内容指纹 `70bbd610…`（poppler 25.07）
- 基线 tag：**`v2026-09-30-submission-ready-r2`**（= `26f4f3b`，四元绑定 manifest `versions/v3/MANIFEST.sha256`，117 条）；
  论文发布 tag `faeco-paper-final-20260930-r2`（= `26f4f3b`）；实验 revision tag `faeco-exp-rev1`（= `87d01ba`）
- 投稿目标期刊：**JCAD（计算机辅助设计与图形学学报）**；投稿包：`paper/zh/submission/`
- 实验入口：`experiments/INVENTORY.md`、`experiments/RESULTS.md`（rev. 2026-09-29 已对齐论文口径）
- 环境：`.venv`（Python 3.11.9）；pytest import 报错先 `.venv\Scripts\python.exe -m pip install -e .`

**版本定义**：代码/论文版本由具名基线（tag）决定；工作树名、运行目录名不定义版本。

## 立即工作

1. **读 `CURRENT_RUN_HANDOFF.md` 最上一节**（2026-09-30 傍晚 终审修正轮）——论文内容**已按用户指令终止修改**，冻结 v3（`26f4f3b`）；OI-018~OI-022 已全部拍板完毕。
2. **投稿剩余动作均为手工 / 流程项**（非论文内容，见 `paper/zh/submission/T20_SUBMISSION_PACKAGE.md`）：
   - 用户本机（Word 稿，清单 `word/转排说明.md`）：MathType 批量转换（OMML→MathType）、黄色占位替换（通信作者 */基金/日期/作者简介）、图 2 通栏、终稿 PDF 导出；
   - 技术待办：检查单 #3 参考文献核对（GB/T 7714 + 中文文献须中英文对照著录）；
   - ⚠ 硬项：**OI-021 AIGC 使用披露**（JCAD 2026 硬要求，未披露视为抄袭）；作者承诺书 + 单位工作邮箱；保密审查证明；英文长摘要（3 页，随修改稿）。
3. 若审稿意见返回：以 `../review_history/paper_audit/consistency_audit_20260911.md` 为数字基线，**先读 `../evidence/PAPER_EVIDENCE_MANIFEST.md`**，只处理新意见；新增内容修改须先取得用户同意（**1-C 插入亦留修稿轮**，OI-018）。

## 不要做什么

- **不要修改论文内容**（用户冻结令仍有效）——含摘要；Word 转排稿中的摘要改写也须先获授权（OI-020）。
- `experiments/` 证据目录严禁删除；`paper/zh/figures/fig_iscas89.pdf` 是编译依赖，亦禁删。
- 论文数字只认 `experiments/20260826_aggregation/summary.json` 及对应产物；引用任何数字前**实查证据文件**。
- 未跑测试不修改 `code/src/rseco/`。
- 压页/版面异常**先查 `\FloatBarrier`**，不要缩字体、行距或砍内容。
- 未拍板前**不要**发送 `draft_email_to_jcad.md`、**不要**启动 Word 转排、**不要**插入 1-C 小节。

## 证据边界

- 论文主结果 = 20260826 统一批量口径（族 B；b17 phase-2 180 s 预算例外已披露）；§4.2 效率优先子研究（族 A，**revision 未完整钉定**）与 §4.4 消融（族 C/D）、§4.6 S 能力边界（族 F）是**各自独立配置，数字严禁互混**。
- 铁律：**`same claim ⇒ same revision + same config family`**；逐数字绑定见 `../evidence/PAPER_EVIDENCE_MANIFEST.md`。
- §4.1 已声明：**以 WNS 严格改善为主要统计口径**（ITC-99 = **18/19**，b06 的 TNS 辅助接受单独声明、不计入）；"WNS 严格改善"≠ timing closure；0.5 ns 为 stress-test 约束。
- SEC：30 实例 29 修改、28/29 完全证明；b17 剩 1 个未证明点（Liberty 同函数）单独报告。
- P&R 验证为 OpenROAD 布局 + 全局布线寄生**估计**；无 DRC signoff（如实声明，D-03=A）。

## 构建与验收（论文）

见 `handoff_20260929.md` §3：`cd paper/zh/manuscript` → `lualatex` ×2 → 质量门 → 双副本 `cp` + SHA256 核对 → 内容指纹（`pdftotext -layout … | sha256sum`）。
