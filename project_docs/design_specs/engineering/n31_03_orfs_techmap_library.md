# N31-03 ORFS Techmap Library 修复路径设计

更新时间：2026-07-31

本文档是 N31-03 的设计文档，对应 **P0-1 Stage B CEC unavailable** 修复路径。`paper/reviews/round1_self_audit.md` 列此项为 P0，**必须解决**才能在论文主表写 "CEC pass"。本文档不下载任何 ORFS 资产（按 handoff 禁止），仅给出 cells.v 接入路径、CEC 修复策略、用户授权需求、Stage D 时序。

## 1. 背景

Stage B 8-case 当前 CEC 全部 unavailable，根因：Yosys 0.9 `synth -noabc + abc -liberty` 流程在 SKY130 HD Liberty 上产生 `sky130_fd_sc_hd__clkinv_1` placeholder（Liberty 实际不含此 cell）。

`paper/reviews/round1_self_audit.md` P0-1：`Stage B CEC unavailable (METH-08)`，影响 Stage B 8-case 形式回验全部不可达，是当前 P0 项。

**当前 limitation L31-01**：SKY130 HD Liberty 不含 `clkinv_1` cell → Stage B CEC 不可达 → mapped-BLIF vs reference-normalized BLIF 形式回验全部 `unavailable`。

`risk_register.md` R31-01：active 状态。

## 2. 根因详细分析

### 2.1 Yosys 0.9 techmap pass 行为

Yosys 0.9 `techmap` pass 在 SKY130 HD Liberty 上需要配套的 `cells.v` techmap library 才能完整映射。SKY130 HD Liberty 实际只定义了 cell 接口（pin/function/timing），但 cell 内部实现需要 `cells.v` 描述。

当 `cells.v` 缺失时，`techmap` pass 退化为 fallback 选择：`sky130_fd_sc_hd__clkinv_1` 这个 cell 名被选作 inverter placeholder（实际 Liberty 中无此 cell，导致 ABC `cec` 不可达）。

### 2.2 ABC `cec` 报错

ABC 0.9 `cec` 报告：
```
Line 10: Cannot find the model for subcircuit sky130_fd_sc_hd__clkinv_1.
Reading network from file has failed.
```

实际 SKY130 HD Liberty 实际有 `sky130_fd_sc_hd__inv_1` 等 inverter cell，但 `clkinv_1` 是 Yosys techmap 内部生成 cell。

### 2.3 修复路径

**核心问题**：Yosys techmap 需要 SKY130 cells.v 配套，ABC 需要 cell model 才能 cec。

**两种修复**：

| 路径 | 描述 | 复杂度 | 影响 |
|---|---|---|---|
| **A：cells.v 配套** | 补 SKY130 cells.v（ORFS 仓库 `flow/platforms/sky130hd/cells.v`） | 中等 | 完整 techmap，无 placeholder |
| **B：替换为 inv_1** | 修改 `synth` 命令序列强制使用 inv_1 而非 clkinv_1 | 简单 | 部分修复，但 inv_1 库可能也不全 |

按 handoff "禁止下载完整 Sky130 PDK"，路径 B 是推荐起步方案。路径 A 需用户授权 ORFS `cells.v` 文件下载。

## 3. 路径 B：替换为 inv_1 cell

### 3.1 实施步骤

1. 修改 `src/rseco/technology_mapping.py` 命令序列
2. 在 `synth -noabc` 之前添加 `techmap -map +/gate2lut.v`（强制 ABC primitives）
3. 移除 `abc -liberty` 直接调用，改用 `synth -top <top>` + `abc -lut 4 -fast`（映射到 4-input LUT 而非 Liberty）
4. 重新跑 Stage B 8-case mapping
5. 检查 mapped BLIF 中是否还含 `clkinv_1`

### 3.2 期望结果

- mapped BLIF 中所有 `clkinv_1` 被替换为 LUT
- CEC 8-case 可能 `pass`（LUT 4-input 是 ABC 原生 primitives，cec 可识别）
- STA 仍能跑（OpenSTA 接受 LUT mapped Verilog）

