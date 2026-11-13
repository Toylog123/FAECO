# FAECO 整体机制只读审计

2026-11-13。以当前 CANON 顶部裁定、ROADMAP 顶部任务及实际调用为依据；未改生产代码、论文或 sealed 证据，未运行 EDA。本审查应用 user-academic-writing-style 的证据与主张纪律。

## 应调研的整体研究问题

**在功能与物理约束下，怎样根据报告路径和网表结构构造有用的修改区域，生成具有不同面积/时序作用及相互影响的局部动作，把有限的实际分析次数分配给单动作与组合，最终取得可靠的面积—时序改善？**

当前用户选定的应用是“Resizer 修时序 → 自有后续联合优化”，并允许固定参考下可配置 WNS 损失。预算定义只是问题约束的一部分。研究主体还包括候选覆盖、动作粒度与交互、分析档位、反馈归因和整体功能/物理验证。无需以重写 Resizer 前端为独立贡献前提；也不能把工具串联、预算参数或已存在的多动作本身算作创新。

## 三条实际调用链，尚未统一

1. **预布局/探索主线（已实现、可配置）**：`code/scripts/run_outerloop_real_wns.py:336` 映射或复用网表 → OpenSTA 基准报告 → 提取关键实例序列与最差端点 D 网 → `flow.run_multi_iteration_case` → `RealWnsEvaluator` 构造/测量动作 → 事务提交与状态刷新。主论文的受控配置由 `code/scripts/run_r22_cut_ablation.py` 固定参数和输入，最终另外调用 `final_sec`。通用 CLI 有局部等价与 topology SEC 接口，不能据此假设每一种 CLI 配置都自动执行同一最终 SEC 流程。
2. **历史 Recovery（单独实现）**：`code/scripts/recover_area.py:142` 比较 baseline/resizer 同名实例的 master → 对历史变更逐个回退测 WNS → 排序并用 safety factor 累加单点损失筛选 → 合并回退 → 反复整体验证、必要时移除尾部动作。它读取 Resizer 原有 SPEF；没有调用上述区域构造、失败反馈或新预算核心，也没有在线重布线/新提取。这是有限回退清单，不是全库候选生成器。
3. **新面积/时序选择（工程核心已实现，在线物理接入未完成）**：`code/src/rseco/budgeted_recovery.py` 提供固定参考门、SEC 合格终点选择、有限组合 beam 与可行非支配档案。`project_docs/evidence/timing_budget_20261113/evaluate_budget.py` 实际只调用 `assess/select_endpoint` 重筛已审 52 个历史物理终点。全仓 `bounded_search` 调用目前仅在专用测试中；没有生产物理 evaluator 调用它。不能画成已经运行的“区域→新 joint beam→新物理反馈”统一流水线。

## 各层能力、现用关系和证据边界

| 层 | 具体代码与已实现能力 | 当前适用边界 |
|---|---|---|
| 网表/图表示 | `netlist.py`、`netlist_io.py`、`graph.py:71`；有向连接、完整区域边界、组合扇入锥，遇顺序输出停止；外部消费者输出保留 | 用作结构与候选范围，不是学习到的 GNN embedding；FF helper/escaped 全计数必须用已验解析链，不能从旧 regex 推完整覆盖 |
| 区域生成 | `cut.py:149/241/266/326` 节点分裂 s-t min-cut 与历史受限区域搜索；`candidate_policy.py:28` 明确覆盖区域+真正加权割 | 报告序列与锥交集形成覆盖区域；覆盖优先是访问顺序，不是全局路径集合覆盖优化；CLI 默认 legacy，受控 weighted_st 需显式参数 |
| 多动作 | `real_wns.py:1804/1815` 调用 `logic_rewrite.py`、`gate_sizing.py`、`buffer_insertion.py`；R 跨族布尔等价换单元，G 同族增大尺寸，B 接收引脚前缓冲；另有 FF 展开/resize、窗口结构重综合 `structure_resynthesis.py` | 参数决定哪些启用；主论文旧受控 R/G/B 不含后补 FF 动作。`_apply_joint`/`_joint_enumerate_combos` 是联合候选实现，不等于其收益已经成立 |
| 调度与提交 | `flow.py:421`、`real_wns.py:1629`、`refinement_loop.py:138`、`search_state.py`；分组实测择优、更新当前网表、刷新报告/原目标锥、缓存去重 | 组可以是实例或整轮，取决配置；旧主线优化当前基准时序，新 recovery 总损失门必须另保固定 Resizer 参考，不能直接继承移动参考语义 |
| 组合/面积预算 | `budgeted_recovery.py:116/141/164`；same-instance 互斥、完整动作集合回调、有限 beam、失败回调计数、SEC 默认门、无收益 fallback | 数值不合格但有真实证书的中间点可保留供补偿；callback 需自行执行并绑定真实结构/物理，尚无在线 adapter。`valid` 不是内核生成的证书 |
| 有限成本与台账 | `search_state.py`、`refinement_loop.py:88`、`sta_ledger.py:77`；迭代/提交/STA/formal/墙钟约束，缓存/前拒绝与实际启动区别 | 多布局 ensemble 一个逻辑 measurement 可含多次工具运行；不能把预算单位当实际 STA 启动数。新 beam 限回调数而非墙钟 |
| 多档 STA | `opensta.py`/`real_wns.py` 理想档；`spef.py` 合成线载；`placed_sta.py` 真布局+CTS+估计寄生；`routed_sta.py` 全流程与提取/读 SPEF；`real_wns.py:2096` 分派 placed/placed_ens/routed/spef | 多后端存在不等于已有自适应多保真资源分配机制；合成 SPEF 不等于提取寄生；多 utilization 不是随机种子独立重复 |
| 新物理闭合验证 | `recovery_qualification_20261112/physical_probe.py:58–103` 及后续 study driver：同 ODB 改 cell、清普通线、合法化/重路由、提取新 SPEF、理想/propagated STA 分开 | 已在冻结实验 driver 工作，不是 `recover_area.py` 或 `bounded_search` 自动接入；当前 constrained-path/TT 与有限 DRC/DRV，IO/multicorner 资格仍不足 |
| 失败归因/反馈 | `failures.py` F1等价/F2边界/F3过大/F4增益不足/F5验证昂贵/F6物理线载失败；`feedback.py` legacy/EMA；`search_state.py:60–110` 分离方法失败、W工具/基础设施标签、S_TECHMAP_MISMATCH | 反馈能运行与反馈改善收益是两回事；旧受控主配置关闭反馈。不能将工具报错送入方法 EMA 后称失败学习 |
| 等价 | `logic_rewrite.py` 库函数/引脚约束；`real_wns.py` 局部/拓扑 checker；`yosys_abc.py`/`z3_formal.py`；实验驱动的 `run_r22_cut_ablation.final_sec:108` | 局部结构合法性、局部功能检查、最终全网表 SEC 是不同门。近期证据 adapter 修正 used-cell scanner 的 escaped FF 漏项；生产旧 scanner 尚未因此自动修复；两态模型不等四态签核 |

