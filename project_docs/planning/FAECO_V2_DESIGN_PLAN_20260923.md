# FAECO-v2 后续改善方案（三层收敛版）

> 日期：2026-09-23（r2 收敛版；r1 逐条核实版已被本版吸收）
> 输入：外部评审意见（7 项建议 / 9 节）+ 第二轮收敛意见（三层结构、顺序调整、S 严格定义、JOINT 规则、stale invalidation）
> 方法：**先核实事实前提**（以权威产物与代码为准）→ 评估工程可行性 → 收敛为三层主线 + 单项实施顺序
> 关联：`project_docs/OPEN_ISSUES.md`（OI-008 / OI-009 / OI-010 / **OI-011 / OI-012**）、`review_history/paper_audit/code_paper_feedback_audit_20260923.md`

---

## 0. 结论先行

1. **收敛意见采纳**：不再横向加功能，方法主线压成三层、论文核心贡献压成 3 条（§6），实施顺序改为
   **事实修正 → Mixed-Fixed 消融 → 失败率反馈 → ΔDepth → S → 电气风险前置**。
2. **但本轮核实发现一个比算法更前置的硬问题（OI-011）**：main 分支的 `code/` **不是**产出论文跨测试集主实验产物的那份实现——产出实现在 `codex/faeco-unified-loop` 分支。main 上**不存在逐轮累积行为**。任何阶段 1 的实验若在 main 上跑，数字与论文不可比。**必须最先处置。**
3. **第二个前置问题（OI-012）**：论文 §4.4 表 6 声称的"失效反馈开/关"对照**在运行器层面不成立**——表 6 四列用的都是不含任何 F1–F6 反馈的 `run_hybrid_repair.py`。也就是说，**当前论文对核心主张"Failure-Aware"没有任何有效对照**。这使 B（Mixed-Fixed 消融）从"最大证据缺口"升级为"**唯一控制变量缺失**"。
4. **两个"已实现但没写/没搬"的机制**（与上轮④同类）：
   - **增量 ECO 的提交/回滚/重抽**已在 codex 分支完整实现（`SearchState.accept_patch` / `rollback` / `replay` 哈希链 / 接受后 `refreshed_cone`）→ 属于**移植 + 论文如实化**，不是新机制；
   - 收敛意见提出的 **stale candidate invalidation 在结构上已被满足**（每轮从提交后的网表重抽关键实例与锥，旧候选自然作废），需要的是**写清楚**，不是补代码。
5. 真正需要新做的、价值最高的仍是 **S（局部结构重综合）**；且其工具链**大部分已在仓库中**（`yosys_abc.py` 已有 BLIF 规范化 + ABC `resyn2` 序列 + ABC CEC；SKY130 映射后 CEC 链亦已有）。S 必须与 **ΔDepth 采集**并为一组做，才能形成"深层逻辑 → 结构重综合 → 逻辑级减少 → 时序改善"的因果证据链。

---

## 1. 事实核实（以权威产物与代码为准）

### 1.1 评审意见逐条核实

