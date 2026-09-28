# FAECO-v2 技术设计（r2 冻结版）

> 日期：2026-09-23（r1 → r2：按 11 项裁定冻结）
> 定位：本文档回答"**怎么实现**"；`FAECO_V2_DESIGN_PLAN_20260923.md` 回答"**做哪几件事、什么顺序**"。
> 约束：**不修改论文**。论文改动统一在方案定案后一次性执行。
> 本版新增重点：**§5 S 的窗口抽取 / graft 接口数据结构与状态机**（用户指定为下一步最该设计、也最易实现出错的部分）。

---

## 0. 本版变更摘要（11 项裁定）

| # | 裁定 | 本版动作 |
|---|---|---|
| 1 | **OI-011 选路径 B**：`SearchState` 是唯一运行时状态所有者 | 改写 §2；`RefinementWeights` **只**表示当前搜索代价参数 $\boldsymbol\lambda$，不保存 EMA 历史 |
| 2 | 纯函数性质不靠"把状态塞进 weights"保住 | §2.2 给出 `update_feedback(...)` 纯函数签名 |
| 3 | L2 **只能加性更新**，乘法式 $\lambda(1+\eta r)$ 不成立 | §3.2 明确 `clip(λ + η_j r_j)`，并写明乘法式为何错 |
| 4 | 命名改为 **EMA-smoothed failure feedback** | §3.1 全篇改称，避免"失败率"概念说过头 |
| 5 | 保留 legacy 严格退化测试 | §3.3 单测规格（逐轮逐位相同） |
| 6 | 默认参数不是全局 $\eta=1$ | §3.4 legacy 与 adaptive 两套参数分离 |
| 7 | F5 不并入 EMA；且需**连续性条件** | §3.5 加 $N_{F5,\text{recent}}\ge2$ |
| 8 | F3-S **不用全局比例**，改窗口局部**双阈值** | §4.4 $R_S$ 定义 + $R_{\text{soft}}=1.2/R_{\text{hard}}=1.5$ |
| 9 | CEC-2 必须闭合成 $C_{\text{orig}}\equiv C_{\text{mapped}}$ | §4.5 改写验证链 |
| 10 | S 第一版生成 **3 个 variant** 并去重 | §4.6 |
| 11 | b06 可证伪测试**拆成两个主张**；三臂增加 $B(k)$ 曲线 | §7、§6.3 |

---

## 1. 设计基线（已核实的实现事实）

| 事实 | 位置 | 影响 |
|---|---|---|
| `refine_weights(weights, failures: set[FailureType]) -> RefinementDecision` 是纯函数，每类 `+= 1.0`；`failures` 是 set | `code/src/rseco/refinement.py:28–78` | 每轮每类最多 +1.0；**无跨轮状态** → EMA 必须由外部状态持有 |
| 初始权重全 1.0，`max_cone_gates=1000` | `refinement.py:9–17` | $w^{(0)}$ 统一为全 1，三臂对照成本极低 |
| F5 动作 `max_cone_gates = max(1, max_cone_gates // 2)` | `refinement.py:56–59` | 搜索空间收缩，**不并入 EMA**（§3.5） |
| 权重进入式(2) 的方式不同：$\lambda_b/\lambda_s/\lambda_f$ 加性入 cost；$\lambda_c$ 进分母折扣 $1+\lambda_c\mathbb{1}[v\in\mathcal{R}]\cdot\mathrm{depth}/\mathrm{depth}_{\max}$；$\lambda_v$ 乘 $0.01$ | `cut.py:166–199` | **量纲/作用不同 → clip 与步长必须分类设定** |
| `CutBoundary(method, boundary_inputs, boundary_outputs, internal_nets, gates)`；`patch_size = len(gates)` | `cut.py:11–30` | S 窗口规格的现成载体 |
| `PatchCandidate` 携带 boundary/gates/equivalence_* | `patch.py:8–59` | S 复用同结构 + 新增统计字段 |
| `Netlist.logic_level(signal)` / `logic_levels()` | `netlist.py:37,68` | ΔDepth 采集无需新建能力 |
| `F3` 阈值 `max_patch_ratio=0.15`（相对全局门数） | `failures.py:19–20` | **对 S 不适用**，S 用窗口局部 $R_S$（§4.4） |
| 已有 ABC 基础设施：BLIF 规范化、`RESYN2_BUILTIN_SEQUENCE`、ABC `cec`、`check_mapped_blif_equivalence`、`make_liberty_cells_v.py` | `yosys_abc.py:15–27,103,215,536`；`code/scripts/` | S 的重综合与验证链约 70% 已有，缺**窗口抽取/回填/库约束重映射** |
| codex 分支 `SearchState` 已有 `failure_history`（含 `event_id`/`cut_hash`/`endpoint`/`action_scope`/`observed_value`/`evidence`）、`accept_patch`/`rollback`/`replay`、`current_cone_gates` | `codex/faeco-unified-loop:src/rseco/refinement_loop.py:120–195` | **路径 B 的状态容器现成**（§2） |

---

## 2. 状态所有权与架构裁定（路径 B）

### 2.1 所有权划分

$$\underbrace{\boldsymbol\lambda = (\lambda_b,\lambda_s,\lambda_f,\lambda_v,\lambda_c)}_{\text{当前搜索代价参数 —— 无历史}},\qquad \underbrace{r_{F1},\dots,r_{F6},\ \text{count},\ \text{last\_round}}_{\text{搜索过程状态 —— 有历史}}$$

两者**不是一类东西**：前者是 cost 的系数，后者是过程记忆。因此：

```text
SearchState                        # 唯一运行时状态所有者
├── refinement_weights  : λ        # 纯参数
├── failure_feedback    : FailureFeedbackState
│   ├── ema              : dict[FailureType, float]
│   ├── count            : dict[FailureType, int]
│   └── last_failure_round : dict[FailureType, int]
├── cone_limit          : int      # M_cone（原 max_cone_gates）
├── current_cone_gates  : list[str]
├── round_id            : int
├── accepted_patches    : list[...]   # 已有：patch 日志（含 base/netlist hash 链）
├── best_netlist / best_wns
└── _snapshots          : list[...]   # 已有：rollback 用
```

```python
@dataclass(frozen=True)
class FailureFeedbackState:
    ema: dict[FailureType, float]
    count: dict[FailureType, int]
    last_failure_round: dict[FailureType, int]
```

### 2.2 纯函数依然保留

```python
def update_feedback(
    old_feedback: FailureFeedbackState,
    old_weights: RefinementWeights,
    failures: set[FailureType],
    cone_limit: int,
    config: FeedbackConfig,
    round_id: int,
) -> tuple[FailureFeedbackState, RefinementWeights, int]:
    """纯函数：EMA 推进 + 权重更新 + 锥上限决策。
    返回 (new_feedback, new_weights, new_cone_limit)；不修改任何入参。"""
```

`SearchState` 负责持有与提交返回值；`refine_weights` 退化为 `update_feedback` 的 `legacy` 特例或直接由其内部复用（见 §3.4）。

**为什么这样更干净**：检查点/复现只需序列化 `SearchState`；消融只需换 `FeedbackConfig`；`rollback()` 天然需要回滚的正是这些状态字段。

---

## 3. L2：EMA-smoothed failure feedback

### 3.1 命名

本机制**命名为 EMA-smoothed failure feedback**。它不是"按当前失败率直接设定权重"，而是"把一次失败的惩罚**分若干轮释放**"（§3.3 的性质）。技术设计与代码注释统一用该名。

### 3.2 更新公式（只允许加性）

$$r_j^{(t)} = \rho\, r_j^{(t-1)} + (1-\rho)\,\mathbb{1}\!\left[F_j^{(t)}\right]$$

$$\boxed{\ \lambda_j^{(t+1)} = \mathrm{clip}\!\left(\lambda_j^{(t)} + \eta_j\, r_j^{(t)},\ \lambda_j^{\min},\ \lambda_j^{\max}\right)\ }$$

