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

### 12.2 实验（ISCAS89, period 0.5ns, rounds=10, multi_path + tns-aware, 8 电路）
| 电路 | baseline WNS | 旧版(非法多驱) | 修复后 | 策略 | 审计 |
|---|---|---|---|---|---|
| s27 | -0.28 | -0.01 | **-0.01** | 4B+1R | ok |
| s382 | -0.94 | -0.10 | **+0.02 (MET)** | 53B+1G | ok |
| s420 | -1.78 | -0.08 | **-0.01** | 35B | ok |
| s641 | -1.86 | +0.01 | **-0.02** | 35B+3G+1R | ok |
| s713 | -1.86 | +0.01 | **-0.01** | 37B+6G+1R | ok |
| s820 | -1.42 | -0.63 | **-0.20** | 78B+3G+1R | ok |
| s832 | -1.15 | -0.47 | **-0.47** | 67B+4G+1R | ok |
| s953 | -1.48 | -0.19 | **-0.09** | 149B+6G+1R | ok |

**修复前版本因 buffer 多驱 bug（同一原始网多 sink 共用 net+__buf，多 buffer 并联驱动一网）产生非法网表，OpenSTA 结果虚高，旧版数据不可信。修复（commit 5c70b30：新网名嵌入 instance+pin、输出引脚跳过、每轮重解析）后重跑：8/8 电路完成，s382 收敛到 MET（+0.02），其余接近收敛；全部 netlist_audit ok（0 多驱）。**

### 12.3 关键结论
- **B 策略在 pre-layout ideal-net 下有效**：高扇出节点（如 s420 的 `_066_` nor4 输出、`_057_` and4 输出）的输入电容负担被 buffer 分担，改善超过插入延迟——推翻 ideal-net 下 B 无效的假设，必须实测验证而非主观预判
- **多轮自适应是关键**：单轮只能解决初始关键路径；rounds=6 时 s641 从 -0.86 继续收敛到 -0.57（第 4-6 轮解决 `_098_`/`_079_`/`_082_`/`_159_` 等新瓶颈）
- **可审计性**：每候选独立子目录 + `candidate_trials` 记录 wns/accepted；审查核对 4 电路 final WNS 与 sta.log 一致、24 处改动全部真实、无被误拒的更好候选; audit-trail fix (commit a82ecf8): round/trial_id fields, accepted by trial_id only, same-inst reset; re-run numbers unchanged, accepted==applied, strict per-round improvement
- **方法边界（诚实记录）**：当前为 ideal-net pre-layout 验证；post-layout 长线负载下 G/B 的相对贡献可能变化，需 Stage C 后续验证；buffer 插入在真实时钟路径上需 CTS/clock-aware 约束保护

- **原"策略空间饱和"结论已被推翻（重要）**：旧版 s820/s832 卡在 -1.11 的真实原因是 runner 仅从默认 `report_checks` 解析单条关键路径（6 实例），策略空间看似饱和；改为显式收集全部违例路径实例（multi_path=True，107+ 实例）后，s820 从 -1.42 到 **-0.63**、s832 从 -1.15 到 **-0.47**，证明瓶颈不是库单元上限而是关键路径覆盖不足。教训：时序修复必须先覆盖全部违例路径，否则会误判策略失效。

### 12.4 buf_8/16 扩展实验（2026-08-04，负面结论）

SKY130 库含 buf_1/2/4/8/16，原实验只用 1/2/4。用 buf_1/2/4/8/16 全试重跑 s832（rounds=10, multi_path, tns-aware, workers=4）：

| 配置 | final WNS | 应用改动 | buf_8/16 接受数 |
|---|---|---|---|
| buf_1/2/4 | -0.47 | 72（67B+4G+1R） | 不适用 |
| buf_1/2/4/8/16 | **-0.61（更差）** | 72（67B+4G+1R） | **0**（1080 trials 全拒） |

结论：pre-layout ideal-net 下大 buffer（buf_8/16）输入电容大、无 wire load 可摊薄，插入只会拖累前级；buf_8/16 应排除在候选集外。与 12.3 的 B 策略有效结论不矛盾——有效的是 buf_1（高扇出负载分担），不是大尺寸 buffer。

### 12.5 决策层（strategy selector，2026-08-04 实现）

从 8 电路 12205 条 trial 数据归纳 cell-type 到策略优先级决策表（src/rseco/strategy_priority_table.json，75 个 cell type）：

- **绝大多数 cell type 下 B 是唯一有正接受率的策略**（如 clkinv_1: B 0.15 / R 0.00 / G 0.00），R/G 接受率几乎全为 0
- 与 buf_8/16 负面结论一致：有效的是 buf_1 的负载分担，不是大 buffer
- runner 新增 --strategy-priorities auto：候选按决策表优先级排序，把"全搜索"变成"预测驱动"（src/rseco/strategy_selector.py + tests/test_strategy_selector.py 4 项测试）

下一步：效率对比实验（同 WNS 下决策驱动 vs 全搜索的 STA 调用数）验证决策层价值。

### 12.6 外环真实 WNS 闭环 + 决策层 + early-stop（2026-08-04 晚）

G/R/B 内环之外，外环（patch 粒度）failure-aware refinement 已接真实 OpenSTA（src/rseco/opensta.py 的 run_opensta_sequential + src/rseco/real_wns.py 的 RealWnsEvaluator）：把 cut 门映射到真实 SKY130 网表，对关键路径实例生成 R/G/B 候选、每候选独立实测、只接受严格 WNS 改善。

