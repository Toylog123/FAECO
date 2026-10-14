# NEXT AGENT PROMPT

> r21 Git收口：实现提交 `e592bfd`、SVG导出规范化提交 `483b5e9` 已成功推送 `origin/main`（2026-10-14）。本轮审稿/配图/计数修复已完成，后续只处理保留的未决项；下文Git待办措辞为推送前记录。

> 给下一位 agent 的提示词。最后更新：2026-10-14（r22_20261014，进行中）。当前指令以下节为准。

## 当前接手提示（r22）

按AGENTS和本目录README阅读当前状态/交接、EXPERIMENT_REGISTRY、OPEN_ISSUES与EXPERIENCE。r22起始main clean/HEAD与origin-main `46ede94`，母稿为r21已验收工作修订，12页/793394B/c65169b7…。

用户最新“继续推进吧那就”授权恢复OI-031逐臂配置和OI-034计数审计，并推进同运行器的新族双割/cost消融；之后推进英文elsarticle、投稿材料、Word必要性和最终排版。新授权覆盖旧消融暂缓，r21不新EDA与不启动Word仅描述历史轮范围。

先复用旧证据，明确可分离性与因果归因的反驳条件；独立开关/TDD通过后锁新族revision、预算、类型、接受、初态、输入/种子和正负判据，再正式开跑。当前只有PLAN-R22-CUT-COST规划，尚无正式新EDA/结果。不得跨族拼接C旧数，不预先写“有效”或假定旧4–5h预算。

所有正式实验必须前登记配置、后登记证据与实际结果，长任务超时/监测。缺历史flags不猜测，缺旧schema不补零。OI-030/031/034继续保留；OI-032/033已修范围保持。阶段commit+push依AGENTS由主线执行。

## r21已完成提示（历史；旧暂缓不作为r22当前指令）

你接手 FAECO 仓库 `D:\BaiduSyncdisk\01_Papers\03_FAECO`。按 AGENTS 和本目录 README 阅读 START_HERE、CURRENT_STATUS、TASK_BOARD、CURRENT_RUN_HANDOFF 最上一节，再查证据 manifest、OPEN_ISSUES 与 EXPERIENCE。

本轮用户授权审稿、配图修改/增加及必要图注/引用调整。五视角模拟审稿和复核已交付，综合 Major Revision；图 1/2 重绘、图 4～7 新增、图 3 沿用。C 的运行器/JOINT 混杂/TNS/多提交已披露；D 从原始台账剔缓存重建真实 STA B(k) 并加表列；B 的 3363/664/104 改称评估记录，b17 实际数未知，不写零或猜测全是新测量。

本轮已验收稿 12 页/7 图/14 表/21 引用，质量项全零；逐页视觉/源字形/40账本审计通过，双PDF及作者版三份一致，文档与记录已完成。阶段 commit+push 待主线执行并另记真实 Git 结果；后续以最新交接与QA为准。

**本轮为 r21 工作修订，不冻结 v19；v18 保持不可变参考。** OI-030 双割独立因果证据、OI-031 C 逐臂配置/历史复现、OI-034 其他族计数语义仍开放；OI-032/033 的披露与计数修复已完成，不将其完成误读为所有科学缺口闭合。

不新跑 EDA，cost/feature 消融、大规模验证、Word 继续暂缓；1-C 不擅自插入。复用优先，数字实查，不跨族拼表，不删除证据。阶段完成同步相关记录并按当前 AGENTS commit+push，旧“等用户明确 push”为历史状态。

## r20/v18 历史提示（不作为 r21 当前指令）

