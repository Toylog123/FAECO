# FAECO 主数据字典（round 5）

更新时间：2026-08-11

用途：把正文、图表和摘要中的关键数字绑定到可复核的实验产物。状态只有在“数字、配置、原始产物和计算关系”均能对上时才标记为可回填。

## A. 主结果与策略实验

| 论文数据 | 数值/范围 | 权威来源 | 配置/口径 | 状态 |
|---|---:|---|---|---|
| 20 轮混合平均改善 | 1.074 ns | experiments/20260807_multiround_8c_067/convergence_summary.json | 20 rounds，R/G/B/JOINT，TNS-aware | 可回填 |
| 20 轮纯 G 平均改善 | 0.161 ns | 同上；逐电路 pureG 目录 | 同一 period/toolchain | 可回填 |
| 20 轮纯 B 平均改善 | 0.536 ns | 同上；逐电路 pureB 目录 | 同一 period/toolchain | 可回填 |
| 真实外层 8/8 严格改善 | +0.01--0.10 ns | experiments/20260804_loocv_real/summary.json | ideal-net OpenSTA；construction-level screening；无独立 SEC | 可回填，但须独立于20轮叙述 |
| 真实外层 STA 调用 | 4,8,3,1,1,3,3,4，总计27 | 同上及各电路 eval_trials.json | early-stop/LOOCV 批次 | 可回填 |
| 110 次全候选调用 | 8,12,12,3,3,18,43,11，总计110 | experiments/20260804_outerloop_grid/*_b1_fbon/*/eval_trials.json | b=1、feedback on 批次 | 已找到，但不能直接宣称与27次同空间同质量 |

ITC-99 主表的 19 个电路均有独立的 `outerloop_result.json`。逐项读取 `baseline_wns` 与 `wns_history[-1]`，并以 `n_candidate_sta_runs` 求和：19 个电路、18 个严格改善、b06 失败、1693 次候选 STA 调用。批处理时间和并发配置来自 `batch_progress.log` 与 `docs/project_management/work_log.md` 的 LOG-20260805-08（3 并发、约 12.5 分钟）。b18/b19 的 93/58 次调用属于独立补充实验，不计入这 1693 次。

## B. 27/110 对照核查

27 次批次的结果：

| 电路 | 基线 WNS | 终值 WNS | STA |
|---|---:|---:|---:|
| s27 | -0.28 | -0.21 | 4 |
| s382 | -0.94 | -0.93 | 8 |
| s420 | -1.78 | -1.75 | 3 |
| s641 | -1.86 | -1.85 | 1 |
| s713 | -1.86 | -1.85 | 1 |
| s820 | -1.42 | -1.36 | 3 |
| s832 | -1.15 | -1.12 | 3 |
| s953 | -1.48 | -1.38 | 4 |

110 次批次的 trial 数确实可逐电路相加得到 110，但其 outerloop_result.json 的终值为：

- s27 -0.21；
- s382 -0.92；
- s420 -1.51；
- s641 -1.85；
- s713 -1.85；
- s820 -1.28；
- s832 -1.12；
- s953 -1.38。

因此当前可证结论是：

> 两个既有批次分别记录了 27 次 early-stop 调用和 110 次 full-candidate 调用；二者的候选全集、排序版本和终值没有被统一元数据证明为完全相同。

在没有候选全集 hash、完整命令行和逐候选映射之前，不写“75.5% 且无质量损失”的强结论。

## C. 当前论文主图的来源一致性

图 1 / 主结果数组：

- baseline：-0.27、-0.98、-1.56、-1.63、-1.33、-1.19、-1.23、-1.31；
- fixed：-0.18、-0.89、-1.55、-1.59、-1.31、-1.17、-1.17、-1.27。

主图现在由 paper/zh/figures/gen_figures.py 和 gen_figures_nature.py 直接读取已审计产物：ISCAS89 读取 `experiments/20260807_real_pr_iscas8/pre_layout_audit_summary.json`，ITC-99 逐电路读取 `experiments/20260805_tcad_sprint1_itc99/*/*/outerloop_result.json`。ISCAS89 16 个 baseline/fixed 网表的预布局 WNS 已由同一 0.5 ns ideal-net OpenSTA 重新核验，并与图中数值逐项一致；因此图表不再依赖手填主结果数组。

图 6 / 收敛与基线表数组：

- 与 experiments/20260807_multiround_8c_067/convergence_summary.json 的混合、pureG、pureB、STA 数值一致；
- 可作为独立 20 轮策略实验表，不应作为图 1 的主结果来源。

## D. P&R 真实证据

原始日志此前位于 WSL：/home/toylog/pr_iscas8。现已归档到 experiments/20260807_real_pr_iscas8 对应 circuit/baseline 或 fixed 目录，并保留 final.odb；预布局两列另由同目录下的 `pre_layout_audit_summary.json` 和 16 份 `pre_layout_audit/sta.log` 复核。

