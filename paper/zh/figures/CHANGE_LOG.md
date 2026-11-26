# 图片修改记录

> 记录**每张图的修改**（内容 / 数据 / 样式 / 尺寸），便于回溯与防混淆（版本 / 配置 / 数据来源）。

## 修改记录

### 2026-11-26 V4 五图体系升级（2 幅高质感机制示意图 + 3 幅收据直驱 Python 矢量数据图）

- **用户美学规范落地**：严格遵循“概念/机制示意图不采用脚本盒线图，仅定量数据图由 Python 从验证收据生成”。
  1. **图 1（系统闭环架构示意图）**：`paper/zh/figures/tcad_20261126/fig1_framework_v4.png`（1355 × 421，300 DPI 无损裁切 PNG，由 `image-generator` 生成并人工视觉核验）——简洁白底炭黑/石油青/焦橙工业级配色，展示冻结已布线版图与标准单元库 → 兼容候选池 → 混合自适应调度 → 局部窗口冲突诊断与保护重布 → 多角时序与物理等价验证 → 合格低面积版图及顶部时序/保持时间反馈闭环。
  2. **图 2（$1.0\times H_{\mathrm{row}}$ 局部窗口机制示意图）**：`paper/zh/figures/tcad_20261126/fig2_boxed_drc_mechanism_v4.png`（1334 × 498，300 DPI 无损裁切 PNG，同视觉体系）——三步递进展示原地降尺寸与直连擦除 → `1.0倍行高窗口` 精确归因冲突邻网 → 锁定无冲突外围线网的保护式局部重布线。
  3. **图 3–5（Python 出版级定量矢量数据图）**：由 `paper/zh/figures/tcad_20261126/generate_tcad_figures_v4_zh.py` 直接读取 `project_docs/evidence/tcad_v4_revision_20261126/` 与既有收据生成 `fig3_anytime_curves_v4_zh.{pdf,svg,png}`（补入 Hybrid FAECO 4 设计曲线与同窗口基线）、`fig4_ablation_v4_zh.{pdf,svg,png}`（三面板：同三门邻网消融、同窗口五级组件消融、UART 批宽 $b$ 倒 U 敏感性曲线）、`fig5_boxed_drc_scaling_v4_zh.{pdf,svg,png}`（双工艺 1–18 门单次预检延迟与 720 s 累计削减）。
- **质量门禁**：3/3 矢量 PDF 全部通过 `audit_pdf_text.py --min-pt 5.0`（实测最小字号 `5.7 / 5.4 / 5.6 pt`）与 `audit_figure_collisions.py`（3/3 均 `0 fail / 0 warn`），全部 5 幅图 600/300 DPI 图像人工视觉检查通过并嵌入 14 页 V4 中文主稿。

### 2026-11-26 中文 4 幅矢量图学术术语精修与灵敏度单门曲线补绘（`nature-figure` 复核）

- **脚本与产物**：`paper/zh/figures/tcad_20261126/{generate_tcad_figures_zh.py, fig1_architecture_zh, fig2_anytime_curves_zh, fig3_geo_causal_ablation_zh, fig4_boxed_drc_scaling_zh}.{pdf,svg,png}`。
- **改动内容**：
  1. 去除全部工程/命令行标签（`ODB/DEF`、`swapMaster`、`FIXED`、`RAW s`、`Request 3`、`geo_m1_k1`/`geo_m1_r0`/`C_med` 等），统一替换为标准学术中文 EDA 术语（`已布线版图快照`、`原地单元替换（零位移）`、`1.0 倍行高局部窗口`、`墙钟时间 (s)`、`同一三门候选提议`、`G(k1)/G(r0)/G(low)`、`灵敏度单门`、`同起序`、`无评估上限`）；
  2. 图 2a 补绘经 `AES_SENSITIVITY_GREEDY_VERIFIED.json` 核验的 `灵敏度单门` 阶梯曲线（`(359.31 s, 11.2608)` → `(489.51 s, 22.5216)` → `(619.30 s, 33.7824 µm²)`），与正文表 3 严格一一对应；
  3. 避免在 5.8 pt 小字标签中嵌套 Matplotlib mathtext 下标导致实测字号跌破 5 pt，改用清晰全字高符号表达。