### 3.3 limitation

- LUT mapping 不再是 SKY130 HD cells，无法做 SKY130 timing（OpenSTA 需要 Liberty cell timing）
- 如果用 LUT mapped，STA 无真实 timing（与当前 combinational 路径 slack=null 类似）
- 适合作为"绕开 CEC limitation 的 fallback"，但不适合作为正式 SKY130 timing ECO 论文

## 4. 路径 A：cells.v 配套

### 4.1 ORFS cells.v 来源

`The-OpenROAD-Project/OpenROAD-flow-scripts` 仓库：
- 路径：`flow/platforms/sky130hd/cells.v`
- commit：与已固定的 `da8f092a02a8e75658cc3100691aabff05f35629` 一致
- 大小：约 100-200 KB
- 许可：Apache-2.0（与 SKY130 HD Liberty 许可一致）

### 4.2 cells.v 内容

cells.v 是 Verilog cell model，描述每个 SKY130 HD cell 的内部实现（assign 表达式）。Yosys `techmap` 加载 cells.v 后能把 generic Verilog 表达式映射到 SKY130 cell 列表。

例子：
```verilog
module sky130_fd_sc_hd__inv_1 (A, Y);
input A;
output Y;
assign Y = ~A;
endmodule

module sky130_fd_sc_hd__buf_1 (A, X);
input A;
output X;
assign X = A;
endmodule
```

### 4.3 cells.v 接入 Yosys 命令序列

```
read_liberty -lib /path/to/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog /path/to/cells.v
read_verilog <input>
hierarchy -check -top <top>
proc
flatten
opt
techmap -map +/gate2lut.v
techmap -map /path/to/sky130_cells.v   # 新增：cells.v 映射
opt
abc -liberty /path/to/sky130_fd_sc_hd__tt_025C_1v80.lib
clean
write_verilog -noattr <mapped.v>
write_blif <mapped.blif>
```

### 4.4 期望结果

- mapped BLIF 中所有 SKY130 cells 都有对应 Liberty cell model
- CEC 8-case 全部 `pass`（每个 cell 都有 model）
- STA 给出真实 SKY130 timing（WNS / TNS / slack 非 null）

### 4.5 用户授权需求

**关键决策**：
- **决策 A**：用户授权下载 ORFS `flow/platforms/sky130hd/cells.v`（约 100-200 KB）
- **决策 B**：用户不接受下载，按路径 B 解决

按 handoff 7/20：
- "禁止下载完整 Sky130 PDK"（7 GB+）
- ORFS `cells.v` 是 PDK 一部分（虽然只有 ~150 KB）

需要用户明确授权 ORFS `cells.v` 单文件下载，才能走路径 A。

## 5. 实施时间表

按 N31-03 推进（无论路径 A 或 B）：

| 阶段 | 工作 | 时间预估 | 依赖 |
|---|---|---|---|
| N31-03-1 | 选路径 A 或 B | 用户决定 | 当前 |
| N31-03-2a (A) | 下载 cells.v + 接入 + 8-case 跑通 | 1-2 周 | ORFS 授权 |
| N31-03-2b (B) | 改 synth 命令序列为 LUT mapping | 1 周 | 无 |
| N31-03-3 | Stage B 8-case CEC 复现 | 1 周 | N31-03-2 |
| N31-03-4 | 更新 `paper/draft/method.md` §3 + experiments.md §4 limitation 表 | 1 天 | N31-03-3 |
| N31-03-5 | 修订 `paper/reviews/round1_self_audit.md` P0-1 → mitigated | 1 天 | N31-03-4 |

总计 3-5 周。

## 6. 设计边界与限制

### 6.1 N31-03 不做的事

- 不下载完整 ORFS PDK（7 GB+）
- 不修改 SKY130 HD Liberty 本身
- 不实现 SKY130 cell 内部优化（保留 Liberty 默认）
- 不实现 clock tree synthesis
- 不实现 timing exception（false path / multicycle path）

