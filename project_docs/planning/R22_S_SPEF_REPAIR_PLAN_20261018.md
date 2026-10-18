# S证据与SPEF连接修复计划

> 执行方式：主线统筹，按AGENTS并行分配独立文件所有权；先反例红灯，后实现和整体回归。不得在新源码未冻结时登记正式EDA。

**目标：** 修复10-18实际审查确认的证明证据覆盖、寄生连接和报告来源问题，使下一轮同族科学复验具备可核验的输入与输出。

**设计依据：** `project_docs/evidence/r22_s_model_audit_20261016/review_20261018/REPORT.md`、`project_docs/evidence/r22_spef_audit_20261016/review_20261018/REPORT.md`。旧258个filtered models并无已证明的函数缺陷，不能按误报重写模型；旧S负结果起点多处非法，需重跑而非推断算法无效。

**约束：** 本阶段不改候选搜索策略、种子、接受预算或既有实验数；保留3ea的72项C′原件。源代码改动须先阶段commit/push可回退；修复后集成回归、新clean HEAD及新注册才能执行正式EDA。全项目实际STA并发不超过两电路。

## 1. S两阶段CEC证据（独立所有权）

- [ ] 在 `code/tests/` 新增实际 `_run_one_variant` 控制：pre pass/post fail，证明两次CEC目录不同、pre证据未被覆盖，另测pre失败短路及重复输出拒绝。
- [ ] 实跑红灯，并保存源码/测试/日志SHA。
- [ ] 修改 `code/src/rseco/structure_resynthesis.py`：`cec_pre/`、`cec_post/` 独立目录；保留两侧原输入SHA、归一化BLIF、实际模型来源及日志SHA的不可覆盖收据。失败路径也留证，不能将bool pass视为完整证明。
- [ ] 既有S测试加新反例绿灯；主线独立复查接线与artifact来源。模型来源可显式锁定当前模型；没有证据支持把旧258文件描述为函数bug。

## 2. SPEF引脚与拓扑（主线关键路径）

- [ ] 写反例：Liberty真实SUM/COUT/Q_N输出；输入名恰为Y不能被当driver；端口网保留一次P和全部I连接；多输出/inline/多模块/向量/alias；未知或歧义pin必须明确拒绝。
- [ ] 实跑红灯。复用既有模块作用域与mapped实例解析器；实际库方向需完整提取而非扩大输出名白名单。
- [ ] 修改 `code/src/rseco/spef.py`：明确实际Liberty与top，逐pin保存方向，按真实driver构建连接与RC；端口/别名须保留物理端点，不能静默丢失。不支持对象返回明确unsupported，不伪造合法连接。
- [ ] 更新 `code/src/rseco/real_wns.py` 两侧调用，使用当前同一Liberty和实际top；旧无库人工构造API兼容策略必须在评审中明确，不让生产回落白名单。
- [ ] 绿灯后核实际s382/b18候选连接集；仅静态核查，暂不称物理STA或收益。

## 3. 两侧寄生与OpenSTA顺序（独立文件所有权）

- [ ] `code/tests/` 红灯控制：换pin后两侧SPEF分别对应自己的网表；含SPEF的Tcl所有timing report均在read_spef之后；ideal/physical刻意不同输出确保解析来源。
- [ ] 修改 `code/scripts/run_parasitic_aware_check.py` 两侧各生SPEF、同一RC，收据逐侧绑定网表/Lib/RC/SPEF/Tcl/日志SHA。未知top或注入缺pin失败不可记有效测量。
- [ ] 修改 `code/src/rseco/opensta.py` 将寄生注入置于所有timing报告之前；非SPEF默认Tcl顺序保持既有语义。
- [ ] 绿灯和适用邻接测试；异常工具退出/无法解析/缺pin不得仅凭一个浮点WNS成为有效结果。

## 4. 集成与后续科学门

- [ ] 当前源码全量回归，固定输入/版本/源SHA，记录超时与退出码；失败先归因。
- [ ] 独立代码/证据评审，记录未决项，commit/push固定新源码。
- [ ] 新clean pin登记D的14项pilot、B3小例、C原调度重建；S先合法s27 on/off、SPEF先合法s382双方同RC。批次共享源码冻结，避免改HEAD使注册失效。
- [ ] S/SPEF正式原族复验与计数；s382旧RC未知时采用明确的新设定，不伪称恢复当时参数。
- [ ] 结果到图4–7/表格/中英正文逐项回填，再编译并逐页视觉验收。

## 最先尝试推翻的主张

若pre pass/post fail后只剩一份CEC对象，则证据保存修复失败；若SUM没有被识别为driver或端口网的cell连接丢失，则寄生连接修复失败；若任一timing报告先于read_spef或换pin后仍复用baseline SPEF，则物理测量来源修复失败。任何一个反例失败均阻断正式EDA，不靠弱化论文措辞闭环。