## 两份稿件应分别引用

- `paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex:94,154–249`：r116 预布局候选区域与调度论文。标题为“候选区域构造与调度”；主证据回答覆盖、节点容量、调度与实际 STA 成本的作用。主矩阵关闭反馈/物理门/结构重综合，配置与后补 FF、物理后验族要分开。英文旧 `paper/en/manuscript/FAECO.tex` 尚未与 r116 中文同口径。
- `paper/en/manuscript/FAECO_recovery.tex:13,199–254`：独立的 Resizer 后 selective reversion 工作稿。旧 14%/67%与安全表述已被审计限制，不能承担当前“完整自有机制”的方法/结果。具体缺口在 `project_docs/evidence/library_area_search_20261113/MANUSCRIPT_GAP_REVIEW.md`。
- 当前已验 28.90625% 是 s382 固定阶段 Resizer 净新增面积回收，来自历史 RESTORE074 在用户新 10ps 门下接受，不是新 beam 在线算法所得。完整三点分母、精确 endpoint 与 SEC 在 `timing_budget_20261113/{ACCEPTANCE.json,area_baseline_audit/RECEIPT.json}`。

## 负面证据如何用于整体设计

CANON 历史 GNN、权重、JOINT、增大粒度和多档门的条目应限制在其候选池、目标、测量档和比较设计内。它们不能被重述成“GNN普遍无信号”或“联合优化不可能”；更不能因为旧方案受限，就把新恢复选择的优势当作已经成立。

可以直接转化为研究约束的事实是：已有候选池覆盖决定可达空间；候选排序不能在没有更优可行终点的池里创造收益；几何/负载变化会使单点增量失去可加性；更精细的接受判据不自动产生更好的候选；已实现的反馈必须经受与固定权重和简单顺序的同预算对照。新候选生成应覆盖全库合法目标，历史 edit provenance 可以提供先验顺序，但不应限制动作来源。

## 整体 related work 的对照轴

主线调研应建立同一张机制矩阵，而非只找“WNS budget”论文：

1. **区域与候选空间**：路径驱动局部 ECO、window/cone rewriting、cut-based remapping，是否保证接口、顺序边界以及候选覆盖。
2. **面积/时序动作及交互**：gate sizing、buffer insertion/removal、重映射、组合交换/补偿、clock/FF 边界；与原生恢复和交互安全并行恢复比较。
3. **搜索与预算分配**：顺序贪心、多轮贪心、beam/joint selection、候选缓存、失败与估计成本；在相同候选池、实际工具预算和最终门下比较。
4. **分析与反馈**：增量 STA、物理感知优化、多保真评估/代理/学习排序、最终重布线/提取，区别排序信号与最终接受证据。
5. **正确性与可审计成本**：局部检查与最终 SEC、事务提交/回滚、真实输出身份与失败归因。它们可以支持可靠实现，但常规安全门本身不构成独占创新。

尚待证明的总体假设应是：**完整候选构造与交互感知的联合选择，能在固定物理验证成本下优于同起点的原生恢复和强简单贪心，增加满足可调时序约束的净面积回收。** 反驳条件包括：简单多轮贪心追平；收益仅来自更多候选/更多路由预算；组合收益不能跨设计保留；完成 IO/角约束后原优势消失。当前代码提供该研究的若干可复用组件，证据尚未证明统一机制优势。

路径阅读提醒：`code/src/rseco/README.md` 的 Stage A/B“仍待启动”清单明显早于现有实现，不适合作为当前架构清单；CANON/ROADMAP 同一文件保留多个历史日期条目，最新裁定优先，不能把历史“下一步唯一”或“尚未实现”直接覆盖顶部已完成工程门。
