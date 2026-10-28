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
