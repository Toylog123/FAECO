# RSECO 旧稿 Claim-Evidence Matrix

更新时间：2026-07-20

审计对象：

- `论文/基于重综合的掩膜前时序ECO框架研究_赵晖学长工作.docx`
- `论文/基于重综合的掩膜前时序ECO框架研究_赵晖学长工作.pdf`

本文档目标不是证明旧稿可以直接投稿，而是判断哪些主张可以继承到 FAECO，哪些必须用新实验重新补证据。

旧稿页级出处、公式/图表编号和文件核验信息见 `legacy_source_locator.md`。

## 1. 核心 claim 审计表

| ID | 旧稿 claim | 来源位置 | 现有证据 | 证据强度 | FAECO 处理方式 | 缺口/补证据动作 |
|---|---|---|---|---|---|---|
| C01 | 传统 buffering 与 gate sizing 难以修复严重逻辑级数违例 | PDF 第1-2页，引言与图1附近 | 旧稿有问题背景；2012 TCAD 最优 buffer insertion 说明固定 routing tree/library/delay model 下的 B&G 可以是强局部优化；RL-Sizer 和 2025 physically-aware sizing 进一步说明现代 sizing 依赖真实 STA、technology/layout features、离散 cell choices 和停止条件；AiTO 的联合 sizing/buffering 消融表明联合动作可优于串行优化，MLBuf 则说明 buffer porosity 会影响下游 PPA。上述工作均未改变 B&G 不修改逻辑功能/级数的基本问题边界 | 中 | 保留为研究动机，但改写为适用范围差异，不写成 B&G 对所有严重违例必然失败 | 用 FAECO 公开实验给出可复现 failure cases；Stage B 必须固定 B&G 工具、library/STA、physical stage、runtime budget 和停止条件后再比较 |
| C02 | RSECO 使用重综合后的新网表辅助原 APR 网表做局部 timing ECO | PDF 第1、4-5页，摘要、第4节、图3 | 旧稿流程描述完整 | 强 | 作为 FAECO 的继承主线 | 新论文中改写为“重综合辅助局部 patch replacement” |
| C03 | SAT-Sweeping 可用于新旧网表等价点搜索 | PDF 第1、5页，摘要、第4.1节、图4 | 旧稿说明采用 SAT-Sweeping；DAC 2006 的归档 Cadence Labs 全文支持 AIG + simulation + SAT + local ODC，证据等级 A；2024 STP SAT-sweeping 全文进一步显示更强 simulation 可减少错误等价候选和 SAT calls，但论文最终仍用 ABC `&cec` 验证结果。当前 FAECO 已接入 Yosys-normalized full-netlist ABC CEC，5-case local smoke 为 5/5 pass，但尚未实现 candidate/boundary-level formal 或 SAT-sweeping 等价点搜索 | 中 | 降级为“候选边界需要形式化等价验证”，不绑定尚未复现的 SAT-Sweeping 实现 | 将 full-netlist CEC 迁移到 EPFL MIT 主数据；若后续需要 candidate/boundary formal，再接 Z3 或 miter/counterexample 日志；文献库错配 PDF 继续禁引，正确核验缓存不进入再分发包 |
| C04 | 关键路径感知的双阶段 min-cut 可产生等价 patch boundary | PDF 第2、4-8页，贡献2、第4.2节、图5、算法1 | 旧稿给出网络流模型；当前 FAECO 已实现 `weighted_st_min_cut_v1`、多候选 ranking、cone-level replacement，并在 5-case batch 中生成 cut、patch 和 summary 表；2012 fixability 工作支持关键性判断应综合路径共享、资源可用性和几何，DAC 2023 restructure-tolerant timing prediction 进一步表明 timing optimization 会替换大量 nets/cells 并改变未替换局部 delay，但二者都不证明 min-cut boundary 等价 | 中 | 作为 FAECO cut search 原型和 baseline 比较入口 | 当前 `critical_path_only_cut` 仍是 Stage A target-output proxy；需接 OpenSTA/真实关键路径、补 boundary closure 和 failure case 统计；若加入学习特征，需按结构变化与 endpoint/path 分组验证 |
| C05 | 递归学习策略可解决 ECO 算法失效问题 | PDF 第2、9-13页，贡献3、第5.2节、算法2、表5、图9、结论 | 旧稿表5报告 w/o CutFinder 3/8 成功、w/ CutFinder 8/8 成功，但仅来自非公开工业 case，缺少重复试验、消融和 formal 日志；2010 robust functional ECO 支撑 fallback 动机，2012 `NEGO-ROUT` 支撑 conflict/history penalty 的多轮资源合法化，2012 multi-patch flow 支撑 rectification 失败后返回 SAT diagnosis，但这些工作都不能验证 FAECO 的 F1-F5；当前 FAECO 只形成 single-refinement Stage A proxy，`avg_iterations=1.0` | 中 | 重构为 FAECO 的 failure-aware cut refinement | 历史与相关工作只能支撑研究动机；仍需实现真正多轮 refinement loop、without F1/F3/F4 ablation 和 max iteration sensitivity，避免写成“已解决所有失效” |
| C06 | 功能损伤可以通过扩展子电路边界解决 | PDF 第9页，第5.1节、图6 | 旧稿描述了悬空输入导致功能改变的问题；正文把图6误引为图1 | 中 | 归入 F1/F2 失败类型 | 修正交叉引用；新实验记录边界不闭合和功能不等价案例 |
| C07 | RSECO 在 8 个工业组合电路案例上有效 | PDF 第11-13页，第6节、表1-5 | 旧稿有工业案例表和结果表 | 中 | 只能作为历史参考或 case study | 主论文证据改用公开 benchmark；工业案例不可作为唯一证据 |
| C08 | RSECO 平均改善 88.16% WNS 和 90.49% TNS，优于商业 B&G | PDF 第1、12页，摘要、表2及正文 | `legacy_table2_recalculation.md` 已确认正文/摘要、Avg 行、逐 case 百分比均值和显示 slack 反算值不一致；原始高精度日志缺失，旧均值不可认证。RL-Sizer、physically-aware sizing、AiTO、MLBuf 和 BUFFALO 分处不同 post-route/post-placement/global-placement 设置。BUFFALO Table IV 最大 TNS/WNS 改善为 71.10%/67.69%，83x 仅是代表性单网，且结论的 77.7% TNS 与摘要/Table IV 不一致。DAC 2023 timing predictor 的 4154x 又是 inference 对 commercial opt+route+STA 总流，不是同阶段 STA 或 timing closure 对比；这些工作均不能认证旧稿百分比或形成横向排名 | 弱 | 不直接作为 FAECO 主结果，也不再把 88.16%/90.49% 视为可靠历史均值 | FAECO 接入 OpenSTA/sequential case 后重新产生 WNS/TNS，并用等 physical stage、runtime/停止条件的 B&G baseline；旧稿只保留逐 case 历史观察 |
| C09 | RSECO 平均仅修改 13.84% 逻辑门，少于 B&G 的 16.15% | PDF 第1、12页，摘要、表3 | 旧稿正文与表3 Avg 行一致；2018 patch-function 工作把 minimum-cost support 与 patch gate count 作为独立目标；2016 resource-aware patch 显示 size 与估计 wiring cost 不能合并；DAC 2018 cost-aware multi-target 论文的 B 级摘要和 ICCAD 2017 官方规范进一步把 weighted support cost、patch gate count、runtime 分列，但不能核验论文算法细节和结果数字；2013 Intuitive ECO 的 IBM 数据也非公开；当前 5-case batch 的 selected boundary size 均为 1 | 中 | 保留“修改规模受控”，并把逻辑规模、wiring/resource cost、runtime 分列；不继承旧百分比 | 扩大公开 benchmark、生成真实 Boolean/Verilog patch，接入 placement/resource features、formal 和 ABC baseline 后再统计均值、方差和 change ratio |
| C10 | RSECO + B&G 可消除所有时序违例，仅额外增加 1.96% 修改量 | PDF 第13页，表4及正文 | 旧稿表4报告全部 TNS=0 和平均 1.96%，但依赖不可复现的商业流程；2013 Intuitive ECO 的工业 flow 说明逻辑 delta 会影响物理综合后的 WNS/TNS 和 gate perturbation，但不能认证 RSECO 的 1.96% 或“全部消除” | 弱 | 暂不作为第一篇核心 claim | 需要商业工具或开源等价 flow 支撑，否则放入 discussion |
| C11 | 算法整体近似线性时间复杂度 | PDF 第8页，第4.3节、式(14) | 式(14)可见，但结论依赖 `f_F,f_G << F_max` 等强假设；当前 runtime 表只有 5 个小型 combinational cases | 弱 | 暂不写近似线性复杂度 claim，改写为“记录分阶段 runtime 并评估扩展性” | 扩大 benchmark 规模后用 runtime table 支撑扩展性趋势，并重写复杂度假设 |
| C12 | 未来可通过全局拓扑信息改进权重设计和割集迭代 | PDF 第14页，结论 | 旧稿作为展望提出；DAC 2023 endpoint multimodal predictor 支持结构变化后使用全局 endpoint/path 表示的动机，DAC 2024 cross-node predictor 支持把 technology shift 与 design shift 分开验证 | 中 | 转化为 FAECO 的新工作入口 | 需要把“全局拓扑”具体化为 boundary complexity、critical path coverage 等特征；学习式扩展仍需公开标签、跨设计/节点切分和 STA 校准 |

