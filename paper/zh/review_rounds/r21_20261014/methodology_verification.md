# r21 方法审稿独立复核

日期：2026-10-14。受检稿件 SHA256：`8c5bc422e3e01c034563a16deac1448030fe093c1d45a846b88c435ef25d18d5`。检查当前 tex、`review_r21_figures.py`、族 D 冻结运行 revision `6276cff` 的 `flow.py/real_wns.py`，并只读重算全部 40 个族 D 运行的原始 trials。未运行新 EDA，未修改稿件或其他文档。

**结论：原 M1/M2/M4 的主要修正已到位；图 5 和 runtime 表仍存在一个需要修正的确定计数错误。当前不能通过“实际 STA 测量开销”口径的复核。**

## 已通过的修正

| 原意见 | 核查结果 |
|---|---|
| M1：族 C 与加权割机制解绑 | §4.4 第一组明确历史关键实例枚举运行器、不调用式 (2)、轮内逐实例提交；混合有 JOINT、随机无 JOINT；承认候选构造与顺序的联合作用，未声称权重独立增益。主要归因问题已处理。 |
| M2：历史结果可复现性 | §4.1 明确 A/B 历史运行 revision 未完整钉定及部分电路重跑漂移，D/F 有独立版本配置。主要 provenance 缺口已处理。 |
| M3：轮数与预算 | C 已写实际 STA 消耗不同，D 已改成预约上限 500；跨族曲线/终点不混用。但 D 的“实际测量”定义仍错误，见下。 |
| M4：物理相关性 | §4.5 首句改为考察收益保持；图 6 全八电路，包含 s420、s953 退化和 s832 持平。描述性后验口径合适。 |
| b17 分布/主结果区别 | F1–F6 表注明默认 60 s 的 785 trials，而主结果用 180 s 的 104。避免把 4044 与 3363 说成同一配置的计数。 |
| S 负结果 | 图 7 用同一批候选的两种分类展示 76 变浅、0 改善、90 下降，并将 s641 标为无窗口/零候选。未把两种分类相加或把 126 候选当成独立电路。 |

## V1（Major，已证实）：图 5 的 k 含缓存复用，不能叫实际 STA 测量序号

**定位：** §4.4 第二组 B(k) 定义与解释、`fig:budget_curves` 图注/横轴、`tab:runtime` 的“STA 次数”及其表注；`paper/zh/figures/data/scripts/review_r21_figures.py → budget_curves()`。

**代码原因：**

- 族 D 的 `flow.py @ 6276cff` 以 `sta_provenance in trial && wns != None` 构造 `best_wns_curve`。
- 同 revision 的 `real_wns.py` 在 `_sta_cache` 命中时复制缓存字典，并加 `skipped_duplicate=True`。复制字典保留了旧的 `sta_provenance`，随后仍写入 trials。
- 因此 provenance 筛选排除了部分前置拒绝，却**没有排除缓存结果**；一个曲线点不必对应一次新的 OpenSTA 执行。
- 当前制图脚本直接取 `best_wns_curve`，横轴 `1..len(curve)`，没有排除这类记录。

**原始台账验证：** 对 `experiments/20260924_threearm/{fixed,adaptive,random_s1,random_s2,random_s3}/{8电路}/eval_trials.json` 共 40 运行重算：按现有 provenance 规则生成的 40 条曲线与归档值逐点一致；这些记录合计含 **13233 条 skipped_duplicate 缓存复用**。每个运行剔除缓存后的记录数，也等于该运行独有 STA report_path 数和 state.budget.sta_used 数。

| 运行 | 归档曲线记录数 | 缓存复用数 | 新 STA 测量数 |
|---|---:|---:|---:|
| fixed/s641 | 558 | 239 | 319 |
| adaptive/s641 | 842 | 514 | 328 |
| fixed/s832 | 300 | 143 | 157 |
| adaptive/s832 | 370 | 213 | 157 |

这意味着 s832 的两臂虽然归档曲线长为 300/370，但新 STA 消耗相同，都是 157；用当前图的终止横坐标解释测量开销会产生错误结论。

**所有八电路合计（区分全部 trials 与带来源的曲线记录）：**