- **质量门禁**：全部 4 幅 PDF 通过 `audit_pdf_text.py --min-pt 5.0`（实测最小字号 `5.6 / 5.8 / 5.8 / 5.7 pt`）与 `audit_figure_collisions.py`（4/4 均 `0 fail / 0 warn`），600 DPI PNG 全幅人工视觉检查通过，已嵌入 12 页中文主稿。

### 2026-11-26 面向 TCAD 的中英双语 4 幅 Python 出版级矢量图（替代旧 ImageGen PNG）

- **英文版**：`paper/en/figures/tcad_20261126/{generate_tcad_figures.py, fig1_architecture, fig2_anytime_curves, fig3_geo_causal_ablation, fig4_boxed_drc_scaling}.{pdf,svg,png}` 与 `figure_metrics_summary.json`（含四设计 0–720 s Anytime AUC）。全部通过 `audit_panel_alignment`、`audit_pdf_text.py`（≥5.6 pt）及 `audit_figure_collisions.py`（4/4 均 0 fail / 0 warn）。
- **中文版**：`paper/zh/figures/tcad_20261126/{generate_tcad_figures_zh.py, fig1_architecture_zh, fig2_anytime_curves_zh, fig3_geo_causal_ablation_zh, fig4_boxed_drc_scaling_zh}.{pdf,svg,png}`。视觉复核捕获 SimHei 缺少 `µ/²/−` 字形与粗体字重，切换为 `Microsoft YaHei` 并调整图 2d 标注右对齐后重新导出，零缺失字形警告，4/4 通过 `audit_pdf_text.py`（≥5.6 pt）与 `audit_figure_collisions.py`（0 fail / 0 warn），600 DPI PNG 逐幅视觉复核通过并已嵌入 13 页中文主稿。
- 所有数值直接读取 `project_docs/evidence/` 下经独立核验的 JSON 收据，零手工硬编码虚构点。

### 2026-11-23 中文 v3 六幅 ImageGen 示意图

六图依次表示整体框架、WNS 损失预算、安全前缀与后缀复测、同一端点四视图和寄生更新、等效缩小与重布线、同起点基线评估。逐幅核对标签、流程及版面。原始模型 PNG 均为 2172 × 724。实验值转入正文和原生表格。提示词和 SHA-256 见 [PROMPTS.json](imagegen_20261123/PROMPTS.json)。

### 2026-10-18 r22 全72矩阵与配对差图完成

`data/previews/r22_matrix_gain_cost_v3/` 为当前审查预览：全72个WNS收益/实际STA点与64项同电路配对差，原始CSV、编辑型PDF/SVG、600dpi PNG及中英图注齐备。v1独立核对72行、64对及16组所有同状态重复轮5454次交叉比较均一致；没有观察到独立权重收益。s27随机UR3少5次STA、s641仅覆盖少8次等不利点保留。

新增PDF碰撞门后，v1实测6处斜排tick边界重叠；v2试竖排、v3把渲染前对齐检查纳入生成器。旧版不覆盖，v3两CSV与v1字节相同，实际PDF对齐PASS、碰撞0FAIL/0WARN、最小字体6.8pt，源预检19PASS/2WARN/0FAIL，51项不完整输入实拒绝且不建输出目录。实际四panel/整图已查看；170×128mm为项目图幅，PNG为预览，两源预警不冒称期刊验收。主稿科学整合仍待其他族复验。

### 2026-10-16 r22 预试验收益—STA代价预览

新增 `data/scripts/review_r22_pilot_cost.py` 与 `data/plot_specs/r22_pilot_cost_contract.json`。输入为独立验收的18项 C′ 两电路预试验，九臂全部保留；横轴计候选理想线网STA加初始基线，纵轴计相对同一初始网表的WNS收益（ps）。重合坐标合列所有策略名，不抖动、不平均、不混入历史C/D。v1标签碰撞保留原件，v2修正并通过双panel人工复核、源预检0FAIL、PDF29文本运行最小7pt；导出CSV/PDF/SVG/600dpiPNG到 `data/previews/r22_pilot_cost_v2/`。完整八电路矩阵仍在运行，本图及中英图注草稿尚未写入正文，也未覆盖正式r21图。

| 日期 | 图号 / 名称 | 修改内容 | 原因 / 依据 | 关联（数据来源 / 审稿 / 提交） |
|------|-----------|----------|-------------|-------------------------------|
| YYYY-MM-DD | fig3_xxx | 改了… | 因… | DATA_SOURCE / r1 / commit |

