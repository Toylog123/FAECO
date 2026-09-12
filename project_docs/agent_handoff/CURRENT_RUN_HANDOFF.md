# Current Run Handoff — 2026-09-12 框架迁移

## 1. 项目概览

FAECO：面向预布局门级时序 ECO 的失效驱动候选搜索（中文论文 + Python 工程 + 公开 benchmark 实验）。
工作区：`D:\BaiduSyncdisk\01_Papers\03_FAECO`；分支 main（与 origin 同步）；活跃基线 = 迁移前最后提交 d329f19。

## 2. 本轮做了什么

1. 复制仓库至新家（robocopy 316,765 文件 / 117.7 GB / 0 失败；`git log`/`git status` 校验一致）。
2. 按模板重组织目录（完整映射表见 `../migration/MIGRATION_20260912.md`）：src+scripts+tests → `code/`；过程文档 → `project_docs/`；benchmarks → `data/raw/benchmarks/`；tmp → `scratch/`；顶层契约（AGENTS/CONTRIBUTING/SECURITY/CHANGELOG/Makefile/.github）。
3. 路径修复：pyproject（code/src 布局）、9 个硬编码绝对路径脚本 `__file__` 锚定、5 处 benchmarks 引用、README 重写、`.codex-handoff.json` 更新。

## 3. 证据门（验收标准）

- [x] git 历史完整（d329f19 可达，远程同步）
- [ ] `python -m pytest code/tests -q` 264 项全绿（迁移后首跑）
- [ ] `bash code/scripts/check_project.sh` 无 FAIL
- [ ] 旧绝对路径（03_FAECO）live 文件残扫为 0

## 4. 下一步（给下一次接手者）

1. 读 `START_HERE.md` → `status_logs/CURRENT_STATUS.md` → `../OPEN_ISSUES.md`。
2. 若 pytest 因 `.venv` 失效报 import 错误：`pip install -e .` 后重跑。
3. 未决事项以 `../OPEN_ISSUES.md` 为准（DOI、DRC、versions 冻结、机制图拆分、旧目录处置）。

## 5. 不要做

- 不要删除 `D:\BaiduSyncdisk\03_FAECO`（迁移源归档，用户处置）。
- 不要改写 `experiments/` 历史产物内记录的旧绝对路径（证据）。
- 不要在本轮继续改论文（审计已闭环）；新意见走第 19 轮流程，且改动前先数字对账。
