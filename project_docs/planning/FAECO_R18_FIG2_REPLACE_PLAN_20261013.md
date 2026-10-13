# FAECO r18 图 2 替换方案（v16 冻结）

日期：2026-10-13
触发：用户指令「用这个图片替换图2」（新图 `违例扇入锥与候选融合排序示意图.png`，1254×1254）

## 1. 背景与目标
- 论文当前处于内容冻结 v15（r17 逻辑一致性精修）。图 2（`fig:cut_generation`）是 §3.1「加权割与候选搜索」的机制总图，源文件 `paper/zh/figures/fig_cut_generation_mechanism_imagegen.png`。
- 用户提供更新版机制图：在旧版 4 面板（(a) 违例扇入锥 / (b) s-t 分裂图 K(G,t) / (c) 加权最小割候选 / (d) 关键路径覆盖割候选）基础上，新增**「候选融合排序」中间层**（依据：cost(v) + 路径覆盖 + 策略优先级），并将 JOINT 标注为「关键路径区段联合」。该增补与 r17 强调的「模块关系清晰化」方向一致。
- 目标：以新图替换旧图 2，不改动正文文字、图表编号与排版。

## 2. 变更内容（仅图件，零 .tex 改动）
- `paper/zh/figures/fig_cut_generation_mechanism_imagegen.png` 字节替换
  - 旧：1,251,525 B（1,254×1,254）sha256 `a3b53e80422f70eace1bffbe875df08d8af26a8a514f31a64d4ba22b282e0904`
  - 新：1,152,805 B（1,254×1,254）sha256 `67af5ce4c917d8c574fbd587d515984a26a6a0c478c1f2bd1e8bd67e59d38304`（源：剪贴板 JPG，经 Pillow 无损转 PNG）
- `.tex` 保持 sha256 `5775eb51…` 不变（沿用同名文件，`\includegraphics` 无需改）
- 图注（caption）不改：现文案「FAECO 候选构造与排序机制…」已覆盖「候选融合排序」

## 3. 判据（验收）
1. 编译 **10 页**（不变）；质量门 Errors / Overfull hbox / Underfull hbox 全 0；`??` = 0
2. 表/图 `\ref` 覆盖 **17/17**；浮动体顺序 **表 1..14 / 图 1..3**
3. 双副本 PDF SHA 一致；图件尺寸 1:1 不变（版式零位移）
4. 图 2 实际落在第 5 页，渲染正常

## 4. 已知限制
- `pdftotext -layout` 内容指纹（仅文本层）**不变**（`c5fa3f26…`）：换图不影响文本层；图件变更由 **PDF 字节 SHA + git 二进制 diff** 记录，不再由文本指纹体现。
- **OI-025**：`figures/` 不在 manifest 覆盖内，故 v16 manifest 相较 v15 仅 **2 行 PDF** 变化（`.tex` 未变）。
