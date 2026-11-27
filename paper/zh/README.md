# paper/zh — FAECO 中文论文目录（2026-11-22 整理版）

当前专注于**中文论文 v3（后布局可调预算与独立面积回收）**，英文工作稿暂冻在 `paper/en/`。

## 一、目录结构

| 路径 | 角色 | 状态 |
|---|---|---|
| `manuscript/FAECO_v3_后布局可调预算面积回收.tex` | **当前唯一活跃中文主稿**（ctexart 双栏，第八轮机制图修订 12 页、6 图、7 表） | 活跃 |
| `FAECO_v3_后布局可调预算面积回收.pdf` | 顶层交付 PDF（与 `manuscript/`、`build/` 同名 PDF 逐字节同步） | 活跃 |
| `manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex` | v1/v2 预布局中文主稿（对应冻结基线 `v19`） | 历史归档 |
| `manuscript/FAECO_R7_补充材料.tex/pdf` | 第七轮随稿补充材料，附录 A–G | 活跃 |
| `manuscript/FAECO_R6_补充材料.tex/pdf` | 第六轮随稿补充材料 | 历史归档 |
| `manuscript/FAECO_补充材料.tex` | v1/v2 预布局中文补充材料 | 历史归档 |
| `build/` | 洁净编译产物目录（仅保留活跃 v3 与归档 v2/补充 PDF，不含过程日志与临时 PNG） | 活跃 |
| `figures/` | 矢量图源（`*.pdf`、`*.svg`）与生成器（`gen_v3_figures.py` 等）；QA 栅格图与对齐 JSON 统一置于 `figures/qa_previews/` | 活跃 |
| `archives/` | 历史轮次备份、旧编译日志（`build_legacy_20261122/`）、早期 Round5 草稿与旧审稿纪录（`manuscript_legacy_20261122/`） | 归档 |
| `review_rounds/`、`responses/`、`submission/` | 各轮审稿记录、回复与期刊格式清单 | 归档/参考 |
| `scripts/` | 编译脚本与 LaTeX 质量门检查 | 工具 |
| `CHANGE_LOG.md` | 中文论文修改流水记录 | 持续维护 |

## 二、现行中文 v3 编译与验收命令

必须在 `paper/zh/manuscript/` 下使用 `lualatex` 连续编译两遍（保证交叉引用与字体路径 `./fonts/` 正确）：

```powershell
cd paper/zh/manuscript
lualatex -interaction=nonstopmode "FAECO_v3_后布局可调预算面积回收.tex"
lualatex -interaction=nonstopmode "FAECO_v3_后布局可调预算面积回收.tex"
Copy-Item "FAECO_v3_后布局可调预算面积回收.pdf" "../FAECO_v3_后布局可调预算面积回收.pdf" -Force
Copy-Item "FAECO_v3_后布局可调预算面积回收.pdf" "../build/FAECO_v3_后布局可调预算面积回收.pdf" -Force
```

若需清理 `manuscript/` 下编译产生的临时 `.aux`/`.log`/`.out`，请移至 `paper/zh/archives/` 或在确认无追踪冲突后再清理，以保持源码目录整洁。

## 三、图表重绘与质检入口

第八轮新增 [窗口覆盖图源](figures/tcad_20261126/fig2_window_context_r8.tex) 与 [搜索机制图源](figures/tcad_20261126/fig4_nonmonotone_search_r8.tex)。原四幅图沿用 [R7 图件说明](figures/tcad_20261126/R7_FIGURE_NOTES.md)，正文图号为 1、3、5、6。独立补充材料可在 `manuscript/` 内选中 `FAECO_R7_补充材料.tex` 单独编译。发布工件及散列见[清单](review_rounds/r20261127_r8_mechanism/R8_RELEASE_MANIFEST.json)。

## 四、写作与数字核对规范

- **数字逐证据包核对**：每项面积、WNS、hold、TNS、用时及 SEC 读取对应端点和配置的原始或核验收据。入口包括 [历史回收](../../project_docs/evidence/postroute_recovery_20261120/REPORT.md)、[SKY130 四场景](../../project_docs/evidence/sky130_joint_constraints_20261123/REPORT.md)、[SKY130HD AES 交叉对照](../../project_docs/evidence/tcad_ibex_20261123/AES_FACTORIAL_REPORT.md)及 [ASAP7 Ibex 反序复跑](../../project_docs/evidence/tcad_ibex_20261123/ASAP7_SERIAL_REPORT.md)。
- **去工程化学术风格**：正文与图注统一使用算法/方法论术语，不引入 `.py` 文件名、Python 函数名、命令行选项或工程 issue 编号。
- **修改留痕**：每次修改 `.tex` 或 `figures/`，同步更新 `paper/zh/CHANGE_LOG.md` 与 `project_docs/LOGS.md`。
