# FAECO 后续长期推进任务清单

更新时间：2026-07-20

本文档按 **长期执行顺序** 记录后续推进任务。已完成或已有初版的任务会在状态更新中说明；实时状态以 `docs/task_board.md` 和 `docs/project_management/long_term_task_plan.md` 为准。

## 1. 当前总判断

项目当前处于：

> **Phase 4 已收口：Stage A 5-case combinational 原型 + Stage B 8-case 端到端 (mapping→SDC→OpenSTA) 全部跑通；90 项测试全绿；A-only 范围 18 commits 全部入库；下一步 Phase 6 论文写作（PM25/26/27/28）和 N05 方法重写符号表。**

2026-07-31 状态更新：

- F12 已完成：Git 初始化 + A-only 范围 18 commits 入库（`9482a34..16b61a6`），按 handoff `initial_commit_scope_audit.md` 划分（A 核心 135 / B 本机 smoke 51 / C 私有版权 55）；push 待用户决策 remote URL。
- F13 已完成：Python 最小工程骨架 + Stage B 4 个新模块（technology_mapping / sdc / opensta / yosys_abc CEC helper）+ 4 个新脚本（map_epfl_to_sky130 / verify_epfl_mapping_cec / run_stage_b_pre_layout_sta / build_stage_b_summary）；90 项测试通过，0 failure，0 error。
- F19 已完成 Stage B 扩展：mapped-BLIF equivalence helper (`check_mapped_blif_equivalence`) 已就绪，但当前 SKY130 Liberty 不含 `clkinv_1` 导致 ABC `cec` 不可达，已记录 R31-01。
- F22 已完成 Stage B 扩展：failure-aware refinement 仍是 Stage A single-refinement proxy；multi-iteration loop 与 without F1/F3/F4 消融待 X19 design 审批（PM22 in_progress）。
- L01 Related Work 已落地：`paper/draft/related_work.md` 按 6 大主题分组覆盖 25A/1B；严格区分 evidence-level A/B；[F08-B] 和 [B06] 禁止引用算法细节与数字；下一步迁入 `paper/submission/related_work.md`（PM26 pending）。
- N05 方法重写就绪审计已重映射：`method_rewrite_readiness.md` 18 项要素按 Stage B 完成状态更新，METH-02 ready / METH-15 ready / METH-17 partial；下一步产出 N05 方法符号表初稿（PM27 pending）。
- Stage B 8-case 端到端：ctrl/int2float/router/cavlc/dec/priority/adder/max mapping 8/8 success + STA 8/8 success；`stage_b_case_summary.{json,md}` + `stage_b_runtime.{json,md}` 已落盘 `experiments/20260731_epfl_8case_stage_b/tables/`。
- CEC limitation (clkinv_1)、STA slack null (combinational 无 path) 已在 STAGE_B_AGENT_HANDOFF.md / stage_b_deferred_execution_checklist.md / risk_register.md / task_board.md / work_log.md / method_rewrite_readiness.md / L01 Related Work 初稿中标注 A/B 边界。
- 下一批 P0 是：PM22/X19 多轮 refinement 设计（需用户 design 审批）；PM27 N05 方法符号表；PM26 Related Work 迁入 submission/。

2026-07-14 状态更新：

