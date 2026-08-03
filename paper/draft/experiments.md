# FAECO Experiments 初稿（Draft 1）

更新时间：2026-07-31

本文档为论文 Experiments 章节的初稿，基于：
- `experiments/20260718_minimal_combinational_batch_demo/tables/*.json`（Stage A 5-case）
- `experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.{json,md}` + `stage_b_runtime.{json,md}`（Stage B 8-case）
- `docs/experiment_design/benchmark_flow.md` / `case_schema.md` / `baseline_protocol.md` / `metrics_and_tables.md`

尚未经用户最终审定；结构和措辞仅作为论文主体起点，禁止作为主表事实性表述。

---

## 1. 实验设置

**工具链**：
- Yosys 0.9（Scoop `yosys 0.9`）+ ABC 1.01（`yosys-abc`）+ OpenSTA 3.1.0（WSL2 `/usr/local/bin/sta`，`parallaxsw/OpenSTA` commit `dc5ccd2d6941289a6a7d3c918b10b493f44a7f56`）+ Z3 5.0.0 + NetworkX 3.6.1 + Python 3.11.9
- 工具链快照：`experiments/environment/toolchain_2026-07-30.json`

**数据集**：
- Stage A：5 个 combinational case（`data/cases/minimal/`），含 c17 N22/N23（两个 target output 同电路）与 c432 / c499 / c880（Genus 风格多行 Verilog parser 兼容）。c432/c499/c880 来源 `jpsety/verilog_benchmark_circuits` commit `b4c6b6203b95b5314d47365f4a8196c08145519b` 未声明 license，仅作本地 smoke，不进入论文主表。
- Stage B：8 个 EPFL `v2025.1` combinational benchmark（ctrl/int2float/router/cavlc/dec/priority/adder/max），固定 commit `8c832d5d07d822d28ba84dc6e95295367702401f` + MIT license，目录 `benchmarks/raw/epfl_v2025_1_full/`。

**SKY130 HD Liberty**：固定 commit `da8f092a02a8e75658cc3100691aabff05f35629`（`The-OpenROAD-Project/OpenROAD-flow-scripts` master），Liberty 文件 `lib/sky130_fd_sc_hd__tt_025C_1v80.lib`（12,800,135 bytes, SHA256 `ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9`）+ 4 个 license/source 文件（LICENSE_BUILD_RUN_SCRIPTS BSD-3-Clause, Apache-2.0 sky130_fd_sc_hd LICENSE）。

**统一 SDC**（`experiments/configs/stage_b_pre_layout.json`）：virtual clock `clk_virtual` 周期 10 ns；input delay / output delay 2 ns；output load 0.05 pf；driving cell `sky130_fd_sc_hd__buf_1`；analysis mode `max`。8 个 case 共用同一 SDC 基线（`sdc.per_case_overrides` 为空）。

## 2. Stage A：5-case 多 baseline 端到端

实验命令：
```bash
python scripts/run_minimal_combinational_demo.py \
    --config experiments/configs/minimal_combinational.json \
    --output-dir experiments/20260718_minimal_combinational_batch_demo
```

输出位于 `experiments/20260718_minimal_combinational_batch_demo/`：

| 文件 | 内容 |
|---|---|
| `tables/case_summary.json` | 每个 run 的 selected patch、rank、score、replacement status、failure types、structural equivalence、formal_equivalence、abc_baseline、runtime、toolchain_snapshot |
| `tables/baseline_comparison.json` | fixed min-cut / seeded random cut / size-only / critical-path-only / ABC rewrite+refactor+resyn / FAECO selected 六种方法 patch size 与 score 对比 |
| `tables/runtime_breakdown.json` | Python + Yosys/ABC 阶段 runtime stage 表 |
| `tables/failure_recovery.json` | Stage A proxy failure recovery 表（F1-F5 initial fail / proxy recovered / recovery rate / avg_iterations） |

**Stage A 关键事实**：
- 5-case Yosys-normalized full-netlist ABC `cec` formal 5/5 `pass`（Stage A 5/5）
- 5-case ABC baseline (`yosys-abc` + Berkeley resyn2 展开序列) 5/5 `success`，optimized BLIF + ABC logs + `print_stats` 已归档
- failure recovery proxy 当前 `avg_iterations=1.0`（single-refinement proxy，非 multi-iteration 统计）
- Yosys/ABC external runtime 已写入同一 schema；OpenSTA Stage B 待启动

## 3. Stage B：8-case 端到端