反馈消融（beam=1，8 电路）：6/8 需学习的电路（s27/s382/s420/s820/s832/s953）反馈 ON 第 2 轮经 critical_path_cover 成功、OFF 8 轮全失败；2/8 首候选可修（s641/s713）。决策层 + early-stop 全 8 电路（beam=1 + 反馈 ON，period 0.5ns）：

| 电路 | 基线 WNS | 反馈ON beam1 STA | 决策层+early-stop STA | final WNS | 轮数 |
|---|---|---|---|---|---|
| s27 | -0.28 | 8 | **4** | -0.21 | 2 |
| s382 | -0.94 | 12 | **8** | -0.93 | 2 |
| s420 | -1.78 | 12 | **3** | -1.75 | 2 |
| s641 | -1.86 | 3 | **1** | -1.85 | 1 |
| s713 | -1.86 | 3 | **1** | -1.85 | 1 |
| s820 | -1.42 | 18 | **3** | -1.36 | 2 |
| s832 | -1.15 | 43 | **3** | -1.12 | 2 |
| s953 | -1.48 | 11 | **4** | -1.38 | 2 |

合计候选 STA 110→27（-75%），8/8 WNS 持平或更好。三层机制：外环 F4 反馈定位 critical_path_cover cut（学习哪里改）→ 内环决策层按 cell-type 优先级排序策略（经验复用怎么改）→ early-stop 首个严格改善即停（效率）。诚实边界：early-stop 是贪心，WNS 与全评估可能略异（本次 s382/s420/s820 反超，属贪心轨迹差异）；决策表对未见 cell type 回退 R,G,B 顺序。实验产物 experiments/20260804_outerloop_decision/（A-only 不入库）；全量 195 passed + 1 subtest。
### 12.7 ITC-99 跨基准泛化验证（2026-08-04 晚）

ISCAS89 8 电路决策层/外环闭环之外，进一步把同一套流程（外环 F1-F5 反馈 + 决策层策略优先级表 + beam=1 + early-stop + 真实 OpenSTA，period 0.5ns）直接迁移到 ITC-99 基准族做跨基准泛化验证。基础设施：

- `scripts/convert_itc99_blif_to_v.py`：ITC-99 的 .blif 是无时钟四字段 .latch（d q 0），Yosys 0.9 read_blif 转出 $ff/$lut 无法回读；转换器在 yosys 会话内先 `techmap`（$lut->$_MUX_ 三元 assign、$ff->$_FF_），再规范化模块名、加全局 CK 端口、把 $_FF_ 改写为行为级 dff（与 ISCAS89 s820/s832/s953 预处理同约定）。techmap 同时修复了 b14/b15/b17 此前 $shr 桶形移位展开导致的 Yosys 0.9 32 位 std::bad_alloc OOM。
- `scripts/convert_itc99_bench_to_blif.py`：b18/b19 发行版 .blif 截断（只剩 latch、逻辑表丢失），从上游恢复完整 .bench（edf2bench 门级格式：b18 3320 DFF/113K 门，b19 6642 DFF/231K 门）并转为标准 BLIF。
- `scripts/run_outerloop_batch.py --iscas89-dir`：batch 并行 driver 支持指向任意电路目录。

结果（19 个可跑电路，17/19 真实 WNS 改善；b18/b19 因 Yosys 0.9 32 位 read_verilog 内存限制无法映射，诚实排除）：

| 电路 | 基线 WNS | final WNS | 接受修复 | STA |
|---|---|---|---|---|
| b01 | -0.59 | -0.59 | 无（G 全有害、无 R 等价候选） | 44 |
| b02 | -0.21 | -0.21 | 无（同上） | 38 |
| b03 | -1.99 | -1.84 | G o41ai_1->2 | 3 |
| b04 | -2.15 | -2.10 | G xnor2_1->2 | 3 |
| b05 | -3.83 | -3.81 | G nor3b_1->2 | 3 |
| b06 | -0.52 | -0.51 | G o22ai_1->2 | 1 |
| b07 | -2.34 | -2.33 | G o21ai_0->1 | 1 |
| b08 | -1.29 | -1.26 | G and2_0->1 | 4 |
| b09 | -1.12 | -1.11 | G nor4_1->2 | 8 |
| b10 | -1.42 | -1.18 | **R nor4bb->and4bb** | 3 |
| b11 | -2.68 | -2.67 | **R lpflow_inputiso1p->or2** | 3 |
| b12 | -2.68 | -2.42 | G nor4_1->2 | 3 |
| b13 | -0.92 | -0.89 | G o21a_1->2 | 7 |
| b14 | -12.23 | -12.19 | G or4_1->4 | 5 |
| b15 | -12.35 | -12.30 | **R nor4bb->and4bb** | 3 |
| b17 | -16.10 | -15.62 | G nor4b_1->2 | 4 |
| b20 | -11.20 | -11.17 | G and3b_1->4 | 5 |
| b21 | -11.29 | -11.27 | G and3b_1->4 | 5 |
| b22 | -12.08 | -12.06 | G mux2_1->2 | 1 |

关键结论：

