# FAECO 稳定化与模块化总体设计

日期：2026-08-28

状态：设计冻结候选（用户已批准“方案 2：稳定化再模块化”）

适用分支：`codex/faeco-unified-loop`

设计基线：`c58ad8ec5e8bc8d8a58e7a77cdce655b8c3e6879`

## 1. 目的与范围

本设计规定 FAECO 从“功能已汇集的统一闭环”推进到“可审计、可复现、可分工维护的研究与工程基线”的路线、模块边界、阶段顺序、硬门禁和智能体交接规则。

本设计解决以下问题：

1. 受审代码、最新代码、主目录实验和论文资产存在多个状态源。
2. 搜索策略、验收规则、运行预算和失败分类仍有语义耦合。
3. `RealWnsEvaluator` 等核心文件职责过多，继续叠加功能会放大回归风险。
4. 测试与外部工具的运行环境未完全固化，旧的通过结论不能自动覆盖最新提交。
5. 实验数字与代码 SHA、配置、工具版本和原始证据之间缺少统一机器可读绑定。

本设计不授权在当前脏 `main` 工作目录中合并、清理、恢复论文文件、删除实验产物或直接运行新的全量实验。各阶段只有通过前一阶段门禁后才能启动。

## 2. 当前事实基线

截至设计审计时：

- 活跃实现位于隔离 worktree 的 `codex/faeco-unified-loop`，HEAD 为 `c58ad8e`，比远端 feature 分支领先 16 个提交。
- 旧 Sol 复审批准的是 `79b8f05`；`79b8f05..c58ad8e` 的新增改动尚未形成新的完整批准记录。
- 在显式设置 `PYTHONPATH=src;scripts` 后，全量回归为 `366 passed, 4 skipped, 1 subtests passed`。
- 默认 `python -m pytest` 会因 `run_sequential_timing_check` 导入路径未固化而在收集阶段失败。
- `git diff --check origin/codex/faeco-unified-loop...HEAD` 当前报告两处尾部空行问题。
- `real_wns.py`、`flow.py`、`cut.py` 分别约 2165、790、765 行，承担多类职责。
- 20260826 实验结论为 ISCAS89 8/8 改善、ITC-99 18/19 改善、SEC 28/28 PASS + 1 N/A；b15 暴露 early-stop 的质量—成本取舍，b17 暴露 60 秒运行预算对有效候选的误拒。
- 主目录 `main` 包含大量历史修改、删除和未跟踪论文/实验资产；不得把该目录当作干净集成环境。

这些事实是后续门禁的起点，不是待实现目标。

## 3. 总体原则

### 3.1 小步推进

每个执行批次应满足：

- 只解决一个清晰问题或一个紧密耦合的问题组。
- 建议代码差异不超过 400 行；超过 800 行必须拆分或在任务说明中解释原因。
- 建议单个批次不跨越两个以上核心模块。
- 先增加可失败的契约测试，再修改行为。
- 每个批次独立提交，提交信息包含阶段 ID。
- 每个批次在进入下一批次前完成自检、独立审查和证据归档。

行数阈值是审查触发器，不是为了达标而机械拆分代码的指标。

### 3.2 门禁优先

任何“完成”必须同时具有：

1. 明确交付物；
2. 可重复命令；
3. 新鲜执行结果；
4. 与代码 SHA 绑定的证据；
5. 已知边界和未覆盖项。

没有证据的功能只能标记为 `implemented-unverified`，不能标记为 `done`。

### 3.3 正确性、质量和成本分离

- 正确性门禁决定候选是否可用，例如结构闭合、功能等价和证据完整性。
- 质量门禁决定候选是否值得接受，例如 setup WNS、TNS、hold、物理配对指标和 patch ratio。
- 资源策略决定是否继续搜索、调度多少候选和何时停止。

已完成且通过正确性与质量门禁的测量，不得仅因运行时间超过软成本阈值而被事后判为无效。硬 timeout 必须在执行层终止任务并记录未完成，而不是完成后再丢弃结果。

