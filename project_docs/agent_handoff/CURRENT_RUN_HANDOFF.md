# Current Run Handoff

> 最近一轮在最上，历史轮次原样保留在下。**新接手者只需读最上一节**。

## 2026-10-13 — 投稿前一致性 pass（r12：第五份外部审稿 M1–M5）+ 重冻结 v10

**本轮性质**：用户提供**第五份外部审稿**（「**投稿前最后一轮审稿人视角**」，对 **v9 / 作者版 10 页**；归档 `paper/zh/review_rounds/r12_20261013/`），审稿人评分 = 问题价值 9 / 方法完整性 8 / 创新表达 8 / 实验完整性 8 / **证据一致性 7** / Integration 匹配度 8.5，**最大风险被明确为可读性风险**（审稿人能否准确理解「哪个实验验证哪个机制」）。审稿人给出的必改清单 **M1–M5**，并明确指令：**「不要再加实验。做一次 Submission consistency pass……完成后，这篇论文才是真正的投稿版本。」** 用户据此裁定范围 = **仅 M1–M5**。审稿人**再次否决**补做 cost/feature 消融（与 r10 立场一致，与 r11 用户「暂缓」裁定一致）。**零数字、零实验、零代码改动**（纯口径统一 + 主张强度 + 措辞）。记录见 `LOGS.md` LOG-20261013-01/02、`CHANGE_LOG.md` r12 行、`versions/v10/README.md`。

1. **M1 · SEC 统计口径统一（表 5）**：表 5（`tab:overview`）ITC-99 行 SEC 列 `\textbf{19/19}` → `18/19`，并在**表注前置**「SEC 列为完全证明的修改网表对数；ITC-99 的 b17 有 1 个等价点未完成证明（见 `\S\ref{sec:ood}`），故记为 18/19」。
   - **判据**：正文自始为「30 实例 / 29 产生修改 / **28/29** 完全证明」，拆分式 `8 (ISCAS89) + 18 (ITC-99) + 2 (PicoRV32) = 28` 一直自洽 ⇒ **表 5 是唯一漏改处**。**审稿人猜「表 7」，实为表 5**（审稿人指出的位置不准，但错误真实存在）。改后全文 `19/19` 计数 = **0**。
2. **M2 · PicoRV32 统计与分母解释（5 处）**：`2/3` → **`2/2`** + 一句「PicoRV32 第三个子模块无 setup 路径，不参与改善判定 / 不计入分母」。落点 = **摘要 CN**、**摘要 EN**、**§4.3**（`sec:ood`）、**结论**、**表 5** PicoRV32 行。改后 `2/3` 计数 = **0**、`2/2` 计数 = **7**（渲染 PDF 逐字复核）。
3. **★ M3 · 表 11 预算解释 —— 本轮最重要取证：论文里存在两个不同的 STA 计数器**（审稿人指出「500 预算」与「4146」看似矛盾）：
   - `state.budget.sta_used`（`code/src/rseco/search_state.py:254` `reserve_budget`；检查点 `code/src/rseco/flow.py:591`）= **每轮迭代预约一次、到迭代边界才判顶**（`trial_count >= sta_budget → stop_reason = "sta_budget"`）的**预约计数**，**逐电路** ≤ 500；**random 臂确实触顶**：`random_s1/s420`、`random_s2/s420 + s641`、`random_s3/s420 + s641`。
   - `n_candidate_sta_runs`（`code/scripts/run_outerloop_real_wns.py:437` = `len(evaluator.trials)`）= **候选级 STA 测量次数**（= 论文 §4.4 口径），逐电路最高 **1321**。
   - ⇒ 表 11 的 8 电路合计（fixed **4146** / adaptive **4883** / random 三种子均值 **5624**）**不受 `500×8` 约束，数字无需更正**；缺的只是口径说明，已写入表 11 表注。**旁证**：`--sta-budget` 的 CLI help 原文即 "Hard maximum candidate STA **reservations**"，而表 11 数的是 **measurements**。
