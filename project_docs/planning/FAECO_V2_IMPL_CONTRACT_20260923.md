# FAECO-v2 实现接口冻结（G2 / G3 / G4）

> 日期：2026-09-23
> 定位：本文档是**施工前最后一道 implementation gate**。它不引入任何新机制，只把 `FAECO_V2_TECH_DESIGN_20260923.md`（r2）里已经冻结的方案写成**代码级接口规范**。
> 约束：**不修改论文**。论文改动在 L1/L2/L3 全部落地后一次性执行。
> 参考：`FAECO_V2_TECH_DESIGN_20260923.md`（r2，方案本体）、`FAECO_V2_DESIGN_PLAN_20260923.md`（路线图）。

---

## 0. 当前状态与推进顺序

**状态**：设计冻结，进入实现准备。G2/G3/G4 为最后 implementation gate——**本文件即该 gate 的规格**，经确认后视为冻结，随即开始 0a。

**已冻结、不再讨论**（本文件不再重新论证）：

| 项 | 取值 |
|---|---|
| 状态所有权 | `SearchState` 唯一状态所有者（路径 B） |
| EMA 更新 | 只允许加性 |
| 参数档位 | legacy 与 adaptive 两套 |
| F5 | 独立门控 |
| S 变体 | 三种 resyn |
| F3-S 阈值 | 1.20 / 1.50 |
| 验证链 | CEC-1 / CEC-2 |
| ΔDepth | 两层采集 |
| S 抽取/graft | 状态机已定（r2 §5） |
| 实验 | Mixed-Fixed / Mixed-Random / Adaptive 三臂 |
| 搜索效率指标 | $B(k)$ |

**推进顺序（冻结）**：

$$\boxed{\ \text{G2/G3/G4 接口冻结}\ \rightarrow\ \text{0a 状态架构迁移}\ \rightarrow\ \text{legacy regression}\ \rightarrow\ \text{L2 Adaptive}\ \rightarrow\ \text{L3 S}\ }$$

**0a 的硬约束**：0a 是正式动工，但**第一阶段不得改变算法行为**。目标不是更好的 WNS，而是先证明

$$\boxed{\ \text{新 SearchState 架构}\ \equiv\ \text{旧 FAECO 行为}\ }$$

即**候选顺序、F1–F6 序列、每轮权重、接受补丁、最终 WNS 全部一致**（判据见 §5）。该 gate 通过后才打开 $\rho=0.5$；L2 稳定后接 S。

**不挡施工的挂起项**：OI-010（§4.2 ISCAS89 报告口径）——只影响论文改写，不影响实现。

---

## 1. 代码锚点与命名对齐（写代码前逐字核对）

### 1.1 权重字段 ↔ 记号

`RefinementWeights`（`code/src/rseco/refinement.py:8–17`）的**实际字段名**与本文记号：

| 记号 | 代码字段 | 初值 |
|---|---|---|
| $\lambda_b$ | `boundary_penalty` | 1.0 |
| $\lambda_s$ | `size_penalty` | 1.0 |
| $\lambda_c$ | `critical_coverage_reward` | 1.0 |
| $\lambda_v$ | `verification_cost_penalty` | 1.0 |
| $\lambda_f$ | `equivalence_stability_reward` | 1.0 |
| $M_{\text{cone}}$ | `max_cone_gates` | 1000 |

> **路径 B 的字段迁移**：$M_{\text{cone}}$ **不再属于** `RefinementWeights`，改为 `SearchState.cone_limit`。`flow.py:328` 现在是 `max_gates = max(1, int(getattr(weights, 'max_cone_gates', 1000)))`，迁移后改为读取 `state.cone_limit`。`RefinementWeights` 只保留 5 个 $\lambda$。
> 过渡期兼容：0a 期间可以保留 `max_cone_gates` 作为 `cone_limit` 的镜像只读属性，避免一次改动过大；legacy regression 通过后再删除。

### 1.2 失败类型 ↔ 记号

`FailureType`（`code/src/rseco/failures.py:9–15`）：

| 记号 | 枚举值 |
|---|---|
| F1 | `F1_equivalence_failure`（`EQUIVALENCE`） |
| F2 | `F2_boundary_invalid`（`BOUNDARY_INVALID`） |
| F3 | `F3_patch_too_large`（`PATCH_TOO_LARGE`） |
| F4 | `F4_timing_gain_insufficient`（`TIMING_GAIN_INSUFFICIENT`） |
| F5 | `F5_verification_too_expensive`（`VERIFICATION_TOO_EXPENSIVE`） |
| F6 | `F6_physical_load_failure`（`PHYSICAL_LOAD_FAILURE`） |

### 1.3 各权重在 cost 里的**实际作用面**（决定 clip 区间）

`cut.py:195–199` 的实际公式：

$$\text{cost}(g)=\max\!\left(0.05,\ \frac{1+\dfrac{\lambda_b}{1+d(g)}+\mathbb 1[r{\in}\mathcal R]\cdot\lambda_f\cdot 0.1\cdot \mathrm{fanout}(g)+\lambda_s\dfrac{s_g^2}{\sum s^2}+\lambda_v\cdot 0.01\cdot n}{1+\mathbb 1[r{\in}\mathcal R]\cdot\lambda_c\dfrac{d(g)}{d_{\max}}}\right)$$

