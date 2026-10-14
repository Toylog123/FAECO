# 图片修改记录

> 记录**每张图的修改**（内容 / 数据 / 样式 / 尺寸），便于回溯与防混淆（版本 / 配置 / 数据来源）。

## 修改记录

| 日期 | 图号 / 名称 | 修改内容 | 原因 / 依据 | 关联（数据来源 / 审稿 / 提交） |
|------|-----------|----------|-------------|-------------------------------|
| YYYY-MM-DD | fig3_xxx | 改了… | 因… | DATA_SOURCE / r1 / commit |

## 规则

1. **每次改图后登记**（图号、修改内容、原因）。
2. 数据图修改：同步数据来源记录（`plot_specs/<figN>_<名称>_data.md`）。
3. 机制图修改：更新提示词（`drawing_prompts/<figN>_<名称>_prompt.md`）。
4. 定稿前核对：图与论文数字一致（交叉表）、数据来自当前版本（非旧版 / 其他配置）。

## 2026-10-14 r21 图件修订

| 图号 | 变化 | 来源与口径 | 导出 |
|---|---|---|---|
| 1 | 迭代提交主循环、可选反馈、独立SEC | §3.2/3.6及算法1 | manual/figures/fig1_iterative_flow_r21.* |
| 2 | 六门锥与12节点分裂图、out→in依赖、wi容量 | cut.py构造及覆盖分支；构造示例 | manual/figures/fig2_candidate_mechanism_r21.* |
| 4 | B族所有可评估实例，零收益与N/A保留 | 20260826_aggregation/summary.json | data/final/fig4_unified_gain_r21.* |
| 5 | 40运行按真实新STA重建B(k)，所有种子及终点 | D族eval_trials，剔cache/前置拒绝 | data/final/fig5_budget_curves_r21.* |
| 6 | 理想线网→全局布线收益成对比较，保留退化 | A/A′同候选8电路 | data/final/fig6_physical_transfer_r21.* |
| 7 | 深度与WNS独立分类，零候选s641保留 | F族126个候选、8电路 | data/final/fig7_s_boundary_r21.* |

脚本 `data/scripts/review_r21_figures.py`，契约及输入指纹 `data/plot_specs/r21_*`。旧图源保留；新图PDF/SVG可编辑、PNG600 dpi。图1/2/4/5宽170 mm，图6宽80 mm×68 mm，图7宽80 mm×94 mm；实际字形≥7 pt（单栏缩放约6.95 pt）。所有数据图带CSV。40台账重算、源预检、PDF字形审计及整稿逐页验收见r21归档，不新增EDA。


## 2026-10-14 r22英文适配与暂停状态

英文7图已保存paper/en/figures，矢量源/PDF/PNG/CSV及来源、字形QA齐备；沿用既有结果，不含有效新C′数据。新增历史correctness审计影响A/D/C相关图表科学解释，需恢复后复验再同步中英图表；目前仅保存工作初稿，不视作投稿定稿。
