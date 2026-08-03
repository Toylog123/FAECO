# Paper Tables (占位)

更新时间：2026-07-31

论文主表占位目录。当前所有表均已在 `experiments/` 下生成 markdown 版本，本目录只放占位说明和交叉引用。

## 占位列表

| 表号 | 内容 | 数据来源 | 状态 |
|---|---|---|---|
| 表 1 | Stage A 5-case multi-baseline comparison | `experiments/20260718_minimal_combinational_batch_demo/tables/baseline_comparison.md` | 已落盘 markdown |
| 表 2 | Stage B 8-case per-case mapping + STA summary | `experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.md` | 已落盘 markdown |
| 表 3 | Stage B 8-case runtime breakdown | `experiments/20260731_epfl_8case_stage_b/tables/stage_b_runtime.md` | 已落盘 markdown |
| 表 4 | Stage A 5-case runtime breakdown | `experiments/20260718_minimal_combinational_batch_demo/tables/runtime_breakdown.md` | 已落盘 markdown |
| 表 5 | Stage A 5-case failure recovery proxy | `experiments/20260718_minimal_combinational_batch_demo/tables/failure_recovery.md` | 已落盘 markdown |
| 表 6 | SKY130 HD Liberty 工具链与版本 | `experiments/environment/toolchain_2026-07-30.json` | 已落盘 |
| 表 7 | FAECO 符号表（Method 章节） | `paper/draft/method_symbol_table.md` §1 | pending（method chapter 获批后正式编号） |
| 表 8 | F1-F5 失败分类与反馈动作（Method 章节） | `paper/draft/method.md` §6 | pending |

## 边界

- 所有表必须可追溯到 `experiments/` 下原始 `tables/*.json`
- Stage B 8-case CEC unavailable 必须明确标注
- Stage A 5-case failure_recovery `avg_iterations=1.0` 是 single-iteration proxy，必须明确标注
- [F08-B] DAC 2018 / [B06] BUFFALO 数据禁止引用到表