| 权重 | 作用面 | 对**排序**的影响 | clip 区间 | 依据 |
|---|---|---|---|---|
| $\lambda_b$ | $\lambda_b/(1+d)$ | 强（随深度衰减） | $[1,8]$ | 直接改变门代价排序 |
| $\lambda_s$ | $\lambda_s\,s_g^2/\sum s^2$ | 强（随锥规模平方） | $[1,8]$ | 同上 |
| $\lambda_f$ | $\lambda_f\cdot0.1\cdot\mathrm{fanout}$ | 强（随扇出线性） | $[1,8]$ | 同上 |
| $\lambda_c$ | 分母 $1+\lambda_c d/d_{\max}$ | 强（最深门最多便宜 $1+\lambda_c$ 倍） | $[0,2]$ | 给到 8 则最深门便宜 9 倍，排序被单项垄断 |
| $\lambda_v$ | $\lambda_v\cdot0.01\cdot n$（$n$ 为锥内门数） | **几乎无**（锥内**常数**，只影响 $0.05$ 地板） | $[1,8]$（低风险） | $n$ 与门无关，是加性常数 |

> **两条应写进代码注释的结论**：① $\lambda_v$ 在现行 cost 里是**锥内常数**，只通过 `max(0.05, ·)` 地板生效——这解释了为什么 F5 的**有效杠杆是 `cone_limit` 减半而不是 $\lambda_v$**，r2 §3.5 把 F5 做成独立门控是正确的。② $\lambda_c$ 是唯一以**分母**进入的权重，因此必须单独设 clip，不能与加性权重同区间。

---

## 2. G2：feedback-off / reject / rollback 各更新哪些状态

### 2.1 状态字段总表（迁移后）

```text
SearchState
├── # --- 网表与事务 ---
├── current_netlist_text        : str
├── netlist_epoch               : int        # 新增：仅"接受提交"时 +1
├── accepted_patches            : list[dict]
├── _snapshots                  : list[dict] # rollback 前态
├── # --- 测量快照 ---
├── current_wns / current_tns / current_min_slack
├── critical_endpoints / critical_instances
├── current_cone_gates          : list[str]
├── # --- 搜索过程状态（新增，路径 B 的核心）---
├── refinement_weights          : RefinementWeights   # λ，纯参数
├── failure_feedback            : FailureFeedbackState # ema / count / last_failure_round
├── cone_limit                  : int                  # M_cone（原 weights.max_cone_gates）
├── round_id                    : int                  # 每轮 +1（含未接受轮）
├── # --- 记账与审计 ---
├── failure_history             : list[dict]
├── tested_candidate_hashes     : set[str]
├── budget                      : dict
└── stop_reason                 : str | None
```

```python
@dataclass(frozen=True)
class FailureFeedbackState:
    ema: dict[FailureType, float]
    count: dict[FailureType, int]
    last_failure_round: dict[FailureType, int]
    recent_f5_rounds: tuple[int, ...]   # 实现时新增：F5 连续性门控需要"最近 W 轮内触发轮数"
```

### 2.2 三个事件的更新契约（**本节的表即实现依据**）

**图例**：`↗` 更新 · `—` 不变 · `⤺` 回滚

| 字段 | feedback-off | reject（候选被拒） | rollback |
|---|---|---|---|
| `current_netlist_text` | — | — | ⤺ 恢复快照 |
| **`netlist_epoch`** | — | —（仅接受时 +1） | **⤺ −1** |
| `accepted_patches` | — | — | ⤺ `pop()` |
| `_snapshots` | — | — | ⤺ `pop()` |
| `current_wns/tns/min_slack` | — | — | ⤺ 恢复 |
| `critical_endpoints/instances` | — | — | ⤺ 恢复 |
| `current_cone_gates` | — | — | ⤺ 恢复 |
| **`refinement_weights`** | **—** | **↗ 仅当 feedback-on 且失败可归因 F1–F6** | **⤺ 恢复** |
| **`failure_feedback`** | **—** | **↗ 同上条件** | **⤺ 恢复** |
| **`cone_limit`** | **—** | **↗ 仅当 F5 门控成立** | **⤺ 恢复** |
| `round_id` | ↗ | ↗ | **—（不回滚）** |
| `failure_history` | ↗ 追加 | ↗ 追加 | — 追加撤销标记 |
| `tested_candidate_hashes` | ↗ | ↗ | **—（不回滚）** |
| `budget` | ↗ | ↗ | **—（不回滚）** |
| `stop_reason` | 视终止条件 | — | — |

### 2.3 三条必须写进代码的裁决

**裁决 1（feedback-off 关的是"反馈→参数"这条边，不是测量）**

`enable_feedback=False` 时：
- ✅ **照做**：失败分类（`failures` 集仍被填充）、`failure_history` 记录、`tested_candidate_hashes` 标记、`budget` 记账、`round_id` 递增。
- ❌ **不做**：`refinement_weights`、`failure_feedback`、`cone_limit` 三者一律不变。

依据：现行 `refinement_loop.py:81` 已经是这个语义（`decision = refine_weights(...) if enable_feedback else None`，而 `:95` 仍写 `failures`）。**保持它**，这样 OI-012 的整改才是"换配置"而非"改语义"。

