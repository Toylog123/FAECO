# 判定带换值的证伪预演（LOG-20261024-23）

## 问题

the routed candidate-level band moves from the pilot scope (2 sigma = 0.087496 ns) to the full-family scope (preview 2 sigma = 0.050419 ns, about 42% narrower) when the I1 batch completes; which of the LOG-20261024-21 conclusions survive and which flip?

## 方法

- NONE -- the two tools are imported and their own functions are called with a band override
- 对照遍必须精确复现存储产物：**the control pass (band in force) must reproduce the stored LOG-20261024-21 artefacts exactly; observed: 20 checks, 0 mismatches, max deviation 0.0**
- the training table is held FIXED between the two passes, so this isolates the effect of the threshold; the final recomputation will also have more labelled rows
- the routed labels come from the COMPLETED I0 batch and the placed labels from the COMPLETED IPLACED, so the I1 batch changes the BAND only; the only unknown is the final band value
- 训练表 1207 行，联表后可用 1117 行，电路 b01, b02, b03, b08, b09, b10, b13

## 带

| 口径 | 2σ (ns) |
|---|---|
| 现行（pilot_subset） | 0.087496 |
| 预览（full_family） | 0.050419 |

## 候选级分类 · resolvable 标签（正例 243 → 389，powered True → True）

| 特征集 | 对照 AUC [CI] | 预览 AUC [CI] | G1 | G2 | G3 | G4 |
|---|---|---|---|---|---|---|
| `kind_only` | 0.573493 [0.5079, 0.6321] | 0.548661 [0.5069, 0.6009] | Y | n | n | n |
| `proxy_only` | 0.667006 [0.6152, 0.7171] | 0.598435 [0.5328, 0.6508] | Y | Y | n | n |
| `proxy_plus_ideal` | 0.889887 [0.8026, 0.9383] | 0.814108 [0.7116, 0.8801] | Y | Y | Y | Y |
| `structural` | 0.444433 [0.3713, 0.5146] | 0.445175 [0.3726, 0.5301] | n | n | n | n |
| `structural_cp_plus_ideal` | 0.811163 [0.7249, 0.8798] | 0.777328 [0.6887, 0.8451] | Y | Y | Y | Y |
| `structural_plus_ideal` | 0.83832 [0.7535, 0.8978] | 0.751665 [0.6312, 0.8493] | Y | Y | n | Y |

## 候选级分类 · gain 标签（正例 12 → 37，powered False → True）

| 特征集 | 对照 AUC [CI] | 预览 AUC [CI] | G1 | G2 | G3 | G4 |
|---|---|---|---|---|---|---|
| `kind_only` | 0.293401 [0.1876, 0.6623] | 0.103804 [0.0556, 0.3111] | n | n | n | n |
| `proxy_only` | 0.63914 [0.4113, 0.8481] | 0.606932 [0.3598, 0.8228] | n | Y | n | n |
| `proxy_plus_ideal` | 0.701207 [0.5067, 0.9196] | 0.657432 [0.4235, 0.8983] | n | Y | n | n |
| `structural` | 0.226244 [0.0820, 0.4253] | 0.661449 [0.4560, 0.8176] | n | Y | n | n |
| `structural_cp_plus_ideal` | 0.243778 [0.0986, 0.4431] | 0.685023 [0.5033, 0.8391] | Y | Y | n | n |
| `structural_plus_ideal` | 0.233974 [0.0881, 0.4381] | 0.684222 [0.4976, 0.8365] | n | Y | n | n |

## 候选级分类 · harm 标签（正例 231 → 352，powered True → True）

| 特征集 | 对照 AUC [CI] | 预览 AUC [CI] | G1 | G2 | G3 | G4 |
|---|---|---|---|---|---|---|
| `kind_only` | 0.597808 [0.5383, 0.6671] | 0.578288 [0.5354, 0.6289] | Y | n | Y | Y |
| `proxy_only` | 0.708769 [0.6446, 0.7768] | 0.69492 [0.6285, 0.7632] | Y | Y | Y | Y |
| `proxy_plus_ideal` | 0.938778 [0.9031, 0.9622] | 0.912983 [0.8811, 0.9437] | Y | Y | Y | Y |
| `structural` | 0.476877 [0.3830, 0.5758] | 0.503017 [0.3987, 0.6112] | n | n | n | n |
| `structural_cp_plus_ideal` | 0.908226 [0.8608, 0.9408] | 0.89582 [0.8497, 0.9346] | Y | Y | Y | Y |
| `structural_plus_ideal` | 0.896756 [0.8496, 0.9328] | 0.904958 [0.8571, 0.9416] | Y | Y | Y | Y |

