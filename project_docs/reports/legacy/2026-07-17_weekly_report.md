# 2026-07-17 周进度报告

周次：FAECO 最小工程闭环推进周

日期范围：2026-07-15 至 2026-07-18

当前阶段：Phase 3 最小算法原型已经形成闭环，Phase 4 已跑通 c17 combinational demo。Phase 1/2 的旧稿审计和实验协议仍需继续校订。

## 1. 本周完成

| ID | 任务 | 证据/产物 |
|---|---|---|
| W01 | 实现 fixed min-cut baseline 最小接口 | `src/rseco/cut.py`，c17 N22 cone 可生成 `fixed_min_cut` boundary |
| W02 | 实现 patch candidate 表示和写回 | `src/rseco/patch.py`，`data/cases/minimal/iscas85_c17_case01/patches/` |
| W03 | 实现 failure-aware refinement 最小接口 | `src/rseco/refinement.py`，F1-F5 可生成确定性权重调整和动作日志 |
| W04 | 将 F3/F4 failure feedback 写入 c17 metrics | `data/cases/minimal/iscas85_c17_case01/results/metrics.json`，当前 failure types 为 `F3_patch_too_large`、`F4_timing_gain_insufficient` |
| W05 | 建立工具链检测脚本和环境快照 | `scripts/check_toolchain.ps1`、`experiments/environment/toolchain_2026-07-15.json`，Python 和 NetworkX 可用，Yosys/ABC/OpenSTA/Z3 未检出 |
| W06 | 实现 deterministic patch ranking | `src/rseco/ranking.py`、`tests/test_ranking.py`，支持 timing gain、patch size、boundary complexity、verification cost、equivalence confidence 综合评分 |
| W07 | 将 ranking 接入 c17 flow | `src/rseco/flow.py`，`selected_patch` 写回 `rank`、`score`、`ranking_features` |
| W08 | 实现最小 combinational demo runner | `scripts/run_minimal_combinational_demo.py`，可生成独立实验目录 |
| W09 | 跑通 c17 最小 combinational demo | `experiments/20260717_minimal_combinational_demo/`，包含 `config.json`、`raw_results/metrics.json`、`summary.md` |
| W10 | 将 F3 size penalty 接入确定性 cut candidate 生成 | `src/rseco/cut.py`、`src/rseco/graph.py`，refinement 后额外生成 `size_refined_cut` |
| W11 | 实现多候选 ranking 输出 | `patch_ranking` 当前包含 `size_refined_cut` 和 `fixed_min_cut`，并选择 score 更高的 `size_refined_cut` |
| W12 | 建立 weighted cut graph 最小接口 | `src/rseco/cut.py`，metrics 写回 `cut_graph.nodes` 和 `cut_graph.node_costs` |
| W13 | 升级为 s-t split graph 表示 | `cut_graph.split_edges` 记录 `gate:in -> gate:out` 容量边，`dependency_edges` 记录 fanin 依赖边 |
| W14 | 写回 `weighted_st_min_cut_v1` cut result | c17 当前 cut edge 为 `NAND2_5:in -> NAND2_5:out`，cut cost 为 `3.0` |
| W15 | 实现真正 weighted s-t min-cut 初版 | `src/rseco/cut.py` 使用 Edmonds-Karp 和 residual reachable-set 求解，synthetic regression test 可区分单 gate 贪心和全局最小割 |
| W16 | 扩展回归测试 | 2026-07-18 运行 `$env:PYTHONPATH='src'; python -m unittest discover -s tests`，35 个测试通过，覆盖 replacement、batch runner、case variant 生成器、raw Verilog 和 BENCH case 导入脚本 |
| W17 | 实现 patch replacement 草案 | `src/rseco/replacement.py`，selected patch 可应用到 cone-level 内部表示 |
| W18 | 写回 replacement artifacts | `patches/replacement.json` 和 `metrics.patch_replacement` 记录 replaced/preserved gates、boundary、patched outputs 和 status |
| W19 | 实现配置驱动 batch runner 骨架 | `scripts/run_minimal_combinational_demo.py --config` 支持多个 run_id，并写出 per-run metrics、`tables/case_summary.json` 和 batch summary |
| W20 | 生成 batch smoke 实验 | `experiments/configs/minimal_combinational.json`、`experiments/20260718_minimal_combinational_batch_demo/`；当前两个 run 均来自 c17，但分别指向 `N22` 和 `N23` |
| W21 | 生成 c17 第二目标 case | `data/cases/minimal/iscas85_c17_case02/`，target output 为 `N23`，可独立生成 metrics、selected patch 和 replacement |
| W22 | 将 batch config 升级为双目标 case smoke | batch 当前包含 `c17_n22_baseline` 和 `c17_n23_variant`，分别对应 c17 的 `N22` 和 `N23` target-output case |
| W23 | 实现 raw Verilog 到最小 case 导入脚本 | `scripts/make_minimal_case_from_raw.py` 可从本地 raw Verilog 生成完整最小 ECO case；已用测试中的临时 raw netlist 验证 |
| W24 | 记录独立 benchmark 数据缺口 | 已探测公开 raw URL，但未获得稳定可靠来源；未引入来源不明的 `c432`/`c499` 文件 |
| W25 | 实现 BENCH 到最小 case 导入脚本 | `scripts/make_minimal_case_from_bench.py` 可从本地 ISCAS-style `.bench` 文件生成完整最小 ECO case；当前支持 `NAND`、`AND`、`OR`、`NOR`、`NOT`、`BUF`、`XOR`、`XNOR` |

