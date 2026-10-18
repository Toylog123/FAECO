# S 历史证据独立复核（2026-10-18）

本包接续 10-16 的只读审计；原审计、历史运行、生产源码、论文和图件均未修改，没有执行 STA、ABC 或 SEC。权威重算为 `V2_REVIEW.json`、`V2_MODEL_RECHECK.json`，第一版输出保留为审计器失败归因，不合并成科学结果。

## 可以复用的证据及必须纠正的结论

- 原 126 条 S 候选、76 条记录的 mapped 层级下降、接受 0、相对记录基准 WNS 为 36 零 / 90 负的计数可复算；这些计数不能自动成为合法 ECO 的能力结论。
- 原报告把 258 份 filtered model 文件标成 defect，**此结论不成立**。原 Python AST evaluator 不能解析合法 Verilog `!`，把 `!A` 与 `~A` 的等价表达式报成语法错误。独立新解析器重算 258 文件、1032 个组合单元条目：全部二值真值表匹配，0 mismatch / 0 unknown。新解析器不调用生产或旧审计表达式解析器；Liberty 输出字段复用前审计，来源 SHA 已回验，故不是独立 Liberty 提取器。
- 新解析器先跑 12 组明确真值表正控、3 组优先级/XOR-XNOR负控，并补 `B1` 信号与 `1'b1` 常量区分。新审计第一版把 B1 名称误滤为常量，产生 314 unknown；保留原件，另存 v2 修正。它是审计实现错误，不是设计、模型或历史实验失败。
- 上述匹配只覆盖现存组合 filtered models 的二值输出函数，不能升级为完整顺序、X/Z 或整机功能证明。

## 已确认的历史对象问题

126 个 S host base 都能按文本 SHA 绑定，但只有 14 个通过全模块静态闭合；126 个 candidate 中仅 10 个通过全模块闭合，base 和 candidate 同时通过只有 6 个。required-input 检查 126/126 通过不能替代命名空间/驱动闭合。

s27 首 S 候选的具体反例：

- 初始 host 文本 SHA `3010c393…` 的记录基准为 -0.27 ns。
- 先接受 helper-B patch，文本 SHA `49b0a840…` / 原件 `on/s27/eval/iter002_cand002/004__11__B/mapped.v`；该 patch 声称 -0.17 ns，但 dff 模块消费未声明 `_03_`，top 的 `_03___buf__11__A2` 无驱动。
- 后续 S 候选 `on/s27/eval/iter009_s009/mapped.v` 的 SHA `684139d1…`、候选文本 SHA `550b021a…`，本身静态闭合通过、旧 STA 为 -0.27 ns，却相对非法 -0.17 ns base 被记为 -0.10 ns。

因此不能用这些负值证明 S 无效；也不能把该 S 的静态通过写成已证明等价或有收益。应先修正同族起点与接受链，再真实重跑。已知 helper-B 缺陷属于此前已修的模块作用域实现问题；本包没有发现它在当前生产再次出现。

八对 on/off 的终点全文 SHA 都相等；其中 s27、s382、s713、s953 的 `wns_history` 尾值仍不同。这是历史状态/指标语义不一致，不能据此判定两侧终点确切时序不同。只有 s820 的两侧终点通过本次静态闭合；静态闭合仍不等于 final SEC。

## 证据保存缺口及当前生产确切位置

`code/src/rseco/structure_resynthesis.py:734` 与 `:745` 的 pre/post CEC 都传同一 `variant_dir`；`:1087–1098` 固定写 `cec_left.blif`、`cec_right.blif`、`abc_cec.log`。因此 post 会覆盖 pre 的独立证据，不应将一份 retained post log 声称为两份独立证明。需要 `cec_pre/`、`cec_post/` 独立目录、输入/模型 SHA 与不可覆盖 receipt，并为一次 pre pass / post fail 保留两个对象。

126 条中仅 86 条可由 window ID + variant + canonical mapped hash 找到现存唯一局部对应，其余 40 条局部对象未恢复。保留的日志路径及现存 SHA 不能追认当时运行字节；新的 SEC 也不能重造被覆盖的 pre 日志。旧 `fresh_proof_plan.json` 可以复用候选地址，但其“模型缺陷”描述须按本包纠正，实际证明前重新核合法域。

## 最小恢复顺序

| 顺序 | 工作 | 验收门 |
|---|---|---|
| 1 | 修 S pre/post 证据覆盖，模型来源明确锁定；保留当前算法/随机种子/预算口径 | 反例 pre pass / post fail 两份 receipts 均可追踪；完整输入 SHA 与来源前后稳定 |
| 2 | 同一合法 s27 起点运行 S on/off pilot | 所有接受链 F1/F2 / required pins / 域检查；全 host 独立 SEC；实际 STA 和 commit 分账 |
| 3 | 按原 S 族八电路、on/off 完成重验 | 不把 C′ 关 S 的结果替代；保留无候选、零收益和不利结果；重算 126/76/0 与层级/时序关系 |
| 4 | 回填图7与中英文叙述 | CSV、正文数字、对象与 proof / timing 来源逐项对应 |

## 来源与本次运行

原 S 的 1907 个来源与前后 manifest 相同；SPEF 的 570 个来源另核。2477 个条目仅 `project_docs/LOGS.md` 上下文日志已更新，其余来源均与旧 SHA 一致。新包对实际读取源码/输入再做前后 SHA，稳定。v2 在 300 秒超时包装下运行，Python 实际约 7.17 秒，exit 0。无新 EDA，无 Git 操作。所有明确缺口仍待根任务按同族证据门闭合。

另见 SPEF 审计 `../../r22_spef_audit_20261016/review_20261018/REPORT.md`。本包的 `OPENSTA_ORDER_PROBE.json` 为无外部进程的真实生产 Tcl 生成探针；初两次脚本调用错误（keyword-only 参数、默认 WSL 绕过 resolver stub）均在启动任何外部进程前终止，第三版通过，保留三版脚本及首次生成 Tcl，不将程序性错误记为科学失败。