4. **M4 · 贡献 1 弱化 `1.07 ns` 与加权割的绑定（§1.3）**：不再把 `1.07\,ns` 对 `0.16\,ns` 紧挂在「多特征加权割 + 关键路径覆盖割」的机制归因上（主实验实际对照的是**候选空间 + 排序**的联合效应），改为「在固定权重、20 轮迭代配置下，**混合候选策略**相较**单一门尺寸调整策略**取得更大的平均 WNS 改善（1.07\,ns 对 0.16\,ns）」。贡献 2 的自我限制句（搜索诊断与控制、非独立增益来源）**保留**。
5. **M5 · 特征动机措辞降调（§3.4 正文 ×3 + 表 4 行 ×3）**：`避免修改跨越局部逻辑闭合边界`→`降低跨越局部逻辑边界候选被优先选择的概率`；`降低候选的功能与结构验证成本`→`使搜索倾向于选择验证规模较小的候选`；`避免在扇出较大的节点上引入电气与负载风险`→`以降低引入电气与负载风险的可能`；表 4 对应行改「降低…的优先级 / 倾向选择… / 降低…候选的优先级」。**依据**：这些特征只进入式 (2) 的**排序**，硬约束来自**构造级检查**，故「避免 / 保证」属过强主张。
6. **另（审稿人「问题 2」）**：§4.4 开头补「…比较候选空间与候选评估顺序的**联合影响，不单独隔离式~`\eqref{eq:cost}` 中各特征项的贡献**（特征项属候选生成过程的一部分，其权重在本组固定不变）：」。
7. **质量门与终检**：**10 页（不变）** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / **0 Overfull vbox**；`??` = 0（`Undefined: 5` = **字体替身警告，非引用**）；表/图引用覆盖 **17/17**（`scratch/check_env_refs.py`）；浮动体编号阅读顺序 **1..14 / 1..3**（`scratch/float_order_probe2.py`）；`.tex` **CRLF 668 / 0 bare LF**（61,948 B，vs v9 **15 insertions / 15 deletions**）；双副本 PDF 字节 SHA **`4ef380f7…`**（2,770,949 B）；内容指纹 **`c7b4d807…`**（poppler 25.07 原始输出）。
8. **重冻结 v10（四要素）**：tag **`v2026-10-12-pre-submission-consistency-r12`** + 论文 tag **`faeco-paper-final-20261013`**；`versions/v10/MANIFEST.sha256`（**117 条全 OK**，相对 v9 **仅 3 条变化** = `.tex` + 双副本 `.pdf`，114 条未变；由 `scratch/gen_manifest_v10.py` 从 v9 派生、**LF-only**）；`BASELINE_INDEX.csv` v9→`superseded` / v10→`active`（11 行、恰 1 active）。**已推送 origin（2026-10-13，用户指令「推送」）**：`main` = `origin/main` = **`b1403d9`**（v10 双 tag 所指），`git ls-remote --tags origin` 中两 tag 的 `^{}` 均 = `b1403d9a683b…`；推送簿记提交位于 tag 之外，符合 r9（`0602326` tag + `f29475c` 文档提交）与 r11 先例。
9. **台账收口**：`LOGS.md`（LOG-20261013-01/02）、`CHANGE_LOG.md`（r12 行）、`PAPER_EVIDENCE_MANIFEST.md` §6（新增「★ 当前发布版 v10」，v9 降为「前序发布版」）、`OPEN_ISSUES.md`（**OI-024** 扩到「r8~r12 全部改动均未同步、与 v10 主稿（指纹 `c7b4d807…`）不一致」/ **OI-027** 更新为 v10 = 10 页 / **新增 OI-029** = 第五份外部审稿落地）、`.workbuddy/memory`。
10. **00_Summary 同步**：按用户 standing 约定同步作者版 PDF（`4ef380f7…`）；文件名不变（本轮**未改标题**）。
11. **本轮踩坑与经验（写入 `versions/v10/README.md` 教训节）**：① **「台账里有两个同名概念」是最隐蔽的口径错误来源** —— 判据 = 一个数字若与另一数字"看起来"违反同一约束，先确认两者**是否同一计数器**，再决定改数字还是补说明；② **审稿人指出的错误位置可能不准，但错误往往真实存在** —— 用完整拆分式回代唯一定位（`8+18+2=28` ⇒ 只有表 5 矛盾）；③ **口径统一 ≠ 数字改动** —— 记录时须与"新增/修改数字"明确区分，否则污染"零数字改动"声明；④ **主张强度修正须回代码确认约束来源**（M5 的「避免 ×3」过强，是因为硬约束在构造级检查、而特征只进排序）；⑤ **`.tex` 每次插入块后须重新归一化行尾**（三引号块用 `\n` 会引入裸 LF，须统一回 CRLF）。

### 下一步（有明确指令再做）

