# Current Run Handoff

> 最近一轮在最上，历史轮次原样保留在下。**新接手者只需读最上一节**。

## 2026-10-09 — 文字专项审稿全量落地轮（r7）：重冻结 v6 + 末页孤儿修复 + Word 稿重建

**本轮性质**：用户提供外部 **FAECO 文字专项审稿**（全文文字级意见，归档 `paper/zh/review_rounds/r7_20261009/comments.md`），审稿人明确"不建议大规模重写、不要求新增实验、不直接改论文文件"。逐项核验后由用户拍板 4 项（摘要方向=**完全采纳审稿人**；执行范围=**全部执行 P0+P1+P2**；§4.6 口径=**采纳审稿人更保守写法**；A\* 可复现性披露=**按审稿人删除**），随后一次性落地全部意见，并修复文字收敛引入的**末页孤儿**。**零数字、零实验改动**，主张强度仅 §4.6 一处**下调**。

1. **P0×5（降主张/修事实）**：摘要"其余无退化"限定为**预布局理想线网 WNS** 口径；§4.1 删"保证不同基准电路均产生 setup 违例"（改述为严格时钟约束、非目标工作频率、不等价于时序收敛）；§4.6 由"枚举瓶颈已排除"下调为"本次扩大候选池未带来时序收益，尚不能排除更大规模扩展"；§3.1 拆开"候选的时序接受条件"与"对最终修复网表执行独立顺序 SEC"；§3.3 纠正事实性错误"缺少 R 等价候选的门不可重写"→"仅关闭 R 相关折扣，仍参与 G/B 候选生成"。
2. **P1×6**：§1.3 三项贡献重组；"20 轮收敛配置"→"20 轮迭代配置"（4 处）；§4.4 首现处补 $B(k)$ 定义（截至第 $k$ 次候选级 STA 的累计最优 WNS 改善曲线，对齐 `code/src/rseco/flow.py:1214`）；符号统一（`A(p)`→`\operatorname{Accept}(p)`、$S$→$S_2$、`\mathcal R`→$V_R$）；去工程日志式表述（子研究/台账/主力/拖高）；F1--F6 与物理门控按"一处定义、余处简引"收敛。
3. **P2×3**：表 1 表头"主要优势"→"主要技术特点"；§5 结论三段压两段；表 8 补 $\Delta_{\mathrm{WNS}}=0$ 行（36/126，使 $0+36+90=126$ 自洽）、§4.5 改题"物理时序评估与失效检测"。
4. **术语统一**：关键词/正文统一"**局部门级修改**"（英文同步 `gate-level local modification`，修 CN/EN 不一致）；"功能保持可用性"→"R 等价候选可用性"；"理想线网收益"→"理想线网 WNS 改善"；表 8"扩池"→"扩大候选池"。
5. **★ 末页孤儿修复（非审稿人要求，为消除本轮引入的版面退化）**：文字收敛后参考文献 [13][14] 被挤到第 9 页、该页约 93% 空白。实测归因：① 参考文献 `itemsep`/`\balance` 已无压缩余量（`footnotesize + linespread 0.95 + itemsep≈0`）；② 纯文字精简约 5 行**亦无效**——节省篇幅被第 3/5/6/7 页**栏底留白**吸收；③ **删正文 10 处 `\FloatBarrier`（双栏下遇待排浮动体会退化为 `\clearpage`）+ 去重精简 7 处 → 8 页**，且图 1/2/3、表 1--8 逐页分布与改前**完全一致**（无浮动体位移）。导言区已加维护注记防回退。图 2 图注 A/B 保持不变（已烧入 PNG，改则图文不一致）。
6. **质量门**：**8 页** / 0 Error / 0 Overfull / 0 Underfull；`??`=0；`\bibitem`↔`\cite` 14/14 且编号按正文首次引用顺序；字节 SHA `09197e5f…`（双副本一致）、内容指纹 `88b03403…`（poppler 25.07）；摘要中 228 字 / 英 148 词。
7. **重冻结 v6**：tag `v2026-10-09-text-review` + 论文 tag `faeco-paper-final-20261009c`；`versions/v6/MANIFEST.sha256`（117 条全 OK，相对 v5 变动 3 条）；`BASELINE_INDEX.csv` v5→superseded / v6→active；`PAPER_EVIDENCE_MANIFEST.md` §6 置 v6 为当前发布版。
8. **Word 转排稿重建**：`word/FAECO_投稿Word转排_20261009c.*`（摘要与关键词改为**从 v6 `.tex` 抽取后写入** `postprocess.py`）；⚠ **同时修正上一轮管线缺陷**——`20261009b` 稿的摘要实为 v4 版（v5 轮重建时漏改 `postprocess.py` 硬编码的 `zh_abs`/`en_abs`/关键词），b 稿已归档 `word/superseded/` 并在该目录 README 写明作废原因。
9. **r7 归档**：`paper/zh/review_rounds/r7_20261009/`（`comments.md` 原文 + `response.md` 逐项核验与**执行记录** + `README.md` + `manuscript_before.tex` 改前 v5 主稿）。