### 3.4 兼容式重构

保留 `RealWnsEvaluator` 和 `run_multi_iteration_case` 的公开调用外观。新模块先在内部接入，契约测试证明行为稳定后再迁移调用者，禁止一次性重写闭环。

### 3.5 证据先于论文数字

论文表格和结论必须从冻结的运行清单和结果生成，不允许人工复制后失去来源。N/A、失败、skip 和未测项目必须独立统计，不得并入通过率。

## 4. 目标架构

目标数据流：

```text
RunSpec
  -> SearchOrchestrator / SearchState
  -> CandidatePlanner + SearchPolicy
  -> VerificationPipeline
  -> AcceptancePolicy
  -> StateCommit
  -> EvidenceStore
  -> Aggregator / Claim Registry
```

### 4.1 RunSpec

`RunSpec` 是一次运行的唯一配置源，至少包含：

- schema 版本；
- 代码 commit、分支和工作树状态；
- benchmark 来源、case ID、输入文件哈希和许可来源；
- Yosys、ABC、OpenSTA、Python、操作系统和工艺库版本/哈希；
- setup/hold/physical 模式与必需指标；
- search policy、候选族、随机种子和排序策略；
- candidate timeout、总 wall budget、STA/formal 数量预算和 patch budget；
- acceptance policy、epsilon、最低收益和最大 patch ratio；
- artifact retention policy；
- 输出目录和 run ID。

CLI 参数可以覆盖配置文件，但最终解析后的完整 RunSpec 必须在运行开始前写入输出目录。未记录的隐式默认值视为设计缺陷。

### 4.2 SearchOrchestrator 与 SearchState

该层只负责：

- 当前网表和当前指标状态；
- 轮次、预算预留与停止条件；
- 候选调度；
- 接受补丁后的原子状态提交；
- failure feedback 的下一轮输入；
- 可重放的 accepted patch 历史。

该层不得直接解析 Liberty、运行 OpenSTA、生成 SPEF 或实现具体候选变换。

### 4.3 CandidatePlanner

该层负责：

- constrained cut 与候选边界；
- R、G、B、JOINT、TOPOLOGY action 生成；
- 候选规范化、哈希和去重；
- 将策略优先级应用到候选队列；
- 输出候选来源、策略族和排序原因。

候选生成与候选是否通过验证必须分离。Planner 不得根据未执行的 STA 结果直接宣告候选成功。

### 4.4 SearchPolicy

至少定义三种明确模式：

| 模式 | 语义 | 用途 |
|---|---|---|
| `fast` | 按确定队列串行执行；第一个通过完整 AcceptancePolicy、到达 `ACCEPTABLE` 的候选被选择并停止本轮 | 效率消融和资源受限运行 |
| `balanced` | 每轮完成各启用策略族的最低验证覆盖以及 RunSpec 指定的 JOINT 配额，然后从已完成验证的候选中确定性选优 | 论文主结果和默认生产模式 |
| `exhaustive` | 完成当轮全部已生成候选的验证后确定性选优；预算不足导致未完成时只产出诊断性部分结果 | 哨兵电路、搜索上界和回归诊断 |

覆盖按“到达验证终态的候选数”计数，而不是按已生成候选数计数。验证终态包括 `ACCEPTABLE` 和带结构化原因的拒绝。如果 Planner 明确记录某个启用策略族没有 actionable candidate，该族可以记为 `unavailable`，但不能静默视为已覆盖。

`balanced` 的每族最低验证数和 JOINT 配额必须在 RunSpec 中显式配置。预算在最低覆盖完成前耗尽时，stop reason 为 `coverage_incomplete_budget_exhausted`，该轮不能进入论文主结果；预算在最低覆盖完成后耗尽时，记录 `budget_exhausted_after_coverage`，可以从已完成候选中选优，但必须保留部分搜索边界。`exhaustive` 未完成全部候选时记录 `partial_budget_exhausted`，不得作为 exhaustive 上界结果。

