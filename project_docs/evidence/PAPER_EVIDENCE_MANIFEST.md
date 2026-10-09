# 论文证据清单（Paper Evidence Manifest）

日期：2026-09-28　定位：`.tex` 统一重构（技术证据冻结 → 论文统一重构）的**前置门槛**——改字前先把每个数字钉到一个实验族。

## 硬约束（改论文时必须遵守）

1. **`same claim ⇒ same code revision + same config family`**（OI-013-A）。一个数字只能来自**一个**实验族。
2. **禁止跨族拼接**：不得把 08-26 产物、sprint1/efficiency-first、`faeco-exp-rev1` 三者的数字放进同一张表或同一句结论。
3. **冻结 revision**：annotated tag **`faeco-exp-rev1` → `87d01ba`**。受 revision 影响的结果须以该 tag + 同一 config family 重跑，方可作为未来主结果。
4. **零回退 ≠ 无回退声明**：只报 WNS 改善，不等同 timing closure。
5. **指标纪律**：`windows_offered` / `N_extracted` 是**重复扫描**指标，**不作**"搜索空间扩大"证据；唯一窗口数用 `N_unique_window`（canonical 窗口哈希去重）。
6. 论文正文**不写工程路径**；路径映射只在本文件与 `CROSSWALK_TEMPLATE.md`。

## 0. 实验族（Family）总表

| 族 | 名称 | 产物目录 | git ref | 关键配置 |
|---|---|---|---|---|
| **A** | sprint1 / efficiency-first（`iterations=1`） | `experiments/20260805_tcad_sprint1_iscas89/`、`20260805_tcad_sprint1_itc99/` | 未钉 revision（2026-08-05 期历史族），**在冻结 revision 下不可复现**（见 A\*）；Yosys `0.67+146`（`map.log` 首行与 B 族逐字相同） | `--max-iterations 1 --early-stop` |
| **A\*** | 效率优先 **@ 冻结 revision** 重跑（判 A 的可复现性） | `experiments/20260928_sprint1/`（8/8 `exit=0`） | git HEAD `6b95f8c`（`run_config.json → git_head`） | 与 A 同配置：`--period 0.5 --max-iterations 1 --candidates-per-iteration 1 --joint-enumerate-depth 3 --early-stop --priority-table …` |
| **A′** | 效率优先候选 → OpenROAD/全局布线后验 | `experiments/20260807_real_pr_iscas8/` | 同上 | 消费 A 族接受候选做后验物理估计 |
| **A″** | SPEF 负载扫描 + 迭代式物理门控 | `20260805_parasitic_s382_scan/`、`20260805_parasitic_b18_scan/`、`20260805_phys_closure/` | 同上 | `--physical-gate`、`unit_len_um=40`；**未标定**（OI-016） |
| **B** | 20260826 统一迭代环主实验（≤8 轮，启用跨轮失效反馈） | `20260826_iscas89_main/`、`20260826_itc99_main/`、`20260826_picorv32_hetero/`、`20260826_sec/`、`20260908_phase2_b17_resume/`，聚合 `20260826_aggregation/summary.json` | 历史族（未钉 revision）；**b03/b06 在 HEAD 上有漂移**（OI-013） | `iterations≤8`、跨轮失效反馈；ITC-99 批次含 `--tns-aware`，ISCAS89 批次不含 |
| **C** | 20 轮收敛配置：候选空间与排序（**固定权重，无 F1–F6**） | 混合列 `20260807_multiround_8c_067/convergence_summary.json`；纯 G/纯 B/随机列 `20260826_ablation_pureG`、`_pureB`、`_random_seed{1,2,3}`，聚合 `20260826_aggregation/ablation_summary.json` | `run_hybrid_repair.py`（不使用 `refine_weights`/`enable_feedback`） | 20 轮上限、固定搜索权重、同预算 |
| **D** | L2 三臂 + k=1 判别（EMA 独立贡献 = 无） | `20260924_threearm/`（+`_aggregation/threearm_report.json`）、`20260924_l2_k1/`（+`_aggregation/k1_discriminant.json`） | `main @ 6276cff`（三臂）、`main @ 1a54087`（k=1） | k=8 三臂 / k=1 两臂，`--no-feedback` vs `--feedback-ema`，`--sta-budget 500` |
| **E** | L3 S 环路消融（**历史族，已被 L1 取代**） | `20260924_l3s_ablation/`、`_k4` | L1 前 | k=8、20 轮、预算 700 |
| **F** | **L1 S 窗口来源（决定性）** | `20260928_s_l1_ablation/`（8 电路 × {off,on}，16/16 `ALL_RUNS_DONE`），聚合 `aggregation/summarize_s_l1.json` | **tag `faeco-exp-rev1` → `87d01ba`** | `on` = `--resynth-per-iteration 8 --resynth-window-pool 32`；两臂同 `--sta-budget 1600`（**不绑定**，max 482） |
| **G** | 3-A 电气风险前置诊断（**内部诊断，不作论文主张**） | `20260926_electrical_3a/`，报告 `reports/FAECO_ELECTRICAL_3A_20260927.md` | — | 四臂采集；判 NO SIGNAL |

