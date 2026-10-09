# 未决问题追踪（Open Issues）

> 未解决的问题必须登记于此；**只要未解决就持续保留**，每轮检查进展。
> **未解决的问题必须告知用户，不得隐瞒或淡化。**

## 已决（2026-09-29 用户拍板；选项与依据原文见 `agent_handoff/DECISION_BRIEF_20260912.md`）

| ID | 问题 | 决策 | 落地动作 | 后续 |
|----|------|------|----------|------|
| OI-003 | versions/v1 基线冻结方案 | **A 轻量冻结** | tag `v2026-09-29-submission-ready`（提交 `d84061a`）+ `versions/v1/MANIFEST.sha256`（117 条全 OK 自校验通过）+ `BASELINE_INDEX.csv` active 行；已推送 origin | 期刊若要求证据打包，再按 D-01=B 补 |
| OI-006 | 机制图处置 | **A 维持现状** | 无动作（9 页稿 3 图布局维持，"4 图拆分"问题不存在） | 投稿后视审稿意见再定 |
| OI-001 | DOI | **A 投稿时按期刊模板补** | 无正文动作（主稿无 DOI 占位符） | 已列入 T20 投稿检查单 |
| OI-002 | DRC signoff | **A 维持如实声明** | 无动作 | Magic/KLayout 补跑留作 rebuttal 备选（OI-002 备选路径保留） |
| OI-018 | 1-C（增量 ECO 小节）插入时机 | **留到修稿轮**（用户 2026-09-30 拍板） | 无动作（§12.2 文本继续留待贴；冻结令维持） | 修稿轮随审稿意见一并插入，届时重走质量门 + 重冻结 |
| OI-019 | JCAD Word 转排路径 | **不问邮件、直接转排**（用户 2026-09-30 拍板） | `draft_email_to_jcad.md` 作废不用；按官方 2026 模板启动 Word 转排 | 转排产物见 `paper/zh/submission/word/`；MathType 环节需用户本机配合 |
| OI-020 | 摘要改写授权 | **授权且同步冻结版**（用户 2026-09-30 拍板） | **已执行（v2，2026-09-30）**：中文摘要压至 295 字去第一人称、英文压至 149 词；重编译 9 页 / 0/0/0；重冻结 v2（`v2026-09-30-submission-ready`，新指纹 `43becd39…`，v1 superseded）。**后续同一授权下的可读性改写（v5，2026-10-09）：中 264 字 / 英 148 词，重冻结 v5（`v2026-10-09-abstract-plain`）。再续（v6，2026-10-09）：随文字专项审稿采纳审稿人摘要，中 228 字 / 英 148 词** | 详见 `CHANGE_LOG.md` 2026-09-30 与 2026-10-09（摘要）行 |
| OI-021 | AIGC 使用披露 | **暂缓**（用户 2026-09-30 拍板） | 无动作；检查单保留该必办项 | ⚠ 投稿时必须解决（JCAD：未披露视为抄袭），建议届时与通信作者共同拟定 |
| OI-022 | 3 个证据汇总文件 git add | **维持默认：不入 git，由 manifest 锁定**（用户未改默认） | 无动作 | `versions/v1、v2/MANIFEST.sha256` 均含此 3 文件 |
| OI-023 | 外部「文字专项审稿」（9 页稿）全量落地 | **用户 2026-10-09 授权「全部执行」（P0+P1+P2，约 20–30 处）** | **已执行并重冻结 v6**（tag `v2026-10-09-text-review` = `968f9a1`；论文 tag `faeco-paper-final-20261009c`）：口径修正 / 贡献重组 / 术语统一 / §4.6 主张强度下调并令表 8 算式闭合（0+36+90=126）/ A* 披露按审稿人删除 / 正文去 `\FloatBarrier` 消除末页孤儿（9 页→8 页）；**零数字、零实验、零新增主张** | 逐项处置见 `paper/zh/review_rounds/r7_20261009/{comments,response,README}.md`；未采纳项的驳回理由（图 2 caption A/B 因已烘入 PNG）亦记录在案 |

**附带发现（2026-09-29，D-01 执行时实测）**：`experiments/20260826_aggregation/summary.json`（论文主数字源）、`ablation_summary.json`、`20260826_sec/summary.csv` 此前**未被 git 跟踪**（与决策简报"git 已跟踪聚合 summary"的描述不符）；现由 `versions/v1/MANIFEST.sha256` 锁定完整性。是否纳入 git 跟踪待用户确认。

### 长期教训（跨轮，2026-10-09 r7 归纳；已同步 `docs/EXPERIENCE.md`）

1. **双栏论文正文禁插 `\FloatBarrier`**：`placeins` 的 `\FloatBarrier` 在双栏模式下遇待排浮动体会**退化为 `\clearpage`**，造成栏底留白、正文后移、**参考文献被挤成孤儿末页**。压页/版面异常应优先调浮动体参数，**禁缩字体/行距/砍内容**。本稿 v6 正文已移除（仅保留图 2 后一处用于约束全宽浮动体）。
2. **Word 转排管线含硬编码摘要**：`scratch/word_convert/postprocess.py` 的 `zh_abs`/`en_abs`/关键词/标题/作者为**硬编码**，不从 `.tex` 读取。改摘要后若只改 `OUT` 路径，会产出**旧摘要**的 Word 稿（v5 轮即发生：`…20261009b.docx` 实为 v4 摘要文本）。**改摘要后必须同步硬编码块并重跑整条管线**（preprocess → pandoc → postprocess → Word 导出）。
3. **内容指纹必须用可复现命令、并跨文档回验**：口径 = `pdftotext -layout <pdf> - | sha256sum`（原始输出，**不**去空白；poppler 25.07）。本轮发现 v6 指纹 `91034fee…` 系误值——用 v5 PDF 反推口径（复现 `0a2b0723…`）后，规范脚本对 v6 稳定给出 `88b03403…`，遂更正 11 个文件（含 `PAPER_EVIDENCE_MANIFEST.md` §6、`versions/v6/README.md`、T20 包）。**字节 SHA ≠ 内容指纹**；指纹值跨文档传播时必须回验。

## 待用户拍板（2026-09-29 决策轮新增；**2026-09-30 已全部拍板完毕**，决议见上方「已决」表 OI-018~OI-022）

> 本节保留作为决策过程记录：OI-018 = 留修稿轮；OI-019 = 直接转排（不发询问邮件）；OI-020 = 授权且同步冻结版（已执行）；OI-021 = 暂缓（投稿时必须解决）；OI-022 = 维持默认（manifest 锁定、不入 git）。S2 表述粒度默认"不列具体开关名"。

## 进行中 / 未解决

