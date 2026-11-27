# FAECO 现行口径（CANON）

## 2026-11-27 第十轮投稿前技术核验

- 三门与十八门反例绑定同一个行高预检执行协议和验收门。两条原记录的有效物理阶段限时一致，均允许至多一次邻网复修且实际为零。SS Hold WNS 相对变化 −0.157652 与 +0.459188 ps，三门拒收、十八门通过。原限时 Hybrid 探针用于历史时间及面积统计。[固定协议原件与复算](evidence/tcad_r10_counterexample_20261127/REPORT.md)
- 主稿显式定义协议限定的可行性、最终授权放行集合、依赖运行历史的完成时间与启发式输出。26 条文献已逐条核验，随稿补件 A–G 与冻结 Git 对象对应。沿用 12 页、6 图、7 表、1 算法。本轮未启动 EDA。
- [中文主稿](../paper/zh/FAECO_v3_后布局可调预算面积回收.pdf) · [独立补件](../paper/zh/manuscript/FAECO_R7_补充材料.pdf) · [审稿对照](../paper/zh/review_rounds/r20261127_r10_final/R10_REVIEW_MAP.md) · [工件清单](../paper/zh/review_rounds/r20261127_r10_final/R10_RELEASE_MANIFEST.json)。正式英文 IEEE 稿、作者事项与提交待确认。

## 2026-11-27 第九轮中文稿定稿校对

- 正文为 12 页、6 图、7 表、1 算法。图 2 区分有限交互半径与短路交叠，图 3 局部放大三处归档标记，图 4 明确派发前后快照、首次暂缓重排和缓存命中后的操作。参考文献字号与间距经重排，原实验表及独立补件继续使用冻结版本。
- [中文主稿](../paper/zh/FAECO_v3_后布局可调预算面积回收.pdf) · [补充材料](../paper/zh/manuscript/FAECO_R7_补充材料.pdf) · [审稿对照](../paper/zh/review_rounds/r20261127_r9_proof/R9_REVIEW_MAP.md) · [工件清单](../paper/zh/review_rounds/r20261127_r9_proof/R9_RELEASE_MANIFEST.json)。正式英文 IEEE 稿和作者材料仍待确认。

## 2026-11-27 第八轮方法机制图修订

- 中文主稿为 12 页、6 图、7 表、1 算法。图 2 补充行高窗口的局部覆盖、请求合并和工作单元上下文；图 4 并列展示实测反例、可达的 Hold 暂缓队列和精确拒收复用示例。原真实版图图顺延为图 3，原量化图顺延为图 5、6。
- 实测反例只覆盖同一冻结参考的 $T_3\subsetneq S_{18}$。原物理收据给出的 SS Hold WNS 变化为 −0.157652 和 +0.459188 ps，分别拒收和通过。队列与缓存面板为机制示意。无新物理实验，独立补件继续使用 R7 公开版本。
- [中文主稿](../paper/zh/FAECO_v3_后布局可调预算面积回收.pdf) · [补充材料](../paper/zh/manuscript/FAECO_R7_补充材料.pdf) · [审稿对照](../paper/zh/review_rounds/r20261127_r8_mechanism/R8_REVIEW_MAP.md) · [工件清单](../paper/zh/review_rounds/r20261127_r8_mechanism/R8_RELEASE_MANIFEST.json)。正式英文稿和作者材料仍待确认。

## 2026-11-27 第七轮中文稿出版校对

- 中文主稿保留 11 页、4 图、7 表及 1 段算法。图 3 为窗口诊断，图 4 为限时交付轨迹，按正文首次引用编号。架构图补 RCX 与复修协议；真实版图图明确归档 DEF、LEF 和实际全块标记的用途。
- 表 1 恢复六个冻结池上界。表 2 按正反序逐臂原精度复算，SKY130HD AES 全块平均单次为 14.39 s，ASAP7 AES 窗口为 7.02 s。UART-TC 历史运行采用相对 Setup 门，各臂交付端点实测三角非负；独立 40 ns 处理器另强制绝对 Setup 下限。OpenDB 复核明确为 25 条终态记录。未新增物理实验。
- [中文主稿](../paper/zh/FAECO_v3_后布局可调预算面积回收.pdf) · [补充材料](../paper/zh/manuscript/FAECO_R7_补充材料.pdf) · [逐条复核](../paper/zh/review_rounds/r20261127_r7_editorial/R7_REVIEW_MAP.md) · [工件清单](../paper/zh/review_rounds/r20261127_r7_editorial/R7_RELEASE_MANIFEST.json)。正式英文稿和作者材料仍待确认。

## 2026-11-27 第六轮中文稿内容与图表专项修订

- 第 5 节先检验局部诊断与保护重布，再展示限时交付、调度适用条件及相对和绝对时序门。主稿为 11 页、4 图、7 表、1 算法，附录 A–G 保留完整证据、逐例数据与工程审计。原生独立提议的失败状态、时序和功耗另列，主回收表保留可比的验收端点。
- 图 2 基于 SKY130HD AES 第 3 次请求的冻结与交付 DEF、LEF 和原有全块 DRC 标记。窗口和降尺寸预览按历史输入重建，图中保护网的完整路径在两份 DEF 中一致。图 3、4 分别复绘正序合格检查点和现有诊断配对，未新增物理实验。科学数据继续使用 `f0fe992b9ce44b8368b620d06b8d95a56179347c` 所对应的冻结证据；R5 来源为 `faeco-paper-final-20261127-r5`。
- [中文主稿](../paper/zh/FAECO_v3_后布局可调预算面积回收.pdf) · [补充材料](../paper/zh/manuscript/FAECO_R6_补充材料.pdf) · [逐条复核](../paper/zh/review_rounds/r20261127_r6_editorial/R6_REVIEW_MAP.md) · [工件清单](../paper/zh/review_rounds/r20261127_r6_editorial/R6_RELEASE_MANIFEST.json)。正式英文 IEEE 稿件和作者材料仍待确认。

## 2026-11-27 第五轮中文定稿

- UART 在补齐三工艺角 Liberty 面积字段后，K9 和 K18 的身份及顺序一致，K36 追加的 18 项均改变，静态池上界由 2.72646 升至 2.95974 µm²。表 10 的 1.50174 µm² 和 55.1% 对应原冻结 K36。原池 23 次完整评估与第 24 次预览截停均回读核对。[K36 核验](evidence/tcad_v5_revision_20261126/R5_ASAP7_UART_POOL_AUDIT.md)
- OpenDB 逐对象复核 4 条参考和 25 条实际交付记录，输入指纹及完整功能实例与各自原网表一致。25 条记录的整版图功能面积差与已接受动作的 master 尺寸差之和按整数 DBU² 一致。[直接 OpenDB 核验](evidence/tcad_v5_revision_20261126/R5_DIRECT_ODB_AREA_REPORT.md)
- 第五轮小修完成，13 页中文稿、5 图、12 表、26 条参考文献。三份 PDF SHA-256 `db474b5a949d12ddfce84e31647d18cec8f918320368818551dc6da798a36ad8`。证据 Git 提交 `f0fe992b9ce44b8368b620d06b8d95a56179347c`，论文冻结标签 `faeco-paper-final-20261127-r5`。正式英文稿与作者材料待确认。 [中文定稿](../paper/zh/FAECO_v3_后布局可调预算面积回收.pdf) · [逐条复核](../paper/zh/review_rounds/r20261127_r5_submission/R5_REVIEW_MAP.md) · [定稿清单](../paper/zh/review_rounds/r20261127_r5_submission/R5_RELEASE_MANIFEST.json)

## 2026-11-27 第四轮投稿前中文修订