1. **跨基准泛化成立**：ISCAS89 上归纳的"先按 cell-type 决策表排序、实测只接受严格改善"策略在 ITC-99 上直接复用，19 个可跑电路 17/19 真实改善（89.5%），大电路 b14/b15/b17/b20/b21/b22 全部成功且多为 G sizing 微幅改善（-0.03~-0.48ns）。
2. **R 策略机理跨电路重现**：b10/b15 的 nor4bb->and4bb（互补同构）与 b11 的 lpflow_inputiso1p->or2 与 ISCAS89 s382 的 R 修复机理一致——同功能不同库单元延迟差，pre-layout 下无 wire load 可借力时 R 比 G 更稳。
3. **失败模式诚实记录**：b01/b02 关键路径 cell（and3b/or4/o211ai 等）无 R 等价候选，G sizing 全部有害（输入电容拖累前级），8 轮反馈无法改进——与 ISCAS89 s382 的 G 失效机理一致，证明"实测接受/拒绝"而不是盲信 G 的必要性。
4. **工具链边界**：b18/b19（23-46 万门）超出 Yosys 0.9 32 位能力（read_verilog bad_alloc），属工具链限制而非方法限制；已用完整 .bench 源恢复并转换，待 64 位 Yosys/OpenROAD 接入后可补跑。
5. **效率**：19 电路外环合计 151 次候选 STA（决策层 + early-stop 生效），小电路 4 并行 45s、大电路 2 并行 5-6 分钟。

实验产物：experiments/20260804_itc99_batch_smoke/、experiments/20260804_itc99_outerloop/、experiments/20260804_itc99_outerloop_large{,_2}/（A-only 不入库）；转换器与 batch driver 增强已 commit（ddb2d39）。


### 12.8 b18/b19 大电路补全 + 现实 period 协议（2026-08-04 深夜）

12.7 中 b18/b19 因 Windows Yosys 0.9 32 位内存限制被诚实排除；当晚发现 WSL2 Ubuntu 已有 64 位 Yosys 0.33（x86_64），直接打通大电路验证：

- **工具链突破**：`run_yosys_mapping` 增加 `yosys_cmd` 参数（WSL2 模式）+ `_to_wsl` 修复（相对路径先 resolve 再转 /mnt/d）+ timeout 300→1500；runner 增加 `--yosys-wsl` 与 `--skip-mapping`（复用已映射网表）。b18（37.6 万门）映射 6 分钟、b19（75.5 万门）映射约 15 分钟，峰值内存 4.7GB。

- **0.5ns 协议（27-36 倍过约束）**：b18 基线 -13.34→修复 -13.27（接受 G maj3_1→maj3_2，24 STA）；b19 基线 -17.44→修复 -16.0（接受 R clkinv_1→bufinv_8，59 STA）。关键发现：b19 的 1.44ns 改善来自 R 策略，证明 pre-layout 大电路上等价替换才是改善主力；0.5ns 下 WNS 绝对值巨大但非现实 ECO 场景。

- **现实 period 协议（95% CP）**：按原始关键路径的 95% 设周期（b18=13.15ns→WNS -0.69，b19=17.04ns→WNS -0.90），落在现实 ECO 区间。修复结果：

| 电路 | period | 基线 WNS | final WNS | 接受修复 | TNS 变化 | STA |
|---|---|---|---|---|---|---|
| b18 | 13.15ns | -0.69 | -0.62 | G maj3_1→maj3_2 | -28.18→-24.7 | 24 |
| b19 | 17.04ns | -0.90 | **+0.54 (MET)** | R clkinv_1→bufinv_8 | -22.71→0.0 | 59 |

结论：**大电路上 failure-aware 修复在现实约束下可收敛时序**（b19 达成 MET、TNS 清零）；b18 改善小是结构边界——关键路径 38 个实例中 36 个为 XOR/MAJ/XNOR 复杂门（乘法器结构），SKY130 中这些门无等价替换候选、G 在 pre-layout 仅微调，诚实记录该边界。

### 12.9 联合修复（JOINT multi-gate sizing，2026-08-05）

12.8 中 b18 单门 G 仅把 -0.69 修到 -0.62。根因：pre-layout 理想网络下大尺寸 cell 输入电容增大拖累前级，单门 upsizing 收益常被抵消（实测 *070*→o21a_4 反使 WNS 变差）。为此新增**联合修复（JOINT）**：把 actionables 中 top-k 个可 G 门同时升级成一个 JOINT 候选，一次 OpenSTA 实测；只接受 WNS 严格改善者。

