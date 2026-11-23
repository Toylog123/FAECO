# ASAP7 GCD 三视图 CONTROL 预检

2026-11-23 · ASAP7-GCD-CONTROL-3VIEW-SMOKE · TCAD 证据准备

从既有 ORFS 最终端点读取 6_final.v、原 6_final.sdc 和 6_final.spef。核心时钟周期 310 ps 并使用传播时钟，虚拟时钟的输入、输出延迟为 62 ps。三个视图共享该次提取的 SPEF，各自载入完整的 ASAP7 RVT FF、TT、SS 五组 Liberty。源运行的详细布线报告为 DRC=0。复测使用 OpenSTA 3.1.0。

| Liberty 视图 | setup WNS (ps) | hold WNS (ps) | 回放状态 |
|---|---:|---:|---|
| FF | −37.960829 | +41.599637 | 完成 |
| TT | −166.709424 | +59.198008 | 完成 |
| SS | −401.929379 | +43.915302 | 完成 |

三次均测到了 setup 和 hold。绝对 hold 均非负。FF 回放与 ORFS 源报告的 −37.9608 / +41.5996 ps 在报告精度下相同。原始 DRC 绑定到既有详细布线端点。本次新增 3 次 STA，新增布线、RCX 和 SEC 均为零。库解析的 STA-1212 提示保留在原始日志。

第一次驱动预检漏加 Liberty 的固定文件名前缀，未启动 EDA。修复名称后，OpenROAD 26Q3 在读取原 ODB 时报告 0.142 高于其支持的 0.134，未取得 STA 测量。该诊断原件见 [失败日志](openroad26q3_odb_diagnostic/FF.log)。后续独立 STA 使用同一已布线端点的 Verilog、SDC 和 SPEF，不涉及 ODB 格式转换。保留的 ODB、DEF 和 Verilog/SPEF/SDC 指纹见 [配置](CONFIG.json)。

## 含义与下一个资格门

本次确认 423 个非填充标准单元的 GCD 可作为验证驱动的开发工件。三视图覆盖 Liberty PVT，使用同一 RC 提取结果。当前未测三种回收策略。端点无 hold 违例、存在 setup 负松弛，为调试相对 setup 预算提供了已知起点。

已实查 ORFS 的两份 Ibex 默认配置。ASAP7 与 SKY130HD 均以 ibex_core 为顶层并定义虚拟 I/O 时钟。ASAP7 默认周期 1000 ps，输入输出延迟各 200 ps。SKY130HD 默认周期 10 ns，输入输出延迟各 2 ns。两份配置可用于同架构的跨工艺开发对照，按照同一设计家族记账。尚未取得这两个配置在本轮的布线、RCX 和 hold 合格端点。随后另选未参与调参的设计家族作留出验证。

[运行脚本](run_gcd_smoke.py) · [结果 JSON](SUMMARY.json) · [投稿实验计划](../../planning/TCAD_SUBMISSION_PLAN_20261123.md)。在同一机器复测时，将脚本复制到 D 盘的空输出目录运行。脚本会读取固定绝对路径下的原始 GCD 五件。
