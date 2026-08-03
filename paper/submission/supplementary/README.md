# Paper Supplementary Materials (占位)

更新时间：2026-07-31

投稿补充材料目录。当前为空，等待各章节定稿后批量生成（PM32 投稿包准备）。

## 计划结构

```
paper/submission/supplementary/
├── README.md
├── toolchain_snapshots.md    (附录 B：实验工具链详细版本)
├── stage_a_artifacts.md      (附录 C：Stage A 5-case 完整产物)
├── stage_b_artifacts.md      (附录 D：Stage B 8-case 完整产物)
├── failure_recovery_logs.md  (附录 E：failure_recovery 表完整数据)
├── runtime_breakdowns.md      (附录 F：runtime breakdown 完整数据)
└── ablation_results.md        (附录 G：without F1/F3/F4 消融结果 — 待 X19)
```

## 附录 B 计划内容 (toolchain_snapshots)

| 工具 | 版本 | 来源 | SHA / commit |
|---|---|---|---|
| Python | 3.11.9 | `.venv` | — |
| Yosys | 0.9 | Scoop | `1979e0b1` |
| ABC | 1.01 | `yosys-abc` | UC Berkeley |
| OpenSTA | 3.1.0 | WSL2 `/usr/local/bin/sta` | `parallaxsw/OpenSTA` commit `dc5ccd2d6941289a6a7d3c918b10b493f44a7f56` |
| Z3 | 5.0.0 | `.venv` | — |
| NetworkX | 3.6.1 | `.venv` | — |
| SKY130 HD Liberty | tt_025C_1v80 | `The-OpenROAD-Project/OpenROAD-flow-scripts` | commit `da8f092a02a8e75658cc3100691aabff05f35629`, SHA256 `ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9` |
| EPFL v2025.1 | commit `8c832d5d07d822d28ba84dc6e95295367702401f` | MIT license | — |

## 附录 C 计划内容 (stage_a_artifacts)

- `tables/case_summary.json`：5-case 每个 run 的 metrics + selected patch + ranking
- `tables/baseline_comparison.{json,md}`：6 baselines × 5 cases patch size / score 对比
- `tables/runtime_breakdown.{json,md}`：Python + Yosys/ABC 阶段 runtime
- `tables/failure_recovery.{json,md}`：F1-F5 initial fail / proxy recovered / recovery rate / avg_iterations
- `environment/toolchain_snapshot.json`：当前 5-case 工具链快照

## 附录 D 计划内容 (stage_b_artifacts)

- `tables/stage_b_case_summary.{json,md}`：8-case 每个 case mapping + STA
- `tables/stage_b_runtime.{json,md}`：mapping_s / sta_s / total_s
- `environment/toolchain_snapshot.json`：当前 8-case 工具链快照
- `<case>/cec/`：每个 case 的 normalized BLIF + ABC cec log（当前 SKY130 `clkinv_1` limitation 下 CEC unavailable）

## 边界

- 补充材料必须与正文一致，禁止在 supplementary 中引入主表未出现的数字
- Stage B 8-case CEC unavailable 必须明确标注在附录 D
- Stage A 5-case failure_recovery `avg_iterations=1.0` 是 single-iteration proxy，必须明确标注在附录 E
- 任何 [F08-B] DAC 2018 / [B06] BUFFALO 数据禁止作为补充材料支撑

## 后续修订

- 等章节初稿全部获用户审定后批量生成附录 B-G
- N31-06 Z3 wrapper 启动后，附录 D 加 candidate-level z3 formal 列
- X19 多轮 refinement 启动后，附录 G（消融）按 without F1/F3/F4 表生成