## 1. 主张骨架 → 证据绑定

### 主张 1 · 候选空间扩展 + 结构化排序（含能力边界）
- 多特征加权割 $C_w$ + 关键路径覆盖割 $C_c$；R/G/B/JOINT 四类变换 → §3（方法，无数字）。
- **排序有价值**：族 C 混合 20 轮均值 **1.074 ns** vs 纯 G **0.161**、纯 B **0.536**、随机 **0.398**；随机臂对照 $k_{1st}$ 恶化 1–2 个数量级（s641 1→123、s713 5→216、s953 1→185）← 族 D §3。
- **能力边界（S）**：族 F 三层裁决 → 见 §2 / 主张 4。

### 主张 2 · 类型化失效归因 + 分层验证
- F1–F6 结构化分类作为**搜索诊断/控制**机制（**不再**主张"反馈驱动收敛"的独立增益）。
- 触发分布（族 B，19 电路 / 4044 trials）：F4 2434、F5 915、F1 138、F3 16、F2 3、F6 0（ITC-99 主实验）。
- **反证据（必并列）**：族 D 三臂 + k=1 判别 → 8/8 电路 adaptive ≡ fixed **逐位相同**，top-1 候选身份 **0 次改变** ⇒ EMA 反馈**无独立贡献**，降级为可选机制。
- 分层验证：构造筛选 → 理想线网 STA →（可选）简化 SPEF 复测 → 独立全网表 SEC。

### 主张 3 · 可复现的迭代 ECO + 功能—时序—物理验证闭环
- 逐轮提交（`$N\gets N+\Delta$`）；冻结 revision + 族纪律（本文件规则 1–3）。
- 结果：族 B **8/8、18/19、2/3**；SEC 族 B 30 实例 → 29 产生网表修改、**28/29 完全证明**（b17 余 1 未证明点为同函数尺寸替换）；族 A′ 后验 PR **5/8 保持改善、1 持平、2 退化 ≤0.02 ns**。

### 主张 4 · 结构候选扩展与能力边界（负结果，S）
- 族 F：$N_{\text{unique window}} = N_S = N_{\text{measured}} = \mathbf{126}$（**无重复窗口哈希**）、$N_{\text{extracted}}=1724$。
- 历史池 8 上限 ⇒ S 候选 **37 → 126（3.4×）**；机制 = 候选数被 `candidates_per_iteration`(=8) 池上限钉死，L1 后 = 每轮配额(8) × 参与轮数。
- 质量层：$\Delta L(\text{SKY130})>0$ **76/126（60.3%）**（历史 16/37 = 43%）；但 $\Delta WNS>0$ **0/126**、$\Delta WNS<0$ **90/126**。
- 能力层：**接受 0/8**，配对 $\Delta WNS$(on−off) **全 0.000**。
- ⇒ 口径：**枚举瓶颈已排除**，但当前 S 构造在该 benchmark/regime 下**无 timing repair capability**；**逻辑深度下降不足以转化为端到端 WNS 收益**。

## 2. 逐数字绑定（论文位置 → 数字 → 族 → 结果文件）

