# r27量化图配色统一验收

7个唯一量化图复用已验收Python绘图逻辑；未运行EDA。所有旧图、旧脚本及已有CSV保持原字节，新图另存。

| 图 | 旧→新 | 数据/绘图逻辑 | 碰撞FAIL/WARN | 字符位置最大变化 |
|---|---|---|---|---|
| r24_cp_gain_cost | paper\zh\figures\data\final\r24_cp_gain_cost\r24_cp_gain_cost.pdf → paper\zh\figures\data\final\r27_palette\r24_cp_gain_cost\r24_cp_gain_cost.pdf | CSV逐SHA一致；科学绘图函数忽略颜色后AST相同 | 0/0 | 0.09034 pt |
| r24_cp_budget_curves | paper\zh\figures\data\final\r24_cp_budget_curves\r24_cp_budget_curves.pdf → paper\zh\figures\data\final\r27_palette\r24_cp_budget_curves\r24_cp_budget_curves.pdf | CSV逐SHA一致；科学绘图函数忽略颜色后AST相同 | 0/0 | 0.42676 pt |
| r24_unified_status | paper\zh\figures\data\final\r24_unified_status\fig4_r24.pdf → paper\zh\figures\data\final\r27_palette\r24_unified_status\fig4_r24.pdf | CSV逐SHA一致；科学绘图函数忽略颜色后AST相同 | 0/2 | 0.82237 pt |
| fig5_budget_curves_r21 | paper/zh/figures/data/final/fig5_budget_curves_r21.pdf → paper\zh\figures\data\final\r27_palette\fig5_budget_curves_r21\fig5_budget_curves_r21.pdf | CSV逐SHA一致；科学绘图函数忽略颜色后AST相同 | 0/0 | 0.00000 pt |
| fig6_physical_transfer_r21 | paper/zh/figures/data/final/fig6_physical_transfer_r21.pdf → paper\zh\figures\data\final\r27_palette\fig6_physical_transfer_r21\fig6_physical_transfer_r21.pdf | CSV逐SHA一致；科学绘图函数忽略颜色后AST相同 | 0/1 | 0.00000 pt |
| fig7_s_boundary_r21 | paper/zh/figures/data/final/fig7_s_boundary_r21.pdf → paper\zh\figures\data\final\r27_palette\fig7_s_boundary_r21\fig7_s_boundary_r21.pdf | CSV逐SHA一致；科学绘图函数忽略颜色后AST相同 | 0/2 | 0.00000 pt |
| fig_iscas89 | paper/zh/figures/fig_iscas89.pdf → paper\zh\figures\data\final\r27_palette\fig_iscas89\fig_iscas89.pdf | CSV逐SHA一致；科学绘图函数忽略颜色后AST相同 | 0/0 | 1.47052 pt |

## 边界与修复

- r24热图/曲线/统一结果图的字符边界最大浮动为0.09034/0.42676/0.82237 pt；热图位图边界另约0.02 pt舍入。ISCAS旧tight_layout重算导致最大字符位置差1.47052 pt、页面裁切差1.23312 pt。不称几何bitwise一致。
- 原fig6/fig7/ISCAS存在浅网格穿数字；在新副本将辅助网格设为无色，ISCAS零参考线同处理。没有改动曲线/数据柱/候选/文本/坐标/线型/标记，旧iteration01保留。
- 所有最终PDF：源码预检、字形底线5 pt、碰撞工具退出码0；5个多面板图（2/8/3/8/2面板）对齐均PASS，两个单面板N/A。
- 最终共5个fill-edge WARN已实看：统一图+2.75/+1.13跨白色axes边界；physical的+0.00标签盒临近另一柱；S图低计数2/0被抽取器合并为20及1标签盒接近小柱。实际字形均完整且分离；各图PALETTE_QA列出解释。
- 数据原文件字节一致并不代表历史科学问题关闭；本轮只更换配色。没有新增统计结论或投稿验收。

生成命令、每图90 s超时及实际耗时见QUANT_BUILD_RUNS.json；仅三图修复命令见QUANT_REPAIR_RUNS.json。每图包含PDF/SVG/PNG、数据CSV、plotter_snapshot、对齐/字形/碰撞/原件比较与PALETTE_QA.json。
