# FAECO-v2 技术设计（L2 失败率反馈 / L3 S 结构重综合 / ΔDepth / 三臂对照）

> 日期：2026-09-23
> 定位：本文档回答"**怎么实现**"；`FAECO_V2_DESIGN_PLAN_20260923.md` 回答"**做哪几件事、什么顺序**"。两者是设计规格与路线图的关系。
> 前置：**OI-011（代码基对账）未定案**。本文档按两条路径分别标注落点，不预设结论。
> 约束：本设计**不修改论文**；论文改动统一在方案定案后一次性执行。

---

## 1. 设计基线（已核实的实现事实）

| 事实 | 位置 | 对本设计的影响 |
|---|---|---|
| 失败反馈唯一实现为纯函数 `refine_weights(weights, failures: set[FailureType])`，每类 `+= 1.0`，`failures` 是 **set** | `code/src/rseco/refinement.py:28–78` | 每轮每类最多 +1.0；**无跨轮状态** → 引入失败率必须新增持久状态 |
| 初始权重全为 1.0（`boundary_penalty`/`size_penalty`/`critical_coverage_reward`/`verification_cost_penalty`/`equivalence_stability_reward`），`max_cone_gates=1000` | `refinement.py:9–17` | $w^{(0)}$ 可固定为全 1，三臂对照的 $w^{(0)}$ 统一成本极低 |
| F5 额外动作 `max_cone_gates = max(1, max_cone_gates // 2)` | `refinement.py:56–59` | 这是**搜索空间收缩**，不是偏好权重，**不应**纳入权重率更新 |
| 权重进入式(2) 的方式不同：$\lambda_b/\lambda_s/\lambda_f$ 加性入 cost；$\lambda_c$ 进入分母折扣 $1+\lambda_c\mathbb{1}[v\in\mathcal{R}]\cdot\mathrm{depth}/\mathrm{depth}_{\max}$；$\lambda_v$ 乘 $0.01$ | `cut.py:166–199` | **各类权重的量纲/作用不同 → 不能用同一个 clip 区间** |
| `CutBoundary(method, boundary_inputs, boundary_outputs, internal_nets, gates)`，`patch_size = len(gates)` | `cut.py:11–30` | **这是 S 的窗口规格的现成载体** |
| `PatchCandidate` 携带 `boundary_inputs/boundary_outputs/gates/patch_size/equivalence_*` | `patch.py:8–59` | S 候选可复用同一结构，只需新增 `cut_method` 取值与重综合统计字段 |
| `Netlist.logic_level(signal)` / `logic_levels()` 已存在 | `netlist.py:37,68` | ΔDepth 采集无需新建能力 |
| `F3` 阈值 `max_patch_ratio = 0.15`（相对全局门数） | `failures.py:19–20` | **S 的窗口通常显著大于 R/G/B 的补丁 → 该阈值需为 S 单独放宽或改口径** |
| 已有 ABC 基础设施：`_normalize_to_blif`、`RESYN2_BUILTIN_SEQUENCE`（balance/rewrite/refactor 全序列）、ABC `cec`、`check_mapped_blif_equivalence`（映射后 BLIF vs 原网表 CEC）、`make_liberty_cells_v.py`（Liberty → cells.v） | `yosys_abc.py:15–27,103,215,536`；`code/scripts/make_liberty_cells_v.py` | S 的重综合链与验证链**约 70% 已有**，缺窗口抽取/回填与库约束重映射 |

**两条路径的落点差异**（OI-011）：

| | 路径 A：移植到 main（`code/` 布局） | 路径 B：反向迁移 codex 分支为新 main |
|---|---|---|
| L2 落点 | `code/src/rseco/refinement.py` + `refinement_loop.py`（新建持久状态） | codex `src/rseco/refinement_loop.py` 的 `SearchState`（**已有 `failure_history`，可扩展出 `failure_rates`**） |
| L3 落点 | `code/src/rseco/`（新增 `resynthesis.py`）+ `cut.py`/`patch.py` | codex `src/rseco/`（**已有 `current_cone_gates`，窗口重抽现成**） |
| 净工程量 | 多一步"移植 + sentinel 复跑证明等价" | 多一步"布局迁移 + 路径修复" |
| 对 L2 的便利性 | 需从零建 rate 状态 | `SearchState` 已有审计型 failure 记录，扩展更自然 |

> 结论：**路径 B 在 L2 上更省**（状态容器现成），**路径 A 在仓库治理上更省**（main 已是迁移后布局且 264 测试在跑）。这是需要用户裁定的唯一实质分歧点。

---

## 2. L2：失败率驱动权重（C）的技术设计

