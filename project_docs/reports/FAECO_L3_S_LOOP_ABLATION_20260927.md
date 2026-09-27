# FAECO L3 S 环路接入与 {S 开, S 关} 消融实验报告

日期：2026-09-27
代码提交：本次改动（`flow.py` / `real_wns.py` / `run_outerloop_real_wns.py` +
3 个脚本 + 9 项单测）
契约：`project_docs/planning/FAECO_V2_IMPL_CONTRACT_20260923.md` §8.13
前置：§8.12（S 机制在真实工具链上的单窗验收）、`reports/FAECO_L3_S_VALIDATION_20260925.md`

---

## 1. 这一轮要回答的问题

§8.12 已证明 S（窗口局部结构重综合）**机制成立**（s641 窗 `DFF_13`：ΔL=+1、ΔWNS=+0.03 ns），
但收益稀疏，且被明确标注为**代理实验**（仅端点锥、单次 graft、无多轮再分析、无 R/G/B 组合、
未用割的时序加权选窗）→ 结果是**下界**，不能据此定 S 的论文定位。

本轮把 S 按 r2 §4.9 接进**实时多轮循环**，在同一口径下跑 `{S 关, S 开}` 两臂，
回答：

> 在既有的候选构造→加权排序→STA 验证纪律之上，**新增"结构重综合"这一候选类型，
> 是否带来独立的最终时序收益？**

## 2. 接入语义（结论先行：单变量对照成立）

S 是**独立候选类型**，与 R/G/B 共用同一批割边界、同一预算、同一接受契约：

* 一轮内的推进顺序是 `R/G/B → S`。**S 只在同轮 R/G/B 全部未改进时才被报价**，
  因此 S 永远不会顶掉一个 R/G/B 的接受。
* **至多一档**：S 不会在自身接受后再触发 S。r2 §4.9 的 `S→G` 一档**有意不做**（v1 范围声明，
  见契约 §8.13.4）：它会同时改动两件事，破坏单变量对照。
* **受 `candidates_per_iteration` 约束**：每轮尝试的窗口数上限 `resynth_per_iteration`，
  每轮实测的 S 候选数上限 `max_candidates_per_iteration`。
* **S 拒绝只记 `severity="info"` 审计事件，绝不进入驱动权重/EMA 的 `failures` 集合。**
  该性质有单测把守：S 开/关两臂的 `weights_trace`、`failure_ema_trace`、
  `history[*].failures` **逐位相同**。

## 3. 关口（gate）——先证明"关掉就是原样"

**在解释任何 S 结果之前必须证明 off 臂没有被动过。** `verify_s_off_reproduces_l2.py`
逐电路比对 off 臂与归档 L2 fixed 臂：

| 比对项 | 结果 |
|---|---|
| success / iterations / stop_reason / final_patch_id | 8/8 全等 |
| baseline_wns / wns / wns_history | 8/8 全等 |
| 接受补丁链（patch_id 序列）| 8/8 全等 |
| `sta_used`（工具调用数）| 8/8 全等 |

**结论：8/8 电路逐位复现归档 L2 fixed 臂**（GATE PASSED）→ S-off 路径完全惰性，
`{S 开, S 关}` 是**单变量**对照，且 off 臂与论文前序实验同源可比。

## 4. 实验口径

| 项 | 值 |
|---|---|
| 电路 | ISCAS89 × 8：s27 s382 s420 s641 s713 s820 s832 s953 |
| 臂 | `off = --no-feedback`；`on = --no-feedback --structure-resynth` |
| 共同口径 | `--period 0.5 --max-iterations 20 --candidates-per-iteration 8 --joint-k 2 --enable-buffer --workers 1 --early-stop` |
| STA 预算 | **700**（两臂相同）|
| S 分配 | `--resynth-per-iteration 1`，变体 `S0,S1,S2` |
| 工具链 | OSS-CAD Suite `Yosys 0.67+146`（驱动脚本显式注入并断言版本）+ WSL OpenSTA 3.1.0 |

