# r22 历史配置与计数恢复报告

日期：2026-10-14。范围：族 C 的 6 个实际配置臂（混合、纯 G、纯 B、随机种子 1/2/3）与 b17 的 180 s 重跑。只读档案，不运行 EDA，不改变原始实验、论文、共享记录或 git。

审计实现：`code/scripts/python/audit_historical_evidence_r22.py`，SHA256 `d4aeb8b943b96dd29a9879708039b8b816bfc5e36122984a73b40ecce1cc134e`。使用 300 s 超时包装，正式审计 51 s 完成，exit=0。输入清单 `inputs_manifest.json` SHA256 `c601089b3296c32fefe7ea1b65d85205afd54202cd6e4fface1ed48645da3f74`，登记 26240 个原始文件/历史 git blob 的存在状态、SHA、字节数及用途。

本报告对应的派生结果：

- `C_configuration_and_counts.json`，SHA256 `6f551239fcc404ef69333028a9f6e746af081eb5f03784de0014ba8f73c4b1ab`。
- `b17_report_crosswalk.json`，SHA256 `66bcb41dacb597f7636db0f59085a050c52f30d68bf3d478abffac4f080bb489`。
- 两个 JSON 都自带 `meta.input_manifest_sha256`、审计脚本 SHA 和逐项 `config_evidence`；原始文件没有被移动、补写或覆盖。

## 结论

**b17 的计数可以从报告档案恢复为 104 个候选 STA 结果，旧 JSON 缺字段不再构成该数量的不可识别条件。** 104 个 trial 与 104 个独有的候选日志/Tcl 路径一一对应，每个日志都有有限的 WNS，且与 trial 数值一致；先前 r21 仅依据 JSON 所作的“无法识别”应更新为“经报告交叉表恢复”。结合 r21 已核查的另 18 实例 2890 条新 STA 结果，当前 ITC-99 主结果可以标明 **2994 个有独有候选报告来源的 STA 结果**；3363 仍是全部候选评估记录数，不改其单位历史。

**族 C 的完整 argv/revision 无法全部恢复；这不是需要再猜一次参数的问题。** 已恢复映射输入、部分配置字段、七个混合电路的 launcher 模板、40 个对照的轮次历史和候选记录。C 没有逐 trial 的 base hash、cache/provenance 与不可覆写报告路径；保留的候选日志跨轮覆盖，无法仅由文件数证明所有历史新增执行次数。报告将已证实字段、launcher 模板、基于代码快照的推断与缺失字段分开。

## 1. 族 C 的配置恢复

| 配置臂 | 原始目录与可恢复字段 | 明确缺失或仅能推断的字段 |
|---|---|---|
| 混合 | `20260807_multiround_8c_067/run_all.bat` 保留七电路 s27/s420/s641/s713/s820/s832/s953 的命令模板：period=0.5、rounds=20、enable-buffer、buf_1/buf_2、joint-pairs=3、tns-aware、workers=2。七份结果保留基线/终点、trial_id、round；日志显示轮内逐实例多次提交。 | launcher 不是进程 argv 捕获；完整 runtime git revision 未保存；s382 不在该 launcher 且 canonical result 缺失。全局终止时间/耗时未保存。 |
| 纯 G | 八份 `20260826_ablation_pureG/<c>/hybrid_result.json`：period=0.5、rounds=20、random_order=false、seed=20260806；观察到的 trial 类型全部 G；rounds_history 完整。 | full argv、only-strategy 具体 flag、workers、tns-aware、max-candidate-sta、strategy-priorities、runtime revision 未保存。观察到只有 G 不等于可以恢复所有 CLI 缺省。 |
| 纯 B | 八份 `20260826_ablation_pureB/<c>/hybrid_result.json`：同上；观察类型全部 B；rounds_history 完整。 | 同纯 G，另 buf-types 不能由目录名称推断为已保存命令。 |
| 随机 1/2/3 | 每臂八份 `20260826_ablation_random_seedN/<c>/hybrid_result.json`：period=0.5、rounds=20、random_order=true、seed=N；观察类型 R/G/B，没有 JOINT trial；rounds_history 完整。 | full argv、workers、tns-aware、joint-pairs、max-candidate-sta、strategy-priorities、runtime revision 未保存。没有 JOINT 结果并不能单独证明某个未记录的 flag 值。 |

七电路的 launcher 模板原文：

```text
python -u scripts/run_hybrid_repair.py --circuit %%c --period 0.5 --rounds 20 --enable-buffer --buf-types buf_1,buf_2 --joint-pairs 3 --tns-aware --workers 2 --output-dir experiments\20260807_multiround_8c_067
```

launcher SHA：`12b96b9b14072a3c0fcd9206d704766c521b838a4fa104cfffc5f3fdecb5968f`。为复现可以把它作为保留的配方发布，但应称历史 launcher 模板，不能把它变成未保存的运行时 argv 证书。

