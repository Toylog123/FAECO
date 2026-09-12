# 证据索引

按域列出证据包。**新增证据时在此登记一行**。

> 本项目实验证据的组织方式：`experiments/<日期>_<主题>/` 目录为原始运行证据（git-ignored，
> 总索引见 `experiments/INVENTORY.md`），其汇总口径进入 `experiments/RESULTS.md` + `results.json`
> 并由论文引用。下表登记**进论文/汇总的关键证据域**及其产物路径。

| 域 | 实验 / 日期 | 路径 | 基线 | 关键结论 | 状态 |
|----|-------------|------|------|----------|------|
| iscas89-main | 20260826 统一批量（效率优先配置） | `experiments/20260826_iscas89_main/` + `experiments/20260826_aggregation/summary.json` | d329f19 前基线 | 8/8 严格 WNS 改善；SEC 8/8 | active |
| itc99-main | 20260826 统一批量 + b17 phase-2（20260908） | `experiments/20260826_itc99_main/`、`experiments/20260908_phase2_b17_resume/` + 聚合 | 同上 | 18/19 严格改善（b06 持平）；b17 +0.38 ns @180 s | active |
| picorv32 | 20260826 异构三子模块 | `experiments/20260826_picorv32_hetero/` + 聚合 | 同上 | +1.13 / +0.07 / regs N/A | active |
| sec | 20260826 SEC + 20260908 b17 phase-2 SEC | `experiments/20260826_sec/summary.csv`、`experiments/20260908_phase2_b17_resume/sec/` | 同上 | 30 实例 29 修改、28/29 完全证明 | active |
| ablation | 20260826 消融（纯 G/纯 B/随机 3 种子/hold） | `experiments/20260826_ablation_*/` + `experiments/20260826_aggregation/ablation_summary.json` | 同上 | 混合 20 轮均值 1.07 ns vs 纯 G 0.16 | active |
| pr-validation | 20260807 OpenROAD 布局+全局布线估计 | `experiments/20260807_real_pr_iscas8/` | 同上 | 5/8 保持改善、1 持平、2 退化≤0.02 ns | active |
| joint-depth | 20260908 b17 joint-depth 消融 | `experiments/20260908_joint_depth_ablation/` | 同上 | depth=4 达 +0.43 ns（批量外探索上限） | active |
| hold-mode | 20260908 ITC-99 b01–b14 hold 模式 | `experiments/20260908_hold_mode_itc99/` | 同上 | 仅 b01 改善 min_slack；诚实 limitation | active |
| multi-iter | 20260908 多轮消融 + --no-early-stop 修复 | `experiments/20260908_multi_iter_ablation/`、`experiments/20260908_multi_iter_fix_full/` | 同上 | b17 多轮 516 STA 无改善（actionable 受限，诚实记录） | active |
