# SKY130 AES 剩余 hold 回退与两门子集

2026-11-24。对象为上轮局部重布线的三门端点 `v4/05`。该端点已经消除全块 DRC 和天线违例，11 条实际改线均为候选数据网或对应邻网，仍在三个视图触发相对 hold 门。原始起点、IO 约束、0.001 ps 相对 hold 容差、绝对 hold、setup WNS/TNS 门和 0.01% 面积目标沿用前轮。[前轮物理结果](AES_SELECTIVE_DRT_REPAIR.md)

## 剩余回退的寄生归因

交叉读取原冻结起点 C 与 `v4/05` 端点 E 的 ODB、SPEF。每组的第一位为 ODB，第二位为 SPEF。12 次 STA 均重现绑定的名义最差路径和相同的寄生标注清单。两个成对物理结果复现原收据。FF／TT 的路径从 `sa03_sr[5]$_DFF_P_` 到 `text_out[29]$_DFF_P_`，SS 的路径从 `key[35]` 到 `u0.w[2][3]$_DFF_P_`。各读数的 hold TNS 均为 0。

| 视图 | CC hold WNS / ps | CE / ps | EC / ps | EE / ps | 仅换 SPEF 的变化 / ps |
|---|---:|---:|---:|---:|---:|
| FF | 336.273898 | 336.251693 | 336.273898 | 336.251693 | −0.022204 |
| TT | 523.914856 | 523.880550 | 523.914856 | 523.880550 | −0.034306 |
| SS | 55.295768 | 55.241145 | 55.295768 | 55.241145 | −0.054623 |

FF／TT 数据到达时刻在九位小数报告的精度内完全相同，捕获时钟分别晚 0.022114／0.034153 ps。SS 的捕获时钟晚 0.157595 ps，数据也晚 0.101567 ps，最终数据要求比原起点晚 0.156164 ps。仅换 ODB 的 hold WNS 变化在三个视图均为 0。

按 SPEF 的 `*CONN` 端子和本地网节点识别每条 `*CAP` 的远端，13 条最差路径数据网和时钟网中只有两条的电容发生变化。按网名和节点别名归一化后，13 条网的电阻边及阻值逐项相同。

| 网 | 原总电容 / pF | 端点总电容 / pF | 主要变化 |
|---|---:|---:|---|
| `clknet_3_1__leaf_clk` | 0.0792723 | 0.0793068 | 地电容 +0.000029780 pF，耦合增量来自 `net8069` 的 +0.000003600 pF 和 `_20134_:A`（位于 `net8267`）的 +0.00000109 pF |
| `_07314_` | 0.0270822 | 0.0270865 | 与 `_08802_` 的耦合 +0.0000339846 pF，同时有其他耦合和地电容减小 |

两条观察网与时钟耦合邻网的 DEF 几何均保持。交叉检验证明整份提取寄生足以造成回退。电容差的远端身份和布局邻近可以缩小修复范围，单个线段的因果仍待隔离。

## 有界物理试验

第一组撤回 `_20883_`，保留 `_20893_` 与 `_20897_` 两个 XOR2 降尺寸。变动的 `net8125` 走线邻近捕获分支及其耦合网 `net8069`，与 `_20883_` 同一组的间距邻网 `_08784_` 也恢复固定。保留 `_20893_` 让与 SS 数据路径耦合的 `_08802_` 仍随实际引脚重布线。原 `_20893_/B` 落点横坐标相对单元基点为 3.450 µm，距新 B 口左边界仅 0.030 µm，而原过孔的 li1 半宽为 0.085 µm。中心点的重叠不足以证明整片接触几何兼容，本轮选用可验收的两门子集和实际重布线。保留释放邻网 `_03615_` 处理 `_20897_` 短路。两门理论面积回收 22.5216 µm²。

CPU0–5 串行运行 4 线程 DRT，单例 DRT／检查／RCX 240 秒、每视图 STA 180 秒、SEC 210 秒。物理端点须经过恢复 `ROUTED` 标志后的独立全块 DRC，再按原门执行候选 SEC。

撤回 `_20883_` 的端点完成 DRT、RCX 和三视图 STA。实测面积回收 22.5216 µm²（0.019331%），恰好只改动六条编辑单元相连的网和 `_03615_`，其他 15,650 条线几何保持。独立全块 DRC 与天线违例均为 0。Setup WNS 在三个视图均无变化，TT／SS 的 setup TNS 分别改善 40.647929／465.888661 ps。FF／TT／SS hold WNS 分别较冻结起点低 0.008105／0.012546／0.166533 ps，仍被三个相对门拒绝，未进入 SEC。

