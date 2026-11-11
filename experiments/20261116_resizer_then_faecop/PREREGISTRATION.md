# 预注册：resizer 之后的残余空间（resizer → FAECO-P，P1′）

- 日期：2026-11-11
- 上游结论：`experiments/20261115_p1_resizer_vs_faeco/REPORT.md`
  （P1：FAECO-P 0/8 胜 resizer；Hybrid = 先 FAECO-P 后 resizer，5/8 胜但均值差 +0.0243 ns < 0.05，均不晋级）
- 本文件在**任何本实验读数产生之前**写定；运行期修订只允许追加到 §7，不得改本文判据。

## 1. 问题

P1 的两个方向（独立对抗、先我方后 resizer）都已封口。剩下唯一没测过的组合方向是**反过来**：
**resizer 先做（当成内层优化器），我们的 ECO 在它的终点上继续做** —— 即
"成熟的全局 resizer 之后，我们的覆盖优先 ECO 还有没有可拿的残余空间"。

这个问题与 P1/Hybrid 不同，它在逻辑上是**可组合性检验的另一半**，且不要求我们的判据比 resizer 更准：
只要 resizer 的 LR 目标是"按灵敏度改尺寸/插 buffer"，它不会做 R（等价改写）、也不会做 JOINT（多实例联合），
也不为"覆盖率"排序；若这些动作在 resizer 终点上仍有效，就说明两者**动作空间互补**。

## 2. 装置（pilot 规模）

- 电路：**s382、s641、s832**（P1 里分属"我们近 resizer / 我们远差 / 我们几乎无收益"三类）。
- 起点网表：`experiments/20261016_r22_cut_ablation_v3/W1/<c>/mapped.v`（与 P1 相同，period 0.5）。
- 流程分两段：
  1. **resizer 段**：`run_resizer.py`（标准流程 + `set_wire_rc` + `repair_timing -setup` + `detailed_placement`
     + tie 网复位），产出 `routed.v` / `routed.def` / `routed.spef`；该段读数复用 P1 归档（逐字节同一流程）。
  2. **导出段（本实验新写）**：从 resizer 段的 `routed.def` + 网表导出**门级 verilog**（剔除物理单元
     `tap*`/`fill*`/`decap*` 及其连接），作为我们 ECO 的输入。若导出失败，本实验按 §4 H1 判 FAIL 并停止。
  3. **我方段**：`run_faecop.sh` 同款配置（`--physical-gate --physical-backend placed_ens --placement-utils 0.30,0.35,0.40`，
     单补丁接受、`--seed 1`、20 轮上限/500 STA 预算），输入 = 导出网表。
- 端点：统一 `rseco.routed_sta`（floorplan→place→CTS→global+detailed route→RCX 提取 SPEF→独立 `sta`），
  每臂每 util 一条，取 util 0.30/0.35/0.40 三布局均值。resizer 段读数直接用 P1 归档的同流程读数。

## 3. 臂

| 臂 | 定义 | 已有读数 |
|---|---|---|
| **R_own** | resizer 单次，读它自己流程的读数（P1 的 resizer 臂） | 有（P1 归档） |
| **R′** | resizer 终点导出网表 → **标准流程**重测（我们 ECO 的对照） | 本实验要跑 |
| **RF** | resizer 终点导出网表 → FAECO-P → 标准流程重测 | 本实验要跑 |
| （参照）**F** | FAECO-P 单跑（P1 的 FAECO-P 臂） | 有（P1 归档） |

- **主比较是 RF vs R′**：两者走**同一条标准流程**、同一个导出网表，唯一差别是我们 ECO 是否插入，
  这样才不把"两段流程不同"混进结论（P1 的 A2 教训）。**R_own 只作参照**，用于报告
  "导出-重入间隙"（re-entry gap = R′ − R_own），间隙大小随结论一起报，不参与 H2 判定。
- F 只作参照，不与 R′/RF 抢主判据。
- 成本必须一并报：resizer 段墙钟（每例一次导出）+ 我方搜索墙钟（每例 3 布局判据 + 布线端点）。

## 4. 判据（运行前写定）

- **H1 可行性门（gate，先于 H2）**：resizer 终点导出的门级网表能被标准流程重新读入并布线，
  **3 例全部**跑通（无 segfault、DRC=0、产出 `routed.v` + `routed.spef`）。任一例不满足 ⇒ H1 FAIL，
  本实验停止，只记录"工具级不可组合"。
