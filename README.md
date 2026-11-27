# FAECO 布线后局部冲突诊断与限时面积回收

> **2026-11-27 第四轮当前总入口**见[现行口径](project_docs/CANON.md)。项目面向 IEEE TCAD，研究布线后局部冲突诊断与限时面积回收。[13 页中文第四轮修订稿](paper/zh/FAECO_v3_后布局可调预算面积回收.pdf) · [第四轮逐条复核](paper/zh/review_rounds/r20261127_r4_submission/R4_REVIEW_MAP.md) · [公开复算入口](project_docs/evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md)。

> **历史冻结 `v22`（`v2026-11-23-cross-pdk-lr-baselines`）** 收录经典 LR 十电路对照及 ASAP7 AES 的全局布线寄生估算。 [11 月 23 日交接快照](project_docs/HANDOFF_2026-11-23.md)

<details>
<summary>历史入口归档（2026-11-09 / 2026-11-13 预布局与单点过渡期说明，点击展开仅作溯源）</summary>

可调预算的真实归档数据复核（不启动新EDA）：

```powershell
.venv/Scripts/python.exe project_docs/evidence/timing_budget_20261113/evaluate_budget.py --budget-ps 0 5 10 20 --output scratch/recovery_budget_results.json
```

输出同时列出待证明候选与已通过SEC的可交付端点。旧 `code/scripts/recover_area.py` 仍是15ps默认/旧SPEF路径，未被本阶段悄悄替换。

> **2026-11-13 当前入口：可调时序预算机制。** 优先读 `project_docs/evidence/timing_budget_20261113/REPORT.md` 与 `project_docs/CANON.md`。保留Resizer前端；默认允许WNS最多损失10ps，TNS辅助、hold保持原门。s382既有端点在该预算下已补SEC101/0：回收Resizer净新增面积28.90625%（总面积−4.399524%，WNS−3.098077ps，TNS−0.231982231ns）。这是已有物理端点重筛，不是新搜索算法收益。新 `code/src/rseco/budgeted_recovery.py` 实现纯策略/有界组合搜索，在线物理评估器、完整IO约束、强基线/跨设计尚待建立；下方strict政策与旧状态均保留历史。

> **2026-11-13 最新续跑**：见 `project_docs/evidence/strict_area_search_20261113/REPORT.md`。新增9组合+2同面积variant全部未过严格门，两排序所有预算前缀均保留原096安全端点（面积−0.594530321%）。完整网表/Liberty另枚举62个静态兼容降面积替换，旧清单只覆盖10；剩余51个遗漏目标本轮未测。静态候选不是收益，自有机制优势/完整约束仍open。
> **2026-11-13 当前研究入口**：[严格时序面积研究](project_docs/evidence/recovery_repair_20261113/REPORT.md) + `project_docs/CANON.md`。s382已有面积下降0.594530321%、propagated WNS/TNS改善及hold不变、SEC通过的局部保守基线；自有机制优势与ICCAD资格尚未建立。下方2026-11-09状态只作历史，工具环境以 `docs/environment.md` 为准，Git状态实时查询。

</details>

## 历史状态（2026-11-22 复核）

- **当时中文 v3**：14 页、5 张矢量图。历轮编译、配图和活跃稿件的交付记录见 [论文变更日志](paper/zh/CHANGE_LOG.md)。
- **版本与目录**：`versions/v20/` 已落地（`BASELINE_INDEX.csv` `status=active` 指向 `v20`，原 `v19` 标为 `superseded`）；`paper/zh/` 下旧备份、编译日志与 QA 预览图已分别归整到 `paper/zh/archives/` 与 `paper/zh/figures/qa_previews/`。
- **核心成果口径**（详见 `project_docs/evidence/postroute_recovery_20261120/REPORT.md`）：
  - **脱离上游日志纯独立重布线回收**：10/10（100%）跨族电路实现 `0.67%–5.58%` 总面积降幅（仅 6–10 次评估、全部 `DRC=0`、`Δhold >= 0`、10/10 SEC PASS），超越 12/12 为 `0.00%` 的原生 `recover_power 100`；
  - **多角与 IO+OCV 联合签核**：在线门控下 SKY130 SS 慢角 **10/10（100%）** 满足 10 ps 预算，IO+OCV 联合审计 **7/7（100%）** 达标；
  - **$O(\log N)$ 转折门隔离**：`b22` 仅用 10 次 STA 定位唯一转折门并回收 356/359 处修改（33.1%）。
- **测试**：`pytest code/tests/test_physical_budget_adapter.py code/tests/test_budgeted_recovery.py code/tests/test_recover_area.py -q` → **54 passed**。
- **环境**：WSL2 Ubuntu（OpenROAD、OpenSTA、Yosys）+ Windows Python `.venv` + LuaLaTeX（详见 `docs/environment.md`）。