**明确排除乘法式** $\lambda_j \leftarrow \lambda_j(1+\eta_j r_j)$：取 $(\rho=0,\eta=1)$ 时它给出 $\lambda\to2\lambda$，**不是** `+= 1.0`，无法与 legacy 对齐。r1 文档中"乘法式首步也得 2.0"的说法只在 $\lambda^{(0)}=1$ 的第一步成立，之后立即发散，**已作废**。

### 3.3 两个必须写进代码的性质

**性质 1（孤立失败的释放总量恰为 $\eta$）**：一次孤立失败后不再发生，则

$$\sum_{k\ge0}(1-\rho)\rho^k = 1 \quad\Longrightarrow\quad \text{累计增量} = \eta_j$$

即 **$\rho$ 只控制"惩罚分多少轮释放"，不改变单次失败的总惩罚量**。$\rho=0$ 退化为立即反馈；$\rho=0.5$ 释放序列为 $0.5,\,0.25,\,0.125,\dots$。这是该设计最干净的一点，应写成注释 + 单测。

**性质 2（legacy 严格退化）**：$(\rho=0,\ \eta_j=1,\ \text{clip 关闭})$ 时逐轮逐位等价于现行 `+= 1.0`。

单测规格：

```text
rho=0, eta=1, clip=off
for each round t in 1..N:
    legacy = refine_weights(legacy_w, failures_t)          # 现行实现
    new_w, new_f, _ = update_feedback(f, new_w, failures_t, ...)
    assert new_w == legacy.weights      # 逐位相等，含 λ_c / λ_f / λ_s / λ_v / λ_b
```

必须覆盖：单类单轮、单类连续多轮、同类多轮混合、多类同轮同时触发（验证 set 语义仍为"每类每轮一次"）。

### 3.4 两套参数（互不要求兼容）

```text
legacy（仅用于证明兼容，不用于实验）
    rho = 0 ; eta_add = 1.0 ; eta_c = 1.0 ; clip = off

adaptive default（用于真实实验）
    rho = 0.5
    eta_add = 0.5            # λ_b, λ_s, λ_f, λ_v
    eta_c   = 0.25           # λ_c 单独步长
    clip = on
    λ_b, λ_s, λ_f, λ_v ∈ [1, 8]
    λ_c ∈ [0, 2]
```

**$\eta_c$ 为什么必须更小**：$\lambda_c\in[0,2]$、初值 1，若 $\eta_c=1$ 则一次孤立 F4 就给 $\Delta\lambda_c=1$，$1\to2$ **一次触顶**——自适应立即退化为二值。$\eta_c=0.25$ 需多次持续 F4 才逼近上限。

**明确不要求**"默认参数复现 legacy 结果"——两者是不同机制档位，兼容性只由 §3.3 的性质 2 保证。

### 3.5 F5：独立通道 + 连续性条件

$$M_{\text{cone}} \leftarrow \max\!\left(M_{\min},\ \left\lfloor \gamma\, M_{\text{cone}} \right\rfloor\right)
\quad\text{仅当}\quad
r_{F5}\ge\tau_5\ \ \land\ \ N_{F5,\text{recent}}\ge 2$$

- $\gamma=0.5$ 保留；$\tau_5=0.5$；$M_{\min}$ 继承现行 $1$。
- $N_{F5,\text{recent}}$ 定义为**最近 $W=3$ 轮**内 F5 触发的轮数（或"自上次减半以来的触发轮数"，实现取前者）。
- 理由：一次偶发 timeout 不缩锥；b17 这类大任务第一次 60 s 超时不应立即收缩。

### 3.6 必须新增的采集字段

| 字段 | 定义 | 用途 |
|---|---|---|
| `n_sta_to_first_improvement` | 首次接受前的候选级 STA 次数 | $N_{\text{STA-to-first-improvement}}\downarrow$ |
| **`best_wns_curve`** | $B(k)=\max_{i\le k}\Delta\mathrm{WNS}_i$，$k$ 为 STA 次序 | **搜索效率的主指标**（§6.3） |
| `wns_gain_per_100_sta` | $\Delta\mathrm{WNS}/N_{\text{STA}}\times100$ | 单位预算产出 |
| `failure_ema_trace` / `weights_trace` / `cone_limit_trace` | 每轮轨迹 | 可解释性与审稿可核 |
| `enable_feedback` / `strategies` / `random_order` / `seed` / `init_weights` / `toolchain` | 运行配置 | **OI-012 暴露的缺口，当前一个都没记** |
| `run_config.json`（argv + git SHA + 工具链版本） | 写入实验目录 | 同上 |

---

## 4. L3：S 局部结构重综合候选

### 4.1 形式定义

$$S(C):\ (I_C,O_C,V_C)\to(I_C,O_C,V_C'),\qquad I_C'=I_C,\ O_C'=O_C,\qquad F_{C'}(I_C)=F_C(I_C)$$

### 4.2 实现层不变量（任一违反 → 拒绝，且**不计入 F1**）

$$\text{no dangling input};\quad \text{no dangling output};\quad \text{no multiple driver}$$
$$\text{no sequential cell};\quad \text{no clock/reset/gating cell};\quad \text{boundary net mapping unchanged}$$
$$\text{all mapped cells} \in \text{allowed SKY130 set};\quad \text{no net/instance name collision with the host netlist}$$

### 4.3 重综合链（3 变体）

每个窗口生成**最多 3 个变体**，不做 ABC recipe 大搜索：

$$S_0=\texttt{resyn2},\qquad S_1=\texttt{resyn2;\,resub},\qquad S_2=\texttt{resyn2;\,resub -z}$$

其中 `resyn2` = 现有 `RESYN2_BUILTIN_SEQUENCE`（`balance; rewrite; refactor; balance; rewrite; rewrite -z; balance; refactor -z; rewrite -z; balance`）。去重按**映射后网表的 canonical hash**，跨变体与已测候选一并去重：

$$\{S_0,S_1,S_2\}\xrightarrow{\text{dedup}}\mathcal{S}_C$$

第一版**不再追加其他 ABC recipe**。

### 4.4 F3-S：窗口局部双阈值（取代全局比例）

$$R_S=\frac{N_{\text{patch}}}{N_{\text{window}}}$$

其中 $N$ **明确限定为窗口内部组合标准单元数**，**不含** PI/PO、边界端口、常数节点。判定：

| 区间 | 处理 |
|---|---|
| $R_S\le 1.20$ | 正常候选 |
| $1.20<R_S\le1.50$ | **保留**，附加 size penalty（$\lambda_s$ 项按 $R_S$ 放大） |
| $R_S>1.50$ | 触发 **F3-S** |

$$\boxed{R_{\text{soft}}=1.20,\qquad R_{\text{hard}}=1.50}$$

**为何不能 $R_S>1.2\Rightarrow$ reject**：ABC 重综合 + techmap 后**深度下降而单元数上升是常态**（例：$L:7\to5$ 同时 $N:20\to25$，$R_S=1.25$）——这类候选恰恰是想要的 timing ECO。硬阈值 1.2 会直接误杀。

**明确不使用** `max_patch_ratio_S = 0.5 × 全局门数`（全局比例对整窗重综合无技术意义）。

> 遗留风险：$R_{\text{hard}}=1.5$ 仍偏宽松，会放过一些面积膨胀候选。缓解：每个候选**必须同时报告面积变化**，并依赖软阈值惩罚 + 物理门控；第一版先按 1.2/1.5 跑，观察分布后再收紧。

### 4.5 验证链（CEC-2 闭合整链）

$$\text{Original}\to\text{Resynthesis}\xrightarrow{\text{CEC-1}}\text{Techmap}\xrightarrow{\text{CEC-2}}\text{Graft}\to\text{STA}$$

| 步 | 比较对象 | 判据用途 |
|---|---|---|
| **CEC-1** | $C_{\text{original}}\equiv C_{\text{resyn}}$ | 判断 Boolean restructuring 是否正确 |
| **CEC-2** | $\boxed{C_{\text{original}}\equiv C_{\text{mapped}}}$ | **一次闭合 resynthesis + mapping 整链** |

