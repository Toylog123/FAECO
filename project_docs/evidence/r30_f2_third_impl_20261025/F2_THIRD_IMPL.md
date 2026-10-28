# F2（第三个布线实现）判决包 — LOG-20261025-28

生成日期：2026-10-25。判据来自 LOG-20261024-25 **开批前**写死的 C1/C2/C3，夹具基线来自同一 LOG。

## 1. 批次与自检

| 项 | 值 |
|---|---|
| 作业表 | `jobs_itc99_f2.tsv` |
| 承诺键数 | 1207 |
| 标签记录 | 1207（解析成功 1207 / 失败 0 / 无日志 0） |
| 带边际量 | 1193（覆盖率 0.988401） |
| 缺失原因 | {"no_base_hash_in_ledger": 14} |
| 摘要口径自检 | 字节 41 / 文本 47 / 命中任一 47 / 未匹配 0 |
| 候选自检 | 1193/1193，批次完整 True，通过 True |
| 第三实现覆盖 | complete=True，覆盖率 1.0 |

## 2. 三个两两实现敏感度带

| 配对 | 2σ (ns) | df | 电路数 | CI95（pooled sd） |
|---|---|---|---|---|
| F0_vs_F1 | 0.049753 | 1193 | 7 | [0.023271, 0.026301] |
| F1_vs_F2 | 0.045540 | 1193 | 7 | [0.021133, 0.024237] |
| F0_vs_F2 | 0.033706 | 1193 | 7 | [0.015764, 0.017855] |

- **max/min = 1.476087**（0.049753 / 0.033706）
- 预注册夹具：可交换合成 **1.028124**、刻意相关 **1.718223**

**C1/C2：NOT EXCHANGEABLE (C2 holds): max/min = 1.476087 is far above the exchangeable fixture (1.028124) and in the range of the deliberately-correlated fixture (1.718223) -> F2's noise level differs from F0/F1 and the implementation sensitivity is driven by the PHYSICAL AXIS (F2 shares the horizontal pin axis with F0 and the vertical one with F1)**

物理轴：F0 = (met3 横 / met2 竖 / util 10)、F1 = (met5 / met4 / util 30)、F2 = (met3 横 / met4 竖 / util 30) → **两轴皆差的一对带最大，只差一轴的对带较小**。

## 3. C3：均值挑选器 vs 单实现挑选器

| 方向 | 池数 | 均值胜 | 单实现胜 | 平 | 精确二项 p |
|---|---|---|---|---|---|
| F0 | 48 | 10 | 10 | 28 | 1.0 |
| F1 | 48 | 7 | 4 | 37 | 0.5488 |
| F2 | 48 | 10 | 11 | 27 | 1.0 |
| **合计** | 144 | **27** | **25** | **92** | **0.8899** |

**C3 does NOT hold: the mean-of-two picker wins 27 vs loses 25 (ties 92, p=0.8899) -> averaging two realisations does NOT improve the pick beyond chance.  Per the pre-registered criterion this is a DATA conclusion, not a tool failure: the synthetic fixture already showed the tool reports the advantage when there is one (38/85/21, p=0.0363).  Note the win/loss count is nominally positive but the exact binomial p=0.8899 is far from significant.**

## 4. 带对已发布判决的影响（三个带全算）

| 配对 | 带 (ns) | resolvable/gain/harm | kind_only 池化 | structural 池化 | structural 池内 | 接受集 增益/损害/惰性 | 增益富集 | 损害比 |
|---|---|---|---|---|---|---|---|---|
| F0_vs_F1 | 0.049753 | 434/48/386 | 0.538238 | 0.432507 | 0.540114 | 0.250000/0.068182/0.681818 | 7.5593 | 0.1944 |
| F1_vs_F2 | 0.045540 | 434/48/386 | 0.538238 | 0.432507 | 0.540114 | 0.250000/0.068182/0.681818 | 7.5593 | 0.1944 |
| F0_vs_F2 | 0.033706 | 500/65/435 | 0.534794 | 0.426741 | 0.516203 | 0.272727/0.068182/0.659091 | 5.6975 | 0.1729 |

**对照遍**：F0/F1 参考带一列逐项复现已发布值（接受集 25.00/6.82/68.18、拒绝集 3.31/35.07/61.62、增益富集 7.5593、损害比 0.1944；`kind_only` 池内 0.555062、`structural` 池化 0.432507）。

**结论**：没有任何一个已发布结论翻转；F1/F2 带与 F0/F1 带在 Δ 量化到 0.01 ns 下完全等价；F0/F2 带跨过一个量化台阶，标签数变化但方向性结论不变 → **已发布用的 F0/F1 带是三者中最大、也就是最保守的一个**。

## 5. 边界

- PROBE on a partially labelled family -- NOT paper evidence.
- the family band DEFINITION stays F0 vs F1: the other pairs are diagnostics and do not change any verdict
- the three-way comparison is about the CHOICE, measured by the regret of the pick against the best candidate in the pool under the held-out labelling
- the deltas are quantised to 0.01 ns, so a regret of 0.0000 ns means "the two pickers landed on candidates that are indistinguishable at the quantum", not "the choice does not matter"
- a band measured on a subset of circuits is not a band for the family: the per-circuit spread differs several-fold across circuits, so a partially finished batch gives a biased band of unknown direction
- ROUNDING CONVENTION: this tool reports 2*pooled_sd of the UNROUNDED pooled sd, while candidate_level_noise.json stores the pooled sd already rounded to 6 decimals and the band is derived from that. The two can differ by 1e-6 ns (ISCAS89: 0.055543 here vs 0.055542 stored). That is a rounding artefact, not a disagreement about the measurement.
- 探针级、**非论文证据**；族带定义仍是 F0/F1，另两对是诊断量，不改任何已发布判决。
- 三个两两差代数相关（`d_F0F2 = d_F0F1 + d_F1F2`）→ 三个估计不独立，**不能做独立性假设下的同质性检验**。
- F2 只在 ITC-99 侧；寄生来自 `estimate_parasitics`、非签核 RC 提取。
- `code/` 未动、HEAD 仍 f761ee1996a83fc4f0f3de0999b74d85a8237858（== origin/main），未提交。

