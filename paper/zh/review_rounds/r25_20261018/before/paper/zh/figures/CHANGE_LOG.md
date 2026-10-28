# 图片修改记录

> 记录**每张图的修改**（内容 / 数据 / 样式 / 尺寸），便于回溯与防混淆（版本 / 配置 / 数据来源）。

## 修改记录

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
