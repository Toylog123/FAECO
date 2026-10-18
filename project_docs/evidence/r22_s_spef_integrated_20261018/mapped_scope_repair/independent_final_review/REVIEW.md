# OI048 冻结源码与证据最终独立审查

客户端日期：2026-10-18。结论：在已复现的 mapped 右侧 top、共同状态门、source-selection 窗口范围，修复与保留证据相符；整体验证 v5 当时仍运行，未据此宣布通过。审查没有运行新求解器、测试、Git 或正式 EDA，未修改生产和原始证据。

FINAL_RECEIPT.json 的 SHA 为 cd5361e2b378a5760b0accf20b2d61df3bb65d406abaafbd8c9f3402970fd5cf。独立核验其全部 176 件 artifact，四份 frozen/source/current SHA 全吻合。20 份实际归一化收据的源/准备输入/模型前后快照、输出 BLIF、命令日志和产物 SHA 全吻合。263 份被读原件及当前源码在审查前后 SHA/size 不变。

## 代码边界

mapped 右侧和 baseline backcheck 均调用现有 shared normalizer，BLIF 按引用图选唯一根并执行 hierarchy/flatten；独立多根默认拒绝，显式模型必须存在，reachable helper 保留。显式 mapped_top_module 是调用者给出的证明范围，不被冒称为另一模型的推断对应关系。

shared normalizer 首先保存 original_source，再进行 BOM 准备和 top 推断；准备后/启动前及调用后均核身份。ordinary/BOM 的 source-window 红灯日志明确两次返回 0 的错误，冻结测试与最后相邻绿色日志包含同样两个参数化控制。47 passed / 1 skipped 是其局部实际结果，未在本审查中重新执行。

共用 ABC 状态门先检查非零退出、多 root 诊断和显式输入/命令 Error，再识别不等价，最后才接受等价；保留 benign abc.rc 查找信息。实际零 rc 的 missing-input 原始日志已核，并与附加 success 文本仍判 error 的控制记录对应。

## 实际 native 证据

| 对象 | 实际保留结果 |
|---|---|
| single identity | pass，左右单 ztop，真实 ABC 等价日志 |
| single inverter | fail，左右单 ztop，真实 ABC 不等价见证 |
| dummy→inverter / inverter→dummy | error，右侧归一化记录多根 ValueError，未启动右侧 Yosys/ABC 比较 |
| explicit ztop | fail，明确选择实际反相模型 |
| explicit missing | error，模型不存在，右侧未启动 |
| reachable helper first | pass，最终只剩可达 ztop |
| ABC baseline | success/backcheck pass；保留 raw output，另归一化 optimized.normalized.blif 后比较 |

根使用原独立 probe 的重放与旧 fix_independent_review_v2 的 original.v 和两个 mapped BLIF 逐字节相同。single inverter 旧/新均 fail；dummy 多根旧 pass、新 error，原始日志分别体现选错第一 root 与唯一根拒绝。这里的 error 是范围不明确的非通过结果，不伪装成已经证明整机不等价。

本地审查器首轮假定了错误的 baseline 派生文件名，未写最终报告；失败脚本/日志/归因独立保留。按实际代码与目录定位 optimized.normalized.blif 后核验通过。该程序性失败未记作生产或科学实验失败。

## 保留限制

v5 当时未完成，当前报告不宣布全量通过。历史科学结果、四态、inout、S/SPEF 正式同族效果和论文数字不由本审查关闭。

范围外静态残项已另报主线：_tail 对 bytes 的直接字符串 join 可能在 mapped CEC timeout 的结果呈现中产生 TypeError。它是 fail-closed 的异常呈现问题，早于本次范围修复；本轮未扩探针或修改源码，不把它混成 OI048 继续错误通过的证据。
