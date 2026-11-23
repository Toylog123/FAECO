# SKY130HD 留出电路起点

预登记对象为 ORFS `sky130hd/aes`（顶层 `aes_cipher_top`，周期 3.6 ns、输入输出延时 0.72 ns）和 `sky130hd/gcd`（顶层 `gcd`，周期 1.1 ns、输入输出延时 0.22 ns）。仅按原 SDC 准备详细布线、寄生提取及三视图 hold 复核。这两个电路的筛选候选和策略结果在规则冻结前不读取。AES 为主留出，GCD 为小规模补充。

ORFS `da8f092a02a8e75658cc3100691aabff05f35629`，OpenROAD 使用与 Ibex 一致的 b511b6a 固定构建，Yosys 使用 0.70+255。物理生产设 `FLOW_VARIANT=base NUM_CORES=4`，CPU 6–11，单设计总限时 3600 s。实际命令为 `wsl taskset -c 6-11 bash scratch/tcad_ibex_20261123/produce_sky_holdouts.sh`，原件输出 `/home/toylog/faeco_tcad_sky_holdout_20261123`。

AES 进入详细布线后，GCD 起点构建提前用 CPU 6–11 上的两个线程独立执行，先准备一套可复核的留出起点。原串行驱动随后会在 GCD 目录已存在处结束，两个原件取各自 `producer.rc`。GCD 起点命令为 `wsl taskset -c 6-11 bash project_docs/evidence/tcad_holdout_20261123/produce_gcd_early.sh`，限时 1200 s。[AES 实发脚本](produce_sky_holdouts.sh) · [GCD 实发脚本](produce_gcd_early.sh)

## GCD 起点资格

原生生产耗时 96.73 s，退出码 0。详细布线 DRC 为零，天线违规报告为空，OpenRCX 提取了 486 个网。约束保持原始 1.1 ns 周期、0.22 ns I/O 延迟和 0.29 ns 虚拟时钟延迟，实际核对 35 个数据输入与 18 个输出。[原始资格收据](GCD_CONTROL.json)

| 视图 | Setup WNS（ps） | Setup TNS（ps） | Hold WNS（ps） | Hold TNS（ps） |
|---|---:|---:|---:|---:|
| TT | −1287.504769 | −57025.463462 | +430.726704 | 0 |
| FF | −371.587539 | −13487.631456 | +358.948093 | 0 |
| SS | −9960.613667 | −534478.715508 | +342.905315 | 0 |

资格命令为 `wsl taskset -c 6-11 python3 -B project_docs/evidence/tcad_holdout_20261123/qualify_sky_holdout.py gcd`。与各角同一份详细布线后 SPEF，三视图 hold 合格。原件仍在 `/home/toylog/faeco_tcad_sky_holdout_20261123/gcd`。

同一冻结 ODB 的只读检查返回 `grt::have_routes=1` 和 `design_is_routed=1`，支持基于内嵌导引和冻结布线复提取的候选入口。使用 TT Liberty 的完整基线网表自证得到 262 项已证明、0 项未证明。上述检查均在候选筛选和调度之前完成。GCD 原生构建及资格核验与 AES 起点准备在 CPU 6–11 同机重叠，两者的编译、布线或资格耗时不计入三臂候选墙钟。[导引检查](GCD_GUIDE_CHECK.txt) · [SEC 自证](GCD_SEC_SELF.json)

## AES 原生起点及 SS hold 修复

原生 ORFS 运行耗时 2832.64 s，退出码 0。最终详细布线 DRC 及天线违例为零，OpenRCX 提取 15,459 个网。原 SDC 的 258 个数据输入、129 个输出，以及 3.6 ns 周期和 0.72 ns I/O 延时均通过逐端口复核。原生起点 TT/FF hold 分别为 +529.873/+341.429 ps，SS 的 hold WNS/TNS 为 −975.978/−124464.094 ps，因此原生起点的状态为 `hold_infeasible`。[原生资格回执](AES_NATIVE_CONTROL.json)

2026-11-24 单独启动一次原生父端点的 SS hold 修复。固定 TT/FF/SS Liberty 和原 SDC，采用 +0.10 ns hold 裕量、最多 10% 缓冲，保留连接与所接单元位置、朝向均未变化的线网详细走线。之后执行 DRT、天线审核、RCX 和三角实际 SPEF 回读。修复及独立验收都不会计入候选方法墙钟。原生端点保留在原路径，修复末级输出单列在 `aes/ss_hold_repair_v1`。实际命令为 `wsl taskset -c 6-11 bash project_docs/evidence/tcad_holdout_20261123/repair_aes_hold.sh`，限时 1800 s。[修复命令](repair_aes_hold.sh) · [修复 Tcl](repair_sky_holdout.tcl)