## 规则

1. **每次改图后登记**（图号、修改内容、原因）。
2. 数据图修改：同步数据来源记录（`plot_specs/<figN>_<名称>_data.md`）。
3. 机制图修改：更新提示词（`drawing_prompts/<figN>_<名称>_prompt.md`）。
4. 定稿前核对：图与论文数字一致（交叉表）、数据来自当前版本（非旧版 / 其他配置）。

## 2026-10-14 r21 图件修订

| 图号 | 变化 | 来源与口径 | 导出 |
|---|---|---|---|
| 1 | 迭代提交主循环、可选反馈、独立SEC | §3.2/3.6及算法1 | manual/figures/fig1_iterative_flow_r21.* |
| 2 | 六门锥与12节点分裂图、out→in依赖、wi容量 | cut.py构造及覆盖分支；构造示例 | manual/figures/fig2_candidate_mechanism_r21.* |
| 4 | B族所有可评估实例，零收益与N/A保留 | 20260826_aggregation/summary.json | data/final/fig4_unified_gain_r21.* |
| 5 | 40运行按真实新STA重建B(k)，所有种子及终点 | D族eval_trials，剔cache/前置拒绝 | data/final/fig5_budget_curves_r21.* |
| 6 | 理想线网→全局布线收益成对比较，保留退化 | A/A′同候选8电路 | data/final/fig6_physical_transfer_r21.* |
| 7 | 深度与WNS独立分类，零候选s641保留 | F族126个候选、8电路 | data/final/fig7_s_boundary_r21.* |

脚本 `data/scripts/review_r21_figures.py`，契约及输入指纹 `data/plot_specs/r21_*`。旧图源保留；新图PDF/SVG可编辑、PNG600 dpi。图1/2/4/5宽170 mm，图6宽80 mm×68 mm，图7宽80 mm×94 mm；实际字形≥7 pt（单栏缩放约6.95 pt）。所有数据图带CSV。40台账重算、源预检、PDF字形审计及整稿逐页验收见r21归档，不新增EDA。


## 2026-10-14 r22英文适配与暂停状态

英文7图已保存paper/en/figures，矢量源/PDF/PNG/CSV及来源、字形QA齐备；沿用既有结果，不含有效新C′数据。新增历史correctness审计影响A/D/C相关图表科学解释，需恢复后复验再同步中英图表；目前仅保存工作初稿，不视作投稿定稿。

## 2026-10-16 r22 全矩阵配图准备

新增 `data/plot_specs/r22_matrix_gain_cost_contract.json` 与 `data/scripts/review_r22_matrix_gain_cost.py`，计划展示全部72项增益/实际STA调用和64项同电路配对差，随机种子分开保留。来源与排序对照保持同族，不用C′覆盖旧C/D/B3或物理/S结果。实际以24项审计负控调用，工具在建输出目录之前拒绝；收据为 `scratch/r22_matrix_plot_incomplete_guard.json`。全72验收前不绘制全矩阵、不插入正文；当前仅准备完成，最终导出和视觉QA待真实完整数据。


## 2026-10-16 r22 图4图注周期纠错

中英图4图注补PicoRV32主核/乘法器/regs的5/2/0.5 ns实际周期；原图PDF/SVG/PNG与数值CSV不变。与中英实验设置同步，来源为r22逐Tcl审计，编辑/编译/视觉记录见 `paper/zh/review_rounds/r22_20261016/metadata_correction_01/`。此为图注元数据纠错，不是重新测量或重新生成图4数据。


## 2026-10-18 D两例反馈机制诊断预览（iteration02，作者QA过/根独立审查待）

新增`data/scripts/review_r22_D_feedback_mechanism.py`（SHA20fc7b98…）与`data/previews/r22_D_feedback_mechanism_v1/iteration02/` PDF/SVG/600dpiPNG；仅D/fixed-adaptive s27/s382 legacybeam8四对象，不替旧D或回填主稿/全56结论。FINAL_RECEIPT a1a150fe…绑定54原件；权重80行、matched round40行与2行summary CSV和四completion/audit/config/result/eval SHA齐，contract及中英caption独立保存。iteration01保留，02将Actual candidates改Candidate records避免缓存记录与唯一候选混淆。