CEC-2 **不写成** $C_{\text{resyn}}\equiv C_{\text{mapped}}$：传递等价理论上等效，但中间表示转换或接口映射出 bug 时不利于调试归因。实现上 CEC-2 只是对 `original.normalized.blif` 与 `win_mapped` 再跑一次 ABC `cec`（可复用 `check_mapped_blif_equivalence`），成本可忽略。

### 4.6 候选编码

复用 `PatchCandidate`，新增：

```python
cut_method = "structure_resynthesis"
gates      = 重综合后的实例名列表
resynth_stats = {
    "variant": "S0|S1|S2",
    "window_gates_before": int, "window_gates_after": int,   # R_S 的来源
    "aig_nodes_before": int,    "aig_nodes_after": int,
    "depth_before": int,        "depth_after": int,          # 窗口级 ΔL_C
    "abc_sequence": str,
    "cec_pre_map": "pass|fail", "cec_post_map": "pass|fail",
    "area_before_um2": float,   "area_after_um2": float,     # §4.4 遗留风险缓解
    "canonical_hash": str,
}
```

### 4.7 拒绝条件与归因（避免污染 F1）

| 触发 | 归因标签 | 是否计入 F1 |
|---|---|---|
| 抽取不变量违反 | `W_EXTRACT_INVARIANT` | 否 |
| ABC 报错 / 超时 | `W_ABC_ERR` / `W_ABC_TIMEOUT` | 否 |
| **CEC-1 失败** | F1 | **是** |
| techmap 产出库外单元 | `W_LIB_OUT_OF_SET` | 否 |
| **CEC-2 失败** | `S_TECHMAP_MISMATCH` | 否（单独统计） |
| $R_S>1.50$ | F3-S | 是（F3 单独子类） |
| 去重命中 | — | 否（不计失败） |
| graft 失败 / 结构自检失败 | `W_GRAFT_ERROR` / `W_STRUCT_ERROR` | 否 |

### 4.8 ΔDepth：两层采集

| 层次 | 定义 | 采集点 |
|---|---|---|
| 窗口级 $\Delta L_C$ | 窗口 `boundary_outputs` 最大逻辑级数 before→after | ② 前后（BLIF）与 ③ 后（SKY130）各一次；**不一致时以 SKY130 级为准并在 stats 里保留两级** |
| 网表级 $\Delta L$ | `logic_level(target_net)` 全网表 before→after | 接受提交时（复用现有 `logic_level_before/after/reduction`） |

报告口径：**三数并列**，如 `L: 7→5, ΔL = −2, ΔWNS = +0.43 ns`。

**一条对论文有用的论证**：SKY130 HD 中大量单元是单级（`nand4`/`o22ai`/`xor2`），因此**G 与 R 在原理上不可能产生 $\Delta L<0$**，只有 S 或 JOINT 能 —— 该点本身即 S 动机的干净论证。

### 4.9 组合规则

$$JOINT=R/G/B\ \text{既有组合},\qquad S\ \text{独立},\qquad \text{至多加一档 } S\to G$$

不在第一版枚举 $S\times R\times G\times B$。$S\to G$：S 接受后仅对同一窗口输出锥内新实例做一次 G 寻优，受 `candidates_per_iteration` 约束。

---

## 5. S 的窗口抽取 / graft 接口数据结构与状态机 ← 本版重点

> 用户判断：S 最容易出 bug 的不是 ABC，而是 **window grafting**；最危险的具体故障是"局部 CEC 通过，但 graft 到全网表后接错 net"。本节把接口与状态机钉死。

### 5.1 数据结构

```python
@dataclass(frozen=True)
class WindowPort:
    host_net: str        # 原网表中的网名 —— graft 后必须逐字保持不变
    module_name: str     # 窗口模块内端口名（确定性生成，见 5.2）
    direction: str       # "in" | "out"
    known_constant: bool # 常量/供电网（如 tie cell、VPWR/VGND）单独标记

@dataclass(frozen=True)
class WindowCell:
    instance: str                  # 原实例名
    cell_type: str                 # SKY130 单元类型
    connections: dict[str, str]    # port -> net（host 侧网名）
    is_sequential: bool            # 必须恒为 False（不变量）

@dataclass(frozen=True)
class WindowSpec:
    window_id: str                 # 确定性 ID：hash(root + sorted(gates))
    root: str                      # boundary_outputs[0]
    ports_in: list[WindowPort]
    ports_out: list[WindowPort]
    cells: list[WindowCell]
    host_to_module: dict[str, str] # host 网名 -> 窗口模块线名
    module_to_host: dict[str, str] # 反向（graft 时按此还原）
    n_window_combo_cells: int      # N_window（§4.4 的 R_S 分母，仅内部组合标准单元）
    source_cut_method: str
    source_cone: str
    extraction_report: dict        # 不变量逐项检查结果

@dataclass(frozen=True)
class GraftPlan:
    window_id: str
    remove_instances: list[str]        # 从 host 网表删除的实例
    insert_cells: list[WindowCell]     # 插入的新实例（instance 名已加前缀）
    namespace_prefix: str              # f"rs_{window_id}_"
    keep_host_nets: list[str]          # 必须原样保留的边界网名
```

### 5.2 命名与确定性要求（graft 正确性的关键）

1. **边界网名不变**：`WindowPort.host_net` 在 graft 前后**逐字相同**；只有窗口内部网被 namespaced。
2. **内部名命名规则**：`module_name = "w_" + <递增序号>`（**不用原始内部网名**，避免与 host 网表重名）；`insert_cells[*].instance = ns_prefix + <原实例名或新序号>`。
3. **确定性**：同一 `window_id` 必须产出完全相同的 `WindowSpec` 与 `GraftPlan` —— 排序固定（按实例名字典序）、无随机、无时间戳。这是去重（§4.3）与复现（§8）的前提。
4. **幂等性检查**：graft 前若发现 `remove_instances` 中任一实例已不存在，立即失败（`W_GRAFT_ERROR`），不做"尽力而为"。

### 5.3 状态机

```
        ┌──────────┐
        │ EXTRACT  │  从 CutBoundary + 当前网表构建 WindowSpec
        └────┬─────┘
             │ 不变量通过
        ┌────▼─────┐
        │  EMIT    │  写 window.v + cells.v（确定性端口名）
        └────┬─────┘
             │
        ┌────▼─────┐  for v in {S0,S1,S2}
        │ RESYNTH  ├──────────────► W_ABC_ERR / W_ABC_TIMEOUT ──► REJECTED
        └────┬─────┘
        ┌────▼─────┐
        │ CEC_PRE  ├──────────────► F1（计入） ─────────────────► REJECTED
        └────┬─────┘
        ┌────▼─────┐
        │ TECHMAP  ├──────────────► W_LIB_OUT_OF_SET ───────────► REJECTED
        └────┬─────┘
        ┌────▼─────┐
        │ CEC_POST ├──────────────► S_TECHMAP_MISMATCH ─────────► REJECTED
        └────┬─────┘
        ┌────▼─────┐
        │ RATIO    ├─ R_S>1.50 ───► F3-S ───────────────────────► REJECTED
        └────┬─────┘   └─ 1.20<R_S≤1.50 → 打 soft penalty 标记后继续
        ┌────▼─────┐
        │  DEDUP   ├─ 命中 ───────► DROPPED（不计失败）
        └────┬─────┘
        ┌────▼─────┐
        │  GRAFT   ├──────────────► W_GRAFT_ERROR ──────────────► REJECTED
        └────┬─────┘
        ┌────▼─────┐
        │ STRUCT   ├──────────────► W_STRUCT_ERROR ─────────────► REJECTED
        │  CHECK   │  check_netlist_structure() on the FULL host netlist
        └────┬─────┘
        ┌────▼─────┐
        │ EMIT_CAND│  → candidate_netlist_text + PatchCandidate(+resynth_stats)
        └──────────┘
```

**硬性顺序约束**：