**裁决 2（rollback 回滚"决策状态"，不回滚"审计与预算状态"）**

- ⤺ **回滚**：`netlist_epoch`、`refinement_weights`、`failure_feedback`、`cone_limit` + `accept_patch` 已定义的 7 个事务/测量字段。
- — **不回滚**：`tested_candidate_hashes`（"已测过"是不可逆事实，若回滚会导致同一候选被反复重测，反而浪费预算）、`budget`（已消耗的 STA/工具次数是物理事实）、`failure_history`（审计日志只追加）。

理由：若回滚 $\lambda$ 与 EMA 但保留 `tested_candidate_hashes`，语义是"**撤销决策、保留记忆**"——这正是 ECO 回滚想要的行为（回到旧网表，但不重复已知无效的候选）。若不回滚 $\lambda$/EMA，则回滚后权重与网表不再对应同一历史，后续 `replay` 无法复现——即用户指出的"语义不自洽"。

`failure_history` 中被回滚轮次的事件**必须打标**：`invalidated_by_rollback=True`，统计时可排除。

**裁决 3（接受轮不推进 EMA）**

接受意味着该轮没有需要反馈的失败集合；现行 loop 在 `success` 分支**先 return 再 refine**（`refinement_loop.py:64–80`）。保持该行为：**accept → 不调用 `update_feedback`**。

### 2.4 事件伪代码（可直接翻译成实现）

```python
def on_reject(state, candidate_key, failures, w_stage_tags, runtime_s):
    state.round_id += 1
    state.failure_history.append({... "stage_tags": w_stage_tags, "failures": [...]})
    state.tested_candidate_hashes.add(candidate_key)          # 含 netlist_epoch，见 §3.4

    attributable, w_tags = split_attribution(failures, w_stage_tags)   # G4 过滤，见 §4.3
    if state.config.enable_feedback and attributable:
        state.failure_feedback, state.refinement_weights, new_limit = update_feedback(
            state.failure_feedback, state.refinement_weights,
            attributable, state.cone_limit, state.config.feedback, state.round_id,
        )
        state.cone_limit = new_limit
    # 事务与测量字段一律不动


def on_accept(state, patch_id, candidate_text, **meas):
    record = state.accept_patch(patch_id, candidate_text, **meas)   # 现有实现
    state.netlist_epoch += 1                                        # 与 accepted_patches 同长
    state.round_id    += 1
    # 不调用 update_feedback（裁决 3）
    return record


def on_rollback(state):
    if not state.rollback():        # 现有实现：恢复事务与测量字段
        return False
    n = len(state.accepted_patches)
    state.netlist_epoch = n                                     # 不变式：epoch == len(accepted)
    state.refinement_weights, state.failure_feedback, state.cone_limit = \
        state._decision_snapshots.pop()                         # 新增：决策状态快照
    _mark_invalidated(state.failure_history, after_round=state.round_id)
    return True
```

> 实现细节：`_snapshots` 目前只存事务/测量字段（`refinement_loop.py:139–147`）。G2 要求**同一次 `accept_patch` 内同时压入决策状态**（$\lambda$、EMA、`cone_limit`、`netlist_epoch`），两者必须原子——压栈在同一处、弹出在同一处，不允许分成两次。

### 2.5 必须写的单测（G2）

| 单测 | 断言 |
|---|---|
| feedback-off 冻结 | 20 轮全拒 + `enable_feedback=False` → $\lambda$、EMA、`cone_limit` **逐轮逐位不变**；`failure_history` 长度 = 轮数 |
| reject 不动作网表 | 全拒路径下 `netlist_epoch == 0`、`accepted_patches == []`、`current_netlist_text` 与初始相同 |
| rollback 原子性 | 接受 2 个后 rollback → 事务/测量/λ/EMA/`cone_limit` 全部回到接受前；`allowed`：`round_id`/`budget`/`tested_*` 不回滚 |
| rollback 空栈 | 无 `_snapshots` 时返回 `False` 且不抛异常、不改变任何字段 |
| 不变式 | 任意时刻 `netlist_epoch == len(accepted_patches)`；`round_id >= netlist_epoch` |
| 接受轮不推 EMA | 接受后 EMA 与接受前逐位相同 |
| 回滚后 replay 一致 | `replay(initial, accepted_patches)` 的输出 hash == `current_netlist_hash` |

---

## 3. G3：Checkpoint 契约、`netlist_epoch`、恢复一致性

### 3.1 `netlist_epoch` 定义

- **含义**：网表版本计次。**仅在接受提交时 +1**。
- **初值**：0（等于初始网表）。
- **不变式**：`netlist_epoch == len(accepted_patches)`（每次接受/回滚后必须成立）。
- **与 `round_id` 的区别**：`round_id` 每轮 +1（含全拒轮），`netlist_epoch` 只在网表真正改变时 +1。两者不可互换。

**用途 1 — 候选过期（stale candidate invalidation 的形式化）**

$$c \text{ 作废}\iff c.\text{epoch\_at\_generation} < \text{state.netlist\_epoch}$$

作废候选**不评估、不做 STA**，记 `W_STALE_CANDIDATE`，**不计入 F1–F6、不进入 EMA**（§4）。这对应 r2 与论文 Algorithm 1 的"该轮提交后基于旧基准的其余候选作废"。

