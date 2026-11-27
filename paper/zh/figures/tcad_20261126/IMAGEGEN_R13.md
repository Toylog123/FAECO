# FAECO 方法图 ImageGen 生成与核验

2026-11-27。使用 Codex 内置 OpenAI ImageGen 生成和修正三幅方法示意。先将既有技术图渲染为模型参考，再以首轮输出作定向修图输入。最终 PNG 按源文件字节存档。

| 图 | 技术参考 | 首轮原件名称 | 入稿原件名称 | 入稿 SHA-256 |
|---|---|---|---|---|
| 1 | [fig1_framework_r10.pdf](fig1_framework_r10.pdf) | exec-11255385-c3d4-4cd0-a8ff-cf52a366f163.png | [fig1_framework_imagegen_r13.png](fig1_framework_imagegen_r13.png) · exec-09e742e8-9fd9-49ef-9ddc-59f9d9c813a4.png | c04f58a95ac3b4cc46ed2383d57010df887dcc08c029fc4142caa90d52898c81 |
| 2 | [fig2_window_context_r9.pdf](fig2_window_context_r9.pdf) | exec-d1a9e2d9-62c6-4286-b6d0-413310d47abc.png | [fig2_window_context_imagegen_r13.png](fig2_window_context_imagegen_r13.png) · exec-1a5d6935-c29e-4a6b-9acb-7f838687d320.png | 174be5022af38dd0d958c56bfccadc822a150bf735391cc1f7fdea6f05e32a3e |
| 4 | [fig4_nonmonotone_search_r10.pdf](fig4_nonmonotone_search_r10.pdf) | exec-3b7f421c-0c48-4bf1-9d2d-a8d58e21b0c6.png | [fig4_nonmonotone_search_imagegen_r13.png](fig4_nonmonotone_search_imagegen_r13.png) · exec-1dc7c8c1-2b8b-43bf-9cef-aa3d87df24cc.png | edc3198e26f08dc3d982edb328e951d2312f8a9e093a53916fc3f9fa0838fe69 |

## 图件核对