- **实现**：`src/rseco/real_wns.py` 增加 `joint_k` 参数（`_apply_joint` 批量替换 + `_eval_one` JOINT 分支 + `__call__` 生成联合候选）；`scripts/run_outerloop_real_wns.py` / `run_outerloop_batch.py` 增加 `--joint-k` 透传；`tests/test_joint_candidates.py` 3 项测试（禁用默认单 job、启用生成 JOINT、`_apply_joint` 批量替换验证）。commit `1dab727`。
- **b18 实验结果（period 13.15ns，joint_k=4）**：baseline -0.69 → JOINT **-0.56**（TNS -28.18→-22.23），25 次候选 STA（iter1-3 同门 _649907_ G 单候选 o221ai_1→2/4 均无改善，触发权重细化换 cut；iter4 random_cut 覆盖 18 个单门候选 + 1 个 JOINT）。JOINT 候选同时升级 4 门：nand3b_1→nand3b_2（_646058_）+ maj3_1→maj3_2（_646060_/_646062_/_646065_）。18 个单门候选最好仅 -0.62，JOINT 唯一达到 -0.56 并被接受；独立复跑 `run_opensta` 核验一致（BASE -0.69 / JOINT -0.56），且优于单门 G 的 -0.62。
- **b19 对照实验（period 17.04ns，joint_k=4）**：baseline -0.90 → +0.54（MET，TNS 0.0），60 次候选 STA（iter1-3 各 2 个 G 单候选无改善，iter4 54 个候选含 R + JOINT）。第 4 轮 **R 候选 clkinv_1→bufinv_8 达到 +0.54 被接受，JOINT 也达 +0.18（MET）但被正确拒绝**——决策层实测择优而非先验选 R/G。结论：b19 上单候选 R 已足够，JOINT 不劣化（+0.18 仍 MET）但非最优；与 b18 形成对照：**联合修复在单门 G 到顶的电路上提供额外增益（-0.62→-0.56），在 R 可达 MET 的电路上不干扰择优**。
- **结论**：多门联合尺寸调整在 pre-layout 也有效——单门 G 因输入电容拖累前级常被拒，联合升级把多个关键门一起增强，净收益为正；JOINT 是 R/G 混合之外新增的 G^J 修复维度，代价是每轮多一次 STA（本次仅 1 个联合候选、25 总 STA 仍远小于全搜索）。

### 12.10 物理感知验证（SPEF 寄生参数扫描，2026-08-05）

评审短板第 1 条：pre-layout ideal-net 未考虑布线延迟。WSL2 无 OpenROAD/PDK（无法真实 P&R），采用诚实可做的**寄生参数感知（parasitic-aware）验证**：解析 mapped 网表 → 按扇出估计线长（unit_len_um × sqrt(fanout)）→ 用典型 SKY130 M2/M3 RC（0.09 Ω/µm、0.21 fF/µm）生成标准 SPEF → OpenSTA read_spef 在含线 RC 下重测 WNS。

- **实现**：`src/rseco/spef.py`（parse_mapped_verilog 顶层模块识别 + estimate_net_rc + build_spef/write_spef）+ `scripts/run_parasitic_aware_check.py`（baseline/repaired × ideal/SPEF 四组 STA）+ `tests/test_spef.py`（6 项：顶层识别、多模块 wrapper、RC 随扇出增长、SPEF 结构、roundtrip、pinless 网跳过）。
- **s382（R lpflow_inputiso1p→or2_1，period 0.5ns）**：ideal 下 -0.94→-0.93（+0.01）；SPEF 下改善随线长变化——5µm 时 +0.03（改善放大），10µm 起被淹没（0.0）。小电路改善幅度本身仅 0.01ns，物理负载下容易淹没，属诚实边界。
- **b18（JOINT 4 门联合升级，period 13.15ns）**：ideal 下 -0.69→-0.56（+0.13）；SPEF 下改善随线长单调衰减：

| 线长模型 | baseline WNS | JOINT WNS | 改善 |
|---|---|---|---|
| ideal（无寄生） | -0.69 | -0.56 | **+0.13** |
| 2 µm | -0.92 | -0.81 | **+0.11** |
| 5 µm | -1.25 | -1.18 | +0.07 |
| 10 µm | -1.80 | -1.77 | +0.03 |
| 20 µm | -3.05 | -3.05 | 0.0 |
| 40 µm | -6.63 | -6.63 | 0.0 |

- **结论**：联合修复收益在轻/中寄生负载下保持（2µm 时 +0.11，几乎不损失），重负载（20µm+）下被线延迟主导而消失。这量化了 pre-layout→post-layout 的收益保持边界：物理感知不是"有或无"，而是随线长的连续衰减；同时诚实记录 SPEF 模型是估计（无真实 P&R），重负载归零是该模型的保守结论。

### 12.10 在线自适应决策层 v2（2026-08-05）

12.5 的决策层 v1 是离线归纳的静态 per-cell-type 优先级表（12205 trial -> strategy_priority_table.json），跨电路 leave-one-out 验证零损失，但一旦冻结无法适应目标电路。评审短板 2（决策智能性）要求引入自适应决策。实现 v2 在线自适应层（src/rseco/adaptive_selector.py）：

- 算法：每个 cell type 维护 UCB1 风格分数 accept_rate + alpha * sqrt(log(global_n)/n_kind) + 指数衰减 gamma=0.98（每次 record 全部臂衰减），实测后实时更新；未试臂固定 0.5 探索分（避免纯 UCB 乐观先验把 B 顶到首位，与 pre-layout 领域先验冲突）。cold start 回退 R/G/B；snapshot JSON 可序列化。
- 接入：RealWnsEvaluator(adaptive=True)（--adaptive 开关），_candidates_for 改用在线顺序，__call__ 每个实测 trial 回写 record；write_trials 输出 adaptive_snapshot。batch runner 同步透传。commit 5529c8b/5e623e8。
- 8 电路无先验对照实验（experiments/20260805_adaptive_iscas89/，A-only）：完全不用静态表冷启动，8/8 全部修复成功：

