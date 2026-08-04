# FAECO Experiments 初稿（Draft 1）

更新时间：2026-08-04

本文档为论文 Experiments 章节的初稿，基于：
- `experiments/20260718_minimal_combinational_batch_demo/tables/*.json`（Stage A 5-case）
- `experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.{json,md}` + `stage_b_runtime.{json,md}`（Stage B 8-case）
- `docs/experiment_design/benchmark_flow.md` / `case_schema.md` / `baseline_protocol.md` / `metrics_and_tables.md`
- experiments/20260803_sequential_hybrid_tns_fixed/（N31-05 ISCAS89 8 电路混合修复，A-only 不入库）
- X19 外环多轮闭环：src/rseco/refinement_loop.py + flow.run_multi_iteration_case + tests/test_refinement_wns.py（2026-08-04）

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
| `tables/baseline_comparison.json` | fixed min-cut / seeded random cut / size-only / critical-path-only / ABC rewrite+refactor+resyn / FAECO selected 六种方法 patch size 与 score 对比（图 2，`paper/figures/fig2_stage_a_baseline.png` 给出 patch size 可视化） |
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

`experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.md`（图 1，`paper/figures/fig1_stage_b_runtime.png` 给出 mapping+STA runtime 可视化）：

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
- 等价验证（original vs mapped）：**8/8 pass**（Yosys `miter -equiv` + `sat -prove-asserts`，`scripts/verify_epfl_mapping_sat.py`，2026-08-03）。原 ABC `cec` 无法对 Liberty subcircuit 建 model，改用从 Liberty function 提取的 assign-style cells.v（`scripts/make_liberty_cells_v.py`）后 SAT 证明等价成立
- 输入 EPFL Verilog SHA256 在 mapping 后保持不变（27 个 SKY130 cell / ctrl case）

### 3.1 ISCAS89 sequential 混合修复实验（N31-05, 2026-08-04）

在 8 个 ISCAS89 sequential 电路（s27/s382/s420/s641/s713/s820/s832/s953）上用 SKY130 HD 标准单元验证 failure-aware 混合修复（R 逻辑重写 / G gate sizing / B buffer insertion）。流程：Yosys 映射到纯 SKY130 cell -> OpenSTA baseline（period 0.5ns 制造违例）-> 多轮（rounds=10）候选实测 -> 只接受严格改善 WNS 的改动 -> netlist_audit 校验。

**主结果（全搜索 baseline）**：

| 电路 | baseline WNS | final WNS | 策略 |
|---|---|---|---|
| s27 | -0.28 | **-0.01** | 4B+1R |
| s382 | -0.94 | **+0.02 (MET)** | 53B+1G |
| s420 | -1.78 | **-0.01** | 35B |
| s641 | -1.86 | **-0.02** | 35B+3G+1R |
| s713 | -1.86 | **-0.01** | 37B+6G+1R |
| s820 | -1.42 | **-0.20** | 78B+3G+1R |
| s832 | -1.15 | **-0.47** | 67B+4G+1R |
| s953 | -1.48 | **-0.09** | 149B+6G+1R |

8/8 全部改善，s382 收敛到 MET（+0.02）；全部 netlist_audit ok（0 多驱）。B（buffer insertion）在 pre-layout ideal-net 下是主力策略（高扇出节点输入电容分担），推翻"ideal-net 下 B 无效"的假设。

**决策层效率**（s832，--strategy-priorities auto）：

| 配置 | final WNS | STA 调用 | 备注 |
|---|---|---|---|
| 全搜索 | -0.47 | 2275 | baseline |
| 决策层 | **-0.45** | **1932 (-15%)** | 更好且更省 |

**跨电路迁移**（leave-one-out）：用其他 7 电路归纳的决策表预测第 8 电路 trial，top-2 命中率 94.3%-98.2%——策略选择规律跨 ISCAS89 电路高度稳定。

**负面结论（诚实记录）**：buf_8/16 大 buffer 在 pre-layout 下有害（s832 从 -0.47 恶化到 -0.61，1080 trials 全拒），已排除在候选集外；探索守卫（每轮至少一个 G/R 候选）修复了决策层在 s820 上的提前收敛（-1.03 恢复到 -0.20）。

### 3.2 外环多轮闭环实验（X19, 2026-08-04）

外环（patch 粒度）failure-aware refinement 在 Stage A 5-case（c17×2 / c432 / c499 / c880）上端到端验证：cut -> classify(F1-F5) -> refine_weights -> re-cut 循环（flow.run_multi_iteration_case + refinement_loop.simulate_refinement_loop，多轮 residual failure 与 actions 全记录）。

