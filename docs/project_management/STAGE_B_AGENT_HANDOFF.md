# FAECO 项目智能体交接

更新时间：2026-08-03

> **接手智能体必须首先读本文件**，再按第 9 节文档地图顺序读其余文档。不要依赖聊天记录或对话摘要推断状态——一切以本文件和 `docs/task_board.md`、`docs/project_management/work_log.md`、`docs/project_management/decision_log.md` 为准。

---

## 1. 项目定位

FAECO（**F**ailure-**A**ware **E**CO）是中文工程类时序 ECO 研究项目，继承 RSECO 学长"重综合辅助 patch replacement"思路：

> 对时序约束变化后的 RTL 重新综合得到时序更优网表，在新旧网表间寻找等价局部子电路，将时序友好 patch 移植回原始网表；当切割失败、patch 过大或时序收益不足时，按 F1-F5 失败类型自适应调整搜索方向。

**当前阶段**：combinational（组合逻辑 cone）。后续扩展 sequential。

---

## 2. 当前状态（2026-08-03 快照）

### 核心指标

| 项 | 值 |
|---|---|
| Git commits | **111**（main 分支） |
| 远程仓库 | `https://github.com/Toylog123/FAECO.git`（**已 push 同步**） |
| 回归测试 | **102 项通过，0 failure，0 error** |
| Stage A | 5-case combinational 端到端（ABC CEC 5/5 pass + baseline 5/5） |
| Stage B | 8-case EPFL mapping→SDC→OpenSTA 8/8 success |
| **等价验证** | **8/8 EPFL case Yosys miter+SAT SUCCESS**（CEC 突破） |
| 论文 | 6 章节 Draft 1 + 5 张主图 + round1/round2 自审稿 |
| 执行授权 | 用户已恢复授权并持续推进；push 已执行 |

### 已关闭的关键项

- **CEC limitation（R31-01）→ mitigated**：ABC `cec` 无法对 Liberty subcircuit 建 model，改用 Yosys miter+SAT（`scripts/verify_epfl_mapping_sat.py` + `scripts/make_liberty_cells_v.py`），8/8 等价证明 SUCCESS。
- **Git push（N31-04）→ done**：111 commits 已推送 GitHub。
- **N31-06 Z3 wrapper → 实施完成**：12 项 TDD 测试，单元测试层面完整。
- **round2 必改清单 → 100%**：4 章节修订 + method §6 + 5 张主图。

---

## 3. 已完成工作

### 3.1 工具链

| 工具 | 版本 | 位置/用途 |
|---|---|---|
| Python | 3.11.9 | `.venv` |
| Yosys | 0.9 | Verilog 规范化 / tech mapping / **miter+SAT 等价验证** |
| ABC | 1.01（`yosys-abc`） | 综合/验证辅助（CEC 主路径不可用，SAT 替代） |
| OpenSTA | 3.1.0 | WSL2 `/usr/local/bin/sta` |
| Z3 | 5.0.0 | candidate/boundary 形式验证 |
| NetworkX | 3.6.1 | 图算法 |
| matplotlib | 3.11.1 | 论文主图 |

> **重要：Yosys 0.9 不支持 UDP primitive**（下载的 skywater cell Verilog 模型含 UDP），且 `read_liberty` 把 cell 标 blackbox。等价验证必须走 miter+SAT 路径（见第 5 节），不要回退到 ABC `cec` 或 `read_liberty` + equiv_simple。

### 3.2 数据资产

| 数据集 | commit | 许可 | 位置 | 入库 |
|---|---|---|---|---|
| EPFL v2025.1 | `8c832d5d...` | MIT | `benchmarks/raw/epfl_v2025_1_full/` | ❌（raw） |
| SKY130 HD Liberty | `da8f092a...` | BSD-3/Apache-2.0 | `benchmarks/raw/openroad_flow_scripts_sky130hd/.../lib/` | ❌ |
| skywater cells 模型 | `ac7fb61f...` | Apache-2.0 | `benchmarks/raw/skywater_cells_models/`（70 cells + UDP + cells_v2.v） | ❌ |
| ISCAS85 c432/c499/c880 | `b4c6b620...` | 未声明 | `benchmarks/raw/iscas85/` | ❌（仅本地 smoke） |