## 2. 当前 demo 状态

| 项 | 当前值 | 证据 |
|---|---|---|
| case | `iscas85_c17_case01` | `data/cases/minimal/iscas85_c17_case01/` |
| target output | `N22` | `results/metrics.json` |
| cone gates | `NAND2_1`, `NAND2_2`, `NAND2_3`, `NAND2_5` | `cone.gates` 字段 |
| initial feedback | `F3_patch_too_large`, `F4_timing_gain_insufficient` | `failure_types` 字段 |
| refinement actions | `increase_size_penalty`, `increase_critical_coverage_reward` | `refinement.actions` 字段 |
| cut graph method | `weighted_st_min_cut_v1` | `cut_result.method` 字段 |
| cut graph source/sink | `source` / `N22` | `cut_graph.source`、`cut_graph.sink` 字段 |
| selected cut edge | `NAND2_5:in -> NAND2_5:out` | `cut_result.cut_edges` 字段 |
| selected gates | `NAND2_5` | `cut_result.selected_gates` 字段 |
| ranked candidate 1 | `patch_N22_size_refined_cut`，patch size 1，score -3.0 | `patch_ranking[0]` |
| ranked candidate 2 | `patch_N22_fixed_min_cut`，patch size 4，score -8.0 | `patch_ranking[1]` |
| selected patch | `patch_N22_size_refined_cut` | `selected_patch` 字段 |
| patch replacement | `internal_cone_replacement_v0`，替换 `NAND2_5`，保留 `NAND2_1`, `NAND2_2`, `NAND2_3` | `patch_replacement` 字段 |
| batch runner | `minimal_combinational_batch`，2 个 c17 target-output case run | `experiments/20260718_minimal_combinational_batch_demo/tables/case_summary.json` |
| equivalence | `pass`，method=`structural_signature` | `equivalence` 字段 |
| 实验目录 | `experiments/20260717_minimal_combinational_demo/` | `summary.md` 和 `raw_results/metrics.json` |

## 3. 当前问题

| ID | 问题 | 影响 | 处理计划 |
|---|---|---|---|
| Q01 | `weighted_st_min_cut_v1` 已有通用 min-cut 初版，但仍只在 c17 和 synthetic cone 上验证 | 算法核心不再是单 gate 贪心，但还不能替代批量 benchmark 证据 | 下一步接入多 case runner，并扩大回归 case |
| Q02 | patch replacement 当前是 cone-level 内部表示，不是可综合 Verilog 写回 | 可以支撑工程闭环记录，但还不能交给 EDA 工具重跑综合/验证 | 后续实现 Verilog patch 写回或 ABC/Yosys 接口 |
| Q03 | equivalence 仍是 structural signature，不是 SAT/ABC/Z3 形式化验证 | 只能作为早期工程 smoke test，不能支撑最终论文实验 | 后续接 ABC SAT 或 Z3 miter，并保留 structural signature 作为快速检查 |
| Q04 | 当前 batch demo 仍只有 ISCAS85 c17 一个真实电路，虽然已有 N22/N23 两个 target-output case | 不能形成跨电路统计结果，也不能支撑论文结果表 | 获取并校验多个真实 ISCAS85 独立电路 raw Verilog 或 `.bench` 文件，再用导入脚本生成 case |
| Q05 | Yosys/ABC/OpenSTA/Z3 当前未检出 | 暂时不能跑真实重综合、ABC baseline、OpenSTA timing 和 SAT 验证 | 保留检测脚本，后续安装工具链并把版本写入每次实验 config |
| Q06 | Git 仓库尚未创建首次提交 | 已有工作区结构和代码，但没有可回退基线 | 确认提交策略后创建首次提交，尤其要决定是否纳入原始材料目录 |

