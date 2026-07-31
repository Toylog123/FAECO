# 旧稿公式与图表审计

更新时间：2026-07-19

审计对象：

- `论文/基于重综合的掩膜前时序ECO框架研究_赵晖学长工作.docx`
- `论文/基于重综合的掩膜前时序ECO框架研究_赵晖学长工作.pdf`

当前结论：

> 16 页 PDF 中的公式主体基本可见，Word 文本抽取未保留公式对象属于抽取限制。DOCX 字段更新证明没有漏掉式(15)，而是原式(16)-(20)缓存编号未刷新，应整体改为式(15)-(19)。其余硬伤包括图号误引、表2四套统计不一致，以及符号假设和可复现性不足。

页级出处、文件哈希和核验边界见 `legacy_source_locator.md`。

## 1. 公式审计表

| ID | PDF 页/编号 | 位置 | 当前问题 | 投稿风险 | FAECO 处理 |
|---|---|---|---|---|---|
| FML-01 | 第3页，式(1) | 布尔电路形式化表征 | 公式可见，但符号域、节点和边的定义仍需统一 | 问题定义可能产生歧义 | 重新定义 netlist graph、node、edge、fanin cone |
| FML-02 | 第3页 | 电路切割条件 | 分割性、隔离性、非对称性主要由文字描述，缺少可执行判定口径 | cut boundary 合法性不清楚 | 改写为工程可验证的 boundary rule |
| FML-03 | 第4页，式(2) | 等价切割定义 | 同态/覆盖约束可见，但与实际 verifier 的接口未闭合 | equivalence claim 不严谨 | 用 boundary I/O truth table 或 SAT miter 定义等价 |
| FML-04 | 第4页，式(3) | 时序 ECO 多目标优化 | 目标项可见，但权重来源、约束和求解顺序不足 | optimization objective 不可复现 | 改为 patch size、timing gain、verification cost 的多目标排序 |
| FML-05 | 第6页，式(4) | 逻辑级数传播公式 | 公式可见，旧稿口径仍需与当前 parser/metrics 对齐 | 新旧实验口径可能不一致 | 在 `metrics_and_tables.md` 中使用工程实现定义 |
| FML-06 | 第6页，式(5)-(8) | slack 反向传播、初始化、改善量和截断 | 公式可见，但该 slack 是逻辑级 proxy，不是真实 STA slack | 容易误写为物理时序结果 | Stage A 用 logic-level slack，Stage B 用 OpenSTA slack |
| FML-07 | 第7页，式(9)-(12) | cut weight 成本函数 | 成本项可见，但参数依据和关键/非关键路径来源不足 | min-cut 权重难以公平复现 | 在 `faeco_algorithm.md` 中改写为特征化权重函数 |
| FML-08 | 第6-7页，式(8)-(13) | 权重截断、常数参数和等价完整性 | 参数取值和截断理由不充分，式(13)与实际 formal 流程未闭合 | 容易被认为是经验调参或过强等价声明 | 加参数敏感性实验，并用 formal verifier 结果支撑等价性 |
| FML-09 | 第8页，式(14) | 时间复杂度分析 | 公式可见，但近似线性依赖 `f_F,f_G << F_max` 等强假设 | 审稿风险高 | 降低表述强度，以扩展性 runtime 实验为主 |
| FML-10 | 第9-11页，PDF 标为式(16)-(20) | 递归学习匹配度和权重更新 | Word 更新 `SEQ MTEqn` 后自动变为式(15)-(19)，证明是缓存编号未刷新；`Kmax=50` 仍缺少敏感性证据 | 编号错误且 failure recovery 结论过强 | 修正为式(15)-(19)，并重构为 F1-F5 taxonomy、显式反馈动作和多轮日志 |

## 2. 图表审计表

| ID | PDF 页 | 图表 | 当前作用 | 问题 | FAECO 处理 |
|---|---:|---|---|---|---|
| FIG-01 | 2 | 图1 RSECO 与传统时序 ECO 对比 | 解释问题背景 | 旧方法名和旧流程不适合新论文直接使用 | 重画为 FAECO problem setting |
| FIG-02 | 3 | 图2 B&G ECO 示意 | 解释传统方法 | 旧图未区分 fixed-tree buffering、post-route sizing、post-placement 联合 B&G 和 global-placement virtual buffering | 按 physical stage 重画 baseline taxonomy；AiTO/MLBuf 仅作相关工作，不画成当前已运行模块 |
| FIG-03 | 5 | 图3 RSECO 框架示意 | 旧稿主流程 | 缺少 failure feedback loop | 重画为 FAECO overall flow |
| FIG-04 | 5 | 图4 SAT-Sweeping 框架 | 等价点搜索 | 不是本文主要创新，细节可压缩 | 放入方法子模块 |
| FIG-05 | 7 | 图5 权重设计示意 | 解释 cut 权重 | 参数依据不足 | 改为 feature-based cut weight 示意 |
| FIG-06 | 9 | 图6 功能损伤示意 | 解释 boundary 不闭合 | 第5.1节正文误写为“如图1所示” | 修正交叉引用，作为 F1/F2 失败类型例子 |
| FIG-07 | 10 | 图7 迭代第二次切割 | 搜索空间优化 | failure 类型过窄 | 改为 failure-aware refinement loop |
| FIG-08 | 10 | 图8 迭代第一次切割 | 搜索空间优化 | 与图7拆分后叙事重复 | 与 FIG-07 合并重画 |
| FIG-09 | 13 | 图9 割集匹配度曲线 | 展示 CutFinder 迭代效果 | 只展示少量工业 case 曲线，缺少统计与公开数据 | 改为多轮 recovery 曲线或 ablation 图 |
| TAB-01 | 12 | 表1 工业电路统计 | 旧工业 case 背景 | 数据不可公开 | 不作为主证据；公开 benchmark 需新表 |
| TAB-02 | 12 | 表2 RSECO vs B&G | 旧核心实验结果 | 商业 baseline 不透明；正文/摘要、Avg 行、逐行百分比均值和显示 slack 反算值均不统一；现代 sizing/B&G 文献的 physical stage、工具和 runtime 口径也互不相同；DAC 2023 timing predictor 的 4154x 还是 inference 对 opt+route+STA 总流，不能作为同阶段 baseline | 旧均值全部降级；按 `legacy_table2_recalculation.md` 保留审计记录，新论文只比较同 stage、同 STA 和同 runtime budget 的可复现 baseline |
| TAB-03 | 12 | 表3 修改规模对比 | patch size 证据 | 指标可继承但数据不可复现 | 新实验保留 patch size/change ratio |
| TAB-04 | 13 | 表4 RSECO+B&G | 组合方法结果 | 依赖商业工具 | 暂不作为第一篇核心结果 |
| TAB-05 | 13 | 表5 CutFinder 优化结果 | 报告 w/o 3/8、w/ 8/8 成功及迭代次数 | 非公开工业 case、无重复试验/消融/formal 日志，不能证明“解决失效” | 仅作历史动机；用公开 benchmark 多轮 recovery 与 ablation 替代 |