- **H2 残余空间（主判据）**：RF 相对 R′ 的布线后 WNS 增益在 **≥2/3 例为正**，且 **三例均值差 ≥ +0.05 ns**
  （0.05 = P1 沿用门槛；噪声底 0.03 ns、布局离散中位 0.055–0.104 ns 已在 P1 量化）。两条都满足才算 PASS。
- **H3 成本（报告项，不作晋级否决）**：我方段墙钟 / resizer 段墙钟 ≤ 3.0；超过则即使 H2 PASS
  也只能写"有收益但成本不划算"。
- **附带报告项（不作判据）**：re-entry gap = R′ − R_own，逐例列出；若 |gap| > 0.15 ns，须在结论里
  声明"导出网表是一个与被测 resizer 臂不同的对象，结论只限 RF vs R′ 的配对比较"。

**晋级规则**：H1 与 H2 同时 PASS ⇒ 扩到 8 例并做逐补丁配对（每例 3–5 步布线）再确认；
H1 PASS 但 H2 FAIL ⇒ 记录"resizer 终点无可利用残余空间"，本路线（布局后 ECO 性能）**整体停止**，
不再调参重跑；H1 FAIL ⇒ 记录"工具级不可组合"，同样停止。

## 5. 读法约束（结论措辞）

- 只允许说"resizer 之后我们的动作还能/不能再拿到 ≥0.05 ns 的布线后增益"；
  **不得**说"我们的方法优于 resizer"（P1 已 0/8 否证）或"组合有收益"（Hybrid 已 +0.0243 否证）。
- 三例 pilot 不是 8 例结论；若扩样，须另立预注册，不得用 pilot 数据回头改判据。
- 导出-重入若引入物理差异（例如 tapcell 位置变化），必须在该例的读数表里单列，不得混入均值。

## 6. 产物

- `experiments/20261116_resizer_then_faecop/`：
  - `export_netlist.py`（从 routed.def + 网表导出门级 verilog，剔除 `tap*`/`fill*`/`decap*`）
  - `run_faecop_after_resizer.sh`（导出 + 我方段）
  - `run_endpoints.py` / `analyze.py`（三布局端点与 H1/H2/H3 判定）
  - `REPORT.md`（读数表 + 判定 + 归因 + 复现命令）
- 记录：`project_docs/LOGS.md`、`docs/EXPERIENCE.md`、`project_docs/CANON.md` §1、registry。

## 7. 运行期修订（只追加，不改上面判据）

### A1（2026-11-11，导出点与对照臂，在任何本实验读数产生之前写下）

- **导出点在 CTS 之前**：`help repair_timing` 确认 26Q3 的 `repair_timing` **没有区域/局部选项**
  （只有 `-setup/-hold/-slack_margin/-max_passes/-repair_tns/...`），"按区域调度 resizer" 在本工具上
  不可实现；因此本实验只检验**时间上串联**（resizer 一次 → 我方 ECO）这一种组合方式。
- 导出用 `write_verilog -remove_cells {sky130_fd_sc_hd__tapvpwrvgnd_1}`（已验证支持 `-remove_cells`）。
  若在 CTS 之后导出，网表会带时钟树，我方标准流程会再建一次时钟树（双重 CTS），故导出点前移到
  **place 之后、CTS 之前**（resizer 在理想时钟下修 setup）。这一改动使 R′/RF 的对照干净，
  代价是：R′ 与 P1 归档的 R_own 之间存在流程差异（P1 的 resizer 在 CTS 之后修），
  该差异按 §4 的 re-entry gap 逐例报告，不参与 H2 判定。
- 主比较由 "RF vs R" 改为 "**RF vs R′**"（§3 已同步）：R′ 与 RF 走同一条标准流程、同一导出网表。
- 可行性检查先行：先在 s382 跑一次导出 + 标准流程重入，确认无 segfault、DRC=0，再跑三例。

### A2（2026-11-11，post-CTS 导出尝试与 re-entry gap，在 RF 臂读数之前写下）

- **尝试过 post-CTS 导出**（`export_netlist.py post-cts s641`，成功产出 13,907 B 网表），但把它喂回
  标准流程时 **segfault**：`route flow returncode=139`，与 P1 里"resizer 的 `routed.v` 塞回标准流程稳定 segfault"
  是同一现象。网表里含 3 个 `clkbuf_16`（时钟树根）与 2 条 `assign`；推测重复 CTS 或 assign 触发崩溃。
  ⇒ **pilot 固定用 pre-CTS 导出（R′ 臂）**，post-CTS 导出件保留在 `exports/s641_postcts/` 作证据，不参与判定。
