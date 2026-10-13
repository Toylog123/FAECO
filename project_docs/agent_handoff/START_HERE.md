# START HERE

接手者入口。**阅读顺序见 `README.md`**。本文件描述"当前"状态，需每轮更新。

## 当前工作区

- 项目：FAECO — 面向预布局门级时序 ECO 的候选探索与失效刻画
- 仓库：`D:\BaiduSyncdisk\01_Papers\03_FAECO`（唯一工作副本）
- 分支：main（**与 `origin/main` 同步**）；**v10 冻结终态 = 本轮收口提交**（r12 一致性 pass；前置 v9 终态 = `e00315a`，链路 `daba5ab` → `da61cdf` → `e00315a`）；remote: https://github.com/Toylog123/FAECO.git（**已推送**）
- 主稿件（唯一 `.tex`，**内容冻结 v10，内容改动留投稿/修稿轮**）：
  `paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex`
  **10 页 / 0 Error / 0 Overfull / 0 Underfull / 0 Overfull vbox**；内容指纹 `c7b4d807…`（poppler 25.07）
- 基线 tag：**`v2026-10-12-pre-submission-consistency-r12`**（四元绑定 manifest `versions/v10/MANIFEST.sha256`，117 条）；
  论文发布 tag `faeco-paper-final-20261013`；前置 v9 = `v2026-10-12-submission-polish-r11` / `faeco-paper-final-20261012c`（= `e00315a`）；实验 revision tag `faeco-exp-rev1`（= `87d01ba`）
- 投稿目标期刊：**Integration, the VLSI Journal**（Elsevier；由 JCAD 改投，OI-028）；旧投稿包 `paper/zh/submission/`（T20/JCAD 版，作历史参考）
- 实验入口：`experiments/INVENTORY.md`、`experiments/RESULTS.md`（rev. 2026-09-29 已对齐论文口径）
- 环境：`.venv`（Python 3.11.9）；pytest import 报错先 `.venv\Scripts\python.exe -m pip install -e .`

**版本定义**：代码/论文版本由具名基线（tag）决定；工作树名、运行目录名不定义版本。

## 立即工作

1. **读 `CURRENT_RUN_HANDOFF.md` 最上一节**（2026-10-13 投稿前一致性 pass r12）：r12 = 用户粘贴的**第五份外部审稿**（「投稿前最后一轮审稿人视角」）的 **M1–M5 全量落地**，用户裁定 **「不要再加实验」**。**五项**：M1 表 5 SEC `19/19`→`18/19` + 表注；M2 PicoRV32 `2/3`→`2/2` + 分母解释（5 处）；M3 表 11 表注补「**两个 STA 计数口径不同**」（预约计数 ≤500/电路 vs 论文口径合计 4146，数字无需更正）；M4 贡献 1 弱化 `1.07 ns`↔加权割绑定；M5 §3.4 + 表 4 措辞降调；另 §4.4 开头补「不单独隔离式 (2)」句。**均零数字/零实验/零代码**。重冻结 **v10**。
2. **当前最高优先 = OI-028：投 Integration, the VLSI Journal**——需**英文稿 + `elsarticle` 格式 + 投稿材料**（cover letter / highlights ≤85 字符 / graphical abstract）；中文稿作内容母本；AIGC 披露改按 **Elsevier** 政策复核（OI-021）。
3. **已暂缓（用户裁定，勿擅启）**：OI-026 cost/feature 消融（**非投稿前置条件**，审稿人要求再做；方案见 `../planning/FAECO_R11_SUBMISSION_POLISH_PLAN_20261012.md` §7）、§七 大规模验证、OI-027 版式压缩。
4. **未同步项（投稿前必办）**：⚠ **OI-024 Word 转排件仍为 v6 版**，现缺 **r8–r12** 全部改动（标题/摘要/术语 + 六张表 + r12 的 15 处文本改动），且 `postprocess.py` 标题/摘要/关键词为硬编码，须随 `scratch/word_convert/` 管线重建并改输入新名；**OI-025** 图源 PNG 不在 manifest 覆盖内。
5. 若审稿意见返回：以 `../review_history/paper_audit/consistency_audit_20260911.md` 为数字基线，**先读 `../evidence/PAPER_EVIDENCE_MANIFEST.md`**，只处理新意见；新增内容修改须先取得用户同意（**1-C 插入留修稿轮**，OI-018）。

## 不要做什么

- **不要修改论文内容**（内容已冻结 v10）——任何内容改动（含摘要）须先取得用户同意，一切内容修改留投稿/修稿轮；Word 转排稿中的摘要改写也须先获授权（OI-020）。
- `experiments/` 证据目录严禁删除；`paper/zh/figures/fig_iscas89.pdf` 是编译依赖，亦禁删。
- 论文数字只认 `experiments/20260826_aggregation/summary.json` 及对应产物；引用任何数字前**实查证据文件**。
- 未跑测试不修改 `code/src/rseco/`。
- 双栏模式下 `\FloatBarrier` 遇待排浮动体会**退化为 `\clearpage`**（造成栏底留白 / 末页孤儿）；本稿正文已移除，仅保留图 2 后一处用于约束全宽浮动体。压页/版面异常**勿再插入 `\FloatBarrier`**——优先调浮动体参数，不要缩字体、行距或砍内容。
- 未拍板前**不要**发送 `draft_email_to_jcad.md`、**不要**启动 Word 转排、**不要**插入 1-C 小节。

## 证据边界

- 论文主结果 = 20260826 统一批量口径（族 B；b17 phase-2 180 s 预算例外已披露）；§4.2 效率优先子研究（族 A，**revision 未完整钉定**）与 §4.4 消融（族 C/D）、§4.6 S 能力边界（族 F）是**各自独立配置，数字严禁互混**。
- 铁律：**`same claim ⇒ same revision + same config family`**；逐数字绑定见 `../evidence/PAPER_EVIDENCE_MANIFEST.md`。
- §4.1 已声明：**以 WNS 严格改善为主要统计口径**（ITC-99 = **18/19**，b06 的 TNS 辅助接受单独声明、不计入）；"WNS 严格改善"≠ timing closure；0.5 ns 为 stress-test 约束。**PicoRV32 = 2/2**（第三子模块无 setup 路径、不计入分母，r12 统一）。
- SEC：30 实例 29 修改、28/29 完全证明；b17 剩 1 个未证明点（Liberty 同函数）单独报告。
- P&R 验证为 OpenROAD 布局 + 全局布线寄生**估计**；无 DRC signoff（如实声明，D-03=A）。

## 构建与验收（论文）

见 `CURRENT_RUN_HANDOFF.md` 最上一节与 `versions/v10/README.md`：`cd paper/zh/manuscript` → `lualatex` ×2 → 质量门（`paper/zh/scripts/checks/latex_quality_gate.py`，Errors/Overfull/Underfull 须全 0）→ 双副本 `cp` + SHA256 核对 → 内容指纹（`pdftotext -layout … | sha256sum`，须用 poppler 25.07）。完成后按用户 standing 约定把作者版 PDF 同步到 `01_Papers/00_Summary/`。