- **OI-028 Integration 转化（当前最高优先）**：英文稿 + `elsarticle` 格式 + 投稿材料（cover letter / highlights ≤85 字符 / graphical abstract）；中文稿作内容母本；**英文标题已定锚**（`FAECO: Candidate Exploration and Failure Characterization for Pre-Placement Gate-Level Timing ECO`）。
- **OI-024 Word 转排件重建**：仍为 v6 版，现缺 **r8–r12 全部改动**（含**六张**新表 + 本次 15 处文本改动）；`scratch/word_convert/postprocess.py` 的标题/摘要/关键词为**硬编码**，须先同步 + 改输入新名 + 重跑整条管线。
- **OI-021 AIGC 披露**：按 **Elsevier** 政策复核。**OI-025** 图源 PNG 不在 manifest 覆盖内。**OI-027** 版式压缩（10 页，留内容定稿后统一排）。
- **OI-026（cost/feature 消融）= 审稿人两轮连续否决 + 用户裁定「暂缓」**，**非投稿前置条件**；方案备于 `project_docs/planning/FAECO_R11_SUBMISSION_POLISH_PLAN_20261012.md` §7（新族 C′ / 新表 / 4–5 h / 允许 NEGATIVE）。
- **§七 大规模验证**（OpenCores / RISC-V 完整模块 / 工业网表）：需新基准接入 + 新算力；暂缓。
- **不得触碰**：① 不要删 `\balance`；② 不要把族 D 的数字与表 9/表 10 并表或交叉换算；③ 不要新增/修改任何既有数字（r12 再次确认零数字改动；`19/19→18/19`、`2/3→2/2` 属口径统一）；④ 不要在正文插 `\FloatBarrier`；⑤ 不要改 `paper/zh/manuscript/` 里 `.tex` 的换行风格（**必须纯 CRLF**，插入块后须重新归一化）；⑥ **manifest 文件必须 LF-only**（`sha256sum -c` 遇 CRLF 会把 `\r` 当文件名；`.gitattributes` 已锁 `versions/*/MANIFEST.sha256 text eol=lf`）。

## 2026-10-12 — 投稿前精修（r11：标题 / 摘要 / 贡献定位 / 术语与语言风险）+ 重冻结 v9

**本轮性质**：用户提供一份「投稿前精修」六阶段方案（阶段 1 贡献重定位 / 阶段 2 §3.4 固定权重声明 / 阶段 3 cost 消融 / 阶段 4 英文标题重设计 / 阶段 5 Related Work 比较焦点句 / 阶段 6 语言风险审计），**先取证核验再执行**（方案落 `project_docs/planning/FAECO_R11_SUBMISSION_POLISH_PLAN_20261012.md`，不做重复项）。用户随后裁定三则：① **英文标题** = `FAECO: Candidate Exploration and Failure Characterization for Pre-Placement Gate-Level Timing ECO`，**中文标题** = `FAECO：面向预布局门级时序 ECO 的候选探索与失效刻画`；② **cost 消融暂缓**（不作为当前投稿前置条件；理由 = 主论证链已闭合，新增会引入"为什么主实验不用这个配置"的解释成本，**若审稿人要求再做**）；③ **Step 1（标题、贡献、语言风险、定位调整）立即执行**。**零数字、零实验、零代码改动**（纯文字/定位）。记录见 `LOGS.md` LOG-20261012-05/06、`CHANGE_LOG.md` r11 行、`versions/v9/README.md`。

