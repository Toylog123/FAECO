# N31-05 SKY130 Sequential ECO 拓展设计

更新时间：2026-07-31

本文档是 N31-05 的设计文档，对应 P1 项 "SKY130 sequential ECO 拓展"。`paper/reviews/round1_self_audit.md` 列此项为 P1-1 (METH-01 sequential cone 未实现)。本文档不实施代码，仅给出 design 方向、SDC clock 扩展、reg-to-reg cone 算法、sequential benchmark 接入路径、TDD outline、Stage C 时间表。

## 1. 背景

当前 Stage B 8-case 全部是 combinational benchmark：
- ctrl / int2float / router / cavlc / dec / priority / adder / max 都是纯组合电路
- 8-case 全部 mapping 8/8 success + STA 8/8 success + slack_status=MET (INF)
- WNS / TNS / slack 全部 null（无 timing path）

**当前 limitation L31-02**：combinational 路径导致 OpenSTA `slack=null` / `slack_status=MET (INF)`，论文主表不能写 "real WNS/TNS 改善"。

**Stage A limitation L31-04**：failure_recovery `avg_iterations=1.0`，当前是 single-iteration proxy。

**Sequential ECO 拓展**同时解决：
1. METH-01 sequential cone：实现 reg-to-reg cone extraction
2. METH-12 candidate-specific timing gain：per-candidate STA 给出真实 WNS/TNS
3. X19 multi-iteration refinement：sequential 路径有真实 timing violation，可触发 failure-aware 循环

## 2. SDC 时钟信号扩展

当前 SDC（`src/rseco/sdc.py`）：
```
create_clock -name clk_virtual -period 10.000
set_load 0.050 [get_ports [all_outputs]]
set_driving_cell -lib_cell sky130_fd_sc_hd__buf_1 -pin X [get_ports [all_inputs]]
set_max_delay 0
```

**Sequential 扩展**：替换 virtual clock 为真实 clock + reg-to-reg 路径：
```
# 主时钟（替换 virtual clock）
create_clock -name clk_main -period 10.000 [get_ports clk]

# Generated clocks（如有 PLL）
# create_generated_clock -name clk_div2 -source clk_main -divide_by 2 ...

# Input delay（reg 输出到 combinational 输入）
set_input_delay -clock clk_main 2.000 [get_ports -filter {direction == input}]

# Output delay（combinational 输出到下一级 reg 输入）
set_output_delay -clock clk_main 2.000 [get_ports -filter {direction == output}]

# Max delay / min delay 分析
set_max_delay 0  (or set_min_delay 0 for hold analysis)

# 可选：clock uncertainty / clock latency
# set_clock_uncertainty 0.100 clk_main
# set_clock_latency 1.000 clk_main
```

`SdcConfig` 需要扩展 `clock_port` 字段（指定哪个 input port 是主时钟）。

## 3. Reg-to-Reg Cone Extraction 算法

Combinational fanin cone 抽取仅沿 forward edge 追溯（`src/rseco/graph.py` `extract_cone`）。Sequential reg-to-reg cone 需要：
- 起点：sequential 输出（reg 输出端口 `Q` 或 `q`）
- 终点：sequential 输入（reg 数据端口 `D` 或 `d`）
- 中间：combinational logic + 同步 clock domain

```
1. start_v ← reg output port of start register
2. end_v ← reg input port (D/d) of end register
3. BFS forward from start_v (along combinational edges only)
4. Skip sequential edges (reg → reg direct connections are clock-domain transfers)
5. Until end_v reached
6. V_C ← vertices in path
7. return (V_C, E_C, start_reg, end_reg, clock_domain)
```

约束：
- 当前实现只覆盖 single-clock-domain；multi-clock 需时钟域分析（`create_generated_clock` + 跨域路径）
- reg-to-reg cone 不包含寄存器本身（仅 combinational logic）
- clock skew / setup-hold 关系由 OpenSTA 内部建模

## 4. Sequential Benchmark 接入路径

### 4.1 EPFL sequential benchmark

