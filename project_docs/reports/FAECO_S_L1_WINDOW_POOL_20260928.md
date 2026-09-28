# FAECO S 窗口来源杠杆（L1）验证报告

日期：2026-09-28
设计出处：`project_docs/planning/FAECO_V2_TECH_DESIGN_20260923.md` §13（诊断/重设计/三层裁决）
诊断依据：`project_docs/reports/FAECO_S_WINDOW_CENSUS_20260928.md`（池子普查）
未决问题：OI-014（S 的论文定位）
前置报告：`FAECO_L3_S_LOOP_ABLATION_20260927.md`（历史 {S 开, 关} 消融）
**Code revision（冻结）**：tag **`faeco-exp-rev1`** → `87d01ba`
产物：`experiments/20260928_s_l1_ablation/`（8 电路 × {`off`, `on`}`，16/16 `ALL_RUNS_DONE`）
裁决工具：`code/scripts/summarize_s_l1.py`（三层）、`compare_s_ablation.py`、`analyze_s_candidates.py`

---

## 0. 一句话

> **NEGATIVE（能力型），但这是有价值的负结果**：L1 把 S 的窗口池上限从 **8 → 33** 真实解除，
> S 候选 **37 → 126（3.4×）**、且**全部来自不同窗口**、权威层深度下降比例升到 **60%**；
> 然而 **`ΔWNS>0` = 0/126、接受 = 0/8、配对最终 WNS 全 0.000**。
> ⇒ **"S 没效果只是枚举太窄"这一解释已被排除**；OI-014 按预锁定规则判 **(B) 降级为可选候选类型**。
> 下一步**不再扩池**，转 §13.7 **S 候选质量归因**。

## 1. 要回答的问题

历史环路消融给出"S 接受 0/8"，但**该证据被集成缺陷混淆**：S 的窗口来源复用 R/G/B 的候选列表，
其长度被 `candidates_per_iteration`(=8) 截断（`flow.py` L626/L607）⇒ 现有结论**只能**说明
"在 R/G/B 的 top-8 割边界里 S 无可接受候选"，**不可外推**为"S 无贡献"。

普查证明 `len(candidates) = min(k + 1, 该锥体的可计分割空间)`（`k=8 → 9`、`k=32 → 33`；
**s27 小锥体饱和于 6**），⇒ 瓶颈在 **L607 枚举的 `k`**，修法 = 给 S 一次
**`k = resynth_window_pool` 的专属枚举**（**不是**加宽切片）。

**L1 要回答**：扩池后 S 是否产出新的可接受候选并改善端点 WNS？**必须分三层回答**，不得跳级。

## 2. 单变量纪律与口径

| 项 | `off`（对照） | `on`（处理） |
|---|---|---|
| 开关 | `--no-feedback` | `--no-feedback --structure-resynth --resynth-per-iteration 8 --resynth-window-pool 32` |

两臂共同口径（逐字相同）：`--period 0.5 --max-iterations 20 --candidates-per-iteration 8
--joint-k 2 --enable-buffer --workers 1 --early-stop --sta-budget 1600 --iscas89-dir …`

- `resynth_per_iteration` 同时提到 8 是必要的：池子扩到 32 后它重新成为每轮上限；
  两者**共同**构成"L1 窗口来源"，`off` 臂仍是唯一自由度。
- 预算取 1600（历史 700）以免"预算被 R/G/B 抢光"伪装成"S 无贡献"；实测**两侧都不绑定**（§3.3）。

## 3. 纪律检查

### 3.1 控制臂逐位复现 —— ✅ 8/8

`new/off` 与归档 `20260924_l3s_ablation/off` **逐位一致**（`mapped.v` 指纹、`final_patch_id`、
`wns`、`stop_reason`、**预算台账指纹**全等），8/8 电路。

⇒ 预算 700→1600 **未改变对照臂**（s382 的真实计数器 `state.budget.sta_used` = 366，
**不是** `n_candidate_sta_runs`=769，后者是另一口径）。

### 3.2 ★ 单变量是否干净 —— ✅ 8/8（本报告最关键的纪律项）

**两臂的非 S（R/G/B/JOINT）试验序列逐位相同**（`kind/patch_id/wns/accepted`）：

| 电路 | s27 | s382 | s420 | s641 | s713 | s820 | s832 | s953 |
|---|---|---|---|---|---|---|---|---|
| 非 S 试验数 | 416 | 769 | 1048 | 596 | 306 | 312 | 306 | 393 |
| 两侧逐位相同 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

⇒ L1 的扩池**完全没有扰动搜索路径**；两臂唯一差别是 S 的额外候选评估。对照是干净单变量。

### 3.3 预算不绑定 —— ✅

`Δsta_used` **恰好等于 `N_S candidate`**（每个 S 候选恰 1 次候选 STA）：

| 电路 | sta_off | sta_on | Δ | 停因（两臂） |
|---|---|---|---|---|
| s27 | 127 | 129 | +2 | max_iterations |
| s382 | 366 | 398 | +32 | max_iterations |
| s420 | 476 | 482 | +6 | max_iterations |
| s641 | 319 | 319 | 0 | max_iterations |
| s713 | 127 | 149 | +22 | max_iterations |
| s820 | 185 | 199 | +14 | max_iterations |
| s832 | 157 | 174 | +17 | max_iterations |
| s953 | 190 | 223 | +33 | max_iterations |

最大 482，**远低于 1600，甚至低于历史 700** ⇒ 预算对结论无任何约束。

### 3.4 惰性单测 —— ✅

`resynth_window_pool` 默认 `None`（及显式 = `candidates_per_iteration`）与未改动版本**逐位相同**；
默认路径只跑一次 `k=8` 枚举、L1 路径出现 `k=32`（spy 断言）。
`test_flow_structure_resynth.py` **11 passed**。

## 4. 结果（三层）

### 4.0 固定指标集（**`windows_offered` 不作 L1 主证据**）

`windows_offered` / `windows_extracted` 含**重复扫描过的割边界**，仅作内部扫描开销指标。
`N_extracted`=1724 ≫ `N_unique_window`=126 即为佐证。固定指标：

| 电路 | `N_unique_window` | `N_extracted` | `N_S candidate` | `N_measured` | `N_accepted` |
|---|---|---|---|---|---|
| s27 | 2 | 38 | 2 | 2 | 0 |
| s382 | 32 | 368 | 32 | 32 | 0 |
| s420 | 6 | 8 | 6 | 6 | 0 |
| s641 | 0 | 0 | 0 | 0 | 0 |
| s713 | 22 | 376 | 22 | 22 | 0 |
| s820 | 14 | 246 | 14 | 14 | 0 |
| s832 | 17 | 245 | 17 | 17 | 0 |
| s953 | 33 | 443 | 33 | 33 | 0 |
| **合计** | **126** | **1724** | **126** | **126** | **0** |

- `N_unique_window` 按 `patch_id` 的 canonical 窗口哈希去重；**无任何重复窗口哈希**
  ⇒ 126 个候选来自 **126 个不同窗口**，扩池是**真探索**而非重跑旧窗口。
- 126 个候选**全部为变体 S0**（S1/S2 与 S0 同 canonical ⇒ 按 r2 §4.7 静默丢弃），
  与历史结论一致。

### 4.1 第一层 · enumeration —— ✅ 池子上限被真实解除（6/6 可测电路）

| 电路 | 历史 `p=1,pool=8` | **L1 `p=8,pool=32`** | Δ | `pool_max` | L1 专属枚举返回 | 参与轮数 | 状态 |
|---|---|---|---|---|---|---|---|
| s27 | 2 | 2 | +0 | 6 | 6 | 1 | **SATURATED**（池只有 6） |
| s382 | 8 | **32** | +24 | 9 | 33 | 4 | LIFTED |
| s420 | 1 | **6** | +5 | 9 | 33 | 1 | LIFTED |
| s641 | 0 | 0 | +0 | 9 | 33 | 0 | **NO-ENGAGE**（抽窗 0） |
| s713 | 7 | **22** | +15 | 9 | 33 | 3 | LIFTED |
| s820 | 6 | **14** | +8 | 9 | 33 | 2 | LIFTED |
| s832 | 5 | **17** | +12 | 9 | 33 | 3 | LIFTED |
| s953 | 8 | **33** | +25 | 9 | 33 | 5 | LIFTED |
| **合计** | **37** | **126** | **+89（3.4×）** | | | | |

**机制被完全解释（可引用）**：历史 s382/s953 的 S 候选数**恰好 = 8 = 池上限**；
L1 后 s382 = **32 = `resynth_per_iteration`(8) × 参与轮数(4)**，池 33 不再绑定。
⇒ **历史 S 候选数被池子钉死；L1 把上限替换为"每轮配额 × 参与轮数"。**
（饱和判据用**直接证据**：L1 专属枚举返回的边界数 ≤ `k=8` 枚举的 `pool_max`。）

> 这一层**只**证明"枚举瓶颈被解除"，**不构成 timing capability**。

### 4.2 第二层 · candidate quality —— 深度改善比例上升，但 `ΔWNS>0` = 0/126

`ΔWNS` 相对**并发基线**（逐 trial 推进接受链重建）测量：

| 电路 | n | R_S ok | `ΔL(sky130)>0` | `ΔWNS>0` | `ΔWNS=0` | `ΔWNS<0` | min | median | max |
|---|---|---|---|---|---|---|---|---|---|
| s27 | 2 | 2 | 0 | 0 | 0 | 2 | -0.100 | -0.100 | -0.100 |
| s382 | 32 | 29 | 27 | 0 | 4 | 28 | -0.230 | -0.180 | 0.000 |
| s420 | 6 | 6 | 1 | 0 | 1 | 5 | -0.370 | -0.090 | 0.000 |
| s713 | 22 | 20 | 15 | 0 | 3 | 19 | -0.340 | -0.030 | 0.000 |
| s820 | 14 | 10 | 7 | 0 | 13 | 1 | -0.020 | 0.000 | 0.000 |
| s832 | 17 | 14 | 5 | 0 | 11 | 6 | -0.090 | 0.000 | 0.000 |
| s953 | 33 | 28 | 21 | 0 | 4 | 29 | -0.540 | -0.100 | 0.000 |
| **合计** | **126** | **109**（soft 17） | **76（60.3%）** | **0** | **36** | **90** | | | |

两个要点：

1. **扩池不是"只堆量"**：`ΔL(SKY130)>0` 从历史的 **16/37（43%）升到 76/126（60.3%）**
   ⇒ 新增的次优窗口**更常真的降低权威层深度**（r2 §4.8 的权威层，不是 BLIF 层）。
2. **但深度改善换不来时序**：`ΔWNS>0` **0/126**，且 **90/126（71%）的 `ΔWNS<0`**
   —— 多数候选**反而让 WNS 变差**（s382 中位 -0.18 ns，s953 -0.10 ns）。
   ⇒ **问题已不在 L1**（枚举已 3.4×），而在 **S transformation quality**：
   结构变浅传不到端点。方向直指 §13.7 的 cell-delay / fanout-cap 抵消，
   或关键路径根本不穿过被重综合窗口。

### 4.3 第三层 · repair capability —— ❌ 0/8 接受，配对全 0.000

| 电路 | wns_off | wns_on | ΔWNS(on−off) | accepted |
|---|---|---|---|---|
| s27 | -0.17 | -0.17 | 0.000 | 0 |
| s382 | -0.76 | -0.76 | 0.000 | 0 |
| s420 | -0.59 | -0.59 | 0.000 | 0 |
| s641 | -0.99 | -0.99 | 0.000 | 0 |
| s713 | -1.20 | -1.20 | 0.000 | 0 |
| s820 | -1.17 | -1.17 | 0.000 | 0 |
| s832 | -1.14 | -1.14 | 0.000 | 0 |
| s953 | -1.20 | -1.20 | 0.000 | 0 |

⇒ 配对：**improved 0 / tied 8 / worse 0**。

## 5. 裁决（§13.4-3 预锁定判据，三层）

| 判据 | 结果 |
|---|---|
| §13.4-1 惰性单测 | ✅（3.4） |
| §3.2 单变量干净（非 S 轨迹逐位相同） | ✅ 8/8 |
| §3.1 控制臂逐位复现归档基线 | ✅ 8/8 |
| §3.3 预算不绑定 | ✅（max 482 / 1600） |
| §13.4-3 **第一层 enumeration** | ✅ 6/6 可测电路 LIFTED（37 → 126，3.4×） |
| §13.4-3 **第二层 candidate quality** | ⚠️ 深度改善 43%→60%，但 **`ΔWNS>0` = 0/126** |
| §13.4-3 **第三层 repair capability** | ❌ accepted 0/8；配对 dWNS 全 0.000 |

### 判定：**NEGATIVE（能力型）** ⇒ OI-014 选 **(B)**

按 §13.4-3 判定规则：未达第三层（`N_accepted,S = 0`，**即使候选 37 → 126**）⇒

> **枚举瓶颈已排除，但当前 S 构造在该 benchmark/regime 下没有体现 timing repair capability。**

⇒ **OI-014 裁 (B)：S 降级为可选候选类型 / 探索性能力**，与 L2 封板结论合并叙述，
主贡献回到「候选构造 + 加权排序 + 失败归因 + STA 验证」。

**明确不做什么**：**不再扩池**（32 → 64 → 128）。L1 已经把池子这条线走到头：
池已不是瓶颈（`pool_max`=9、L1 枚举 33、实际用满 33），继续加大只会重复本结论。

**下一步（§13.7 S 候选质量归因）**：回答"**为什么通过 CEC 的 S patch 没有 timing gain？**"——
(i) 窗口内 logic depth 是否实际下降（本轮：`ΔL(SKY130)>0` 76/126，已部分回答）；
(ii) 映射后 depth 是否又回来；(iii) cell delay 是否变差；(iv) fanout/cap 是否抵消结构收益；
(v) critical path 是否根本不穿过该窗口。

## 6. 边界与待查项

1. **只覆盖纯 S 候选类型**：r2 §4.9 的 `S→G` 一档**有意未实现**（避免同时改两件事破坏单变量，契约 §8.13.4）。
2. **`resynth_per_iteration=8` 现成为 S 的主要约束**（s382: 8×4=32；s953: 33）。
   但本报告已证明**配额不是瓶颈**——候选质量而非数量决定结论。
3. **s641 全程 `N_S candidate = 0`**（`rounds_with_s = []`，报价 297 窗但抽窗 0）：
   属**程序/几何**原因（r2 §4.2 不变量拒绝），与能力结论必须分开。
4. **⚠️ 待查（记账异常，不影响上述结论）**：s420 报告 6 候选与 6 条变体级拒绝
   `W_STRUCT_ERROR`（均标 S0），但磁盘上只有 **8 个窗口 × {S0,S1,S2}**；
   8 个 S0 槽位无法同时产出 6 候选 + 6 条 S0 拒绝 ⇒ `rejections` 台账在 s420 上**未闭合**。
   已登记 **OI-017**。**不影响**候选数/实测数/`ΔWNS`/接受数/三层判定。

## 7. 复现

```bash
export YOSYSHQ_ROOT=/c/oss-cad-suite-build/oss-cad-suite
export PATH="$YOSYSHQ_ROOT/bin:$YOSYSHQ_ROOT/lib:$PATH"
git checkout faeco-exp-rev1

FAECO_OUT_ROOT="$PWD/experiments/20260928_s_l1_ablation" \
FAECO_RESYNTH_PER_ITER=8 FAECO_RESYNTH_WINDOW_POOL=32 FAECO_STA_BUDGET=1600 \
bash code/scripts/run_s_ablation_batch.sh off,on s27,s382,s420,s641,s713,s820,s832,s953

# 三层裁决 + 固定指标集 + 单变量纪律
.venv/Scripts/python.exe code/scripts/summarize_s_l1.py \
  --root experiments/20260928_s_l1_ablation \
  --json-out experiments/20260928_s_l1_ablation/aggregation/summarize_s_l1.json
# 标准台账与配对差
.venv/Scripts/python.exe code/scripts/compare_s_ablation.py --root experiments/20260928_s_l1_ablation
# S 候选双层深度 × ΔWNS 交叉表
.venv/Scripts/python.exe code/scripts/analyze_s_candidates.py --root experiments/20260928_s_l1_ablation/on
```