| # | 意见主张 | 核实 | 证据 |
|---|---|---|---|
| ① | F1–F6 只是"失败一次权重 +1"，太像 heuristic | **成立**。`refinement.py:41–66` 为固定 if-else 映射表，每类 `+= 1.0`；初始权重全为 1.0（`RefinementWeights`） | `code/src/rseco/refinement.py` |
| ② | 缺"Mixed + 固定权重"对照，无法单独证明 Failure-Aware | **成立，且升级为"唯一控制变量缺失"**（见 §1.2 新-6） | 论文 §4.4 tab:ablation；`run_hybrid_repair.py` |
| ③ | ITC-99 中 G 主导、B/R 覆盖明显更低 | **半成立**。G 主导属实（G 覆盖 17/19 电路、约 69 次）；"B/R 覆盖低"**不成立**——B 覆盖 14/19 电路 33 次、R 覆盖 10/19 电路 29 次。准确表述应为"**收益幅度**由 G 主导" | `eval_trials.json` 的 `kind` 统计（`scratch/count_strategy_dist.py`） |
| ④ | Algorithm 1"不叠加补丁"→ 更像找最佳补丁 | **前提错误，方向正确**。实测 `base_netlist_hash` **逐轮内唯一、跨轮变化**，且变化发生在**接受轮之后**（b01 iter1 接受 1 个 patch → iter2 基准哈希改变；b01 8 轮 9 个基准、b03 9 个、b04 8 个、b05 8 个）；只有效率优先配置（sprint1，iters=1）不叠加 | 探针 `scratch/probe_base_hash2.py`（逐 trial 校验同轮哈希唯一、跨轮改变） |
| ⑤ | 物理信息只用于后验过滤，应前移到排序 | **成立，且有硬前置**：电气量 `max_transition`/`max_capacitance`/`max_fanout`/`area` 在 4044 条 trial 中**覆盖率 0**（字段存在、从未填充） | 探针 `scratch/check_feasibility_data.py` |
| ⑥ | b17 单独 60→180 s 是"针对 benchmark 调参" | **成立**（论文已披露，但方法层面不漂亮） | 论文 §4.3；`20260908_phase2_b17_resume` |
| ⑦ | 只以 WNS 为主要目标 | **部分不成立**。接受谓词已含 `tns_aware` 分支（ΔWNS=0 且 ΔTNS>0 亦可接受），且 20 轮收敛配置**实际已启用**（`--tns-aware`）；跨测试集主实验未启用 | `20260807_multiround_8c_067/run_all.bat`；论文 `eq:accept` §3.5 |
| ⑧ | 建议新增 ΔDepth 指标 | **部分已有**：sprint1 的 `outerloop_result.json` 含 `logic_level_before/after/reduction` 字段，但值为 None/0 未填充 | 探针 `scratch/check_accumulation.py` |
| ⑨ | 建议新增 S = 局部结构重综合 | **可行且价值最高；基础设施比预期完整**（见 §1.2 新-4） | `code/src/rseco/yosys_abc.py`（714 行） |

### 1.2 本轮新增核实（意见未提）