| ID | 问题 | 发现日期 | 状态 | 影响 | 尝试过 | 下一步 | 阻塞 |
|----|------|----------|------|------|--------|--------|------|
| OI-004 | 实验目录磁盘占用（历史瘦身残留） | 2026-08-28 | blocked（用户声明不删） | experiments/ 共 116 GB / 122 目录（itc99_main 19G、phys_closure 2.6G 等） | 已清理 STA 中间日志 + 旧仓库副本全删（2026-09-12） | INVENTORY 的 cleanup-candidates 档位待用户逐项确认；实验证据严禁删 | 用户 |
| OI-005 | 旧目录空壳 `D:\BaiduSyncdisk\03_FAECO` | 2026-09-12 | 基本关闭 | 内容已全删（含旧 .venv、C 盘 3 个 worktree；3 条 codex 分支已推送固化） | robocopy 校验 + 全量删除 | 会话关闭后空壳若仍在，手动删除即可 | 无 |
| OI-007 | hold 模式跨测试集效果有限 | 2026-09-08 | 记录在案（不阻塞投稿） | 14 电路仅 b01 改善 min_slack；已写入论文 limitation | 单 patch 无法同时改善 setup+hold | 未来工作（多目标 hold/setup 联合搜索） | — |
| OI-008 | 论文表 F1/F6 反馈动作描述与代码实现不一致 | 2026-09-23 | **论文侧已修正**（2026-09-23）；**S1 补充说明已成文并更正本条两处过时表述**（2026-09-30） | 三处差异已按代码事实修正论文 8 处表述（另 F4 行措辞统一，共 9 处）；已发表数字不受影响 | 逐行对照 `refinement.py` + `git show 216a118` 溯源 + 实测产物统计；**2026-09-30 复跑探针复核**（19 电路 / 4044 trials 分布逐项一致） | **【2026-09-30 更正】** ① 本条原记"当前 `code/` 已无旧事件名字符串"已过时：0a 步骤 4 合并（`258f588`）后，`real_wns.py:1864` 的运行器**仍以 `acceptance_budget_violation` 写试验台账**——故产物与现行代码在事件层**一致**，真正的差异是"工具层事件名 vs 方法层 F4 分类名"的两层命名分工（`failures.py` 的 `FailureType` 承担归因）；② 该两层对应关系已成文为投稿补充材料 `paper/zh/submission/supplementary/S1_失效事件名映射说明.md`，**"投稿前建议在补充材料说明"事项就此闭合**；③ "反馈的独立贡献"隔离实验已由 L2 三臂 + k=1 判别完成（见 OI-012），残余事项仅剩 S1 的转 Word 排版 | 投稿流程（随补充材料提交） |
| OI-009 | **Algorithm 1 的"不叠加"描述与主实验实际行为矛盾** | 2026-09-23 | **论文侧已修正**（2026-09-23） | 论文 Algorithm 1 第 250 行称"各轮候选均相对固定基线 $G_0$ 评估，不叠加多个局部补丁"，但实测 `base_netlist_hash` **逐轮内唯一、跨轮变化**（b01 8 轮 9 个基准 / b03 9 个 / b04 8 个 / b05 8 个），且变化发生在**接受轮之后**（b01 iter1 接受 1 个 patch → iter2 基准哈希改变）——**主实验实际为逐轮累积叠加**，仅"效率优先配置"（sprint1）为单轮不叠加。§4.3 对 PicoRV32 的"由 R/G/B 多类接受补丁叠加形成"表述反而与实测一致，与 Algorithm 1 自相矛盾 | 探针 `scratch/probe_base_hash2.py`（逐 trial 校验：同轮内哈希唯一、跨轮改变）；`20260805_tcad_sprint1_iscas89` summary `iterations=1` | **已改**：Algorithm 1 重写为"从**当前网表** $N$ 提取锥 → 接受后 `$N\gets N+\Delta$` 提交为下一轮基准 → 同轮候选共享同一基准且互不叠加 → 该轮一旦提交，基于旧基准的其余候选作废"；并拆出失败反馈为独立步骤；算法后补"候选按轮提交…效率优先配置仅执行单轮，不产生累积叠加"。遗留：把该行为与 OI-011 的 codex 实现（`SearchState.accept_patch` / `refreshed_cone`）对齐到同一层级描述 | OI-011 已定案（路径 B）；本项复核并入实施步骤 0a（`SearchState` 落权威布局） |
| OI-010 | 论文 §4.2 的 ISCAS89 策略分布与实测不符 | 2026-09-23 | **已闭合（2026-09-28 晚）：⚠️ 原判「两族均不支持该映射」系本人解析错误——该分布本就有据；A\* 重跑改为「可复现性限制」证据** | §4.2 称"JOINT 对应 s27/s382/s420/s953，G 对应 s641/s713/s832，R 对应 s820"（4 JOINT + 3 G + 1 R）。**两套 ISCAS89 运行都不支持该映射**：① `20260826_iscas89_main` 实测 **G 23 次/7 电路（s27/s382/s420/s641/s713/s832/s953）、R 4 次/2 电路（s641、s820）、JOINT 0、B 0**；② 图 4 源 `20260805_tcad_sprint1_iscas89` 的 `eval_trials.json` 为旧格式（多对象拼接、非严格 JSON，即 20260806-16 修掉的写盘 bug），无法直接统计，其 `summary.json` 仅记 3 个电路（s953/s832/s820，`iterations=1`）。**并且 §4.2 的数据集归属本身存疑**：§4.2 称"图 4 对应效率优先配置（最大 1 轮 + 首改进即停）"，但 `20260826_iscas89_main/summary.json` 显示 `iterations: 8`、`wns_history` 长度 3–7（多轮累积）；`20260805_tcad_sprint1_iscas89/summary.json` 却为 `iterations: 1`。`RESULTS.md` §2 的 strategy 列同源同错（"JOINT 是主要增益来源 4/8"） | 探针 `scratch/probe_iscas89_dist.py`、`scratch/probe_iscas89_two.py`、`scratch/probe_sprint1_dist.py`；两套 summary.json | **【2026-09-28 裁定：选 A】** §4.2 该段所有量（WNS / strategy distribution / accepted patch / STA count / 图表）**必须全部来自同一 efficiency-first / sprint1（`iterations=1`）实验族**；`20260826`（`iterations: 8`）是另一算法运行状态，**只能用于多轮/收敛类实验**。sprint1 缺字段 ⇒ **重跑 sprint1，不得从 20260826 借值**。原则：`same claim ⇒ same code revision + same config family`。**本轮不改该句（避免编造）**：需用户先裁定 §4.2 以哪套运行报告——(A) 效率优先/Tcad-sprint1 口径（则需重跑或从旧格式产物恢复策略分布，并解决其 summary 仅 3 电路的问题）；(B) 20260826 口径（则 §4.2 的策略分布改为 G 7/8 电路、R 2/8 电路、JOINT 0，并把"效率优先/1 轮"表述改为与 `iterations: 8` 一致）。定案后一并同步 `RESULTS.md` §2 | 用户（投稿前） |
**▲【2026-09-28 晚 · 更正与闭合】** 该条原判据（"两套 ISCAS89 运行都不支持该映射"）**不成立，系本人的解析错误**：图 4 源族 `20260805_tcad_sprint1_iscas89` 的 `eval_trials.json` 确为"多对象拼接、非严格 JSON"，但**只要用 `json.JSONDecoder().raw_decode(…)[0]` 读第一个对象**即可拿到 `call_log[0].accepted.kind`——逐电路结果为 **JOINT{s27,s382,s420,s953} / G{s641,s713,s832} / R{s820}**，**恰好就是 §4.2 所写的 JOINT 4 / G 3 / R 1**；且**独立印证**：A′ 族 `20260807_real_pr_iscas8/manifest.json` 的 8 条候选标签（`029_JOINT_JOINT`、`001_JOINT_JOINT`、`089_JOINT_JOINT`、`000__101__G`、`000__085__G`、`002__121__R`、`002__140__G`、`006_JOINT_JOINT`）**逐条与之一致**。此前之所以误判，是因为把该文件按单对象 `json.load` 读取、`JSONDecodeError` 被 `try/except` 静默吞掉（探针输出 `{}`）而未察觉。⇒ **结论：§4.2 的策略分布不需替换、不需从任何族"借数字"**；原裁定"A 口径 + 重跑补齐"的**方向保留**（§4.2 全部量仍须同属 efficiency-first 族 ✓），但**"重跑"的用途改变**。
**重跑（新族 A\* `experiments/20260928_sprint1/`，git HEAD `6b95f8c`，与 A 同配置）实测**：8/8 电路仍严格改善，但**候选序列漂移**——接受类型分布变为 **G 6 / JOINT 1（s382）/ R 1（s820）**；s382 候选级 STA 2→41、s420 90→66。⇒ 该结果**只作"族 A 在冻结 revision 下不可复现"的可复现性限制**写入 §4.2 的「族与可复现性」段，**不替换 A 的历史数字**（替换即等于"从其他实验族借数字"，正是本条要防的错误）。A\* 的 8 个 `final_patch_id` 与族 B（`20260826_iscas89_main`）**逐电路完全相同**，说明 A\* 实为族 B 流水线的第 1 轮切片，不是族 A 的重现。
**方法论教训（已写入 skill `doc-evidence-number-consistency`）**：判"某台账不支持某结论"之前，必须先确认**能够读到该台账**；`json.load` 抛 `Extra data` 只说明它不是单对象 JSON，不说明字段不存在。**禁止用被 `try/except` 兜住的解析失败作为"无证据"的依据。** | 已闭合 |
| OI-011 | **main 分支 `code/` 不是产出论文主实验产物的实现（代码谱系分叉）** | 2026-09-23 | **已裁定路径 B；G2/G3/G4 已冻结；0a 步骤 2–5 已实施并过 gate（`a12ecab`/`9ac06bf`/`258f588`/`870d062`/`9870abc`/`1777a78`），**等价门 24/24 × 3 电路全 PASS**；**legacy regression 步骤 6 亦通过：8 个 ISCAS89 电路（s27/s382/s420/s641/s713/s820/s832/s953）**8/8 × 24/24 全等**（含 bookkeeping），报告 `reports/FAECO_LEGACY_REGRESSION_20260923.md`，下一阶段 L2 Adaptive 解除阻塞 | 产物侧字段 `base_netlist_hash`/`acceptance_evidence`/`sta_provenance`/`topology_metrics`/`cache_key`/`config_hash` 在 **main 的 `code/` 全 0 命中**；产出实现在 `codex/faeco-unified-loop` 分支（`flow.py:483` 建 `SearchState`、`:684` 接受后 `refreshed_cone=extract_fanin_cone(...)`、`:726` 调 `accept_candidate`；`real_wns.py:784 accept_candidate` 内 `self.mapped_text=str(text)`）。main 侧 `flow.py:392` 锥只抽一次、`real_wns.py:197` 后 `mapped_text` **永不更新** → **main 无逐轮累积行为**。谱系 `merge-base=b8c3759 (08-13)`，main 在 08-14~09-07 无提交（恰跨 20260826 主实验期）。**任何阶段 1 实验若在 main 上跑，数字与论文不可比。必须最先处置。** | `git log -S` 检索产物字段（限 `-- "*.py"`）；`codex/faeco-unified-loop:src/rseco/{flow,real_wns,refinement_loop}.py` 逐行对照 | **路径 B 已定**：`SearchState` 为**唯一运行时状态所有者**（详见 `planning/FAECO_V2_TECH_DESIGN_20260923.md` §2）。实施步骤 0a：把 `SearchState` 体系落到权威布局，增持 `FailureFeedbackState`/`cone_limit`/`round_id`；`rollback()` 需同时回滚 EMA 与 cone_limit；以 3 电路 sentinel 复跑复现既有数字（或如实记录差异）。**配套前置 G2/G3/G4 已冻结**：状态更新契约 / checkpoint+`netlist_epoch` 契约 / `W_*`→F1–F6 映射 → `planning/FAECO_V2_IMPL_CONTRACT_20260923.md`。**0a 第一阶段不得改变算法行为**，gate = 等价报告六项全等（候选顺序 / F1–F6 序列 / 每轮权重 / 接受补丁 / 最终 WNS / STA 次数）。另须修一处既有缺口：`candidate_hash` 不含基准网表，多轮去重会误杀（改 `candidate_key = sha256(netlist_hash ‖ candidate_hash)`）。**实施与 gate 结论（2026-09-23）**：步骤 2 EMA 反馈（`a12ecab`）→ 3 `SearchState`+checkpoint+G2/G4（`9ac06bf`）→ 4 codex 能力合并（`258f588`）+ 09-12 路径修复（`870d062`）→ 5 等价门。报告：`reports/FAECO_0A_EQUIVALENCE_20260923.md`。**gate 结果：codex `9435846` vs main `fcdf06b`，`s382`/`b03`/`b06` 三电路均 24/24 项全等（E1–E6 全 PASS），回归 411 passed/4 skipped，算法行为未变**。已获硬证据：`experiments/20260826_iscas89_main/s382/s382/outerloop_result.json` 的 `state` 键集与 codex `SearchState.to_dict()` 完全一致 → §8.3「基线 = codex 谱系」由推断升级为实测。**A5 已裁定**：产物为串行 `--workers 1` + 内层 `early_stop=True`；runner 默认保留 `True`，旧口径"首次接受即停"写作 `--max-patches 1`。**附带钉住产物配置**：ISCAS89 主实验用 `--candidates-per-iteration 1`（s382 因此 24/24 精确复现），且批次启用 `--tns-aware` | **0a 已完成；下一步 L2 Adaptive（$\rho=0.5$）** |
| OI-012 | **论文 §4.4 表 6 的"失效反馈开/关"对照在运行器层面不成立** | 2026-09-23 | **论文侧已修正**（2026-09-23） | §4.4 原称"以**禁用 F1–F6 失效反馈**、保持权重固定的纯 G/纯 B/随机为基线，与**启用失效反馈**的 20 轮混合策略比较"。**证据链三重闭合**：(a) 表 6 四列均出自 `code/scripts/run_hybrid_repair.py`（混合列由 `20260807_multiround_8c_067/run_all.bat` 证实），该脚本**不使用** `refine_weights`/`RefinementWeights`/`enable_feedback`；(b) 该脚本输出 schema 与四列产物完全一致（`rounds_history` + `candidate_sta_before_round/after_round`、`random_order`、`seed`、`improvement`）；(c) 表 6 混合列 8/8 电路与 `20260807_multiround_8c_067/convergence_summary.json` **逐值精确吻合**（0.28/1.00/1.54/1.63/1.33/0.99/0.57/1.25，均值 1.074），纯 G 列均值 0.161 亦同源。→ 四列**都无 F1–F6 反馈**，该表实际对比"候选空间 + 排序启发式"。**附带修正三处**：表注"随机列与混合列共享 R/G/B/**JOINT** 候选类型"不成立（随机列实测 B 7154/G 3114/R 1954，**JOINT 0**）；`tab:configs` 中"20 轮收敛"列的 `F1--F6 失效反馈 = 轮内 + 跨轮` 无依据；**表 6 三列基线所用的 `20260826_ablation_pureG/pureB/random_seed{1,2,3}` 目录顶层运行脚本 0 个**（.bat/.sh/.md/.log 全无），调用命令未归档 | `code/scripts/run_hybrid_repair.py`（imports + 输出 schema grep）、`20260807_multiround_8c_067/run_all.bat` 与 `convergence_summary.json`、`20260826_ablation_*/hybrid_result.json`、探针 `scratch/probe_ablation_cfg{,2}.py` | **已改**：§4.4 首段重写为"比较候选空间与候选排序两类设置"并明示"各列由同一固定权重运行器产生、不构成失效反馈的开关对照，失效反馈的独立贡献需另设对照实验量化"；表标题改为"候选空间与候选排序设置的 WNS 改善对比"；表注改为"纯 G/纯 B 列分别只生成 G/B 候选，随机列与混合列在混合候选空间生成候选（混合列另含 JOINT 组合候选）…各列均使用固定搜索权重、不启用 F1--F6 权重重整"；`tab:configs` 20 轮收敛列反馈行改为"不启用（固定权重）"并在表注说明。遗留：**核心主张 Failure-Aware 目前仍无有效对照**，须由 `planning/FAECO_V2_DESIGN_PLAN_20260923.md` §2 的三臂实验补齐（且须归档运行命令 + 在结果 JSON 记录 `enable_feedback`）。**2026-09-24 三臂实验已完成整改与补齐**：运行命令归档（`run_config.json`：argv+resolved args+git head+臂身份）与结果 JSON 的 `enable_feedback`/`feedback_config` 均已落地（提交 `6e44fae`→`6276cff`）；三臂 × 8 电路结果见 `reports/FAECO_L2_THREEARM_20260924.md`——**§6.4 行 ③ 命中：EMA 失效反馈在 k=8 混合候选 regime 下无独立贡献**（8/8 电路终点/k₁st/maxB(k) 与 fixed 全等，4 电路多花 9%–116% STA），价值定位回退到「候选空间 + 权重排序」（random 臂 k₁st 恶化 1–2 个数量级为对照证据）。**遗留**：k=1（隔离反馈 regime）的 fixed vs adaptive 补充对未跑，L2 最终判读待用户裁定 → **2026-09-24 k=1 判别实验已完成，L2 封板**（`reports/FAECO_L2_K1_DISCRIMINANT_20260924.md`）：8/8 电路逐位相同、top-1 候选身份 0 次改变（EMA 高频触发且权重漂移可观但低于割评分 top-1 重排阈值）→ 按预锁定判据 EMA 降级为可选机制、不调 ρ/η；论文表述拆分为「候选空间+权重排序」+「失败归因（诊断）」，对照实验义务（运行命令归档 + enable_feedback 记录 + 开关对照）已全部履行 | 用户（投稿前补实验） |
| OI-013 | **20260826 批次产物只能部分由 codex HEAD 复现（revision 未钉死）** | 2026-09-23 | **已裁定（2026-09-28）：选 A —— 认当前冻结 HEAD；已打 tag `faeco-exp-rev1` → `87d01ba`** | 0a 步骤 5 做对照时顺带验证产物可复现性：**`s382` 完全复现（24/24，含 `n_candidate_sta_runs=22`）**，但 **`b03` 仅 12/24、`b06` 仅 8/24**，且差异落在 decision core（非仅计数）：`b03` 产物 `-1.27`（8 轮每轮接受）vs HEAD/`30f4164` 给 `-1.21`；`b06` 产物 6 个 `--tns-aware` 接受（TNS -3.98→-3.92，`stop=max_iterations`）vs HEAD 无接受（`stop=stagnation`）。**已排除**：环境（Yosys `0.67+146` 与产物 `map.log` 逐字相同）、参数复原方法（s382 已 24/24）、束宽（b03 在 k=1 与 k=8 结果相同）、HEAD 特有（`3e93fd2`、`30f4164` 两处 worktree 定点重跑 b03 仍 `-1.21`）。**2026-09-24 更新（legacy regression 配置 A 的附带检查，`reports/FAECO_LEGACY_REGRESSION_20260923.md` §8）**：ISCAS89 批次用配置 A（k=1、**无** `--tns-aware`）在 **7/8 电路 decision-reproducible**（`s27/s382/s420/s641/s713/s820/s953`，其中 `s713`/`s820` 仅差一个 `E6.n_candidate_sta_runs` 计数），唯一例外 **`s832` 为"路径不同、终点相同"**（最终 `wns=-1.16`/`tns=-5.48`/`final_patch_id`/`final_netlist_hash` 全等，仅接受轮次 1–3 vs 1–4 不同）。**且实测 `--tns-aware` 只属 ITC-99 批次**：s382 不含该开关复现 24/24，含该开关首轮接受点 `-0.88→-0.98`、匹配度降至 11/24（已登记为契约修订 A8） | `code/scripts/compare_0a_equivalence.py`；产物时间戳（`s382 11:22 / b03 11:25 / b01 11:29 / b06 11:51`）对照 08-26 当天 7 个落在 10:47–12:25 的代码提交（`5966991` 恢复 critical-path cover 首选候选、`d595c71` 保留非 R 可改写门、`30f4164`/`b7abaac`/`c58ad8e` 改 F2/SEC 检查而检查结果经 `r_available_for` 反向影响候选生成）；三个 worktree 定点重跑；`code/scripts/compare_equivalence_sweep.py`（2026-09-24 新增的多电路聚合判定） | **【2026-09-28 裁定：选 A + 固化 tag】** 主实验基线**认当前冻结 HEAD**，冻结为 annotated tag
**`faeco-exp-rev1` → `87d01ba`**。规则写明为：**下一轮权威主实验以一个冻结 commit 为基准，随即打 tag /
记 hash**；**禁止**把"20260826 的 `b03`/`b06`"与"当前 HEAD 的其他电路"拼成同一张表。
原则：`same claim ⇒ same code revision + same config family`（而非"哪个数字好用用哪个"）。
`b03` 取 HEAD 的 **-1.21**（优于产物 -1.27）。08-26 产物**保留为历史实验族，不删除、不改数字**，
但**不再作为未来主结果的局部补丁来源**；受 revision 影响的结果须以 `faeco-exp-rev1` + 同一 config family 重跑。
**定性已完成，revision 待钉**：这是 codex 谱系内部 08-26→08-28 的**既有漂移**，非本次合并引入。需用户裁定"论文主实验基线取哪个 revision"——(A) 认 HEAD 行为（则 `b03`/`b06` 相关数字需按 HEAD 重跑更新，方向是 HEAD 更优：-1.21 优于 -1.27）；(B) 认 08-26 产物（则须继续定位到具体 commit 并固化 tag）。**裁定影响面已收窄**：ISCAS89 侧 7/8 电路的论文数字可由 HEAD 复现（`s713`/`s820` 需接受 E6 计数口径差异），`s832` 终值一致仅轨迹不同 ⇒ 实质分歧集中在 **ITC-99 的 `b03`/`b06`（终值不同）**。**另有 2 个未记入论文的开关需登记**：`candidates_per_iteration=1`（两批次共用）与 `tns_aware=true`（**仅 ITC-99 批次**，见报告 §5.3 与契约 A8） | 用户（投稿前） |
| OI-014 | **L3 S 机制已验证；接入实时循环的 {S 开, S 关} 消融给出"无独立贡献"（能力型）——论文定位待裁定** | 2026-09-25 → 09-28 更新 | **已裁定（2026-09-28）：(B) 降级为可选候选类型/探索性能力** —— L1 全量三层裁决为 NEGATIVE（能力型），按预锁定 §13.4-3 规则判 (B)；**不阻塞投稿** | ① 机制侧（§8.12）：真实工具链九阶段全通过，22 项单测；`s641` 窗 `DFF_13` **ΔL=+1、ΔWNS=+0.03 ns**，CEC-1/2 双闭合 + 全网表 structure_check 通过 + 复跑逐位相同。② **环路侧（09-27 新，§8.13）**：8 电路 × {S 关, S 开}，S 在 **7/8 电路真的执行**（抽窗 469、实测候选 37），**接受 0/8**，两臂 `dWNS`/`maxB(k)`/`k₁st`/接受链**逐位相同**；37 候选 **ΔL(BLIF)>0 37/37、ΔL(SKY130)>0 16/37、ΔWNS>0 0/37**（含 16 个权威层变浅者亦无一改善）→ 窗口不在真时序关键锥上。off 臂 **8/8 逐位复现归档 L2 fixed 臂**（惰性 gate 通过）；两臂 `sta_used` 差 ≤8、全停 `max_iterations`（预算不绑定） | 真实 Yosys `0.67+146`+ABC+WSL OpenSTA；`code/scripts/run_s_ablation_batch.sh`（钉版本）、`compare_s_ablation.py`（配对差 + 台账 + 区分"没执行/执行了没用"）、`verify_s_off_reproduces_l2.py`（惰性 gate）、`analyze_s_candidates.py`（双层深度 × ΔWNS 交叉表）；`code/tests/test_flow_structure_resynth.py`（9 项，含"S 拒绝不改反馈通路"逐位断言）；回归 486 passed / 4 skipped | ① **已完成**加宽分配稳健性对照（`k4`：配对差仍全 0.000、候选 37→39 ⇒ 排除"配额不足"，瓶颈定位为可用窗口集合受"接受次数"限流）；② 裁定 S 定位——证据倾向 **(B) 如实降级为可选类型**并与 L2 封板结论合并，主贡献回到「候选构造 + 加权排序 + 失败归因 + STA 验证」；(A) 独立贡献需先实现**时序加权选窗**（当前割选窗与 R/G/B 同源，正是被实测定位的瓶颈） | 用户（投稿前） |
| OI-015 | **既有物理门（SPEF 复测）在 ISCAS89 上几乎无判别力：F6 标签近乎恒真** | 2026-09-27 | **已裁定（2026-09-28）：降级为物理诊断/过滤机制；标定另开 OI-016，不得以"让 F6 变多"为目标** | s27 实测：20 轮官方口径 **521/532 trial 为 F6**（98%）、小规模探针 **32/34**，`physical_delta` **29/34 恰为 0** → 成对物理增益并不区分候选。**2026-09-27 规模化坐实**：8 电路 4349 条物理 trial 中 `physical_delta≠0` 仅 **10.3%**、F6 少数类仅 **1.17%**（51/4349）。与 OI-008 的"ITC-99 主实验 F6 触发 0 次"互补。直接关切 §7 第⑦条（b17"人工放宽预算"）质疑 | 3-A 四臂采集（`phys`/`elec` 带 `--physical-gate`）；探针 `scratch/elec_probe/phys_elec_probe` | **【2026-09-28 裁定：降级 + 另开标定】** 不采用简单的三选一。① **机制定位先降级**：F6 当前**只能**安全主张"对**少量** ideal-net 有利、但物理估计后失效的候选进行**识别与拒绝**"；**不得**主张"F6 显著改善后续搜索或物理 WNS"。② **同时允许做 `unit_len_um` 标定**，但**标定目标必须在实验前定义，且不得以 `maximize F6 count` 为目标**（否则变成"为了让机制看起来有用而调参"）。合理目标：`min |WNS_simplified_SPEF − WNS_OpenROAD|`，或至少最大化排序/符号一致性 `sign(ΔWNS_SPEF) = sign(ΔWNS_OpenROAD)` —— 即**用 OpenROAD 作外部参照标定物理 proxy，而不是用 F6 命中率标定**。③ 标定后 F6 若仍罕见，**接受该事实**。⇒ 标定工作转为独立任务 **OI-016**。④ (C) 弱化 F6/物理增益表述、主实验只报理想口径 —— 仍作为**兜底**保留 | 用户（投稿前） |
| OI-016 | **物理 proxy（`unit_len_um` 等）标定：以 OpenROAD 为外部参照** | 2026-09-28 | **已开（由 OI-015 裁定引出；不阻塞 3-A/当前 L1）** | 现状物理门参数（`physical_unit_len_um=40`、`fanout/depth_penalty=1.0`、`min_physical_gain_ns=0.01`）**手工设定且未标定**，判别力弱（见 OI-015）。任务目标：把简化的 SPEF/物理估计与真实物理实现对齐 | 需新增外部参照链：OpenROAD（或等价 STA/RC 工具）在 sky130 上对同一网表出 WNS | **标定目标（须写在实验之前，冻结）**：主判据 `min |WNS_simplified_SPEF − WNS_OpenROAD|`；辅判据 `sign(ΔWNS_SPEF) = sign(ΔWNS_OpenROAD)` 的一致率。**明确禁止**以 `maximize F6 count` / 提升物理门触发率为目标。**产出**：标定后的 `unit_len_um` 等参数 + 标定报告 + 参数依据。**注意**：标定**不得**反改论文既有数字的既有实验族；若标定后 F6 仍罕见，如实接受（联动 OI-015） | 用户（后置；投稿前可选） |
| OI-017 | **`structure_resynth.rejections` 台账在 s420 上未闭合** | 2026-09-28 | **记录在案（不阻塞 L1 裁决；不影响候选数/实测数/ΔWNS/接受数）** | s420 的 {S on} 报 6 个候选（全 S0）与 6 条变体级拒绝 `W_STRUCT_ERROR`（**均标 S0**），但磁盘 `case/results/structure_resynth/round020/` 下只有 **8 个窗口 × {S0,S1,S2}**。8 个 S0 槽位无法同时产出 6 候选 + 6 条 S0 拒绝 ⇒ 台账不闭合。其余 7 电路 rejections 为空、无此现象。`W_STRUCT_ERROR` 的语义是**硬有效性失败**（`structure_check(grafted, baseline_text=…).ok == False` ⇒ 返回 `(LABEL_STRUCT_ERROR, None)`，**不产候选**） | `experiments/20260928_s_l1_ablation/on/s420/outerloop_result.json`（`structure_resynth.rejections`）、`case/results/structure_resynth/round020/` 目录树；`code/src/rseco/structure_resynthesis.py` L694-712 / L757-774（`if candidate is not None … elif label is not None …`，S1/S2 同 canonical ⇒ `(None,None)` 丢弃） | **待查（低优先，仅记账语义）**：需按 (窗口, 变体) 逐槽打点，确认是 `variant` 标签记录错位还是 S1/S2 的 `(None,None)` 路径在 STRUCT 失败时未走。**在任何后续引用该 `rejections` 台账的结论前必须先解决**；本报告的 L1 裁决**不依赖**该台账 | 后续（S 候选质量归因时顺带） |