| 电路 | baseline | static final (STA) | adaptive final (STA) |
|---|---|---|---|
| s27 | -0.28 | -0.21 (4) | -0.21 (4) |
| s382 | -0.94 | -0.93 (8) | -0.93 (8) |
| s420 | -1.78 | -1.75 (3) | -1.75 (3) |
| s641 | -1.86 | -1.85 (1) | -1.85 (1) |
| s713 | -1.86 | -1.85 (1) | -1.85 (1) |
| s820 | -1.42 | -1.36 (3) | **-1.28 (18)** |
| s832 | -1.15 | -1.12 (3) | -1.12 (43) |
| s953 | -1.48 | -1.38 (4) | -1.38 (11) |

- 关键结论（诚实双向）：
  1. 无需人工先验：在线层从零开始 8/8 收敛到与静态表同等（7/8）或更优（s820 -1.28 vs -1.36）的 WNS，证明修复质量不依赖人工归纳表。
  2. s820 案例：在线探索发现静态表遗漏的 G and2_0->and2_4 修复（-1.28），静态表 3 次 STA 只能到 -1.36。
  3. 代价是探索开销：无先验冷启动导致 s820/s832/s953 探索更多（STA 18/43/11 vs 3/3/4），8 电路合计 88 vs 27（+226%）。静态表的价值 = 压缩探索；两者互补，最佳实践是先 warm-start（静态表或历史 trial 预训练）再在线微调。

### 12.11 寄生参数感知（SPEF）验证（2026-08-05）

评审短板 1（物理感知）的量化落地：用 OpenSTA read_spef 对同一 baseline/repaired 网表分别跑 ideal 与 SPEF 两种 STA（src/rseco/spef.py 生成估计 net RC，默认 40um/unit；scripts/run_parasitic_aware_check.py 跑 4 组）。真实数据（experiments/20260805_parasitic_{s382,b18}/，A-only）：

| 电路 | period | ideal baseline | ideal repaired | SPEF baseline | SPEF repaired |
|---|---|---|---|---|---|
| s382 | 0.5ns | -0.94 | -0.93 (+0.01) | -2.37 | -2.37 (0.00) |
| b18 | 13.15ns | -0.69 | -0.56 (+0.13) | -6.63 | -6.63 (0.00) |

结论（诚实负面导向）：**pre-layout 理想网络下有效的修复在加入寄生 RC 后改善归零**——证明物理负载对修复有效性影响巨大，量化了物理感知 ECO 的必要性，也是方法当前最重要的边界。SPEF 为简化估计（lumped RC、非真实 P&R 版图），完整 OpenROAD + PDK LEF/DEF 流程未接入（见 limitation L31-01）；作为方法边界而非成熟物理验证。commit 0b44eb0；论文 sec:parasitic + limitation 更新 commit a722c03；232 测试全绿。
### 12.12 Hold 时间修复（2026-08-05，评审短板 3 场景扩展）

评审短板 3 要求扩展场景（Hold 违例修复）。pre-layout 理想网络基准没有天然 hold 违例（min slack 均匀为正），因此注入 **受控 hold 场景**：OpenSTA set_clock_uncertainty -hold 0.8ns，让 B（buffer insertion）策略修复最差 min（hold）路径。

实现（commit 4a7f226）：
- src/rseco/opensta.py：run_opensta_sequential 增加 hold_uncertainty / min_path，解析 worst slack min 返回 min_slack/min_slack_status；
- src/rseco/real_wns.py：RealWnsEvaluator 增加 hold_mode，接受"严格改善 worst min slack 且不劣化 setup WNS"的候选（与 setup 循环同一 failure-aware 接受规则）；
- src/rseco/hold_repair.py + scripts/run_hold_repair.py：DFF D 端插 buffer 链候选，多轮迭代（每轮修当前最差端点，更新网表再测）；
- TDD 9 个 hold 测试（241+1 全绿）。

真实数据（experiments/20260805_hold_repair/，A-only）：

| 电路 | period | hold baseline (min_slack) | 修复后 (min_slack) | WNS | 轮数/插入 |
|---|---|---|---|---|---|
| s382 | 0.5ns | -0.36 | **-0.33** | -0.94 → -0.93 | 2 轮，DFF_2/DFF_13 各 1×buf_1 |
| s27 | 0.5ns | -0.36 | -0.36（无改善） | -0.28 | 1 轮，4 候选全无效 |

诚实双面结论：
1. **s382 hold 修复真实有效**：多轮迭代把 worst min slack 从 -0.36 抬到 -0.33，且 setup WNS 不劣化反而略好（-0.94→-0.93），证明 B 策略在受控 hold 场景下有真实可测收益；
2. **s27 诚实失败**：插 buffer 后 min slack 不动（-0.36），因该电路多端点同时并列最差 min slack，单点修复抬不动 worst——与 s382 形成对照，说明"每个候选 OpenSTA 实测、只接受严格改善"的规则确实防止了无效插入（4 个候选全部被拒绝）；
3. 这是 **synthetic 场景**（理想网络无天然 hold 违例），论文需透明标注；真实 post-layout hold 修复需要时钟树/P&R 数据（见 limitation）。

### 12.13 评审缺陷 1+4：双目标联合割（Joint Bi-Objective Cut，2026-08-05）

评审意见 1（核心算法"打补丁式修复"导致逻辑不自洽）：F1（等价）与 F4（时序增益）互斥、加权最小割恒选单门、critical_path_cover 直到复核阶段才硬塞。落实为**双目标联合割**：