**为什么预算取 700 而不是 L2/论文主口径的 500**：L2 fixed 臂 off 侧最大 `sta_used = 476`
（s420），在 500 下已接近绑定；S on 侧每轮最多追加 3 次测量、20 轮上限 +60 → 536。
取 700 保证**两臂都不撞墙**。否则 on 臂的早停会把"预算被 R/G/B 抢光"**伪装成**"S 无贡献"。
**证据**：本实验两臂 `sta_used` 见下表，最大差 +8，且 16/16 run 的 `stop_reason` 均为
`max_iterations`（不是预算）→ 预算不绑定，成立。

## 5. 结果

### 5.1 配对表（off vs on，逐电路）

| 电路 | off dWNS | on dWNS | 差 | off maxB(k) | on maxB(k) | off k₁st | on k₁st | off 接受数 | on 接受数 | on 端 STA / off 端 STA |
|---|---|---|---|---|---|---|---|---|---|---|
| s27 | 0.100 | 0.100 | **0.000** | 0.100 | 0.100 | 30 | 30 | 1 | 1 | 129 / 127 |
| s382 | 0.220 | 0.220 | **0.000** | 0.220 | 0.220 | 3 | 3 | 7 | 7 | 374 / 366 |
| s420 | 0.970 | 0.970 | **0.000** | 0.970 | 0.970 | 2 | 2 | 19 | 19 | 477 / 476 |
| s641 | 0.640 | 0.640 | **0.000** | 0.640 | 0.640 | 1 | 1 | 11 | 11 | 319 / 319 |
| s713 | 0.130 | 0.130 | **0.000** | 0.130 | 0.130 | 5 | 5 | 2 | 2 | 134 / 127 |
| s820 | 0.020 | 0.020 | **0.000** | 0.020 | 0.020 | 1 | 1 | 2 | 2 | 191 / 185 |
| s832 | 0.090 | 0.090 | **0.000** | 0.090 | 0.090 | 1 | 1 | 5 | 5 | 162 / 157 |
| s953 | 0.110 | 0.110 | **0.000** | 0.110 | 0.110 | 1 | 1 | 5 | 5 | 198 / 190 |

**8/8 电路的 `dWNS`、`maxB(k)`、`k₁st`、接受数逐位相同**（`diff` 全为 `0.000`）。

### 5.2 S 是否真的执行了（台账）

这是本报告最关键的一张表：**必须先把"没执行"与"执行了没接受"分开**。

| 电路 | 是否启用 | 轮首 S 轮数 | 报价窗口 | **成功抽窗** | 产出候选 | **STA 实测** | 接受 | 拒绝标签 |
|---|---|---|---|---|---|---|---|---|
| s27 | True | 2 | 109 | 37 | 2 | 2 | 0 | — |
| s382 | True | 8 | 76 | 76 | 8 | 8 | 0 | — |
| s420 | True | 1 | 2 | 1 | 1 | 1 | 0 | — |
| s641 | True | **0** | 72 | **0** | 0 | 0 | 0 | — |
| s713 | True | 7 | 123 | 105 | 7 | 7 | 0 | — |
| s820 | True | 6 | 123 | 93 | 6 | 6 | 0 | — |
| s832 | True | 5 | 102 | 65 | 5 | 5 | 0 | — |
| s953 | True | 8 | 92 | 92 | 8 | 8 | 0 | — |

* **S 在 7/8 电路真正执行**（累计成功抽窗 469 个、产出并实测候选 **37** 个）。
* **接受数 0/8**。
* s641 是唯一的例外：**报价 72 个窗口、成功抽窗 0**。这是"**S 被报价但本电路没有可抽窗**"
  （割边界含时序/受禁单元，或边界门在当前已提交网表中不存在 → r2 §4.2 不变量拒绝），
  属"程序/几何"原因，**不是**"S 没有贡献"的证据。判读时必须与其余 7 个电路分开。