该子集的捕获分支总电容增量从三门端点的 +0.0000345 pF 缩小至 +0.0000127 pF，原先两个观测到的耦合增量均消失。SS 数据网 `_07314_` 的总电容差由 +0.0000043 pF 变为 −0.0000046 pF，即使其与 `_08802_` 的耦合增量相同。物理成对结果显示 FF／TT 回退减轻约 64%，同时 SS 回退扩大。相对 hold 判据要求同时考察三个视图。

撤回 `_20897_` 后，保留 `_20883_` 与 `_20893_`，仅额外释放已定位的间距邻网 `_08784_`。实测面积同样回收 22.5216 µm²，七条计划内网改线，其他 15,650 条网几何保持。FF／TT hold WNS 分别较冻结起点低 0.014100／0.021705 ps，SS 改善 0.171640 ps。`_07314_` 的总电容增量为 +0.0000113 pF，捕获分支总电容增量为 +0.0000218 pF。这一组合给 SS 留出了余量，仍需修复 FF 与 TT 的相对损失。

撤回 `_20893_` 后，释放 `_08784_`、`_03615_`，完成三个两门组合的物理枚举。FF／TT 精确复现三门端点的 hold WNS，SS 相对冻结起点改善 0.099476 ps。捕获分支的 +0.0000345 pF 总电容及两条耦合增量与三门端点相同，SS 数据网的 +0.0000107 pF 差来自地电容。三个两门组合均超过面积目标，独立全块 DRC 和天线检查均为零，FF／TT 均因相对 hold 回退被拒。

| 撤回单元 | 面积回收 / µm² | FF／TT／SS hold WNS 变化 / ps | Setup 门 | 拒绝视图 |
|---|---:|---|---|---|
| `_20883_` | 22.5216 | −0.008105／−0.012546／−0.166533 | 通过 | FF／TT／SS |
| `_20897_` | 22.5216 | −0.014100／−0.021705／+0.171640 | 通过 | FF／TT |
| `_20893_` | 22.5216 | −0.022204／−0.034306／+0.099476 | 通过 | FF／TT |

### 等面积替换的选择

原矩阵 `fixed/06` 的单门替换 `_21033_` 与原未锁线零编辑对照相比，只改动该门连接的三条网和 `net8148`，时钟线路形状一致。FF／TT hold WNS 分别改善 0.063172／0.099032 ps，SS 不变。13 条最差路径网中，仅 FF／TT 发射时钟的 `clknet_3_0__leaf_clk` 电容变化，总电容增加 0.0001006 pF。该发射支路证据支持把这一门加入上述 SS 改善的两门组合，替换原 `_20897_`。两条释放邻网为 `_08784_` 和 `net8148`。候选仍以真实三视图测量和独立物理检查验收。

### 等面积替换通过原门

三门 `_20883_`、`_20893_`、`_21033_` 回收 33.7824 µm²（0.028996%）。11 条实际改线均在计划内，15,646 条保护线和组件位置保持。DRT、恢复 `ROUTED` 后的全块 DRC 及天线检查均为零。原 IO 下的 FF／TT／SS 全部通过绝对与相对 hold，hold TNS 均为零，原 setup 门通过，各视图新增负 setup 端点数均为零。SEC 11,089 已证、0 未证，证明对象绑定原起点与实际 routed.v，后者 SHA-256 为 `55f2e09803d4d780bb2d42ee035b437c3f93480b6f5d53831bd5d17187c9fd51`。

| 视图 | hold WNS / ps | hold WNS 变化 / ps | setup WNS 变化 / ps | setup TNS 变化 / ps |
|---|---:|---:|---:|---:|
| FF | +336.322858 | +0.048961 | −0.001332 | 0 |
| TT | +523.991739 | +0.076883 | −0.002220 | +9.683365 |
| SS | +55.467408 | +0.171640 | −0.003553 | +464.297045 |

相对保留 `_20883_` 和 `_20893_` 的两门端点，补上 `_21033_` 使 FF／TT hold 余量增加 0.063061／0.098588 ps，SS 精确相同。六次精确成对 STA 显示 FF／TT 发射时钟分别晚 0.062406／0.097751 ps，数据到达晚 0.063062／0.098586 ps，捕获时钟和数据要求时刻在报告精度内相同。捕获支路与 SS 数据网的电容记录保持相同，发射支路重现 `fixed/06` 的 +0.0001006 pF 总电容差及相同的逐项耦合差。相同的时钟线路几何、匹配的捕获支路与数据网、改变的发射支路共同把这次改善定位到局部寄生改变。

