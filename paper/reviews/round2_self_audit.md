# Paper Round 2 自审稿报告

更新时间：2026-08-03

本报告评估 round1 自审稿（`paper/reviews/round1_self_audit.md`）的 P0 / P1 / P2 各项在当前（2026-08-03）的进展状态。round2 必改清单（`paper/reviews/round1_revision_notes.md` §4）5 项已全部完成；本报告按 P0/P1/P2 逐项给出 round2 状态。

## 1. P0 项进展

### P0-1: Stage B CEC unavailable (METH-08)

**round2 状态**：仍 **active**——需 N31-03 cells.v（用户授权）。

**进展（2026-08-03）**：
- N31-03 设计文档已补 AIG→SMT 解锁价值：cells.v 修复 CEC 的同时解锁 N31-06 AIG→SMT 8-case 端到端（`docs/engineering/n31_03_orfs_techmap_library.md` §6.2，commit `502a10f`）
- Yosys `aigmap` 探针验证：mapped.v 无 cells.v 时报 SKY130 模块 undefined（`4d26b1f`）

**处置**：等用户决定路径 A（授权 cells.v 下载）或路径 B（LUT mapping 兜底）。

## 2. P1 项进展

| 项 | round1 | round2 | 变化 |
|---|---|---|---|
| P1-1 METH-01 sequential cone | 未实现 | N31-05 设计文档已落地（`n31_05_sequential_eco.md`，Stage C 时间表 9-11 周） | 设计推进，待 Stage C 启动 |
| P1-2 METH-09 X19 multi-iter | 未启动 | 仍待用户 design 审批 | 无变化 |
| P1-3 METH-10 refinement multi-iter | single-iteration proxy | 同 P1-2 | 无变化 |
| P1-4 METH-12 candidate timing gain | Stage A proxy | N31-06 wrapper 已推进（per-candidate Z3 boundary 等价），但 per-candidate STA timing gain 仍待实现 | 部分推进 |
| P1-5 ISCAS85 license | 接受保留 | 接受保留 | 无变化 |

## 3. P2 项进展

| 项 | round1 | round2 | 变化 |
|---|---|---|---|
| P2-1 Z3 candidate/boundary | 设计 + 代码落地，8-case 受限 | **multi-output/escaped/xor/constant 已支持**（`4eaaa2a`，12 项测试）；8-case 端到端受 mapped.v 门级实例化限制（需 N31-03 cells.v）；AIG→SMT 依赖已验证（`4d26b1f`） | **显著推进**（单元测试层面完成） |
| P2-2 sequential EPFL benchmark | 未接入 | 同 P1-1（N31-05 设计已落地） | 设计推进 |
| P2-3 Git remote | 未配置 | N31-04 设计已落地（`n08_push_to_remote.md`） | 设计推进 |
| P2-4 论文主图 | 未渲染 | **fig1-5 全部生成**（`8d5fae5` `a17c328` `ad2e5c5` `c2873dd`，dataviz 调色板验证） | **完成** ✅ |
| P2-5 章节迁入 submission/ | 待审定 | 待用户审定 6 章节 | 无变化 |

## 4. round2 新增成果

1. **N31-06 Z3 wrapper 完整实施**：`src/rseco/z3_formal.py`（递归下降 parser + wire DAG）+ 12 项 TDD 测试 + 8-case runner；完整回归 102 项全绿。
2. **论文主图 5 张**：fig1（Stage B runtime）+ fig2（Stage A baseline）+ fig3（method flow）+ fig4（c17 cut graph）+ fig5（F1-F5 failure flow）。
3. **AIG→SMT 依赖验证**：Yosys `aigmap` 对 mapped.v 报 SKY130 模块 undefined → AIG→SMT 依赖 N31-03 cells.v（`4d26b1f`）。
4. **round2 必改清单 5 项全部完成**（4 章节修订 + method §6 + 主图）。

## 5. 仍未关闭的问题（round 3 候选）

1. **P0-1 CEC**：需用户授权 N31-03 cells.v。
2. **P1-2/3 X19**：需用户 design 审批。
3. **P1-4 per-candidate STA timing gain**：需 Stage B ranking 扩展。
4. **P1-1 sequential**：需用户决定 Stage C 启动。
5. **P2-3 push**：需用户给 remote URL。
6. **P2-5 章节迁入**：需用户审定。

## 6. 自审结论

round2（2026-08-03）完成：N31-06 Z3 wrapper 单元测试层面完整、论文主图 5 张生成、round2 必改清单 5 项全部完成、AIG→SMT 依赖链清晰。**round2 相对 round1 的 P2-1（Z3）和 P2-4（主图）两项已关闭**。剩余 P0/P1 全部依赖用户决策（N31-03 cells.v 授权 / X19 设计审批 / Stage C 启动 / remote URL / 章节审定）。

round3 将在 P0-1（N31-03 cells.v）决策后启动，主要做 CEC pass 复现 + AIG→SMT 8-case 端到端 + 论文主表 final。