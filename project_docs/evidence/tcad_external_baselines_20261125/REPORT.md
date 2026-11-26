# 同口径外部基线与功耗实测报告（OpenROAD 原生回收与 TritonSizer 预检）

2026-11-25。针对投稿评估中「最新 720 s 多角全验收协议缺少同口径现代外部基线与功耗」及「TritonSizer 兼容性预检」两项缺口（[OI-105](../../OPEN_ISSUES.md) · [投稿判断](../tcad_publication_assessment_20261125/REPORT.md)），本报告在已核的三大设计（SKY130HD AES、ASAP7 UART、SKY130HD `riscv32i`）上完成同工具链、同原约束与同验收门的实测对照。

## 1. OpenROAD 原生 `repair_timing -recover_power 100` 与 FAECO 端点功耗

### 协议与工具绑定
- 使用与 FAECO 正式矩阵完全一致的 OpenROAD 二进制：`/home/toylog/.cache/bazel/_bazel_toylog/c540bbdc4bbb635360729b4d7a91c803/execroot/_main/bazel-out/k8-opt/bin/openroad_unstamped`（`b511b6a`）。
- 对每个设计的冻结 `CONTROL` 起点（`6_final.odb` + 原 `6_final.sdc` + 原 `6_final.spef` + 原 TT Liberty）分别运行两档原生恢复：
  - `native_default`：`remove_fillers` → `repair_timing -recover_power 100 -verbose`
  - `native_allow_setup`：`remove_fillers` → `repair_timing -recover_power 100 -allow_setup_violations -verbose`
  - 注：在 `riscv32i` 上初试未前置 `remove_fillers` 时 OpenROAD 触发 `Signal 11`；前置 `remove_fillers` 并以单线程执行 `repair_timing` 后 5.97–6.29 s 正常完成并修改 24 个实例，消除了调用接线假阴性。
- 凡原生工具报告改动 ≥1 实例，均执行合法化（`detailed_placement`）、全芯片全局与详细重布线（4 线程、`droute_end_iter 64`）、天线检查、真实 RCX 及原 FF/TT/SS 三角 STA 与原验收门核验；同时对各设计 `CONTROL` 与已核 FAECO 最优端点在同 TT 库与真实 SPEF 下运行 `report_power -digits 9 -format json`。
- 原始运行根：`/home/toylog/faeco_tcad_native_recover_power_20261125_v1`。独立原始日志核验脚本：[verify_native_recover_power.py](verify_native_recover_power.py)，核验收据：[NATIVE_RECOVER_POWER_VERIFIED.json](NATIVE_RECOVER_POWER_VERIFIED.json)（SHA-256 `9e274d6bececb7e7e5d0156da34605a39ca3492bfc71f634218949705289818b`）。

### 实测汇总

三设计上 `native_default` 与 `native_allow_setup` 产生逐位一致的改门数与重布线终态；按原多角联合验收门，三设计的 OpenROAD 原生回收合格面积均为 **0.0000 µm²**：

