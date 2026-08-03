# Experiments

每次实验运行使用独立子目录，论文中的每张结果表都必须能追溯到这里的实验输出。

```text
YYYYMMDD_short_name/
|-- config.json
|-- environment/
|   `-- toolchain_snapshot.json
|-- logs/
|-- raw_results/
|-- tables/
|-- figures/
`-- summary.md
```

## 配置目录

| 文件 | 用途 |
|---|---|
| `configs/minimal_combinational.json` | 最小 batch runner 配置；当前包含 c17 的 N22/N23 smoke cases，以及 c432/c499/c880 三个独立 ISCAS85 combinational cases |

## 当前实验

| 实验目录 | 说明 | 生成命令 |
|---|---|---|
| `20260717_minimal_combinational_demo/` | 本地 c17 单 case combinational demo，包含 selected patch、replacement、ranking 和 failure feedback 输出 | `python scripts/run_minimal_combinational_demo.py` |
| `20260718_minimal_combinational_batch_demo/` | 配置驱动 batch demo，写出 per-run raw metrics、`tables/case_summary.json` 和 `tables/baseline_comparison.json/md`；当前 `case_count=5`，其中 3 个是独立 ISCAS85 电路 `c432/c499/c880` | `python scripts/run_minimal_combinational_demo.py --config experiments/configs/minimal_combinational.json --output-dir experiments/20260718_minimal_combinational_batch_demo` |

当前 5-case batch 是工程 smoke，不是论文主实验集。c432/c499/c880 来自 license 未声明的第三方整理仓库；来源边界和 EPFL `v2025.1` 替代方案见 `docs/experiment_design/benchmark_source_and_license_audit.md`。

Git 忽略的 X21 readiness probe 已验证 8 个固定 EPFL Verilog 经 Yosys 规范化后与同 tag 官方 BLIF 的 ABC CEC 全部通过，stats 也一致；该 probe 不属于本目录的正式实验，尚未创建 EPFL case、batch config 或论文结果表。2026-07-20 已批准 Yosys JSON 作为 FAECO 权威内部格式，正式导入下一步是实现 JSON importer、case 构造和官方 BLIF 回验产物写回。同日 OpenSTA 已在 WSL2 中构建并通过 `tmp/faeco_opensta_smoke_20260720_01/` 最小 STA smoke，但尚未作为 Stage B runner 写入本目录正式实验表。

2026-07-31 更新：Stage B 已端到端跑通。`20260731_epfl_8case_stage_b/` 含 ctrl/int2float/router/cavlc/dec/priority/adder/max 共 8 个 case 的 mapping+STA 完整产物，`tables/stage_b_case_summary.{json,md}` 和 `stage_b_runtime.{json,md}` 已落盘；`20260731_epfl_ctrl_sky130_mapping/` 保留 ctrl 的 SKY130 Liberty mapping 单 case 产物；`20260731_epfl_ctrl_stage_b/` 保留 ctrl 端到端试点产物。Stage B runner 命令：

```bash
python scripts/run_stage_b_pre_layout_sta.py \
    --output-dir experiments/20260731_epfl_8case_stage_b \
    --sta-command "wsl -d Ubuntu -- /usr/local/bin/sta"
```

CEC 形式回验（mapped-BLIF vs original-normalized）当前 SKY130 Liberty 不含 `sky130_fd_sc_hd__clkinv_1` 导致 ABC `cec` 不可达，所有 8 case CEC 跑出 `unavailable`，已记录于 `risk_register.md` R31-01 与 `STAGE_B_AGENT_HANDOFF.md` limitation 段落。`experiments/20260720_epfl_wave1_yosys_json/` 与 `experiments/20260728_epfl_wave2_yosys_json/` 是 X21 的 EPFL Yosys JSON 导入实验。

2026-08-03 更新：N31-06 Z3 candidate/boundary formal wrapper 已实施（`src/rseco/z3_formal.py` + 12 项 TDD 测试）。`20260731_epfl_8case_stage_b/z3_boundary/` 是 N31-06 8-case runner 实验产物（`scripts/run_z3_candidate_boundary_check.py`），8-case 端到端全 error 是诚实 limitation（mapped.v 是 SKY130 门级实例化，assign-only wrapper 无法构建 replaced 侧表达式；需 N31-03 cells.v 解锁 AIG→SMT），记录于 R0803-01。该目录是实验产物，不进入 A-only 范围。

## 当前表格产物

