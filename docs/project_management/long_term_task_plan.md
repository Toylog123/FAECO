# FAECO 长期任务规划表

更新时间：2026-07-20

状态说明：

- `done`：已完成
- `in_progress`：进行中
- `pending`：未开始
- `blocked`：被阻塞

| ID | 阶段 | 任务 | 状态 | 优先级 | 交付物 | 完成标准 |
|---|---|---|---|---|---|---|
| PM00 | Phase 0 | 固定项目主线 | done | P0 | `docs/mainline.md` | FAECO 定位明确 |
| PM01 | Phase 0 | 整理工程目录 | done | P0 | `docs/engineering_structure.md` | 工程/论文/实验目录分离 |
| PM02 | Phase 0 | 归纳原始材料 | done | P0 | `docs/materials/` | 论文、课题构想、文献都有索引 |
| PM03 | Phase 0 | 建立证据化文献矩阵 | in_progress | P1 | `literature_matrix.md`、`core_paper_notes.md`、`source_manifests/` | 已核验 25 篇 A 级全文和 1 条 B 级官方证据；DAC 2018 多源 OA 复核仍为 B，待写作结构获批后按 25A/1B 形成 Related Work 初稿 |
| PM04 | Phase 1 | 抽取旧稿核心 claim | done | P0 | `claim_evidence_matrix.md` | 摘要、贡献、结论 claim 完整 |
| PM05 | Phase 1 | 建立 claim-evidence matrix | done | P0 | `claim_evidence_matrix.md`、`legacy_source_locator.md` | C01-C12 已有 PDF 页级来源、证据强度、继承策略和补证据动作 |
| PM06 | Phase 1 | 旧稿预投稿审计 | done | P0 | `pre_submission_review.md` | P0/P1/P2 问题清单 |
| PM07 | Phase 1 | 公式和图表完整性检查 | done | P0 | `formula_figure_audit.md`、`legacy_source_locator.md`、`legacy_table2_recalculation.md` | 已核对 PDF 标号(1)-(14)/(16)-(20)、图1-9、表1-5，并查明公式缓存编号、交叉引用和表2统计冲突 |
| PM08 | Phase 2 | 选定第一批 benchmark | done | P0 | `benchmark_selection.md`、`benchmark_source_and_license_audit.md` | 已固定 EPFL `v2025.1` 主来源、8 个 Verilog/官方 BLIF 参照和当前 ISCAS85 使用边界 |
| PM09 | Phase 2 | 定义 ECO case schema | done | P0 | `case_schema.md` | 输入输出字段完整 |
| PM10 | Phase 2 | 定义 baseline protocol | done | P0 | `baseline_protocol.md` | fixed/random/size/critical path/ABC baseline 与运行边界明确 |
| PM11 | Phase 2 | 定义指标和结果表模板 | done | P0 | `metrics_and_tables.md` | 指标公式和表格模板明确 |
| PM12 | Phase 3 | 初始化 Git 仓库 | done | P0 | `.git` | 后续代码和文档可版本管理 |
| PM13 | Phase 3 | 搭建 Python 项目骨架 | done | P0 | `pyproject.toml`、`src/`、`tests/` | 能运行测试 |
| PM14 | Phase 3 | 实现 netlist / graph 最小表示 | done | P0 | `src/rseco/netlist` | 小型电路可表示 |
| PM15 | Phase 3 | 实现 cone extraction | in_progress | P0 | `src/rseco/graph` | 能抽取 fanin/fanout cone |
| PM16 | Phase 3 | 实现 equivalence checking | done | P0 | `src/rseco/equivalence`、`src/rseco/yosys_abc.py` | structural signature 和 Yosys-normalized full-netlist ABC CEC 均可运行；当前 5-case local smoke formal 为 5/5 pass |
| PM17 | Phase 3 | 实现 fixed min-cut baseline | done | P0 | `src/rseco/cut` | baseline 可运行 |
| PM18 | Phase 3 | 实现 failure-aware refinement | done | P0 | `src/rseco/refinement.py` | F1-F5 反馈可执行，并写入 c17 metrics |
| PM19 | Phase 3 | 实现 patch ranking | done | P1 | `src/rseco/ranking.py`、`tests/test_ranking.py` | 确定性 score 可计算，并写入 c17 selected patch |
| PM20 | Phase 4 | 跑通 combinational demo | done | P0 | `experiments/20260717_minimal_combinational_demo/` | c17 最小 case 可由脚本端到端生成实验目录 |
| PM21 | Phase 4 | 批量 combinational 实验 | in_progress | P0 | result tables | 当前 5-case ISCAS batch 仅作本地 smoke；Yosys/ABC formal/baseline 已接入并产出 5/5 pass/success；X21 已完成 EPFL wave 1 Yosys JSON 导入报告，仍需 JSON case loader/flow、EPFL formal/batch 主表和 Stage B WNS/TNS |
| PM22 | Phase 4 | 多轮 recovery 与消融实验 | in_progress | P0 | recovery/ablation tables | 真正多轮 refinement 可记录 residual failures、停止原因和首次恢复轮次，并生成 without F1/F3/F4 表 |
| PM23 | Phase 5 | sequential cone extraction 设计 | pending | P1 | design doc | reg-to-reg cone 边界明确 |
| PM24 | Phase 5 | sequential 实验 | pending | P1 | experiment results | 路径级 ECO 有结果 |
| PM25 | Phase 6 | 写 Introduction | pending | P1 | paper draft | 背景-缺口-方法-证据完整 |
| PM26 | Phase 6 | 写 Related Work | pending | P1 | paper draft | 文献矩阵转成论文段落 |
| PM27 | Phase 6 | 写 Method | pending | P1 | `method_rewrite_readiness.md`、paper draft | 已完成就绪审计；待 X18/X19/X21/X22 关闭阻塞项后，使符号、伪代码、流程和实现字段一致 |
| PM28 | Phase 6 | 写 Experiments | pending | P1 | paper draft | 表格和结论一致 |
| PM29 | Phase 7 | 模拟审稿 | pending | P1 | review report | P0/P1 问题明确 |
| PM30 | Phase 7 | 修改论文 | pending | P1 | revised draft | 主要问题关闭 |
| PM31 | Phase 8 | 确定投稿目标 | pending | P1 | venue note | 格式和范围明确 |
| PM32 | Phase 8 | 准备投稿包 | pending | P1 | submission package | 可提交 |

## 当前最近 3 个任务

1. PM21/X21：把已生成的 EPFL ctrl/int2float/router Yosys JSON 接入 case loader/flow，生成正式 ECO cases，并补官方 BLIF 回验和正式 batch 表。
2. PM21/X22：基于已安装的 WSL2 OpenSTA 设计 Stage B 路径桥、report parser、WNS/TNS、critical path 和 runtime 写回。
3. PM22：确定 Stage A recovery 成功口径后，实现真正多轮 refinement loop 和 without F1/F3/F4 消融。


