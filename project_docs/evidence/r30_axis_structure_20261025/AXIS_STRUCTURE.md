# 实现效应与物理轴结构 — LOG-20261025-31 / 32

两件事：**① C3 的机制定论**（"取均值降噪"为什么在本族失败）；**② 把两个物理轴拆开测**，并得到一条关于"判定带"本身的方法学结论。

## 1. C3 的机制（LOG-20261025-31）

### 1.1 控制遍

- 逐方向与总体是否复现已发布产物：{"F0": true, "F1": true, "F2": true}
- 总体：发布 {"n_pool_direction_pairs": 144, "averaged_better": 27, "single_better": 25, "ties": 92, "exact_binomial_p": 0.8899} / 重算 {"n_pool_direction_pairs": 144, "averaged_better": 27, "single_better": 25, "ties": 92, "exact_binomial_p": 0.8899}

### 1.2 退化结构

| 电路 | F0/F1 | F0/F2 | F1/F2 |
|---|---|---|---|
| b01 | 106/571 | 87/571 | 103/571 |
| b02 | 15/55 | 55/55 **全等** | 15/55 |
| b03 | 6/71 | 11/71 | 5/71 |
| b08 | 11/127 | 127/127 **全等** | 11/127 |
| b09 | 11/92 | 92/92 **全等** | 11/92 |
| b10 | 32/216 | 32/216 | 216/216 **全等** |
| b13 | 19/75 | 75/75 **全等** | 19/75 |

非退化电路：b01／b03

### 1.3 两条预测

- 预测 1：if the held-out realisation is IDENTICAL to the single picker's realisation on that circuit, the single picker is already exact (regret 0 in every comparison) and averaging can only tie or lose -- it must never win
  → 10 个格，违例 0 个，**成立 = True**
- 预测 2：if the held-out realisation is IDENTICAL to the second averaged realisation on that circuit, the mean is a shrinkage toward the truth, so the averaged regret must not exceed the single regret
  → 10 个格，违例 0 个，**成立 = True**

### 1.4 配对效应量

| 分组 | n | 平均遗憾 单→均 | 配对改进 (ns) | 折合量子 | Wilcoxon p | 自助 CI95 |
|---|---|---|---|---|---|---|
| full_family | 288 | 0.012569 → 0.011111 | 0.001458 | 0.1458 | 0.2135 | [-0.000903, 0.004028] |
| non_degenerate_circuits | 96 | 0.016042 → 0.01375 | 0.002292 | 0.2292 | 0.3052 | [-0.001563, 0.006875] |
| degenerate_circuits | 192 | 0.010833 → 0.009792 | 0.001042 | 0.1042 | 0.4301 | [-0.001875, 0.004167] |
| label_truth_equals_single_picker | 64 | 0.0 → 0.00625 | -0.00625 | -0.625 | 0.0004 | [-0.01125, -0.002188] |
| label_truth_equals_second_averaged | 64 | 0.015625 → 0.00625 | 0.009375 | 0.9375 | 0.0004 | [0.003437, 0.017188] |
| label_all_three_differ | 160 | 0.016375 → 0.015 | 0.001375 | 0.1375 | 0.3052 | [-0.000938, 0.004167] |

### 1.5 相关结构（OI-052 第 30 条）

- 恒等式 `imp02 = imp01 + imp12` 最大偏差：6.939e-18
- full_family：pearson r = -0.7640672147276872，spearman = -0.6464830330899702，var(imp02)/(var01+var12) = 0.235933，自助 CI95 [-0.877397, -0.596337]
- non_degenerate：pearson r = -0.6524346024906311，spearman = -0.5844982854887422，var(imp02)/(var01+var12) = 0.349058，自助 CI95 [-0.766748, -0.534117]
- degenerate：pearson r = -0.863255522385568，spearman = -0.7806677115068975，var(imp02)/(var01+var12) = 0.141964，自助 CI95 [-0.956172, -0.643711]

