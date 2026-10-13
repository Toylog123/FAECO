# Work Progress

本文件按**倒序**记录每一轮工作（最新在上）。完整正序日志见 `LOGS.md`。

## 2026-10-13 大同行入口改写（r13：摘要 + §1.1 引言）：重冻结 v11

- **做了什么**：**用户直接指定的大同行入口改写（摘要 + §1.1）**（非外部审稿），裁定「**摘要应该改**——这是当前版本最值得做的最后一处"非技术性增强"」：现摘要对 EDA 小同行清楚，但对 **Integration 这类期刊的大同行入口偏窄**（缺"为什么 ECO 重要 / 为什么需要这个阶段 / 为什么已有方法不够"）。**仅改中/英摘要两段**，按「**大背景 → 具体问题 → 方法 → 结果 → 意义**」重排：补首句大背景 + 次句 ECO 定位 + 第三句收窄到预布局门级时序 ECO；方法句补「关键路径覆盖割」使中英对称；末句并入"意义"。**`.tex` diffstat 2 insertions / 2 deletions（恰 2 行替换）**。
- **★ 与用户草案 5 处偏离（逐条取证）**：① 术语「工程变更**优化**」→「工程变更**命令**」（ECO = Engineering Change **Order**；§1.1 正文原文即如此）；② **保留** r12 M2 分母解释句（审稿人 ★★★★ 指定落点）；③ **保留** r6「其余无退化」（P0 边界声明；加入大背景句后更不可删）；④ 去「快速探索」无据修饰；⑤ 末句补"意义"。**遵从用户自我约束**：不写"先进制程"（用"集成电路规模与设计复杂度持续提升"）；摘要仍无第一人称。
- **关键结果**：**10 页（不变）** / 0 Error / 0 Overfull / 0 Underfull / 0 Overfull vbox；`??`=0；表/图引用 **17/17**；浮动体顺序 1..14 / 1..3；`.tex` `8fccfab0…`（62,936 B；668 CRLF / 0 bare LF）；双副本 PDF `a720829b…`（2,773,302 B）、内容指纹 `65e29b84…`（poppler 25.07）；tag `v2026-10-13-abstract-broaden-r13` + 论文 tag `faeco-paper-final-20261013b`；`versions/v11/MANIFEST.sha256` 117 条全 OK（相对 v10 恰 3 条变化）。**零数字、零实验、零代码改动**。摘要长度：中文 244→**349** 汉字、英文 164→**214** 词（原 JCAD ≤300 字/≤150 词规则随改投失效，新约束记 OI-028 复核）。**v11 尚未推送 origin**（按惯例等指令）。
- **★ 本轮自造事故**：改写脚本 `raw.decode()` 未归一化即 `replace("\n","\r\n")` ⇒ **668 处 `\r\r\n`** ⇒ LuaLaTeX 视为额外换行 ⇒ **83 Errors / 2 Overfull / 11 页**；`count("\r\n")` 与 `count("\n")-count("\r\n")` 无法检出（仍 668/0）。`scratch/fix_r13_eol.py` 修复后全绿。
- **下一步**：**待用户裁定 §1.1 引言入口是否同补大背景**；OI-028 投 Integration（英文稿 + `elsarticle` + 投稿材料；英文摘要 214 词须按作者指南复核上限）；OI-024 Word 转排件仍 v6（缺 r8–r13 全部改动）须随管线重建；OI-021 AIGC 披露按 Elsevier 政策复核；OI-026 cost 消融**审稿人两轮否决 + 用户暂缓**。

## 2026-10-13 投稿前一致性 pass（r12）：第五份外部审稿 M1–M5 + 重冻结 v10

