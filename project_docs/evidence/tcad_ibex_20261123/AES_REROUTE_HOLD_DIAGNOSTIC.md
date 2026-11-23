# SKY130 AES 重布线后的 hold 归因

2026-11-24。AES 的 screened 对照共做了 18 次详细布线、寄生提取和 FF／TT／SS STA，正式端点全部因相对 hold 回退被拒。18 次均满足绝对 hold，最小余量为 +53.686389 ps，所有视图 hold TNS 为 0。零编辑重布线复现了 SS 的共同回退。对三项代表性违约，交叉读入 ODB 和 SPEF 复现了全部回退，并定位到最差 hold 路径上的时钟到达变化。

## 零编辑重布线

沿用 AES hold 合格起点 `ss_hold_targeted_v2b/6_final.odb`、冻结的原始 IO 约束、ODB 内嵌 guides、四线程 local DRT 和原矩阵的 RCX 与 Liberty。执行零编辑 DRT、RCX 和三个视图 STA。原矩阵的 `noop` 只对冻结布局重提取 RC，三个视图的 hold 值与原起点精确一致。新试验实际运行了 DRT，详细布线和提取完成，DRC 为 0，功能网表哈希与起点相同，面积变化为 0。原门按每视图 0.001 ps 容差记录 `SS:hold_regression`。运行入口见 [AES_ZERO_REROUTE_COMMAND.txt](AES_ZERO_REROUTE_COMMAND.txt)。

| 视图 | 冻结起点 hold WNS / ps | 零编辑重布线 / ps | 变化 / ps |
|---|---:|---:|---:|
| FF | 336.273898 | 336.273953 | +0.000056 |
| TT | 523.914856 | 523.914856 | 0.000000 |
| SS | 55.295768 | 54.618976 | −0.676792 |

零编辑的 DEF 有六条网发生变化，分别是 `_03312_`、`clk`、`clknet_0_clk`、`net255`、`net7927`、`net8407`，无组件位置变化。18 次旧评估也都改变了这六条未编辑网。对 DEF 的 NETS 条目作同样的空白规范化后，`clk` 和其余三条 `_03312_`、`net255`、`net7927` 在 18 次均与零编辑结果精确一致。`clknet_0_clk` 在 15 次与零编辑一致，例外是 `single/04`、`faeco/06` 和 `fixed/02`。零编辑说明即便功能网表无改动，同样的 local DRT 流程也会改变冻结起点的时钟走线与 hold。当前结果来自一轮零编辑运行。

## 代表性违约的寄生交叉验证

原起点、零编辑与全部 18 次评估的每视图最差 hold 路径一致。SS 的路径为 `key[35]` 经 `input57`、`_19297_`、`_19304_` 到 `u0.w[2][3]$_DFF_P_`。FF 和 TT 的路径为 `sa03_sr[5]$_DFF_P_` 经 `_17769_` 到 `text_out[29]$_DFF_P_`。这 18 次都没有改动上述最差路径的组合数据单元或数据连线。SS 的数据使用原 SDC 的虚拟输入时钟，捕获经过真实时钟树。FF／TT 的发射和捕获共享时钟根，分别经过 `clknet_3_0__leaf_clk` 和 `clknet_3_1__leaf_clk` 两条分支。SS 捕获也经过后一条分支。

复用原矩阵绑定的 OpenROAD 执行 12 次只读 STA。下表用 C 表示冻结起点，E 表示该候选。两字母的第一位是 ODB 来源，第二位是 SPEF 来源。每个视图的 CC 和 EE 都与原收据精确相等。全部四种组合均保留同一最差路径，hold TNS 均为 0。每组的四份寄生标注清单完全相同，均为 93 个未标注驱动、0 个部分标注驱动。

| 候选／视图 | CC hold WNS / ps | CE / ps | EC / ps | EE / ps | 仅换 SPEF 变化 / ps | 仅换 ODB 变化 / ps |
|---|---:|---:|---:|---:|---:|---:|
| `fixed/02` SS | 55.295768 | 53.686389 | 55.295768 | 53.686389 | −1.609379 | 0 |
| `fixed/05` FF | 336.273898 | 336.203676 | 336.273898 | 336.203676 | −0.070222 | 0 |
| `fixed/05` TT | 523.914856 | 523.806443 | 523.914856 | 523.806443 | −0.108413 | 0 |

