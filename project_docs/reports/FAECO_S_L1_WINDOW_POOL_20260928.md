# FAECO S 窗口来源杠杆（L1）验证报告

日期：2026-09-28
设计出处：`project_docs/planning/FAECO_V2_TECH_DESIGN_20260923.md` §13（诊断/重设计/三层裁决）
诊断依据：`project_docs/reports/FAECO_S_WINDOW_CENSUS_20260928.md`（池子普查）
未决问题：OI-014（S 的论文定位；**待本报告裁决，不得跳级**）
前置报告：`FAECO_L3_S_LOOP_ABLATION_20260927.md`（历史 {S 开, 关} 消融）
**Code revision（冻结）**：tag **`faeco-exp-rev1`** → `87d01ba`
产物：`experiments/20260928_s_l1_ablation/`（8 电路 × {`off`, `on`}）

---

## 0. 一句话

> **待填** —— 严格按三层裁决：enumeration / candidate quality / repair capability。

## 1. 要回答的问题

历史环路消融给出"S 接受 0/8"，但**该证据被集成缺陷混淆**：S 的窗口来源复用 R/G/B 的候选列表，
其长度被 `candidates_per_iteration`(=8) 截断（`flow.py` L626/L607）⇒ 现有结论**只能**说明
"在 R/G/B 的 top-8 割边界里 S 无可接受候选"，**不可外推**为"S 无贡献"。

普查（§13.1.1）证明：

- **`len(candidates) = min(k + 1, 该锥体的可计分割空间)`**：未饱和电路 `k=8 → 9`、`k=32 → 33`
  （**枚举随 `k` 线性增长**）；**s27 小锥体饱和于 6**（`k=8`/`k=32` 均 6）——L1 对其**天然惰性**。
- ⇒ 瓶颈**不在 L626 切片**（只损失 1 个窗口），而在 **L607 枚举的 `k`**；修法 = 给 S 一次
  **`k = resynth_window_pool` 的专属枚举**（**不是**加宽切片）。

**L1 要回答**：把 S 的窗口池从 8 扩到 32（未饱和电路 4×）后，S 是否产出**新**的可接受候选、
并最终改善端点 WNS？**并且必须分三层回答**（§13.4-3）—— 不得因"扩池成功、候选数增加"就升格。

## 2. 单变量纪律与口径

| 项 | `off`（对照） | `on`（处理） |
|---|---|---|
| 开关 | `--no-feedback` | `--no-feedback --structure-resynth --resynth-per-iteration 8 --resynth-window-pool 32` |

两臂**共同**口径（逐字相同）：
`--period 0.5 --max-iterations 20 --candidates-per-iteration 8 --joint-k 2 --enable-buffer
--workers 1 --early-stop --sta-budget 1600 --iscas89-dir …`

- **`resynth_per_iteration` 同时提到 8 是必要的**：池子扩到 32 后，它重新成为每轮上限
  （历史 1/轮 × 20 轮根本覆盖不到 32）；两者**共同**构成"L1 窗口来源"，`off` 臂仍是唯一自由度。
- **预算取 1600（历史 700）**：`W_s=32` 最坏情形 S 候选数上界 ≈ `32 × #触及轮`，须同步放大预算，
  否则"预算被 R/G/B 抢光"会把"S 无贡献"伪装出来（§13.5）。两臂同预算，并**必须给出两臂
  `sta_used` 证明不绑定**（§13.4-5）。

## 3. 纪律检查（先于结论）

### 3.1 控制臂逐位复现

`new/off` 须与归档 `20260924_l3s_ablation/off` **逐位一致**（`mapped.v` 指纹 / `final_patch_id` /
`wns` / `stop_reason` / **预算台账指纹**）。预算 700→1600 只有在不绑定时才不影响等价性，
故此项同时验证"预算放宽未改变对照臂"。

**结果：待填**

> 注：真实 STA 预算计数器是 `state.budget.sta_used`，**不是** `n_candidate_sta_runs`
> （后者是另一口径，两者可差 2×）。探针 `scratch/check_l1_discipline.py`。

### 3.2 惰性单测（先决条件，§13.4-1）

`resynth_window_pool` 默认 `None`（及显式等于 `candidates_per_iteration`）时与未改动版本
**逐位相同**；默认路径只跑一次 `k=8` 枚举、L1 路径出现 `k=32`（spy 断言）。
**`test_flow_structure_resynth.py` 11 passed**（含 2 项新单测）。

### 3.3 预算不绑定（§13.4-5）

**结果：待填**（两臂 max `state.budget.sta_used` vs 1600）

## 4. 结果（三层）

### 4.0 固定指标集（**`windows_offered` 不作 L1 主证据**）

