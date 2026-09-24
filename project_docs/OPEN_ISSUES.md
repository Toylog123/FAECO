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
| OI-009 | **Algorithm 1 的"不叠加"描述与主实验实际行为矛盾** | 2026-09-23 | **论文侧已修正**（2026-09-23） | 论文 Algorithm 1 第 250 行称"各轮候选均相对固定基线 $G_0$ 评估，不叠加多个局部补丁"，但实测 `base_netlist_hash` **逐轮内唯一、跨轮变化**（b01 8 轮 9 个基准 / b03 9 个 / b04 8 个 / b05 8 个），且变化发生在**接受轮之后**（b01 iter1 接受 1 个 patch → iter2 基准哈希改变）——**主实验实际为逐轮累积叠加**，仅"效率优先配置"（sprint1）为单轮不叠加。§4.3 对 PicoRV32 的"由 R/G/B 多类接受补丁叠加形成"表述反而与实测一致，与 Algorithm 1 自相矛盾 | 探针 `scratch/probe_base_hash2.py`（逐 trial 校验：同轮内哈希唯一、跨轮改变）；`20260805_tcad_sprint1_iscas89` summary `iterations=1` | **已改**：Algorithm 1 重写为"从**当前网表** $N$ 提取锥 → 接受后 `$N\gets N+\Delta$` 提交为下一轮基准 → 同轮候选共享同一基准且互不叠加 → 该轮一旦提交，基于旧基准的其余候选作废"；并拆出失败反馈为独立步骤；算法后补"候选按轮提交…效率优先配置仅执行单轮，不产生累积叠加"。遗留：把该行为与 OI-011 的 codex 实现（`SearchState.accept_patch` / `refreshed_cone`）对齐到同一层级描述 | OI-011 已定案（路径 B）；本项复核并入实施步骤 0a（`SearchState` 落权威布局） |
| OI-010 | 论文 §4.2 的 ISCAS89 策略分布与实测不符 | 2026-09-23 | **待修正（本轮改判：先定数据集归属）** | §4.2 称"JOINT 对应 s27/s382/s420/s953，G 对应 s641/s713/s832，R 对应 s820"（4 JOINT + 3 G + 1 R）。**两套 ISCAS89 运行都不支持该映射**：① `20260826_iscas89_main` 实测 **G 23 次/7 电路（s27/s382/s420/s641/s713/s832/s953）、R 4 次/2 电路（s641、s820）、JOINT 0、B 0**；② 图 4 源 `20260805_tcad_sprint1_iscas89` 的 `eval_trials.json` 为旧格式（多对象拼接、非严格 JSON，即 20260806-16 修掉的写盘 bug），无法直接统计，其 `summary.json` 仅记 3 个电路（s953/s832/s820，`iterations=1`）。**并且 §4.2 的数据集归属本身存疑**：§4.2 称"图 4 对应效率优先配置（最大 1 轮 + 首改进即停）"，但 `20260826_iscas89_main/summary.json` 显示 `iterations: 8`、`wns_history` 长度 3–7（多轮累积）；`20260805_tcad_sprint1_iscas89/summary.json` 却为 `iterations: 1`。`RESULTS.md` §2 的 strategy 列同源同错（"JOINT 是主要增益来源 4/8"） | 探针 `scratch/probe_iscas89_dist.py`、`scratch/probe_iscas89_two.py`、`scratch/probe_sprint1_dist.py`；两套 summary.json | **本轮不改该句（避免编造）**：需用户先裁定 §4.2 以哪套运行报告——(A) 效率优先/Tcad-sprint1 口径（则需重跑或从旧格式产物恢复策略分布，并解决其 summary 仅 3 电路的问题）；(B) 20260826 口径（则 §4.2 的策略分布改为 G 7/8 电路、R 2/8 电路、JOINT 0，并把"效率优先/1 轮"表述改为与 `iterations: 8` 一致）。定案后一并同步 `RESULTS.md` §2 | 用户（投稿前） |
| OI-011 | **main 分支 `code/` 不是产出论文主实验产物的实现（代码谱系分叉）** | 2026-09-23 | **已裁定路径 B；G2/G3/G4 已冻结；0a 步骤 2–5 已实施并过 gate（`a12ecab`/`9ac06bf`/`258f588`/`870d062`/`9870abc`/`1777a78`），**等价门 24/24 × 3 电路全 PASS**；**legacy regression 步骤 6 亦通过：8 个 ISCAS89 电路（s27/s382/s420/s641/s713/s820/s832/s953）**8/8 × 24/24 全等**（含 bookkeeping），报告 `reports/FAECO_LEGACY_REGRESSION_20260923.md`，下一阶段 L2 Adaptive 解除阻塞 | 产物侧字段 `base_netlist_hash`/`acceptance_evidence`/`sta_provenance`/`topology_metrics`/`cache_key`/`config_hash` 在 **main 的 `code/` 全 0 命中**；产出实现在 `codex/faeco-unified-loop` 分支（`flow.py:483` 建 `SearchState`、`:684` 接受后 `refreshed_cone=extract_fanin_cone(...)`、`:726` 调 `accept_candidate`；`real_wns.py:784 accept_candidate` 内 `self.mapped_text=str(text)`）。main 侧 `flow.py:392` 锥只抽一次、`real_wns.py:197` 后 `mapped_text` **永不更新** → **main 无逐轮累积行为**。谱系 `merge-base=b8c3759 (08-13)`，main 在 08-14~09-07 无提交（恰跨 20260826 主实验期）。**任何阶段 1 实验若在 main 上跑，数字与论文不可比。必须最先处置。** | `git log -S` 检索产物字段（限 `-- "*.py"`）；`codex/faeco-unified-loop:src/rseco/{flow,real_wns,refinement_loop}.py` 逐行对照 | **路径 B 已定**：`SearchState` 为**唯一运行时状态所有者**（详见 `planning/FAECO_V2_TECH_DESIGN_20260923.md` §2）。实施步骤 0a：把 `SearchState` 体系落到权威布局，增持 `FailureFeedbackState`/`cone_limit`/`round_id`；`rollback()` 需同时回滚 EMA 与 cone_limit；以 3 电路 sentinel 复跑复现既有数字（或如实记录差异）。**配套前置 G2/G3/G4 已冻结**：状态更新契约 / checkpoint+`netlist_epoch` 契约 / `W_*`→F1–F6 映射 → `planning/FAECO_V2_IMPL_CONTRACT_20260923.md`。**0a 第一阶段不得改变算法行为**，gate = 等价报告六项全等（候选顺序 / F1–F6 序列 / 每轮权重 / 接受补丁 / 最终 WNS / STA 次数）。另须修一处既有缺口：`candidate_hash` 不含基准网表，多轮去重会误杀（改 `candidate_key = sha256(netlist_hash ‖ candidate_hash)`）。**实施与 gate 结论（2026-09-23）**：步骤 2 EMA 反馈（`a12ecab`）→ 3 `SearchState`+checkpoint+G2/G4（`9ac06bf`）→ 4 codex 能力合并（`258f588`）+ 09-12 路径修复（`870d062`）→ 5 等价门。报告：`reports/FAECO_0A_EQUIVALENCE_20260923.md`。**gate 结果：codex `9435846` vs main `fcdf06b`，`s382`/`b03`/`b06` 三电路均 24/24 项全等（E1–E6 全 PASS），回归 411 passed/4 skipped，算法行为未变**。已获硬证据：`experiments/20260826_iscas89_main/s382/s382/outerloop_result.json` 的 `state` 键集与 codex `SearchState.to_dict()` 完全一致 → §8.3「基线 = codex 谱系」由推断升级为实测。**A5 已裁定**：产物为串行 `--workers 1` + 内层 `early_stop=True`；runner 默认保留 `True`，旧口径"首次接受即停"写作 `--max-patches 1`。**附带钉住产物配置**：ISCAS89 主实验用 `--candidates-per-iteration 1`（s382 因此 24/24 精确复现），且批次启用 `--tns-aware` | **0a 已完成；下一步 L2 Adaptive（$\rho=0.5$）** |
| OI-012 | **论文 §4.4 表 6 的"失效反馈开/关"对照在运行器层面不成立** | 2026-09-23 | **论文侧已修正**（2026-09-23） | §4.4 原称"以**禁用 F1–F6 失效反馈**、保持权重固定的纯 G/纯 B/随机为基线，与**启用失效反馈**的 20 轮混合策略比较"。**证据链三重闭合**：(a) 表 6 四列均出自 `code/scripts/run_hybrid_repair.py`（混合列由 `20260807_multiround_8c_067/run_all.bat` 证实），该脚本**不使用** `refine_weights`/`RefinementWeights`/`enable_feedback`；(b) 该脚本输出 schema 与四列产物完全一致（`rounds_history` + `candidate_sta_before_round/after_round`、`random_order`、`seed`、`improvement`）；(c) 表 6 混合列 8/8 电路与 `20260807_multiround_8c_067/convergence_summary.json` **逐值精确吻合**（0.28/1.00/1.54/1.63/1.33/0.99/0.57/1.25，均值 1.074），纯 G 列均值 0.161 亦同源。→ 四列**都无 F1–F6 反馈**，该表实际对比"候选空间 + 排序启发式"。**附带修正三处**：表注"随机列与混合列共享 R/G/B/**JOINT** 候选类型"不成立（随机列实测 B 7154/G 3114/R 1954，**JOINT 0**）；`tab:configs` 中"20 轮收敛"列的 `F1--F6 失效反馈 = 轮内 + 跨轮` 无依据；**表 6 三列基线所用的 `20260826_ablation_pureG/pureB/random_seed{1,2,3}` 目录顶层运行脚本 0 个**（.bat/.sh/.md/.log 全无），调用命令未归档 | `code/scripts/run_hybrid_repair.py`（imports + 输出 schema grep）、`20260807_multiround_8c_067/run_all.bat` 与 `convergence_summary.json`、`20260826_ablation_*/hybrid_result.json`、探针 `scratch/probe_ablation_cfg{,2}.py` | **已改**：§4.4 首段重写为"比较候选空间与候选排序两类设置"并明示"各列由同一固定权重运行器产生、不构成失效反馈的开关对照，失效反馈的独立贡献需另设对照实验量化"；表标题改为"候选空间与候选排序设置的 WNS 改善对比"；表注改为"纯 G/纯 B 列分别只生成 G/B 候选，随机列与混合列在混合候选空间生成候选（混合列另含 JOINT 组合候选）…各列均使用固定搜索权重、不启用 F1--F6 权重重整"；`tab:configs` 20 轮收敛列反馈行改为"不启用（固定权重）"并在表注说明。遗留：**核心主张 Failure-Aware 目前仍无有效对照**，须由 `planning/FAECO_V2_DESIGN_PLAN_20260923.md` §2 的三臂实验补齐（且须归档运行命令 + 在结果 JSON 记录 `enable_feedback`）。**2026-09-24 三臂实验已完成整改与补齐**：运行命令归档（`run_config.json`：argv+resolved args+git head+臂身份）与结果 JSON 的 `enable_feedback`/`feedback_config` 均已落地（提交 `6e44fae`→`6276cff`）；三臂 × 8 电路结果见 `reports/FAECO_L2_THREEARM_20260924.md`——**§6.4 行 ③ 命中：EMA 失效反馈在 k=8 混合候选 regime 下无独立贡献**（8/8 电路终点/k₁st/maxB(k) 与 fixed 全等，4 电路多花 9%–116% STA），价值定位回退到「候选空间 + 权重排序」（random 臂 k₁st 恶化 1–2 个数量级为对照证据）。**遗留**：k=1（隔离反馈 regime）的 fixed vs adaptive 补充对未跑，L2 最终判读待用户裁定 | 用户（投稿前补实验） |
| OI-013 | **20260826 批次产物只能部分由 codex HEAD 复现（revision 未钉死）** | 2026-09-23 | **待裁定（发现于 0a 步骤 5；不阻塞 L2）；2026-09-24 影响面已收窄（legacy regression 附带的 8 电路复现性检查）** | 0a 步骤 5 做对照时顺带验证产物可复现性：**`s382` 完全复现（24/24，含 `n_candidate_sta_runs=22`）**，但 **`b03` 仅 12/24、`b06` 仅 8/24**，且差异落在 decision core（非仅计数）：`b03` 产物 `-1.27`（8 轮每轮接受）vs HEAD/`30f4164` 给 `-1.21`；`b06` 产物 6 个 `--tns-aware` 接受（TNS -3.98→-3.92，`stop=max_iterations`）vs HEAD 无接受（`stop=stagnation`）。**已排除**：环境（Yosys `0.67+146` 与产物 `map.log` 逐字相同）、参数复原方法（s382 已 24/24）、束宽（b03 在 k=1 与 k=8 结果相同）、HEAD 特有（`3e93fd2`、`30f4164` 两处 worktree 定点重跑 b03 仍 `-1.21`）。**2026-09-24 更新（legacy regression 配置 A 的附带检查，`reports/FAECO_LEGACY_REGRESSION_20260923.md` §8）**：ISCAS89 批次用配置 A（k=1、**无** `--tns-aware`）在 **7/8 电路 decision-reproducible**（`s27/s382/s420/s641/s713/s820/s953`，其中 `s713`/`s820` 仅差一个 `E6.n_candidate_sta_runs` 计数），唯一例外 **`s832` 为"路径不同、终点相同"**（最终 `wns=-1.16`/`tns=-5.48`/`final_patch_id`/`final_netlist_hash` 全等，仅接受轮次 1–3 vs 1–4 不同）。**且实测 `--tns-aware` 只属 ITC-99 批次**：s382 不含该开关复现 24/24，含该开关首轮接受点 `-0.88→-0.98`、匹配度降至 11/24（已登记为契约修订 A8） | `code/scripts/compare_0a_equivalence.py`；产物时间戳（`s382 11:22 / b03 11:25 / b01 11:29 / b06 11:51`）对照 08-26 当天 7 个落在 10:47–12:25 的代码提交（`5966991` 恢复 critical-path cover 首选候选、`d595c71` 保留非 R 可改写门、`30f4164`/`b7abaac`/`c58ad8e` 改 F2/SEC 检查而检查结果经 `r_available_for` 反向影响候选生成）；三个 worktree 定点重跑；`code/scripts/compare_equivalence_sweep.py`（2026-09-24 新增的多电路聚合判定） | **定性已完成，revision 待钉**：这是 codex 谱系内部 08-26→08-28 的**既有漂移**，非本次合并引入。需用户裁定"论文主实验基线取哪个 revision"——(A) 认 HEAD 行为（则 `b03`/`b06` 相关数字需按 HEAD 重跑更新，方向是 HEAD 更优：-1.21 优于 -1.27）；(B) 认 08-26 产物（则须继续定位到具体 commit 并固化 tag）。**裁定影响面已收窄**：ISCAS89 侧 7/8 电路的论文数字可由 HEAD 复现（`s713`/`s820` 需接受 E6 计数口径差异），`s832` 终值一致仅轨迹不同 ⇒ 实质分歧集中在 **ITC-99 的 `b03`/`b06`（终值不同）**。**另有 2 个未记入论文的开关需登记**：`candidates_per_iteration=1`（两批次共用）与 `tns_aware=true`（**仅 ITC-99 批次**，见报告 §5.3 与契约 A8） | 用户（投稿前） |

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