```
你是 FAECO 仓库（D:\BaiduSyncdisk\01_Papers\03_FAECO）的新任执行者。请先按顺序阅读：

1. AGENTS.md（协作契约与规则）
2. project_docs/agent_handoff/README.md（阅读顺序）
3. project_docs/agent_handoff/START_HERE.md（当前状态与立即工作）
4. project_docs/agent_handoff/CURRENT_RUN_HANDOFF.md（只读最上一节 = 2026-10-13 学术叙事收敛 r20（13 处改写））
5. project_docs/evidence/PAPER_EVIDENCE_MANIFEST.md（动 .tex 前的强制门槛，含逐数字绑定）
6. project_docs/OPEN_ISSUES.md（未决问题必须知晓并如实告知用户）
7. paper/zh/submission/T20_SUBMISSION_PACKAGE.md（投稿检查单 + 决策点）
8. project_docs/planning/FAECO_R11_SUBMISSION_POLISH_PLAN_20261012.md（r11 精修方案 + 消融设计 + 投稿材料清单；目标期刊已改投 Integration，JCAD 旧核实见 paper/zh/submission/JCAD_REQUIREMENTS_20260929.md）

【当前状态（一句话）】
**r20（本轮最新）= 用户对作者版(7) = v17 的第五轮通读意见：学术叙事收敛轮**（非外部审稿、非技术修改、**不增实验**）：
用户判断「这一版的整体框架已经基本正确，主线比之前清晰很多」，本轮**「已经不是『需要重构』，而是『需要最后一次学术叙事收敛』」**；
唯一核心 = **Candidate exploration under limited verification budget**（有限验证预算下的候选探索）；
要求**强化「候选探索」为唯一主线**，让加权割（扩大候选空间）/ $C_c$（提高关键路径覆盖）/ R/G/B/JOINT（候选类型）/
ranking（降低搜索成本）/ F1–F6（理解搜索失败）/ SEC·SPEF（保证候选可靠性）都围绕该主线服务。
用户裁定 3 项：核心问题句 = **替换为新句**；贡献结构 = **2 条贡献 + 平台段落**；§4.1 边界句 = **删除**。
落地 **13 处叙述层改写**：E1/E2 摘要核心思想句（CN/EN）；E3 §1.1 核心问题句替换；
E4 §1.3 贡献分层（引导句改「主要贡献」/ 贡献① 核心、② 辅助 / 原第③条移出 enumerate 改为独立「实现与验证平台」段落）⇒ **2 条贡献 + 1 平台**；
E5 §3.3.3 末去防御 + 失效反馈弱化；E6a/b/c 全篇「更新搜索参数」→「搜索分析的输入」（含 §4.5 计划外第 4 处）⇒ 全篇 0 残留；
E7 §4.5 标题改「预布局候选筛选的物理相关性分析」（label 不变）；E8 §5 结论收束句强化；Edel 删 §4.1「不等同于完整时序收敛」边界句。
**零数字（词级 token 比对：数字/引用键 0 差异，`\命令` 差异仅 `\item` 6→5、`\textbf` 83→81）/ 零实验 / 零代码 / 零参考文献**；摘要 CN 372→410 汉字、EN 217→241 词。
重冻结 **v18**（tag `v2026-10-13-narrative-convergence-r20` + 论文 tag `faeco-paper-final-20261013i`，
双副本 PDF `1ebb2864…` 2,610,131 B，**11 页** 0/0/0/0、页数与 v17 相同；内容指纹 `63e62c52…`）。
**v11 + v12 + v13 + v14 + v15 + v16 + v17 + v18 均尚未推送 origin**（按惯例等用户指令）。
前序 **v17**（r19 论文定位重构，tag `v2026-10-13-positioning-r19`，指纹 `42bfb149…`，11 页）**亦未推送**；
前序 **v16**（r18 图 2 机制图替换，tag `v2026-10-13-fig2-update-r18`，指纹 `c5fa3f26…`）**亦未推送**；
前序 **v15**（r17 逻辑一致性精修，tag `v2026-10-13-logic-calibration-r17`）**亦未推送**；
前序 **v14**（r16 术语一致性与 claim 强度校准，tag `v2026-10-13-terminology-calibration-r16`，指纹 `f8437a73…`）**亦未推送**；
前序 **v13**（r15 全篇去防御化编辑，tag `v2026-10-13-defensive-purge2-r15`）**亦未推送**；
前序 **v12**（r14 去防御化重构，tag `v2026-10-13-defensive-purge-r14`）**亦未推送**；
**v11**（r13 大同行入口改写，tag `v2026-10-13-abstract-broaden-r13`）**亦未推送**；
**v10**（r12 一致性 pass，tag `v2026-10-12-pre-submission-consistency-r12`，指纹 `c7b4d807…`）**已推送**（`main` = `origin/main` = `b1403d9`）。
——**均零数字/零实验/零代码改动**。**目标期刊已由 JCAD 改投 Integration, the VLSI Journal（OI-028）**；
**审稿人连续两轮否决**补做 cost 消融、用户亦裁定**暂缓**。
剩余 = 英文稿/`elsarticle` + 投稿材料（OI-028）、Word 转排件重建（OI-024）、AIGC 披露按 Elsevier 复核（OI-021）。

【本轮目标（按优先级）】
1. **OI-028 投 Integration**：以中文稿为内容母本产**英文稿** + `elsarticle` 格式 + 投稿材料
   （cover letter / highlights ≤85 字符 / graphical abstract）；英文标题已定锚。
2. **OI-024**：Word 转排件仍为 v6 版，缺 **r8–r20** 全部改动（标题/摘要/术语 + 六张表 + r12 的 15 处文本改动 + r13 的摘要两段与 §1.1 引言改写 + r14 的 10 处 + r15 的 11 处 + r16 的 17 处 + r17 的 12 处 + r18 的图 2 替换 + r19 的 12 处定位重构 + r20 的 13 处叙事收敛）——
   投稿前**必须**随 `scratch/word_convert/` 管线重建；`postprocess.py` 的标题/摘要/关键词为硬编码，
   须先同步为 v18 文本并把输入路径改为新稿名。
3. 投稿必办：**OI-021 AIGC 使用披露**改按 **Elsevier** 政策复核；作者承诺书/保密审查；英文长摘要。
4. 若审稿意见返回：以 project_docs/review_history/paper_audit/
   consistency_audit_20260911.md 为数字基线，并先读 PAPER_EVIDENCE_MANIFEST.md，
   只处理新意见；新增内容修改须先取得用户同意（含 1-C 小节插入，OI-018 已拍板留修稿轮）。
5. **暂缓（用户裁定 + 审稿人连续两轮否决，勿擅启）**：OI-026 cost/feature 消融（**非投稿前置条件**）、§七 大规模验证、OI-027 版式压缩。

【约束 / 不要做】
- ❌ 不要修改论文内容（含摘要）——用户冻结令；Word 转排稿中的摘要改写也须 OI-020 授权。
- ❌ 不要用 PDF 字节 SHA256 断言"内容一致"——用内容指纹：
     pdftotext -layout <pdf> - | sha256sum
- ❌ 不要跨实验族拼数字。铁律 same claim ⇒ same revision + same config family；
   8/8、18/19、2/2 三元组全属族 B；ITC-99 严格改善 = 18/19（b06 TNS 辅助接受单独声明）；
   PicoRV32 = 2/2（第三子模块无 setup 路径、不计入分母，r12 已统一）。
- ❌ 不要缩字体/行距/砍内容压页——双栏下 `\FloatBarrier` 会退化为 `\clearpage`（v6 正文已移除，仅留图 2 后一处）；版面异常优先调浮动体参数，勿再插入 `\FloatBarrier`。
- ❌ 不要删 `\balance`（末页分栏平衡承重件，删则末页右栏只剩一条文献）；不要改 `.tex` 换行风格（**必须纯 CRLF**）；**manifest 必须 LF-only**（`.gitattributes` 已锁 `versions/*/MANIFEST.sha256 text eol=lf`，写完须用 `open(..., newline="\n")`）。
- ❌ 未拍板前不发询问邮件、不启动 Word 转排、不插 1-C 小节。
- experiments/ 证据目录严禁删除；paper/zh/figures/fig_iscas89.pdf 是编译依赖，亦禁删。
- 未跑测试不修改 code/src/rseco/。
- 环境异常：pytest 报 import 错误先 .venv\Scripts\python.exe -m pip install -e .

【论文构建与验收（照抄）】
  cd paper/zh/manuscript
  lualatex -interaction=nonstopmode "FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex"   # 跑两遍
  python ../scripts/checks/latex_quality_gate.py        # Errors/Overfull/Underfull 须全 0（PAGES 当前 11）
  cp "FAECO_....pdf" ../FAECO_....pdf                   # 同步双副本，二者 SHA256 须一致
  pdftotext -layout "FAECO_....pdf" - | sha256sum        # 内容指纹（当前 63e62c52…）
  # 质量门的 "Undefined: 5" 是字体替身警告，不是引用未解析；判引用看 '??' 计数。

【完成标准（证据门）】
- [x] r20 学术叙事收敛（13 处叙述层改写）已落地，v18 已冻结（tag `v2026-10-13-narrative-convergence-r20`）；
      论文内容已定稿（r12 的 M1–M5 + r13 摘要/§1.1 + r14 去防御化 + r15 全篇去防御化 + r16 术语/claim 校准 + r17 逻辑一致性精修 + r18 图 2 替换 + r19 定位重构 + r20 叙事收敛均已完成）。
- [ ] Word 转排稿（若启动）：按官方 2026 模板，转排稿 SHA256 与来源 LaTeX 版本
      登记回 T20_SUBMISSION_PACKAGE.md §3。
- [ ] S1–S5 补充材料定稿（初稿已完成）并经用户确认。
- [ ] 全套交接文档同步更新并 commit（LOGS.md、WORK_PROGRESS.md、
      status_logs/CURRENT_STATUS.md、TASK_BOARD.md、CURRENT_RUN_HANDOFF.md、
      START_HERE.md、NEXT_AGENT_PROMPT.md、OPEN_ISSUES.md）。
```

两点使用提示：

- 若上下文有限，**只读 1/3/4/5/6 五项即可接手**——其余信息在 `CURRENT_RUN_HANDOFF.md` 与 `T20_SUBMISSION_PACKAGE.md` 里都有链接。
- 目标期刊已改投 **Integration, the VLSI Journal**（OI-028）；JCAD 旧要求核实见 `paper/zh/submission/JCAD_REQUIREMENTS_20260929.md`（历史参考），Elsevier / Integration 要求待补。官网抓取原始证据在 `scratch/jcad_research/`（git-ignored）。