## 项目简介

FAECO 在已布线设计上生成等价的降面积候选，利用布线前冲突标记定位可放行的邻线，并按墙钟预算回收面积。当前有效端点的验收包含重布线与寄生提取、多角时序、独立 DRC 和 SEC。 [现行范围与证据](project_docs/CANON.md)

- 项目类型：算法研究（EDA / 时序优化）
- 技术栈：Python、Yosys、OpenSTA、OpenROAD 26Q3、SKY130HD、ASAP7 和 LuaLaTeX。

## 历史预布局设计

FAECO 三阶段流水线（映射准备 → 加权割与候选生成 → 验证与接受）：

1. **映射准备**：Yosys 两步流程生成 SKY130 HD 映射网表；Liberty 提供单元逻辑与时序信息。
2. **加权割与候选生成**：违例扇入锥上构造 s-t 分裂图，Liberty 函数匹配生成 R 候选；加权最小割 $C_w$ 与关键路径覆盖割 $C_c$ 互补实例化 R/G/B/JOINT 候选，按割代价、路径覆盖、策略优先级排序。
3. **验证与接受**：OpenSTA 理想线网测量 ΔWNS（接受谓词，TNS-aware 平局分支可选）；10 ps 物理门控下进入简化 SPEF 复测；F1–F6 失效反馈更新割权重；最终独立顺序 SEC（Yosys equiv_simple/equiv_induct）验证功能等价。

关键设计文档：`code/src/DESIGN.md`（源码层设计）、`project_docs/design_specs/engineering/`（工程设计）、`docs/environment.md`（工具链与复现环境）。

## 现行权威状态入口

1. **接手、复现、自检与后续实验**见 [交接](project_docs/HANDOFF_2026-11-25.md)。
2. **唯一现行口径**：`project_docs/CANON.md`（任何文档与它冲突，以它为准）
3. **目录 / 版本 / 数据资产 / 结构性坑**：`project_docs/PROJECT_MAP.md`
4. **事实流水**：`project_docs/LOGS.md`（正序，可回溯）
5. **未决问题（未解决持续保留，必须告知）**：`project_docs/OPEN_ISSUES.md`
6. **证据索引**：`project_docs/evidence/PAPER_EVIDENCE_MANIFEST.md`

> `project_docs/WORK_PROGRESS.md` 停在 r93（2026-10-28）、`project_docs/agent_handoff/` 停在 r30（2026-10-24）——**自 2026-11-04 起停用，只作溯源，不再更新**，逐轮记录只落 `LOGS.md` + `CANON.md`（口径有变时）。

## 快速开始

1. **环境**：读 `docs/environment.md`；Python 依赖见根 `pyproject.toml`（`pip install -e .`）；WSL2 内 Yosys/OpenSTA 按 environment.md 安装。Windows 侧跑 yosys 需 OSS-CAD `bin` + `lib` 同时入 PATH。
2. **测试**：`bash code/scripts/run_with_timeout.sh 300 .venv/Scripts/python.exe -m pytest code/tests -q`（须用 `.venv/Scripts/python.exe` 显式 Python，不能只写 `python`）。
3. **实验**见 [现行交接](project_docs/HANDOFF_2026-11-25.md) 的复现命令与 [实验登记](project_docs/evidence/EXPERIMENT_REGISTRY.md)。
4. **论文**：当前活跃中文 v3 主稿 `paper/zh/manuscript/FAECO_v3_后布局可调预算面积回收.tex`（归档 v2 稿与补充材料同在 `manuscript/`，详见 `paper/zh/README.md`）；**必须 `cd` 入 `manuscript/` 后显式选目标、LuaLaTeX 连跑两遍**（不能自动猜主文件）。洁净成品 PDF 在 `paper/zh/` 与 `paper/zh/build/`。
5. **交接**见 [2026-11-25 交接](project_docs/HANDOFF_2026-11-25.md)。

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
| `project_docs/` | 过程文档：交接（`HANDOFF_2026-11-25.md`）/ 基线（`baselines/`）/ 证据（`evidence/`）/ 日志（`LOGS.md`）/ 未决（`OPEN_ISSUES.md`）/ 现状（`CANON.md`、`PROJECT_MAP.md`）/ 设计规范 / 归档（`archive/`） |

### 版本与辅助

| 目录 | 角色 |
|------|------|
| `versions/` | 冻结版本集合。各冻结版与当前工作稿的对应关系见 [交接](project_docs/HANDOFF_2026-11-25.md) 与 [版本规范](project_docs/versioning.md)。 |
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
