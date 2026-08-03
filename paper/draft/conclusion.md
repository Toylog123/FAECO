# FAECO Conclusion 初稿（Draft 1）

更新时间：2026-07-31

本文档为论文 Conclusion 章节的初稿，基于：
- `paper/draft/introduction.md`（PM25）贡献陈述
- `paper/draft/experiments.md`（PM28）端到端结果
- `paper/draft/method_symbol_table.md`（N05）符号与算法骨架
- `paper/draft/related_work.md`（L01）边界声明
- `docs/project_management/roadmap.md` 当前所处阶段

尚未经用户最终审定；结构和措辞仅作为论文主体终点，禁止作为主表事实性表述。

---

## 1. 工作总结

FAECO（Failure-Aware Resynthesis-Assisted ECO）继承 RSECO 旧稿的"重综合辅助 patch replacement"思路，把 failure-aware 反馈循环形式化为 5 类失败（F1-F5）+ deterministic 权重调整 + weighted s-t min-cut 重新搜索的原型，并在公开 benchmark 上端到端跑通：

1. **Stage A**：5 个 combinational case（c17 × 2 + c432 + c499 + c880）的 multi-baseline 端到端验证 —— Yosys-normalized full-netlist ABC `cec` formal 5/5 `pass`，ABC baseline (`yosys-abc` + Berkeley resyn2) 5/5 `success`，failure recovery proxy 表记录 F1-F5 initial fail / proxy recovered / recovery rate。
2. **Stage B**：8 个 EPFL `v2025.1` combinational benchmark（ctrl/int2float/router/cavlc/dec/priority/adder/max）的 mapping→SDC→OpenSTA pre-layout STA 端到端跑通 —— mapping 8/8 success，STA 8/8 success；产物 `experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.{json,md}` + `stage_b_runtime.{json,md}` 全部落盘。

**贡献**：
1. F1-F5 失败分类驱动的 failure-aware 切割与替换原型，单轮权重调整已实现并跑通 5-case 端到端。
2. EPFL `v2025.1` + SKY130 HD Liberty 公开组合逻辑 benchmark 上的可复现 mapping→SDC→STA 端到端流程（8-case 跑通）。
3. 基于 Yosys + ABC + OpenSTA 的开源工具链完成所有映射、等价与 STA 实验，全部产物可复现。

## 2. 当前 limitation（透明声明）

| ID | limitation | 影响 | 后续工作 |
|---|---|---|---|
| L31-01 / R31-01 | SKY130 Liberty 不含 `clkinv_1` cell，Stage B 8-case CEC 全部 `unavailable` | mapped-BLIF 与 reference BLIF 的 ABC `cec` 不可达 | N31-03 获取 ORFS 配套 techmap library（`cells.v` + `cells.vh` + Liberty），需用户授权下载完整 PDK 部分 |
| L31-02 | 8-case 全 combinational，无 timing path | STA `wns/tns/slack=null` / `slack_status=MET (INF)` | N31-05 SKY130 sequential ECO 拓展（DFF/restore 进 SDC，准备 clock tree） |
| L31-04 / X19 | failure_recovery 仍是 single-iteration proxy | `avg_iterations=1.0`，未实现真正 multi-iteration loop + without F1/F3/F4 消融 | PM22 X19 multi-iteration refinement 设计（需用户 design 审批） |
| L31-03 | Z3 candidate/boundary formal 未接入 | 当前仅 full-netlist formal + structural signature 两条路 | N31-06 Z3 candidate/boundary formal wrapper（Z3 已装，需 Python wrapper） |

## 3. 未来工作

按优先级：

1. **PM22 / N31-01 X19 multi-iteration refinement**：在成功口径获批后实现真正多轮 refinement loop、residual failure 分类、停止原因和 without F1/F3/F4 消融。这是把当前 `stage_a_proxy` 升级为 `multi_iteration` 的关键依赖。
2. **N31-03 ORFS techmap library**：获取 `cells.v` + `cells.vh` + Liberty 配套，消除 `clkinv_1` placeholder，修复 Stage B CEC limitation。
3. **N31-05 SKY130 sequential ECO 拓展**：把 DFF/restore 信号加进 SDC，准备 clock tree，扩展 mapping/STA 到 sequential EPFL benchmark。
4. **N31-06 Z3 candidate/boundary formal**：candidate/boundary 形式回验使用 Z3，补充当前仅 full-netlist formal 的覆盖。
5. **N31-04 N08 push to remote**：push 到 GitHub remote。当前本地 commit `b2eb459` 已就位，待用户决策 remote URL。

## 4. 公开性边界

本文**不引用**：
- 工业设计未声明 license 的 benchmark 数据
- [F08-B] DAC 2018 cost-aware multi-target（B 级证据）的算法细节、复杂度或实验数字
- [B06] BUFFALO（B 级证据）的 9-design PPA 数字与训练规模

所有数字均来自本机运行产物（`experiments/20260718_minimal_combinational_batch_demo/` 和 `experiments/20260731_epfl_8case_stage_b/`），通过 `python scripts/run_minimal_combinational_demo.py` / `python scripts/run_stage_b_pre_layout_sta.py` 可复现。工具链版本与 snapshot 已写入每个实验目录的 `environment/toolchain_snapshot.json`。

## 5. 后续修订

- L01 Related Work 迁入 `paper/submission/` 后，本文"工作"段重排并补充引用文献。
- N05 方法符号表获批后，本文的"工作"段补 X19 multi-iteration refinement 的算法描述。
- PM27 Method 章节正文（基于 method_symbol_table.md 重排）落地后，本文的"工作"段补具体细节。
- 用户最终审定后迁入 `paper/submission/conclusion.md`。
- 任何对 B 级证据 [F08-B] 和 [B06] 的引用须保留禁止声明，禁止引用其算法细节与数字。