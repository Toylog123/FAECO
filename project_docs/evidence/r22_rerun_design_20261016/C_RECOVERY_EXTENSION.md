# C48 原族恢复增量复核（2026-10-16）

本包只扩展既有 `README.md`、`manifest_preview.json` 和历史 C 审计，不重复 806 个来源的全量审计，不改旧结果、生产源码或测试，不运行 EDA。`C_RECOVERY_EXTENSION.json` 登记本次 120 个增量/交叉比较文件的存在状态与逐文件 SHA256、五个 Git 源码 blob、检索命令和结果。`execution_ready=false`、`formal_source_pin=null`。以下“相同”均来自实际打开文件后的比较。

## 新增证据：十四份完整 trial 台账和终点跨表相同

08-26 pureG 的六例（s27/s382/s420/s713/s820/s832）与 `20260807_pureG_20round_067` 同电路 `hybrid_result.json` 的整个 `candidate_trials` 数组逐项相同；pureB 的八例与 `20260807_pureB_20round_067` 全部逐项相同。十四对文件的其他差异只有 `rounds_history`、`random_order`、`seed` 三个顶层字段。其初始 `mapped.v` 和最终 `mapped_hybrid.v` 也分别逐字节相同。

这比只比较 WNS/候选数强，建立了十四份完整 trial 内容及终点的交叉表。但它不证明“08-26 是复制旧结果”，也不证明“重新执行过”：确定性重跑和派生/补字段档案都可能产生这些观测。两份结果 JSON 本身 SHA 不同，未找到创建/复制转换记录，不能据此把旧 launcher 直接提升为 08-26 的实际 argv 或 runtime source pin。

旧 pureG 的 s641/s953 目录与 baseline 存在，但 result 和 final 均缺失；日志停在过程中，不能借给这两例完整旧 recipe/result 身份。16 对初始 mapped 均字节相同。具体比较和每个 SHA 在 JSON 的 `pure_arm_older_crosswalk`。

新增打开的旧 launcher：两族各有 `run_all.bat` 覆盖 s382/s420/s641，`run_rest.bat` 覆盖其余五例。旧命令模板为：

```text
python -u scripts/run_hybrid_repair.py --circuit <c> --period 0.5 --rounds 20 --only-strategy G --workers 2 --output-dir experiments\20260807_pureG_20round_067
python -u scripts/run_hybrid_repair.py --circuit <c> --period 0.5 --rounds 20 --only-strategy B --enable-buffer --buf-types buf_1,buf_2 --workers 2 --output-dir experiments\20260807_pureB_20round_067
```

这是旧目录的可恢复 launcher；对十四个相同 trial 档案提供有力 recipe 见证，仍不是 08-26 进程 argv。对照的 tns-aware、JOINT、STA cap、priority 是否因未写 flag 而等于某版默认值，依赖未恢复的实际源码，继续标为 unknown。

## 源码与随机调度补证

`cb0bc74b2eb5387f9ddb1c32fe9de7cd979e43e1:scripts/run_baseline_G_batch.py` 的 SHA256 为 `64a581087c001e451ee58662d2116b1391e08b86b338a9df50bafcdc1655070b`，与当前同名脚本逐字节相同。它构造 workers=2、按需 only-strategy 和 random-order/seed、2400 秒单电路外超时的命令。它默认 rounds=3，且不传 enable-buffer；其结果查询为 `<out>/<c>/<c>/hybrid_result.json`，不等于 C40 的 `<family>/<c>/hybrid_result.json` 布局。因此这是可复用历史批处理实现，不能作为缺失 C40 launcher 的替身。

同一 commit 的 `experiments/20260806_baseline_random_v2_README.md` 明确记录旧 shuffle 曾错误嵌入 priority 条件分支，修正版使用共享 RNG、无 priority 时也 shuffle。该说明对应 3 轮、20260806/07/08 种子的其他目录，不能错绑为 C 的 20 轮、seed1/2/3。`cb0bc74:scripts/run_hybrid_repair.py` 确有独立 `if args.random_order: rng.shuffle(cands)`；这证明一份可审查实现有正确调度，不能证明当时 dirty 执行树与该 blob 相同。

`526a77fdb55beed642287f2609e2c05130962a36` 的实际 diff 将并行候选从完成顺序改为提交顺序收集，再遍历全部结果选 best。该 tie 顺序是调度语义，不能因使用并行池改回 as_completed。当前 runner 与 scratch/codex_wt 备份 SHA 不同；保留多个快照不是自动恢复了实际运行版本。

本次对 reachable Git 全历史的限定检索，没有找到 C40 目录字符串的 tracked scripts 变更、v3 绑定的 scripts/docs 变更，或 canonical mixed/s382 的 mapped/result 历史。检索 argv/stdout 已登记；空结果只覆盖这些检索范围，不声称外部备份或不可达 Git 对象也不存在。

## s382：起点内容可供新重建，canonical 运行身份仍缺

canonical `20260807_multiround_8c_067/s382/{mapped.v,hybrid_result.json,mapped_hybrid.v}` 仍缺失。另一个实际打开的 sibling `20260807_multiround_s382_067` 有 1097 条 trial、WNS -0.98→-0.79，result SHA `5165a302e937c66c72cf2eb4f0844c71428df4e08762d71da22e9342ea59a32b`，它明确不匹配发布混合终点。

v3 sibling 有 910 条 trial、WNS -0.98→0.02、61 条 accepted 标记，result SHA `fc05c78d8d6a265bd1b8a8f9b6fed5d33066dbc75ee77ab72fc27d77400b48d9`。它与发布汇总数值一致仍不足以认定 canonical；本次未找到新增来源连接。两 sibling 的起点都为 `608cf28c7da49b245ec5cb44207552cd112a638275741c3eab74c13be0a06221`，与已审计其他 C/D 臂相同。

