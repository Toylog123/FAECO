# B17 证明恢复与新完整模型 SEC（2026-10-16）

**新证明已通过：12879 proven、0 unproven，13.375 s，`equiv_status -assert` 成功；本次 log 的 No SAT model 警告为零。** 只覆盖下述真实 phase-2 b17 accepted candidate 对其原始 raw mapped baseline。保留旧 12812/1 部分证明，不把另一个 phase-1 b17 的 12812/0 日志拿来替换，也没有重新证明其他 B23。

本任务原为只读恢复；发现具体层级/SAT 缺口后，主线明确授权一次 `common.final_sec`，内部180 s、外部240 s超时。只运行这一次新 SEC，没有重新 mapping、STA、修复搜索、生产或测试修改。

## 对象身份与接受绑定

| 对象 | 精确仓库相对路径 | 原始文件字节 SHA256 |
|---|---|---|
| 真实 raw baseline | `experiments/20260908_phase2_b17_resume/b17/mapped.v` | `1e47b8cc8c9c6394488e916ecdcbe89140a0e605e2f43700833b3dec25cbe644` |
| 实际 accepted candidate | `experiments/20260908_phase2_b17_resume/b17/eval/iter005_cand005/000__184320__G/mapped.v` | `9903fd632e3e139833b0ef5c308fd6c79f50b22fc7663ec2e46512e54100b82a` |
| 旧 SEC gold | `experiments/20260805_tcad_sprint1_itc99/b17/b17/case/original/original.v` | `0c544b388295eaf38ba7fde5c053aece9a8f2ee9575222ad8a9a14fc97771a35` |
| 旧 receipt | `experiments/20260908_phase2_b17_resume/sec/sec_result.json` | `7a91c8bbf8c83da2d563b5cca2c9fdbd6d5287310be65792a811947742e49646` |
| 旧 log | `experiments/20260908_phase2_b17_resume/sec/sec.log` | `5c590900caf54801eee9eb1173be379ccc1013c90803a0197c5b0f0972429a8b` |
| 旧 model | `data/raw/benchmarks/raw/skywater_cells_models/sky130_cells_v2.v` | `fd864f3ba0776f34a0faf475f733418ffa2b30adead703eaade390c4675fcefc` |

原 phase-2 `outerloop_result.json` 是旧 schema，**没有 `state.current_netlist_text` 或 `state.current_netlist_hash`**。本次没有虚构该字段。接受绑定由三条独立档案交叉支持：104行 ledger 中只有一行 accepted=true，iteration=5、instance=`_184320_`、G、nor4b_1→nor4b_2、patch=`patch_P2_U2983_random_cut`、WNS=-16.15；result/run.log 的成功 patch 和 WNS 相同；独立旧 SEC receipt 明确钉定该候选与 gold/model 的原字节 SHA，本次均回验匹配。这个证据限于“明确归档 accepted candidate”，不等于恢复不存在的 runtime state 文本哈希。

真实 baseline 为 phase-2 的完整 `b17/mapped.v`，不是仅凭旧 SECgold 命名选择。全文比较确认：baseline→accepted candidate **只有 `_184320_` 的一个类型字符串由 nor4b_1 改为 nor4b_2**，其他文本逐字相同；`dff` helper 完全一致。旧 SECgold 与真实 baseline 只在空行分布不同；删除空行后每个非空行逐字一致，未删注释、token、声明或模块。

## 唯一未证明点与可证实原因

实际旧日志 `experiments/20260908_phase2_b17_resume/sec/sec.log:115149`：

```text
Unproven $equiv $auto$equiv_make.cc:294:find_same_wires$10593: \_177917__gold \_177917__gate
```

`_177917_` 是组合网，不是寄存器；由 `_184320_.Y` 驱动。四输入完全保持 A=P2_INSTQUEUERD_ADDR_REG_1_、B=..._0_、C=..._2_、D_N=..._3_。实际 Liberty 的 nor4b_1/_2 均为 `Y=(!A & !B & !C & D_N)`，无 three_state，input/output角色一致；旧模型的两模块亦有同一组合函数。精确模块、实际函数、所有直接消费实例/pin 在 JSON。模型实际使用的 FF 是 dff wrapper 内的 dfxtp_1，旧模型有真实 posedge CLK 状态语义；本次实际 Liberty 的 D/CLK、state/next_state 字段也保存在 JSON，生成新模型见 proof 包。

