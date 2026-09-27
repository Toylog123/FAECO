# FAECO 3-A 电气风险前置：采集口径相关性判定

- 产物根：`experiments\20260926_electrical_3a`
- 臂对（对照:采集）：`phys:elec, base:cap`
- 有效 trial 行数：8298

## Gate 0 —— 两臂行为一致性（采集必须惰性）

- 通过：**True**
  - `phys`：8 电路，全部一致
  - `base`：8 电路，全部一致

## 预算不绑定核对（sta_used 必须 < sta_budget）

| 臂对 | 电路 | control sta_used | capture sta_used | sta_budget |
|---|---|---|---|---|
| phys | s27 | 408 | 408 | 1600 |
| phys | s382 | 166 | 166 | 1600 |
| phys | s420 | 292 | 292 | 1600 |
| phys | s641 | 830 | 830 | 1600 |
| phys | s713 | 412 | 412 | 1600 |
| phys | s820 | 349 | 349 | 1600 |
| phys | s832 | 996 | 996 | 1600 |
| phys | s953 | 273 | 273 | 1600 |
| base | s27 | 127 | 127 | 1600 |
| base | s382 | 366 | 366 | 1600 |
| base | s420 | 476 | 476 | 1600 |
| base | s641 | 319 | 319 | 1600 |
| base | s713 | 127 | 127 | 1600 |
| base | s820 | 185 | 185 | 1600 |
| base | s832 | 157 | 157 | 1600 |
| base | s953 | 190 | 190 | 1600 |

## 采集覆盖率

| 臂对 | 电路 | trials | 含电气量 | 覆盖率 |
|---|---|---|---|---|
| phys | s27 | 532 | 524 | 98.5% |
| phys | s382 | 324 | 324 | 100.0% |
| phys | s420 | 147 | 136 | 92.5% |
| phys | s641 | 943 | 886 | 94.0% |
| phys | s713 | 611 | 595 | 97.4% |
| phys | s820 | 363 | 353 | 97.2% |
| phys | s832 | 1186 | 1158 | 97.6% |
| phys | s953 | 375 | 373 | 99.5% |
| base | s27 | 416 | 404 | 97.1% |
| base | s382 | 769 | 704 | 91.5% |
| base | s420 | 1048 | 996 | 95.0% |
| base | s641 | 596 | 558 | 93.6% |
| base | s713 | 306 | 306 | 100.0% |
| base | s820 | 312 | 308 | 98.7% |
| base | s832 | 306 | 300 | 98.0% |
| base | s953 | 393 | 373 | 94.9% |

## 标签可用性（双类下限 20）

| 标签 | 行数 | 正例 | 负例 | 可用 |
|---|---|---|---|---|
| `f6` | 4349 | 4298 | 51 | 是 |
| `no_physical_gain` | 4349 | 4296 | 53 | 是 |
| `hard_fail` | 8298 | 1371 | 6927 | 是 |
| `no_ideal_gain` | 8298 | 8191 | 107 | 是 |

## 失败事件直方图

- `F6_physical_load_failure`: 4298
- `acceptance_budget_violation`: 1368
- `F3_patch_too_large`: 11

## 预锁定判定

**NO SIGNAL** —— no feature cleared 0.65 on >= 2 usable labels with a consistent direction (best single oriented AUC 0.6519); keep electrical quantities out of eq. (2).

- 可用标签：['f6', 'hard_fail', 'no_ideal_gain', 'no_physical_gain']

> 判据在采集前写定于 `code/scripts/analyze_electrical_correlation.py` 头部：
> 需**同一特征**在 **≥2 个可用标签**上同时越过 AUC 阈值且方向一致；
> 连续量（vs 物理增益的 Spearman）仅供参考、不参与判定。