### 提交、排序与停止规则

git 归档 `26058ca:scripts/run_hybrid_repair.py` 和 `cb0bc74:scripts/run_hybrid_repair.py` 的 blob 已登记 SHA；两版都是每个关键实例评估候选后贪心提交，随后进入下一个实例，某个 pass 没有改进即 break。候选 helper 直接调用 OpenSTA，不包含 `_sta_cache`。8/13 快照有 random/only-strategy/rounds_history 接口，8/4 快照尚无这些接口。

这两版是**可审查的语义快照，不是恢复出的实际执行 revision**。混合原始日志支持轮内逐实例提交；对照的 JSON schema 与较新快照相容。随机脚本是每个实例内部 shuffle，不改变关键实例遍历顺序。当前证据不能证明各臂来自相同代码 revision，也不能保证所有未记录 flags 相同。

40 个 08-26 对照均有最后一个 `rounds_history.improved=false`。观测 pass 数在 2--5 之间，所有结果都保留 rounds=20 上限；因此不能称它们全部跑满 20 轮。未保存候选 STA cap，不能根据没有触顶字段就补写“预算不绑定”。

## 2. 族 C 的计数与重复语义

| 臂 | 可用 canonical 台账数 | 全部候选评估记录 | 有限 WNS 记录 | 现存候选日志文件 | 其中有限 WNS 日志 | 重复候选描述（首条之外） |
|---|---:|---:|---:|---:|---:|---:|
| 混合 | 7/8 | 7159 | 7099 | 4876 | 4846 | 1778 |
| 纯 G | 8/8 | 3066 | 3066 | 1403 | 1403 | 1663 |
| 纯 B | 8/8 | 8782 | 8778 | 3388 | 3384 | 5394 |
| 随机 1 | 8/8 | 12222 | 12212 | 5114 | 5110 | 6615 |
| 随机 2 | 8/8 | 11797 | 11787 | 5098 | 5094 | 6206 |
| 随机 3 | 8/8 | 12859 | 12843 | 5130 | 5125 | 7221 |

“重复候选描述”按 instance/kind/to_type 相同计算。由于各次候选可能从不同、已提交的当前网表生成，没有逐 trial base hash，**这个指标不是重复网表数量，也不是缓存命中次数**。所有这些 C 旧台账均不记录 sta_provenance 与 skipped_duplicate，不能套用族 D 的筛选规则。

R/G/B helper 复用形如 `cand_hybrid/<instance>_<kind>_<target-size-or-buffer>/` 的输出目录。跨 pass 的同描述再次评估会覆盖此前 sta.log/sta.tcl/mapped.v；某些 JOINT 路径也由相同组合构成。这解释了日志文件数少于 trial 数。有限 WNS 台账数则还与全部评估记录数不同，混合七电路有 60 条非有限 WNS 记录。

因此：

- **确定恢复：** 全部评估记录数、有限结果记录数、现存候选报告数量、候选描述重复数、轮次历史。
- **代码语义推断：** 所查看的 runner 版本每个 trial 对应一次候选 OpenSTA 调用尝试，没有软件缓存；若实际执行版与该语义一致，候选调用尝试数等于全部 trial 数。
- **无法独立恢复：** 实际执行版、所有跨轮历史成功测量及失败/重试的精确次数、覆盖前的各次候选输入/报告、各臂总墙钟。没有足够事件来源，不能把全部 trial、有限结果或独有日志的任何一个值直接宣布为完整新增 STA 调用数。

### s382 的候选来源恢复

canonical `20260807_multiround_8c_067/s382/hybrid_result.json` 缺失。另存同日 `20260807_multiround_s382_067_v3/s382/hybrid_result.json`：910 条记录、904 个有限结果、基线 -0.98、终点 +0.02、改善 +1.00、最大观测 pass=5，首次严格改善在记录 3；这些值与 canonical `convergence_summary.json` 的 s382 汇总一致，映射输入哈希也与其他各臂一致。

但保存的 launcher 不含 s382，未找到将该 v3 文件明确绑定到发布汇总的来源连接。它应标为 **“强数值/输入匹配的候选来源，来源身份待证明”**，在本包单独列出，不自动借入 canonical 合计、不直接替换主表中缺失的首次改善单元格。若作者决定用它，需要以来源说明作明确归档裁定；不能仅凭终点和数量相同反向认定实际 argv/revision。

## 3. 输入哈希与公平比较可恢复项

所有可用臂的每个电路初始 `mapped.v` 字节 SHA 均一致；s382 的 v3 也与五个对照一致。因而可在补充材料证明这些留存产物的**映射起点相同**，不必只依据相同 WNS 猜测输入相同。

