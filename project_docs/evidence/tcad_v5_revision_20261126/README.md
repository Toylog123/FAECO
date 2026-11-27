# FAECO V5 Revision Experiment Suite (`tcad_v5_revision_20261126`)

[论文图表和复算入口](REPRODUCIBILITY.md)提供标准库复算脚本与代表性原件包。核验 SHA-256 时请使用保留仓库字节的检出，例如运行 `git -c core.autocrlf=false clone`，以免换行转换改变收据指纹。

本目录包含 V5 补强实验、收据和无 EDA 预检。已验结果与活动批次见 [V5 实验报告](REPORT.md)，原中断点见 [执行交接](../../HANDOFF_2026-11-26_V5_EXEC.md)。

## 命令展开与实跑

以下命令在 WSL2 Ubuntu 中执行。先从本目录展开顺序并核对路径，命令展开不会运行 EDA，也不会创建输出、锁或日志。

```bash
bash run_all_v5_experiments.sh --plan
bash run_all_v5_experiments.sh --stage 4 --plan
bash run_all_v5_experiments.sh --stage 5 --plan
```

实际运行会获取共享 EDA 锁并按列出的顺序绑定逻辑 CPU 0–5 串行执行。Stage 4 包含先跑双 AES 的 60/120/240 s，再跑两个同协议 0 s 对照。Stage 5 先执行 10 ns 和原 40 ns 的 reference-only 反证，只有本次发布的参考拒因与原记录匹配才继续，最后执行 tc40ns_mmmc_drv 的严格参考资格与三臂比较。Stage 3 和 Stage 4 各有八个 720 s 臂，选择阶段前应预留参考准备时间与外层退出开销。计费臂的子超时和验收门由各驱动控制。

```bash
# 本机挂载、输入与工具齐备后的离线先决项检查。
python3 -B smoke_verify_v5.py

# 从既有原始目录和收据续接。省略 --stage 会执行完整顺序。
bash run_all_v5_experiments.sh
bash run_all_v5_experiments.sh --stage 2

# 在独立目录重建结果。再次使用同一路径可续接该目录。
bash run_all_v5_experiments.sh --stage 5 --output-root /home/toylog/faeco_v5_replay

# 从独立的新 run-* 子目录仅跑 Stage 4 两个零秒对照。
bash run_all_v5_experiments.sh --matched-zero --force --output-root /home/toylog/faeco_v5_replay
```

默认使用既有 V5 原始目录和收据，Stage 1 有现存收据则复用，Stage 2–4 由驱动按键续接，Stage 5 校验已有资格和搜索证据。使用 --output-root 时，新版 V5 原始产物与汇总分别写入指定根的阶段子目录和 receipts/。使用 --force 时总是分配新的 run-* 子目录，省略 --output-root 时使用 /home/toylog/faeco_v5_reruns。强制重建保留既有证据，并仍读取驱动所需的冻结前置输入。默认总日志为 /home/toylog/faeco_v5_master.log，共享锁为 /home/toylog/faeco_v5_eda.lock。可通过 FAECO_V5_LOG_FILE、FAECO_V5_EDA_LOCK、FAECO_V5_CPUS 改变外壳配置。并行工作应使用同一个 EDA 锁，计时复验保持报告的 CPU 绑定。

## 主机适配边界

启动器从自身位置解析驱动。各阶段驱动与复用的前代评估器仍绑定本机的 /mnt/d/BaiduSyncdisk 仓库资产、/home/toylog 冻结输入与历史基准、ORFS/Liberty/OpenROAD 以及 STA/SEC 包装器。--output-root 只重定位本轮输出。40 ns 处理器另有已实跑的隔离捕获与重建入口，从独立输入副本执行 RTL 综合、参考资格、首批候选及完整三臂在线搜索。SEC 截停的进程组修复由同输入短窗与足窗回归验证，并已完成修复后的三臂复跑和进程观测。完整异机重建需要对应工具、冻结输入及 Linux 基础环境。计时比较说明运行主机和 CPU 条件。 [隔离捕获与重建](REPRODUCIBILITY.md#从独立输入副本重建-40-ns-处理器参考) · [V5 实验报告](REPORT.md)

Stage 2–4 的已完成键可续接。Stage 2B 区分实例不在冻结网表、触及受保护时钟网、工具超时以及完成物理评估后的通过或拒收。AES 额外报告排除时钟网动作后的数据网投影。Stage 4 保留历史纯微批次和默认探针读数。双 AES 新测子预算为 0、60、120、240 s。历史 0 s 的派发或拒收复用规则与 V5 不同，使用同协议补测作为直接对照。Stage 5 的完整流程保留真实 ORFS 合成时钟目标、全部 I/O 延时和三角资格，参考点未合格时停止候选搜索。

10 ns 参考点已完成布线，SS Setup 与异步 reset removal 未达严格时序资格。[10 ns 资格收据](V5_STEP5_TC10NS_QUALIFICATION.json) 记录了该次结果。40 ns 配置在 TT／SS／FF 单元角上执行原生时序修复，三个角的 Setup 和 Hold 均非负，TT 的一处引脚同时超过转换时间与负载电容上限。[40 ns 资格收据](V5_STEP5_TC40NS_MMMC_QUALIFICATION.json) 电气变体在原生全局布线中为 `repair_design` 加入 15% 电容裕量和 10% 转换时间裕量，三个配置的 I/O 延迟均为绝对 2 ns。当前仅电气裕量变体通过完整参考资格。选择 Stage 5 将自动按顺序完成三种参考变体及合格参考上的三个在线比较臂。[合格参考收据](V5_STEP5_TC40NS_MMMC_DRV_QUALIFICATION.json)

详细交接、实验与审稿条目映射及跑完后的 V5 改稿清单见 [HANDOFF_2026-11-26_V5.md](../../HANDOFF_2026-11-26_V5.md)。
