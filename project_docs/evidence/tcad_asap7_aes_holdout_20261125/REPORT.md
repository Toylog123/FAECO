# 7 nm ASAP7 `aes_cipher_top` 独立留出验证报告（2026-11-25）

本报告记录全新 7 nm 独立留出设计 `asap7/aes`（`aes_cipher_top`，22,819 实例，72% 利用率，单时钟 380 ps 原 SDC，无硬宏，此前未用于任何 FAECO 调参或规则选择）的共同起点制备、P0 资格验收、冻结筛选、共享灵敏度排名 6 臂正反序墙钟对照，以及同口径功耗与 OpenROAD 原生回收基线实测（关联 [OI-105](../../OPEN_ISSUES.md)）。

## 1. 原生制备、最小共同起点修复与 P0 资格

- 原生制备脚本：[produce_asap7_aes.sh](produce_asap7_aes.sh)，采用与既有实验完全一致的 ORFS + OpenROAD `b511b6a`（`openroad_unstamped`）4 线程制备，575.06 s 完成（`22,819` 实例，`72%` 利用率，`5_route_drc.rpt = 0`，原生天线 `0`）。
- 初始 P0 资格检验（[qualify_asap7_aes.py](qualify_asap7_aes.py)）核实 FF/TT/SS hold 全正（`+35.358 / +52.071 / +24.664 ps`）、三视图电气违例全 0、源/导出 SDC 全匹配、全网表 SEC `10,027/0`，但独立单线程 `drt::check_drc` 检出 M3 上 2 处微瑕（`net4557` / `net5205` 在 `(18.63, 33.92)`）。
- 最小共同起点保护修复（[repair_asap7_aes_control.py](repair_asap7_aes_control.py)，`repaired_control_v4`）：保持其余 `12,391` 条信号网 `FIXED`，仅开放违例点 ±0.35 µm 内 `21` 条非时钟 M3 邻网，以 `-or_seed 2` 局部重布后原样恢复全网 `ROUTED` 状态，且按 ORFS 规范先写 `6_final.{odb,def,v,sdc}` 再执行 `extract_parasitics`（避免 OpenROAD 内存 RCX 移除 ASAP7 `RECT` 金属补丁）。
- 修复后共同起点 **P0 全项资格 `hold_qualified`**（`repaired_control_v4/CONTROL.json`）：
  - 原 380 ps 周期、76 ps I/O、77.930 ps 虚拟时钟延迟，源/导出 SDC 逐命令匹配，内嵌导引完备；
  - FF/TT/SS setup WNS `−2.660 / −153.121 / −428.275 ps`，hold WNS **`+35.358431 / +52.071299 / +24.663563 ps`**，三视图 `MAX_SLEW = 0`、`MAX_CAPACITANCE = 0`；
  - 独立全块 DRC **`0`**、天线 **`0`**，原生至修复全网表两态 SEC **`10,027 / 0`**；功能标准单元基线面积 **`1,181.81106 µm²`**。

## 2. 冻结筛选与 720 RAW s 同排名 6 臂正反序对照

- 冻结 SPEF TT 筛选（`screen_qualified_v1`，1 路串行）：实测 **`156.267725 RAW s`**（包装 161 s，rc0），选出 18 项兼容降尺寸候选（主要为 `AOI221xp5 / AOI211xp5 / NAND3xp33 / NOR3xp33`），全额计入每臂 720 RAW s 窗口。
- 共享严格零动作预检（`probe_zero_v1` 与矩阵内 `preflight/zero`）：全部一次通过原门、独立 DRC/天线 0、SEC `10,027/0`。
- 正式 6 臂驱动：[run_asap7_aes_rank_aligned.py](run_asap7_aes_rank_aligned.py)，原始运行根 `/home/toylog/faeco_tcad_asap7_aes_20261125_v1/asap7/aes/matrix_rank_aligned_v1`，CPU 0–5 独占串行、4 线程、纯墙钟 720 RAW s（无请求上限），三方法逐臂在窗内现测同一 TT 灵敏度排序并校验跨臂逐项一致。逐角 setup WNS 预算 `3.8 ps`（1% 周期），FF/TT/SS setup TNS 预算 `38.0 / 317.382 / 1,226.177 ps`，hold 非负且相对容差 `0.001 ps`。
- 独立核验脚本：[verify_asap7_aes_holdout.py](verify_asap7_aes_holdout.py)，核验收据：[ASAP7_AES_HOLDOUT_VERIFIED.json](ASAP7_AES_HOLDOUT_VERIFIED.json)（SHA-256 `d2df3be99b701b97b63db87ec1c2a20c01702958582b590415d7fa3b1a59a5da`）。

