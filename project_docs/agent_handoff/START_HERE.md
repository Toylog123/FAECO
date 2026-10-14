# 当前状态：paused（2026-10-14）

> **2026-10-14：用户明确暂停，状态 paused。仅完成状态保全与交接；等待用户明确恢复，不得自动执行下文历史推进任务。**

暂停检查点main `71a4c12`已推送；后续仅行政收口，最终HEAD以git log -1为准。没有运行中的项目实验。最后全回归667 passed/4 skipped/156 subtests；新K1–K6仍未解决，多输出parser尚未实施。中文12页/英文27页与各7图14表已保存，但历史A六项缺证、D38/40和C代表9/12结构缺陷需补验，B28完整SEC绑定保留。完整断点与恢复顺序见 `CURRENT_RUN_HANDOFF.md`（状态目录内则 ../CURRENT_RUN_HANDOFF.md）。


## 暂停前历史记录

# START HERE

> r21 Git收口：实现提交 `e592bfd`、SVG导出规范化提交 `483b5e9` 已成功推送 `origin/main`（2026-10-14）。本轮审稿/配图/计数修复已完成，后续只处理保留的未决项；下文Git待办措辞为推送前记录。

接手者入口。**阅读顺序见 `README.md`**。最后更新：2026-10-14（r22_20261014，进行中）。

## 当前立即工作（r22，以本节为准）

- 用户继续授权恢复机制证据与投稿推进，旧r21暂缓只作历史；先读CURRENT_RUN_HANDOFF最上r22节、CURRENT_STATUS、TASK_BOARD、EXPERIMENT_REGISTRY、OPEN_ISSUES与EXPERIENCE。
- 源码/历史审计阶段28c3c2b已push，旧production644全回归+后加39组合门分别有证据。真实C′首pilot已执行两W0、最终SEC阻断，原目录完整保留，无有效新族结果；当前修复OI-035跨模块B插入/OI-036局部namespace伪pass。
- 修复后新commit/pin/v2与当前版本完整回归，重跑受影响矩阵；不要沿用旧源码通过或中间WNS，不拼旧C。不把records减launch称缓存：实读12/14和11/13、缓存0，各2条是F1前置拒绝。
- 当前中文12页/7图14表/21refs全门通过，三PDF e27eaf3a…/793545B。2994是有独有报告的候选STA结果，3363仍评估记录；不是全工具调用。英文27页首draft待视觉/事实核验，非提交件。
- OI-030/031/034/035/036开放；OI-032/033已修范围追踪。旧论文correctness受影响范围待审计，不推定全有效或全无效。主线负责稿/图/code/EDA/Git；专职记录只改记录文档。

## r21已完成提示（历史；旧暂缓不作为r22当前指令）

- 唯一工作副本 `D:\BaiduSyncdisk\01_Papers\03_FAECO`，分支 main；本轮起始 HEAD `73dc0e7`、clean。当前是 r21 工作修订，**不冻结 v19**；v18 作为不可变参考保留。
- 用户授权论文审稿、配图修改/增加和必要图注/引用。五视角审稿已形成 Major Revision，图 1/2 重绘、图 4～7 新增、图 3 沿用，正文必要证据说明已修。
- 先读 `CURRENT_RUN_HANDOFF.md` 最上一节、`status_logs/CURRENT_STATUS.md`、`TASK_BOARD.md`，再读 `../evidence/PAPER_EVIDENCE_MANIFEST.md` 与 `../OPEN_ISSUES.md`。
- 本轮已验收稿 12 页/7 图/14 表/21 引用，质量项全零。逐页视觉/源字形/40账本审计通过，双PDF和作者版三份一致，文档与记录已完成；阶段commit+push待主线执行，最新状态只认最上一节，不套用下方旧 v18 状态。
- OI-030/031 机制与配置缺口、OI-034 历史计数审计继续开放；OI-032 批次披露、OI-033 D 真实计数修复已完成。B 的 3363/664/104 是评估记录，b17 实际 STA 未识别；不得再称真实测量。
- 不新跑 EDA；cost 消融、大规模验证、Word 转排继续暂缓；不擅自插 1-C，不删除证据。阶段 commit+push 依当前 AGENTS，旧“push 等用户”仅为历史状态。
- 图源验收须结合字节哈希和渲染；不能只看文本指纹。验收后的作者版按既有约定同步 `01_Papers/00_Summary/`。

## r20/v18 历史快照（下列冻结/推送安排不作为 r21 当前指令）

## 当前工作区

- 项目：FAECO — 面向预布局门级时序 ECO 的候选探索与失效刻画
- 仓库：`D:\BaiduSyncdisk\01_Papers\03_FAECO`（唯一工作副本）
- 分支：main；**v18 冻结终态 = v18 双 tag 所指提交**（`git rev-parse v2026-10-13-narrative-convergence-r20^{commit}`；r20 **单一提交**（13 处叙述层改写 + 台账/交接层同步），其后另有 tag 之外的簿记提交；前置 v17 终态 = `40eb8b8`、v16 终态 = `0000885`、v15 终态 = `49aa835`、v14 终态 = `4d5e511`、v13 终态 = `0a03841`、v12 终态 = `dfc0394`、v11 终态 = `d59e00f`、v10 终态 = `b1403d9`、v9 终态 = `e00315a`）；remote: https://github.com/Toylog123/FAECO.git（**v11 + v12 + v13 + v14 + v15 + v16 + v17 + v18 均尚未推送**——按项目惯例 push 等用户明确指令；v10 及以前已推送）
- 主稿件（唯一 `.tex`，**内容冻结 v18，内容改动留投稿/修稿轮**）：
  `paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex`
  **11 页 / 0 Error / 0 Overfull / 0 Underfull / 0 Overfull vbox**；内容指纹 `63e62c52…`（poppler 25.07）；第 11 页为参考文献孤儿页（版式压缩见 OI-027）
