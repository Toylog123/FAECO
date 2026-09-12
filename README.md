# FAECO：面向预布局门级时序 ECO 的失效驱动候选搜索

本工程实现并验证 **FAECO（Failure-Aware ECO）**——一种面向预布局门级时序 ECO 的失效驱动候选搜索引擎：在已映射网表的违例扇入锥上构造多特征加权割与关键路径覆盖割生成候选，利用 F1–F6 失效反馈更新搜索，并以"库函数/结构筛选 → OpenSTA 理想线网测量 → 简化 SPEF 物理门控 → 独立顺序 SEC"分层验证，覆盖设计、实验、论文全流程。

- 项目类型：算法研究（EDA / 时序优化）
- 主要技术栈：Python 3.11 + Yosys/OSS-CAD 0.67 + OpenSTA 3.1.0 + OpenROAD 2.0 + SKY130 HD PDK + XeLaTeX
- 当前阶段：论文修订（中文稿 9 页，第 18 轮审稿修订 + 全文一致性审计完成）

## 整体设计

FAECO 三阶段流水线（映射准备 → 加权割与候选生成 → 验证与接受）：

1. **映射准备**：Yosys 两步流程生成 SKY130 HD 映射网表；Liberty 提供单元逻辑与时序信息。
2. **加权割与候选生成**：违例扇入锥上构造 s-t 分裂图，Liberty 函数匹配生成 R 候选；加权最小割 $C_w$ 与关键路径覆盖割 $C_c$ 互补实例化 R/G/B/JOINT 候选，按割代价、路径覆盖、策略优先级排序。
3. **验证与接受**：OpenSTA 理想线网测量 ΔWNS（接受谓词，TNS-aware 平局分支可选）；10 ps 物理门控下进入简化 SPEF 复测；F1–F6 失效反馈更新割权重；最终独立顺序 SEC（Yosys equiv_simple/equiv_induct）验证功能等价。

关键决策与设计细节：

- `code/src/DESIGN.md` — 源码层设计（模块划分与演进）
- `project_docs/design_specs/engineering/` — 工程设计文档（n31_05 顺序 ECO、工具链、Z3 形式化等）
- `docs/environment.md` — 工具链版本与复现环境
- 历史版 README（RSECO 叙事时期）：`project_docs/archive/README_pre_framework_20260912.md`

## 最新进展

**当前权威状态入口：**

1. 工作进度（倒序记录）：`project_docs/WORK_PROGRESS.md`
2. 总工作日志（正序，可回溯）：`project_docs/LOGS.md`（原 docs/project_management/work_log.md，2026-07 至今全量）
3. 当前状态（最新一轮）：`project_docs/agent_handoff/status_logs/CURRENT_STATUS.md`
4. 任务看板（每步任务与证据门）：`project_docs/agent_handoff/TASK_BOARD.md`
5. 未决问题（未解决持续保留，必须告知）：`project_docs/OPEN_ISSUES.md`
6. 论文一致性审计：`project_docs/review_history/paper_audit/`（含 consistency_audit_20260911.md）

最近一轮（2026-09-12）：工程按 `99_项目模板` 框架完成架构迁移（代码入 `code/`、过程文档入 `project_docs/`、原始基准入 `data/raw/`、临时件入 `scratch/`），映射全记录见 `project_docs/migration/MIGRATION_20260912.md`；迁移前最新工作为第 18 轮审稿修订（3d984c6）与全文一致性审计（d329f19，修复 8 处正文与实验产物的矛盾）。

## 快速开始

1. 环境：读 `docs/environment.md`；Python 依赖见根目录 `pyproject.toml`（`pip install -e .`），WSL2 内 Yosys/OpenSTA 按 environment.md 安装。
2. 测试：`python -m pytest code/tests -q`（264 项）。
3. 实验：`experiments/INVENTORY.md` 为全部实验目录总索引，`experiments/RESULTS.md` 为顶层结果汇总；复现入口脚本在 `code/scripts/`。
4. 论文：中文主稿 `paper/zh/manuscript/FAECO_面向预布局门级时序ECO的失效驱动候选搜索.tex`，latexmk -xelatex 编译；图脚本 `paper/zh/figures/gen_figures.py`。
5. 交接：读 `project_docs/agent_handoff/START_HERE.md` 与 `CURRENT_RUN_HANDOFF.md`。

## 目录角色

### 仓库契约（顶层）

| 文件 / 目录 | 角色 |
|------|------|
| `README.md` | 本文档：总览 / 设计 / 进展 / 快速开始 / 目录角色 / 工作规则 |
| `AGENTS.md` | 智能体行为契约：质疑 / 质量 / 自我批判 / 记录 / 并行 |
| `CONTRIBUTING.md` | 协作规范：分支 / 提交 / PR / 多智能体分工 |
| `SECURITY.md` | 安全与密钥管理（什么不进仓库） |
| `CHANGELOG.md` | 变更日志（按版本记录重要变更） |
| `.codex-handoff.json` | 交接元数据（read_order 阅读顺序） |
| `.github/` | PR 模板 + CI 自动检查 |
| `Makefile` | 统一命令入口（make check / test / manifest） |

