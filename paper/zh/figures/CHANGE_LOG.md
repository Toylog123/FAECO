# 图片修改记录

> 记录**每张图的修改**（内容 / 数据 / 样式 / 尺寸），便于回溯与防混淆（版本 / 配置 / 数据来源）。

## 修改记录

### 2026-10-18 r22 全72矩阵与配对差图完成

`data/previews/r22_matrix_gain_cost_v3/` 为当前审查预览：全72个WNS收益/实际STA点与64项同电路配对差，原始CSV、编辑型PDF/SVG、600dpi PNG及中英图注齐备。v1独立核对72行、64对及16组所有同状态重复轮5454次交叉比较均一致；没有观察到独立权重收益。s27随机UR3少5次STA、s641仅覆盖少8次等不利点保留。

新增PDF碰撞门后，v1实测6处斜排tick边界重叠；v2试竖排、v3把渲染前对齐检查纳入生成器。旧版不覆盖，v3两CSV与v1字节相同，实际PDF对齐PASS、碰撞0FAIL/0WARN、最小字体6.8pt，源预检19PASS/2WARN/0FAIL，51项不完整输入实拒绝且不建输出目录。实际四panel/整图已查看；170×128mm为项目图幅，PNG为预览，两源预警不冒称期刊验收。主稿科学整合仍待其他族复验。

### 2026-10-16 r22 预试验收益—STA代价预览

新增 `data/scripts/review_r22_pilot_cost.py` 与 `data/plot_specs/r22_pilot_cost_contract.json`。输入为独立验收的18项 C′ 两电路预试验，九臂全部保留；横轴计候选理想线网STA加初始基线，纵轴计相对同一初始网表的WNS收益（ps）。重合坐标合列所有策略名，不抖动、不平均、不混入历史C/D。v1标签碰撞保留原件，v2修正并通过双panel人工复核、源预检0FAIL、PDF29文本运行最小7pt；导出CSV/PDF/SVG/600dpiPNG到 `data/previews/r22_pilot_cost_v2/`。完整八电路矩阵仍在运行，本图及中英图注草稿尚未写入正文，也未覆盖正式r21图。

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

## 2026-10-16 r22 全矩阵配图准备

新增 `data/plot_specs/r22_matrix_gain_cost_contract.json` 与 `data/scripts/review_r22_matrix_gain_cost.py`，计划展示全部72项增益/实际STA调用和64项同电路配对差，随机种子分开保留。来源与排序对照保持同族，不用C′覆盖旧C/D/B3或物理/S结果。实际以24项审计负控调用，工具在建输出目录之前拒绝；收据为 `scratch/r22_matrix_plot_incomplete_guard.json`。全72验收前不绘制全矩阵、不插入正文；当前仅准备完成，最终导出和视觉QA待真实完整数据。


## 2026-10-16 r22 图4图注周期纠错

中英图4图注补PicoRV32主核/乘法器/regs的5/2/0.5 ns实际周期；原图PDF/SVG/PNG与数值CSV不变。与中英实验设置同步，来源为r22逐Tcl审计，编辑/编译/视觉记录见 `paper/zh/review_rounds/r22_20261016/metadata_correction_01/`。此为图注元数据纠错，不是重新测量或重新生成图4数据。