| 论文位置 | 数字 / 结论 | 族 | 结果文件 | 复核 |
|---|---|---|---|---|
| 摘要 / 1.3 / 结论 | ISCAS89 8/8 严格改善 | **B** | `20260826_aggregation/summary.json` → `iscas89[]`（8 条全 `final>baseline`） | ✅ |
| 摘要 / 1.3 / 结论 | ITC-99 18/19（b06 持平） | **B** | 同上 → `itc99[]`（19 条，b06 $\Delta=0$） | ✅ |
| 摘要 / 1.3 / 结论 | PicoRV32 2/3（`picorv32_regs` 无 setup 路径） | **B** | 同上 → `picorv32[]` | ✅ |
| §4.3 ITC-99 成本 | 19 电路共 **3363** 次候选级 STA | **B** | 同上 → $\sum$ `n_candidate_sta_runs` = 3363 | ✅ |
| §4.3 ITC-99 分布 | 中位数 **+0.18** ns、均值 **+0.43** ns | **B** | 同上（19 值重算一致） | ✅ |
| §4.3 b17 | 默认 60 s 全拒；放宽 180 s 得 **+0.38** ns；**104** 次 STA；接受 G:nor4b₁→nor4b₂ | **B** | `20260908_phase2_b17_resume/`（`summary.json` → `itc99[] b17.scaled_run`） | ✅ |
| §4.3 b06 | `-0.56` 持平；**664** 次候选级 STA 中**无一次严格超过基线** | **B** | `20260826_itc99_main/b06/b06/eval_trials.json`（`trials` 长度 = **664**） | ✅ 2026-09-28 审计：正文已删「333 持平」明细，只保留「无一次严格超过」，与 664 trials 口径一致 |
| §4.3 b18/b19 | +0.07 / +1.44 ns；**7.57 万 / 15.10 万个 SKY130 单元**；24 / 59 次 STA | **B** | `20260804_itc99_b18b19_repair/{b18,b19}/`：`outerloop_result.json`（`baseline_wns` −13.34 / −17.44、`wns_history[-1]` −13.27 / −16.0、`n_candidate_sta_runs` 24 / 59）+ `map.log`（`Number of cells` = **75 707 / 151 047**；dff 3 270 / 6 542，与 ITC'99 官方 b18 3 320 FF、b19 6 642 FF 相符，确认为公开 b18/b19） | ✅ 2026-09-28 全部逐项复核；**原「37.6 万 / 75.5 万门」在任何证据文件中均无法定位，已更正为映射网表单元数** |
| §4.3.2 PicoRV32 | +1.13 / +0.07 ns | **B** | `20260826_aggregation/summary.json` → `picorv32[]` | ✅ |
| §4.3 SEC | 30 实例 / 29 修改 / **28/29 完全证明**；b17 12812 已证明 + 1 未证明 | **B**（b17 = phase-2） | `20260826_sec/summary.csv`（**29 行 PASS + `picorv32_regs` N/A，共 30 行**——2026-09-29 实读更正，原记"22 行 PASS"为笔误；30/29/28+1 口径与正文逐项吻合）、`20260908_phase2_b17_resume/sec/sec_result.json` | ✅ |
| §4.2 图 3 + §4.5 表 7 预布局列（**效率优先子研究**） | ISCAS89：`-0.18/-0.89/-1.55/-1.59/-1.31/-1.17/-1.17/-1.27`（s420 仅 +0.01 ns） | **A** | `20260805_tcad_sprint1_iscas89/<c>/<c>/outerloop_result.json` → `wns_history[-1]`（8/8 逐值吻合） | ✅ |
| §4.5 表 7 全局布线列 | 5 改善 / 1 持平 / 2 退化 ≤0.02 ns | **A′** | `20260807_real_pr_iscas8/post_route_audit_summary.json` / `pre_layout_audit_summary.json` | ✅ 逐值吻合 |
| §4.2 策略分布 | JOINT 4（s27/s382/s420/s953）/ G 3（s641/s713/s832）/ R 1（s820） | **A** | `20260805_tcad_sprint1_iscas89/<c>/<c>/eval_trials.json` → `call_log[0].accepted.kind`（**注意该文件是多对象拼接、非严格 JSON，须用 `JSONDecoder().raw_decode` 读首对象**）；独立印证 `20260807_real_pr_iscas8/manifest.json` 的 8 条候选标签 | ✅ 两独立台账一致 |
| §4.2 可复现性限制 | 冻结 revision 重跑：仍 8/8 改善，但分布变为 G 6 / JOINT 1（s382）/ R 1（s820）；s382 2→41 次 STA、s420 90→66 次 | **A\*** | `20260928_sprint1/<c>/outerloop_result.json` + `eval_trials.json`（accepted `kind`） | ✅ |
| §4.4 表 6 纯 G / 纯 B / 随机（均值 0.161 / 0.536 / 0.398） | — | **C** | `20260826_ablation_pureG`、`_pureB`、`_random_seed{1,2,3}` → `ablation_summary.json` | ✅ |
| §4.4 表 6 混合 20 轮（均值 **1.074**） | — | **C** | `20260807_multiround_8c_067/convergence_summary.json`（逐值吻合） | ✅ |
| §4.4 (iii) EMA 无独立贡献 | adaptive ≡ fixed 8/8 逐位相同；top-1 身份 0 次改变 | **D** | `20260924_l3s_*` 之外的 `20260924_threearm_*`、`20260924_l2_k1_*` | ✅ |
| §4.6 SPEF 门控 | s382 的 50、b18 的 6 个候选均未通过复测 | **A″** | `20260805_parasitic_s382_scan/`、`20260805_parasitic_b18_scan/` | ⚠️ 待逐项复核；**表述按 OI-015 降级口径** |
| §4.6 S 能力边界（新增） | 37→126（3.4×）；76/126；0/126；90/126；接受 0/8；配对全 0.000；$N_{\text{extracted}}$=1724 | **F** | `20260928_s_l1_ablation/aggregation/summarize_s_l1.json`（`totals` / `tier1` / `tier2_totals` / `tier3`） | ✅ |
| §4.6 S 纪律（新增） | 控制臂 8/8 逐位复现；非 S 试验序列逐位相同；预算不绑定（max 482/1600） | **F** | 同上 + `reports/FAECO_S_L1_WINDOW_POOL_20260928.md` §3 | ✅ |
| §4.6 表 8 S 三层 | 枚举 37→126 / 结构 76/126（60.3%，历史 16/37=43%）/ 时序 0/126、90/126、0/8、配对 0.000 | **F** | 同上 | ✅ |
| §4.4 / §结论 limitation EMA（新增） | adaptive ≡ fixed 8/8 逐位相同；top-1 身份 0 次改变 | **D** | `20260924_l2_k1_aggregation/k1_discriminant.json`、`20260924_threearm_aggregation/threearm_report.json` | ✅ |

