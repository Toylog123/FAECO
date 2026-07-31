# FAECO 方法重写就绪审计

更新时间：2026-07-19

## 1. 审计目的

本文档判断 FAECO 方法章节的各个组成部分是否已有工程事实和实验字段支撑。它不是论文方法正文，也不把目标设计、接口占位或本地 smoke 写成已完成的方法贡献。

当前事实来源按以下顺序解释：

1. `src/rseco/`、`tests/` 和实验产物决定“当前已实现什么”。
2. `docs/experiment_design/` 定义目标口径、指标边界和后续实现要求。
3. RSECO 旧稿只提供历史问题动机和待重定义思想，不作为 FAECO 实现或实验结果的权威来源。

状态含义：

- `ready`：当前实现和字段足以支持受限、准确的方法描述。
- `partial`：已有可描述接口，但关键语义仍是代理、硬编码或仅覆盖局部场景。
- `blocked`：关键行为尚未实现，当前不得写成方法能力或实验结论。

## 2. 方法要素就绪矩阵

| ID | 方法要素 | 当前工程事实 | 状态 | 可写边界 | 缺口与依赖 |
|---|---|---|---|---|---|
| METH-01 | 问题输入与 case schema | original/resynthesized netlist、target output、metadata 和 metrics 路径已进入 case loader 与 runner | partial | 可定义当前组合逻辑、单目标输出的 Stage A 输入；X21 EPFL MIT 8-case 已规范化、license 与 blob SHA 已归档，可支撑论文主集 | Stage A case loader 仍只接 ISCAS-style Verilog；EPFL JSON 与 Yosys JSON 暂未直接喂入 case loader；需 [G24] |
| METH-03 | 图模型与 cone extraction | 当前 parser 可构造门级有向图，并按 target output 抽取 fanin cone | partial | 可描述组合逻辑 fanin cone | 尚无 fanout、reg-to-reg 或 sequential cone；assign-style EPFL 输入需先规范化 |
| METH-04 | 新旧网表等价点映射 | `equivalence_map` 只存在于目标算法文档输入定义 | blocked | 不得描述自动等价点发现或 mapping 质量 | 当前代码没有内部节点匹配、映射生成或映射验证 |
| METH-05 | fixed/weighted cut 搜索 | fixed min-cut、weighted graph 和确定性 weighted s-t cut 已实现并有测试及 5-case smoke | ready | 可描述当前 Stage A cut graph、node cost 和确定性 cut 选择 | 仅在当前组合逻辑 cone 语义内成立，尚未由公开主 benchmark 验证扩展性 |
| METH-06 | boundary closure 判定 | `build_case_metrics` 调用失败分类时把 `boundary_closed=True` 固定传入 | blocked | 只能说明字段和失败类型 F2 已预留 | 尚无悬空输入、未映射输出、多输出覆盖或 reconvergence closure 检查 |
| METH-07 | Boolean patch synthesis | patch candidate 当前记录 selected gates、boundary、size 和等价字段 | blocked | 可描述候选表示，不得称为补丁函数综合 | 尚无 Boolean patch function、逻辑重建或可综合 patch 生成 |
| METH-08 | 等价验证 | structural signature 已实现；ABC formal wrapper 能记录 pass/fail/error/timeout/unavailable；隔离 5-case 全网表 Yosys-BLIF-ABC 探针均 pass；Stage B mapped-BLIF equivalence wrapper (`check_mapped_blif_equivalence` in `src/rseco/yosys_abc.py`) 已实现 | partial | 必须分别描述结构签名、隔离探针、Stage A 5-case 5/5 pass 和 Stage B mapped-vs-original 形式回验框架 | Stage B mapped-vs-original CEC 受 SKY130 Liberty 不含 `clkinv_1` 限制，当前全部 8 case 跑出 `unavailable`；探针比较 original/resynthesized 全部主输出，不是对候选 patched netlist 的闭环验证 |
| METH-09 | F1-F5 失败分类 | `classify_failures` 可按等价、边界、change ratio、logic-level reduction 和验证时间返回类型 | partial | 可写为当前分类接口及 Stage A 代理口径 | F2 输入被硬编码为通过，F5 时间被硬编码为 0；F3 未实现绝对 size 阈值，F4 尚无真实 timing gain |
| METH-10 | failure-aware refinement | F1-F5 对应的确定性权重调整已实现，当前每个 case 记录一次动作 | blocked | 可描述单次反馈原型 | X19 需实现重新生成候选、重新分类 residual failures、停止原因和首次恢复轮次 |
| METH-11 | candidate-specific timing 特征 | 当前逻辑级变化来自整网表目标输出，并向所有候选传入同一数值 | blocked | 只能称为 Stage A target-output logic-level proxy | 需 X19 的候选级重算；Stage B OpenSTA 已接但 WNS/TNS/slack 因纯组合电路为 null，不能写入真实 timing gain |
| METH-12 | deterministic ranking | score 公式、稳定排序和 equivalence penalty 已实现 | partial | 可描述 ranking 接口和确定性 tie handling | 当前候选 timing gain 相同、verification cost 均为 0，尚不能证明多目标特征有效 |
| METH-13 | replacement | `internal_cone_replacement_v0` 能把 selected patch 写入 cone-level 内部表示并记录 `applied` | partial | 必须使用“内部表示替换”措辞 | 未生成可综合 Verilog、未回写完整网表、未对替换后网表做 formal/STA closure |
| METH-14 | 迭代停止条件 | 算法文档定义 max iterations、成功和失败停止条件 | blocked | 可列为目标设计要求 | 当前 flow 没有迭代循环、residual failure 或停止原因字段 |
| METH-15 | runtime 记录 | per-case schema 和 batch runtime breakdown 已覆盖 Python 阶段及外部 wrapper 状态；Stage B 8-case 汇总写回 `tables/stage_b_runtime.{json,md}` 含 mapping / sta / total 秒 | ready | 可描述 schema 和 Stage A + Stage B 已测 Python/Yosys/ABC/OpenSTA runtime | 当前 YOSYS/ABC/OpenSTA 单进程 wall-clock；多线程/分布式 runtime 未测；OpenSTA 路径转换 (Windows→WSL2) 含 WSL PATH translation warning |
| METH-16 | 方法输出 | metrics、candidate、ranking、replacement 和 batch 表已有结构化产物 | partial | 可描述实验记录结构 | 没有 `patched_netlist`、formal counterexample、STA report 或多轮 failure log |
| METH-17 | 主实验支撑 | 5-case 本地 smoke、Stage A 多 baseline 接口、Stage B 8-case (ctrl/int2float/router/cavlc/dec/priority/adder/max) 全部 mapping+STA success | partial | 可写为 Stage A/B 端到端工程可行性证据；正式主表仍需多 PDK/多 corner 扩展 | Stage B CEC 当前 `unavailable` (L31-01)；3 个 ISCAS85 大 case 许可未声明；sequential EPFL case 尚未接入；Z3 candidate/boundary formal 未接入 |
| METH-18 | failure-feedback 消融 | baseline protocol 已定义 without F1/F3/F4 等配置 | blocked | 只能写入实验计划 | 当前没有消融配置、运行结果或统计表，依赖 X19 |

