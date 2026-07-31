# FAECO Research Workspace

本工作区用于接手并扩展 RSECO 学长工作，目标是形成可复现、可投稿的中文时序 ECO 工程类研究论文。

## 当前主线

**FAECO: Failure-Aware ECO + Reproducible Timing ECO Benchmark Flow + Timing-Aware Patch Ranking**

1. **FAECO**：继承学长 RSECO 的重综合辅助 patch replacement 思路，但不沿用 RSECO 名称；重点放在切割失败后的自适应权重调整和恢复机制上。
2. **Reproducible Timing ECO Benchmark Flow**：补足旧工作缺少公开代码和公开数据的问题，建立公开 benchmark 上可复现实验流程。
3. **Timing-Aware Patch Ranking**：在多个候选 patch 中引入时序收益、patch 大小、边界代价和验证代价的排序准则。

## 当前进展（2026-07-31）

Stage B 批次 0-7 已完成，仓库已建立首阶段基线（7 commits `9482a34..05ada8b`）。当前可直接复现的端到端能力：

- **最小 SKY130 HD Liberty 时序资产已固定**：`benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a02a8e75658cc3100691aabff05f35629/`，Liberty `sky130_fd_sc_hd__tt_025C_1v80.lib` (12,800,135 bytes) + 4 个 license/source 文件，全部 SHA256 与 `benchmarks/source_manifests/sky130hd_openroad.json` 一致。
- **EPFL `v2025.1` 8-case 库**：固定 commit `8c832d5d07d822d28ba84dc6e95295367702401f`、MIT license，目录 `benchmarks/raw/epfl_v2025_1_full`；wave 1 + wave 2 共 8 个电路（ctrl/int2float/router/cavlc/dec/priority/adder/max）已规范化。
- **Stage A**：5-case combinational smoke（c17 × 2 + c432 + c499 + c880）+ Yosys-normalized full-netlist ABC CEC 5/5 pass + ABC baseline 5/5 success + 结构化 runtime/environment。
- **Stage B**：8-case 端到端 mapping → SDC → OpenSTA pre-layout STA 全链路 8/8 success；产物 `experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.{json,md}` + `stage_b_runtime.{json,md}`。
- **回归基线**：90 项测试通过，0 failure，0 error（66 旧 + 24 新增 Stage B TDD 测试）。

**已知 limitation**：
- CEC 形式回验 status=error/unavailable：ABC 0.9 报 `sky130_fd_sc_hd__clkinv_1 not found in liberty`，原因是 Yosys 0.9 `synth -noabc + abc -liberty` 流程产生的 inverter placeholder 不在 SKY130 Liberty 实际 cell list。需要 ORFS 配套 techmap library 才可完全修复（属 PDK 部分，按 handoff 禁止下载完整 PDK）。
- STA slack_status=MET：所有 8 个 EPFL case 都是纯组合电路（无 flip-flop），OpenSTA 报 "No paths found." + "worst slack max INF"，WNS/TNS/slack 均为 null，正确反映"无 timing violation"。

详细执行记录见 `docs/project_management/work_log.md`（按日期索引，2026-07-31 段落含 LOG-20260731-01 至 LOG-20260731-10 共 10 条）。

## 顶层目录

| 路径 | 作用 |
|---|---|
| `docs/` | 主线、工程结构、实验方案、论文审计、项目管理文档 |
| `docs/project_management/` | 路线图、里程碑、风险、决策记录、Stage B 交接 |
| `docs/experiment_design/` | benchmark、failure taxonomy、baseline protocol、metrics |
| `docs/paper_audit/` | claim-evidence、formula-figure、pre-submission 审计 |
| `docs/reports/` | 阶段汇报、组会汇报、周报 |
| `src/rseco/` | Python 实现：yosys JSON importer、technology mapping、SDC generator、OpenSTA runner、ABC CEC、refinement、ranking 等 |
| `tests/` | unittest 测试（90 项覆盖） |
| `scripts/` | 数据准备、实验运行、结果汇总等 CLI 入口 |
| `experiments/` | 每次实验运行的配置、原始结果和表格 |
| `experiments/configs/` | 实验 JSON 配置（minimal_combinational.json、stage_b_pre_layout.json） |
| `experiments/environment/` | 工具链快照 |
| `benchmarks/raw/` | 公开 benchmark 原始数据（EPFL v2025.1 + ISCAS85 + SKY130 HD） |
| `benchmarks/source_manifests/` | benchmark 来源、license、blob SHA 固定 |
| `data/cases/` | 最小 ECO case 数据 |
| `paper/` | 论文稿件、图表 |

## 当前不做什么

- 不假设旧 RSECO 代码可以恢复，第一版算法使用确定性 scoring 而非 GNN/RL。
- 不下载完整 Sky130 PDK（7 GB+），仅用最小 SKY130 HD Liberty 时序资产。
- 不写入 ISCAS85 c432/c499/c880 的派生仓库；当前仅作本地 smoke（许可不完备）。
- 不写成 signoff timing 或虚构 SPEF；仅报告 pre-layout STA。

## 工程验证

```bash
$env:PYTHONPATH='src'
python -m unittest discover -s tests
```

工具链版本：Python 3.11.9、Yosys 0.9、ABC 1.01（`yosys-abc`）、OpenSTA 3.1.0（WSL2 `/usr/local/bin/sta`）、Z3 5.0.0、NetworkX 3.6.1。

## 下一步

按优先级：

1. **L01 Related work 初稿**（基于 25A/1B 已核验文献证据，可独立启动写作）。
2. **X19 多轮 refinement 设计**（当前 Stage A 只跑 1 轮权重更新；真实 multi-iteration loop 需要 design 审批）。
3. **SKY130 techmap library**（修复 CEC limitation；需 ORFS 配套 cell.v，属 PDK 部分）。
4. **Z3 / 完整 formal**（boundary formal、candidate comparison，可作为后续增强）。

## 关键文档入口

- 论文主线：`docs/mainline.md`
- Stage B 执行状态：`docs/project_management/STAGE_B_AGENT_HANDOFF.md`
- Stage B 详细清单：`docs/project_management/stage_b_deferred_execution_checklist.md`
- 任务看板：`docs/task_board.md`
- 长期计划：`docs/project_management/long_term_task_plan.md`
- 风险登记：`docs/project_management/risk_register.md`
- 决策日志：`docs/project_management/decision_log.md`
- 工作日志：`docs/project_management/work_log.md`
- 审计报告：`docs/paper_audit/`

## 已归档的前期方案

- `docs/planning/项目重启与论文推进方案.md`
- `docs/planning/RSECO学长论文接手发表方案.md`