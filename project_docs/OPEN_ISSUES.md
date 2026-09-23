# 未决问题追踪（Open Issues）

> 未解决的问题必须登记于此；**只要未解决就持续保留**，每轮检查进展。
> **未解决的问题必须告知用户，不得隐瞒或淡化。**

## 等待用户决策（选项与建议见 `agent_handoff/DECISION_BRIEF_20260912.md`）

| ID | 问题 | 状态 | 决策选项摘要 | 阻塞 |
|----|------|------|--------------|------|
| OI-003 | versions/v1 基线冻结方案 | 待决策 | A 轻量冻结（tag+manifest，推荐）/ B 中量（+证据汇总复制）/ C 完整体（≥25GB，不推荐） | 用户 |
| OI-006 | 机制图（已重定义） | 待确认 | 原"4 图拆分"针对旧 12 页版；**当前 9 页稿仅 3 图，拆分问题已消失**。A 维持现状（推荐）/ B 按审稿意见增补旧素材 1–2 张 | 用户 |
| OI-001 | DOI（已降级） | 待投稿流程 | 主稿正文**无占位符**（仅注释行与模板示例含 DOI 字样；中图法分类号已填）；投稿时按期刊模板补稿件编号/DOI 字段即可 | 投稿流程 |
| OI-002 | DRC signoff（已定性） | 待投稿流程/rebuttal 备选 | 论文已如实声明；补跑需引入 Magic/KLayout（天级），建议仅在审稿被要求时做 | 按需 |

## 进行中 / 未解决

