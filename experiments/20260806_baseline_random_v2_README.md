# 随机顺序基线（修正版）3 种子实验说明

## 背景：发现并修复 --random-order 未真正打乱的 bug
- 原实现把 shuffle 嵌套在 `if args.strategy_priorities:` 分支内，基线运行未传 priority table 时**不会打乱候选顺序**，三个种子结果完全一致（本质仍是默认顺序的"伪随机"基线）。
- 修复：shuffle 移到独立分支（无论是否用优先级表都打乱），并复用同一 RNG 实例（避免同长度列表被施加相同置换）。
- s27 验证：seed 20260807 与 20260809 的接受路径 trial_id 不同（_11_ 的 trial_id 2 vs 3），打乱生效。

## 3 种子（20260806/07/08）8 电路运行记录
- 目录：20260806_baseline_random_v2_seed{20260806,20260807,20260808}
- 命令：run_baseline_G_batch.py --random-order --seed N --out-dir ...（内部 run_hybrid_repair.py --workers 2）
- 工具链：OSS-CAD 0.67 映射网表（复用 20260805_tcad_sprint1_iscas89）、OpenSTA 3.1.0（WSL2）、周期 0.5ns、3 轮、接受规则=严格改善 WNS。
- 进度日志：20260806_baseline_random_v2_seed*.log

## 观察（截至部分完成）
- s27/s382/s420 三种子一致：-0.18 / -0.81 / -1.17
- s641 出现种子差异：seed06/07 = -0.99、seed08 = -1.16（-0.99 优于混合 -1.59 与纯 G -1.18）
- s713：seed06/07/08 均 -1.28
- s820（seed08）：-1.17

## 待办
- 全部跑完后汇总 8 电路 × 3 种子均值±std，更新论文 sec:baseline 与 fig_baseline。