**A-only 范围**：入库的是 `src/` `tests/` `scripts/` `docs/` `paper/`（除 raw 材料）+ `experiments/configs` + `benchmarks/source_manifests`。raw 许可材料、实验产物、data/ **不入库**。

### 3.3 关键脚本

| 脚本 | 用途 |
|---|---|
| `scripts/run_stage_b_pre_layout_sta.py` | Stage B 8-case 端到端（mapping+SDC+OpenSTA） |
| `scripts/verify_epfl_mapping_sat.py` | **等价验证主路径**（Yosys miter+SAT，8/8 pass） |
| `scripts/make_liberty_cells_v.py` | 从 Liberty function 生成 assign-style cells.v |
| `scripts/make_paper_figures.py` | 论文 5 张主图 |
| `scripts/run_z3_candidate_boundary_check.py` | N31-06 Z3 candidate/boundary |
| `scripts/run_minimal_combinational_demo.py` | Stage A batch |
| `scripts/build_stage_b_summary.py` | Stage B 汇总表 |

### 3.4 论文框架

- `paper/draft/`：introduction / related_work / method_symbol_table / method / experiments / conclusion（全部 Draft 1）
- `paper/figures/`：fig1-5 已生成
- `paper/reviews/`：round1_self_audit + round1_revision_notes + round2_self_audit
- `paper/submission/`：占位

---

## 4. 关键决策记录（decision_log 摘要）

| 日期 | 决策 | 理由 |
|---|---|---|
| 2026-07-20 | Stage B tech mapping 用 `synth -noabc + abc -liberty` | 避免 Yosys techmap 生成 clkinv_1 placeholder |
| 2026-07-31 | OpenSTA 接入 WSL2 via `_to_sta_path` | Windows→WSL 路径转换 |
| 2026-08-03 | **等价验证改 Yosys miter+SAT** | ABC `cec` 对 Liberty subcircuit 建 model 失败（连极简 Liberty 也失败）；read_liberty 标 blackbox；skywater 模型含 UDP |
| 2026-08-03 | **从 Liberty function 提取 assign cells.v** | 绕过 UDP（Yosys 0.9 不支持）和 blackbox |
| 2026-08-03 | **GitHub push 到 Toylog123/FAECO** | 用户明确要求；仓库已有历史，未用 git init（会破坏） |

完整记录：`docs/project_management/decision_log.md`。

---

## 5. 等价验证路径（重要）

### 5.1 主路径：Yosys miter + SAT（8/8 pass）

```bash
python scripts/make_liberty_cells_v.py   # 生成 benchmarks/raw/skywater_cells_models/sky130_cells_v2.v
python scripts/verify_epfl_mapping_sat.py --output-dir tmp/sat_verify
```

原理：从 Liberty boolean function 提取 assign-style cells.v（无 UDP/blackbox），Yosys `read_verilog` 读入后 `miter -equiv` 创建比较电路，`sat -prove-asserts` 证明不可满足（等价）。

### 5.2 不用的路径（工具限制记录）

- **ABC `cec`**：`read_blif` 对 Liberty subcircuit 建 model 普遍失败（连极简 Liberty 也失败）——不用
- **Yosys `read_liberty` + equiv_simple**：read_liberty 把 cell 标 blackbox，无法展开——不用
- **下载的 skywater Verilog 模型**：含 UDP primitive，Yosys 0.9 不支持——不用（只作许可证据）

### 5.3 Z3 candidate/boundary（补充）

`src/rseco/z3_formal.py`（12 项 TDD）用于 patch 局部等价（multi-output/escaped/xor/constant）。8-case 端到端受限（mapped.v 门级实例化），等价主路径已由 SAT 解决，Z3 保留为 patch 验证补充。

---