* 拒绝标签为空：被拒绝的尝试都是 **DEDUP 丢弃**（同一 `G_r` 上同一窗口的确定性重跑），
  按 r2 §4.7 **不计失败**，因此没有 CEC/ratio/graft/structure 级拒绝。

### 5.3 S 候选为什么全部不被接受（机制解释）

对 37 个被实测的 S 候选，逐条取 r2 §4.8 的**双层深度**与相对"当时已提交基线"的 WNS 差：

| 统计量 | 结果 |
|---|---|
| ΔL(**BLIF/AIG 层**) > 0 | **37/37** |
| ΔL(**SKY130 层**，权威层) > 0 | **16/37** |
| ΔWNS > 0 | **0/37** |
| **ΔL(SKY130) > 0 且 ΔWNS > 0** | **0/37** |
| R_S 判定 | ok 33 / soft 4 |
| 变体分布 | **全部 S0**（S1/S2 与 S0 逐位相同 → 按 §4.7 DROP）|

两个必须并列的事实：

1. **S 确实在降结构**：37/37 候选都把窗口的 BLIF/AIG 深度降了 2–8 级（R_S 全在双阈值内，
   33 个 ok、4 个 soft），且 CEC-1/CEC-2 全闭合、全网表结构自检通过。
2. **但测不到时序好处**：**连那 16 个把权威层（SKY130）深度也降下来的候选，ΔWNS 也全是 ≤ 0**
   （最好的两个是 ΔWNS = 0.000，即时序中性）。同时有 4 个 s953 候选 SKY130 深度反而 +1、
   ΔWNS 为负。

→ 这**不是**"降到错的那一层"能解释的（那只解释了 21/37），而是更强的结论：
**这些被割选中的窗口不在真正的时序关键锥上**，窗口内结构性变浅（甚至权威层变浅）
传不到端点 WNS。这与 §8.12 的代理实验判读一致（"结构深度下降多在非时序关键锥"；
s713 有"结构变浅但更慢"）。

## 6. 判读

**负向结论（能力型，非程序型）**：S 在 7/8 电路真的执行了、拿到了与 R/G/B 同一总预算、
产出的候选形式验证全闭合，但**没有任何一个改善 WNS**；两臂的最终 `dWNS`、B(k) 曲线、
k₁st、接受链**逐位相同**。

在**当前**这个 regime 下（k=8 混合候选、`resyn2` 族、小窗单次 graft），
**S 是可选类型，不是独立贡献**。这与 L2 对 EMA 反馈的封板结论同形：
> 增量主要来自**候选构造与权重排序**，以及**验证纪律**，而不是新增的搜索维度。

**必须同时声明的边界**（否则结论会被过度外推）：

1. **S 的分配是 1 窗/轮 → 37 次测量**，而 R/G/B 同期约 450 次。§7 的加宽分配对照（4 窗/轮）
   已排除"S 被饿着"：候选数仅 37→39、配对差仍全 `0.000`，并定位到真正的瓶颈是
   **可用窗口集合**（受不同 `G_r` 个数限流）而非配额。
2. **S→G 一档未实现**（有意，见契约 §8.13.4）→ 本报告的"无独立贡献"是针对
   **纯 S 候选类型**，不含"S 之后再做一次 G"。
3. **割选窗仍未做时序加权**：本实验用的是与 R/G/B 相同的割候选（含 critical-path cover 默认候选），
   不是"用 `weighted_cut_candidates` 的时序权重专门挑最深的窗"。§5.3 的机制解释恰恰指向
   这一点是**下一步真正的杠杆**。
4. 上游基线本身在该 regime 已把可用增益吃得很满（8 电路 20 轮，`sta_used` 127–477）。

## 7. 稳健性：加宽 S 的分配（`--resynth-per-iteration 4`）

> 目的：排除"S 被饿着"这一最强反驳（k1 下 S 只拿到 37 次测量、而 R/G/B 同期约 450 次）。

