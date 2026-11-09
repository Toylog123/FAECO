# FAECO：面向预布局门级时序 ECO 的候选探索与失效刻画

> **接手者第一站（2026-11-09 起）：`project_docs/HANDOFF_2026-11-09.md`**（三十秒现状 + 复现入口 + 自检命令）。本文档只做总览与目录索引；任何进度、口径、结论以 HANDOFF / CANON 为准，本文档不与它们冲突。

## 当前状态（2026-11-09 复核）

- **论文**：中文主稿 **11 页 / 7 图 / 5 表 / 17 参考文献**，补充 **15 页 / 22 表 / 5 图**；两份质量门均 GATE PASS（Errors/Overfull/Underfull 全 0，Undefined 5 = 字体替身警告）。英文 `paper/en/manuscript/FAECO.tex` 仍 26 页且**未同口径**（摘要仍写 1.07 / 0.16 ns，中文现行 1.29 / 1.68 ns）。
- **git**：`main` 领先 `origin/main` **30 条未推送提交**，工作区 clean，HEAD = `faa533a`。`git describe --tags` = `faeco-paper-final-20261028-26-gfaa533a`。
- **基线**：`versions/v19/MANIFEST.sha256`（148 条）= **139 OK / 9 FAILED**，9 条漂移 = r95/r95b 文本改动 + r108/r113 代码改动的预期结果；**v20 待建**（收录 r95–r116）。
- **测试**：`PATH` 前置 OSS-CAD `bin`+`lib` 后，`.venv/Scripts/python.exe -m pytest code/tests -q` → **1056 passed + 156 subtests**（唯一红 = `test_fix_crcrlf.py` 的 `\r\r\n` 扫描，已随编码缺陷一并修复）。
- **环境**：WSL2 Ubuntu（默认 v2）可用：OpenROAD 2.0、OpenSTA 3.1.0、`/usr/bin/yosys` 0.33（shim 0.70+255）。Windows 侧 OSS-CAD 的 `yosys` 需 `bin` 与 `lib` **同时**入 PATH，否则 `yosys -V` 报 `0xC0000139`（DLL 导出缺失）的假红。

## 项目简介

本工程实现并验证 **FAECO**（方法名）——面向预布局门级时序 ECO 的**候选探索与失效刻画**框架：在已映射网表的违例路径局部逻辑上，按多种结构特征构造并统一排序修改候选以扩展有效候选空间；将候选失效归纳为若干类型，用于诊断搜索过程并引导后续控制；候选按轮提交，并依次通过时序分析与等价性检查验证，覆盖设计、实验、论文全流程。

- 项目类型：算法研究（EDA / 时序优化）
- 技术栈：Python 3.11 + Yosys/OSS-CAD 0.67 + OpenSTA 3.1.0 + OpenROAD 2.0 + SKY130 HD PDK + LuaLaTeX（ctexart 双栏）

## 整体设计

FAECO 三阶段流水线（映射准备 → 加权割与候选生成 → 验证与接受）：

1. **映射准备**：Yosys 两步流程生成 SKY130 HD 映射网表；Liberty 提供单元逻辑与时序信息。
2. **加权割与候选生成**：违例扇入锥上构造 s-t 分裂图，Liberty 函数匹配生成 R 候选；加权最小割 $C_w$ 与关键路径覆盖割 $C_c$ 互补实例化 R/G/B/JOINT 候选，按割代价、路径覆盖、策略优先级排序。
3. **验证与接受**：OpenSTA 理想线网测量 ΔWNS（接受谓词，TNS-aware 平局分支可选）；10 ps 物理门控下进入简化 SPEF 复测；F1–F6 失效反馈更新割权重；最终独立顺序 SEC（Yosys equiv_simple/equiv_induct）验证功能等价。

关键设计文档：`code/src/DESIGN.md`（源码层设计）、`project_docs/design_specs/engineering/`（工程设计）、`docs/environment.md`（工具链与复现环境）。

## 现行权威状态入口

1. **三十秒现状 + 复现入口 + 自检 + 后续规划**：`project_docs/HANDOFF_2026-11-09.md`（接手者第一站）
2. **唯一现行口径**：`project_docs/CANON.md`（任何文档与它冲突，以它为准）
3. **目录 / 版本 / 数据资产 / 结构性坑**：`project_docs/PROJECT_MAP.md`
4. **事实流水**：`project_docs/LOGS.md`（正序，可回溯）
5. **未决问题（未解决持续保留，必须告知）**：`project_docs/OPEN_ISSUES.md`
6. **证据索引**：`project_docs/evidence/PAPER_EVIDENCE_MANIFEST.md`

> `project_docs/WORK_PROGRESS.md` 停在 r93（2026-10-28）、`project_docs/agent_handoff/` 停在 r30（2026-10-24）——**自 2026-11-04 起停用，只作溯源，不再更新**，逐轮记录只落 `LOGS.md` + `CANON.md`（口径有变时）。

## 快速开始

1. **环境**：读 `docs/environment.md`；Python 依赖见根 `pyproject.toml`（`pip install -e .`）；WSL2 内 Yosys/OpenSTA 按 environment.md 安装。Windows 侧跑 yosys 需 OSS-CAD `bin` + `lib` 同时入 PATH。
2. **测试**：`bash code/scripts/run_with_timeout.sh 300 .venv/Scripts/python.exe -m pytest code/tests -q`（须用 `.venv/Scripts/python.exe` 显式 Python，不能只写 `python`）。
3. **实验**：`experiments/INVENTORY.md` 总索引、`experiments/RESULTS.md` 顶层汇总；复现入口脚本在 `code/scripts/`。
4. **论文**：中文主稿 `paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex`、补充 `paper/zh/manuscript/FAECO_补充材料.tex`；**必须 `cd` 入 `manuscript/` 后显式选目标、LuaLaTeX 连跑两遍**（不能自动猜主文件）。当前 PDF 在 `paper/zh/build/`。
5. **交接**：读 `project_docs/HANDOFF_2026-11-09.md`。