| 设计（PDK） | 方法 | 改门数 | 名义面积回收 | 合格回收（原全门） | ΔSetup WNS (FF/TT/SS, ps) | ΔSetup TNS (TT/SS, ps) | ΔHold WNS (FF/TT/SS, ps) | DRC / 天线 | 拒收原因 |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| SKY130HD AES | FAECO 最优（720 s） | 6 | 67.5648 µm² (0.0580%) | **67.5648 µm²** | −0.09 / −0.03 / −0.04 | +10.24 / −192.36 | +0.049 / +0.077 / +0.730 | 0 / 0 | 全部通过（SEC 11089/0） |
| SKY130HD AES | OpenROAD 原生（511.6 s） | 120 | 426.6592 µm² (0.3662%) | **0.0000 µm²** | −1.04 / **−42.77** / **−761.82** | **−16,235.44** / **−301,722.27** | **−0.400** / **−0.496** / **−20.001** | 0 / 0 | TT/SS setup WNS & TNS 违例（超预算 1.2×–21.2×）；FF/TT/SS 相对 hold 全违例 |
| ASAP7 UART | FAECO 最优（720 s） | — | 0.83106 µm² (1.0519%) | **0.83106 µm²** | 最大损失 1.36 ps | SS +6.59 | 全非负且非退化 | 0 / 0 | 全部通过（SEC 567/0） |
| ASAP7 UART | OpenROAD 原生 | 16 | 0.00000 µm² (0.0000%) | **0.00000 µm²** | −0.05 / −0.03 / −0.01 | −10.98 / −26.99 | **−0.094** / **−0.110** / +0.200 | 0 / 0 | 仅作 16 处同面积 `BUFx3→HB3xp67` 替换（面积净减 0）；FF/TT 相对 hold 违例 |
| SKY130HD `riscv32i` | FAECO 最优（720 s） | 9 | 75.0720 µm² (0.1051%) | **75.0720 µm²** | 通过 60 ps 门 | 通过原 TNS 门 | 全非负且非退化 | 0 / 0 | 全部通过（SEC 4559/0） |
| SKY130HD `riscv32i` | OpenROAD 原生 | 24 | 86.3328 µm² (0.1209%) | **0.0000 µm²** | −14.93 / −16.05 / −19.49 | **−5,621.11** / −101,108.36 | +1.537 / +1.998 / +8.592 | 0 / **1** | **TT setup TNS 损失 5,621.11 ps（超 600 ps 预算 9.4×）**；**新增 1 处天线违规** |
| ASAP7 AES（独立留出） | FAECO 最优（720 s） | 6 | 0.61236 µm² (0.0518%) | **0.61236 µm²** | +0.02 / −0.14 / −0.24 | −0.64 / −6.25 | 0.000 / +0.000 / −0.000 | 0 / 0 | 全部通过（SEC 10,027/0） |
| ASAP7 AES（独立留出） | OpenROAD 原生 | 179 | 1.86624 µm² (0.1579%) | **0.00000 µm²** | — | — | — | 失败 | 720 s 重布线超时（`rc=124`，实测 674.87 s）且出现 `checkConnectivity break, net text_out[14]` |

### FAECO 已验收最优端点的同口径功耗（TT 角，真实提取 SPEF）

| 设计 | CONTROL 总功耗 / mW | FAECO 总功耗 / mW | 总功耗变化 | 组合逻辑功耗变化 | 静态漏电变化 |
|---|---:|---:|---:|---:|---:|
| SKY130HD AES（6 门，67.5648 µm²） | 66.539489 | 66.515438 | **−0.0361%** | **−0.0489%** | **−0.0217%** |
| ASAP7 UART（0.83106 µm²） | 1.040511 | 1.033649 | **−0.6595%** | **−2.1420%** | **−0.7770%** |
| SKY130HD `riscv32i`（9 门，75.0720 µm²） | 19.338720 | 19.330594 | **−0.0421%** | **−0.2045%** | **−0.0915%** |
| ASAP7 AES（6 门，0.61236 µm²，独立留出） | 14.130032 | 14.127691 | **−0.0166%** | **−0.0227%** | **−0.0137%** |

### 归因结论
- 在三个设计上，OpenROAD 原生单角 `repair_timing -recover_power 100` 均未能交付任何符合多角、原约束、物理与无新增天线硬门的面积回收：在 AES 上冻结 TT 寄生误判导致重布线后 SS setup 恶化 761.82 ps、SS hold 恶化 20.00 ps；在 UART 上仅做同面积缓冲替换且重布线破坏 FF/TT hold；在 `riscv32i` 上虽然三视图 hold 均改善且 setup WNS 合格，但重布线后 TT TNS 超 600 ps 预算 9.4 倍并引入 1 处天线违规。
- 相比之下，FAECO 三个已验收端点在交付正面积回收的同时，总功耗、组合功耗与静态漏电均同步下降。

## 2. TritonSizer 兼容性预检

