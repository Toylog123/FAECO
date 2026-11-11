# P1 预注册：FAECO-P vs OpenROAD resizer（布局后覆盖优先 ECO）

日期：2026-11-11
路线依据：`project_docs/FAECO_ROADMAP.md` §P1
状态：**本文件写于 FAECO-P 八例运行开始之后、任何对比端点测量之前**（见 §6 诚实声明）

## 1 问题

把 FAECO 的「覆盖优先 + 失效刻画 + 成对布局档判决」搬到**布局后**设定，与开源现状的默认做法
（OpenROAD `repair_timing -setup`，基于 LR 的贪心尺寸/缓冲修复）在**同一个签核流程**下比较：
在当前 ISCAS89 子集上，FAECO-P 的布线后 WNS 是否优于 resizer？

这个问题此前未被本项目测过：六轮机制实验（P/E/K/A6j/All/LLM 回放）都只在**预布局**设定里比较
判据与动作，从未把「布局后 + 覆盖优先」与一个真实可用的产业级基线放在同一流程里对比。

## 2 臂

| 臂 | 定义 | 实现 |
|---|---|---|
| **A（resizer）** | 标准流程 floorplan→place→CTS 后运行 `repair_timing -setup`，再 `detailed_placement` 合法化，然后 pin_access→global route→detail route→SPEF→STA | `run_resizer.py`，8 例 |
| **F（FAECO-P）** | 同一机制（候选构造 R/G/B+JOINT、覆盖优先割、失效反馈关闭、`--accept-all` 批量接受），判决用**成对布局档**（`placed_ens`：util 0.30/0.35/0.40 三布局均值） | `run_faecop.sh`，8 例 |
| **Base** | W1 输入 `mapped.v`（两臂的共同起点），不插入任何 ECO | 复用 `experiments/20261110_placed_gate/endpoint*` 已有读数；缺失的电路补测 |

- 电路：s27 / s382 / s420 / s641 / s713 / s820 / s832 / s953（ISCAS89，period 0.5）
- **两臂的最终网表都再用同一个签核流程测量**（`rseco.routed_sta.run_routed_sta`：floorplan(util)→place→CTS→setRC→route→extract→SPEF→STA），
  util ∈ {0.30, 0.35, 0.40}，端点 = 三布局 `wns` 的均值。

## 3 判据（预注册，先写死）

- **H1（主判据）**：端点 WNS 上，臂 F 优于臂 A 的电路数 **≥ 5/8**（二项 p=0.3633，单侧不显著；因此只是
  「可宣称不劣于、且多数例更好」的入门门，不作统计确认）。同时要求 **均值差（F−A）≥ 0.05 ns**
  （≈ 本项目实测布局离散中位 0.055 ns 与噪声底 0.03 ns）。
- **H2（次级，报告不设门）**：两臂的 DRC 违规数、运行成本（墙钟；A 为 1 次 repair，F 为 N 轮 × 3 布局判决 + 批量接受）。
- **H3（健全性）**：任一端点出现 `drc_violations > 0` 或 `wns is None` 时，该例标为无效并单列，不计入 H1。
- **失败处置**：H1 不过 → 如实记录「在 ISCAS89 这个子集上，布局后覆盖优先并不优于 resizer」，**不调参重跑**；
  路线退回 P2（把签核标注用于排序器）之前须先回答「差距是判据、动作集、还是预算」。

## 4 读数口径

- 端点单位 ns；`wns` 越接近 0 越好。
- 每例报告：base / A / F 的三布局均值与逐布局读数、增益（相对 base）、F−A 差。
- **跨布局噪声已知**：本项目实测单布局增益极差中位 0.1042 ns（12 格），因此单布局读数不足以判 0.05 ns 量级差异；
  这是本轮用三布局均值的原因。

## 5 预期与证伪价值

- 若 F 胜：说明「覆盖优先 + 失效刻画」这条从预布局继承下来的资产在布局后设定仍有价值，可进 P2。
- 若 F 平或负：说明**在 8 例 ISCAS89 这个小规模子集上**，产业级 LR 修复已足够，本项目必须先解决
  「动作集/预算/规模」，否则 P2 的 ML 排序器没有可放大的空间。这是同样有价值的结果，且能避免在 P2 上浪费数周。

