# Paper Figures

更新时间：2026-08-03

论文主图目录。当前 2 张实验图已生成（`scripts/make_paper_figures.py`，matplotlib，dataviz 默认 categorical 调色板已验证）。其余图占位待 method chapter 获批后补充。

## 图列表

| 图号 | 文件 | 内容 | 数据来源 | 状态 |
|---|---|---|---|---|
| 图 1 | `fig1_stage_b_runtime.png` | Stage B 8-case mapping + STA runtime 分组柱状图 | `experiments/20260731_epfl_8case_stage_b/tables/stage_b_runtime.md` | **已生成** (2026-08-03, 1162×618) |
| 图 2 | `fig2_stage_a_baseline.png` | Stage A 5-case patch size 按 baseline 方法分组柱状图（fixed/random/size-only/FAECO） | `experiments/20260718_minimal_combinational_batch_demo/tables/baseline_comparison.md` | **已生成** (2026-08-03, 1156×619) |
| 图 3 | `fig3_method_flow.png` | FAECO 三阶段流水线流程图（Resynthesis / Cut & Refine / Verify & STA） | `paper/draft/method.md` §1 | **已生成** (2026-08-03, 1076×515) |
| 图 4 | `fig4_cut_graph.png` | s-t split graph 示例（c17 N22 cone） | `src/rseco/cut.py` synthetic regression test | pending |
| 图 5 | `fig5_failure_flow.png` | F1-F5 失败分类触发流程图 | `paper/draft/method.md` §6 + `src/rseco/failures.py` | pending |

## 渲染命令

```bash
.venv/Scripts/python.exe scripts/make_paper_figures.py
```

## 调色板

图 1/2 用 dataviz 默认 categorical palette（slot 顺序：blue `#2a78d6` / orange `#eb6834` / aqua `#1baf7a` / yellow `#eda100`），已用 `validate_palette.js --mode light` 验证 4 色通过（CVD ΔE ≥ 9.1，normal-vision ≥ 22.9）；aqua/yellow 低于 3:1 对比度，按 relief rule 带直接标签。

## 边界

- 所有图可追溯到 `experiments/` 下原始 `tables/*.json`
- Stage B 8-case limitation（CEC unavailable / slack=null）必须明确标注在图标题或图注
- [F08-B] DAC 2018 / [B06] BUFFALO 数据禁止引用到图

## 渲染工具

- Markdown → PNG：`md-to-pdf` + `pdf-to-png` 工具链，或 Pandoc + LaTeX
- 表格：直接用 markdown 表格（`stage_b_case_summary.md` + `stage_b_runtime.md`），渲染成 PNG 用 `pandoc -t latex`

## 边界

- 所有图必须可追溯到 `experiments/` 下原始 `tables/*.json`，禁止生成不存在的数据
- Stage B 8-case limitation（CEC unavailable / slack=null）必须明确标注在图标题或图注
- [F08-B] DAC 2018 和 [B06] BUFFALO 数据禁止引用到图