原始 SS min slack 为 −975.978 ps。修复增加 197 个缓冲，涉及 399 个实例，清除 381 条受影响网的走线，保留 14,881 条原详细走线。布线前的 min slack 估计为 +100.062 ps。新端点耗时 428.59 s，退出码 0，详细布线 DRC 为零，天线检查为零，提取 15,656 个网。原生与修复后 `6_final.sdc` 字节一致，SHA-256 `379f839cc62d103d029661350ad1a79355419c4fd1a4733d698ab2c365686a9b`。[修复后资格回执](AES_REPAIRED_CONTROL.json)

| 视图 | 原生 hold WNS（ps） | 修复后 hold WNS（ps） | 修复后 hold TNS（ps） | 修复后 setup WNS（ps） |
|---|---:|---:|---:|---:|
| TT | +529.872590 | +523.914911 | 0 | −377.759601 |
| FF | +341.429052 | +336.273953 | 0 | +679.875045 |
| SS | −975.978187 | −66.615602 | −66.615602 | −13648.035591 |

实际 SS SPEF 仍有从输入 `key[70]` 到 `u0.w[1][6]$_DFF_P_` 的 hold 违例，剩余负裕量为 66.616 ps。修复后的端点仍为 `hold_infeasible`。该分支在资格门结束，筛选、候选物理评估和 SEC 计数均为零。已完成的 GCD 用于正式留出验证。

预登记一轮针对该剩余接收引脚的增量修复。在 v1 最终 ODB 上核对唯一负端点后，只在 `u0.w[1][6]$_DFF_P_/D` 前插入一个 `dlygate4sd1_1`，SS 读回目标裕量 +0.20 ns，原 SDC 保持。`dlygate4sd1_1` 的 SS Liberty 最小上升弧表首项为 0.545 ns，高于 `buf_1` 的 0.148 ns。尝试结束后分别复核 DRT、天线、RCX 和三视图 hold。仅通过资格的端点再用原生网表做整网 SEC。新路径 `aes/ss_hold_targeted_v2`，1200 s 硬限时，执行命令 `wsl taskset -c 6-11 bash project_docs/evidence/tcad_holdout_20261123/repair_aes_targeted.sh`。[执行脚本](repair_aes_targeted.sh) · [单引脚操作](repair_aes_targeted.tcl)

首次执行核对到原 SS 唯一违例引脚，随后在名字断言处退出，未进入 DRT。固定 OpenROAD 会为 `-buffer_name` 自动添加唯一后缀，因此把检查改为核对 `insert_buffer` 返回的对象，以及其输出与目标 D 引脚的实际连接。首轮故障日志及当时的两份驱动保留在 `ss_hold_targeted_v2`。同一父端点、目标、插入单元与原 SDC 的技术重试单列在 `ss_hold_targeted_v2b`。

技术重试增加一个实例 `faeco_hold_target_v28641`，输出只接原目标 D 引脚。合法化后清除一条受影响网的原详细走线，保留 15,655 条线网的原走线。详细布线、天线检查和 RCX 耗时 115.96 s，退出码 0，DRC 与天线均为零，提取 15,657 个网。原生、v1 和 v2b 最终 SDC 字节一致。基于最终 SPEF 的 TT/FF/SS hold WNS 分别为 **+523.915/+336.274/+55.296 ps**，hold TNS 均为 0。单独读回目标 D 引脚的 SS hold 为 **+633.552 ps**，超过 +0.20 ns 的目标。原生至 v2b 整网 SEC 为 **11089 已证明、0 未证明**。v2b 已具备独立留出起点资格。负 setup WNS 为 TT −380.501 ps 和 SS −13648.043 ps，后续只适用相对 setup 包络。[最终资格](AES_TARGETED_CONTROL.json) · [目标引脚读回](AES_TARGETED_SS.txt) · [原生至最终 SEC](AES_TARGETED_SEC.json)

原件包保留在工作区 `scratch/tcad_ibex_20261123/`。`sky130hd_holdout_control_v1.tar.gz` 绑定 GCD、AES 原生与 v1 持续修复原件，SHA-256 为 `a3d581d5184ebd761b2e4daec160bec789736417a5b3802ed4b14bfeaa4bdeac`。`sky130hd_aes_targeted_hold_v2.tar.gz` 绑定技术失败和修复成功两个目录，SHA-256 为 `9018b329f4a4f378883b1a6c3cde25aea6d796cd0494d82b21c386ca84a4c631`。