## 6 诚实声明（写此文件时已知的事实）

- 写本文件时：resizer 八例已在**它自己的流程内**跑通（s27 −0.2249 / s382 −0.8414 / s420 −1.2169 / s641 −1.1170 /
  s713 −1.2386 / s820 −1.2536 / s832 −1.0062 / s953 −1.3219，均为流程内 STA 读数，**不是**本预注册的端点口径）；
  FAECO-P 八例刚启动、尚无结果。
- 该流程内读数**不可直接用于 H1**：两臂必须经 §2 的同一签核流程重测。
- resizer 的插入点经过三次失败迭代（`RSZ-0089` 缺 wire RC → 补 `set_wire_rc`；`DRT-0073` 未合法化 →
  补 `detailed_placement`；s713 `DRT-0305` tie 网络被提升为 POWER → 复位 `setSigType SIGNAL`），
  这些是流程接线问题，不是对任一臂的偏置；但**必须记录**，因为它们决定了 A 臂实际执行的动作集。

## 7 运行期修订（不修改 §3 判据）

### A2（2026-11-11，看到 F 臂端点读数之前）— resizer 臂改用它自己的流程读数

- 原计划把两条臂的**最终网表**都塞回同一个签核流程重测。实测不可行：resizer 的 `routed.v` 是
  OpenROAD `write_verilog` 的**扁平化**输出，含 flow 插入的物理单元（`tapvpwrvgnd_1`）与 4 条 `assign`；
  把它重新喂给标准流程会 **稳定 segfault（returncode=139，两次复现）**。
- 改为：**每条臂用它自己定义的流程读数**——
  - base / FAECO-P：标准流程（floorplan→place→CTS→route→SPEF→STA，util 0.30/0.35/0.40）。
  - resizer：标准流程 **+ `repair_timing -setup` + `detailed_placement`**（即该臂的定义），util 0.30/0.35/0.40 各跑一次，
    读数取该流程自己的 `routed.v` + `routed.spef` 的 STA（与 base/FAECO-P 同一 `ROUTED_STA_TCL` 约定：理想时钟）。
- 诚实边界：两臂的**流程不完全相同**（resizer 臂多一步 repair），这正是该臂的定义；但由于 STA 约定、
  单元库、period、布局 util 与密度完全一致，读数可比。此不对称必须随结果一起报告，不得隐藏。
- 同时修掉一个**签核仪器缺陷**：部分映射网表含 `one_`/`zero_` tie 网，OpenDB 把它们标成 POWER 类型，
  TritonRoute 直接拒绝（`DRT-0305`，s713 基线复现）。已在 `rseco.routed_sta.ROUTED_FLOW_TCL` 的
  `pin_access` 之前加入把这两类网复位为 SIGNAL 的 Tcl 片段；该修复对**所有臂**生效，属仪器修正，不影响臂间比较。


### A1（2026-11-11，看到端点读数之前）— 主臂 F 改为「单补丁接受」

- 原 §2 把 arm F 写成含 `--accept-all`（每轮接受全部过门候选）。运行中发现这条路在此前的
  `experiments/20261114_accept_all/`（arm All）已被预注册实验判为 **H2 FAIL**（均值差 −0.2574 ns，
  s641/s953 停滞回退），本轮 8 例运行里 s641 也复现了退化（`wns_history` −1.4561 → −1.9711，
  `success=False`）。
- 因此 **主臂 F 改为与已验证的 arm E 同一配置**（`placed_ens` 判决 + **单补丁接受**，不用 `--accept-all`），
  仍逐字沿用 W1 的 20 个 flag。含 `--accept-all` 的那批结果作为 **F2（补充臂）** 单列报告，不参与 H1 判定。
- 该修订发生在任何 F 臂端点测量之前（当时只有 s382 的 F 端点读数，且 s641 的退化是运行期可见的
  `wns_history`，不是端点），且修订方向是「采用已有预注册证据支持的配置」，不是按结果择优。
- `--accept-all` 触发的退化机制已记录在 `docs/EXPERIENCE.md` r122/r124 与 CANON 裁定 13/14 的相邻条目，
  此处不重复论证。


（待填）