1. `CEC_PRE` 必须在 `TECHMAP` 之前 —— 这样"映射前过后失败"能干净归因到 `S_TECHMAP_MISMATCH`。
2. `GRAFT` 之后**必须**对**完整 host 网表**跑一次 `check_netlist_structure()`，**之后**才允许 STA。这是针对"局部 CEC 对但 graft 接错 net"这一具体故障的强制门。
3. `DEDUP` 放在 `GRAFT` 之前（用映射后网表 hash）—— 避免对重复候选做无用的 graft 与 STA。

### 5.4 接口契约（谁调谁）

```python
def extract_window(netlist_text: str, boundary: CutBoundary) -> WindowSpec | None
def emit_window_verilog(spec: WindowSpec, out_dir: Path) -> Path          # -> window.v
def run_variant(spec: WindowSpec, variant: str, out_dir: Path, *,
                abc_timeout_s: float, lib_path: Path) -> VariantResult
def check_cec_pre(spec, variant_result, out_dir) -> CecResult
def techmap(spec, variant_result, out_dir, *, lib_path) -> Path | None     # -> win_mapped.v
def check_cec_post(spec, spec_original_blif, mapped_v, out_dir) -> CecResult
def ratio_check(spec, variant_result) -> RatioVerdict
def graft(netlist_text: str, spec: WindowSpec, plan: GraftPlan) -> str
def structure_check(grafted_text: str) -> StructureReport
def to_patch(spec, variant_result, verdict, grafted_text) -> PatchCandidate
```

**契约要点**：全部为**纯文本进 / 纯文本出**（除 IO 路径参数），不持有全局状态；因此可独立单测，也便于与 `SearchState` 解耦。

### 5.5 必须写的单测（针对最易错处）

| 单测 | 断言 |
|---|---|
| 抽取不变量 | 构造含 DFF/时钟的锥 → `extract_window` 返回 `None` |
| 命名确定性 | 同一 `window_id` 调用两次 → `WindowSpec` 逐字段相同 |
| 边界名不变 | graft 前后 `ports_in/out` 的 `host_net` 集合完全一致 |
| **无网名冲突** | 构造 host 网表中已存在 `rs_...` 前缀 → graft 立即失败而非静默覆盖 |
| 幂等/重复 graft | 对同一 `netlist_text` graft 两次 → 第二次失败 |
| **graft 后结构自检** | 故意制造悬空 net → `structure_check` 报错且候选被拒 |
| 去重 | 3 变体产生 2 个相同 canonical hash → 只保留 1 个 |
| $R_S$ 计数口径 | 手工构造 $N_{\text{window}}=20$、$N_{\text{patch}}=25$ → $R_S=1.25$ 保留且带 soft 标记；$=31$ → F3-S |

---

## 6. 三臂对照实验设计

### 6.1 三臂定义

| 臂 | 候选空间 | 候选排序 | `enable_feedback` | 命令行 |
|---|---|---|---|---|
| **Mixed-Fixed** | R/G/B/JOINT | 权重驱动（割代价+路径覆盖） | **False** | `--strategies R,G,B,J --joint-pairs k --enable-buffer --no-feedback` |
| **Mixed-Random** | R/G/B/JOINT | 随机打乱 | False | 同上 + `--random-order --seed {1,2,3}` |
| **FAECO-Adaptive** | R/G/B/JOINT | 权重驱动 | **True** | 去掉 `--no-feedback` |

**统一口径**：`--rounds 20`、`--period 0.5`、$\boldsymbol\lambda^{(0)}=(1,1,1,1,1)$、同一工具链、**同一运行批（同日）**、候选级 STA 预算上限一致。

> **不可拼旧数据**：现有 `20260826_ablation_random_seed{1,2,3}` 虽已是混合候选空间（B 7154/G 3114/R 1954），但**无 JOINT**，不能充当 Mixed-Random。

### 6.2 记录要求

结果 JSON（含 §3.6 全部字段）+ `run_config.json` + 运行 `.bat`/`.sh`，三者齐备。这是 OI-012 的整改项。

### 6.3 $B(k)$ 曲线（**搜索效率的主指标**）

$$B(k)=\max_{i\le k}\Delta\mathrm{WNS}_i$$

$k$ 为 STA 次序。**即使最终不放论文也必须内部保存**，理由：

```text
方法 A：第 5 次 STA 找到 +0.01 ns，之后再无进步
方法 B：第 20 次才首次改善，第 50 次已达 +0.8 ns
```

只看 `n_sta_to_first_improvement` 会**错误地判定 A 更优**。$B(k)$ 曲线能同时表达"多早"与"多好"，是这三臂比较的主图。

### 6.4 判读标准（事先写定）

| 结果 | 判读 |
|---|---|
| Adaptive 的 $B(k)$ 在同等 $k$ 下不劣、且 $N_{\text{STA-to-first-improvement}}$ 显著更低 | EMA 反馈成立（价值定位=更快找到有效候选） |
| Adaptive 最终 ΔWNS 更高但 STA 更多 | 价值定位改为"更高上限"，须说明预算代价 |
| $B(k)$ 曲线基本重合 | **EMA 反馈无独立贡献** → 核心贡献须改为"候选空间+排序"或改以 S 为主体 |

**统计强度提示（诚实标注）**：仅 8 个电路，均值差异容易被单电路主导。报告**必须**给逐电路配对差值，而非只给均值；判读以"多数电路方向一致"为准，不做显著性断言。

### 6.5 执行顺序（冻结）

$$\boxed{\ \text{Mixed-Fixed}\ \to\ \text{Adaptive}\ \to\ S\ \text{smoke}\ \to\ \text{b06 stress}\ }$$

先跑"最可能推翻核心主张"的一对（Mixed-Fixed vs Adaptive），而非先跑 pureG/pureB（那只回答候选空间）。

---

## 7. b06 可证伪测试：拆成两个主张

| 主张 | 判据 | 若成立 | 若不成立 |
|---|---|---|---|
| **结构能力**（弱）| $N_R=0$ 且 S 产出 `CEC=PASS` 且（$\Delta L_C<0$ 或拓扑确实改变） | 已证明 S 突破了"只在库等价单元中替换"的候选空间限制 | S 连合法候选都产不出 → 实现或方法有问题 |
| **时序救援**（强）| 在 R/G/B 均无法改善的 b06 上 S 取得 $\Delta\mathrm{WNS}>0$ | S 能解决 b06 的时序瓶颈 | **不得**直接判定 S 主张失败 |

**若出现 $\Delta L=-2$ 但 $\Delta\mathrm{WNS}=0$**，正确结论是：

> S 扩展了结构搜索空间，但**尚未证明**能够解决 b06 的时序瓶颈。

而不是"S 的技术主张不成立"。分级结论比一刀切的可证伪设计更严谨。

---

## 8. 实施顺序与验收

| 步 | 内容 | 验收标准（可证伪） |
|---|---|---|
| 0a | OI-011 路径 B：把 `SearchState` 体系落到权威布局；`SearchState` 增持 `FailureFeedbackState` / `cone_limit` / `round_id` | 3 电路 sentinel 复跑复现既有数字（或如实记录差异） |
| 1 | `update_feedback` 纯函数 + legacy 退化测试（§3.3） | 单测逐位相同；264 测试全绿 |
| 2 | schema 扩展 + `run_config.json` 归档 + `B(k)` 落盘 | 新跑一臂即可见 §3.6 全字段 |
| 3 | 三臂对照（先 §6.5 第一对） | §6.4 判读表出结论，无论正负 |
| 4 | ΔDepth 采集填充（两层） | `logic_level_*` 不再是 None/0；报告含两级 $\Delta L$ |
| 5 | S 候选生成器（§5 全状态机） | ① §5.5 单测全绿；② 局部 CEC 通过；③ 至少产出 1 个 $\Delta L<0$ 且 $\Delta\mathrm{WNS}>0$ 的接受候选 |
| 6 | S→G 两阶段 | 同窗口 S 后 G 的增益 > 单独 S |

---

## 9. 技术方案完善路线（回答"之后如何完善"）

> 原则：**不再横向加机制**，只把现有三层里"实现时一定会撞上、现在还没钉死"的接口补齐。按优先级：

