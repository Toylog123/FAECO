# FAECO 框架迁移记录（2026-09-12）

> 源：`D:\BaiduSyncdisk\03_FAECO` → 目标：`D:\BaiduSyncdisk\01_Papers\03_FAECO`
> 依据：`99_项目模板/project_docs/migration/FRAMEWORK_MIGRATION_GUIDE.md`
> 方式：robocopy 全量复制（316,765 文件 / 117.7 GB / 0 失败；目录 rename 因 BaiduSync 客户端句柄阻塞改用复制），git 历史与远程保留；源目录内容已于同日删除（仅剩空壳，OPEN_ISSUES OI-005）。

## 1. 目录映射表

| 迁移前（源项目） | 迁移后（框架） | 方式 | 说明 |
|---|---|---|---|
| `src/rseco/` | `code/src/rseco/` | git mv | 源码 |
| `scripts/*` | `code/scripts/*` | git mv | 实验与审计脚本；原 README 存为 `code/scripts/README_faeco_20260912.md` |
| `tests/*` | `code/tests/*` | git mv | 264 项测试；原 README 同上 |
| `pyproject.toml` | 根目录（路径改 `code/src`、`code/tests`） | 原地改 | `pip install -e .` / pytest 布局适配 |
| `docs/project_management/work_log.md` | `project_docs/LOGS.md` | git mv | 总工作日志（正序全量） |
| `docs/project_management/task_board.md` | `project_docs/agent_handoff/TASK_BOARD.md` | git mv | 任务看板 |
| `docs/project_management/{decision_log,future_task_backlog,roadmap,milestones,long_term_task_plan,risk_register}.md` | `project_docs/` 同名 | git mv | 决策/未决/规划 |
| `docs/project_management/{handoff_20260813,STAGE_B_AGENT_HANDOFF,stage_b_deferred_execution_checklist}.md` | `project_docs/agent_handoff/` | git mv | 历史交接 |
| `docs/project_management/initial_commit_scope_audit.md` | `project_docs/archive/` | git mv | 历史审计 |
| `docs/project_management/weekly_status_template.md` | `project_docs/reports/weekly/` | git mv | 周报模板 |
| `docs/paper_audit/` | `project_docs/review_history/paper_audit/` | git mv | 论文评审/审计（34 轮历史 + consistency_audit_20260911） |
| `docs/reports/` | `project_docs/reports/legacy/` | git mv | 历史周报/进展 |
| `docs/engineering/`、`docs/engineering_structure.md` | `project_docs/design_specs/` | git mv | 工程设计规范 |
| `docs/experiment_design/` | `experiments/design/` | git mv | 实验设计文档（就近实验） |
| `docs/mainline.md` | `project_docs/mainline.md` | git mv | 研究主线 |
| `docs/planning/` | `project_docs/planning/` | git mv | 项目规划 |
| `docs/{EFFECT_IMPROVEMENT_PLAN,ENGINEERING_HANDOFF}_20260805.md` | `project_docs/archive/` | git mv | 已完成的历史计划/交接 |
| `docs/{README,EXPERIENCE,GLOSSARY,environment}.md` | `docs/` 同名 | 重写 | 模板骨架 + FAECO 内容 |
| `docs/literature/`、`docs/materials/` | `docs/`（原地） | — | 技术性资料保留 |
| `docs/superpowers/`（未跟踪） | `project_docs/archive/superpowers/` | mv | 会话计划归档 |
| `.superpowers/backup/`（1 个跟踪文件 + 7 个未跟踪） | `project_docs/archive/superpowers_backup/` | mv + git add | work_log 引用的分析脚本/报告全部纳入跟踪 |
| `benchmarks/` | `data/raw/benchmarks/` | mv + git add | raw 数据不跟踪（.gitignore 更新），README + iscas89/itc99 manifests 跟踪，其余 3 个 manifest 维持原排除策略 |
| `data/` | `data/`（原地） | — | cases 跟踪不变 |
| `experiments/` | `experiments/`（原地） | — | 新增 `design/` 子目录 |
| `paper/` | `paper/`（原地）+ 模板补充 `paper/GLOSSARY.md`、`zh/review_rounds/`、`zh/scripts/`、`zh/fonts/` | — | |
| 根目录 `tmp_*.log`、`tmp_paper_extract.txt`、`abc.history`、`.tmp_alg.txt` | `scratch/tmp_logs/` | mv | git-ignored |
| 根目录 `.tmp/`、`.tmp_evt/`、`tmp/`、`_faeco_review_tmp/`、`_tmp_joint_test/`、`tmp_hold_probe/`、`tmp_multipath_verify/`、`tmp_spef_probe/`、`docs/project_management/_verify_tmp.txt` | `scratch/` | mv | git-ignored |
| `.venv/`、`.git/`、`.pytest_cache/` | 原地随复制 | — | `.venv` 可编辑安装需重装（环境文档已注明） |
| 模板骨架 | 顶层 AGENTS/CONTRIBUTING/SECURITY/CHANGELOG/Makefile/.github、`project_docs/{agent_handoff,baselines,evidence,migration,reports,review_history,worktrees,ARCHIVE_POLICY,FILE_ORGANIZATION,RECORDS,versioning}`、`code/{scripts 检查脚本,DESIGN.md,README}`、`data/{manifests,schemas}`、`project/`、`skills/`、`versions/`、`scratch/` | 复制 | 模板示例内容（module_a、experiments/v1、example_paper 等）已删除 |
| 根 `README.md` | 重写（旧版存 `project_docs/archive/README_pre_framework_20260912.md`） | 重写 | 框架结构 + FAECO 填充 |
| `.codex-handoff.json` | 重写 | 重写 | 新布局 read_order |