- **re-entry gap 已在 R′ 三例实测**（R′ 三布局均值 − R_own）：s382 **+0.004 ns**、s641 **−0.223 ns**、
  s832 **−0.212 ns**（R′ 三布局均值 −0.8374 / −1.3529 / −1.2712；R_own −0.8414 / −1.1295 / −1.0587）。
  两条 |gap| > 0.15 ns ⇒ 触发 §4 的附带报告条款：**pre-CTS 修复变体在 s641/s832 上明显弱于 P1 的 post-CTS resizer 臂**，
  因此本实验的 R′ 只能读作"一个已知较弱的 resizer 变体终点"，H2 结论只限 **RF vs R′ 的同流程配对比较**，
  不得表述为"在 P1 resizer 之上仍有残余空间"。


### A3（2026-11-11，扁平导出网表的读入适配，在任何 RF 端点读数之前写下）

导出的网表是**扁平网表**，`write_verilog` 把时钟单元写成转义层次名：`sky130_fd_sc_hd__dfxtp_1 \DFF_14/_0_ (...)`；
而本机制按 W1 的层次模型（顶层实例化 `dff DFF_14`）识别触发器。结果是运行时直接失败：
`s382: no critical instances / endpoint D net (endpoint=DFF_14)`。为了让"同一份网表、同一流程"真的可比，
做了三层**仪器层适配**（只影响"能不能读这份网表"，不改任何判据）：

1. **实例名归一**：`exports/<c>/resized_gate_flat.v` 只把 `\DFF_x/_0_` 重命名为 `DFF_x`
   （s382 21 处 / s641 19 处 / s832 5 处），声明、连线、单元类型一字不改；由此 STA 报告端点、
   `dff_d_input_net` 与网表实例三者对得上。
2. **解析器增加多行实例起始检测**（`code/src/rseco/netlist.py::_verilog_statements`）：
   OpenROAD 把第一个命名连接写在实例头同一行（`... DFF_14  (.D(UC_17VD),`），不满足原有的
   "以 `(` 结尾"判据，整份网表会解析成 **0 个门**，随后 `logic_levels()` 缺 net 抛
   `KeyError: 'UC_17VD'`。新分支只在旧分支未命中时触发，既有 Yosys 网表的解析结果不变；
   全量回归 **1095 passed / 7 skipped / 156 subtests**。
3. 运行参数加 `--relaxed-instance-parse`（既有开关，用于扁平族）。

**影响面**：上述改动不改变 `min_physical_gain 0.010`、placed_ens 三布局均值、paired TNS/hold 不回退这些判据；
它只把"resizer 终点网表"变成机制可读的等价输入。**证据边界**：若 RF 臂在 `DFF_x` 归一化后的网表上
跑不出任何被接受候选，结论只能写成"在**这份** 扁平终点网表上未见残余空间"，并同时报告：
(a) 2 轮可行性试跑 s382 共 66 个候选、`physical_delta` 最大 +0.0088 ns（低于 0.010 门槛）；
(b) 该读数来自 2 轮/预算 80 的试跑，不是正式臂结果。


### A4（2026-11-11，对照臂必须与机制输入同字节，在任何 RF/R′ 端点读数被解读之前写下）

首次测量时对照臂读的是**原始导出网表** `exports/<c>/resized_gate.v`（转义名 `\DFF_14/_0_`），
而 RF 臂的输入是**归一化后的** `exports/<c>/resized_gate_flat.v`（`DFF_14`）。两者逻辑等价，
但字节不同，完整重布局/布线后会有微小读数差：s382 实测 **−0.0027 ns**（R′ −0.8470 vs 同网表重入 −0.8497）。
这个量级恰好与被判效应同阶，因此：

- **对照臂 R′ 改为测归一化网表**（`measure.py::netlist_for` 已改），即 R′ 与 RF **输入字节完全相同**，
  唯一差别是 RF 在上面接受过补丁。
- 首次那批（原始导出为对照）读数全部作废重测，缓存清空；`re-entry gap` 仍按 R′ 归一化版重算。
- 归因边界：`resized_gate.v` 与 `resized_gate_flat.v` 除 5–21 个 FF 实例名外完全相同
  （声明、连线、单元类型与参数一字未改，见 `_sanitize_names.py` 的 `rewrites=21/19/5`），
  故这一改动不影响 R′ 的物理含义，只消除实例名带来的布局随机性。