**用途 2 — 去重键（这是一个必须补的实现缺口）**

现有 `candidate_hash`（`refinement_loop.py:63–73`）只含 `gates`/`boundary_inputs`/`boundary_outputs`/`action`，**不含基准网表**。同一个割窗口在不同 epoch 上是不同候选，仅按 `candidate_hash` 去重会把合法候选误判为"已测"。故：

$$\boxed{\ \text{candidate\_key}=\mathrm{sha256}\big(\text{netlist\_hash\_at\_generation}\ \Vert\ \text{candidate\_hash}\big)\ }$$

`tested_candidate_hashes` 存 `candidate_key`（与 §2.4 伪代码一致）。

### 3.2 Checkpoint 字段清单（全量，缺一不可恢复）

| 组 | 字段 | 现有 `to_dict()` 是否已含 | 备注 |
|---|---|---|---|
| 元信息 | `schema_version`, `cell`/`circuit`, `config_hash`, `git_sha`, `toolchain_versions`, `created_at` | ❌ | 新增 |
| 初始条件 | `initial_netlist_text`（或 `initial_netlist_hash` + 路径） | ❌ | 新增，`replay` 必需 |
| 网表事务 | `current_netlist_text`, `current_netlist_hash` | ✅ | — |
| | `netlist_epoch` | ❌ | **新增** |
| | `accepted_patches` | ✅ | 含 `netlist_text` 链 |
| | `_snapshots` | ❌ | **新增**（见 §3.3 瘦身方案） |
| 测量 | `current_wns/tns/min_slack` | ✅ | — |
| | `critical_endpoints`, `critical_instances` | ✅ | — |
| | `current_cone_gates` | ✅ | — |
| 搜索过程状态 | `refinement_weights` | ❌ | **新增**（5 个 $\lambda$） |
| | `failure_feedback`（`ema`/`count`/`last_failure_round`） | ❌ | **新增** |
| | `cone_limit` | ❌ | **新增**（不再走 weights） |
| | `round_id` | ❌ | **新增** |
| 记账与审计 | `failure_history` | ✅ | — |
| | `tested_candidate_hashes` | ✅ | 排序后存，键为 §3.1 的 `candidate_key` |
| | `budget` | ✅（已过滤 `_` 前缀键） | `_deadline_monotonic` 有意不入盘 |
| | `stop_reason` | ✅ | — |
| 有效配置 | `enable_feedback`, `feedback.rho/eta_add/eta_c/clip`, `strategies`, `init_weights`, `random_order`, `seed` | ❌ | **新增** —— 直接补 OI-012 的缺口 |

> **`_snapshots` 瘦身**：快照里的 `current_netlist_text`（整份网表）不必入盘——它可由 `initial_netlist_text` + `accepted_patches[:i]` 通过 `replay` 重建。故 checkpoint 中 `_snapshots[i]` 只存**标量 + hash**：
> `{epoch, netlist_hash, wns, tns, min_slack, critical_endpoints, critical_instances, cone_gates, refinement_weights, failure_feedback, cone_limit}`。
> 恢复时用 `replay` 重建每层网表文本，并**逐一校验 hash**。

### 3.3 恢复一致性（restore）契约

```text
restore(checkpoint) -> SearchState 必须满足：
R1  校验 schema_version 与 config_hash；不匹配 → 拒绝恢复（不静默降级）
R2  用 initial_netlist_text + accepted_patches 做 replay，逐条校验
      base_netlist_hash == hash(前一状态)，任一条不符 → 抛 "not a contiguous replay"
R3  replay 结果 hash == checkpoint.current_netlist_hash，否则拒绝
R4  netlist_epoch == len(accepted_patches)（不变式），否则拒绝
R5  每个 _snapshots[i].netlist_hash 与 replay 到第 i 步的 hash 相符，否则拒绝
R6  恢复后继续运行，必须与"不中断运行"逐项等价（§5 的同一判据）
```

**明确不作要求的**：跨工具链版本恢复、跨 cell 恢复、跨 `config_hash` 恢复——一律拒绝并报错，不做兼容层。

### 3.4 落盘格式

- 单一 JSON 文件 `state_checkpoint.json`，UTF-8，键排序（`sort_keys=True`）以保证**字节级确定性**。
- 文件名带 epoch：`state_checkpoint_e{netlist_epoch:03d}_r{round_id:03d}.json`，便于"最近一次成功检查点"定位。
- 与实验产物同目录归档，并在 `run_config.json`（§4.4）中登记 checkpoint 路径。

### 3.5 必须写的单测（G3）

| 单测 | 断言 |
|---|---|
| 往返一致 | `restore(to_dict(state))` 后所有字段逐位相等 |
| 确定性 | 同一 `state` 连续两次 `to_dict()` → 字节相同 |
| 链断裂拒绝 | 篡改 `accepted_patches[i].netlist_text` → restore 抛 `not a contiguous replay` |
| epoch 不变式 | 构造 `netlist_epoch != len(accepted_patches)` 的 checkpoint → restore 拒绝 |
| 快照校验 | 篡改 `_snapshots[i].netlist_hash` → restore 拒绝 |
| **中断等价** | 跑 N 轮；另跑 N/2 轮→检查点→restore→继续 N/2 轮；两者候选顺序/权重/接受补丁/最终 WNS 逐项相同 |
| 配置守卫 | 改 `config_hash` → restore 拒绝 |

