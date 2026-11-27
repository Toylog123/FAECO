# 窗口诊断的技术 LEF、检查器上下文与 Stage 1 时序复核

2026-11-27，V5 修订 R2-1/R2-2。距离取自冻结的技术 LEF，单位为 µm。表中的条件量保留原关键字，便于区分间距约束、端头宽度、判定范围与过孔包围。数值表示 LEF 文本，工具使用转换后的数据库单位。

## 输入身份

| 工艺 | 冻结技术 LEF（WSL） | SHA-256 | 行高与数据库单位 |
| --- | --- | --- | --- |
| SKY130HD | `/home/toylog/faeco_eda/orfs/flow/platforms/sky130hd/lef/sky130_fd_sc_hd.tlef` | `8e99b4e8b016db0713029ebcae6b2cc2aedd9c2c49682e2f23521dd0b1a2085e` | `SITE unithd` 2.72 µm（37–41 行），1000 DBU/µm（27 行） |
| ASAP7 | `/home/toylog/faeco_eda/orfs/flow/platforms/asap7/lef/asap7_tech_1x_201209.lef` | `7694bf4f8ef2f9745e4579f454788a0cf048e8605320f32d1d83ec540ed4ca41` | `SITE asap7sc7p5t` 0.270 µm（同目录 RVT 单元 LEF 的 36–40 行），1000 DBU/µm（技术 LEF 的 39 行） |

两份技术 LEF 的指纹与 [V4 规则审计收据](../tcad_v4_revision_20261126/LEF_AND_DETERMINISM_AUDIT.json) 一致。ASAP7 的 RVT 单元 LEF 为 `asap7sc7p5t_28_R_1x_220121a.lef`，SHA-256 `4eb73f825720d95eba4da455c7b2e7a28e444e88e9d8595d13492cf5eecfc0d1`。生产窗口从冻结 ODB 内首个实际行的 bbox 高度读取行高。既有回放两工艺分别记录 2720、270 DBU。SKY130HD 技术 LEF 还定义了高 5.44 µm 的 `unithddbl`，适用行高在实现中由实际版图读取。 [窗口实现](../tcad_boxed_drc_20261126/boxed_drc.py) · [回放收据](../tcad_boxed_drc_20261126/BOXED_DRC_RECALL_AUDIT.json)

## 已核规则字段

### SKY130HD

| 层 | 规则与原始距离（µm） | 技术 LEF 行 |
| --- | --- | --- |
| `li1` | `SPACINGTABLE PARALLELRUNLENGTH 0`，`WIDTH 0 0.17` | 69–71 |
| `met1` / `met2` | `SPACINGTABLE PARALLELRUNLENGTH 0`，`WIDTH 0 0.14`、`WIDTH 3 0.28` | 105–108 / 148–151 |
| `met3` / `met4` | `SPACINGTABLE PARALLELRUNLENGTH 0`，`WIDTH 0 0.30`、`WIDTH 3 0.40` | 190–193 / 230–233 |
| `met5` | `SPACINGTABLE PARALLELRUNLENGTH 0`，`WIDTH 0 1.60` | 272–274 |
| `mcon` | `SPACING 0.19`，`ENCLOSURE BELOW 0 0`、`ABOVE 0.03 0.06` | 82–88 |
| `via` | `SPACING 0.17`，`ENCLOSURE BELOW 0.055 0.085`、`ABOVE 0.055 0.085` | 127–132 |
| `via2` / `via3` | 均为 `SPACING 0.20`。`ENCLOSURE BELOW` 分别为 `0.04 0.085`、`0.06 0.09`。`ABOVE` 均为 `0.065 0.065` | 171–176 / 211–216 |
| `via4` | `SPACING 0.80`，`ENCLOSURE BELOW 0.19 0.19`、`ABOVE 0.31 0.31` | 252–258 |

