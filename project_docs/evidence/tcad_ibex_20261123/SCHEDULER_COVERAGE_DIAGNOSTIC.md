# 六次物理预算下的拆分覆盖诊断

基于 `fa25f608` 已运行的筛选池和物理收据。三个 SKY130HD 设计采用各自冻结的 CONTROL、原始 SDC、三角验收门、18 个有序候选、每组三门和六次物理评估上限。ASAP7 校验使用两组已有的反序串行实测，每臂达到 0.01% 功能面积目标即停。各设计沿用各自原有门限。 [筛选矩阵](SCREEN_ABLATION_REPORT.md) · [ASAP7 串行实测](ASAP7_SERIAL_REPORT.md)

## 物理评估覆盖

三个 SKY130HD 设计的筛选 FAECO 都实际尝试了 `{1,2,3} → {1} → {2,3} → {2} → {3} → {4}`。数字是筛选池内从 1 开始的排序位置。首批被拒后，递归消耗了四次评估，最后一槽按现行规则只尝试一门，总共覆盖四个不同实例。Ibex 六次均只触发 SS 相对 hold。GCD 第 1、3、5 次同时触发三角相对 hold 和 FF TNS，其余三次只触发 TT/SS 相对 hold。AES 六次均只触发 SS 相对 hold。

根因可追到调用链。矩阵从 `run_screened_matrix.py` 经 `run_setup_budget_sweep.run_arm`、`compare_ibex.run_method` 调用 `adaptive_batch_recovery`。评估端记录逐视图拒收原因并向策略返回端点可行性。策略对任何未接受的多门组合立即左、右递归，再继续排序池，末次顶层派发保留单门。三个设计均在首批递归里用掉前五次。 [矩阵入口](run_screened_matrix.py#L144) · [评估入口](run_setup_budget_sweep.py#L214) · [调度分派](compare_ibex.py#L413) · [递归与末次规则](../../../code/src/rseco/physical_budget_adapter.py#L231)

## 原收据回放

先用原递归规则复算调度，再检验一种延迟拆分规则。若一次拒收包含任一视图的 `hold_regression`，本次跳过其子集，继续测试池中下一个整批。其余拒收继续用原递归规则。保留六次上限、最后一槽单门和原接受条件。候选键由已接受动作加本次动作组成，查询时按完整动作 ID 排序。收据只在同一设计、同一 CONTROL 与门限下匹配完整元组。若遇到从未测过的元组，回放停在该处。

对三个矩阵读了全部 54 份新排序候选收据，对 ASAP7 两组读了 12 份候选收据。检查了每次的 CONTROL SDC 哈希、scope、DRT/RCX 完成标记、DRC 和三视图。重复元组的 ODB、DEF、Verilog 哈希和逐视图 WNS、TNS、hold 一致。凡接受的端点均交叉检查了 SEC 证明点数量、gold 与 gate 哈希和 gate 实际字节。两种调度的五条回放各自均匹配到全部元组。下表是用同一验收门重放的顺序与已实测物理端点。所有面积均以各自 CONTROL 功能面积为参照。

| 设计 | 延迟收据回放的首次达标 | 六次上限内最佳合格面积减量 | 原实测固定臂首达时间，含筛选 |
|---|---|---:|---:|
| SKY130HD Ibex | 第 3 次 `{7,8,9}`，22.5216，SEC 13648/0，见 `screened/fixed/03` | 62.56，第 5 次累计 `{7…15}`，SEC 13648/0 | 562.523 RAW s |
| SKY130HD GCD | 第 5 次 `{13,14,15}`，11.2608，SEC 262/0，见 `screened/fixed/05` | 11.2608 | 146.249 RAW s |
| SKY130HD AES | 未达标。五个整批和最后单门均触发相对 hold | 0 | 未达标 |
| ASAP7 Ibex，两组串行 | 第 3 次 `{2,3}`，0.26244，SEC 17363/0，见两组各自的 `faeco/03` | 0.26244，按目标停止 | — |

SKY130HD 三条延迟回放与各自固定批次的六个实测元组逐项相同。Ibex 第 4 次的累计面积减量为 43.792，实测固定批次做到该端点已花 730.236 RAW s，超出 720 s 窗口。GCD 的前三个后续整批中，`{4,5,6}`、`{7,8,9}` 和 `{10,11,12}` 均仅触发 TT/SS 相对 hold。AES 至少有两组不同的三门组合各实际减了 33.7824，分别触发 SS 与 TT/FF 相对 hold。所有新排序候选均只触发相对 hold 门，因而未进入正式 SEC。 [Ibex 收据](SCREEN_MATRIX_IBEX_RESULTS.json) · [GCD 收据](SCREEN_MATRIX_GCD_RESULTS.json) · [AES 收据](SCREEN_MATRIX_AES_RESULTS.json)

ASAP7 两组首批及其左侧单门失败原因均为 TT/SS WNS 和 FF/TT/SS TNS，无相对 hold 触发，因而保留原轨迹 `{1,2,3} → {1} → {2,3}`。原六次主比较中固定批次实测回收为 0。串行复跑中单门和 FAECO 各用了三次 DRT/RCX，FAECO 比单门少执行一次中间端点 SEC，观测缩短 35.195–40.311 WSL monotonic s。两组最后端点均按原有 tradeoff 门允许的 FF setup 跨零交付，新增 15 个负 setup 端点。 [原主比较](REPORT.md#asap7-主比较) · [反序原始结果](ASAP7_SERIAL_RESULTS.json)

## 归因

Ibex、GCD 的零收益包含明确的覆盖损失。原拆分耗尽预算前没到达实测已经通过的低位整批，延迟拆分的回放能覆盖这些端点。AES 已有固定臂覆盖第 1–16 项，正式收益仍为零，当前证据指向相对 hold 验收。另有 Ibex 原 FAECO 第三次的 17.5168 减量，在历史零编辑重布线的 hold 参照下做了诊断 SEC 13648/0。该记录说明参照会影响已测端点的判定，正式主档仍以原冻结 CONTROL 为准。 [Ibex 诊断 SEC](SKY130_SCREEN_FAECO_HOLD_SEC.json)

延迟规则是看过收据后提出的诊断假设。它在三条 SKY130HD 轨迹上重现固定批次，在已观测的两条 ASAP7 轨迹上保留首批拆分。未测的子集、改变起点或验收门后的轨迹，以及新策略的运行时间仍未知。本轮没有新增 DRT、STA 或 SEC。若验证该规则的泛化，应冻结触发定义，在未用于本诊断的设计上沿用同池同门，对比固定批次和原 FAECO 的同面积目标与同时间结果。
