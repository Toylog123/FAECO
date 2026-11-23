# SKY130 十个 v22 物理端点追溯

2026-11-23。从保留的路由产物、Tcl、OpenSTA 原始日志和 Yosys 回执对齐 v22 的十个名义正回收端点，并核对 s641 多角替代点和 s713/s832 历史 IO+OCV 回退点。完整路径、当前文件字节 SHA-256、绝对 setup/hold WNS、TNS 及相对差值见 [ENDPOINTS.json](ENDPOINTS.json)。此次追溯仅回读现存证据。

## v22 十个名义正回收端点

面积单位 µm²，百分数表示回收比例。各时序列为同一候选 `routed.v` 和 `routed.spef` 相对该列历史 CONTROL 的 `Δsetup WNS / Δhold WNS`，单位 ps。TT、SS、FF 三列取多角审计原始日志，IO+OCV 取十例复测原始日志。SEC 列为 Yosys 已证/未证 `$equiv` 个数。

| 电路 | 物理端点 | CONTROL → 端点面积 | TT | SS | FF | TT IO+OCV | IO+OCV 端点绝对 hold (ps) | 两态 SEC |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| s382 | [RUN_008](../../../scratch/tool_agnostic_iscas89/s382/evals/RUN_008/) | 1052.2592 → 1033.4912 (1.78%) | -6.705 / +0.000 | +34.940 / +0.000 | +1.724 / +0.000 | +15.465 / -0.059 | -100.819 | 101/0 |
| s420 | [RUN_010](../../../scratch/tool_agnostic_iscas89/s420/evals/RUN_010/) | 942.1536 → 889.6032 (5.58%) | +4.120 / +0.013 | +17.917 / +0.074 | -2.840 / +0.014 | +5.732 / +0.689 | -66.746 | 95/0 |
| s641 | [RUN_005](../../../scratch/online_ablation/s641_ablation/evals/RUN_005/) | 1133.5872 → 1111.0656 (1.99%) | -0.427 / +0.104 | -18.505 / +0.791 | +2.104 / -1.400 | +4.907 / -0.362 | -82.921 | 136/0 |
| s713 | [RUN_008](../../../scratch/tool_agnostic_iscas89/s713/evals/RUN_008/) | 1131.0848 → 1104.8096 (2.32%) | +0.629 / +3.646 | -4.583 / +41.831 | +0.404 / -3.944 | -10.147 / +0.197 | -98.116 | 134/0 |
| s832 | [RUN_009](../../../scratch/tool_agnostic_iscas89/s832/evals/RUN_009/) | 1167.3696 → 1147.3504 (1.71%) | -4.165 / +2.643 | +40.008 / +4.722 | -5.409 / +2.053 | -17.204 / +0.156 | -74.524 | 162/0 |
| s953 | [RUN_001](../../../scratch/online_ablation/s953_ablation/evals/RUN_001/) | 2433.5840 → 2417.3184 (0.67%) | -9.880 / +2.988 | +90.459 / +7.789 | +2.310 / +2.038 | -7.108 / -1.027 | -119.652 | 271/0 |
| b04 | [RUN_006](../../../scratch/tool_agnostic_itc99/b04/evals/RUN_006/) | 4078.9120 → 4043.8784 (0.86%) | +5.311 / +0.070 | +53.423 / -0.130 | +3.409 / -0.102 | +5.961 / +3.197 | -120.096 | 357/0 |
| b05 | [RUN_005](../../../scratch/universal_batch_recovery/b05/evals/RUN_005/) | 3424.5344 → 3305.6704 (3.47%) | +6.706 / +1.894 | +20.826 / -2.327 | +3.779 / -1.383 | +3.834 / +2.829 | -38.507 | 404/0 |
| b11 | [RUN_005](../../../scratch/tool_agnostic_itc99/b11/evals/RUN_005/) | 3181.8016 → 3153.0240 (0.90%) | +4.989 / -1.632 | +20.655 / -0.467 | -29.022 / -0.177 | +5.225 / +0.473 | -81.408 | 346/0 |
| b12 | [RUN_005](../../../scratch/universal_batch_recovery/b12/evals/RUN_005/) | 7977.6512 → 7912.5888 (0.82%) | +1.441 / +0.089 | +64.588 / +0.306 | +29.798 / +0.066 | +1.461 / -4.932 | -45.881 | 761/0 |

历史名义选择口径下，十个端点面积均下降（0.668%–5.578%，平均 2.010%），名义评估 `Δsetup ≥ −10 ps` 且相对 hold 非退化。在本表的多角 TT 回读列中，b11 对 **R** 的 hold 下降 1.632 ps，其名义选择对 **C** 报告为 +0.620 ps。固定这十个候选端点后，SS setup 9/10 满足 10 ps 门限，FF hold 5/10 满足严格相对非退化。若还对 FF setup 应用 10 ps 门限，b11 下降 29.022 ps。

同一批候选的 IO+OCV setup 满足 10 ps 门限的有 8/10，s713 和 s832 超限。IO+OCV 相对 hold 下降的有 s382、s641、s953、b12。十个候选点及其各自历史 CONTROL 的 IO+OCV 绝对 hold 均低于零，回读范围分别为 -120.096 至 -38.507 ps、-123.293 至 -40.949 ps。联合结论须同时标明端点、CONTROL、约束模式和相对/绝对门限。

