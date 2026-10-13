# 版本 v16 —— 图 2 机制图替换（r18：用户指定换图，零 .tex 改动）

| 项 | 值 |
|---|---|
| 提交 | **`v16 双 tag 所指提交`**（r18 单一提交：图件 + 双副本 PDF + 台账 + 交接层；`git rev-parse v2026-10-13-fig2-update-r18^{commit}` 可验。**v16 未推送 origin**，与 r11–r17 先例一致） |
| tag | `v2026-10-13-fig2-update-r18`（版本 tag）、`faeco-paper-final-20261013g`（论文 tag） |
| 远端 | **尚未推送 origin**（v11 + v12 + v13 + v14 + v15 + v16 均未上远端；`origin/main` = `b1403d9`。等待用户「推送」指令） |
| 前置 | v15 = 提交 `49aa835`，tag `v2026-10-13-logic-calibration-r17` / `faeco-paper-final-20261013f` |
| 触发 | 用户指令：**「用这个图片替换图2」**（新图 `违例扇入锥与候选融合排序示意图.png`，1,254×1,254） |
| 论文中文题 | **FAECO：面向预布局门级时序 ECO 的候选探索与失效刻画**（未变） |
| 论文英文题 | **FAECO: Candidate Exploration and Failure Characterization for Pre-Placement Gate-Level Timing ECO**（未变） |
| 论文 `.tex` | `5775eb516ea74d2f23f7366554bd537d8a9bafe77eb584ea74bf8b71a07c05b7`（61,801 B；**668 CRLF / 0 裸 LF / 0 `\r\r\n`**）—— **与 v15 逐字节相同（本轮零 `.tex` 改动）** |
| 双副本 PDF 字节 SHA256 | `05ee4ec01474510768d80d167eb62a0162f09919a3912f7e4e75e472ab7498fb`（**2,604,856 B**，两处一致；v15 为 `b1d6e5a2…` / 2,769,586 B） |
| 内容指纹（poppler 25.07） | `c5fa3f26c064904e7f43e6e5f1c59e70c9f0de372b0047aa5978168903560f0f`（**与 v15 相同**，见「本轮特性」） |
| 页数 / 质检 | **10 页**（不变） / `Errors 0 · Overfull hbox 0 · Underfull hbox 0 · Overfull vbox 0`、`undefined` 5（全部为字体替身警告）、`??` = 0 |
| 引用覆盖 | 表 14 + 图 3 = **17/17 均被正文 `\ref`**（`scratch/check_env_refs.py` → 未被引用的表/图: 无） |
| 浮动体顺序 | 表 1..14、图 1..3 严格递增（`scratch/float_order_probe2.py` → ALL OK） |
| 图 2 落点 | 第 5 页（figure* 通栏），渲染正常 |
| 摘要篇幅 | **未变**（CN 345 汉字 / EN 203 词，同 v15） |
| manifest | `versions/v16/MANIFEST.sha256` **117 条**，`sha256sum -c` 全 OK；**相对 v15 恰 2 条变化**（双副本 `.pdf`），`.tex` 及 114 条源码/实验未变；**LF 行尾** |
| 归档 | `paper/zh/review_rounds/r18_20261013/`（含 `README.md` / `figure_before.png` = v15 图 2 / `figure_after.png` = v16 图 2） |
| 方案 | `project_docs/planning/FAECO_R18_FIG2_REPLACE_PLAN_20261013.md` |

## 变更明细（图件，零正文改动）

| 项 | v15 | v16 |
|---|---|---|
| `paper/zh/figures/fig_cut_generation_mechanism_imagegen.png` | 1,251,525 B，sha256 `a3b53e80…` | **1,152,805 B**，sha256 `67af5ce4…` |
| 尺寸 | 1,254 × 1,254 | **1,254 × 1,254**（1:1 不变 ⇒ 版式零位移） |
| 内容 | 4 面板 (a)–(d) + 底部 R/G/B/JOINT | **新增「候选融合排序」中间层**（依据：cost(v) + 路径覆盖 + 策略优先级）；JOINT 标注改「关键路径**区段**联合」 |
| 源 | ImageGen 直出 PNG | 用户剪贴板 JPG（`.venv` Pillow 12.3 无损转 PNG，RGB） |
| `.tex` / 图注 / 图表编号 | — | **全部不变**（沿用同名文件，`\includegraphics` 与 caption 无需改） |

## 本轮特性（重要）

1. **文本层零变化 ⇒ 内容指纹不变**：`pdftotext -layout` 只抽文本层，换图为栅格图不影响之，故 v16 内容指纹 = v15（`c5fa3f26…`）。**本轮的变更证据 = PDF 字节 SHA + git 二进制 diff**，不能再依赖文本指纹判「内容是否变化」。
2. **manifest 仅 2 行变化**：`figures/` 不在 manifest 覆盖内（**OI-025**），且 `.tex` 未变，故 v16 相对 v15 仅双副本 PDF 两行变化。

## 不改清单（明确保留）

| 项 | 理由 |
|---|---|
| `.tex`（正文 / 摘要 / 图注 / 图表编号 / 参考文献） | 本轮仅换图件；用户未要求改文字 |
| 图 2 图注「FAECO 候选构造与排序机制：…」 | 已覆盖「候选融合排序」语义，无需改写 |
| 其余 2 张图（图 1 方法流程、图 3 ISCAS-89） | 未在请求范围内 |
| r12 M1/M2/M3 表注、PicoRV32 分母说明、负结果本体、r6 P0「其余无退化」 | 既有裁定载体 / 证据本身（同 r14–r17） |
| 「控制」12 处、「门尺寸调整」等域内术语 | r16/r17 已裁定保留 |

## 与用户意见的偏离 / 需用户确认项

1. **沿用原文件名而非用户给的中文名**：为免动 `.tex`（也避免破坏 v15 `.tex` 哈希与 manifest 口径），新图落在 `fig_cut_generation_mechanism_imagegen.png`，未新增 `违例扇入锥与候选融合排序示意图.png` 文件。**如希望改用中文名/新 ASCII 名并同步 `\includegraphics`，回退成本 1 行 `.tex`。**
2. **JPG→PNG 转码**：源只有剪贴板 JPG（276,388 B），已用 Pillow 无损转 PNG 保持管线一致；若需保留原始 JPG 以免任何重编码，可改存 `.jpg` 并同步 `\includegraphics` 扩展名。
3. **图注未动**：新图新增「候选融合排序」中间层，图注现文案未逐项点出该层（表述为「候选构造与排序机制」）。如需在图注中显式点出「候选融合排序」层，可加 1 句。

## 本轮教训（写入 `MEMORY.md`）

1. **纯栅格图变更无法被文本指纹捕获**：`pdftotext` 内容指纹对换图**完全不敏感**；验收换图必须看 **PDF 字节 SHA + 页面渲染**，不能只比对文本指纹。
2. **换图优先保持同尺寸（1:1）**：新旧同为 1,254×1,254 ⇒ 版式零位移、页码 10 不变、无需调 `\FloatBarrier`；若分辨率/比例变化，须重跑版面复核。
