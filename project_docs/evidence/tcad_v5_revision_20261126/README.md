# FAECO V5 Revision Experiment Suite (`tcad_v5_revision_20261126`)

本目录包含响应第二轮同行评审（85/100，Major Revision 偏小修）的全部 V5 补强实验脚本、无 EDA 预检脚本与一键启动器。

## 快速运行（WSL2 Ubuntu，独占 6 核 `taskset -c 0-5`）

```bash
# 1. 2 秒预检（验证导入、先决路径与离线反例提取）
python3 smoke_verify_v5.py

# 2. 全量顺序执行 5 阶段（支持断点续跑，合计约 2.3 小时，日志写入 /home/toylog/faeco_v5_master.log）
bash run_all_v5_experiments.sh

# 3. 或分阶段运行
bash run_all_v5_experiments.sh --stage 1   # ~5-8 min: 功耗补测 + 7nm 5组非零DRC + 4线程DRT 3x确定性
bash run_all_v5_experiments.sh --stage 2   # ~15 min:  UART Setup去重消融 + 原生recover_power挂载保护后端
bash run_all_v5_experiments.sh --stage 3   # ~45 min:  UART & SKY130HD AES 四档预算(0/0.5/1/2%)独立在线搜索
bash run_all_v5_experiments.sh --stage 4   # ~40 min:  双AES Hybrid探针子预算(0/60/120/180/240s)敏感性
bash run_all_v5_experiments.sh --stage 5   # ~35 min:  万门级独立Timing-closed(SKY130HD riscv32i @ 10ns)硬门控实测
```

详细交接、实验与审稿条目映射及跑完后的 V5 改稿清单见 [HANDOFF_2026-11-26_V5.md](../../HANDOFF_2026-11-26_V5.md)。
