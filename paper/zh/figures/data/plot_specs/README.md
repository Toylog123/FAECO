# 定量图绘制说明

本目录保存论文中**定量折线图**的绘制说明与数据规格。系统结构图和流程图由 draw.io 绘制（见 `figures/sources/`）；定量折线图由 Python 脚本生成，以保证数据点、坐标轴和输出文件可复现。

结构：

- `*.txt` / `*.md`：每张定量图的说明（数据来源、坐标轴、线型 / 配色约定、输出路径）。
- `DATA_SOURCE_TEMPLATE.md`：**图表数据来源记录模板**（每张数据图一份，写清来源 / 版本 / 配置，防弄混）。
- `README.md`：本说明。

生成命令示例：

```powershell
python paper/zh/figures/scripts/generate_plots.py
```

输出到 `paper/zh/figures/data/final/`。

约定：

- **数据来源必须记录**：每张数据图填 `DATA_SOURCE_TEMPLATE.md`（数据文件、基线 / 版本、配置、口径），放 `plot_specs/<figN>_<名称>_data.md`——防止弄混版本 / 配置。
- 数据必须来自 `project_docs/evidence/` 中的证据包，脚本内注释注明来源路径。
- 配置变更时**新建记录**，不覆盖旧数据来源。
- 黑白灰配色 + 线型 / marker 区分数据系列，适配论文线稿风格与黑白打印。