- `src/rseco/cut.py`：`build_weighted_cut_graph(..., r_available=None)`——无 R 等价候选的门 `critical_reward` 置零并强制绑定 G/B 权重（硬约束，从根源上避免 F1 失败）；`weighted_cut_candidates(..., critical_first_default=True)`——首轮**并行**生成加权全局最小割与关键路径覆盖割，两个候选同时进入 OpenSTA 实测、哪个先严格改善 WNS 用哪个。
- `src/rseco/flow.py`：`run_multi_iteration_case` 增加 `r_available` 透传；`src/rseco/real_wns.py` 增加 `build_r_available()` + 前期 P1 的 `joint_mix` 首轮默认候选。
- 评分公式：`Score = Δtiming×λ₁ - size_penalty×λ₂ + boundary_stability×λ₃`（时序增益、尺寸罚分、边界稳定性三目标）。
- TDD：`tests/test_cut_patch.py` +4、`tests/test_joint_candidates.py` 更新（21 项相关测试全绿）。

### 12.14 评审缺陷 2：物理感知内环化 + F6（2026-08-05）

评审意见 2（物理寄生参数导致 WNS 改善归零，最致命）：把粗略物理估计从"事后验尸"嵌入内环。落实：

- `src/rseco/spef.py`：`build_spef` 支持 `fanout_penalty/depth_penalty` 可调惩罚因子（替换"40um/unit"粗糙估计）；`src/rseco/opensta.py` `run_opensta` 支持 `spef_path`。
- `src/rseco/real_wns.py` 物理门控：ideal 改善 > 10ps 才生成 SPEF 复测，SPEF 下同样改善才接受；否则丢弃并触发 F6。
- `src/rseco/failures.py` 新增 `F6_physical_load_failure`；`refinement.py` F6 → boundary_penalty+1、下一轮排除高扇出门。
- 论文措辞同步：FAECO 定位为**物理 ECO 的前端逻辑筛选器（Logic Filter）**，输出候选集为后续物理尺寸调整保留可测改善余量（b18 JOINT ideal +0.13、轻负载 SPEF +0.11），不再宣称"pre-layout 修复保证 post-layout 有效"。

### 12.15 评审缺陷 3：异构现代基准 OOD 泛化（2026-08-05）

评审意见 3（ISCAS89→ITC-99 同源同构，不等于跨设计泛化）。引入 **PicoRV32 基准族**（完全异构的现代开源设计）在统一 OSS-CAD 0.67 工具链下验证：

| 电路 | 类型 | cells/DFF | period | baseline WNS | final WNS | 接受修复 |
|---|---|---|---|---|---|---|
| picorv32 | 控制密集（RISC-V 核） | 7797/1597 | 5.0ns | -9.96 | **-8.83** | R clkinv_1→bufinv_16（+1.13） |
| picorv32_pcpi_mul | 数据密集（32×32 乘法器） | ~/255 | 2.0ns | -4.22 | -4.17 | G nand3_1→nand3_2（+0.05） |
| picorv32_regs | 存储密集（寄存器堆） | ~/992 | 0.5ns | -0.19* | -0.19*（无改善） | ---（见注） |

*注：0.67 下寄存器堆映射为 enable-flop（edfxtp）网表、内部 reg-to-reg 路径为空（I/O 主导），FAECO reg-to-reg 修复环无候选空间；0.33 下 -0.19 亦无改善（mux2 主导、无 R 候选）——两种工具链均诚实负结果。

0.33 对照（历史归档）：pcpi_mul -4.09→-2.89（G nor2_1→nor2_4，+1.2）；regs -0.19 无改善。0.67 网表与 0.33 不同，基线与修复空间均变（pcpi_mul 乘法器关键路径在 0.67 下为 nor/nand 链，upsize 收益有限）。

### 12.16 评审缺陷 4：工具链统一 OSS-CAD 0.67 + 分治切割（2026-08-05）

评审意见 4（工具链版本分裂与 32 位内存崩溃）：彻底弃用 Yosys 0.9，统一工具链。落实：

- **OSS-CAD Suite nightly（Yosys 0.67+146，64 位）**安装到 `C:\oss-cad-suite-build\oss-cad-suite`；`scripts/run_sequential_timing_check.py` 新增 `_find_oss_cad_root()`/`_yosys_env()`，默认 `yosys_cmd` 解析为 OSS-CAD 绝对路径 `bin/yosys.exe`。
- **关键 bug 修复**：Windows CreateProcess 解析裸命令 `yosys` 用**父进程 PATH**（子进程 env PATH 对查找无效），prepend OSS 目录无效时会静默回退到 scoop shim 的 Yosys 0.9——必须传绝对路径。已修复（map.log 确认 0.67）。
- **兼容性修复**：OpenSTA 3.1.0 的 Verilog parser 拒绝 `wire signed` 声明（Yosys 0.67 write_verilog 保留 RTL signed 属性），`run_yosys_mapping` 在写网表后自动去掉 `wire signed`（位宽不变，仅结构 STA 用）；PicoRV32 子模块须以 `--circuit <top>` 指定正确 top（同一源文件含多个模块），`synth -top` 误选整核会导致无时钟路径。
- runner 反转：`run_outerloop_real_wns.py` 的 `--no-yosys-wsl` 改为 `--yosys-wsl`（默认 OSS 0.67，WSL 0.33 显式回退）。
- **分治切割**：`src/rseco/cut.py` 新增 `split_cone_by_depth` + `_subcone_from_gates`；`src/rseco/flow.py` 新增 `_cone_candidates`，超大锥按逻辑深度拆子锥独立生成候选（论文"分治切割"卖点）。
- **0.67 复验**：s382 baseline -0.98 → 修复 **-0.85**（5 轮迭代，优于 0.33 的 -0.92）；b18 映射 227s/4.87MB、b19 510s/10.3MB 成功（无 bad_alloc）；全量回归 **252 passed**。
- **注意**：0.67 映射网表与 0.33/0.9 不同，基线和修复空间都会变；论文对早期表格（0.9/0.33）与统一后 0.67 复验分别标注。
### 12.17 迭代式物理感知闭环初探（F6 反馈实证，2026-08-05）

