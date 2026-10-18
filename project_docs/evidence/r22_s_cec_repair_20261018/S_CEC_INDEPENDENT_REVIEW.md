# S CEC 独立代码与证据审查

客户端日期：2026-10-18。结论：正式生成 S 证据前仍须补一处实际归一化输入身份门；本审查未修改生产源码，未运行真实 Yosys/ABC/STA。

审查者独立读取 structure_resynthesis.py、yosys_abc.py 修复及实际归一化调用路径，并逐 SHA 复核作者 FINAL_VERIFICATION.json 列出的全部 66 件原件。归档中的 cec_pre=pass、cec_post=fail 分处独占目录，各自 artifact SHA 均吻合；timeout 的原始 stdout/stderr bin 字节也实际核验相符。被审两份生产源码及专用测试在独立探针前后 SHA 不变。

## 必修：实际过滤模型仅记录调用后的身份

yosys_abc.py 的 _normalize_to_blif 实际让 Yosys 读取派生的 *_cells.v；S 外层对完整模型来源及 model_input 快照做前后核查，但派生模型只在 finally 的 artifacts 中记录调用后 SHA。该派生文件不在现有漂移门内。

独立最小探针复用默认 factory 和真实归一化、收据代码，仅控制 subprocess 边界。在归一化调用返回时改变 cec_left_cells.v，实际 81 字节变为 129 字节；前 SHA 为 caef908a4b36de7820a88cb1fa824795ab0242a891dd22abd039f03df3ff8c6e，后 SHA 为 b38ef96b8db09209a5d6844ed1b82de1a9bfbdeb93f06c78d20a33ab4c175285。外层结果及 receipt 仍为 pass，input_drift 为空。未改模型的对照同样 pass。由此可以确定通过收据未绑定归一化边界的实际模型字节；这不是已有模型函数错误或真实等价证明错误的证据。

建议在共享归一化 helper 内统一记录实际 Verilog/BOM 清理后输入及过滤模型的 before/after 身份、调用命令、所有返回分支，并使漂移成为非通过结果。不要在 S 内另复制一套归一化实现。

## 次要：归一化启动错误缺少命令日志

独立 FileNotFoundError 负控制正确返回 unavailable 并保留外层 receipt，但缺少 cec_left.normalize.log。该分支从共享 helper 异常跳出，未生成包含实际命令的归一化日志。它不会放行有效证明；可随上述共享异常收据处理补齐命令、错误及已有原始流。

## 已接受的范围

- pre/post 目录隔离且不可覆盖，pre 失败短路成立。
- 原 reference/candidate/model 来源及快照漂移，以及 ABC 消费 BLIF 的前后漂移，会使结果不可用。
- 模型来源记录为实际 cells_v；配置 Liberty 没有被冒称为本次直接证明输入。
- 已有 timeout bytes 同时保留可读替换文本及原始二进制流。

探针原件保存在 independent_review_20261018/，入口及逐件 SHA 见同名 JSON。此次探针 wrapper 上限 300 秒、实际 6 秒、退出 0。它只检验实现边界，不代替正式 S 同族复验，也不扩大到历史模型函数的科学结论。