复跑命令：
```bash
FAECO_OUT_ROOT=<root>/experiments/20260924_l3s_ablation_k4 \
FAECO_RESYNTH_PER_ITER=4 \
  bash code/scripts/run_s_ablation_batch.sh on      # 8/8 exit=0
python code/scripts/compare_s_ablation.py \
  --off-root experiments/20260924_l3s_ablation/off \
  --on-root  experiments/20260924_l3s_ablation_k4/on
```

### 7.1 结果：结论不变，**且配额根本不是瓶颈**

| 电路 | off dWNS | k4 on dWNS | 差 | k4 接受数 | k4 抽窗 | k4 候选 | k4 实测 | k4 端 STA |
|---|---|---|---|---|---|---|---|---|
| s27 | 0.100 | 0.100 | **0.000** | 0 | 38 | 2 | 2 | 129 |
| s382 | 0.220 | 0.220 | **0.000** | 0 | 100 | 8 | 8 | 374 |
| s420 | 0.970 | 0.970 | **0.000** | 0 | 4 | 3 | 3 | 479 |
| s641 | 0.640 | 0.640 | **0.000** | 0 | 0 | 0 | 0 | 319 |
| s713 | 0.130 | 0.130 | **0.000** | 0 | 123 | 7 | 7 | 134 |
| s820 | 0.020 | 0.020 | **0.000** | 0 | 106 | 6 | 6 | 191 |
| s832 | 0.090 | 0.090 | **0.000** | 0 | 74 | 5 | 5 | 162 |
| s953 | 0.110 | 0.110 | **0.000** | 0 | 116 | 8 | 8 | 198 |

**k4 的配对差同样全为 `0.000`，接受数同样 0/8**；候选总数 37 → **39**（仅 +2）。
39 个候选的交叉表：**ΔL(BLIF)>0 39/39、ΔL(SKY130)>0 17/39、ΔWNS>0 0/39**，
且 **ΔL(SKY130)>0 且 ΔWNS>0 = 0/39**。

### 7.2 这张表真正说明的事：瓶颈是"可用窗口数"，不是"每轮配额"

把配额从 **1 窗/轮提到 4 窗/轮**，候选数几乎不动（37→39），说明分配不是绑定约束。
原因在 §8.13.3 的去重语义：

* S 的窗口身份是 `(current_netlist_hash, boundary_key)` —— **同一 `G_r` 上同一窗口是确定性重跑**，
  已测即跳过（这是"不重复付费"的正确性要求，不是保守）。
* 因此 **S 在整个运行中可触及的窗口集合上界 ≈ (不同 `G_r` 的个数) × (每 `G_r` 可用的割边界数)**。
  实测 `windows_offered` 远大于"轮数 × 8"里的**实际尝试数**：多数轮次里 8 条割边界
  在**同一个 `G_r`** 上早已被测过 → 被去重跳过，扫描走完即结束该轮。
* 而 `G_r` 只在**接受**时改变；S 又只在 R/G/B **失败**的轮次才被报价 →
  **S 的可用窗口集合被"接受次数"结构性限流**，与配额无关。

→ 加宽配额无法给 S 更多机会；要给 S 更多机会，只能改变**窗口来源**
（即：用时序加权挑更深的窗、或允许跨 `G_r` 重测），而不是加大配额。
这恰好再次指向 §6 边界 ③。

（k4 顺带产出一条独立观察：`s420` 在 k4 下出现 1 次 `W_STRUCT_ERROR` 窗口级拒绝——
graft 后全网表结构自检拦下一个候选。该候选被正确拒绝且不计失败，机制按设计工作。）

## 8. 对论文的含义（尚未动 `.tex`）

按"先方案、后论文"的既定纪律，本轮**未触碰任何 `.tex`**。基于本报告的可用表述方向：

* **§4.8 的论证得到实测加强**：论文已论证"SKY130 HD 中大量单元是单级，G/R 原理上不可能
  产生 ΔL<0，只有 S/JOINT 能"。本轮进一步给出**反向证据**：即使 S 产生了 ΔL>0
  （37/37）、甚至权威层 ΔL>0（16/37），也未必换成 ΔWNS>0（0/37）→
  **"结构深度下降"不是"时序改善"的可替代指标**，这本身是一个干净的、可引用的实测结论。