- 基线 tag：**`v2026-10-13-narrative-convergence-r20`**（四元绑定 manifest `versions/v18/MANIFEST.sha256`，117 条）；
  论文发布 tag `faeco-paper-final-20261013i`；前置 v17 = `v2026-10-13-positioning-r19` / `faeco-paper-final-20261013h`，v16 = `v2026-10-13-fig2-update-r18` / `faeco-paper-final-20261013g`，v15 = `v2026-10-13-logic-calibration-r17` / `faeco-paper-final-20261013f`，v14 = `v2026-10-13-terminology-calibration-r16` / `faeco-paper-final-20261013e`，v13 = `v2026-10-13-defensive-purge2-r15` / `faeco-paper-final-20261013d`，v12 = `v2026-10-13-defensive-purge-r14` / `faeco-paper-final-20261013c`，v11 = `v2026-10-13-abstract-broaden-r13` / `faeco-paper-final-20261013b`，v10 = `v2026-10-12-pre-submission-consistency-r12` / `faeco-paper-final-20261013`（= `b1403d9`）；实验 revision tag `faeco-exp-rev1`（= `87d01ba`）
- 投稿目标期刊：**Integration, the VLSI Journal**（Elsevier；由 JCAD 改投，OI-028）；旧投稿包 `paper/zh/submission/`（T20/JCAD 版，作历史参考）
- 实验入口：`experiments/INVENTORY.md`、`experiments/RESULTS.md`（rev. 2026-09-29 已对齐论文口径）
- 环境：`.venv`（Python 3.11.9）；pytest import 报错先 `.venv\Scripts\python.exe -m pip install -e .`

**版本定义**：代码/论文版本由具名基线（tag）决定；工作树名、运行目录名不定义版本。

## 立即工作

1. **读 `CURRENT_RUN_HANDOFF.md` 最上一节**（2026-10-13 学术叙事收敛 r20（13 处改写））：**用户对作者版(7) = v17 的第五轮通读意见**（非外部匿名审稿，**不增实验**）。用户判断「整体框架已基本正确、主线比之前清晰很多」，本轮**「已经不是『需要重构』，而是『需要最后一次学术叙事收敛』」**；唯一核心 = **Candidate exploration under limited verification budget**，要求让所有章节回答同一问题「如何在有限验证预算下进行有效的预布局 ECO 候选探索」。用户裁定 3 项：核心问题句 = 替换为新句；贡献结构 = 2 条贡献 + 平台段落；§4.1 边界句 = 删除。**13 处改写**（E1/E2 摘要核心思想句 / E3 §1.1 核心问题句 / E4 §1.3 贡献分层 / E5+E6 失效反馈弱化 / E7 §4.5 标题 / E8 §5 结论 / Edel 删 §4.1 边界句）；全部唯一命中；**零数字/零实验/零代码/零参考文献**；页数 11（不变）。重冻结 **v18**；无新增遗留。
2. **当前最高优先 = OI-028：投 Integration, the VLSI Journal**——需**英文稿 + `elsarticle` 格式 + 投稿材料**（cover letter / highlights ≤85 字符 / graphical abstract）；中文稿作内容母本；AIGC 披露改按 **Elsevier** 政策复核（OI-021）。
3. **已暂缓（用户裁定，勿擅启）**：OI-026 cost/feature 消融（**非投稿前置条件**，审稿人要求再做；方案见 `../planning/FAECO_R11_SUBMISSION_POLISH_PLAN_20261012.md` §7）、§七 大规模验证、OI-027 版式压缩。
4. **未同步项（投稿前必办）**：⚠ **OI-024 Word 转排件仍为 v6 版**，现缺 **r8–r20** 全部改动（标题/摘要/术语 + 六张表 + r12 的 15 处文本改动 + r13 的摘要两段 + §1.1 改写 + r14 的 10 处 + r15 的 11 处 + r16 的 17 处 + r17 的 12 处 + r18 的图 2 替换 + r19 的 12 处定位重构 + r20 的 13 处叙事收敛），且 `postprocess.py` 标题/摘要/关键词为硬编码，须随 `scratch/word_convert/` 管线重建并改输入新名；**OI-025** 图源 PNG 不在 manifest 覆盖内。
5. 若审稿意见返回：以 `../review_history/paper_audit/consistency_audit_20260911.md` 为数字基线，**先读 `../evidence/PAPER_EVIDENCE_MANIFEST.md`**，只处理新意见；新增内容修改须先取得用户同意（**1-C 插入留修稿轮**，OI-018）。

## 不要做什么

- **不要修改论文内容**（内容已冻结 v18）——任何内容改动（含摘要）须先取得用户同意，一切内容修改留投稿/修稿轮；Word 转排稿中的摘要改写也须先获授权（OI-020）。
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

见 `CURRENT_RUN_HANDOFF.md` 最上一节与 `versions/v18/README.md`：`cd paper/zh/manuscript` → `lualatex` ×2 → 质量门（`paper/zh/scripts/checks/latex_quality_gate.py`，Errors/Overfull/Underfull 须全 0）→ 双副本 `cp` + SHA256 核对 → 内容指纹（`pdftotext -layout … | sha256sum`，须用 poppler 25.07）。完成后按用户 standing 约定把作者版 PDF 同步到 `01_Papers/00_Summary/`。