### OI-014 **L3 S（窗口局部结构重综合）机制已验证；接入实时循环的 {S 开, S 关} 消融给出"无独立贡献"（能力型）结论——**但 2026-09-28 定位到该证据被集成缺陷混淆（S 的窗口池被 R/G/B 配额截断）**——论文定位待裁定** | 2026-09-25 开 / 2026-09-28 更新 | 待裁定（不阻塞投稿；阻塞 §4/§5 的 S 相关表述） | 报告 `reports/FAECO_L3_S_VALIDATION_20260925.md`（机制）、`reports/FAECO_L3_S_LOOP_ABLATION_20260927.md`（环路消融）；契约 §8.12 / §8.13；技术设计 §13（窗口来源重设计）

### OI-015 **既有"物理门"（SPEF 复测）在 ISCAS89 上几乎无判别力：F6 标签近乎恒真** | 2026-09-27 开 / 2026-09-27 更新（规模化坐实） | 记录在案（不阻塞 3-A；阻塞 F6 相关表述与"物理增益"类数字） | 契约 §8.15；3-A 报告 `project_docs/reports/FAECO_ELECTRICAL_3A_20260927.md`

- **【2026-09-27 更新】规模化证据（8 电路 × `phys`/`elec` 两臂，4349 条带回电气记录的物理 trial）**：
  - **`physical_delta ≠ 0` 仅 448/4349 = 10.3%** ⇒ 约 **90% 候选的成对物理 WNS 与打补丁前完全一致**；
  - **F6 少数类仅 51/4349 = 1.17%**，且高度集中（`s420` 20/136、`s641` 13/886，其余六电路各 1–8）
    ⇒ 除 s420 外物理门几乎**从不接受**；
  - 因 51 个少数样本上的 AUC 是高方差估计，3-A 判定**拒绝**了唯一那条近阈读数
    （`worst_max_capacitance_slack` @ `f6` = 0.6519，仅高阈值 0.0019、跨电路不同向）。
  - ⇒ 此前"32/34"的小规模探针结论在**全量规模上被坐实**：该门既不能当好标签，也不能当有效筛选器。