作者source preflight19P2W0F（170mm项目预览/PNG预览）、panel alignment0F0W、collision0F0W、actualPDFglyph7pt/0below5，VISUAL_REVIEW保存全PNG/PDF与4panel实看；记录员实核54原件SHA-size与CSV行数，未替代独立视觉。根独立审查仍待，不能写最终交付或投稿格式通过；无新EDA/生产/HEAD/主稿变动。


### 2026-10-18 D机制iteration02根独立预览接受（LOG82）

ROOT_FIGURE_ACCEPTANCE3067eb58…/ROOT_REVIEW_WRAPPER记录根独立从原result/eval/current14completion重算80weights/40rounds/2summary CSV，并实看全PNG/PDF四panel；75原件SHA稳定、7pt/碰撞/对齐通过，120s wrapper实际6s exit0。接受仅s27/s382 fixed-adaptive legacybeam8四对象诊断预览，未插入正文、未替旧D或全56科学结论，不构成投稿版式最终确认。作者初始QA/iteration01原件保留。


### 2026-10-18 D诊断图英文caption补件（LOG106，待根接受）

新增r22_D_feedback_mechanism_v1/CAPTION_EN_v2.md（86831fdb…）仅ideal-wire STA改ideal-net STA，SUPPLEMENT18e08613…绑定新旧文本；记录员实际全文单替换及原FINAL/PDF/PNG SHA不变。未重绘/改数据/覆盖旧caption；仅外部图注补充待根接受，仍为两例诊断预览，不正文回填或全56推断。


2026-10-18续（LOG107）：ROOT_CAPTION_EN_V2_ACCEPTANCE8dcf657c…已实际文本接受CAPTION_EN_v2.md（86831fdb…）；后续主稿集成选此新图注，原图像/FINAL/data均不变，图像QA沿ROOT_FIGURE3067eb58…，无需重绘或重复glyph/collision门。正文当前未插该预览。


### 2026-10-18 EN Fig3包含尺寸v5授权（LOG109，未通过）

v4分节FloatBarrier令A图表先于B正文，但28页及15/21/23/24浮动留白被根列为不可最终交付，sync暂停。根实际测v4PDF5d1be23c…Fig3所有可见label/tick/legend最小8.184960pt；MEASUREMENT016641c0…记录.78→.70 linewidth投影7.345477pt≥6.8。只授权EN既有Fig3 include宽.70，原向量源/数据/中文图不变，保barrier/短note/8行；新PDF实际字形、读序、空页和完整contact验收待，不能把投影当v5实测或提前称通过/OI050闭合。


2026-10-18 EN v5实际构建/字形（LOG111）：EN v5仅Fig3 include宽.70，当前source d89b207c…/PDFc2783046…实核匹配；两编译rc0/26页render0，图和A表同15、下一Cross-dataset标题16，实际图内label/tick/legend最小7.345520pt≥6.8。作者静态/实测门已过，visual字段仍pending，最终不同owner/根接受与canonical/metadata同步待，OI050open；ZH不重编，原图vector/data不动。 EDIT4a1c114b…/build825dd0eb…/STATIC128315a8…/actualglyph23f79ebf…；保v4投影为预估，v5为实际PDF测量，未提前最终接受。


2026-10-18根局部视觉/向量绑定（LOG112）：根实看ENv5第15页图表、A8行和注清晰有序，作者继续既定sync。14 included vectorPDF currentSHA均等固定f761 Gitblob（root_vector_head_binding/VECTOR_HEAD_BINDINGc4ff6ad9…），记录员逐SHA核当前14件；此为固定Gitblob字节绑定，不冒称编辑前filesystem快照。作者final/完整视觉与不同owner/根最终接受/同步收据仍待，OI050不提前闭。


2026-10-18作者最终v5/实际副本同步（LOG113）：FINAL_QA_v21902d011…作者38页视觉/限定inverse scope/A8行与EN实测字号通过；SYNC29a6ee35…ZH build-root-manuscript三PDF同173ae809…，ENv5与canonical build同c2783046…，4metadata已同步，记录员当前逐源/PDF/metadataSHA核符。Tex冻结/作者最终清单收尾；不同ownerchecker1291f4e9…仅syntax prepared未执行，独立与根最终接受待/OI050open，不再误写同步未执行。


