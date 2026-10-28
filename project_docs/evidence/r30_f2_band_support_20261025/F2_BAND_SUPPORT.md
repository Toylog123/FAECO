# F2 带支撑混淆审计 — LOG-20261025-30

**问题**：LOG-20261025-28 用三个两两带（max/min = 1.476087）判定"C1 不成立、C2 成立"。
这三个带**是否建立在同一批电路上**？

## 1. 对照遍

- 已发布产物：{"F0_vs_F1": 0.049753, "F0_vs_F2": 0.033706, "F1_vs_F2": 0.04554}
- 本次重算：{"F0_vs_F1": 0.049753, "F0_vs_F2": 0.033706, "F1_vs_F2": 0.04554}
- 逐项一致：{"F0_vs_F1": true, "F0_vs_F2": true, "F1_vs_F2": true}；比值一致：True（发布 1.476087 / 重算 1.476087）
- 判决分类器一致：True（阈值取自 `scratch/interpret_f2_result.py`，即 LOG-25 开批前写死的 1.10 / 1.35）

## 2. 退化的逐候选统计

| 电路 | F0/F1 | F0/F2 | F1/F2 |
|---|---|---|---|
| b01 | 106/571 | 87/571 | 103/571 |
| b02 | 15/55 | 55/55 | 15/55 |
| b03 | 6/71 | 11/71 | 5/71 |
| b08 | 11/127 | 127/127 | 11/127 |
| b09 | 11/92 | 92/92 | 11/92 |
| b10 | 32/216 | 32/216 | 216/216 |
| b13 | 19/75 | 75/75 | 19/75 |

（分子 = 布线后 WNS **逐位相同**的配对候选数，分母 = 配对候选总数）

## 3. 三种口径的带

| 口径 | F0/F1 | F1/F2 | F0/F2 | max/min | 判决 |
|---|---|---|---|---|---|
| 全族 | 0.049753 | 0.045540 | 0.033706 | 1.476087 | C2 成立 |
| 共同非退化子集 b01／b03 | 0.040078 | 0.041550 | 0.035406 | **1.173530** | **INCONCLUSIVE** |
| 各对自己的携方差支撑 | 0.049753 | 0.050272 | 0.039884 | 1.260455 | INCONCLUSIVE |

## 4. 显著性门

- 留一电路：1.218976 … 1.758842（7 次全部 > 1.10）
- 电路集自助 2000 次（seed 20261025）：CI95 [1.145302, 3.273719]，中位数 1.508452，最大 4.673566，只有 0.0051 落到 1.10 以下，46 次无定义

## 5. 恒等性指纹

- 规则：d_F0F2 = d_F0F1 + d_F1F2 per candidate; if one pair is identically zero on a circuit the other two pairs have equal SD there -- an identity, so a mismatch would mean the degeneracy is a bookkeeping artefact
- b02：F0_vs_F2 退化（55 对）→ 另两对 sd 0.014460964589381505 / 0.014460964589381505，相等：True
- b08：F0_vs_F2 退化（127 对）→ 另两对 sd 0.023924351677205451 / 0.023924351677205451，相等：True
- b09：F0_vs_F2 退化（92 对）→ 另两对 sd 0.051076805389922833 / 0.051076805389922833，相等：True
- b10：F1_vs_F2 退化（216 对）→ 另两对 sd 0.025475269383095345 / 0.025475269383095345，相等：True
- b13：F0_vs_F2 退化（75 对）→ 另两对 sd 0.018786294010551156 / 0.018786294010551156，相等：True
- 全部成立：True

## 6. 不是批次假象的证据

- b01：I0_vs_I2: 均不同 ｜ I1_vs_I2: 均不同 ｜ I0_vs_I1: 均不同
- b02：I0_vs_I2: 逐字节相同 final.odb ｜ I1_vs_I2: 均不同 ｜ I0_vs_I1: 均不同
- b03：I0_vs_I2: 均不同 ｜ I1_vs_I2: 均不同 ｜ I0_vs_I1: 均不同
- b08：I0_vs_I2: 逐字节相同 final.odb ｜ I1_vs_I2: 均不同 ｜ I0_vs_I1: 均不同
- b09：I0_vs_I2: 逐字节相同 final.odb ｜ I1_vs_I2: 均不同 ｜ I0_vs_I1: 均不同
- b10：I0_vs_I2: 均不同 ｜ I1_vs_I2: 逐字节相同 final.odb ｜ I0_vs_I1: 均不同
- b13：I0_vs_I2: 逐字节相同 final.odb ｜ I1_vs_I2: 均不同 ｜ I0_vs_I1: 均不同

