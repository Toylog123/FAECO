# Current Run Handoff

> 最近一轮在最上，历史轮次原样保留在下。**新接手者只需读最上一节**。

## 2026-10-09 — 参考文献修复轮：重排文献表 + 重冻结 v4 + Word 稿重建（用户授权"方案 A"）

**本轮性质**：T20 检查单 #3 参考文献核对（`paper/zh/submission/REFERENCE_AUDIT_20261009.md`，LOG-20261009-02）发现 **1×P0**——参考文献编号未按正文首次引用顺序排列（首处引用渲染 `[1, 7, 9]`，18/19 条错位，违反 JCAD 规范一.1）。用户 **2026-10-09 授权"方案 A"**：从 `.tex` 源头修复 → 重冻结 v4 → Word 稿随管线重建。**零数字、零实验、零正文主张改动**——仅参考文献著录层。记录见 `LOGS.md` LOG-20261009-03。

1. **P0（编号顺序）**：`thebibliography` 由 19 条按正文首次引用顺序重排为 **14 条**；正文首处引用现渲染 `[1, 2, 3]`、全表按引用顺序递增。
2. **5 条纯 URL 工具/文档引用改正文页脚脚注**（JCAD 规范一.12）：picorv32 / yosys / OpenSTA / skywater-pdk（引用 2 次，含原 `liberty` 所指的 Liberty 文件句）→ 5 处 `\footnote{\url{…}}`；同时消除 `liberty`/`sky130` 的 bibitem-cite 不匹配。
3. **P1/P2 全处置**：会议文献 `[C] //` 空格（11 条）、期刊名 `Integration, the VLSI Journal` 全称、BUFFALO 题名补全（…`via group relative policy optimization`）、kravets 页码 `1-6`→`71:1-71:6`、`[Z]` 类型移出、DOI 中 `_` 转义（`6\_5`）。
4. **质量门**：9 页 / 0 Error / 0 Overfull / 0 Underfull；`??`=0；正文无 `[15]`–`[19]`；字节 SHA `dea21bb3…`（双副本一致）、内容指纹 `6ca972d5…`（poppler 25.07）。
5. **重冻结 v4**：tag `v2026-10-09-reference-fix`（= 提交 `1d01881`）+ 论文 tag `faeco-paper-final-20261009`；`versions/v4/MANIFEST.sha256`（117 条全 OK）；`BASELINE_INDEX.csv` v3→superseded / v4→active；`PAPER_EVIDENCE_MANIFEST.md` §6 置 v4 为当前发布版。
6. **Word 转排稿随管线重建**：`word/FAECO_投稿Word转排_20261009.docx` + `…_Word导出.pdf`（8 页，本机 Word 实测），5 条 URL 为 Word 原生脚注（落引用页页脚）；`preprocess.py` 守卫 19→14；旧 20260930 稿归档 `word/superseded_20260930/`（附 README 说明作废原因）；`word/转排说明.md` 更新至 20261009。
7. **T20 包同步**：检查单 #3 状态 → ✅ 已修；§3 登记新 Word 件字节 SHA256（docx `984cf0bc…`、PDF `4cf7dfd4…`）。

**不要做**：论文内容修改仍按用户指令**终止**——此后仅剩投稿手工项与审稿修稿轮（1-C 插入也在修稿轮，OI-018）；`sha256sum -c versions/v4/MANIFEST.sha256` 117 条应全 OK。

> **提交说明**：本轮 `1d01881`（论文制品 + v4 版本记录）已提交并打双 tag；后续文档同步提交见 `git log`。**注意**：v4 双 tag 为附注标签，取提交须用 `<tag>^{commit}`。

---

## 2026-09-30（傍晚）— 终审修正轮：5 处正文一致性修正 + 冻结 v3（内容修改终止）

**本轮性质**：用户终审确认前 4 项一致性问题已改对，提出**最后 5 处正文修正**并明示"改完即停止内容修改、不加任何实验"。记录见 `LOGS.md` LOG-20260930-07。

1. **5 处修正全部落地**（零数字、零实验）：① §3.4 F6 交叉引用纠错（§4.4→§4.5）；② §4.1 接受准则复述闭合 b06 TNS 辅助接受例外；③ 摘要（中/英）PicoRV32 分母解释（`picorv32_regs` 无 setup path **不参与判定**，消除"其余 1 个电路"歧义；中文 298 字 / 英文 150 词）；④ 表 8 补 $\Delta L=L_{\mathrm{before}}-L_{\mathrm{after}}$ / $\Delta_{\mathrm{WNS}}$ 符号定义；⑤ §4.5 F6 措辞对齐"启用式反馈"口径。
2. **质量门**：9 页 / 0 Error / 0 Overfull / 0 Underfull / 0 引用警告；字节 SHA `28647dc0…`（双副本一致）；内容指纹 `70bbd610…`（poppler 25.07）。
3. **冻结 v3**：tag `v2026-09-30-submission-ready-r2`（= 提交 `26f4f3b`）+ 论文 tag `faeco-paper-final-20260930-r2`；manifest `versions/v3/MANIFEST.sha256`（117 条全 OK）；v2/v1 依次 superseded。
4. **Word 转排稿同步**：摘要串与正文 5 处随管线重建，Word 引擎重导出 8 页（首页目检通过）；`word/转排说明.md` 与 T20 检查单锚点已刷新至 v3。
5. **用户手工收尾清单不变**（`word/转排说明.md`）：MathType 转换 / 黄色占位 / 图 2 通栏 / AIGC 披露（OI-021，投稿时必须解决）/ 终稿 PDF。