1. **★ 决定性核验：六阶段中三阶段已在 r10/v8 落地，不可重做**。阶段 2（§3.4 特征设计动机 + 固定权重 $1.0$ 声明）、阶段 3 所指的 runtime 表（= 表 11 `tab:runtime`）、阶段 5（§2.2 基线定位 + 表 2 `tab:baseline_cmp`）**均已由 r10 落地**；重做会造出**重复表**与**自相矛盾句**。故本轮只落地真正未做的部分。
2. **★ 取证更正（OI-026，纠正 r10 台账的误定位）**：审稿人所指的 cost/feature 消融**不能在 §4.4 的运行器上做** —— 表 9/表 10 出自 **族 C**，其运行器 `code/scripts/run_hybrid_repair.py` 的 `parse_args()` **完全没有 λ 参数**，候选排序只由 `--strategy-priorities` + `strategy_selector.exploration_order()` + 可选 `--random-order` 决定，**根本不调用 `cost(v)`（`cut.py:182–213`）**。因此 r10 台账"加权割消融…改 `flow.py:359/385`"属**误定位**（`flow.py:359/385` 是 constrained-cut/cover-cut 分支，不是 λ 硬编码点）。正确表述：式 (2) 消融 = **新实验族 C′**，需给 `real_wns.py` 的权重对象（现仅 3 键 λ_b/λ_s/λ_c）补 **λ_v/λ_f** 并新加 CLI（λ_v/λ_f **无初始参数、无 CLI** = 真正的代码缺口）；预算由"40–60 min"更正为 **4–5 h**。附带澄清 **λ_c 三重角色**：节点代价深度折扣（`cut.py:208`）、关键路径覆盖候选**插入**（`cut.py:306`，门控 `critical_reward > 1.0`）、尺寸精化割 `covered` 奖励（`cut.py:403`）。
3. **7 组改动（23 insertions / 23 deletions）**：① 标题 CN/EN；② 摘要 CN/EN + 英文关键词（减"structured framework"，增"candidate exploration"）；③ §1.3 贡献 1/2 重写（**贡献 1** 框架定位 = 多特征加权割 + 关键路径覆盖割扩展局部修改空间 + 候选排序降低验证开销，并给 1.07 vs 0.16 ns；**贡献 2** 失效刻画机制 = F1--F6 六类，明确**定位为搜索诊断与候选控制、非独立收敛增益来源**；**贡献 3 保留**）；④ 术语统一（`类型化失效归因`→`类型化失效刻画`、`失效归因`→`失效刻画`、`结构化归因`→`类型化刻画`、**`结构化排序`→`候选排序` ×7**）；⑤ §2.2 比较焦点句；⑥ **结论末句（M4）**不得停在"当前 EMA 反馈与 S 候选均未取得独立收益"，改为"实验分析进一步揭示了候选排序、验证预算和结构扩展之间的关系，为后续预布局 ECO 搜索策略设计提供依据"；⑦ 3 处语言风险修正。
4. **重命名（live pointers 已更新，历史记录保留旧名）**：`…FAECO_面向预布局门级时序ECO的…结构候选搜索与失效归因.tex` → **`…FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex`**（PDF 双副本同步改名）。**live pointers 已同步**：`tools/sync_to_summary.py`、`paper/zh/figures/{insert_spef,convert_tables}.py`、`paper/zh/manuscript/{_extract_pages,_render_exp}.py`、`README.md`、`paper/zh/README.md`、`docs/GLOSSARY.md`、`.codex-handoff.json`、`START_HERE.md`、`NEXT_AGENT_PROMPT.md`。**历史记录刻意保留旧名**：`versions/v1..v8/`、`CHANGE_LOG.md`/`LOGS.md` 旧行、`agent_handoff/` 快照、`submission/`。
5. **语言风险实测（非臆造）**：v8 `.tex` 计数 —— `首次提出`=0 / `显著`=0 / `有效提升`=0 / `创新`=0 / `突破`=0；`优于`=1（事实陈述）、`有效`=5（均为"有效/valid"义）、`证明`=8（均为 SEC/CEC 形式证明）、`关键`=39（多为"关键路径"）。结论：仅约 5 处真实风险，已逐一处置。
6. **质量门与终检**：**10 页** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / **0 Overfull vbox** / 0 undefined refs；`??`=0（`Undefined: 5` = **字体替身警告，非引用**）；表/图引用覆盖 **17/17**（`scratch/check_env_refs.py`，硬编码路径已随重命名更新）；浮动体编号阅读顺序 **1..14 / 1..3**（`scratch/float_order_probe2.py`，须传 `<pdf> <tex>`）；论文 `.tex` **`22de39a0…`**（668 CRLF / 0 bare LF, 61,144 B，vs v8 **23 insertions / 23 deletions**）；双副本 PDF 字节 SHA **`f642e533…`**（2,769,731 B）；内容指纹 **`3832eeb2…`**（poppler 25.07 原始输出）。
7. **重冻结 v9（四要素）**：tag **`v2026-10-12-submission-polish-r11`** + 论文 tag **`faeco-paper-final-20261012c`**（**均 → `e00315a`**，即 v9 终态提交；链：`daba5ab` 主稿/台账 → `da61cdf` 指针状态同步 → `e00315a` handoff 补记）；`versions/v9/MANIFEST.sha256`（**117 条全 OK**，相对 v8 **仅 3 条变化** = `.tex` + 双副本 `.pdf`，114 条未变；由 `scratch/gen_manifest_v9.py` 从 v8 派生）；`BASELINE_INDEX.csv` v8→`superseded` / v9→`active`（10 行、恰 1 active）。**已推送 origin**（`main` = `origin/main` = `e00315a`，21 个 tag 全部上远端）。
8. **台账收口**：`LOGS.md`（LOG-20261012-05/06）、`CHANGE_LOG.md`（r11 行）、`PAPER_EVIDENCE_MANIFEST.md` §6（新增"★ 当前发布版 v9"，v8 降为"前序发布版"）、`OPEN_ISSUES.md`（**OI-026 标暂缓** / **OI-024 扩到"r8+r9+r10+r11 改动均未同步 + 标题/摘要为旧口径 + 术语仍为旧名"** / **OI-027 更新为 v9 = 10 页** / **OI-028 记入已定标题与重命名**）、`.workbuddy/memory`。
8b. **★ 发现并修复「指针/状态层」三轮漂移（非本轮改动，系 r9/r10/r11 遗留）**：`README.md`、`START_HERE.md`、`NEXT_AGENT_PROMPT.md`、`.codex-handoff.json`、`WORK_PROGRESS.md`、`CURRENT_STATUS.md`、`TASK_BOARD.md` 七份文档**只跟到 v6**（`b1eee25` / 8 页 / JCAD / 指纹 `88b03403`；`.codex-handoff.json` 的 `project` 串甚至是旧题目），与本轮新标题拼成"**新标题 + v6 旧状态**"的混合信息（旧 stem 残留探针 `grep -rln 结构化候选搜索与失效归因` 揪出）。已全部同步到 v9（commit **`da61cdf`**）。**教训：交接层不止 `CURRENT_RUN_HANDOFF.md` 一份** —— r9/r10 只更新它，导致其余 7 份漂移 3 轮；下一轮收口须按 `AGENTS.md` 工作规则 7 逐份过：**WORK_PROGRESS / CURRENT_STATUS / TASK_BOARD / CURRENT_RUN_HANDOFF / START_HERE / NEXT_AGENT_PROMPT / `.codex-handoff.json` / README**。
9. **00_Summary 同步**：按用户 standing 约定同步作者版 PDF 为 **`FAECO_面向预布局门级时序ECO的候选探索与失效刻画_作者版.pdf`**（`f642e533…`），**旧名文件已删除**（同一论文只保留一份最新作者版）。

