# R22 pilot 动态独立审计

日期：2026-10-14。审计对象为保留的 `experiments/20261014_r22_cut_ablation/`、production pin `28c3c2b5c6325ffbad4e4ac54cc3caab237d68a5`。审计者没有启动 EDA、改原输入或 runner 结果。主线报告 session 66717 以 exit 1 停止；本次实际读取 batch_failures、两份 runner.log、result/trials/config/preregistered/input 收据和 SEC raw 网表。

## 动态门结论

**pilot 未通过，扩展门关闭。** 18 个预锁运行中只有 s27/W0、s382/W0 已执行；二者 runner exit 0，最终 SEC 都因 helper 内容改变而在证明启动前拒绝。通过动态门 0/18，其余 16 个没有启动，不能当失败试验或完成结果。

| 已运行对象 | 初始WNS | runner报告最终WNS | 新候选STA / 预约数 | records | 显式cache | 无launch原因 | 最终SEC |
|---|---:|---:|---:|---:|---:|---|---|
| s27/W0 | −0.27 | −0.17 | 12 / 12 | 14 | 0 | 2项F1前置拒绝 | helper改变，未启动证明 |
| s382/W0 | −0.98 | −0.93 | 11 / 11 | 13 | 0 | 2项F1前置拒绝 | helper改变，未启动证明 |

条数差不是缓存数；上表按 `sta_executed`、`skipped_duplicate`、`n_cache_replays` 与 failure 字段实查。原速记“cache2”已撤回。完整逐项检查、artifact hashes 与 helper 原文保存于 `PILOT_DYNAMIC_AUDIT.json`。

## 已证实的根因与通过漏洞

1. 两份初始 mapped 网表均为 helper-first：先 `module dff`，后实际 circuit。s27 已提交 B 动作 `_11_.A2`，s382 已提交 B 动作 `_073_.B1_N`；都关联真实 STA seq=5、`accepted=True`、`committed=True` 且原 trials `failure_events=[]`。
2. `insert_buffer` 在全文找到目标实例并重接输入，把新 wire 加到全文最后一个 wire 后，却把新 buffer 放在全文第一个 `endmodule` 前。结果 s27 的 `_bufb__11__A2` 和 s382 的 `_bufb__073__B1_N` 出现在 dff helper 内，接入只属于 circuit 的 `_03_` / `_021_` 网。helper 变化是实际多了一只门，不能用文本规范化或覆盖 helper 消除。
3. 旧 local F1 按全文实例/网名构造 identity buffer 连通性，旧 F2 解析器把所有模块的 inputs/outputs/wires/gates 合到一域；新 buffer 和主模块新 wire 因而在错误的合并图内形成虚假闭合。实际调用旧 full-text F1/F2 均返回 pass；只取实际 circuit 后，两份 F2 都返回 `declared-undriven`，新网分别为 `_03___buf__11__A2`、`_021___buf__073__B1_N`。全网表 SEC 的 helper 字节锁正确拒绝了这条错误提交路径。

此前单模块 B 声明/闭合探针没有覆盖真实 helper-first 多模块输入；这是静态测试输入域缺口，不能说 644 通过就证明真实 mapped 网表安全。归因为**实现 bug + 安全检查 namespace 缺口**，不是 cost/cover 机制被推翻，也不是实验输入损坏。

## 其余动态链路实查

两份实际 argv 与注册命令一致，政策均 weighted_st/weighted/configured，五权重1、0.5ns、20轮、500候选STA、workers1、R/G/B、joint_k2、S/TOPOLOGY off。原输入/共享 mapped/臂 mapped SHA 与收据一致；SEC raw initial 等于共享 mapped，raw final 等于已提交 state。真实 events seq 唯一且与非cache trials 一一对应；新 launch 数=预约数≤500；按原 schema 重算 observed/valid curves 与归档一致；pool origin 均只 weighted。

这些一致性不能使错误网表合法。原 `B_valid` 首次改善均 seq=5，报告收益分别0.10/0.05ns，但其合法性建立在有漏洞的 local 门上且最终 SEC 未通过，**不可作为有效时序/机制收益引用**。没有 W1/U0/U1/C 等比较，cost 是否改变真实候选身份、Cw 是否提供额外合法机会、cover-only 与 Full 优劣均尚不可识别。

## 修复与恢复边界

主线授权本审计者仅修 `buffer_insertion.py`，新增 `test_r22_multimodule_buffer.py`；root 处理 R/G namespace、evaluator 的 top模块构造、F1/F2 与 batch 失败归档。B修复采用公共 `verilog_modules.module_spans`：以显式 top_module 或唯一实例确定 module span，重接/声明/插入全部在该 span 内；重复实例未指定 top、目标模块内重复实例、显式目标缺失均抛 ValueError；其他模块逐字保持。API 新增 keyword-only `top_module: str | None = None`，既有单模块/未知实例 no-op 兼容保留。

新增最小 helper-first/top-first/top-middle、重复实例命名空间及两份真实冻结 mapped 输入测试首次 **9 failed / 1 passed，0.91s**，已复现旧错误与缺失 API。修复后联合新10项、既有B7项、静态动作13项实际 **30 passed / 0 failed / 0 skipped，1.00s，exit0**，120s超时包装，JUnit存于 `buffer_namespace_junit.xml`。此处两份真实 pilot 输入确实被执行；在不带实验归档的新 checkout 中，这两项明确 skip，8项自包含 namespace 测试仍执行。生产/测试/公共utility SHA256 已写JSON修复收据；再次实查原 pilot artifact hashes 全部不变。尚未将这30项冒称修复后的整体回归或真实SEC通过。

修复后须新 source pin、独立 v2 实验目录，按预锁配置重跑受影响矩阵；保留本次失败数据。只有固定两电路九臂共18个运行通过动态门，才可扩其余六电路；不放宽 SEC、不关 B、不事后调整候选臂以换正收益。