- **现象（实测，真实工具链）**：以论文既有物理门参数（`physical_unit_len_um=40`、`fanout/depth_penalty=1.0`、`min_physical_gain_ns=0.01`）跑 s27：
  - 20 轮官方口径（`run_electrical_collection.sh` 的 `phys` 臂，`k=8`、`--joint-k 2`、`--physical-gate`）
    **521/532 trial 发射 `F6_physical_load_failure`**（98%）；
  - 小规模探针（`--max-iterations 2 --candidates-per-iteration 3`）**32/34 为 F6**，
    且 `physical_delta`（成对物理 WNS 增益）**29/34 恰为 0**。
- **含义**：
  1. 该物理门在当前参数下**几乎不区分候选** —— "接受/拒绝"两侧的成对物理 WNS 变化多为 0；
     F6 不是一个可用的判别标签（正例率 98%，AUC 无从谈起）。
  2. 这与 **OI-008 记录的"F6 在 19 电路 ITC-99 主实验中触发 0 次"** 并不矛盾而是互补：
     F6 只在物理门控实验里出现，而那套门控的触发率**极端不平衡**。
  3. 直接关系到 §7 第⑦条的外部质疑（b17 "人工放宽预算"）：物理门参数是**手工设定且未标定**的，
     这会成为审稿攻击面。