所有模式使用 CandidatePlanner 输出的稳定队列；相同 RunSpec、输入哈希和 seed 必须得到相同顺序。`fast` 的“改善”不等同于只看原始 WNS，而是候选通过完整 AcceptancePolicy。不得继续使用含义不明的布尔 `early_stop` 作为论文主配置描述；兼容层只能把它显式映射为 `fast` 并记录弃用告警。

### 4.5 VerificationPipeline

每个候选按以下状态机推进：

```text
GENERATED
  -> STRUCTURAL_PASSED
  -> FORMAL_PASSED
  -> STA_MEASURED
  -> PHYSICAL_PAIRED (当 RunSpec 要求时)
  -> ACCEPTABLE
  -> SELECTED
```

任一阶段失败都必须产生结构化事件，包含：

- gate ID；
- failure code；
- candidate/cut/base hash；
- 输入配置哈希；
- 工具与版本；
- 原始证据路径；
- runtime 和 timeout 状态；
- 可重试性；
- 人类可读摘要。

F1–F6 可以继续作为论文层 failure taxonomy，但执行层必须同时记录发生阶段，避免一个 failure code 同时承担调度、正确性和质量三种语义。

### 4.6 AcceptancePolicy

AcceptancePolicy 只接收已经完成验证的结构化指标，不运行工具。默认规则：

- 必需的正确性门禁全部通过；
- required metrics 全部可用，否则 fail-closed；
- setup WNS 严格改善超过 epsilon；
- TNS、hold 或 physical 指标按 RunSpec 的允许退化预算判断；
- patch ratio 不超过上限；
- 候选 provenance 完整。

如果运行目标是 hold 或 paired physical，主排序指标必须随模式改变，不能继续统一按 setup WNS 排序。

多个 `ACCEPTABLE` 候选使用以下确定性比较顺序：

1. setup 模式：setup WNS 增益、setup TNS 增益；
2. hold 模式：hold min-slack 增益、setup WNS 增益；
3. paired physical 模式：RunSpec 指定的 physical 主指标增益、physical 次指标、setup WNS 增益；
4. 以上模式共同的后续 tie-break：较小 patch ratio、较小 candidate hash 字典序。

缺失的非必需次指标不优于可用值；缺失必需指标直接 fail-closed。runtime 只进入调度和成本统计，不进入质量选优 tie-break。

### 4.7 EvidenceStore 与保留策略

证据分三层：

- A 层永久保留：RunSpec、manifest、结果 JSON、failure events、accepted patch、SEC 证据、工具版本、汇总输入。
- B 层按需保留：失败诊断所需的代表性候选网表和日志。
- C 层可再生：未接受候选的全量 `mapped.v`、重复 STA 日志和临时映射目录。

只有在 A 层清单证明 C 层可再生后，自动清理策略才能处理 C 层。任何删除工作必须是独立任务，并遵循用户逐路径授权。

### 4.8 Aggregator 与 Claim Registry

Aggregator 只接受合法 manifest，不从目录名猜测配置。每条论文 claim 至少绑定：

- claim ID；
- run ID 集合；
- code commit；
- RunSpec hash；
- 工具链 hash；
- 原始指标；
- 聚合脚本版本；
- 适用边界。

论文的主结果、消融、效率、SEC 和物理结果必须分别注册，禁止把不同搜索模式或不同工具版本混入同一主表而不标注。

## 5. 门禁体系

### G0：设计冻结门禁

通过条件：

- 本设计经用户确认；
- 模块职责、阶段顺序、主搜索模式和论文口径无未决冲突；
- 后续第一个实施计划只覆盖 Phase 0–1，不一次性规划全部阶段。

失败处理：修订本设计，不启动实现。

### G1：仓库与基线门禁

通过条件：