| 文件 | 说明 |
|---|---|
| `20260718_minimal_combinational_batch_demo/environment/toolchain_snapshot.json` | 本次实验运行时的工具链快照，记录 Python、Yosys、ABC、OpenSTA、Z3、NetworkX 的可用状态、命令、路径和版本；当前记录 Yosys 0.9、`yosys-abc` ABC 1.01、OpenSTA 3.1.0 和 NetworkX 3.4.2 可用，Z3 不可用 |
| `20260718_minimal_combinational_batch_demo/tables/case_summary.json` | 每个 run 的 selected patch、rank、score、replacement status、failure types、structural equivalence result、formal equivalence status/reason、ABC baseline status/reason、Python flow runtime、结构化 `runtime` stage schema、`toolchain_snapshot` 路径和 `toolchain` 可用性 map |
| `20260718_minimal_combinational_batch_demo/tables/baseline_comparison.json` | 从同一 metrics 中抽取 fixed min-cut、seeded random cut、size-only、critical-path-only、ABC rewrite/refactor/resyn 与 FAECO selected candidate 的 patch size、score、change ratio、formal equivalence status/reason、ABC baseline status/reason、Python flow runtime 和结构化 `runtime` stage schema 对比；random 当前使用 `seed=20260714`、`trials=5` |
| `20260718_minimal_combinational_batch_demo/tables/baseline_comparison.md` | 可直接阅读的多 baseline vs FAECO patch-size 对比表 |
| `20260718_minimal_combinational_batch_demo/tables/failure_recovery.json` | Stage A proxy failure recovery 表，按 failure type 聚合 initial fail count、proxy recovered count、recovery rate 和 run ids |
| `20260718_minimal_combinational_batch_demo/tables/failure_recovery.md` | 可直接阅读的 failure recovery proxy 表；当前 `avg_iterations=1.0` 来自已记录的 single-refinement iteration count，不是多轮恢复统计 |
| `20260718_minimal_combinational_batch_demo/tables/runtime_breakdown.json` | 从 per-case `metrics.runtime` 汇总出的 runtime stage 表，记录 stage duration、status、category 和 tool |
| `20260718_minimal_combinational_batch_demo/tables/runtime_breakdown.md` | 可直接阅读的 batch runtime breakdown 表；状态和类别细节保留在 JSON 中 |

## 当前边界

- batch 输出已经从 c17 双目标 smoke 扩展为最小多电路 combinational 实验，并调用 Yosys/ABC 生成 formal/baseline artifact；c432/c499/c880 仍因来源 license 未完备只作为本地 smoke，不进入论文主表。
- single-case 和 batch runner 均已在实验目录下归档 `environment/toolchain_snapshot.json`，并把 `toolchain_snapshot` 路径与 `toolchain` 可用性 map 写入 `config.json`；snapshot 每个工具条目包含 `version` 字段，当前 batch 记录 Python 3.11.9、Yosys 0.9、UC Berkeley ABC 1.01、OpenSTA 3.1.0、NetworkX 3.4.2，Z3 版本为 `null`。
- `baseline_comparison` 目前比较 fixed min-cut、seeded random cut、size-only、critical-path-only、ABC rewrite/refactor/resyn 与 FAECO selected；ABC baseline 当前为 Yosys-normalized BLIF 输入、显式 rewrite/refactor/resyn 序列、ABC `print_stats` 和 CEC backcheck，5 个 local smoke 均为 `success`。
- `failure_recovery` 当前是 Stage A proxy：初始触发某 failure type 的 run 若最终 `replacement_status=applied`，则计为 proxy recovered。当前 `avg_iterations=1.0` 只表示每个 recovered run 记录了 1 次 single-refinement proxy iteration；它可以用于跟踪 failure-aware candidate generation 是否产生可应用 replacement，但还不是多轮迭代恢复率。
- `equivalence_result=pass` 当前仍来自 structural signature；`formal_equivalence_result` 另行记录 Yosys-normalized full-netlist ABC CEC。当前 5-case local smoke 的 formal 为 5/5 `pass`，并归档 normalized BLIF、sanitized Verilog（仅 BOM 输入需要）、ABC CEC log、命令、scope 和 runtime。
- `runtime_total` 和 `runtime_breakdown` 保持兼容字段；新增 `metrics.runtime` 结构化 stage schema，并汇总到 `tables/runtime_breakdown.json/md`。当前 `formal_equivalence` 与 `abc_baseline` 阶段是 `external_tool_wrapper`，已记录真实 Yosys/ABC runtime；OpenSTA 3.1.0 本体已可用，但 Stage B 的真实 STA runtime、WNS/TNS 和 report parser 仍待写入同一 schema 和表格。