### 下一步（有明确指令再做）

- **OI-026（cost/feature 消融）= 用户裁定「暂缓」**，**不作为当前投稿前置条件**；方案已就绪（`planning/FAECO_R11_SUBMISSION_POLISH_PLAN_20261012.md` §7 = 新族 C′ / 新表 / **4–5 h** / **允许 NEGATIVE**）；**仅当审稿人明确要求时**再启动，且须先落方案。
- **OI-028 Integration 转化（当前最高优先）**：英文稿 + `elsarticle` 格式 + 投稿材料（cover letter / highlights ≤85 字符 / graphical abstract）；中文稿作内容母本；**英文标题已定锚**（见本轮）。
- **§七 大规模验证**（OpenCores / RISC-V 完整模块 / 工业网表）：需新基准接入 + 新算力；**暂缓**。
- **不得触碰**：① 不要删 `\balance`；② 不要把族 D 的数字与表 9/表 10 并表或交叉换算；③ 不要新增/修改任何既有数字（r10/r11 均已确认零数字改动）；④ 不要在正文插 `\FloatBarrier`；⑤ 不要改 `paper/zh/manuscript/` 里 `.tex` 的换行风格（**必须纯 CRLF**，插入块后须重新归一化）；⑥ **manifest 文件必须 LF-only**（`sha256sum -c` 遇 CRLF 会把 `\r` 当文件名，报 `'…'$'\r': No such file or directory`，须用 `open(..., newline="\n")` 写）。

## 2026-10-12 — 复审四（r10，零算力增强）+ 目标期刊改投 Integration：重冻结 v8

**本轮性质**：用户提供**第三方复审四**（对 **v7 / 作者版 9 页**；总判断 = 已从「实验不闭环」提升为「**基本完整的 EDA 论文实验体系**」，**主要问题不再是实验不足，而是创新高度、方法定位与期刊匹配**；归档 `paper/zh/review_rounds/r10_20261012/comments.md`）。用户三则裁定：① 执行范围 = **只做零算力项**；② 运行时间表口径 = **族 D 三臂**；③ 目标期刊 = **改投 Integration, the VLSI Journal**（取代 JCAD）。**零数字、零实验、零代码改动**。记录见 `LOGS.md` LOG-20261012-03/04、`CHANGE_LOG.md` r10 行、`versions/v8/README.md`。