2026-10-18不同owner最终38页接受（LOG119）：FINAL334a893b…/VISUALaf2c892e…/REPORTfd1aa6f2…已冻结，63final原件逐SHA-size核符/562来源视觉后仍稳定。独立实际12+26页/10contact+两表页高res，A8行/完整注/图3最小7.345520pt及A图表先于B正文，无新裁切碰撞或异常空白，限定接受A元数据/EN局部版式/同步。根最终接受待/OI050暂open，非整体科学或投稿接受。


2026-10-18根最终接受（LOG120）：ROOT_MANUSCRIPT_ACCEPTANCE472b441b…实际accepted，重核独立63原件/562来源、作者finalsource/PDF/canonical与metadata、八实际表行和29图中文字min7.345520pt、45源与HEAD稳定。OI050仅A句表/EN Fig3包含布局与A-B读序/编译副本与metadata门关闭；非其它科学或投稿验收。ZH173ae809…/ENc2783046…为当前有效工作稿PDF，旧失败及v1-v4留档。

### 2026-10-18 r24 C′新图作者完成，根验收待

新增review_r24_cp_gain_cost.py及独立预览r24_cp_gain_cost_v1/v2，未覆盖原图5/原r22图，无新EDA/生产源码/HEAD变动。复用MATRIX_AUDIT_72(a34da9c3…)与72completion，逐项SHA、原accepted CSV及数值核验通过。两面板170×70mm中文热图保留全部72对象/144格数值，a改善ps（CSV含ns），b候选实际STA；6858candidate、8458records、另72baseline严格分开。W1/U1终点及成本全同，无独立权重收益；W1相对L少35–75次/合计427次，不利s641C与s27UR3保留。

v1面板标记超自动探测窗导致alignment WARN，原件保留；v2仅下移标记和标题，alignment PASS/0WARN、collision0FAIL0WARN、PDF最小7pt/嵌入字体/中文提取通过。源预检19P2W0F，WARN为170mm项目图幅及PNG预览。作者实际查看两个panel与完整PDF渲染，未见裁切或重叠。CSV/汇总/配对表/源码快照/manifest/QA齐，根独立验收与主稿插入待。

随后根实际查看v2完整PDF渲染，接受72格/零值/两panel/字号并授权晋级。24文件已复制至data/final/r24_cp_gain_cost，逐文件SHA及size与preview相同，PROMOTION_RECEIPT记录；PDF4650d401…不变。旧preview及v1保留，未改原图5/TeX，主文插入由根负责；此为该图工作稿接受，不外推投稿规格或其他科学证据。

### 2026-10-18 r24六门方法图作者完成，根验收待

新增review_r24_toy_mechanism.py及r24_toy_mechanism_v1–v4独立预览；绑定METHOD_EVIDENCE最终b0eff5f…的人工toy，6个cost与两组边界由生成器另算核符。170×98mm图上保留六门全部代价/R可用性/c双引脚、Cc={g1,g4,g6}与Cw={g6}的input/output/internal及实际cover-first顺序；无共同融合分数、无λc调cover顺序、无STA/SEC或效果实验。旧图2未覆盖，TeX由根负责。

v1缺空集字形/边框触边、v2DTD审计拒绝、v3SVG审计器math/shorthand及Windows换行问题均保历史。v4中文“无”、边框内收、去可选DTD、补等价font-size、toy.v固定原文LF；QA只补审计器缺math标准库命名空间，不改审计规则。v4实际font7pt/嵌入、碰撞0F0W、b/c对齐PASS0W、SVG7–8pt仅170mm宽度WARN；源码19P2W0F。作者实看三panel与整PDF，数字、连接、边界、c双引脚清晰，根验收待。

随后根实际查看v4完整PDF渲染接受六门/成本/双引脚/两边界顺序，授权晋级。25原文件已逐SHA/size复制至manual/figures/r24_toy_mechanism，PROMOTION_RECEIPT9f7a1772…、PDFe87b7049…不变；preview/旧图2保留，TeX仍由根负责。

### 2026-10-18 r24图4功能证明状态标记作者完成