新 C 同族重建可预注册直接使用已有对照/D 的这一 SHA 起点，明确这是新运行选定的冻结输入；无需借入任何 sibling 的接受终点或 trial。但不能补写“canonical 起点文件已找回”，也不能从新跑结果反填 canonical 运行身份。

## 最小保留调度的安全适配设计（未实施）

复用历史 `run_hybrid_repair.py` 主循环，另加证据和安全接口；不要把其候选交给 C′ cut/evaluator 调度器取代主循环。新增 mapped-input 入口，复制并核验归档起点而不重新映射。新 source/Lib/model/input pin 在整体回归通过并提交后创建，执行前后核验；复用 common 的 `final_sec`、receipt、completion 验证，检查布尔 False，不把 unsupported/nonzero/timeout 当 complete。

必须保留的可测试顺序：

1. 每 pass 对当前 text 刷新多路径 STA，取得固定的 critical-instance 顺序；当前快照在 pass 开头解析 cells，不是每个候选后重新枚举关键路径。
2. 每实例从其当时当前 text 生成全部候选；候选共享该实例 base，全部评估后按提交顺序选严格 best，再提交最多一个。下个实例基于已经提交的 text；一个 pass 可以多次提交。
3. 单一 seeded RNG 在每实例候选列表内 shuffle；不打乱实例顺序、不改为首个改善即返回。workers 并发只在实例内，全部 join 后才允许提交。
4. 接受规则原样保留：WNS 严格增大，或启用 tns-aware 时 WNS **精确相等**且 TNS 增大；不引入 epsilon/新排序目标。整 pass 无改善停止，20 是上限。
5. mixed 的轮后 JOINT 阶段保留：从该 pass 已接受单点的 best_by_inst 取排序实例对，再受 joint-pairs 限制。不能改成全候选笛卡尔积、全轮一次提交或给随机臂补 JOINT。

JOINT 有需要明确保留和门控的细节：源码是在已提交 singles 的当前 text 上再次应用对应操作。R/G 同目标可能幂等，B 的二次应用却可能是不同或非法变换。适配必须记录真实 base/patch/candidate，复用修复后的编辑器和合法性门，不能因“为了保留旧调度”接受非法候选，也不能静默把 JOINT 改为在 pass 起点应用后仍称旧算法。先以 mock 构造重复 B/重名/未连接输入反例；若需要修正 JOINT 的数学定义，需作为明确算法变更另预注册并与旧定义区分。

安全和计数放在主循环边界：

- 所有完整候选在正确 top 上走当前 actual-Liberty metadata、physical instance 唯一、连接完整、F1/F2/多输出/三态语义门，随后才预约并启动真实 STA；提交复用已评估的确切 candidate bytes。绝不能仅靠末尾 SEC 来允许错误候选污染时序选择。
- 每 run/pass/instance/trial 使用不可覆写唯一目录，保存 base/candidate/pin mapping/命令/源码/Lib/model/输入 hash。不要继续采用会跨 pass 覆盖的 `{instance}_{kind}_{size}` 路径。
- 分开登记 proposal、candidate evaluation、precheck reject、STA reservation、实际 launch、结果/失败/重试、accepted commit；baseline/refresh/final STA 分账。首版不新增 cache 或重复候选跳过，避免无记录地改变旧运行器行为；如以后启用，两者另计。
- source 中 accepted 标记会因同实例后续覆盖而回改，不能当累计 commit 数。新 commit ledger 追加、不回写；可额外输出旧格式 final-applied 视图。
- 每终点从该 run 冻结初始 raw 到最终 committed raw 做独立全网 SEC，绑定完整模型和 receipt；若实际 used 三态/Z 不在证明域，保留 unsupported/non-pass。全矩阵失败照实保留，不能拼接旧成功结果或 C′。

STA cap 的旧值仍未知，且所审查 JOINT 阶段没有 singles 那样的预算检查；新适配不能私自宣称严格同预算。若选择 cap=0，应预注册为“重建选择、无限候选上限”；若要在 JOINT 预约前强制预算，须明确这是安全预算协议补全，会影响触顶路径。

## 仍需预注册的配置，不伪造历史值

| 配置项 | 当前证据 | 新同族重建最小处理 |
|---|---|---|
| mixed 七例 | launcher: rounds20、RGB+B、buf1/2、JOINT3、tns-aware、workers2 | 保留该 recipe，显式化其他字段；s382 采用相同规则须标新重建决策 |
| pureG / pureB | C trial 种类与 seed/rounds；十四对完整旧台账/终点同一，旧 launcher workers2 | only G/B、workers2 是有旧 recipe 支持的重建候选；tns-aware/JOINT/cap/priority 仍显式决策 |
| random1/2/3 | C 保存 random_order=true、seed1/2/3、实际 RGB、无 JOINT trial | 保持实例内 shuffle；选择 joint=0 时注明新声明参数；buf-types/workers/tns-aware/cap/priority 不冒充已恢复 |
| canonical mixed s382 | 起点 hash 可选；完整 canonical run 缺 | 冻结新起点而不替代旧 ledger/终点，不声称旧 identity 恢复 |
| runtime source / Lib | 仅语义快照与当前文件 hash | 旧 pin 继续 null；新实现整体回归后建立新 pin |

先用 mock trace 测出会推翻“同调度”的结果：首改善与全候选 best 不同、多实例单 pass 多提交、并行逆完成仍保持 tie 选择、无改善停止、seed 仅影响候选顺序、JOINT 重复 B 被合法性门拒绝、STA cap 和实际 launch 分账、SEC/receipt 篡改失败。通过后才做新 source 冻结和首反证 pilot。这里没有实施或启动这些步骤。