`windows_offered` 含**重复扫描过的割边界**（s27 的 114 ≈ `19×6`），**不是** unique window 数，
仅作**内部扫描开销指标**。本报告固定看：

| 指标 | 含义 | 来源 |
|---|---|---|
| `N_unique_window` | 按 **canonical hash** 去重的窗口数（`hash(netlist_hash ‖ boundary_key)`） | 由 `mark_candidate_tested` 语义/`eval_trials.json` 推 |
| `N_extracted` | 抽窗通过 r2 §4.2 不变量的次数 | `structure_resynth.windows_extracted` |
| `N_S candidate` | S 产出的候选数 | `structure_resynth.candidates` |
| `N_measured` | 真正做了候选 STA 的次数 | `structure_resynth.measured` |
| `N_accepted` | **S 接受数（决定层）** | `structure_resynth.accepted` |

**后四个最关键。**

### 4.1 第一层 · enumeration：L1 自身是否有效

非饱和电路上 `N_S,L1 > N_S,old`。

| 电路 | 历史 `p=1,pool=8` | `k4` `p=4,pool=8` | **L1 `p=8,pool=32`** | 判定 |
|---|---|---|---|---|
| s27 | 2 | 2 | 2 | **饱和**（池 6），L1 天然惰性 |
| s382 | 8 | 8 | 待填 | |
| s420 | 1 | 3 | 待填 | |
| s641 | 0 | 0 | 待填 | |
| s713 | 7 | 7 | 待填 | |
| s820 | 6 | 6 | 待填 | |
| s832 | 5 | 5 | 待填 | |
| s953 | 8 | 8 | 待填 | |
| **合计（`cand`）** | **37** | **39** | **待填** | |

> 旁证（`eval/` 目录数 = 候选评估数，2026-09-28 抽查）：
> `OLD/on/s382 = 23`（15 R/G/B + 8 S）、`NEW/off/s382 = 15`（≡历史）、
> **`NEW/on/s382 = 41+`（15 + ≥26 S，仍在跑）**。

### 4.2 第二层 · candidate quality：问题是否已不在 L1

看 `N_CEC pass`、`N_measured`，以及 S 候选的 **`ΔWNS` 分布**。

**结果：待填**（若枚举涨 3× 而全部 `ΔWNS ≤ 0` ⇒ **问题在 S transformation quality，不在 L1**）

### 4.3 第三层 · repair capability：决定 OI-014

`N_accepted,S` 与 `ΔWNS_final,on − ΔWNS_final,off`（配对）。

**结果：待填**

## 5. 裁决（§13.4 预锁定判据）

| 判据 | 结果 |
|---|---|
| §13.4-1 惰性 | ✅（3.2） |
| §13.4-2 池子普查（含 s27 饱和反例） | ✅（普查报告） |
| §13.4-3 第一层 enumeration | 待填 |
| §13.4-3 第二层 candidate quality | 待填 |
| §13.4-3 第三层 repair capability | 待填 |
| §13.4-5 预算不绑定 | 待填 |

**判定规则**：达到第三层 ⇒ 才有资格重新考虑 **(A) 独立贡献**；若 `N_accepted,S = 0`
——**即使候选 37 → 100+**——结论仍为"**枚举瓶颈已排除，但当前 S 构造在该 benchmark/regime 下
没有体现 timing repair capability**" ⇒ 选 **(B) 降级为可选候选类型/探索性能力**。

**若为负结果的下一步**（§13.7）：**禁止**继续扩池（32→64→128），转做 **S 候选质量归因**：
(i) depth 是否实际下降；(ii) 映射后 depth 是否回来；(iii) cell delay 是否变差；
(iv) fanout/cap 是否抵消结构收益；(v) critical path 是否根本不穿过被重综合窗口。

**对 OI-014 的裁定建议：待填**

## 6. 复现

```bash
export YOSYSHQ_ROOT=/c/oss-cad-suite-build/oss-cad-suite
export PATH="$YOSYSHQ_ROOT/bin:$YOSYSHQ_ROOT/lib:$PATH"
# code revision
git checkout faeco-exp-rev1

FAECO_OUT_ROOT="$PWD/experiments/20260928_s_l1_ablation" \
FAECO_RESYNTH_PER_ITER=8 FAECO_RESYNTH_WINDOW_POOL=32 FAECO_STA_BUDGET=1600 \
bash code/scripts/run_s_ablation_batch.sh off,on s27,s382,s420,s641,s713,s820,s832,s953

# 三层裁决
.venv/Scripts/python.exe code/scripts/compare_s_ablation.py  --root experiments/20260928_s_l1_ablation
.venv/Scripts/python.exe code/scripts/analyze_s_candidates.py --root experiments/20260928_s_l1_ablation/on
.venv/Scripts/python.exe scratch/check_l1_discipline.py
```
