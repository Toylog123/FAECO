# P1′ 第二轮：post-CTS resizer 终点之后还有残余空间吗？

- 日期：2026-11-11
- 预注册：`PREREGISTRATION.md`（读数前写定）
- 上一轮：`experiments/20261116_resizer_then_faecop/`（pre-CTS 变体终点，H1/H2 PASS，mean +0.0786 ns）
- 上游：`experiments/20261115_p1_resizer_vs_faeco/`（P1：我们的机制 0/8 胜 post-CTS resizer）

## 1. 问题

上一轮证明的残余空间存在于一个 **pre-CTS** `repair_timing` 变体终点上，而那个变体比 P1 实际对手弱
0.19/0.21 ns（re-entry gap），所以它不能回答：**在真正的 P1 resizer（post-CTS 修复）之上还有没有余量**。
本轮把 resizer 段换成 post-CTS 修复，其余装置不变。

## 2. 装置（与预注册一致）

| 项 | 值 |
|---|---|
| 电路 | s382、s641、s832（period 0.5） |
| resizer 段 | 标准 place 流程 → CTS → `setRC` → `repair_timing -setup` → `detailed_placement` → `write_verilog` |
| 网表归一化 | `\DFF_x/_0_` → `DFF_x`（与上一轮同一变换；上一轮已验证单元/网络/FF 一一映射） |
| 我方段 | FAECO-P，flag 与上一轮 RF 臂逐字相同（`--physical-gate --physical-backend placed_ens --placement-utils 0.30,0.35,0.40 --seed 1`） |
| 端点 | `run_routed_sta(..., skip_clock_tree=True)`：place → **跳过 CTS** → route → RCX SPEF → 独立 `sta`；三布局 0.30/0.35/0.40 均值 |

**跳过 CTS 的理由**（探针，不是选择性调参）：导出网表已含时钟树，再跑 `clock_tree_synthesis` 会让
OpenROAD 直接 segfault。s641 三变体实测：a) 原样 **rc=139**；b) 跳过 CTS **rc=0**（RCX 170 nets）；
c) 跳过 CTS + 去掉 `assign` **rc=0** ⇒ 双重建树是原因，`assign` 不是。
`skip_clock_tree=True` 只替换那两行，其余 Tcl 与默认流程逐字相同（回归测试 `PostCtsFlowTest`），
两个臂完全一致。

## 3. 读数（三布局均值，WNS ns）

| 电路 | R′post @0.30 | @0.35 | @0.40 | **均值** | RFpost @0.30 | @0.35 | @0.40 | **均值** | **RF−R′** | R_own(P1) | gap |
|---|---|---|---|---|---|---|---|---|---|---|---|
| s382 | −0.8101 | −0.8218 | −0.8419 | **−0.8246** | −1.0022 | −0.9784 | −0.9911 | **−0.9906** | **−0.1659** | −0.8414 | +0.0168 |
| s641 | −1.1092 | −1.1290 | −1.1024 | **−1.1135** | −1.6547 | −1.6583 | −1.6250 | **−1.6460** | **−0.5325** | −1.1295 | +0.0160 |
| s832 | −1.1460 | −1.0912 | −1.1880 | **−1.1417** | −1.6435 | −1.6160 | −1.6292 | **−1.6296** | **−0.4879** | −1.0587 | −0.0830 |

- 全部 18 次布线 `DRC=0`、无 segfault。
- **re-entry gap 均值 −0.0167 ns，逐例 +0.0168 / +0.0160 / −0.0830，全部 |gap| < 0.15**
  ⇒ 本轮**没有触发**声明条款：R′post 忠实复现了归档的 P1 resizer 终点
  （这一点比上一轮的 pre-CTS 变体好得多，后者 gap 为 −0.19/−0.21）。

## 4. 判定

| 门 | 结果 |
|---|---|
| H1 可行性（3/3 重入、DRC=0、产出 routed.v+spef） | **PASS** |
| H2 残余空间（≥2/3 为正 且 均值 ≥ +0.05 ns） | **FAIL**（positive **0/3**、均值 **−0.3954 ns**） |
| H3 成本（仅报告） | s382 218 / s641 153 / s832 148 次候选 STA；接受 2/1/1 |
| **PROMOTE** | **NO** |

**结论：在真正的 post-CTS resizer 终点之上，我们当前的机制没有残余空间，反而把终点做差**
（−0.166 / −0.532 / −0.488 ns，三例一致为负）。上一轮 pre-CTS 变体上的正转移**不迁移**到 post-CTS 终点。

## 5. 为什么失败（诊断，比结论更重要）

被接受的补丁只有 1–2 个单门改尺寸，但布局档判断的增量很大：