| 优先级 | 缺口 | 为什么必须先补 | 补法 |
|---|---|---|---|
| **G1** | **S 的窗口抽取 / graft 接口与状态机** | 用户已识别为最易实现出错处；"局部 CEC 对但 graft 接错 net"是典型故障 | ✅ **本版 §5 已完成** |
| **G2** | `update_feedback` 与 `SearchState` 的**集成点与调用时序**：`enable_feedback` 语义、EMA 推进的轮次定义、`rollback()` 是否回滚 EMA/cone_limit | 定义不清 → 消融实验的"关反馈"到底关了什么会再次说不清（OI-012 的同类风险） | 明确：`enable_feedback=False` 时 **EMA 不推进、权重不变、cone_limit 不变**；`rollback()` **回滚 EMA 与 cone_limit**（否则回滚后语义不自洽） |
| **G3** | **检查点 / 复现契约**：`SearchState` 的序列化格式与恢复语义 | OI-011 的 sentinel 复跑与任何中断恢复都依赖它；也是 3 变体去重与 pat 日志链的前提 | 定义 JSON schema（含 `round_id`/`accepted_patches`/`failure_feedback`/`cone_limit`），并规定"恢复后继续必须产出一致结果"的测试 |
| **G4** | **失败归因分类学的收敛**：S 的 `W_*` / `S_TECHMAP_MISMATCH` 与 F1–F6 的映射规则 | 直接决定失败统计是否可信；若污染 F1，§4.4 之外的所有失败分布都要重述 | 固定 §4.7 表并写入实现；**统计时 `W_*` 与 F1–F6 分开汇报** |
| **G5** | **ΔDepth 两层不一致时的裁决规则** | BLIF 级与 SKY130 级 $\Delta L$ 可能不一致，不先定口径会出现"同一候选两个数" | §4.8 已定"以 SKY130 级为准、两级都保留"；需补**多输出端口的聚合规则**（取 max） |
| **G6** | **三臂的编排与预算控制**：跨电路并行、单候选验证时限、$N_{\text{STA}}$ 上限如何做到三臂严格一致 | 预算不一致 → 三臂对比直接被审稿人否定 | 写 `run_config.json` 契约 + 一个"三臂预算一致性"检查脚本 |
| **G7** | **E（电气风险前置）的采集契约**：`transition/capacitance/fanout/area` 的字段定义、单位、与 Liberty 单位的一致性 | 阶段 3 全部依赖它；口径不清会重演"字段存在但覆盖率 0" | 定义 OpenSTA 报告解析的字段表与单位校验（写进 `project_docs` 或 `docs/GLOSSARY.md`） |
| **G8** | **统计判读的强化** | 8 电路、无显著性检验；若判读不事先定，容易被"事后解释" | §6.4 已加"逐电路配对差值 + 不做显著性断言"；可补**置换检验/符号检验**作为内部参考 |

**建议填补顺序**：G2 → G3 → G4（都属"状态与归因语义"，与 §5 配套，实现前必须定死）→ 实施步骤 0a–3 → G5/G6 → 实施步骤 4–6 → G7/G8。

**当前方案所处的阶段判断**：L2 与 L3 已从"路线图"进入"可直接写代码的技术规格"。**唯一还挡在实现前面的不是新机制，而是 G2/G3/G4 这三项状态与归因语义的钉死**——它们和 §5 同属"实现前必须定死"的类别。

> **✅ 更新（2026-09-23 晚）**：**G2/G3/G4 已写成代码级接口规范**（待确认后冻结）→ `FAECO_V2_IMPL_CONTRACT_20260923.md`（G2 三事件状态更新契约、G3 checkpoint 字段与 `netlist_epoch`/恢复一致性、G4 `W_*`→F1–F6 映射）。本文件据此不再新增机制；后续所有实现遵循该契约。**推进顺序改为**：
> $$\text{G2/G3/G4 接口冻结} \rightarrow 0a\ \text{状态架构迁移} \rightarrow \text{legacy regression} \rightarrow \text{L2 Adaptive} \rightarrow \text{L3 S}$$
> **0a 第一阶段不得改变算法行为**，其 gate 是"新架构 ≡ 旧行为"六项全等（候选顺序 / F1–F6 序列 / 每轮权重 / 接受补丁 / 最终 WNS / STA 次数），通过后才打开 $\rho=0.5$。

---

## 10. 遗留待裁定 / 风险

| 项 | 状态 |
|---|---|
| **G2/G3/G4 接口规格** | ✅ 已写成（待确认）→ `FAECO_V2_IMPL_CONTRACT_20260923.md` |
| OI-011 路径 | ✅ 已裁定：**B**（`SearchState` 为唯一状态所有者） |
| S 的 F3-S 阈值 | ✅ 已裁定：窗口局部 $R_{\text{soft}}=1.2$、$R_{\text{hard}}=1.5$ |
| L2 参数 | ✅ 已裁定：adaptive 默认 $\rho=0.5,\eta_{\text{add}}=0.5,\eta_c=0.25$；legacy 单独一档 |
| $R_{\text{hard}}=1.5$ 偏宽松 → 会放过面积膨胀候选 | ⚠️ 待第一版跑完看分布再收紧；缓解＝每候选报告面积变化 |
| 8 电路统计强度弱 | ⚠️ 以逐电路配对差值为准，不做显著性断言（§6.4） |
| OI-010 的 §4.2 报告口径 | ⚠️ 仍待裁定（不影响本文档的实施，只影响论文改写） |

---

## 11. 阶段 3：电气风险前置（E）与 F6 拆分（2026-09-27 新增）

设计出处：`FAECO_V2_DESIGN_PLAN_20260923.md` §3 阶段 3-A / 3-B。本节只写"怎么做"，
实施按计划顺序（3-A 结论出来后才决定 3-B 是否值得做）。

### 11.1 3-A：电气量的采集与"入式"判据（**已实现**）

采集口径、四臂实验设计、**预锁定的判定判据**（Gate 0 臂有效性 / 标签可用性下限 /
多标签一致才判 SIGNAL）已在 `FAECO_V2_IMPL_CONTRACT_20260923.md` §8.15 写死，
实现见 `code/src/rseco/electrical.py` 与 `code/scripts/analyze_electrical_correlation.py`。
本节不再重复，只记两条**与后续设计耦合**的决定：

1. **电气量取自理想 STA**（不带 SPEF），因为"前置"的语义就是"在付物理分析的钱之前可得"。
   若最终决定入 ranking，特征必须保持这一来源，否则排序器会隐式依赖物理 STA 的结论。
2. **未入式前不新增任何 ranking 路径**：采集与判定都在 evaluator 之外的只读通道完成，
   trial 记录里的 `electrical` 字段不被 `ranking` / `accept` / `refinement` 读取
   （有单测断言采集开关不改变 `weights_trace` / `failure_ema_trace` / `history[*].failures`）。

### 11.2 3-B：把 F6 拆成 $F_{6L}$（器件负载）与 $F_{6W}$（线负载）

**问题**：$F_6$ 现在是一个**单一标签**（"理想增益未兑现"），无法回答"为什么未兑现"。
计划 §3 明令"没有能判定为什么失败的能力时，不要拆 $F_6$"。3-A 的采集提供的正是这个能力
（负载电容、扇出、关键路径电气剖面），因此 3-B 的前提是 **3-A 判定为 SIGNAL 或至少
出现"电气量与失败同向"的稳定迹象**；若 3-A 判 NO SIGNAL，则 3-B **不做**（如实写进 limitation）。

**形式化（可加分解，构造性成立）**。关键路径上的延迟增量按来源三分：

$$\Delta d_{\text{total}} \;=\; \underbrace{\Delta d_{\text{cell}}}_{\text{理想 STA}}
\;+\; \underbrace{\Delta d_{\text{load}}}_{\text{线电容→器件负载}}
\;+\; \underbrace{\Delta d_{\text{wire}}}_{\text{线电阻→互连延迟}}$$