- F01 已形成初版：核心 claim 已抽取到 `docs/paper_audit/claim_evidence_matrix.md`。
- F03 已形成初版：预投稿审计已写入 `docs/paper_audit/pre_submission_review.md`。
- F02 已完成页级校订：C01-C12 已写入 PDF 页码、证据强度和补证据动作，并新增 `legacy_source_locator.md`。
- F04 已完成页级校订：已核对 PDF 标号(1)-(14)/(16)-(20)、图1-9、表1-5；Word 字段更新证明后五式应重编号为(15)-(19)，并确认图6误引和表2四套统计冲突。
- F05 已完成来源治理更新：EPFL `v2025.1` 固定为论文主来源，8 个 Verilog/官方 BLIF blob、MIT 许可和当前 ISCAS85 使用边界已归档；隔离规范化 CEC 为 8/8 pass。
- F06 已形成初版：ECO case schema 已写入 `docs/experiment_design/case_schema.md`。
- F07 已形成初版：baseline protocol 已写入 `docs/experiment_design/baseline_protocol.md`。
- F08 已形成初版：metrics and tables 已写入 `docs/experiment_design/metrics_and_tables.md`。
- F09 已形成初版：failure taxonomy 已写入 `docs/experiment_design/failure_taxonomy.md`。
- F10 已形成初版：FAECO 算法伪代码已写入 `docs/experiment_design/faeco_algorithm.md`。
- F12 已完成：Git 已初始化，当前分支为 `main`。
- F13 已完成：Python 最小工程骨架已建立，基础测试可运行。
- F15 已完成最小批次：c17 N22/N23、c432、c499、c880 共 5 个 cases 已生成；其中 c432/c499/c880 仅作本地 smoke，论文主集待 X21 迁移到 EPFL。
- F17 已完成最小版：已实现简单 Verilog netlist 读取、gate count、logic level 和 fanin cone 表示。
- F18 已完成 fanin 部分：c17 N22 cone 可自动抽取；fanout 和 sequential path cone 待后续扩展。
- F19 已完成 wrapper 初版并由 X18 正式接入：structural signature 与 Yosys-normalized full-netlist ABC `cec` 分离记录；2026-07-20 已批准 formal scope 为门级 full-netlist 全部主输出对比，当前 5-case local smoke formal 为 5/5 pass、ABC baseline 为 5/5 success。
- F20 已完成 5-case baseline 扩展：fixed/random/size-only/critical-path-only/ABC wrapper/FAECO selected 均进入 comparison 表；隔离探针已生成并回验 optimized BLIF，同时确认正式 AIG node/level 指标应取自 ABC `print_stats`，不能使用当前 parser 对 assign/LUT Verilog 的 0-gate 结果。
- Patch candidate 表示已完成最小版：`candidates.json` 和 `selected_patch.json` 可由 flow 写回。
- F21 已完成最小版：`classify_failures` 可识别并记录 F1-F5。
- F22 已完成最小版：`refine_weights` 可将 F1-F5 转为确定性搜索权重和动作日志；c17 已验证 F3/F4 反馈。
- F14 已完成：工具链策略与 `scripts/check_toolchain.ps1` 已建立，首份环境快照已归档；OpenSTA 只读审计已固定官方 commit、Ubuntu 24.04 依赖和 WSL2 推荐路径。2026-07-20 已在 WSL2 中安装依赖、核验 CUDD archive SHA256、构建 OpenSTA 3.1.0，并通过最小 Liberty/Verilog/SDC smoke。
- weighted s-t min-cut 已完成初版：`weighted_st_min_cut_v1` 使用 Edmonds-Karp/residual reachable-set，并有 synthetic regression test 区分全局最小割和单 gate 贪心。
- Patch replacement 草案已完成：`internal_cone_replacement_v0` 可将 selected patch 应用到 cone-level 内部表示，并写回 `metrics.patch_replacement` 与 `patches/replacement.json`。
- Batch runner 骨架已完成：`experiments/configs/minimal_combinational.json` 可驱动 `scripts/run_minimal_combinational_demo.py --config`，并写出 per-run metrics 与 `tables/case_summary.json`。
- c17 N23 第二目标 case 已完成：`data/cases/minimal/iscas85_c17_case02` 可独立生成 metrics、selected patch 和 replacement。
- raw Verilog 导入脚本已完成：`scripts/make_minimal_case_from_raw.py` 可从本地 raw Verilog 生成完整最小 ECO case。
- BENCH 导入脚本已完成：`scripts/make_minimal_case_from_bench.py` 可从本地 ISCAS-style `.bench` 文件生成完整最小 ECO case。
- Genus 风格多行 Verilog parser 已完成：可读取 c432/c499/c880 这类 generic-gate Verilog 的多行 input/output/wire 声明。
- c432/c499/c880 三个独立 ISCAS85 电路已生成 minimal cases 并接入 batch config；当前 `case_count=5`，所有 run 均有 selected patch 和 replacement 输出。
- 当前 5-case ISCAS batch 仅作本地 smoke；c432/c499/c880 上游 license 未声明，不进入论文主实验或可再分发包。
- Related Work 已核验 25 篇 A 级全文和 1 条 B 级官方证据；DAC 2006 SAT Sweeping 已通过归档的 Cadence Labs 正确全文升级为 A，但文献库错配 PDF 继续禁止引用，正确核验缓存也不进入再分发包；LIT-M01/M02 已固定 4154x 非同阶段 STA 加速、跨节点训练仍使用 7-nm 目标设计以及处理后数据/模型/Cadence flow 未公开的边界。DAC 2018 cost-aware multi-target 仍因无合法公开全文保持 B。
- 下一批 P0 是按已批准的门级 formal scope 和 Yosys JSON 权威格式，正式接入显式 ABC 序列与 stats、实现 Yosys JSON importer、导入 EPFL 第一波数据、刷新真实 formal/baseline/runtime，实现多轮 refinement 和 without F1/F3/F4 消融，并基于已安装的 WSL2 OpenSTA 接入 Stage B 路径桥、report parser、WNS/TNS 和 critical path artifact。