## 6. 已知 limitation

| 项 | 说明 | 处理 |
|---|---|---|
| STA slack_status=MET | 8 case 全 combinational → slack=null / MET(INF) | 合理；N31-05 sequential 补 WNS/TNS |
| failure_recovery proxy | `avg_iterations=1.0` | X19 multi-iteration（待 design 审批） |
| N31-06 Z3 8-case 端到端 | mapped.v 门级实例化 | 等价主路径已由 SAT 解决 |
| ISCAS85 许可 | c432/c499/c880 未声明 | 仅本地 smoke |

---

## 7. 剩余待办（按优先级）

| 优先级 | 任务 | 依赖 |
|---|---|---|
| P0 | X19 multi-iteration refinement | 用户 design 审批（failure recovery 成功口径） |
| P1 | N31-05 sequential Stage C | 用户决定启动（9-11 周工作量） |
| P1 | SAT 验证并入正式 Stage B 表格 | 把 `sat_equivalence_summary.json` 并入 `stage_b_case_summary.md` |
| P2 | 论文章节迁入 `paper/submission/` | 用户审定 6 章节 |
| P2 | Z3 patch-level 集成 | FAECO patch ranking 产生多候选后 |

---

## 8. 执行规则

1. **TDD**：行为变更必须先写失败测试再实现。
2. **A-only 范围**：禁止 `git add .`；只 commit 代码/文档/配置，不 commit raw 许可材料/实验产物。
3. **不升级 Yosys 0.9**（当前门数口径依赖）。
4. **不下载完整 Sky130 PDK**（7 GB+）。
5. **失败保留原始日志**，缺失值写 `unavailable` + 原因，禁止填 0。
6. **每完成一项**：更新 `docs/task_board.md` + `docs/project_management/work_log.md`（带日期 LOG 条目）+ 必要时 `decision_log.md`。
7. **push**：已配置 origin（Toylog123/FAECO）。push 前跑 102 项回归，push 后确认 `git status` 与 origin 同步。
8. **工具链快照**：`experiments/environment/toolchain_YYYY-MM-DD.json`，不覆盖历史快照。

---

## 9. 文档地图（接手必读顺序）

| 顺序 | 文档 | 内容 |
|---|---|---|
| 1 | `docs/project_management/STAGE_B_AGENT_HANDOFF.md` | **本文件** |
| 2 | `docs/task_board.md` | 任务看板（含 X/N31 系列状态） |
| 3 | `docs/project_management/work_log.md` | 每日日志（LOG-20260714 至 LOG-20260803-13） |
| 4 | `docs/project_management/decision_log.md` | 关键决策 |
| 5 | `docs/project_management/risk_register.md` | 风险登记 |
| 6 | `docs/project_management/long_term_task_plan.md` | 长期规划 |
| 7 | `docs/paper_audit/method_rewrite_readiness.md` | 18 项方法要素就绪矩阵 |
| 8 | `docs/engineering/` | 工具链 + N31-03/04/05/06 设计 |
| 9 | `paper/draft/README.md` | 论文章节索引 |
| 10 | `paper/reviews/round2_self_audit.md` | 最新自审稿 |

**起点命令**：

```powershell
cd D:\BaiduSyncdisk\03_FAECO
& .\.venv\Scripts\Activate.ps1
$env:PYTHONPATH='src'
python -m unittest discover -s tests   # 期望 102 项通过
git status                             # 期望 main 与 origin/main 同步
```

---

## 10. 继续/恢复指令模板

接手后如要继续推进，可直接使用：

```text
按 docs/project_management/STAGE_B_AGENT_HANDOFF.md 继续项目。
当前状态已核对（102 测试 / 8-case SAT 8/8 pass / GitHub push 完成）。
下一步：[X19 设计 | N31-05 sequential | SAT 并入正式表 | 论文章节迁入]。
```

---

*本交接文档随项目进展持续更新。当前快照 2026-08-03（111 commits / 102 测试 / CEC 8/8 / GitHub 已 push）。*
