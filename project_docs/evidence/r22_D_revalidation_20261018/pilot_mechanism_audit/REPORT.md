# D pilot 两例机制归因（限定 s27/s382）

反馈实际开启、实际更新，并传入候选cut生成器；没有发现本次“反馈未传参”的实现缺陷。s382的实际候选排序发生变化，但两个实例的更新后dispatch没有引入该base下的新cut，评估器前的候选去重使实际候选/STA序列保持相同。这是当前两例、当前legacy beam与去重设定的有限机制解释；不能据此宣告反馈普遍无效，也不改去重强行制造效果。完整D56及其他六电路的机制本轮未审。

| 事实 | s27 fixed/adaptive | s382 fixed/adaptive |
|---|---|---|
| baseline → final WNS (ns) | -0.27 → -0.18 | -0.98 → -0.83 |
| 新candidate STA / candidate records / cache replay | 两臂87 /155 /68 | 两臂124 /272 /148 |
| fixed feedback | false、无反馈动作、权重不变 | 同左 |
| adaptive feedback | true、ema/rho=.5/eta_add=.5/eta_c=.25/clip=true | 同左 |
| 首次反馈更新及首次生效快照 | 第3轮失败后；第4轮size=1.25、critical=1.125 | 第4轮失败后；第5轮critical=1.125 |
| 动作记录 | size与critical各18次 | critical17次 |
| 最终权重 | size=1.4999980926513672、critical=2 | size=1、critical=2 |
| 同轮实际pool/dispatch排序 | 20轮均同 | 第7–20轮不同；第5、6轮虽已有权重变化，排序仍同 |
| pool set和dispatch set | 20轮每轮均同 | 20轮每轮均同 |
| 所有重复same-base跨臂检查 | 326个轮次对，set均同 | 292个轮次对，set均同 |
| 实际RealWnsEvaluator调用 | 两臂各8次，全部仍初始权重 | 两臂各11次，全部仍初始权重 |
| 实际候选与STA序列 | candidate/base/kind/instance/patch/accept/commit/sta_executed全部同序；87份actual STA event身份/结果同序 | 相同检查全部同序；124份actual STA event身份/结果同序 |

上述326/292为静态trace交叉比较次数，不是新实验数。权重/动作完整原始值、每轮hash及每个same-base交叉对保存在actual_v2/MECHANISM_AUDIT.json。actual STA event序列比较排除report_dir与runtime，只比较seq/kind/candidate/base/WNS/TNS/error/timeout/status；未将时间或路径不同当成候选不同。

## 源码链和归因

1. `run_outerloop_real_wns.py:275`区分no_feedback和ema，:419/:436将enable_feedback及feedback_config传入multi-iteration loop；本次四份完整run_config与result均相符。两臂的resolved_args.adaptive=false是独立UCB策略层的开关，不是EMA反馈关掉。两臂proxy_ranking=false，策略R/G/B、beam8、max_instances8、joint_k2、topology开启。
2. `refinement_loop.py:320–322`先记录本轮weights，再调用evaluator(failures,weights)；:331起接受轮直接continue，不推进EMA；:391–395失败轮执行describe_actions/update_feedback，更新的是下一轮使用的weights。更新后的s27第4轮、s382第5轮快照符合这个顺序。
3. `flow.py:649–659`每轮将当前weights传入_cone_candidates；:388–395进入constrained_weighted_cut_candidates，:674截为beam8，:681–687保存实际pool/dispatch。`cut.py:361–365`将weights放入nodecost与region参数，:392–403 region_score直接使用size/critical等权重，:453按分数排序。s382实际排序变化提供了动态印证，不能把同终点解释成参数没进生成器。
4. `flow.py:708–718`在RealWnsEvaluator调用(:744–745)之前，根据当前base+cut gates/boundaries/action身份执行mark_candidate_tested；重复者添加F4/no_new_candidate后continue。`search_state.py:239–245`拒绝已试过的候选。两例在权重首次生效之后没有新的same-base dispatch身份，实际call_log也没有任何更新权重下的新调用。call_log只见初始权重源于无新调用，不能据此说接口漏传weights。
5. RealWnsEvaluator对已接收cut，按critical顺序选actionable(:2458–2466)，以策略表/独立UCB(_strategy_order :1263–1266)生成R/G/B；EMA cut权重不是这个策略层的参数。本次UCB关闭、proxy关闭(:2652–2658按job_index恢复顺序)，因而同base+同cut的策略动作本来不应仅因EMA权重值而改变。作用路径是cut改变后改变可修复gate/dispatch，而非把同一动作重复STA。

可归因层次：尚无已证实现未传递问题；已证当前两例出现“反馈更新后未出现新cut身份”的搜索状态。s27排序不变，s382只改变已有集合内部顺序；不构成普遍的权重无效定理。新颖性限制与已接受轮不推进反馈共同解释本次相同序列；仍保留原方法目标，后续完整矩阵若再有差异应逐对象实查。

## 证据与复跑

完整读取四份run_config、outerloop_result、eval_trials、completion；四completion SHA与ROOT_COMPLETION_AUDIT_07冻结集合相同。另读manifest与45份源码/脚本，全部SHA匹配注册f761ee1996a83fc4f0f3de0999b74d85a8237858；共63份读入来源前后SHA稳定。未读取正在运行的其它job结果作结论，未执行STA/CEC/仿真或生产函数。

实际执行脚本为包内`audit.py`，通过120秒timeout包装器执行，实际5秒退出0；完整命令与UTF8环境见INVOCATION.json，stdout/stderr见AUDIT_RUN_V2.log。脚本不导入生产代码。用新的不存在目录传--output-dir可重跑，禁止覆盖现有actual_v2。首版脚本audit_v1.py/actual_v1/日志保留，v2仅补明确actual STA event身份序列比较，非重跑科学实验。READ_SHA_MANIFEST.json给出每个原件SHA/size；不以当前source反推旧D运行，结论仅属于本次新pin四个实际完成对象。