| 编号 | 发现 | 证据 |
|---|---|---|
| 新-1 | **OI-009**：Algorithm 1 第 250 行"各轮候选均相对固定基线 $G_0$ 评估，不叠加多个局部补丁"与实测矛盾；§4.3 对 PicoRV32 的"多类接受补丁叠加"表述反而与实测一致 → 论文自相矛盾 | `scratch/probe_base_hash2.py` |
| 新-2 | **OI-010**：§4.2 称 ISCAS89 策略分布为 4 JOINT + 3 G + 1 R；实测 **G 23 次/7 电路、R 4 次/2 电路、JOINT 0**。`RESULTS.md` §2 同源同错 | `scratch/count_strategy_dist.py` |
| 新-3 | **OI-011（高）main 分支 `code/` 并非产出主实验产物的实现**：产物字段 `base_netlist_hash`/`acceptance_evidence`/`sta_provenance`/`topology_metrics`/`cache_key`/`config_hash` 在 main 的 `code/` 中**全 0 命中**；产出实现位于 `codex/faeco-unified-loop`（其 `flow.py:483` 建 `SearchState`、`:684` 接受后 `refreshed_cone = extract_fanin_cone(...)`、`:726` 调 `accept_candidate`；`real_wns.py:784 accept_candidate` 内 `self.mapped_text = str(text)`）。main 侧 `flow.py:392` 锥只抽一次、`real_wns.py:197` 后 `mapped_text` 永不更新 → **main 无逐轮累积**。谱系：`merge-base = b8c3759 (2026-08-13)`，main 在 08-14~09-07 无提交（跨 20260826 主实验期） | `git grep` / `git log -S --all` / `git show codex/...` |
| 新-4 | **S 的基础设施已存在约 70%**：`yosys_abc.py` 已含 ① `_normalize_to_blif`（Verilog→BLIF）② `RESYN2_BUILTIN_SEQUENCE` = `balance; rewrite; refactor; balance; rewrite; rewrite -z; balance; refactor -z; rewrite -z; balance` ③ ABC `cec` 回检 ④ `check_mapped_blif_equivalence`（SKY130 映射后 BLIF vs 原网表 CEC）。缺的是：割窗口抽取/回填、库约束下重映射、窗口级 ΔDepth | `code/src/rseco/yosys_abc.py:15–27,103,215,536` |
| 新-5 | **增量 ECO 的提交/回滚/重抽已完整实现**（唯在 codex 分支）：`SearchState.accept_patch()` 原子追加 + 快照前态 + 推进 $G_r$ + 更新 `critical_endpoints/critical_instances/current_cone_gates`；`rollback()` 撤销末次 patch 并保留审计日志；`replay()` 带 base 哈希链连续性校验（`"accepted patch log is not a contiguous replay"`） | `codex/faeco-unified-loop:src/rseco/refinement_loop.py:134–190` |
| 新-6 | **OI-012：表 6 的"反馈开/关"对照不成立**。表 6 四列运行器均为 `run_hybrid_repair.py`，该脚本**不使用** `refine_weights`/`RefinementWeights`/`enable_feedback`（imports 仅 gate_sizing/buffer_insertion/logic_rewrite/netlist_audit/strategy_selector）→ 四列均无 F1–F6 反馈。故该表实际对比的是"**候选空间 + 排序启发式**" | `code/scripts/run_hybrid_repair.py`；`20260807_multiround_8c_067/run_all.bat` |
| 新-7 | 现有消融三臂**已有两臂可复用但不可直接比较**：`20260826_ablation_random_seed{1,2,3}` 的候选空间**已是混合**（B 7154 / G 3114 / R 1954 trials）且 `random_order=true`；缺失的是 **Mixed + 权重驱动排序 + 反馈关**（Mixed-Fixed）。三臂还跨两套运行日期（混合列 20260807 vs 基线 20260826），不可直接对比 | 探针 `scratch/probe_ablation_cfg{,2}.py` |
| 新-8 | **结果 JSON 未记录对照所必需的关键配置**：`hybrid_result.json` 无 `enable_feedback`/`strategies`/`init_weights`；仅 `random_order`/`rounds`/`seed` 有记录。→ 论文"禁用失效反馈""保持权重固定"等表述**无归档证据**，重做三臂时若不扩 schema 会重复同一缺口 | 同上 |

---

## 2. 三层结构（收敛后的主线）

### 第一层：当前论文必须完成

| 项 | 内容 | 为何必须 |
|---|---|---|
| **L1-a 事实修正** | OI-009（Algorithm 1 + §3.2/§3.5 改写为逐轮累积）、OI-010（§4.2 策略分布 + RESULTS.md §2）、**OI-012（§4.4 把表 6 重新定位为"候选空间/排序消融"）** | 这是**事实一致性**问题，优先于任何算法升级；三处都直接改变读者对方法性质的理解 |
| **L1-b Mixed-Fixed 消融** | 三臂、同预算、同轮数、同候选池、同 $w^{(0)}$：① **Mixed-Fixed**（混合池 + 权重驱动排序 + 反馈关）② **Mixed-Random**（混合池 + 随机顺序 + 反馈关）③ **FAECO-Adaptive**（混合池 + 权重驱动排序 + 反馈开） | 论文现在**无法回答**"收益来自混合候选空间还是失效反馈"；且现有表 6 无任何有效反馈对照（新-6） |