## 两个合格批次的单次合并检验

把上轮合格的三门 `02` 与本轮等面积替换组合，从同一个冻结起点合并为六门。两份资格回执均通过独立全块 DRC 与 SEC，实际证明绑定的网表与物理产物哈希一致。两个批次的实例和 11 条允许改动的数据网互不重合，合并允许改动 22 条数据网，其中四条是原先局部 DRC 确认涉及的邻网，分别为 `_08784_`、`net4840`、`net8148`、`net8407`。保留其他 15,635 条保护线。合并只运行一次，重新提取并验收。

六门实测面积回收 **67.5648 µm²（0.057992%）**。22 条计划内数据网全部重布线，其他 15,635 条保护线和组件位置保持。原 IO 下各视图 hold TNS 为 0，绝对与相对 hold 都合格。恢复 `ROUTED` 后的独立全块 DRC 与天线违规均为零。SEC 对冻结网表与实际 routed.v 证明 11,089 项，未证为 0，候选网表 SHA-256 为 `33e0dc9a4ef42cee14a9e4505840e64e09fcb0815d95e50e973e3cf6837e26d2`。

| 视图 | hold WNS / ps | hold WNS 变化 / ps | setup WNS 变化 / ps | setup TNS 变化 / ps |
|---|---:|---:|---:|---:|
| FF | +336.323080 | +0.049183 | −0.086153 | 0 |
| TT | +523.991572 | +0.076716 | −0.155875 | +10.139001 |
| SS | +56.078031 | +0.782263 | −0.008882 | +380.168785 |

合并的 hold WNS 变化与两个三门端点各自变化的和相差最多 0.000222 ps，证据范围是这两个批次。SS 新增一个负 setup 端点，`text_out[83]$_DFF_P_/D`，slack 从冻结起点的 +0.329958 ps 变为 −0.214495 ps，与上轮单独 `02` 的新增端点相同。三个视图均满足原 setup WNS/TNS 预算。

## 原件与入口

原件均位于 WSL `/home/toylog/faeco_tcad_sky_holdout_20261123`。

| 原件相对路径 | SHA-256 |
|---|---|
| `aes_v4_05_residual_cross_v1/results.json` | `3cf2ea52a82fbf547fffd2c4b1b897a43113fe0327796f13f2bcd29262969bed` |
| `aes_v4_05_residual_caps_v2/path_net_cap_deltas.json` | `5e953bd49b63579aa1b669227606f46ce4313d44d0b708a45bf5a09429bc0126` |
| `aes_v4_05_residual_rc_audit_v3/path_net_resistance_audit.json` | `e19aa6243ab48f939baee236fcd6e94fdfd3ef8b7b19d841922de272c739376d` |
| `aes_v4_05_subset_drop_20883_v1/05/receipt.json` | `053e2addc7d90da71560e0b11a7819f3d567ce2b8bb7ace5836068ce26c3c359` |
| `aes_v4_05_subset_drop_20883_v1/path_net_cap_deltas.json` | `c67447ccb4466aee54b79c3cc87ab7e781e8e938c423ba63994823f544d678a8` |
| `aes_v4_05_subset_drop_20883_v1_qualified/results.json` | `a272f0875c90711553e76951e78d176e61ce6a19c7fc67a570c3a338fd0af683` |
| `aes_v4_05_subset_drop_20897_v1/05/receipt.json` | `2e8fed57d5f5af9ca8853980bc62dc611125fdc1692d00a1330ff8f5d44ee5c2` |
| `aes_v4_05_subset_drop_20897_v1/path_net_cap_deltas.json` | `9d1de309f4a1f16482287bb7c9799ff2b3e52170fc0c37c4954c6845646b9f8c` |
| `aes_v4_05_subset_drop_20897_v1_qualified/results.json` | `bb924a849428fd6243f14b475bf7ee9165c47868f319da1a38f1059243b30031` |
| `aes_v4_05_subset_drop_20893_v1/05/receipt.json` | `bb34b5ab86ee0d0c94cc8d625cba055d33123752baea79f325251d553796b1f4` |
| `aes_v4_05_subset_drop_20893_v1/path_net_cap_deltas.json` | `c7d88e1d97870e6e0cfb66a28f5059ce62e07e804a4b1a12f4eb25d9c32979c8` |
| `aes_v4_05_subset_drop_20893_v1_qualified/results.json` | `e1fb1c9c4bb4c35fb96f6f82d8642c3913ce5b1e739c1729e7d5974110322e8f` |
| `aes_v4_05_donor_direction_v1/results.json` | `4d79c58b8a36c001205ea3f7c107ccb52f9c91cbac78f35aeab0f752de1c1387` |
| `aes_v4_05_donor_launch_compensation_v1/05/receipt.json` | `fbdb05190606a10e5bfcf3735930c59571dc54efe8c2181e6fe0aef1380be820` |
| `aes_v4_05_donor_launch_compensation_v1_qualified/results.json` | `2541b0d52fdccb53c1d11a419684955ee7ba83a705b74d000885d47c5f73d857` |
| `aes_v4_05_donor_launch_compensation_v1_qualified/05/sec/receipt.json` | `4134738e8babd5dd36ee27e803b1acb88a9f0dd9bad08fc073651fcbce619f98` |
| `aes_v4_05_donor_paired_exact_v1/results.json` | `f9789a535f8ecacd2476f94ea12e49bceec473129cfae1a8c61bb17f3a3bb26d` |
| `aes_v4_05_qualified_union_six_v1/05/receipt.json` | `bb47277ab03ccf19938c34cee4ae43accce3e330efb8b714f7b858106acb3e24` |
| `aes_v4_05_qualified_union_six_v1_qualified/results.json` | `662ded5cb91cd2eff5bd38ca2d02d0359f0532a22b01864a65f65044111d49c4` |
| `aes_v4_05_qualified_union_six_v1_qualified/05/sec/receipt.json` | `64606c7c6f5686e0c701e3a88401ae7db96dc4856404b34f02d8b8517492a0d3` |
| `aes_v4_05_qualified_union_six_v1_named_setup/results.json` | `681a492c6d5cd6d656bd531f844439f26d1081ac76ab745bba4f1eb784e8223c` |