- **做了什么**：用户粘贴**第五份外部审稿**（「投稿前最后一轮审稿人视角」，对 v9 / 作者版 10 页；归档 `paper/zh/review_rounds/r12_20261013/`），评分 = 问题价值 9 / 方法完整性 8 / 创新表达 8 / 实验完整性 8 / **证据一致性 7** / Integration 匹配度 8.5；**最大风险 = 可读性风险**（审稿人能否理解「哪个实验验证哪个机制」）。用户裁定 **「不要再加实验。做一次 Submission consistency pass」**（仅 M1–M5）。落地：**M1** 表 5 ITC-99 行 SEC `19/19`→`18/19` + 表注声明拆分口径（正文自始 28/29 = 8+18+2，表 5 是唯一漏改处）；**M2** PicoRV32 `2/3`→`2/2` + 分母解释（摘要 CN/EN、§4.3、结论、表 5 共 5 处）；**M3** 表 11 表注补「**两个 STA 计数口径不同**」；**M4** 贡献 1 弱化 `1.07 ns` ↔ 加权割绑定；**M5** §3.4 正文 ×3 + 表 4 行 ×3 措辞降调；另按审稿人「问题 2」§4.4 开头补「第一组不单独隔离式 (2) 各特征项」句。**`.tex` diffstat 15 ins / 15 del（15 处替换）**。
- **关键结果（本轮最重要取证 M3）**：**论文存在两个不同的 STA 计数器** —— `state.budget.sta_used`（`search_state.py:254` `reserve_budget`；检查点 `flow.py:591`）为**每轮迭代预约、迭代边界判顶**的预约计数（逐电路 ≤500，**random 三种子在 s420/s641 触顶** `stop_reason=sta_budget`）；`n_candidate_sta_runs`（`run_outerloop_real_wns.py:437` = `len(trials)`）为**候选级 STA 测量次数**（论文口径，逐电路最高 1321）⇒ 表 11 的 **4146/4883/5624 不受 500×8 约束、数字无需更正**。**质量门**：**10 页（不变）** / 0 Error / 0 Overfull / 0 Underfull / 0 Overfull vbox；`??`=0；表/图引用 **17/17**；浮动体顺序 1..14 / 1..3；`.tex` `c5828999…`（668 CRLF / 0 bare LF）；双副本 PDF `4ef380f7…`、内容指纹 `c7b4d807…`（poppler 25.07）；tag `v2026-10-12-pre-submission-consistency-r12` + 论文 tag `faeco-paper-final-20261013`；`versions/v10/MANIFEST.sha256` 117 条全 OK（相对 v9 恰 3 条变化）。**零数字、零实验、零代码改动**（`19/19→18/19`、`2/3→2/2` 属口径统一）。**已推送 origin（2026-10-13，用户指令）**：`main` = `origin/main` = `b1403d9`，v10 双 tag 已上远端。
- **下一步**：OI-028 投 Integration（英文稿 + `elsarticle` + 投稿材料）；OI-024 Word 转排件仍为 v6 版（缺 r8–r12 全部改动）须随管线重建；OI-021 AIGC 披露改按 Elsevier 政策复核；OI-026 cost 消融**审稿人再次否决 + 用户暂缓**（非投稿前置条件）。


## 2026-10-12 投稿前精修轮（r11）：标题 / 摘要 / 贡献定位 / 术语与语言风险 + 重冻结 v9

> ⚠ 说明：r8/r9（v7）、r10（v8）两轮未在本文件登记，详见 `LOGS.md`（LOG-20261012-01~04）与 `CURRENT_RUN_HANDOFF.md`。本节从 v9 起恢复登记。