新增review_r24_unified_status.py及previews/r24_unified_status，复用原B族汇总与原图4全部30行/29数值+regs N/A。逐原CSV全部字段字符串相同；按原模型audit0869d234…实际三态记录，仅b09/b20/b21改为空心端点+虚线并列“功能证明不支持”图例，Pico/b17不加此标记；未标对象不宣称新增证明。无新EDA或C′替换，原图4/6/7不变。

170×90mm等宽三panel，现稿中文字体，actualPDF7pt/全部嵌入/文本页内、对齐PASS0F0W；源码19P2W0F。collision0FAIL2WARN已实看为+2.75/+1.13文本跨空白axes填充边界进入白色gutter，无字线碰撞或页面溢出；不移除数据消WARN。作者实际查看a/b/c及全PDF，状态标记和全部数值可读；数据绑定/CSV/源码/QA齐，根接受及正式晋级待。

随后根实际查看全图接受29数值+regs完整及三个unsupported标记，逐项认可两个白gutter WARN解释。23原文件已逐SHA/size晋级data/final/r24_unified_status，PDF33487a8e…不变；PROMOTION_RECEIPT保存复制核验。原图2/4/5/6/7逐SHA与本轮before备份一致（OLD_FIGURES_UNCHANGED），不覆盖旧图6/7。主稿include由根更新。

### 2026-10-18 r24 C′本族逐STA曲线重建与新预览

按根明确授权补REV01本族曲线，新增audit_r24_cp_budget_curves.py与review_r24_cp_budget_curves.py，静态重建审计77b1ecff…绑定已验收MATRIX72/a34da9c3…及每对象eval/result/config/completion原SHA。6858真实candidate_ideal process逐seq对trial，排除72baseline/缓存/前拒；192次committed逐hash/WNS/顺序对state.accepted_patches与final终点。全部72可重建，无gap；0cache提交/0accepted未committed/0failedlaunches，8458records不当测量。B(k)仅明确提交才更新，不复用旧图生成器的best-observed逻辑。

新独立previews/r24_cp_budget_curves_v2保6930点/72条原曲线/192commit，170×108mm 2×4，逐k和完整停止点全等才合并为46条图线；等价组显式覆盖全部72，无外推到500，无旧图/TeX变动。W0/U0、W1/U1全8重合，C仅s641不同，UR2在s27/s713/s820重合；所有不利/交叉保留，COMMON_BUDGET_COUNTERCHECK明确s27UR3和s420的三个UR在部分预算领先W1，不称处处支配。

v2仅加CSV严格SHA门和逐panel内容框，v1历史保留。作者实看8panel及全PDF；7pt/嵌入、对齐PASS0F0W、collision0F0W，源码19P2W0F（170mm/PNG预览）。34文件FINAL_MANIFEST5d1ea1c2…、PDFc944599a…，根接受及晋级待；无新EDA/搜索/STA/SEC。

随后根实际查看完整8panel及严格k/B定义、72→46等价/局部反例，接受工作稿并授权晋级。全部34原文件逐SHA/size复制到data/final/r24_cp_budget_curves，PDFc944599a…不变；PROMOTION_RECEIPT保存核同记录。COMMON_BUDGET_COUNTERCHECK为CSV（非JSON），保s27UR3及s420三个UR部分预算领先的原算术。v1/v2及原图不改，TeX插入由根负责。

## 2026-10-18 r25 主线图选择与图注精简

- 正文保六门静态例、72终点/成本热图及真实STA提交曲线；其余六图移至独立补充材料。只改图件编排与正文图注，不改9个PDF/SVG/CSV/数值。
- 三幅主图短图注保留人工例/图例含义、测量计数/排除口径、精确重合和自然停止信息，全部原始图件及旧稿已在r25 before钉定。

## 2026-10-18 r26内置图片模型六门图科学核查

- 根实际调用内置image_gen生成六门图；独立图件智能体实际view_image原PNG，20项科学内容PASS：六门类型/全边集/g3双c引脚/P与R标记/两区域集合与顺序/两节点代价和均与原toy相符，无虚构测量或证明结果。逐门cost按prompt省略，图注仍需保人工静态例、全权重1及非STA测量限定。
- 原PNG字节复制到`manual/figures/r26_ai_regions/r26_ai_regions.png`，SHA `f852a69f076484c2d4377e852b9813cae3596444c04d02a26477d5259d21d010`前后相同，原输出保留，无像素编辑。prompt、SOURCE_PROVENANCE、manifest同目录；QA为`review_rounds/r26_20261018/FIG2_AI_QA.md/json`。
- 模型/provider/版本未由内置API公开，不编造；本结果为内部工作稿科学核查，不声称可编辑矢量/PDF字体审计或投稿资格已验收。未改旧图、TeX、统计图或运行EDA；图1v1不在本次验收范围，待修复另审。