## 2. 当前 FAECO 证据增量

| ID | 当前证据 | 支撑的论文表述 | 不能支撑的表述 |
|---|---|---|---|
| EVID-01 | `experiments/20260718_minimal_combinational_batch_demo/` 已覆盖 c17 N22/N23、c432、c499、c880 共 5 个 combinational cases | FAECO 已形成公开 benchmark Stage A 原型 flow，结果能追溯到 per-case metrics 和 batch tables | 不能声称已覆盖论文级 benchmark 规模，也不能替代 sequential timing ECO 实验 |
| EVID-02 | `tables/baseline_comparison.json/md` 覆盖 fixed、random、size-only、critical-path-only、Yosys/ABC rewrite/refactor/resyn 和 FAECO selected | 可写成“已建立多 baseline 对比表结构，并完成 5-case local smoke 结果；ABC baseline 产出 optimized BLIF、stats、日志和回验状态” | 不能写成 FAECO 已正式优于 ABC 或商业工具，因为当前 ABC baseline 是独立 resynthesis baseline，不是 FAECO patch 的性能对照胜负结论 |
| EVID-03 | `formal_equivalence_result` 和 `abc_baseline_status` 在正式 5-case artifact 中分别为 5/5 `pass` 和 5/5 `success`；raw results 归档 normalized BLIF、sanitized Verilog、ABC logs、optimized BLIF、stats 和 runtime | 可写成“Yosys-BLIF-ABC 技术路径已进入正式 runner，并覆盖当前 5 个本地 smoke case” | 不能把 full-netlist CEC 写成 candidate patch/boundary formal，也不能把未许可的 3 个 ISCAS case 当作论文主集 |
| EVID-04 | `environment/toolchain_snapshot.json` 记录 Python 3.11.9、Yosys 0.9、UC Berkeley ABC 1.01、OpenSTA 3.1.0、NetworkX 3.4.2 可用；Z3 不可用 | 可写成“实验环境可追溯，Yosys/ABC/OpenSTA 工具可用性与版本进入实验产物” | 不能把 OpenSTA 本体可用写成 Stage B runner 已产生 WNS/TNS；Z3/SAT-SMT 路径仍未安装 |
| EVID-05 | `tables/runtime_breakdown.json/md` 汇总 5 个 case 的 runtime stage duration/status/category/tool，其中 formal 和 ABC baseline 阶段为真实 Yosys/ABC external runtime | 可写成“已建立分阶段 runtime reporting schema，并记录 Yosys/ABC 外部工具耗时” | 不能写成真实 OpenSTA runtime，因为 Stage B 尚未接入 |
| EVID-06 | `patches/replacement.json` 和 per-case metrics 记录 `internal_cone_replacement_v0` applied | 可写成“selected patch 可应用到 cone-level 内部表示” | 不能写成已生成可综合 patched Verilog 或完成布局布线后验证 |
| EVID-07 | `tables/failure_recovery.json/md` 按 F3/F4 聚合 5-case Stage A proxy recovery，当前 initial fail count=5、proxy recovered count=5、rate=1.000、`avg_iterations=1.0` | 可写成“已建立 failure recovery 统计表结构，并在 5-case 原型中记录 F3/F4 的代理恢复结果和 single-refinement proxy iteration count” | 不能写成多轮迭代恢复率，也不能说明真实 timing closure 已恢复；当前 ABC full-netlist pass 不等于 candidate/boundary patch formal |
| EVID-08 | EPFL `v2025.1` 的 commit、MIT license、8 个 Verilog 和 8 个官方 BLIF blob 已固定；隔离探针中 8 个 Yosys 规范化 BLIF 对官方 BLIF 的 ABC CEC 与 stats 全部一致 | 可写成“公开 benchmark 来源、许可、独立参考格式和规范化功能一致性已形成可追溯证据，论文主集将迁移到该固定版本” | 尚未建立正式 EPFL cases、resynthesis、target、正式 formal/runtime 或主表；权威内部格式也未批准，不能写成论文级公开 benchmark 实验已经完成 |
| EVID-09 | `core_paper_notes.md` 已核验 25 篇 A 级全文和 1 条 B 级官方证据；DAC 2006 SAT Sweeping 已由归档的 Cadence Labs 6 页全文升级为 A，正确 PDF SHA、错配文件 SHA 和再分发边界均进入 source manifest；DAC 2018 cost-aware multi-target 仍为 B | 可写成“核心 related-work 已形成分级证据链，覆盖 remapping、fixability、resource competition、multi-error/multi-target/resource-aware patch、functional correspondence、simultaneous ECO、传统/学习式/物理感知/LLM buffering、结构变化容忍/跨节点 timing prediction、SAT sweeping 和 formal scaling” | 不能写成完整系统综述；两篇 ML timing 工作均未公开处理后数据、模型与 Cadence flow，4154x 不是同阶段 STA 加速，130-nm 到 7-nm 结果仍使用一个 7-nm 训练设计；DAC 2018 仍缺 A 级全文，SAT 核验缓存不可再分发且不证明 FAECO formal 已通过 |

