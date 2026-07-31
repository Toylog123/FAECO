# Metrics and Tables

更新时间：2026-07-20

本文档定义 FAECO 的评价指标、结果表模板，以及当前 Stage A 原型已经生成的可追溯表格。

## 1. 指标分层

| 层级 | 指标 | Stage A | Stage B |
|---|---|---|---|
| 正确性 | equivalence result、equivalence pass rate | 必须 | 必须 |
| 时序收益 | logic level reduction、critical cone depth | 必须 | 可选 |
| 真实时序 | WNS、TNS、violating paths | 可选 | 必须 |
| 修改规模 | patch size、change ratio | 必须 | 必须 |
| 搜索质量 | recovery success rate、iteration count | 必须 | 必须 |
| 工程效率 | runtime total、runtime breakdown | 必须 | 必须 |
| 稳定性 | timeout rate、failure type distribution | 建议 | 建议 |

## 2. 核心指标定义

| 指标 | 定义 | 说明 |
|---|---|---|
| `patch_size` | patch 中 gate 数 | 修改规模的主要指标 |
| `change_ratio` | `patch_size / original_gate_count` | 用于跨 benchmark 比较 |
| `logic_level_reduction` | `logic_level_before - logic_level_after` | Stage A 的时序 proxy |
| `critical_coverage` | patch 覆盖的关键路径节点数 / 关键路径节点数 | 衡量 cut 是否命中关键路径 |
| `equivalence_pass_rate` | pass candidate 数 / candidate 总数 | 衡量边界合法性和验证结果 |
| `formal_equivalence_result` | ABC/SAT wrapper 返回的 pass/fail/timeout/error/unavailable | 当前正式 runner 使用 Yosys-normalized full-netlist BLIF + ABC `cec`；无 Yosys/ABC 时必须记录 `unavailable` 而不是 pass |
| `abc_baseline_status` | ABC rewrite/refactor/resyn baseline 的 success/timeout/error/unavailable | 当前正式 runner 使用 Yosys-normalized BLIF + `yosys-abc -s` 显式序列，并记录 optimized BLIF、stats、日志和 CEC backcheck |
| `toolchain_snapshot` | 当前实验目录中的工具链快照 JSON 路径 | single-case 和 batch runner 已写入 `config.json`；batch `case_summary.json` 逐行透传该路径；snapshot 工具条目含 `version` 字段 |
| `toolchain` | 当前实验运行时的工具可用性 map | 已覆盖 `python/yosys/abc/opensta/z3/networkx`，用于解释 unavailable baseline 和 verification 结果 |
| `recovery_success_rate` | 初始失败后 refinement 成功数 / 初始失败数 | FAECO 核心指标 |
| `failure_recovery` | 按 failure type 聚合的恢复统计表 | 当前 batch 已有 Stage A proxy 表；proxy recovered 表示 run 最终 `replacement_status=applied`，还不是多轮迭代恢复率 |
| `runtime_total` | 单个 case 从读取到输出结果的 wall-clock 时间 | 当前原型已测量 Python flow runtime；外部 EDA runtime 待接入 |
| `runtime` | 结构化 runtime stage schema | `schema_version=1`，包含 `total_s` 和 `stages[]`；每个 stage 记录 `id/category/tool/status/duration_s`，用于区分 Python flow 和外部工具 wrapper/真实工具耗时 |
| `runtime_verification` | 等价验证总时间 | 验证成本 |
| `WNS_improvement` | `WNS_after - WNS_before` | Stage B 使用，负值越接近 0 越好 |
| `TNS_improvement` | `TNS_after - TNS_before` | Stage B 使用 |

## 3. 状态码

| 状态 | 含义 |
|---|---|
| `success` | 等价通过，且达到最小时序收益和修改规模要求 |
| `non_equivalent` | 等价验证失败 |
| `boundary_invalid` | 边界不闭合或 mapping 不完整 |
| `patch_too_large` | patch size 或 change ratio 超阈值 |
| `timing_not_improved` | 时序收益不足 |
| `verification_timeout` | 等价验证超时 |
| `case_timeout` | 整个 case 超时 |

## 4. Benchmark Summary

| Suite | Circuit | Type | Gates | PIs | POs | Original LL | Resyn LL | Cases |
|---|---|---|---:|---:|---:|---:|---:|---:|
| ISCAS85 | c432 | combinational | TBD | TBD | TBD | TBD | TBD | TBD |

## 5. Main Comparison

| Case | Method | Status | Eq Pass | LL Before | LL After | LL Gain | Patch Size | Change Ratio | Runtime(s) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| TBD | fixed min-cut | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| TBD | FAECO | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

当前原型表：`experiments/20260718_minimal_combinational_batch_demo/tables/baseline_comparison.json` 和 `baseline_comparison.md` 已从同一 per-case metrics 中抽取 fixed min-cut、seeded random cut、size-only、critical-path-only、ABC rewrite/refactor/resyn 与 FAECO selected candidate 的 patch size、score、change ratio 和 runtime 对比。random cut 当前使用固定 `seed=20260714` 和 `trials=5`，先作为 Stage A aggregate baseline；ABC baseline 已生成 optimized BLIF、ABC `print_stats`、日志和 CEC backcheck，当前 5-case local smoke 均为 `success`。该表是 Main Comparison 的 Stage A 雏形，但 c432/c499/c880 仍只作 license 未完备的本地 smoke，不是论文主结果表。