- **对 3-A 的处置（已实施）**：3-A 的预锁定判据不依赖单一 F6 标签 ——
  ① 标签**双类各 ≥20 才算可用**，退化标签如实报为不可用、不产出判定；
  ② 判定要求**同一特征在 ≥2 个可用标签上同时成立**；③ 另跑理想 regime 提供
  `no_ideal_gain` / `hard_fail` 两个有方差的标签。见契约 §8.15(b)(c)。
- **需用户裁定（投稿前）**：(A) 保留现有物理门参数并**如实报告其判别力不足**
  （把"物理门"降级为"保守的成对一致性检查"而非"增益筛选器"）；(B) 标定 `unit_len_um`
  等参数使物理门有判别力（需额外标定实验与依据）；(C) 在论文中**弱化 F6/物理增益**相关表述，
  主实验数字只报理想（无 SPEF）口径。**当前证据不支持**用现有物理门做"增益筛选"的强主张。

- **机制已验证（§8.12）**：`code/src/rseco/structure_resynthesis.py` 在真实 Yosys `0.67+146` + ABC + WSL OpenSTA 上端到端打通（EXTRACT→…→STRUCT 九个阶段全通过并出候选）；22 项单测；**§5.5 判据达成**：`s641` 窗 `DFF_13`（root `G127`，29 门，R_S=1.00）**ΔL=+1、ΔWNS=+0.03 ns、ΔTNS=+0.01 ns**，CEC-1/CEC-2 双闭合 + 全网表 structure_check 通过 + 逐次复跑逐位相同。
- **【2026-09-27 新】接入 `run_multi_iteration_case`（r2 §4.9）并做正式口径消融**（8 电路 × {S 关, S 开}，`k=8`、20 轮、`--joint-k 2`、STA 预算 700 两臂相同；契约 §8.13）：
  - **单变量对照成立且有 gate 把守**：off 臂 **8/8 电路逐位复现归档 L2 fixed 臂**（success/iterations/stop_reason/final_patch_id/wns/wns_history/接受补丁链/`sta_used` 全等）→ S-off 路径完全惰性（`code/scripts/verify_s_off_reproduces_l2.py`）。
  - **S 真的执行了**：7/8 电路（除 `s641`）累计成功抽窗 **469** 个、产出并实测候选 **37** 个；`s641` 是"报价 72 窗但**成功抽窗 0**"（r2 §4.2 不变量拒绝）→ 属**程序/几何**原因，与能力结论必须分开。
  - **结果：接受 0/8 电路**，且两臂 `dWNS`、`maxB(k)`、`k₁st`、接受数**逐位相同**（8/8 电路 `diff = 0.000`）；两臂 `sta_used` 最大差 +8、16/16 run 均停在 `max_iterations` → **预算不绑定**（排除"S 被饿着"的第一层）。
  - **机制解释（关键表）**：37 个候选 **ΔL(BLIF)>0 为 37/37**、**ΔL(SKY130，权威层)>0 为 16/37**、**ΔWNS>0 为 0/37**，且 **ΔL(SKY130)>0 且 ΔWNS>0 = 0/37**；R_S 判定 ok 33/soft 4；变体全为 S0（S1/S2 与 S0 逐位相同 → §4.7 DROP）。→ **不是"降到错的那一层"能解释的**（那只解释 21/37），而是"**被割选中的窗口不在真正的时序关键锥上**，窗口内结构变浅传不到端点 WNS"。