## 2. 单轴带与量子格（LOG-20261025-32）

| 变体 | 轴 | 2σ (ns) | 支撑 | n/df | 量子格 |
|---|---|---|---|---|---|
| published_two_axis_all_circuits | both_axes | 0.049753 | b01／b02／b03／b08／b09／b10／b13 | 1200/1193 | idx 5 |
| single_axis_vertical | vertical_only | 0.039884 | b01／b03／b10 | 855/852 | idx 4 |
| single_axis_horizontal | horizontal_only | 0.050272 | b01／b02／b03／b08／b09／b13 | 985/979 | idx 6 |
| two_axis_common_subset | both_axes | 0.040078 | b01／b03 | 640/638 | idx 5 |
| single_axis_vertical_common | vertical_only | 0.035406 | b01／b03 | 640/638 | idx 4 |
| single_axis_horizontal_common | horizontal_only | 0.04155 | b01／b03 | 640/638 | idx 5 |

### 2.1 判决（按量子格分组）

| 量子格 | 变体 | 标签 r/g/h | kind_only 池化 | structural 池化 | structural 池内 | 接受集 增益/惰性 | 富集/损害比 |
|---|---|---|---|---|---|---|---|
| idx 4 | single_axis_vertical／single_axis_vertical_common | 500/65/435 | 0.5347941653160454 | 0.42674068071312804 | 0.5162030872248986 | 0.272727/0.659091 | 5.6975/0.1729 |
| idx 5 | published_two_axis_all_circuits／two_axis_common_subset／single_axis_horizontal_common | 434/48/386 | 0.5382377151493479 | 0.4325066965339954 | 0.5401144876346554 | 0.25/0.681818 | 7.5593/0.1944 |
| idx 6 | single_axis_horizontal | 389/37/352 | 0.5486613322410238 | 0.4451750049436425 | 0.5306411074346604 | 0.25/0.704545 | 11.0483/0.1419 |

结构检查（同一格 ⇒ 逐位相同）：holds = True，违例 0

### 2.2 带的量子格普查

| 带 | 值 | 量子格 | 实际纳入 |
|---|---|---|---|
| pilot_subset band (LOG-20261024-20) | 0.087496 | idx 9 | 0.09 |
| band-change preview (LOG-20261024-23) | 0.050419 | idx 6 | 0.06 |
| published family band F0/F1 (LOG-20261024-24) | 0.049752 | idx 5 | 0.05 |
| probe F0/F1 (LOG-20261025-28) | 0.049753 | idx 5 | 0.05 |
| probe F1/F2 (LOG-20261025-28) | 0.04554 | idx 5 | 0.05 |
| probe F0/F2 (LOG-20261025-28) | 0.033706 | idx 4 | 0.04 |
| single-axis vertical | 0.039884 | idx 4 | 0.04 |
| single-axis horizontal | 0.050272 | idx 6 | 0.06 |
| two-axis, common subset | 0.040078 | idx 5 | 0.05 |
| single-axis vertical, common subset | 0.035406 | idx 4 | 0.04 |
| single-axis horizontal, common subset | 0.04155 | idx 5 | 0.05 |

### 2.3 |routed delta| 直方图（0.01 ns 步长）

- 0×0.01: 171；1×0.01: 273；2×0.01: 137；3×0.01: 89；4×0.01: 68；5×0.01: 48；6×0.01: 44；7×0.01: 60；8×0.01: 51；9×0.01: 52；10×0.01: 32；11×0.01: 33；12×0.01: 26；13×0.01: 21；14×0.01: 9；15×0.01: 13；16×0.01: 10；17×0.01: 8；18×0.01: 10；19×0.01: 1

### 2.4 与已发布参考值的数字对照（flip 表标的是"数字动了"，不是"判决翻转"）

