# Paper Round 1 自审稿报告

更新时间：2026-07-31

本报告对 `paper/draft/` 下 6 个章节初稿（introduction / related_work / method_symbol_table / method / experiments / conclusion）做第一轮自审，逐项按 `paper/reviews/README.md` 检查清单评估，给出每项的 P0/P1/P2 状态与处置建议。

## 1. 方法 (Method, PM27 + N05)

| 要素 | 状态 | 自审结论 |
|---|---|---|
| METH-01 partial | P1 | combinational fanin cone 已实现；sequential reg-to-reg cone 待 PM23 (M5) 启动。结论中明确披露 limitation。 |
| METH-02 ready | **通过** | Yosys 规范化命令序列已 TDD 实现并跑通 5-case + 8-case。`src/rseco/yosys_abc.py`。 |
| METH-05 ready | **通过** | weighted s-t min-cut 已 TDD 实现并通过 synthetic regression test。`src/rseco/cut.py`。 |
| METH-08 partial | **P0** | Stage A 5-case CEC 5/5 pass；Stage B 8-case CEC 全部 `unavailable` (R31-01)。需 N31-03 ORFS techmap library 修复。 |
| METH-09 partial | P1 | F1-F5 taxonomy 已写；X19 multi-iteration 待启动 (PM22)。 |
| METH-10 partial | P1 | failure-aware refinement single-iteration proxy。X19 设计待用户审批。 |
| METH-12 partial | P1 | deterministic ranking 已实现，但 candidate timing gain 当前相同（Stage A proxy）。 |
| METH-15 ready | **通过** | runtime schema 已写，Stage B 8-case runtime 已落盘。 |
| METH-17 partial | P1 | Stage A 5-case + Stage B 8-case 跑通；3 项 limitation（CEC / ISCS85 / sequential）已记录。 |

**方法章 P0 问题 1 个**：METH-08 Stage B CEC unavailable（待 N31-03）。
**方法章 P1 问题 4 个**：METH-01 sequential、METH-09 X19、METH-10 multi-iter、METH-12 timing gain。

## 2. 实验 (Experiments, PM28)

| 检查项 | 状态 | 自审结论 |
|---|---|---|
| Stage A 5-case multi-baseline 表格 | **通过** | `experiments/20260718_minimal_combinational_batch_demo/tables/baseline_comparison.md` |
| Stage B 8-case per-case mapping + STA 表格 | **通过** | `experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.md` |
| Stage B 8-case runtime breakdown | **通过** | `experiments/20260731_epfl_8case_stage_b/tables/stage_b_runtime.md` |
| Stage A 5-case failure recovery proxy 表 | **通过** | `experiments/20260718_minimal_combinational_batch_demo/tables/failure_recovery.md` |
| Stage B 8-case CEC unavailable limitation 标注 | **通过** | `paper/draft/experiments.md` §4 + `stage_b_summary.json` `notes` 字段 |
| Stage B 8-case STA slack=null limitation 标注 | **通过** | `paper/draft/experiments.md` §4 + `stage_b_case_summary.md` 表 |

**实验章无 P0 问题**；所有 limitation 均透明标注。

## 3. 相关工作 (Related Work, L01)

| 检查项 | 状态 | 自审结论 |
|---|---|---|
| 6 大主题分组覆盖 25A/1B | **通过** | `paper/draft/related_work.md` §1-§6 |
| [F08-B] / [B06] 禁止引用算法细节与数字 | **通过** | `paper/draft/related_work.md` §8 明确声明 |
| [T01]/[T02]/[T05]/[F01]/[F03]/[F07] 工业数据禁止作为对比 | **通过** | `paper/draft/related_work.md` §8 明确声明 |
| 公开性边界（可写 / 禁写）声明完整 | **通过** | `paper/draft/related_work.md` §7（与 FAECO 关系小结）+ §8（证据等级禁止声明） |

**相关工作章无 P0/P1 问题**。

## 4. 限制与未来工作

