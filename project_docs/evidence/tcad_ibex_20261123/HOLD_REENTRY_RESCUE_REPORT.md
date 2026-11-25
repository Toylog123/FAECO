# 完整布线 hold 拒收后的检查点重入补救

2026-11-25。上一轮 GCD 检查点重入在同面积有合格替代时未节省总耗时。本轮只处理已有实布证据显示因相对 hold 失败、预估回收超过同一冻结池所有已验收端点的候选。历史合格上限指已实际评估的台账。 [上一轮配对](GCD_LOCAL_ROUTE_REENTRY_REPORT.md)

## 运行前冻结

| 设计 | 原始台账提案 | 拟回收（µm²） | 已验收上限（µm²） | 历史独立拒因 |
|---|---|---:|---:|---|
| SKY130HD GCD | `screened/fixed/02` 三门 | 18.7680 | 15.0144 | TT、SS 相对 hold |
| ASAP7 UART | `cell_02/fixed_online/01` 三门 | 0.26244 | 0.23328 | SS 相对 hold |
| ASAP7 UART | `cell_02/fixed_online/04` 六门 | 0.34992 | 0.23328 | TT、SS 相对 hold |
| ASAP7 UART | `cell_02/fixed_online/05` 六门 | 0.34992 | 0.23328 | TT、SS 相对 hold |

GCD 合格上限按同后端原固定与 FAECO 两臂合计。UART 核对原在线矩阵、去重、末次预留和等面积定向验收。排除已知有同面积合格解的 GCD `_091_`，以及有其它时序或物理拒因的历史对象。完整候选 ID、历史逻辑及物理收据和合格基线均写入运行协议。

同一机器按 GCD、UART 串行。GCD 原 CPU 6–11，UART 原 CPU 0–5，均用四个 DRT 线程。先从同一冻起点新跑待补救候选的原完整后端，复现仅 hold 拒收才派发重入。重入从同一冻起点生成两轮限域 ODB，清洁进程加载该 ODB、解除保护编码、跳过第二次 pin access 并完成 DRT。GCD 沿用直连、参考时钟和至多 20 条几何邻网的范围。UART 沿用各候选原直接网与已登记释放网范围，再在第二进程解除保护以尝试替代布线。每条补救链的两段 DRT 共用 100 秒超时。最终完整验收使用原 I/O、FF/TT/SS 的 setup、hold、电气、独立 DRC、天线和 SEC。成功端点再以同配方重入一次作复现确认。

追加时间从从头候选被拒后开始，含两段路由、状态保存和解锁、RCX、逐角 STA、电气、独立 DRC、天线，以及通过时的 SEC。所有失败尝试也计入；备用的重复成功确认另记。实验代码还可能为时序拒收但有完整终态的候选运行诊断 SEC，其费用另列。终态合格面积与高于历史前沿的新增面积分开。同设计的多个候选共享动作及冻起点，净回收取最大，分别列出全部补救费用。

## 两段补救结果

四次新鲜完整布线均复现原来的纯 hold 拒收。四次补救也都完成实际 DRT、RCX 和三角 STA，独立全块 DRC 和天线均为零。四个补救物理网表均完成 SEC，GCD 为 262/0，UART 为 567/0。最终只有 UART 三门通过全部原门。

| 候选 | 新鲜从头（RAW s） | 触发后追加（RAW s） | 补救后原门 | 合格回收（µm²） | 超过原最佳（µm²） |
|---|---:|---:|---|---:|---:|
| GCD 三门 | 12.711 | 35.227 | TT、SS 拒收 | — | 0 |
| UART 三门 `01` | 28.852 | 38.101 | 通过 | 0.26244 | 0.02916 |
| UART 六门 `04` | 28.868 | 36.618 | TT 拒收 | — | 0 |
| UART 六门 `05` | 28.376 | 36.645 | TT 拒收 | — | 0 |

UART 的三次触发合计追加 111.364 秒，GCD 加 UART 共 146.591 秒。UART 成功候选从触发所需的完整尝试到补救验收总用 66.952 秒。另花 37.786 秒独立确认一次，复现了最终 ODB、DEF、网表、去日期 SPEF 与逐角时序。表中失败项的时间按原门拒收后不展开诊断 SEC 的计法。 [GCD 原件](GCD_HOLD_REENTRY_RESCUE_RESULTS.json) · [UART 原件](../tcad_holdout_20261123/UART_HOLD_REENTRY_RESCUE_RESULTS.json)

## 补救方向和失败位置

GCD 重入从 9 个检查点标记进入第 3 轮，布线完成。与从头相比，功能网表不变，实际规范几何改了 8 条网，含 `clknet_0_clk`。该网总提取电容为 13.3128→14.7743 fF，原 TT/SS 最差路径身份保持，hold 分别再下降 2.614908／11.468937 ps。这里比较的是原布线与先限域再解锁的两条链路。 [GCD 实测收据](GCD_HOLD_REENTRY_RESCUE_RESULTS.json)

