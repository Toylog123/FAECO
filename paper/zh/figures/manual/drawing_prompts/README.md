# 手工绘图提示词

本目录保存**手工绘制图**（系统结构图、数据通路图、硬件结构图等）的**详细设计提示词**。

## 要求

- **结构示意，不只是简单流程**：提示词必须包含模块清单、连线与数据流、层次分区、关键接口标注（见 `MECHANISM_FIGURE_PROMPT_TEMPLATE.md`）。
- **论文中先放草图**：复杂机制图在当前稿中用草图 / 占位（`figures/candidates/`）。
- **提示词文件给绘制者**：每个机制图一份提示词文件（`<figN>_<名称>_prompt.md`），最终由用户 / 绘制者按提示词手工绘制。

## 约定

- 提示词按当前中文稿中的图片文件名编写，定稿 PNG 导出到 `paper/zh/figures/manual/figures/`。
- 源文件（draw.io 等）放在 `paper/zh/figures/manual/figures/`。
- 定量折线图由脚本生成（`figures/scripts/`），**不使用**本目录的提示词。
