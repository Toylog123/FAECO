# r22 集成独立反驳审查

日期：2026-10-16。审查者仅只读 `graph.py`、`cut.py`、`flow.py`、`run_outerloop_real_wns.py`、`run_r22_cut_ablation.py`，没有修改源码/正式测试，没有运行 EDA 或全套。审查者参与编写的 `real_wns.py` 不作为独立验收对象；本报告只通过真实 evaluator 的公开属性检测集成调用契约。

**最终限定结论：本审查发现的 IR-1/2/3/4 及 IR-3-split，均已在主线修复后的冻结对象上独立复跑原探针确认消失。** 初次和中间轮次的失败值、源码身份完整保留；本结论只覆盖下列进程内集成反例及拒绝控制，未代替全工程回归、真实 EDA 或独立最终 SEC。

## 版本与执行

- 可复现探针：`scratch/r22_resume_20261016/integration_review_probe.py`，60 s timeout 包装，约 5 s / exit 0；第一轮曾在零输入 source 处直接触发 KeyError，随后探针捕获异常以继续检查其它项目，未修生产代码。
- 首完整探针日志：`integration_review_probe.log`，before/after 七文件哈希相同，保留 metadata 失败的原对象。
- 第二轮日志：`integration_review_probe_final.log`，审查期间 `flow.py` SHA256 从 `8e41e149062a856c8e5679b6ca43cc9e3085e37482dd50efc8e77cdf3dc3e2e6` 变为 `2ebe04c3eb70d53090663b99b09ee2a8da5fa51607c6f53ba7a5417e8220054d`；第二轮元数据已经正确。不得把两个版本拼成一个冻结验收对象。
- 限定已有集成用例：`pytest code/tests/test_r22_scope_integration.py -q`，90 s timeout，实际 **6 passed / 2.39 s / exit 0**。执行时主线已增加第六例；没有引用旧的“五例”数量作本次结论。
- 本报告 JSON 保存首轮与第二轮完整结果、每轮源码 SHA256、探针与日志 SHA256；报告生成时再次保存当前源码哈希。全工程尚非冻结状态。

## IR-1：无输入常量源未连接 source，weighted cut 抛异常

位置：`cut.py:_build_st_capacities` 约 697 行。source 边条件只有 `any(input_signal not in output_to_gate for ...)`；无输入物理 gate 的 `any([])` 为 false。

独立构造 `tie(H, inputs=()) -> sink(Y,H)`，cone 正确保留两个物理 gate，依赖为 `tie:out -> sink:in`。随后 `solve_weighted_cut` 实际抛 **`KeyError: 'source'`**，而非生成有限割。真实 conb 为无输入源，因此这不是未知 Verilog 语法需求。需要明确无输入物理源的 source 连接与空/常量锥策略，不能仅补一个空 residual 字典消除异常后返回空割。

## IR-2：同模块 assign 别名 root 未解析，刷新可提交空 cone

位置：`graph.py:extract_fanin_cone` 的 root lookup 与 `flow.py:_refreshed_candidate_cone`（约 69 行）；初始 `run_multi_iteration_case` 同样直接传 `case.target_output`。

合法最小输入 `buf g(n,A); assign Y=n;` 中，parser 实际给出 `resolve_alias('Y') == 'n'`。以 `Y` 调用 cone/flow refresh 得到 `gates=[]`；以 `n` 控制调用得到 `gates=['g']`。说明 parser 已有别名事实，但图集成遗漏了它。

S 集成反例保留原 15 门 HOST 的函数，仅将最后 `g15` 输出改为 `alias_Y` 并新增 `assign Y=alias_Y`；另外保留一个与 top 有同名实例的合法 helper。复用现有 S 工具/时序边界 stub，真实 loop 实际 **accepted=1、current_wns=-1.2、current_cone_gates=[]、refreshed_cone_gates=[]**；helper 原字节保留。此探针证明空图被刷新路径当作成功提交，不是证明真实工具或 SEC 接受了错误功能。

需要解析别名时保持 root 对应真实输出的契约，并对不存在的 root/异常空 cone 明确拒绝或显式处理；不能把合法常量 root 一律当成错误。修复前“刷新失败不会提交”只覆盖抛异常的失败，不覆盖这种静默空图。

## IR-3：多输出物理 cell 的 cone 外消费者丢失，割边界不闭合

位置：`graph.py:extract_fanin_cone` 只保存 root fanin，`boundary_outputs=list(roots)`；`cut.py:_boundary_outputs_for_gates` 仅从 cone 内 gate 输入找消费者。

独立构造三个 gate：`add` 输出 `S,CO`，`CO -> sinkY -> Y`，`S -> sinkZ -> Z`。从 root `Y` 提取的 cone 正确保留 `add,sinkY`，但不保留 `sinkZ` 的消费事实。选择物理 cell `add` 的割实际得到 **boundary_outputs=['CO']、internal_nets=['S']**；真实 `S` 仍被 cone 外的 `sinkZ` 使用，因此不能作为内部网处理。