### 2.1 状态定义

```python
# 新增（不可变，随 RefinementWeights 一起传递，保持 refine_weights 的纯函数性质）
failure_rates: tuple[float, ...]   # 长度 6，索引对应 F1..F6 的顺序
```

放在 `RefinementWeights` 内（而非独立可变对象）的理由：现有 `refine_weights(weights, failures) -> RefinementDecision` 是纯函数、可单测、被 `simulate_refinement_loop` 与 `flow.py` 两处复用；把 rate 并入 weights 可**零改动调用方签名**。

初始值：`failure_rates = (0.0,) * 6`。

### 2.2 更新规则

每轮（无论该轮是否失败）：

$$r_j^{(t)} = \rho\, r_j^{(t-1)} + (1-\rho)\,\mathbb{1}[F_j\in\mathcal{F}^{(t)}],
\qquad
w_j^{(t+1)} = \mathrm{clip}\!\left(w_j^{(t)} + \eta\, r_j^{(t)},\ w_j^{\min},\ w_j^{\max}\right)$$

**关键性质（必须在实现中作为断言保住）**：取 $(\rho=0,\ \eta=1,\ w^{\min/max}=\mp\infty)$ 时，该式**逐位退化为现行 `+= 1.0` 规则**——因为此时 $r_j^{(t)}=\mathbb{1}[F_j]$，增量为 0 或 1。这使现有全部实验结果可解释为新机制的**特例**，而非被推翻。验收测试必须显式覆盖这条等价性。

### 2.3 参数与 clip 区间（按权重的角色分别设定）

| 权重 | 作用 | 建议 $w^{\min}$ | 建议 $w^{\max}$ | 默认 $\eta$ | 依据 |
|---|---|---|---|---|---|
| `boundary_penalty` $\lambda_b$ | 加性入 cost，$/ (1+\mathrm{depth})$ | 1.0 | 8.0 | 1.0 | 8× 上限避免单一失败类型压倒其余项 |
| `critical_coverage_reward` $\lambda_c$ | **分母折扣**（乘性） | 0.0 | 2.0 | 1.0 | 其折扣幅度为 $1+\lambda_c\cdot\mathrm{depth}/\mathrm{depth}_{\max}$，$\lambda_c=2$ 已可达 3× 折扣；给到 8 会使排序反转 |
| `equivalence_stability_reward` $\lambda_f$ | 加性，$0.1\lambda_f\cdot\mathrm{fanout}$ | 1.0 | 8.0 | 1.0 | 同 $\lambda_b$ |
| `size_penalty` $\lambda_s$ | 加性，$\lambda_s s^2/S$ | 1.0 | 8.0 | 1.0 | 同 $\lambda_b$（注意 F6 当前不驱动 $\lambda_s$，见 OI-008） |
| `verification_cost_penalty` $\lambda_v$ | 加性，$0.01\lambda_v n_C$ | 1.0 | 8.0 | 1.0 | 同 $\lambda_b$ |
| `max_cone_gates` | 离散收缩，**不参与率更新** | — | — | — | 见 §2.4 |

全局 $\rho$ 默认 **0.5**：单类连续失败时 $r\to 1$（增量 $\le\eta$），单次失败后 $r=0.5$（半量增量）——即"偶发失败小步、持续失败大步"，且总量有界。

### 2.4 F5 的特殊处理（不并入率更新）

`max_cone_gates //= 2` 是搜索空间的**单向收缩**，语义上不是偏好。改为**率门控**：仅当 $r_{F5} \ge \theta$（建议 $\theta=0.5$，即连续两次或等效累积）时才减半。理由：现状下任一 F5 触发即永久减半锥上限，在长任务（b17）上可能过度收缩；门控后仍能收缩但更稳。

### 2.5 触发时序

- `failures` 是 **set**，故同一轮内同一 $F_j$ 只贡献一次 $\mathbb{1}[F_j]$；**该行为保持不变**（不改为按候选计数），以免与现有语义脱钩。
- "轮内 vs 跨轮"：rate 状态的推进点与现行权重推进点完全相同（`simulate_refinement_loop` 每次 `refine_weights` 调用即一轮）。因此**现有 `enable_feedback` 开关天然复用**：`enable_feedback=False` 时既不更新 $r$ 也不更新 $w$。

### 2.6 必须采集的新指标（否则无法证明 Failure-Aware 的价值）

在 `outerloop_result.json` / `hybrid_result.json` 中新增：