实现办法是**给 SPEF 模型的 R、C 各加一个独立比例因子**（`estimate_net_rc` 现有
`r = 0.09·len`、`c = 0.21·len/1000`，R/C 共用同一个 `len`，无法单独缩放）：

| 额外参数 | 默认 | 作用 |
|---|---|---|
| `wire_res_scale` | 1.0 | 缩放网表线电阻（SPEF `*RES`） |
| `wire_cap_scale` | 1.0 | 缩放网表线电容（SPEF `*CAP`） |

**默认均为 1.0 ⇒ SPEF 逐字节不变 ⇒ 既有产物与等价门不受影响**（与 3-A 的 `electrical_capture`
同一条惰性纪律）。三个 STA 点：

| 点 | 配置 | 语义 |
|---|---|---|
| $L$ | 无 SPEF | 理想（cell-only） |
| $L_{C}$ | SPEF，`wire_res_scale=0` | 只有线**电容**（器件负载） |
| $L_{RC}$ | SPEF，全比例 | 完整 RC |

于是（对同一候选、同一配对基线）：

$$\Delta d_{\text{cell}} = \Delta d(L) - \Delta d(L_0), \qquad
\Delta d_{\text{load}} = \Delta d(L_{C}) - \Delta d(L), \qquad
\Delta d_{\text{wire}} = \Delta d(L_{RC}) - \Delta d(L_{C})$$

**恒等式按构造成立**，不是拟合出来的 —— 这是"可判定"而非"猜测"的关键。

**归因标签**（写入 `failures.py`，替代单一 $F_6$）：

$$F_{6L}:\ \Delta d_{\text{load}} < 0 \ \wedge\ |\Delta d_{\text{load}}| > |\Delta d_{\text{wire}}|,
\qquad
F_{6W}:\ \Delta d_{\text{wire}} < 0 \ \wedge\ |\Delta d_{\text{wire}}| \ge |\Delta d_{\text{load}}|$$

（"$<0$"=该项让增益变小。两标签互斥且完备地覆盖 $F_6$ 的"增益被吃掉"情形；
$\Delta d_{\text{load}} = \Delta d_{\text{wire}} = 0$ 而仍失败者留在 $F_4$ 或新的 $F_{6?}$，不强行归类。）

**代价与记账**：每候选多 **1 次** STA（$L_C$；$L$ 与 $L_{RC}$ 物理门已经在跑），
必须计入同一个 `sta` 预算（两臂同值），并在报告里给出 `sta_used` 证明预算不绑定。

**验收（3-B 的 gate）**：
1. 恒等式自检：逐候选核对 $\Delta d_{\text{cell}} + \Delta d_{\text{load}} + \Delta d_{\text{wire}}
   = \Delta d(L_{RC}) - \Delta d(L_0)$ 在数值容差内成立（$10^{-9}$ 量级）；
2. **惰性**：`wire_res_scale=wire_cap_scale=1.0` 时与未改动版本逐位相同（SPEF 文本哈希 + 端到端轨迹）；
3. **可判定性**：$F_{6L}$/$F_{6W}$ 各自都拿到双类 $\ge 20$ 的样本（沿用 3-A 的类别下限纪律），
   否则如实报"本 regime 不可判定"；
4. 与 3-A 的电气量对照：$F_{6L}$ 应与 `d_cap_slack` / `cp_total_capacitance` 同向，
   $F_{6W}$ 应与 `cp_max_fanout` / 线长代理同向 —— **若不对应，说明标签或特征之一有误，
   先归因再谈入式**。

### 11.3 与 3-A 的依赖关系（冻结）

$$\text{3-A 判定} \to \begin{cases}
\text{SIGNAL} & \Rightarrow \text{3-B 实施（上表三点 + 新标签），并标定式 (2) 权重} \
\text{NO SIGNAL} & \Rightarrow \text{3-B 不做；电气量保持"仅采集"，$F_6$ 不拆分（如实写 limitation）}
\end{cases}$$

**论文侧一律等 3-A 判定与 OI-015 裁定后一次性改**（沿用"技术方案先行、论文后改"）。

---

## 12. 阶段 1-C：增量 ECO 形式化与失效候选处理（2026-09-27 新增）

设计出处：`FAECO_V2_DESIGN_PLAN_20260923.md` §1-C「增量 ECO 形式化 + stale invalidation
**写清楚**」。**这不是新机制**：语义早已在 `code/src/rseco/search_state.py` 实现并通过 0a
等价门；缺口只在论文——现稿仅在 §3 用一句话带过"多轮配置下修复网表由接受的补丁逐轮累积形成"
（第 257 行），没有形式化，也没写失效候选 / 回退 / 重放。全文检索 `.tex` 无
`stale`/`epoch`/`rollback`/`回放` 任一关键词。

### 12.1 待写清的机制（与代码一一对应）

| 语义 | 代码位置 | 论文现状 |
|---|---|---|
| 补丁累积：$G_k = p_k\circ\cdots\circ p_1(G_0)$ | `accept_patch` / `replay` | 仅一句带过 |
| 纪元 $e := \lvert\{p_i\}\rvert$，$e = \texttt{netlist\_epoch}$ | `accept_patch`（`e ← len(accepted_patches)`） | 无 |
| 候选复合身份 $\mathrm{key}=H(H(G_e)\Vert H(\text{cut},\text{action}))$ | `candidate_key` / `mark_candidate_tested` | 无 |
| 失效判据 $\text{stale}(e_0)\iff e_0<e$，不评估、不记账、不入 EMA | `is_stale` / `record_stale_candidate` | 无 |
| 回退只恢复**决策态**，审计/预算态不可逆 | `rollback` + `DecisionSnapshot` | 无 |
| 确定性重放与校验 | `replay`（哈希比对，契约 R5） | 无 |
| 不变式 $e=\lvert\mathcal P\rvert$、$r\ge e$ | `check_invariants` | 无 |

三条**必须写对、否则与实现不符**的语义：

1. **接受轮不推进 EMA**（契约 §2.3 裁定 3）——否则"接受"会被误报成一次失败反馈。
2. **失效候选记入工具层**（stage tag `W_STALE_CANDIDATE`），**不得**进入 F1–F6 方法层，
   否则"失效感知"的失败谱会被基础设施事件污染（同 §4.1 的 $W_*$ 隔离）。
3. **回退不返还预算**：`tested_candidate_hashes` / `budget` / `failure_history` 是"已发生的事实"，
   被回退步的事件标 `invalidated_by_rollback` 而非删除——这条直接支撑"审计可复现"的主张。

### 12.2 拟插入论文的文本（`paper/zh/manuscript/…tex`，待贴）

拟作为 §3 末尾新增小节（紧跟第 257 行那段之后），编号顺延。文本以现状代码为准，
不引入任何新符号约定（沿用稿件既有的 $G_r$ / 补丁 $p$ / 哈希 $H$ 记号）：

```latex
\subsection{增量式 ECO 的累积语义与失效候选处理}\label{sec:incremental}

多轮配置下，修复网表并非每轮从头重算，而是由接受的补丁\emph{逐轮累积}形成。
设初始网表为 $G_0$、第 $i$ 次接受的补丁为 $p_i$，则第 $k$ 次接受后的修复网表为
\begin{equation}\label{eq:accum}
  G_k \;=\; p_k \circ p_{k-1} \circ \cdots \circ p_1\,(G_0),
\end{equation}
其中 $\circ$ 表示在上一轮网表上施加一次局部替换。运行状态因此只需维护
\emph{累积纪元} $e := |\mathcal{P}|$（已接受补丁数）与当前网表 $G_e$；
二者一并进入候选身份，使\emph{同一}割窗在不同纪元被视为\emph{不同}候选：
\begin{equation}\label{eq:candkey}
  \mathrm{key}(c) \;=\; H\!\bigl(\,H(G_e)\,\|\,H(\text{cut},\text{action})\,\bigr).
\end{equation}
每次接受先在当前状态上取一份决策快照，再原子地追加补丁并推进 $e \leftarrow e+1$；
由于同一轮至多接受一次，恒有 $e = |\mathcal{P}|$，且轮计数不小于 $e$。

由此，候选自生成之时便绑定到生成纪元 $e_0$。若同一轮内先有候选被接受（$e$ 增大），
则其余候选随之\emph{失效}：
\begin{equation}\label{eq:stale}
  \text{stale}(e_0) \;\Longleftrightarrow\; e_0 < e .
\end{equation}
失效候选不再提交时序测量、不消耗工具预算，也不更新失败反馈；它被记入\emph{工具层}
日志而非\emph{方法层}失败谱，因此不污染失效感知的统计口径。同理，回退一次接受只恢复
决策状态（纪元、权重、反馈），已消耗的预算与已测候选集合作为不可逆的审计事实保留，
被回退步骤产生的事件仅标记为"已失效"而非删除。该累积语义的直接后果是可重放：给定
$G_0$ 与补丁序列 $\{p_i\}$，由式~\eqref{eq:accum} 可确定性重建 $G_k$，且重建哈希与
运行时一致，使多轮搜索可中断续跑。效率优先配置（\S\ref{sec:eff_prio}）仅执行单轮，
$\mathcal{P}$ 至多含一个补丁，上述累积与失效规则退化于无形。
```

