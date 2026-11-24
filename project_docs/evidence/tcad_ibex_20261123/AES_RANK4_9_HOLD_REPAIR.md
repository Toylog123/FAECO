# SKY130 AES 排名 4–9 六门的 hold 归因与修复

2026-11-24。对象是正式固定批次和 FAECO 都在窗口末端截断、随后在线下完成重试的同一个六门候选。六个实例为 `_11178_`、`_11724_`、`_12777_`、`_12929_`、`_13098_`、`_13122_`。它在冻结起点上实际回收面积 67.5648 µm²，独立全块 DRC 与天线合格；FF 和 TT 相对 hold 分别回退 0.049849／0.077660 ps，SS 余量改善 0.442979 ps。三个视图均满足绝对 hold。此前通过的六门合并试验使用另一组动作。[原六门后验结果](AES_PROTECTED_ONLINE_REPORT.md)

## 路径与寄生归因

以正式已接受的排名 4–6 三门作 C，以该六门候选作 E。每个视图交叉读取 C／E 的 ODB 与 SPEF，以下两字母依次表示 ODB、SPEF 的来源。12 次 STA 严格复现对应的两份原收据。FF／TT 最差路径始终为 `sa03_sr[5]$_DFF_P_` 到 `text_out[29]$_DFF_P_`，SS 为 `key[35]` 到 `u0.w[2][3]$_DFF_P_`。所有 hold TNS 均为零，寄生标注均为 93 个未标注驱动、0 个部分标注驱动，名单逐组相同。

| 视图 | CC hold WNS / ps | CE / ps | EC / ps | EE / ps | 仅换 SPEF 的变化 / ps |
|---|---:|---:|---:|---:|---:|
| FF | 336.273953 | 336.224049 | 336.273953 | 336.224049 | −0.049905 |
| TT | 523.914856 | 523.837196 | 523.914856 | 523.837196 | −0.077660 |
| SS | 55.906613 | 55.738747 | 55.906613 | 55.738747 | −0.167866 |

SPEF 更换使 FF／TT 发射时钟提前 0.007927／0.023365 ps，同时捕获时钟延后 0.041842／0.054121 ps。数据到达提前 0.007928／0.023365 ps，要求时间延后 0.042022／0.054300 ps，二者共同解释了余量回退。SS 数据到达不变，捕获时钟延后 0.167608 ps；原始三门所留的 SS 余量使六门仍通过相对冻结起点的 SS 门。

13 条观察路径网的 SPEF 电阻边和阻值在节点名称归一化后逐项相同。出现电容差异的是三条时钟树网。捕获分支 `clknet_3_1__leaf_clk` 的总电容增加 0.0000792 pF，其中地电容增加 0.000074512 pF，提取的 `net8139` 耦合项增加 0.000004662 pF。整个 SPEF 的作用由交叉 STA 复现，并有路径时钟差作证据。单个几何段的电容贡献没有被单独替换。

## 等面积替换

选择用 `_21033_` 替换 `_13098_`，保留其他五门。以 DEF 的同层路由中心线距离筛查，`_13098_` 相连的 `net7951` 和 `net8215` 的改动段距捕获分支均为 0.34 µm，距耦合邻网 `net8139` 分别为 1.70 和 1.36 µm。其余两个新增单元的改线距捕获分支至少约 76 µm。此前单门物理结果给出 `_21033_` 的独立选点依据，它使 FF／TT 发射支路电容增加 0.0001006 pF。同一零编辑重布线口径下，FF／TT hold 分别改善 0.063172／0.099032 ps，SS 完全相同。

沿用原失败六门留存的四条已确定信号邻网 `_01220_`、`net4840`、`net8222`、`net8407`，以及原单门 donor 改动过的 `net8148`。第一次只清除 18 条直接编辑网和这五条有据邻网，其他 15,634 条网含时钟均锁定。四线程详细布线绑定 CPU0–5，保留一次内部 pin access。DRT／检查／RCX 单次限时 240 秒，三角 STA 各 180 秒，SEC 210 秒。沿用每视图 36 ps setup WNS 损失预算、FF／TT／SS 各 360／360／27049.177334 ps 的 setup TNS 损失预算，以及绝对 hold 合格和相对 hold 容差 0.001 ps。状态恢复后的独立全块 DRC、天线和 SEC 同样验收。若首趟给出新的可归属非时钟 DRC 邻网，最多作一次同动作局部重布线重试。修复独立于此前正式计时结果。

### 第一次物理尝试即通过全部门

实测回收 **67.5648 µm²（0.057992%）**，与失败六门的面积相同。23 条实际改线与计划完全一致，15,634 条固定线路与组件位置保持。一次 DRT、RCX 和三视图 STA 均完成，恢复 `ROUTED` 后的独立全块 DRC 与天线均为零。SEC 11,089 已证、0 未证，候选网表 SHA-256 为 `fc9f07b315a1b8e7adc85a401a82554316f5566031d3321395633499c81f21b1`。端点实测用时 137.851 RAW 秒，含 18.863 秒 SEC。