本轮截至等面积替换的 13 个原始目录归档至 `scratch/tcad_ibex_20261123/aes_residual_hold_optimization_20261124.tar.gz`。压缩包 109925296 字节、233 个成员，207 个普通文件逐项 SHA-256 与原件核对一致。压缩包 SHA-256 为 `022cf082854c45cc1e4350b12841d505d063a2718cea9f448683c9dd1c3bc1b6`。

六门合并的四个目录另归档于 `scratch/tcad_ibex_20261123/aes_qualified_union_repair_20261124.tar.gz`，其中包含合并前版本的原驱动、实跑、独立验收及新增负 setup 路径。压缩包 29028405 字节、56 个成员，48 个普通文件逐项 SHA-256 与原件核对一致。压缩包 SHA-256 为 `b351d794555e0f566bce0c83038104d91a9791eedfce12fa7823c9faaf418478`。

交叉 STA 的首版逐网电容表有一条耦合记录以本地节点作远端标签。方向修正只重算 SPEF 电容表，STA 原件与旧解析表完整保留，报告采用正确辨识远端的表。

[交叉 STA 和 SPEF 电容脚本](probe_aes_residual_hold.py) · [子集局部重布线驱动](probe_aes_selective_repair.py) · [物理验收驱动](qualify_aes_selective_routes.py)

等面积替换在 WSL 中从仓库根目录复现，输出路径用新目录。

```bash
raw=/home/toylog/faeco_tcad_sky_holdout_20261123
e=project_docs/evidence/tcad_ibex_20261123
bash code/scripts/run_with_timeout.sh 650 taskset -c 0-5 python3 -B \
  "$e/probe_aes_selective_repair.py" "$raw/aes_matrix_v1" "$raw/aes_donor_replay" \
  --case 05 --omit-instance _20897_ --add-singleton-slot 06 \
  --release-neighbor _08784_ --release-neighbor net8148
bash code/scripts/run_with_timeout.sh 370 taskset -c 0-5 python3 -B \
  "$e/qualify_aes_selective_routes.py" "$raw/aes_matrix_v1/config.json" \
  "$raw/aes_donor_replay" "$raw/aes_donor_replay_qualified" --cases 05
```

六门合并从两个既有通过回执及其物理端点重新验收。

```bash
bash code/scripts/run_with_timeout.sh 650 taskset -c 0-5 python3 -B \
  "$e/probe_aes_selective_repair.py" "$raw/aes_matrix_v1" "$raw/aes_union_replay" --case 05 \
  --qualifying-union "$raw/aes_selective_drt_repair_v4_02_qualified/results.json" \
  "$raw/aes_v4_05_donor_launch_compensation_v1_qualified/results.json"
bash code/scripts/run_with_timeout.sh 370 taskset -c 0-5 python3 -B \
  "$e/qualify_aes_selective_routes.py" "$raw/aes_matrix_v1/config.json" \
  "$raw/aes_union_replay" "$raw/aes_union_replay_qualified" --cases 05
```
