# S 两阶段CEC证据修复（2026-10-18）

本包按 `R22_S_SPEF_REPAIR_PLAN_20261018.md` 的第1项执行。只修改 `structure_resynthesis.py`、专用新测试，另经主线明确授权最小修复共享 `yosys_abc.py` 日志函数。没有修改模型函数、搜索算法、随机种子、候选接受预算或历史实验；没有执行真实EDA、Git或论文/图件变更。

## 真实反例与归因

`RED_V2.log` 为旧生产源下真实红灯：5 failed / 3.10s。测试走实际S状态机、实际factory/归一化/CEC接口，只把外部Yosys/ABC进程替为确定控制。pre pass/post fail后返回原有 `S_TECHMAP_MISMATCH`，但S0只剩post的 `abc_cec.log`（NOT EQUIVALENT），pre证明已覆盖；另有pre失败缺receipt、归一化失败/ABC超时缺receipt、已有阶段目录未拒绝。原件见 `RED_V2_ARTIFACTS/` 与来源清单。

第一份 `RED.log` 使用了错误factory名 `real_resynth_tools`，属于测试接线错误，未改生产；改成实际 `default_resynth_tools` 后才得到上述真实红灯。两份原日志/测试分别保留。

实现首绿后进一步反驳：`RED_V3_TIMEOUT_BYTES.log` 为1 failed / 8 passed / 0.68s。`TimeoutExpired` 的stdout/stderr可能是bytes，共享logger直接拼接str抛TypeError，把timeout降成unavailable并丢失partial日志。经主线授权，在共享logger层根治；没有复制第二套ABC调用、没有改status parser或argv。

## 实现

- S状态机将两次证明分别送 `variant/cec_pre/` 与 `variant/cec_post/`。
- 每次真实factory CEC独占创建全新阶段目录；旧目录直接抛 `FileExistsError`，不启动工具、不覆盖旧证明。
- 阶段先保存reference/candidate原字节快照、实际cells_v模型快照及来源/快照SHA，再从快照归一化；记录归一化BLIF、实际过滤模型、normalize日志、ABC日志等全部阶段文件SHA/长度。
- 成功、非等价、归一化失败、异常和超时路径均写不可覆盖的 `receipt.json`。原输入/模型来源及快照前后不稳定，或ABC调用期间归一化输入漂移，均返回unavailable，不能保留pass。
- 共享 `_write_text_log` 对bytes使用UTF-8 replacement生成可读文本，同时逐字保存 `.stdout.bin` / `.stderr.bin`。S的timeout reason使用同一解码helper避免bytes进入JSON；真实stderr字节仍由原始bin保全。
- receipt明确实际模型为既有cells_v；Liberty配置路径不冒称直接参与本次CEC。工具解析阶段若整体unavailable，仍由旧factory的run_variant提前失败，不把未发生的CEC记成一次证明。

## 验证

`GREEN_FINAL.log`：**47 passed / 1 skipped / 3.69s**；300秒超时包装，约5秒退出0。覆盖新10项控制、既有S、flow/S和yosys_abc邻接测试。新控制包含pre pass/post fail、pre失败短路、pre/post双pass候选语义保持、归一化失败、字符串/字节超时、旧目录不可覆盖、原model/reference与归一化BLIF漂移拒绝。

`SOURCE_FINAL_BEFORE.json` 与 `SOURCE_FINAL_AFTER.json` 三份被测源码/测试SHA完全一致。`GREEN_V1.log`（27pass）和`GREEN_V2.log`（46pass/1skip）保留，只把最终源码与GREEN_FINAL绑定，不将早期源码QA倒签到后续版本。最终源码原字节以 `final_*.py` 另存。

复制出的控制产物只为保存本次mock QA，不是历史运行或实际工具证明；receipt内绝对路径保持原件，归档位置映射另记录，不能将路径搬迁当作重新执行。

| 未完成 | 后续门 |
|---|---|
| 整体集成回归 | 由主线待所有并行生产改动冻结后运行；本包不宣称全库通过 |
| 独立代码/证据审查 | 主线核receipt输入/模型/归一化/日志绑定及失败路径 |
| 正式S同族科学恢复 | 新clean源码pin后先合法s27 on/off，再八电路；本包mock QA不替代真实SEC/STA或S收益结论 |
