# ASAP7 Ibex CONTROL 资格复查

2026-11-23 · TCAD-IBEX-P0-P1-DEFAULT-SKY130HD-ASAP7

**CONTROL 达到预注册 hold 与物理资格。** ORFS 构建耗时 1140.755 s，退出码 0。Ibex 使用默认 `base` 配置、原始 ORFS SDC 与固定 OpenROAD/Yosys。CTS、详细布线、RCX 均完成。详细布线标记 5,457 → 663 → 445 → 11 → 0，RCX 提取 20,323 个网。ORFS 最终报告计 20,435 个标准单元、面积 2403.6 µm²。

## 固定端点与约束

- ORFS 源版本 `da8f092a02a8e75658cc3100691aabff05f35629`，OpenROAD 构建标识 `bazel-nostamp`，其完整二进制 SHA-256 在生产回执中。实际综合日志记录 SLANG 前端，Yosys 为 `0.70+255`。固定 4 线程，外层 3,600 s。
- 原始 SDC 为 `clk_i` 上 1,000 ps 核心时钟，同周期虚拟 I/O 时钟，数据输入输出延迟各 200 ps，虚拟时钟源延迟 161.775 ps。最终 SDC 使用传播核心时钟，保留虚拟时钟及源约束对应的 157 个数据输入与 106 个输出。三视图在每次独立链接后核对了这两组真实端口。SPEF 与网表及 ODB、DEF、最终 SDC 一并绑定到同一物理端点。
- 所有视图共用该次详细布线后提取的 SPEF，分别加载五组 RVT FF、TT、SS Liberty。温压取实际 Liberty 头，RC 为单独提取的一份共享结果。

| Liberty 视图 | 温压 | Setup WNS (ps) | Hold WNS (ps) | Setup TNS (ps) | Hold TNS (ps) |
|---|---|---:|---:|---:|---:|
| FF | 0.77 V / 0°C | +0.380362 | +35.955849 | 0.000 | 0.000 |
| TT | 0.70 V / 25°C | -382.748166 | +53.158783 | -449949.738 | 0.000 |
| SS | 0.63 V / 100°C | -1085.186052 | +77.237466 | -1628197.197 | 0.000 |

三套独立 OpenSTA 读数的 hold 均为正。TT、SS 的 setup 保留负裕量，后续性能比较以各自固定参考衡量相对预算。候选、额外布线与 SEC 尚未在本资格步骤中执行。

## FF 原生与独立读数

原生报告在 FF 上给出 setup +0.772160 ps、hold +35.9558 ps。第一次资格驱动把 0.10 ps 原生数值交叉检查当作输出回执条件，测完三视图后报告相差约 0.392 ps。诊断固定原 SDC、Liberty 和同一 SPEF，分别读回最终 ODB 和导出网表。

| FF 读回 | Setup WNS (ps) | Hold WNS (ps) |
|---|---:|---:|
| 同一 OpenROAD，直接读最终 ODB | +0.772160 | +35.955849 |
| 同一 OpenROAD，以 Verilog 与 LEF 重新链接 | +0.677236 | +35.955849 |
| 独立 OpenSTA，以 Verilog 重新链接 | +0.380362 | +35.955849 |

三个成功读回的最差 setup 路径均从 `if_stage_i.instr_rdata_id_o[15]$_DFFE_PP_` 到 `cs_registers_i.minstret_counter_i.counter_val_o[25]$_DFFE_PN0P_`。固定 ODB 和独立 OpenSTA 的 required time 均为 1127.285645 ps，arrival time 分别是 1126.513428 ps 和 1126.905273 ps。同一二进制从 ODB 切到 Verilog+LEF 对应约 0.095 ps 的差量，独立 OpenSTA 再产生约 0.297 ps 的差量。使用同一独立读回口径做后续 P1 各策略比较。未提供 LEF 的早期 OpenROAD 网表诊断在建库检查退出，未产生时序读数，原件保留。

P0 严格资格按预注册执行。原生数值交叉检查在 JSON 中单列。最终回执核对三个已完成日志、精确 Tcl 和冻结输入指纹，回填时未追加三视图 STA。共有三次资格 STA、两次成功附加 FF 诊断，一次失败的附加装载诊断。

## 交付入口

- [端点与三角结果](CONTROL.json) · [生产回执](PRODUCER_RECEIPT.json) · [生产命令](PRODUCER_COMMAND.txt)。
- [ORFS 原配置](ORFS_SOURCE_CONFIG.mk) · [原始 SDC](ORFS_SOURCE_CONSTRAINT.sdc) · [资格脚本](qualify_asap7_control.py)。
- WSL 原始工程 `/home/toylog/faeco_tcad_ibex_20261123/control_asap7`。完整阶段日志和最终产物分别在 `logs/asap7/ibex/base/` 与 `results/asap7/ibex/base/`，资格及诊断 Tcl/日志在 `qualification/` 与 `qualification_ff_diagnostic/`。