旧 sec.ys 仅 `equiv_make gold gate equiv; prep -top equiv; equiv_simple; equiv_induct; equiv_status`，**没有 flatten，也没有 status -assert**。日志104061–104062明确报告：

```text
Warning: No SAT model available for cell _184320__gate (sky130_fd_sc_hd__nor4b_2).
Warning: No SAT model available for cell _184320__gold (sky130_fd_sc_hd__nor4b_1).
```

旧 equiv_simple/induct 都对 `_177917_` failed。日志还对其他层级 SKY/dff 单元报告无 SAT model。故旧 receipt 虽写 result=pass、exit0，实际 unproven=1，sec_run.log 也写 fail；旧 note 所称“find_same_wires false-negative”不是已证明的单一根因。这里有更具体证据：未展开的 library-cell hierarchy 阻止 SAT import。新完整模型+展开流程消除了缺口，支持 proof-flow limitation 的归因；未做只改 flatten 的消融，因此不把工具内部某函数直接定罪。

## 当前支持域与新证明流程

完整 baseline 和 accepted candidate 均通过 actual Liberty required-input 校验；所有已用 SKY types 在库中可识别，无实际三态 used-type。`two_state_sec_unsupported_reason` 两侧均无拒绝原因。冻结的 `x_identity_certificate.py` 对全文解析通过，sources=[]，即没有显式 X；也未遇显式 Z/三态 primitive。证书和文本 UTF-8 hash 保存在 JSON，不能推论任意未驱动网的四态/初态行为已经另行证明。

主线授权执行的是现有 `code/scripts/run_r22_cut_ablation.py:final_sec`。完整 raw 两侧先校验，再共享字节相同的 helper，按实际 used types 从实际 Liberty 生成完整 models；脚本使用 proc、memory、equiv_make、hierarchy、flatten、opt_clean、equiv_simple、equiv_induct -seq 10、equiv_status -assert。保留 raw 与拆分 top/helper 对象，未丢弃 helper 状态。

完整新证据目录：`project_docs/evidence/r22_b_model_audit_20261016/B17_new_model_proofs/final_sec/`，包含 initial_raw.v、final_raw.v、gold.v、gate.v、helpers.v、cells.v、sec.ys、sec.log、result.json。预生成 `model_preflight.v` 与实际 cells.v SHA 同为 `07e0d0fc964e93158b696d36fb93003899ca0316a5fc14945c59514d81b9bb65`。12879是当前展开模型的证明点数量，不与旧12813点机械合并计数。

运行实际 pin 为 `ddb4c3319d973aa522aeb652473ee97e960889f2`。整个 producer source_manifest、HEAD、所有原始来源和模型 SHA 前后均一致，逐项输出 hash 在 JSON。SHA绑定真实 raw bytes、用于证明的 UTF-8/LF文本、实际Lib、旧runtime model receipt、当前 producer、checker、helpers 和证明脚本；未倒填缺失的历史运行revision/dirty状态。

## 限制与反驳验收

当前结论是该精确二态支持域对象在上述完整网表 sequential-induction 流程中的证明通过。它不恢复旧状态字段、旧完整 CLI/tool binary hash，也不对其他 B23 自动增加认证。后续引用必须使用这份新 result/log 和原始输入哈希；输入/模型/producer 任一变化必须失效重登记，禁止静默再生或换候选。

必须保留的反驳门：改 nor4b 函数或输入绑定不能过证明；缺 actual required input、引入三态/Z、X消费者必须在相应门拒绝；修改 dff helper 必须拒绝共享或单独完整处理；“exit0但有unproven”不能算pass。本次不另跑负控 EDA，主线既有控制包的适用性应按其自身 pin 判断。

审计启动第一次在读取旧 ANSI map.ys 时 UTF-8 解码失败，尚未调用 SEC；保留失败日志。仅对该历史配方改为 CP936 严格解码并保留原字节 SHA，netlist仍严格UTF-8并显式CRLF→LF。第二次 wrapper 25s exit0，内部唯一新 SEC 13.375s。未覆盖任何旧 proof/result/model。
