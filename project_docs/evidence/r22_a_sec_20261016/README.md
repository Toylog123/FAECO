# A 六例独立 SEC 恢复输入预览（2026-10-16）

当前仅完成只读来源审计、输入登记和工具测试，**未运行 EDA 或正式 SEC，六例仍为 `pending_sec`**。`input_manifest.json` 是源码尚未冻结时的对象预览：`source_tree_clean=false`；执行器会拒绝将此清单用于正式证明。它不构成新的 source pin 或科学有效性结论。

## 实际证明对象

新 gold 固定为原 A run 的 `mapped.v`；新 gate 固定为 A′ 显式 `fixed/mapped.v`。A′ 的 `baseline/mapped.v` 只作来源交叉表与 accepted 改动见证。六个 fixed 文件均可由对应 A′ baseline 仅按原始 accepted ledger 替换单元类型逐字重建；引脚、实例范围及其他字节未变。原始结果没有可恢复的最终运行时网表哈希，因此这里绑定的是当前归档 counterpart，不声称补造旧 runtime identity。

每例 gold 为 `experiments/20260805_tcad_sprint1_iscas89/<circuit>/<circuit>/mapped.v`；gate 为 `experiments/20260807_real_pr_iscas8/<circuit>/fixed/mapped.v`；见证 baseline 为同一路径的 `baseline/mapped.v`。完整相对路径、文件大小、SHA256、角色及所读来源均在 manifest 的 `files`、`cases` 中。

| circuit | 原 A gold SHA256 | accepted counterpart gate SHA256 | A′ baseline 与原 A gold 相同 |
|---|---|---|---|
| s382 | `608cf28c7da49b245ec5cb44207552cd112a638275741c3eab74c13be0a06221` | `cdbb670f39933e94d5023e0a29cfab3d1bf1dac5cedf2e50ec704ec01dc8925f` | True |
| s420 | `19e5679c4356a8aad2f956919501854a367c58620ef47c71606e0cc302fc7ed3` | `c6471a72e9ddd5b7995c5519bdeca2fa6473418ce3789d60267a77e4033bc219` | True |
| s641 | `3665ba3076114eff30e701dd57d8d0f5d296f7ebc677fbdf4fdcfbdd79f3855e` | `b3a53ed8a2a6aec8764fadfd98cc89106b13fed599539816b53af7aed86958b1` | True |
| s713 | `a17cf08d47e8d14861f69b96595e380690b471c3044002f22f9c4bb006afb6fd` | `3c982ac08503110ad5d6c64ed76197da7d4c1fc6acc0cc032a8825d6db43a695` | False |
| s832 | `5966dcf411817b457f366951b713ce4579b4bbd8fee38004d621a6eca1675d96` | `11acbbf2bf61512dc800689e15336d804472c8a009917475da2fc948b7e98a99` | True |
| s953 | `ff5f6a2fdbf03098f8b4fb33c3a6dd9c90d761ddc052b1e9ad4a6b319b83c6bf` | `84d5e6ec40ac37c27a67834f676026eb7e4ebb8d12a83707eceb212775e128c6` | True |

**s713 的两个 baseline 不相同。** 实查差异仅为 12 条 `assign <net> = 1'h1;` 被 A′ 转换为 `_tie0_` 至 `_tie11_` 的 `conb_1 .HI(<net>)`。主证明直接用原 A baseline → A′ fixed，因而必须同时证明常量单元转换和 accepted sizing 改动。不得把两个 baseline 的不同 SHA256 写成同一对象；主证明通过时不需要为了增加数量重复做 bridge。

## 旧 SEC 的错绑边界

`experiments/20260814_iscas89_sec/<circuit>/verify.ys`、`verify.log` 及其原 gold/gate 文件只作为旧来源登记。旧 gate 指向原 run 的 baseline `mapped.v`，并非 accepted fixed；旧日志中的 successful proof 不能升级为本次六例的通过证明。新脚本复用 `code/scripts/run_r22_cut_ablation.py.final_sec`，从本次注册的实际 Liberty 生成完整模型，并执行 `equiv_simple`、`equiv_induct -seq 10`、`equiv_status -assert`。

原始六份 `eval_trials.json` 均在合法 JSON 后带字面量 `\n`。登记器只明确兼容此已知后缀，并在 `json_trailers` 中逐份记录；其他尾随内容拒绝。原档案未修改。

## 源码冻结后的操作

1. 主线完成整体回归并 commit，确认 `code/` 无修改或未跟踪文件。
2. 在新的目录登记正式 manifest，不覆盖本次预览：

```powershell
& 'C:\Program Files\Git\bin\bash.exe' code/scripts/run_with_timeout.sh 120 .venv/Scripts/python.exe code/scripts/python/prove_historical_a_r22.py --dry-run --manifest project_docs/evidence/r22_a_sec_20261016_frozen/input_manifest.json
```

3. 检查正式清单 `source_tree_clean=true`、HEAD、源码与 Liberty SHA256 后，再启动独立证明：

```powershell
& 'C:\Program Files\Git\bin\bash.exe' code/scripts/run_with_timeout.sh 1500 .venv/Scripts/python.exe code/scripts/python/prove_historical_a_r22.py --manifest project_docs/evidence/r22_a_sec_20261016_frozen/input_manifest.json --output-dir project_docs/evidence/r22_a_sec_20261016_frozen/proofs
```

每例沿用底层 SEC 的 180 秒超时；每次调用前后核验 HEAD、源码集合/哈希、归档输入及 Liberty。遇到输入/源码变化、缺文件、无法唯一识别 counterpart、非 accepted 类型改动或不完整 pass receipt 时拒绝。`proofs/<circuit>/receipt.json` 保存实际 proof exit code、状态、原始 gold/gate、源码 pin、Liberty 与所有生成工件（包括 cells.v）的哈希；非 pass 立即停止后续例。已存在 manifest 或证明目录一律不覆盖。

这一步恢复功能正确性证据，不重新测量 STA、不改历史收益/计数、不把 A 与其他族合并归因。

## 本轮验证

专属测试 `code/tests/test_r22_a_sec_recovery.py`：9 passed（0.97 s），涵盖正确输入绑定、缺失/错配/重复 crosswalk、无法辨识 accepted action、源码 pin 变化、dirty registration 拒绝、输入 hash 变化及 proof 失败 receipt。红/绿/干跑日志在 `scratch/r22_resume_20261016/a_sec_recovery_*.log`。整体回归与正式 SEC 由主线在源码冻结后执行。