## 2. 路径修复清单

| 文件 | 修复 |
|---|---|
| `pyproject.toml` | `where=["code/src"]`、`pythonpath=["code/src"]`、`testpaths=["code/tests"]` |
| `code/scripts/run_b19_eval.py`、`gen_b19_repaired.py` | `ROOT`/`sys.path` 改 `__file__` 锚定（parents[2]） |
| `paper/zh/figures/gen_figures.py` | `OUT`、3 处实验目录改 `__file__`/`PROJECT_ROOT` 锚定 |
| `paper/zh/figures/{gen_figures_alt,gen_figures_nature,convert_tables,insert_spef}.py` | 绝对路径改锚定；两个工具脚本同时改指当前主稿文件名 |
| `paper/zh/manuscript/{_extract_pages,_render_exp}.py` | 反斜杠绝对路径改锚定 + 指向当前主稿 PDF |
| `code/scripts/{make_liberty_cells_v,run_b19_eval,resynthesize_minimal_cases,run_parasitic_aware_check,verify_b17_final_sec}.py` | `benchmarks/raw/...` → `data/raw/benchmarks/raw/...`（含文档字符串） |
| `experiments/{run_joint_scan,run_joint_scan_nostop,run_spef_extend}.py` | 绝对 `ROOT` 改 `__file__` 锚定；内部 `ROOT/'scripts'` → `ROOT/'code/scripts'` |
| `code/tests/*.py`（19+12 个文件） | 测试锚点 `parents[1]` → `parents[2]`（code/tests 深一层）；`ROOT/"scripts"` → `ROOT/"code/scripts"` |
| `project_docs/design_specs/engineering/toolchain_setup.md` | 历史验证命令中的旧绝对路径改为占位说明 |
| `.gitignore` | 合并模板（scratch/project/data/raw/安全条目）；去掉模板的全局 `*.pdf`（FAECO 图源 PDF 需跟踪）；benchmarks 排除路径迁移 |
| `README.md`、`.codex-handoff.json`、`docs/*`、`project_docs/{WORK_PROGRESS,OPEN_ISSUES,agent_handoff/*}` | 重写/新建（内容见各文件） |

## 3. 不改写项（证据保护）

- `experiments/**` 历史产物 JSON/CSV 中记录的旧绝对路径（如 `experiments/20260814_iscas89_sec/summary.json`）：属证据记录，保留原样。
- `paper/zh/archives/`、`paper/zh/manuscript/backups/`（git-ignored 归档）：原样随迁。
- `LOGS.md` 历史条目中出现的旧路径：历史事实，不回溯改写；新旧路径对照以本文件为准。

## 4. 验证

- git：`git log` 完整（d329f19 可达）；`git status` 干净（仅预期 renames/adds）。
- 测试：`python -m pytest code/tests -q`（迁移后首跑，264 项）。
- 框架体检：`bash code/scripts/check_project.sh`。
- 残扫：live 代码/文档中旧绝对路径（03_FAECO）为 0。
