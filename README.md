# FAECO：面向预布局门级时序 ECO 的候选探索与失效刻画

本工程实现并验证 **FAECO**（方法名）——面向预布局门级时序 ECO 的**候选探索与失效刻画**框架：在已映射网表的违例路径局部逻辑上，按多种结构特征构造并统一排序修改候选以扩展有效候选空间；将候选失效归纳为若干类型，用于诊断搜索过程并引导后续控制；候选按轮提交，并依次通过时序分析与等价性检查验证，覆盖设计、实验、论文全流程。

- 项目类型：算法研究（EDA / 时序优化）
- 主要技术栈：Python 3.11 + Yosys/OSS-CAD 0.67 + OpenSTA 3.1.0 + OpenROAD 2.0 + SKY130 HD PDK + LuaLaTeX（ctexart 双栏）
- 当前阶段：**r22 已于2026-10-16按用户“继续”恢复**；先修正确性门，再整体回归/独立复核和新版本真实实验。中文工作稿12页、7图14表；英文 `elsarticle` 初稿27页、7图14表。两版科学结论仍待历史正确性补验，不能作为投稿定稿；v18保留为历史冻结基线。目标期刊为 **Integration, the VLSI Journal**。

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

本轮（2026-10-16，r22恢复）：多输出、模块作用域、提交前刷新、三态导出和必需输入检查已修复。A六个实际接受终点、B两组Pico和B17均已获得绑定实际对象的新独立SEC证明。后续反例又发现时序单元仅比较IQ、单行实例漏读和公共唯一性门误拦位置参数三个缺口，现已分别修复；原始反例V3拒绝非法复位→置位替换，保留合法尺寸调整。最新完整回归v8为**969 passed/4 skipped/156 subtests，155.12s，170文件SHA前后一致**，全进程采用`PYTHONUTF8=1`。真实Z/0反例已推翻当前Yosys二态SEC的四态能力，三态对象继续返回unsupported，四态后端问题仍保留。实际证据见`project_docs/evidence/r22_correctness_20261016/`；C′须另建新pin/v3输入和pilot，D56同族恢复独立于C′，历史C/B3另行重建。当前论文不是投稿定稿。

历史记录：最近一轮（2026-10-13，r15 全篇去防御化编辑）：论文**内容冻结 v13**（tag `v2026-10-13-defensive-purge2-r15`，**10 页** 0/0/0/0，内容指纹 `55bde9d4…`）——**用户直接指定的第二轮语言风格轮**（非外部审稿）：用户在 r14 后按**正式期刊审稿人（Integration / TODAES / TVLSI 方向）视角**通读，裁定「**这一版技术内容已经比较成熟，但文字风格仍有明显'答辩稿/项目报告'痕迹。最大的问题不是 claim 过强，而是作者过于主动解释审稿人可能的问题，导致主线贡献被稀释**」，要求从「证明我没有问题」转向「清楚告诉读者我做了什么、发现什么」，**减少解释性文字、提高陈述力度**（不是增加内容）。落地**正文 11 处语言风格改写**（E1–E11，`.tex` diffstat 11/11）；**三处必要偏离**（§2.3 保表 2 引用 / §4.1 保留全文唯一一处「不等同于」/ §5 结论「参考」口径）；**摘要结构与篇幅未变**；**零数字/零实验/零代码/零参考文献**。前序轮：r14（v12，去防御化重构 10 处）、r13（v11，摘要 + §1.1 大同行入口改写）、r12（v10，第五份外部审稿 M1–M5）、r11（v9，投稿前精修 Step 1）、r10（v8，零算力增强 + 改投 Integration）、r8/r9（v7）、r7 文字专项审稿（v6）。逐条见 `paper/zh/CHANGE_LOG.md` 与 `versions/v13/README.md`。

更早（2026-09-12）：工程按 `99_项目模板` 框架完成架构迁移（代码入 `code/`、过程文档入 `project_docs/`、原始基准入 `data/raw/`、临时件入 `scratch/`），映射全记录见 `project_docs/migration/MIGRATION_20260912.md`。

## 快速开始

1. 环境：读 `docs/environment.md`；Python 依赖见根目录 `pyproject.toml`（`pip install -e .`），WSL2 内 Yosys/OpenSTA 按 environment.md 安装。
2. 测试：`bash code/scripts/run_with_timeout.sh 300 .venv/Scripts/python.exe -m pytest code/tests -q`；结果和被测版本见当前交接记录。
3. 实验：`experiments/INVENTORY.md` 为全部实验目录总索引，`experiments/RESULTS.md` 为顶层结果汇总；复现入口脚本在 `code/scripts/`。
4. 论文：中文主稿 `paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex`，**须 `cd` 入 `manuscript/` 目录后用 `lualatex` 连跑两遍**；当前图脚本 `paper/zh/figures/data/scripts/review_r21_figures.py`。
5. 交接：读 `project_docs/agent_handoff/START_HERE.md` 与 `CURRENT_RUN_HANDOFF.md`。

r22已恢复；先读 `project_docs/agent_handoff/CURRENT_RUN_HANDOFF.md`。完整回归v8与精确反例V3已通过；提交源码后用新pin和新v3目录登记实验，v2只登记未执行且禁止执行。9臂共享每电路同一映射SHA，workers=1、STA预算500、最多2电路并发；映射后的实际输入先查模型支持域，两电路18项pilot全部通过独立最终SEC才扩展。不要重用或覆盖失败v1或仅登记v2的证据。

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
| `code/` | 代码资产：`src/rseco/` 源码（含显式候选政策与STA账本）+ `scripts/` 实验/审计入口 + `tests/` 回归 |
| `project/` | 构建工程 / 运行脚本（生成工程 git-ignored，当前为空） |
| `experiments/` | 实验定义、设计与输出证据（`INVENTORY.md` 总索引 / `RESULTS.md` 汇总 / `design/` 实验设计文档） |
| `docs/` | 技术文档：环境（`environment.md`）、术语（`GLOSSARY.md`）、经验库（`EXPERIENCE.md`）、文献（`literature/`）、原始材料（`materials/`） |

### 项目级共享

| 目录 | 角色 |
|------|------|
| `data/` | 数据治理：`cases/` 构造用例（跟踪）+ `raw/benchmarks/` 原始基准（raw 不跟踪，manifests 登记 SHA） |
| `paper/` | 论文：`zh/` 中文主版；`en/` 英文工作初稿（manuscript/figures/references/scripts/submission；build/FAECO.pdf为已保存预览）；两版结论待补验；`GLOSSARY.md` 术语表 |
| `project_docs/` | 过程文档：交接（agent_handoff）/ 基线（baselines）/ 评审（review_history）/ 进度（WORK_PROGRESS）/ 日志（LOGS.md）/ 未决（OPEN_ISSUES）/ 报告（reports）/ 设计规范（design_specs）/ 决策（decision_log）/ 规划（roadmap、milestones、planning）/ 迁移（migration）/ 归档（archive） |

### 版本与辅助

| 目录 | 角色 |
|------|------|
| `versions/` | 历史冻结版本集合（v18为最近冻结基线，r21/r22是未冻结工作修订；冻结不代表已通过r22科学审计；见 `project_docs/versioning.md` 与 `project_docs/OPEN_ISSUES.md`） |
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