`fixed/02` 的 SS 数据到达时间在九位小数报告中相同，仅换 SPEF 后捕获时钟到达晚 1.609564 ps，数据要求晚 1.609325 ps，解释了 WNS 的回退。此候选的时钟根网 `clknet_0_clk` 的布线与零编辑结果仍有差别，在 SS 下较零编辑再损失 0.932587 ps。

`fixed/05` 在 SS 较冻结起点改善 0.190514 ps。其 FF 和 TT 的两条相对 hold 违约来自捕获和发射端时钟变化不等。FF 的捕获与发射时钟分别晚 0.156582 ps 和 0.086665 ps，TT 分别晚 0.247895 ps 和 0.139773 ps。该候选的时钟根及两条分支的 DEF 条目与零编辑一致，提取的捕获分支 `clknet_3_1__leaf_clk` 总电容由 0.0792723 pF 升至 0.0793813 pF，SPEF 中与 `_20134_` 的耦合项增加 0.00000109 pF。交叉验证归因的是整份 SPEF 的效果，单个寄生元件的贡献仍未单独测量。

## 原 18 次评估的对照重算

保留原候选物理结果和 0.001 ps 容差，只把 FF／TT／SS 相对 hold 比较线换成零编辑重布线值。8／18 次评估能通过数值比较，对应 13 个不同编辑集中的 5 个单门编辑。三种方法的最大可见面积收益均为 11.2608 µm²，即起点 116507.9904 µm² 的 0.009665%。面积收益 33.7824 µm² 的六次三门评估仍有相对 hold 回退。`fixed/02` 在 SS 低 0.932587 ps，`fixed/05` 仍在 FF／TT 低 0.070277／0.108413 ps。

| 方法 | 评估中通过重算的次数 | 通过重算的旧试验编号 |
|---|---:|---|
| 单门贪心 | 4／6 | 01、02、04、06 |
| 固定批次 | 1／6 | 06 |
| FAECO | 3／6 | 02、04、06 |

两轮诊断没有重跑策略轨迹或候选 SEC。正式结果继续使用原起点与原门，三种方法的 AES 正式面积收益均为 0。

## 复现和原件

原矩阵位于 WSL `/home/toylog/faeco_tcad_sky_holdout_20261123/aes_matrix_v1`，使用 `config.json`、`control/receipt.json`、`noop/receipt.json` 和 `screened/{single,fixed,faeco}/` 下的逐试验记录。候选 DRT 日志读取的 `sky130hd/rcx_patterns.rules` 指向矩阵记录内的 `sky130hs/rcx_patterns.rules`，两路径 SHA-256 一致。诊断原件同父目录。

| WSL 原件 | SHA-256 |
|---|---|
| `aes_matrix_v1/config.json` | `bc62ef9ac0225aca50768bd1b243ae1311a2565c7863ad4183d29a23030002d9` |
| `aes_zero_reroute_diag_v1/noop/receipt.json` | `8cfbff74559103f990f73b39073efba3c08a7c6d15c6f7e686cc69052a466052` |
| `aes_zero_reroute_diag_v1/noop/layout_changes.json` | `84a4013eb98c02f6ef738ccc79043a5ffbd28a6dde98ecf25fb45af0a3dce174` |
| `aes_hold_cross_diag_v1/inputs.json` | `872d357715b8db8d60113e44b35f7a58bd6ad7aa04eb8ad661a9ae2db5c0afdd` |
| `aes_hold_cross_diag_v1/results.json` | `8894f60adb0bb8cda566f7dbc49a4adccbf2a9b750f70e59526892f6cdab404d` |

从仓库根目录在 WSL 运行交叉验证，输出目录为新目录。原件包含每项 STA 的 Tcl 和计时报告，单项超时 90 秒。

```bash
raw=/home/toylog/faeco_tcad_sky_holdout_20261123
bash code/scripts/run_with_timeout.sh 1200 taskset --cpu-list 0-5 python3 \
  project_docs/evidence/tcad_ibex_20261123/probe_aes_hold_cross.py \
  "$raw/aes_matrix_v1" "$raw/aes_hold_cross_diag_replay"
```