## 4. 下周计划

| ID | 任务 | 优先级 | 完成标准 |
|---|---|---|---|
| N01 | 获取并导入真实独立电路 cases | P0 | 至少 3 个 ISCAS85 独立 combinational 电路 raw Verilog 或 `.bench` 文件来源可追溯，生成 case 后接入 batch config，并产生统一 metrics 和 summary |
| N02 | 将 baseline 和指标协议转为实验配置 | P0 | 形成可被脚本读取的 config 草案，覆盖 fixed、size-refined、weighted cut、ranking 和 replacement 输出 |
| N03 | 扩大 weighted min-cut 和 replacement 回归测试 | P0 | 覆盖多 cut edges、tie-breaking、single-root c17 和后续多 case |
| N04 | 设计 Verilog patch 写回路径 | P0 | 明确从 internal replacement 到 patched netlist 的序列化方案 |
| N05 | 校订旧稿 claim-evidence matrix | P0 | 每个旧稿核心 claim 都标明证据强度、继承方式和新实验补证据方案 |
| N06 | 校订公式与图表审计 | P0 | 用 PDF 逐项核对缺失公式、图号、表号和实验数据来源 |
| N07 | 准备组会 PPT 初稿 | P1 | 形成 12-15 页 PPT 结构，能讲清旧问题、新主线、当前 demo 和下周计划 |

## 5. 风险变化

| 风险 ID | 变化 | 处理 |
|---|---|---|
| R01 | 旧代码不可复现风险继续存在，但工程替代路线更清楚 | 继续以公开 benchmark 和自建 flow 为主证据 |
| R02 | 可复现实验风险有所降低 | 已有 demo runner、独立实验目录和回归测试，后续扩展批量 case |
| R03 | 方法创新性风险有所降低 | failure-aware feedback、weighted min-cut 和 cone-level replacement 已有初版；下一步用多 case 结果补证据 |
| R04 | 工具链风险仍为 active | 当前只确认 Python/NetworkX 可用，Yosys/ABC/OpenSTA/Z3 仍需安装或配置 |
| R05 | 论文证据链风险仍为 active | PM05/PM07 未完成，需要继续校订旧稿 claim 和公式图表 |

## 6. 需要确认的决策

1. patch replacement 是否继续先走内部数据结构，再逐步输出可综合 Verilog。
2. 下一个 P0 工程任务是否优先扩展多 case runner，而不是先接外部 EDA 工具链。
3. 组会汇报是否采用“FAECO 最小闭环已跑通，但论文级工具链与批量实验尚未完成”的表述。
4. 创建首次提交前，是否纳入 `论文/`、`课题构想/`、`ECO相关文献/` 等原始材料目录。

## 7. 本周结论

本周后半段完成了 FAECO 从“设计文档和单一 fixed cut demo”到“带 failure feedback、候选生成、ranking、实验目录、回归测试、weighted s-t min-cut 和 cone-level replacement”的最小工程闭环。当前 c17 demo 已能记录初始失败类型，将 F3/F4 转化为权重调整，生成更小的 `size_refined_cut`，并通过 deterministic ranking 选择该 candidate。7 月 18 日进一步把 cut graph 升级为 s-t split graph 表示，`solve_weighted_cut` 已由单 gate 最低成本选择升级为 Edmonds-Karp/residual reachable-set min-cut，并在 metrics 中写回 split edges、dependency edges、`selected_gates`、cut edges 和 `patch_replacement`。

这个结果还不是论文级实验结论。当前最关键的工程缺口已经从“实现真正 min-cut / patch replacement”转为“获取可追溯 raw benchmark，并把 batch runner 从 c17 双目标 smoke 扩展成真实多 benchmark 实验”。下一步应优先获取并校验至少 3 个 ISCAS85 独立 combinational 电路 raw Verilog 或 `.bench` 文件，用导入脚本生成 case，把 replacement 输出纳入统一 summary，再决定是否向可综合 Verilog patch 写回推进。