| 检查项 | 状态 | 自审结论 |
|---|---|---|
| L31-01 / R31-01 SKY130 `clkinv_1` 透明 | **通过** | `paper/draft/experiments.md` §4 + `paper/draft/conclusion.md` §2 + `risk_register.md` R31-01 |
| L31-02 STA slack=null 透明 | **通过** | `paper/draft/experiments.md` §3 + `paper/draft/conclusion.md` §2 |
| L31-04 / X19 failure_recovery proxy 透明 | **通过** | `paper/draft/experiments.md` §3 + `paper/draft/conclusion.md` §2 + `paper/draft/method.md` §6 |
| N31-03 / N31-05 / N31-06 未来工作明确 | **通过** | `paper/draft/conclusion.md` §3 + `docs/project_management/roadmap.md` |

**限制与未来工作章无 P0/P1 问题**。

## 5. 工具链与可复现性

| 检查项 | 状态 | 自审结论 |
|---|---|---|
| Yosys 0.9 / ABC 1.01 / OpenSTA 3.1.0 版本明确 | **通过** | `paper/draft/experiments.md` §1 + `experiments/environment/toolchain_2026-07-30.json` |
| SKY130 Liberty SHA256 与 manifest 一致 | **通过** | `paper/draft/experiments.md` §1 + `benchmarks/source_manifests/sky130hd_openroad.json` |
| EPFL `v2025.1` commit 固定 | **通过** | `paper/draft/experiments.md` §1 |
| 每个实验目录有 toolchain_snapshot.json | **通过** | `experiments/20260718_minimal_combinational_batch_demo/environment/toolchain_snapshot.json` + `experiments/20260731_epfl_8case_stage_b/environment/toolchain_snapshot.json` |
| runner 命令可复现 | **通过** | `paper/draft/experiments.md` §2/§3 给出完整命令 |

**工具链与可复现性章无 P0/P1 问题**。

## 6. P0 / P1 / P2 问题汇总

### P0（必须解决）

1. **Stage B CEC unavailable (METH-08)**：受 SKY130 Liberty 不含 `clkinv_1` 影响，8-case CEC 全部 unavailable。
   - **处置**：N31-03 ORFS techmap library 获取（待用户授权 PDK 下载）。

### P1（可后续解决）

1. METH-01 sequential cone 未实现
2. METH-09 X19 multi-iteration refinement 设计未启动
3. METH-10 failure-aware refinement 仍是 single-iteration proxy
4. METH-12 deterministic ranking 中 candidate timing gain 当前相同（Stage A proxy）
5. ISCAS85 c432/c499/c880 许可不完备（仅作本地 smoke）

### P2（可接受 / 改进）

1. Z3 candidate/boundary formal wrapper 设计与代码已落地（`src/rseco/z3_formal.py` + 12 项 TDD 测试（7 原 + 5 multi）+ 8-case runner）。multi-output / escaped-identifier / xor / constant 支持已实现（2026-08-03，`4eaaa2a`，完整回归 102 项全绿）。端到端剩余 limitation：mapped.v 是 SKY130 门级实例化（0 assign，含 `clkinv_1` placeholder），assign-only wrapper 无法构建 replaced 侧 Z3 表达式 → 8-case 全 error 是诚实结果；支持需 Yosys AIG→SMT 路径（N31-06 设计文档已声明边界，见 `docs/engineering/z3_candidate_boundary_formal.md`）
2. Sequential EPFL benchmark 未接入（N31-05 设计已落地，pending 用户决定 Stage C 启动）
3. Git remote 未配置（N31-04 设计已落地，pending 用户决定）
4. 论文主图未渲染（pending figure rendering tool）
5. 章节初稿需迁入 `paper/submission/`（待用户审定）

## 7. 处置建议

1. **P0 必须解决**：N31-03 ORFS techmap library（需用户授权）。
2. **P1 顺序**：先解决 METH-12（timing gain 真实化），再做 X19 设计（METH-09 / METH-10）。sequential cone 与 ISCAS85 许可可后续单独处理。
3. **P2 并行**：N31-04 / N31-05 / N31-06 与论文写作（PM30）并行推进。

## 8. 自审结论

FAECO 当前阶段在 P0 CEC limitation 未解决前，可以作为受限的方法+流程工作产出论文（`paper/draft/` 6 章节初稿 + 8-case Stage B 端到端 + 25A/1B 文献边界），但不能在主表或主结论里宣称为"CEC pass 的 failure-aware ECO 方法"。P0 解决后，论文可以升级到"端到端 CEC pass + pre-layout STA"的完整方法学。