## 3. 禁用 / 不可用字段

| 字段 / 台账 | 处置 | 依据 |
|---|---|---|
| `structure_resynth.rejections`（s420） | **任何论文统计或机制主张都不得引用**，直到 OI-017 闭合 | OI-017（8 窗口 × {S0,S1,S2} 无法同时产出 6 候选 + 6 条 S0 拒绝） |
| `windows_offered` / `N_extracted` | 只作内部扫描开销；**不得**作"搜索空间扩大"证据 | OI-014 指标纪律（$N_{\text{extracted}}$=1724 ≫ 126） |
| F6 / 物理增益类表述 | 只可主张"识别并**拒绝少量** ideal-net 有利、物理失效的候选"；**不得**主张"显著改善物理 WNS" | OI-015 裁定 |
| 3-A 采集结论 | **内部诊断**（判 NO SIGNAL），不进入论文主张 | `reports/FAECO_ELECTRICAL_3A_20260927.md` |
| 族 E（`20260924_l3s_ablation`）的"37 候选 / 接受 0" | 只可作"历史族"引用；**主营 S 结论改用族 F** | 族 E 被集成缺陷混淆（池 8 上限） |
| 事件名 `acceptance_budget_violation` | 与现行 `F4_timing_gain_insufficient` 语义一致但字符串不一致，需在补充材料说明 | OI-008 |

## 4. 本次核对发现的**口径问题**（需用户确认后才改 `.tex`）

| # | 问题 | 事实 | 处置 |
|---|---|---|---|
| **D-1** ✅ 已落地 | 摘要/结论"三组 8/8、18/19、2/3"跨族 | "18/19"与"2/3"只来自**族 B**；"8/8"在 §4.2 是**族 A**（sprint1）——同一 claim token 混用两族（族 B 自身亦有 ISCAS89 8/8） | 三元组**整体绑到族 B**（摘要中/英与 §4.3 明写"统一跨测试集评估 + 同一实验族 + 同一 revision 绑定"）；§4.2 改题为**效率优先子研究**并与 §4.3 明确分开统计 |
| **D-2** ✅ 已落地 | 族 A / 族 B 的 revision 可复现性 | 族 B 为历史族（b03/b06 有漂移，OI-013）；**族 A 亦**为历史族，且经 **A\*** 证实**在冻结 revision 下不可复现** | §4.2 加 **"族与可复现性"** 段：声明"A 为历史冻结产物、revision 未完整钉定"，并如实并列 A\* 的分布差异；§结论 把"全部数字绑定固定 revision"改为"绑定明确实验族，A 单独声明限制"；**不做反向 commit 猜测** |
| **D-3** ❌ **前提被推翻** | §4.2 策略分布无证据（OI-010-A） | **更正**：族 A 自身 `eval_trials.json` 的 `call_log[0].accepted.kind` **支持** JOINT 4/G 3/R 1，且 A′ 的 `manifest.json` 8 条候选标签**逐条印证**。此前"两族均不支持"是把该文件（**多对象拼接、非严格 JSON**）按单对象 `json.load` 读、异常被 `try/except` 静默吞掉所致的**解析错误** | **不删除该分布**（有据可查）；§4.2 补上台账来源说明。A\* 重跑得 G 6/JOINT 1/R 1，只作**可复现性限制**并列报告，**不用它替换 A 的历史数字**（否则即"从其他实验族借数字"） |