实验命令：
```bash
python scripts/run_stage_b_pre_layout_sta.py \
    --output-dir experiments/20260731_epfl_8case_stage_b \
    --sta-command "wsl -d Ubuntu -- /usr/local/bin/sta"
```

`experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.md`：

| benchmark | mapping | mapping_s | sta | sta_s | slack_status |
|---|---|---|---|---|---|
| ctrl | success | 1.226 | success | 3.111 | MET |
| int2float | success | 1.479 | success | 0.640 | MET |
| router | success | 1.582 | success | 0.628 | MET |
| cavlc | success | 3.306 | success | 0.616 | MET |
| dec | success | 1.377 | success | 0.621 | MET |
| priority | success | 4.991 | success | 0.632 | MET |
| adder | success | 5.713 | success | 0.662 | MET |
| max | success | 16.784 | success | 3.268 | MET |

`experiments/20260731_epfl_8case_stage_b/tables/stage_b_runtime.md`：每个 case 记录 mapping_s / sta_s / total_s。max case 最慢（16.8s mapping + 3.3s STA = 20.0s），cavlc 第二慢（3.3s mapping）。

**Stage B 关键事实**：
- mapping 8/8 success（Yosys `synth -noabc + abc -liberty` SKY130 HD Liberty）
- STA 8/8 success（OpenSTA pre-layout STA via WSL2）
- `wns / tns / slack = null`，`slack_status = MET`（INF）—— 8 个 EPFL case 全 combinational，无 timing path
- CEC 形式回验（mapped-BLIF vs reference-normalized BLIF）：8/8 status=`unavailable`，原因是 Yosys 0.9 `synth -noabc + abc -liberty` 流程产生 `sky130_fd_sc_hd__clkinv_1` placeholder，SKY130 HD Liberty 实际不含此 cell
- 输入 EPFL Verilog SHA256 在 mapping 后保持不变（27 个 SKY130 cell / ctrl case）

## 4. limitation 与边界

| ID | limitation | 实验影响 | 处理 |
|---|---|---|---|
| L31-01 | SKY130 Liberty 不含 `clkinv_1` cell | Stage B CEC 不可达 | N31-03 ORFS techmap library 获取（待用户授权 PDK 下载） |
| L31-02 | 8 case 全 combinational | STA slack=null / slack_status=MET (INF) | N31-05 SKY130 sequential ECO 拓展（待 DFF 进 SDC） |
| L31-04 | failure_recovery 仍是 single-iteration proxy | `avg_iterations=1.0` | X19 multi-iteration refinement（待用户 design 审批） |
| 补充 | METH-12 candidate-specific timing gain 当前是 Stage A proxy | ranking 无法区分 candidate 时序收益 | P1-4（round1 自审稿）：Stage B STA 已接，per-candidate timing gain 待实现 |

## 5. 工具链与可复现性

每个实验目录都有：
- `config.json`：runner 配置
- `environment/toolchain_snapshot.json`：每工具版本、命令、路径、可用性
- `raw_results/`：原始 metrics + Yosys/ABC/OpenSTA 完整日志
- `tables/`：阶段汇总表
- `summary.md`：阶段摘要

工程验证命令：
```bash
$env:PYTHONPATH='src'
python -m unittest discover -s tests  # 90 项通过
```

`python scripts/build_stage_b_summary.py --summary <path> --output-dir <tables>` 可从 stage_b_summary.json 重新生成 case / runtime 表。

## 6. 与 [F08-B]/[B06] 的边界声明

本 Experiments 章节**不引用**：
- [F08-B] DAC 2018 cost-aware multi-target 的算法细节、复杂度或实验数字（仅 B 级证据）
- [B06] BUFFALO 的 9-design PPA 数字与训练规模（仅 B 级证据）
- [T01]/[T02]/[T05] 工业数据与 metal-only 约束下的违例修复率与 runtime
- [B02]/[B03]/[B04]/[B05]/[M01]/[M02] 的训练规模、对照曲线与商业结果

所有数字均来自 `experiments/20260718_minimal_combinational_batch_demo/` 和 `experiments/20260731_epfl_8case_stage_b/` 的本机运行产物，可通过 runner 命令复现。

## 7. 后续修订

- N05 方法符号表获批后，本 Experiments 章节补 X19 multi-iteration refinement 的 ablation 表。
- L01 Related Work 迁入 `paper/submission/` 后，本文的"工具链"段重排并补充引用文献。
- 用户最终审定后迁入 `paper/submission/experiments.md`。
- Stage B CEC 限制修复（SKY130 techmap library）后，本文"形式回验"段补真正的 CEC pass 表。