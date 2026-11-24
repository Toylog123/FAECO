# SKY130 AES 局部重布线修复

2026-11-24。沿用 `ss_hold_targeted_v2b` 冻结起点、3.6 ns 原时钟、720 ps 原输入输出延迟、原 FF／TT／SS 库和 RCX 规则。每视图仍执行绝对 hold 合格与 0.001 ps 容差下的相对 hold 不回退，沿用 36 ps setup WNS 预算和各视图的 setup TNS 预算。面积目标为起点的 0.01%，对应 11.650799 µm²。固定批次旧试验 `02` 与 `05` 均有三个 XOR2 降尺寸动作，最大可回收 33.7824 µm²。上轮诊断将这两个候选的相对 hold 损失定位到最差路径的时钟寄生变化。[原试验诊断](AES_REROUTE_HOLD_DIAGNOSTIC.md)

## 实际锁线和验收

用原 ODB 的嵌入 guides。把原 DEF 中需要保留的信号线设为 `FIXED`，替换前读回每条固定线。局部 DRT 重新布线候选数据网，接着重提取寄生并执行三视图 STA、天线检查和 DRC。几何审计按连接端集合比较 DEF NETS，完整比较每条网的坐标、线型规则、走线段和过孔，只有终端序列以及 `ROUTED/FIXED` 标志允许规范化。再将候选副本的线型标志恢复为 `ROUTED`，验证线路、组件和电源网几何不变后运行全块 `drt::check_drc`。固定形状之间的部分规则会被 FlexGC 跳过，因此候选只有在这次检查、原时序门和面积目标均通过时才执行 SEC。

工具为矩阵绑定的 OpenROAD 二进制，SHA-256 `2d9662715130538b50e93b614c33099a5e183eef0cc31b642099daea8d203e19`。其 Bazel execroot 对应本机 OpenROAD 提交 `b511b6a2bc936844b0319efc8b4972bb4ad7d911`。该版本的 `definReader.cpp:1967–1978` 在 FLOORPLAN 模式注册 NETS 和走线路径回调；TritonRoute 的 `io.cpp:721–725` 识别 `FIXED`，`FlexDR_init.cpp:2674` 排除固定网重新布线。四线程详细布线使用同一 CPU0–5 集合，候选逐个运行，最多 64 个 DRT 迭代，DRT／检查／RCX 阶段超时 240 秒，STA 每视图 180 秒，SEC 210 秒。以下时间仅用来定位运行阶段。

### 启动与审计修正

| WSL 运行 | 实查结果 |
|---|---|
| `aes_selective_drt_repair_v1` | 零编辑跑到 DRT 与天线零违例，随后因全块 DRC 的 Tcl 命名空间调用错误退出，未提取寄生或测 STA。`02` 已启动并停止，`05` 未启动。 |
| `aes_selective_drt_repair_v2` | 修正为 `drt::check_drc`。零编辑完成 DRT/RCX/STA，实际 DEF 中没有 FIXED 网，精确复现既有六条改线与 SS −0.676792 ps。所用 `read_def -incremental` 在此版本跳过 NETS；随后停止已启动的 `02`，保留原件。 |
| `aes_selective_drt_repair_v3` | 改用对既有块的 `read_def -floorplan_initialize`。零编辑明确读回 15,657 条 FIXED 网。首个几何审计把 DEF 导入造成的端子顺序翻转计为几何变化，原收据及其驱动均保留。重新按连接端集合和原线路几何验收同一原始物理端点。 |

v3 零编辑经过真实 DRT、RCX 和三视图 STA，15,657 条网几何全部与起点相同，面积变化为零。FF／TT／SS 的 hold WNS 为 +336.273898／+523.914856／+55.295768 ps，每视图的 setup WNS/TNS 与 hold WNS/TNS 均精确复现起点。天线与状态规范化后的全块 DRC 为零，SEC 11,089 已证、0 未证。其规范化 DEF 字节与起点 DEF 相同。独立对冻结起点运行相同的全块检查同样为零违例。

## 三门候选与邻网修复

锁定所有未编辑网时，`02` 的三视图时序均满足原门，但全块 DRC 看见一处 met1 金属间距违例和三处 met1 短路。间距涉及已编辑的 `net7963` 和邻网 `net8407`，短路涉及替换单元 `_11178_` 和邻网 `net4840`。`05` 也有一处间距和三处短路，分别涉及 `net7882`、邻网 `_08784_`，以及替换单元 `_20897_`、邻网 `_03615_`。这两个候选的四处违例均出现在独立全块检查，DRT 自带最终违例计数均为 0。

| v3 全量保留未编辑网 | 面积回收 / µm² | FF／TT／SS 的 hold WNS 变化 / ps | 全块 DRC | 原时序门 |
|---|---:|---|---:|---|
| `02` | 33.7824 | +0.000111／+0.000500／+0.053069 | 4 | 通过 |
| `05` | 33.7824 | −0.029921／−0.046019／−0.283107 | 4 | 三视图相对 hold 回退 |

两个候选各自只有 9 条直接编辑网。邻网修复将每次全块 DRC 指向的两条非时钟邻网加入同一次清线重布线，15,646 条其他信号和时钟网仍固定。所有面积、时序及证明判定均相对原冻结起点。

### `02` 邻网修复验收通过

将 `net8407` 与 `net4840` 加入重布线范围后，实际变动的 11 条线与设定范围逐条吻合。15,646 条固定网均无几何变化，组件位置无变化。按 TT Liberty 功能面积计，从 116507.9904 µm² 回收 33.7824 µm²（0.028996%）。DRT 自带 DRC、候选 ODB 的全块 DRC、恢复原线型标志后的全块 DRC 和天线违规均为 0。SEC 11,089 已证、0 未证。