- 图 1。两个派发入口共享验证后端，结果按探针或微批次的来源解释。探针不复修，微批次至多一次复修，探针失败从冻结参考回退。入稿时用 LaTeX 裁掉底部空白，原 PNG 保留。
- 图 2。短路见证位于新引脚与邻线交互位置，邻线伸出请求窗。右图为合并请求与检查盒相交，检查盒在读入上下文内，返回标记与请求盒相交。斜线标出局部位置，图示未按比例绘制。
- 图 4(a)。核对实测差值 +0.459188 ps（十八门通过）与 −0.157652 ps（三门拒收）及严格子集关系。 [固定协议复算](../../../../project_docs/evidence/tcad_r10_counterexample_20261127/REPORT.md)
- 图 4(b)、(c)。四个列状态分别为派发、首次 Hold 暂缓后重排、两个后续批次合格、取出暂缓批并二分。缓存按冻结输入和验证配置限定，未命中时从冻结参考验证。两面板是机制示意。
- 图 3 依据归档 DEF、LEF 与标记，图 5 和图 6 依据实测记录。稿件致谢记录生成工具及作用范围。 [TCAD 投稿说明](https://ieee-ceda.org/publications/tcad/tcad-paper-submissions) · [IEEE 图件分辨率指南](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/resolution-and-size/)

## 最终采用的提示词

### 图 1 整体流程

**生成**

~~~text
Image 1 is the existing technical schematic and serves as the semantic and layout reference. Use case: scientific-educational diagram, artwork for the full text width of a two-column IC CAD paper. Restyle the reference flowchart as polished, crisp camera-ready scientific artwork. Aim for a wide 2.4:1 occupied area, centered on a pure white canvas with enough white breathing space. Clean black-navy Arial-like typography, cool slate and restrained warm sand, arrow heads small and unmistakable, subtle border weights, horizontal and vertical alignment. Three columns headed “Candidate dispatch”, “Shared validation”, “Outcome”. Put “Shared wall-clock budget” in a discreet bracket across the top. Preserve precisely this topology. In left column small “Frozen routed reference” goes down to “Compatible candidate pool”. It branches toward upper “Full-pool probe” with sublabel “No repair”, and lower “Adaptive microbatches” with sublabel “At most one repair”. Both feed the top of exactly the same three central consecutive stages: “Windowed DRC and net attribution” then “Protected rerouting” then “RCX, multi-corner STA, physical checks and SEC”. From the last stage two right-pointing arrows reach the respective top “Probe outcome” and bottom “Microbatch outcome”. Below the top title use “Pass → save and stop” and “Reject or expire → restart from R”. Below the bottom title use “Pass → save and continue” and “Reject → update frontier”. A single dashed connector with unmistakable arrowhead at adaptive microbatches returns from the “Reject or expire” line. A separate, thin dotted feedback connector from bottom outcome to adaptive microbatches denotes continued search. Tiny low-ink chip, grouped gates and check icons optional only if they do not replace labels or arrows; NO top title, figure number, credit, mockup, shadow, gradients, 3D, scenery, ornamental graphic or duplicate words. Accurately render English labels. Keep arrows from entering unrelated nodes. Legibility and topology are decisive, reduce unnecessary drawing complexity.
~~~

**定向修图**

~~~text
Targeted edit to this exact scientific flowchart. Preserve its alignment, text and color scheme, three columns and all solid arrows. Remove the dashed outline around the entire right section, and remove both feedback paths underneath the chart, including their two explanatory captions. Keep the top shared wall-clock bracket. In the top right “Probe outcome”, preserve the pass line, and replace the reject/expire line with the exact text “Reject or expire → microbatch from R”. Keep the Microbatch outcome pass and reject lines. The action labels convey the transitions so no arrows should come from the right side or run along the bottom. Tight, wide framed composition with white margins on all edges. Keep the original label spelling and wording otherwise, and introduce no additional symbols or links. Transparent background not needed.
~~~

### 图 2 行高窗口与规则上下文

**生成**

~~~text
Image 1 is the existing technical schematic and serves as the semantic and layout reference. Use case: scientific-educational. Use the reference as a geometry plan to create an elegant high-contrast two-panel explanatory schematic for a VLSI journal, full-width and about 3:1 occupied aspect ratio, white canvas, navy outline, muted desaturated blue and teal, and burnt orange for short/marker. Flat precise line art. Retain the left/right conceptual layout and source rectangle geometry. Left panel header exactly “(a) Local witness and window”. Thin navy rectangle labeled “DRC request” encloses a smaller pale slate rectangular “Cell boundary” with a teal rectangular “New pin” near its right edge. A distinct gray horizontal “Neighbor wire” enters from the right, overlaps the tip of the pin in the right-edge interior of the cell, and extends out of the request. A small burnt orange hatched rectangle inside the request is exactly where wire and pin overlap, called “Short witness”. A subtle dash-dot teal rectangular outline around the cell, entirely inside the DRC request, is the bounded reach. Mark the horizontal distances with compact arrows and labels “Row height” for the wide expansion between the left side of the request and cell, “Rule reach” for the shorter expansion from the cell right edge to the teal dash-dot outline. Right panel header exactly “(b) Request and checker context”. Show a navy outline “Merged request Q” that bounds two partly overlapping light blue dashed constituent boxes around two small cell rectangles; do NOT use extra labels for the two little boxes. Overlay a faint gray dashed “Worker check box” that intersects Q and extends to the right of Q. Place a teal dotted “Read context” rectangle around and larger than the worker check box. One horizontal gray wire enters the worker right-to-left area. A small orange “Returned marker” box straddles the right border of Q, intersects both Q and the horizontal wire, inside the worker check box. Each label belongs visually to its own geometry, with short leaders for callouts and no crossing. Uniform sans typography, clean low-ink lines, no invented shapes, no surrounding intro, no figure title, no extra equations, no branding, no scale bar, no photography or 3D. The diagram is conceptual, match relative containment/intersections precisely.
~~~

**定向修图**

~~~text
Targeted scientific correction, keeping the two-panel layout, white canvas, typography and colors. In panel (a), delete both the “Rule reach” label and its double-headed dimension arrow at the bottom right, plus its right vertical extension lines below the request. Keep “Bounded reach” pointing directly at the teal dash-dot outline. Keep the left “Row height” dimension only. Correct the short geometry: move the LEFT end of the gray neighbor wire inward, clearly into the teal New pin, approximately 35 pixels to the left of the dark Cell boundary right edge in the original. The orange hatched rectangle is the actual intersection, overlaid ON TOP of both the pin and the gray neighbor wire; neither the orange rectangle nor the start of the gray wire lies outside the cell outline. The visible gray wire continues right past the request unchanged. Adjust the orange Short witness callout to point to that intersection. Right panel (b) is already technically correct: preserve it exactly including all words, margins and overlap. No new labels, no branding. Produce a wide high-resolution graphic.
~~~

### 图 4 固定协议反例、队列及缓存

**生成**

~~~text
Image 1 is the existing technical schematic and serves as the semantic and layout reference. Use case: scientific-educational. Polish the supplied VLSI paper reference as a quiet, editorial scientific diagram, white canvas, wide occupied content about 2.6:1, highly legible semi-bold sans and math, restrained dark slate / ink, pale blue, pale teal for acceptance, pale orange for rejection. Exact semantics matter more than decoration. Recompose the reference into a wide two-up top and a full-width bottom one-line three-part strip. Top left panel with short header “(a) Fixed-protocol counterexample”, show a teal large rectangle labeled “S18 accepted” and exactly “+0.459188 ps”; inside it show a smaller warm-bordered rectangle with “T3 rejected” and exactly “−0.157652 ps”. Below “T3 is a strict subset of S18”. Small label above boxes “SS Hold WNS change”. No invented data. Top right panel header “(b) Hold feedback and deferred split”. Most important: make a compact four-column, three-row schematic table, exact content. Column headings, left to right “Dispatch”, “Defer B”, “Accept D, then C”, “Split B”. Row headings “Queue”, “Deferred”, “Accepted”. Row Queue values across: “B C D” | “D C” | “∅” | “B1 B2”. Row Deferred: “∅” | “B” | “B” | “∅”. Row Accepted: “∅” | “∅” | “C ∪ D” | “C ∪ D”. Use simple small aligned colored tiles around populated values, centered, spaced, do not make extra rows, do not omit empty-set symbols. Bottom strip header “(c) Exact rejection reuse”. Two equal statements beneath optional short arrows: “Same cumulative set → reuse rejection” and “Changed cumulative set → validate from R”. Add compact quiet subheading “Same frozen input and validation settings” under header if legible. No axes, no bar chart, no extra graphic, no figure number, no branding, no gradients or 3D. Check values and labels verbatim. Keep excellent scan hierarchy.
~~~

**定向修图**

~~~text
Targeted precise edit to the bottom text only in this exact scientific diagram. Keep the entire top two panels visually unchanged, especially S18, T3, +0.459188 ps, −0.157652 ps and all twelve queue-state cells. Under “(c) Exact rejection reuse” change the left statement from “Same cumulative set → reuse rejection” to exactly “Eligible Setup rejection hit → reuse”. Change its right-hand statement from “Changed cumulative set → validate from R” to exactly “No eligible hit → validate from R”. Keep “Same frozen input and validation settings”. Do not add a cache result, number, symbol, secondary line, or image adornment. Same wide framing, equal scan hierarchy and easy typesetting.
~~~

## 入稿核验

图1、2、4分别置于第4、4、6页，RGB 有效分辨率分别为 302.57、324.53、300.93 dpi，按中文稿实际置入尺寸测量。嵌入 PDF 的三组像素分别与对应 PNG 一致。正式英稿排版调整图宽时需按最终尺寸另检。图3、5、6仍使用冻结矢量数据图件。

连续两遍 LuaLaTeX 构建并渲染全部 12 页，无断引用及溢出。表6、7位于第10页，第11页起讨论。数值表身、公式、算法和参考文献与 R12 一致。工作稿已按生成范围更新致谢。

- 源稿 SHA-256：0ba9dcd41eb5bd786c61cadfb50d20714a94840bcc358fe31f89cb540bd6f22d
- 三份同步 PDF 的 SHA-256：5d36e6aba16af66db66a4e4ada8d9abc075c6e0bef9dd199bcb430ea2258fbe2
- 版本标签：faeco-paper-imagegen-20261127-r13