- `phase0_integration_base_sha` 固定为本地跟踪 ref `origin/main=b8c37590d7960715a0ec132f9b1c152973803675`；
- `phase0_base_sha` 固定为 `c58ad8ec5e8bc8d8a58e7a77cdce655b8c3e6879`，实现初始审计范围为 `79b8f05..c58ad8e`；Phase 0 实现工作必须从该 SHA 新建 `codex/faeco-phase0-stabilization`，不得直接叠加在包含本设计提交的治理分支 HEAD 上；
- `phase0_validated_head_sha` 在 P0.2、所有阻断性 P0.x 正确性修复及 P0.3 完成后生成；它必须是 `phase0_base_sha` 的后代，只包含已列入 Phase 0 closure matrix 的实现/测试/验证入口改动，并在新的 Sol review 和 `verification-summary.json` 中记录；
- `governance_head_sha` 指包含本设计和后续计划的文档提交链，仅作为执行依据，不是 P0.4 的实现合并源，待 G8 再随最终受审分支集成；
- 从 `phase0_integration_base_sha` 创建一次性分支 `codex/faeco-integration-audit` 和干净 integration worktree；P0.4 的唯一合并源是冻结后的 `phase0_validated_head_sha`，不得回退使用 `phase0_base_sha`，也不得在本地主目录 `main` 上演练；
- `phase0_validated_head_sha` 冻结后如发生任何代码或测试变化，G2、G3 和 Sol review 自动失效，必须重新执行并产生新的 validated SHA；
- P0.1 开始时重新解析并记录这些 ref；任一 ref 与本节 SHA 不一致时立即停止，由总体负责人更新设计/计划后再继续，禁止自动改用新 HEAD；
- 精确记录 `main`、feature、本地和远端 SHA；
- 审计 `79b8f05..c58ad8e` 的新增提交；
- 当前脏 `main` 的 modified/deleted/untracked 资产只读清点，不恢复、不删除、不混入；
- feature 分支工作树保持干净；
- `git diff --check` 通过；
- 形成新的 Sol review 结论。

失败处理：停留在 G1；不得 merge、push 或启动基于最新 HEAD 的正式实验。

### G2：测试入口门禁

通过条件：

- 在干净 shell 中直接执行标准命令即可运行测试，不依赖人工设置未记录的 `PYTHONPATH`；
- 全量 Python 回归通过；
- 零收集错误；
- 所有 skip 都有原因、责任人和 release 处理方式；
- 快速 smoke 测试有独立命令；在当前参考 Windows 主机、记录 Python/CPU 信息的干净 shell 中，连续三次执行均不得超过 60 秒；其他主机只能提供补充数据，不能用更宽时限替代本门禁；
- 测试命令写入 README 或统一开发入口。

当前基准：显式路径下 366 passed、4 skipped。G2 不能仅以这个历史数字通过，必须在修复后的 SHA 上新鲜复跑。

### G3：工具链与真实 SEC 门禁

通过条件：

- 工具路径和版本由 RunSpec/环境探测记录；
- native Yosys 映射、WSL Yosys/ABC SEC、OpenSTA smoke 均有真实执行证据；
- 非 ASCII 路径用例通过；
- async clear/preset、vector port、输出 alias、深锥结构签名等新增修复具有真实或契约级验证；
- 无未解释的环境 skip。

失败处理：允许代码单测继续，但不得进入正式 benchmark 门禁。

### G4：配置、验收与策略语义门禁

通过条件：

