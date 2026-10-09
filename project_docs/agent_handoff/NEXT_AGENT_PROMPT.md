# NEXT AGENT PROMPT

> 给下一位 agent 的完整提示词。**每轮结束前更新**。最后更新：2026-10-09（文字专项审稿全量落地轮 r7）。

```
你是 FAECO 仓库（D:\BaiduSyncdisk\01_Papers\03_FAECO）的新任执行者。请先按顺序阅读：

1. AGENTS.md（协作契约与规则）
2. project_docs/agent_handoff/README.md（阅读顺序）
3. project_docs/agent_handoff/START_HERE.md（当前状态与立即工作）
4. project_docs/agent_handoff/CURRENT_RUN_HANDOFF.md（只读最上一节 = 2026-10-09 文字专项审稿全量落地轮）
5. project_docs/evidence/PAPER_EVIDENCE_MANIFEST.md（动 .tex 前的强制门槛，含逐数字绑定）
6. project_docs/OPEN_ISSUES.md（未决问题必须知晓并如实告知用户）
7. paper/zh/submission/T20_SUBMISSION_PACKAGE.md（投稿检查单 + 决策点）
8. paper/zh/submission/JCAD_REQUIREMENTS_20260929.md（JCAD 要求核实报告）

【当前状态（一句话）】
OI-018~022 已全部拍板并执行；用户 2026-10-09 授权完成三次收敛——① **参考文献著录层修复**
（文献 19→14 条按正文首次引用顺序重排，修 P0；5 条纯 URL 工具/文档引用改正文页脚脚注），
② **摘要可读性改写**（用户反馈"技术要点过多、大同行难懂"：去 R/G/B/JOINT、F1--F6 等未展开术语，
改概念化 + 补动机；中 264 字·英 148 词），
③ **外部「文字专项审稿」P0+P1+P2 全量落地**（口径修正 / 贡献重组 / 术语统一 / §4.6 主张强度下调 /
正文去 `\FloatBarrier` 消除末页孤儿，9 页→8 页）——均零数字/零实验/零主张改动。
重冻结为 v6（tag `v2026-10-09-text-review` = `b1eee25`，内容指纹 `88b03403…` poppler 25.07 口径）——
**论文内容修改仍已终止**；Word 转排稿随管线再重建
（paper/zh/submission/word/FAECO_投稿Word转排_20261009c.docx，旧三批归档 superseded/）；
补充材料 S1–S5 初稿完成。剩余仅投稿手工项（MathType/占位/图 2 通栏/终稿 PDF/AIGC 披露）与审稿修稿轮。

【本轮目标（按优先级）】
1. 等用户完成 Word 稿手工收尾（word/转排说明.md）：MathType 批量转换（OMML→MathType）、
   黄色占位替换（通信作者 */基金/收稿日期/作者简介）、图 2 通栏、终稿 PDF 导出；
   完成后须重算 Word 件哈希并更新 T20_SUBMISSION_PACKAGE.md §3。
2. 投稿时必办：AIGC 使用披露（OI-021，JCAD 硬要求，未披露视为抄袭）——用户拍板暂缓，
   届时与通信作者共同拟定；作者承诺书/保密审查（单位流程）；作者工作邮箱确认。
3. 若审稿意见返回：以 project_docs/review_history/paper_audit/
   consistency_audit_20260911.md 为数字基线，并先读 PAPER_EVIDENCE_MANIFEST.md，
   只处理新意见；新增内容修改须先取得用户同意（含 1-C 小节插入，OI-018 已拍板留修稿轮）。

【约束 / 不要做】
- ❌ 不要修改论文内容（含摘要）——用户冻结令；Word 转排稿中的摘要改写也须 OI-020 授权。
- ❌ 不要用 PDF 字节 SHA256 断言"内容一致"——用内容指纹：
     pdftotext -layout <pdf> - | sha256sum
- ❌ 不要跨实验族拼数字。铁律 same claim ⇒ same revision + same config family；
   8/8、18/19、2/3 三元组全属族 B；ITC-99 严格改善 = 18/19（b06 TNS 辅助接受单独声明）。
- ❌ 不要缩字体/行距/砍内容压页——双栏下 `\FloatBarrier` 会退化为 `\clearpage`（v6 正文已移除，仅留图 2 后一处）；版面异常优先调浮动体参数，勿再插入 `\FloatBarrier`。
- ❌ 未拍板前不发询问邮件、不启动 Word 转排、不插 1-C 小节。
- experiments/ 证据目录严禁删除；paper/zh/figures/fig_iscas89.pdf 是编译依赖，亦禁删。
- 未跑测试不修改 code/src/rseco/。
- 环境异常：pytest 报 import 错误先 .venv\Scripts\python.exe -m pip install -e .

【论文构建与验收（照抄）】
  cd paper/zh/manuscript
  lualatex -interaction=nonstopmode "FAECO_面向预布局门级时序ECO的结构化候选搜索与失效归因.tex"   # 跑两遍
  python ../scripts/checks/latex_quality_gate.py        # Errors/Overfull/Underfull 须全 0，PAGES 应为 8
  cp "FAECO_....pdf" ../FAECO_....pdf                   # 同步双副本，二者 SHA256 须一致
  pdftotext -layout "FAECO_....pdf" - | sha256sum        # 内容指纹（当前 88b03403…）
  # 质量门的 "Undefined: 5" 是字体替身警告，不是引用未解析；判引用看 '??' 计数。

【完成标准（证据门）】
- [ ] OI-018~OI-022 用户拍板并按选择执行。
- [ ] Word 转排稿（若启动）：按官方 2026 模板，转排稿 SHA256 与来源 LaTeX 版本
      登记回 T20_SUBMISSION_PACKAGE.md §3。
- [ ] S1–S5 补充材料定稿（初稿已完成）并经用户确认。
- [ ] 全套交接文档同步更新并 commit（LOGS.md、WORK_PROGRESS.md、
      status_logs/CURRENT_STATUS.md、TASK_BOARD.md、CURRENT_RUN_HANDOFF.md、
      START_HERE.md、NEXT_AGENT_PROMPT.md、OPEN_ISSUES.md）。
```

两点使用提示：

- 若上下文有限，**只读 1/3/4/5/6 五项即可接手**——其余信息在 `CURRENT_RUN_HANDOFF.md` 与 `T20_SUBMISSION_PACKAGE.md` 里都有链接。
- JCAD 要求的完整核实（费用、流程、2026 新规）在 `paper/zh/submission/JCAD_REQUIREMENTS_20260929.md`，官网抓取原始证据在 `scratch/jcad_research/`（git-ignored）。