| 电路 | 归档 mapped.v SHA256 |
|---|---|
| s27 | `b80c931d0ca423c26c6600f2ad442b0f9f3a36f696878eafeea195cda88cadeb` |
| s382 | `608cf28c7da49b245ec5cb44207552cd112a638275741c3eab74c13be0a06221` |
| s420 | `19e5679c4356a8aad2f956919501854a367c58620ef47c71606e0cc302fc7ed3` |
| s641 | `3665ba3076114eff30e701dd57d8d0f5d296f7ebc677fbdf4fdcfbdd79f3855e` |
| s713 | `a17cf08d47e8d14861f69b96595e380690b471c3044002f22f9c4bb006afb6fd` |
| s820 | `12a3bc4d0d9bcdd9071250654a9484b80716f94e1eff454e232e2ab7e76d49e8` |
| s832 | `5966dcf411817b457f366951b713ce4579b4bbd8fee38004d621a6eca1675d96` |
| s953 | `ff5f6a2fdbf03098f8b4fb33c3a6dd9c90d761ddc052b1e9ad4a6b319b83c6bf` |

每臂的 map.ys/map.log/sta.tcl 与映射网表均登记。map.ys 的历史源路径一部分指向后来移除的 faeco-unified-loop 工作树，另一部分指向旧根目录；它们不保存原始 RTL 字节哈希。当前 `data/raw/.../<c>.v` 的哈希仅以“当前对应源文件”发布，不能冒充运行时原始 RTL 的 captured hash。相同 mapped.v 解决映射起点一致性，却不恢复工艺库原始字节、全部映射参数与 source revision。

## 4. b17 的报告级闭合

原始台账 SHA：`b5e76e129f42c07f009fc959b1a31489bb6ef65cafa7ae281004e55f92a43b7e`。初始 mapped.v SHA：`1e47b8cc8c9c6394488e916ecdcbe89140a0e605e2f43700833b3dec25cbe644`。

恢复规则是以 JSON 的 iteration 为组，按 trial 保存次序给组内序号，精确构造：

```text
eval/iter{iteration:03d}_cand{iteration:03d}/{local_index:03d}_{instance}_{kind}/sta.log
```

104/104 路径存在且无额外候选 sta.log；所有日志有 `worst slack max` 数值、与相应 JSON WNS 一致；对应 sta.tcl 指向该目录的候选 mapped.v。未发现 timeout/timed out/killed。迭代分组分别为 80、2、2、2、18；交叉表逐 trial 给出 instance/kind/to_type、WNS 双来源及两份文件 SHA。基线 STA 在根目录另存，未混进 104。

这次恢复使用实际报告文件，而非“无缓存字段，所以都是新执行”的推断。旧 JSON 没有 provenance 不等于零；也不妨碍在保留了独有候选报告的情况下恢复数量。104 可作为有独有候选报告来源的 STA 结果数，不等于包括基线/刷新/重试/SEC 的工具全部执行次数。

period、strategies R/G、joint_enumerate_depth、init_weights、hold_mode、proxy_ranking 可从 outerloop_result 恢复。run.log 保留 skip-mapping 与基线/终点；总日志只保存了部分命令。**完整 argv、实际运行 git revision、完整 timeout 参数来源仍缺失。** 可把该档案作为结果复核包发布，不能称指定 commit 可完整重跑的权威实验包。

## 5. OI-031/OI-034 的建议状态与补充材料发布

- OI-034 中 b17 旧 schema 数量未知的子问题可闭合为“报告级恢复 104”；更新 r21 的未知标记时保留历史报告与本次证据，不篡改旧判断。
- OI-031 的**档案恢复审计**可以完成：恢复到现存档案的上限，缺失 flags/argv/revision 被明确标注；**完整复现实验身份**仍是客观限制，不能写成已恢复。若需要补齐公平性与完整复现，只能在未来授权时建立新冻结族，不能反向补造历史配置。
- C 的精确新 STA 执行总数可归为“历史来源不足而不可识别”，不是无限等待项。保留每层可证实数字和覆盖原因即可完成本轮审计义务；不把新 EDA 设为这里的必要步骤。
- 补充材料发布应包含本报告、两个结果 JSON、inputs_manifest 与只读脚本；主表继续使用 C 的历史终点，附同映射起点与配置缺失表。缺失 s382 canonical ledger 和候选 v3 的证据身份分开列出。

## 审计自检记录

第一次运行因 Windows 路径分隔符与 manifest POSIX 键不一致出现 KeyError，未写派生包；只修正审计脚本的路径规范化后复跑。正式运行成功，b17 104 个日志/Tcl 的全部断言通过；40 个对照 rounds_history 的相邻计数衔接与终点记录数通过。没有读取默认 60 s b17 的 1.49 GB JSON，也没有使用新 EDA 或重写历史档案来填缺失项。