**不要做**：① 论文内容修改仍按用户指令**终止**（本轮系用户授权执行外部审稿意见）；② **不要再往正文插 `\FloatBarrier`**（导言区已有注记）；③ 改正文后必须复核"图表是否仍紧跟其引用处"，并把页数/图表页码分布列入常规验收；④ 任何 `.tex` 摘要/题录改动**必须同步** `scratch/word_convert/postprocess.py` 的硬编码串（`preprocess.py` 的 `N_BIB` 守卫只管参考文献条数）；⑤ v6 双 tag 为附注标签，取提交须用 `<tag>^{commit}`。

---
## 2026-10-09 — 摘要可读性改写轮：去术语 + 重冻结 v5 + Word 稿再重建

**本轮性质**：用户反馈"摘要太多技术要点、很难让大同行看懂"，授权改写。**仅中/英摘要两段**（`.tex` 两处），重编译 → 重冻结 v5 → Word 转排稿随管线再重建。**零数字、零实验、零主张改动**——正文、公式、图表、参考文献一字未动。记录见 `LOGS.md` LOG-20261009-04。

1. **去术语/缩写、只留概念**：删除 R/G/B/JOINT、F1--F6、多特征加权割、关键路径覆盖割、违例扇入锥、简化 SPEF 复测、独立全网表顺序等价检查、纯 G、WNS/TNS 等**未展开的机制名与缩写**，改为概念化表述（"按多种结构特征构造修改候选并统一排序""将候选失效归纳为若干类型""依次通过时序分析与等价性检查验证""仅门尺寸调整"）。
2. **补"为什么重要"**：首句点明时序 ECO 在芯片设计中的位置与预布局阶段约束（合法修改手段有限、候选空间大、验证代价高）。
3. **结果层保留主数字与诚实边界**：8/8、18/19、2/3；1.07 vs 0.16 ns；"无实例退化""尚未达到完全时序收敛"（替代"非 timing closure"）；结尾保留"单纯降低逻辑深度未必带来时序收益"。
4. **字数**：中文 **264 字**（原 298）、英文 **148 词**（原 150），均符合 JCAD ≤300 字/≤150 词；英文维持无第一人称。
5. **质量门**：9 页 / 0 Error / 0 Overfull / 0 Underfull；`??`=0；字节 SHA `5c37725a…`（双副本一致）、内容指纹 `0a2b0723…`（poppler 25.07）。
6. **重冻结 v5**：tag `v2026-10-09-abstract-plain`（= 提交 `1c67f50`）+ 论文 tag `faeco-paper-final-20261009b`；`versions/v5/MANIFEST.sha256`（117 条全 OK，相对 v4 变动 3 条）；`BASELINE_INDEX.csv` v4→superseded / v5→active；`PAPER_EVIDENCE_MANIFEST.md` §6 置 v5 为当前发布版。
7. **Word 转排稿再重建**：`word/FAECO_投稿Word转排_20261009b.docx` + `…_Word导出.pdf`（8 页，本机 Word 实测）；`postprocess.py` 摘要串同步、OUT 改 `…_20261009b.docx`；旧 20260930/20261009 两批归档 `word/superseded/`（README 说明作废原因）；`word/转排说明.md` 更新。

**正文刻意保留机制名**（R/G/B/JOINT、F1--F6 等）——摘要给大同行、正文给同行，这是本轮的设计取舍。

**不要做**：论文内容修改仍按用户指令**终止**（本轮改写系用户明确授权）；`sha256sum -c versions/v5/MANIFEST.sha256` 117 条应全 OK；v5 双 tag 为附注标签，取提交须用 `<tag>^{commit}`。

---

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