| 电路 | baseline WNS | fixed WNS | ΔWNS | baseline TNS | fixed TNS | 证据 |
|---|---:|---:|---:|---:|---:|---|
| s27 | -0.36 | -0.22 | +0.14 | -0.67 | -0.46 | pr_run.log + final.odb |
| s382 | -1.16 | -1.02 | +0.14 | -15.77 | -14.58 | pr_run.log + final.odb |
| s420 | -1.80 | -1.82 | -0.02 | -15.74 | -15.81 | pr_run.log + final.odb |
| s641 | -2.10 | -2.02 | +0.08 | -27.17 | -26.79 | pr_run.log + final.odb |
| s713 | -1.59 | -1.58 | +0.01 | -23.00 | -22.87 | pr_run.log + final.odb |
| s820 | -1.52 | -1.49 | +0.03 | -6.92 | -6.83 | pr_run.log + final.odb |
| s832 | -1.51 | -1.51 | 0.00 | -6.94 | -6.85 | pr_run.log + final.odb |
| s953 | -1.60 | -1.61 | -0.01 | -33.58 | -33.79 | pr_run.log + final.odb |

已确认的 P&R 配置：

- OpenROAD v2.0-17598-ga008522d8；
- SKY130 HD merged LEF、sky130_fd_sc_hd tt_025C_1v80.lib；
- 0.5 ns clock；
- utilization 30、target density 0.7、met1--met5 routing；
- global placement、detailed placement、CTS、global route、detailed route；
- estimate_parasitics -global_routing；
- 16 个运行均有 final.odb。

限制：

- pr.tcl 没有指定 DRC report，日志出现 DRT-0290 “skipped writing DRC report”；
- 因此正文应写“OpenROAD 后布线时序对比”，不写“DRC-clean signoff”；
- 当前表 5 的数字已具备预布局 STA 日志、布线后 pr_run.log 和 ODB 证据，不需要为表 5 重跑；后续只在需要 DRC/多角或功耗拥塞证据时安排受控补跑。

## E. SPEF 与 Hold

SPEF 扫描：

- s382：理想 +0.01 ns；5 μm/unit 时 +0.03 ns；40 μm/unit 及以上为 0；
- b18：理想 +0.13 ns；2、5、10 μm/unit 时分别约 +0.11、+0.07、+0.03 ns；40 μm/unit 及以上为 0。

来源：

- experiments/20260805_parasitic_s382_scan/u*/summary.json；
- experiments/20260805_parasitic_b18_scan/u*/summary.json。

Hold：

- experiments/20260806_hold_repair_067/*/hold_result.json；
- 7/8 电路 improved=true，s27 未改善；
- hold_uncertainty_ns=0.8；
- 属于约束注入场景，不是自然 hold signoff。

## F. 代理评分的当前证据边界

## G. 失败类型记录边界

对当前 `experiments/` 下可解析的 `outerloop_result.json` 做了全目录审计：可直接追溯到的失败记录包括 F3（48 条）、F4（359 条）和 F6（11 条）。这三个数字来自多个实验批次，只用于判断记录边界，不作为论文中的统一失败率。F1、F2、F5 在代码的分类器、阈值或反馈接口中存在，但没有在现有主实验 JSON 中形成可审计的独立发生率；正文因此只把 F1--F6 写成机制定义，不写成六类均已完成实证消融。

当前代码已经具备：

- src/rseco/proxy_ranking.py；
- src/rseco/real_wns.py 的 proxy metadata 归档；
- scripts/run_outerloop_real_wns.py 的显式 `--proxy-ranking` 开关（默认关闭，以保持历史批次口径）；
- scripts/run_outerloop_batch.py 的 --no-proxy-ranking 转发；
- 28 个 focused tests 全部通过。

当前新增审计产物：

- `experiments/20260811_proxy_smoke_s27/s27`：1 个电路 smoke run，29 个候选均有 proxy features、rank 和实测 WNS；
- `experiments/20260811_proxy_outerloop_8c`：7 个电路完整落盘，s420 在父批处理超时前仅留下部分 STA 目录，故不作为完整 8 电路结果；完整 7 个电路均有逐候选 proxy 字段；
- 该批次的排序改变了历史 runner 的搜索轨迹，且并未复现旧 27 次批次的逐电路成功行为，因此不能把代理评分写成已验证的质量/效率提升结果；它目前只证明审计字段和 opt-in 执行链路已落地。

下一批真实实验必须至少归档：

1. candidate_id、circuit、iteration、strategy；
2. proxy features 和总排序值；
3. measured WNS/TNS、accepted、failure type；
4. candidate-space hash、命令行、工具版本；
5. full-eval 与 early-stop 的逐电路对照。