- **做了什么**：用户提供「投稿前精修」六阶段方案，经取证核验后裁定三项（① 中英标题定稿；② cost 消融暂缓；③ Step 1 立即执行）。落地 **7 组改动**：中/英标题定稿（`Candidate Exploration and Failure Characterization…` / 「面向预布局门级时序 ECO 的候选探索与失效刻画」）+ 摘要 CN/EN 重写 + §1.3 贡献 1/2 重写（贡献 3 保留）+ 术语统一（失效归因→失效刻画、结构化排序→候选排序 ×7）+ 结论末句改写（不留"未取得独立收益"式收尾）+ §2.2 比较焦点句 + 3 处语言风险修正；**主稿文件随标题改名**（`.tex` + 双副本 `.pdf`，同步 live pointer 文件；历史记录保留旧名）；新增 `.gitattributes` 强制 `versions/*/MANIFEST.sha256` 为 LF。
- **关键结果**：**10 页 / 0 Error / 0 Overfull / 0 Underfull / 0 Overfull vbox**；`??`=0；表/图引用覆盖 **17/17**；浮动体编号阅读顺序 1..14 / 1..3；`.tex` `22de39a0…`（668 CRLF / 0 bare LF）；双副本 PDF 字节 `f642e533…`、内容指纹 `3832eeb2…`（poppler 25.07）；tag `v2026-10-12-submission-polish-r11` + 论文 tag `faeco-paper-final-20261012c`（= `e00315a` **终态**；r11 收尾时已用 `git tag -f` 由 `daba5ab` 重指）；`versions/v9/MANIFEST.sha256` 117 条全 OK（相对 v8 恰 3 条变化）。**零数字、零实验、零代码改动**（纯文字与定位）。
- **下一步**：OI-028 投 Integration（英文稿 + `elsarticle` + 投稿材料）；OI-024 Word 转排件仍为 v6 版须随管线重建；OI-021 AIGC 披露改按 Elsevier 政策复核；OI-026 cost 消融**暂缓**。

## 2026-10-09 文字专项审稿全量落地轮（r7）：重冻结 v6 + 末页孤儿修复 + Word 稿重建

- **做了什么**：用户提供外部**文字专项审稿**（`paper/zh/review_rounds/r7_20261009/comments.md`）并授权全部执行。① 逐项核验后经用户拍板 4 项（摘要方向 / A\* 披露 / 执行范围 / §4.6 口径）；② 一次性落地 **P0×5 + P1×6 + P2×3 + 术语统一**（`.tex` 共 60+ 处替换，逐处唯一性校验，全程保持纯 CRLF）；③ 摘要按审稿方向重写（中 228 字 / 英 148 词）；④ 修复文字收敛引入的**末页孤儿**（删正文 10 处 `\FloatBarrier` + 去重精简 7 处 → 9→8 页）；⑤ 重冻结 v6 + Word 转排稿重建（并修正 b 稿摘要漏同步的管线缺陷）；⑥ 台账/交接同步。
- **关键结果**：**8 页 / 0 Error / 0 Overfull / 0 Underfull**；`??`=0；`\bibitem`↔`\cite` 14/14 且编号按首次引用顺序；字节 SHA `09197e5f…`（双副本一致）、内容指纹 `88b03403…`（poppler 25.07）；tag `v2026-10-09-text-review` + 论文 tag `faeco-paper-final-20261009c`；`versions/v6/MANIFEST.sha256` 117 条全 OK。**零数字、零实验改动**（仅 §4.6 主张强度下调）。
- **下一步**：投稿手工/流程项（MathType 批量转换、黄色占位替换、图 2 通栏、终稿 PDF；⚠ OI-021 AIGC 披露）；Word 引擎导出的 PDF 若由用户在本机生成，须回填 `T20_SUBMISSION_PACKAGE.md` §3 的两处新哈希。

## 2026-10-09 摘要可读性改写轮：去术语 + 重冻结 v5 + Word 稿再重建