## 5. 复现锚点

- 族 F：`git checkout faeco-exp-rev1`；`bash code/scripts/run_s_ablation_batch.sh off,on s27,s382,s420,s641,s713,s820,s832,s953`（`FAECO_RESYNTH_PER_ITER=8 FAECO_RESYNTH_WINDOW_POOL=32 FAECO_STA_BUDGET=1600`）；裁决 `.venv/Scripts/python.exe code/scripts/summarize_s_l1.py --root experiments/20260928_s_l1_ablation`。
- 族 B：聚合 `experiments/20260826_aggregation/aggregate.py` → `summary.json`。
- 族 C：`experiments/20260826_aggregation/ablation_summary.py`；混合列 `20260807_multiround_8c_067/convergence_summary.json`。
- 族 A：`experiments/20260805_tcad_sprint1_iscas89/`。**读法陷阱**：`eval_trials.json` 为**多对象拼接、非严格 JSON**，必须
  `json.JSONDecoder().raw_decode(open(p, encoding='utf-8').read())[0]`，**不可**用 `json.load`（会抛 `Extra data`；若被
  `try/except` 吞掉则误判为"无 kind 字段"，曾据此错判 OI-010）。
- 族 A\*：`bash code/scripts/run_sprint1_batch.sh`（`FAECO_OUT_ROOT=experiments/20260928_sprint1 FAECO_K=1 FAECO_PARALLEL=4 FAECO_EXTRA="--priority-table code/src/rseco/strategy_priority_table.json"`）；判分布：读 `eval_trials.json → trials[*].accepted==True → kind`。
- 族 D：`code/scripts/compare_threearm.py`、`code/scripts/analyze_k1_discriminant.py`。
- 工具链版本：Yosys `0.67+146`（`map.log` 首行，族 A/B/F 逐字相同）；OpenSTA 3.1.0（WSL）；SEC 走 WSL Yosys 0.33。

## 6. 最终发布前审计 + 冻结（2026-09-28）

