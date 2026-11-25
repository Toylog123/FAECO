# UART 布线前 hold 风险预筛

2026-11-25。用已有实际布线的 UART 端点作开发诊断。候选预估面积相同的 `_0562_` 和 `_0886_` 在寄生交换中显示不同 SS hold 判定。本轮先检验事前可获得的几何是否具备可迁移的分辨力。 [寄生交换报告](UART_DEFERRED_RESERVATION_REPORT.md)

## 运行前规约

取冻结 UART 起点的 DEF、SPEF、网表、SDC 和三角 Liberty。每角取 OpenSTA 各路径组前四条最小延时路径，每端点一条，按原时序约束另对已有两门合格前缀提取同样的路径。几何一律用实际候选重布线的共同冻结起点。拟重布范围用候选动作的直接信号网。先保存冻结池及所有路径的网级评分，再读取物理候选结果。

同层平行线段的正重叠长度除以轨距，再除以 `1 + 间距/轨距`，累计距离不超过三轨的贡献。主分数取触达网与各敏感路径时钟网的重叠贡献，逐路径取最大。另记同公式的全路径和数据网得分、现行触达网总电容，以及面积和动作数。分数高表示更可能出现 hold 回退。近距或高耦合仅表明与重布敏感网相邻，尚无确定的时序变化方向。

实布验收分别取 UART 原三法、去重 ABBA、末次预留六臂和已验收等面积定向探针。按同一累计动作和去日期物理指纹合并跨臂重复。定向探针单列，未齐全三角 STA 的候选单列。标签沿用原各角绝对及相对 hold 门，另报三角原有联合验收。

几何规则进入独立设计的条件是两门起点上 `_0562_` 的时钟风险分数高于 `_0886_`，正式池 SS AUC 至少 0.65，剔除两个已知对照后 SS AUC 大于 0.5 且至少三个通过和三个拒收。其余分数用于解释误判；同分赋半分。耗时用同后端的 RAW 时钟分记。该轮只降低不具分辨力的方向的优先级，生产策略和门限沿用。

## UART 实测分辨力

两个已验收起点合计 6 次 STA，各角各取 8 条路径。全部 18 个候选涉及的 54 条直接信号网均有平面线段，生成特征耗时 7.941 RAW s。独立验收原件累计 96 条正式物理记录，去重后剩 18 个正式端点，三角齐全。另有一个已有的定向合格端点。先落盘特征，随后才读取验收标签。 [特征与路径](UART_HOLD_GEOMETRY_SCORES.json) · [结果与原件绑定](UART_HOLD_GEOMETRY_RESULTS.json)

| SS 对照范围 | hold 拒收 / 通过 | 时钟几何 AUC | 直接电容 AUC | 数据几何 AUC |
|---|---:|---:|---:|---:|
| 全部正式实布端点 | 8 / 10 | 0.9125 | 0.7625 | 0.9000 |
| 去掉已知关键对照 | 7 / 10 | 0.9143 | 0.7714 | 0.9286 |

已知合格 `_0886_` 是额外定向原件，未进入两行正式统计。移除该对照时正式组实际只移除 `_0562_`。固定批宽后，单门的四个跨类对与三门的十二个跨类对，时钟分数均完整排序，直接电容分别正确 3 对和 10 对。其余批宽没有同组的通过与拒收。TT 只有 2 处 hold 拒收，动作数本身已把这两处与其余端点分开。FF 无 hold 拒收。 [候选明细](UART_HOLD_GEOMETRY_RESULTS.json) · [同宽与末次前沿复核](UART_HOLD_GEOMETRY_FRONTIER.json)

## 两序末次候选的选择

用实际前五次请求、同臂已验收集合和原候选排除规则，重建之前两臂的第六次派发资格。两序均有三项同面积动作，预估各回收 0.08748 µm²。采用面积优先，再取各角时钟几何风险最大值较低的候选，最后沿用直接电容与原池顺序打破同分。

| 追加动作 | 时钟几何风险 | 同两门前缀下的已有实布验收 |
|---|---:|---|
| `_0886_` | 0.000000 | 全门通过，累计回收 0.23328 µm² |
| `_0562_` | 0.832578 | SS 相对 hold 拒收 |
| `_0601_` | 3.268821 | 暂无真实标签 |

两臂历史电容顺序均选 `_0562_`，若在同一个决策点用几何风险重排则均会选 `_0886_`。合格结果来自原定向验收。本阶段通过筛选规则的开发入围门，线上耗时和与固定批次的正式胜负尚待同预算验证。 [双序前沿](UART_HOLD_GEOMETRY_FRONTIER.json)

## SKY130HD GCD 冻结转移

沿用 UART 的规则和参数，以历史 GCD 的共同物理后端、冻结 18 项候选池和原 SDC 做跨设计跨工艺检验。评分阶段使用冻结布线上的 64 条触达网和每角 8 条最小路径，3 次参照 STA 及特征耗时 2.525 RAW s。12 条实际物理记录合并为 9 个端点，评分后才读取标签。该历史 GCD 已用于其他调度实验，本轮仍使用同一历史后端比较，未把后来开启保护布线的 GCD 端点混入。 [冻结特征](../tcad_ibex_20261123/GCD_HOLD_GEOMETRY_SCORES.json) · [端点与原标签](../tcad_ibex_20261123/GCD_HOLD_GEOMETRY_RESULTS.json)