**统一口径（硬约束）**：$N_{\text{round}}=20$、候选级 STA 预算一致、候选池为 R/G/B/JOINT（引入 S 后为 R/G/B/S/JOINT）、$w^{(0)}=(1,1,1,1,1)$、period 0.5 ns、同一工具链、**同一运行日期批**。
**必须同时扩 schema**（新-8）：结果 JSON 记录 `enable_feedback`、`strategies`、`random_order`、`seed`、`init_weights`、`toolchain`、`n_candidate_sta_runs`、`n_sta_to_first_improvement`。

### 第二层：真正强化 Failure-Aware

**先只做全局失败率（C），复杂度受控；C′（按候选类型细分）留作第二步。**

$$r_j^{(t)} = \rho\, r_j^{(t-1)} + (1-\rho)\,\mathbb{1}[F_j], \qquad w_j^{(t+1)} = \mathrm{clip}\!\left(w_j^{(t)}(1+\eta r_j^{(t)}),\ w_{\min},\ w_{\max}\right)$$

**实施建议（保证与现有结果兼容）**：等价加性-率形式

$$w_j^{(t+1)} = \mathrm{clip}\!\left(w_j^{(t)} + \eta\, r_j^{(t)},\ w_{\min},\ w_{\max}\right)$$

在 $(\rho=0,\ \eta=1,\ \text{无 clip})$ 时**逐位退化为现行 `+=1.0` 规则**——现行机制成为新机制的特例，既有结论可解释为特例而非被推翻。乘法式在 $(\eta=1,\ r=1,\ w^{(0)}=1)$ 时首步同样得 2.0，两者首步一致。

**必须直接用实验证明两件事**：
$$N_{\text{STA-to-first-improvement}} \downarrow, \qquad \frac{\Delta WNS}{100\ \text{STA}} \uparrow$$
即 Failure-Aware 的价值定位是"**在相同验证预算下更快找到有效候选**"，而非"把最终 WNS 做得更高"。`rounds_history` 已含 `candidate_sta_before_round/after_round`，可直接支撑前者。

**为何 C′ 延后**：$r_{j,k}$（$k\in\{R,G,B,JOINT\}$）会立刻带来 ① 部分 (failure-type, candidate-type) 组合样本过稀（F2 实测仅 3 次、F3 16 次）② 参数解释复杂度上升，论文容易显得"调参很多"。路径应为 **global failure statistics → 做出明确收益 → 再做 candidate-type-conditioned feedback**。

### 第三层：S —— FAECO-v2 的真正核心升级

**严格定义**（不是"用 ABC 做 rewrite/refactor"）：

$$S(C):\ (I_C, O_C, V_C) \rightarrow (I_C, O_C, V_C'), \qquad I_C' = I_C,\ O_C' = O_C, \qquad F_{C'}(I_C) = F_C(I_C)$$

即**边界引脚接口保持、窗口功能等价**，仅内部布尔网络被重构。候选链：

$$\text{cut window} \rightarrow \text{AIG} \rightarrow \boxed{\text{balance / rewrite / refactor / resub}} \rightarrow \text{techmap} \rightarrow \text{local CEC} \rightarrow \text{STA}$$

> `yosys_abc.py` 的 `RESYN2_BUILTIN_SEQUENCE` 已覆盖 balance/rewrite/refactor，仅缺 `resub` 一条命令。

**R 与 S 必须在论文里说清楚**：

| | 定义 | 改变什么 | 天花板 |
|---|---|---|---|
| **R** | existing library equivalent implementation | 在已有标准单元的等价实现空间里换（同逻辑级数） | 受"库中无等价单元"限制（b06 根因） |
| **S** | Boolean network restructuring | 改变局部布尔网络**拓扑与逻辑级数** | 突破上述天花板；唯一能直接产出 $\Delta \text{Depth}<0$ 的候选类型 |

**ΔDepth 与 S 并为一组做**（不拆到相隔很远的两个阶段）。S 最漂亮的证据不是只有 $\Delta WNS=+x$，而是同时出现
$$L_{\text{critical}}: 7 \rightarrow 5, \qquad \Delta L = -2, \qquad \Delta WNS = +0.43\ \text{ns}$$
从而形成"深层逻辑 → 结构重综合 → 逻辑级减少 → 时序改善"的**因果链**。`logic_level_before/after/reduction` 字段坑位已在 schema 中，属"补采集"而非新建能力。