进入下一轮代码实现前，以下边界已经明确：

1. 旧 RSECO 论文哪些 claim 可以继承；
2. 哪些 claim 必须由新实验补证据；
3. benchmark flow 应该如何构造；
4. FAECO 的最小原型到底要证明哪些结论。

## 2. 近期优先任务：第 1-2 周

| ID | 任务 | 优先级 | 前置条件 | 交付物 | 完成标准 |
|---|---|---|---|---|---|
| F01 | 抽取旧稿核心 claim | P0 | 学长论文 docx/PDF 已归档 | `docs/paper_audit/claim_evidence_matrix.md` 初版 | 摘要、贡献、结论和实验段中的核心主张全部列出 |
| F02 | 建立 claim-evidence matrix | P0 | F01 | `claim_evidence_matrix.md` 完整版 | 每个 claim 标注已有证据、证据强度、缺口和补证据方式 |
| F03 | 旧稿预投稿审计 | P0 | F01 | `docs/paper_audit/pre_submission_review.md` | 输出 P0/P1/P2 问题清单 |
| F04 | 公式与图表审计 | P0 | 旧稿 PDF/Word | `docs/paper_audit/formula_figure_audit.md` | 缺失公式、符号不一致、图表问题明确 |
| F05 | 第一批 benchmark 候选表 | P0 | benchmark flow 草案 | `docs/experiment_design/benchmark_selection.md` | ISCAS/EPFL/ITC 是否使用、用途和取舍明确 |
| F06 | case schema 定义 | P0 | F05 | `docs/experiment_design/case_schema.md` | original/resynthesized/cone/patch/metrics 字段明确 |

## 3. 实验定义任务：第 2-4 周

| ID | 任务 | 优先级 | 前置条件 | 交付物 | 完成标准 |
|---|---|---|---|---|---|
| F07 | baseline protocol 定稿 | P0 | F05/F06 | `docs/experiment_design/baseline_protocol.md` | fixed min-cut、random、size-only、critical-path-only、ABC baseline 定义清楚 |
| F08 | metrics and tables 定稿 | P0 | F02/F06 | `docs/experiment_design/metrics_and_tables.md` | WNS/TNS、logic level、patch size、runtime、success rate 公式和表模板明确 |
| F09 | failure type 细化 | P0 | `failure_aware_cut.md` | `docs/experiment_design/failure_taxonomy.md` | F1-F5 每类失败有检测条件和反馈动作 |
| F10 | FAECO 算法伪代码 | P0 | F09 | `docs/experiment_design/faeco_algorithm.md` | 输入、输出、循环、停止条件、失败反馈均明确 |
| F11 | ranking 参数方案 | P1 | `patch_ranking.md` | `docs/experiment_design/ranking_parameters.md` | score 各项特征、默认权重、消融方式明确 |