- `fast`、`balanced`、`exhaustive` 具有独立契约测试；
- RunSpec 具有 schema version、解析快照、稳定 config hash 和完整默认值展开测试；CLI 覆盖后的最终值必须进入快照，禁止保留未记录的隐式默认值；
- search policy 与 AcceptancePolicy 完全分离；
- AcceptancePolicy 是不运行外部工具的纯逻辑接口，required metrics 缺失时 fail-closed，setup/hold/paired physical 的主指标和 tie-break 符合 §4.6；
- 完成后的正确候选不因软 runtime 阈值被事后作废；
- hard candidate timeout、campaign wall budget、STA/formal 数量预算具有不同 stop reason；
- 同一 RunSpec 和 seed 的候选顺序、hash 与结果可重放；
- b15 fixture 能明确复现 fast 与 exhaustive/balanced 的差异；
- b17 fixture 能证明软成本超限只产生成本事件、不会否定已完成且通过 AcceptancePolicy 的候选，并能区分真实 hard timeout。

失败处理：不得重跑 b17 或生成新的论文主表。

### G5：哨兵实验门禁

哨兵集与目的：

| Case | 覆盖目的 | 最低通过条件 |
|---|---|---|
| s27 | 最小端到端 smoke | mapping、STA、候选、SEC、manifest 全链通过 |
| s382 | 常规 sequential 与 hold/physical 入口 | balanced 模式可重放；接受/拒绝证据完整 |
| b15 | JOINT 与 search-policy 取舍 | fast 与 balanced/exhaustive 结果分开记录；balanced 不在检查 JOINT 前提前结束 |
| b17 | 大电路与 runtime policy | 已完成的有效候选不被软 F5 误拒；hard timeout/总预算行为可解释 |
| b18 | 大规模 JOINT 与物理配对 | paired physical 数据和工具来源完整；不外推为 P&R signoff |
| picorv32 | OOD 与异构时钟/端口 | 正确 top/clock 选择；N/A 与失败单独记录 |

哨兵运行必须使用固定输入哈希和 RunSpec。某 case 因工具或数据不可用时，G5 为 blocked，不能用旧结果替代新鲜运行。

### G6：模块化重构门禁

通过条件：

- `RealWnsEvaluator` 对外接口保持兼容；
- CandidatePlanner、VerificationPipeline、AcceptancePolicy、EvidenceStore 至少在代码层形成清晰边界；
- 每次抽取后 G2–G5 中适用的门禁复跑；
- golden fixture 的候选 hash、failure events 和 accepted patch 仅在有设计决策时变化；
- 不在同一批次同时重写搜索算法和证据 schema。

失败处理：回退当前小批次提交，不回退已通过门禁的前序批次。

### G7：全量实验门禁

通过条件：

- 主实验使用冻结的 `balanced` RunSpec；
- `fast` 只作为效率消融，`exhaustive` 只作为指定子集上界；
- 每个 accepted patch 对应 SEC 结果，SEC 通过率为 100%；
- N/A 不进入分母，失败不改写为 N/A；
- 随机实验记录所有 seeds；
- 每个批次有完整性检查和中断恢复策略；
- 聚合结果能够从原始 manifest 全量重建。

失败处理：只重跑失败或缺证据的 run ID，不覆盖原始目录，不手工修改 summary。

### G8：论文与发布门禁

通过条件：

- 所有 headline 数字均能从 Claim Registry 追溯；
- 工具版本、搜索模式和 benchmark 分母一致；
- b15 质量—成本取舍如实呈现；
- b17 不再由无关成本阈值制造假失败；
- estimated SPEF 只支持 Logic Filter 定位；没有 DRC、多 corner 或真实布线证据时不得写 signoff；
- DOI/accession 占位符在投稿包中清除或明确标记；
- integration worktree 全量验证和独立复审通过；
- 用户明确批准后才 merge/push。

## 6. 分阶段路线

### Phase 0：冻结与保护

目标：建立唯一可实施基线，不引入新算法特性或主动改变 search/acceptance 语义。P0.2 如发现必须改变行为才能关闭的 Critical/Important finding，原审查批次只记录并阻断；由总体负责人建立单独的 P0.x 正确性修复批次，先冻结期望契约、再最小修复并重新审查，不能把行为修复混入资产审计或测试入口整理。

小步批次：

