# 2026-07-14 周进度报告

周次：课题接手与项目重启周

日期范围：2026-07-07 至 2026-07-14

当前阶段：Phase 1，论文证据审计

## 1. 本周完成

| ID | 任务 | 证据/产物 |
|---|---|---|
| W01 | 固定新研究主线 | `docs/mainline.md`，方法名暂定为 FAECO，中文题目暂定为“基于验证反馈的重综合辅助时序 ECO 框架” |
| W02 | 完成工程目录初步重构 | `docs/engineering_structure.md`，并保留 `论文/`、`课题构想/`、`ECO相关文献/` 原始材料目录 |
| W03 | 归纳原始材料 | `docs/materials/original_materials_index.md`、`docs/materials/rseco_legacy_paper_summary.md`、`docs/materials/materials_to_paper_mapping.md` |
| W04 | 建立项目管理体系 | `docs/project_management/roadmap.md`、`milestones.md`、`long_term_task_plan.md`、`future_task_backlog.md`、`risk_register.md`、`decision_log.md` |
| W05 | 完成本周汇报规划 | `docs/reports/2026-07-14_weekly_report_plan.md`，已形成 12-15 页 PPT 叙事结构 |
| W06 | 启动旧稿证据审计 | `docs/paper_audit/claim_evidence_matrix.md`，已从旧中文稿摘要、贡献、方法、实验、结论抽取核心 claim |
| W07 | 完成旧稿预投稿审计初版 | `docs/paper_audit/pre_submission_review.md`，已按 P0/P1/P2 分类列出投稿前问题 |
| W08 | 固定第一批 benchmark 选择思路 | `docs/experiment_design/benchmark_selection.md`，优先 ISCAS85 与 EPFL combinational，后续扩展 ISCAS89/ITC99 |
| W09 | 定义 ECO case schema 初版 | `docs/experiment_design/case_schema.md`，明确 original/resynthesized/cone/patch/metrics 字段 |
| W10 | 完成公式与图表审计初版 | `docs/paper_audit/formula_figure_audit.md`，已明确旧稿公式、图表和表格需要重做 |
| W11 | 固定 baseline 协议初版 | `docs/experiment_design/baseline_protocol.md`，已定义 fixed/random/size/critical-path/ABC baseline |
| W12 | 固定指标和表格模板初版 | `docs/experiment_design/metrics_and_tables.md`，已定义 main comparison、failure recovery、ablation、runtime 表 |
| W13 | 写出 FAECO 算法伪代码初版 | `docs/experiment_design/faeco_algorithm.md`，已形成 failure classification、weight refinement 和 ranking 流程 |
| W14 | 初始化 Git 仓库 | `.git`，当前分支为 `main`，尚未创建提交 |
| W15 | 建立 Python 最小工程骨架 | `pyproject.toml`、`src/rseco/metrics.py`、`src/rseco/failures.py`、`tests/test_metrics_and_failures.py` |
| W16 | 建立第一个最小 case | `benchmarks/raw/iscas85/c17.v`、`data/cases/minimal/iscas85_c17_case01/` |
| W17 | 完成第一组单元测试 | `python -m unittest discover -s tests`，5 个测试通过 |
| W18 | 实现最小 case loader、Verilog parser 和 flow | `src/rseco/case_loader.py`、`src/rseco/netlist.py`、`src/rseco/flow.py` |
| W19 | 生成 c17 草案 metrics | `data/cases/minimal/iscas85_c17_case01/results/metrics.json`，包含 gate count、logic level、patch size、failure types |
| W20 | 扩展单元测试 | `python -m unittest discover -s tests`，8 个测试通过 |
| W21 | 实现 fanin cone 自动抽取 | `src/rseco/graph.py`，可从 c17 自动生成 N22 cone |
| W22 | 实现最小结构等价接口 | `src/rseco/equivalence.py`，original/resynthesized c17 N22 cone 结构等价为 pass |
| W23 | 重新生成 c17 metrics | `results/metrics.json` 中 `equivalence_result` 已更新为 `pass` |
| W24 | 扩展单元测试 | `python -m unittest discover -s tests`，11 个测试通过 |
| W25 | 实现 fixed min-cut baseline 最小接口 | `src/rseco/cut.py`，c17 cone 可生成 fixed boundary |
| W26 | 实现 patch candidate 表示 | `src/rseco/patch.py`，候选 patch 和 selected patch 可写回 |
| W27 | 建立工具链策略文档 | `docs/engineering/toolchain_setup.md`，记录当前未检出 Yosys/ABC/OpenSTA/z3/networkx |
| W28 | 扩展单元测试 | `python -m unittest discover -s tests`，13 个测试通过 |
| W29 | 实现 failure-aware refinement 最小闭环 | `src/rseco/refinement.py`、`src/rseco/flow.py`，c17 的 F3/F4 可输出动作日志和下一轮权重 |
| W30 | 扩展单元测试 | `python -m unittest discover -s tests`，15 个测试通过 |
| W31 | 工具链检测脚本与环境快照 | `scripts/check_toolchain.ps1`、`experiments/environment/toolchain_2026-07-15.json`，外部 EDA 工具未检出，NetworkX 可用 |