| ID | 问题 | 发现日期 | 状态 | 影响 | 尝试过 | 下一步 | 阻塞 |
|----|------|----------|------|------|--------|--------|------|
| OI-004 | 实验目录磁盘占用（历史瘦身残留） | 2026-08-28 | blocked（用户声明不删） | experiments/ 共 116 GB / 122 目录（itc99_main 19G、phys_closure 2.6G 等） | 已清理 STA 中间日志 + 旧仓库副本全删（2026-09-12） | INVENTORY 的 cleanup-candidates 档位待用户逐项确认；实验证据严禁删 | 用户 |
| OI-005 | 旧目录空壳 `D:\BaiduSyncdisk\03_FAECO` | 2026-09-12 | 基本关闭 | 内容已全删（含旧 .venv、C 盘 3 个 worktree；3 条 codex 分支已推送固化） | robocopy 校验 + 全量删除 | 会话关闭后空壳若仍在，手动删除即可 | 无 |
| OI-007 | hold 模式跨测试集效果有限 | 2026-09-08 | 记录在案（不阻塞投稿） | 14 电路仅 b01 改善 min_slack；已写入论文 limitation | 单 patch 无法同时改善 setup+hold | 未来工作（多目标 hold/setup 联合搜索） | — |
| OI-008 | 论文表 F1/F6 反馈动作描述与代码实现不一致 | 2026-09-23 | **论文侧已修正**（2026-09-23），遗留 1 项可追溯性事项 | 三处差异已按代码事实修正论文 8 处表述（另 F4 行措辞统一，共 9 处）；已发表数字不受影响 | 逐行对照 `refinement.py` + `git show 216a118` 溯源 + 实测产物统计 | 遗留：产物旧事件名 `acceptance_budget_violation` 与现行 `F4_timing_gain_insufficient` 字符串不一致，投稿前建议在补充材料说明；另"反馈的独立贡献"仍需隔离实验（现有消融混杂两变量） | 用户（投稿流程） |
| OI-009 | **Algorithm 1 的"不叠加"描述与主实验实际行为矛盾** | 2026-09-23 | **论文侧已修正**（2026-09-23） | 论文 Algorithm 1 第 250 行称"各轮候选均相对固定基线 $G_0$ 评估，不叠加多个局部补丁"，但实测 `base_netlist_hash` **逐轮内唯一、跨轮变化**（b01 8 轮 9 个基准 / b03 9 个 / b04 8 个 / b05 8 个），且变化发生在**接受轮之后**（b01 iter1 接受 1 个 patch → iter2 基准哈希改变）——**主实验实际为逐轮累积叠加**，仅"效率优先配置"（sprint1）为单轮不叠加。§4.3 对 PicoRV32 的"由 R/G/B 多类接受补丁叠加形成"表述反而与实测一致，与 Algorithm 1 自相矛盾 | 探针 `scratch/probe_base_hash2.py`（逐 trial 校验：同轮内哈希唯一、跨轮改变）；`20260805_tcad_sprint1_iscas89` summary `iterations=1` | **已改**：Algorithm 1 重写为"从**当前网表** $N$ 提取锥 → 接受后 `$N\gets N+\Delta$` 提交为下一轮基准 → 同轮候选共享同一基准且互不叠加 → 该轮一旦提交，基于旧基准的其余候选作废"；并拆出失败反馈为独立步骤；算法后补"候选按轮提交…效率优先配置仅执行单轮，不产生累积叠加"。遗留：把该行为与 OI-011 的 codex 实现（`SearchState.accept_patch` / `refreshed_cone`）对齐到同一层级描述 | 用户（OI-011 定案后复核一次） |
| OI-010 | 论文 §4.2 的 ISCAS89 策略分布与实测不符 | 2026-09-23 | **待修正（本轮改判：先定数据集归属）** | §4.2 称"JOINT 对应 s27/s382/s420/s953，G 对应 s641/s713/s832，R 对应 s820"（4 JOINT + 3 G + 1 R）。**两套 ISCAS89 运行都不支持该映射**：① `20260826_iscas89_main` 实测 **G 23 次/7 电路（s27/s382/s420/s641/s713/s832/s953）、R 4 次/2 电路（s641、s820）、JOINT 0、B 0**；② 图 4 源 `20260805_tcad_sprint1_iscas89` 的 `eval_trials.json` 为旧格式（多对象拼接、非严格 JSON，即 20260806-16 修掉的写盘 bug），无法直接统计，其 `summary.json` 仅记 3 个电路（s953/s832/s820，`iterations=1`）。**并且 §4.2 的数据集归属本身存疑**：§4.2 称"图 4 对应效率优先配置（最大 1 轮 + 首改进即停）"，但 `20260826_iscas89_main/summary.json` 显示 `iterations: 8`、`wns_history` 长度 3–7（多轮累积）；`20260805_tcad_sprint1_iscas89/summary.json` 却为 `iterations: 1`。`RESULTS.md` §2 的 strategy 列同源同错（"JOINT 是主要增益来源 4/8"） | 探针 `scratch/probe_iscas89_dist.py`、`scratch/probe_iscas89_two.py`、`scratch/probe_sprint1_dist.py`；两套 summary.json | **本轮不改该句（避免编造）**：需用户先裁定 §4.2 以哪套运行报告——(A) 效率优先/Tcad-sprint1 口径（则需重跑或从旧格式产物恢复策略分布，并解决其 summary 仅 3 电路的问题）；(B) 20260826 口径（则 §4.2 的策略分布改为 G 7/8 电路、R 2/8 电路、JOINT 0，并把"效率优先/1 轮"表述改为与 `iterations: 8` 一致）。定案后一并同步 `RESULTS.md` §2 | 用户（投稿前） |
| OI-012 | **论文 §4.4 表 6 的"失效反馈开/关"对照在运行器层面不成立** | 2026-09-23 | **论文侧已修正**（2026-09-23） | §4.4 原称"以**禁用 F1–F6 失效反馈**、保持权重固定的纯 G/纯 B/随机为基线，与**启用失效反馈**的 20 轮混合策略比较"。**证据链三重闭合**：(a) 表 6 四列均出自 `code/scripts/run_hybrid_repair.py`（混合列由 `20260807_multiround_8c_067/run_all.bat` 证实），该脚本**不使用** `refine_weights`/`RefinementWeights`/`enable_feedback`；(b) 该脚本输出 schema 与四列产物完全一致（`rounds_history` + `candidate_sta_before_round/after_round`、`random_order`、`seed`、`improvement`）；(c) 表 6 混合列 8/8 电路与 `20260807_multiround_8c_067/convergence_summary.json` **逐值精确吻合**（0.28/1.00/1.54/1.63/1.33/0.99/0.57/1.25，均值 1.074），纯 G 列均值 0.161 亦同源。→ 四列**都无 F1–F6 反馈**，该表实际对比"候选空间 + 排序启发式"。**附带修正三处**：表注"随机列与混合列共享 R/G/B/**JOINT** 候选类型"不成立（随机列实测 B 7154/G 3114/R 1954，**JOINT 0**）；`tab:configs` 中"20 轮收敛"列的 `F1--F6 失效反馈 = 轮内 + 跨轮` 无依据；**表 6 三列基线所用的 `20260826_ablation_pureG/pureB/random_seed{1,2,3}` 目录顶层运行脚本 0 个**（.bat/.sh/.md/.log 全无），调用命令未归档 | `code/scripts/run_hybrid_repair.py`（imports + 输出 schema grep）、`20260807_multiround_8c_067/run_all.bat` 与 `convergence_summary.json`、`20260826_ablation_*/hybrid_result.json`、探针 `scratch/probe_ablation_cfg{,2}.py` | **已改**：§4.4 首段重写为"比较候选空间与候选排序两类设置"并明示"各列由同一固定权重运行器产生、不构成失效反馈的开关对照，失效反馈的独立贡献需另设对照实验量化"；表标题改为"候选空间与候选排序设置的 WNS 改善对比"；表注改为"纯 G/纯 B 列分别只生成 G/B 候选，随机列与混合列在混合候选空间生成候选（混合列另含 JOINT 组合候选）…各列均使用固定搜索权重、不启用 F1--F6 权重重整"；`tab:configs` 20 轮收敛列反馈行改为"不启用（固定权重）"并在表注说明。遗留：**核心主张 Failure-Aware 目前仍无有效对照**，须由 `planning/FAECO_V2_DESIGN_PLAN_20260923.md` §2 的三臂实验补齐（且须归档运行命令 + 在结果 JSON 记录 `enable_feedback`） | 用户（投稿前补实验） |

### OI-008 明细（2026-09-23 代码—论文对照，含实测触发分布）

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