EPFL `v2025.1` wave 1+2 8 个 benchmark 全部 combinational。Sequential EPFL benchmark 候选：

| benchmark | 描述 | 推荐 stage |
|---|---|---|
| `des_perf` | Performance-critical design（system） | stage C 候选 |
| `pci_bridge32` | PCI 桥（system） | stage C 候选 |
| `mem_ctrl` | Memory controller | stage C 候选 |
| `usb_phy` | USB PHY | stage C 候选 |

EPFL `v2025.1` 包含的 sequential benchmark 总数需核对（待扩展 wave 3+ 时确认）。

### 4.2 ISCAS89 sequential benchmark

为快速验证 sequential ECO 流程，可先用 ISCAS89（`s27` / `s208` / `s298` / `s386` / `s420` / `s510` 等）：

| benchmark | 描述 | 难度 |
|---|---|---|
| `s27` | 小型 4 flip-flop | 入门 |
| `s208` | 中型 8 flip-flop | 中等 |
| `s298` | 14 flip-flop | 中等 |
| `s386` | 6 flip-flop | 中等 |
| `s420` | 16 flip-flop | 中等 |
| `s510` | 6 flip-flop | 较难 |

ISCAS89 来源同样是 `jpsety/verilog_benchmark_circuits` repo，许可不完备，仅作本地 smoke。

## 5. TDD 测试 outline

`tests/test_sequential_eco.py`：

| 测试 | 输入 | 期望 |
|---|---|---|
| `test_sdc_with_real_clock_port` | SdcConfig.clock_port="clk" | SDC 含 `create_clock -name clk_main -period 10 [get_ports clk]` |
| `test_sdc_with_no_clock_port_falls_back_to_virtual` | SdcConfig.clock_port=None | SDC 含 virtual clock (向后兼容) |
| `test_extract_reg_to_reg_cone_basic` | EPFL sequential benchmark + start_reg + end_reg | cone 包含 combinational logic 不含 reg |
| `test_extract_cone_skips_sequential_edges` | s27 netlist | start_reg 的 Q 节点到 end_reg 的 D 节点不经过 reg 边界 |
| `test_opensta_with_real_clock_runs` | sequential benchmark + 真实 clock SDC | StaResult.status=success, wns/tns 非 null |
| `test_sequential_opensta_parses_path` | STA 输出含 reg-to-reg path | parser 提取 startpoint / endpoint / path slack |
| `test_multi_iteration_refinement_triggers_on_real_timing_failure` | X19 loop + sequential benchmark + bad patch | residual failure 触发 multi-iteration |

## 6. Stage C 时间表

按 PM23 (M5) 和 N31-05 推进：

| 阶段 | 工作 | 时间预估 | 依赖 |
|---|---|---|---|
| Stage C-1 | `src/rseco/sdc.py` 加 `clock_port` 字段 | 1 周 | 当前 SdcConfig 已 ready |
| Stage C-2 | `src/rseco/graph.py` 加 reg-to-reg cone extraction | 1-2 周 | 当前 extract_cone 已实现 |
| Stage C-3 | 接入 ISCAS89 s27 / s208 / s298 smoke | 1 周 | Stage C-1 + C-2 完成 |
| Stage C-4 | 接入 EPFL sequential benchmark (des_perf / pci_bridge32) | 1-2 周 | Stage C-3 验证流程 |
| Stage C-5 | Stage C 端到端：8-case sequential mapping + STA | 2 周 | Stage C-4 完成 |
| Stage C-6 | X19 multi-iteration refinement 在 sequential 路径上跑 | 2 周 | PM22 X19 设计获批 |
| Stage C-7 | 论文 round 3 sequential 章节 | 1 周 | Stage C-5 + C-6 完成 |

总计约 9-11 周（约 2-3 个月）。

## 7. 设计边界与限制

### 7.1 N31-05 不做的事

- 不实现 multi-clock 域分析（stage D 之后）
- 不实现 timing exception（false path / multicycle path）
- 不实现 IR drop / clock tree synthesis（pre-CTS 阶段不适用）
- 不修改 Stage A 5-case 端到端（保持向后兼容）
- 不实现 dynamic ECO 增量