---

## 4. G4：`W_*` 流水线结果 → F1–F6 的映射

### 4.1 核心原则：两层分离，两层不同命运

```text
W_* 层（工具 / 实现 / 基础设施）
    ├── 只进 failure_history 与统计报表
    ├── 不进 EMA、不改权重、不改 cone_limit
    └── 目的：不让 ABC 报错、抽取 bug、超时这类噪声抬高 λ

F1–F6 层（方法失效模式）
    ├── 唯一有权进入 EMA 与权重更新的一层
    └── 定义域 = "候选在方法意义下失效"
```

**唯一的 Failure-Aware 输入是 F1–F6。** 这是 `Failure-Aware` 这个名字能站住的前提——若 `W_*` 能改权重，则方法失效与工具失效不可区分。

### 4.2 映射表（S 与非 S 统一）

| 来源（流水线阶段） | 标签 | 映射到 `FailureType` | 进 EMA |
|---|---|---|---|
| 抽取不变量违反（r2 §4.2） | `W_EXTRACT_INVARIANT` | — | ❌ |
| ABC 报错 | `W_ABC_ERR` | — | ❌ |
| ABC 超时 | `W_ABC_TIMEOUT` | — | ❌ |
| techmap 产出库外单元 | `W_LIB_OUT_OF_SET` | — | ❌ |
| **CEC-1 失败** | — | **`EQUIVALENCE`（F1）** | ✅ |
| **CEC-2 失败** | `S_TECHMAP_MISMATCH` | —（单独统计） | ❌ |
| **$R_S>1.50$** | —（子类标 `S_window_ratio`） | **`PATCH_TOO_LARGE`（F3）** | ✅ |
| 去重命中 | —（`DROPPED`，**不算失败**） | — | ❌ |
| graft 失败 | `W_GRAFT_ERROR` | — | ❌ |
| 结构自检失败 | `W_STRUCT_ERROR` | — | ❌ |
| 候选过期（§3.1） | `W_STALE_CANDIDATE` | — | ❌ |
| 预算耗尽（STA/工具次数） | `W_BUDGET_EXHAUSTED` | — | ❌ |

**测量侧（`classify_failures`，`failures.py:25–51`）—— 保持不变**：

| `FailureType` | 触发条件（现行） |
|---|---|
| F1 | `equivalence_passed is False` |
| F2 | `boundary_closed is False` |
| F3 | `change_ratio(patch_size, original_gate_count) > 0.15` |
| F4 | `logic_level_reduction < 1` |
| F5 | `verification_runtime_s > 60.0` |
| F6 | 物理门控路径产生（当前 `code/` 不产 $\lambda_s$ 增量，见 OI-008） |

### 4.3 三条必须写进代码的裁决

**裁决 1 — 短路优先，禁止双重归因。** 若在某个 `W_*` 阶段就已拒绝（如 `W_EXTRACT_INVARIANT`、`W_ABC_TIMEOUT`、`W_GRAFT_ERROR`），则该候选**不再进入 `classify_failures`**，因此不会同时产生 F1–F6。状态机（r2 §5.3）的顺序即是短路顺序。

**裁决 2 — F3-S 是 F3 的**子类**，共用 EMA 通道。**
$R_S>1.50$ 在 EMA 中**计入 `FailureType.PATCH_TOO_LARGE`**（与 R/G/B 的全局比例失败共用一条通道），但在 `failure_history` 中带 `subtype="S_window_ratio"` 以便分开统计分布。

理由：① 语义上二者都是"补丁过大"，共用 $\lambda_s$ 合理（$\lambda_s$ 惩罚锥规模，对 S 同样适用）；② **避免在论文的 F1–F6 表里凭空增加第 7 个通道**——S 的引入不应改写已发表的失效模式分类。

**裁决 3 — 统计口径强制分离。** 所有报表必须**分两张表**：F1–F6 分布（方法）与 `W_*` 分布（基础设施）。禁止合并成一个"失败总数"。`W_*` 占比本身是工程质量指标（例如 `W_GRAFT_ERROR` 长期不为 0 就说明 S 实现有问题），应单独监控。

实现接口：

```python
_ATTRIBUTABLE = frozenset({
    FailureType.EQUIVALENCE, FailureType.BOUNDARY_INVALID,
    FailureType.PATCH_TOO_LARGE, FailureType.TIMING_GAIN_INSUFFICIENT,
    FailureType.VERIFICATION_TOO_EXPENSIVE, FailureType.PHYSICAL_LOAD_FAILURE,
})

def split_attribution(failures: set[FailureType], stage_tags: list[str]) -> tuple[set[FailureType], list[str]]:
    """返回 (可归因失败集, W_* 标签)。只有前者允许进入 EMA。"""
    return {f for f in failures if f in _ATTRIBUTABLE}, list(stage_tags)
```

### 4.4 必须新增的采集字段（与 G3 的 checkpoint 呼应）