## 3. 必须重画的新图

| ID | 新图 | 用途 |
|---|---|---|
| NEW-FIG-01 | FAECO 总体框架 | 展示 resynthesis、candidate patch、verification、failure classification、refinement、ranking |
| NEW-FIG-02 | Failure-aware cut refinement loop | 展示 F1-F5 如何反馈到 cut weights |
| NEW-FIG-03 | Benchmark case generation flow | 展示 original/resynthesized/cone/patch/metrics 如何生成 |
| NEW-FIG-04 | Stage A 到 Stage B 的迁移 | 说明 combinational cone 到 sequential reg-to-reg cone |

## 4. 必须重做的新表

| ID | 新表 | 用途 | 当前覆盖状态 |
|---|---|---|---|
| NEW-TAB-01 | Benchmark summary | benchmark、gate count、logic level、case 数 | 部分覆盖：5-case batch 已有 case summary；EPFL 8 候选已有隔离 AIG stats/CEC，但尚未导入正式 cases，不能并入论文主表 |
| NEW-TAB-02 | Main comparison | fixed/random/size/critical-path/FAECO 指标对比 | 部分覆盖：`tables/baseline_comparison.json/md` 已覆盖 fixed/random/size-only/critical-path-only/ABC wrapper/FAECO；ABC baseline 当前为 `unavailable`，不是最终主结果表 |
| NEW-TAB-03 | Failure recovery | 初始失败数、恢复成功数、recovery success rate | 部分覆盖：`tables/failure_recovery.json/md` 已生成 Stage A proxy 表，并记录 single-refinement proxy `avg_iterations=1.0`；当前还缺真正多轮 recovery iteration 统计 |
| NEW-TAB-04 | Ablation | without F1/F3/F4 feedback 等消融 | 未完成：尚未生成禁用反馈项的配置和结果表 |
| NEW-TAB-05 | Runtime breakdown | extraction、cut、verification、ranking、total | 部分覆盖：`tables/runtime_breakdown.json/md` 已汇总 Python flow stage；ABC 相关阶段当前为 wrapper unavailable，不是真实外部 EDA runtime |
| NEW-TAB-06 | Toolchain/environment traceability | 工具版本、可用性和实验环境 | 已有原型：`environment/toolchain_snapshot.json` 当前记录 Python/NetworkX/Yosys 版本；ABC/OpenSTA/Z3 在正式 batch 中仍为 unavailable |

## 5. 当前工程证据边界

| 证据项 | 可写入论文的位置 | 当前边界 |
|---|---|---|
| 5-case batch demo | 实验设置或原型验证 | 只能说明 Stage A flow 已成形，不能作为最终统计结论 |
| structural equivalence pass | 工程 smoke check | 不能替代 ABC/SAT/Z3 formal equivalence |
| ABC wrapper status | 实验可追溯性和工具链说明 | 当前全部 `unavailable`，不能写成 ABC baseline 成功 |
| runtime breakdown 表 | 实验设置、工程效率指标 | 当前外部工具阶段只是 wrapper 探测耗时，不是真实 EDA runtime |
| failure recovery 表 | failure-aware refinement 证据 | 当前是 Stage A proxy，`avg_iterations=1.0` 只来自 single-refinement proxy，不能写成多轮恢复率或最终论文统计结论 |
| cone-level replacement | 方法实现说明 | 不能写成可综合 patched netlist 或布局布线后结果 |
| benchmark source manifest | 实验设置和可复现性 | 已固定 EPFL `v2025.1`、MIT license、8 个 Verilog/官方 BLIF blob，隔离规范化 CEC 为 8/8 pass；尚未导入或产生 EPFL FAECO 实验结果，当前 ISCAS85 batch 仍只作本地 smoke |

## 6. 当前处理结论

旧稿的公式和图表可以作为“要表达的思想”的来源，但不能直接作为 FAECO 新论文的最终方法定义。PDF/OOXML/Word 字段核验已经排除“漏掉式(15)”的误判，并确定原式(16)-(20)应重编号为式(15)-(19)；图号误引、表2统计冲突和理论/实验可复现性不足仍需修复。新论文应先以代码和实验产物确认已实现行为，再用 `method_rewrite_readiness.md` 区分可写、代理和阻塞项；`faeco_algorithm.md`、`failure_taxonomy.md`、`baseline_protocol.md` 和 `metrics_and_tables.md` 主要定义目标设计与指标边界，不能单独证明实现完成。
