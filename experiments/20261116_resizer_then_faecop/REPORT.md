# P1′：resizer 之后的残余空间（resizer → FAECO-P）

- 日期：2026-11-11（pilot）
- 预注册：`PREREGISTRATION.md`（判据在读数前写定；§7 A1 记录导出点与对照臂修订）
- 上游：`experiments/20261115_p1_resizer_vs_faeco/REPORT.md`（P1：FAECO-P 0/8 胜 resizer；Hybrid 先我方后 resizer 5/8 胜但 +0.0243 ns 未过门）

## 1. 问题

P1 与 Hybrid 已封「独立对抗」与「先我方后 resizer」两个方向。本实验测最后一个组合方向：
**resizer 先做，我们的 ECO 在它的终点上继续做** —— resizer 的 LR 目标不会做 R（等价改写）、
不做 JOINT（多实例联合）、也不按覆盖率排序；若这些动作在 resizer 终点上仍有效，说明两者**动作空间互补**。

## 2. 装置

| 项 | 值 |
|---|---|
| 电路 | s382、s641、s832（P1 里「近 resizer / 远差 / 近无收益」三类各一） |
| 起点 | `experiments/20261016_r22_cut_ablation_v3/W1/<c>/mapped.v`，period 0.5 |
| resizer 段 | `export_netlist.py`：标准 place 流程 + `setRC.tcl` + `repair_timing -setup` + `detailed_placement`（**CTS 之前**，见预注册 A1）+ `write_verilog -remove_cells {tapcell}` 导出门级网表 |
| 我方段 | `run_rf.sh`：FAECO-P（单补丁接受、`--physical-gate --physical-backend placed_ens --placement-utils 0.30,0.35,0.40`、`--seed 1`） |
| 端点 | `rseco.routed_sta`：floorplan→place→CTS→global+detailed route→RCX SPEF→独立 `sta`；util 0.30/0.35/0.40 三布局均值 |

臂：

| 臂 | 定义 | 说明 |
|---|---|---|
| R_own | resizer 归档读数（P1，post-CTS repair） | 仅参照，用于算 re-entry gap |
| R′ | 导出网表 → 标准流程重测 | RF 的对照（同流程、同网表） |
| RF | 导出网表 → FAECO-P → 标准流程重测 | 主臂 |

## 3. 读数

### 3.1 R′（导出网表 → 标准流程重测）与 re-entry gap

| 电路 | R_own（P1 归档） | R′ u0.30 | R′ u0.35 | R′ u0.40 | R′ 均值 | gap = R′−R_own |
|---|---|---|---|---|---|---|---|
| s382 | −0.8414 | −0.8359 | −0.8497 | −0.8385 | −0.8413 | **+0.0001** |
| s641 | −1.1295 | −1.3220 | −1.3071 | −1.3278 | −1.3190 | **−0.1895** |
| s832 | −1.0587 | −1.2092 | −1.2813 | −1.3232 | −1.2712 | **−0.2125** |

> R′ 的对照臂用**归一化网表** `resized_gate_flat.v`（与 RF 的输入同字节，见预注册 A4）。
> 用原始转义名网表作对照时 s382 会差 0.0027 ns（实例改名改变布局随机性），量级与被判效应同阶，故作废重测。

- 全部 9 次布线 **DRC=0**、无 segfault ⇒ **H1 可行性门 PASS**。
- s641/s832 的 |gap| > 0.15 ns：pre-CTS 修复变体明显弱于 P1 的 post-CTS resizer 臂（见预注册 A2）；
  post-CTS 导出虽成功，但喂回标准流程 segfault，故 pilot 固定用 pre-CTS 导出。

### 3.2 RF（resizer 终点 → FAECO-P）

| 电路 | R′ 均值 | RF 均值 | **RF−R′** | RF 接受数 | 接受动作 |
|---|---|---|---|---|---|
| s382 | −0.8413 | −0.8413 | **+0.0000** | 0 / 74 候选 | （无：最大物理增量 +0.0092，未过 0.010 门） |
| s641 | −1.3190 | −1.1988 | **+0.1202** | 3 / 255 | G `nor2_1→2`（_104_）、G `a21oi_1→2`（_103_）、G `o211ai_1→2`（_080_） |
| s832 | −1.2712 | −1.1555 | **+0.1157** | 2 / 297 | R `dlymetal6s2s_1→buf_2`（split4）、G `nand2b_1→4`（_152_） |

逐补丁布线后归因（util 0.35 单布局，`chain_patches.py` → `patch_chain_pilot1.json`）：

| 电路 | 起点 R′ | patch 1 | patch 2 | patch 3 |
|---|---|---|---|---|
| s641 | −1.3071 | −1.2551（**+0.0520**） | −1.2107（**+0.0444**） | −1.1754（**+0.0353**） |
| s832 | −1.2813 | −1.2276（**+0.0538**） | −1.1768（**+0.0508**） | — |