### 12.3 验收

1. **语义一致**：文中每条断言都能在 `search_state.py` 找到对应实现（见 §12.1 表），
   无"论文有而代码无"或反之。
2. **不引入新符号冲突**：与稿件既有记号表一致；`\ref{sec:eff_prio}` 等交叉引用编译后无 `??`。
3. **质量门不变**：lualatex ×2，0 Error / 0 Overfull / 0 Underfull，页数变化仅因新增小节；
   日志中 5 处 `undefined` 仍是字体替身警告（非引用）。
4. **与单轮结果不冲突**：单轮配置下新小节明确退化为空操作，与既有实验数字无张力。

### 12.4 应用 gate

本节只放**待贴文本**。实际改 `.tex` 仍等以下一起做，避免二次返工（沿用"技术方案先行、
论文后改"）：

- OI-013（主实验基线 revision）与 OI-014（S 定位）**裁定后**；
- 3-A 判定落地后（若 NO SIGNAL，§7 limitation 需一并写明"电气量仅采集、不入式"）。

---

## 13. 阶段 2-A 后续：S 的窗口来源缺陷与重设计（2026-09-28 新增）

设计出处：阶段 2-A 的延伸；直接关系到 **OI-014 的证据基础**。本节只写诊断与方案，
**不动代码、不动 `.tex`**（沿用"技术方案先行"）。

### 13.1 诊断：S 的窗口宇宙被 R/G/B 的每轮配额截断（新发现，可量化）

> ⚠️ 本节的**归因**已由 §13.1.1 的实测普查**修正**：截断本身只占 1 个窗口，真正封顶的是
> 割枚举的 `k`。结论（S 的窗口池与 R/G/B 束宽耦合）不变，但杠杆点从"切片"移到"枚举"。

`flow.py` 里的两行决定了 S 的可触及窗口集：

```python
# L626 —— 加权割列表按 R/G/B 的每轮配额截断
round_candidates = list(candidates[:max_candidates_per_iteration])
# L890 —— S 复用的是同一个截断列表
for boundary in round_candidates:
```

⇒ **S 的窗口池 ≤ `candidates_per_iteration`（消融中 = 8）/ 每个 `(G_r, cone)`**，与
`resynth_per_iteration` **无关**：配额再大，也只能从这 8 个里取。实测（`20260924_l3s_ablation`
与 `_k4`，8 电路 × 20 轮）：

| | `resynth_per_iteration=1` | `=4` | 差 |
|---|---|---|---|
| S 候选总数 | **37** | **39** | **+2（+5%）** |
| 逐电路 | 2 / 8 / 1 / 0 / 7 / 6 / 5 / 8 | 2 / 8 / **3** / 0 / 7 / 6 / 5 / 8 | 仅 s420 变 |
| 触及轮数 | 2 / 8 / 1 / 0 / 7 / 6 / 5 / 8 | 1 / 2 / 1 / 0 / 2 / 2 / 2 / 2 | 配额只改变"摊入几轮" |
| 接受 | 0 / 8 电路 | 0 / 8 电路 | — |

**把每轮配额从 1 提到 4，只是把同一批窗口压缩进更少的轮次**，几乎不增加总数 ——
因为池子只有 8 个。这把此前"加大 `resynth_per_iteration` 无用"的**经验观察**升级为**机制解释**。

第三条佐证（去重命中率极高）：s713 在 k=1 下 `windows_offered=123`、`windows_extracted=105`，
但只有 **7** 个是**新**窗口 ⇒ **93% 的抽窗是同一批割边界被重复走过**（永久去重把它们挡掉）。

⇒ **结论**：当前集成把"S 的候选空间"与"R/G/B 的每轮采样配额"**耦合**了。S 从未拥有属于
自己的窗口来源；因此 {S 开, S 关} 观测到的"接受 0/8"**只覆盖到"在 R/G/B 的 top-8 割边界里
S 无接受"**，不可外推为"S 这一机制无贡献"。

### 13.1.1 ★ 池子普查结果（2026-09-28 实测）—— 并**修正了 13.1 的归因**

只读插桩 `s_stats["pool_census"]`（§13.4-2）实测（2026-09-28）：

| 实验口径 | `len(candidates)`（未截断） | `len(round_candidates)`（截断后） |
|---|---|---|
| `candidates_per_iteration = 8`，s382 / s713 / s832 / s953，各 2 轮 | **9** | 8 |
| `candidates_per_iteration = 8`，s420 / s713 / s832 / s953，**各 20 轮** | **[9] × 20** | [8] × 20 |
| `candidates_per_iteration = 32`，s382 / s953，各 2 轮 | **33** | 32 |
| `candidates_per_iteration = 8`，**s27**，20 轮（L1 重跑时的反例） | **6** | 6 |
| `candidates_per_iteration = 32`，**s27**（L1 重跑） | **6（未变）** | — |

三条结论：

1. **`len(candidates) = min(k + 1, 该锥体的可计分割空间)`**，在**未饱和**的电路上与轮次、cone、
   `G_r` 无关（s420/s713/s832/s953 各 20 轮恒为 9）；那个 `+1` 是前置的
   `_critical_path_cover_cut`。⇒ **截断只损失 1 个窗口，L626 不是瓶颈**，13.1 把它当主因是
   **不完全的归因**。
2. **反例：小锥体会饱和。** s27（10 门，目标锥 G10 极小）的割图**总共只有 6 个可计分边界**，
   `k=8` 与 `k=32` 都返回 6 ⇒ 此时 L1 **天然惰性**（`window_pool=32` 但 `window_pool_offered`
   仍 6、S candidates 仍 2、接受仍 0）。判定 L1 有效性必须**排除饱和电路**。
3. **加权割枚举随 `k` 线性增长**（未饱和时 k=8 → 9，k=32 → 33）⇒ **L1 可行且改动极小**：
   给 S 一次 `k = resynth_window_pool` 的**专属枚举**，即可把 S 的窗口池从 **8 → 32（4×）**。