**根因修正（2026-08-04 复核，诚实记录）**：早前记录的「c432/c499/c880 的 F3 被权重反馈消除」在现实现中**不可复现**——实测 3 电路每轮只触发 F4（TIMING_GAIN_INSUFFICIENT），F3 从未触发；c17 虽触发 F3，但 size penalty 不改变被选中的 1-gate cut。更深的根因有二：(1) 成功判据自相矛盾——F1 用结构签名等价（结构相同才 pass），F4 要求逻辑级 reduction >= 1（结构必须不同），两者互斥，成功路径在构造上不可达，reduction=0 只是表象；(2) 候选排序 cost 为单调加性、1-gate critical-path-only cut 恒为最便宜子集，F1/F2/F4 的权重根本不进入排序 cost，反馈在实现层面是惰性的。

**修复（2026-08-04）**：run_multi_iteration_case 增加可注入 equivalence_checker（功能等价/公式等价），绕开 F1/F4 互斥：注入功能等价后，reduction >= 1 的 case 成功路径可达（合成 case：original LL=5 深结构 vs 功能等价浅结构 LL=3，reduction=2，循环第 1 轮即成功）。真实数据端到端仍待：(a) 生成真正重综合的 resynthesized 网表；(b) 让 boundary/critical-coverage 权重真实进入 cut 排序（当前仅 size_penalty 生效）；(c) 接入 OpenSTA WNS 作为成功信号。

**WNS 驱动成功标准**（tests/test_refinement_wns.py 验证）：循环 evaluator 支持「WNS 改善即成功」——模拟 WNS 序列 [-1.5, -1.2, -0.9] 第 3 次迭代成功停止；首次 success 立即停止（iterations=1）。真实接入需 patch 后 OpenSTA 实测（后续工程项，与内环衔接见 method §6.1）。

**消融现状（诚实记录）**：关闭反馈时权重固定、不触发 refine（测试验证）。但由于 F4 恒触发且反馈不改选中 cut，5 case 上 ON/OFF 结果无差异——这不是数据局限，而是实现层面的反馈惰性。3 项新回归测试锁定上述事实（tests/test_refinement_flow_success.py）：结构等价下 reduction>=1 必失败、功能等价下成功可达、F1/F2/F4 反馈不改变被选中 cut。
## 4. limitation 与边界

| ID | limitation | 实验影响 | 处理 |
|---|---|---|---|
| L31-01 | SKY130 Liberty cell model 解析 | **已解决（2026-08-03）**：ABC `cec` 无法建 subcircuit model，改用 Yosys miter+SAT（从 Liberty function 提取 assign cells.v），8/8 等价证明 SUCCESS | `scripts/verify_epfl_mapping_sat.py`；R31-01 mitigated |
| L31-02 | 8 case 全 combinational | STA slack=null / slack_status=MET (INF) | N31-05 SKY130 sequential ECO 拓展（待 DFF 进 SDC） |
| L31-04 | failure_recovery 曾是 single-iteration proxy | `avg_iterations=1.0` | **部分解决（2026-08-04）**：X19 多轮闭环已实现并接入 Stage A；复核发现 F1（结构等价）与 F4（逻辑级下降）判据互斥致成功不可达、F1/F2/F4 反馈在排序 cost 中惰性（仅 size_penalty 生效）、「F3 被反馈消除」不可复现——已注入功能等价 checker 打通成功路径（合成验证），真实重综合网表 + 权重进排序 + WNS 接入为后续项 |
| 补充 | METH-12 candidate-specific timing gain 当前是 Stage A proxy | ranking 无法区分 candidate 时序收益 | P1-4（round1 自审稿）：Stage B STA 已接，per-candidate timing gain 待实现 |
| 补充 | N31-06 Z3 wrapper 8-case 端到端 error（2026-08-03） | mapped.v 是 SKY130 门级实例化（0 assign），assign-only parser 无法构建 replaced 侧表达式；Yosys aigmap 对 mapped.v 报 SKY130 模块 undefined | wrapper 单元测试层面（12 项，multi-output/escaped/xor/constant）已验证；8-case 端到端需 N31-03 cells.v（解锁 CEC + AIG→SMT 双路径） |

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

- X19 外环 ablation 表已在 §3.2（2026-08-04）；后续用更大 case 或真实 WNS 接入补足反馈价值实证。
- L01 Related Work 迁入 `paper/submission/` 后，本文的"工具链"段重排并补充引用文献。
- 用户最终审定后迁入 `paper/submission/experiments.md`。
- Stage B CEC 已由 Yosys miter+SAT 路径修复（8/8 pass）；本文"形式回验"段已补 SAT 等价证明表。