| 字段 | 用途 |
|---|---|
| `best_wns_curve`：$B(k)=\max_{i\le k}\Delta\mathrm{WNS}_i$ | 搜索效率主指标 |
| `n_sta_to_first_improvement` | 达到首次改善所需 STA 次数 |
| `wns_gain_per_100_sta` | 单位预算产出 |
| `failure_ema_trace` / `weights_trace` / `cone_limit_trace` | 可解释性与审稿可核 |
| `attribution_table`：`{event_id: {"stage_tag": ..., "failure": ..., "subtype": ...}}` | 支持 §4.3 裁决 3 的两表分离 |
| `run_config.json`：argv + git SHA + 工具链版本 + **`enable_feedback`/`strategies`/`init_weights`/`random_order`/`seed`** | **OI-012 的整改项**（此前一个都没记） |

### 4.5 必须写的单测（G4）

| 单测 | 断言 |
|---|---|
| `W_*` 不改权重 | 构造仅含 `W_ABC_TIMEOUT` 的事件序列跑 20 轮 → $\lambda$、EMA、`cone_limit` 与 0 轮相同 |
| 短路不双归因 | `W_EXTRACT_INVARIANT` 触发时，`failure_history` 中该候选**无** F1–F6 记录 |
| CEC-2 归因 | `S_TECHMAP_MISMATCH` 出现时 `EQUIVALENCE` **不**出现在同一事件 |
| F3-S 通道 | $R_S=1.6$ → EMA 的 `PATCH_TOO_LARGE` 计数 +1，且 `subtype=="S_window_ratio"` |
| 两表分离 | 报表输出含两个独立分布；`W_*` 总数不进入 F1–F6 合计 |
| 过期候选 | epoch 不匹配的候选 → `W_STALE_CANDIDATE`，EMA 不变、无 STA 调用 |

---

## 5. 0a 行为等价 gate（legacy regression）

### 5.1 等价判据（逐电路，**六项全等**）

| # | 判据 | 比较对象 |
|---|---|---|
| E1 | **候选顺序** | 每轮候选的 `candidate_key` 序列（按生成序）逐项相同 |
| E2 | **F1–F6 序列** | `failure_history` 的 `(round_id, 序号, failure_type)` 序列逐项相同 |
| E3 | **每轮权重** | `refinement_weights` 五个字段逐轮逐位相同；`cone_limit` 逐轮相同 |
| E4 | **接受补丁** | `patch_id` 序列 + 每条 `base_netlist_hash` / `netlist_hash` 相同 |
| E5 | **最终 WNS** | `current_wns` / `current_tns` / `current_min_slack` 相同 |
| E6 | **STA 调用次数** | `budget["sta_used"]` 相同 |

**实现方式**：0a 直接把 `update_feedback` 以 **legacy 档**（$\rho=0$、$\eta=1$、clip off）接入，由 r2 §3.3 性质 2 保证与现行 `+=1.0` 逐位等价——即"**架构换新、行为不变**"通过构造保证，再由本 gate 实测验证。

### 5.2 执行与判据

- **被比对象**：~~旧实现 = `run_hybrid_repair.py`~~ → **见 §8.3 的修正**：行为基线 = codex 谱系实现（产出论文主实验数字的那份代码），过程基线 = main 的 `code/` 布局 + main 独有功能；0a 的 E1–E6 是**移植不变性**检验。
- **哨兵电路**：3 个，取"便宜 + 中等 + 最难"三点以覆盖不同失败模式分布：
  - `s382`（ISCAS89，最便宜，能跑多轮）
  - `b03`（ITC-99，中等规模，多轮累积）
  - `b06`（ITC-99，历史最难，F4/F5 密集；也是后续 S 的证伪电路）
  若 `b06` 因 60 s 预算边界出现工具抖动，**换 `b02` 而不是调参**。
- **运行条件**：固定 seed、固定工具链、`--workers 1`（禁并行以消除调度顺序差异）、`--rounds 20 --period 0.5`。
- **产物**：`equivalence_report.json`（逐电路六项对照 + 首个不一致点的上下文）。

### 5.3 不通过时的处置（先归因，不调参）

任一项不一致 → **gate 不通过**，按 AGENTS §4 逐层排查：

```text
① 复现：能否稳定复现该不一致
② 校验输入：两边的输入网表 / 割 / 候选列表 hash 是否相同
③ 检查实现：差异是否来自移植（字段迁移遗漏、快照时机、去重键变化）
④ 对照设定：是否无意中改了口径（例如 candidate_key 变了导致 STA 次数变化）
```

**禁止**用调参、改 seed、缩小轮数来让报告变绿。若差异确认为"**实现可修**"，修完复跑；若确认为"**设定需改**"（即新架构语义确实不同），则**回到 G2/G3 修改契约**，并如实记录差异原因——不得在报告里隐去。

### 5.4 0a 的明确非目标

- ❌ 不追求更好的 WNS；
- ❌ 不启用 $\rho=0.5$；
- ❌ 不接入 S；
- ❌ 不改 `max_patch_ratio`、不改 $B(k)$ 之外的采集字段。

0a 唯一的交付物 = **E1–E6 全等的 `equivalence_report.json`** + 264 项测试全绿。

---

## 6. 阶段门与后续