1. P0.1：只读审计 main/feature/remote 状态，生成资产与 SHA 清单。
2. P0.2：审查 `79b8f05..c58ad8e`，无行为变化的 finding 可在原批次关闭；需要行为变化的 finding 转为阻断性 P0.x 正确性修复批次。
3. P0.3：修复默认测试入口和 diff-check；复跑全量测试与真实 SEC smoke。
4. P0.4：从 `phase0_integration_base_sha` 创建干净 integration worktree，将冻结的 `phase0_validated_head_sha` 作为唯一源演练合并但不 push。

出口门禁：G1、G2、G3。

### Phase 1：配置和策略语义

目标：在不拆大文件前，先把最容易造成实验口径错误的语义固化。

小步批次：

1. P1.1：定义 RunSpec schema、解析后的配置快照和 config hash。
2. P1.2：拆分 hard timeout、总预算和软成本信号。
3. P1.3：将 AcceptancePolicy 提取为纯逻辑接口。
4. P1.4：定义 fast/balanced/exhaustive，并保留旧 CLI 的兼容映射和弃用告警。
5. P1.5：增加 b15/b17 契约 fixture。

出口门禁：G4。

### 6.1 Phase 0–1 追踪表

| 批次 | 最小交付物 | 必须存在的契约/检查 | 出口门禁 |
|---|---|---|---|
| P0.1 | `baseline-audit.json`、只读资产清单、`phase0_integration_base_sha`、`phase0_base_sha`、`governance_head_sha` | ref 与本设计不一致时 fail；从 phase0 base 新建实现分支；不得修改脏 main | G1 |
| P0.2 | `delta-review.md`、finding closure matrix | Critical/Important 零开放；行为 finding 必须进入独立 P0.x | G1 |
| P0.3 | 统一测试入口、`verification-summary.json`、冻结的 `phase0_validated_head_sha` | 默认 pytest、smoke 3×≤60s、diff-check、skip 清单、真实 SEC smoke；validated SHA 后续变化会使结果失效 | G2、G3 |
| P0.4 | integration 演练记录、精确 merge SHA、干净状态证明 | 只在 `codex/faeco-integration-audit` 合并 `phase0_validated_head_sha`，不使用 base SHA，不 push | G1–G3 |
| P1.1 | RunSpec schema、resolved snapshot、config hash | schema/version/default/CLI override/hash 稳定性测试 | G4 |
| P1.2 | runtime/budget 语义和结构化 stop reason | soft cost、hard timeout、wall/STA/formal budget 分离测试 | G4 |
| P1.3 | 纯 AcceptancePolicy 接口 | fail-closed、setup/hold/physical、确定性 tie-break 测试 | G4 |
| P1.4 | fast/balanced/exhaustive 和旧 CLI 映射 | 覆盖计数、预算耗尽、稳定顺序、弃用告警测试 | G4 |
| P1.5 | b15/b17 golden fixtures | 质量—成本差异和软 F5/硬 timeout 分离测试 | G4 |

### Phase 2：哨兵验证

目标：证明新语义解决真实问题，暂不运行全量 benchmark。

顺序：s27 → s382 → b15 → b17 → b18 → picorv32。前一个 case 未通过时不得并行扩张到后一个高成本 case。

出口门禁：G5。

### Phase 3：兼容式模块化

目标：降低核心文件耦合，同时保持 Phase 2 行为。

建议抽取顺序：

1. CandidatePlanner；
2. VerificationPipeline；
3. AcceptancePolicy 实现与指标模型；
4. EvidenceStore；
5. SearchOrchestrator 瘦身；
6. 清理兼容层和废弃参数。

每次只抽取一个边界；每次抽取都必须复跑适用哨兵。

出口门禁：G6。

### Phase 4：证据与实验系统

目标：实现 manifest 驱动的批量运行、恢复、聚合和保留策略。

小步批次：

1. P4.1：run ID、manifest 和 events schema；
2. P4.2：断点恢复与幂等聚合；
3. P4.3：artifact retention dry-run；
4. P4.4：Claim Registry 和自动表格；
5. P4.5：全量实验 dry-run 后再正式运行。

