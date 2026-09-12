# FAECO — Failure-Aware Resynthesis-Assisted Timing ECO

**面向逻辑级时序 ECO 的 failure-aware 修复框架**：在重综合辅助 patch replacement 思路基础上，建立公开 benchmark 上的可复现实验流程，研究等价 patch 切割失败后的自适应恢复机制。

> 中文工程类研究项目 · 目标：可复现、可投稿的时序 ECO 论文

---

## 目录

- [1. 项目简介](#1-项目简介)
- [2. 研究主线与贡献](#2-研究主线与贡献)
- [3. 当前进展（2026-08-03）](#3-当前进展2026-08-03)
- [4. 核心方法](#4-核心方法)
- [5. 快速开始](#5-快速开始)
- [6. 实验复现](#6-实验复现)
- [7. 目录结构](#7-目录结构)
- [8. 工具链](#8-工具链)
- [9. Benchmark 与许可](#9-benchmark-与许可)
- [10. 已知 limitation](#10-已知-limitation)
- [11. 文档导航（智能体交接）](#11-文档导航智能体交接)
- [12. 路线图](#12-路线图)

---

## 1. 项目简介

FAECO（**F**ailure-**A**ware **E**CO）继承 RSECO 学长的"重综合辅助 patch replacement"思路，但不再沿用 RSECO 名称，避免让新工作看起来只是整理或复刻学长系统。核心思想：

> 对时序约束变化后的 RTL 重新综合，得到时序更优的新网表；在新旧网表之间寻找等价局部子电路，将新网表中时序友好的 patch 移植回原始网表。当 min-cut 产生的 patch boundary 无法通过等价验证、patch 过大或时序收益不足时，根据失败原因自动调整搜索方向。

**第一阶段**：处理 timing path 上的组合逻辑 cone（combinational）。
**第二阶段**：扩展到 sequential benchmark 中的局部组合逻辑 cone。

不直接修改寄存器结构，定位为"时序路径局部组合逻辑 ECO"。

---

## 2. 研究主线与贡献

**FAECO = Failure-Aware ECO + Reproducible Timing ECO Benchmark Flow + Timing-Aware Patch Ranking**

1. **算法贡献**：F1-F5 失败分类驱动的 failure-aware cut refinement——根据等价失败、patch size、关键路径覆盖不足和时序收益不足动态调整 cut weights。
2. **流程贡献**：构建公开 benchmark 上的 resynthesis-assisted timing ECO case generation flow，补足旧工作工业案例不可复现的问题。
3. **排序贡献**：timing-aware patch ranking，在多个候选 patch 中平衡 WNS/TNS 改善、patch size、边界复杂度和验证成本。
4. **实验贡献**：在公开 benchmark 上对比 fixed min-cut、random cut、size-only cut、critical-path-only cut 与本文方法。

---

## 3. 当前进展（2026-08-03）

### 回归基线

```
102 项测试通过，0 failure，0 error
（66 Stage A + 24 Stage B + 12 N31-06 Z3）
```

### Stage A：5-case combinational 端到端

| 检查项 | 结果 |
|---|---|
| 数据集 | c17×2（N22/N23）+ c432 + c499 + c880 |
| 形式验证 | Yosys-normalized full-netlist ABC CEC 5/5 `pass` |
| ABC baseline | rewrite/refactor/resyn 5/5 `success` |
| 产物 | `experiments/20260718_minimal_combinational_batch_demo/tables/` |

### Stage B：8-case EPFL 端到端

| benchmark | mapping | mapping_s | sta | sta_s | slack_status |
|---|---|---|---|---|---|
| ctrl | success | 1.226 | success | 3.111 | MET |
| int2float | success | 1.479 | success | 0.640 | MET |
| router | success | 1.582 | success | 0.628 | MET |
| cavlc | success | 3.306 | success | 0.616 | MET |
| dec | success | 1.377 | success | 0.621 | MET |
| priority | success | 4.991 | success | 0.632 | MET |
| adder | success | 5.713 | success | 0.662 | MET |
| max | success | 16.784 | success | 3.268 | MET |

### 等价验证（关键突破，2026-08-03）

```
Yosys miter + SAT：8/8 EPFL case 等价证明 SUCCESS
（original == mapped，sat -prove-asserts 不可满足）
```

- 原 ABC `cec` 无法对 Liberty subcircuit 建 model（工具限制），改用 **Yosys miter + SAT** 路径解决
- `scripts/verify_epfl_mapping_sat.py` + `scripts/make_liberty_cells_v.py`
- `risk_register.md` R31-01 → **mitigated**

### 论文框架

| 章节 | 文件 | 状态 |
|---|---|---|
| Introduction | `paper/draft/introduction.md` | Draft 1 |
| Related Work（6 主题 / 25A/1B） | `paper/draft/related_work.md` | Draft 1 |
| Method 符号表 | `paper/draft/method_symbol_table.md` | Draft 1 |
| Method 正文 | `paper/draft/method.md` | Draft 1 |
| Experiments | `paper/draft/experiments.md` | Draft 1 |
| Conclusion | `paper/draft/conclusion.md` | Draft 1 |
| 论文主图 ×5 | `paper/figures/fig{1..5}.png` | 已生成 |
| 自审稿 round1/round2 | `paper/reviews/` | 已落地 |

### Git / GitHub

```
仓库：111 commits（main 分支）
远程：https://github.com/Toylog123/FAECO.git（已 push 同步）
```

---

## 4. 核心方法

### 4.1 三阶段流水线（fig3）

```
(a) Resynthesis     Yosys synth -top <t> -noabc + abc -liberty <lib>
                    → mapped 网表（SKY130 HD Liberty cells）
(b) Cut & Refine    fanin cone → weighted s-t min-cut → F1-F5 失败反馈
(c) Verify & STA    Yosys miter+SAT 等价 + OpenSTA pre-layout STA
```

### 4.2 F1-F5 失败分类

| 失败类型 | 检测条件 | 反馈动作 |
|---|---|---|
| F1 等价失败 | ABC cec ≠ pass | 加权 verification cost |
| F2 边界失败 | boundary_closed=False | 收紧 cone 边界 |
| F3 size 过大 | size > threshold | 提升高 fanout gate cost |
| F4 timing 收益不足 | ΔWNS < threshold | 重算 candidate gain |
| F5 验证超时 | timeout > threshold | 加权 verification cost |

### 4.3 等价验证三条路径

1. **结构签名**（`src/rseco/equivalence.py`）——快速检查
2. **Yosys miter + SAT**（`scripts/verify_epfl_mapping_sat.py`）——**主路径**，8/8 EPFL case pass
3. **Z3 candidate/boundary**（`src/rseco/z3_formal.py`）——patch 局部验证补充（12 项 TDD）

### 4.4 SDC + OpenSTA

确定性 virtual-clock SDC（`src/rseco/sdc.py`）→ OpenSTA pre-layout STA（`src/rseco/opensta.py`，WSL2 `_to_sta_path` 路径转换）。

---

## 5. 快速开始

### 环境要求

- Windows 11 + WSL2 Ubuntu 24.04（OpenSTA）
- Python 3.11.9

### 安装与验证

```powershell
# 1. 激活虚拟环境
cd D:\BaiduSyncdisk\03_FAECO
& .\.venv\Scripts\Activate.ps1

# 2. 设置 Python path
$env:PYTHONPATH='src'

# 3. 工具链版本
python --version                # 3.11.9
yosys -V                        # 0.9
yosys-abc -h                    # ABC 1.01
wsl.exe -d Ubuntu -- /usr/local/bin/sta -version   # 3.1.0

# 4. 完整回归
python -m unittest discover -s tests   # 102 项通过
```

### 核心依赖

```bash
pip install z3-solver==5.0.0 networkx==3.6.1
```

---

## 6. 实验复现

```bash
# Stage A 5-case batch
python scripts/run_minimal_combinational_demo.py \
    --config experiments/configs/minimal_combinational.json \
    --output-dir experiments/20260718_minimal_combinational_batch_demo

# Stage B 8-case 端到端（mapping + SDC + OpenSTA）
python scripts/run_stage_b_pre_layout_sta.py \
    --output-dir experiments/20260731_epfl_8case_stage_b \
    --sta-command "wsl -d Ubuntu -- /usr/local/bin/sta"

# 等价验证（Yosys miter + SAT，8/8 pass）
python scripts/verify_epfl_mapping_sat.py --output-dir tmp/sat_verify

# 生成 Liberty function cells.v
python scripts/make_liberty_cells_v.py

# 论文主图
python scripts/make_paper_figures.py

# N31-06 Z3 candidate/boundary check
python scripts/run_z3_candidate_boundary_check.py --output-dir <dir>
```

---

## 7. 目录结构

| 路径 | 作用 |
|---|---|
| `src/rseco/` | Python 实现（22 模块：yosys_json / technology_mapping / sdc / opensta / z3_formal / yosys_abc / cut / ranking / refinement 等） |
| `tests/` | unittest 测试（102 项） |
| `scripts/` | 数据准备、实验运行、结果汇总 CLI（13 个） |
| `docs/` | 主线、工程结构、实验方案、论文审计、项目管理 |
| `docs/project_management/` | 路线图、里程碑、风险、决策、工作日志、**智能体交接** |
| `docs/engineering/` | 工具链 + N31-03/04/05/06 设计文档 |
| `paper/draft/` | 论文 6 章节 Draft 1 + README 索引 |
| `paper/figures/` | 论文主图 ×5 |
| `paper/reviews/` | 自审稿 round1/round2 + 修订说明 |
| `paper/submission/` | 投稿版本占位 |
| `experiments/` | 实验配置、原始结果、表格 |
| `benchmarks/raw/` | EPFL v2025.1 + ISCAS85 + SKY130 HD（许可材料，不入库） |
| `benchmarks/source_manifests/` | benchmark 来源、license、blob SHA 固定 |
| `data/cases/` | 最小 ECO case 数据 |

---

## 8. 工具链

| 工具 | 版本 | 用途 |
|---|---|---|
| Python | 3.11.9 | 主实现 |
| Yosys | 0.9 | Verilog 规范化、tech mapping、等价验证（miter/SAT） |
| ABC | 1.01（yosys-abc） | 综合/验证辅助 |
| OpenSTA | 3.1.0（WSL2） | pre-layout STA |
| Z3 | 5.0.0 | candidate/boundary 形式验证 |
| NetworkX | 3.6.1 | 图算法 |
| matplotlib | 3.11.1 | 论文主图 |

---

## 9. Benchmark 与许可

| 数据集 | 版本/commit | 许可 | 用途 |
|---|---|---|---|
| EPFL | `v2025.1` / `8c832d5d...` | MIT | 论文主集（8 combinational） |
| SKY130 HD Liberty | `da8f092a...`（ORFS） | BSD-3-Clause / Apache-2.0 | Stage B timing 模型 |
| ISCAS85 c432/c499/c880 | `b4c6b620...`（第三方） | 未声明 | 仅本地 smoke |
| skywater cells 模型 | `ac7fb61f...` | Apache-2.0 | 等价验证（本地） |

> 原始许可材料（Liberty、EPFL Verilog、skywater models、ISCAS85）**不进入 Git 仓库**，仅存于 `benchmarks/raw/`（A-only 范围之外）。

---

## 10. 已知 limitation

| 项 | 说明 | 处理 |
|---|---|---|
| STA slack_status=MET | 8 case 全 combinational，无 timing path → slack=null / MET(INF) | 合理结果；N31-05 sequential 扩展可补 WNS/TNS |
| failure_recovery proxy | `avg_iterations=1.0`（single-iteration） | X19 multi-iteration（待 design 审批） |
| N31-06 Z3 8-case 端到端 | mapped.v 门级实例化，assign-only parser 受限 | 等价验证主路径已由 SAT 解决；Z3 保留 patch 局部验证 |

---

## 11. 文档导航（智能体交接）

**接手智能体必读（按顺序）：**

1. `docs/project_management/STAGE_B_AGENT_HANDOFF.md` — 项目交接总览（当前状态、授权、下一步）
2. `docs/task_board.md` — 任务看板
3. `docs/project_management/work_log.md` — 每日工作日志（LOG-2026xxxx 按日期）
4. `docs/project_management/decision_log.md` — 关键决策记录
5. `docs/project_management/risk_register.md` — 风险登记
6. `docs/project_management/long_term_task_plan.md` — 长期任务规划
7. `docs/paper_audit/method_rewrite_readiness.md` — 18 项方法要素就绪矩阵
8. `docs/engineering/` — 工具链 + N31-03/04/05/06 设计文档
9. `paper/draft/README.md` — 论文章节索引
10. `paper/reviews/round1_self_audit.md` + `round2_self_audit.md` — 自审稿

---

## 12. 路线图

| 阶段 | 状态 |
|---|---|
| Phase 0-4（主线/审计/原型/第一轮实验） | ✅ 完成 |
| Phase 5（sequential cone） | 待启动（N31-05） |
| Phase 6（论文初稿） | 🔄 进行中（6 章节 Draft 1） |
| Phase 7（内部审稿） | 🔄 进行中（round1/round2 自审） |
| Phase 8（投稿准备） | 待启动 |

---

*详细执行记录见 `docs/project_management/work_log.md`（按日期索引）。项目交接见 `docs/project_management/STAGE_B_AGENT_HANDOFF.md`。*
