# Paper Figures (占位)

更新时间：2026-07-31

论文主图占位目录。当前所有图均未生成，只有占位说明；后续 N05/N08 阶段根据 `experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.md` 和 `experiments/20260718_minimal_combinational_batch_demo/tables/baseline_comparison.md` 渲染。

## 占位列表

| 图号 | 内容 | 数据来源 | 状态 |
|---|---|---|---|
| 图 1 | FAECO 三阶段流水线流程图（Resynthesis / Cut & Refine / Verify & STA） | `paper/draft/method.md` §1 | pending（method chapter 获批后） |
| 图 2 | Stage A 5-case multi-baseline comparison bar chart（patch size × 6 baselines） | `experiments/20260718_minimal_combinational_batch_demo/tables/baseline_comparison.md` | pending |
| 图 3 | Stage B 8-case mapping + STA 时间 bar chart（mapping_s / sta_s / total_s） | `experiments/20260731_epfl_8case_stage_b/tables/stage_b_runtime.md` | pending |
| 图 4 | s-t split graph 示例（c17 N22 cone） | `src/rseco/cut.py` synthetic regression test | pending |
| 图 5 | F1-F5 失败分类触发流程图 | `paper/draft/method.md` §6 + `src/rseco/failures.py` | pending |

## 渲染工具

- Markdown → PNG：`md-to-pdf` + `pdf-to-png` 工具链，或 Pandoc + LaTeX
- 表格：直接用 markdown 表格（`stage_b_case_summary.md` + `stage_b_runtime.md`），渲染成 PNG 用 `pandoc -t latex`

## 边界

- 所有图必须可追溯到 `experiments/` 下原始 `tables/*.json`，禁止生成不存在的数据
- Stage B 8-case limitation（CEC unavailable / slack=null）必须明确标注在图标题或图注
- [F08-B] DAC 2018 和 [B06] BUFFALO 数据禁止引用到图