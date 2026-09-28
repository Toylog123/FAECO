# FAECO S 窗口池普查报告（阶段 2-A 后续）

日期：2026-09-28
契约/设计：`project_docs/planning/FAECO_V2_TECH_DESIGN_20260923.md` §13（诊断与重设计）
未决问题：OI-014（S 的论文定位）
产物：`experiments/20260928_pool_census_fast/`、`experiments/20260928_pool_census_k32/`、
`experiments/20260928_s_pool_census/`
插桩位置：`code/src/rseco/flow.py`（`s_stats["pool_census"]`，**只读**）

---

## 1. 要回答的问题

技术设计 §13 诊断出"S 的窗口来源与 R/G/B 的束宽耦合"，但**归因到哪一行**还没定：
是 **L626 的切片**（`candidates[:max_candidates_per_iteration]`），还是 **L607 的枚举 `k`**
（`_cone_candidates(..., k=max_candidates_per_iteration)`）？

这决定了修法的形态与成本：

- 若是**切片** ⇒ 加宽切片即可（一行）；
- 若是**枚举** ⇒ 必须用更大的 `k` 重新枚举（并且要验证枚举是否随 `k` 增长；若不增长，
  则瓶颈在 cone/深度切分，改动大得多）。

§13.4-2 把这一步定为**最便宜、最先做**的验证。

## 2. 方法：只读插桩 `pool_census`

在 `flow.py` 计算完 `round_candidates` 之后、进入 S 循环之前，记录两个长度：

| 字段 | 含义 |
|---|---|
| `candidates_len` | **未截断**的加权割候选列表长度 `len(candidates)` |
| `round_candidates_len` | **截断后**交给 R/G/B 与 S 的列表长度 `len(round_candidates)` |

**惰性保证**：通过 `s_stats.setdefault(...)` 且仅在 `structure_resynth` 为真时记录 ⇒
**{S 关} 臂的产物逐位不变**（不新增 key），§13.4-1 的惰性先决条件仍成立。全量测试
**536 passed / 4 skipped**。

三个口径（其余参数与 S 环路消融一致：`--period 0.5 --joint-k 2 --enable-buffer
--workers 1 --early-stop --no-feedback --structure-resynth`）：

| # | 口径 | 电路 | 轮数 |
|---|---|---|---|
| A | `--candidates-per-iteration 8` | s382 / s713 / s832 / s953 | 2 |
| B | `--candidates-per-iteration 8` | s420 | **20（全程）** |
| C | `--candidates-per-iteration 32` | s382 / s953 | 2 |

## 3. 结果

| 口径 | `len(candidates)`（未截断） | `len(round_candidates)`（截断后） |
|---|---|---|
| **A** `k = 8`，4 电路 × 2 轮 | **9** | 8 |
| **B** `k = 8`，s420 **全 20 轮** | **[9] × 20** | [8] × 20 |
| **C** `k = 32`，2 电路 × 2 轮 | **33** | 32 |

原始读数（逐轮序列）：A 的四电路均为 `[9, 9]`；B 为 `[9]*20`；C 为 `[33, 33]`。

## 4. 结论

1. **`len(candidates) = k + 1`，且与轮次、cone、`G_r` 无关。**
   s420 全 20 轮恒为 9（尽管 20 轮里接受过 R/G/B 补丁、cone 与 `G_r` 都在变）；
   `k` 变到 32 时恒为 33。那个 `+1` 是前置的 `_critical_path_cover_cut`。
   ⇒ **L626 的截断只损失 1 个窗口，不是瓶颈。**
2. **加权割枚举随 `k` 线性增长**（8 → 9，32 → 33）。
   ⇒ **给 S 一次 `k = resynth_window_pool` 的专属枚举，即可把 S 的窗口池从 8 扩到 32（4×）**，
   **无需**改 cone / 深度切分。

**可引用的定量形式**：S 的可触及窗口上界
= **不同 `G_r` 数 × `candidates_per_iteration`**
—— 即 **S 的触达范围被 R/G/B 的束宽直接决定**。

## 5. 对技术设计的修正（自我更正）

§13.1 初稿把主因归到 **L626 切片**；本普查显示那是**不完全的归因**（切片只占 1 个窗口）。
已在技术设计 §13.1 顶部加"归因已修正"警示、补全 §13.1.1 表、标记 §13.4-2 完成，
并把 **L1 的修法从"加宽切片"改为"S 专属的更大 `k` 枚举"**。

> 这正是把最便宜的验证放在实现之前的收益：**结论在写代码之前就改了一次**。

## 6. 局限与下一步

- **只测了边界数，没测"多出来的窗口是否有用"。** 第 9–32 名是加权割枚举按 `weights`
  排序的**次优边界**，它们是否能产出可接受的 S 候选，仍是**未验证的经验问题**。
- **未实现 L1**（新增机制须先定案；技术设计 §13 只写方案）。论文侧未动 `.tex`。
- **下一步（OI-014 的裁定前提）**：实现 L1（`resynth_window_pool = 32`，默认值 =
  `candidates_per_iteration` ⇒ 逐位惰性）→ 重跑 {S 开, S 关} → 用新证据裁
  (A) 独立贡献 / (B) 降级可选。
- `experiments/20260928_s_pool_census/` 的 s713/s832/s953 20 轮普查在收尾（用于把
  "与轮次无关"的结论从 1 个电路扩到 4 个）。

## 7. 复现

```bash
export YOSYSHQ_ROOT=/c/oss-cad-suite-build/oss-cad-suite
export PATH="$YOSYSHQ_ROOT/bin:$YOSYSHQ_ROOT/lib:$PATH"

# 口径 A（k=8，2 轮）
.venv/Scripts/python.exe code/scripts/run_outerloop_real_wns.py --circuit s382 \
  --no-feedback --structure-resynth --resynth-per-iteration 1 --resynth-variants S0,S1,S2 \
  --period 0.5 --max-iterations 2 --candidates-per-iteration 8 --joint-k 2 \
  --enable-buffer --workers 1 --early-stop --sta-budget 300 \
  --iscas89-dir data/raw/benchmarks/raw/iscas89 \
  --output-dir experiments/20260928_pool_census_fast/on/s382

# 口径 C（k=32）：同上，改 --candidates-per-iteration 32 与输出目录

# 读取读数
python -c "import json;d=json.load(open('<out>/s382/outerloop_result.json'));\
print(d['structure_resynth']['pool_census'])"
```