> **可引用表述**：S 的可触及窗口上界 = **不同 `G_r` 数 × `min(candidates_per_iteration, 割空间)** ——
> 也就是 **S 的触达范围被 R/G/B 的束宽直接决定**（小锥体除外）。这是"S 与 R/G/B 耦合"的**定量形式**。

### 13.2 目标与单变量纪律

**目标**：让 S 的候选空间由"割空间 + S 自己的选择准则"决定，而非由 R/G/B 的配额决定；
**不破坏** {S 开, S 关} 的单变量对照。

**纪律**：{S off, S on(新窗口来源)} 两臂，其余口径逐字相同；off 臂须**逐位复现归档基线**。
新窗口来源由 `resynth_window_pool` 控制，**默认 = `candidates_per_iteration`** ⇒
默认路径与现状**逐位相同**（惰性，同 `electrical_capture` 纪律）。

### 13.3 方案（三 lever，建议按 L1 → L2 顺序验证；L3 暂缓）

**L1（池子规模 —— 已按 §13.1.1 普查结果修正）**：S 不复用 R/G/B 的候选列表，而是**用更大的 `k`
重新枚举一次割候选**作为 S 的专属窗口池（第二次 `_cone_candidates(..., k=resynth_window_pool)`，
`resynth_window_pool` 建议 32 起）。**不可实现为"加宽 `candidates[:W_s]` 切片"** ——
§13.1.1 实测未截断列表只有 **9**，切片加宽无效。默认 `resynth_window_pool = candidates_per_iteration`
⇒ 默认路径与现状**逐位相同**。改动面：`flow.py` 一处（新增参数 + 一次枚举调用）。

> **✅ L1 已实现（2026-09-28，用户定案后）**：`run_multi_iteration_case(..., resynth_window_pool=None)` +
> CLI `--resynth-window-pool`。惰性判据写成**严格守卫**（`is not None and > candidates_per_iteration`）：
> 默认与"显式等于 `candidates_per_iteration`"两条路径都与现状逐位相同（2 项新单测把守，含
> "默认只跑一次枚举、k 恒为 8"与"S 专属枚举出现在 k=32"的 spy 断言，以及 `weights_trace` /
> `failure_ema_trace` / `history[*].failures` 逐位相同）。
>
> **重跑口径（`experiments/20260928_s_l1_ablation`）**：8 电路 × {`off`, `on`}；
> `on` = `--structure-resynth --resynth-per-iteration 8 --resynth-window-pool 32`，
> `off` = 无开关；两臂共同 `--period 0.5 --max-iterations 20 --candidates-per-iteration 8
> --joint-k 2 --enable-buffer --workers 1 --early-stop --no-feedback --sta-budget 1600`。
> **`resynth_per_iteration` 同时提到 8 是必要的**：池子扩到 32 后，`resynth_per_iteration` 重新成为
> 每轮的上限（此前 1/轮 × 20 轮根本覆盖不到 32）；两者共同构成"L1 窗口来源"，`off` 臂仍是唯一对照。

**L2（时序加权选窗）**：S 在自己的窗口池内按**时序权重**排序，使每轮名额优先给最关键窗口。
权重择一（定案时冻结）：
- (a) 窗口覆盖的**关键路径门数**（复用 `active_critical`）；
- (b) 边界输出的 **slack**（越负越优先）；
- (c) 窗口内**最差 slack**。

> 现状 `round_candidates` 的顺序来自 `_cone_candidates` 的**失效感知加权**（`weights` + critical
> discount），它优化的是"R/G/B 的期望收益"，与"S 的深度压缩收益"**不是同一个目标**；
> L2 即把选择准则换成 S 自己的。

**L3（曝光轮数）**：解除"仅当 R/G/B 全失败轮才报价 S"。**不建议先做** —— 它与 L1/L2 的效果
会混在一起；且当前 37 个候选**全部**落在 R/G/B 失败的轮里，尚无证据显示曝光是瓶颈。

### 13.4 预锁定验收判据（写在实现之前）

1. **惰性（先决）**：`resynth_window_pool == candidates_per_iteration` 时与未改动版本**逐位相同**
   （窗户/候选/接受计数、`rounds_with_s`、{S on} 全轨迹含 STA 记账）。
2. **池子普查（✅ 2026-09-28 全部完成，见 §13.1.1）**：
   - 截断后 8、未截断 **9**（`= k + 1`），四电路一致且 s420 全 20 轮恒定；
   - `k = 32` 时未截断 **33** ⇒ **枚举随 `k` 线性增长** ⇒ **L1 成立**（窗口池 8 → 32，4×）。
   - ⇒ 瓶颈**不在 L626 切片**（只占 1 个窗口），而在 **L607 枚举的 `k`**；且该瓶颈**可通过
     给 S 一次专属枚举直接解除**。**无需**改 cone / 深度切分。
3. **有效性（2026-09-28 用户裁定：改为三层裁决，禁止跳级）**——**不得因"扩池成功、候选数增加"
   就升格 S**：
   - **第一层 enumeration**：非饱和电路 `N_S,L1 > N_S,old` ⇒ 只证明"L1 的 enumeration bottleneck
     被真实解除"，**不构成 timing capability**；
   - **第二层 candidate quality**：看 `N_CEC pass` / `N_measured` / S 候选 `ΔWNS` **分布**；
     若枚举涨 3× 而全部 `ΔWNS ≤ 0` ⇒ **问题在 S transformation quality，不在 L1**；
   - **第三层 repair capability**：`N_accepted,S > 0` 且 ≥1 电路 `ΔWNS_on−off > 0`（最好 `ΔL < 0`）
     ⇒ **这才决定 OI-014**。若 `N_accepted,S = 0`（**即使候选 37 → 100+**）⇒ 仍选 **(B) 降级可选**。
4. **指标口径（固定，不得用 `windows_offered` 作主证据）**：`windows_offered` 含**重复扫描的割边界**
   （s27 的 114 ≈ `19×6`），**不是** unique window 数，仅作内部扫描开销指标。报告固定看
   `N_unique_window`（canonical hash 去重）、`N_extracted`、`N_S candidate`、`N_measured`、
   `N_accepted` —— **后四个最关键**。
5. **预算不绑定**：两臂同 `sta` 预算；新增 S 候选的 STA 计入同一预算；停因不因预算。
6. **可证伪的失败判据**：若池子扩到 `W_s` 后接受仍为 0，结论即为
   **"该 cone 的割空间内，割局部重综合没有可接受候选"**（能力边界）→ 如实写 limitation，
   **而不是继续加大 `W_s`**；并转入 **S 候选质量归因**（见 §13.7）。

### 13.5 成本

每新增一个 S 候选 ≈ 窗口抽取 + CEC-1 + CEC-2 + resyn(ABC) + 1 次候选 STA。
`W_s=32` 的最坏情形下 S 候选数 ≤ `32 × #触及轮`，故 8 电路 × 20 轮需同步放大 `sta` 预算
（或按比例约束 `W_s`）；否则**预算先绑定**、S 的效果被预算切断（这本身是要报告的混淆项）。

### 13.6 与 OI-014 的关系（建议裁定顺序）

**OI-014 的现有证据被 13.1 的缺陷混淆**：{S 开, S 关} 的"接受 0/8"只说明
"在 R/G/B 的 top-8 割边界里 S 无可接受候选"，不足以支持 (B)"S 是可选类型"。建议：

1. 先做 **13.4-2 池子普查**（只读、便宜）；
2. 若可扩空间大 ⇒ 实现 **L1(+L2)** 并重跑 {S 开, S 关}；
3. 用新证据再裁 (A) 独立贡献 / (B) 降级可选。

### 13.7 负结果分支：S 候选质量归因（2026-09-28 用户裁定新增）

若 L1 后仍 `N_accepted,S = 0`（**即使 S 候选 37 → 100+**），这是一个**有价值的负结果**：
到那时"**S 不行只是 enumeration 太窄**"这一解释已被排除。此时**禁止**继续扩池
（32 → 64 → 128），而应直接查：

> **为什么通过了 CEC 的 S patch 没有 timing gain？**

归因分解（逐条量化，而非笼统结论）：

| # | 待查项 | 判据/证据 |
|---|---|---|
| (i) | 窗口内 **logic depth 是否实际下降** | `ΔL(BLIF)` / `ΔL(SKY130)`（已有 `analyze_s_candidates.py`） |
| (ii) | **映射后 depth 是否又回来** | 比较重构网表在 techmap 前后的 depth |
| (iii) | **cell delay 是否变差** | 重构窗口内单元延迟/驱动变化 |
| (iv) | **fanout/cap 是否抵消结构收益** | 窗口边界负载变化 |
| (v) | **critical path 是否根本不穿过被重综合窗口** | 窗口门 ∩ `active_critical` 的覆盖率 |

共享 → 与 OI-014 的 (B) 判定合并叙述；主贡献回到「候选构造 + 加权排序 + 失败归因 + STA 验证」。

论文侧仍未动 `.tex`。
