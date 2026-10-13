# r18 归档 —— 图 2 机制图替换（2026-10-13）

## 指令来源
用户指令：**「用这个图片替换图2」**，附新图 `违例扇入锥与候选融合排序示意图.png`（1,254×1,254，剪贴板 JPG）。

## 内容
| 文件 | 说明 |
|---|---|
| `figure_before.png` | v15 图 2（`fig_cut_generation_mechanism_imagegen.png`，sha256 `a3b53e80…`） |
| `figure_after.png` | v16 图 2（sha256 `67af5ce4…`，源为剪贴板 JPG 经 Pillow 无损转 PNG） |

## 差异要点
- 新版在旧版 4 面板（(a) 违例扇入锥 / (b) s-t 分裂图 K(G,t) / (c) 加权最小割候选 / (d) 关键路径覆盖割候选）基础上，**新增「候选融合排序」中间层**（依据：cost(v) + 路径覆盖 + 策略优先级）。
- JOINT 标注：旧「关键路径联合」→ 新「关键路径**区段**联合」。
- 尺寸 1,254×1,254 不变（1:1），版式零位移；`.tex` 与图注未动。

## 关联产物
- 冻结版本：`versions/v16/`（tag `v2026-10-13-fig2-update-r18` / `faeco-paper-final-20261013g`）
- 方案：`project_docs/planning/FAECO_R18_FIG2_REPLACE_PLAN_20261013.md`
- 双副本 PDF 字节 SHA256：`05ee4ec01474510768d80d167eb62a0162f09919a3912f7e4e75e472ab7498fb`