| 阶段 | 内容 | 通过条件（gate） | 不通过怎么办 |
|---|---|---|---|
| **G2/G3/G4** | 本文件 | 三节单测清单全部实现且绿 | 补规格，不进 0a |
| **0a** | `SearchState` 架构迁移（legacy 档接入） | §5.1 六项全等 + 264 测试全绿 | 按 §5.3 归因，禁用调参 |
| **legacy regression** | 与 0a 同一 gate，扩到全 8 电路 | 8/8 电路六项全等 | 同上 |
| **L2 Adaptive** | 打开 $\rho=0.5$、$\eta_{\text{add}}=0.5$、$\eta_c=0.25$、clip on | 三臂判读（r2 §6.4）：$B(k)$ 不劣且 $N_{\text{STA-to-first}}$ 显著更低，或如实报告"无独立贡献" | 按判读表改写核心贡献 |
| **L3 S** | 接入 r2 §5 状态机 | ① §5.5 单测全绿 ② 局部 CEC 通过 ③ ≥1 个 $\Delta L<0$ 且 $\Delta\mathrm{WNS}>0$ 的接受候选 | 按 r2 §7 分级结论如实报告 |

---

## 7. 遗留与风险

| 项 | 状态 |
|---|---|
| OI-010（§4.2 ISCAS89 报告口径） | ⚠️ 挂起，不挡施工（只影响论文） |
| OI-008 遗留（F6 是否恢复 $\lambda_s$ 增量） | ⚠️ G4 保持现状：F6 不产 $\lambda_s$；若要恢复须先补物理门控采集 |
| `candidate_hash` 不含基准网表（§3.1 用途 2） | ⚠️ **必须在 0a 修**，否则多轮去重会误杀候选 |
| `_snapshots` 与决策状态必须原子压栈（§2.4） | ⚠️ 实现时最易漏，已列入 G2 单测 |
| `to_dict()` 现不含 `_snapshots`（§3.2） | ⚠️ 实现时最易漏，已列入 G3 单测 |
| 8 电路统计强度弱 | ⚠️ 逐电路配对差值，不做显著性断言（r2 §6.4） |
| `R_hard=1.5` 偏宽松 | ⚠️ 第一版跑完看分布再收紧 |

---

## 8. 0a 迁移方案（2026-09-23 侦察结论）

> 本节是 0a 动工前的实地核查结果，全部可复核（命令与输出见 `LOGS.md` LOG-20260923-11）。

### 8.1 五条决定性事实

| # | 事实 | 影响 |
|---|---|---|
| 1 | **codex 分支是 09-12 框架迁移*之前*的布局**：根目录为 `src/`、`scripts/`、`tests/`、`benchmarks/`，**没有 `code/`** | **"反向迁移布局"会撤销整个 09-12 迁移，不可行**。路径 B 的正确含义是「采用 codex 的**状态架构**，落在 main 现有布局里」 |
| 2 | merge-base = `b8c3759`（2026-08-13）；main 分叉后**仅 2 个提交**触及源码：`35fd558`（迁移/路径）、`766b589`（`--no-early-stop` 功能）——**二者都不在 codex** | main 有 codex 缺少的**功能**，不能整文件覆盖 |
| 3 | `code/src/rseco` 11 个差异文件中 **10 个与分叉点逐字节相同**；唯一有内容差异的 `flow.py` 差的 43 行正是 `766b589` 的功能（不是路径修补） | **codex 版本是严格超集**，可作迁移基线 |
| 4 | `code/scripts/run_hybrid_repair.py` 两侧**逐字节相同**（该运行器从未使用 `SearchState`） | 0a **不能**通过它来验证状态架构 |
| 5 | `run_outerloop_real_wns.py` 是**双向分叉**：codex 多出预算参数（`--max-patches`/`--sta-budget`/`--formal-budget`/`--wall-timeout-s`）与 SEC/等价/边界 checker 构造器 + import shim；main 多出 `--early-stop`/`--no-early-stop` 且**默认 early-stop 开启** | 必须**三方合并**，不能取任一侧 |

**差异规模（codex 相对 main，新增/删除）**：`real_wns.py` +1522/−65 · `flow.py` +350/−56 · `replacement.py` +304/−1 · `refinement_loop.py` +248/−7 · `cut.py` +155/−0 · `failures.py` +86/−1 · `equivalence.py` +85/−15 · `yosys_abc.py` +73/−13 · `logic_rewrite.py` +58/−0 · `netlist.py` +21/−1 · `refinement.py` +5/−1。

### 8.2 迁移策略：能力合并，不整文件覆盖

1. **仅 codex 有新增**的文件（`refinement_loop.py`/`real_wns.py`/`cut.py`/`failures.py`/`replacement.py`/`equivalence.py`/`logic_rewrite.py`/`yosys_abc.py`/`netlist.py`/`refinement.py`）→ 以 codex 内容为基，落在 `code/` 布局。
2. **双向分叉**文件（`flow.py`、`run_outerloop_real_wns.py`）→ 逐块合并，**必须保留 main 的 `--no-early-stop`**。
3. **新增文件**（`feedback.py` 及新测试）→ 直接落在 main 布局；codex 无同名文件，零冲突。
4. 合并后必须重新执行 §3.3 的 `R1–R6` 与 G2/G3 单测，再进 §5 的等价 gate。