详见 [TRITONSIZER_COMPAT_AUDIT.md](TRITONSIZER_COMPAT_AUDIT.md)。克隆检出官方归档提交 `31c4a04`（2018-12-01）证实其强依赖 Tcl 8.4.20、2018 年私人 OpenSTA fork 与闭源字节码 `sizer.tbc` / `libtbcload1.7.so`，且自定义 ISPD13 Liberty 解析器不支持 SKY130HD，不具备在同工具链与多角详细重布线验收闭环下直接接入的条件。

## 3. 经典 5 轮冻结寄生拉格朗日松弛（LR）四设计同门实测与保护后端解耦对照（2026-11-26）

- 驱动：[run_lr_4designs.py](run_lr_4designs.py) 与全片重布对照 [run_lr_aes_fullroute_control.py](run_lr_aes_fullroute_control.py)；原始运行根 `/home/toylog/faeco_tcad_lr_4designs_20261126_v1`；核验收据：[LR_4DESIGNS_VERIFIED.json](LR_4DESIGNS_VERIFIED.json)。
- 协议：按 Chen/Chu (TCAD'99) 与 Flach (TCAD'14) 范式，在完全相同的冻结 `CONTROL`、同 18 项筛选候选池与同 1% 周期 Setup 预算下，于冻结 TT SPEF 上执行 5 轮子梯度乘子更新与拉格朗日降尺寸决策；随后将 LR 收敛提交集送入完全相同的物理签核闭环（FF/TT/SS 三角、独立全块 DRC=0、天线=0、Yosys SEC）。为最严格公平对比，先慷慨将 **FAECO 的 `1.0 × H_row` 窗口化局部保护重布线后端**赋予 LR；对唯一通过的 `sky130hd/aes` 另跑不带保护后端的标准全片重布线对照以解耦因果。

| 设计（PDK） | LR 冻结 SPEF 提交 | 物理后端 | 物理耗时（s） | 合格回收（原全门） | 验收判定与根因 |
|---|---:|---|---:|---:|---|
| SKY130HD `aes` | 18/18（197.69 µm²） | **标准全片重布（独立 LR）** | >600.0（超时） | **0.0000 µm²** | 600 s 详细布线超时（`rc=124`，未完成 DRT/RCX/STA/SEC） |
| SKY130HD `aes` | 18/18（197.69 µm²） | **挂载 FAECO 窗口化保护后端** | **140.90** | **197.6896 µm²（100% 池）** | **通过**：窗口预检 8.22 s（18 盒→17 marker→精确 7 邻网）救活全部 18 门，0 DRC、SEC 11,089/0，三角 Hold 全改善 |
| SKY130HD `riscv32i` | 18/18（147.64 µm²） | 挂载 FAECO 窗口化保护后端 | 245.62（超时） | **0.0000 µm²** | 一次性提交 18 门引发 240 s 局部 DRT 超时 |
| ASAP7 `uart` | 18/18（1.1810 µm²） | 挂载 FAECO 窗口化保护后端 | 25.58 | **0.0000 µm²** | `FF:setup_budget`（−6.68 ps vs 2.70 ps）+ `TT/SS:hold_regression`（−0.008/−0.154 ps） |
| ASAP7 `aes` | 18/18（1.7642 µm²） | 挂载 FAECO 窗口化保护后端 | 463.85 | **0.0000 µm²** | 触发 DRC 重试且 `SS:hold_regression`（−0.012 ps） |

### 机制归因
1. **窗口化保护后端是可插拔的通用使能器**：在 `sky130hd/aes` 上，脱离 FAECO 后端的独立 LR 在 600 s 标准全片重布中超时归零，而挂载我们的 `1.0 × H_row` 窗口化保护后端后 140.9 s 一次性验收全部 18 门（197.69 µm²），直接证明该保护后端可赋能外部优化器。
2. **增量微批次与多角物理反馈同样不可替代**：即便慷慨挂载 FAECO 窗口化保护后端，一次性冻结寄生 LR 仍在 **3/4 设计上全部失败（0.0000 µm²）**（DRT 拥塞超时、多角 FF setup / TT+SS hold 崩盘与 SS hold 退化），而 FAECO 增量自适应微批次在 **4/4（100%）设计**上均稳定交付全签核正收益。
