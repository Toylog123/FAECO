# OI-077 触发器动作接入方案：就地展开（unfold），不改检查器（2026-11-03）

状态：**已实施（2026-11-03 r113）**，结果见 `experiments/20261103_ff_unfold/REPORT.md` 与 OI-077 结案段
关联：`project_docs/OPEN_ISSUES.md` OI-077、`LOGS.md` LOG-20261102-17/18/19、LOG-20261103-01

## 1. 结论

不做「放宽等价检查器」，也不止于「修实例名正则」。第三条路：

> 把触发器动作从**改 helper 子模块**改成**在目标模块里就地展开（unfold）该实例**——
> 把一个 `dff DFF_k (...)` 实例换成等价的 `sky130_fd_sc_hd__dfxtp_4 DFF_k (...)`，
> helper 模块一字不动。

这样 `_scoped_module_pair()` 的「非目标模块必须字节不变」这条不变式**不需要动**，
修改仍然只发生在被证明覆盖的顶层模块内。

## 2. 实测证据（`scratch/oi077_unfold_probe.py`，真实网表 s27，0.67 族）

| 判定 | 结果 |
|---|---|
| 现行 FF_SUBMOD（全文 `dfxtp_1→dfxtp_4`） | 被拒：`Non-target helper module changed`（复现 r111 的失败） |
| 逐实例展开 | **通过同一个检查器**（helper 字节不变） |
| 展开前后实例集合 | 相同（n=11，其中 dff 实例 3 个） |
| 连接差异（除 `CK→CLK` 引脚名） | **无**；唯一变化是 cell_type `dff → sky130_fd_sc_hd__dfxtp_4` |
| 展开后残留 dff 实例 | 0（helper 定义保留、变为未引用） |

0.67 族 helper 的形状（实测，三例一致）：

```
module dff(CK, Q, D);
  input CK; wire CK;  output Q; wire Q;  input D; wire D;
  sky130_fd_sc_hd__dfxtp_1 _0_ (.CLK(CK), .D(D), .Q(Q));
endmodule
```

实例用**命名连接** `.CK() .D() .Q()`，且 D/Q 引脚名与库单元相同 ⇒ 展开只是一次
`cell_type` 替换 + 一个引脚改名，可证明保持连接与功能。

## 3. 为什么不选另外两条

**A. 放宽 `_scoped_module_pair`（否决）**
该函数把 helper 当"共同定义"参与证明；改 helper 后若仍只在顶层做等价，
实际证明域比声明域小（静默少证）。要放开就必须把证明域改成**整网表含 helper**，
重做证明器 + 重跑 30 例 SEC 回归。收益仅是"允许改共享时序元件"，而
"我放宽了自己的安全网"在审稿里极难辩护。

**B. 只修 `_INSTANCE_LINE_RE`（不够）**
正则只解决"STA 报告里的含点号实例名能不能被认出来"（0.70 族）。
0.67 族（论文族）的触发器**根本不在 `cells` 里**：`gate_sizing._CELL_INST_RE`
只吃 `sky130_fd_sc_hd__\w+`，`dff` 这种 helper 实例解析不出来，
所以 `by_inst` 里没有触发器，`_SEQUENTIAL_CELL_RE` 那条追加逻辑永远空转，
最后才落到"改子模块"的兜底分支——死结不在正则。

**C. 先把网表预展开再重跑（备用）**
等于换输入族，与既有 1.29 ns 矩阵不可比，只能当兜底，不能当主路径。

## 4. 改动点（5 处，全部开关保护，默认关）

| 位置 | 改动 |
|---|---|
| `code/src/rseco/gate_sizing.py` | 新增 helper 实例解析（`dff` 等"非顶层、体内恰有一个 sky130 时序原语"的模块），产出 `Cell(instance, 'dff', pins={'CK','D','Q'})`；**不改**现有 `_CELL_INST_RE` |
| `code/src/rseco/real_wns.py` 新增 `_unfold_helper_seq()` | 形状守门：helper 体内必须只有端口声明 + 一个 `dfxtp_{1,2,4}` 实例且 `.CLK/.D/.Q ↔ CK/D/Q` 一一对应，否则 **fail closed** 记 `F2_boundary_invalid: unsupported helper shape` |
| `real_wns.py:2701`（`if self.enable_ff_resize:` 分支） | 把 `FF_SUBMOD` 换成 `FF_UNFOLD`：**一个**候选、`patch_size = n_unfold`、`critical_rank = 0`；按 scope 选目标实例（见 §5） |
| `real_wns.py:1659`（`elif kind == "FF":`） | 新增 `__mode__ == "unfold"` 分支调用上述函数；旧的 `submodule` 分支保留但不再使用（可留作负面对照） |
| `code/scripts/run_outerloop_real_wns.py` | 新增 `--ff-scope {cone,all}`（默认 `cone`）；`--enable-ff-resize` 语义不变（默认关 ⇒ 既有族逐位复现） |