## 目录角色

### 仓库契约（顶层）

| 文件 / 目录 | 角色 |
|------|------|
| `README.md` | 本文档：总览 / 现状 / 设计 / 入口 / 快速开始 / 目录角色 / 工作规则 |
| `AGENTS.md` | 智能体行为契约：质疑 / 质量 / 自我批判 / 记录 / 并行 |
| `CONTRIBUTING.md` | 协作规范：分支 / 提交 / PR / 多智能体分工 |
| `SECURITY.md` | 安全与密钥管理（什么不进仓库） |
| `CHANGELOG.md` | 变更日志（按版本记录重要变更） |
| `.codex-handoff.json` | 交接元数据（现行 read_order 指向 HANDOFF / CANON） |
| `.github/` | PR 模板 + CI 自动检查 |
| `Makefile` | 统一命令入口（make check / test / manifest） |

### 当前版本（主目录 = 最新最好的版本）

| 目录 | 角色 |
|------|------|
| `code/` | 代码资产：`src/rseco/` 源码 + `scripts/` 实验/审计入口 + `tests/` 回归 |
| `project/` | 构建工程 / 运行脚本（git-ignored，当前为空） |
| `experiments/` | 实验定义、设计与输出证据（`INVENTORY.md` / `RESULTS.md` / `design/`） |
| `docs/` | 技术文档：`environment.md`、`GLOSSARY.md`、`EXPERIENCE.md`、`literature/`、`materials/` |

### 项目级共享

| 目录 | 角色 |
|------|------|
| `data/` | 数据治理：`cases/` 构造用例（跟踪）+ `raw/benchmarks/` 原始基准（raw 不跟踪，manifests 登记 SHA） |
| `paper/` | 论文：`zh/` 中文主版；`en/` 英文工作初稿（`build/FAECO.pdf` 为已保存预览） |
| `project_docs/` | 过程文档：交接（`HANDOFF_2026-11-09.md`）/ 基线（`baselines/`）/ 证据（`evidence/`）/ 日志（`LOGS.md`）/ 未决（`OPEN_ISSUES.md`）/ 现状（`CANON.md`、`PROJECT_MAP.md`）/ 设计规范 / 归档（`archive/`） |

### 版本与辅助

| 目录 | 角色 |
|------|------|
| `versions/` | 历史冻结版本集合（**v19 是最后一个冻结基线 = r28 + r94 口径修订**；v20 待建以收录 r95–r116。见 `project_docs/versioning.md`） |
| `skills/` | 项目级技能（ARS 学术技能 + academic-paper 写作技能） |
| `scratch/` | 临时脚本 / 探针 / 运行日志（git-ignored） |

## 工作规则

1. **版本定义**：每个版本 = 论文 + 源码 + 测试 + 证据的四元绑定，冻结为 `versions/<基线ID>/` 完整快照；详见 `project_docs/versioning.md`。
2. **工作树**：一次性执行环境，物理位置在同步仓库之外，注册于 `project_docs/worktrees/WORKTREE_REGISTRY.csv`。
3. **结论口径**：每条结论区分「软件本地复现 / 策略复现 / 硬件复现 / 实测数据」；论文数字必须与 `experiments/` 产物对账。
4. **证据自包含**：每个证据包含 README + 摘要 + 输入/来源 + 原始输出 + SHA-256 清单；实验证据文件严禁删除。
5. **产物隔离**：生成产物放 git-ignored 的 `project/`、`scratch/`，绝不放在源码或主稿件旁。
6. **中英双版本**：论文以 `zh/` 为主版本；只有进入英文期刊流程时才维护 `en/`，两版结论必须一致。
7. **交接即承诺**：每轮结束只更新 `project_docs/LOGS.md`（收尾一条）+ `project_docs/CANON.md`（口径有变时）；`WORK_PROGRESS.md` 与 `agent_handoff/*` 已停用，不再更新。
8. **质疑优先**：任何结论、方案与数字在采信前先质疑与验证；证据高于权威。
9. **质量标准**：设计先评审后实施；实施不轻易降级，需要时敢于大改。
10. **Git 纪律**：阶段性工作完成即 `git commit` + `git push`；重大改动前先固化当前状态；**禁止 `git add -A`**（按路径逐条 add）。
11. **行尾纪律**：`.tex` / `.md` / `OPEN_ISSUES.md` 纯 LF；`LOGS.md` 纯 CRLF；`.sh` 由 gitattributes 管；**禁止出现 `\r\r\n`**（写盘用 `newline=''` + 显式换行，不要用文本模式默认翻译）。
12. **经验沉淀**：解决问题后当天登记到 `docs/EXPERIENCE.md`。
13. **并行协作**：可分解的独立子任务默认并发；关键路径留在主线。
14. **破坏性操作防护**：删除 / 覆盖 / 重构前先 `git status`；删除用 `git rm`，不裸 `rm`。

## 历史专项

2026-10-14 ~ 10-25 的 r22 / r30 历史状态、判定带证伪预演、GNN 裁决等专项记录已**从本文档移除**，完整原文在 git 历史与 `project_docs/LOGS.md`（LOG-20261024/20261025 系列）中可溯源。需要时读 `project_docs/CANON.md` 的现行结论，不要从历史段落取状态。