`SPACINGTABLE PARALLELRUNLENGTH` 行的数值是表的平行长度列坐标，`WIDTH` 后首项是宽度行坐标，余项是间距。这里的金属层普通 `SPACING` 样例在原件中被注释，实填能复核的是上表平行长度表。SKY130HD 的 `VIARULE ... GENERATE` 还可含 `SPACING ... BY ...`，例如 `L1M1_PR` 301–309 行中的 `0.36 BY 0.36`，用于生成过孔阵列时的切孔节距。

### ASAP7

| 层 | 规则与原始距离（µm） | 技术 LEF 行 |
| --- | --- | --- |
| `M1` | `SPACING 0.018`，另有 `SPACING 0.018 RANGE 0.036 1.0`。`LEF58_EOLKEEPOUT` 为 `EOLKEEPOUT 0.01825 EXTENSION 0.0 0.0 0.031`。`LEF58_CORNERSPACING` 为 `CONVEXCORNER CORNERONLY 0.01 WIDTH 0.018 SPACING 0.018` | 116、119、121、123 |
| `M2` | 普通 `SPACING 0.018`。`LEF58_SPACING` 为 `SPACING 0.018 ENDOFLINE 0.025 WITHIN 0.020 ENDTOEND 0.031 PARALLELEDGE 0.025 WITHIN 0.020` | 138、163–165 |
| `M3` | 普通 `SPACING 0.018`。`LEF58_SPACING` 为 `SPACING 0.018 ENDOFLINE 0.025 WITHIN 0.0125 ENDTOEND 0.031 PARALLELEDGE 0.025 WITHIN 0.020` | 205、215–217 |
| `M2` / `M3` | `LEF58_EOLKEEPOUT` 均为 `EOLKEEPOUT 0.025 EXTENSION 0.0 0.0125 0.031 CORNERONLY`。`LEF58_CORNERSPACING` 均为 `CONVEXCORNER WIDTH 0.0 SPACING 0.020` | 167–173 / 219–226 |
| `V0` / `V1` / `V2` | 普通切孔 `SPACING 0.018` | 107 / 130 / 195 |
| `V3` / `V4` / `V5` / `V6` | `PROPERTY LEF58_SPACINGTABLE` 内为 `SPACINGTABLE DEFAULT 0.034 CUTCLASS ...`，表项以 `-` 记。适用的切孔类别见各块 `LEF58_CUTCLASS`。包围条件另列在 `LEF58_ENCLOSURE` | 251–276 / 332–359 / 412–443 / 493–520 |
| `M4` / `M5` | 普通 `SPACING 0.024`。平行长度表 `PARALLELRUNLENGTH 0.0`、`WIDTH 0.0 0.024`、`WIDTH 0.025 0.072`。`LEF58_SPACING` 为 `SPACING 0.024 ENDOFLINE 0.025 WITHIN 0.040 ENDTOEND 0.040`。角规则 `CORNERONLY 0.048 WIDTH 0.0 SPACING 0.040`。端头禁布区 `EOLKEEPOUT 0.025 EXTENSION 0.048 0.02425 0.048 CORNERONLY` | 285、291–312 / 368、373–397 |
| `M6` | 普通 `SPACING 0.032`。平行长度表 `PARALLELRUNLENGTH 0.0`、`WIDTH 0.0 0.032`、`WIDTH 0.033 0.072`。`LEF58_SPACING` 为 `SPACING 0.032 ENDOFLINE 0.0375 WITHIN 0.040 ENDTOEND 0.040`。角规则 `CORNERONLY 0.048 WIDTH 0.0 SPACING 0.040`。端头禁布区 `EOLKEEPOUT 0.050 EXTENSION 0.048 0.03225 0.048 CORNERONLY` | 456、460–478 |
| `M7` | 普通 `SPACING 0.032`。平行长度表同 `M6`。`LEF58_SPACING` 为 `SPACING 0.030 ENDOFLINE 0.0375 WITHIN 0.040 ENDTOEND 0.040`。角规则 `CORNERONLY 0.075 WIDTH 0.0 SPACING 0.040`。端头禁布区同 `M6` | 529、533–554 |
| `V7` / `V8` / `V9` | 普通切孔 `SPACING` 分别为 `0.046`、`0.057`、`0.057` | 568 / 596 / 623 |
| `M8` / `M9` | `SPACINGTABLE PARALLELRUNLENGTH` 列坐标为 `0.0 0.39975 1.19975 1.79975`。表中间距为 `0.040`、`0.50`、`1.00`，增大的值位于宽线且长平行列。另有 `MINIMUMCUT 2 WIDTH 1.805 WITHIN 1.705`，方向限定见原行 | 579–589 / 608–617 |
| `Pad` | `SPACINGTABLE PARALLELRUNLENGTH 0.0 11.99975`，`WIDTH 0.0 2.0 2.0`、`WIDTH 11.99975 2.0 3.0`。`MINIMUMCUT` 另用 `WITHIN 1.705` | 632–638 |