评审战略建议把 SPEF 从"事后验尸报告"提升为"驱动算法迭代的物理先验约束"。落地：

- **接线**：`scripts/run_outerloop_real_wns.py` 新增 `--physical-gate/--min-physical-gain/--physical-fanout-penalty/--physical-depth-penalty/--physical-unit-len`，透传 `RealWnsEvaluator`；`src/rseco/real_wns.py` 的 SPEF 生成支持 `unit_len_um/depth_penalty` 可调；`src/rseco/flow.py` 在每轮 evaluator 返回后扫描本轮 `trials`，有 `physical_failure=True` 即 `failures.add(PHYSICAL_LOAD_FAILURE)`，`refine_weights` 触发 `increase_boundary_penalty_physical`——F6 从"标记"变成"驱动下一轮割图"。
- **OpenSTA 超时**：b18 0.67 大网表单次 STA ~210s，`run_sequential_timing_check.py` 超时 180s → 900s。
- **s382（0.67 网表，period 0.5ns，unit_len=2µm，fp=1.0）**：325 trials 中 50 个 ideal 改善候选（>10ps）全部在 SPEF 复测下归零（physical WNS -1.32~-1.37 vs ideal baseline -0.98）；30 轮探索无接受，boundary_penalty 1.0→6.0。**F6 负反馈实证：物理门控把"ideal 有效、物理无效"的候选在进入下游物理 ECO 前量化剔除。**
- **b18（0.67 网表，period 13.15ns，unit_len=2µm）**：486 trials 中 6 个 ideal 改善候选全部 SPEF 失败（-2.41 vs -2.24，0.67 网表关键路径为乘法器长链）；6 轮全拒，boundary_penalty 1.0→7.0。诚实负结果。
- **0.33 网表对照（不启用门控，仅事后扫描）**：b18 JOINT 修复 ideal +0.13，SPEF 扫描 2µm +0.11 / 5µm +0.07 / 10µm +0.03 / 20µm 归零——轻负载下同一逻辑候选保留真实物理余量；s382 u5 +0.03。
- **结论表述（论文 \S IV-G / tab:phys_closure）**：两类结果共同支撑"FAECO 是物理 ECO 的前端逻辑筛选器（Logic Filter）"：0.67 下无候选通过 ideal+SPEF 双门（收敛到不引入物理劣化），0.33 轻负载下候选保留 +0.11 改善余量。

### 12.18 TCAD 冲刺 Sprint 1-3（2026-08-05）

- **Sprint 1：0.67 统一复验完成（解决硬伤 1）**：修复了 `run_yosys_mapping` 中 dff 黑盒预处理的实际生效问题——`circuit_for_script` 在 `circuit = pre` 切换后未重算，Yosys 始终读原始文件，导致 s820/s832/s953 报 Module dff not part of design。修复后添加回归测试锁定（commit f8bf00b，257 测试全绿），3 电路 0.67 映射成功。8 电路 0.67 统一复验：s27 -0.27→-0.18、s382 -0.98→-0.89、s420 -1.56→-1.55、s641 -1.63→-1.59、s713 -1.33→-1.31、s820 -1.19→-1.17、s832 -1.23→-1.17、s953 -1.31→-1.27（全部 joint-enumerate-depth 3）。论文 tab:iscas_main 更新为 0.67 数据 + 表头注记，旧表格标注“基于旧 0.9/0.33 工具链”。
- **Sprint 2：消融 + 参数敏感性（解决硬伤 1-2）**：3 电路（s382/b15/picorv32）纯 R/G/B 消融：B 在 0.67 下全部零改善（与 0.9 时代“B 主力”相反，诚实记录）；s382 纯 R/B 失败、纯 G -0.83、混合 -0.89（混合优于单策略）；b15/picorv32 单策略可达混合水平。λ 敏感性（s382）：全部 8 组权重（λ_b {0.5,1,1.5,2}、λ_s/λ_c {0.5,1,2}）final WNS 恒为 -0.83，性能面完全平坦。论文新增 \S IV-H （sec:ablation，tab:ablation）+ 敏感性段落。
- **Sprint 3：定位升级 + 文本精修**：摘要最后一句加入 Logic Filter 定位 + 候选 STA 剪减高达 75%；limitation 补 SPEF 归零不否定 FAECO，而是保守门控；hold 小节开头加失败感知接受规则通用性一句。论文 13 页 PDF 编译通过，无 undefined ref/citation。

### 12.19 skill 流程：完整性审计 + 多视角评审 + 修订（2026-08-05）