1. **★ 决定性核验：审稿人要的运行时间表不可零算力实现**。审稿人要求 `方法 \| STA 次数 \| 总运行时间(s)`，方法列 = **Random / Pure G / FAECO**，三列出自**表 9 = 族 C**（`20260807_multiround_8c_067` + `20260826_ablation_*`）。穷举探针 `scratch/probe_runtime_fields.py` 证明**族 C 全部 JSON 与 `.log` 均无任何时间字段** ⇒ 该列在冻结 revision 下**不可恢复**（族 C 的调用命令亦未归档，OI-012）。
2. **★ 关键否证：族 D 不能充当表 9/表 10 的数据**。族 D（`20260924_threearm`）的 `random_s1/s2/s3` 带 `--random-order`，看似正好补"结构化 vs 随机"，但**实测复现失败**（`scratch/probe_famD_repro.py`）：结构化 s27 首次改善 **1 vs 30**、随机三种子均值 ΔWNS **0.40 vs 0.265**、混合 20 轮 **1.07 vs 0.285**。根因 = **运行器不同**（表 9 出 `code/scripts/run_hybrid_repair.py`（OI-012 已证）vs 族 D 出 `code/scripts/run_outerloop_real_wns.py`，`git_head` 亦不同）⇒ **硬族边界，禁止并表**。故表 11 采用族 D 独立口径并在表注显式声明「与表 9、表 10 出自不同运行配置，STA 计数不与表 10 的首次改善位置口径对应」。
3. **旁证 r9 纠错方向正确**：族 D 报告 `reports/FAECO_L2_THREEARM_20260924.md` 第 54 行「s641: 1→123；s713: 5→216；s953: 1→185」与 **v6 版 §4.4 原句完全一致** ⇒ 确认 v6 原句取自族 D，r9 改为同族族 C 三种子口径是正确处置。
4. **★ STA 计数口径对账（`scratch/reconcile_sta_counts.py`）**：`n_candidate_sta_runs` == `len(trials)` 即论文口径。§4.3 的 **3363** = 18 电路合计 3259 + **b17 的 180 s 重跑目录 `20260908_phase2_b17_resume/b17`（= 104）**（与正文"104 次候选级 STA 测量内取得 +0.38 ns"自洽）；表 12 的 **4044** = 同一 18 电路 + **b17 默认批次（785）**。差异**纯由 b17 目录选择造成**，均可追溯；`state.budget.sta_runs`（3401）**非**论文口径。
5. **落地 5 项（全部零算力）**：① **新增 §3.4 特征设计动机**（`sec:feature_motivation`）——逐项说明式 (2) 的边界/尺寸/验证/扇出/深度特征对应的预布局 ECO 风险，不引入公式证明，声明权重取固定值（默认 $1.0$）；顺带把原 §3.4 类型化失效归因顺延为 §3.5。② **新增 表 4** `tab:feature_motivation`（特征 ↔ 式 (2) 项 ↔ ECO 风险）。③ **§2.2 补整段「为什么无法直接定量比较」**（结构重映射依赖布局后负载与备用单元布局 / 逻辑补丁以 SAT·CEC 而非 WNS 为判据 / B/G 物理优化含学习驱动需训练环境与商用或内部流程）+ **表 2** `tab:baseline_cmp`。④ **§4.4 第二组补引导句 + 表 11** `tab:runtime`（族 D 三臂：固定权重 **4146 次/2010.8 s**、EMA 自适应 **4883/2065.3 s**、随机排序三种子均值 **5624/2460.3 s**；结构化较随机少 **26.3%** 次、少 **18.3%** 墙钟）。⑤ **§5 结论补失效统计句**（F4 占候选级评估 **60.2%**，与表 12 一致）。
6. **3 处硬编码 `§3.5` 改 `\S\ref{sec:validation}`**：插入 §3.4 后 §3.5 顺延，硬编码会失准（全库仅此 3 处，跨 2 行，已逐一核对指代同一小节）。
7. **质量门与终检**：**9 → 10 页** / 0 Error / 0 Overfull hbox / 0 Underfull hbox / **0 Overfull vbox** / 0 undefined refs；`??`=0；逐页行数 `[52,68,65,74,35,60,67,68,72,52]`；表/图引用覆盖 **14/14 + 3/3**、编号阅读顺序 **1..14 / 1..3 全递增**（**加固版探针 `scratch/float_order_probe2.py`** —— 按 `.tex` 的 `\caption` 反查、按"最长可匹配数字前缀"解析编号，可排除行内引用与数字粘连）；论文 `.tex` `3bb99129…`；双副本 PDF 字节 SHA `6f27a08b…`；内容指纹 `96a2070f…`（poppler 25.07）。
8. **★ 版面调平（Overfull 归零，可复用经验）**：① 表 4「深度」行的不可断行数学 `$\lambda_c\,\mathrm{depth}/\mathrm{depth}_{\max}$` 撑破 `p{2.0cm}` → 列宽改 **1.3/2.6/3.0 cm**。② 余 `Overfull \vbox (0.95665pt)` 定位为 **`\balance` 末页（第 10 页）分栏溢出**：**试改 `\linespread{0.95→0.94}` 反而恶化至 1.55127pt**（证明行距不是正确杠杆，已回退）；**试注释 `\balance` 则全绿但末页右栏只剩 `[14]` 一条文献**（**正是 `\balance` 要防的缺陷 ⇒ 必须保留**）；最终**删除表 14 表注中与正文重复的一句**（释放 1 行）→ 全绿。③ 插入块曾引入 **60 处裸 LF**，已由 `scratch/fix_r10_eol.py` 归一化为纯 **CRLF 668/0**（`.tex` 必须纯 CRLF）。
9. **重冻结 v8（四要素）**：tag **`v2026-10-12-review-r10`** + 论文 tag **`faeco-paper-final-20261012b`** + `versions/v8/MANIFEST.sha256`（**117 条全 OK**，相对 v7 **仅 3 条变化** = `.tex` + 双副本 `.pdf`，114 条未变）+ `BASELINE_INDEX.csv` active 行（v7 → superseded）。
10. **台账收口**：`LOGS.md`（LOG-20261012-03/04）、`CHANGE_LOG.md`（r10 行）、`PAPER_EVIDENCE_MANIFEST.md` §6（新增"当前发布版 v8"，v7 降为"前序发布版"）、`OPEN_ISSUES.md`（**OI-021 按 Elsevier 政策复核 / OI-024 扩到六张表 / OI-025 记 v8 / OI-026 记为"已获算力授权" / OI-027 更新为 10 页 / 新增 OI-028 目标期刊改判**）、`.workbuddy/memory`。
11. **00_Summary 同步**：按用户 standing 约定同步作者版 PDF，SHA-256 与双副本一致（`6f27a08b…`）。