| 字段 | 定义 | 用途 |
|---|---|---|
| `n_sta_to_first_improvement` | 首次接受的候选之前累计的候选级 STA 次数 | 证明 $N_{\text{STA-to-first-improvement}}\downarrow$ |
| `wns_gain_per_100_sta` | $\Delta\mathrm{WNS} / N_{\text{STA}} \times 100$ | 证明单位验证预算产出 $\uparrow$ |
| `failure_rates_final` | 每轮 $r_j$ 的终值（或逐步轨迹） | 可解释性；审稿人可核 |
| `weights_trace` | 每轮 $(w_1..w_5)$ | 同上 |
| `enable_feedback` / `strategies` / `random_order` / `seed` / `init_weights` / `toolchain` | 运行配置 | **OI-012 暴露的缺口**：当前一个都没记 |
| 运行命令归档 | 实验目录内写 `run_config.json`（argv + 环境 + git SHA） | 同上 |

---

## 3. L3：S 局部结构重综合候选的技术设计

### 3.1 形式定义与不变量

对窗口 $C$：$S(C):\ (I_C,O_C,V_C)\to(I_C,O_C,V_C')$，且 $F_{C'}(I_C)=F_C(I_C)$。

实现层不变量（任一违反即**拒绝**该候选）：

1. **接口保持**：`boundary_inputs` 与 `boundary_outputs` 的**名称集合与位宽完全不变**（仅内部网表可变）。
2. **时序边界**：窗口内不得含 DFF / 时钟 / 复位单元（与论文既有"不改写 D 触发器、时钟和复位"的声明一致）。
3. **唯一驱动**：每个 `boundary_input` 在窗口内被恰一个端口消费；`boundary_output` 由窗口内恰一个实例驱动。
4. **无悬空**：重综合后不得出现无驱动的内部网或未被消费的输出。
5. **门数守卫**：`patch_size' \le \kappa\cdot|\text{gates}|`（见 §3.7 对 F3 阈值的处理）。

### 3.2 窗口抽取

输入：`CutBoundary`（来自 `cut.py` 的加权割或关键路径覆盖割）+ 当前 `mapped.v` 文本。
输出：自洽的窗口 Verilog `window.v`（单模块，端口 = `boundary_inputs` + `boundary_outputs`）。

步骤：
1. 只保留 `boundary.gates` 中的单元实例（`internal_nets` 为内部线网）。
2. `boundary_inputs` 中位于 `internal_nets` 的网改名为模块输入端口；其余为常量/供电网，按需保留。
3. `boundary_outputs` 作为模块输出端口。
4. 通过已有 `parse_mapped_netlist` 取实例与连线，避免自行写 Verilog 解析。

> 复用：`netlist.py` 的 `Gate`/`Netlist` 与 `netlist_io.py` 已做解析；窗口 Verilog 只用于喂 Yosys，**不进入主网表**。

### 3.3 重综合链（尽量复用 `yosys_abc.py`）

链路（与方案 §2 的候选链一一对应）：

| 步 | 工具/命令 | 复用情况 |
|---|---|---|
| ① 窗口 → BLIF | Yosys：`read_verilog window.v cells.v; hierarchy -top W; flatten; opt_clean; write_blif win.blif` | `_normalize_to_blif` 同型，需扩展为**多端口 + cells.v** |
| ② AIG + 重综合 | ABC：`read_blif win.blif; strash;` + `RESYN2_BUILTIN_SEQUENCE` + **`resub` / `resub -z`** + `print_stats; write_blif win_resyn.blif` | 序列已存在，**仅需追加 `resub` 两条** |
| ③ 回映射到 SKY130 | Yosys：`read_blif win_resyn.blif; abc -liberty <sky130>.lib; opt_clean; write_verilog win_mapped.v` | 需新写薄封装；库映射流程 `run_yosys_mapping` 已有先例 |
| ④ 局部 CEC（映射前） | ABC `cec win.blif win_resyn.blif` | `_run_abc_cec` 现成 |
| ⑤ 局部 CEC（映射后） | 原窗口 vs `win_mapped.v` → `check_mapped_blif_equivalence` | **现成** |
| ⑥ STA | 回填后由现有 OpenSTA 通道测量 | 现成 |

**建议在 ③ 之前先做 ④**：映射前 CEC 通过而映射后不通过，能直接把失败归因到"库映射/techmap"而非"重综合算法"，对论文的自检叙事有价值。

### 3.4 回填

1. 解析 `win_mapped.v` 得到新实例集合与网表连线。
2. 在 `mapped.v` 文本中：删除原窗口实例，插入新实例（**保持 `boundary_inputs`/`boundary_outputs` 网名不变**，仅重命名新实例的内部网以避免与外部网冲突，命名建议前缀 `rs_<patch_id>_`）。
3. 立即做结构自检：实例名唯一、无多驱动、无悬空。
4. 产出新的 `candidate_netlist_text`（与现有真实 STA 通道的输入格式一致）。