| 臂 | 全部 trials（现 runtime 表口径） | 带 STA 来源的归档曲线记录 | 其中缓存复用 | 新 STA 测量数 |
|---|---:|---:|---:|---:|
| Fixed | 4146 | 3949 | 2002 | 1947 |
| Adaptive | 4883 | 4686 | 2683 | 2003 |
| Random seed 1 | 5356 | 5167 | 2728 | 2439 |
| Random seed 2 | 5516 | 5180 | 2704 | 2476 |
| Random seed 3 | 6000 | 5643 | 3116 | 2527 |
| Random 三种子均值 | 5624 | 5330 | 2849.3 | 2480.7 |

当前 runtime 表的数值能由全部 trials 重现，不能把这些原始数字判为造假；错误是将该字段称为实际 STA 测量次数。全部 trials 还包含无 STA provenance 的前置拒绝。制图使用的归档曲线不含这些前置拒绝，但仍含缓存。因此需要同时修正图 5 和 runtime 表的字段口径。

**无需新 EDA 的修法（二选一，语义需全文一致）：**

1. 保留归档曲线和历史记录数，将图的 k 改为“带 STA 来源的候选评估记录序号（含缓存复用）”，runtime 相应列改为“全部候选评估记录数（含缓存与前置拒绝）”，停止用它们解释实际 OpenSTA 测量成本。
2. 从原始 trials 中筛选 `sta_provenance`、有效 wns、`not skipped_duplicate`，重新构造实际测量 B(k)，按末列更新成本。原始归档数据不改，派生图/CSV注明新筛选规则，墙钟 runtime 原值可保留。该口径下，族 D 的新测量数与 500 上限实际一致。

## V2（Minor，已证实）：图 5 隐去归档 B(k) 的负值

`budget_curves()` 在曲线前补 `(0,0)`，同时设置 y 轴下界为零。归档累计最佳只在候选记录中取最大值，并未把“保留原网表”的零收益选项纳入：s382/fixed、s713/fixed 等早期曲线包含 -0.01 ns。图中负段因此被裁去，而且新增起点到首个负点会下降。建议若 B(k) 表示可保留的最优修复收益，则在重建曲线时采用 `max(0, cumulative_max(delta))`，同时注明零值含不修改基线；若保留原始“最佳已评估候选”定义，则显示负 y 范围，不额外引入会改变单调性的零起点。

## 保留的边界

当前修订没有补 cost 消融或物理模型标定，应继续保留已写明的证据范围。原报告中的 b06 电容归因、排除清单、C 全部 flags 的恢复属于待核实/补充材料项，本复核不把它们升级为新的已证实错误。除 V1 的计数语义与 V2 的曲线显示外，没有在本次五分钟复核中发现新的确定数值矛盾。

## 重建 schema 与增益规则（后续独立审查补注）

使用 `outerloop_result.json.baseline_wns` 作为整次运行的初始基线，禁止用变化中的 `acceptance_evidence.metric_references.setup_wns` 或 `state.current_wns` 重锚。原始 trials 按存储顺序筛选：存在 OpenSTA `sta_provenance`、`wns` 为有限数值、`skipped_duplicate` 非 true。每保留一条，实际 k 加一；单点收益是 `wns-baseline_wns`，可保留网表的 B(k) 是 `max(0, 到当前为止所有实测收益)`。测了但没有接受的候选也应消耗 k；B(k) 表示观察到的收益而不是已提交链。

缓存记录不新增实际 k；只有当前缓存结果的原始测量已在本运行更早出现并贡献同一收益时才可以安全跳过。本次 40 运行通过 cache_key/报告路径/wns 交叉检查，实际测量 report_path 唯一，且缓存值均可追溯到本运行更早实测。辅助审计脚本：`paper/zh/review_rounds/r21_20261014/verify_sta_ledger.py`。脚本只读原始文件并输出审计 JSON，不改归档或绘图生成器。

fixed/s641 的第一条实测样例：`iteration=1`、`instance=_091_`、`kind=G`、`accepted=true`、无 skipped_duplicate 标记、`wns=-1.42`、初始 baseline_wns=-1.63，所以 k=1 的 gain/B 都为 +0.21 ns。其 `sta_provenance.tool=OpenSTA`，报告为 `experiments/20260924_threearm/fixed/s641/eval/iter001_cand001/000__091__G/sta.log`；已实际打开报告末尾，`worst slack max -1.42` 与台账一致，TNS=-18.29、hold min slack=0.44。`run_config.json` 绑定 revision `6276cff54310e2078106ec3cef3255034f67d9ed`、workers=1、sta_budget=500。审计辅助函数已实际运行，40/40 通过，exit=0。
