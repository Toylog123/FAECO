# OI045：归一化实际read输入的证明绑定

本子包保留前一阶段FINAL原件，修复独立审查实际发现的filtered model身份漂移和启动失败证据缺口。只改共享 `_normalize_to_blif`、S对该helper的日志/收据接入与专用新测试；没有复制另一套归一化或ABC实现，没有改原工具flags、ABC状态解析器或正常归一化成功判据。没有真实EDA或Git。

## 红灯

`RED.log`：4失败/10通过，0.92秒；首两项直接复现实际read_verilog的filtered model或prepared Verilog变化后仍pass；第三项FileNotFound缺normalize日志；第四项原按固定receipt拒绝重用设计。主线指出共享helper的非S调用者可合法重用output路径，因此先调整第四项为“连续重用成功且两个attempt证据保全”，保留原RED，不把该需求变化伪装成生产故障。

`RED_V2.log`：按最终兼容要求仍为4失败/10通过，2.32秒。生产修改发生在该真实红灯之后。

## 最小修复

- 每次调用在 `<requested.blif>.normalize/attemptNNNNNN/` 独占分配不可覆盖目录和receipt，保留旧attempt；canonical输出路径和原调用API保持。
- 记录并逐字保存实际命令消费的prepared Verilog与filtered cells（或实际完整cells文件）的before/after字节。快照身份均从同一次read_bytes计算，不能给未消费的父model或事后artifact倒签身份。
- 实际read输入发生变化或消失，返回非零125，即便底层进程返回0也不能继续ABC。FileNotFound等启动失败返回非零127，留下normalize日志和receipt；超时仍124并保partial输出字节。正常返回码/成功口径保持。
- 同一attempt保实际命令、进程/返回状态、异常类型、输入漂移、归一化输出观察值、完整日志及原始bytes SHA。旧attempt快照不随下一次canonical文件重用而变化。
- S阶段递归收集artifact SHA，将本次归一化receipt和其快照纳入pre/post阶段收据；不再重复覆写shared helper已保存的Verilog normalize日志。

## 当前验证

`GREEN_FINAL.log`：**51 passed / 1 skipped / 4.28s**，300秒超时包装约5秒退出0；三份owned源码/测试before/after SHA完全一致。新增四项真实缺口控制和既有S/yosys_abc/flow-S邻接全部覆盖，未把mock控制写成真实CEC。

另用原独立probe逻辑重放，仅修改输出目录以保留原件（`ORIGINAL_PROBE_POST.log`）：unchanged控制仍pass；derived_model_drift现在unavailable，内层receipt明确`input_drift=[cells_model]`、底层rc0/返回rc125；normalize_launch_error仍nonpass且现在有normalize.log和FileNotFound receipt。120秒包装约5秒退出0，来源SHA稳定。原新probe全部文件另作字节归档。

| 尚待 | 门 |
|---|---|
| 主线独立复核OI045 | 原probe重放、输入/模型/receipt绑定复查 |
| 全项目集成回归v2 | 主线在冻结源码上执行；本包不预先宣称完成 |
| 正式同族S证据 | 新clean pin注册、合法起点、真实工具证明与STA分账；静态/mock通过不代替科学验收 |
