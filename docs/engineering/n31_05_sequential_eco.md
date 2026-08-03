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

## 11. Gate sizing 修复器（G 策略）首轮实现（2026-08-03）

方向 B 的 failure-aware 混合修复（逻辑重写 R / gate sizing G / buffer insertion B）中 **G 策略（gate sizing）已完成首轮实现**，ISCAS89 sequential 实验暂不理想，原因审查中。

### 11.1 实现

- `src/rseco/gate_sizing.py`：解析 SKY130 cell 网表 + 逻辑深度 critical gate 选择 + 更大尺寸候选 + 贪心放大
- `scripts/run_gate_sizing.py`：Yosys mapping + OpenSTA 评估
- `tests/test_gate_sizing.py`：TDD 测试（三者当前均 untracked，未 commit）

### 11.2 实验（ISCAS89 sequential）

| 电路 | critical gates | baseline WNS | 结果 |
|---|---|---|---|
| s27 | 3 | -0.28 VIOLATED | 无改善 |
| s382 | 8 | -0.94 | 无改善 |
| s420 | 1 | -1.78 | 无改善 |

`sized_gates` 全空（未选出可放大的 gate）。

### 11.3 原因（审查中）

- 逻辑深度 critical gate 选择 ≠ OpenSTA 关键路径
- SKY130 尺寸（_1/_2/_4）delay 差异 < WNS 精度
- 电路太小（critical gate 数量少，无尺寸余量）

### 11.4 状态

- G 策略首轮实现完成，实验结论暂不入论文主表
- 待审查结论后决定：修正 critical gate 选择策略 / 换更大电路（如 ITC-99）/ 补 B（buffer insertion）策略做混合切换