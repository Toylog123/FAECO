# 第四轮审稿意见与证据对照

评审原件保存在本地 `scratch/r4_submission/REVIEWER_ORIGINAL.txt`，29134 字节，SHA-256 `55df9b8a11a34353c38279761334aa971e9307f7e4cbfd76bead32499b86b268`。评审对象为 13 页中文稿。核对工作从第三轮发布提交 `2c0e6e47` 开始，以本轮生成的 TeX 与证据记录为准。评审给出的投稿建议用于规划内部修订。正式英文稿和作者信息由作者确认。

## 审稿意见与处理

| 评审条目 | 核验与处理 | 状态 |
| --- | --- | --- |
| III.2、X · ASAP7 Liberty 解析与候选池 | 第三轮确认旧索引漏收 TT INVBUF 库中 37 条未以分号结束的面积字段。UART 和 AES 的旧原生提议分别有 16/16、142/174 项因此无法绑定。同一索引用于 FAECO 枚举和统计。只规范三个库角的面积字段后，两基准的 18 项历史已筛选前缀、顺序和面积差逐项一致。完整面积以冻结实例和 OpenDB master 尺寸交叉核对，UART 为 101.89962 µm²，AES 为 1414.39122 µm²；重新计算表 3、4、10。 [库与前缀审计](../../../../project_docs/evidence/tcad_v5_revision_20261126/R4_ASAP7_LIBERTY_AUDIT.md) · [20 个端点回读](../../../../project_docs/evidence/tcad_v5_revision_20261126/R4_ASAP7_AREA_ENDPOINT_READBACK.json) | 已复核并回填 |
| III.3、X · 历史派发限制 | SKY130HD AES 的 A–D 和独立 Full 都有 6 次派发上限。表 8 标识 A–D，表 4 与图 3 分别标识所绘参与臂。E 单次探针在 180 s 子窗内通过，实际探针约 137.603 s，未进入回退。 [历史配置](../r20261127_r3_submission/R3_HISTORICAL_CONFIG.md) · [E 回执](../../../../project_docs/evidence/tcad_v4_revision_20261126/HYBRID_FAECO_4DESIGNS_VERIFIED.json) | 原始配置与终稿均核对 |
| III.1、X · 处理器功耗估计 | 表 12 标出 TT 默认活动的参考和三个端点均在 50 次后报告未收敛，功耗只作为辅助信息。追加诊断使用同一二进制和冻结输入，并对照输出数值与传播轨迹。轨迹只用于判断收敛，调度结论取合格面积、限时收益和首达时间。 [表体与源记录](../../../../project_docs/evidence/tcad_v5_revision_20261126/V5_STAGE5_TABLE12.json) 四份存档功耗 JSON 主体与按相同输入增加调试观测后逐字节相同，传播仍在编译期 50 次限制触发 STA-2402。 [专项轨迹](../../../../project_docs/evidence/tcad_v5_revision_20261126/R4_STAGE5_POWER_TIMING_REPORT.md#50-轮功耗传播诊断) | 已复核并回填 |
| III.5、X · 物理验收与形式化 | 式（1）增加物理合法性谓词，包含修改信号网连通、放置合法和保护网核验。可行域函数以物理、时序、等价性判定，交付另判断墙钟。全信号物理 LVS 仍未验证。 [既有终态检查](../../../../project_docs/evidence/tcad_v5_revision_20261126/R3_FINAL_PHYSICAL_CONNECTIVITY_REPORT.md) | 式（1）及正文均核对 |
| III.4、X · 同起序批宽复验 | 表 8 独立分组列出同 TT 起序的单门和固定三门。两臂上限 19 次，实际各派发 6 次、完成 5 次，末次均触及墙钟。两臂净回收分别为 33.7824 和 67.5648 µm²，时间均值分别为 12.623 和 34.810 µm²。共同达到 33.7824 µm² 的时间为 567.47 和 235.89 s。 [原任务与结果](../../../../project_docs/evidence/tcad_v5_revision_20261126/V5_REVIEW_MATCHED_BATCH_VERIFIED.json) | 源表和终稿表 8 均核对 |
| III.6、X · 外部方法与原生物理对照 | OpenROAD 独立原生流程、冻结寄生 LR 投影、AuDoPEDA 起序对照分别据实标注。UART 原生标准提议的完整 16 项在原 270 ps 保护后端一次完成，零 DRC、零天线、零净面积，FF/TT/SS 相对 Hold 均退化，未进入候选 SEC。ASAP7 AES 的新证据覆盖绑定。本文的外部比较针对局部诊断、保护式重布线及同池同后端的限时调度。 [原生重放与 81 份原件](../../../../project_docs/evidence/tcad_v5_revision_20261126/R4_ASAP7_NATIVE_UART_PROTECTED.md) | UART 物理准入已实测，AES 物理终态与更强同域方法待验 |
| VI、VII · 两版摘要 | 历史单次回放的诊断加速为 3.04–16.69 倍，双 AES 配对端到端的累计诊断耗时下降约 72–75%。SKY130HD AES 成功全池探针将 98.8448 µm² 回收量提高到 197.6896 µm²，等于翻倍。 [窗口诊断与计时](../../../../project_docs/evidence/tcad_boxed_drc_20261126/REPORT.md) · [全池探针回执](../../../../project_docs/evidence/tcad_v4_revision_20261126/HYBRID_FAECO_4DESIGNS_VERIFIED.json) | 两版摘要均核对 |
| VI · 图 1 与图 2 | 按作者已确认的图像生成方案保留两幅 ImageGen 示意。图 2(b) 图注标明黑色竖条为新引脚金属，菱形标出其与灰色邻线的冲突位置。 [图像来源与核验](../r20261127_r3_submission/FIGURE_PROVENANCE.md) | 图注及第 5 页已目检 |
| VI · 预算、式（4）、表 9 与术语 | 从方法定义删除与主图表无关的旧固定档和 1 ns 串行复验段，原实验留档。式（4）标明 200 ps 与 0.1 是冻结寄生起序的经验常数。表 9 的累计耗时纳入完成预检但后续物理尝试触限的请求。术语使用三工艺角与合格交付。 [旧串行协议](../../../../project_docs/evidence/tcad_ibex_20261123/ASAP7_SERIAL_REPORT.md) · [表 9 原汇总](../../../../project_docs/evidence/tcad_boxed_drc_20261126/BOXED_DRC_VERIFIED.json) | 原口径与终稿均核对 |
| VI、X · 第 5.7 节终态时序与复现入口 | 固定与自适应终态时序直接取 SEC 修复后各自交付的三工艺角报告。可见链接使用“FAECO 公开实验归档与复算说明”，版本标识和补充材料以最终仓库链接为准。 [当前复算索引](../../../../project_docs/evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md) [同批时序附证](../../../../project_docs/evidence/tcad_v5_revision_20261126/R4_STAGE5_POWER_TIMING_REPORT.md#终态三工艺角时序) | 终态时序及固定公开链接已核验 |
| VI、X · 文献和 TCAD 制式 | 核对参考文献 [14] 的 arXiv PDF 与作者 HTML，两者包含副标题，摘要索引只显示主标题。正文恢复全题。TCAD 正式稿需 IEEE 双栏、至少 10 pt、正文和修回所需材料合计至多 14 页、100–250 词摘要和 4–8 个关键词。作者 ORCID、在投与历史投稿声明、实际 AI 用途与参考文献需按最终英文包检查。中文稿的 13 页用于本轮稿件校验。 [14 原文](https://arxiv.org/pdf/2610.18890) · [TCAD 投稿说明](https://ieee-ceda.org/publications/tcad/tcad-paper-submissions) | 投稿明确为材料核对，英文正式稿待作者确认 |

## 历史配置核验

| SKY130HD AES 臂 | 初序 | 旧派发上限 | 时序反馈 | 已发／完成 |
| --- | --- | ---: | --- | ---: |
| A · 窗口单门 | 窗内实际 TT 灵敏度 | 6 | 关闭 | 6／5 |
| B · 窗口固定三门 | 原池 | 6 | 关闭 | 6／5 |
| C · 窗口 Hold 暂缓 | 原池 | 6 | 暂缓 | 6／5 |
| D · 窗口 Pure | 原池 | 6 | 暂缓，随后按直连电容重排 | 6／5 |
| Full · 全块诊断 | 原池 | 6 | 与对应 Pure 对照 | 正、反各 5／4 |
| E · Hybrid | 原池 | 探针 180 s 子窗 | 第一阶段一次全池探针通过 | 1／1 |

六次上限设于历史调度入口。A 的 TT 排序覆盖 `CorrectedComparison.arm` 的动作顺序，仍沿用该入口的 `MAX_REQUESTS`。B 与 C 也经该入口。表 8 的 D 与表 4 的 Full 依联配实验的两个窗口口径执行。E 首次探针通过后停机。 [A–C 入口](../../../../project_docs/evidence/tcad_v4_revision_20261126/run_v4_windowed_ablation.py#L101) · [D 与 Full 的协议](../../../../project_docs/evidence/tcad_boxed_drc_20261126/run_sky130hd_aes_boxed_comparison.py#L100)

表 9 累计的是各臂已完成的预检，调用数按回执 `diag_calls`。正反序共十臂，所列派发请求均取得预检结果，最终未完物理验证的请求也计入。截停请求未计入完成物理评价数。 [统计回执](../../../../project_docs/evidence/tcad_boxed_drc_20261126/BOXED_DRC_VERIFIED.json)

## 发布核验

- TeX 为 `577ac53a61fbe5049504e8bb04440031d760c1237cb5557e9742e8888478efc4`，84,843 字节。三个中文 PDF 副本均为 `b79696aa3cfc13ac3a0638e8add3fba2aa15899d56f1f0d243d695d4aa5b252d`，各 2,662,007 字节。
- LuaLaTeX 双遍、13 页逐页目检、5 图／12 表／26 条引用计数、更新数字回读和既有 LaTeX 质量门通过。既有模板仍有 5 项字体替代提示。图件原始字节复核通过。固定证据链接在 PDF 的第 12、13 页，匿名下载返回 HTTP 200 且内容与 Git 记录相符。[第四轮中文 PDF](../../FAECO_v3_后布局可调预算面积回收.pdf) · [固定版本实验索引](https://github.com/Toylog123/FAECO/blob/29daeeea82ef251c097f55446b04210814d1a020/project_docs/evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md)
- 本轮中文修订及定向验收完成。独立全信号 LVS、ASAP7 AES 规范动作的共同后端终态，以及正式英文包、作者资料和 IEEE 版式仍待确认或验证。