## 消融（标签 = resolvable）

| 特征集 | 对照 AUC [CI] | 预览 AUC [CI] |
|---|---|---|
| `ideal_only` | 0.885202 [0.8002, 0.9411] | 0.854611 [0.7624, 0.9212] |
| `ideal_plus_placed` | 0.909955 [0.8348, 0.9519] | 0.859205 [0.7605, 0.9156] |
| `placed_only` | 0.926597 [0.8519, 0.9698] | 0.894462 [0.7930, 0.9509] |
| `proxy_only` | 0.667006 [0.6078, 0.7121] | 0.598435 [0.5293, 0.6515] |
| `proxy_plus_ideal` | 0.889887 [0.8032, 0.9398] | 0.814108 [0.7110, 0.8811] |
| `proxy_plus_placed` | 0.910411 [0.8328, 0.9549] | 0.820525 [0.7134, 0.8869] |
| `structural` | 0.444433 [0.3701, 0.5161] | 0.445175 [0.3732, 0.5321] |

## 接受判据的物理选择性（布线后）

| 项 | 对照（带 0.087496） | 预览（带 0.050419） |
|---|---|---|
| 接受集 n | 44 | 44 |
| 拒绝集 n | 1149 | 1149 |
| 接受集 真实增益/损害/惰性 | 0.1136 / 0.0455 / 0.8409 | 0.2500 / 0.0455 / 0.7045 |
| 拒绝集 真实增益/损害/惰性 | 0.0061 / 0.2071 / 0.7868 | 0.0226 / 0.3203 / 0.6571 |
| 增益富集 | 18.6533 | 11.0483 |
| 损害比 | 0.2194 | 0.1419 |
| 置换 p 增益/损害（电路匹配） | 0.0 / 0.004 | 0.0 / 0.0 |
| 逐电路 增益 | 3W/0L/4T p=0.25 | 5W/0L/2T p=0.0625 |
| 逐电路 损害 | 1W/6L/0T p=0.125 | 1W/6L/0T p=0.125 |

## 结论分层

**站得住**：
- the graph features carry no candidate-level physical signal for the RESOLVABLE and HARM labels (structural AUC 0.445175 / 0.503017, CI still includes 0.5, G1 fails)
- adding the graph features to the label HURTS, and more than before (structural_plus_ideal 0.751665 vs ideal_only 0.854611; the gap widens from 0.047 to 0.103)
- the cheap placed stage is still the strongest single feature (placed_only 0.894462)
- the ideal-net acceptance criterion has real physical selectivity, and the harm part gets STRONGER (harm ratio 0.2194 -> 0.1419, permutation p -> 0.0)

**会翻 / 必须改述**：
- "the graph features carry no signal" does NOT hold for the GAIN label: the positive count goes 12 -> 37 (above the power floor) and the structural AUC flips from 0.226244 to 0.661449 (CI [0.4560, 0.8176], G1 and G2 pass, G3 and G4 do not). Hence "training a GNN to replace OpenSTA has nothing to gain in this family" MUST be qualified: it holds for the resolvable and harm labels, not for the gain label.
- "the ideal net lies = harm avoidance works, gain does not" must become "harm avoidance is stronger, gain is limited": the accepted set's real gain rate goes 11.36% -> 25.00% and the inert share 84.09% -> 70.45%. The gain ENRICHMENT falls 18.6533 -> 11.0483 because the REJECTED set's real gain rate also rises (0.61% -> 2.26%), not because the accepted set got worse.

**不变的禁令**：
- the "accepted N candidates therefore improved the WNS" phrasing is still forbidden (a quarter of the accepted set is a real gain at best, and the enrichment falls)

## 边界

- 探针级证伪预演，**不是论文证据**。
- 预演**固定了训练表**（只变门槛），最终数字由定稿链在 I1 收齐后重算；唯一未知量是带的最终值。
- G3/G4 在 `gain` 标签上仍不过，**不得据 `gain` 标签的单点 AUC 宣称图特征有信号**。
- `code/` 未动、HEAD 未变、未提交。
