# R3 配套证据

## ASAP7 注入用例逐例复算

五个窗内用例均在合并请求窗内产生实际标记，窗外控制的两处标记 bbox 都在请求窗外。注入模式来自 Stage 1 配置，标记类型按独立全块报告读取。五组窗内的全块与窗口报告分别逐字节一致。下表的全块／窗口列记录标记数，同一类型的计数以上述全块报告为对象。

| 原件用例 | 层 | 注入模式（间隔／nm） | 实报短路／金属间距 | 全块／窗口 | 标记位置 |
| --- | --- | --- | ---: | ---: | --- |
| `asap7_nz_01_m1_short` | M1 | 短路（0） | 7／4 | 11／11 | 窗内 |
| `asap7_nz_02_m1_spacing` | M1 | 间距（10） | 9／1 | 10／10 | 窗内 |
| `asap7_nz_03_m2_short` | M2 | 短路（0） | 3／2 | 5／5 | 窗内 |
| `asap7_nz_04_m2_spacing` | M2 | 间距（12） | 0／2 | 2／2 | 窗内 |
| `asap7_nz_05_m3_spacing` | M3 | 间距（14） | 8／1 | 9／9 | 窗内 |
| `asap7_nz_06_m3_scope_control_oow` | M3 | 窗外短路控制 | 2／0 | 2／0 | 窗外 |

五组窗内合计 27 个短路、10 个金属间距标记，窗口与全块一致，共 37 个。两个窗外标记单列。窗外扰动的位置由合成控制指定，位于命题 1 所限定的变更几何之外。这里核验受控扰动下的标记和源对象；生产放行还需要对应冻结信号网的可归因身份，候选交付还需要完整物理及等价验收。 [Stage 1 收据](../../../../project_docs/evidence/tcad_v5_revision_20261126/V5_STEP1_POWER_7NM_DET_VERIFIED.json) · [原始 ZIP](../../../../project_docs/evidence/tcad_v5_revision_20261126/V5_REVIEW_ORIGINALS.zip) · [复算器](../../../../project_docs/evidence/tcad_v5_revision_20261126/verify_review_evidence.py)

对每行在 ZIP 下读取 `faeco_v5_step1_20261126_v1/asap7_controlled_nonzero_drc/<用例>/full_drc.rpt` 与 `box_0.rpt`，同目录保留生成 Tcl 和 `meta.txt`。Stage 1 收据 SHA-256 为 `85bfc1657fbc0663649e417abbe7a9c9827d7d1cded05c121133bd150f28a235`，ZIP SHA-256 为 `eec4d4bdc4911ec42aa31cb874c0fb9a1ebfa4a11508a19573858f9137d3237f`。

| 用例编号 | 全块报告 SHA-256 | 窗口报告 SHA-256 |
| --- | --- | --- |
| 01 | `03fd0412622e5355f928fb6bf27d26061443d8b10f7afae2ac70ed154ea82a55` | 同全块 |
| 02 | `490942fd9e77a7a46b7860c7ae99081113029bc7c41e793dfb61b102c6d779e1` | 同全块 |
| 03 | `e2fc230b6a73cfad79d1d40adf24c702d6b3d4d40ba32b9eb89dc0da285fabb9` | 同全块 |
| 04 | `502dcce488bc2bb20095ffc046a88541fcd8b47ad49b92bee131643cb07ee6ae` | 同全块 |
| 05 | `483fec2f53d3fd85c77f7971b3422c78c9e3208d0fffaeeeb8dd44034f7fb4da` | 同全块 |
| 06 | `f2a434b80b1b9d402e0b205f709d53a6aace195b064bc9680b13fd1c79e5d7cc` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

## Stage 2B ASAP7 原生提议接入缺口