- **5 个被接受补丁的布线后增量全部为正**，且逐步单调累积；布局档判据给出的 placed_delta
  依次为 0.0358 / 0.0229 / 0.0101（s641）与 0.0465 / 0.0157（s832），
  布线后/布局档比值 1.2–3.5 ⇒ 与 arm K 观察到的「布局档系统性低估」一致。
- s382 的 RF 与 R′ **逐位相同**（0 接受）：resizer 终点在这个设计上已无我方动作空间内的改进。

## 4. 判定

| 门 | 判据（预注册） | 实测 | 结论 |
|---|---|---|---|
| H1 可行性 | 3 例导出网表能重入标准流程、DRC=0、产出 routed.v+spef | 3/3 成功（18 次布线全部 DRC=0，逐位可复现） | **PASS** |
| **H2 残余空间（主判据）** | RF−R′ 在 ≥2/3 例为正 **且** 三例均值 ≥ +0.05 ns | 2/3 为正（s641 +0.1202、s832 +0.1157、s382 0.0000），均值 **+0.0786 ns** | **PASS** |
| H3 成本 | 仅报告（我方段 / resizer 段墙钟） | 我方段每例 4–20 轮 × 每轮 3 布局判据，resizer 段单次调用 | 报告项 |
| re-entry gap | |gap|>0.15 需声明 | s641 −0.1895、s832 −0.2125、s382 +0.0001 | 见下 |

**PROMOTE = YES**（`summary.json`）。

### 4.1 能写什么、不能写什么

- **能写**：在一个 **pre-CTS 的 resizer 变体终点**上，我们的 ECO 用 **2–3 个单实例动作**
  再拿到 **+0.12 ns 量级**（s641 +0.120、s832 +0.116，三布局均值），且每个补丁的布线后增量都为正。
  这说明 resizer 的终点在**我们的动作空间内**不是局部最优，两者动作空间**存在互补**（resizer 不做 R 等价改写、
  不做按覆盖率排序的选择）。
- **不能写**：「在 P1 的 resizer 之上还有 +0.12 ns」——本实验的 resizer 段是 **pre-CTS + repair_timing**
  的变体，其终点比 P1 的 post-CTS resizer 弱 **0.19 / 0.21 ns**（re-entry gap），
  故结论**只限 RF vs R′ 的配对比较**（预注册 A2 声明条款）。
- **不能写**：三例 pilot 已证明方法更优——样本 3 例，且 RF 段成本远高于 resizer 单次调用。

> ⚠ 结论依赖一个**新修的解析器分支**（`code/src/rseco/netlist.py`，commit `ef72abd`）：
> OpenROAD `write_verilog` 的扁平网表把首个命名连接写在实例头同一行，旧解析器把每个实例切成碎片
> ⇒ 门数 0 ⇒ `logic_levels()` 抛 `KeyError`。修后 W1 网表解析不变（91 gates），并加了回归用例。

## 5. 复现

```bash
# 1) 导出 resizer 终点网表（每例约 2 min）
.venv/Scripts/python.exe experiments/20261116_resizer_then_faecop/export_netlist.py s382 s641 s832
# 2) R' 端点（3 例 × 3 布局）
.venv/Scripts/python.exe experiments/20261116_resizer_then_faecop/measure.py --arms Rprime --circuits s382,s641,s832 --utils 0.30,0.35,0.40
# 3) 我方段
bash experiments/20261116_resizer_then_faecop/run_rf.sh s382 s641 s832
# 4) RF 端点 + 判定
.venv/Scripts/python.exe experiments/20261116_resizer_then_faecop/measure.py --arms RF --circuits s382,s641,s832 --utils 0.30,0.35,0.40
.venv/Scripts/python.exe experiments/20261116_resizer_then_faecop/analyze.py
```

## 6. 边界

- 三例 pilot，不是 8 例结论；扩样须另立预注册。
- 导出点前移到 CTS 之前（A1），R′ 与 R_own 的差即 re-entry gap，随读数表一并报告。
- 我方段成本（每例 3 布局判据 + 端点）远高于 resizer 单次调用；即使 H2 PASS 也只能写
  「有残余空间」，不能写「更优的方法」。
- **实例改名等价性已单独验证**（`scratch/_check_rename_equivalence.py`）：归一化网表与原导出网表
  单元多重集相同（91 / 122 / 149 个单元）、网络集合相同、FF 名 1:1 映射（21 / 19 / 5），
  字符差全部来自实例名变短 ⇒ 改名不改拓扑，只影响布局随机性。
- 端点只测 **WNS**（`report_checks -path_delay max`），未测 TNS / 功耗 / 面积；
  RF 的 2–3 个单元变大是否会带来功耗代价，本实验未测。
- 三个电路在 P1 里分属「近 resizer / 远差 / 近无收益」三类，是**刻意**选的三种处境，不代表全族分布。