### r26图1定向编辑与独立科学QA

- 根以原prompt生成v1、实际发现候选直提/拒绝入提交/B画INV三缺陷后，调用内置image_gen定向编辑。独立图件智能体实际查看v1/v2并逐科学箭头追踪，v2结合实查主文e8413a7b图注/正文接受：候选→局部检查→STA→判定；拒绝仅回队列，通过才提交，提交独立回输入，最终SEC独立在搜索后。
- v2原PNG逐字节复制到`manual/figures/r26_ai_overview/r26_ai_overview.png`，1475780B/SHA `709a7982bf5ceacc6a423ebc9b8e02b465e85b0f314764470ba222ddb645456e`不变；原v1 SHA `3350585c62cf9fd6adfafdaeef5da8cc05eaaf5c54bd4bcd694fdf1f5ccc8d43`保拒绝副本/原因，原输出均保留。prompt、editprompt、来源记录和manifest齐。
- 科学QA16项PASS，2非阻塞观察保留：交叉的候选/拒绝连接线以异色、无节点及可追踪路径区分；编辑消失的固定目标刷新标签由当前精确图注/正文补足。报告`review_rounds/r26_20261018/FIG1_AI_QA.md/json`。未改像素/TeX/统计图、未EDA；模型/version/provider未知，不冒称矢量/字体审计或投稿资格通过。


## r27 2026-10-19 — 全文量化图低饱和配色统一

- 7个唯一量化图在`data/final/r27_palette/`新建副本，复用已验收Python源；蓝灰为主、少量灰褐比较，白底。原图/数据/脚本未覆盖，所有已有CSV逐SHA相同。
- 仅配色调整；绘图科学函数忽略颜色后AST一致，候选/数值/筛选/文本/坐标/曲线线型和标记保留。重渲染产生微量字体/图例浮动及ISCAS tight_layout裁切差，详见r27回执，不称bitwise几何相同。
- 原fig6/fig7/ISCAS辅助网格穿字，在新副本设为无色；ISCAS零参考线同处理，iteration01原件保留。最终7图碰撞FAIL为0、字形工具通过；5个多面板对齐通过。每图已实际视觉检查；fill-edge WARN保留说明。无新EDA。
- 记录：`paper/zh/review_rounds/r27_20261019/QUANT_PALETTE_RESULT.json`及同名MD；本文档条目仅量化图，AI图由主线另记。


## r27 2026-10-19 — 用户指定黑白灰，量化图替代蓝灰工作副本

- 最新“黑白灰配色”取代此前蓝灰方案；7图另存`data/final/r27_monochrome/`。旧彩图、蓝灰源/图包及验收回执保留；BLUEGREY_SUPERSEDED_RESULT.json/md明确留档。
- 已验收蓝灰最终源仅替换十六进制颜色与输出目录，完整源AST在忽略这两类字符串后相同。10对已有CSV及ISCAS派生源表逐SHA一致；数据、候选、坐标、文字、标记与线型不变。
- 7图原始PDF操作数/嵌入栅格/原生PNG为中性。关闭MuPDF ICC后7图RGB渲染最大通道差均0；默认ICC灰阶转换至RGB的1/255舍入单列，未对图像像素后处理。
- 已重做源码/5pt字形/碰撞及最终输出颜色检查，全部工具rc0、碰撞FAIL0，5个多面板对齐PASS；实际查看7图全图及全部面板，5个既有fill-edge WARN说明保留。微量字体/裁切浮动详见验收回执，不称bitwise几何一致。无新EDA、生产代码及HEAD变更。
- 最终结果与路径映射：`paper/zh/review_rounds/r27_20261019/QUANT_PALETTE_RESULT.json`及同名MD；量化图配色验收不关闭科学未决事项。