## 3. 旧稿硬伤处置门槛

| ID | 旧稿问题 | 当前处置策略 | 就绪状态 | 新稿约束 |
|---|---|---|---|---|
| SRC-01 | PDF 公式编号从 (14) 跳到 (16) | Word 字段更新已证明原 (16)-(20) 应为 (15)-(19) | ready | 新稿重新编号，不复制旧 PDF 缓存编号 |
| SRC-02 | 第 5.1 节“图1”实际指图6 | 页级位置已确认 | ready | 新稿使用自动交叉引用并逐项复核 |
| SRC-03 | 表2正文、Avg 行、逐 case 均值和 slack 反算值冲突 | 原始高精度日志缺失，无法认证唯一旧均值 | ready | 删除旧 B&G/RSECO 平均改善 claim，只使用可追溯的新实验数据 |
| SRC-04 | “CutFinder 有效解决失败”和近线性扩展等强结论 | 当前只有单次 Stage A proxy，且无 formal/STA closure 或规模曲线 | blocked | 在 X18/X19/X21、OpenSTA 和 runtime scaling 完成前不得恢复这些结论 |

## 4. 旧公式处置原则

| 旧稿公式组 | 表达内容 | FAECO 处置 | 当前门槛 |
|---|---|---|---|
| (1) | 布尔电路表示 | 保留问题思想，重新定义 graph、node、edge 和 cone 符号 | METH-01/METH-03 达到 `ready` 后定稿 |
| (2)-(3) | 等价切割与多目标 timing ECO | 不直接继承；分别重定义 boundary、formal verification 和 ranking objective | METH-06/METH-08/METH-12 |
| (4)-(8) | 逻辑级、slack 传播与改善量 | 拆成 Stage A logic-level proxy 和 Stage B OpenSTA 指标 | Stage A 可受限描述，Stage B 等待 OpenSTA |
| (9)-(13) | cut cost、截断与等价完整性 | 以代码中的 node cost、cut solver 和 verifier 字段重写 | 参数敏感性、boundary closure 和 formal 仍缺失 |
| (14) | 近似线性复杂度 | 删除强复杂度结论，以多规模 runtime 曲线替代 | 等待 X21 规模扩展和真实外部工具 runtime |
| 原 (16)-(20)，校正为 (15)-(19) | 匹配度与迭代权重更新 | 不复制旧递归公式；按 F1-F5、反馈动作、residual failure 和停止条件重新定义 | 等待 X19 真正多轮日志与消融 |