| 类别 | 指标 | 参考值（已发布族带） | 对照值 | flips | 该行的极性 |
|---|---|---|---|---|---|
| label_count | resolvable_positives | 434 | 500 | True | 越多越算（阈值放宽 → 纳入更多，**不是判决变强**） |
| label_count | gain_positives | 48 | 65 | True | 越多越算（阈值放宽 → 纳入更多，**不是判决变强**） |
| label_count | harm_positives | 386 | 435 | True | 越多越算（阈值放宽 → 纳入更多，**不是判决变强**） |
| classifier | kind_only_pooled_auc(resolvable) | 0.5382377151493479 | 0.5347941653160454 | False | 越高越算 |
| classifier | structural_within_pool_auc(resolvable) | 0.5401144876346554 | 0.5162030872248986 | False | 越高越算 |
| classifier | structural_pooled_auc(resolvable) | 0.4325066965339954 | 0.42674068071312804 | False | 越高越算 |
| acceptance | accepted_real_gain_rate | 0.25 | 0.272727 | True | 越高越算（**朝判决更有利**） |
| acceptance | accepted_inert_rate | 0.681818 | 0.659091 | True | 越低越算（**朝判决更有利**） |
| acceptance | gain_enrichment | 7.5593 | 5.6975 | False | 越高越算（**朝判决更有利**） |
| acceptance | harm_ratio | 0.1944 | 0.1729 | True | 越低越算（**朝判决更有利**） |
| label_count | resolvable_positives | 434 | 389 | False | 越多越算（阈值放宽 → 纳入更多，**不是判决变强**） |
| label_count | gain_positives | 48 | 37 | False | 越多越算（阈值放宽 → 纳入更多，**不是判决变强**） |
| label_count | harm_positives | 386 | 352 | False | 越多越算（阈值放宽 → 纳入更多，**不是判决变强**） |
| classifier | kind_only_pooled_auc(resolvable) | 0.5382377151493479 | 0.5486613322410238 | True | 越高越算 |
| classifier | structural_within_pool_auc(resolvable) | 0.5401144876346554 | 0.5306411074346604 | False | 越高越算 |
| classifier | structural_pooled_auc(resolvable) | 0.4325066965339954 | 0.4451750049436425 | True | 越高越算 |
| acceptance | accepted_real_gain_rate | 0.25 | 0.25 | False | 越高越算（**朝判决更有利**） |
| acceptance | accepted_inert_rate | 0.681818 | 0.704545 | False | 越低越算（**朝判决更有利**） |
| acceptance | gain_enrichment | 7.5593 | 11.0483 | True | 越高越算（**朝判决更有利**） |
| acceptance | harm_ratio | 0.1944 | 0.1419 | True | 越低越算（**朝判决更有利**） |
| label_count | resolvable_positives | 434 | 434 | False | 越多越算（阈值放宽 → 纳入更多，**不是判决变强**） |
| label_count | gain_positives | 48 | 48 | False | 越多越算（阈值放宽 → 纳入更多，**不是判决变强**） |
| label_count | harm_positives | 386 | 386 | False | 越多越算（阈值放宽 → 纳入更多，**不是判决变强**） |
| classifier | kind_only_pooled_auc(resolvable) | 0.5382377151493479 | 0.5382377151493479 | False | 越高越算 |
| classifier | structural_within_pool_auc(resolvable) | 0.5401144876346554 | 0.5401144876346554 | False | 越高越算 |
| classifier | structural_pooled_auc(resolvable) | 0.4325066965339954 | 0.4325066965339954 | False | 越高越算 |
| acceptance | accepted_real_gain_rate | 0.25 | 0.25 | False | 越高越算（**朝判决更有利**） |
| acceptance | accepted_inert_rate | 0.681818 | 0.681818 | False | 越低越算（**朝判决更有利**） |
| acceptance | gain_enrichment | 7.5593 | 7.5593 | False | 越高越算（**朝判决更有利**） |
| acceptance | harm_ratio | 0.1944 | 0.1944 | False | 越低越算（**朝判决更有利**） |
| label_count | resolvable_positives | 434 | 500 | True | 越多越算（阈值放宽 → 纳入更多，**不是判决变强**） |
| label_count | gain_positives | 48 | 65 | True | 越多越算（阈值放宽 → 纳入更多，**不是判决变强**） |
| label_count | harm_positives | 386 | 435 | True | 越多越算（阈值放宽 → 纳入更多，**不是判决变强**） |
| classifier | kind_only_pooled_auc(resolvable) | 0.5382377151493479 | 0.5347941653160454 | False | 越高越算 |
| classifier | structural_within_pool_auc(resolvable) | 0.5401144876346554 | 0.5162030872248986 | False | 越高越算 |
| classifier | structural_pooled_auc(resolvable) | 0.4325066965339954 | 0.42674068071312804 | False | 越高越算 |
| acceptance | accepted_real_gain_rate | 0.25 | 0.272727 | True | 越高越算（**朝判决更有利**） |
| acceptance | accepted_inert_rate | 0.681818 | 0.659091 | True | 越低越算（**朝判决更有利**） |
| acceptance | gain_enrichment | 7.5593 | 5.6975 | False | 越高越算（**朝判决更有利**） |
| acceptance | harm_ratio | 0.1944 | 0.1729 | True | 越低越算（**朝判决更有利**） |
| label_count | resolvable_positives | 434 | 434 | False | 越多越算（阈值放宽 → 纳入更多，**不是判决变强**） |
| label_count | gain_positives | 48 | 48 | False | 越多越算（阈值放宽 → 纳入更多，**不是判决变强**） |
| label_count | harm_positives | 386 | 386 | False | 越多越算（阈值放宽 → 纳入更多，**不是判决变强**） |
| classifier | kind_only_pooled_auc(resolvable) | 0.5382377151493479 | 0.5382377151493479 | False | 越高越算 |
| classifier | structural_within_pool_auc(resolvable) | 0.5401144876346554 | 0.5401144876346554 | False | 越高越算 |
| classifier | structural_pooled_auc(resolvable) | 0.4325066965339954 | 0.4325066965339954 | False | 越高越算 |
| acceptance | accepted_real_gain_rate | 0.25 | 0.25 | False | 越高越算（**朝判决更有利**） |
| acceptance | accepted_inert_rate | 0.681818 | 0.681818 | False | 越低越算（**朝判决更有利**） |
| acceptance | gain_enrichment | 7.5593 | 7.5593 | False | 越高越算（**朝判决更有利**） |
| acceptance | harm_ratio | 0.1944 | 0.1944 | False | 越低越算（**朝判决更有利**） |

**`flips=true` ≠ "判决被推翻"**：本包与 LOG-32 说的"已发布结论无一翻转"，指的是**判决方向没有反过来**；上表被标 `flips=true` 的行多数是**判决被加强**的方向。

## 3. 边界

- PROBE level, NOT paper evidence.  A single-axis band can only be measured on the circuits where that axis is active, so the single-axis bands and the two-axis band are NOT measured on the same circuits; the common-subset rows are the like-for-like comparison and they cover only 2 circuits.  The post-route WNS is quantised to 0.01 ns.  Parasitics come from estimate_parasitics, not signoff RCX.
- PROBE level, NOT paper evidence.  The three pairwise realisation differences are algebraically dependent (d_F0F2 = d_F0F1 + d_F1F2), so this is a mechanism check, not an independence test.  The non-degenerate subset has only 2 circuits, so its C3 verdict has very low power -- it can REFUTE the advantage but cannot establish it.  The post-route WNS is quantised to 0.01 ns, so a regret of 0.0000 ns means "the two picks are indistinguishable at the quantum".  Parasitics come from estimate_parasitics, not signoff RCX.
- `code/` 未动、HEAD 仍 f761ee1996a83fc4f0f3de0999b74d85a8237858，未提交。