### r27 两示意图内置模型黑白灰编辑及整稿输出
- 图1/2分别沿r26原图内置image_gen定向编辑，原字节存r27_mono_overview/与r27_mono_regions/，prompt/provenance与逐项科学核查齐。图1 13项、图2 14项PASS；旧图保留。
- 原生PNG严格R=G=B分别70.525169%/78.446261%，最大通道差11/12，未伪称单通道；两稿最终以文档层DeviceGray输出并逐页验中性，未手工修改AI像素。图1无点交叉/图2淡灰P成员及图注依赖、未知模型身份和投稿资格未核验保留。

## 2026-10-19 r28：图件在论文中的占幅调整

- 按用户反馈，仅调整TeX includegraphics宽度：图1/2为正文宽82%，数据图为原栏宽/正文宽92%；补充ISCAS89配对图已有约6.12pt最小字，保原栏宽。所有图保持纵横比。
- 九个唯一图像原字节、数据、黑白灰与全部正文/图注不变；逆替换核r27源逐字同，19文件before完整保留。后续整稿构建/DeviceGray/字号/全页视觉与副本身份以r28最终回执为准，不把计划当已验。

### r28 图幅验收
- 无新图生成/像素编辑/绘图源或数据变动，九唯一图字节逐SHA保持r27。仅TeX放置宽度改变，保持纵横比；两PNG实际139.3952×92.9301mm，定量图最小字6.39716/6.11806bp。
- 完整19页与关键图页已实看，图4/5的普通浮动约束防止堆页/裁底；中间失败保历史，最终双稿仍严格黑白灰。见r28/ACTUAL_FIGURE_SIZE_QA及FINAL_DELIVERY。

## r95 2026-10-28 — 臂名显示标签 CO 与改善量单位 ns（另存 r95_monolabel）

- 起因：r95 审稿面板 R1/R2 指出臂名 `C`（仅覆盖区域）与子锥 $C_i$、区域族 $C_c/C_w$ 同字母，图例与表内易误读；图 3(a) 色标与格内标注用 ps，正文用 ns。
- 处置：**只改显示层，不改数据**。两张量化图（`r24_cp_gain_cost`、`r24_cp_budget_curves`）另存 `data/final/r95_monolabel/`，源脚本置其 `sources/`，`r27_monochrome/` 原产物整目录保留不动。
- 脚本改动（`sources/r24_cp_gain_cost.py`）：新增 `ARM_LABELS`，数据键仍为 `'C'`（审计作业集与 STYLES 查找不受影响），仅 `set_xticks` 用显示标签；改善矩阵改用 `wns_gain_ns`，格内两位小数（全部接受改善均为 10 ps 整数倍，0.02–0.46 ns，两位小数无损），色标 0–0.4 ns；两个面板分别用 `ns_label`/`count_label`，STA 面板仍为整数。`sources/r24_cp_budget_curves.py` 仅把图例 `('C','C')` 改为 `('C','CO')`。
- 数据一致性：`r24_cp_gain_cost_source.csv`、`r24_cp_gain_cost_paired.csv`、`r24_cp_gain_cost_arm_summary.csv`、`PAIRED_SUMMARY.json`、`PANEL_ALIGNMENT.json`，以及曲线图的 `CANDIDATE_STA_COMMITTED_CURVES.csv`、`COMMIT_EVENTS.csv`、`CURVE_RECONSTRUCTION_AUDIT.json`、`RECONSTRUCTION_SOURCE_BINDING.json`、`PANEL_CONTENT_BOXES.json`，与 `r27_monochrome/` 同名文件**逐字节相同**。仅 `FIGURE_CONTRACT.json`（措辞：ps→ns、C→CO、reuse 追加 relabel 说明）与 `SOURCE_BINDING.json`（渲染件 SHA 与数据字段说明）随新产物更新。
- 运行守卫照旧生效：审计文件 SHA `a34da9c3…`、`head 3ea0f75`、72 作业、逐 `completion.json` SHA、SEC 与 STA 台账范围；输出 72 对象、候选 STA 6858、曲线 6930 点、46 个全等组，与 r27 一致。
- 两处一次成型的坑已修：初版把两位小数格式套到 STA 面板，四位数挤成 `177.00177.00`；改为按面板传格式化函数后重绘。首版产物未入库，存 `scratch/r95_qa/old_gain_cost_try1/`。
- 版面：两图物理尺寸仍 170×70 mm 与 170×108 mm，正文占幅 92% 未动，主稿页数不变。