| 视图 | hold WNS / ps | 相对冻结起点的 hold WNS 变化 / ps | setup WNS 变化 / ps | setup TNS 变化 / ps |
|---|---:|---:|---:|---:|
| FF | +336.337069 | +0.063172 | +0.070610 | 0 |
| TT | +524.013555 | +0.098699 | −0.155875 | −31.106229 |
| SS | +55.949023 | +0.653255 | +1.007194 | +268.755684 |

三个视图的 hold TNS 均为零。TT 新增两处负 setup 端点，分别是 `sa13_sr[4]$_DFF_P_/D` 和 `sa30_sr[7]$_DFF_P_/D`。SS 新增一处 `text_out[83]$_DFF_P_/D`，FF 为零。原 setup WNS/TNS 预算各角均满足。

失败六门与修复六门各做三视图高精度路径复检，实际最差路径身份保持。FF／TT 的 hold 分别改善 0.113021／0.176359 ps，发射时钟分别延后 0.080168／0.126958 ps，捕获分别提前 0.032008／0.048339 ps。SS 数据到达时刻相同，捕获时钟提前 0.210046 ps，hold 改善 0.210276 ps。捕获分支总电容恢复到 0.0792723 pF，原先的 +0.0000792 pF 增量完全消失；发射分支新增 +0.0001006 pF。13 条路径网的电阻记录保持。修复证据覆盖这次同时撤回和补入的干预。

## 原件与入口

原始目录均在 WSL `/home/toylog/faeco_tcad_sky_holdout_20261123`。

| 原件相对路径 | SHA-256 |
|---|---|
| `aes_protected_online_censored_retry_v1/retry/receipt.json` | `7bd01fe05b63425be40f034319470d132385d4d17486cbfadc6afe329b528943` |
| `aes_rank4_9_residual_cross_v1/results.json` | `1c0eb2da40f203a324269678f5c0cd0ef293946f7527f3396a2bcefcd5c460a9` |
| `aes_rank4_9_residual_cross_v1/path_net_cap_deltas.json` | `4dec64b1c6f0ce551961d3c9737229f6be409a1385c8c8c9cb91fb1b18c9bd2b` |
| `aes_rank4_9_residual_cross_v1/path_net_resistance_audit.json` | `e19aa6243ab48f939baee236fcd6e94fdfd3ef8b7b19d841922de272c739376d` |
| `aes_rank4_9_donor_replace_13098_v1/repair_plan.json` | `76890f35c807ae7129f4f0ffc34716a2ad9320cd89b10c8d5f2069767f23c269` |
| `aes_rank4_9_donor_replace_13098_v1/result.json` | `f9609181296bcf41b959a01efb9a2a93cc6c0a44bb9d156d28c8762879ef6d69` |
| `aes_rank4_9_donor_replace_13098_v1/candidate/sec/receipt.json` | `e5305b4d1a89ff53d060af7f3f0918f63cbe6d324dd7f8e9ffe902af3115b5ce` |
| `aes_rank4_9_repair_paired_exact_v1/results.json` | `b2e1639f1bdbd112e0a576792922fadfe133aa5bfea05e6a84a8be6ef45ae8cf` |
| `aes_rank4_9_repair_paired_exact_v1/path_net_cap_deltas.json` | `936679f9af57ae5c4fcfc5f293d12f098b80ddb0068e8f9843cb0223742d7f4a` |

三个阶段的原件归档为 `scratch/tcad_ibex_20261123/aes_rank4_9_hold_repair_20261124.tar.gz`。归档 29105129 字节、104 个成员，97 个普通文件逐个核对 SHA-256；包 SHA-256 为 `775f09b276b7f2c74d1ad1fc9cd06946453113a67cd91292b17127b34449e8a5`。

[交叉 STA 与寄生诊断驱动](probe_aes_residual_hold.py) · [六门等面积替换驱动](probe_aes_rank6_repair.py)

从 WSL 仓库根目录复现等面积替换，输出使用新目录。

```bash
raw=/home/toylog/faeco_tcad_sky_holdout_20261123
e=project_docs/evidence/tcad_ibex_20261123
bash code/scripts/run_with_timeout.sh 730 taskset -c 0-5 python3 -B \
  "$e/probe_aes_rank6_repair.py" "$raw/aes_matrix_v1" "$raw/aes_protected_online_matched_v1" \
  "$raw/aes_protected_online_censored_retry_v1/result.json" \
  "$raw/aes_v4_05_donor_direction_v1/results.json" \
  "$raw/aes_v4_05_donor_launch_compensation_v1_qualified/results.json" \
  "$raw/aes_rank4_9_repair_replay" --omit _13098_
```