### 6 臂实测结果

| 调度（同实时灵敏度起序 & 同在线后端） | 正/反序完成评价 | 两序窗内最大合格回收（µm² / %） | 首达 0.01% 及共同实收 `0.20412 µm²`（正/反序 RAW s） | 窗内最大端点 ΔSetup WNS (FF/TT/SS, ps) | 窗内最大端点 ΔHold WNS (FF/TT/SS, ps) | SEC |
|---|---:|---:|---:|---:|---:|---:|
| `single_sensitivity`（强单门） | 2/3 · 2/3 | 0.204120（0.0173%，2 门） | 667.13 / 637.02 | +0.002 / +0.003 / +0.006 | −0.000007 / +0.000007 / 0.000000 | 10,027/0 |
| `fixed_online`（同排名固定三门） | 2/3 · 2/3 | **0.612360（0.0518%，6 门）** | **418.55 / 401.62** | +0.019 / −0.137 / −0.240 | 0.000000 / +0.000021 / −0.000111 | 10,027/0 |
| `faeco_dedup`（同排名 FAECO） | 2/3 · 2/3 | **0.612360（0.0518%，6 门）** | **414.55 / 417.00** | +0.019 / −0.137 / −0.240 | 0.000000 / +0.000021 / −0.000111 | 10,027/0 |

- **跨序逐字节复现**：三种策略各自正反序最优端点的 ODB、DEF、网表与去日期 SPEF 100% 逐字节一致；`fixed_online` 与 `faeco_dedup` 产出逐字节相同的 6 门物理端点。
- **批处理相对强单门的跨工艺独立收益**：在相同 720 RAW s 硬时窗与相同灵敏度排序下，批处理（`fixed_online` 与 `faeco_dedup`）回收面积为强单门的 **3.00×**（`0.612360` vs `0.204120 µm²`），到达共同实收 `0.204120 µm²` 提前 **220–252 RAW s**（`faeco_dedup` 414.55/417.00 s vs `single_sensitivity` 667.13/637.02 s）。
- **动态反馈与布线前诊断的诚实边界**：
  1. 共享灵敏度排序后，前两批均一次通过全部原门、未触发相对 hold 拒收，因此 FAECO 动态反馈未分叉，与同排名固定三门打平（与 SKY130HD `riscv32i` 一致）。
  2. 六臂共执行 **16 次**全块在线预诊断，全部为 **`0 marker`**（本组 7 nm 兼容换门未触发可归属布线前邻线冲突），单线程全块 `drt::check_drc` 平均每次消耗 **44.02 RAW s**。这表明在零冲突的大规模 7 nm 设计上，全块布线前预检产生固定时间税，凸显了局部窗口化 DRC 预检的工程改进价值。

## 3. 同口径功耗与 OpenROAD 原生 `recover_power` 基线

- **FAECO 最优 6 门端点功耗**（TT 角，真实提取 SPEF，`report_power -digits 9 -format json`）：总功耗 `14.13003 → 14.12769 mW`（**−0.0166%**），组合逻辑功耗 **−0.0227%**，静态漏电 **−0.0137%**。
- **OpenROAD 原生 `repair_timing -recover_power 100`**：前置 `remove_fillers` 后 7.56 s 内改动 **179 个实例**（名义面积 −1.86624 µm² / −0.1579%）；但在随后的同平台 4 线程全局/详细重布线中出现 `Error: checkConnectivity break, net text_out[14]` 并在 720 s 时限内超时退出（`rc=124`，实测 674.87 s 超时裁剪），未能交付任何可验收端点（合格面积回收 **`0.0000 µm²`**）。