### 3.5 候选编码

复用 `PatchCandidate`，新增：

```python
cut_method = "structure_resynthesis"
gates      = 重综合后的实例名列表
resynth_stats = {
    "window_gates_before": int, "window_gates_after": int,
    "aig_nodes_before": int,    "aig_nodes_after": int,
    "depth_before": int,        "depth_after": int,        # 窗口级逻辑级数
    "abc_sequence": "strash;balance;rewrite;refactor;resub;...",
    "cec_pre_map": "pass|fail", "cec_post_map": "pass|fail",
}
```

`patch_id` 建议 `patch_S<root>_structure_resynthesis`，与现有 `patch_<root>_<method>` 命名一致。

### 3.6 ΔDepth：定义与采集点

**两个层次都报**（这是 S 的因果证据链核心）：

| 层次 | 定义 | 采集点 |
|---|---|---|
| 窗口级 $\Delta L_C$ | `logic_levels()` 在窗口子网表上，`boundary_outputs` 的最大级数 before→after | 步骤 ② 前后（BLIF 级）与 ③ 后（SKY130 级）各记一次 |
| 网表级 $\Delta L$ | `Netlist.logic_level(target_net)` 在全网表 before→after | 接受提交时（复用现有 `logic_level_before/after/reduction` 字段） |

**报告口径**（写入实验汇总）：`L_critical: 7 → 5, ΔL = −2, ΔWNS = +0.43 ns` 这种**三数并列**形式，而不是只报 ΔWNS。

> 注意：SKY130 HD 中大量单元是单级（`nand4`/`o22ai`/`xor2`），因此**网表级 ΔL 只可能由 S（拓扑改变）或 JOINT 产生，G 与 R 在原理上不可能产生 ΔL<0**。这句话本身就是 S 动机的干净论证。

### 3.7 拒绝条件与失败归因

| 触发 | 归因 | 建议去向 |
|---|---|---|
| 接口名称/位宽变化、多驱动、悬空 | 实现缺陷 | 记为 `S_interface_violation`，**不进 F1**（避免污染 F1 语义） |
| 映射前 CEC 失败 | 重综合不等价 | 归 **F1** |
| 映射前通过、映射后失败 | 库映射问题 | 记为 `S_techmap_mismatch`，单独统计 |
| 门数膨胀超限 | 面积/补丁过大 | 归 **F3**，但**阈值需为 S 单独设定** |

**F3 阈值问题**：现行 `max_patch_ratio = 0.15` 是相对**全局门数**，对 S 的窗口口径不适用（窗口本身就可能是全局的较大比例）。建议 S 用**相对窗口**的比值：`gates_after / gates_before > 1.2` 判 F3；或对 S 采用 `max_patch_ratio_S = 0.5` 的独立阈值。**这是必须先定的设计参数**，否则 S 会被 F3 大量误杀。

### 3.8 与 JOINT / S→G 的组合规则

- 第一版：$JOINT = R/G/B$ 既有组合，**S 独立成类**，不并入 JOINT（避免组合空间膨胀）。
- 额外允许一档 **S→G**：S 被接受后，对**同一窗口输出锥内**的新实例做一次 G 型尺寸寻优，候选数受 `candidates_per_iteration` 上限约束。
- 不在第一版枚举 $S\times R\times G\times B$。

---

## 4. 三臂对照实验设计（L1-b，精确规格）

### 4.1 三臂定义

| 臂 | 候选空间 | 候选排序 | `enable_feedback` | 命令行 |
|---|---|---|---|---|
| **Mixed-Fixed** | R/G/B/JOINT | 权重驱动（割代价+路径覆盖） | **False** | `--strategies R,G,B,J --joint-pairs k --enable-buffer --no-feedback` |
| **Mixed-Random** | R/G/B/JOINT | 随机打乱 | False | 同上 + `--random-order --seed {1,2,3}` |
| **FAECO-Adaptive** | R/G/B/JOINT | 权重驱动 | **True** | 去掉 `--no-feedback` |

**统一口径**：`--rounds 20`、`--period 0.5`、$w^{(0)}=(1,1,1,1,1)$、同一工具链、**同一运行批（同一日）**、候选级 STA 预算上限一致。

> 现有 `20260826_ablation_random_seed{1,2,3}` 的候选空间已是混合（B 7154/G 3114/R 1954）但**无 JOINT**，故不可直接充当 Mixed-Random；三臂必须重跑，不能拼旧数据。