## 6. Failure Recovery

| Failure Type | Initial Fail Count | Recovered Count | Recovery Rate | Avg Iterations | Avg Runtime(s) |
|---|---:|---:|---:|---:|---:|
| F1 | TBD | TBD | TBD | TBD | TBD |
| F2 | TBD | TBD | TBD | TBD | TBD |
| F3 | TBD | TBD | TBD | TBD | TBD |
| F4 | TBD | TBD | TBD | TBD | TBD |
| F5 | TBD | TBD | TBD | TBD | TBD |

当前 batch 表：`experiments/20260718_minimal_combinational_batch_demo/tables/failure_recovery.json` 和 `failure_recovery.md` 已从 5 个 case 的 `failure_types`、`replacement_status` 与 `refinement_iteration_count` 汇总生成。当前 5 个 case 均触发 F3/F4，且 replacement 状态均为 `applied`，因此 Stage A proxy recovery rate 为 1.000，`avg_iterations=1.0`。该口径只表示“初始 failure 后产生了可应用 replacement，且每个 recovered run 记录了 1 次 single-refinement proxy iteration”，不表示多轮迭代恢复率。ABC full-netlist formal 已在当前 5-case local smoke 中通过，但它不是 candidate/boundary-level patch formal。

## 7. Ablation

| Method | Success Rate | Eq Pass Rate | Avg LL Gain | Avg Patch Size | Avg Runtime(s) |
|---|---:|---:|---:|---:|---:|
| fixed min-cut | TBD | TBD | TBD | TBD | TBD |
| FAECO full | TBD | TBD | TBD | TBD | TBD |
| without F1 | TBD | TBD | TBD | TBD | TBD |
| without F3 | TBD | TBD | TBD | TBD | TBD |
| without F4 | TBD | TBD | TBD | TBD | TBD |

## 8. Runtime Breakdown

| Case | Parse | Cone Extraction | Structural Equivalence | Formal Equivalence | ABC Baseline | Cut Search | Ranking | Replacement | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

当前原型同时保留兼容字段 `runtime_total`、`runtime_breakdown` 和结构化字段 `runtime`。`runtime.stages[]` 当前包含 `parse_netlists`、`cone_extraction`、`equivalence`、`formal_equivalence`、`abc_baseline`、`cut_search`、`ranking`、`replacement`；其中 `formal_equivalence` 和 `abc_baseline` 的 `category` 为 `external_tool_wrapper`，当前 5-case local smoke status 分别为 `pass` 和 `success`，耗时为真实 Yosys/ABC 调用 wall-clock。OpenSTA Stage B 接入后，STA 阶段应继续写入同一 schema。

当前 batch 表：`experiments/20260718_minimal_combinational_batch_demo/tables/runtime_breakdown.json` 和 `runtime_breakdown.md` 已从 5 个 case 的 per-case `metrics.runtime` 汇总生成。JSON 保留 stage status/category/tool，Markdown 提供可读耗时表。论文中引用 runtime 时应优先追溯到 JSON，再按需要排版为最终表格。

## 9. Stage B Timing Table

| Case | Method | WNS Before | WNS After | TNS Before | TNS After | Violating Paths Before | Violating Paths After | Patch Size | Runtime(s) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| TBD | FAECO | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## 10. Reporting Rules

1. 不只报告成功 case，也报告失败和 timeout。
2. 不只报告平均值，要保留每个 benchmark 的原始结果。
3. Stage A 不声称真实 WNS/TNS，只报告 logic-level timing proxy。
4. Stage B 接入 OpenSTA 后再正式报告 WNS/TNS。
5. 所有表格必须能追溯到 `experiments/*/raw_results/`、`experiments/*/tables/` 和同目录下的 `environment/toolchain_snapshot.json`。

## 11. 当前缺口

- `baseline_comparison` 目前覆盖 fixed min-cut、seeded random cut、size-only、critical-path-only、ABC rewrite/refactor/resyn 与 FAECO selected。
- `failure_recovery` 当前已有 Stage A proxy 表，`avg_iterations=1.0` 来自 single-refinement proxy iteration log；后续需要实现和记录真正多轮 refinement loop，才能报告 recovery iterations 分布和多轮恢复率。
- single-case 和 batch runner 已归档 `environment/toolchain_snapshot.json`，并把 `toolchain_snapshot` 与 `toolchain` 写入 `config.json`；batch summary 逐行记录工具可用性。当前 batch 快照显示 Python 3.11.9、Yosys 0.9、UC Berkeley ABC 1.01、OpenSTA 3.1.0、NetworkX 3.4.2 可用；Z3 不可用。
- ABC rewrite/refactor/resyn baseline 已接入正式 runner；当前 5-case local smoke 均为 `success`，并生成 optimized BLIF、ABC stats、日志和 original/optimized CEC backcheck。
- `runtime_total`、`runtime_breakdown`、结构化 `runtime` schema 和 batch `runtime_breakdown` 表已覆盖 Python flow 与 Yosys/ABC external tool stages；OpenSTA Stage B 真实 runtime 尚未接入。
- `equivalence_result=pass` 当前来自 structural signature；`formal_equivalence_result` 已接入 Yosys-BLIF-ABC full-netlist CEC，当前 5-case local smoke 均为 `pass`。该结果不能外推为 candidate/boundary formal，也不能把 license 未完备的 ISCAS case 写入论文主表。