- **背景**：应用 academic-research-skills（升级至 v3.19.0/3.2.0/1.10.0/2.11.0，通过 ghfast.top 镜像）优化论文与流程，按 pipeline mid-entry 协议从 Stage 2.5（INTEGRITY）进入。
- **Stage 2.5 完整性审计（通过）**：ghost citation 检查：27/27 bibitem 全部被引用，零孤儿零悬挂；内部数据一致性：15 项全通过（主表/消融表/敏感性/摘要/limitation/hold 与实验数据一致）；Crossref/Semantic Scholar 引用真实性抽查：发现并删除 2 条虚构引用（wang2016restruc / wang2024seq），修正 5 处 venue 错误（wang2012nego→ASP-DAC、zhong2024stp→DATE、liu2021rlsizer→DAC、chen2024aito→Integration、huang2025phys补 TCAD）。commit 4aa3591。
- **Stage 3 多视角评审（Major Revision）**：5 视角评审：创新性 68、方法严谨 74、证据充分性 71、论证连贯 78、写作 72。两个 CRITICAL：（0） 0.67 下 SPEF 门控全归零是否意味修复无效；（2）混合必要性证据仅 s382 单点。
- **Stage 4 修订（R1+R2 已落地）**：R1——s382 混合 vs 纯 G 差异机制精确化（候选生成层原因：混合时从 actionable 门 _070_ 出发，JOINT 窗口只命中 _057_+_059_；纯 G 抽働全部预算命中 _059_+_063_）；R2——F6 反馈把 boundary_penalty 提升至 6-7，将搜索推向保守候选领域，是学习行为而非空转。commit 2fad9cd，13 页 PDF 编译通过。

### 12.20 ITC-99 19 电路 0.67 统一复验（2026-08-05，本地未提交）

Sprint 1 的“ITC-99 19 电路 0.67 统一复验”补全（此前仅 ISCAS89 8 电路完成）。运行配置与 ISCAS89 复验一致：统一 OSS-CAD 0.67 映射 + joint-enumerate-depth 3（JOINT 滑动窗口深度 ≤3、上限 50 组合）+ 决策层优先级表 + beam=1 + early-stop，3 并发约 12.5 分钟跑完 19 电路（实验产物 experiments/20260805_tcad_sprint1_itc99/，A-only）。

- **结果 18/19 改善（94.7%，旧 0.9/0.33 为 17/19）**：b01 -0.63→-0.62（R）、b02 -0.24→-0.22（JOINT）、b03 -1.86→-1.43（JOINT×3）、b04 -2.43→-2.28（JOINT maj3×3）、b05 -3.75→-3.63（JOINT）、b06 诚实失败（6 轮 156 次候选全拒）、b07 -2.13→-2.02（R）、b08 -1.23→-1.18（G）、b09 -1.14→-1.13（R）、b10 -1.40→-1.28（JOINT）、b11 -1.95→-1.82（JOINT）、b12 -2.28→-1.99（JOINT）、b13 -1.45→-1.36（R）、b14 -12.53→-12.38（R xor2_1→ha_1）、b15 -12.55→-11.85（JOINT）、b17 -16.53→-16.10（JOINT）、b20 -13.21→-11.23（JOINT，+1.98）、b21 -13.70→-11.54（JOINT，+2.16）、b22 -11.68→-11.21（JOINT）。策略分布 5 R / 1 G / 12 JOINT。
- **版本漂移（如实记录）**：b01/b02 从旧版“诚实失败”转为 R/JOINT 改善，b06 从旧版改善转为失败——映射版本改变具体候选集合，整体收敛率 94.7% 与旧版 89.5% 同量级，跨基准泛化结论不变。
- **论文同步**：tab:itc99 全部换 0.67 数据 + caption 注记（同 tab:iscas_main 措辞）；小节文字/摘要/贡献/结论 17/19→18/19；limitation(4) 改为“ISCAS89 8 电路 + ITC-99 19 电路主表已在 0.67 下复验，仅 b18/b19 JOINT+SPEF 对照实验仍基于 0.33 归档网表（phys_closure 已标注并给出 0.67 baseline/候选数据）”；未来工作去掉“全量 34 电路表格重跑”，改为“补齐 b18/b19 0.67 修复闭环 + 多 corner/多工艺库”。13 页 PDF 编译通过（无 undefined ref/citation，ITC-99 表区域无 overfull）。
### 12.21 b18 0.67 敏感性 + 修复闭环（2026-08-05，本地未提交）

对 0.67 映射的 b18（period 13.15ns，复用 20260805_toolchain_b18b19/b18_v067/mapped.v）跑常规混合修复（不启用物理门控）：JOINT 自动枚举深度 3 收敛到 _649420_→nor4_2 + _649432_→a211oi_2，WNS -2.24→-2.09（93 次候选 STA，单轮收敛）。边界惩罚 λ_b 三点扰动（0.5/1.0/2.0，其余权重固定）全部收敛到同一 JOINT 修复，性能面在 ±100% 权重变化下完全平坦——敏感性结论从 s382（-0.83 平坦）扩展到 37.6 万门大电路。

- **论文同步**：phys_closure 表补 dagger 行（0.67 b18 JOINT -2.24→-2.09）+ 敏感性段落补 b18 三点扰动 + 工具链复验节补 b18 修复闭环 item + ITC-99 后续段补 0.67 收敛句 + limitation(4) 改为“b18 已有 0.67 修复闭环，b18/b19 SPEF 门控对照仍基于 0.33，b19 0.67 修复闭环为后续”+ 未来工作改为“补齐 b19”。13 页 PDF 编译通过（无 undefined ref/citation）。