守门沿用现有 s27 基准：`--enable-ff-resize` 关闭时 s27 必须仍为 −0.18 / 49 次 STA。

## 5. 组合动作的口径（这是关键设计选择）

实测已知：**全升 > 单点**（净 +0.3615 vs +0.2158，1.67 倍），说明"要么一起升、要么不升"。
但"全设计"在 b18（7.57 万单元）上没有意义（面积 +10.71% 是 ISCAS89 小例的数）。

因此把动作定义成 **cone 边界的时序单元集合**：

- `cone`（默认）：Q 网 ∈ `patch.boundary_inputs` 或 D 网 ∈ `patch.boundary_outputs` 的触发器，
  典型 2–6 个 —— 正是"关键路径的起点与终点"；
- `all`：全设计所有触发器（只有小例用），保留为对照/消融。

一个候选 = 一次原子提交，`patch_size = n`，不做逐实例枚举（逐实例会被 beam 截断，r110 已证）。

## 6. 实验设计（先小后大）

1. **守门**：`--enable-ff-resize` off vs on，s27 → 逐位相同（−0.18 / 49）。
2. **动作定义对照（8 电路 × 3 臂）**：W1（基线）/ W1+`cone` / W1+`all`，
   同 20 轮、同 500 次候选 STA、同随机源。
   报表：逐例 ΔWNS、超带数、净额、候选 STA 次数、同库面积和。
3. **功能**：每例终点网表跑现有独立 SEC（与论文同一路径），要求 8/8 无未证明点。
4. **物理**：取终点网表对做固定布局四数（`run_eco_phys_samelayout.sh` 复用），
   确认理想档增益在布线后是放大（期望 2.0–2.9 倍）还是衰减。
5. **判据**：只有 (3) 全过且 (2) 至少 4 例超带，才写"接入后增益"；否则仍按现在的"缺口"写法。

## 7. 风险

| 风险 | 处理 |
|---|---|
| 升驱动不改变 CK→Q 固有延迟，收益全靠输出 slew | 用物理档验；理想档若只有 4/8 正，就如实写"选择性可用" |
| 全升改变每个 FF 的 CK 引脚电容，理想时钟看不见 | 物理档必须走 CTS 后读法；论文并列"理想时钟下可能偏乐观" |
| 面积 +2.12–10.71%，远高于 W1 的 0.27–4.92% | 面积与 ns 同列报；不写"零成本" |
| 大 patch 候选可能被 proxy 排序压到最后 | FF 行沿用 `critical_rank=0 / strategy_rank=0`，并检查 beam 是否截断 |
| 展开后 helper 变未引用，等价器/流程是否接受 | 已实测：检查器通过；物理流程 `flatten` 后无影响，需在首次物理档确认 |

## 8. 工作量与收益

- 代码：约 120 行（含守门与解析），1 天。
- 计算：8×3 臂约 3–4 h；SEC 与物理档另 3–4 h。
- 若 +0.3615 ns 能在搜索内兑现：1.29 → 约 1.65 ns，与 OpenROAD 的 1.81 倍收窄到约 1.4 倍，
  这是目前唯一能真正抬高上限的抓手；否则把"动作集完备性"钉成一条可复现的负结果。

## 9. 决策记录

- 2026-11-03 实施：`--ff-scope {cone,all}`；`cone` 结果 1.29→1.68 ns、超带 5/8→7/8、SEC 3/3、面积 +2.45%–3.18%；`all` 同终点但 STA +21.6%、面积 +7.37% ⇒ 采用 `cone`。

- 2026-11-03：提出"就地展开"方案，并以真实网表实测三判定（见 §2）。
  未改生产代码，未动论文。等待批准后再实施。

**禁止**：为让"全升"通过而放宽 `_scoped_module_pair`；用预展开网表另起一族来冒充同族增益。