### 下一步（有明确指令再做）

- **OI-026（已获用户算力授权，"可以投入新的算力"）**：feature/cost 消融 —— **须先落方案**（`planning/`：消融臂定义 / 预锁定判据 / 族归属），再改 `code/src/rseco/flow.py:359/385` + `cut.py` 加候选源开关 + 单元测试，再跑 ISCAS89（估 **40–60 min**），结果入表并**重冻结 v9**。审稿人明示：补 runtime（已补）+ baseline 定位（已补）+ **feature 消融**可"明显提高一个档次"。
- **§七 大规模验证**（OpenCores / RISC-V 完整模块 / 工业规模 netlist）：需新基准接入 + 新算力；审稿人自注"不一定实现"。
- **OI-028 Integration 转化**：英文稿 + `elsarticle` 格式与投稿材料（中文稿作内容母本）；AIGC 披露按 Elsevier 政策复核（OI-021）。
- **绝对不要做**：① 不要删 `\balance`；② 不要把族 D 的数字与表 9/表 10 并表或交叉换算；③ 不要新增/修改任何既有数字（本轮已再次确认零数字改动）；④ 不要在正文插 `\FloatBarrier`；⑤ 不要改 `paper/zh/manuscript/` 里 `.tex` 的换行风格（必须纯 CRLF）。

## 2026-10-12 — 复审三·针对性增强（r9，零算力项）+ r8 文字复审并入：重冻结 v7

**本轮性质**：用户提供第三方审稿意见（总判断「**不建议大改方法，而做针对性增强**」；核心诊断 = **论文声称的贡献强度 > 实验已经证明的强度**；归档 `paper/zh/review_rounds/r9_20261012/comments.md`）。用户四则裁定：① 执行范围 = **只做零算力项**；② 摘要 = **改口径并压回 150 词**；③ 版面 = **等内容定稿再统一排**；④ 搜索效率（k₁st）指标 = **同源重算 + 弱化主张**。同时把上一轮「已改但未冻结」的 r8 文字复审（21 行）**并入本轮**。**零数字、零实验、零代码改动**。记录见 `LOGS.md` LOG-20261012-01/02 与 `CHANGE_LOG.md` 两行。