### 7.2 与现有代码的集成点

- 调用方：`scripts/run_stage_b_pre_layout_sta.py` 加 `--sequential` 标志
- 输入：sequential Verilog + SDC with clock_port
- 输出：同 Stage B 端到端，但 mapping + STA 对 reg-to-reg path
- 依赖：yosys ABC 已有 `synth -flatten` 支持 reg-to-reg cone（待验证）

## 8. 处置建议

按优先级：

1. **Stage C-1 + C-2 优先**：SDC clock_port + reg-to-reg cone 是 Stage C 入口
2. **Stage C-3 用 ISCAS89**：许可不完备但流程验证足够
3. **Stage C-4 用 EPFL sequential**：license 完备，作为论文主集
4. **Stage C-5 + C-6 并行**：8-case sequential + X19 multi-iteration

## 9. 后续修订

- 用户决定是否启动 Stage C（涉及 9-11 周工作量 + N31-05 + PM23 + X19 三个 P0/P1 启动）
- 不启动时，本设计文档保留为 stage C 入口；round 2 修订时 `method_rewrite_readiness.md` METH-01 保持 partial
- N31-05 启动时同步更新 `method_rewrite_readiness.md` METH-01 → ready
- 当前 round 1 自审稿 P1-1 (sequential cone) 与 P1-2 (X19 multi-iteration) 在 Stage C 启动后升级为 done

## 10. 当前状态总结（2026-08-03 更新）

- **技术路径已验证**：ISCAS89 sequential 全链路跑通（s27/s382/s420/s641 等 8 个门级电路）
  - Yosys `synth + dfflibmap + abc -liberty` → 纯 SKY130 cell（DFF → `dfxtp_1`）
  - OpenSTA 输出真实 reg-to-reg timing path + slack（10ns→MET 7.6-9.2，0.5ns→VIOLATED -0.28 至 -1.86）
- **数据已获取**：ISCAS89 17 电路（ispras，Apache-2.0，manifest 归档），8 个门级可直接用
- **方向 B（时序 ECO）创新点已定**：failure-aware 混合修复（逻辑重写 R / gate sizing G / buffer insertion B 自适应切换）
- 下一步：Stage C-1/C-2（SDC clock_port + reg-to-reg cone）基础上实现 G/B 修复器 + 混合切换
- ITC-99 作为更大规模主实验（待获取）

## 11. Gate sizing 修复器（G 策略）实现状态（2026-08-03）

方向 B 的 failure-aware 混合修复（逻辑重写 R / gate sizing G / buffer insertion B）中 **G 策略（gate sizing）已完成实现**。首轮实验无改善，经审查智能体定位根因并修复后，ISCAS89 sequential 上 **3/4 电路真实改善**。

### 11.1 实现

- `src/rseco/gate_sizing.py`：解析 SKY130 cell 网表 + 逻辑深度 critical gate 选择 + 更大尺寸候选 + 贪心放大
- `scripts/run_gate_sizing.py`：Yosys mapping + OpenSTA 评估
- `tests/test_gate_sizing.py`：TDD 测试

### 11.2 审查修复（commit `ef74d1d`，108 测试全绿，已 push）

审查智能体定位首轮"无改善"的三个根因并修复：

- **RC1（硬阻断）**：`run_opensta()` 的 `link_design` 用了 parent 目录名（`cand/`），导致所有 candidate link 失败、WNS=None、贪心永不接受 → 改为从 Verilog module 声明解析 top_module
- **RC2（方法）**：逻辑深度选门 ≠ OpenSTA 真实关键路径 → 改为从 `report_checks` 输出解析关键路径实例
- **贪心改进**：试所有更大尺寸选最优（原来只试第一个）

### 11.3 修正后实验（ISCAS89, period 0.5ns）

| 电路 | baseline WNS | final WNS | 改善 |
|---|---|---|---|
| s27 | -0.28 | -0.20 | +0.08 |
| s382 | -0.94 | -0.94 | 0.0（瓶颈 `lpflow_inputiso1p_1` 无更大尺寸变体）|
| s420 | -1.78 | -1.41 | +0.37 |
| s641 | -1.86 | -1.43 | +0.43 |