- **做了什么**：用户反馈"摘要太多技术要点、难让大同行看懂"并授权改写。**摘要两段 + §1.1 引言首段**：① 删 R/G/B/JOINT、F1--F6、多特征加权割、关键路径覆盖割、违例扇入锥、简化 SPEF 复测、独立全网表顺序等价检查、纯 G、WNS/TNS 等**未展开机制名与缩写**，改概念化表述；② 首句补"为什么重要"（时序 ECO 在芯片设计中的位置 + 预布局阶段约束）；③ 结果层保留 8/8、18/19、2/3、1.07 vs 0.16 与"无实例退化/尚未达到完全时序收敛"边界；④ 英文摘要同步改写（维持无第一人称）。重编译 → 重冻结 v5 → Word 转排稿随管线再重建（postprocess 摘要串同步）。
- **关键结果**：9 页 / 0 Error / 0 Overfull / 0 Underfull；`??`=0；中文 **264 字**（原 298）、英文 **148 词**（原 150），均合规；PDF 字节 SHA `5c37725a…`（双副本一致）、内容指纹 `0a2b0723…`；tag `v2026-10-09-abstract-plain` + 论文 tag `faeco-paper-final-20261009b`（提交 `1c67f50`）；`versions/v5/MANIFEST.sha256` 117 条全 OK（相对 v4 变动 3 条）。**零数字、零实验、零主张改动**——正文/公式/图表/参考文献未动；正文刻意保留机制名（摘要给大同行、正文给同行）。
- **下一步**：投稿手工/流程项（用户 Word 收尾 + ⚠ OI-021 AIGC 披露 + 承诺书/保密审查/英文长摘要）。

## 2026-10-09 参考文献修复轮：重排文献表 + 重冻结 v4 + Word 稿重建（用户授权方案 A）

- **做了什么**：用户授权方案 A（修 `.tex` 源头 → 重冻结 v4 → Word 重建，涉冻结文件）。① **P0**：`thebibliography` 按正文首次引用顺序由 19 条重排为 **14 条**（原首处引用渲染 `[1,7,9]`，18/19 条错位，违反 JCAD 规范一.1）；② 5 条纯 URL 工具/文档引用（picorv32/yosys/OpenSTA/skywater-pdk×2）按规范一.12 改 `\footnote{\url{…}}` 正文页脚脚注，消除文献表序号占用与 `liberty`/`sky130` 的 bibitem-cite 不匹配；③ P1/P2：`[C]//`→`[C] //`（11 条）、`Integration` 全称、BUFFALO 题名补全 "via Group Relative Policy Optimization"、kravets 页码 `1-6`→`71:1-71:6`、`[Z]` 类型移出、DOI `_` 转义（`6\_5`）；④ 重编译 + 质量门；⑤ **重冻结 v4**（manifest 117 条全 OK，`BASELINE_INDEX.csv` v3→superseded）；⑥ Word 转排稿随管线重建（preprocess 守卫 19→14，pandoc 生成 5 条 Word 原生脚注，Word 引擎导出 8 页），旧稿归档。
- **关键结果**：**9 页 / 0 Error / 0 Overfull / 0 Underfull**；`??`=0；正文无 `[15]`–`[19]`；PDF 字节 SHA `dea21bb3…`（双副本一致）、内容指纹 `6ca972d5…`（poppler 25.07）；tag `v2026-10-09-reference-fix`（投稿就绪）+ 论文 tag `faeco-paper-final-20261009`。**零数字、零实验、零正文主张改动**——仅文献表与引用呈现形式。
- **下一步**：投稿手工/流程项 —— 用户 Word 手工收尾（MathType/占位/图 2 通栏/终稿 PDF，须重算 Word 件哈希）、⚠ OI-021 AIGC 披露（JCAD 硬要求）、承诺书/工作邮箱/保密审查/英文长摘要。

## 2026-10-09 文档同步轮：v3 交接文档对齐 + Word 件哈希登记