`LEF58_SPACING` 中第一项 `SPACING` 是端头间距，`ENDOFLINE` 后的是端头宽度阈值。紧随其后的 `WITHIN` 与 `PARALLELEDGE` 子句中的 `WITHIN` 各为独立判定距离，`ENDTOEND` 为相对端头间距。`EOLKEEPOUT` 的首个长度也是端头宽度，`EXTENSION` 三项按 backward、side、forward 顺序读取。可将 `M1–M3` 普通间距 0.018 µm 和 `M2/M3` 端头间距参数作为并列事实。端头、过孔和角规则各自依完整条件作用。注入回放只确认所见 `Short`/`Metal Spacing` 文本标记与关联标签，规则条款的存在与源码加载能力均不等于该条款被这组注入触发。 [端头属性解析](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/odb/src/lefin/lefTechLayerSpacingEolParser.cpp#L388-L453) · [禁布区属性解析](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/odb/src/lefin/lefTechLayerEolKeepOutRuleParser.cpp#L74-L103) · [DRT 端头规则装载](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/io/io.cpp#L1589-L1638)

## OpenROAD 窗口、上下文与标记

固定源码为 OpenROAD 上游提交 `b511b6a2bc936844b0319efc8b4972bb4ad7d911`，本地源码根 `/home/toylog/rseco_timing/vendor/OpenROAD-b511b6a`。实测所用 Bazel `execroot/_main/src` 指向该树的 `src`。 [上游提交](https://github.com/The-OpenROAD-Project/OpenROAD/commit/b511b6a2bc936844b0319efc8b4972bb4ad7d911)

| 环节 | 已核行为 | 上游位置 |
| --- | --- | --- |
| 命令与请求盒 $Q$ | Tcl 取四个 DBU 坐标。`checkDRC` 从同一 ODB 初始化整版图、工艺和 GCell 网格。零面积请求盒回退到 `design_->getTopBlock()->getBBox()`，即默认全块。 | [`TritonRoute.tcl` 494–521 行](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/TritonRoute.tcl#L494-L521)、[`TritonRoute.cpp` 1248–1276 行](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/TritonRoute.cpp#L1248-L1276) |
| worker 与上下文 | 以步长 7 在同一 GCell 网格生成基盒。分别外扩成 `drcBox` 与 `extBox`，仅调度 `drcBox` 和 $Q$ 相交的检查器。每个已调度检查器以它自己的 `extBox` 查询固定对象和详细布线对象。`DRCSAFEDIST` 默认 500 DBU，`MTSAFEDIST` 默认 2000 DBU，导入非默认规则时用其最大间距更新 `MTSAFEDIST`。这些距离从各自 worker 基盒起算。 | [`TritonRoute.cpp` 1181–1217 行](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/TritonRoute.cpp#L1181-L1217)、[`FlexGC_init.cpp` 176–218 行](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/gc/FlexGC_init.cpp#L176-L218)、[`drt-global.h` 36–40 行](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/drt-global.h#L36-L40)、[`io.cpp` 501–517 行](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/io/io.cpp#L501-L517) |
| 输出标记 | 检查器返回的标记仅在其 bbox 和 $Q$ 相交时纳入结果，按 bbox、层、约束、源对象去重。写报告时再次检查交集。`Rect::intersects` 包括边界相接。FAECO 多请求盒合并报告时按违例文本类型、含层名的 bbox 行和 `srcs` 行去重。 | [`TritonRoute.cpp` 1219–1241 行](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/TritonRoute.cpp#L1219-L1241)、[1452–1457 行](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/TritonRoute.cpp#L1452-L1457)、[`geom.h` 726–730 行](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/odb/include/odb/geom.h#L726-L730)、[FAECO 报告合并](../tcad_boxed_drc_20261126/boxed_drc.py) |

典型金属短路和成对金属间距路径用两个最大矩形的广义交集构造 `markerRect`。正面积短路对应交叠区域，简单间距对应两矩形间的间隙区域。若短路矩形相接造成零宽或零高，对应维度的标记盒外扩 1 DBU 再按属性决定是否生成标记。短路路径区分两个已固定图形、障碍物和同网非充分金属。正文可据此在简单导电几何类别上把“报标盒与见证相交”作为可核验前提，保留其他条件规则对图形和对象身份的依赖。 [`FlexGC_main.cpp` 587–599 行](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/gc/FlexGC_main.cpp#L587-L599) · [`FlexGC_main.cpp` 800–903 行](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/gc/FlexGC_main.cpp#L800-L903)

窗口与全块的标记集合一致需要一项实现层条件。全块结果中与 $Q$ 相交的每个目标标记，至少由一个 `drcBox` 与 $Q$ 相交且加载相同 `extBox` 上下文的检查器生成。`FlexGCWorker::Impl::addMarker` 自身只去重，因此不能仅由几何见证落在 $Q$ 或仅由工具筛选语句推出上述条件。报告已验证的实证范围时，使用 SKY130HD 已测换门回放与 ASAP7 合成扰动的标记匹配。窗外负对照的两个短路 bbox 在该请求盒之外。最终候选仍走状态归一后的全块 DRC。 [`FlexGC.cpp` 109–120 行](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/gc/FlexGC.cpp#L109-L120) · [Stage 1 收据](V5_STEP1_POWER_7NM_DET_VERIFIED.json) · [全块终检脚本](../tcad_ibex_20261123/audit_aes_unlocked_drc.py)

### ASAP7 M2 端头的查询上下文

M2 的 `ENDOFLINE 0.025` 限定端头宽度，查找间距相关的导线边时沿端头两端各给出 20 nm，普通端头和相对端头的法向查询值分别含 18 nm 和 31 nm。取一条沿正 x 方向、朝下的横边，从 $(x_0,y_0)$ 到 $(x_1,y_0)$，以 nm 为单位。该端头的外侧间距查询盒为 $[x_0-20,x_1+20]\times[y_0-31,y_0]$。平行边触发条件另查边端点附近的矩形。例如东向端头低端点 $(x,y)$ 的一侧平行边查询盒为 $[x-25,x]\times[y-20,y+20]$。处于盒内的平行边改变时，原有端头与对面导线的形状可以保持不动，规则的适用性及标记仍可能变化。这是命题 1 要求旧图形对的规则上下文保持相同的具体例子。 [固定源码的方向分支](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/gc/FlexGC_eol.cpp#L203-L285) · [端头间距查询盒](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/gc/FlexGC_eol.cpp#L436-L506)

## §4.2 可直接采用的文字

> **引脚接入层的局部几何覆盖。** 令 $B_i$ 为替换后实例的包围盒。参考状态在所考查规则下无违例。考虑替换引发的同层异网短路和简单成对间距违例，且至少一个参与图形发生变化，变更图形位于 $B_i$ 内。若交叠区域或成对间距的最短距离见证落在有效芯片范围内，且其到变更图形的距离不超过 $H_{\mathrm{row}}$，则该局部见证落在 $B_i$ 四向外扩一行高所得窗口内。多实例窗口合并保留各实例的覆盖范围。该条件用于定位局部几何交互。表 X 分别列出两套技术 LEF 的基本间距、端头条件与切孔规则。
>
> 在所用 OpenROAD 版本中，窗口请求保留同一版图与 GCell 网格，选择检查盒与请求窗口相交的检查器。每个检查器在独立扩张的上下文盒内查询导线、引脚与障碍。窗口接口返回包围盒与请求窗口相交的标记。以同一预览的全块检查为参照，§5.4 分别核验实际换门和受控扰动的报告一致性。完成重布线后，候选还需通过全块物理终检。

表题可用“冻结技术 LEF 的代表性引脚接入层规则与条件”。主稿可仅保留 SKY130HD `li1`/`met1`、ASAP7 `M1` 至 `M3` 和所需切孔行。若需要保留规则阈值形式的充分条件，可将首段中的见证距离换成“对所讨论规则给定经核验的上界 $r_\ell$，且 $r_\ell\le H_{\mathrm{row}}$”。上下文依赖规则可写作 $V_\ell(p_1,p_2;\Gamma)$，其中 $\Gamma$ 含端头和邻近对象等适用条件。图 2 中可将“行高自适应窗口精确归因”改为“行高窗口筛取冲突标记”，在图注说明扩张上下文由检查器管理，全块终检决定版图验收。

## Stage 1 反例的 SS Hold 原始口径

三份原件的数值键均为 `views.SS.hold_wns_ps`，单位为 ps。相对变化由读出的原精度直接计算。

| 对象 | 原始 SS Hold | 相对冻结参考变化 | WSL 原件 / SHA-256 |
| --- | ---: | ---: | --- |
| 冻结参考 | 55.29576796448055 | 0 | `/home/toylog/faeco_tcad_sky_holdout_20261123/aes/ss_hold_targeted_v2b/qualification/CONTROL.json` / `c697450a257ef4e63182f02c0ce4fb3c5925b41f366628a97672ac440192d4f8` |
| $T_3$ | 55.138116294983774 | −0.15765166949677223 | `/home/toylog/faeco_v4_windowed_ablation_20261126_v1/sky130hd_aes/fixed_boxed/fixed_online/01/initial/receipt.json` / `46baf806d39ad417d909416ccae469c0275942a3a0f82d1c235c46f5878d9d5c` |
| $S_{18}$ | **55.75495620746551** | **+0.45918824298496475** | `/home/toylog/faeco_v4_hybrid_faeco_20261126_v1/sky130hd_aes/phase1_optimistic_probe/initial/receipt.json` / `56bbf8a961ed8230c693dc518a3e394fd172bda605ce9e167435174cb77f17f7` |

$T_3$ 与 $S_{18}$ 两份物理收据绑定同一 `6_final.sdc`，SHA-256 `379f839cc62d103d029661350ad1a79355419c4fd1a4733d698ab2c365686a9b`。$S_{18}$ 的原始增量与 Stage 1 `part1_counterexample_and_timing_audit.counterexample_superset_S.views_delta_ps.SS.d_hold_wns_ps` 精确一致。另一次功耗配套三角 STA 在 `part2_power_and_6corner.sky130hd_aes_hybrid_18g` 中保存参考 55.29576952835171 ps 与端点 55.75495778432341 ps。主稿的可行域反例可按原物理收据写成参考 55.295768 ps、三门 55.138116 ps、十八门 55.754956 ps，对应相对变化 −0.157652、+0.459188 ps。结论按 0.001 ps 相对 Hold 门保持一致。 [Stage 1 汇总原件](V5_STEP1_POWER_7NM_DET_VERIFIED.json)