| 视图 | hold WNS / ps | hold WNS 变化 / ps | setup WNS 变化 / ps | setup TNS 变化 / ps |
|---|---:|---:|---:|---:|
| FF | +336.273953 | +0.000056 | −0.084821 | 0 |
| TT | +523.914856 | 0 | −0.157652 | −0.996980 |
| SS | +55.906613 | +0.610845 | −0.007105 | −103.000275 |

三个视图 hold TNS 均为 0。原 setup 门允许表中的回退。SS 负 setup 端点由 603 增至 604。独立回读同一条 `u0.w[1][19]$_DFF_P_` 到 `text_out[83]$_DFF_P_` 路径，接收端 D 引脚的 setup slack 由 +0.329958 ps 变为 −0.228706 ps。该证据覆盖放开两条邻网的一个 AES 三门端点。

### `05` 邻网修复后仍因相对 hold 回退被拒

加入 `_08784_` 和 `_03615_` 后，实际只改动 11 条计划内的线，固定网和组件位置不变。DRT 自带 DRC、候选 ODB 的全块 DRC、恢复原线型后的全块 DRC 及天线违规均为 0，产生 33.7824 µm² 的面积收益候选。FF／TT／SS 的 hold WNS 分别为 +336.251693／+523.880550／+55.241145 ps，相对起点下降 0.022204／0.034306／0.054623 ps。三个视图均符合绝对 hold 门，hold TNS 均为 0，三个相对回退均超过 0.001 ps 容差。原 setup 门合格，候选未进入 SEC。

后续寄生归因、等面积替换和六门联合端点见 [AES hold 优化](AES_RESIDUAL_HOLD_OPTIMIZATION.md)。

## 原件和入口

原矩阵 `/home/toylog/faeco_tcad_sky_holdout_20261123/aes_matrix_v1`。各阶段物理收据、输入、绑定、DRC、RCX、STA、SEC 和独立审计位于同一父目录。旧技术试验原脚本以 `producer_v1.py`、`producer_v2.py`、`producer_v3.py` 分别保存在对应运行目录。

本轮 10 个原始运行与验收目录已归档到仓库的 `scratch/tcad_ibex_20261123/aes_selective_drt_repair_20261124.tar.gz`，含 252 个成员，224 个普通文件逐个通过原件 SHA-256 核对。压缩包 157214689 字节，SHA-256 `e69ad275ab7f9636a4b0cef12f7438eb4fd584fffefc93d934926042bdb36dc5`。

| 原件相对路径 | SHA-256 |
|---|---|
| `aes_selective_drt_repair_v3/zero/receipt.json` | `cd117d9f7c654a81e032f7b4172a833cbe58d64b1076b3eba16ab1381b1e99d5` |
| `aes_selective_drt_repair_v3/02/receipt.json` | `e21b659dad3414635e595b65c96edb276d3c8a3ffdcb4bfd179aa2c02f1e04eb` |
| `aes_selective_drt_repair_v3/05/receipt.json` | `d8bfee96dba7ccab54438aa9f7a701780f3a741113217bb04a13cd469f99d78e` |
| `aes_selective_drt_repair_v3_qualify_zero/results.json` | `10fd88081ea13f1d6930daec21039a7185c4f04bb088551b18748578cf4b8e9b` |
| `aes_selective_drt_repair_v4_02/02/receipt.json` | `8da3af7a5bcaf9d54d30e0aa2a472f3e2f9c6aa93c57ce37f05ed4a9209a7cb4` |
| `aes_selective_drt_repair_v4_02_qualified/results.json` | `410d42e0258080e1df55918fcf53dda31f18807a71b452c782e86e49fb128ee5` |
| `aes_selective_drt_repair_v4_02_named_setup/results.json` | `cc4c7a534542c23b091b9adc2f2e410c3c88371b2661f1cbe26c79ab9d1b2111` |
| `aes_selective_drt_repair_v4_05/05/receipt.json` | `28c7cd09549eeaaa4243870009c05eab26886cf85a31da8bc8a36b9e4e30cf6c` |
| `aes_selective_drt_repair_v4_05_qualified/results.json` | `3ba9c7f56a4060138ea0982df7c71e15bdef525e97539f611815f9d3b0ab115b` |

[局部重布线驱动](probe_aes_selective_repair.py) · [独立 DRC 审计](audit_aes_unlocked_drc.py) · [原物理端点的后验验收](qualify_aes_selective_routes.py) · [新增负 setup 端点回读](probe_aes_named_setup.py)

从仓库根目录在 WSL 复现 `02` 的两阶段验收，使用新的输出目录。

```bash
raw=/home/toylog/faeco_tcad_sky_holdout_20261123
evidence=project_docs/evidence/tcad_ibex_20261123
bash code/scripts/run_with_timeout.sh 990 taskset -c 0-5 python3 -B \
  "$evidence/probe_aes_selective_repair.py" "$raw/aes_matrix_v1" "$raw/aes_repair_replay_02" \
  --case 02 --release-neighbor net8407 --release-neighbor net4840
bash code/scripts/run_with_timeout.sh 370 taskset -c 0-5 python3 -B \
  "$evidence/qualify_aes_selective_routes.py" "$raw/aes_matrix_v1/config.json" \
  "$raw/aes_repair_replay_02" "$raw/aes_repair_replay_02_qualified" --cases 02
```