- **做了什么**：① 提交 09-30 遗留的 v3 同步批（`5bc0e7d`：LOGS-07 + CURRENT_RUN_HANDOFF v3 节 + T20 锚点 + Word 转排稿随管线重导出）；② 实测复核冻结完好——`versions/v3/MANIFEST.sha256` 117/117 OK、PDF 双副本字节 SHA `28647dc0…`、内容指纹 `70bbd610…`（poppler 25.07）、v3 双 tag 经 `^{commit}` 解析均 = `26f4f3b`；③ 刷新 `START_HERE.md`（HEAD/指纹/tag 由 09-29 旧值 → v3）、`CURRENT_STATUS.md`（补本轮 + 09-30 终审轮）、`TASK_BOARD.md`（T20 行 → v3）、`NEXT_AGENT_PROMPT.md`（v2 → v3）、`.codex-handoff.json`（全字段刷新）、T20 包 §0/§3；④ 登记 Word 转排件字节 SHA256 到 T20 包 §3。
- **关键结果**：main = `5bc0e7d`（论文 v3 tag 仍 = `26f4f3b`）；**未动论文内容、未动代码**；文档与仓库实态对齐。
- **下一步**：投稿手工/流程项 —— 用户 Word 手工收尾（MathType/占位/图 2 通栏/终稿 PDF）、检查单 #3 参考文献核对、⚠ OI-021 AIGC 披露、承诺书/保密审查/英文长摘要。

### 追加：T20 检查单 #3 参考文献核对（2026-10-09）

- **做了什么**：抓取 JCAD 官方《参考文献规范》原文，对 19 条文献做逐条事实核验（IEEE/ACM/dblp/出版社）+ 规范合规比对，报告落 `paper/zh/submission/REFERENCE_AUDIT_20261009.md`。
- **关键结果**：无虚构文献；**发现 1×P0 —— 编号未按正文引用顺序（首处渲染 `[1,7,9]`，18/19 错位）**；5×P1（`[C]//` 缺空格 11 条 / 4 条网址类待定 / Integration 非全称 / BUFFALO 题名截断 / `[Z]` 类型）；4×P2。19 条全英文 → 双语著录规则不适用。修复方案（重排 `.tex` → 重冻结 v4 → Word 重建）**待用户授权**，未动论文。
- **下一步**：等用户对是否修冻结 `.tex` 拍板。

## 2026-09-30 终审修正轮：5 处正文修正 + 重冻结 v3（内容修改终止）

- **做了什么**：用户终审确认前 4 项已改对，提出最后 5 处正文一致性修正（零数字、零实验）：§3.4 F6 交叉引用纠错（§4.4→§4.5）/ §4.1 接受准则闭合 b06 TNS 辅助接受例外 / 摘要（中英）PicoRV32 分母解释（`picorv32_regs` 无 setup path 不参与判定；中文 298 字、英文 150 词）/ 表 8 补 $\Delta L$、$\Delta_{\mathrm{WNS}}$ 符号定义 / §4.5 F6 措辞对齐"启用式反馈"。Word 转排稿随管线同步重建，Word 引擎重导出 8 页。
- **关键结果**：9 页 / 0 Error / 0 Overfull / 0 Underfull / 0 引用警告；字节 SHA `28647dc0…`（双副本一致）、内容指纹 `70bbd610…`；**重冻结 v3**（tag `v2026-09-30-submission-ready-r2` = `26f4f3b` + 论文 tag `faeco-paper-final-20260930-r2`，manifest `versions/v3`，117 条；v2/v1 superseded）。**用户明示"改完即停止内容修改、不加任何实验"。**

## 2026-09-30 投稿执行轮：五项拍板落地 + 摘要适配重冻结 v2 + Word 转排完成

- **做了什么**：① 用户拍板 OI-018~022（1-C 留修稿轮 / 直接转排 / 摘要授权且同步冻结版 / AIGC 暂缓 / 维持 manifest 默认）；② OI-020 执行——中英摘要按 JCAD 规则改写（295 字 / 149 词，去第一人称），其余正文零改动；**重冻结 v2**（tag `v2026-09-30-submission-ready` = `4dc16c6`）；③ OI-019 执行——Word 转排三件套（`paper/zh/submission/word/`：docx + Word 引擎导出 PDF + 转排说明），管线 = 引用字面化预处理 → pandoc（OMML）→ python-docx JCAD 版式；**本机 Microsoft Word 实测 8 页全对**；④ 方正免费字体四款经 AUR SHA256 校验装为用户级字体。
- **关键结果**：论文未动（v1/v2 冻结版与既有 manifest 未变）；Word 转排件为可溯源新制品（哈希见 T20 包 §3）。