---

## 3. 实施顺序

$$\boxed{\text{事实修正} \rightarrow \text{Mixed-Fixed 消融} \rightarrow \text{失败率反馈} \rightarrow \Delta\text{Depth} \rightarrow S \rightarrow \text{电气风险前置}}$$

其中 **事实修正** 与 **Mixed-Fixed 消融** 是"当前论文必须做"；**失败率反馈**让 Failure-Aware 真正站住；**$\Delta$Depth + S** 把工作从"搜索策略改进"提升为"面向深层逻辑的 ECO 方法"。

| 阶段 | 动作 | 前置 | 成本 | 风险 |
|---|---|---|---|---|
| **0a（新增，最先）** | **代码基对账（OI-011）**：把 stateful 循环（`SearchState`/`accept_candidate`/`rollback`/`replay` + 接受后重抽锥）移植回 main 的 `code/` 布局；或反向迁移布局并声明 codex 分支为权威 | 无（但阻塞其余全部） | 3–5 天（含 264 测试回归 + sentinel 复跑校验） | 中：需证明移植后能复现既有数字（取 3 个电路做端到端对照） |
| **0b** | **事实修正 L1-a**（OI-009 / OI-010 / OI-012 + RESULTS.md §2 同步） | 0a 结论（"实际行为"以哪份代码为准） | 小时级 | 低（纯事实对齐，不改数字） |
| **1-A** | **Mixed-Fixed 三臂消融 L1-b**（含 schema 扩展） | 0a | 改造 1–2 天 + 单臂约 1 天（8 电路 × 20 轮） | 低 |
| **1-B** | **失败率反馈 C**（全局 $\rho,\eta$；含退化为现行规则的自洽性） | 1-A 作对照基线 | 改 `refinement.py` 单函数 1 天 + 重跑验证 | 中：必须保留固定权重版作对照；须显式证明"更少 STA 达同等/更优 WNS" |
| **1-C** | 增量 ECO 形式化 + stale invalidation **写清楚** | 0a（机制已在 codex 分支） | 论文 1 天 | 低（不是新机制） |
| **2-A** | **ΔDepth 采集与报告 + S 局部重综合**（一组） | 1-A/1-B 定稿候选空间 | **3–5 周**（窗口抽取/回填 + 库约束重映射 + 局部 CEC 接入 + ΔDepth 汇总；工具链约 70% 已有） | 中—高：组合替换的等价性证明链更复杂；需保证 S 不破坏 $I_C/O_C$ 边界 |
| **3-A** | **电气风险前置 E**（先采集 → 再统计相关性 → 才决定是否入 ranking） | 需重跑主实验以采集电气量 | 采集 3–5 天 + 相关性 1–2 天 +（若相关）入式 3 天 | 中：权重需标定 |
| **3-B** | F6 拆 load/wire（$F_{6L}$ / $F_{6W}$） | 3-A 的采集 + 可判定失败主因（$\Delta d=\Delta d_{\text{cell}}+\Delta d_{\text{load}}+\Delta d_{\text{wire}}$ 或稳定 proxy） | 3-A 之后 3 天 | 低 |
| **4（可选）** | C′ 候选类型细分失败率、$T(c)$ 自适应预算、J 词典序接受、K 学习型选择器 | 视目标期刊与审稿意见 | 各项 3 天 ～ 2–3 周 | 见 §5 |

### 明确**不做**的三件事

