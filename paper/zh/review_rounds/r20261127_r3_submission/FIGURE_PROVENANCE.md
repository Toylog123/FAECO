# 第三轮图 1–2 图像生成与核验

2026-11-27。按作者指示用 Codex 内置 OpenAI 图像生成工具制作两张非数据示意，并在稿件致谢注明用途。图 3–5 的数据绘制由原脚本与源资产承接。

| 图 | 文件 | 读图核验 |
| --- | --- | --- |
| 1 | [流程](../../figures/tcad_20261126/fig1_framework_imagegen_r3.png) | 六个状态按冻结参考、候选池、限时调度、局部后端、验收、检查点排列。虚线由验收节点返回调度器。PDF 绘制约 331 ppi。 |
| 2 | [窗口诊断与重布线](../../figures/tcad_20261126/fig2_boxed_drc_imagegen_r3.png) | 黑色直连线、灰色邻线、请求窗口及短路标记可辨，右图两根线互不相交。窗口与实例尺寸是图示，四向一行高以正文定义为准。PDF 绘制约 396 ppi。 |

两张 PNG 均为 2172 × 724 像素，保存模型原件；TeX 仅裁切外边缘空白。一次图 2 改稿因右图两网碰接而弃用。正式稿不从插图读出几何距离或测量刻度。

## 所用提示词 1


Create Fig. 1, a publication-quality IEEE EDA paper diagram. Generate an extremely wide and compact grayscale workflow strip on pure white paper. Use a single horizontal row of exactly six thin, sharp rectangular boxes, linked only with five straight black right arrows between their side centers. Center the strip vertically in the image with broad plain white space above and below so that we can crop it to a ~7:1 strip. Each box must have ONLY its exact English title on two lines, in spacious large highly legible neutral sans serif. Exact labels left to right: "Frozen routed
reference"; "Candidate
pool"; "Budgeted
scheduler"; "Local DRC and
protected routing"; "Physical, STA,
and SEC checks"; "Verified
checkpoint". New lines are real linebreaks, no visible slash, title spelling exact. There is one subordinate and thin dashed feedback route below the boxes starting at the bottom of box 5, running left beneath box 4 and turning upward, with arrowhead entering the bottom of box 3. No label on feedback. All edges thin and crisp but dark enough at 17 cm print width. White or 5% gray box fills, black text and arrows. This is a flat 2D technical flowchart without any icons, no title or caption, no shadows, no borders around full image, no colors, no textures, no branding, no extra boxes or arrows.


## 所用提示词 2


Generate Fig. 2, a highly simplified grayscale top-view routing mechanism schematic for a two-column IEEE EDA manuscript. Wide canvas, three equally sized black-outline technical mini-panels horizontally, labeled only (a), (b), (c) in clear black sans-serif just above the top left of every panel. Preserve ample flat pure white outer margins for cropping. Use diagrammatic flat black and gray orthogonal strokes on white, no perspective. It is the same single standard-cell location in three states, match exact relative positions. In each panel draw a light-gray rectangular target cell at lower middle and a tiny dark pin on its top edge. In (a) the outlined cell is wider, top pin slightly left of center; a dark thick L-shaped signal line from this pin bends left to leave the region. A second independent gray thin horizontal neighboring wire crosses left to right above the cell with visible white clearance from the L-shaped signal. In (b) the target cell shrinks in width keeping its left edge, and its new pin is on top near center; the old direct signal wire is absent; the same thin horizontal neighbor at the same position now intersects the new dark tab pin once. Show a dashed rectangular query window around the cell with uniform expansion on every side and a small hollow diamond directly at the single intersection. In (c) exactly the same small cell and pin as in (b). Restore the dark thick direct signal from the pin by bending it down then left, and locally detour the independent thin gray neighbor in an upward inverted U over the pin, keeping its two far-left and far-right portions unchanged horizontally. Make two complete continuous electrically separate wire paths with visible white clearance. Draw the same dashed window in (b) and (c) with no additional boxes. Schematic spatial relationships take precedence over decoration. Keep visual order protected neighbor and target on separate nets. No arrow glyphs, no legend, no legend text, no units, no layer name, no letter labels beyond (a), (b), (c); exact details will be explained in the LaTeX caption. Dashes are a crisp technical outline, never confused with either solid wire. Polished spare engineering figure, moderate line weights, black/white/light gray only.