| 电路 | 接受补丁 | 布局档 `physical_delta` | 布线后端点变化 |
|---|---|---|---|
| s382 | G `_059_`、G `_057_` | +0.1217、+0.0635 | −0.1659 |
| s641 | G `_091_`（a2111oi_0→4） | **+0.6090** | **−0.5325** |
| s832 | G `_140_`（and2_0→2） | +0.0577 | −0.4879 |

**是不是「双重建 CTS」造成的假象？不是。** 直接用 placed 流程测 s641 的两份网表（`scratch/_probe_postcts_judge.py`）：

| 流程 | 输入网表 | 加一个 `a2111oi_0→4` 后 | 差 |
|---|---|---|---|
| 原样（流程自建 CTS） | −2.1035 | −1.4666 | **+0.6369** |
| 跳过 CTS | −2.0723 | −1.4536 | **+0.6187** |

⇒ 布局档估算器**真的认为**这个动作值 +0.6 ns，与 CTS 无关。

**真正的冲突是档位之间的绝对水平差**：同一份 post-CTS 网表，placed 档判 −2.10、
布线后端点只有 −1.11（**差约 1 ns**）。布局档在该网表上既悲观（绝对水平），
其 +0.6 ns 的改善在布线后翻转成 −0.53 ns（符号）。因此**布局档判断在这类终点上不是可迁移的代理**：
它把「弱驱动单元在估计线载下的延迟」当成主要矛盾，而布线后的实际瓶颈与重布局后的落位才是决定项。

这正是上一轮 pre-CTS 结果不能外推的原因：pre-CTS 变体的布局档读数离布线后较近，单门动作小步累积
（+0.05/+0.04/+0.03 逐补丁）能迁移；post-CTS 终点上机制会挑出布局档增益极大的单步动作，
而这类动作的迁移性最差。

## 6. 能写 / 不能写

**能写**

- 在 post-CTS resizer 终点上，本文机制的接受补丁使布线后 WNS 在 **3/3 电路变差**，均值 **−0.395 ns**；
  pre-CTS pilot 的正转移不迁移。
- 本轮的对照端点忠实：R′post 与归档 P1 resizer 端点差 +0.017/+0.016/−0.083 ns（|gap|<0.15）。
- 布局档（`estimate_parasitics -placement`）判断在 post-CTS 终点上不可迁移：绝对水平比布线后低约 1 ns，
  且把 +0.62~+0.64 ns 的布局档改善翻成 −0.53 ns 的布线后回退。

**不能写**

- 不能写「post-CTS 终点没有残余空间」——本轮只检验了**本文机制的动作空间与判断器**，
  没有检验其他动作空间（例如批量/更强动作）在 post-CTS 终点上的表现。
- 不能写「resizer 已经最优」——P1 与 P1′ 都只覆盖 3–8 个 ISCAS89 小例、只测 WNS。
- 不能说「pre-CTS pilot 的结论作废」——它回答的是另一个总线（较弱变体终点），结论仍然成立。

## 7. 对路线的影响

P1′ 这条线（「把 resizer 当内层优化器、我们做外层补丁」）在**当前机制**下已经封口：

1. pre-CTS 变体终点：有 +0.0786 ns 残余（pilot PASS）；
2. post-CTS 终点（= 真正的 P1 对手）：残余为**负**（本轮 FAIL）。

若还要继续这条线，必须先解决**判断器与端点的一致性**（例如用布线后档做判断，或限制动作幅度），
而不是继续换动作空间。该前提已写入 `project_docs/FAECO_ROADMAP.md` 的 P1′ 段。

## 8. 复现

```bash
.venv/Scripts/python.exe experiments/20261117_postcts_residual/export_netlist.py post-cts s382 s641 s832
.venv/Scripts/python.exe experiments/20261117_postcts_residual/_sanitize_names_postcts.py
.venv/Scripts/python.exe experiments/20261117_postcts_residual/measure.py --arms RprimePost
bash experiments/20261117_postcts_residual/run_rf.sh s382 s641 s832
.venv/Scripts/python.exe experiments/20261117_postcts_residual/measure.py --arms RFpost
.venv/Scripts/python.exe experiments/20261117_postcts_residual/analyze.py
# 期望：H1 PASS / H2 FAIL / mean_delta −0.3954 / PROMOTE=NO
```

## 9. 边界

- 3 例 pilot（s382/s641/s832），只测 setup WNS；未测 TNS/功耗/面积/DRC 之外的签核项。
- 端点流程跳过 CTS（输入网表已含时钟树），时钟按既有理想时钟约定处理，两臂一致；
  这不是签核级时钟传播。
- resizer 段仍是「标准 place 流程 + `repair_timing`」，不是商业工具；R_own 取自 P1 归档。
- 布局档读数来自 `estimate_parasitics -placement` 的估计线载，不是签核 RC。