### 8.3 等价基线的修正（对 §5.2 的修订）

侦察前 §5.2 写的是"旧实现 = `run_hybrid_repair.py`"。事实 4 表明该运行器与状态架构无关，故修正为：

| 角色 | 定义 |
|---|---|
| **行为基线** | **codex 谱系实现**的行为——它就是产出论文主实验数字的那份代码 |
| **过程基线** | main 的 `code/` 布局 + main 独有功能（`--no-early-stop`） |
| **0a 的检验性质** | **移植不变性**：在 main 布局上跑出的结果，与在 codex 分支上跑出的结果 **E1–E6 六项全等** |

**运行条件必须显式对齐**以消除默认值差异：两侧都**显式传 `--early-stop`**、固定 seed、`--workers 1`、`--rounds 20 --period 0.5`。

### 8.4 `--early-stop` 默认值差异（已处置，无需裁决）

main 默认 `early_stop=True`（为兼容 20260826 批次而设），codex 默认 `False`。**处置**：不改任何一侧的默认值，改为**在等价实验中显式传参**。这样既不破坏 main 的向后兼容，也消除比较歧义。

### 8.5 分步计划与进度

| 步骤 | 内容 | 状态 |
|---|---|---|
| 1 | 0a 侦察与迁移方案（本 §8） | ✅ 完成 |
| 2 | `FailureFeedbackState` + `update_feedback` + `describe_actions` + legacy 退化单测 | ✅ 完成 |
| 3 | `SearchState` 扩展 + checkpoint/恢复一致性 + `candidate_key` + G2/G4 事件契约 | ✅ 完成 |
| 4 | 运行器接入（legacy 档）+ codex 能力合并（§8.2） | ⏭ 待做 |
| 5 | E1–E6 等价报告（`s382`/`b03`/`b06`）+ 全量回归 | ⏭ 待做 |

**步骤 2 交付**：`code/src/rseco/feedback.py`（新模块，与 codex 无冲突）+ `code/tests/test_feedback_legacy_equivalence.py`。
验证：新单测 17 项 / 155 子测试全绿；**全量 281 passed, 4 skipped**（264 基线 + 17 新增，无回归）。

**步骤 3 交付**：`code/src/rseco/search_state.py`（新模块，与 codex 的 `SearchState` 无文件冲突）+ `code/tests/test_search_state.py`（28 项）。
覆盖：G2 三事件契约（feedback-off 冻结参数但照记分类/日志/去重/预算、reject 不动网表、接受轮不推 EMA、rollback 原子恢复决策状态且保留审计与预算、空栈干净返回、链断拒绝、不变式、replay 一致）、候选身份复合键、过期候选只记账、G4 归因分层（`W_*` 20 轮不改权重、短路不双归因、未知 `W_*` 标签报错、`S_TECHMAP_MISMATCH` 分类）、G3 checkpoint（全字段往返、字节确定性、`effective_config` 记录、**中断等价 R6**、文件名带 epoch/round、R1 config 守卫、R3 链校验、R4 epoch 不变式、R5 快照校验、快照数不匹配拒绝）。
验证：新单测 28 项全绿；**全量 309 passed, 4 skipped**（281 基线 + 28 新增，无回归）。

**步骤 3 顺带做的交叉核对**：`stop_reason` 的 8 项取值集合与产物实测一致——`experiments/20260826_*/` 中实际出现的仅 `max_iterations`(26) / `max_patches`(30) / `stagnation`(2)，均已在集合内 ✓。

### 8.6 实施中的契约修正（amendment）

| # | 契约原文 | 实施修正 | 理由 |
|---|---|---|---|
| A1 | §2.4 伪代码在 `on_accept` 与 `on_reject` 内各自 `round_id += 1` | `round_id` 改由 `begin_round()` **每轮推进一次**；accept/reject 不再自增 | 一轮内"既拒绝候选又接受一个"的场景会**重复计数**。伪代码是示意性的，`round_id` 的语义（"这是第几轮"）未变 |
| A2 | §3.1 `candidate_key = sha256(netlist_hash ‖ candidate_hash)` | 实现为 `SearchState.candidate_key()`；`tested_candidate_hashes` 存复合键 | 与契约一致，此处仅记录落点 |
| A3 | §2.2 表的 `tested_*` 在 reject 行为 `↗` | feedback-off 时**仍**标记 | 去重属于"测量事实"，与裁决 1（只关"反馈→参数"这条边）自洽 |

**步骤 2 抓出的两个实现陷阱**（一度写错，由单测发现，已写入代码注释）：

1. **EMA 必须每轮推进**（含未观察轮）。若只在"该失败再次出现"时推进，单次失败只贡献 $(1-\rho)\eta$ 且**永不衰减**——那是"失败率"而非"释放"，与 r2 §3.3 性质 1 冲突。
2. **权重在 EMA 非零期间持续移动**（释放就发生在未观察轮），但**锥门控只在 F5 被观察的轮次评估**，否则一次失败 episode 会通过自己的衰减尾巴反复缩锥。

两条在 $\rho=0$ 时都退化为 legacy（观察轮 `rate=1`、未观察轮 `rate=0`），故逐位等价仍然成立——这一点由「64 个子集穷举 + 20 轮累积」测试钉住。