* **方法主线的定位被再次确认**：FAECO 的价值主张应落在
  **失败归因驱动的候选构造 + 加权排序 + 严格验证纪律**，S 作为**可选扩展类型**陈述，
  必须附上"S 的收益依赖时序加权选窗"这一条件，而不是作为并列的"第三个搜索维度"。
* **诚实性要求**：若论文要报 S，必须同时报"我们把 S 的分配从 1 窗/轮加到 4 窗/轮
  （候选 37→39）仍未 improve"的稳健性结果与 §5.3 的机制表，否则属选择性报告。

## 9. 复现

```bash
# 两臂（off/on）
bash code/scripts/run_s_ablation_batch.sh            # 默认 off,on × 8 电路

# 关口：off 臂必须逐位复现归档 L2 fixed 臂
python code/scripts/verify_s_off_reproduces_l2.py \
  --off-root experiments/20260924_l3s_ablation/off \
  --ref-root experiments/20260924_threearm/fixed      # 期望 GATE PASSED 8/8

# 聚合判定（配对差 + 台账 + "没执行/执行了没用"区分）
python code/scripts/compare_s_ablation.py --root experiments/20260924_l3s_ablation \
  --json-out experiments/20260924_l3s_ablation/aggregation/s_ablation_summary.json

# 候选机制解释（双层深度 × ΔWNS 交叉表）
python code/scripts/analyze_s_candidates.py \
  --root experiments/20260924_l3s_ablation/on \
  --json-out experiments/20260924_l3s_ablation/aggregation/s_candidates_k1.json

# 稳健性：加宽 S 分配（4 窗/轮）
FAECO_OUT_ROOT=<root>/experiments/20260924_l3s_ablation_k4 \
FAECO_RESYNTH_PER_ITER=4 bash code/scripts/run_s_ablation_batch.sh on
python code/scripts/compare_s_ablation.py \
  --off-root experiments/20260924_l3s_ablation/off \
  --on-root  experiments/20260924_l3s_ablation_k4/on
python code/scripts/analyze_s_candidates.py \
  --root experiments/20260924_l3s_ablation_k4/on
```

单测：`code/tests/test_flow_structure_resynth.py`（9 项）；
全套回归 `486 passed / 4 skipped`。

## 10. 产物位置

> `experiments/2026*/` 被 `.gitignore:60` 忽略 → 下述产物**只存在于本地工作区**，
> 进版本库的是**本报告中的汇总数字**（与 L2 三臂报告同例）。复现脚本与口径已全部入库。

```
experiments/20260924_l3s_ablation/
  off/<circuit>/outerloop_result.json        对照臂（逐位复现 L2 fixed）
  on/<circuit>/outerloop_result.json         处理臂（含 structure_resynth 台账）
  on/<circuit>/eval_trials.json              含 kind=="S" 的 37 条实测记录（resynth 元数据）
  on/<circuit>/eval/iterNNN_sMMM/{mapped.v,sta.log}   S 候选的 STA 产物（与 R/G/B 的
                                             iterNNN_candNNN 命名可区分）
  on/<circuit>/case/results/structure_resynth/roundNNN/<root>_<n>g/S{0,1,2}/  窗口级产物
  aggregation/s_ablation_summary.json, s_candidates_k1.json
  logs/{arm}_{circuit}.log
experiments/20260924_l3s_ablation_k4/on/    加宽分配（4 窗/轮）的稳健性对照臂
```

> 说明：S 窗口产物落在 `case/results/` 下，这是 `run_multi_iteration_case` 的
> `artifact_dir` 默认值（`case_dir/"results"`）。位置可用但不够干净——**遗留清理项**：
> 让 runner 把 `structure_out_dir` 默认指向 `<output-dir>/structure_resynth`，
> 避免写入输入夹具目录。
