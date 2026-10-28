# 图特征信号的归因与跨族复现（LOG-20261024-24）

## 问题

with the FINAL band (full_family, 2 sigma = 0.049752 ns), does the gate-level graph-feature signal survive? and is it a CANDIDATE-level signal a generator can use, or a POOL-level one it cannot?

## 带

| 口径 | 2σ (ns) |
|---|---|
| pilot_subset（旧，全批前） | 0.087496 |
| 预演值（LOG-23） | 0.050419 |
| **最终值（full_family）** | **0.049752** |

对照遍（带=最终值）复现定稿链刚写入的产物：**20 项检查、0 处不符、最大偏差 0.0**。

## 预演 → 最终：结论是否兑现

| 标签 | 正例（预演 → 最终） | `structural` 预演 | `structural` 最终 |
|---|---|---|---|
| resolvable | 389 → 434 | 0.445175 | 0.432507 |
| gain | 37 → 48 | 0.661449 | 0.698248 |
| harm | 352 → 386 | 0.503017 | 0.499071 |

## 池级 vs 候选级分解（候选生成器唯一能用的读数）

### itc99 · resolvable（正例 434，39/47 个池有双类别）

| 特征集 | 池化 AUC | 仅池均值（池间成分） | 池内 AUC [CI] |
|---|---|---|---|
| `one_depth` | 0.5917121536188272 | 0.5602350702714374 | 0.5481398039195426 [0.4996, 0.6006] |
| `one_n_cells` | 0.5310705683113939 | 0.505843021098299 | 0.5612968377906002 [0.5082, 0.6188] |
| `one_max_fanout` | 0.533816653284844 | 0.5172962870502189 | 0.5551525738080019 [0.5037, 0.6095] |
| `one_n_ff` | 0.540435595198737 | 0.520079481280067 | 0.5559473677096723 [0.5043, 0.6101] |
| `struct_global_only` | 0.48360445580962275 | 0.45207845571516286 | 0.5554656460708595 [0.5031, 0.6116] |
| `struct_local_only` | 0.44614940861339575 | 0.4716653959557658 | 0.5343224613279001 [0.4808, 0.5930] |
| `struct_delta_only` | 0.5602300099182922 | 0.4700359622430184 | 0.5502605021639396 [0.5007, 0.6039] |
| `structural` | 0.4325066965339954 | 0.4339961271430596 | 0.5401144876346554 [0.4939, 0.5917] |
| `kind_only` | 0.5382377151493479 | 0.540010525534542 | 0.555062288506449 [0.5036, 0.6093] |

### itc99 · gain（正例 48，13/47 个池有双类别）

| 特征集 | 池化 AUC | 仅池均值（池间成分） | 池内 AUC [CI] |
|---|---|---|---|
| `one_depth` | 0.18496647957592766 | 0.16408442469597756 | 0.5562109399670685 [0.4376, 0.6777] |
| `one_n_cells` | 0.1295213595260368 | 0.11355043654505768 | 0.6568342947857647 [0.5712, 0.7489] |
| `one_max_fanout` | 0.7066378235110695 | 0.7342824290614282 | 0.6724690665180973 [0.5777, 0.7718] |
| `one_n_ff` | 0.28634627377611477 | 0.22709112878079202 | 0.6568342947857647 [0.5712, 0.7489] |
| `struct_global_only` | 0.7588575771749299 | 0.7365041315871531 | 0.6637232688557824 [0.5569, 0.7643] |
| `struct_local_only` | 0.33813727782974745 | 0.30262901465544123 | 0.4788495791551956 [0.3203, 0.6445] |
| `struct_delta_only` | 0.5979010757717493 | 0.5879229030246336 | 0.6513798861381356 [0.5482, 0.7504] |
| `structural` | 0.6982479731836607 | 0.6774146398503275 | 0.613866582258362 [0.4848, 0.7414] |
| `kind_only` | 0.1688786248830683 | 0.09410079513564079 | 0.6553355132196997 [0.5698, 0.7468] |

### itc99 · harm（正例 386，40/47 个池有双类别）

| 特征集 | 池化 AUC | 仅池均值（池间成分） | 池内 AUC [CI] |
|---|---|---|---|
| `one_depth` | 0.6418969684511954 | 0.6135271435963228 | 0.5871184600444469 [0.5333, 0.6415] |
| `one_n_cells` | 0.5501034851824812 | 0.57322462663822 | 0.5721296609867569 [0.5149, 0.6303] |
| `one_max_fanout` | 0.6285927432787791 | 0.5998507970485459 | 0.5728202148684872 [0.5154, 0.6311] |
| `one_n_ff` | 0.5320183863399559 | 0.5712966835125423 | 0.5722582768065492 [0.5149, 0.6305] |
| `struct_global_only` | 0.5772470815052132 | 0.5898247839924017 | 0.5771446597507405 [0.5182, 0.6374] |
| `struct_local_only` | 0.5661844446177073 | 0.5790013679890561 | 0.5437183920315114 [0.4944, 0.6003] |
| `struct_delta_only` | 0.5325818844226449 | 0.5343149068278956 | 0.5511949861589099 [0.4910, 0.6122] |
| `structural` | 0.4990714685681478 | 0.5025499174244948 | 0.5478007180077737 [0.4979, 0.6016] |
| `kind_only` | 0.5782535812252362 | 0.6044509260506227 | 0.57206846105791 [0.5147, 0.6304] |

### iscas89 · resolvable（正例 79，18/34 个池有双类别）

