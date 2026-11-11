# 预注册：post-CTS resizer 终点之后是否还有残余空间（P1′ 第二轮）

- 日期：2026-11-11
- 前置：`experiments/20261116_resizer_then_faecop/`（P1′ pilot：pre-CTS 变体终点之后有 +0.0786 ns 均值残余空间，PROMOTE=YES）
- 上游：`experiments/20261115_p1_resizer_vs_faeco/`（P1：FAECO-P 0/8 胜 post-CTS resizer）
- **本文件在任何 post-CTS 端点读数之前写定**；运行期修订只允许追加 §7，且必须标注时间与理由。

## 1. 为什么做这一轮

P1′ pilot 证明的是「在一个 **pre-CTS** `repair_timing` 变体终点之上」还有残余空间。
但那个变体比 P1 实际对手弱 0.19/0.21 ns（re-entry gap），所以它**不能回答**「在真正的 P1 resizer
（post-CTS 修复）之上还有没有余量」。本轮把 resizer 段换成 **post-CTS 修复**，端点流程其余部分保持不变。

## 2. 装置

| 项 | 值 |
|---|---|
| 电路 | s382、s641、s832（与 P1′ pilot 同三例，便于逐例对照） |
| 起点 | `experiments/20261016_r22_cut_ablation_v3/W1/<c>/mapped.v`，period 0.5 |
| resizer 段 | 标准 place 流程 → CTS（`clkbuf_4/8`，root `clkbuf_16`）→ `source setRC.tcl` → `repair_timing -setup` → `detailed_placement` → `write_verilog -remove_cells {tapcell}`（`export_netlist.py post-cts`） |
| 网表归一化 | `\\DFF_14/_0_` → `DFF_14`（与 P1′ pilot 同一变换；pilot 已单独验证：单元多重集/网络集合不变、FF 名 1:1） |
| 我方段 | `run_rf.sh`：FAECO-P，flag 与 P1′ pilot 的 RF 臂**逐字相同**（单补丁接受、`--physical-gate --physical-backend placed_ens --placement-utils 0.30,0.35,0.40`、`--seed 1`） |
| 端点 | `measure.py` → `rseco.routed_sta.run_routed_sta(..., skip_clock_tree=True)`：floorplan→place→**跳过 CTS**→route→RCX SPEF→独立 `sta`；util 0.30/0.35/0.40 三布局均值 |

**为什么跳过 CTS（仪器约束，不是选择性调参）**：导出网表已含时钟树；再跑 `clock_tree_synthesis` 会让
OpenROAD 直接 segfault。已在 s641 上做过三变体探针（`scratch/_probe_postcts.py`）：

| 变体 | returncode | 结果 |
|---|---|---|
| a) 原样（流程自建 CTS） | **139（segfault）** | 崩在流程内 |
| b) 跳过 CTS | **0** | `ROUTED_FLOW_OK`，RCX 提取 170 nets |
| c) 跳过 CTS + 去掉 `assign` | **0** | 同上（`assign` 不是原因） |

`skip_clock_tree=True` 只把 `clock_tree_synthesis / repair_clock_nets` 两行换掉，其余 Tcl 与默认流程**逐字相同**
（有回归测试 `PostCtsFlowTest`）。时钟按既有理想时钟约定处理（不 `set_propagated_clock` 到端点 STA），
**两个臂完全一致**。

臂：

| 臂 | 定义 |
|---|---|
| R_own | P1 归档的 post-CTS resizer 读数（三布局均值：s382 −0.8414 / s641 −1.1295 / s832 −1.0587），仅参照 |
| R′post | post-CTS 导出网表（归一化）→ 跳过 CTS 的标准流程 → 端点（**RFpost 的对照，同字节**） |
| RFpost | 同一网表 → FAECO-P → 同一端点（主臂） |

## 3. 判据（读数前写定）

- **H1 可行性（门）**：3/3 电路的导出网表能被重入流程并布线完成，`DRC=0`，产出 `routed.v` + `routed.spef`，
  且 STA 给出非空 WNS。任一例失败 ⇒ 记「post-CTS 终点不可重入」，H2 不判定。
- **H2 残余空间（主判据）**：`RFpost − R′post` 在 **≥2/3 例为正**，**且** 三例均值 **≥ +0.05 ns**。
  - 过门 ⇒ 可写「在我们的动作空间内，post-CTS resizer 终点不是局部最优，2–3 个单实例动作仍增加
    0.05–0.12 ns 量级」。
  - 不过门 ⇒ **停这条线**，如实记录「post-CTS 之后没有可复现的残余空间」，不调参重跑。
- **H3 成本（仅报告）**：我方段墙钟 / resizer 段墙钟；候选 STA 次数。
- **re-entry gap（必须报告）**：`R′post − R_own`。若任一例 |gap| > 0.15 ns ⇒ 触发声明条款：
  R′post 与原 resizer 终点不可互换，**结论只限 RFpost vs R′post 配对**，不得写「在 P1 resizer 之上仍有 +x ns」。

## 4. 读法约束（写死）

- 3 例 pilot，不是 8 例结论；扩样须另立预注册。
- 端点只有 WNS（`report_checks -path_delay max`），未测 TNS/功耗/面积；我方动作会让个别单元变大。
- 时钟树作为普通门存在于网表中、端点 STA 按理想时钟计时 ⇒ **两臂都忽略时钟树延迟**，
  这使读数接近「数据路径 WNS」，不得据此声称签核级时钟传播。
- 判据只允许比较 RFpost 与 R′post（同网表、同流程、唯一差别是我方补丁）。

## 5. 复现

```bash
# 1) post-CTS 导出（每例约 2 min）
.venv/Scripts/python.exe experiments/20261117_postcts_residual/export_netlist.py post-cts s382 s641 s832
.venv/Scripts/python.exe experiments/20261117_postcts_residual/_sanitize_names_postcts.py
# 2) 对照臂端点（3 例 × 3 布局，每例每次约 2–5 min）
.venv/Scripts/python.exe experiments/20261117_postcts_residual/measure.py --arms RprimePost
# 3) 我方段
bash experiments/20261117_postcts_residual/run_rf.sh s382 s641 s832
# 4) 主臂端点 + 判定
.venv/Scripts/python.exe experiments/20261117_postcts_residual/measure.py --arms RFpost
.venv/Scripts/python.exe experiments/20261117_postcts_residual/analyze.py
```

## 6. 与上一轮的关系

- 上一轮（pre-CTS 变体）结论**不因本轮改变**：它回答的是「变体终点之后有余量」。
- 本轮若 PASS，两句可以并列写；若 FAIL，则必须写「余量只存在于较弱的变体终点上，post-CTS 终点上未观察到」，
  这是更强的负面结论，也封掉整条 P1′ 路线。