两种原生模式均从同一冻结 ODB 记录预存在的、非固定实例及原 master，调用 `remove_fillers` 和 `repair_timing -recover_power 100`，再仅输出两态同名且 master 变化的实例。旧保护后端把已导出 Verilog 通过 `logical_masters()` 过滤成带 TT 面积记录的实例表。逐条核实后，UART 的 16 项与 AES 的 142 项均能在相应冻结 Verilog 中找到同名实例和相同旧 master，接入失败发生在原 TT 面积索引。 [冻结提议提取与绑定](../../../../project_docs/evidence/tcad_v5_revision_20261126/run_v5_step2_dedup_and_native_protected.py#L167) · [后端实例索引](../../../../project_docs/evidence/tcad_ibex_20261123/compare_ibex.py#L342)

实际读入的 `asap7sc7p5t_INVBUF_RVT_TT_nldm_220122.lib` 含相关 master 及数字面积，例如 `BUFx3_ASAP7_75t_R` 对应 `area : 0.08748`，该行缺少分号。两设计各自五份 TT 库的 INVBUF 副本同 SHA-256 `a4ceb32e418e1aac8667e28fbd8e9e46baf520180be4db075598a4d7c681a56e`。当时的面积解析正则要求以 `;` 结束，因而漏收字段。UART 16 项为 `BUFx3_ASAP7_75t_R` → `HB3xp67_ASAP7_75t_R`；AES 142 个相同缺口包含这类替换 129 项，其余为四组 buffer／inverter 替换。原始结果中的未绑定数量据此复现。 [面积解析器](../../../../code/src/rseco/logic_rewrite.py#L196) · [原生提议实跑结果](../../../../project_docs/evidence/tcad_v5_revision_20261126/V5_STEP2_DEDUP_NATIVE_VERIFIED.json)

在内存对 INVBUF 文本的 37 条未以分号结束的数字 `area` 行补 `;`，复用原解析器和原实例映射程序。库文件与原始网表保持原字节。两个设计的 TT 面积键均由 160 增至 197。四个原生臂均比较全部提议，记录如下。

| 设计与选项 | 原提议 | 原面积索引未绑定 | 内存规范化后未绑定 | 旧 master 不符／目标面积漏项 |
| --- | ---: | ---: | ---: | ---: |
| ASAP7 UART 常规 | 16 | 16 | 0 | 0／0 |
| ASAP7 UART 允许 Setup 违例 | 16 | 16 | 0 | 0／0 |
| ASAP7 AES 常规 | 174 | 142 | 0 | 0／0 |
| ASAP7 AES 允许 Setup 违例 | 174 | 142 | 0 | 0／0 |

原物理试验的拒收口径保留。此复测只覆盖选定提议的名称与面积索引，后续 DRT、时序、电气、DRC、天线、SEC 及合格面积需新的物理执行才能判定。

### 冻结原始路径和指纹

原提议根为 `/home/toylog/faeco_v5_step2_dedup_native_20261126_v1/native_protected/`，按 `<设计>/<模式>/extract/` 读取 `native_diffs.txt` 与 `extract_native.tcl`。读取 Tcl 的五条 `read_liberty` 实际路径，使用与 `read_db` 相同目录的 `6_final.v`。原始提议两模式同字节，Tcl 模式各自保留。

| 对象 | SHA-256 |
| --- | --- |
| UART 两模式的 `native_diffs.txt` | `269d62f05c711c9177d5ad07ebca53b0d33668f110c5ba2ed9cc397dcd24d44c` |
| UART 常规 `extract_native.tcl` | `36dbce8414d5d43575adb23bdb8c07052f06aad949fe6506a40876a7593f8dfc` |
| UART 允许 Setup `extract_native.tcl` | `3cb396fb1f8a924fc771da0da6611e8ab5a93efc27dd9e5327b500860bd6f5f7` |
| AES 两模式的 `native_diffs.txt` | `b584b04793a5b36b151e741228433cfb0f5cc3214c657d01c56d5acdf18a51ae` |
| AES 常规 `extract_native.tcl` | `981feecfe95df63b553fc44a1c2d3ff97c66f41eee4d50d5c6904900cd42daa1` |
| AES 允许 Setup `extract_native.tcl` | `c6cfcb61f1d6541de030664766b8e7587ab3c37749ff3eab97f12aa34b61955c` |
| UART 冻结 `6_final.v` | `3b50d975941e90f623fd38b55b86e4a7ed6e9de6160f50cc42b2fb97c735d338` |
| AES 冻结 `6_final.v` | `9d346a8c142aad1d03c30af8ca567d5b7522c136cdde8f32761a4ccae9b61d5f` |

复核时用 `compare_ibex.liberty_areas(...)` 构建原面积表，再用 `logical_masters(...)` 和 `align_db_instances(...)` 对照实例。对 INVBUF 文本替换 `(?m)^([ \t]*area[ \t]*:[ \t]*[\d.eE+-]+)[ \t]*$` 为 `\1;`，再次调用 `parse_generic_liberty_catalog(...)` 并合并面积表，重算命中和原 master 一致性。

## 四份最终物理检查的公开证据

参考和修复后各臂终态未改写 ODB 或 DEF。物理专项的三个交付候选按预期更换 5／12／4 个单元，全部实例零位移；受保护的 5469／5435／5474 条网在各自对照中几何不变。PINS 和 SPECIALNETS 与共同参考分别逐字节一致。专项检测只覆盖这组 40 ns 参考及三个交付端点上的放置和 VDD／VSS 物理连通性。完整的信号网 LVS 保持独立验证范围。 [专项报告](../../../../project_docs/evidence/tcad_v5_revision_20261126/R3_FINAL_PHYSICAL_CONNECTIVITY_REPORT.md) · [原件包](../../../../project_docs/evidence/tcad_v5_revision_20261126/R3_FINAL_PHYSICAL_CONNECTIVITY_ORIGINALS.zip) · [只读核验](../../../../project_docs/evidence/tcad_v5_revision_20261126/verify_r3_final_physical_connectivity.py)

## 命题 1 的上下文示例

冻结 ASAP7 M2 技术 LEF 的 `LEF58_SPACING` 指定普通端头间距 0.018 µm、端头宽度 0.025 µm、端头内 `WITHIN` 0.020 µm、端头对端头 0.031 µm、并行边间距 0.025 µm 和该分支的 `WITHIN` 0.020 µm。固定 OpenROAD 根据方向分别形成并行边适用性查询盒。例中取东向端头边的 low 端点 $(x,y)$，其一侧查询盒为 $[x-0.025,x] \times [y-0.020,y+0.020]$ µm。相反端点和其他方向采用相应翻转，端头对端头分支可将间距查询扩至 0.031 µm。并行边的出现或消失会改变适用性，即使不移动最初的两个图形。这里给出一条规则的方向性查询构造；通用窗口覆盖论证仍以有限作用半径和未变图形对的上下文不变条件为前提。 [冻结规则字段](../../../../project_docs/evidence/tcad_v5_revision_20261126/WINDOW_RULE_SCOPE.md) · [并行边查询](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/gc/FlexGC_eol.cpp#L203-L242) · [端头间距查询](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/gc/FlexGC_eol.cpp#L444-L476)


## 两组历史 TT 功耗的终态绑定

从历史比较器的原生 TT 功耗报告及运行 Tcl 回查。下表各行比较当时已交付的 FAECO 端点与该行的 CONTROL，两端调用同一冻结 SDC，分别读取各自 ODB 与 SPEF。原 `report_power` 使用默认活动，四份报告均含 STA-2402（寄存器活动传播在 50 次内未收敛）。这些读数用于各自约束下的变化估计。原始报告的可移植归档待接入。

| 历史参考 | FAECO 物理端点 | 总／组合／漏电的相对变化（%） |
| --- | --- | ---: |
| ASAP7 UART，270 ps | `faeco_tcad_uart_wallclock_20261125_v1/cell_03/faeco/16/initial` | −0.65947110／−2.14200844／−0.77702528 |
| SKY130HD riscv32i，6 ns | `faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i/matrix_rank_aligned_v1/cell_03/faeco/03/retry` | −0.04209048／−0.20449865／−0.09145704 |

原报告根为 `/home/toylog/faeco_tcad_native_recover_power_20261125_v1/`，每个设计的 `power` 子目录含两端的 `control_power.json`、`faeco_best_power.json` 和同名 Tcl／日志。比较组合功耗使用 `Combinational.total`，总功耗和漏电使用 `Total.total` 与 `Total.leakage`。

| 设计 | CONTROL 报告 SHA-256 | FAECO 报告 SHA-256 | 共用 SDC SHA-256 |
| --- | --- | --- | --- |
| `asap7_uart` | `69cc5633811c4458edd5a47d310f68d2511ecd7c33784e908122fc5f3eefe031` | `975c9179df71dbadf6e4e83b1e153f412c263ae24d3672cec391ffc226423610` | `d6a317c88e07abd1d6dcb9a8ac20d6b7aa2fceb1cdf69213b4c36dc4b49be6c9` |
| `sky130hd_riscv32i` | `a484a4a3dc9520f0495fc14ccbd7efaeac4fb1e74c580c072dd8c2c4887e8e06` | `503f4a9ff3c92e85d592dc032de8a229adb7bc801e0babe3a3123ddc947b3bcf` | `74524c0bcc0e07bb1a43609125b5f7bfd03250ac47715ea492a73fb067229d7b` |
