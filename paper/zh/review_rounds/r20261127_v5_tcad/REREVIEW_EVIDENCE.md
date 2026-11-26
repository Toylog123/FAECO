# V5 TCAD 复审证据裁决

**科学裁决为小修。** 绝对 Setup 门槛分叉、同起序批宽对照、限时处理器反例和核心指标已经复核。仍须修正窗口回放的非零提议数并收齐当前稿件的资源边界、复跑路径和图表可读性。**正式投稿资格待验。** 本轮收到的是中文复审稿，尚无同一拟投英文提交包可核。

本裁决执行[冻结的 V1–V7 判据](REREVIEW_CRITERIA.md)，其 SHA-256 为 `0e59c6c48de2e29d4246a6c29a012dfbf9ef66418604d2b89f35d35e8efc6959`。核验对象是 `scratch/v5_rereview_build/FAECO_v3_后布局可调预算面积回收` 中的冻结快照。TeX SHA-256 为 `13820299a4aa73c26e4967abb6bf83bfd22c29317d4cf881d2db5af6b4a5f85c`，14 页 PDF SHA-256 为 `fc2c06ad070fe4fc61b9f7282055d7b25e132bc6c1f99d508bfe6ebd09d4d9bb`。证据提交为 `4bfa762585bf83b507bd2d289245e05db67480f9`。本次未读作者答复，未运行新 EDA。以下 TeX 行号和页码均对应这一快照。 [冻结稿指向的公开证据索引](https://github.com/Toylog123/FAECO/blob/4bfa762585bf83b507bd2d289245e05db67480f9/project_docs/evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md)

| 组 | 判定 | 遗留影响 |
|---|---|---|
| V1 | 部分解决 | 次要。历史回放非零分母需更正，匹配总数和机制判断成立 |
| V2 | 完全解决 | 未见留在当前范围内的关键门槛缺口 |
| V3 | 完全解决 | 限于已核对照，批宽复验的共同面积端点身份不同 |
| V4 | 部分解决 | 次要。未采集完整进程树与首次读档，当前论述限于验收时间 |
| V5 | 完全解决 | 外部算法排序和近临界或多模式普适性仍在稿件结论范围之外 |
| V6 | 部分解决 | 次要。公开离线复算与阶段入口通过，完整物理重建仍需外部输入路径适配 |
| V7 | 部分解决 | 当前稿需处理末页与小字，正式英文投稿包待验 |

## V1｜窗口覆盖、同引擎报标与生产放行

§4.2（TeX 270–333）将标注图形的几何见证、请求盒筛选和规则上下文、原网放行分开。技术 LEF 表给出基本 0.018 µm、条件距离与高层规则，并撤去全类 15 倍判断。冻结源码索引具体到工作单元选取、`drcBox` 与 `extBox`、marker bbox 相交，以及类型／含层 bbox／源对象的归并键。补充正文明确 7 nm 合成注入与自然零标记的区别。公开脚本从六组原始报告复算窗内 TP/FP/FN 为 37/0/0、窗外为 0/0/2。生产解释仍以冻结版图已有的可归因信号网和全块终检为界。 [窗口规则及源码锚点](../../../../project_docs/evidence/tcad_v5_revision_20261126/WINDOW_RULE_SCOPE.md) · [公开复算入口](../../../../project_docs/evidence/tcad_v5_revision_20261126/verify_review_evidence.py)

**必须更正。** §5.4（TeX 624）称 SKY130HD AES 有“9组非零冲突提议”。直接读取历史收据的九组 `full_unique_markers` 得到 0、6、5、8、11、4、10、4、8，所以应为 **9 组历史提议，8 组非零、1 组零，共 56 个标记**。逐组表、图和结论应使用同一分母。56 个标记的总数及对应的同引擎匹配结论保持成立。 [历史回放逐组收据](../../../../project_docs/evidence/tcad_boxed_drc_20261126/BOXED_DRC_RECALL_AUDIT.json)

## V2｜时序、电气与执行规则

§3.1、§4.3–4.4、§5.5、§5.7、§6 明示相对预算和绝对零下限、每角 Hold WNS、Stage 5 的 Hold TNS、电气比较键和原违例幅度限制、异步检查与解析失败、单模式及三 PVT 共名义 SPEF。500 ps UART 是同一版图放宽时钟，40 ns 处理器为独立重建，两个在线参考的相对 Setup 下限已为正。对 470.5 ps 补证核对六份 STA、两条时钟改动与固定 I/O。SS 从参考的 **+0.794642 ps** 变为同一候选的 **−0.568545 ps**。相对门通过，绝对门唯一拒因为 `SS:setup_floor`。另外在补证 ZIP 直接核对旧候选物理、全块 DRC 和 SEC 文件的摘要与协议一致，原 13 门的 Verilog 与 SPEF 指纹吻合，DRC 标记为零且 SEC 567/0。该补证只重判已有物理候选的时序，稿内结论与其一致。 [近临界复验](../../../../project_docs/evidence/tcad_v5_revision_20261126/V5_REVIEW_SETUP_FLOOR_VERIFIED.json) · [补证原件](../../../../project_docs/evidence/tcad_v5_revision_20261126/V5_REVIEW_SUPPLEMENT_ORIGINALS.zip)

同一 SDC 下 T3 是 S18 的严格子集，原件给出 SS Hold 分别变动 −0.157652 和 +0.459188 ps，S18 通过独立 DRC 和 11,089/0 SEC。公式解释把墙钟单列。§4.4 说明首轮全量归因与复修归因子集、整网放行，以及不同历史缓存的语义。UART 去重实测只证实 FF Setup WNS 命中，TNS 标签拼写差异已在正文披露。绝对收敛的初轮失败来源与最终电气合格参考在 §§5.7–6 分开。 [Stage 1 原收据](../../../../project_docs/evidence/tcad_v5_revision_20261126/V5_STEP1_POWER_7NM_DET_VERIFIED.json) · [执行协议索引](../../../../project_docs/evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md) · [40 ns 资格](../../../../project_docs/evidence/tcad_v5_revision_20261126/V5_STEP5_TC40NS_MMMC_DRV_QUALIFICATION.json)

## V3｜保护后端各干预的因果对照

§§5.3–5.4 分开报告三项效应。同三门请求中，几何接触 105.60 s 返回但 Hold 拒收，现场归因为 122.75 s 并通过，SS Hold 相对参考分别为 −10.482 与 +0.885 ps。提前诊断的 2×2 对照给出同一端点首达与此前少做的详细布线。全块对窗口另报预检开销与共同目标首达，未用前项替代后项。历史 A/B 起序和排序成本差异已在正文及图注标注。

同起序补证在共池、共后端、共计费且关闭反馈、探针和缓存后运行 b=1/b=3。两臂 18 个动作顺序一致、完整评估各 5 次，终态 33.7824／67.5648 µm²，时间平均 12.623294／34.809579 µm²。到达共同面积 33.7824 µm² 的时刻为 567.47／235.89 s，对应动作和物理端点不同。该实验支持该参考下改变批宽改变联合可行性和窗内交付，稿内保留适用边界。 [归因配对](../../../../project_docs/evidence/tcad_geo_neighbor_20261125/AES_GEO_VS_ONLINE_VERIFIED.json) · [前移交叉对照](../../../../project_docs/evidence/tcad_ibex_20261123/AES_FACTORIAL_REPORT.md) · [同起序批宽补证](../../../../project_docs/evidence/tcad_v5_revision_20261126/V5_REVIEW_MATCHED_BATCH_VERIFIED.json)

## V4｜计时、负结果和资源边界

§5.7 与表 12 保留单门／固定三门／FAECO 的终态 48.7968／91.3376／31.2800 µm²、各自首达、共面积首达、功能面积比例、失败二分及 TT 默认活动功耗。原件复核相同面积物理指纹和共目标时间，固定三门终态及时间均值仍最高。§§4.4、5.6 清楚拆分历史探针和 V5 协议；六条正预算臂先行、两个 0 s 后补，保留两个 AES 的探针机会成本、截停阶段及同轨但首达波动。 [Stage 4 原收据](../../../../project_docs/evidence/tcad_v5_revision_20261126/V5_STEP4_PROBE_SENS_VERIFIED.json) · [Stage 5 原收据](../../../../project_docs/evidence/tcad_v5_revision_20261126/V5_STEP5_10K_TIMING_CLOSED_TC40NS_MMMC_DRV_VERIFIED.json)

**剩余。** 补证有代表性 DRT 内部 CPU／wall／进程峰值，覆盖小 UART、两种 AES 和处理器，并有自然结束、实际 DRT 截停的验收、子进程回收与外层返回时间。实际固定臂最后验收为 653.078613 s，外层返回 653.079025 s。FAECO 早先合格检查点在 355.093431 s，末派后外层返回为 720.085671 s。完整进程树 CPU、峰值内存和检查点对下游首次可读时刻未测。依冻结的资源阈值仍为部分解决。现有证明范围只涉及窗内验收，保留明确未测项及应计时点，避免形成硬接口返回或跨机器成本承诺。 [资源与退出账本](../../../../project_docs/evidence/tcad_v5_revision_20261126/REVIEW_SUPPLEMENT.md)

## V5｜参考资格与基线边界

表 3 相邻注释列出旧 6 ns `riscv32i` 的 0 条输入延时、99 条输出延时和 ABC 单位问题，限定于共享旧参考的内部比较。§5.7 保留 10 ns、首个 40 ns 以及 JPEG、Ethmac 的资格失败说明。§5.2、表 4–5 和证据册将原生全片重布的完整拒收与超时分开，识别 ASAP7 绑定失败、SKY130HD AES 冻结时钟网超域、119 项数据网投影及 24 项截停。原生行排除出同池分母。冻结 TT 五轮提出 18/18 的行为以全池直提作比较，强外部方法的实际共同域缺口有说明。公开脚本已核 14 项原生准入记录。 [旧约束记录](../../../../project_docs/OPEN_ISSUES.md#oi-1112026-11-26open-riscv32i-旧约束缺失输入延迟) · [Stage 2 准入收据](../../../../project_docs/evidence/tcad_v5_revision_20261126/V5_STEP2_DEDUP_NATIVE_VERIFIED.json)

## V6｜离线复算与阶段复跑

在证据目录与固定提交无差异的状态下运行 `python -B verify_review_evidence.py`，退出 0。297 份原件及 37 份补证逐件通过索引检查。Stage 2–5 的终态、时间均值、可得验收时刻均复算。处理器 12 个检查点另核原 STA、DRC、天线及 SEC，比较 ODB、DEF、网表的存档指纹。两个 ZIP 的哈希分别为 `eec4d4bdc4911ec42aa31cb874c0fb9a1ebfa4a11508a19573858f9137d3237f` 和 `b5b94043223ad269ec735ceea32ab2fa4ea5b96efe08868bce900e8f36d4e712`。主稿已删除旧 107/74 诊断数字。136 是按已完成请求计的历史离线重判，证据索引列出 200−2−62 的分母与 62 个不同累计动作集。 [公开可执行索引](https://github.com/Toylog123/FAECO/blob/4bfa762585bf83b507bd2d289245e05db67480f9/project_docs/evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md)

以 Git Bash 分别检查已有证据状态及不存在的新输出根下的 `--plan`，退出皆为 0。能列出 Stage 4 常规扫描和 `--matched-zero`，以及 Stage 5 两个 `--reference-only` 变体和合格 DRV 三臂。未生成输出根。静态检查表明启动器在实际运行时验证预期资格拒因并检查新发布状态，解决了原入口错选阶段的问题。

**剩余。** `--output-root` 可重定位输出，物理驱动仍依赖冻结主机的输入、PDK 与辅助工具路径。README 明列恢复相同路径或适配后核验字节身份的条件，但尚无与输出同样完整的输入根配置。大体积 ODB、DEF、SPEF 未全包含在公开包。本轮可核已提交证据及命令展开，不能标注清洁检出可独立完成物理复跑，也没有发现公共离线复算的阻断。 [复跑与先决输入](../../../../project_docs/evidence/tcad_v5_revision_20261126/README.md)

## V7｜当前稿件与正式投稿

**当前稿件部分解决。** 已核 TeX/PDF 哈希、编译日志和 PDF 14 页。逐页检查 112 dpi 渲染，未见实质内容溢出或图表叠盖。交叉核对 `.aux` 的 24 个文献键及正文实际交叉引用，未发现未解析项。日志仍有字体替代。第 14 页仅留下参考文献 [24]，应与参考文献页合并。第 8 页主总表的代表数字有效字号约 6.1 pt，第 10 页图 4 的部分注释约 5.3 pt，第 11 页图 5 的部分注释约 5.4 pt，应修改最终渲染中的可读性。当前致谢已区分 Codex 辅助与机制示意生成记录。 [冻结 TeX](../../../../scratch/v5_rereview_build/FAECO_v3_后布局可调预算面积回收.tex) · [冻结 PDF](../../../../scratch/v5_rereview_build/FAECO_v3_后布局可调预算面积回收.pdf)

**正式投稿待验。** TCAD 官方要求 IEEE 双栏和至少 10 pt 条件，Regular Paper 不超过 14 页，并为修回所需作者资料保留篇幅。每位作者需有 ORCID。致谢中的生成式 AI 声明须明确工具及影响内容，待作者在拟投英文包中确认具体工具与用途。当前中文 14 页稿仅是本轮复审对象。 [IEEE TCAD 投稿说明](https://ieee-ceda.org/publications/tcad/tcad-paper-submissions)