TT/SS 各为 6 拒、3 过。时钟几何在两角的 AUC 均为 0.7500，18 个跨类对里正确 9 对、同分 9 对。直接电容的 AUC 为 0.5556。三个非零分都是拒收端点，六个零分端点中通过和拒收各三个。共享 `_089_/_090_` 的两组三门实布面积均减少 11.2608 µm²，其中加 `_091_` 的组合因 TT/SS 相对 hold 拒收，加 `_093_` 的组合通过。两者时钟几何均为 0，数据几何同分。各自独有的三条触达网在采样路径上的分数都是 0，两组实际布线均在冻结布局的 `clk` 和 `clknet_0_clk` 上出现几何变化。 [GCD 转移原件](../tcad_ibex_20261123/GCD_HOLD_GEOMETRY_RESULTS.json)

在 GCD 的 5 个等面积跨类对上，几何正确 2 对、同分 3 对，AUC 0.70。几何同分时回到电容排序后 AUC 为 0.80，与只按电容排序相同。对全部 GCD 组合这样打破同分，AUC 由 0.7500 降到 0.7222。UART 正式池 10 个等面积 SS 跨类对中，三种排序的 AUC 均为 0.70。 [等面积与同分复核](HOLD_GEOMETRY_TIEBREAK_RESULTS.json)

## GCD 同分的实布归因

对以上等面积的两组实布网表和 SPEF 做 TT/SS 双向交换。8 次 STA 共 4.577 RAW s，每角四组的最差路径及 SPEF 标注数均保持一致。TT 最差路径为 `reset` 到 `ctrl.state.out[1]`，SS 为 `resp_rdy` 到 `ctrl.state.out[0]`。每组 5 个驱动未标注、0 个驱动部分标注。

| 角 | 实布通过端点 hold WNS（ps） | 只换拒收端点网表（ps） | 只换拒收端点 SPEF（ps） | 实布拒收端点（ps） |
|---|---:|---:|---:|---:|
| TT | 430.889630 | 430.889630 | 430.392555 | 430.392555 |
| SS | 343.843010 | 343.843010 | 341.973116 | 341.973116 |

仅交换 SPEF 分别重现 −0.497075 ps 和 −1.869893 ps 的实际 hold 差，超出原相对门；仅交换网表的变化为 0。这一对的风险来自原冻结直接网几何分数没有捕捉到的实布寄生。归因范围限于这两角和这对候选。 [八组交换](../tcad_ibex_20261123/GCD_HOLD_GEOMETRY_EXCHANGE.json)

## 判断与后续

几何分数有开发池的排序价值，但关键等面积决策的跨设计结果未达到预期。单独使用几何分数、用电容打破同分均未在 GCD 等面积组上提供额外收益。本轮保留原去重派发与原验收门，暂缓新增在线对照。后续先在等面积同分候选上比较限域试布线加增量寄生预估能否看见时钟支路变化，并对比这项预筛耗时与省下的完整 DRT/RCX 时间。先用不同候选验证区分力与净开销，再进入和去重、固定批次共用物理后端的等预算对照。

## 复现

原始 Tcl、STA 日志、流水和收据存档于 `scratch/tcad_ibex_20261123/uart_hold_geometry_20261125_v1.tar.gz` 与 `scratch/tcad_ibex_20261123/gcd_hold_geometry_20261125_v1.tar.gz`，均已与原件比对。两包 SHA-256 分别为 `bdbc52222882d301e2766c57b09735dcff51475212577c3ab42ea98f9f21ff6a` 和 `d9875c82b697bea8a6bd52cd3d2bec6e6c47c4ad80d10fdc760571f310f0a8ba`。

```bash
h=project_docs/evidence/tcad_holdout_20261123
r=/home/toylog
out=$r/faeco_tcad_uart_hold_geometry_reproduction
bash code/scripts/run_with_timeout.sh 320 taskset -c 0-5 python3 -B "$h/probe_uart_hold_geometry.py" score "$out" --runs \
  "$r/faeco_tcad_uart_online_20261125_matrix_v2" "$r/faeco_tcad_uart_dedup_20261125_v1" \
  "$r/faeco_tcad_uart_deferred_reservation_20261125_v1" "$r/faeco_tcad_uart_fixed_area_probe_20261125_v1"
sha256sum "$out/scores.json"
bash code/scripts/run_with_timeout.sh 120 taskset -c 0-5 python3 -B "$h/probe_uart_hold_geometry.py" evaluate "$out"
bash code/scripts/run_with_timeout.sh 60 taskset -c 0-5 python3 -B "$h/replay_uart_geometry_tail.py" "$out"
i=project_docs/evidence/tcad_ibex_20261123
g=$r/faeco_tcad_sky_holdout_20261123
transfer=$g/gcd_hold_geometry_transfer_reproduction
swap=$g/gcd_hold_geometry_exchange_reproduction
bash code/scripts/run_with_timeout.sh 180 taskset -c 0-5 python3 -B "$i/probe_gcd_hold_geometry_transfer.py" score "$transfer" \
  --seed "$g/gcd_incident_cap_pair_20261124_v1"
bash code/scripts/run_with_timeout.sh 120 taskset -c 0-5 python3 -B "$i/probe_gcd_hold_geometry_transfer.py" evaluate "$transfer"
bash code/scripts/run_with_timeout.sh 400 taskset -c 0-5 python3 -B "$i/probe_gcd_geometry_tie.py" "$transfer" "$swap"
python3 -B "$h/compare_hold_geometry_ties.py" "$out/results.json" "$transfer/results.json" "$swap/score_tiebreak.json"
```