## 多角替代与 IO 回退

| 电路和角色 | 端点 | CONTROL → 端点面积 | TT | SS | FF | TT IO+OCV | IO+OCV 绝对 setup / hold (ps) | 两态 SEC |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| s641 多角替代 | [RUN_005](../../../scratch/multicorner_gated_s641/evals/RUN_005/) | 1133.5872 → 1126.0800 (0.66%) | +4.740 / +1.204 | +71.686 / +2.672 | +2.277 / +1.286 | — | — | 136/0 |
| s713 历史 IO 回退 | [s713](../../../experiments/20261115_p1_resizer_vs_faeco/arms/Resizer/s713/) | 1131.0848 → 1131.0848 (0.00%) | — | — | — | +0.000 / +0.000 | -2172.881 / -98.219 | CONTROL 恒等 |
| s832 历史 IO 回退 | [s832](../../../experiments/20261115_p1_resizer_vs_faeco/arms/Resizer/s832/) | 1167.3696 → 1167.3696 (0.00%) | — | — | — | +0.000 / +0.000 | -1809.225 / -75.316 | CONTROL 恒等 |

- s641 两个 `RUN_005` 来自不同目录和不同替换集合。替代点的同库 SS setup 改善 71.686 ps，FF hold 改善 1.286 ps，正回收 0.662%。替代点 IO+OCV 没有绑定的日志。其历史 TT 比较的 CONTROL 载入 OpenROAD-src 测库，候选载入 ORFS 库。当前 WSL 两个 TT 库的 SHA-256 分别为 `92eb4e93a3d4c2563018ac81cdec2f02fdeaced9b39337ed5c141fa63e0ad8f8` 和 `ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9`。表列出该次原始读数，TT hold 依该读数为 +1.204 ps。
- s713、s832 的历史 IO 在线搜索各检查十次，最后回退至原始 Resizer 布线 **R**，面积收益为零。“IO+OCV setup 10/10 达标”由 8 个正回收端点和这 2 个零回收端点组成，两次回退均继承原始 CONTROL 的负绝对 hold。

## 路由输入、时序 CONTROL 与形式证明绑定

- **R** 是候选 `flow.tcl` 实际读取的 Resizer 路由终点。ISCAS89 位于 `experiments/20261115_p1_resizer_vs_faeco/arms/Resizer/<电路>/`，ITC-99 位于 `experiments/20261113_itc99_recovery/arms/Resizer/<电路>/`。
- **C** 是后续回读用的独立重布线 CONTROL，位于 `scratch/iscas89_postroute_verify/<电路>/CONTROL/` 或 `scratch/itc99_postroute_verify/<电路>/CONTROL/`。R 和 C 的 `routed.v`、`routed.spef`、`routed.def` 分别用 SHA-256 标识。两者在 s713/s832 的三个文件上均有字节差异。
- 十个名义候选的 `flow.log` 均有 `PHYSICAL_OK`、`drc.rpt` 均为空。路由输入 DEF 仍在，历史候选的 Tcl 输出网表和 SPEF，未写出候选布线 DEF。s641 多角替代点同样缺候选布线 DEF。
- SEC 绑定通过去除无引脚 tap 实例、统一读入换行，再逐字符核对当前端点到原始 proof 输入。proof 文件的实际 SHA-256 与原始回执一致，十个名义端点的 Yosys 日志均有非空证明且未证数为零。这里的 SHA 标识现有产物，历史物理运行启动时的输入锁仍缺。

| 电路 | 候选路由输入 | 三角 CONTROL | IO+OCV CONTROL | SEC 金标准网表 | 候选 V / SPEF SHA-256 前缀 |
|---|---|---|---|---|---|
| s382 | R | R | R | R | b0e29995cb2f / 60e7d5188083 |
| s420 | R | C | C | C | c5ae9b11a2cf / c1dcf23fa55a |
| s641 | R | C | C | C | 8e9f927876c7 / 6c277673f191 |
| s713 | R | C | C | C | 0afee2bf242e / f553a9826412 |
| s832 | R | C | C | C | 000282489506 / 0bc1c195dac5 |
| s953 | R | C | C | C | 9d87158747c6 / 134aa81d15f0 |
| b04 | R | R | R | C | 760c0c626f84 / 73854232c5c9 |
| b05 | R | R | C | R | 554091991049 / 7d9ce5a1691a |
| b11 | R | R | R | R | 0aa51e08a495 / 4586df22a712 |
| b12 | R | R | R | R | 6efc656cacba / 1f6000e5766b |

名义选择的 CONTROL 时序取历史生产器记录。除 s382 的历史常量外，源于 C 的 `result.json`，其路径按行列于 JSON。s382 三角与 IO+OCV 的 R 是可回读的实物基准。b05 3.47% 的候选来自 `universal_batch_recovery/b05`，其三角重测也来自该目录。早期 `multicorner_signoff/b05_*` 使用 2.78% 的另一候选。

s713/s832 此后的联合门控使用各自固定的输入快照重测 CONTROL 和候选，为新端点保存布线后 DEF，并分别报告相对门限与绝对违例。

历史入口：[重布线与在线搜索](../postroute_recovery_20261120/REPORT.md) · [强基线与十例 IO+OCV](../postroute_strong_baselines_20261122/REPORT.md)。