## 2. 当前问题

| ID | 问题 | 影响 | 处理计划 |
|---|---|---|---|
| Q01 | 旧代码和旧数据不可用 | 不能复现学长旧实验，也不能直接沿用旧论文结果作为新论文主证据 | 不依赖旧实现，重建公开 benchmark flow |
| Q02 | 旧稿工业案例不可公开 | 中文投稿时可复现性不足 | 旧工业结果只作为背景或参考，论文主证据转向公开 benchmark |
| Q03 | 旧稿公式和符号抽取存在缺失 | 方法定义可能不够严谨，影响投稿审稿 | 已建立 `formula_figure_audit.md` 初版，下一步用 PDF 逐项校订 |
| Q04 | 第一阶段组合逻辑场景不够贴近真实 timing ECO | 容易被质疑工程真实性 | 论文中明确 Stage A/Stage B，第二阶段抽取 sequential reg-to-reg cone |
| Q05 | 当前 Git 仓库尚未创建首次提交 | 已经可以版本管理，但尚无基线快照 | 在确认提交策略后创建首次提交 |

## 3. 下周计划

| ID | 任务 | 优先级 | 完成标准 |
|---|---|---|---|
| N01 | 完成 claim-evidence matrix 校订版 | P0 | 每个旧稿核心 claim 都有证据强度、继承方式和新实验补证据方案 |
| N02 | 校订公式与图表审计 | P0 | 用 PDF 逐项核对缺失公式、图号、表号和实验数据来源 |
| N03 | 将 baseline 和指标协议转为实验配置 | P0 | 形成可被脚本读取的 config 草案 |
| N04 | 实现 patch replacement 草案 | P0 | 能把 selected patch 应用到目标 cone 的数据结构 |
| N05 | 将 refinement weights 接入 weighted cut 与 patch replacement | P0 | 细化动作可改变候选 boundary 或 patch 结果 |
| N06 | 准备组会 PPT 初稿 | P1 | 12-15 页 PPT，可按“旧问题-新方法-实验计划-风险”讲清楚 |

## 4. 风险变化

| 风险 ID | 变化 | 处理 |
|---|---|---|
| R01 | 旧代码和旧数据不可用风险仍为 active | 已将项目路线调整为基于公开 benchmark 重建，不再依赖旧代码 |
| R02 | 组合逻辑真实性风险仍为 active | 保留 sequential cone 扩展作为 Phase 5 的必要任务 |
| R03 | 中文论文创新性不足风险有所降低 | 主贡献聚焦 failure-aware cut refinement，而不是简单复现 RSECO |
| R04 | benchmark case 构造风险仍为 active | 已建立 benchmark selection、case schema、baseline protocol 和指标模板，下一步转为实验配置 |
| R09 | 无版本管理风险已缓解 | Git 已初始化，下一步需要首次提交形成基线快照 |

## 5. 需要确认的决策

1. 本周汇报是否采用“课题接手后的方向确认与执行规划汇报”定位。
2. FAECO 是否作为新方法名继续使用。
3. 第一阶段 combinational benchmark、第二阶段 sequential path cone 的路线是否可以作为论文实验主线。
4. 是否继续尝试联系学长获取旧代码和实验日志；即使拿到，也只作为参考，不作为新工作的唯一基础。
5. 中文投稿目标是否先按工程类论文准备，等第一轮实验结果出来后再确定具体期刊或会议。

## 6. 本周结论

本周完成了从“恢复旧 RSECO 项目”到“基于旧思路重构 FAECO 新工作”的方向转换。当前项目已经具备主线、目录、材料索引、任务管理、汇报框架、旧稿审计初版、benchmark 选择、case schema、baseline 协议、指标表模板、FAECO 伪代码、Git 仓库、Python 最小骨架、第一个 ISCAS85/c17 最小 case、case loader、简单 Verilog parser、fanin cone 自动抽取、结构等价检查和第一份可重复生成的草案 metrics。下一步应校订审计文档，并实现 fixed min-cut baseline、patch candidate 表示和首个可执行 demo。