## 4. 工程准备任务：第 3-5 周

| ID | 任务 | 优先级 | 前置条件 | 交付物 | 完成标准 |
|---|---|---|---|---|---|
| F12 | 初始化 Git 仓库 | P0 | 文档结构稳定 | `.git` | 代码和文档进入版本管理 |
| F13 | 建立 Python 项目配置 | P0 | F12 | `pyproject.toml`、测试命令 | 能运行最小测试 |
| F14 | 确定工具链安装策略 | P0 | F07 | `docs/engineering/toolchain_setup.md` | Python、Yosys、ABC、OpenSTA、Z3/NetworkX 的安装方式明确 |
| F15 | 建立最小样例数据 | P0 | F06 | `data/cases/minimal/` | 至少 3 个小型 case 可用于单元测试 |
| F16 | 建立实验目录规范 | P1 | F08 | `experiments/template/` 或说明文档 | 每次实验输出可追溯 |

## 5. 最小原型任务：第 5-9 周

| ID | 任务 | 优先级 | 前置条件 | 交付物 | 完成标准 |
|---|---|---|---|---|---|
| F17 | netlist/graph 最小表示 | P0 | F13/F15 | `src/rseco/netlist` | 能表示小型门级电路 |
| F18 | cone extraction | P0 | F17 | `src/rseco/graph` | 能抽取 fanin/fanout cone |
| F19 | equivalence checking | P0 | F17 | `src/rseco/equivalence` | 能判断两个 cone 是否等价 |
| F20 | fixed min-cut baseline | P0 | F18 | `src/rseco/cut` | 能生成初始 patch boundary |
| F21 | failure classification | P0 | F19/F20 | `src/rseco/cut` | 能识别 F1-F5 至少部分失败类型 |
| F22 | failure-aware refinement | P0 | F21 | `src/rseco/cut` | 能根据失败反馈调整 cut weights |
| F23 | patch ranking | P1 | F20/F21 | `src/rseco/ranking` | 能输出 deterministic score |
| F24 | 最小端到端 demo | P0 | F17-F23 | `experiments/*demo*` | 一个 case 完整跑通 |

## 6. 第一轮实验任务：第 9-13 周

| ID | 任务 | 优先级 | 前置条件 | 交付物 | 完成标准 |
|---|---|---|---|---|---|
| F25 | 批量 combinational benchmark 实验 | P0 | F24 | `experiments/*combinational*` | 至少 8 个来源和许可明确的公开 benchmark 有 formal 可追溯结果 |
| F26 | fixed vs FAECO 对比 | P0 | F25 | result table | 成功率、patch size、runtime 可比较 |
| F27 | failure-aware 消融实验 | P1 | F25/F26 | ablation table | without F1/F3/F4 feedback 等消融完成 |
| F28 | ranking 消融实验 | P1 | F25 | ranking table | random/size/timing/critical-path/FAECO ranking 对比完成 |
| F29 | 失败案例分析 | P1 | F25 | `experiments/*/failure_analysis.md` | 至少列出典型失败和原因 |

## 7. Sequential 场景扩展任务：第 13-18 周

| ID | 任务 | 优先级 | 前置条件 | 交付物 | 完成标准 |
|---|---|---|---|---|---|
| F30 | sequential benchmark 选择 | P1 | F25 | `benchmark_selection.md` 更新 | ITC/ISCAS sequential 目标明确 |
| F31 | reg-to-reg cone extraction 设计 | P1 | F30 | `docs/experiment_design/sequential_cone_flow.md` | 寄存器边界、路径定义明确 |
| F32 | sequential cone demo | P1 | F31/F24 | demo experiment | 能抽取一个路径 cone 并运行 FAECO |
| F33 | 路径级时序指标接入 | P1 | F32 | experiment results | 能输出路径 delay 或 WNS/TNS |
| F34 | sequential 实验总结 | P1 | F32/F33 | `summary.md` | 能说明方法向真实场景迁移的可行性 |