1. **新增三张表**（数字**全部由既有台账现算**：`scratch/build_r9_tables.py` → `review_rounds/r9_20261012/table_data.json`）：**表 5** 三测试集总体结果（8/8、18/19、2/3；ΔWNS 均值/中位 0.16/0.10、0.43/0.18、0.60/0.60；SEC 8/8、19/19、2/2）、**表 8** 首次取得改善所需的候选级 STA 次数（结构化排序 vs 随机排序三种子）、**表 9** F1--F6 触发次数（19 电路 / 4044 次，138/3/16/2434/915/0，F4 占 60.2%）。表 9 须先套 **OI-008 事件名映射**（工具层 `acceptance_budget_violation` ≡ 方法层 F4）才与 `PAPER_EVIDENCE_MANIFEST.md:38` 逐项一致。
2. **摘要口径**：「以记录失效并调整搜索参数」→「**作为搜索诊断与消融分析的依据**」（+ 一句消融负结果）；中 **228 字** / 英 **149 词**（压回 JCAD ≤150）。
3. **§1.3 三贡献重组**：贡献 1 补"统计特征（边界、候选规模、验证代价、扇出）+ 关键路径特征（覆盖、逻辑深度）"；贡献 2 明确「**搜索诊断与候选控制**…而非独立的收敛增益来源」；贡献 3 补"统一数据流"与分层验证次序。
4. **§3.6** 补「在实际运行中，总运行时间主要由候选级 STA 测量与最终 SEC 决定，单次最小割求解所占比例很小」。
5. **§4.1 补运行环境**：WSL2 / Ubuntu 24.04.4 LTS / 内核 `6.6.87.2-microsoft-standard-WSL2` / **AMD Ryzen 7 7435H** / WSL 可见 16 逻辑核与 15 GB 内存。
6. **★ §4.4 k₁st 主动纠错（本轮最重要的一处；非审稿人提出，系自查发现）**：原句把 **族 C 的 ΔWNS（0.40 ns）** 与 **族 D 单种子（seed 1）** 的首次改善次数（s713 5→216、s953 1→185）并列——**跨实验族 + 单种子**，而表注写"随机列为种子 1/2/3 的均值"，即**该句口径与它所引的表格自相矛盾**；族 D seed 2 下 s713=5、s953=1（与结构化排序**相同**），单种子会翻转结论。经用户裁定改为**同族族 C 三种子口径**并弱化（7 个有台账电路 6 个优于随机均值；种子敏感最大相差 7 倍；s713 相反），**结论页口径同步**。证据 `review_rounds/r9_20261012/k1st_audit.{md,json}`（逐条回原始 `candidate_trials` 校验，非解析产物）。
7. **§4.5 物理口径弱化 ×2**：标题句去"物理验证"；段末补「本节的物理结果为基于布局与全局布线寄生估计的**后验评估**…**不等同于对物理实现有效性的验证**」。
8. **★ 补齐 4 张表的正文引用（投稿硬伤；非审稿人提出）**：`scratch/check_env_refs.py` 审计发现 **表 4/5/9/11 零正文引用**（其中**表 4、表 11 属 v6 既有遗留**——机械终检只查 `??` 与未定义引用，**不报"未被引用的 label"**）。已在 §4.1/§4.3.1/§4.6 各补一句，表/图引用覆盖 **14/14**。
9. **r8 并入（21 行）**：表 3 F5 行改"当前配置的单候选验证时限"、表 4 F1--F6 行「仅轮内」→「启用」、§1.3 导语去宣传语、§2.1 窗口表述、§4.4 补对照条件；**图 2 图注 A/B → $P_w$/$P_c$ 并同步重绘 imagegen 图源 PNG**（顺带消除 v6 遗留的图文不一致）。期间自查并修复本轮自造的 Overfull hbox（表 4 中列回退为「启用」）。
10. **质量门与终检**：**9 页** / 0 Error / 0 Overfull / 0 Underfull / 0 Overfull vbox / 0 undefined refs；`??`=0；表 1--11 与图 1--3 **视觉顺序递增**（`scratch/float_order_probe.py`，按 `pdftotext -bbox-layout` 的 (页,栏,y) 判定）；14 `\bibitem` ↔ 14 `\cite` 且编号按首次引用顺序；双副本 PDF 字节 SHA `417398ab…`、内容指纹 `8c8fd2fd…`（poppler 25.07）；论文 `.tex` `4539efa4…`。
11. **重冻结 v7**：tag `v2026-10-12-review-r9` + 论文 tag `faeco-paper-final-20261012`（均 → 提交 `0602326`）；`versions/v7/MANIFEST.sha256`（**117 条全 OK**，相对 v6 **仅 3 条变化** = 论文 `.tex` + 双副本 `.pdf`）；`BASELINE_INDEX.csv` v6→superseded / v7→active；`PAPER_EVIDENCE_MANIFEST.md` §6 置 v7 为当前发布版。
12. **00_Summary 同步**：新增 `tools/sync_to_summary.py`（幂等 + staleness 守卫 + SHA-256 回读）与 `Makefile` 的 `summary` 目标；本轮已把作者版 PDF 同步到 `01_Papers/00_Summary/`（`417398ab…`）。

**不要做**：① ⚠ **Word 转排件仍是 v6 版**（摘要与三张新表未同步）——投稿前**必须**随管线重建（**OI-024**），且 `postprocess.py` 的摘要/关键词为**硬编码**，须先同步为 v7 文本；② **不要再往正文插 `\FloatBarrier`**（导言区已有注记）；③ 页数 8→9 属三张新表所致（末页 81 行**满页、非孤儿**），**版式压缩留待内容定稿后统一排**（**OI-027**），不得为此缩字号/行距/裁内容；④ 加权割（cost）消融**未做**（**OI-026**），若做需先给 `flow.py:359/385` 加候选源开关 + 单元测试 + ~40–60 min 算力；⑤ **图源 PNG 不在 manifest 覆盖内**（**OI-025**，117 条口径不含 `paper/zh/figures/`），图 2 重绘只能靠 git 回溯；⑥ v7 双 tag 为附注标签，取提交须用 `<tag>^{commit}`。

---
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