## 5. 当前可写与禁写边界

### 5.1 当前可进入方法初稿的内容

- FAECO 面向局部组合逻辑 ECO 的问题范围和输入 schema。
- 当前 fanin cone、fixed/weighted cut、候选表示和确定性 ranking 的已实现接口。
- structural signature 与 formal equivalence 的严格区分。
- F1-F5 taxonomy 作为目标分类框架，以及当前仅完成的单次反馈原型。
- Stage A logic-level proxy、Stage B OpenSTA 指标和外部工具 runtime 的分层口径。

这些内容仍需在方法写作设计获批后落成符号表、伪代码和正文，不能由本审计文档替代。

### 5.2 当前不得写成已实现或已验证的内容

- 自动等价点映射、真实 boundary closure 或 Boolean patch synthesis。
- 可综合 patched Verilog、替换后网表 formal pass 或 timing closure。
- 5-case ABC baseline 已完成，或 5-case 已通过 ABC/SAT formal。
- 基于真实 STA 的 critical path、WNS/TNS 改善和 timing-aware ranking 收益。
- 多轮 failure recovery、首次恢复轮次、without F1/F3/F4 消融结论。
- 近线性复杂度、公开 benchmark 上的可扩展性或相对现有方法的优越性。

## 6. 方法章节交付门槛

| 交付物 | 当前状态 | 允许开始条件 | 完成条件 |
|---|---|---|---|
| 符号表 | pending | 方法章节结构和命名获批 | 每个符号可映射到代码字段或明确的目标接口 |
| 算法伪代码 | pending | X19 成功口径与循环设计获批 | 与实际循环、residual failure、停止原因和输出字段一致 |
| 总体流程图 | pending | X18/X19 的模块边界稳定 | 明确区分已实现 Stage A、外部 formal 和待接入 Stage B |
| failure-aware loop 图 | pending | X19 产生真实多轮日志 | 图中每个反馈箭头都有实现和日志字段 |
| 方法正文 | pending | 符号表和伪代码通过工程反校 | 不包含本审计列出的禁写 claim |
| 方法相关结果表 | pending | X18/X19/X21 和 OpenSTA 产生数据 | formal、runtime、recovery、ablation 和 benchmark 来源均可追溯 |

## 7. 下一依赖顺序

1. X18：把 Yosys/`yosys-abc` 规范化、formal、ABC baseline 和外部 runtime 接入正式 runner。
2. X19：实现候选级重新评估、多轮 residual failure、停止原因和消融配置。
3. X21：导入 EPFL `v2025.1` 第一波公开 benchmark，替换许可不完整的主表依赖。
4. OpenSTA：补真实 critical path、WNS/TNS 和 Stage B closure。
5. N08：在方法正文进入可追溯写作前建立经批准的 Git 基线；当前仍未 staging、未提交。

结论：方法重写的事实边界已经可审计，但完整 Method 仍为 `pending`。当前可以准备受限的符号和接口映射，不能把目标算法文档直接转写为已实现方法。
