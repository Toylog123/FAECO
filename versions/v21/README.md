# 版本 v21 —— 中文 v3 后布局强基线对照与万门级增量绕线定稿基线（2026-11-23）

| 项 | 值 |
|---|---|
| 基线 ID | `v2026-11-23-postroute-baselines-b15` |
| 前置基线 | `v20`（`v2026-11-22-postroute-v3-zh`，历史参照保持不可变） |
| 当前论文（中文 v3） | `paper/zh/manuscript/FAECO_v3_后布局可调预算面积回收.tex`（15 页，6 套 Nature 矢量图，LuaLaTeX 0 Error / 0 Overfull / 0 Undefined） |
| 英文稿状态 | **暂冻**（按指令先只推进中文版本，英文稿保留历史同步点） |

## 本轮新增冻结内容（相对 v20）

1. **源码与测试增强**（55 项单元测试全通过）：
   - `code/src/rseco/physical_budget_adapter.py` 新增 `slack_margins_ps`（联合松弛裕量感知 + 安全驱动排序融合）与 `render_local_incremental_flow_tcl`（局部直连线网增量绕线流程）；
   - `code/tests/test_physical_budget_adapter.py` 新增对应单测验证。
2. **新增核心证据包** `project_docs/evidence/postroute_strong_baselines_20261122/{REPORT.md, SUMMARY.json}`：
   - **全 10 电路四方法强基线对照**：OpenROAD 原生（`0/10`）、固定 SPEF 灵敏度批处理（`5/10` 有效、均降 `0.14%`、最高退化 `-123.44 ps`）、单门在线灵敏度贪心（`9/10`、`s953` 为 `0.00%`）、FAECO 独立闭环（`10/10`、均降 `2.01%`、`b12` 为单门贪心的 `2×`）；
   - **完整 PPA 功耗与 10/10 IO+OCV**：`10/10` 降低总功耗（均 `-0.96%`）与组合功耗（均 `-3.72%`，最高 `-8.26%`），显式 IO+OCV 补齐至 **10/10（100%）** 达标；
   - **万门级 `b15` 突破**：`b12` 局部增量提速 `2.12×`（`52.94 s` vs `112.02 s`）；`b15`（`33,737.36 µm²`、5,494 组件）提速 **`7.7×`**（`184.83 s`、`DRC=0` vs 全芯片重布线 `1426.14 s` 残留 66 DRC），提交 5 门回收 `-0.26%` 面积、`TT +0.068 ps`、`SS +199.996 ps`、`FF hold 0.000 ps`、`leakage -0.84%`、`IO+OCV +0.027 ps`、**全网表 SEC PASS**。
3. **Nature 图件与论文结构重排**：新增 `fig_strong_baselines_zh.pdf`（`audit_pdf_text.py` $\ge 5.8\text{ pt}$、`audit_figure_collisions.py` **0 fail, 0 warn PASS**），并将 §6–§8 顺排为《在线物理闭环、强基线对照与规模突破》→《讨论（含局限）》→《结论》（15 页、页均字数均衡、0 Overfull）。

## 验证命令

```bash
.venv/Scripts/python.exe -m pytest code/tests/test_physical_budget_adapter.py code/tests/test_budgeted_recovery.py code/tests/test_recover_area.py -q
.venv/Scripts/python.exe versions/v21/make_manifest.py
```