- 完整功能面积为 ASAP7 UART 101.89962 µm²、AES 1414.39122 µm²，冻结网表与 OpenDB master 尺寸逐项复核。旧索引同时影响预筛集合和面积分母。规范三个库角的字段后，两个历史 K18 的身份、顺序及动作面积差一致，20 个交付端点的净面积同原账本；表 3、4、10 使用完整分母。[Liberty 与端点证据](evidence/tcad_v5_revision_20261126/R4_ASAP7_LIBERTY_AUDIT.md)
- 标准 270 ps UART 原生提议的 16 项完整同面积替换在共同后端完成布线、独立 DRC 和天线检查。净回收为零，三工艺角相对 Hold 拒收。ASAP7 AES 完成绑定核验，实际共同物理终态待验。[原生重放](evidence/tcad_v5_revision_20261126/R4_ASAP7_NATIVE_UART_PROTECTED.md)
- 图 1–2 延用作者指定的 ImageGen 方案并澄清图 2(b) 引脚，数据图沿用原文件。表 12 仍取修复后的 40 ns 同次三臂。四份默认活动报告在固定 50 次未收敛，仅作辅助估计。现行 13 页中文稿双遍编译、逐页目检、取数和公开链接均通过。三份 PDF SHA-256 `b79696aa3cfc13ac3a0638e8add3fba2aa15899d56f1f0d243d695d4aa5b252d`。正式英文稿与投稿作者材料待确认。 [现行中文稿](../paper/zh/FAECO_v3_后布局可调预算面积回收.pdf) · [第四轮复核](../paper/zh/review_rounds/r20261127_r4_submission/R4_REVIEW_MAP.md) · [公开复算](evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md#第四轮专项证据)

## 2026-11-27 第三轮中文修订与定向复核

- 现行中文稿 13 页、5 图、12 表、26 条参考文献。表 12 统一到 SEC 进程组清理修复后的隔离三臂。单门／固定三门／自适应终态分别 40.0384／91.3376／31.2800 µm²，时间均值分别 22.7497／37.3614／23.3685 µm²。首次正式单门的 48.7968 µm² 保留为历史。表 4 绑定历史 270 ps UART 和 6 ns 处理器，各功耗以匹配端点为准。[复算入口](evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md)
- 参考及三个修复后交付 ODB 全部通过只读放置、VDD/VSS 连通和已布线状态检查。生产 DRT 的连通检查覆盖修改信号网，全信号物理 LVS 待验。ASAP7 原生动作失败归因于 TT Liberty 语法覆盖，生产适配器及共同物理后端待验证。 [专项原件](evidence/tcad_v5_revision_20261126/R3_FINAL_PHYSICAL_CONNECTIVITY_REPORT.md) · [未决项](OPEN_ISSUES.md)
- 按作者指示，图 1–2 为图像模型示意，图 3–5 沿用数据图。双遍 LuaLaTeX、数值回读与版面目检完成。三份 PDF SHA-256 `2f90bd3ed54cd4824d42aa54678fac8e745daafed1013bad91ab06d4ff8ad71e`。正式英文 IEEE 投稿包及作者材料待确认。 [中文稿](../paper/zh/FAECO_v3_后布局可调预算面积回收.pdf) · [第三轮复核](../paper/zh/review_rounds/r20261127_r3_submission/R3_REVIEW_MAP.md)

## 2026-11-27 V5 第三轮之前的中文定稿与模拟复审

- 同起序 SKY130HD AES 批宽补证中，固定三门和单门分别回收 67.5648 与 33.7824 µm²，时间平均收益为 34.809579 与 12.623294 µm²。首个合格三门组合包含单独评估时因 SS Hold 被拒的一项。同终态面积的两个首达点不共享动作或物理产物。470.5 ps UART 原候选的 SS Setup WNS 从 +0.794642 降至 −0.568545 ps，相对门通过，绝对零下限拒收。[补证及资源记录](evidence/tcad_v5_revision_20261126/REVIEW_SUPPLEMENT.md)
- 13 页中文定稿、5 图、12 表及 26 条参考文献通过模拟复审及本轮补证的定向核验。图 1–2 的原始生成追溯至 Google Antigravity `generate_image`，已按确证更新致谢。三份 PDF SHA-256 均为 `a25b036458667d1ef6830fe6c5e66f38591a2104b1b3da3262f8b5cbd581a4c6`。正式英文 IEEE 包、作者资料与 ORCID 待确认。 [中文定稿](../paper/zh/FAECO_v3_后布局可调预算面积回收.pdf) · [终版模拟复审](../paper/zh/review_rounds/r20261127_v5_tcad/REREVIEW_FINAL.md) · [英文投稿入口](../paper/en/README.md)
- V5 离线复算绑定 297 份实验原件和 37 份审稿原件；Windows 清洁提取及篡改拒收已验证。完整 EDA 物理复跑需要恢复冻结输入和工具映射。跨设计稳定速度和硬返回接口仍待验证，原生和先进方法的共域可执行性以未决项为准。 [公开证据索引](evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md)
- SKY130HD GCD 同一三门提议完成常规、窗口和全块预检对照。两种预检均无标记。三臂首轮独立全块 DRC 均检出同三处 met1 短路，位置全部在原诊断窗口中。仅放行 `net242` 复修后均清零，最终仍因 TT 相对 Hold 下降 0.022621 ps 拒收，回收均为零。该配对界定一个非 AES 提议的检查阶段。 [三臂同提议报告与复算](evidence/tcad_ibex_20261123/GCD_WINDOW_DIAGNOSIS_REPORT.md)
- GCD 冻结三门的等数量单邻网对照已核验。几何择一选 `_073_`，仍需追加 `net242` 复修。事后直接放行已知 `net242` 首轮独立 DRC 清零并省去一次 DRT/RCX。两臂的 TT 相对 Hold 均下降 0.022621 ps，合格回收为零。结论限这一同提议的两种选网。 [单网预放行报告](evidence/tcad_ibex_20261123/GCD_GEOMETRY_RELEASE_REPORT.md)
- 40 ns 处理器固定三门／自适应各复跑一次，重现 91.3376／31.2800 µm² 的终态。两次补测获得进程树的搜索 CPU、scope 内存高水位与独立读者接受时刻。自适应臂末次 DRT 在 720.080274 s 退出，外层返回在 720.122790 s 被观察到。720 s 继续按候选验收解释。 [资源与读档补测](evidence/tcad_v5_revision_20261126/REVIEW_SUPPLEMENT.md#40-ns-处理器配对复跑的进程树与下游读取)
- 小 UART 和两项最大网数代表双 AES 的原候选分别重放了完整七阶段。候选墙钟 25.148／117.165／166.992 s，cgroup CPU 43.720／278.485／414.282 s，scope 内存峰 726.195／2594.973／4559.102 MiB。 [三项资源](evidence/tcad_v5_revision_20261126/REVIEW_SUPPLEMENT.md#小-uart-与两项最大代表设计的阶段资源)
- 40 ns 处理器上原 TT 灵敏度与 AuDoPEDA 功耗恢复首轮排序投影共用固定三门、相同目标和保护后端。两臂各完成 6 次，分别验收 4／2 次，回收 91.3376／43.7920 µm²。该对照覆盖一个设计上的两种起序。 [外部排序结果](evidence/tcad_v5_revision_20261126/REVIEW_SUPPLEMENT.md#40-ns-处理器同池同后端的外部排序对照)
- R3-1 UART 已布线参考与候选在同一 WSL 的两个代码目录、独立输入路径中分别重跑三角 STA。每组 6 份完整时序报告与原档一致，单字节修改的 SPEF 在派发前被拒。此实验证实冻结端点的异址时序重放。跨主机工具／PDK 与完整物理重建仍待验。 [异址重放](evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md#r3-1-冻结-uart-端点的异址-sta-重放)
- V6 在同一 WSL 主机的私有用户、挂载和网络环境中遮蔽旧根、从只读副本重建 40 ns 处理器参考和固定首批。参考及首批 ODB／DEF／Verilog 相同，参考 SDC 相同，两份 SPEF 各仅日期不同。后续三臂有 18 次共同完成请求重现动作、门与物理结果。隔离单门、固定三门和自适应终态分别为 40.0384／91.3376／31.2800 µm²。单门末次 SEC 在窗口内无收据，旧 Yosys 后代继续写入。短窗 A/B 与足窗证明验证修复。修复版完整三臂复跑重现 18 次共同完成和各终态。单门再次在 SEC 截停，同组工具已在下一臂起序前退出。10,523 次采样未见跨臂重叠，时间均值按各轮报告。完整跨机器执行及通用硬返回待验证。 [两组原件与命令](evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md#从独立输入副本重建-40-ns-处理器参考)

## 2026-11-27 V5 实验与终态复核完成，中文稿进入修订

- Stage 5 采用独立重建并通过三角时序和物理资格门的 40 ns SKY130HD `riscv32i`。同一 18 项候选池、验证后端与 720 s 计费窗内，单门、固定微批次、自适应 FAECO 分别交付 6／12／4 项，面积 48.7968／91.3376／31.2800 µm²，时间平均回收 23.0862／38.4928／23.5088 µm²。固定微批次在该参考上的终态与时间平均收益均最高。固定与自适应前三派发的首次分叉源于 DRC／天线拒收后的处理差异；相对 Hold 暂缓未触发。已逐阶段核对收据及交付物。[Stage 5 收据](evidence/tcad_v5_revision_20261126/V5_STEP5_10K_TIMING_CLOSED_TC40NS_MMMC_DRV_VERIFIED.json) · [实验报告](evidence/tcad_v5_revision_20261126/REPORT.md)
- 中文稿应以已完成的 V5 结果更新相对预算、探针成本和严格参考的结论，完成编译与版面复核后开展面向 TCAD 的模拟审稿与复审。原生候选未入共同合格排序，强外部学习方法的同后端执行仍为未决项。[未决项](OPEN_ISSUES.md)

## 2026-11-27 Stage 4 同协议对照完成，Stage 5 候选阶段开始

- 同一回退协议下，SKY130HD AES 的 0／60／120／240 s 分别交付 9／6／6／18 项，合格面积为 98.8448／67.5648／67.5648／197.6896 µm²。ASAP7 AES 分别交付 6／6／6／3 项，合格面积为 0.61236／0.61236／0.61236／0.30618 µm²。ASAP7 纯微批次与 60／120 s 终态等字节，AUC 由 0.261014 降至 0.208023／0.158731 µm²。失败探针可延迟首次交付，并减少窗内合格回收。最终八臂收据 SHA-256 `5a63f0adfc02a897f8e8fd6f18eea3a972eb635207164e427b23dadf0868299c`。[Stage 4 收据](evidence/tcad_v5_revision_20261126/V5_STEP4_PROBE_SENS_VERIFIED.json)
- Stage 5 候选流程于约 02:52:26 (UTC+08:00) 接锁，实际预筛台账于 02:52:30 写入。将同一 18 项候选池，以及计入筛选和在线灵敏度排序的 720 s 墙钟，在合格的 40 ns 带电气裕量参考上对比单门、固定微批次和自适应 FAECO。终态待正向物理与等价验收。[V5 实验报告](evidence/tcad_v5_revision_20261126/REPORT.md)

## 2026-11-27 Stage 5 独立参考已获完整资格

- 40 ns 带电气裕量的 `riscv32i` 独立重建通过三角 Setup／Hold、电气、DRC、天线与参考 SEC 自检。FF／TT／SS Setup WNS 为 +31.551／+29.021／+6.842 ns，Hold WNS 为 +0.386／+0.596／+1.925 ns，六项 TNS 为零。I/O 保持 65 个非时钟输入、99 个输出以及绝对 2 ns 延时，最终导出 SDC 与前一 40 ns 实现逐字节一致。参考包含 5,456 个功能单元，面积 69,750.6464 µm²，按 TT `nand2_1` 折合约 18,582 个 NAND2 等效门。Stage 5 预检已绑定 40,000 ps 冻结周期和 400 ps 相对 Setup 预算。三个同窗候选臂在双 AES 0 s 对照之后等待同一 EDA 锁。[参考资格收据](evidence/tcad_v5_revision_20261126/V5_STEP5_TC40NS_MMMC_DRV_QUALIFICATION.json) · [V5 实验报告](evidence/tcad_v5_revision_20261126/REPORT.md)

## 2026-11-27 Stage 4 两设计六个正探针预算完成

- ASAP7 AES 的 60／120／240 s 全池探针均达到子预算，前两档截停于 DRT，240 s 档截停于 RCX。回退合格面积依次为 0.61236／0.61236／0.30618 µm²，AUC 为 0.208023／0.158731／0.064844 µm²。SKY130HD AES 的 240 s 探针则完整交付 18 项。六个新测臂收据 SHA-256 `63f13fd71ed84954246f4b13ce35064f11d4ec0f5558e4839ef6a9e390b5b763`。双 AES 同协议 0 s 对照排队，作为回退性能的直接比较。[Stage 4 收据](evidence/tcad_v5_revision_20261126/V5_STEP4_PROBE_SENS_VERIFIED.json)
- 带 15% 电容裕量与 10% 转换时间裕量的 40 ns 重建于 02:19:51 (UTC+08:00) 接过 EDA 锁，保持三个库角、2 ns 绝对 I/O 与原有时序验收门。参考资格及在线候选臂待实测。[V5 实验报告](evidence/tcad_v5_revision_20261126/REPORT.md)

## 2026-11-27 Stage 4 SKY130HD AES 三个正探针预算完成

- 60／120 s 探针分别截停在详细布线与 SEC，均回退交付 6 项、67.5648 µm²，终态物理产物一致，AUC 分别为 14.143977／9.264451 µm²。240 s 探针约 134.036 s 完成，同窗交付 18 项、197.6896 µm²，AUC 为 129.761367 µm²，终态与历史默认探针读数的物理产物一致。ASAP7 AES 新测在运行。历史 0 s 臂的派发上限或拒收复用规则有差异，已登记两个同 V5 回退协议的 0 s 对照，另保留历史参照。[Stage 4 收据](evidence/tcad_v5_revision_20261126/V5_STEP4_PROBE_SENS_VERIFIED.json) · [V5 实验报告](evidence/tcad_v5_revision_20261126/REPORT.md)

## 2026-11-27 Stage 5 多角参考的电气边界与 Stage 4 开跑

- 40 ns 多角 `riscv32i` 完成独立重建，固定 2 ns I/O，65 个非时钟输入与 99 个输出均覆盖。FF／TT／SS Setup WNS 分别为 +31.520／+28.981／+6.616 ns，Hold WNS 为 +0.397／+0.617／+1.944 ns，六项 TNS 均为零。DRC 与天线为零，参考网表的 SEC 自检为 4,559/0。TT 同一 `_3804_/Y` 超过转换时间与电容上限，严格参考资格仍未通过，候选臂未启动。下一变体保留三角与绝对 I/O 条件，加入原生电气裕量。[40 ns 资格收据](evidence/tcad_v5_revision_20261126/V5_STEP5_TC40NS_MMMC_QUALIFICATION.json)
- Stage 4 于 01:20:27 (UTC+08:00) 开跑，从 SKY130HD AES 的 60 s 探针子预算开始。五点对照中 0 s 与默认点为已绑定历史参照。两个 AES 的 60／120／240 s 为新测。[V5 实验报告](evidence/tcad_v5_revision_20261126/REPORT.md)

## 2026-11-27 Stage 3 两设计八臂完成

- 同一 270 ps ASAP7 UART 冻结参考和 720 s 计费窗下，Setup 预算 0／0.5／1／2% 的合格回收分别为 0.32076／0.77274／0.83106／0.83106 µm²，对应 5／12／13／13 项。四档终态三角均无新增负 Setup 端点。1% 与 2% 的 19 个候选身份及拒因完全相同，终态 ODB、DEF、网表及去日期 SPEF 一致。两档交付时间差留作计时波动。[预算扫频实测收据](evidence/tcad_v5_revision_20261126/V5_STEP3_MULTIBUDGET_VERIFIED.json)
- SKY130HD AES 的 0% 档完成 6 个候选，均触发 Setup 拒因，窗内无合格交付。0.5%、1%、2% 的五个完成候选同轨，最终相对预算下均合格回收 9 项、98.8448 µm²，并新增 1 个 TT 负 Setup 端点，终态物理与等价验收一致。八臂收据 SHA-256 `63234f456393e13124c321a0b91bc81c30536ba1b5af34de023c4f5caec714c3`。40 ns 多角 `riscv32i` 已启动物理构建，保持 2 ns 绝对 I/O 延时。Stage 4 双 AES 实验在其后等待同一 EDA 锁。[V5 实验报告](evidence/tcad_v5_revision_20261126/REPORT.md)

## 2026-11-26 V5 接手续跑

- **已复核**：Stage 1 与 Stage 2 第一批的 SHA-256 和交接一致。Stage 1 的时序数据为 FF／TT／SS 三个 PVT 角各自的 Setup／Hold 读数，功耗为 TT 实布 SPEF 下工具默认活动估算。`ASAP7 UART-TC` 的 13 门端点功耗与原始 SDC 的 13 门端点分别追溯。Stage 2A 去重两臂的最大回收均为 0.83106 µm²，AUC 0.434369→0.476433，完成评估 20→19；最终面积首次交付 546.572→507.573 s，计费总墙钟 634.563→588.027 s。详见 [V5 实验报告](evidence/tcad_v5_revision_20261126/REPORT.md)。
- **续跑配置**：Stage 2B 的首轮续跑于 22:45:27 (UTC+08:00) 发现窗口预检误用规范化实例名，保留原件后于 22:56:37 续跑。AES 两个完整 120 项提案绑定到既有网表，但包含连接冻结时钟网的同一触发器替换，均超出只允许直接数据网和诊断邻网重布的保护范围。另设两臂 119 项数据网投影，独立报告。ASAP7 UART 的 16 个实例确实超出冻结动作空间。各臂逐键更新收据，EDA 串行绑定 CPU 0–5。[实验登记](evidence/EXPERIMENT_REGISTRY.md#tcad-v5-revision-suite-续跑预登记)
- **Stage 2 已结束**：600 s 批次中，AES 两臂的完整提案在保护范围预检阶段退出。`riscv32i` 两臂各 24 项，均通过严格零动作预检；AES 两个 119 项投影均通过局部预检。这四次候选详细布线均触及 600 s 上限，未获得候选 STA 与 SEC。Stage 2 最终收据 SHA-256 `b6ef9577384fdabe88f6b82baabfa9344a98f726c9881e6c1e7e5334e8963da4`。两种保护边界均无法用于合格回收的数值排序。[V5 实验报告](evidence/tcad_v5_revision_20261126/REPORT.md)
- **长跑前验收**：Stage 3 逐档更新真实三角 Setup WNS／TNS 门，并复核两设计的冻结周期和 18 项候选池。Stage 4 从原始收据导入 0 s 和默认参照，ASAP7 AES 默认有效子窗约 169.12 s，迟于子窗的探针结果不交付。Stage 5 先独立验证 10 ns 构建和绝对时序收敛。旧 riscv32i 6 ns 原生导出 SDC 含 99 条输出延时和 0 条输入延时，新参考明确给非时钟输入和输出各施加 2 ns 延时，并核对逐端口覆盖。[未决项](OPEN_ISSUES.md#oi-1092026-11-26open-万门级独立对照的资格门与共用后端缺失)
- **Stage 5 参考点反证与 Stage 3 实跑**：10 ns 的独立 `riscv32i` 实现完成布线，含 5,504 个功能单元，65 个非时钟输入和 99 个输出均覆盖，DRC 与天线为零。SS 最差 Setup WNS −22.392385 ns，最差 min slack −0.126299 ns，后者来自异步 reset removal。参考点未达严格时序门，候选臂未启动。Stage 3 于 23:52:37 (UTC+08:00) 按 ASAP7 UART 0% 开始，Stage 5 另准备保留绝对 I/O 条件的多角独立重建。[10 ns 资格收据](evidence/tcad_v5_revision_20261126/V5_STEP5_TC10NS_QUALIFICATION.json)

## 2026-11-26 V5 实跑第一批：Stage 1 完成、Stage 2 部分完成（中断点）

- **进度**：Stage 1 完成（`V5_STEP1_POWER_7NM_DET_VERIFIED.json`，SHA-256 `85bfc165…`）；Stage 2 完成 2A 两臂与 2B 第一遍八 key（`V5_STEP2_DEDUP_NATIVE_VERIFIED.json`，SHA-256 `917a6655…`），2B 第二遍（SKY 两设计 600 s 预算 `::rt600s`）中止未落盘；Stage 3/4/5 未启动。续跑命令、必查项与六处脚本修正见[执行交接](HANDOFF_2026-11-26_V5_EXEC.md)。
- **功耗（TT 真实 SPEF，总／组合／漏电，均降）**：`SKY130HD AES` 18 门 −0.102%／−0.140%／−0.064%；`ASAP7 UART-TC` 13 门 −0.660%／−2.142%／−0.777%；`ASAP7 UART K=36` 19 门 −0.623%／−2.234%／−1.391%。**这是 V5 表 4 的功耗口径来源。**
- **7 nm 受控非零 DRC（`asap7/aes`）**：窗内 5 例（M1/M2/M3 短路与间距）共 37 marker，TP/FP/FN = 37/0/0，marker 集合与网集合逐例完全相同，注入 aggressor 全部被 boxed 捕获，单次预检均值提速 17.34×；另有 1.05×$H_{\mathrm{row}}$ 窗外负对照 2 marker 仅全块可见。**写作要求**：必须声明 aggressor 为受控合成网（`FAECO_NZ_*`，真实层几何），不得表述为「真实邻居网被破坏性注入」；窗外对照如实作为作用域边界。
- **4 线程确定性**：`asap7/uart` 与 `sky130hd/aes` 各 3× 重复完整 DRT+RCX+三角 STA，去日期 SPEF 逐字节一致、判据一致、WNS 极差 0.000 ps。**该 3 门批次本身是 `SS:hold_regression` 拒收**，结论严格限定为「产物与判据确定性」，不得外推为接受性再现。
- **UART 去重消融（同窗口 720 s）**：`dedup_off` 0.83106 µm²／AUC 0.4344／20 次评估／634.6 s，`dedup_on` 0.83106 µm²／AUC 0.4764／19 次评估／588.0 s。**统一表述**：同终态面积下，去重提高 anytime AUC 9.7%、少一次物理评估、早 46.6 s；禁写「去重提高回收面积」。
- **原生 `recover_power` 挂保护后端（240 s 第一遍）**：SKY 两设计（120／24 项）因触及 240 s 单次路由上限而 `rejected`，**属超时而非物理判定**；7 nm 两设计（16／174 项）判 `not_in_action_space`——原生改到 ORFS 端口缓冲实例（`output43`、`u6820` 等），不在冻结 runner 的 `ref_masters` 内。**不得**据此断言「原生回收为 0 故 FAECO 更优」，须待 600 s 第二遍补齐物理判定。
- **口径校验锚点**（换算与库路径已对齐既有收据）：AES 控制点 FF／TT Setup 678.249／−380.501 ps、SS −13,648.043 ps、Hold 336.274／523.915／55.296 ps，与 `faeco_tcad_sky_holdout_20261123/aes/ss_hold_targeted_v2b/qualification/CONTROL.json` 逐位一致；UART-TC 端点三角 Setup 255.927／190.381／28.931 ps 与既有收据一致。

## 2026-11-26 V5 冲刺就绪（第二轮同行评审 85/100 后的脚本、预检与交接状态）

- **第二轮模拟同行评审结论**：V4 14 页中文稿评为 **Major Revision 偏小修（接近 Minor Revision，85/100，较 V3 71.5 分明显提升）**；核心框架已稳固，无需推翻，下一轮聚焦两条证据链收口：① 命题 1 数学严密化 + 7 nm 非零受控 DRC 实证；② 非单调可行域形式化 + 补齐最后 5 项高杠杆实验（功耗/6角、4 线程 DRT 确定性、Setup 去重消融、原生挂载保护后端、双设计多档预算在线搜索、双 AES 探针敏感性、万门级独立 Timing-closed 基准）。
- **脚本与预检状态**：全部 5 个可断点续跑脚本及一键启动器已落盘 `project_docs/evidence/tcad_v5_revision_20261126/` 并通过语法、LF 行尾、模块导入、先决路径及离线反例提取无 EDA 预检（`smoke_verify_v5.py` `PREFLIGHT_SMOKE_PASS`，已确认 SKY130HD AES 真实非单调可行域反例 $T_3 \subset S_{18}$ 与全部 4/4 Hybrid 验收检查点 $\le 720.00\text{\,s}$）；**本轮未启动长时 EDA 运行**，留待用户在空闲时段一键执行。详见 [V5 交接手册](HANDOFF_2026-11-26_V5.md)。

## 2026-11-26 V4 大修专项闭环：LEF 规则实证、同窗口组件消融、Hybrid FAECO 四设计实测、Timing-closed 基准与参数敏感性

- **双工艺真实 `.tlef` 规则与 3× RCX/STA 确定性**：解析本地 `sky130_fd_sc_hd.tlef`（$H_{\mathrm{row}}=2.72\,\mu\text{m}$）与 `asap7_tech_1x_201209.lef`（$H_{\mathrm{row}}=0.27\,\mu\text{m}$）证实：SKY130HD 全栈 `li1–met5`/`mcon–via4`（$\le 1.60\,\mu\text{m}$）及 ASAP7 引脚与中下层 `V0–V7`/`M1–M7`（$\le 0.072\,\mu\text{m}$，引脚层 `M1–M3` 仅 `0.018 µm`）均严格小于 $1.0\times H_{\mathrm{row}}$；ASAP7 高层电源/全局层 `M8`/`M9`/`Pad` 超出 $H_{\mathrm{row}}$ 但不受原地单元替换影响，命题 1 现以集合论（$\Delta G(S)\oplus B(r_{\mathrm{drc}})$）与引脚层作用域 $\mathcal{L}_{\mathrm{pin}}$ 严格限定。3 次重复 RCX+三工艺角 STA 去日期 SPEF 逐字节一致、Hold 极差严格 `0.000 ps`。全 4 设计 18 项池均为 18/18 互异实例。[LEF 与确定性审计](evidence/tcad_v4_revision_20261126/LEF_AND_DETERMINISM_AUDIT.json) · [离线容差审计](evidence/tcad_v4_revision_20261126/OFFLINE_RECEIPT_AUDIT.json)
- **同 $1.0\times H_{\mathrm{row}}$ 窗口后端四级组件消融**：在 `SKY130HD AES` 同一窗口后端（720 s）下，`窗口灵敏度单门` `33.7824 µm²`（AUC `11.721`）、`窗口固定微批次` `33.7824 µm²`（AUC `17.621`，微批次独立提 AUC `+50.3%`）、`窗口微批次+Hold 暂缓（去电容重排）` `33.7824 µm²`（AUC `17.605`）、`完整窗口 FAECO（+电容重排）` **`98.8448 µm²`**（9 门，AUC `19.37`，直连电容重排独立贡献 `2.93×` 面积净增）；7 nm `ASAP7 AES` 补齐 `窗口固定微批次` `0.61236 µm²`（6 门，AUC `0.247`），与 `窗口 FAECO`（`0.61236 µm²`，AUC `0.254`）基本一致，清晰区分两设计上微批次与自适应反馈的独立贡献。[组件消融核验](evidence/tcad_v4_revision_20261126/WINDOWED_ABLATION_VERIFIED.json)
- **Hybrid FAECO（有界乐观全池探针 + 自适应微批次回退）四设计实测**：统一探针子预算 $\tau_{\mathrm{probe}}=\min(180\text{ s},0.30(\tau_{\max}-t_{\mathrm{screen}}))$、单遍无重试。在 `SKY130HD AES` 上探针 137.6 s 一次通过 18/18 门（**`197.6896 µm²`，100.0% 池，AUC `128.78`**，2.00× 纯微批次 FAECO）；在 `SKY130HD riscv32i`（探针 180.2 s 截断回退）、`ASAP7 UART`（探针 26.1 s 拒收回退）、`ASAP7 AES`（探针 169.2 s 截断回退）上分别交付 `75.0720`、`0.83106`、`0.61236 µm²`，**全 4/4 设计终态严格持平或 2.00× 超越纯微批次 FAECO 且全部 0 DRC/SEC 全证**。[Hybrid 核验](evidence/tcad_v4_revision_20261126/HYBRID_FAECO_4DESIGNS_VERIFIED.json)
- **绝对时序收敛（Timing-closed）基准与 `b`/`K` 参数敏感性**：建立 `asap7/uart @ 500 ps` 绝对收敛基准（FF/TT/SS Setup WNS `+255.85/+190.42/+30.29 ps`，Hold WNS `+50.31/+67.50/+54.05 ps`），窗口 FAECO 回收 **`0.83106 µm²`（13/18，1.052%，AUC `0.4561`）** 领先单门（`0.68526`）与固定微批次（`0.33534`），终态仍严格 Timing-closed。`asap7/uart` 批宽敏感性呈倒 U 型（`b=1/2/3/6/9/18` → `0.685/0.831/0.831/0.729/0.685/0.744 µm²`，AUC 峰值 `0.526/0.491` 落于 `b=2,3`）；扩展池规模 `K=9/18/36` 分别回收 `0.496/0.831/1.502 µm²`（`K=36` 达 `1.901%` 功能单元面积）。论文统一区分 **ECO 合格解（ECO-qualified）** 与 **绝对时序收敛（Timing-closed）** 状态。[V4 总报告](evidence/tcad_v4_revision_20261126/REPORT.md) · [Timing-closed 与敏感性核验](evidence/tcad_v4_revision_20261126/TIMING_CLOSED_DRC_SENS_VERIFIED.json)

## 2026-11-26 工艺无关局部窗口化布线前 DRC 预检（`1.0 × H_row`）双工艺正反序闭环

- **零漏报与零位移反驳性审计**：基于「起点 DRC=0 + 原地 `swapMaster` 零邻居位移 + 擦除直连网不生远端违例」不变式，对每个被编辑实例外扩 `1.0 × H_row`（SKY130HD 自动 2.72 µm，ASAP7 自动 0.27 µm，零工艺魔数），裁剪并合并重叠窗口后调 `drt::check_drc -box`，规范去重输出至 `drc_neighbor_evidence()`，终检 `unlocked_drc` 仍坚持全块 DRC。全部 14 组历史不重复批次（37 组回放）实测 `moved_other = 0`；SKY130HD AES 9 组共 56 个真实 marker 在 `0.5/1.0/2.0 H_row` 均实现 **56/56（100%）marker 与释放邻网完全一致**；`1.0 × H_row` 单次预检在 130 nm 提速 **3.04×–6.31×**、在 7 nm 提速 **4.61×–16.69×**。[审计收据](evidence/tcad_boxed_drc_20261126/BOXED_DRC_RECALL_AUDIT.json)
- **130 nm SKY130HD AES 4 臂正反序（720 RAW s，CPU 0–5 独占）**：共同 5 组请求 `full == boxed` marker 与释放邻网 100% 相同、0 重试；单次预检由 14.40 s 降至 **3.33 s（4.32×）**；`faeco_boxed_drc` 首达提前 27.6–41.3 s、达 67.5648 µm² 提前 34.1–51.5 s，并将第 5 批 9 门端点拉入 720 s 内通过全门，正反序合格回收由 67.5648 跃升至 **98.8448 µm²（+46.30%，0.0848% 整芯，捕获 18 项候选池上界的整整 50.00%）**；该 9 门端点 FF/TT/SS Setup WNS 仅变 −0.082/−0.044/+0.050 ps（<0.23% 预算）、三角 Hold 全改善（+0.059/+0.093/+0.783 ps）、独立全块 DRC/天线 0、SEC 11,089/0、跨序 ODB/DEF/V/去日期 SPEF 逐字节一致，TT 真实 SPEF 总/组合/漏电功耗分别降 **−0.0512% / −0.0710% / −0.0320%**。
- **7 nm ASAP7 AES 6 臂同排名正反序（720 RAW s，含公平窗口化强单门 `single_boxed_drc`）**：`faeco_boxed_drc` 单次预检由 38.11 s 降至 **7.03 s（5.42×）**，到达 0.01% 提前 35.7–36.6 s、到达 6 门 0.612360 µm² 提前 **64.7–66.0 s**（510.36/509.78 vs 575.08/575.74 s），并在两序均于 720 s 内跑完第 3 批暴露出 `SS:hold_regression` 触发暂缓探索第 4 批。即使将同一窗口化预检同步赋予强单门基线（使其回收从全块 0.20412 增至 **0.306180 µm²**），`faeco_boxed_drc` 仍以 **2.00×** 面积（0.612360 vs 0.306180 µm²）与提前 163–169 s 胜出，三策略跨序逐字节复现、SEC 10,027/0。[窗口化 DRC 报告](evidence/tcad_boxed_drc_20261126/REPORT.md) · [独立核验](evidence/tcad_boxed_drc_20261126/BOXED_DRC_VERIFIED.json)
- **四设计经典 5 轮冻结寄生拉格朗日松弛（LR）同门实测与后端解耦对照**：在同 18 项池与 1% Setup 预算下，经典子梯度 LR 在四设计上均于冻结 TT SPEF 提交 18/18 门（1.5–5.0 s）。即使慷慨挂载 FAECO 的 `1.0 × H_row` 窗口化保护后端，LR 仍在 **3/4 设计上全部失败（0.0000 µm²）**：`sky130hd/riscv32i` 240 s 局部 DRT 超时、`asap7/uart` 报 `FF:setup_budget`（−6.68 ps）与 `TT/SS:hold_regression`、`asap7/aes` 触发重试并报 `SS:hold_regression`（463.85 s）；仅在 `sky130hd/aes` 上借由 FAECO 窗口化保护后端（8.22 s 检出 17 marker→7 邻网）一次性通过全部 18 门（197.69 µm²，140.9 s，SEC 11,089/0），而同一 18 门提交在脱离 FAECO 保护后端的标准全片重布中 600 s 超时（`0.0000 µm²`）。证实 FAECO 的窗口化保护后端可作为通用物理使能器，同时增量微批次与多角物理反馈对跨设计 100% 稳定交付不可替代。[外部基线报告 §3](evidence/tcad_external_baselines_20261125/REPORT.md) · [LR 核验](evidence/tcad_external_baselines_20261125/LR_4DESIGNS_VERIFIED.json)

## 2026-11-26 几何邻网消融、四设计原生外部基线/功耗与 7 nm ASAP7 AES 独立留出

- **SKY130HD AES 几何邻网预放行消融（正反序 6 臂独验）**：固定同一 FAECO 调度、18 项池、720 RAW s 窗口与原三视图全门，正反序对照等规模几何最近邻 `geo_m1_k1`（召回 46.2%）、全覆盖接触几何 `geo_m1_r0`（召回 100%、放行 3.19×）与 FAECO 现场 DRC 诊断 `online`。两几何基线正反序合格回收均为 **0.0000 µm²**，`online` 两序均回收 **67.5648 µm²**（首达 490.07/501.25 RAW s，ODB/DEF/V/去日期 SPEF 跨序逐字节一致，SEC 11,089/0）。在完全相同的 Request 3 三门提议上，`geo_m1_k1`（3 网）因漏冲突触发重试（208.73 s）且误放保护网令 SS hold 降 10.482 ps；`geo_m1_r0`（9 网）虽 0 重试且用时更短（105.60 s），却因多放 6 条无冲突保护网同样令 SS hold 降 10.482 ps 而被拒；`online`（精确 3 网，122.75 s）使 FF/TT/SS hold 均改善（+0.049/+0.077/+0.885 ps）并全门通过。证实布线前 DRC 诊断的核心因果价值是精确锁定最小真冲突邻网集以守住多角相对 hold 边界。[几何邻网消融报告](evidence/tcad_geo_neighbor_20261125/REPORT.md) · [独立核验](evidence/tcad_geo_neighbor_20261125/AES_GEO_VS_ONLINE_VERIFIED.json)
- **7 nm 独立留出设计 `asap7/aes`（`aes_cipher_top`，22,819 实例，72% 利用率，380 ps 单时钟原 SDC）**：经 21 条局部 M3 非时钟网保护修复后取得 `hold_qualified` 共同起点（FF/TT/SS hold +35.358/+52.071/+24.664 ps、零电气、独立 DRC/天线 0、原生至修复 SEC 10,027/0）。冻结筛选 156.27 RAW s 得 18 项兼容候选。共享实时灵敏度排名 6 臂正反序（720 RAW s 纯墙钟）：同排名批处理（`fixed_online` 与 `faeco_dedup`）均回收 **0.612360 µm²**（0.0518%，6 门，SEC 10,027/0），为强单门 `single_sensitivity` **0.204120 µm²**（0.0173%，2 门）的 **3.00×**；到达共同实收 0.204120 µm²，`faeco_dedup`（414.55/417.00 s）与 `fixed_online`（418.55/401.62 s）较强单门（667.13/637.02 s）早 **220–252 RAW s**。三策略各自正反序 ODB/DEF/V/去日期 SPEF 逐字节一致。前两批直接通过未触发 hold 反馈，同排名固定三门与 FAECO 产出同一 6 门端点；16 次全块预诊断均 0 marker、均耗 44.02 s，明确给出零冲突大规模设计的全块预检时间税边界。[7 nm 独立留出报告](evidence/tcad_asap7_aes_holdout_20261125/REPORT.md) · [独立核验](evidence/tcad_asap7_aes_holdout_20261125/ASAP7_AES_HOLDOUT_VERIFIED.json)
- **四设计同口径外部基线（OpenROAD 原生 `repair_timing -recover_power 100`）、同口径功耗与 TritonSizer 预检**：在 SKY130HD AES / `riscv32i` 与 ASAP7 UART / AES 四个设计上，同版本 OpenROAD 原生回收（`native_default` 与 `-allow_setup_violations` 均一致）在真实详细重布线、RCX 与原全门验收下合格回收全为 **0.0000 µm²**（AES 120 门 SS setup −761.82 ps 且三角 hold 全退化；UART 16 门同面积替换且 FF/TT hold 退化；`riscv32i` 24 门 TT TNS 损失 5,621.11 ps 超预算 9.4× 且新增 1 处天线；ASAP7 AES 179 门 720 s 内重布线超时 `rc=124` 且报 `checkConnectivity break`）。四设计 FAECO 已验收最优端点在 TT 真实 SPEF 下总功耗、组合功耗、静态漏电全部同步下降（AES −0.036%/−0.049%/−0.022%；UART −0.660%/−2.142%/−0.777%；`riscv32i` −0.042%/−0.205%/−0.092%；ASAP7 AES −0.017%/−0.023%/−0.014%）。TritonSizer 官方归档提交 `31c4a04`（2018-12-01）强依赖 Tcl 8.4.20、旧私人 OpenSTA fork 与闭源 `sizer.tbc` 且不支持 SKY130HD，不具备同工具链接入条件。[外部基线与功耗报告](evidence/tcad_external_baselines_20261125/REPORT.md) · [TritonSizer 审计](evidence/tcad_external_baselines_20261125/TRITONSIZER_COMPAT_AUDIT.md)

## 2026-11-23 现行投稿目标

用户选定 IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems（TCAD）作为 FAECO 后布局 v3 的投稿目标。此前 2026-10-12 的 Integration 决策对应预布局历史稿。 [投稿实验计划](planning/TCAD_SUBMISSION_PLAN_20261123.md) · [GCD 资格预检](evidence/tcad_preflight_20261123/REPORT.md)

## 2026-11-25 投稿判断与交接

中文稿可围绕候选换门引入的冲突、现场 DRC 诊断与限时合格面积展开。已有工作覆盖后期换门、多角与等时限评测、局部详细布线，论文增量落在按候选实际冲突选择放行网、减少完整物理重试，以及对合格回收曲线的影响。最直接的现有机制证据是 AES 同调度同物理端点省时。UART 支撑开发设计上的面积与时间收益，riscv32i 在同榜对照中分离了批宽和未触发的反馈。跨设计同端点省时及同口径外部基线仍待验证。中文主稿和配图本轮未改。[文献与投稿判断](evidence/tcad_publication_assessment_20261125/REPORT.md) · [接手入口](HANDOFF_2026-11-25.md)

## 2026-11-25 SKY130HD riscv32i 灵敏度排序对齐

同冻结 18 项、原门与 720 RAW s，三法逐臂现场重排且同付筛选成本。正反序六臂独验通过。同榜固定三门与 FAECO 两序均回收 75.072 µm²（0.10510%），强单门均为 57.5552 µm²（0.08058%）。同实收 48.7968 µm² 时，两种批处理较单门早约 297–304 RAW s。各批处理提交四个相同累计动作，三次完整全过，末次截窗。九门最大端点的 ODB、去日期 SPEF 及三角指标一致，独立全块 DRC／天线零、SEC 4559/0。

同榜固定与 FAECO 在任何共同实收上的首达差均在 0.67 RAW s 内，两次 FAECO 未触发 hold 延后、二分或拒收缓存复用。旧 v2 现行 FAECO 从 45.0432 增至 75.072 µm²，共用排名的固定也由 52.5504 增至 75.072 µm²。该开发对照支持先统一灵敏度起序，再逐项评估调度，反馈的独立优势与跨设计迁移仍待验证。[两阶段报告](evidence/tcad_rank_alignment_20261125/REPORT.md) · [六臂独验](evidence/tcad_rank_alignment_20261125/RISCV_RANK_ALIGNED_VERIFIED.json)

## 2026-11-25 纯墙钟留出：SKY130HD riscv32i 与 ASAP7 ethmac

`riscv32i` v2 采用原约束、同在线后端、18 项冻结池和 720 RAW s 纯墙钟。六臂独验通过，两序灵敏度单门／固定批次／现行去重 FAECO 的最大合格回收均为 57.5552／52.5504／45.0432 µm²，分别占初始功能面积 0.08058%／0.07357%／0.06306%。0.01% 预设小目标由单门先到，约 139–140 RAW s；其余两法约 204–205 s。以至少 45.0432 µm² 为另一个共同阈值，现行两序约 418–419 s 先到，两种基线约 508–514 s。现行最佳端点的 SS setup TNS 退化 1287.844 ps，低于两种基线，三法最优均通过原门、独立 DRC／天线和 SEC 4559/0。

现行去重两序在第 1、3、6 次因原 setup 门拒收，约消耗 431–432 RAW s，均未触发相对 hold 重排。单动作冻结 TT TNS 相加在两个已核组合上分别高估和低估实际损失。上述排序对齐复测由该失效证据提出。`ethmac` 原生末段恢复 DRT/RCX，源约束一致且三角 hold 与 SEC 合格，原 TT／SS max slew 违规 9／1017 项且独立 DRC 止于限时，起点资格未通过，未派候选。两工艺的独立同预算优势仍未建立。[实验报告](evidence/tcad_wallclock_schedule_20261125/REPORT.md) · [SKY 完整独验](evidence/tcad_wallclock_schedule_20261125/RISCV_WALLCLOCK_VERIFIED.json) · [Ethmac 资格](evidence/tcad_wallclock_schedule_20261125/ETHMAC_CONTROL_INCOMPLETE.json)

## 2026-11-25 UART 纯墙钟开发对照

原约束 UART 共用 18 项池、在线后端和完整验收。等额计入 81.564 RAW s 筛选，每臂 720 RAW s，取消六次评估上限，四种调度正反序独验 8/8。两序的固定批次／灵敏度单门／现行去重 FAECO／交错去重 FAECO 最大合格回收分别为 0.33534／0.77274／0.83106／0.75816 µm²。现行比灵敏度单门多回收 7.547%，到同实收 0.77274 µm² 两序早 105.569／103.522 s。三个预设较小面积目标均由灵敏度单门先达。现行最佳端点两序同一，回收原功能面积的 1.051855%，最大 setup WNS 损失 1.363215 ps，原三角 hold、独立 DRC／天线及 SEC 567/0 通过。

交错两序均在第 26 次请求的 DRT/RCX 超窗，25 次完成中 14 次由 hold 拒收，比现行的 9 次多，两法都验收八个检查点。开发结果限定在所测 UART，就地冻结现行去重、固定和灵敏度单门的留出对照。独立留出收益待验证。[开发报告](evidence/tcad_wallclock_schedule_20261125/REPORT.md) · [完整独验](evidence/tcad_wallclock_schedule_20261125/UART_WALLCLOCK_VERIFIED.json)

## 2026-11-25 UART 两组六门的窄域 hold 补救

从两个原拒收 ODB 分别只开放 TT 捕获叶及两条窗内反馈网。保留原线和只清末级反馈两种做法均复现原几何、三角及 TT／SS 拒因。主动清除同一时钟叶使两项实布仅改变该叶，TT／SS hold 均下降，原门仍拒。所有实跑独立 DRC／天线零，诊断 SEC 567/0。

含范围计算，主两级追加 20.912／21.217 RAW s，连主动清叶累计 35.383／36.118 RAW s，高于旧全解锁的 33.790／33.028 s。两窄域路径及全解锁均无六门合格端点，已验收最大回收 0.26244 µm²。当前窄域规则结束于这两个固定提议的诊断，原验收门及在线部署保持。[试验报告](evidence/tcad_ibex_20261123/UART_TT_CAPTURE_WINDOW_RESCUE_REPORT.md)

## 2026-11-25 检查点重入补救的四候选验证

两个原约束设计中预先锁定四个仅因 hold 拒收、且面积潜力超过各自已核历史前沿的实布候选。从头新鲜布线均复现纯 hold 拒收，再触发两轮限域检查点重入，并按原门做完整验收。SKY130HD GCD 的一项仍为 TT／SS 拒，追加 35.227 RAW s，历史最佳保持 15.0144 µm²。ASAP7 UART 三项中，三门 `_0562_/_0601_/_0886_` 通过并复现，独立 DRC／天线零、SEC 567/0。两项六门的 SS 均过、TT 仍低于原门。

UART 验收回收 0.26244 µm²，较历史最佳 0.23328 µm² 增加 0.02916 µm²（12.5%）。成功项两段补救成本为 38.101 RAW s，UART 的三次补救合计 111.364 RAW s，两设计四次合计 146.591 RAW s。后验确认 UART 三项从头拒收的预 RCX ODB 与对应两轮检查点逐字节相同，直接重入原 ODB 后终态物理、逐角时序与原门逐项复现。三项实际追加共 102.635 RAW s，少 8.729 s；其中成功项用 35.817 s。追加时间计失败，重复确认单列。同设计取最大合格回收。当前仅保留为存在面积缺口且纯 hold 拒收时的单次备用，适用范围与触发权衡待验证。[试验报告](evidence/tcad_ibex_20261123/HOLD_REENTRY_RESCUE_REPORT.md)

## 2026-11-25 GCD 两轮限域布线状态重入

同一冻结 GCD 起点、原门、两项同面积候选，正反序与从头完整布线配对。同进程续跑四次均无最终可验收产物。新进程由检查点重入，452 条保护网解锁前后几何与导引一致，沿用 pin access，第二次 DRT 从第 3 轮恢复初始标记。新进程矩阵八次均完成三角、独立全块 DRC 与天线检查和 SEC，DRC／天线均零、SEC 262/0。

含全部检查的正／反序从头用时 27.475／27.474 RAW s，重入用时 29.557／29.572 RAW s，分别多 2.082／2.097 s。`_091_` 两序从 TT／SS 相对 hold 拒收转为通过，重复得到同一新物理端点，回收 11.2608 µm²，TT／SS hold WNS 分别提高 0.533990／1.869893 ps。`_093_` 两法均过原门，规范化几何、去日期 SPEF、三角结果一致。检查点重入作为备用物理实现保留，部署条件和触发成本待独立验证。[配对报告](evidence/tcad_ibex_20261123/GCD_LOCAL_ROUTE_REENTRY_REPORT.md) · [独立核验](evidence/tcad_ibex_20261123/GCD_ROUTE_CHECKPOINT_AUDIT.json)

## 2026-11-25 GCD 限域与增量寄生预筛未过放行门

在历史同冻结起点和原门下，新鲜完整后端正反序复现 `_091_` 的 TT／SS 相对 hold 拒收和 `_093_` 的正式验收，两完整评估用时 21.568／21.628 RAW s。dirty GRT 原估计经零编辑校准与直接网比例写回冻结 SPEF 均误收 `_091_`。两轮保护外网的限域 DRT，以及不保护外网的 0／2 轮早停，均误拒 `_093_`。限域两筛加完整验收用时 30.117／29.950 RAW s；不保护外网的两次初始 DRT 预览也超过可省的完整拒收花费。

在正序 `_093_`，0 到 2 轮的关键 TT/SS 路径网几何与总电容一致，完整详细布线后 `clk`／`clknet_0_clk` 发生几何变化，总电容由 10.79950／13.35230 降至 9.91285／13.09290 fF。该对照支持将后段实布寄生变化纳入后续诊断。这些预筛均未满足原 TT／SS 的正确区分与同机净收益双门，维持真实完整验收和现行派发。[试验报告](evidence/tcad_ibex_20261123/GCD_LOCAL_HOLD_PREVIEW_REPORT.md)

## 2026-11-25 布线前几何 hold 风险的开发核对与 GCD 转移

冻结评分只依赖派发前路由几何和此前已通过端点的最小路径。UART 正式物理候选去重为 18 个，SS 8 拒、10 过，时钟几何 AUC 0.9125，直连电容 0.7625。去掉与已知对照重合的正式候选后，时钟几何 AUC 0.9143。末次只读重放选择此前定向试通过的 `_0886_`，该读数沿用已有候选验证。

同公式转移到 9 个 GCD 历史同后端物理候选，TT、SS 各 6 拒 3 过，时钟几何 AUC 0.75。零几何分包含三次拒收和三次接受，等面积的拒收 `_091_` 与通过 `_093_` 也同分。后验用电容破同分未改善关键等面积比较。生产调度和原门继续沿用，独立在线同预算效果待有判别力的派发规则。[UART 开发报告](evidence/tcad_holdout_20261123/UART_HOLD_GEOMETRY_REPORT.md)

GCD 同分两点的 TT／SS 双向 SPEF 与网表交换中，替换实布 SPEF 重现真实 hold WNS 差 −0.497075／−1.869893 ps，只换网表和交互效应均为零。各角内部最差路径以及寄生注释计数一致。两点实布更改了 `clk` 和 `clknet_0_clk` 的几何，当前预筛仅输入预计重布的直连信号网。两个工艺各有一项端点对证实实布寄生足以重现原门结果，低成本预筛仍需在明确的排序任务和实际验证成本下评估。[GCD 交换结果](evidence/tcad_ibex_20261123/GCD_HOLD_GEOMETRY_EXCHANGE.json)

## 2026-11-25 ASAP7 UART 末次预留的同预算六臂对照

在同一冻结原约束起点、18 候选和在线后端，将现行去重、末次预留、在线固定按正反序各跑一次。各臂计共同筛选 81.564 RAW s，均完成六次实际候选评估，0.01% 均在第三次达到。两序的最大合格回收为在线固定 0.23328、去重 0.20412、末次预留 0.14580 µm²。

末次预留按冻结规则把一次机会给原相对 hold 拒收后延迟的候选。面积同分时，既有电容优先级使两序均选 `_0562_`，累计候选能减少 0.23328 µm² 面积，但 SS hold WNS 相对损失 0.008424 ps 超过 0.001 ps 原容差。两次正式拒收，面积以此前已通过的两门计算。规则在已读 UART 开发设计上复现了劣化，后验 `_0886_` 的合格端点仍是下文的定向证据。[六臂报告](evidence/tcad_holdout_20261123/UART_DEFERRED_RESERVATION_REPORT.md) · [独立核验](evidence/tcad_holdout_20261123/UART_DEFERRED_RESERVATION_VERIFIED.json)

独立的七次 SS STA 用原 SDC、同 SS RVT 库，将候选网表和实际 SPEF 在同两门参考处交换。只换候选网表时，两组 SS hold WNS 均为参考 54.060298 ps；只换 SPEF 就分别复现 `_0562_` 的 54.044491 ps 和 `_0886_` 的 54.061783 ps。原约束的 54.051915 ps 门可区分真实结果，此处冻结参考寄生的指标把两候选均判通过。原调度和验收门沿用。低成本几何风险或增量寄生反馈的排序收益需同预算实证。[交换探针原件](evidence/tcad_holdout_20261123/UART_HOLD_EXCHANGE_RESULTS.json)

## 2026-11-25 ASAP7 UART 后验定向三门达到既有固定面积

使用同冻结布线、原三角时序、同在线物理后端，单独验证 `_0814_`／`_0886_`／`_1027_`。该候选实际回收 0.23328 µm²，等于既有固定四门面积，最大逐角 setup WNS 损失 0.042272 ps，无新增负 setup，独立 DRC 和天线 0，SEC 567/0。在读取既有轨迹后，仅做一个事后定向验证。自动调度的同预算结果仍见去重 ABBA。[物理核验](evidence/tcad_holdout_20261123/UART_FIXED_AREA_PROBE_VERIFIED.json)

## 2026-11-25 ASAP7 UART 去重的正反序实物验证

原 FAECO 与去重 FAECO 共用冻结 UART 起点、原三角与 18 候选，每臂计同一筛选和 720 RAW s，均完成 6 次实际物理评估。去重只复用同臂具备完整物理测量且仅因 setup 超预算的累计拒收。两轮各复用一次，第 6 次均新验收同一三门，面积从原调度的 0.14580 提升至 0.20412 µm²（总功能单元面积的 0.25835%），仍比历史在线固定四门 0.23328 µm² 少 0.02916 µm²。

对应 0.14580 µm² 的同两门端点，去重第 5 次比原调度第 6 次早 24.147／23.504 RAW s。预设 0.01% 阈值各臂均在第 3 次，位于首次复用之前。新三门符合原时序、电气、独立 DRC、天线与 SEC，各序独立复核，SEC 567/0。[配对报告](evidence/tcad_holdout_20261123/UART_REJECTION_DEDUP_REPORT.md) · [独立核验](evidence/tcad_holdout_20261123/UART_REJECTION_DEDUP_VERIFIED.json)

## 2026-11-25 SKY130HD GCD 固定提议的保护路由对照

常规、在线、在线、常规四臂各正式评估同一三门，各两次实际 DRT/RCX，其中一次为重试。两次在线预诊断耗 0.715／0.910 RAW s，均无标记。初次实际布线后四臂独立全块 DRC 均有相同 3 处 `net242`／`net266` met1 短路。按标记放行同一 `net242` 重布后均清零，TT 相对 hold WNS 损失 0.022621 ps，超过预设 0.001 ps 容差。四臂最终合格回收均为 0。[正式报告](evidence/tcad_ibex_20261123/GCD_MARKER_MECHANISM_REPORT.md) · [四臂独立核验](evidence/tcad_ibex_20261123/GCD_MARKER_MECHANISM_VERIFIED.json)

现行保护流程与早期 GCD 合格配对共用三门提议和原约束，本轮增加固定邻线与独立 DRC。两种流程的物理版图不同。在线预诊断可识别某些候选替换直接引起的冲突，GCD 多次复跑表明后续详细布线引起的冲突仍需正式检查。[历史对照](evidence/tcad_ibex_20261123/INCIDENT_CAP_PRIORITY_REPORT.md)

## 2026-11-25 AES 同在线后端的灵敏度单门扩展

同一 18 门、原 I/O、冻结布线起点、720 RAW s 与六次逻辑请求上限。灵敏度单门按冻结 TT 输出引脚裕量的去顶权重排序，每臂重新查询且计入硬窗；FAECO 采用原批宽、相对 hold 反馈与触达电容顺序。正反序四臂独立核验。

| 派发 | 正序／反序 0.01% 首达 / RAW s | 正序／反序首次回收至少 33.7824 µm² / RAW s | 两序各自最大合格回收 / µm² |
|---|---:|---:|---:|
| TT 灵敏度单门 | 489.515／497.493 | 619.296／629.378 | 33.7824 |
| FAECO | 472.398／477.342 | 472.398／477.342 | 67.5648 |

0.01% 为预设共同阈值，两臂都在请求 3 首达，FAECO 主要少做一次 SEC。33.7824 µm² 是从相同验收前缀重读的共同绝对面积，FAECO 早 146.899／152.036 RAW s。窗口最优单门新增一个 SS 负 setup，FAECO 无新增，均符合原验收门及 SEC 11089/0。批宽、反馈与排序的独立贡献仍需消融。[配对报告](evidence/tcad_ibex_20261123/AES_SENSITIVITY_GREEDY_REPORT.md) · [独立核验](evidence/tcad_ibex_20261123/AES_SENSITIVITY_GREEDY_VERIFIED.json)

## 2026-11-25 中文 v3 工作稿阶段记录

本地 16 页中文草稿已纳入 UART 去重 ABBA、AES 灵敏度单门和 GCD 诊断边界。LuaLaTeX 双遍后逐页核对，草稿源码、PDF 和补丁保存在 `scratch/tcad_ibex_20261123/manuscript_uart_dedup_20261125/zh/`。按用户最新要求先推进实验，仓库主稿源码和三份 PDF 保持 `6a79448b` 的 15 页版本；实验阶段提交实验文件和证据。[仓库中文稿](../paper/zh/FAECO_v3_后布局可调预算面积回收.pdf)

## 2026-11-25 ASAP7 UART 原约束下完成三种在线调度正反序比较

三法共用原约束的已布线冻结起点、18 个预筛候选和在线物理后端。每臂计筛选 81.564 RAW s，使用 720 RAW s 与六次实际请求上限。各臂均到达六次上限，720 s 时限均有剩余。FF／TT／SS 使用原三角，setup WNS 允许损失 2.7 ps，绝对与相对 hold、电气、独立 DRC、天线和 SEC 沿共同门。

| 派发 | 正序／反序 0.01% 首达 / RAW s | 两序各自窗内最大合格回收 / µm² |
|---|---:|---:|
| 原序单门 | 152.165／151.161 | 0.17496 |
| 在线固定批次 | 152.778／152.067 | 0.23328 |
| FAECO | 151.795／152.289 | 0.14580 |

三种最优端点跨序复现，均逐角过门、独立 DRC 与天线为零、SEC 567/0。36 次在线诊断均无 marker、邻网释放或重试。FAECO 的回收低于两种基线，首达次序跨序变化；两次均重复验证同一个 FF setup 拒收三门，二分后累计身份还原是明确的候选配额损耗，已登记 OI-106。此轮表明现行后端与验收可迁移至 UART，UART 没有触发可测的诊断重试收益。[实验报告](evidence/tcad_holdout_20261123/UART_ONLINE_REPORT.md) · [独立核验](evidence/tcad_holdout_20261123/UART_ONLINE_VERIFIED.json)

## 2026-11-25 中文 v3 稿与 TCAD 投稿评估

- 现行中文 v3 以布线后局部冲突诊断和限时面积回收为主线，分别报告 AES 同端点后端收益、同后端单门比较和固定批次首达。加入 CoRe-ECO 的机制对照、SKY130HD Ibex 时序退化归因和 ASAP7 UART 原约束起点资格。双遍 LuaLaTeX 后 15 页、6 幅现有 ImageGen 示意、18 表、22 条参考文献，三份 PDF 逐字节一致。[中文工作稿](../paper/zh/FAECO_v3_后布局可调预算面积回收.pdf)
- 选题符合 TCAD，建议补齐投稿前关键证据。以独立设计继续检验现行诊断与调度，加入同后端灵敏度排序单门，分别量化候选批宽、反馈排序和诊断的收益。跨设计验证与强对照归 OI-105。[投稿成熟度评估](../paper/zh/review_rounds/r20261125_tcad_readiness/REVIEW_REPORT.md)

## 2026-11-24 AES 同在线后端的 FAECO 与单门贪心正反序

同一冻结起点、同一 18 动作池、同一在线诊断和物理后端。每臂计入共同筛选 113.363 RAW s、原 3.6 ns 与 I/O、720 RAW s 硬窗、6 次逻辑请求上限，应用相同三角 setup／hold、电气、独立 DRC、天线和 SEC 门。

| 派发 | 正序／反序 0.01% 首达 / RAW s | 两序 720 RAW s 内最大合格面积回收 / µm² |
|---|---:|---:|
| 原序单门贪心 | 607.806／599.796 | 22.5216 |
| FAECO | 469.963／471.424 | 67.5648 |

两种策略各自跨序复现相同的首达和最优物理端点。FAECO 试到第 3 次达阈值、单门第 4 次达阈值，实际首达分别回收 33.7824／22.5216 µm²。两种策略均完成四次请求并接受两次，FAECO 的两次接受合计六个动作，单门接受两个。该结果支持 AES 上相对原序单门贪心的联合调度收益。同后端固定批次在前轮首达最快，独立设计和排序／批处理分量仍需配对量化。[配对报告](evidence/tcad_ibex_20261123/AES_ONLINE_GREEDY_REPORT.md) · [独立核验](evidence/tcad_ibex_20261123/AES_ONLINE_GREEDY_VERIFIED.json)

## 2026-11-24 ASAP7 UART 原生起点资格

- ORFS 原生 UART 完成详细布线、寄生提取和原约束三角检查，周期 270 ps、I/O 54 ps、虚拟时钟延迟 66.270 ps。FF／TT／SS hold WNS +50.315／+67.502／+54.053 ps，hold TNS 均为 0。setup WNS +25.853／−39.580／−199.705 ps；TT、SS 的负 setup 余量须在后续协议中以共同起点为参照。
- 原生和独立检查的 DRC、天线均为 0，三角最大转换时间和最大电容违规均为 0，冻结网表自 SEC 567/0。原设定下的冻结 CONTROL 具备进入搜索比较的起点资格。候选派发、候选 DRT/STA/SEC 均为 0，跨设计性能仍待正式对照。[制备报告](evidence/tcad_holdout_20261123/UART_CONTROL_RUN.md) · [独立核验](evidence/tcad_holdout_20261123/UART_CONTROL_VERIFIED.json)

## 2026-11-24 原生 JPEG 起点资格

- SKY130HD JPEG 原生制备实际完成详细布线、两轮原生天线修复及 RCX，最终 DRC 和天线为 0。原 5 ns、1 ns I/O 与原时钟关系在最终端点核对一致。FF／TT hold WNS +218.048／+357.532 ps；SS hold WNS/TNS −2,340.727／−41,475.257 ps，原生冻结起点资格拒收。最差为异步 reset removal，另一个常规输入 D 端 hold −1,256.375 ps。未启动候选、未计策略结果。[资格报告](evidence/tcad_holdout_20261123/JPEG_CONTROL_REPORT.md) · [资格登记](evidence/EXPERIMENT_REGISTRY.md#2026-11-24-tcad-sky130hd-jpeg-original-control-qualification-v1)

## 2026-11-24 AES 调度 × 物理后端 2×2 与交换顺序复跑

同冻结起点和原筛选池，四组合按正反两种顺序全新实跑，各臂保留原 I/O、三角 setup/hold、电气、独立 DRC、天线和新 SEC，硬窗 720 RAW s、面积目标 0.01%、6 次请求上限。四个条件各自的首达与最优跨序都复现同动作、ODB／DEF／网表、去日期 SPEF 和完整三角验收。以下耗时含相同筛选收费与各臂真实准备、诊断及工具。

中文主稿以同墙钟下的最大合格面积回收为主指标，以达到共同面积目标的时间为配对指标。十个小电路的贪心对照按相同重布线评估次数上限报告。

| 派发与后端 | 正序／反序首达 / RAW s | 两序窗内均回收 / µm² |
|---|---:|---:|
| 固定＋常规 | 448.639／443.274 | 33.7824 |
| 固定＋在线诊断 | 364.633／370.875 | 33.7824 |
| FAECO＋常规 | 641.814／648.247 | 33.7824 |
| FAECO＋在线诊断 | 483.860／483.867 | 67.5648 |

- 固定同派发切在线时，正反序同端点首达各早 84.006／72.399 RAW s；FAECO 同派发切在线时各早 157.954／164.380 s。在线后端内固定首达更早，FAECO 在 619.309／620.070 RAW s 分别获相同六门、窗内合格面积多 33.7824 µm²。常规后端内 FAECO 更晚且窗内面积持平，四次常规臂第 4 次均在 DRT 截停。分项开销解释了这次同电路组合效应，跨设计仍待验证。
- 六门的三角 hold WNS 均改善、hold TNS 为零，原 setup 预算合格、无新增负 setup、独立全块 DRC 与天线为 0、SEC 11089/0。正反序第五次在线 FAECO 各在 SS／TT STA 截停，旧冷启动九门的 98.8448 µm² 仍是另一轮的窗外证据。[2×2 正反序报告](evidence/tcad_ibex_20261123/AES_FACTORIAL_REPORT.md) · [独立核验](evidence/tcad_ibex_20261123/AES_FACTORIAL_VERIFIED.json)

## 2026-11-24 无旧候选报告的 AES 冷启动在线 ECO

- 诊断对当前候选在冻结 ROUTED 布局真实换门并清除直连旧线，以单线程全块 DRC 当场读取可归属标记。原同六门实际预检 14.367 RAW s 复现八个完整后续标记，保留其直连旧线的对照多 30 处旧线标记，冻结零动作报告为空。在线每次诊断均计费，只在完整非空报表且各标记都有可操作信号邻网时预放行。最终拟验收端点还需原三角、实际提取、独立恢复 ROUTED 的全块 DRC、天线与 SEC。
- 同机串行固定／在线固定／在线 FAECO，原 720 RAW s、0.01%、原筛选池与三视图门。固定→在线固定只改物理诊断：在相同的第二个请求接受同一 33.7824 µm² 端点，含筛选首达 429.504→358.364 RAW s（−16.56%），实时诊断两次共 28.531 RAW s 已计。在线固定窗口内完成 5 次，纯固定 3 次，合格最优面积相同。
- 同在线物理后端下，FAECO 第 3 次于 476.504 RAW s 首达 33.7824 µm²，晚于在线固定；第 4 次却在 609.356 RAW s 以完整三视图、独立 DRC 0、天线 0、SEC 11089/0 合格，累计回收 67.5648 µm²（0.057992%）。该点三角 hold WNS 都改善、没有新增负 setup 端点。旧 v3 曾因这组非法初评布局的 SS hold 下降跳过其重试，当前实际修复验证此组可行。最后启动的第五次在独立检查被截停，不计正式回收。三臂测量限于本设计和本顺序。[冷启动矩阵报告](evidence/tcad_ibex_20261123/AES_COLD_ONLINE_REPORT.md)
- 第 5 次当时实际完成 DRT、RCX 和三角 STA；窗外对精确原产物补真实独立 DRC、天线和 SEC 11089/0，各门合格，回收 98.8448 µm²（0.084840%），TT 新增 1 个负 setup 且原预算内。该点有独立资格，自身在原 720 s 未完成验收，正式矩阵仍为 67.5648 µm²。[冷启动矩阵报告](evidence/tcad_ibex_20261123/AES_COLD_ONLINE_REPORT.md) · [独立核验](evidence/tcad_ibex_20261123/AES_COLD_ONLINE_VERIFIED.json)

## 2026-11-24 已有 DRC 诊断输入的同六门 ECO 组件对照

- 新入口用动作请求、物理收据及完整的独立全块 DRC 证据绑定原矩阵、SDC 和候选几何，由可归属的标记提取非时钟信号邻网。缺少任一标记的可操作邻网时回到常规初试及标记重试；真正新增标记仍可触发原有的一次重试。驱动根据输入计算动作和邻网，当前物理调用由已验证的 AES 后端执行。
- 冻结同一六门、同机同核按常规→预放行→预放行→常规实跑，均保留 720 RAW s、0.01% 目标、原 I/O、三角时序及物理／SEC 门。含相同筛选，正序和反序首达分别 335.523→231.616 RAW s、333.166→231.123 RAW s（−30.97%、−30.63%）。每组从两轮 DRT/RCX、三角 STA 和独立全块 DRC 降为一轮。四臂均回收相同 65.0624 µm²（0.055844%），ODB／DEF／V、去日期 SPEF、三角结果相同，独立 DRC 与天线为 0，SEC 11089/0，TT 和 SS 各新增一个负 setup 端点，原预算通过。
- 提前放行的证据来自已有同候选失败布线与独立检查，两次实际读取和映射耗 0.067 RAW s 左右，均进入计时。若开始时无诊断，须另计产生该布线和标记的代价。同输入四臂证明组件重复验证支出可减少，跨候选自动获取诊断与跨电路物理效果仍待检验。[组件对照报告](evidence/tcad_ibex_20261123/AES_DIAGNOSTIC_REPAIR_REPORT.md) · [独立核验](evidence/tcad_ibex_20261123/AES_DIAGNOSTIC_REPAIR_VERIFIED.json)

## 2026-11-24 AES 真实 DRC 标记定向修复与同硬窗对照

- 上轮 v3 比 v2 固定首达多 76.952 RAW s。首达前多做一个失败中间批的初始物理验证；分项差异 DRT/RCX +51.921 s、三角 STA +8.969 s、独立全块 DRC +13.016 s。次序、阶段数和原收据可独立核对，秒数来自两次实际运行。
- 由 v3 第 5 次独立全块 DRC 的 6 个短路、2 个间距问题定位四条非时钟邻网。保持完整排名 4、6、12、13、16、17 从冻原重布线，单独试验和新正式运行都只改变这四网加 20 条直接数据网，15,633 条保护网几何未变，各通过独立全块 DRC 0、天线 0、原三角联合门和 SEC 11089/0。定向正式六门回收 65.0624 µm²（0.055844%），三视图 hold WNS 改善 +0.059064/+0.092537/+0.937028 ps，TT、SS 各有一个新增负 setup 端点，原 tradeoff setup 预算通过。
- 新一轮同机串行、0.01% 目标、720 RAW s 硬窗。首两批采用同样的动作，定向第 2 次直接按历史标记放开两条邻网。固定和定向达标均为第 2 个请求、同一 33.7824 µm² 物理端点；含筛选首达 434.356→332.365 RAW s（实测少 101.991 s，23.48%），少一次原有 DRC 失败的初次物理验证。硬窗最优从固定 33.7824 到定向 65.0624 µm²，定向六门第三次于 454.205 RAW s 通过。定向只计划三次，输入含 AES 旧标记和已选六门，首次物理、独立 DRC、三角及 SEC 均新跑并计成本。这是本设计的定向物理修复验证。[AES 定向修复报告](evidence/tcad_ibex_20261123/AES_MARKER_REPAIR_REPORT.md) · [配对核验](evidence/tcad_ibex_20261123/AES_MARKER_REPAIR_VERIFIED.json)

## 2026-11-24 初次相对 hold 延后后的触达电容排序对照

- 同一候选池内，原 FAECO 的两个相对 hold 拆分请求被延后，六次预算耗尽前未重访，实际仍走固定批次。新规则以真实相对 hold 触发，只按原冻 DEF/SPEF 触达网电容和面积一次重排未评估候选；保持共同起点、原 I/O 和三角联合门、单次 pin access、6 次调用、720 RAW s 与 0.01% 目标，实际准备时间计新臂。
- Ibex 两臂新跑均在 720 RAW s 完成 4 次，均正式回收 43.792 µm²（0.030282%）。同一 22.5216 µm² 目标由固定第 3 次提前至新臂第 2 次，含筛选和新臂特征准备 435.254→368.345 RAW s（减少 66.909 s，15.37%）。新臂达标端点无新增负 setup。窗内同面积点的 SS hold WNS 高 3.330 ps、SS setup TNS 较固定低 78.129 ns，新增负 setup 固定 0、新臂 SS 1。六次最优 62.56→68.816 µm²，额外回收发生在 720 s 之后。[Ibex 独立核验](evidence/tcad_ibex_20261123/IBEX_INCIDENT_CAP_PAIR_VERIFIED.json)
- GCD 转移中，两臂均在第 5 次达标，含筛选首达 94.279→94.451 RAW s，窗内均完成 6 次。新臂第 6 次换用一个不同单门，最优面积回收 11.2608→15.0144 µm²（0.234742%→0.312989%），三角 hold 和原 setup 预算通过、SEC 262/0，新增 TT 负 setup 一个。两设计均按固定→新臂各跑一次，同机各有分配的 CPU 组。首达耗时差用该顺序的实测值描述。[GCD 独立核验](evidence/tcad_ibex_20261123/GCD_INCIDENT_CAP_PAIR_VERIFIED.json) · [触达电容报告](evidence/tcad_ibex_20261123/INCIDENT_CAP_PRIORITY_REPORT.md)
- AES 共同保护后端的 720 RAW s 硬窗对照 v2，两臂各派发 4、完成 3，固定第 2 次、新臂第 3 次首次回收 33.7824 µm²（0.028996%），含筛选和实测准备分别 447.229／622.069 RAW s。优化次组因 FF/TT 相对 hold 拒收，第 3 组重试后通过原 setup／hold、独立全块 DRC 与天线为 0、SEC 11089/0，且新增 SS 负 setup 1 个。v1 优化臂的截停异常保留为不完整记录。v2 的真实窗尾截停能生成核验终态，在计算时间和预算内回收时以 v2 整对为准。[AES 配对报告](evidence/tcad_ibex_20261123/AES_INCIDENT_PRIORITY_MATCHED_REPORT.md)
- AES 后续按初始相对 hold 延后部分重试的 v3 单臂，保留原联合验收，在 524.181 RAW s 复现 v2 优化同一 33.7824 µm² 候选和 SEC 11089/0。观察比 v2 优化提前 97.888 s，仍晚于 v2 固定 76.952 s。实际省去 v2 已实测仍拒的第 2 组重试，新臂在窗内也访问了更多请求，最终合格面积相同。第 4 次六门重试未测，第 5 次的 65.0624 µm² 候选窗外独立补审发现 8 个 DRC 标记并拒收。v3 此次为已观测设计上的开发臂。[AES 配对和重试报告](evidence/tcad_ibex_20261123/AES_INCIDENT_PRIORITY_MATCHED_REPORT.md)

## 2026-11-24 AES 正式排名 4–9 候选的独立等面积修复

- 窗外完成后被拒的排名 4–9 六门，以正式合格的排名 4–6 三门作对照。12 次交叉 STA 显示，原候选的 SPEF 精确复现三角 hold 下降，FF/TT 同时发射提前、捕获延后。现场保护时钟网几何时，提取的捕获分支电容增加 0.0000792 pF。基于同层邻近性与已有单门的发射时钟趋势，把 `_13098_` 等面积换为 `_21033_`，其余五门保持。新端点从同冻结起点一次完成物理验收，回收 67.5648 µm²（0.057992%），相对冻结起点 FF/TT/SS hold 改善 +0.063172/+0.098699/+0.653255 ps，解锁态全块 DRC、天线为零，SEC 11089/0。
- 替换保留原 setup 预算，TT 新增两个负 setup 端点，SS 新增一个。配对路径复检确认捕获分支原电容增量消失且发射分支电容增 0.0001006 pF。137.851 RAW s 为单次定向替换的真实验证，原 720 s 比较与原排位不变。该端点和此前等面积手选合并是不同动作证据。[排名 4–9 归因与修复](evidence/tcad_ibex_20261123/AES_RANK4_9_HOLD_REPAIR.md)

## 2026-11-24 统一单次 pin access 的 Ibex 与 AES 正式对照

- Ibex 原冻结起点、统一有序筛选池与单次 pin access，三臂各六次独立实跑并计入四路筛选的 77.493 RAW s。单门／固定／FAECO 在 720 s 窗内完成 5／4／4 次、回收 0／43.792／43.792 µm²；六次最终回收 7.5072／62.56／62.56 µm²。固定与 FAECO 都在第 3 次以 22.5216 µm² 达到 0.01% 目标，含筛选首达 452.492／454.058 RAW s，首达端点三角无新增负 setup，SEC 13648/0。两者六次轨迹和逐次物理结果均相同，观测时间对应一次串行次序。[Ibex 正式报告](evidence/tcad_ibex_20261123/IBEX_SCREENED_THREE_WAY_REPORT.md)
- AES 原冻结起点、原有序池，三方法共用保护与真实 DRC marker 放行规则。720 RAW s 硬窗内单门／固定／FAECO 分别完成 3／2／2 个逻辑评估，各启动 5 次物理 route，累计 12 次完成 DRT/RCX、36 视图 STA、3 候选 SEC。正式回收 11.2608／33.7824／33.7824 µm²。固定与 FAECO 在相同的第 2 次自动放行两数据邻网后通过原门与 SEC 11089/0，含筛选首达 532.099／529.887 RAW s。两臂前三个实际派发及已验收物理端点一样，首达差异按一次顺序观察。共同第 3 次六门重试被窗末截停，窗外完整诊断 67.5648 µm² 的候选仍因 FF/TT 相对 hold 退化拒收。先前手选六门证据和本次硬窗结果分别记录。[AES 正式报告](evidence/tcad_ibex_20261123/AES_PROTECTED_ONLINE_REPORT.md)

## 2026-11-24 单次 pin access 冻结搜索与 ODB 重入前置验证

- GCD 原冻结起点 hold-aware 搜索在同机串行 A→B→B→A，各 6 次调用。A 为默认双次 pin access，B 为显式单次。四臂均在第 5 次达到同一 11.2608 µm² 面积回收，SEC 262/0。含同一历史筛选成本，顺序交换两对的双次／单次首达分别为 122.989／118.740 RAW s、118.933／113.860 RAW s，实测节省 4.249／5.073 s。24 个候选的动作、拒因、DEF/V、去日期 SPEF、三角全量时序和证明保持一致，单次原始 ODB 字节仍有差异。后续正式 SKY130 嵌入导引冻结起点对照对各方法统一显式启用 `--single-pin-access`，原默认值、外部导引入口和既有实验继续按各自对应配置。更广矩阵尚未开始。[搜索报告](evidence/tcad_ibex_20261123/PIN_ACCESS_SEARCH_REPORT.md)
- 保存中间 ODB 后，各设计按 A→A、B→B、A→B、B→A 续做一个固定动作组，同一设计的四组 DEF/V、去日期 SPEF、三视图时序、电气和验收相同。GCD 四组均回收 15.0144 µm²（0.312989%，SEC 262/0），三角 hold 均改善，原从冻结起点直接累计相同动作的端点因 TT/SS 相对 hold 拒收。Ibex 四组均因 TT 新电容违例及 TNS 损失 1029.633 ps 超出 1000 ps 限额而拒，6 个新增负 setup 端点，另做诊断 SEC 13648/0；原冻结起点累计同六门通过。保持路由起点策略对照独立，后续全矩阵沿同一冻结起点评估。[重入报告](evidence/tcad_ibex_20261123/PIN_ACCESS_REENTRY_REPORT.md)

## 2026-11-24 筛选并行、物理组件对照与 AES 残余 hold 优化

- Ibex/GCD 的冻结 SPEF TT 筛选使用单线程独立候选探针的有界四路并行，复现原有的精确探针序列和有序池。Ibex 1→4 路在新增一次配对中用时 131.941→77.493 RAW s，减少 41.27%。GCD 两组交换顺序分别为 50.709→37.271 s、51.952→39.206 s，减少 26.50% 和 24.53%。六臂各设计探针数不变，合计 116 次。该时间对应完整筛选预处理与探针，物理搜索另有其原实跑证据。[筛选报告](evidence/tcad_ibex_20261123/SCREEN_WORKERS_BENCHMARK.md)
- 去掉显式重复 `pin_access` 并保留 DRT 自带步骤时，GCD 两对单个物理端点评估时间减少 3.101／3.449 RAW s，Ibex 减少 46.727／22.067 RAW s。各设计四臂均通过原联合门和 SEC，DEF、V、去日期 SPEF、DRC、逐角时序和实际改线一致。GCD 仅保留显式调用的补充方式产生相同的单次调用 ODB。读回的接入点多重集相同，仅在诊断副本删除接入点及其引用后两方式 ODB 才一致。原冻结搜索配方沿用，组件时间差与原对象不一致分别报告。[pin access 对照](evidence/tcad_ibex_20261123/PIN_ACCESS_AB_REPORT.md)
- AES 原第 5 次的残余 hold 降幅经 12 次交叉 STA 确认为候选寄生变化。原三门的三个两门子集均未通过三视图相对门。以已有单门的发射支路时序为线索替换一门后，实际净回收 33.7824 µm²（0.028996%），三角 hold 均改善，无新增负 setup 端点，解锁态全块 DRC、天线均为 0，SEC 11089/0。再与前轮独立合格三门合并，重新实跑回收 67.5648 µm²（0.057992%），三视图 hold 变化 +0.049183/+0.076716/+0.782263 ps，解锁态全块 DRC、天线为 0，SEC 11089/0。六门在原 tradeoff 口径下新增一条 SS 负 setup 端点，slack 从 +0.329958 ps 到 −0.214495 ps，两项为追加定向修复端点。[AES 残余 hold 优化](evidence/tcad_ibex_20261123/AES_RESIDUAL_HOLD_OPTIMIZATION.md)

## 2026-11-24 调度覆盖与 AES 路由修复验证

- 显式启用的原因感知调度在三角相对 hold 拒收时延后拆分，并保留原联合门。在原冻结筛选池实跑，Ibex 与 GCD 各六次，覆盖到原 FAECO 错过的合格动作。Ibex 在含筛选 652.022 RAW s 达到 22.5216 µm²（0.015574%，SEC 13648/0），六次内回收 62.56 µm²。GCD 在 154.336 RAW s 达到 11.2608 µm²（0.234742%，SEC 262/0），也是六次内最好。两者首达端点三视图均无新增负 setup 端点，六次动作和物理端点均与各自原固定臂相同。原固定臂在不同实验负载下分别用时 562.523 和 146.249 RAW s。两条原 ASAP7 setup-only 轨迹用现版本只读回放，保留原拆分和 0.26244 的面积减量。新调度尚需独立设计实测。[调度报告](evidence/tcad_ibex_20261123/HOLD_AWARE_REPAIR_REPORT.md)
- AES 的未编辑网保护恢复了零编辑在三角的原 setup/hold WNS/TNS。对原第 2 次按实际全块 DRC 释放两条非时钟邻网，实测保护的 15,646 条网均未变，实际回收 33.7824 µm²（0.028996%）。FF/TT/SS hold 变化 +0.000056/0/+0.610845 ps，恢复 ROUTED 类型后的全块 DRC 与天线为零，SEC 11089/0。依据原 tradeoff setup 门验收，SS 新增一条负 setup 端点，slack 从 +0.329958 ps 到 −0.228706 ps。原第 5 次对照的三视图相对 hold 仍不合格。当前有一个定向修复的验收端点，原六臂矩阵的统计沿原报告。[AES 保护路由报告](evidence/tcad_ibex_20261123/AES_SELECTIVE_DRT_REPAIR.md)

## 2026-11-24 SKY130HD 候选筛选、同预算消融与留出验证

- Ibex、GCD、AES 各完成两种排序 × 三种调度 × 六次物理验证。三套矩阵共 108 次 DRT/RCX、324 次视图 STA、5 次候选 SEC、0 次缓存。按原 I/O/SDC、三视图 1% 周期的 WNS 预算及登记的 TNS 门，正式验收仍要求 hold 非负且相对原 CONTROL 非退化、DRC=0、电气无新增违例和非空两态 SEC。清单包含每个候选的绝对裕度、原端点差值和新增负 setup 端点。各筛选臂的 720 RAW s 预算全额计入本设计的固定 SPEF TT 筛选时间。三设计的原面积排序均回收零。两种排序各 54 次，TT WNS 或 TNS 超预算的计数为 45／0。[总报告](evidence/tcad_ibex_20261123/SCREEN_ABLATION_REPORT.md) · [实验登记](evidence/EXPERIMENT_REGISTRY.md#2026-11-23-tcad-sky130hd-screen-ablation-holdout-v1)
- 计入筛选后，只有固定批次达到 0.01% 面积目标。Ibex 在 562.523 RAW s 的第三次候选验收回收 22.5216 µm²（0.01557%，SEC 13648/0），六次前缀回收 62.56 µm²（0.04326%）。Ibex 筛选单门第六次回收 7.5072 µm²，完成时间 923.421 RAW s。GCD 留出在 146.249 RAW s 的第五次验收回收 11.2608 µm²（0.23474%，SEC 262/0），也是六次内的回收。Ibex 与 GCD 的达标端点三视图均无新增负 setup 端点。三设计 FAECO 在六次与 720 s 均回收零。AES 留出六臂均回收零，冻结筛选的 18 个候选均只因相对 hold 拒收。[Ibex 核验](evidence/tcad_ibex_20261123/SCREEN_MATRIX_IBEX_VERIFIED.json) · [GCD 核验](evidence/tcad_ibex_20261123/SCREEN_MATRIX_GCD_VERIFIED.json) · [AES 核验](evidence/tcad_ibex_20261123/SCREEN_MATRIX_AES_VERIFIED.json)
- Ibex 四个温和降档及低扇出探针均通过三角 setup 预算和绝对 hold，均触发相对原 CONTROL 的 SS hold 拒收。按历史零编辑重布线做独立归因，补证的三个探针与已实跑的 FAECO 第三次端点均通过两态 SEC 13648/0。后者实测面积下降 17.5168 µm²，SS hold 与该零编辑物理端点相同。这个 hold 参照仅用于归因，采用此参照的整套搜索和计时尚未运行。[探针证明](evidence/tcad_ibex_20261123/SKY130_SCREEN_HOLD_SEC_VERIFIED.json) · [FAECO 端点证明](evidence/tcad_ibex_20261123/SKY130_SCREEN_FAECO_HOLD_SEC.json)
- 调度收据回放确认三例 SKY130HD 的筛选 FAECO 前五次均用于首批及拆分，六次仅覆盖排名 1–4；Ibex 和 GCD 已测合格批次分别在排名 7–9、13–15。按相对 hold 拒因延后拆分的回放重现三个固定臂的动作序列，触及 Ibex/GCD 的已验收端点，AES 仍为零。两次 ASAP7 轨迹按原 setup 拒因保留原拆分。新规则的独立样本收益与实际时间仍未验证。[调度诊断](evidence/tcad_ibex_20261123/SCHEDULER_COVERAGE_DIAGNOSTIC.md)
- AES 同配方零编辑 DRT/RCX 的绝对 hold 保持三角正裕度，SS 相对原 CONTROL 下降 0.676792 ps。换零编辑参照后，筛选池已有 8/18 次评估的物理和时序投影通过，最大回收 0.009665%，未达 0.01% 面积目标，也未做候选 SEC。对两个面积减量 33.7824 µm² 的固定批次，以 12 次 ODB/SPEF 交叉 STA 定位到三个拒收视图的寄生变化。六次该幅度的三门评估在投影下仍被拒，原正式矩阵回收为零。[AES 归因](evidence/tcad_ibex_20261123/AES_REROUTE_HOLD_DIAGNOSTIC.md)

## 2026-11-23 TCAD Ibex 双工艺原始起点核验

- ASAP7 Ibex 原始 ORFS CONTROL 已完成 CTS、详细布线（DRC=0）和 RCX。按原约束独立 STA，FF/TT/SS 的 hold WNS 为 +35.956/+53.159/+77.237 ps，均非负。共享零动作通过三视图、电气与 SEC（17363/0）。每臂六次物理评估后，单门／固定微批次／FAECO 自适应分别回收 0.37908／0／0.26244 TT Liberty 功能单元面积；公共窗口 1325.602 s 内分别回收 0.26244／0／0.26244。本配置下 FAECO 在等调用次数时低于单门，等墙钟时与单门持平。[原始起点](evidence/tcad_ibex_20261123/asap7_control/CONTROL.json) · [三臂核验](evidence/tcad_ibex_20261123/ASAP7_P1_VERIFIED.json)
- SKY130HD Ibex 原始 ORFS CONTROL 的最终 DRC、天线违规均为零，RCX 完成。在原 I/O 与完整 ODB 下，SS hold WNS 为 −1379.766 ps，原始起点未达进入三臂的门限。从原物理快照完成共同 hold 修复，并核验最终 DRC=0、天线零、RCX、原 SDC 字节一致、原始至修复两态 SEC 13648/0。修复起点的 FF/TT/SS hold WNS 为 +288.152/+466.107/+115.914 ps，SS setup WNS 为 −38.757 ns。两次零动作 DRT 均产生 −0.079936 ps 的 SS hold 变化，未进入候选。正式零编辑门从冻结布线 ODB 重新 RCX 后三视图无变化，SEC 13648/0。三臂从同一修复起点启动，每个候选执行局部 DRT 和新 RCX。旧 −10 ps 对照暂停前，单门六次与固定微批次第一次已有完整收据，七次均拒收。固定微批次第二次仅完成 DRT/RCX，未启动 STA。随后封存旧执行，FAECO 自适应未启动。[原始起点](evidence/tcad_ibex_20261123/sky130_control/CONTROL.json) · [修复起点](evidence/tcad_ibex_20261123/sky130_control/REPAIRED_CONTROL.json) · [零动作核验](evidence/tcad_ibex_20261123/SKY130_NOOP_AUDIT.json) · [正式命令](evidence/tcad_ibex_20261123/SKY130_P1_REEXTRACT_COMMAND.txt)

- 新评测协议双工艺执行结束。主档逐视图允许 1% 原周期的 WNS 损失及登记的 TNS 损失，三方法各六次独立候选测量，沿用原约束、hold 与 SEC 门。ASAP7 单门／固定批次／FAECO 在 1200 s 内回收 0.26244／0／0.26244，六次评估回收 0.37908／0／0.26244。首达 0.01% 面积为 1135.931 s／未达到／810.920 s，两种达标方法得到同一端点，FF 新增 15 个负 setup 端点，SEC 17363/0。两臂并行负载不同，时间结果按观测描述。SKY130HD 在 720 s 内和六次评估后均回收零，所有候选的 TT WNS/TNS 退化超出包络。
- 新协议诊断以 0% 为参照，ASAP7 的 protect@0.5% 与 protect@1% 都找到保持 FF setup 非负的端点。单门与 FAECO 分别回收 0.24786 与 0.13122，无新增负 setup 端点，SEC 均 17363/0。0% 的两种模式、SKY130HD 的全部诊断和 ASAP7 的固定批次均回收零。主档的真实墙钟与缓存诊断成本分账。[本轮报告](evidence/tcad_ibex_20261123/REPORT.md#按原周期归一化的-setup-预算对照) · [登记](evidence/EXPERIMENT_REGISTRY.md#2026-11-23-tcad-ibex-p1-setup-protocol-v1) · [评测方法](planning/FAECO_EVALUATION_PROTOCOL_DRAFT_20261123.md)

- ASAP7 同机独占 EDA 队列，固定 CPU 0–5、四线程，依 FAECO→单门和单门→FAECO 完成两对至相同面积目标的串行复跑。四臂均在第三次回收 0.26244，且 ODB/DEF/V、去日期 SPEF、各角时序和 SEC 与前轮首次达标端点一致。按预登记的 WSL 单调钟，逆序 FAECO/单门 688.233/728.543 s，原序 695.670/730.866 s，单门分别多 40.311/35.195 s。两组差异主要来自单门多一次 SEC。宿主 QPC 和 WSL RAW 抽查显示该 WSL 单调钟快约 4%–4.6%，原值按同一时钟报告。[复跑报告](evidence/tcad_ibex_20261123/ASAP7_SERIAL_REPORT.md) · [时钟对照](evidence/tcad_ibex_20261123/ASAP7_SERIAL_CLOCK_AUDIT.md)
- SKY130HD TT 的 18 个候选最差路径都经过本次降驱动的高扇出缓冲 `buf_12 → buf_1`。两个代表分支做七组 ODB/SPEF 交叉 STA，沿用 CONTROL 的 SPEF 时切换到候选 ODB，FIFO 与寄存器堆分别损失 474.644/403.733 ps WNS 和 24.628/22.368 ns TNS。仅替换为候选 SPEF 时 WNS 只变动 −0.002665/+0.986766 ps，TNS 改善 0.035481/0.565102 ns。在这两个分支，换门主导 TT 恶化。FIFO 体现新负端点的累加，寄存器堆体现既有负端点的退化。[TT 归因](evidence/tcad_ibex_20261123/SKY130_TT_CAUSE.md)

## 2026-11-23 中文 v3 配图与实验口径修订

中文活跃工作稿为 14 页，含六幅 ImageGen 示意图、十例 SKY130 逐端点对照与 s713/s832 联合评测。v22 标签锁定此前中文稿和工程基线。英文工作稿暂冻。[中文工作稿](../paper/zh/FAECO_v3_后布局可调预算面积回收.pdf) · [联合评测](evidence/sky130_joint_constraints_20261123/REPORT.md) · [图件记录](../paper/zh/figures/imagegen_20261123/PROMPTS.json)

## 2026-11-23 SKY130 端点对齐与 s713/s832 联合约束复查

- v22 历史十个名义正回收端点的面积降幅为 0.67%–5.58%、均值 2.01%，均有零 DRC 和非空全网表两态 SEC。逐端点回读已绑定网表、SPEF、证明输入和各分析所用 CONTROL。部分历史分析使用独立重布线 CONTROL，和候选路由输入的 Resizer 快照存在字节差异。[逐端点证据](evidence/sky130_joint_constraints_20261123/ENDPOINTS.md)
- 保持上述十个物理端点时，SS setup 预算通过 9/10，FF hold 严格相对非退化 5/10。将 s641 切至面积降 0.662% 的多角替代点后，分别为 10/10 和 6/10，该替代点缺 IO+OCV 绑定。十个名义端点的 IO+OCV 相对 setup 预算通过 8/10，另外两个以原始 CONTROL 回退达相对 setup 门且面积收益为零。十个名义端点及对应历史 CONTROL 的 IO+OCV 绝对 hold 全部为负。历史的通过率分别对应各条件和端点。
- `SKY130-JOINT-B10-S713-S832` 为两例新联合评测。每例固定同一 CONTROL 快照，使用同一候选网表与 SPEF 测时钟约束下 TT、SS、FF 及 TT+IO+OCV，四场景均需通过 10 ps setup 损失预算、hold 非退化与非负硬门，并要求正面积收益、DRC=0、最终非空两态 SEC。最终实测每例 10 个候选，合计 20 个候选均 DRC=0，全部保留 IO+OCV 绝对 hold 违例，严格接受 0/2。
- s713 严格门及相对诊断均无正收益端点，候选 IO+OCV hold 为 −99.035 至 −98.036 ps，原 CONTROL 为 −98.219 ps。s832 的 `RUN_005` 仅在 IO+OCV 不要求绝对 hold 非负的相对诊断条件下回收 3.7536 µm²（0.322%），IO+OCV setup/hold 分别改善 +6.404/+0.801 ps，绝对 hold 仍为 −74.515 ps，DRC=0、SEC 162/0。这一项计作诊断。结果的作用域为冻结设计、候选顺序、两例 10 次评估预算及明确的四场景约束。[联合约束证据](evidence/sky130_joint_constraints_20261123/)

## 2026-11-23 横向对比扩展与 ASAP7 7 nm 两万门跨工艺定稿（`v22`）

- **活跃基线与中文主稿**：基线升级至 **`v22`（`v2026-11-23-cross-pdk-lr-baselines`）**；中文 v3 主稿 `paper/zh/manuscript/FAECO_v3_后布局可调预算面积回收.tex`（15 页，6 套 Nature 矢量图，LuaLaTeX 0 Error / 0 Overfull / 0 Undefined，无孤儿参考文献尾页，经 `user-academic-writing-style` 全文学术化润色）已集成 LR 10 电路同台基线、OpenROAD 负裕度开关证伪、文献 8 类横评表 1、以及 ASAP7 7 nm 两万门级 `aes_cipher_top` 验证（`v22` 清单 `165 OK / 0 FAIL`、`pytest` 核心 65 项全通过）；英文稿 `paper/en/` 维持暂冻。证据入口：`project_docs/evidence/cross_pdk_lr_baselines_20261123/{REPORT.md, SUMMARY.json}`。
- **OpenROAD 原生负裕度开关证伪（`s382`）**：在 `CONTROL`（`WNS = -0.8485 ns`）上显式施加 `-slack_margin -1.0` 或 `-setup_margin -1.0 -allow_setup_violations` 均仍返回 `0 Resized / +0.00%`。
- **Track A：经典拉格朗日松弛（`LR_DOWNSIZE`）10 电路实测**：5 轮冻结 SPEF 子梯度 LR 宣称 `7.81%–14.14%` 降幅（17–60 门），重合法化 + 15 轮详细重布线 + 新 RCX + 传播 STA 后 **10/10（0% 合格）** 发生 `-79.60 ~ -706.03 ps` Setup 坍塌，有效面积降幅均 `0.00%`。
- **Track B：ASAP7 7 nm 多 Vt `aes_cipher_top`（20,097 实例，MLCAD26 全局布线评估口径）**：扩展 `logic_rewrite.py` 与 `physical_budget_adapter.py` 至通用多库 Liberty 枚举（`10,010` 候选，`15.4 s`）。`CONTROL` 基准 `2136.4220 µm²`（`WNS = -85.279 ps`、`TNS = -12405.20 ps`、`hold = +41.607 ps`、`total_power = 0.432 W`）；OpenROAD 原生虽触发 341 处替换回收 `0.118%`，但 **TNS 恶化 `-2516.01 ps`（`-20.3%`）**；FAECO 提交 **191 门**回收 **`0.266%`（`2130.7504 µm²`，原生的 `2.25×`）**、$\Delta\text{WNS}=+0.000\,\text{ps}$、**$\Delta\text{TNS}=+48.181\,\text{ps}$（改善）**、$\Delta\text{hold}=+0.000\,\text{ps}$、总功耗降至 `0.431 W`、**Yosys `1252/1252 $equiv` 全证明**（明确区分该节全局布线寄生口径与 SKY130 详细重布线签核，不跨 PDK 混算均值）。

## 2026-11-23 终检定格：强外部基线、完整 PPA 与万门级 `b15` 局部增量突破（`v21`）

- **活跃基线与中文主稿**：基线升级至 **`v21`（`v2026-11-23-postroute-baselines-b15`）**；中文 v3 主稿 `paper/zh/manuscript/FAECO_v3_后布局可调预算面积回收.tex`（15 页，6 套 Nature 矢量图，LuaLaTeX 0 Error / 0 Overfull / 0 Undefined）已重组 §6–§8 叙事顺序并纳入完整强基线与 PPA 数据；英文稿 `paper/en/` 暂冻。证据入口：`project_docs/evidence/postroute_strong_baselines_20261122/{REPORT.md, SUMMARY.json}`。
- **同起点四方法强基线对照（10 电路，$B=10\text{ ps}$，6–10 次评估）**：OpenROAD 原生（`0/10 = 0.00%`）、离线固定寄生灵敏度批处理（仅 `5/10` 通过重布线后验，有效均降 `0.14%`，`s641/s713/s832` 退化高达 `-40.89 ~ -123.44 ps`）、单门在线灵敏度贪心（`9/10` 有效、均降 `2.11%`，在 `s953` 失灵为 `0.00%`）、FAECO 独立闭环（**`10/10` 全胜**、均降 `2.01%`、`b12` 回收 `2×` 于单门贪心）。
- **10/10 完整功耗与 IO+OCV**：`10/10` 同步降低总功耗（均 `−0.96%`）与组合逻辑功耗（均 `−3.72%`，最高 `s420 −8.26%` / 漏电 `−8.68%`）；`b04/b11/b12` 显式 IO+OCV 全部达标，实现 **10/10（100%）** 显式 IO+OCV 合规。
- **万门级 `b15`（`33,737.36 µm²`，5,494 组件，`UTIL=25%`）局部增量突破**：局部直连线网增量绕线（`render_local_incremental_flow_tcl`）在 `b12` 提速 `2.12×`（`52.94 s` vs `112.02 s`）；在 `b15` 全 6 轮均收敛至 `DRC=0`（`184.83–200.92 s`，相对全芯片重布线 `1426.14 s` 残留 66 DRC 提速 **`7.7×`**），`RUN_006` 提交 5 门净回收 `88.84 µm²`（`−0.26%`）、`TT +0.068 ps`、`SS +199.996 ps`、`FF hold 0.000 ps`、`IO+OCV +0.027 ps`、静态漏电 `−0.84%`、**全网表 SEC PASS**（在 `+445.66 ps` 绝对 hold 裕量下采用 `0.05 ps` RCX 提取舍入底噪容差覆盖 `−0.021 ps` 微波）。

## 2026-11-22 现状定格：中文 v3 主线定稿 + 目录与 v20 基线整理（英文暂冻）

- **唯一活跃中文主稿**：`paper/zh/manuscript/FAECO_v3_后布局可调预算面积回收.tex`（LuaLaTeX 14 页，5 套 Nature 风格矢量图表，`0 Error / 0 Overfull / 0 Undefined`；双副本 PDF 同步于 `paper/zh/` 与 `paper/zh/build/`）。已完成去工程化学术语言润色（去除脚本名、Python 符号与命令行参数）。
- **版本与范围**：当前活跃基线为 **`v20`（`v2026-11-22-postroute-v3-zh`）**；按用户指示**先专注中文版本与工程梳理**，英文稿 `paper/en/` 暂冻维持历史同步状态，预布局 v1/v2 中文稿在 `paper/zh/manuscript/` 作历史归档保留。
- **补充扩展成果口径**（相对 2026-11-20 初报扩增）：通用纯独立模式由 `8/8` 扩展至 **10/10（100%）** 跨族全胜（含 `b05` `-3.47%` / `+7.43 ps`、`b11` `-0.90%`、`b12` `-0.82%` / TT `-0.03 ps` / SS `+64.59 ps`）；SKY130 真实多角签核实现 **SS 10/10（100%）** 合规（在线三角重跑修正 `s641` 至 `-0.66%` / SS `+71.69 ps`）；在线 IO+OCV 联合门控实现 **7/7（100%）** 合规；规模边界实测揭示 `b14`（0 候选）与 `b15`（35% 利用率 5,494 组件，单次全芯片重布线超 1200 s）。

## 2026-11-20 口径升级：完全脱离 Resizer 日志的通用独立面积回收（Resizer 仅作对比基线）

用户正式拍板将项目定位切换为**不依赖 Resizer 修改日志或修复前网表的通用布局后面积回收机制**（Resizer 及其原生 `recover_power` 仅作为外部对比基线）。证据入口：`project_docs/evidence/postroute_recovery_20261120/{REPORT.md,SUMMARY.json}`。

- **独立候选生成**：`code/src/rseco/physical_budget_adapter.py::generate_compatible_candidates` 仅读取布线后 `routed.v` 与 Liberty 库枚举合法降面积替换（50 项单元测试通过）。
- **纯独立 6 例全重布线 + SEC 实证（$B=10\text{ ps}$，仅 6–10 次评估，ZERO Resizer 日志）**：
  - `s382`：−1.78%（1052.26→1033.49 µm²），ΔWNS −6.70 ps，Δhold +0.00 ps，SEC PASS
  - `s420`：**−5.58%**（942.15→889.60 µm²），**ΔWNS +4.12 ps（改善）**，Δhold +0.01 ps，SEC PASS（较依赖历史名单的 1.59% 提升 **3.5×**）
  - `s641`：−1.99%（1133.59→1111.07 µm²），ΔWNS −0.43 ps，Δhold +0.10 ps，SEC PASS
  - `s713`：−2.32%（1131.08→1104.81 µm²），**ΔWNS +0.63 ps（改善）**，Δhold +3.65 ps，SEC PASS
  - `s832`：−1.71%（1167.37→1147.35 µm²），ΔWNS −4.17 ps，Δhold +2.64 ps，SEC PASS
  - `s953`：−0.67%（2433.58→2417.32 µm²），ΔWNS −9.88 ps，Δhold +2.99 ps，SEC PASS
  - `b04`（4078.91 µm²，197 候选，6 次评估）：**−0.86%**（4043.88 µm²），**ΔWNS +2.47 ps（改善）**，Δhold +0.09 ps，SEC PASS
  - `b05`（3424.53 µm²，201 候选，6 次评估）：**−2.78%**（3329.44 µm²），**ΔWNS +4.85 ps（改善）**，Δhold +1.10 ps，SEC PASS
  - 全部 8/8（ISCAS89 6 例 + ITC-99 `b04/b05`）`DRC=0`、**8/8 Δhold ≥ 0.00 ps**、**8/8 全网表两态 SEC PASS**；而对比基线 OpenROAD `repair_timing -recover_power 100` 在全部 12/12 电路上均做 0 次修改（0.00%）。
- **显式 IO 约束 + OCV 降额压力审计（7 电路）**：在 `input/output_delay=0.10ns, load=0.01pF, transition=0.05ns` + `-early 0.90 / -late 1.10` 下，`5/7` 通过 10ps 门限（`s382` +15.46ps、`s420` +6.05ps、`s641` +5.57ps、`s953` −7.11ps、`b05` +6.92ps），`s713`（−10.08ps）与 `s832`（−40.76ps）暴露 IO+OCV 敏感性；独立 SS/FF `.lib` 因 PDK 未安装暂缺。历史基于差分回退的结果（`RESTORE074`、`RECOVERED_V2`、`b22`）保留作为“有前序修改日志时的增量诊断与转折门隔离算法”验证。

## 2026-11-20 在线物理闭环、ISCAS89 全8例重布线验收与 b22 转折门隔离突破

证据入口：`project_docs/evidence/postroute_recovery_20261120/{REPORT.md,SUMMARY.json}`。

1. **ISCAS89 全 8 例真实重布线物理验收（$B=10\text{ ps}$）**：在相同 `CONTROL` 起点上统一执行 `replace_cell` → 重合法化 → 清除信号线 → `detailed_route -droute_end_iter 15`（全部 `DRC=0`）→ 新 RCX 提取 → 独立传播时钟 STA + 全网表两态 SEC。OpenROAD 原生 `repair_timing -recover_power 100` 在 8/8 电路上均做 0 次修改（0.00%）。我方方法在 6/8 电路上取得 1.55%–4.68% 完整映射单元总面积下降（`s382` −4.40%/−3.10ps、`s420` −1.59%/−5.70ps、`s641` −1.55%/−3.88ps、`s713` −2.99%/−2.94ps、`s832` −3.00%/−8.71ps、`s953` 在线二分隔离 `14/23` −4.68%/+17.26ps），6/6 通过全网表 SEC；`s27` 无改，`s820` 因重布线敏感经二分精确回退至 `CONTROL`（0.00%）。所有电路 `hold > +0.45 ns`（无 hold 违例；`s641/s832/s953` 相对 `CONTROL` 存在 `−0.50 ~ −11.31 ps` 轻微 hold 波动，报告实测值而不隐瞒）。
2. **ITC-99 代表 4 例真实重布线物理验收（`b04, b05, b11, b12`）**：OpenROAD 原生 `recover_power 100` 在 4/4 电路上仍为 0.00%（跨两族共 12/12 为 0%）。`b05` 直接通过 $B=10\text{ ps}$ 重布线与全网表 SEC（总面积 −5.04%、$\Delta\text{WNS}=+8.63\text{ ps}$、$\Delta\text{hold}=+0.94\text{ ps}$）；`b04`（−12.32ps）、`b11`（−29.15ps）、`b12`（−90.81ps）暴露固定 SPEF 乐观偏差，未宣称在 10ps 下合格。
3. **在线全库候选搜索与同预算消融（`s382, s641, s953`）**：`code/src/rseco/physical_budget_adapter.py` 将 `bounded_search` 正式接入上述真实重布线评估器与 `SPACE_AUDIT` 全库候选。`s382` 产出跨源组合 `ONLINE_007`（`_096_ + rebuffer1`，面积 −1.31%、$\Delta\text{WNS}=-7.028\text{ ps}$、$\Delta\text{hold}=0.000\text{ ps}$、SEC 101/0）。在 `budget=12` 同预算消融中：`s641` 上 `Sequential Greedy` 胜出（`22.52 µm² / −1.99%`，$\Delta\text{WNS}=-0.43\text{ ps}$ vs `bounded_search` `15.01 µm²`），证明紧凑预算下**全库候选覆盖 + 顺序贪心**更高效；`s953` 两者平手（`16.27 µm²`），且 `RUN_012` 实证 `_225_ + _231_` 可将单测 `−23.57 ps` 补偿至 `−2.96 ps`。
4. **`recover_area.py` 升级与 `b22` 突破**：修复 `parse_named_instances` 漏掉转义实例（OI-085 生产脚本侧修复），并将尾部回滚升级为 **Tipping-Gate Isolation + Continued Bisection**（44 项单元测试通过）。在 `b22`（359 修改）上仅用 10 次验证 STA 定位并隔离唯一转折门 `_160630_`，将固定 SPEF 回收率从超时 0.0% 提升至 **33.1%（356/359，3024.15 µm²，ΔWNS +0.0011 ns）**。
5. **`s382` 显式 IO 约束审计（OI-082）**：加入 `input/output_delay=0.10ns, load=0.01pF, transition=0.05ns` 后，`CONTROL/RESTORE074/ONLINE_007` 的 setup WNS 逐位不变，`ONLINE_007` 的 TNS 优于 `CONTROL`（`-14.715` vs `-14.753`）；`CONTROL` 自身带 IO 约束后 `hold=-0.0720ns`，两候选仅差 `-0.03~-0.22 ps`。多角验证仍开放。

## 2026-11-13 总体机制调研结论与研究入口

本轮整体机制定向调研入口为 `project_docs/evidence/overall_related_work_20261113/REPORT.md`（配SOURCES/MECHANISM_AUDIT/LITERATURE_NOTES，由主线汇合）。整体近邻包括E-Layout（ICCAD2026）、PCR（2026预印本）、RL-CCD（DAC2023）、Trident2（ICCAD2013）、Task-based（TCAD2023）、OpenPhySyn（WOSET2020）与OpenROAD。预算参数、多动作、反馈本身不能直接作为独创性依据，也不能据已有近邻否定整个项目。

实际旧outerloop、历史recover_area与新budgeted_search三链尚未统一。待检验的总体假设是：完整候选覆盖与交互选择，能在同样实际物理验证成本下改善预算内净面积回收。须与强贪心/原生恢复比较并做组件消融、完整约束及跨设计验证；OI-086继续open。本轮为定向研究而非系统综述，0新EDA/0SEC，未改稿件/生产代码或既有科学结论。

## 2026-11-13 可调预算核心与历史CLI工程门通过

纯预算选择/有限组合核心及测试已实现，历史端点evaluate_budget CLI支持用户预算，拒绝负数/NaN/inf，真实52端点0/5/10/20ps与核心结果一致。完整回归v2为1147passed/156subtests（pytest128.96s，wrapper132s/rc0），REGRESSION_RECEIPT确认code全py前后SHA不变。v1的5failed/1142passed保留，系未前置已验packaged Yosys镜像；仅修正环境后重跑，没有为通过而修改生产代码。

通过范围是纯核心、历史端点选择及工程回归，不是在线物理搜索已接入或新算法收益。物理评估器adapter、完整IO/多角/跨设计、旧生产parser/SEC scanner及其它未决保持open。测试生成fixture已备份恢复/隔离，不纳入科学证据。

## 2026-11-13 RESTORE074在10ps政策下限定接受

根与独立验收已齐：`timing_budget_20261113/ACCEPTANCE.json` SHA `2de50d475fec765bb0b8729addf75a43d8e929bdcf06b04b752d4fb6eafdff75` 接受精确既有RESTORE074端点于10ps预算/现有约束域。SEC全部输入输出SHA、102功能实例（含21FF）、41种实际cell模型与重建SHA通过，101proven/0unproven；无额外重路由或STA，新增仅已登记1SEC。

s382同阶段分母A0=892.1056、AR=1052.2592、AF=1005.9648，回收46.2944/160.1536=28.90625%，总面积降4.399524%；WNS损0.003098077ns、hold改善0.003577305ns、TNS损0.231982231ns。明确是用户允许WNS预算且TNS辅助后的历史端点接受，旧strict失败保持；不是新算法在线搜索收益，完整IO/多设计/机制优势未成立。纯预算核心/历史适配器独立审查无阻断缺陷，整体回归与物理在线接入状态另报。

## 2026-11-13 10ps候选根验证通过，最终独立回执待收

主线独立DEF/固定Liberty重算A0/AR/AF=892.1056/1052.2592/1005.9648，功能实例94/102/102，ROOT_READBACK.json绑定；s382净新增面积回收28.90625%、总面积降4.399524%。RESTORE074精确既有端点相对CONTROL：WNS−0.003098077ns、hold+0.003577305ns、TNS−0.231982231ns，符合当前10ps WNS与hold硬门（TNS辅助），不属于旧strict通过。

根rawSEC101proven/0unproven及全部proof/sourceSHA已核，未重路由端点；最终独立agent接受回执尚待，完整限定acceptance收齐后再记录。新增代价仅1SEC，历史重筛0route/0STA；这不是新算法搜索收益，也不代表缺失IO约束已补或全部设计可用。

## 2026-11-13 s382 净新增面积分母实查通过（仅此快照）

`timing_budget_20261113/area_baseline_audit/REPORT.md` 已完整展开层级并绑定原flow/DEF/V/Liberty：综合输入809.5264，修复前CTS快照A_0=892.1056，Resizer最终A_R=1052.2592，RESTORE074最终A_F=1005.9648。综合→CTS/前处理82.5792不计Resizer分母；该受控流程repair前后最终master净差160.1536，回收46.2944，净新增面积回收率28.90625%，总面积下降4.399524375743%另报。

A_R为repair后合法化/布线最终快照，未存立即repair结束快照；此值为该受控流程最终master净差，不是瞬态resize累计。8新增buffer+24已有实例最终master变化与日志34次resizes是不同统计。仅s382分母被核，不能恢复其它13设计旧比例，亦不是28.90625%操作无效。面积审计不替代该AF的时序/hold/SEC与IO资格；正式端点接受仍待proof根/独立核验。

> **可调预算草案审查补充（2026-11-13）**：W_R/A_R/H_R固定为Resizer输出，A_0仅用于净新增面积回收率分母，不替换接受门参考。无可行正收益时精确返回原CONTROL或已验证档案端点；评分仅生成提案，ΔA/ΔWNS比率不能保证安全。对既有物理端点按不同预算筛选计0新EDA；预算改变候选搜索后产生的新独立运行另行预注册/计数。旧IO约束覆盖不足仍在，不因新预算或档案筛选宣称完整安全。

## 2026-11-13 可调WNS预算的面积回收机制草案（尚未实现）

当前机制草案保留Resizer前端，以其固定终点作为参考W_R、A_R；用户配置允许WNS最大损失B，单位ns，必须非负且有限，**拟默认B=0.010ns**。目标为 `max (A_R-A(x))`，约束 `W(x)>=W_R-B`（1e-6ns仅数值容差），并保留原hold非退化/非负门、完整结构、DRV/物理检查及SEC；TNS完整报告，作为同面积等情况下的辅助择优。

每轮结合面积收益与时序代价选择动作，组合必须实际复测；保留已验证非支配终点，使不同预算选择已有有效对象。预算始终相对固定Resizer参考，不能每步重置，也不能把单动作预测累加当组合安全保证。界面可用ps，但须明确转换到ns；0/5/10/20ps只是配置示例，不代表新增实验。

这是设计草案，具体选择算法、实现及物理验证仍pending。现有CLI `max-degradation`默认0.015且使用旧SPEF测量，不能声称本次已实现可调机制或已将默认改成10ps。此次不改代码/封存证据，不启动EDA。保留前端的本阶段草案不取消长期独立生成与统一选择机制的探索目标。

## 2026-11-13 用户澄清：保留Resizer前端，自有后续优化机制

默认流程为共同初始设计 → Resizer时序修复 → 自有面积/时序联合优化 → 物理验证。Resizer可以是正式前端，不要求自行重写时序修复器，也不要求主方法脱离Resizer独立冷启动。自有贡献应落在候选构造、联合选择、交互处理和物理反馈；可以利用Resizer修改历史作为线索，但候选能力不能仅限于撤销其历史动作。比较同一Resizer终点上的原生恢复、简单贪心与自有机制，固定约束和评估预算。沿用净新增面积回收率主指标及总面积/时序并列报告，WNS预算10ps、TNS辅助、hold原安全门不变。此前“仅baseline/可选warm start”“必须从初态独立完成修时序”不再是项目要求。这里明确研究边界，不声明新算法已实现，也不未经核验将Resizer称为已证明最优的SOTA。


> **面积归因补充（2026-11-13，现行）**：A_0应取同一物理阶段、Resizer调用前的完整面积；不能用综合前或CTS前A_0与布线后A_R作差并全部归因Resizer。若端到端对照无法隔离其它阶段，指标应称「相对共同初态的净面积开销」，不称「Resizer专属新增面积」。当前area_audit.json明确未展开baseline层次（No baseline hierarchy expansion），因此新增面积回收比例暂不报数。

## 2026-11-13 用户最新评价重点与完整自有机制方向

评价重点转为时序修复的净新增面积回收率：`(A_R - A_F) / (A_R - A_0)`。A_0为同初始网表在共同测量阶段的完整面积，A_R为Resizer修复终点完整面积，A_F为最终方案完整面积；三者必须同库、同阶段、同实例计数口径且A_R>A_0。该分母是修时序的净新增面积，不是所有被改动单元面积之和。小分母带来的高比例不等于总面积收益大，须并列绝对节省A_R−A_F、总面积降幅、三份完整面积及WNS/TNS/hold。A_0尚未完成同口径核验，不报告旧67%或据旧解析分母推新回收率。

终极方向是从同一个初始网表独立生成修时序与减面积动作，用统一选择与物理反馈形成完整自有机制；Resizer是外部baseline或可选warm start，机制不依赖其edit历史或rollback名单。当前仅方向探索，尚未实现或证明算法优势；此次只记录方向，不制定实现设计、不运行新EDA。现行首轮WNS损失预算10ps、TNS辅助、hold原安全门保持；新政策与历史strict证据继续分开。

## 2026-11-13 用户最新政策：首轮WNS损失预算10ps

用户明确允许小幅WNS下降并选择首轮10ps预算。新现行接受门为propagated WNS >= CONTROL −0.010ns（另加1e-6ns数值容差）；TNS仅辅助完整报告/同面积次级择优。hold原安全门保持：相对CONTROL非退化1e-6ns且hold>=0；正面积、实际结构/物理证据及SEC条件不变。报告0/5/10ps三档对照，10ps是明确允许的工程权衡，不能称零时序退化。

新证据域 `timing_budget_20261113` 与旧strict/WNS-primary政策分离；旧WNSprimary prereg/PLAN/RESCREEN和失败历史不改。旧selectedSEC暂不执行，按新门重新筛选再决定证明对象。此条只更新用户政策，不宣称任何新筛选数值或接受端点；IO约束等未决不因允许10ps而解决。

## 2026-11-13 用户接受规则更新：WNS优先，TNS次级

用户明确「优先wns，wns符合了之后tns不是很重要」。从本条起，新政策采用WNS-primary：相对CONTROL的propagated WNS与hold非退化（1e-6ns纯数值容差），hold>=0及既有结构/物理/证明条件仍为硬门；可行集合内面积收益为首选目标。TNS完整报告，作为同面积时的次级择优，不再单独硬拒绝候选。

这是用户改变目标后的新评估口径，不覆盖旧WNS/TNS/hold全非退化研究。旧strict失败、预注册、封存工件和结论保留；新policy包与旧历史隔离，先用已有实际物理端点重筛并为新入选者补SEC，不把重筛称新物理实验。尚未据此公布任何新数值结果或接受点；完整约束/IO/泛化边界仍在。拟25候选新EDA须等新政策定稿，不沿旧门自动启动。

## 2026-11-13 严格搜索阶段结案：固定邻域无增益，候选覆盖待扩

`strict_area_search_20261113/REPORT.md`记录9个096固定seed双动作与独立2个054中间档探针：新增11route/22STA，全部证据有效但strict0，无新增SEC。面积优先与风险优先在主预算k3及所有前缀均精确返回已接受FORWARD096（省6.256/0.594530321%，WNS/TNS改善、hold不变），不重路由seed。本轮否证该固定9点星形邻域扩大严格面积收益的假设，不支持风险排序优势；不外推排序普遍无效或所有候选无效，也不再对该无可行改进池调排序当新机制。

完整102功能实例/335pin的固定Liberty静态审计得到62个逻辑签名兼容且降面积的替换（33实例），旧13只有10正面积目标覆盖10/62，另3零面积。62为候选不是收益，52遗漏也非全部实现bug。FF12/clock-family14/其它组合36个目标须按约束和物理门分别验证；同实例目标互斥，不能把节省相加。已实测遗漏054→2单/双点均更差，不否定其余目标。

下一阶段优先完整候选生成与实际电气/物理资格验证，先审未测组合逻辑，clock/FF受完整约束门保护。原及当前脚本缺数据IO delays/loads/transition；完整约束、等预算强基线、跨设计/角泛化、自有机制优势仍未建立。生产算法和冻结论文未改，旧sealed证据不修改，当前阶段结案不等于ICCAD研究目标完成。

## 2026-11-13 s382 严格补偿阶段结果（A–D独立复核完成）

本轮A13单点恢复、B12有限组合、C13从CONTROL孤立回退、D3路径补偿，共41次新routing/82次终点STA，另2次路径诊断STA。A/B全部严格失败；C唯一通过点为FORWARD__096_，全13独立审核与SEC101proven/0unproven已通过：省mapped-cell面积6.256 μm²（0.594530321046%），propagated ΔWNS+0.001714739461534 ns、ΔTNS+0.004840851 ns、Δhold0。它是已验简单单动作baseline，限该电路/实现/配置约束与证明模型域，不是新机制或完整signoff。

D三补偿经主线与独立复核全部有效但strict失败：057/083虽均省2.378121%，前者WNS/TNS/hold均降；083 WNS改善但TNS/hold降；buf8省2.140309%却三指标均降。不得拿这些较大面积收益替代严格可行baseline，或放宽门槛宣布成功。独立机制、强同预算基线、完整约束及跨电路泛化继续未建立；旧论文不改。

## 2026-11-13 用户新增目标：独立机制与零退化面积优化

本条记录本轮研究目标和接受门，不覆盖下面的历史证据，也不表示目标已实现。以 ICCAD 标准发展自有选择/补偿机制：相对同起点 Resizer CONTROL，完整 mapped-cell 面积下降，同时重新布线/提取后的 propagated-clock WNS、TNS、hold 均不下降（1e-6 ns 仅为数值容差），并满足 hold>=0 与已明确检查的物理约束。2/5/10 ps 放宽档仅作诊断，不允许当主结果或隐藏失败。

独立机制须有明确算法、可归因的有效性与同预算强基线；不能将原生工具改名或单例试探称为新颖性。完整 SDC/DRV 约束覆盖、跨电路/跨实现泛化尚未建立，三臂均有负 setup slack，不声称时序闭合。当前 s382 单点补偿13/13未过严格门；有限组合按运行前冻结规则推进，未通过则记录失败与归因，不放宽目标。路径补偿或从 CONTROL 开始的安全事务式前向选择只是下一阶段待评估方案，未由本条授权新 EDA。

## 2026-11-13 接手审计优先裁定：Recovery 尚未晋级

以下裁定优先于本文件旧 Recovery 20/21 及 11-12 交接摘要；历史正文保留溯源。

- **136/202 是归档回退配方计数**（ISCAS v2 65/107 + ITC 71/95），不是 136 个独立零效应证明，202 也不是所有 Resizer 操作。145/202 混入旧74例统计，不作当前结果。
- **面积须重新审计**：旧 CLI 的 `\\w+` 实例名解析漏掉 escaped DFF。旧 14% 是新增面积回收比例；从旧 summary 推出的 4.542% 也只是旧解析器分母，不能当完整总面积结果。s382 完整具名单元核算 CONTROL 1052.2592 → RECOVERY 1005.9648 平方微米，下降4.399524%；旧分母611.8368漏21个触发器。
- **14例全导出网表复核**：`area_audit.json` 的28份网表全解析、连接未知单元0；纳入所有Liberty已知导出实例（含clock/probe），只排除无连接tap物理单元。总面积降幅逐例算术平均 **3.071500828%**，最大b07 **7.810443177%**，绝对节省逐例与旧解析相同。遗漏除escaped DFF外还包括escaped buffer，s820另有旧代码主动排除的probe。这里是cell面积，不是core/die面积；新增面积回收分母仍须展开原始baseline层次，不能直接确认旧14%。
- **固定寄生结论不能当物理安全证明**：s382 空操作 DEF 重入与原独立 STA 逐位一致；同起点完整合法化/重布线/提取后，历史回退配方13处仍有面积收益，但 propagated-clock setup差−0.0099716346 ns、hold差−0.0000185962 ns、TNS差−0.312647 ns，未过预注册1e-6 ns严格不退化门。两臂路由DRC=0并不等于完整约束通过。
- 原生 `recover_power 100` 在此例0次resize，与CONTROL相同；这是单例可行性测量，不能称超过调优后的最强基线。三臂setup仍负，不能称时序闭合。DRV约束覆盖与完整SEC按实际回执，不猜测通过。
- 当前状态 **NON_PROMOTION**。先修完整面积/动作解析及物理接受链，再考虑联合恢复或学习加速；不以此单例否定恢复方向，也不修改冻结论文。配置、失败原件及量化结果见 `project_docs/evidence/recovery_qualification_20261112/`。

> **效力**：本文件是项目**唯一**的现行口径。与任何其他文档冲突时，以本文件为准。
> **范围**：`project_docs/` 下其余 150 余份文档一律视为历史记录，只能作为溯源，**不能作为决策依据**。
> **维护**：产生新读数或新裁定 → 先改本文件，再落 `LOGS.md`。**禁止在别处另立一份「最新说法」。**
> **核验**：2026-11-04 10:20（GMT+8）。以下每个数字都标了可直接复核的来源。

---

## 0 三十秒定位

| 问题 | 答案 |
|---|---|
| 论文现在什么状态 | **r28 + r94–r101 口径 + r102–r116 实验与修订（2026-11-09）**。中文主稿 11 页 / 7 图 / 5 表 / 17 refs + 补充材料 15 页 / 22 表 / 5 图 + 英文 26 页（英文仍停在 r94 前叙事，**未同口径**） |
| 有没有做完却没进论文的东西 | **极少**：扩面族 1393 候选 × 三档物理标签仍 **0 命中**；其余实验均已入文或明确记为未评估（b05、s820@u35） |
| 项目最硬的结论 | **收益来自覆盖，不来自权重或规模**：W1 8/8 正、合计 1.29→**1.68 ns**（补入触发器后）、**7/8 超各自判定带**、扣带净额 0.1616 ns；节点加权、JOINT、pin swap、扩覆盖、加带五条抓手全部否证 |
| 下一步唯一该做的 | 见 §8；当前未决集中在论文档位与提交，不在机制 |

---

## 1 论文定版（r28 底稿 + r94–r101 口径 + r102–r116 实验与修订）

**r94（2026-10-28）只加限定句，不改任何数字、不加新图、不加新实验、不减内容。** 内容清单见 `paper/zh/CHANGE_LOG.md` 的 r94 条目。

**r95（同日晚）在主稿 §4.1 加判定带分解句**：5/8 电路超各自带、贡献 89.1%、扣带净额 0.12120 ns、余 3 个低于噪声分辨率；带取 ISCAS89 基族逐电路 `cand_threshold`（0.024558–0.08474 ns），**非** ITC-99 的 0.049752。

**r95b（同日）去防御化**：主稿 19 处、补充 2 处，删元话语、合并多重免责、去重复、语序陈述化，**不改读数**。

**r96（2026-10-30）把固定布局四数写进 §4.5 + 补充 S4.2/S4.3**：主稿新增一段 + 表 6（8 例布线后基线/修改后/改善），A′ 段两处改口径（补「两侧各自独立完成布局与布线」、把「方向并非全部保持」限定为「该单点实现上」），§5 两处推论句随之改写（删「物理估计后的收益损失」，改为带内差值不可确认）；补充新增 S4.2（表 S12，A/B/C/D 四数）、S4.3（表 S13，ITC-99 六例），并把两处硬编码「主文表6」改为「主文表7」（插入新表后原表顺延）。

**r98（2026-10-30）五位评审大修落地 + 压页回 10 页**：① **口径纠错（C2 级）**——固定布局后验的网表对**不是受控 W1**，而是**策略枚举纯 G 臂**。证据两条：`20261029_eco_phys_contrast/<c>/eco/raw.v` 与 `20260826_ablation_pureG/<c>/mapped_hybrid.v` **逐字节相同**（s27/s382 已核 md5）；同布局族 `20261029_eco_phys_samelayout` 的 **C−A 逐例 8/8 等于表 4 纯 G 列**（0.09/0.17/0.35/0.45/0.05/0.02/0.07/0.09），而 W1 为 0.09/**0.15**/0.35/**0.46**/0.05/0.02/0.07/**0.10**。主稿 §5.5、补充 S4.2 正文与表题、表注统一改为「纯G配置」，并写明「理想档合计与 W1 同为 1.29 ns（5 例相同、3 例差 0.01–0.02 ns），两族终点网表不同，本节读数不能当作 W1 网表读数」。补充 S4.2 原「口径差尚未查清」改为**已查明＝族差**。② **判定带统一**：以逐电路带 0.02456–0.08474 为主口径（8 例中 **5 例超带**，s820/s713/s832 记未确认）；跨族带 0.049752 只用于 ITC-99 族，补充注明「若统一按 0.049752 计则 6 例」。③ 其余评审点：0.12120 明写为截断均值（与 89.1% 非区间）、W0/U0 补「每电路仅 5–12 次评估、0 提交」、两组后验差异**不归因布局控制**、补充 S4.3 补 b15 主导性（占合计 45%、B=−30.18、恶化 125.6%）。④ **压页（10→11→10）**：表 5（W1 网表代价）并入正文（8/8 缓冲列恒 0、单元数列 8/8 不变，仅面积列有效），**主稿表数 7→6**（两份均含 1 个跨栏 `table*`，只数 `begin{table}` 会漏 1 张），原「表 7 简化线载」现为**表 6**（补充两处「主文表7」已同步改「主文表6」）。

**r99（2026-10-30）冷读修表与一处数字纠错**：① **四数组超带数 5→6**——s820 的 $+0.08$\,ns 高于其逐电路带 0.0717\,ns（高出 0.008、小于重跑噪声 0.03），r98 把它与 s713/s832 一并写成「在带内」不成立；现口径为「6 例高于带值，其中 s820 余量小于噪声，s713 与 s832 在带内，三例记未确认」。主稿 §5.5、补充 S4.2 正文与表注统一，补充原「若按跨族带 0.049752 则 6 例」的第二口径已删。② **表 5 恢复「修改后 D」列**（r98 曾以「可由基线+改善还原」删去；冷读表明读者不会还原），现为 电路/B/修改后D/改善/比例，表注写明 B、D 均为布线后、A/C 见补充 S4.2。③ **判定带 σ 来源写明**：σ 由独立物理标签族按电路估计（每电路 6 对配对网表，df=5），不取自本节读数——排除循环论证怀疑。④ 其余：表 2 补「两臂数值相同故合并」（读者原需自行凑 6858）；§5.1 点名 5 个超带电路；§5.5 开篇区分三组「8 对」网表、末段写明 5/8 与 8/8 差异源于网表对与寄生来源均不同；「规范化门集合」→「排序后的门集合」，补「关联引脚计数」定义与 $\langle\cdot
angle$ 记号。⑤ 压页 11→10（句内压缩，未删数字、未缩字号）。

**r100（2026-10-31）四数口径扩面、按测试集分表**：① **ITC-99 b01--b10（10 例）**写入补充 S4.4（`sec:itc_ext`，表 S14 `tab:itc_ext`）：D−B **9/10 为正**（$+0.01$--$+1.19$\,ns），均值 **0.2840**、中位 **0.0750**，**6/10** 超跨族带 0.049752、8/10 超 0.03 噪声；比例 $-0.3\%$--$43.6\%$（均值 11.1\%），合计 2.84/20.20＝**14.1\%**；**唯一负值 b04＝$-0.01$\,ns**，小于噪声底，记带内未确认，不删不改。与既有 6 例合并 **n=16**：15 正／12 超带／14 超噪声，均值 0.8969（受 b15 单例主导）、中位 **0.2150**。② **ISCAS89 新 9 例（7 例有效）**写入补充 S4.5（`sec:iscas_ext`，表 S15 `tab:iscas_ext`）：D−B **7/7 为正**（$+0.01$--$+0.78$\,ns），均值 **0.1700**、中位 0.04，3/7 超跨族带、5/7 超噪声；比例 0.6\%--18.6\%（均值 7.0\%），合计 1.19/12.48＝**9.5\%**；s400 与 s444 换门 0 个、无候选。③ **三处处置随表记录**：ITC 首版输入为 Windows 侧 Yosys 0.67 映射且 `dff` 子模块残留（b03 30 个 `dff`、仅 1 个 `dfxtp`），已隔离 `_stale67/` 并在 WSL 内 0.70+255 重映射到 `_src_y70/`；b05/b07/b09 的 `assign 1'h1` 常量网络被 TritonRoute 判 POWER/GROUND 拒布（`DRT-0305`），读 DEF 后把 `one_`/`zero_` 改 SIGNAL 解决，不改网表与约束；ISCAS 扩面取 17 例族网表，与主文表 5 纯 G 终点网表非同一批，两表不并。④ 主稿 §5.5 末段加 1 句指向 S4.4/S4.5，**既有读数与图表一律未动**。

**r101（2026-10-31）布局实现敏感性、判定带作用域收窄**：① **实验** `experiments/20261031_layout_stability/`：s641 与 b13 × floorplan 利用率 30/35/40 × base/ecofix 共 12 次运行，D−B 符号 **6/6 全正**（s641 +0.86/+0.89/+0.84，极差 0.05 ns；b13 +0.11/+0.10/+0.10，极差 0.01 ns），C−A 三档恒定（+0.45/+0.05），**util 35 逐位复现**主文表 5 的 s641 与表 S13 的 b13 读数（A/B/C/D 偏差均 0.0000）⇒ 流程确定、差异归因 floorplan；12 次布线 DRC 全 0，网表与换门清单三档逐字节相同。② **新增限定**：s641 跨布局极差 0.05 ns 约为其逐电路判定带（0.0246）的 2 倍 ⇒ **判定带与 0.03 ns 噪声底均只覆盖网表级离散，不含布局实现离散**；大效应例不受影响（0.86 为带值 34 倍），边际例（s820 的 +0.08 对带 0.0717、b04 的 −0.01）仍记未确认且理由升级。已登记 **OI-074**。③ **论文**：补充新增 S4.6（`sec:layout_stab`）与跨栏表 S16（`tab:layout_stab`，6 行三档四数），主稿 §5.5 噪声底句后加 1 句（读数 + 带值作用域 + 指向 S4.6）；**既有读数、图表与结论主句一律未动**，补充 11→**12 页**、表 16→**17**，主稿仍 **10 页**。

**注**：§5.1 理想档 5 例超带（s27/s382/s420/s641/s953）与 §5.5 四数组 6 例超带是两批不同读数，勿混。

**r102–r116（2026-11-02 ~ 11-09）**：逐步记录见 `paper/zh/CHANGE_LOG.md` §r102–§r116 与 `LOGS.md` LOG-20261102-01…04、LOG-20261103-*、LOG-20261104-*、LOG-20261109-*；此处只留裁定级结论。

1. **五条"加机制"的路全部否证**：决策层实现本就是候选集 argmax（r102，加带把累积从 8/8 打到 4/8）；pin swap 0/4 超带、中位 0.0388 ns（r104）；JOINT 深度 3 有 7/8 终点逐位相同（r106）；每实例候选上限作为预算分配手段不改变受控零点（r107/108）；扩覆盖 8→10000 同预算增量 **0.0000 ns**（r110a）。
2. **判定带作用域收窄（OI-074）**：48 次物理流程显示带与 0.03 ns 噪声底**只覆盖网表级离散，不含布局实现离散**（s953 跨布局 0.02↔0.19）。
3. **外部参照**：同 8 网表 + 同 Liberty + 同 OpenSTA 读法下 OpenROAD `repair_timing -setup`（默认参数）合计 **2.3286 ns、8/8 超带**；本文 1.29 ns 时为其 **1.81 倍**，补入触发器后为 **1.39 倍**。**只作幅度参照**（预算不对等、动作集不同），不作优劣判定。
4. **映射族守门**：0.67 族网表上重跑 OpenROAD 与 0.70 族首跑 **8/8 逐位相同** ⇒ r111 的"比值作废"已撤回；判据是"网表是否同一批"，不是"映射器版本是否相同"。
5. **动作集缺口已补（OI-077 关闭，r113）**：触发器以 `module dff` 共享壳存在，改壳会被等价检查 fail-closed 拒。改为**就地展开**（`dff` 实例换同族 `dfxtp_*`、helper 字节不变），检查器只加一条精确 fold-back 识别。结果 3 例接受（s820 +0.11、s832 +0.15、s953 +0.13），合计 **1.29→1.68 ns（+30.2%）**、**超带 5/8→7/8**、候选 STA +11.8%、面积 +2.45–3.18%、**独立全网表 SEC 3/3 通过**；`all` 与 `cone` 同终点但 `all` 的 STA +21.6%、s953 面积 +7.37% ⇒ **作用域取 cone**。
6. **布线后保留（r113b）**：s820/s832/s953 布线后增量 **+0.4102 / +0.4085 / +0.3655 ns**，为理想档的 **1.6–3.2 倍**（收益在真实寄生下被放大）；u35 下 s832 +0.4011、s953 +0.3783 互证，s820 两次详细布线均未收敛，记未评估。三例布线后 WNS 仍为负 ⇒ 只主张**违例收窄**，不主张收敛。
7. **ITC-99 复现（r114）**：b01 0.01→0.06（超 0.049752 带）、b03 0.66→0.72，合计 **0.69→0.80（+15.9%）**、候选 STA +20.7%、SEC 2/2；b02 被 F3 补丁比例与 TNS 规则拒（与 s641/s713 同类）。该组为另起的同配置对照，**不与表 3 跨测试集族合并**；b05 未跑完不纳入。
8. **映射族不统一（OI-078，won't-fix）**：0.70 网表喂受控运行器为 **0 候选 / 0 STA**（割构造不通，非解析问题），统一等于重做 72 次主矩阵 + 换触发器实现 + 全文改数。维持 0.67 = 论文主族、0.70 = ITC-99 与物理后验；**跨族只比方向与量级，不比差值**。
9. **可复现性（r115）**：从原始 RTL 重新映射（同一 0.67 路径）后重跑覆盖优先配置，8 例终点读数与候选 STA 次数**逐例复现表 3**（合计 1.29 ns、847 次、5/8 超带），不依赖归档中间网表。
10. **判定带的布局限定入文（r116，OI-074 的论文侧；2026-11-09）**：机制审查三方向中，A（换判据档解锁 B 类）**证伪**（扇出线载模型结构上无法表达缓冲收益，见 `EXPERIENCE.md` r117）、C（判据/排序换布局后档）**预证伪**（r30 的 LOG-20261025-34 已测、决策级 H1 两族均未触发，见 r119），B 以 r103 的 8 例×3 档数据落地：主稿 §5.5「6 例高于带值」加「利用率 35 这一次布局」限定、噪声底句由 r101 两例扩为 r103 八例、补充 S4.6 表由 2 例扩为 8 例 23 行并补 s27/s953 两条未评估边界；**冻结读数、主结论、图表编号与 7/8 超带等头条数字均未动**，补充 14→**15 页**。对应 LOG-20261109-04。

11. **真实布局寄生档做接受判据（2026-11-10，预注册实验 `20261110_placed_gate`；论文数字未动）**：把接受判据从理想档换到**真实布局后端**（floorplan→place→CTS→`set_wire_rc met2/met4`→`estimate_parasitics -placement`），端点改用**完整布线 + RCX 提取 + 独立 `sta` 读 SPEF**。4 例（s382/s641/s832/s953）× 两臂（I=理想判据、P=布局判据）。**H1 构成 PASS**：臂 P 在 s641/s832 各接受 1 个 B 类缓冲（+0.0270 / +0.0109），臂 I 4 例 11 个接受 B=0（W1 全 8 例 0/606）⇒ **"理想判据废掉缓冲插入"在真实布局寄生下成立**。**H2 转移 FAIL**：布线后增益 I +1.1157 ns（均值 0.2789）/ P +1.2495（0.3124），P 更好仅 **2/4**、均值差 **+0.0334 ns** < 预注册 0.05 门槛；H3 分辨率份额 0.50 未过 ⇒ **PROMOTE = NO，按既定规则停止、不扩 8 例、不调参重跑**。可写的最强结论是**成本**：把 gate 抬到该档位自己的分辨率（布局离散 0.055 ns）后，`P_g005` 4 接受 / **602 次候选评估** 对臂 I 11 / **1157**（**−48%**）而端点不降（均值 0.3095 / 0.3067 / 0.3124 / 0.2789 互不可分辨）；补丁链 9 个接受步中 7 步布线后为正、2 步为负（−0.0326，同一补丁），"验证式接受"可得量级 ≤0.03 ns/例 ⇒ 决策效应要高于噪声须**加大动作粒度**，不是换更贵的判据。**不得**据此写"布局判据更好"。代码新增 `code/src/rseco/placed_sta.py`、`code/src/rseco/routed_sta.py`，`real_wns.py` 增 `physical_backend` 分派（默认仍 `spef`，理想档路径未变：臂 I 终态网表与 W1 逐字节相同）。对应 `LOGS.md` LOG-20261110-01、`EXPERIENCE.md` r120、`experiments/20261110_placed_gate/REPORT.md`。

12. **布局集成判据（arm E，2026-11-11）**：把接受判据的判决换成 k=3 布局读数均值后，
    单布局判决与集成判决在「接近门槛」候选上的分歧率 **46.8%**（H1 PASS，说明单布局档判决确实一半是布局抽签），
    但**端点收益没有随之兑现**（H2 FAIL：E 优 2/4，均值差 +0.0112 ns < 0.05；H3 成本 0.84×），
    **不晋级、不得写「修判决精度能提高质量」**。机制侧瓶颈定位为**单次动作的效应量/测量分辨率**，
    不是接受判据精度。证据：`experiments/20261111_placed_ens_gate/REPORT.md`；代码 `physical_backend="placed_ens"`。

13. **动作粒度（arm A6j / A6，2026-11-12）**：把一次动作从 2 门放大到 6 门（机制已有的
    `--joint-k`，不改判据）后，**端点仍不动**。4 例 × 三布局布线后均值：A6j +1.2289 / 均值 0.3072
    对 arm E +1.2381 / 0.3095，**差值 −0.0023 ns**（预注册 H2 FAIL：仅 1/4 优）；成本 1.15×（H3 PASS）。
    **H1 也是 FAIL**：8 个被接受补丁里只有 **1 个**是 6 门联合动作（贪心单步选择下，单门动作几乎
    总能赢，s641 单门 +0.609 对 6 门 +0.4767）⇒ **不是"大动作没用"，而是"机制几乎不选大动作"**。
    补丁链（布线后逐补丁增量）给出本轮最重要的正面线索：**两个最大增量 +0.1001 / +0.1253 都来自
    B 类插缓冲**，即理想线网判据从不接受、而真实布局档判据才开始接受的那一类 ⇒ 下一步应把 **B 类
    做成主搜索方向**，或改选择结构（多联合候选 / 先接受后组合），而不是继续调阈值。
    **不得**据此写"动作粒度不是瓶颈"的强版本，只能写"在当前贪心单步 + 每轮 1 个联合候选的结构下
    放大动作宽度不转化为端点收益"。证据：`experiments/20261112_action_granularity/REPORT.md`。

14. **按种类校准排序（arm K，2026-11-13）**：把「已过物理门的候选」按 `layout_delta × k[kind]` 排序
    （`k` 固定为 B 5.64 / G 0.60 / JOINT 0.53，来自 s382+s953 的 4 个逐补丁布线后步；**接受门仍用原始
    布局档 delta ≥ 0.010 ns**，故校准不能放进物理未过门的动作）。结果：**判决确实改变**（s641 接受 2 个 B、
    s953 2 个 B、s382 1 个 B，而 arm E 在同样电路上 0 个 B），**但端点没有转移**——
    布线后三布局均值 s641 +0.9444（E +0.9093）、s832 +0.0131（E +0.0131 ⇒ **±0.0000**）、
    s382 +0.1851（E +0.1780）、s953 **+0.0401（E +0.1377，−0.0976）**；held-out 两例均值差 **+0.0175 ns**
    < 0.05（H2 FAIL）、B 接受在 s832 为 0（H1 FAIL：pools 里 20 轮仅第 1 轮有合格候选且无 B 过关）、
    候选 STA **1005 vs 738 = 1.36×**（H3 FAIL）⇒ **PROMOTE = NO，停线**。
    **不得**写「按种类校准能提高质量」；**也不得**反写「B 类无价值」——本轮只证到「4 步估出的常数不足以
    支撑可转移的排序规则」（s953 在 util 0.35 的布线后读数 −1.8794 比 base −1.8769 还差）。
    重开前提：先补**每电路 5–10 个逐补丁布线后配对**再重新拟合。证据：
    `experiments/20261113_buffer_calibration/REPORT.md`；代码 `postroute_calibration` / `_candidate_score`。
- **2026-11-14：判据侧选择空间上限（离线分析，不构成新判决）**。四臂统一到三布局布线后均值后，
  端点 4 例均值 I 0.2727 / P 0.2983 / E 0.3095 / K 0.2957 ns（极差 0.0368）；合格池 top-3 同实例仅 15%（3/20 轮），
  但跨臂 top-1 同实例 4/7、同种类 6/7；逐补丁"布局档 vs 布线后" Spearman 0.164（n=10）。
  ⇒ 判据有自由度但落在布局噪声 0.1042 ns 之下，**继续改判据的期望收益 ≈0**，瓶颈在候选生成与动作集。
  禁写"某个判据更优/更差能提高质量"；再开判据侧实验前必须先做离线回放并报告 top-1 跨判据一致性。
  见 `experiments/20261114_selection_ceiling/ANALYSIS.md`、`project_docs/LOGS.md` 2026-11-14 条。

15. **方向转折：从预布局机制优化转布局后 SOTA ECO（2026-11-11）**。六轮预注册实验封口后，
    用户明确「要做新 SOTA、要实证不要论述」→ 项目方向从「预布局门级 ECO 的判据优化」转为
    「布局后（post-placement）覆盖优先 ECO 对标 OpenROAD resizer 与 E-Layout（ICCAD 2026）」。
    **差异化**：覆盖优先调度（文献独一）+ 全开源 + 更宽动作空间（R+G+B+JOINT）。
    **路线**：P1 FAECO-P vs resizer → P2 +ML 排序器 → P3 跨设计迁移 → P4 Pareto 多目标。
    完整路线与判定门见 `project_docs/FAECO_ROADMAP.md`。
    **不得**重启已被裁决的六条不可能门与路线文档 §4 新增十二条。
    交叉引用：`docs/EXPERIENCE.md` r124、`project_docs/LOGS.md` LOG-20261111-01。

16. **P1 判定：FAECO-P 输给 OpenROAD resizer（2026-11-11，`experiments/20261115_p1_resizer_vs_faeco`）**。
    8 例 ISCAS89、同 W1 网表、三布局（util 0.30/0.35/0.40）布线后均值：base→resizer **+0.5836 ns**、
    base→FAECO-P **+0.2473 ns**、FAECO-P−resizer **−0.3362 ns**，**0/8 电路更优**（预注册门槛 ≥5/8 且 ≥0.05）
    ⇒ **PROMOTE = NO**。
    差距主因是**动作量**（布线后 DEF 逻辑单元净增：resizer 8/9/13/38 vs FAECO-P 0/0/0/1；FAECO-P 八例仅接受 16 个
    单实例补丁），与本文"收益来自覆盖"一致；成本上 FAECO-P 每候选 3 次布局判决，也劣于 resizer 的单次全局 LR。
    **不得**写「换更聪明的判据可超过 resizer」，**也不得**写「FAECO-P 无效」（对 base 8/8 为正）。
    该路线（以判决精度取胜）至此封口；下一步只允许问**可组合性**——同一 resizer 流程、只把起始网表换成
    FAECO-P 输出（Hybrid 臂，公平 A/B）。证据：`experiments/20261115_p1_resizer_vs_faeco/REPORT.md`、
    `docs/EXPERIENCE.md` r125、`project_docs/LOGS.md` LOG-20261111-02。

17. **Hybrid 组合臂同样不晋级（2026-11-11，`summary_hybrid.json`）**。同一 resizer 流程、只把起始网表换成
    FAECO-P 终点网表，三布局均值：胜 **5/8**、均值差 **+0.0243 ns** ⇒ 胜场达标但幅度未达
    +0.05 ns 门槛，**PROMOTE = NO**。增益集中在 s820（+0.1559）/ s953（+0.0680），s832（−0.0623）/s641（−0.0215）/
    s27（−0.0125）反向，量级与布局离散同阶。
    ⇒ **不得**写「我们的 ECO 与 resizer 组合有收益」；P1 及其组合臂一并封口，本路线续做必须换题
    （只允许"把 resizer 当内层优化器、我们做预算调度"这类可量化的调度问题）。
    该臂为**事后追加**（P1 判定后提出），判据在读数前写定，但结论强度不得等同预注册臂。
    证据：`experiments/20261115_p1_resizer_vs_faeco/summary_hybrid.json`、`REPORT.md` §4b、
    `docs/EXPERIENCE.md` r126、`project_docs/LOGS.md` LOG-20261111-03。

18. **P1′ pilot：resizer 终点之后仍有残余空间（2026-11-11，`experiments/20261116_resizer_then_faecop`）**。
    镜像组合——resizer 先做（pre-CTS `repair_timing` 变体）、我们的 ECO 在其终点上继续做，对照臂用**同字节**网表重测。
    3 例 pilot、三布局（util 0.30/0.35/0.40）布线后均值：RF−R′ = s382 **0.0000**、s641 **+0.1202**、s832 **+0.1157**，
    均值 **+0.0786 ns**；预注册门（≥2/3 为正 且 均值 ≥+0.05）**PASS，PROMOTE=YES**。逐补丁归因（util 0.35）：
    5 个被接受补丁的布线后增量**全部为正**且单调累积（+0.0520/+0.0444/+0.0353 与 +0.0538/+0.0508）。
    ⇒ **可写**「在一个 pre-CTS resizer 变体终点上，我方单实例动作仍有 +0.12 ns 量级残余空间，两者动作空间互补」；
    **不得写**「在 P1 的 resizer 之上还有 +0.12 ns」——该变体终点比 P1 post-CTS resizer 弱 0.19/0.21 ns（re-entry gap），
    结论只限 RF vs R′ 配对；三例 pilot 不构成方法优越性证明（成本远高于 resizer 单次调用）。
    同轮修掉一条仪器缺陷：OpenROAD 扁平网表的多行实例（首连接与实例头同行）使解析器切碎、门数 0 ⇒ `KeyError`
    （`code/src/rseco/netlist.py`，commit `ef72abd`，回归用例 +18/+33 行），**修前所有扁平网表输入都不可用**。
    证据：`experiments/20261116_resizer_then_faecop/{PREREGISTRATION,REPORT}.md`、`summary.json`、
    `patch_chain_pilot1.json`；`docs/EXPERIENCE.md` r127；`project_docs/LOGS.md` LOG-20261111-04。

19. **P1′ 二轮：post-CTS resizer 终点之上没有残余空间（2026-11-11，`experiments/20261117_postcts_residual`）**。
    把 P1′ 的 resizer 段换成 **post-CTS** 变体（与 P1 实际对手同形），其余装置不变，三例 pilot、三布局端点。
    读数（WNS ns，三布局均值）：R′post **−0.8246 / −1.1135 / −1.1417**（s382/s641/s832），
    RFpost **−0.9906 / −1.6460 / −1.6296** ⇒ RF−R′ **−0.1659 / −0.5325 / −0.4879**，均值 **−0.3954 ns**
    ⇒ **H2 FAIL（0/3 为正）、PROMOTE=NO**；对照端点忠实（re-entry gap +0.0168/+0.0160/−0.0830，|gap|<0.15，未触发声明条款）。
    **根因（可写）**：布局档（`estimate_parasitics -placement`）在 post-CTS 终点上**不是可迁移代理**——
    同一网表 placed 判 −2.10、布线后 −1.11（差约 1 ns），且 +0.609 的布局档改善在布线后翻成 −0.532
    （探针证明该 +0.62~+0.64 与双重建 CTS 无关：with-CTS +0.6369、skip-CTS +0.6187）。
    ⇒ **可写**「在 post-CTS resizer 终点上，本文机制的接受补丁使布线后 WNS 3/3 变差（均值 −0.395 ns）；pre-CTS pilot 的正转移不迁移」；
    **不得写**「post-CTS 终点没有残余空间」（只试了本机制的动作空间与判断器）、「resizer 已最优」、
    「pre-CTS pilot 结论作废」（它回答的是另一个（较弱）变体终点）。
    P1′ 线在当前机制下封口；继续必须先解决**判断器与布线后端点的读数一致性**，而不是换动作空间。
    仪器：post-CTS 网表重入标准流程需 `skip_clock_tree=True`（`code/src/rseco/routed_sta.py`，默认渲染不变，回归 `PostCtsFlowTest`）。
    证据：`experiments/20261117_postcts_residual/{PREREGISTRATION,REPORT}.md`、`summary.json`；
    `docs/EXPERIENCE.md` r128；`project_docs/LOGS.md` LOG-20261111-05。

20. **Recovery 诊断：Resizer 69% 改动对 WNS 无贡献，FAECO 面积效率 4.4×（2026-11-12，
    `experiments/20261112_resizer_recovery`）**。对 Resizer 在 8 例 ISCAS89 上的 107 个改动逐 reversion
    测量（路由后签核 STA、理想时钟、`sta_routed`，max_degradation=0.05 ns）：**74/107（69%）回退后
    WNS 纹丝不动**（Δ=0.000 ns）——直接逐门核证 Resizer 的盲目放大。主结果：FAECO-P 面积 +8.1% 换
    +0.247 ns WNS 改善 vs Resizer +48.8% 换 +0.584 ns ⇒ **FAECO 面积效率 4.4× Resizer（几何均值，
    7/8 例，p=0.0352）**，逐例效率比 s27 23.5× / s382 1.5× / s420 4.6× / s641 2.2× / s713 9.2× /
    s820 5.5× / s832 0.5× / s953 3.0×。**可写**"FAECO 面积效率是 Resizer 的 4.4×"、"Resizer 69%
    改动可逐门核证为浪费，FAECO 通过覆盖优先从根源上避免了这种浪费"；**不得写**"FAECO WNS 优于 Resizer"
    （Resizer 均值 +0.584 > FAECO +0.247，面积换来的）、"Resizer 无效"（对 base 8/8 为正）、
    "Recovery 臂是生产流程"（离线诊断工具）。代码落点：`experiments/20261112_resizer_recovery/run_recovery.py`
    （v4，正确 Liberty area 解析 + `sta_routed` 评估）。面积效率法的结构性解释（覆盖优先只改关键门 vs
    全局 LR 大开大合）为此前各裁定（11–17）中"动作量是主要差距"提供正面诊断证据。记录：
    `project_docs/LOGS.md`（LOG-20261112-01）、`docs/EXPERIENCE.md`（r129）、`REPORT.md`。

| 项 | 值（r116 现行） | 来源 |
|---|---|---|
| 版本 | r28 底稿 + r94–r101 口径 + r102–r116 实验与修订 / 2026-11-09 | `paper/zh/CHANGE_LOG.md` §r116 |
| 主稿 `.tex` SHA256 前缀 | `d5bbc9bd`（51,669 B，纯 LF，484 行） | 本日实测 |
| 主稿 PDF SHA 前缀 | `47c5964c`（3,024,657 B） | 本日实测 |
| 补充 `.tex` / PDF 前缀 | `c9c73242` / `04df3914`（86,744 B，纯 LF，916 行） | 本日实测 |
| 英文 `.tex` / PDF 前缀 | `327987d2` / `a14498a7`（纯 LF，**自 r96 起未同口径**） | 本日实测 |
| 页数 | 主稿 **11** / 补充 **15** / 英文 **26** | `pdfinfo` 实测 |
| 规模 | 主稿 `\bibitem` **17**、图 **7**、表 **5**（4+1 跨栏）；补充 表 **22**（20+2 跨栏）、图 **5** | 本日实测 |
| 编译引擎 | **lualatex**（xelatex 会产出 2.32 MB 的异构 PDF，两者不可混当同一版） | 2026-11-03 实测 |
| 质量门 | 主稿 0 Errors / 0 Overfull / 0 Underfull / 0 `??`；补充同 | `latex_quality_gate.py` |
| 冻结纪律 | 任何内容改动（**含摘要**）须用户明确同意（r96 起历轮修订均已获用户授权） | `AGENTS.md` |

21. **Recovery v2 全量通过：选择性回退 3 例 ≥20% 面积回收、全例 ΔWNS ≤0.006 ns（2026-11-12，
    `experiments/20261112_resizer_recovery`）**。在 Resizer 的 post-CTS 终点网表上，对 107 个被修
    改的 gate 逐一独立 STA 评估 WNS 影响，用安全系数 1.5×（补偿逐候选间时序耦合）+ 后验证循环（退化
    超标则逐次回退最后一步）累积回退。v2 全量 8 例结果：65/107（61%）回退、**3 例 ≥20% 面积回收**
    （s382 22.8%, s820 20.1%, s953 21.6%）、**全例 ΔWNS ≤0.006 ns**（最大绝对值 0.0057 @ s420）、
    无一例 WNS 差于 baseline。CLI 工具 `code/scripts/recover_area.py`（`--resizer-dir` + `--baseline`
    → 自动出 `summary.json` + `recovered.v`，s382 8 秒完成）。论文 draft 见
    `paper/en/manuscript/FAECO_recovery.tex`（IEEEtran, pdflatex 编译 4 页，0 错误 0 undefined refs）。
    可写：「在 Resizer 最佳 WNS 基础上选择性回退不必要改动，平均回收 14.1% 面积而 WNS 无损」。
    不得写：「我们改进了 Resizer」（其 WNS 步骤原样保持，只在之后回退）、「我们的 ECO 优于 Resizer」
    （不同任务——Resizer 做优化，我们做恢复）。记录：`project_docs/LOGS.md` LOG-20261112、
    `docs/EXPERIENCE.md` r129。

**r97 改善比例口径（引用前必读）**：比例 = 改善量 / **该档位基线 WNS 绝对值** × 100。预布局 `(C−A)/|A|`、布线后 `(D−B)/|B|`。ISCAS 8 例逐例均值 **15.9%**、总量比 **15.4%**（1.97/12.83）；ITC-99 6 例逐例均值 19.6%、总量比 15.1%（11.51/76.45）。**两族不得合并统计**（规模、修改构造、布局条件均不同）。**比例必须与绝对改善并列读**：s27 的 `+0.13 ns` 因基线仅 `0.39 ns` 而显示为 `33.3%`，与 `+0.89 ns` 的 s641（36.2%）几乎相同，绝对量差 6.8 倍。数据源 `experiments/*/ratio.tsv`（`code/scripts/gen_ratio_table.py` 生成）。

**中英口径到 r94 为止同步**：ITC-99 SEC **16/19**（三态 b09/b20/b21 不计入二态证明）、b17 **12,879 点 / 0 未证**。英文旧值 `18/19` 与 `12,812 + 1` 已清零。**r95/r95b/r96/r97 四轮只改了中文两份**，英文仍用旧叙事（摘要 `1.07 ns 对 0.16 ns`、§4.5 仅「5 改善/1 持平/2 退化」），**不得据英文稿反推中文口径**。

**前版（r28 原样，仅存档参考）**：`.tex` `f0f4d5e0`（46,137 B）、PDF `e71feb3d`、CJK 8554。

**基线已收口（2026-10-28）**：`active` = **v19 / r28**（tag `25a1796`），`versions/v19/MANIFEST.sha256` 148 条，**在该提交检出时** `sha256sum -c` 为 148/148 OK。此后 r95/r95b 的文本改动与 r108/r113 的代码改动均未重建清单：**2026-11-04 实测 139 OK / 9 FAILED**——主/补两份 `.tex` + 四个 PDF 副本（r95/r95b），加 `code/src/rseco/real_wns.py`、`code/tests/test_r22_cli_controls.py`、`code/tests/test_r22_scope_integration.py`（r108/r113），**全为预期漂移、非损坏**。**r21–r27 共 7 轮仍无基线**，只能从 `review_rounds/` 取中间稿。校验 v18 须先 `git checkout 73dc0e7`（v18 MANIFEST 记 `.tex` = `f65929ca`）。编号偏差：v19 对应 r28，打破旧约定 `vN↔r(N+2)`；定稿后统一建 v20 收录 r95–r115。

---

## 2 论文的 8 条声称 vs 证据（强度裁决）

**这是本文件最该看的一节。** 可写 = 直接保留；须加限定 = 必须补口径句；撑不住 = 不得再主张。

| # | 论文声称 | 证据状况 | 裁决 |
|---|---|---|---|
| 1 | 覆盖优先 W1 在 **8/8** 电路改善，平均 **0.161 ns** | 72 次运行；W0/U0 全无改善、W1 8/8、s641 省 8 次 STA | **可写**，但必须写明**理想线网档**；且须说明 0.161 是轨迹累计，**单候选边际中位数只有 0.020 ns**（§7.2） |
| 2 | 候选 STA 次数比 3 个随机顺序配置少 **7.8–19.0%** | 表 11 | **可写**——这是全篇最硬的一条 |
| 3 | 加权与统一容量**未观察到差异** | W1 vs U1 | **可写**（干净的负结果） |
| 4 | 同库单元面积 **+0.27%–4.92%** | 面积表 | **可写** |
| 5 | 跨测试集 ITC-99 表 | 只报**理想档** | **须加限定（F-1）**：同一批端点在布线后档，13 个已标电路中 b01/b02/b04/b06 增量落进判定带，**b04 由 +0.18 → −0.01** |
| 6 | §5.6 物理后验 **5 改善 / 1 持平 / 2 退化** | **单一实现点** | **须加限定（F-2）**：同族其他归档实现上 s420、s953 符号翻转、s832 变改善；这些 0.01–0.02 ns 差**全落在实现轴**（族内地板 0.000000 ns） |
| 7 | 顺序等价性 **18/19**（EN）/ **16/19**（中文） | 两稿不一致 | **中英冲突**，须统一（P1 附带） |
| 8 | b17 规模 **12879 点**（EN：12812 点 + 1 未证） | 两稿不一致 | **中英冲突**，须统一（P1 附带） |

---

## 3 冻结数字（引用前不需再查；改动须记 LOG）

| 数字 | 值 | 性质 |
|---|---|---|
| **判定带（主口径）** | **逐电路 0.024558–0.08474 ns**（基族 `cand_threshold`） | ISCAS89 八例的超带判定只用这一列；r95 起为主口径 |
| **判定带（ITC-99 族）** | **0.049752 ns / `full_family`**（量子格 idx 5） | 只用于 ITC-99 族；**禁**套到 ISCAS89 八例上 |
| 噪声底 | 同网表重跑 \|ΔWNS\| ≤ **0.03 ns**（中位 0.01） | 只含网表级离散，**不含布局实现离散**（OI-074） |
| OpenSTA 报告量子 | **0.01 ns** | 决定「改善」的最小分辨率 |
| 判据门槛 | `Δ_WNS > 0`（式 `eq:accept`） | 是实现里的 argmax 细节（r102 反事实已证），**不代表可分辨** |
| 三元组（族 B） | 8/8、18/19、2/2 | 摘要级 |
| 三档衰减 | ITC-99 **0.8524 / 0.7278**；ISCAS89 **0.8911 / 0.7870** | 衰减集中在布局阶段 |
| H1（扩面族） | `structural − kind_only` = **+0.103**，CI `[0.052976, 0.177924]` | **CI 不含 0**；绝对 AUC **0.500238** vs **0.401095**（两者都在随机附近） |
| H2 | 布局后 **0.843611** / 理想 **0.353081** | 说的是「便宜档很强」，**不是**「结构特征到顶」 |
| GNN | 池内 AUC **0.479242** < `kind_only` **0.555062** | 信号 ≈ kind |
| H3 富集 | **10.007411**（扩面族）/ **7.5593**（基族） | 两族都对，**不可混用** |
| H4 | **58/58**（48 同口径 + 10 跨口径） | 10 对只证明两个标签定义等价 |
| **W1 终点（表 3）** | 合计 **1.2900 ns**、均值 **0.16125**、**5/8 超带**、候选 STA **847** | 受控矩阵 W1 的 8 例 |
| **补入触发器（r113）** | 合计 **1.6800 ns（+30.2%）**、均值 **0.2100**、**7/8 超带**、扣带净额 **0.1616**、候选 STA **947** | 族 O；独立 SEC 3/3 |
| **外部参照（r112）** | OpenROAD 同网表 **2.3286 ns** = 本文 1.29 ns 的 **1.81 倍**；补入触发器后 **1.39 倍** | 族 N；**只作幅度参照**，不作优劣判定 |
| **布线后档（r113b）** | s820 **+0.4102** / s832 **+0.4085** / s953 **+0.3655 ns**（理想档的 1.6–3.2 倍） | 族 O 物理档；终点仍全负 ⇒ 只主张违例收窄 |
| **ITC-99 复现（r114）** | b01 0.01→**0.06**、b03 0.66→**0.72**，合计 **0.69→0.80（+15.9%）**、STA +20.7% | 族 P；b02 被 F3/TNS 拒，b05 未跑完 |

---

## 4 实验族 ↔ 论文节（切勿混用）

> **表号自 r96 起已重排**（固定布局四数进主稿、简化线载下沉补充 S4.8），本表只保证「族 ↔ 节」的对应；
> 具体表号以 `.tex` 里引用解析的结果为准，**不要从本表抄表号**。完整族卡（含守门、禁用范围、产物清单）
> 在 `project_docs/evidence/PAPER_EVIDENCE_MANIFEST.md`，那份是权威。

| 族 | 目录 | 论文位置 |
|---|---|---|
| A | `20260805_tcad_sprint1_iscas89/` | §4.2 |
| A\* | `20260928_sprint1/` | 可复现性证据 |
| A′ | OpenROAD posterior | §4.5 |
| A″ | — | §4.6 |
| B | `20260826_iscas89_main/` | 摘要三元组 + §4.3 |
| C | `run_hybrid_repair.py` | §4.4 表 6 |
| D | `run_outerloop_real_wns.py` | §4.4 EMA（**复现不出表 6 / 表 9**，运行器是硬边界） |
| F | L1 S 窗口池 | §4.6 表 8 |
| G | 内部诊断 | **不进论文** |
| **扩面族** | `20261025_physical_labels_itc99_ext/` | **0 命中** |
| I / J | `20261029_eco_phys_samelayout/`、`20261029_itc99_eco_fournum/` | 补充 S4.2 / S4.3（四数 A/B/C/D） |
| K / L | `20261030_eco_ext_itc/`、`20261030_eco_ext_iscas/` | 补充 S4.4 / S4.5（四数扩面） |
| M | `20261031_layout_stability/` | 补充 S4.6（布局实现敏感性，OI-074） |
| **N** | `20261102_or_baseline067/`（+ 0.70 族首跑 `20261102_openroad_baseline/`） | 主稿 §5.5 外部参照一句 + 补充 S4.7 |
| **O** | `20261103_ff_unfold/` | 主稿 §5.4 动作集补入段 + 摘要；补充 S5.3 |
| **P** | `20261104_ff_itc/` | 补充 S5.3「其他测试集」段 |
| **R** | `20261104_w1_remap067/` | 补充 §6 复核入口一句（RTL 重映射复现表 3） |

铁律：`same claim ⇒ same revision + same config family`，**禁跨族拼表**。revision 冻结 tag `faeco-exp-rev1` → `87d01ba`。

---

## 5 已裁定不可翻（11 条）

1. **OI-014(B)**：S 降为可选候选类型；主贡献 = 候选构造 + 加权排序 + 失效刻画 + STA 验证。
2. **OI-015**：F6 降为物理诊断/过滤，只可主张「识别并拒绝 ideal-有利/物理失效候选」，**禁**主张「显著改善物理 WNS」，**禁** `maximize F6 count`。
3. **L2 封板**：三臂 + k=1 ⇒ EMA 失效反馈无独立贡献（8/8 逐位相同），降级可选。
4. **L1/S 为 NEGATIVE（能力型）**：扩池 37→126 窗口、`ΔL>0` 43%→60.3%，但 `ΔWNS>0` = 0/126、接受 0/8。
5. **物理档结论**：谱系 理想 → 布局后 → 布线后，**衰减集中在布局阶段**；监督可用布局后档，**最终验收必须布线后档**。
6. **「理想线网说谎」的准确形状**：避害更强、增益有限（接受集真实增益 25.00%、惰性 68.18%、损害比 0.1944、增益富集 7.5593 倍）。**禁写**「接受 N 个候选因此改善 WNS」。
7. **图结构（拓扑）在候选级无物理信号**：池内 AUC 低于 `kind_only`；GNN 四档无一超过平凡基线，去掉单元类型嵌入即归零 ⇒ 信号 ≈ kind。
8. **判据缺陷 OI-052 第 39 条**：GNN 的 `<0.53` 门对带信息的架构**不可满足**（真实标签探针 0.565744 > 平凡基线 0.517298）——那个 NEGATIVE 可能是假阴性。
9. **「多跑一个实现取平均」不得作为实践建议**（C3：全族平局是两个方向相反、各自显著的效应相消）。
10. **触发器动作必须就地展开，不放宽等价器**（r113）：改 `module dff` 壳会改动非目标模块而被 fail-closed 拒；正解是在目标模块内把实例换成同族库单元、helper 字节不变。**禁**以「放开检查器」换取接入。
11. **族间矛盾已归因**：扩面族 `structural − kind_only` 为正、基族为负，主因 = **`kind_only` 基线在两族方向相反**，**不是**「图特征变强」。⇒ 不得声称「直接训 GBDT/GNN 打分器」。

---
11. **2026-11-14 — 批接受 arm All（预注册，H1 PASS / H2 FAIL / 不晋级）**：
    把判据降到最低（每轮接受全部 `paired_improved` 候选）后，4 例均值增益差 **-0.2574 ns**（arm All 0.0521 / arm E 0.3095），s382/s832 微弱改善 +0.008/+0.009 < 布局离散 1/10，s641/s953 因 stagnation 回退到基准。
    **六轮实验全部封口**（P/E → K → A6j → All），当前 R/G/B + joint_k=2 + 覆盖优先的动作空间布线上限 ≈ 0.31 ns/4 例均值。
    **不可写**：「批接受可以替换贪心单步选择」「当前动作种类还有额外物理收益」。
    代码落点：`real_wns.py`（`accept_all`/`_build_cumulative_netlist`/`_apply_static`）、`run_outerloop_real_wns.py`（`--accept-all`）、`test_accept_all.py`（4 用例）。
    实验：`experiments/20261114_accept_all/`，REPORT sha256@16=cd631f84a8a490c9。
    重开需先：测 stagnation 回退前 63 个候选的独立布线后收益。



## 6 六处口径问题（F-1 ~ F-6）

| 编号 | 级别 | 内容 | 状态 |
|---|---|---|---|
| F-1 | 高 | ITC-99 表只报理想档；布线后 b04 由 +0.18 → −0.01 | **已修**（r96 加 S4.3 四数；r100 扩到 b01–b10，b04 记未确认） |
| F-2 | 高 | §5.6 单实现点；s420/s953 翻号 | **已修**（r96 把结论圈定为「该单点实现上」；r101 进一步证明该 0.01–0.02 ns 属实现轴） |
| F-3 | 中 | 结构代理对象混读（池内 AUC 0.85–0.93 是「布局后 Δ 预测布线后 Δ」，与拓扑无关） | **未修** |
| F-4 | 中 | 接受判据真实构成未报（增益/损害/惰性三分） | **未修** |
| F-5 | 低 | T2 的 RC 是估的，只写到命令级 | **未修** |
| F-6 | 中 | 把「0」当效应消失（实为低于 0.01 ns 报告粒度） | **未修** |

原始判定：`scratch/r88_paper_audit/PAPER_DECISION.md`（LOG-20261027-83）。
**结论：论文要改的是口径，不是数字。**
**r96–r101 已销掉 F-1、F-2**；F-3 ~ F-6 未逐条销号，按 open 处理，动它们之前先在 `LOGS.md` 记一条判定。

---

## 7 r94 决定性读数（2026-10-28 新增，改全局判断）

脚本：`scratch/r94_acceptance/acceptance_swap.py` / 产物 `acceptance_swap.json`。**零新 STA、零新 EDA。**

### 7.1 判据门槛 vs 兑现率（双族同向、单调）

| 接受判据 | 扩面族 接受 / 兑现 | 基族 接受 / 兑现 |
|---|---|---|
| `ideal > 0`（**论文现行**） | 37 / **21.62%** | 29 / **27.59%** |
| `ideal > band` | 9 / **55.56%** | 7 / **85.71%** |
| `ideal > 2·band` | — | 4 / **100%** |

口径：用**边际**字段 `post_marginal_delta_wns`（非累积 `post_delta_wns`）。与 r93 的 8/37、19/37 **逐位一致**（已硬断言）。代价是「产量换质量」，37 → 9 → 4，**不得**声称「改判据即可提升 WNS」。

### 7.2 被接受候选的效应量分布（根因）

| | 扩面族 | 基族 |
|---|---|---|
| 改善**恰好 = 0.010 ns**（1 量子） | **16 / 37（43%）** | **10 / 29（34%）** |
| ≤ 0.020 ns（2 量子） | 22 / 37（**59.5%**） | 17 / 29（**58.6%**） |
| 最好候选 | 0.200 ns | 0.210 ns |
| `> 5·band` | **0** | **0** |

判定带 ≈ **5 个量子**，而被接受的改善中位数 = **2 个量子**。

### 7.3 全池候选类型构成（1393，`batch=round35_ext_full`）

| 类型 | 数量 | 占比 | 理想档有改善 | 最优 |
|---|---:|---:|---:|---:|
| **B** 缓冲器插入 | 700 | 50% | **2（0.3%）** | 0.01 ns |
| **R** 等价替换 | 464 | 33% | 6（1.3%） | 0.06 ns |
| **G** 门尺寸 | 198 | 14% | **29（15%）** | 0.20 ns |
| **JOINT** | 19 | 1.4% | **0（0%）** | — |
| BASE / FINAL | 6 / 6 | 哨兵 | 未测 | — |

**统一解释（属推论，非直接测量）**：理想线网档无互连负载 ⇒ 插 buffer 只增一级门延迟 ⇒ **B 类被该判据系统性废掉**；真正有效的是 G，而 G 只占 14%。这同时解释 W1 8/8（覆盖区域更易命中 G）、加权无差异（割权重不影响命中 G）、STA 少 7.8–19%（不生成无效 B/R）。

### 7.4 由此确立的第一性原因

> **动作粒度 < 测量分辨率。** 判定带 ≈ 5 个量子，候选能产生的中位改善 = 2 个量子。
> 排序、预算、判据阈值都不改变这个比值；**只有改动作空间或改判据档位的物理模型才行。**
>
> **r113 兑现了前半句**：把触发器动作补进动作集后，合计 1.29 → 1.68 ns、超带 5/8 → 7/8（§3）。

---

## 8 现行待决（2026-11-04 交接时点）

| # | 待决 | 现状 / 建议 |
|---|---|---|
| **P1** | 论文档位：直接投 JCAD，还是先把英文稿拉回同口径 | 中文两篇已定版（11 / 15 页，质量门 PASS）；**英文稿自 r96 起未同口径**，不统一不宜投英文刊 |
| **P2** | ITC-99 表是否改双档陈述 | 补充 S4.3/S4.4 已给四数 A/B/C/D，主稿不引；**保持现状**即可，零新数据 |
| **P3** | ~~git 提交~~ | **已做**：`7677b21` 之后全部改动已按路径拆条提交，工作区干净。**未 push**，origin 已配置（github.com/Toylog123/FAECO.git） |
| **P4** | v19 基线清单 | `versions/v19/MANIFEST.sha256` 自 r95 后未重建（当前 142 OK / 6 FAILED 属预期差异）；定稿后建 v20 |
| **P5** | 落空率入文 + OI-069/070/072/073 | 均未入文，逐条在 `OPEN_ISSUES.md` |
| **P7** | 预算结论（64 次候选 STA 保留 97.7%）是否入文 | 未定；不加也不动摇主结论 |
| **P8** | 六例超带是否加「util 30/35 这次布局」限定 | **已在 r116 落地**（2026-11-09）：主稿 §5.5 加「利用率 35 这一次布局」限定 + 三档一致超带 4/8 的说明；剩余仅英文稿同口径问题（P1） |
| **P9** | 是否转路径 A（边界论文） | 已按路径 B 定稿——补入触发器把上限从 1.29 抬到 1.68 ns，A 的前提不再成立 |
| **P10** | OI-076：`_joint_enumerate_combos` 是否默认只 G | 未改，默认保持现状；改它要重跑 JOINT 相关族 |
| **P11** | 两处未评估项 | s820@util35 两次详细布线未收敛、ITC-99 b05 未跑完 —— **已如实记为「未评估」，不要再补数字** |
| **P12** | 英文稿同口径 | 摘要与 §4.5 仍是 r94 前叙事（1.07/0.16），对齐到 1.29/1.68 口径约需一轮 |

### 已否决，不得重启

| 项 | 否决依据 |
|---|---|
| 候选级结构/电学打分器 | GNN 池内 AUC **0.479242** < `kind_only` **0.555062**；6/6 代理无判别力（r93 线 C 按计划终止） |
| 自适应时限 `base + k·n_c` | R² **0.0977**；反事实重放 STA **3129→3902**、多花 **87002.9 s**——是花时间买质量，不是省测量 |
| 按线载敏感度分档准入门 | 6/6 代理无候选级判别力；且该病在**实现轴**，不在负载轴 |
| beam 回退（top-B 并行） | 累计 WNS 差可能仅 1–2 个量子，**不可分辨**；且与省 STA 目标冲突 |
| 把判定带塞进接受规则（「加带」） | 累积 8/8 → **4/8**（r102 反事实重放） |
| pin swap | 0/4 超带、中位 0.0388 ns、42% 反噬（r104） |
| JOINT 加深到 depth 3 | **7/8 终点逐位相同**（r106） |
| 用每实例候选上限做预算分配 | 受控实验零点不变（r107/108）——瓶颈不是分配方式 |
| 扩覆盖 8→10000 | 同预算增量 **0.0000 ns**（r110a） |
| 把映射族统一到 0.70 | 0.70 网表在受控运行器上 **0 候选 / 0 STA**，割构造不通（OI-078） |

---

## 9 历史文档索引

见 **`project_docs/ARCHIVE_INDEX.md`**。本文件之外的一切「主线 / 路线图 / 最新进展 / 里程碑」类文档**均已失效**；`mainline.md`、`roadmap.md`、`milestones.md`、`long_term_task_plan.md`、`risk_register.md`、`RECORDS.md`、`decision_log.md`、`future_task_backlog.md`、`ARCHIVE_POLICY.md`、`FILE_ORGANIZATION.md` 十份已在头部加失效横幅；`project_docs/agent_handoff/` 下的 README / CURRENT_RUN_HANDOFF / START_HERE 亦已在 2026-11-04 加横幅（停在 r30）。

**仍然活跃、可直接读的四份**：
- **`project_docs/HANDOFF_2026-11-09.md`** —— 交接入口（三十秒现状 + 复现入口 + 自检命令 + 后续规划），**新接手先读它**（2026-11-04 版保留为历史）
- `project_docs/CANON.md`（本文件）—— 口径
- `project_docs/LOGS.md` —— 逐轮事实流水（只追加）
- `project_docs/OPEN_ISSUES.md` —— 未决问题容器

---

## 10 环境与红线

- **WSL 可用**（2026-11-04 实测）：`wsl.exe -d Ubuntu`，默认发行版已是 `Ubuntu`（旧的 `Ubuntu-24.04` 已注销）。内含 `openroad` v2.0、`sta` 3.1.0、`sby`/`z3`、`yosys-smtbmc`。
- **三个 Yosys 是分工，不是冗余**：`/usr/bin/yosys` **0.33** = SEC 证明链 pin（不要卸、不要拿去映射）；`/usr/local/bin/yosys` → `oss-latest` **0.70+255** = ITC-99 映射（转发 shim，软链会 ENOENT）；Windows `bin/yosys.exe` **0.67+146** = ISCAS89 主族映射。判族只看 `mapped.v` 头 `Generated by Yosys ...`。详见 `docs/environment.md`。
- **映射族不统一（OI-078，won't-fix）**：0.67 = 论文主族，0.70 = ITC-99 与物理后验；**跨族只比方向与量级，不比差值**。
- Python 用 **`.venv/Scripts/python.exe`**（numpy 2.4.6）；**WSL 的 `python3` 没有 numpy**，换解释器 = 换口径。
- **行尾纪律**：`.tex` 与 `OPEN_ISSUES.md` 为**纯 LF**；`LOGS.md` 为 **CRLF**；`*.sh` 由 `.gitattributes` 强制 LF（否则 WSL 下 shebang 带 \r 会直接失败）；`versions/*/MANIFEST.sha256` 必须 LF-only。改完用字节计数复核，`write_text` 会静默翻成 CRLF。
- **编译引擎 = lualatex**：xelatex 能出同页数 PDF，但字节数差 ~0.7 MB，两者不可混当同一版。
- **禁 `git add -A`**（行尾假象会混进提交），按路径逐条 add。HEAD 一律以 `git log -1` 为准，本文件不记哈希（记了就必过期）。
- **本目录下 `os.remove` 会重定向进 Windows 回收站** ⇒ 删完须清 `D:\$Recycle.Bin`，否则磁盘不释放；被其它进程占用的目录连 `mv` 都会 Permission denied。
- **长任务**：`sta` 必须带 `-no_splash -exit`，否则挂住等 stdin；物理流程 `detailed_route` 必须给 `-droute_end_iter`。
- 冻结纪律：论文一旦冻结，任何内容改动（含摘要）须先取得用户明确同意（r96 起历轮均已授权）。