**不要做**：论文内容修改已按用户指令**终止**——此后仅剩投稿手工项与审稿修稿轮（1-C 插入也在修稿轮，OI-018）；`sha256sum -c versions/v3/MANIFEST.sha256` 117 条应全 OK。

---

## 2026-09-30（下午）— 投稿执行轮：五项拍板落地 + 摘要适配重冻结 v2 + Word 转排完成

**本轮性质**：用户拍板 OI-018~022 后执行。记录见 `LOGS.md` LOG-20260930-05/06。

1. **拍板结果**：OI-018 1-C 留修稿轮；OI-019 直接转排（询问邮件作废删除）；OI-020 授权且同步冻结版；OI-021 AIGC 暂缓（**投稿时必须解决**）；OI-022 维持默认（manifest 锁定、不入 git）。
2. **OI-020 已执行**：中英摘要按 JCAD 改写（295 字 / 149 词，去第一人称），其余正文零改动；质量门 9 页 / 0/0/0；**重冻结 v2**（tag `v2026-09-30-submission-ready` = `4dc16c6`，新内容指纹 `43becd39…` poppler 25.07，v1 superseded）+ 论文 tag `faeco-paper-final-20260930`。
3. **OI-019 已执行（Word 转排）**：`paper/zh/submission/word/` 三件套——`FAECO_投稿Word转排_20260930.docx` + `…_Word导出.pdf`（**本机 Microsoft Word COM 导出，实测 8 页全对**）+ `转排说明.md`。管线：引用字面化预处理（式1-3/表1-8/图1-3/算法1/文献[1-19] 零未解析）→ pandoc（OMML）→ python-docx JCAD 版式（题录块单栏 + 正文双栏 continuous 同页、三线表、上标引文、首页脚注块）。**LibreOffice 预览的多栏表格竖排是其渲染局限**（XML 经探针验证合规），校对以 Word 为准。
4. **方正字体已装**（用户请求）：官方免费四款（书宋/仿宋/黑体简体，出版场景免费）经 AUR SHA256 校验装为用户级字体；docx 用免费版实名；GBK 版为商业字库（编辑部终排用自有正版）。
5. **用户手工收尾清单**（`word/转排说明.md`）：MathType 批量转换（OMML→MathType）、黄色占位替换（通信作者 \*/基金/日期/作者简介）、图 2 通栏、AIGC 披露（OI-021）、终稿 PDF 导出。

**不要做**：除上述用户手工项与审稿修稿轮外，不再改论文；LaTeX 冻结版与 v2 manifest 未动（`sha256sum -c versions/v2/MANIFEST.sha256` 117 条应全 OK）。

---

## 2026-09-30 — 补充材料成文轮（S1–S5 全部初稿完成）

**本轮性质**：T20 补充材料成文 + 台账更正，**未动论文、未改代码**。记录见 `LOGS.md` LOG-20260930-01..04。

1. **S1–S5 初稿完成**（`paper/zh/submission/supplementary/`）：S1 失效事件名映射（**OI-008 投稿前必办项就此闭合**）、S2 实验族与可复现性（功能差异命名脱敏）、S3 SEC 逐实例表、S4 环境工具链、S5 基准来源许可。清单与检查单状态已同步。
2. **更正两处过时表述**（均以实查为准）：① OI-008"当前 `code/` 已无旧事件名"——0a 合并（`258f588`）后 `real_wns.py:1864` 仍以 `acceptance_budget_violation` 写台账，正确表述是"工具层事件名 ↔ 方法层 F 分类"两层分工；② manifest §2 SEC 行"22 行 PASS"——实读 CSV 为 **29 PASS + 1 N/A = 30**，与论文口径闭合。
3. **缺口闭合**：PicoRV32 补建 source manifest（`picorv32.json`，clone HEAD `a473fc8f…`；`modules/` 三个 .v 为上游单文件的三份相同副本——易误判点已在 manifest/S5 写明）。
4. **待用户拍板不变**（OI-018~OI-022）：1-C 插入时机 / Word 转排路径 / 摘要改写授权 / AIGC 披露 / 3 个证据文件 git add。S2 的表述粒度亦待用户定。
5. 论文内容冻结未破（指纹 `7adf0279…`，poppler 25.07 口径，见经验库第 11 条）。

---

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