## 2026-09-30 补充材料成文轮：S1–S5 全部初稿完成

- **做了什么**：`paper/zh/submission/supplementary/` 成文 S1（失效事件名映射，**闭合 OI-008 投稿前必办项**）/ S2（实验族与可复现性，脱敏）/ S3（SEC 逐实例，29 PASS + 1 N/A = 30）/ S4（环境工具链）/ S5（基准来源许可）；更正两处过时表述（OI-008 两层命名分工、manifest SEC 行 22→29+1）；补建 PicoRV32 source manifest。
- **关键结果**：论文未动（内容指纹仍 `7adf0279…`）；代码未改；S1–S5 初稿待用户确认。

## 2026-09-29 决策轮：D-01~D-03 落地 + RESULTS.md 对齐 + T20 启动

- **做了什么**：① 用户拍板 D-01=A / D-02=A / D-03=A，T20 目标期刊=JCAD；② D-01 落地——`versions/v1` 轻量冻结（manifest 117 条全 OK 自校验 + tag `v2026-09-29-submission-ready` = `d84061a`，已 push），并实测发现 3 个论文数字源证据文件（`20260826_aggregation/summary.json` 等）此前未被 git 跟踪，现由 manifest 锁定；③ D-02/D-03 台账结案（OPEN_ISSUES「已决」表 + 决策简报注记）；④ `experiments/RESULTS.md` 对齐论文终稿口径——实查修正 ISCAS89/ITC-99/PicoRV32 中位数（+0.10/+0.18/+0.60）与 ITC-99 success 口径（18/19 严格改善），b06 补 TNS 辅助接受事实；⑤ T20 投稿包骨架落 `paper/zh/submission/`（检查单 + cover letter 草稿 + 补充材料清单），JCAD 官方要求调研进行中；⑥ 1-C 评估完毕：代码侧已实现并过 gate，剩余动作是论文插入小节，与内容冻结冲突，待用户拍板。
- **关键结果**：main = `d84061a` + 4 个 tag 上 origin；论文未动（仍 9 页冻结版，内容指纹 `7adf0279…`）；RESULTS.md 三处数字错误已修正并与 `summary.json` 对账一致。
- **下一步**：JCAD 调研回填检查单 → S1–S5 补充材料成文 → 用户决定 1-C（插入论文 / 留到修稿轮）。

## 2026-09-29 论文终稿收敛 + 仓库收敛 + 版面收尾（详见 `agent_handoff/handoff_20260929.md`）

- **做了什么**：终稿审稿三批修改（评审 15 项优先 7 项 `681841a`、第二轮 10 项 `0ea80b6`、必改 4 项 `a8142b6`）；版面两次修复回 9 页（根因均为双栏下 `\FloatBarrier` 退化 `\clearpage`）；删除 81 个历史 `.tex` 与 82 个历史 PDF（删前均先入库固化）；发布冻结 tag `faeco-paper-final-20260929`，机械终检全过（0 `??`、29 label 唯一、19 bibitem ↔ 19 cite）。**用户明确要求停止论文内容修改。**
- **关键结果**：9 页 / 0 Error / 0 Overfull / 0 Underfull；PDF 字节 SHA256 `9af41d77…`（双副本一致）、内容指纹 `7adf0279…`。

## 2026-09-14 交接整理收尾