这是已支持的多输出物理 cell/普通 fanout 情形，不需要扩展 Verilog 语法。需要把全网外部消费者或已识别的外部边界带入 cone/子锥/割表示，使任何被选物理 cell 的对外输出都进入边界。该探针不声称已经观察到真实 S/topology 错误接受；独立最终 SEC 仍是必要门。

## IR-4：真实 evaluator metadata 属性错配，审查中已修复

首轮实际 evaluator 有 `lib`、没有 `cells`；`flow._analysis_cell_options` 原读 `cells` 导致 `{}`。独立构造 Liberty 明确给出 `CO,SUM` 的 fa 输入，flow refresh 实际失败 `cannot determine output pin`；显式传同一 Liberty 输出元数据的控制正常保留 `add`。

第二轮主线已改读 `lib`，该 probe 的 options 包含正确 `CO,SUM`，刷新得到 `add`，新增的第六个集成用例也通过。这里只确认该属性契约反例已消失，不将其扩展为整个新版本已验收。

## 通过的正向/拒绝控制

- secondary output 的 cone 内依赖、同物理节点、split 信息由限定已有集成测试确认；不能由此推出 IR-3 的 cone 外边界已正确。
- CLI 初始端点从 `single` top slice 查 D；已有同名 helper/top endpoint 反例通过，源码实读也确认该调用顺序。
- S 缺失 target module 时实际 accepted=0、current_wns=-1.5，记录 `F2_boundary_invalid`；提交前异常刷新门确实有效。
- 合法 helper 在上述 S alias 候选中原字节保留，刷新选 top 而非同名 helper 实例。
- batch `sec_designs` 实际忽略注释中的假 module，共享 helper 保持正确；改动 helper 时抛 ValueError 拒绝。没有调用 `final_sec` 工具进程，故不报告新的最终 SEC 通过。

本审查反例不决定旧历史族 C/D 的有效性，不构成新时序收益或论文科学结论恢复的证据。主线须修复后在新冻结对象上重新核查；本报告保留原反例与版本身份。

## 第二轮独立复核：原反例消失，split 存在剩余分支

主线据上述反例增加正式红测后修复 source、root alias、全网 external boundary；本审查仅重跑原 probe。`integration_review_rereview.log` 与 `integration_review_rereview2.log` 均使用 60 s timeout 包装、exit 0，七文件每次运行前后 SHA 相同。

- IR-1：零输入源得到非空 finite cut，实际选择 `sink`，不再 KeyError。
- IR-2：alias root cone 保留 `g`；同函数 15 门 S 候选被提交后 refreshed cone 保留全部 `g1..g15`，helper 字节保持。
- IR-3：原反例的 `cut(add)` 现在暴露 `S,CO`，`S` 不再列作该 cut 的 internal net；external 输出没有变为额外 timing root。
- IR-4：真实 evaluator 的 `lib` 元数据传入正确，fa 的 CO/SUM 控制正常。

新增同根探针为 `src -> add -> sinkY -> Y`，同时 `add.S -> cone 外 sinkZ -> Z`。以 max_subcone_gates=2 分锥，含 `sinkY,add` 的 part 正确带 `external_boundary_outputs=['S']`，但 `_subcone_from_gates` 的 internal 列表仍为 `['S','CO']`。`fixed_min_cut(part)` 实际返回 boundary `['Y','S']`、internal `['S','CO']`，交集为 `['S']`，违反边界/内部互斥。

此问题定位于 split 对 internal_nets 的同步，而非重新否定已修复的全锥外部边界。没有运行窗口重写或工具，不能据此声称已发生错误时序接受。后续修复后需要同一 split 反例交集归零；JSON 保留复现值与对应 SHA。

## 最终冻结对象独立复跑

主线通知 production/tests 冻结后，本审查只运行 scratch 原探针；60 s timeout 包装，`integration_review_final_frozen.log` 实际约 5 s / exit 0。七个生产文件的 run-before/run-after SHA256 完全相同，具体值保存在 JSON 的 `final_frozen_probe`。

| 原反例/控制 | 最终实际结果 |
|---|---|
| 无输入 source | 非空有限割，selected_gates=`['sink']` |
| 真实 evaluator metadata | options 含实际 CO/SUM，刷新 gates=`['add']` |
| assign alias root | flow refresh gates=`['g']` |
| cone 外 secondary consumer | add cut boundary=`['S','CO']`，internal=`[]` |
| split external/internal 一致性 | boundary/internal 交集=`[]` |
| S 同函数 alias + helper | accepted=1，刷新 cone 15 门，helper 字节保持 |
| S 缺失 top | accepted=0，WNS 保持 -1.5，记录 F2_boundary_invalid |
| batch module namespace | 相同 tops/共享 helper 正确，假 module 注释被忽略，helper 改动被拒 |

没有再运行正式测试文件以干扰主线正在执行的整体回归；上文 6 passed 仅属于较早的已有集成用例快照。最终独立复跑结果本身是本节所列 scratch 探针，不借用主线口述的整体通过数。