## 3. 可继承内容

| 类型 | 可继承内容 | 继承方式 |
|---|---|---|
| 问题定义 | 掩膜前 timing ECO，严重时序违例，重综合辅助局部替换 | 保留为新论文背景 |
| 基本流程 | 原始网表、重综合网表、等价点、patch boundary、替换验证 | 改写为 FAECO 总体框架 |
| 指标体系 | WNS、TNS、Max-LL、runtime、patch size、change ratio | 保留并补充 equivalence pass rate 和 recovery success rate |
| 算法入口 | 网络流 min-cut、关键路径感知权重、失败后权重调整 | 重构为 fixed min-cut baseline + failure-aware refinement |
| 工程叙事 | 传统局部物理 ECO 不适合严重逻辑级数违例 | 保留，但需补文献和公开实验 |

## 4. 不能直接继承的内容

| 类型 | 问题 | 处理 |
|---|---|---|
| 工业实验结果 | 数据不可公开，原始数据和代码不可恢复 | 只作为背景，不作为新论文主证据 |
| 商业工具对比 | B&G 参数、版本、运行条件不透明 | 改用开源 baseline；若保留商业结果，必须降级为参考 |
| 递归学习 claim | 缺少失败分类、消融实验和统计支撑 | 重写为 FAECO failure-aware cut refinement，并重新实验 |
| 公式定义 | PDF 中公式主体可见；Word 字段更新证明原式(16)-(20)应改为(15)-(19)，符号假设和实现口径仍不完整 | 以 PDF/OOXML 为旧稿定位源，并按 FAECO 工程定义重写 |
| 复杂度 claim | 依赖未完整展示的符号和假设 | 降低表述强度，以 runtime 实验为主 |

## 5. 对 FAECO 的直接结论

FAECO 论文不应写成“恢复 RSECO 旧系统”。更稳妥的写法是：

> 继承 RSECO 的重综合辅助 timing ECO 问题定义，将旧稿中较弱的递归权重调整思想系统化为 failure-aware cut refinement，并通过公开 benchmark flow、明确 baseline、可复现实验和工程指标重新建立证据链。

下一步应优先补：

1. 实现 X21 Yosys JSON importer，把已接入的 Yosys/ABC formal/baseline 迁移到 EPFL MIT 主数据。
2. 接入 OpenSTA Stage B，刷新真实 WNS/TNS、critical path 和 STA runtime。
3. 实现真正多轮 refinement、failure recovery 与 ablation 表。
4. 将 cone-level replacement 扩展为可综合 Verilog patch 写回。
5. 按 `legacy_source_locator.md` 修正公式缓存编号和图6误引；按 `legacy_table2_recalculation.md` 删除不可认证的旧均值 claim。