### 当前版本（主目录 = 最新最好的版本）

| 目录 | 角色 |
|------|------|
| `code/` | 代码资产：`src/rseco/` 源码 + `scripts/` 实验与审计脚本 + `tests/` 264 项测试 |
| `project/` | 构建工程 / 运行脚本（生成工程 git-ignored，当前为空） |
| `experiments/` | 实验定义、设计与输出证据（`INVENTORY.md` 总索引 / `RESULTS.md` 汇总 / `design/` 实验设计文档） |
| `docs/` | 技术文档：环境（`environment.md`）、术语（`GLOSSARY.md`）、经验库（`EXPERIENCE.md`）、文献（`literature/`）、原始材料（`materials/`） |

### 项目级共享

| 目录 | 角色 |
|------|------|
| `data/` | 数据治理：`cases/` 构造用例（跟踪）+ `raw/benchmarks/` 原始基准（raw 不跟踪，manifests 登记 SHA） |
| `paper/` | 论文：`zh/` 中文主版（manuscript/figures/review_rounds）；`GLOSSARY.md` 术语表 |
| `project_docs/` | 过程文档：交接（agent_handoff）/ 基线（baselines）/ 评审（review_history）/ 进度（WORK_PROGRESS）/ 日志（LOGS.md）/ 未决（OPEN_ISSUES）/ 报告（reports）/ 设计规范（design_specs）/ 决策（decision_log）/ 规划（roadmap、milestones、planning）/ 迁移（migration）/ 归档（archive） |

### 版本与辅助

| 目录 | 角色 |
|------|------|
| `versions/` | 冻结版本集合（当前为空，冻结策略见 `project_docs/versioning.md` 与 OPEN_ISSUES） |
| `skills/` | 项目级技能（ARS 学术技能 + academic-paper 写作技能） |
| `scratch/` | 临时脚本 / 探针 / 运行日志（git-ignored） |

## 工作规则

1. **版本定义**：每个版本 = 论文 + 源码 + 测试 + 证据的四元绑定，冻结为 `versions/<基线ID>/` 完整快照；工作树名、运行目录名不定义版本，详见 `project_docs/versioning.md`。
2. **工作树**：一次性执行环境，物理位置在同步仓库之外，注册于 `project_docs/worktrees/WORKTREE_REGISTRY.csv`。
3. **结论口径**：每条结论区分「软件本地复现 / 策略复现 / 硬件复现 / 实测数据」，避免过度声称；论文数字必须与 `experiments/` 产物对账（先更新聚合 summary，再动论文）。
4. **证据自包含**：每个证据包含 README + 摘要 + 输入/来源 + 原始输出 + SHA-256 清单，见 `project_docs/evidence/README.md`；实验证据文件严禁删除。
5. **产物隔离**：生成产物放 git-ignored 的 `project/`、`scratch/`，绝不放在源码或主稿件旁。
6. **中英双版本**：论文以 `zh/` 为主版本；只有进入英文期刊流程时才维护 `en/`，两版结论必须一致。
7. **交接即承诺**：本轮结束前更新 `WORK_PROGRESS.md`、`CURRENT_STATUS.md`、`TASK_BOARD.md` 与 `CURRENT_RUN_HANDOFF.md`，按下一次接手者角度写明「下一步做什么、证据门是什么、不要做什么」。
8. **质疑优先**：任何结论、方案与数字在采信前先质疑与验证；证据高于权威，不因来源（用户、上级、主流、既有代码）而盲目认可与服从。
9. **质量标准**：设计先评审后实施；实施不轻易降级，论文以提升代替降低说法；需要时敢于大改，力争力所能及做到最好。
10. **Git 纪律**：阶段性工作完成即 `git commit` + `git push`，里程碑打 tag；工程代码推进前先固化当前状态（备份）；可为新版本复制目录（含脚本），但复制后自包含、不引用旧版本文件。
11. **文档同步**：任何目录 / 结构 / 路径变更后，必须同步更新主目录文档（`README.md` 目录角色与工作规则、`AGENTS.md`、`.codex-handoff.json`），文档与真实结构保持一致。
12. **经验沉淀**：解决问题后当天登记到 `docs/EXPERIENCE.md`（现象 / 原因 / 解决 / 验证），避免反复踩坑。
13. **并行协作**：可分解的独立子任务默认多智能体并发，不串行；识别依赖（独立并行、有依赖串行）；并行结果汇合后统一过审查门，关键路径留在主线。
14. **破坏性操作防护**：删除 / 覆盖 / 重构前确保可回退——先 `git status` 确认已提交，未跟踪文件先备份；删除用 `git rm`，不裸 `rm`。
