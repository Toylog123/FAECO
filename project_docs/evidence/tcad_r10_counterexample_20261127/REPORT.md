# R10 SKY130HD AES 固定执行协议核验

**证据性质。** 本轮读取原实验的输入绑定、请求、执行台账、输出收据与端点文件。用于图 4(a) 的对照是消融 fixed-boxed 首次提议 $T_3$ 与经典冻结 TT SPEF LR 提议 $S_{18}$ 的物理核验。它们均进入允许至多一次邻线修复的同一执行协议，且第一次物理实现即结束各自核验。本轮未启动 EDA。以下 $T_3$、$S_{18}$ 分别指这两条原始执行记录。

| 项目 | $T_3$，fixed-boxed 首提 | $S_{18}$，经典 LR 物理核验 |
|---|---:|---:|
| 替换数 | 3 | 18 |
| 初始窗口的局部标记 | 0 | 17 |
| 初始归因释放邻线 | 0 | 7 |
| 配置允许／实际调用的修复重试 | 1／0 | 1／0 |
| 路由器 DRC／移除保护后的独立全块 DRC | 0／0 | 0／0 |
| SS Hold WNS（ps） | 55.138116294984 | 55.754956207466 |
| 相对布线后参考的 SS Hold WNS 变化（ps） | −0.157652 | +0.459188 |
| 门控结果与 SEC | SS Hold 回归，未进入 SEC | FF／TT／SS 时序门全部通过，SEC 11089 已证／0 未证 |

参考 SS Hold WNS 为 55.295767964481 ps，Hold 绝对下限 0，数值容差 0.001 ps。两个请求中的三个确切动作是 `\_10814_=sky130_fd_sc_hd__xor2_2`、`\_10992_=sky130_fd_sc_hd__xor2_2` 与 `\_11167_=sky130_fd_sc_hd__xor2_2`。以“实例＝目标单元”为集合元素逐项核对，$T_3\subsetneq S_{18}$。因此，对这组冻结输入和执行协议，以最终物理实现及同一门控定义的可行集合族不具向下封闭性。窗口标记属于初始诊断，两个端点最终均通过全块 DRC。

## 固定的执行协议

- 两案绑定同一个 SKY130HD AES 矩阵配置、资格核验结果、已筛选 18 动作池和保护 scope。矩阵配置还绑定同一份控制 ODB／DEF／Verilog／SDC／SPEF、源 FF／TT／SS Liberty、RC 设置与抽取规则、OpenROAD／OpenSTA／Yosys。OpenROAD 可执行文件 SHA-256 为 `2d9662715130538b50e93b614c33099a5e183eef0cc31b642099daea8d203e19`。原始绑定和完整哈希见 [输入清单](R10_MATCHED_COUNTEREXAMPLE_INPUTS.json)。
- 两个驱动均使用 `ColdOnlineComparison.attempt`。窗口诊断采用 `diagnose_boxed`，外扩 1.0 个行高（2720 DBU，即 2.72 μm）。初始走线使用冻结连接与本次替换的直接信号线，加入窗口检出的归因邻线，保护其余冻结走线。两案均配置最多一次由全块 DRC 标记触发的邻线修复，实际 `passes` 都只有 `initial`。初次 DRT 均使用四线程、一次内部 pin access、从冻结 ODB 保留的 guides、`-verbose 1 -droute_end_iter 64`，且均未传入 `-or_seed`。 [fixed-boxed 驱动](../tcad_v4_revision_20261126/run_v4_windowed_ablation.py) · [经典 LR 驱动](../tcad_external_baselines_20261125/run_lr_4designs.py) · [共用执行器](../tcad_ibex_20261123/run_aes_cold_online.py) · [保护式后端](../tcad_ibex_20261123/run_aes_protected_online.py)
- 两案按顺序执行窗口诊断、DRT／RCX、FF STA、TT STA、SS STA 与去保护的独立全块 DRC。两案逐阶段配置上限及有效上限均为 60／240／180／180／180／120 s。同一门控策略按视图检查 Setup WNS／TNS 与 Hold，窗口标记用于选取初始释放集合。通过物理和时序门的请求进入 SEC，$S_{18}$ 实际外层 SEC 上限 210 s，内层 Yosys 上限 180 s。$T_3$ 的 SS Hold 失败在 SEC 前终止。 [执行台账与原始回执](R10_MATCHED_COUNTEREXAMPLE_ORIGINALS.zip) · [核验值](R10_MATCHED_COUNTEREXAMPLE_VERIFIED.json)
- 两案的外层任务计时不同。fixed-boxed 首次请求处还有 606.63696756 s，其 720 s 外层窗口已计入原筛选 113.36303244 s；经典 LR 完成提议后按 600 s 的物理外层窗口执行。两次均在各自外层窗口内完成，逐阶段的有效限时与配置限时一致。固定执行协议指上面的输入、诊断、受保护实现与门控设置。

## 原 Hybrid 探针口径

V4 Hybrid 的乐观全池探针也提交同一 $S_{18}$。该探针直接调用一次 `physical`，受 180 s 探针子窗口约束。其 DRT／RCX、FF、TT、SS 和独立全块 DRC 的有效上限分别约为 171.626、88.215、83.916、80.122、75.328 s。原 Hybrid 探针与经典 LR 的 $S_{18}$ 实现所得 ODB、DEF、Verilog 均逐字节相同，三视图数值及 SEC 计数一致，SPEF 唯一字节内容差异为 `*DATE` 行。图 4(a) 的固定协议对照取经典 LR 原件。Hybrid 探针用于其原有调度、用时和面积结果。 [探针驱动](../tcad_v4_revision_20261126/run_v4_hybrid_faeco.py)

## 原件与核验

| 原件目录 | 归档采用的角色 |
|---|---|
| `/home/toylog/faeco_v4_windowed_ablation_20261126_v1/sky130hd_aes/fixed_boxed` | `subset`，`fixed_online/01` |
| `/home/toylog/faeco_tcad_lr_4designs_20261126_v1/sky130hd_aes` | `superset`，`physical` |
| `/home/toylog/faeco_v4_hybrid_faeco_20261126_v1/sky130hd_aes` | `probe`，`phase1_optimistic_probe` |

[原件 ZIP](R10_MATCHED_COUNTEREXAMPLE_ORIGINALS.zip) 含 78 个原始日志、Tcl、请求及收据文件，[输入清单](R10_MATCHED_COUNTEREXAMPLE_INPUTS.json) 绑定原始路径、大小和各自 SHA-256。体积较大的端点和冻结输入保留在 WSL 原件目录，并已通过哈希复核。将 ZIP、输入清单与 [核验脚本](verify_matched_counterexample.py) 置于同一目录后可用 Python 3 执行：

~~~bash
python3 verify_matched_counterexample.py
python3 verify_matched_counterexample.py --verify-live
~~~

第一条命令重算归档内部的绑定、协议和反例数值。第二条在可访问原 WSL 路径的环境中额外复核冻结输入与端点原件哈希及 SPEF 去日期后内容。 [已执行核验输出](R10_MATCHED_COUNTEREXAMPLE_VERIFIED.json)