1. **不现在把电气项塞进式(2)**：当前覆盖率 0，塞进去等于"公式越来越漂亮但输入没经过实验标定"。
2. **不现在拆 F6**：没有能判定"为什么失败"的能力时，$F_6$ 与 $F_{6L}/F_{6W}$ 的差别只是猜测。
3. **不把 $T(c)$ 包装成主要创新**：$T(c)=\mathrm{clip}(T_0+a|V_c|+b|E_c|,\,30,\,180)$ 定位为 **verification-cost-aware mechanism / implementation policy**，用于消除 b17"人工放宽预算"质疑，不与 Failure-Aware / S 同级。

---

## 4. 关键设计裁定

### 4.1 增量 ECO：需要的是"写清楚"，不是"补机制"

收敛意见提出的流程已被 codex 分支的 `SearchState` 结构满足：

$$\text{Accept one patch} \rightarrow \text{commit} \rightarrow \text{STA update} \rightarrow \text{re-extract critical endpoint} \rightarrow \text{regenerate candidates}$$

- `accept_patch()` 原子追加 + 快照前态 + 推进 $G_r$ + 更新 `critical_endpoints/critical_instances/current_cone_gates`；
- 接受后 `flow.py` 侧 `refreshed_cone = extract_fanin_cone(...)` 重抽锥；
- 由此**旧候选天然作废**（stale candidate invalidation）——不需要额外的显式失效机制；
- `rollback()` 已具备；$N_{\text{best}}$ 回滚保护可在其上加一层"末次 patch 若使 WNS 劣化则回退"的策略。

**待写清的**：接受轮之后基准变化（OI-009）；同轮内多候选共享同一基准、互不叠加；回滚触发条件；补丁日志哈希链的连续性校验（`replay()` 已实现）。

### 4.2 JOINT 与 S 的候选空间规则（现在就要定）

**不建议** $JOINT = R+G+B+S$（组合空间迅速膨胀），**也不建议**枚举 $S\times R\times G\times B$。第一版保持：

$$JOINT = R/G/B\ \text{的既有组合}, \qquad S\ \text{独立}, \qquad \text{至多再加一档 } S \rightarrow G$$

$S \rightarrow G$ 是自然的两阶段逻辑：$\underbrace{S}_{\text{降低逻辑深度}} \rightarrow \underbrace{G}_{\text{优化驱动}}$，比直接枚举干净得多。

---

## 5. 可行性评估（关键依赖与冲突）

| 项 | 改动面 | 依赖 | 成本 | 风险 |
|---|---|---|---|---|
| 0a 代码基对账 | main `code/` 与 codex `src/` 两个布局 | 无 | 3–5 天 | 中（需 sentinel 复跑证明等价） |
| B Mixed-Fixed 三臂 | 运行器 flag + 结果 schema | 0a | 1–2 天改造 + 约 1 天/臂 | 低 |
| C 失败率反馈 | `refinement.py` 单函数 + 2 参数 | 无 | 1 天 + 重跑 | 中（须保留固定权重对照） |
| ΔDepth + S | 新候选生成器（窗口抽取→AIG→resyn→techmap→回填）+ 局部 CEC | ABC 与 SKY130 CEC 已有 | 3–5 周 | 中—高 |
| E 电气风险前置 | OpenSTA 报告解析 + 式(2) | **必须先采集**（当前覆盖 0） | 3–5 天 + 1–2 天相关性 + 3 天入式 | 中 |
| G F6 拆分 | 需先有 E 的采集 | E | 3 天 | 低 |
| $T(c)$ 自适应预算 | `flow.py` 预算逻辑（现固定 60 s） | 可复用 `max_cone_gates` 减半机制 | 2–3 天 + 重跑 | 低—中：需说明 $T(c)$ 只依赖候选规模、不依赖 benchmark 身份 |
| J 词典序接受 $\text{SEC}\succ\text{WNS}\succ\text{TNS}\succ\text{Area}$ | `accept` 谓词 | 无 | 3–5 天 | **高**：SEC 是网表级验证（ISCAS89 0.3–0.5 s、b17 17 s），**不能放在每候选接受路径上**；可行形态是"候选级局部 CEC + 网表级全局 SEC"两层，词典序只能在网表级生效 |
| K bandit / 学习型选择器 | 复用 `adaptive_selector.py`（UCB1 已在库） | 无 | 2–3 周 | 中：历史验证属 2026-08 旧工具链口径，需在当前口径重验 |