- **做了什么**：核查交接文档体系，发现并补齐三处缺口：上轮交接文档变更未提交（本轮 commit+push）、`NEXT_AGENT_PROMPT.md` 为空模板（已补全：目标=D-01~D-03 落地 + T20、约束、证据门）、`.codex-handoff.json` 时间戳过期（已刷新，read_order 补入决策简报）；核查 versions/v1/ 为模板占位（与待 D-01 决策一致）。
- **关键结果**：pytest 264 passed + 4 skipped（环境验证通过）；全套交接文档提交推送，仓库随时可无口头交接。
- **下一步**：不变——用户拍板 D-01~D-03 → 执行决策 → T20 投稿件打包。

## 2026-09-12（下午）决策简报 + 交接收尾

- **做了什么**：为 OPEN_ISSUES 中三项待决策事项（versions/v1 冻结、机制图、DOI/DRC）核实最新事实并编写决策简报 `agent_handoff/DECISION_BRIEF_20260912.md`；刷新 OPEN_ISSUES（OI-001 降级：主稿无 DOI 占位符；OI-006 重定义：当前 9 页稿仅 3 图，原拆分问题已消失；新增 OI-007 hold limitation 记录）与 TASK_BOARD（U26-06/U26-08 关闭、U26-07 部分完成、新增 D-01~D-03 决策项与 T20 投稿打包任务）；重建全套交接文档。
- **关键结果**：三项决策均有明确建议（轻量冻结 / 维持 3 图 / 维持如实声明+按需 rebuttal），用户拍板后下一轮即可执行。
- **下一步**：用户读简报做 D-01~D-03 决策 → 执行（tag+manifest / 无动作 / 关闭对应 OI）→ T20 投稿件打包。

## 2026-09-12 框架架构迁移 + 环境重建 + 旧副本清理

- **做了什么**：robocopy 全量复制仓库（316,765 文件 / 117.7 GB / 0 失败）至 `D:\BaiduSyncdisk\01_Papers\03_FAECO`，git 历史与远程保留；按 99_项目模板重组织（code/、project_docs/、data/raw/benchmarks/、scratch/、顶层契约）；路径修复（pyproject、12+ 硬编码脚本、19+12 测试锚点）；交接文档重建。随后 `.venv` 用 Python 3.11.9 重建并装依赖；C 盘 3 个 git worktree 删除（分支先推送固化、未提交文档抢救归档）；旧目录全删。
- **关键结果**：pytest 264 passed + 4 skipped 全绿；check_project.sh PASS；live 文件旧路径残扫 0；main 与 origin 同步（35fd558 → f5b6380）。
- **映射全记录**：`migration/MIGRATION_20260912.md`。

## 2026-09-11 第 18 轮审稿修订 + 全文一致性审计

- **第 18 轮**（3d984c6）：接手中断会话的未提交修订（SEC 口径细分、b17 预算披露、benchmark 纳入规则、tab:configs、SPEF 公式、F6 降强），修正幽灵引用/重复段落/配置表事实错误；排版债清零（0 Overfull，9 页）。
- **一致性审计**（d329f19）：修复 8 处正文与实验产物的矛盾（策略分布、b21 +2.75、3363 次 STA、b06 声明、b18/b19 归属、SEC 计数 5 处口径、随机种子、pcpi_mul +0.07）；审计记录 `review_history/paper_audit/consistency_audit_20260911.md`。

## 2026-09-08 ~ 09-09 实验补齐与结果汇总（摘要）

b17 phase-2 重跑（+0.38 ns / 104 STA / SEC 12812+1 unproven）；joint-depth 消融；hold-mode ITC-99（诚实 limitation）；multi-iter ablation 与 --no-early-stop 修复；`experiments/RESULTS.md` + `results.json` 顶层汇总。详见 `LOGS.md`。

（2026-08-11 ~ 08-13 的 17 轮命名版审稿史、2026-08-26 unified-loop 主实验、更早 N31 系列见 `LOGS.md` 与 `review_history/paper_audit/`。）