UART 重入三次只改变 `_0429_`、`clk`、`clknet_0_clk` 的最终几何，功能网表保持。三门的 SS WNS 从 54.038593 ps 升至 54.066501 ps，越过 54.051915 ps 原门。SS 最差路径保持 `rxd` 到 `uart_rx_inst.rxd_reg/D`，数据到达在报告精度下相同，捕获时钟略提前。两个六门的 SS 分别改善 0.221212／0.221226 ps，TT 却仍分别低于同一原门 0.001547／0.000422 ps。该范围对这两组残余 TT 违例没有足够作用。 [UART 原件](../tcad_holdout_20261123/UART_HOLD_REENTRY_RESCUE_RESULTS.json)

## 复用已被原门拒绝的 ODB

逐字节核对发现，UART 三次原完整布线的预提取 ODB 与重做限域后保存的检查点分别完全相同，且三个检查点均无 DRC 标记。补测只从已被拒的原 ODB 在新进程解锁和重入，跳过重新生成检查点的第一段。仍完整测量触发后的原门、独立全块 DRC、天线及 SEC，并对比最终实物与两段补救的身份。补测使用同样三项，GCD 第一阶段采用较窄的另一路由窗口，未纳入 ODB 复用配对。

| UART 候选 | 两段补救追加（RAW s） | 复用原 ODB 追加（RAW s） | 实测少用（s） | 原门结果 |
|---|---:|---:|---:|---|
| `01` | 38.101 | 35.817 | 2.284 | 通过，回收 0.26244 µm² |
| `04` | 36.618 | 33.790 | 2.828 | TT 拒收 |
| `05` | 36.645 | 33.028 | 3.617 | TT 拒收 |
| 三项合计 | 111.364 | 102.635 | 8.729 | 1 项通过 |

三项的最终 ODB、DEF、网表、去日期 SPEF、三角时序、独立 DRC/天线及 SEC 结果均与两段补救一致，且没有重复 pin access。两批在同机串行的不同时段执行，表中的差值按实际观测报告。以 `01` 为例，复用原 ODB 省掉原先约 14 秒的第一段 DRT，但本次最终 DRT 用时 21.70 秒，原先为 13.81 秒，不能把省掉的第一段时间直接当作总收益。沿真实流程从头候选验证加复用补救，`01` 总用 64.669 秒。 [直接复用原件](../tcad_holdout_20261123/UART_RESCUE_EXISTING_ODB_RESULTS.json)

## 判断与下一步

四项主试只救回一项，批量默认触发不值得。UART 在原最佳 0.23328 µm² 的基础上多回收 0.02916 µm²，若面积目标恰好缺这一档，且完整原拒收 ODB 已保存，可考虑只触发一次复用补救。当前可行条件来自单一 UART 成功候选，尚未独立验证出可靠的事前选门规则。

下一步限定在相对 hold 拒收且无同等收益可用端点时，建立只尝试一次的同预算补救。优先在 UART 这两个残余 TT 拒收的六门上试更窄的最差路径捕获时钟邻域，分别记录各角改善、原门终态和新增耗时，再用另一独立设计验证触发条件。面积结果按超过已验收前沿的净值比较。

## 复现

三个执行目录归档到 `scratch/tcad_ibex_20261123/hold_reentry_rescue_20261125_v1.tar.gz`，含所有通过、拒收、诊断和复现的 Tcl／布线／提取／验收原件。归档 494 项、18,095,482 字节，已逐项与原件比对，SHA-256 `31a5f0da724b6655cb9fc4e84960d62fc53df93b7445aa4d82d3e772e650e466`。

```bash
h=project_docs/evidence/tcad_ibex_20261123
r=/home/toylog
g=$r/faeco_tcad_sky_holdout_20261123
gout=$g/gcd_hold_reentry_rescue_reproduction
uout=$r/faeco_tcad_uart_hold_reentry_rescue_reproduction
bash code/scripts/run_with_timeout.sh 470 taskset -c 6-11 python3 -B "$h/run_hold_reentry_rescue.py" gcd "$gout" \
  --source "$g/gcd_local_hold_preview_20261125_v2"
bash code/scripts/run_with_timeout.sh 1100 taskset -c 0-5 python3 -B "$h/run_hold_reentry_rescue.py" uart "$uout" \
  --source "$r/faeco_tcad_uart_online_20261125_matrix_v2" "$r/faeco_tcad_uart_dedup_20261125_v1" \
  "$r/faeco_tcad_uart_deferred_reservation_20261125_v1" "$r/faeco_tcad_uart_fixed_area_probe_20261125_v1"
bash code/scripts/run_with_timeout.sh 470 taskset -c 0-5 python3 -B "$h/run_uart_rescue_from_rejected_odb.py" \
  "$uout" "$r/faeco_tcad_uart_rescue_existing_odb_reproduction"
```