**算力参照**：ITC-99 主实验 3363 次候选级 STA、2 路并行、墙钟约 2.4 h；单电路最贵 b06 664 次、b01 597 次。SEC 便宜（ISCAS89 0.3–0.5 s / b17 17 s）→ **成本瓶颈是 STA 次数，不是 SEC**。

---

## 6. 方法主图与论文核心贡献（压成 3 条）

方法主图只留这 8 个框：

$$\boxed{\text{Critical Endpoint}} \rightarrow \boxed{\text{Weighted / Critical-Path Cut}} \rightarrow \boxed{R/G/B/S} \rightarrow \boxed{\text{Failure-Aware Candidate Ranking}} \rightarrow \boxed{\text{Local CEC + STA}} \rightarrow \boxed{\text{Physical Gate}} \rightarrow \boxed{\text{Accept / Rollback}} \rightarrow \boxed{\text{Incremental Re-analysis}} \circlearrowleft$$

核心贡献 3 条（其余全部降为实现细节）：

1. **Failure-aware adaptive candidate search** —— 失效反馈真正改变后续候选优先级，并由 Mixed-Fixed 消融**单独证明**。
2. **Cut-guided local structural resynthesis** —— S 候选突破标准单元等价替换上限，并用 $\Delta \text{Depth}$ 直接证明深层逻辑压缩。
3. **Incremental functional–timing–physical validation loop** —— 候选局部验证、STA、物理复核与逐轮网表更新形成闭环。

**降级为实现细节**：自适应 timeout、F6 分类、TNS 分支、rollback。

---

## 7. 与评审意见的差异（需反馈的 6 点）

1. **第④条误诊**：不是"FAECO 缺少迭代 ECO"，而是"FAECO 已是迭代 ECO，论文写成了单候选选择（且 main 分支代码也不含该行为）"。修正 = 移植 + 写对，不是重构算法。
2. **第③条"B/R 覆盖低"不成立**：B 覆盖 14/19 电路。准确批评是"**收益幅度**由 G 主导"。
3. **第⑦条部分不成立**：`accept` 已含 TNS 分支且 20 轮收敛配置已启用 → 应改为"跨测试集主实验启用并报告 `tns_aware` 结果"。
4. **第⑧条被高估为"新增指标"**：`logic_level_*` 字段坑位已在 schema 中，属"补采集"。
5. **第⑤条硬前置被忽略**：电气量覆盖率为 0，必须先采集 → 再统计相关性 → 才决定是否入 ranking。
6. **第⑦/⑨条与 SEC 位置的冲突未被识别**：词典序把 SEC 放首位工程上不可行，须拆为"候选级局部 CEC + 网表级全局 SEC"。

---

## 8. 阻塞项与下一步

**阻塞（必须先解决，否则阶段 1 全部实验无效）**：**OI-011 —— 仓库内代码 ≠ 产出论文结果的代码**。
可选路径：

- **(A) 移植（推荐）**：将 `codex/faeco-unified-loop` 的 stateful 循环移植进 main 的 `code/` 布局，用 3 个电路的 sentinel 复跑校验能复现既有数字；
- **(B) 反向迁移**：把 codex 分支布局迁移为新 main 并声明其为权威实现。

两条路径都必须同时修好 **新-8 的 schema 记录缺口**（`enable_feedback`/`strategies`/`init_weights`/`toolchain`），否则重做的三臂消融会重复"结论无可追溯证据"。

**建议的立即动作（按序）**：0a 代码基对账 → 0b 事实修正（OI-009/010/012）→ 1-A Mixed-Fixed 三臂 → 1-B 失败率反馈 → 2-A ΔDepth + S。