出口门禁：G7。

### Phase 5：论文与发布

目标：冻结论文证据包并安全集成。

顺序：结果冻结 → claim 审计 → 表图生成 → 论文回填 → PDF/引用/版面复核 → 独立审稿 → 用户批准 → merge/push。

出口门禁：G8。

## 7. 推进与汇报策略

### 7.1 单批次状态机

每个小批次只能处于：

`planned -> in_progress -> gate_check -> review -> completed`

如果门禁失败：

`gate_check -> failed -> diagnose -> revised -> gate_check`

禁止在门禁失败状态下将后继任务标成 in_progress。

### 7.2 每批次必交付内容

- 任务说明和范围；
- 修改文件清单；
- 新增/变化的契约；
- 测试命令与完整结果摘要；
- 门禁矩阵；
- 风险、skip 和未完成项；
- 精确 commit SHA；
- 下一批次是否获准启动。

### 7.3 独立审查

- 实现智能体不能独自宣布自己的批次通过最终门禁。
- 审查智能体只读检查 diff、测试和证据；不得顺手修改实现。
- Critical/Important finding 未关闭时批次不能完成。
- 同一批次最多三轮自动修订审查；超过三轮交回用户决策。

### 7.4 并行限制

允许并行：

- 文档审计与只读资产盘点；
- 不共享输出目录的独立测试；
- 已冻结 RunSpec 下不同 benchmark 的正式批次。

禁止并行：

- 两个智能体同时修改 `real_wns.py`、`flow.py` 或同一 schema；
- 一边改变搜索/验收语义，一边启动正式实验；
- 一边合并 feature，一边处理脏 main 资产；
- 多个运行写入同一实验目录。

## 8. 智能体任务包规则

后续交给其他智能体的每个任务包必须写明：

1. 任务 ID 与所属 Phase；
2. 唯一目标；
3. 输入 commit 和允许修改的路径；
4. 禁止修改的路径与禁止动作；
5. 必须先读的设计/交接文件；
6. 必须新增或更新的测试；
7. 必须执行的门禁命令；
8. 交付物和完成标准；
9. 失败时停止条件；
10. 面向下一智能体的交接内容。

任务包不得只写“优化”“完善”“修复所有问题”等无边界描述。

## 9. 回退与恢复策略

- 每个小批次一个独立提交；不使用 `git reset --hard` 清理用户工作。
- 行为变化必须保留旧配置或 fixture 作为对照，直到新门禁通过。
- 实验目录采用新 run ID，禁止覆盖旧结果。
- schema 变化必须带 schema version 和只读迁移器；不得原地改写历史 manifest。
- 高成本实验中断后从 manifest 恢复，不能靠目录存在与否猜测完成状态。
- 如果新策略在哨兵集上劣化，回退当前策略批次，不回退仓库稳定化和证据基础设施。

## 10. 成功标准

方案 2 完成时应满足：

- 仓库具有唯一受审、可合并的实现基线；
- 标准测试命令在干净环境可直接运行；
- 工具链、配置、预算和门禁全部进入 RunSpec；
- 搜索、验收和资源预算语义分离；
- b15 的不同模式取舍清楚，b17 不再被软运行时阈值制造假失败；
- 核心模块职责明确，兼容接口稳定；
- 哨兵和全量实验均可由 manifest 重放；
- 所有 accepted patch 具有 SEC 和必要质量证据；
- 论文数字能追溯到 run ID、配置哈希、工具链和 commit；
- 其他智能体能够在不读取全部历史会话的情况下，根据任务包安全推进。

## 11. 下一步边界

本设计批准并提交后，下一步只为 Phase 0–1 编写详细实施计划。Phase 2–5 暂不展开成逐文件实现步骤，待前置门禁通过后分别规划，避免因当前事实变化导致远期计划失真。