日志行级差分（退化对上）：
- b02_I0_I2：日志行数 1542 vs 1542，仅差 15 / 15 行（`Number of slots` 与计时/内存行）
- b08_I0_I2：日志行数 34303 vs 34303，仅差 51 / 51 行（`Number of slots` 与计时/内存行）
- b09_I0_I2：日志行数 54054 vs 54054，仅差 50 / 50 行（`Number of slots` 与计时/内存行）
- b13_I0_I2：日志行数 35329 vs 35329，仅差 50 / 50 行（`Number of slots` 与计时/内存行）
- b10_I1_I2：日志行数 34436 vs 34436，仅差 51 / 51 行（`Number of slots` 与计时/内存行）

## 7. 分层判决

### SURVIVES

- **C1_fails**：the three pairwise bands are NOT exchangeable, and this holds in every comparison: full family 1.476087, common non-degenerate subset 1.17353, each pair on its own support 1.260455, leave-one-circuit-out 1.218976..1.758842, and per circuit b01 1.166605 / b03 1.34556 -- all above the pre-registered exchangeable threshold 1.10
- **band_value**：the published family band (F0 vs F1, 0.049753 ns) is unchanged: the F0/F1 pair has NO degenerate circuit, so it is neither diluted nor support-confounded
- **published_verdicts**：LOG-20261025-28 established that no published verdict flips under the other two bands; that conclusion is untouched, because it is a threshold-sensitivity statement, not a between-band comparison

### WITHDRAWN

- **C2_holds**：C2 does NOT survive the unconfounded comparison: on the common non-degenerate subset the ratio is 1.17353 and on each pair's own variance-carrying support it is 1.260455 -- both inside the INCONCLUSIVE band [1.10, 1.35).  The full-family value 1.476087 crossed the C2 threshold only because the dilution pushed the F0/F2 band down and because b09's sd is outsized
- **physical_axis_mechanism**：the claim "the implementation sensitivity is driven by the physical axis (F0/F1 differs on both axes -> largest band; F2 vs F0 differs on one axis -> smallest band)" is not supported: on the common subset the ordering is F1/F2 0.04155 > F0/F1 0.040078 > F0/F2 0.035406, i.e. the ONE-axis pair F1/F2 carries the LARGEST band.  The full-family ordering was a dilution artefact.
- **C2_is_not_disproved**：the withdrawal means the data no longer SUPPORTS C2, not that C2 was disproved: the bootstrap over circuit sets has a CI95 that straddles the pre-registered C2 threshold of 1.35, so C2 is neither established nor refuted -- it is simply no longer a conclusion this family can carry
- **f0f1_is_the_largest**：the statement "the published F0/F1 band is the largest of the three, i.e. the most conservative" holds only under the full-family pooling; on the common subset F1/F2 (0.04155) exceeds F0/F1 (0.040078).  The safe statement is that F1/F2 and F0/F1 are EQUIVALENT at the 0.01 ns quantisation of the measured deltas, so every verdict computed with either one is identical.

### NEW_FINDING

- **partial_degeneracy**：the third realisation is PARTIALLY degenerate: on b02/b08/b09/b13 the vertical pin-layer change (met2 -> met4) left the routed database (final.odb) BYTE-IDENTICAL to F0 for every candidate, and on b10 the horizontal pin-layer change (met5 -> met3) left it byte-identical to F1.  The runs really executed (the logs differ in the place_pins slot count and in the timing lines; the placement lines are identical), so this is a property of the designs and the realisation axis, not a skipped job.
- **single_axis_is_inert_here**：the family band is measured on the pair that differs on BOTH axes, so 0.049752 ns is an UPPER bound on the sensitivity to a single physical axis, not an unbiased estimate of it
- **identity_fingerprint_holds**：the per-circuit identity (if one pair is identically zero, the other two pairs must have the same within-circuit sd) holds on every degenerate circuit: True

## 8. 边界

- PROBE level, NOT paper evidence.  The post-route WNS is quantised to 0.01 ns, so "identical" means identical at that quantum.  The floorplan is frozen, so the utilisation part of the realisation axis has no effect and only the pin layers differ.  The three pairwise differences are algebraically dependent (d_F0F2 = d_F0F1 + d_F1F2 per candidate), so their correlations carry no independent information.  Parasitics come from estimate_parasitics, not from signoff RCX.
- `code/` 未动、HEAD 仍 f761ee1996a83fc4f0f3de0999b74d85a8237858，未提交。