### 6.2 与 Stage B 已落地端到端的关系

路径 A 修复后：
- Stage B 8-case mapping 8/8 success（不变）
- Stage B 8-case STA 8/8 success（不变）
- **Stage B 8-case CEC 8/8 pass**（从 `unavailable` 升级为 `pass`）
- mapped BLIF 含真实 SKY130 cells（非 placeholder）
- **N31-06 AIG→SMT 解锁**：cells.v 提供 SKY130 cell 模型后，Yosys `aigmap` 可把 mapped.v 归约到 AIG（当前报 `Module '\sky130_fd_sc_hd__nand2b_1' ... is not part of the design`），从而打通 Z3 candidate/boundary 的 8-case 端到端（2026-08-03 验证，见 `docs/engineering/z3_candidate_boundary_formal.md`）

路径 B 修复后：
- Stage B 8-case mapping 8/8 success（不变）
- Stage B 8-case STA 8/8 success（可能变为 `skipped` 因为 LUT 无 Liberty timing）
- Stage B 8-case CEC 8/8 pass（仍 `pass` 因为 LUT 是 ABC primitives）
- mapped BLIF 含 LUT cells（不是 SKY130 cells）

## 7. 处置建议

按优先级：

1. **决策 A（用户已选，2026-08-03）**：用户选择路径 A（下载 cell 模型）。
2. **实施结果（路径 A 变体）**：下载 skywater cells Verilog 模型（70 cells + UDP，296 KB）后发现 Yosys 0.9 不支持 UDP primitive；改用 **Liberty function 提取方案**（`scripts/make_liberty_cells_v.py` → assign-style `sky130_cells_v2.v`）。
3. **最终解法**：`scripts/verify_epfl_mapping_sat.py` 用 Yosys `miter -equiv` + `sat -prove-asserts`，**8/8 EPFL case 等价证明 SUCCESS**。

## 8. 当前状态总结（2026-08-03 更新）

- **Stage B CEC limitation 已解决**：8/8 EPFL case Yosys miter+SAT 等价证明 SUCCESS（`tmp/sat_verify/sat_equivalence_summary.json`）
- 原 ABC `cec` 路径不可用原因已诊断：ABC read_lib 对 Liberty subcircuit 建 model 普遍失败（连极简 Liberty 也失败）；Yosys read_liberty 把 cell 标 blackbox；下载的 skywater Verilog 模型含 UDP 且 Yosys 0.9 不支持
- `risk_register.md` R31-01 → **mitigated**
- 路径 B（LUT mapping 兜底）不再需要
- 论文主表可写 "original==mapped 等价验证 8/8 pass"

## 9. 后续修订

- 正式 Stage B runner（`scripts/run_stage_b_pre_layout_sta.py`）后续可把 `sat_equivalence_summary.json` 并入 per-case 表
- `experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.md` 可加 cec_sat 列（8/8 pass）
- 论文 experiments/method/conclusion 章节 CEC 描述更新为 SAT 等价证明路径
- 路径 A 修复后 Stage B 8-case CEC 全部 `pass`，`paper/draft/experiments.md` §3 表格更新
- 路径 B 实施后 Stage B 8-case CEC 全部 `pass` 但 STA 标 `skipped`，`paper/draft/experiments.md` §3 表格更新

## 10. 与 handoff 的边界

按 `STAGE_B_AGENT_HANDOFF.md`：
- "禁止下载完整 Sky130 PDK" → ORFS `cells.v` 是 PDK 一部分（虽然 ~150 KB）
- 决策 A 需用户明确授权 ORFS `cells.v` 单文件下载
- 决策 B 不下载任何 ORFS 资产，改用 LUT mapping 兜底
- 任何 N31-03 启动后，按 handoff 7/20 决议执行 A-only 范围审计 + 提交前复跑 90 项测试 + 同步 `STAGE_B_AGENT_HANDOFF.md`