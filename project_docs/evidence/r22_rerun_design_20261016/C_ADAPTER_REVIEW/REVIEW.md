# C adapter 独立只读复核（OI-042 未闭环）

结论：冻结对象的限定 QA 38/38 通过，但新增反驳探针发现一个正式运行阻断。没有修改作者文件、production、HEAD 或注册器 WIP，没有启动 EDA。实际八个 retained inputs 的检查仅为静态 F1/F2。

## 阻断：最后一次 STA 调用内 TCL 漂移仍提交

`C_RECONSTRUCTION_ADAPTER/adapter.py:269` 的 `finally` 记录 invocation 后只在第282行核对 `mapped.v`，缺少 `sta.tcl` 与本次捕获 SHA 的结束核对。下一次 retry 会检查 TCL，但最后一次调用没有后续检查；第298行 `remember` 反而将已改 TCL 作为新 evidence 基线接受。README 声称 finally 再核验 TCL，与实现不符。

单次候选进程边界探针保持 `read_verilog` 输入正确，在捕获 snapshot 后将同一个 live TCL 写成额外 `read_liberty /wrong/library.lib`。原正常 fake process/SEC 返回值保持不变；适配器仍提交1个候选并写 `qa_complete`。归档 attempt TCL SHA 与最终 live TCL SHA 不同，完整 receipt 见 REVIEW.json。这里不把 mock 当真实 STA 错值证明；反例证明的是已承诺的输入完整性门未拒绝漂移，因此时序输入/模型可能不再对应归档快照，正式运行应被阻断。

可复现命令（输出目录必须不存在）：

```powershell
.venv/Scripts/python.exe project_docs/evidence/r22_rerun_design_20261016/C_ADAPTER_REVIEW/probe_tcl_postcall_drift.py --output-dir scratch/c_review_new_probe
```

反驳性验收：当前探针应抛 PinDrift、无 commit/complete；补同样的 baseline/refresh/final 与 timeout/exception 结束路径控制，正常未变输入及合法重试仍通过。应核对本次启动前后的相同 `expected_tcl`；不得仅在下一 retry 或回验时采纳漂移后的 SHA。由作者/root修复，本独立复核不改源码。

## 通过范围

- QA_REPORT 显式冻结清单54个路径的 before/after SHA 全一致；HEAD 保持 `3ea0f757f5e9bab4a2df75c458b0c665eabcb258`。未加载动态 source_manifest，因此没有读取 parser 正在编写的 register_run WIP。
- 38限定QA独立复跑通过，66.09s；wrapper180s结束72s/exit0。所有 STA/SEC 边界 stub；八个实际 retained C 输入静态门接受。日志 `scratch/c_adapter_review/qa.log`。
- 对照现存 `run_hybrid_repair.py`：每 pass 重新解析一次 snapshot 并取得固定 critical 顺序；每实例在当前 text 枚举并全评估，按提交顺序的严格 _accepts 取 best，立即提交，允许多 commit；R/G/B 及 JOINT 都在相应 current text 施加。共享 RNG 只 shuffle 候选，futures 按提交顺序收集；JOINT 用排序后的已接受 singles、在已提交文本再次施加。未发现把 C 换为 outerloop/C′ 的证据。
- 六臂×八电路、20 rounds/period0.5/CK、workers2、hybrid JOINT3、random JOINT0、cap0、empty priorities、wall3600 是预览的明确重建参数；原 argv/revision、部分输入 provenance 未被倒填为历史恢复值。当前保留的 pureG mapped 是新选择，非 canonical mixed 身份证明。
- 可见静态门、trial base/candidate byte SHA、提交时再检查、旧 trial 不可变清单、reservation/attempt/观测分账与失败 complete 门已覆盖。缺失启动观测不会被当成功 complete。候选预算按 actual reservation/retry 扣，preview cap0不绑定；final SEC有180秒预留。
- final SEC 当前绑定 actual initial/final raw、gold/gate/helpers split、实际 used-cell model 与预飞 SHA；非零 proven/零 unproven/success/无 NoSAT 门存在。该结论基于源码与 mock 反例，不等于真实 SEC 通过。没有对尚未运行的新 C48作科学结果声明。

## 边界

没有扩大到任意 Tcl/Verilog 或已知 compact F2 布局支持限制。没有审查未冻结的 register_run.py/test_register_run.py。当前结论只有一个新阻断 OI-042，不代表已发现其它科学正确性问题；阻断修复后仍需新来源 pin、独立回验与正式正负控制。