- **判读**：在当前 regime 下 **S 是可选候选类型，不是独立贡献**——与 L2 的 EMA 封板结论同形（增量来自候选构造 + 加权排序 + 验证纪律，而非新增搜索维度）。**反向加强 §4.8 的论证**：即使 S 产生 ΔL>0、甚至权威层 ΔL>0，也未必换成 ΔWNS>0 → "结构深度下降"不是"时序改善"的可替代指标。
- **必须同时声明的边界**：① **已完成**加宽分配对照（`--resynth-per-iteration 4`，8/8 电路）：配对差仍全 `0.000`、接受数仍 0/8，候选仅 37 → **39** → **"S 被饿着"被排除**；并定位到真正瓶颈是**可用窗口集合**（窗口身份 `(netlist_hash, boundary_key)` 去重 ⇒ 可触及窗口上界 ≈ 不同 `G_r` 个数 × 每 `G_r` 割边界数，而 `G_r` 只在接受时改变）→ **加大配额无用，只能改窗口来源**；② r2 §4.9 的 `S→G` 一档**有意未实现**（避免同时改两件事破坏单变量对照，契约 §8.13.4）→ 结论仅针对**纯 S 候选类型**；③ **割选窗仍未做时序加权**（用的是与 R/G/B 相同的割候选）——这既是被实测定位到的瓶颈，也是下一步真正的杠杆；④ 上游在该 regime 已把可用增益吃得较满。
- **待裁定**：(A) 把 S 作为**独立贡献**写入 §4/§5（现有证据不支持，需先实现时序加权选窗）；(B) **如实降级为可选候选类型**并与 L2 封板结论合并叙述，主贡献回到「候选构造 + 加权排序 + 失败归因 + STA 验证」。**当前证据倾向 (B)。**
- **【2026-09-28 新】瓶颈定位到具体代码行（比 ① 的"窗口身份去重"更精确）**：`flow.py` L626
  `round_candidates = list(candidates[:max_candidates_per_iteration])` **截断**加权割列表，
  而 L890 的 S 循环**复用的正是这个截断列表** ⇒ **S 的窗口宇宙 ≤ `candidates_per_iteration`（=8）/
  每个 `(G_r, cone)`**，与 `resynth_per_iteration` 无关。实测（`20260924_l3s_ablation` vs `_k4`）：
  配额 1→4 只使候选 **37→39（+2，仅在 s420）**，7/8 电路逐位相同，触及轮数由 ~7 轮压到 ~2 轮
  ⇒ **配额只改变"摊入几轮"，不改变池子**。去重命中率佐证：s713 `offered=123/extracted=105/新窗口=7`
  （**93% 是同一批割边界被重复走过**）。
  ⇒ 现有"接受 0/8"只覆盖到"**在 R/G/B 的 top-8 割边界里 S 无可接受候选**"，**不可外推为"S 无贡献"**
  —— OI-014 的现有证据**被这一集成缺陷混淆**。设计见技术设计 **§13**（L1 池子规模 / L2 时序加权选窗 /
  L3 曝光轮数；预锁定验收判据见 §13.4）。
