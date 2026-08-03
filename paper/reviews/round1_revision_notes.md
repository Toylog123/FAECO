# Paper Round 1 修订说明（Round 1 → Round 2）

更新时间：2026-07-31

本报告是 `paper/reviews/round1_self_audit.md` 的对应修订说明，记录每个 P0 / P1 / P2 项的处置状态、需要用户决定的事项，以及 round 2 之前必须完成的修改清单。

## 1. P0 项处置

### P0-1: Stage B CEC unavailable (METH-08)

**状态**：**保留到 round 2** —— 需要 N31-03 ORFS techmap library。

**根因**：Yosys 0.9 `synth -noabc + abc -liberty` 流程产生 `sky130_fd_sc_hd__clkinv_1` placeholder，但 SKY130 HD Liberty 实际不含此 cell。

**处置计划**：
1. N31-03 ORFS techmap library 获取（需用户授权 PDK 下载）
2. 把第 3 节 "重综合 + Technology Mapping" 命令序列从 `synth -noabc + abc -liberty` 改回 raw `techmap`
3. 跑 8-case 端到端复现，期望 CEC 5/5 → 8/8 `pass`
4. 更新 `experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.md` 的 cec 列

**用户决定需要**：
- 是否授权下载 ORFS `cells.v` + `cells.vh`（属 PDK 部分）
- 如果不授权，本论文将保留当前 limitation，CEC 表列为 `unavailable`，论文不声称端到端 CEC pass

## 2. P1 项处置

### P1-1: METH-01 sequential cone 未实现

**状态**：**保留到 round 2** —— 需要 PM23 (M5) 设计启动。

**处置计划**：
1. N31-05 SKY130 sequential ECO 拓展：把 DFF/restore 信号加进 SDC，准备 clock tree
2. 把 fanin cone 扩展为 reg-to-reg cone（含前级寄存器边界）
3. 接入 `experiments/20260731_epfl_8case_stage_b` 等真实 sequential EPFL benchmark

**用户决定需要**：是否启动 PM23 sequential 设计（涉及新方法要素，约 2-3 周工作量）

### P1-2: METH-09 X19 multi-iteration refinement 设计未启动

**状态**：**保留到 round 2** —— 需要 PM22 设计审批。

**处置计划**：
1. 用户给出"failure recovery 成功口径"：什么条件下算"已恢复"？
2. 设计 multi-iteration loop：每次迭代后重新分类 residual failures + 记录停止原因
3. 设计 without F1/F3/F4 ablation 表格

**用户决定需要**：X19 设计口径（这是 P0 之外的最高优先级 P1）

### P1-3: METH-10 failure-aware refinement 仍是 single-iteration proxy

**状态**：与 P1-2 同源 —— X19 设计启动后一起处理。

### P1-4: METH-12 deterministic ranking 中 candidate timing gain 当前相同（Stage A proxy）

**状态**：**保留到 round 2** —— Stage B STA 已实现但 candidate-specific timing gain 需要重算。

**处置计划**：
1. 在 `src/rseco/ranking.py` 加入 per-candidate STA timing gain（每个候选 patch 在 mapping 后跑 STA，提取 WNS/TNS/slack）
2. 更新 `paper/draft/method.md` §6 描述 candidate-specific timing gain
3. 在 `experiments/20260731_epfl_8case_stage_b` 加 timing gain 字段

**用户决定需要**：是否扩展 ranking 到 per-candidate STA（涉及新增 STA runner per candidate，性能开销大）

### P1-5: ISCAS85 c432/c499/c880 许可不完备

**状态**：**接受保留** —— 仅作本地 smoke，不进入论文主表。

**处置**：在 `paper/draft/experiments.md` §1 已明确"仅作本地 smoke"。

## 3. P2 项处置

### P2-1: Z3 candidate/boundary formal 未接入

**状态**：保留到 round 2 + P32 投稿前如未实现则明确标注 limitation。

### P2-2: Sequential EPFL benchmark 未接入

**状态**：与 P1-1 同源。

### P2-3: Git remote 未配置

**状态**：**round 2 之前需用户决定**。

**处置**：等用户提供 GitHub remote URL；本地 commit `5aec0f2` 已就位。

### P2-4: 论文主图未渲染

**状态**：保留到 round 2。

**处置**：用 `pandoc -t latex` + LaTeX 渲染 `paper/figures/` 下的图 1-5 占位。

### P2-5: 章节初稿需迁入 `paper/submission/`

**状态**：**round 2 之前需用户决定**。

**处置**：等用户审定所有 6 个章节初稿后批量迁入。

## 4. round 2 之前必须完成的修改清单

按优先级：

1. **修订 introduction.md / method.md / experiments.md / conclusion.md**：根据自审稿结论，移除"未验证"表述（如"可能"、"后续"），改为更明确的实验支撑描述
2. **重写 method.md §6**：candidate-specific timing gain 描述与代码一致
3. **修订 experiments.md §3**：当 N31-03 ORFS techmap library 获取后更新
4. **修订 conclusion.md §3**：N31-03 / N31-05 / N31-06 进展更新
5. **生成论文主图**：从 `experiments/` 渲染图 1-5

## 5. 文档维护清单（round 2 之前必须同步）

- `paper/draft/README.md`：反映所有章节当前状态
- `paper/draft/method_symbol_table.md`：与 `paper/draft/method.md` 同步
- `experiments/configs/stage_b_pre_layout.json` `notes`：随 P0/P1 处置状态更新（已 round1 audit 注释）
- `docs/task_board.md`：PM25-29 完成状态（已 done）
- `docs/project_management/work_log.md`：round 1 自审稿与修订说明 LOG 条目
- `docs/project_management/risk_register.md`：R31-01 状态（已 mitigated 但 limitation 保留）

## 6. 用户决定需求汇总

按优先级：

1. **N31-03 ORFS techmap library 下载授权**（P0-1）
2. **N08 remote URL**（P2-3）
3. **PM25-29 / paper/draft/ 章节审定**（P2-5）
4. **PM22 X19 failure recovery 成功口径**（P1-2）
5. **PM23 sequential cone 设计启动**（P1-1）

## 7. 处置结论

本论文 round 1 自审稿产出 1 个 P0 + 4 个 P1 + 5 个 P2，全部已经标注在论文初稿各章节 limitation 段落。当前 P0（P0-1 Stage B CEC）需要用户授权 ORFS techmap library 才能解决。P1-1 / P1-2 / P1-3 / P1-4 / P2-1 / P2-2 均依赖后续工作启动。round 2 修订将在 P0 解决后启动，主要做"修订描述与代码一致 + 论文主图渲染 + 投稿包准备"。