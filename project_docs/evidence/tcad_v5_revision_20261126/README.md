# FAECO V5 Revision Experiment Suite (`tcad_v5_revision_20261126`)

本目录包含 V5 补强实验、收据和无 EDA 预检。已验结果与活动批次见 [V5 实验报告](REPORT.md)，原中断点见 [执行交接](../../HANDOFF_2026-11-26_V5_EXEC.md)。

## 快速运行（WSL2 Ubuntu，独占 6 核 `taskset -c 0-5`）

```bash
# 1. 2 秒预检（验证导入、先决路径与离线反例提取）
python3 smoke_verify_v5.py

# 2. 顺序执行各阶段，日志写入 /home/toylog/faeco_v5_master.log
bash run_all_v5_experiments.sh

# 3. 或分阶段运行
bash run_all_v5_experiments.sh --stage 1   # ~5-8 min: 功耗补测 + 7nm 5组非零DRC + 4线程DRT 3x确定性
bash run_all_v5_experiments.sh --stage 2   # UART Setup 去重与原生 recover_power 的保护后端评估
bash run_all_v5_experiments.sh --stage 3   # 8 臂，每臂 720s 计费窗，另含参考资格
bash run_all_v5_experiments.sh --stage 4   # 6 个新测臂，每臂 720s 计费窗，另含参考资格
bash run_all_v5_experiments.sh --stage 5   # 独立构建和资格通过后执行 3 个候选臂

# 只检查独立 10ns 参考点。与其他 EDA 串行执行
taskset -c 0-5 python3 -B run_v5_step5_10k_timing_closed.py --reference-only
```

Stage 2–4 的已完成键可续接。Stage 2B 区分实例不在冻结网表、触及受保护时钟网、工具超时以及完成物理评估后的通过或拒收。AES 额外报告排除时钟网动作后的数据网投影。Stage 4 的纯微批次与默认探针是历史参照，双 AES 新测子预算为 60、120、240 s。Stage 5 的完整流程保留真实 ORFS 合成时钟目标、全部 I/O 延时和三角资格，参考点未合格时停止候选搜索。

详细交接、实验与审稿条目映射及跑完后的 V5 改稿清单见 [HANDOFF_2026-11-26_V5.md](../../HANDOFF_2026-11-26_V5.md)。