- **【2026-09-28】池子普查结果 —— 并**修正**了上面的归因**：只读插桩 `s_stats["pool_census"]`
  （仅 S 开启时记录，{S off} 产物逐位不变）在 **s382/s713/s832/s953** 四电路上给出
  **`len(candidates) = 9`、`len(round_candidates) = 8`** —— ⇒ **L626 的截断只损失 1 个窗口**，
  **不是瓶颈**；真正封顶的是 **L607 `_cone_candidates(..., k=max_candidates_per_iteration)`**：
  **枚举本身只被要求返回 8 个**（+1 前置关键路径 cover = 9）。
  ⇒ **修正 L1**：扩池必须**用更大的 `k` 重新枚举**（S 专属第二次枚举），
  **不能**实现为"加宽 `candidates[:W_s]` 切片"（切片只会从 9 变 9）。
  —— 这是"最便宜的先做"在设计被实现前就纠正它的收益。
  **补充普查（✅ 已完成）**：`candidates_per_iteration = 32` 时未截断列表 = **33**（s382/s953 一致）；
  s420 全 20 轮恒为 **9** ⇒ 关系为 **`len(candidates) = min(k+1, 该锥体的可计分割空间)`**
  （未饱和时与轮次/cone/`G_r` 无关）。
  ⇒ **枚举随 `k` 线性增长 ⇒ L1 成立**（给 S 一次 `k=32` 专属枚举即可把窗口池 8 → 32，**4×**），
  无需改 cone / 深度切分。**可引用表述**：S 的可触及窗口上界 = 不同 `G_r` 数 ×
  `min(candidates_per_iteration, 割空间)` —— **S 的触达范围被 R/G/B 的束宽直接决定**（小锥体除外）。
- **【2026-09-28】闭合反例：小锥体**饱和**，`k+1` 不是上界（L1 重跑暴露）**：`s27`（10 门，目标锥
  G10 极小）在 `k=8` 与 `k=32` 下 `len(candidates)` 均为 **6**（`pool_census` = `[3,6,6,…]`，20 轮），
  L1 重跑中 `window_pool=32` 但 `window_pool_offered` 仍 **6**、S 候选仍 2、接受仍 0。
  ⇒ L1 对"割空间 < `candidates_per_iteration`"的电路**天然惰性**（非失效，是无可扩余地）；
  **判定 L1 有效性必须排除饱和电路**。报告 `reports/FAECO_S_WINDOW_CENSUS_20260928.md` §3.1。
- **【2026-09-28】L1 已实现并重跑**（`resynth_window_pool`，严格惰性守卫，2 项新单测）：
  `experiments/20260928_s_l1_ablation/`（8 电路 × {off,on}，`on` = `--resynth-per-iteration 8
  --resynth-window-pool 32`，两臂 `--sta-budget 1600`）。
- **【2026-09-28 ★ L1 全量裁决：NEGATIVE（能力型）⇒ 裁 (B)】** 报告
  `reports/FAECO_S_L1_WINDOW_POOL_20260928.md`；工具 `code/scripts/summarize_s_l1.py`。
  8 电路 × {`off`,`on`}，16/16 `ALL_RUNS_DONE`，`on` = `--resynth-per-iteration 8
  --resynth-window-pool 32`，两臂同 `--sta-budget 1600`（**两侧都不绑定**，max 482）。
  - **纪律全过**：① 控制臂 8/8 逐位复现归档 `off`（`mapped.v`/`patch_id`/`wns`/停因/预算台账）；
    ② **单变量干净 8/8**：两臂**非 S（R/G/B/JOINT）试验序列逐位相同**
    （s27 416、s382 769、s420 1048、s641 596、s713 306、s820 312、s832 306、s953 393）；
    ③ 惰性单测 11 passed。
  - **第一层 enumeration ✅**：`s382 8→32`、`s420 1→6`、`s713 7→22`、`s820 6→14`、
    `s832 5→17`、`s953 8→33`；**37 → 126（3.4×）**。`s27` **SATURATED**（池只有 6）、
    `s641` **NO-ENGAGE**（抽窗 0）。**机制被完全解释**：历史 s382/s953 候选数**恰好 = 8 = 池上限**；
    L1 后 = `resynth_per_iteration`(8) × 参与轮数 ⇒ **历史 S 候选数被池子钉死**。
  - **第二层 candidate quality ⚠️**：`ΔL(SKY130)>0` 由历史 43% 升到 **76/126（60.3%）**
    ⇒ 新窗口**更常真的降低权威层深度**；但 **`ΔWNS>0` = 0/126**，且 **90/126 的 `ΔWNS<0`**
    （多数候选**反而让 WNS 变差**）⇒ **问题不在 L1，在 S transformation quality**。
  - **第三层 repair capability ❌**：**接受 0/8**、配对 `ΔWNS(on−off)` **全 0.000**。
  - **固定指标集（纪律）**：`N_unique_window` = `N_S candidate` = `N_measured` = **126**
    （**无重复窗口哈希** ⇒ 126 个候选来自 126 个不同窗口，扩池是真探索）；
    `N_extracted`=1724 ≫ 126 ⇒ 印证该字段是**重复扫描**指标，**不作**"搜索空间扩大"的证据。
  - **判定**：**枚举瓶颈已排除，但当前 S 构造在该 benchmark/regime 下没有体现 timing repair
    capability** ⇒ **(B)**。**明确不做**：不再扩池（32→64→128，池已用满且非瓶颈）。
  - **下一步（§13.7）**：转 **S 候选质量归因**——为什么通过 CEC 的 S patch 没有 timing gain？
    (i) 窗口内 depth 是否真的下降（已部分回答 76/126）；(ii) 映射后 depth 是否又回来；
    (iii) cell delay 是否变差；(iv) fanout/cap 是否抵消结构收益；(v) critical path 是否不穿过窗口。
  - **⚠️ 待查（不影响上述结论）**：s420 报 6 候选 + 6 条变体级拒绝 `W_STRUCT_ERROR`（均标 S0），
    但磁盘上只有 8 窗口 × {S0,S1,S2} ⇒ `rejections` 台账在 s420 上**未闭合**，见 **OI-017**。