**3/4 电路真实改善**；修复后 `sized_gates` 正常选出并放大（已非空）。

### 11.4 s382 天花板 → 混合策略动机（创新点）

s382 显示**单手段（gate sizing）天花板**：关键路径瓶颈 cell（`lpflow_inputiso1p`）无更大尺寸可换，故 WNS 无法继续改善。这正印证 failure-aware 混合修复（逻辑重写 R / buffer insertion B）的必要性——gate sizing 单手段不足时切换到 R/B 策略，是本项目方向 B 的核心创新点。

### 11.5 状态

- G 策略实现完成，ISCAS89 3/4 真实改善，实验结论可入论文主表（标注方法边界：单手段天花板）
- 下一步：R/B 策略实现 + 混合切换（结合 s382 天花板 case 验证自适应切换逻辑）

## 12. R/B 策略与混合修复实现状态（2026-08-03 晚）

方向 B 的 failure-aware 混合修复（逻辑重写 R / gate sizing G / buffer insertion B）**已全部实现并验证**：三类策略生成候选后均经 OpenSTA 实测，只接受严格改善 WNS 的改动；多轮循环每轮重解析关键路径，持续解决新出现的瓶颈。

### 12.1 实现
- `src/rseco/logic_rewrite.py`（R）：Liberty function 规范化（变量按首现重命名）+ 跨 family 等价候选（如 `lpflow_inputiso1p_1` 的 `X=A|SLEEP` → `or2_*`）+ pin 映射重写
- `src/rseco/buffer_insertion.py`（B）：高扇出 net 检测 + 输入/输出 pin 插 buffer（含 wire 声明与重连）
- `src/rseco/gate_sizing.py`（G）：同 family 更大尺寸候选（沿用 11 节）
- `scripts/run_hybrid_repair.py`：多轮贪心（`--rounds`）+ `--enable-buffer` 开关 + 每候选独立子目录与 `candidate_trials` 记录（可审计）
- `tests/test_logic_rewrite.py`（9）+ `tests/test_buffer_insertion.py`（5）+ `tests/test_gate_sizing.py`（6）共 20 个单元测试全绿

### 12.2 实验（ISCAS89, period 0.5ns, rounds=6）
| 电路 | baseline WNS | G/R 单混合 | G+R+B（rounds=6） | 改善 |
|---|---|---|---|---|
| s27 | -0.28 | -0.20 | **-0.01** | +0.27 |
| s382 | -0.94 | -0.92 | **-0.80** | +0.14 |
| s420 | -1.78 | -1.41 | **-0.23** | +1.55 |
| s641 | -1.86 | -1.40 | **-0.57** | +1.29 |

**4/4 电路大幅改善**；s382 由 R 突破 G 单手段天花板，其余电路由 B 策略（高扇出节点插 buffer 分担输入电容）贡献主要改善。

### 12.3 关键结论
- **B 策略在 pre-layout ideal-net 下有效**：高扇出节点（如 s420 的 `_066_` nor4 输出、`_057_` and4 输出）的输入电容负担被 buffer 分担，改善超过插入延迟——推翻 ideal-net 下 B 无效的假设，必须实测验证而非主观预判
- **多轮自适应是关键**：单轮只能解决初始关键路径；rounds=6 时 s641 从 -0.86 继续收敛到 -0.57（第 4-6 轮解决 `_098_`/`_079_`/`_082_`/`_159_` 等新瓶颈）
- **可审计性**：每候选独立子目录 + `candidate_trials` 记录 wns/accepted；审查核对 4 电路 final WNS 与 sta.log 一致、29 处改动全部真实、无被误拒的更好候选
- **方法边界（诚实记录）**：当前为 ideal-net pre-layout 验证；post-layout 长线负载下 G/B 的相对贡献可能变化，需 Stage C 后续验证；buffer 插入在真实时钟路径上需 CTS/clock-aware 约束保护