**★ 当前发布版（2026-10-09 摘要可读性改写，v5）**：tag **`v2026-10-09-abstract-plain`**（论文 tag `faeco-paper-final-20261009b`）；PDF 字节 SHA256 **`5c37725a3850a6e18ba2480584f08582d98d143171b9dad0425a528a95a737fa`**（双副本一致）；**内容指纹（poppler 25.07）`0a2b0723e174307216184700bc47fa4c0f4ced730c55e373762ff10cbb1573cf`**；**9 页 / 0 Error / 0 Overfull / 0 Underfull**。改动**仅中/英摘要两段**（用户反馈"技术要点过多、大同行难懂"）：去 R/G/B/JOINT、F1--F6、加权割、扇入锥、SPEF/SEC、纯 G 等未展开机制名与缩写，改概念化表述并补"为什么重要"；结果层保留 8/8、18/19、2/3、1.07 vs 0.16 与"无退化/非时序收敛"边界。中文 264 字、英文 148 词（JCAD ≤300/≤150）。**零数字改动、零实验改动、零主张改动**——正文、公式、图表、参考文献均未变，各数字绑定不受影响。基线 manifest `versions/v5/MANIFEST.sha256`（117 条全 OK），v4/v3/v2/v1 依次 superseded。Word 转排稿随管线重建（`paper/zh/submission/word/FAECO_投稿Word转排_20261009b.*`）。
**★ 前序发布版（2026-10-09 参考文献规范修复，v4）**：tag **`v2026-10-09-reference-fix`**（论文 tag `faeco-paper-final-20261009`）；PDF 字节 SHA256 **`dea21bb38b70d4d4ff6c1eb276760da8f3842e78cd738a50ff3199d6a062cd81`**（双副本一致）；**内容指纹（poppler 25.07）`6ca972d512132958ed42d29b4eed5f8d3766de4bee0c7b2dc7ca54dc592c4121`**；**9 页 / 0 Error / 0 Overfull / 0 Underfull**。改动仅参考文献呈现：`thebibliography` 19→14 条（按正文首次引用顺序重排，修 P0）、5 条纯 URL 工具/文档引用改正文页脚脚注（`\footnote{\url{…}}`，JCAD 一.12）、会议文献 `[C] //` 空格、期刊名 `Integration` 全称、BUFFALO 题名补全、kravets 页码 `71:1-71:6`。**零数字改动、零实验改动、零正文主张改动**——各数字绑定不受影响（见 §2/§4 逐数字表）。基线 manifest `versions/v4/MANIFEST.sha256`（117 条全 OK），v3/v2/v1 依次 superseded。Word 转排稿随管线重建（`paper/zh/submission/word/FAECO_投稿Word转排_20261009.*`）。
**★ 前序发布版（2026-09-30 终审 5 处正文一致性修正）**：PDF 字节 SHA256 **`28647dc083282ffb2dce1837b08726315de3eca1b2201539454a396767c46fb8`**（双副本一致）；**内容指纹（poppler 25.07）`70bbd6103c993ead46e4100d902a3c0dd70c04ec2328c64a49d82e519cbfbeb0`**；**9 页 / 0 Error / 0 Overfull / 0 Underfull**。改动 5 处：§3.4 F6 交叉引用纠错（§4.4→§4.5）、§4.1 接受准则闭合 b06 例外复述、摘要（中/英）PicoRV32 分母解释（`picorv32_regs` 无 setup path 不参与判定）、表 8 补 ΔL/ΔWNS 符号定义、§4.5 F6 措辞与方法层对齐——**零数字改动、零实验改动，全部数字绑定不变**。基线 `v2026-09-30-submission-ready-r2`（manifest `versions/v3/MANIFEST.sha256`），v2/v1 依次 superseded。
**★ 前序发布版（2026-09-30 投稿格式适配 · 摘要改写，OI-020 授权）**：PDF 字节 SHA256 **`df82292f21b791be6572e6e1832aedb787ec2e47a9bb2a5208eb0bfbb42906df`**（双副本一致）；**内容指纹（poppler 25.07）`43becd394413276053e9c28f690c1248bdd9841b44d6fd2e8fc09a381b8f5c1f`**；**9 页 / 0 Error / 0 Overfull / 0 Underfull**。改动仅中英摘要两段（中文压至 295 字、去"本文"句式；英文压至 149 词），**全部数字、实验族归属、表格、其余章节零改动**——各数字绑定不受影响（摘要数字 8/8、18/19、2/3 仍属族 B，1.07/0.16 仍属族 C）。基线 `v2026-09-30-submission-ready`（manifest `versions/v2/MANIFEST.sha256`），前一基线 `v2026-09-29-submission-ready`（manifest `versions/v1/`）标记 superseded、保留可回溯。
**★ 前序发布版（2026-09-29 终稿收敛两批 + 版面收尾）**：tag **`faeco-paper-final-20260929`**（提交 `a8142b6`）；PDF SHA256 **`9af41d77…`**（两份一致）；**9 页 / 0 Error / 0 Overfull / 0 Underfull**。
**★ 内容指纹（判定"内容是否真一致"须用此项）**：`pdftotext -layout` 全文的 SHA256 = **`7adf027909213f00ba3dab5af68f8189b878e43c63e0a40844ed509bd78587b6`**。**PDF 字节 SHA256 含编译时间戳，重编译必变，不可作内容指纹**——已实测：同一 `.tex` 重编译后字节 SHA256 由 `5c98b77d…` 变为 `611741c5…`，但页数、质量门、文本指纹三者全同。
**【2026-09-29 晚补注：指纹与 pdftotext 实现绑定】** 本指纹由 **poppler 25.07.0**（WinGet：`%LOCALAPPDATA%\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin\pdftotext.exe`）产出；Git Bash 默认解析的 `pdftotext` 是 **xpdf 4.00**（`C:\Program Files\Git\mingw64\bin\`），对同一 PDF 给出**不同的**指纹 `443c5c3a…`（内容等价、提取文本不同）。复算不一致时先核对工具，再谈内容（经验库第 11 条）。本日已用 poppler 25.07.0 复算**精确复现** `7adf0279…`，且 git 工作区干净、字节 SHA256 与本节记录一致——**冻结完好**。
**前序版本链（均保留，可逐级回溯）**：`faeco-paper-layout-final`（9 页，SHA256 `5c98b77d…`，指纹 `856fac5b…`）→ 2026-09-29 第一批（评审 10 项，SHA256 `820e8cff…`，指纹 `7da2dc7d…`）→ 2026-09-29 第二批（必改 4 项 + 版面收尾，即当前版）。**当前版相对第一批仅有 4 处口径/表述改动 + 1 处 `\FloatBarrier` 删除；全部数字、实验族归属、表格数值未变。**

**终稿批次一（2026-09-29，评审第二轮 10 项）**：摘要减负约 25%（删 SEC 28/29 与 S 的四个数字）、术语统一「失败→失效」、相关工作两处降调、表 1 定位改「局部时序 ECO」、§4.1 去审计味、**式(2) 的 0.01/0.1 补真实解释**（已回代码核实 `code/src/rseco/cut.py:200/202` 为硬编码常量）、表 2 精简、表 3 改名、图 2 图注压一句并放大、§4.6 措辞、§3.4 改「启用失效反馈控制时」。

**终稿批次二（2026-09-29，必改 4 项）**：① §4.1 明确 WNS 严格改善为主口径、b06 的 TNS 辅助接受**不计入**"严格 WNS 改善"统计（消解 §4.3「18/19」的口径歧义）；② §4.1 修正 §4.5 的实验族归属（OpenROAD 后验用 §4.2 接受候选；SPEF 负载扫描与门控实验单独报告）；③ §3.3/§3.5 失效反馈统一为"启用式"并定位为搜索诊断与控制机制（独立增益交 §4.4 检验）；④ §4.4 改"两组实验"句式（先候选空间与排序，再单独检验 Fixed/Adaptive）。**以上 4 项均为表述/口径，不触及任何数字与证据绑定。**

**版面收尾（2026-09-29，仅排版）**：批次二使正文净变动后回到 10 页（第 10 页仅 8 条参考文献、约 80% 空白）。根因：**`placeins` 的 `\FloatBarrier` 在双栏模式下遇到待排浮动体会退化为 `\clearpage`**——§3.4 表 `tab:failures` 之后、§3.5 之前的那个屏障前方有表未排出，于是强制结束第 5 页，正文整体后移，参考文献被挤成孤儿页。**删除该处唯一一个多余 `\FloatBarrier` 即恢复 9 页**：第 5 页 = 图 2 + §3.3 正文 + 表 3 + §3.5 开头，第 9 页 = §5 结论 + 参考文献 [1]–[19]（约 95% 满）。除该行外`.tex` 与上一版逐字节相同（`diff` 仅 `311d310`）。

**机械终检（2026-09-29，用户指定的最后一轮检查）**：0 处 `??`；日志无 `LaTeX Warning: Reference/Citation`、无 undefined references；29 个 `\label` 无重复；19 条 `\bibitem` 与 19 个 `\cite` 键一一对应（无孤立条目、无缺失条目）。**遗留（无可见影响，未改）**：6 个 `\label` 未被 `\ref` 引用（`eq:dtiming`、`sec:exp`、`sec:impl`、`sec:overview`、`sec:conclusion`、`tab:s_boundary`）——删标签或补引用均属内容改动，按"停止内容修改"保留原样；`\ref{#1}` 的报警来自第 44 行 `\eqref` 宏重定义，为检查脚本误报。

**版面修复（2026-09-28，仅排版、不动任何数字/主张）**：原第 5 页仅 7 行、约 80% 空白，且 §3.3 正文被截断跨页。根因：图 2 是 1254×1254 正方形 `figure*`，`width=0.85\textwidth`（14.4×14.4 cm），配合 `[!htbp]` 中的 `p`（允许生成纯浮动页）与图前 `\FloatBarrier` 夹逼，LaTeX 生成只含图的浮动页。修复：图 2 改 `[!tb]`（禁浮动页）+ `width=0.55\textwidth`、删除图前屏障、合并 2 组相邻重复 `\FloatBarrier`（292/293、343/344）。结果：**10 页 → 9 页**，第 5 页 7→43 行（图 2 + 正文 + 表 3 同页共存），末页结论与参考文献 [1]–[19] 同页、不再孤立成页。

审计五项结论（探针：`scratch/probe_final_audit.py`、`probe_headline_numbers.py`、`probe_c_means.py`）：

1. **四处同口径**：标题（中/英）、摘要（中/英）、§1.3 贡献、§结论 均以「结构化候选搜索 + 类型化失效归因 + 可复现迭代闭环」三支柱叙述；`Failure-Aware` = 0、`失效驱动` = 0、`独立提升` = 0。3 处 `独立贡献` 与 2 处 `自适应收敛` 全为**否定式/对照式**表述。
2. **数字可唯一定位**：用户点名的 8/8、18/19、2/3、1.07、0.40、37→126、76/126、0/126 全部在族 B/C/F 中定位并复算一致（1.074/0.398；F：uniq=cand=meas=126、sky=76、pos=0、neg=90、acc=0、paired_tied=8）。**审计中新发现并更正**：b18/b19 门数（见下）。
3. **实验族无交叉混用**：§4.2→族 A、§4.3→族 B、§4.4→族 C(+D)、§4.5→族 A′/A″、§4.6→族 F；§4.1 明示四组子研究不合并统计。
4. **高风险词扫描**：`失效驱动`/`驱动下一轮`/`提高搜索收益`/`SPEF反馈`/`独立提升`/`Failure-Aware` 均 0；`物理感知`=1（§2 述他人方向）；**修正 1 处**：§2 对比表 FAECO 行「按失败反馈迭代搜索」→「按失败类型结构化诊断与控制」。
5. **冻结**：打 tag 并记录 SHA256（如上）。

**本次审计更正（2 处，均为口径/事实，非结论）**：
- **b18/b19 门数**（§4.3.1）：原「37.6 万 / 75.5 万门」在 `20260804_itc99_b18b19_repair/` 的任何文件中均无法定位（`map.log` 实为 75 707 / 151 047 单元；`docs/engineering/n31_05_sequential_eco.md` 同文档内亦自相矛盾地写过「23–46 万门」）。**已更正为映射网表单元数**，绑到 `map.log`。
- **§2 对比表旧叙事**：「按失败反馈迭代搜索」与新口径（失效反馈为**诊断/控制**，不作独立增益）冲突，**已改为「按失败类型结构化诊断与控制」**。

**stale 标记**：`experiments/_stale_20260924_threearm_oldsign/`（旧符号结果，不参与任何证据链）**保留不删**，仅在 `.gitignore`/说明中标注为 stale 排错证据。

**表达与口径收敛（2026-09-28，用户评审 15 项中的优先 7 项）**：用户指出论文偏“实验审计报告”、负结果（EMA、S）出现过频而压住正贡献，要求做减法而非新增实验。已改：① 贡献 3 去掉“可复现”（§4.2 已承认早期族 revision 未完整钉定，易被审稿人抓住），并删除“数字绑定/不跨子研究拼接”等实验治理表述（留 §4.1）；② 贡献 1 删除 S 负结果整段、贡献 2 删除“首选候选身份 0 次改变”，负结果分别只留 §4.6 与 §4.4；③ §3.4 明确 EMA 为**可选扩展**（仅 §4.4 消融对象，不属主方法必要组成）；④ Algorithm 1 第 8 步与 §3.2(b) 把失效反馈改为“启用时才更新权重”；⑤ §4.2 删除无数据支撑的“JOINT 沿关键路径压缩多级逻辑深度”；⑥ §4.4 补 Adaptive 与 Fixed 在 8/8 电路上三项指标一致的定量句；⑦ 结论压为三段。**上述删减仅调整数字的出现位置与详略，被删数字在 §4 对应小节中仍完整保留并可定位，故本节各数字的证据绑定不受影响。**

**传播性更正（历史文档加注，不改原历史内容）**：`project_docs/review_history/paper_audit/consistency_audit_20260911.md` 第 32 行曾把「b18/b19 门数 37.6 万/75.5 万」列为"对账通过"结论，现将该行划除并加 **【2026-09-28 更正】** 注，指向本节。该文件其余内容为 2026-09-11 历史快照，整体保留；`project_docs/LOGS.md`、`review_history/response_reviewers_*.md`、`design_specs/engineering/n31_05_sequential_eco.md` 中的同源旧数字属**历史流水记录**，按约定原样保留、不篡改。