- **【2026-09-28 用户三层裁决口径（已执行）】** 不直接看最终 WNS 一项，按三层顺序裁决；
  **不得因"L1 扩池成功、候选数明显增加"就把 S 升格**：
  - **第一层 enumeration（L1 自身是否有效）**：非饱和电路上 `N_S,L1 > N_S,old`。
    成立 ⇒ 只证明"**L1 的 enumeration bottleneck 被真实解除**"，排除"S 没效果只是因为从未获得
    足够候选"这一解释。**不构成 timing capability**。
  - **第二层 candidate quality（问题是否已不在 L1）**：看 `N_CEC pass`、`N_measured`，
    以及 S 候选的 `ΔWNS` **分布**。若枚举涨 3× 但全部 `ΔWNS ≤ 0` ⇒ **问题在 S transformation
    quality，不在 L1**。
  - **第三层 repair capability（决定 OI-014）**：`N_accepted,S > 0` 且至少一个电路
    `ΔWNS_on−off > 0`（最好同时 `ΔL < 0`）。
  - **判定规则**：达到第三层 ⇒ 才有资格重新考虑 (A) 独立贡献；若 `N_accepted,S = 0`
    ——**即使 S 候选 37 → 100+**——结论仍为"**枚举瓶颈已排除，但当前 S 构造在该 benchmark/regime
    下没有体现 timing repair capability**" ⇒ 选 **(B) 降级为可选候选类型/探索性能力**。
  - **负结果的处置**：若出现"候选 37→100+ 而 accepted 仍 0"，这是**有价值的负结果**；
    **不得**再把 window pool 32→64→128 继续扩大，而应转向 **S 候选质量归因**：分解
    (i) logic depth 是否实际下降；(ii) 映射后 depth 是否又回来；(iii) cell delay 是否变差；
    (iv) fanout/cap 是否抵消结构收益；(v) critical path 是否根本不穿过被重综合窗口。
- **【2026-09-28 指标口径纪律：不得再用 `windows_offered` 作 L1 主证据】** 它包含**重复扫描过的
  割边界**（s27 的 114 ≈ `19×6`），不是 unique window 数。L1 报告固定看：
  `N_unique_window`（按 window/canonical hash 去重）、`N_extracted`、`N_S candidate`、`N_measured`、
  `N_accepted` —— **其中后四个最关键**。`windows_offered` 只保留作**内部扫描开销指标**，
  **不承担"搜索空间扩大多少"的解释责任**。
- **论文改动一律等裁定后一次性进行**（本轮仍未触碰任何 `.tex`）。

### OI-008 明细（2026-09-23 代码—论文对照，含实测触发分布）

> 【2026-09-30 加注】下表"旧版事件名，当前 `code/` 已无此字符串"的说法在 **0a 步骤 4 合并（`258f588`）后已过时**：现行 `real_wns.py:1864` 仍以 `acceptance_budget_violation` 写试验台账（另有姊妹事件 `acceptance_budget_unavailable`）。差异的正确表述是**两层命名分工**（工具层事件名 ↔ 方法层 F4 分类名），非"产物与代码不一致"；已成文为 `paper/zh/submission/supplementary/S1_失效事件名映射说明.md`。下表按历史快照保留。

**实测触发分布**（权威源：`experiments/20260826_itc99_main/b*/b*/eval_trials.json`，19 电路 / 4044 trials，探针 `scratch/count_failures.py`）：

| 产物事件名 | 次数 | 对应 FailureType（`failures.py`） |
|---|---:|---|
| `acceptance_budget_violation` | 2434 | **F4** `F4_timing_gain_insufficient`（`failures.py:47` 判定"未满足接受判据"）——**旧版事件名，当前 `code/` 已无此字符串** |
| `F5_verification_too_expensive` | 915 | F5 |
| `F1_equivalence_failure` | 138 | F1 |
| `F3_patch_too_large` | 16 | F3 |
| `F2_boundary_invalid` | 3 | F2 |
| `F6_physical_load_failure` | 0（本实验） | F6（仅物理门控实验触发） |

| 项 | 论文表述 | 代码实际 | 性质与影响 |
|----|----------|----------|-----------|
| F1 局部功能/结构失败 | 表 tab:failures F1 行仅写"增加边界惩罚 $\lambda_b$" | `refinement.py` L41–46：`boundary_penalty += 1.0` **且** `equivalence_stability_reward += 1.0`（对应式(2) 扇出项 $\lambda_f$） | **论文漏写一项**。F1 在主实验中实测触发 **138 次**，即该反馈动作**实际生效**，属实质遗漏而非纯表述问题 |
| F6 SPEF 复测失败 | 表 F6 行写"增加边界惩罚 $\lambda_b$ **与尺寸惩罚 $\lambda_s**" | 当前 `code/` 仅 `boundary_penalty += 1.0` | 论文**多写**一项。但 F6 由 20260807 物理门控实验（旧内环代码路径）触发，**当时是否实现了 $\lambda_s$ 增量尚未溯源**，不能排除"重构后丢失" |
| $\lambda_c$ 作用 | §3.3 文字："用于调整关键路径覆盖割 $C_c$ 的排序优先级与覆盖得分权重" | 该用途成立（`cut.py` L270/L291），**另有**节点代价分母折扣（`cut.py` L193，仅 `r_ok` 门，式(2) 未列该项） | 表述**不完整**，非错误 |
| 事件命名可追溯性 | — | 主实验产物用旧名 `acceptance_budget_violation`，现代码输出 `F4_timing_gain_insufficient` | 语义一致（已核实 `failures.py:47` 判定条件相同）；但产物与当前代码字符串不一致，投稿前建议在论文或补充材料中说明，避免审稿人对照代码时困惑 |

影响评估：**所有已发表数字不受影响**（事件名映射语义一致，F4 占比 60% 与论文"主循环主要由 F4 驱动"相符）；需处置的是 F1/F6 两行的反馈动作描述，其中 F6 行需先溯源 20260807 实验代码。

## 已关闭（近期）

| ID | 问题 | 关闭说明 |
|----|------|----------|
| OI-005（主体） | 旧仓库副本 | 2026-09-12 内容全删（LOG-20260912-02），仅剩空壳 |
| — | §4.3.1 数据混源 | 2026-09-11 一致性审计修复（d329f19） |
| — | C 盘分支处置 | 3 个 worktree 删除前推送固化 + 抢救 2 份未提交文档（archive/phase0_worktree_salvage_20260912/） |
| — | 网络阻塞推送 | 已恢复，全部提交已上 origin/main |
