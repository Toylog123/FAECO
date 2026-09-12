# figures — 论文图（分 data/manual 两类）

配图**区分两类**：数据脚本生成图（`data/`）与手工绘制图（`manual/`）。

```text
figures/
├── data/                    # 数据脚本生成图（脚本生成，可复现）
│   ├── scripts/             # 生成脚本（nature-figure）
│   ├── plot_specs/          # 数据说明 + DATA_SOURCE_TEMPLATE（来源/版本/配置）
│   └── final/               # 数据图定稿（PNG，被 .tex 引用）
├── manual/                  # 手工绘制图（用户按提示词绘制）
│   ├── drawing_prompts/     # 机制图设计提示词（结构示意）
│   └── figures/             # 手工图（源 + 草图 + 定稿都在这里）
└── README.md  CHANGE_LOG.md # 说明 + 图片修改记录
```

## 绘图分工

| 图类型 | 归属 | 由谁画 | 方式 |
|--------|------|--------|------|
| 数据图（定量折线图、统计图、曲线） | `data/` | AI 用 `nature-figure` 技能 | 脚本生成，数据来自证据包，**可复现**；每张图填数据来源记录（`data/plot_specs/DATA_SOURCE_TEMPLATE.md`） |
| 机制图（结构图、流程图、硬件图） | `manual/` | **详细设计提示词 → 草图 → 用户手工画** | AI 给含结构示意的提示词（`manual/drawing_prompts/`）+ 草图（`manual/candidates/`），用户按提示词绘制 |

- 命名：`fig<N>_<描述>.png`，与 .tex 中 `\ref` 对应。
- 定稿：数据图 → `data/final/`，手工图 → `manual/figures/`（`.tex` 的 `\graphicspath` 已配置两目录）。

## 数据图格式（默认最清晰）

数据图脚本生成**默认输出最清晰格式**：

- **矢量优先**：SVG / PDF（投稿 / 出版 / 缩放用）。
- **高分辨率位图**：PNG ≥ 300 dpi（论文内嵌用）。
- 脚本默认同时生成矢量 + 高分辨率 PNG；`data/final/` 中保留最清晰版本。
