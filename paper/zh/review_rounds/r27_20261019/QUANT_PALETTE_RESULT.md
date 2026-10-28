# r27 黑白灰量化图配色统一验收

用户最新“黑白灰配色”取代此前蓝灰方案。7个唯一量化图复用已验收Python最终绘图源，仅替换颜色与输出目录；未运行EDA。所有旧图、旧脚本及已有CSV保持原字节，蓝灰包保留为superseded。

| 图 | 旧→黑白灰新副本 | 数据/绘图逻辑 | 碰撞FAIL/WARN | 字符位置最大变化 |
|---|---|---|---|---|
| r24_cp_gain_cost | paper\zh\figures\data\final\r24_cp_gain_cost\r24_cp_gain_cost.pdf → paper\zh\figures\data\final\r27_monochrome\r24_cp_gain_cost\r24_cp_gain_cost.pdf | CSV逐SHA一致；科学绘图函数忽略颜色后AST相同 | 0/0 | 0.09034 pt |
| r24_cp_budget_curves | paper\zh\figures\data\final\r24_cp_budget_curves\r24_cp_budget_curves.pdf → paper\zh\figures\data\final\r27_monochrome\r24_cp_budget_curves\r24_cp_budget_curves.pdf | CSV逐SHA一致；科学绘图函数忽略颜色后AST相同 | 0/0 | 0.42676 pt |
| r24_unified_status | paper\zh\figures\data\final\r24_unified_status\fig4_r24.pdf → paper\zh\figures\data\final\r27_monochrome\r24_unified_status\fig4_r24.pdf | CSV逐SHA一致；科学绘图函数忽略颜色后AST相同 | 0/2 | 0.82237 pt |
| fig5_budget_curves_r21 | paper/zh/figures/data/final/fig5_budget_curves_r21.pdf → paper\zh\figures\data\final\r27_monochrome\fig5_budget_curves_r21\fig5_budget_curves_r21.pdf | CSV逐SHA一致；科学绘图函数忽略颜色后AST相同 | 0/0 | 0.00000 pt |
| fig6_physical_transfer_r21 | paper/zh/figures/data/final/fig6_physical_transfer_r21.pdf → paper\zh\figures\data\final\r27_monochrome\fig6_physical_transfer_r21\fig6_physical_transfer_r21.pdf | CSV逐SHA一致；科学绘图函数忽略颜色后AST相同 | 0/1 | 0.00000 pt |
| fig7_s_boundary_r21 | paper/zh/figures/data/final/fig7_s_boundary_r21.pdf → paper\zh\figures\data\final\r27_monochrome\fig7_s_boundary_r21\fig7_s_boundary_r21.pdf | CSV逐SHA一致；科学绘图函数忽略颜色后AST相同 | 0/2 | 0.00000 pt |
| fig_iscas89 | paper/zh/figures/fig_iscas89.pdf → paper\zh\figures\data\final\r27_monochrome\fig_iscas89\fig_iscas89.pdf | CSV逐SHA一致；科学绘图函数忽略颜色后AST相同 | 0/0 | 1.47052 pt |

## 颜色、数据与视觉核查

- 7图PDF原始绘画操作数、嵌入栅格及Matplotlib原生导出PNG均中性；未出现真实彩色操作数。7图关闭MuPDF ICC后的RGB渲染最大通道差均0，所有native PNG也均0。默认MuPDF ICC对合法DeviceGray会产生最多1/255的RGB通道舍入差，原值单列记录，不归为彩色源。没有后处理图像像素。
- 10对已有CSV逐SHA完全一致；ISCAS额外生成的源表也与先前蓝灰副本逐SHA一致。每个图与旧源/旧PDF和新源均绑定SHA。
- 已实际查看全部7张最终PDF渲染及全部面板：黑白灰曲线的线型、标记、线宽、空实心及热图数值仍可辨认；原始标记与线型未修改。热图原有连续数值映射保留，仅改灰阶色图。
- 所有最终PDF：源码预检、字形底线5 pt、碰撞工具退出码0；5个多面板图（2/8/3/8/2面板）对齐均PASS，两个单面板N/A。

## 保留的边界

- r24热图/曲线/统一结果图的字符边界最大浮动为0.09034/0.42676/0.82237 pt；热图位图边界另约0.02 pt舍入。ISCAS旧tight_layout重算导致最大字符位置差1.47052 pt、页面裁切差1.23312 pt。不称几何bitwise一致。
- 原fig6/fig7/ISCAS辅助网格穿字的无色修复原样继承，未再改动曲线、数据柱、候选、文本、坐标、线型和标记；早前iteration01与蓝灰包均保留。
- 最终共5个fill-edge WARN已实看：统一图+2.75/+1.13跨白色axes边界；physical的+0.00标签盒临近另一柱；S图低计数2/0被抽取器合并为20及1标签盒接近小柱。实际字形均完整且分离；各图PALETTE_QA列出解释。
- 仅量化图配色验收，不等于科学未决事项关闭或投稿格式准入。

运行：QUANT_MONOCHROME_PREPARE.json、QUANT_MONOCHROME_BUILD_RUNS.json、QUANT_MONOCHROME_COLOR_AUDIT.json；异常归因见QUANT_MONOCHROME_RUN_NOTES.md。每图含PDF/SVG/PNG、数据CSV、plotter_snapshot、对齐/字形/碰撞/原件比较与PALETTE_QA.json。