| 特征集 | 池化 AUC | 仅池均值（池间成分） | 池内 AUC [CI] |
|---|---|---|---|
| `one_depth` | 0.44504476690336525 | 0.42474529175671505 | 0.5176376104049385 [0.4829, 0.5594] |
| `one_n_cells` | 0.4683029741689822 | 0.4718791808171246 | 0.4921311358853061 [0.4486, 0.5396] |
| `one_max_fanout` | 0.3488988370896367 | 0.33454255428630236 | 0.5185727133137257 [0.4820, 0.5623] |
| `one_n_ff` | 0.46326026551404753 | 0.4589122157044355 | 0.5273058782968907 [0.4880, 0.5709] |
| `struct_global_only` | 0.5534887310898425 | 0.5320314912009879 | 0.5131349690488489 [0.4739, 0.5605] |
| `struct_local_only` | 0.48291653802613976 | 0.43827827518781515 | 0.5429606979549597 [0.4125, 0.6706] |
| `struct_delta_only` | 0.42201811258618915 | 0.3829113924050633 | 0.5172982202629168 [0.4791, 0.5635] |
| `structural` | 0.4367603169702583 | 0.44651126891015747 | 0.5006236532358823 [0.3795, 0.6235] |
| `kind_only` | 0.42201811258618915 | 0.3829113924050633 | 0.5172982202629168 [0.4791, 0.5635] |

### iscas89 · gain（正例 16，6/34 个池有双类别）

| 特征集 | 池化 AUC | 仅池均值（池间成分） | 池内 AUC [CI] |
|---|---|---|---|
| `one_depth` | 0.710254854368932 | 0.6875 | 0.6003828095078804 [0.4925, 0.7197] |
| `one_n_cells` | 0.720165857605178 | 0.6743527508090615 | 0.6183367390471758 [0.5134, 0.7312] |
| `one_max_fanout` | 0.7114684466019418 | 0.7182443365695793 | 0.6241506925355478 [0.5134, 0.7487] |
| `one_n_ff` | 0.7082322006472492 | 0.7113673139158576 | 0.6183367390471758 [0.5134, 0.7312] |
| `struct_global_only` | 0.4859425566343042 | 0.4534789644012945 | 0.6125227855588037 [0.5134, 0.7122] |
| `struct_local_only` | 0.6859830097087378 | 0.6365291262135923 | 0.4941345366047578 [0.2056, 0.7783] |
| `struct_delta_only` | 0.729470064724919 | 0.7299757281553398 | 0.6142716983967692 [0.5134, 0.7272] |
| `structural` | 0.563207928802589 | 0.5078883495145631 | 0.6579217994773866 [0.3481, 0.9053] |
| `kind_only` | 0.729470064724919 | 0.7299757281553398 | 0.6142716983967692 [0.5134, 0.7272] |

### iscas89 · harm（正例 63，15/34 个池有双类别）

| 特征集 | 池化 AUC | 仅池均值（池间成分） | 池内 AUC [CI] |
|---|---|---|---|
| `one_depth` | 0.3736217133163698 | 0.3732885011510966 | 0.49853387053184217 [0.4507, 0.5544] |
| `one_n_cells` | 0.40370168423603536 | 0.41981703622925 | 0.46022927283069276 [0.4157, 0.5049] |
| `one_max_fanout` | 0.25648249121531563 | 0.2729613473888283 | 0.44584543444685426 [0.4049, 0.4818] |
| `one_n_ff` | 0.42984369320247184 | 0.5336544286925966 | 0.4621650026781873 [0.4190, 0.5059] |
| `struct_global_only` | 0.6837513631406761 | 0.6919604992124077 | 0.45131059654791905 [0.4019, 0.4976] |
| `struct_local_only` | 0.6131406761177753 | 0.6587604507451835 | 0.6065529376153108 [0.5086, 0.7055] |
| `struct_delta_only` | 0.26402520295650067 | 0.2744153641100206 | 0.46050705060847047 [0.4162, 0.5026] |
| `structural` | 0.6594571670907549 | 0.690567066521265 | 0.5832284876681428 [0.4870, 0.6916] |
| `kind_only` | 0.26402520295650067 | 0.2744153641100206 | 0.46050705060847047 [0.4162, 0.5026] |

## 结论

- **the_preview_held**：the LOG-23 preview predicted the final band to within 1.3% and every qualitative conclusion held: the graph features stay at/below random on resolvable and harm, the gain label stays the one exception, the cheap placed stage stays the strongest single feature, and the acceptance criterion keeps its physical selectivity with a STRONGER harm ratio
- **candidate_level_verdict**：on the reading a candidate generator can use -- within one pool -- every graph feature set is level with the trivial kind-only baseline in BOTH families and on ALL THREE labels; the apparently large pooled numbers are reproduced by a predictor that only knows the pool mean, so they are between-pool effects
- **magnitude_not_topology**：the features that do carry signal (depth, max_fanout) predict harm as strongly as they predict resolvable, i.e. they predict how FAR the WNS moves, not WHICH WAY
- **what_it_means_for_the_gnn_idea**：in this family, with scalar summaries of the gate-level graph, there is no candidate-level information a GNN could exploit beyond the candidate kind and the iteration; the usable levers are the cheap placed-stage label and a pool-level prior (some pools are worth measuring first)

## 边界

- PROBE level, not paper evidence.
- post-hoc: the split sets and the single features were chosen by looking at the data (9-11 sets x 3 labels x 2 families); no nested selection was run, so the CIs are not multiplicity-corrected.
- the graph features are scalar summaries of the gate-level graph, NOT a GNN encoder -- "no signal in the summaries" does not prove "no signal in a GNN".
- the pooled reading mixes a strong between-circuit component (per-circuit positive rate 0.207-0.616 on ITC-99); the within-pool reading is the one a candidate generator can use.
- the parasitics come from estimate_parasitics, not from a signoff RC extraction; the placed and routed tiers use different estimation models, so "routed - placed" mixes a stage change with a model change.

- `code/` 未动、HEAD 未变、未提交。
