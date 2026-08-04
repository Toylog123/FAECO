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