### 4.2 记录要求

每臂每个电路必须落盘：结果 JSON（含 §2.6 全部新字段）+ `run_config.json`（argv/git SHA/工具链版本）+ 运行 `.bat`/`.sh`。**这是 OI-012 的整改项，不可省**。

### 4.3 先跑"能推翻主张的那一对"（自杀式测试）

**不要**先跑 pureG/pureB（那只回答候选空间）。优先级：

1. **Mixed-Fixed vs FAECO-Adaptive**——若二者无显著差异，则"Failure-Aware"不成立，后续 S 的论文叙事必须随之调整。这是**最可能推翻核心主张**的对照，必须最先做。
2. 之后补 Mixed-Random，用于区分"权重驱动排序"与"随机排序"的贡献。

### 4.4 判读标准（事先写定，避免事后解释）

| 结果 | 判读 |
|---|---|
| Adaptive 的 $N_{\text{STA-to-first-improvement}}$ 显著更低、最终 ΔWNS 不劣 | Failure-Aware 成立（价值定位=更快找到有效候选） |
| Adaptive 最终 ΔWNS 更高但 STA 次数更多 | 价值定位改为"更高上限"，但需说明预算代价 |
| 二者无差异 | **Failure-Aware 无独立贡献** → 论文核心贡献需改为"候选空间+排序"或补 S 作为主张主体 |

---

## 5. 实施顺序与验收

| 步 | 内容 | 验收标准（可证伪） |
|---|---|---|
| 0a | OI-011 定案（路径 A 或 B） | 3 个电路 sentinel 复跑能复现既有数字（或明确记录差异与原因） |
| 1 | C 的 rate 状态 + 更新规则 + 退化等价性测试 | 单测证明 $(\rho=0,\eta=1)$ 与现行 `+=1.0` **逐位相同**；264 测试全绿 |
| 2 | schema 扩展 + 命令归档 | 新跑一臂即可看到 §2.6 全部字段；目录内有 `run_config.json` |
| 3 | 三臂对照（先 1） | §4.4 判读表出结论，无论正负 |
| 4 | ΔDepth 采集填充 | `logic_level_*` 不再是 None/0；报告含窗口级与网表级两个 ΔL |
| 5 | S 候选生成器 | ① 窗口抽取/回填的结构自检通过率 100%；② 局部 CEC 通过；③ S 能产出至少一个 $\Delta L<0$ 且 $\Delta\mathrm{WNS}>0$ 的接受候选（否则 S 的动机未坐实） |
| 6 | S→G 两阶段 | 在同一窗口上 S 后 G 的增益 > 单独 S |

**第 5 步的"能推翻主张的测试"**：在 b06（库中无等价单元、G/B/R 均无解的历史最难电路）上跑 S。若 S 在 b06 上仍无严格改善，则"S 突破标准单元等价替换上限"这一主张**不成立**，必须如实改写而不是回避。

---

## 6. 风险清单

| 风险 | 影响 | 缓解 |
|---|---|---|
| 路径 A 移植后数字有漂移 | 主实验不可比 | sentinel 复跑 + 若漂移则如实记录并说明 |
| rate 状态引入后既有结论变化 | 论文数字需重跑 | 保留 $(\rho=0,\eta=1)$ 退化路径作对照；先跑 1 电路冒烟 |
| S 被 F3 大量误杀 | 有效候选进不了接受集合 | 先定 §3.7 的 S 专用阈值 |
| S 的面积/扇出膨胀 | 物理门控或 DRC 风险 | 门数守卫 + S 单独报告面积变化 |
| 窗口级 CEC 通过但全网表 SEC 失败 | 论文的 SEC 声明受威胁 | 保持"局部 CEC 候选级 + 网表级 SEC"两层，不可用局部 CEC 替代 SEC |
| 三臂中 Adaptive 无优势 | 核心主张需调整 | §4.3 的优先顺序 + §4.4 的判读表**事先**写定 |

---

## 7. 待用户裁定（阻塞项）

1. **OI-011 路径 A / B** —— 决定 §1 表的落点，阻塞步骤 0a 及其后全部。
2. **§3.7 的 S 专用 F3 阈值**（建议：窗口内比值 1.2，或 `max_patch_ratio_S = 0.5`）—— 不先定则 S 实现无法判定接受/拒绝。
3. **§2.3 的参数默认值**（$\rho=0.5$、$\eta=1.0$、加性权 $[1,8]$、$\lambda_c\in[0,2]$）—— 可先用默认值跑 1 电路冒烟，再定终值。
