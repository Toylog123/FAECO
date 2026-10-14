# r21 配图与计数证据交叉表

本轮为已有归档重算与图件修订，无新EDA。输入文件指纹见 `paper/zh/figures/data/plot_specs/r21_source_manifest.json`。

| 位置 | 族/输入 | 口径 | 派生证据 |
|---|---|---|---|
| 图4 | B统一summary | 29有效setup实例，regs N/A | fig4_unified_gain_r21.csv |
| 图5、表11新STA | D 40个eval_trials及run_config | OpenSTA来源、有限wns、非cache；Fixed1947/EMA2003/随机2439,2476,2527 | fig5_budget_curves_r21.csv、fig5_sta_count_audit_r21.csv、r21/sta_ledger_audit.json |
| 表11评估记录 | D trials全数 | 4146/4883/随机均值5624，含前置拒绝及cache | 同上 |
| §4.3 3363/664/104 | B main19，b17替换180s批次 | 全部候选评估记录；18新schema实际STA2890、b17未知 | r21/sta_count_followup.md |
| 图6 | A→A′同候选 | 理想线网/全局布线估计分别对各自baseline | fig6_physical_transfer_r21.csv |
| 图7 | F L1 | 126候选、76降深度、0正WNS、36零、90负；s641零 | fig7_s_boundary_r21.csv |

C历史策略枚举与当前双割的机制归因分开。1.07/0.16/0.54/0.40的原收益值保留；C随机臂不含JOINT，不能作为纯排序对照。