## 8. 论文写作任务：第 16-22 周

| ID | 任务 | 优先级 | 前置条件 | 交付物 | 完成标准 |
|---|---|---|---|---|---|
| F35 | 论文详细大纲 | P0 | F02/F10/F25 | `paper/draft/outline.md` | 章节、图表、证据对应明确 |
| F36 | Introduction 初稿 | P1 | F35 | `paper/draft/introduction.md` | 背景-缺口-方法-证据完整 |
| F37 | Related Work 初稿 | P1 | L01 核心精读与错配文献补档 | `paper/draft/related_work.md` | timing ECO、functional ECO、formal verification、B&G、ML timing 均有已核验来源和明确问题设置边界 |
| F38 | Method 初稿 | P1 | F10/F22 | `paper/draft/method.md` | FAECO 流程、失败反馈、ranking 讲清楚 |
| F39 | Experiments 初稿 | P1 | F25-F29 | `paper/draft/experiments.md` | 表格、指标、结论一致 |
| F40 | Discussion/Limitations | P1 | F29/F34 | `paper/draft/discussion.md` | 适用边界和局限清楚 |
| F41 | 中文论文整合初稿 | P0 | F36-F40 | `paper/draft/faeco_manuscript.md` | 形成完整稿 |

## 9. 投稿准备任务：第 22 周以后

| ID | 任务 | 优先级 | 前置条件 | 交付物 | 完成标准 |
|---|---|---|---|---|---|
| F42 | 内部模拟审稿 | P0 | F41 | `paper/reviews/internal_review.md` | P0/P1/P2 问题清单 |
| F43 | 第一轮大修 | P0 | F42 | revised manuscript | P0/P1 问题关闭 |
| F44 | 确定中文投稿目标 | P1 | F43 | `paper/submission/venue_selection.md` | 目标期刊/会议、格式、字数明确 |
| F45 | 格式整理 | P1 | F44 | formatted manuscript | 符合投稿要求 |
| F46 | 投稿材料准备 | P1 | F45 | cover letter / supplement | 投稿包完整 |
| F47 | 最终归档 | P1 | F46 | final archive | 论文、实验、代码、图表版本一致 |

## 10. 每周推进机制

每周至少更新三个文件：

1. `docs/project_management/weekly_status_template.md` 复制成当周周报；
2. `docs/project_management/long_term_task_plan.md` 或本文档中的任务状态；
3. `docs/task_board.md` 中的近期任务状态。

每周例行检查：

- 当前是否还在正确 Phase；
- 是否有 P0 风险变为 active；
- 实验结果是否能追溯；
- 论文 claim 是否有证据；
- 是否需要调整投稿目标。

## 11. 当前立即执行顺序

从现在开始，建议按下面顺序执行：

1. 将已接入的 Yosys-BLIF-ABC formal/baseline 迁移到 X21 EPFL first wave，生成 license 可用的正式 batch 表。
3. 刷新 5-case formal equivalence、ABC baseline、工具版本和外部 runtime artifacts。
4. 实现真正多轮 refinement loop，并生成 without F1/F3/F4 ablation 配置和表格。
5. 按已批准的 Yosys JSON 权威格式，导入 EPFL ctrl/int2float/router，保留 MIT notice、固定 blob SHA、Yosys JSON、官方 BLIF 回验证据并生成 case。
6. 基于已安装的 WSL2 OpenSTA 3.1.0，设计 Windows-WSL 路径桥接、STA 输入生成、report parser，并把 WNS/TNS、critical path 和 runtime 写入正式 runner artifacts。
7. 基于新实验结果准备组会 PPT 初稿。



