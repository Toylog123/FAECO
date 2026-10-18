# C transaction adapter 独立只读复核

结论：OI-042 原始探针在新冻结 adapter 上被拒绝；本轮范围内未发现新的可复现阻断。60 个显式冻结文件 before/after SHA 一致，HEAD 保持 `3ea0f757f5e9bab4a2df75c458b0c665eabcb258`。未修改作者文件、production、旧报告或 HEAD；未启动 EDA，也未进行真实注册。

## OI-042 精确重放

使用旧独立 probe 原字节（SHA `b370ec4557c68b5517132c4204ae8e0c92873bc5061f1b378175d8b2d8b2b374`）运行至全新 `scratch/c_transaction_probe`。新 adapter SHA `ef3d7acc2c09db2668ec15770565084029be5807900910c54358a26f6fe65911` 在候选 invocation finally 重新检查 `input_snapshot` 并抛 PinDrift，exit1；commit文件0、commit事件0、无completion/run_result。确切 receipt 为本目录 `OI042_EXACT_REPLAY.json`，原日志 `scratch/c_transaction_review/exact_probe.log`。

静态核对确认：同一 snapshot 检查也在 helper 返回后执行；TCL 全字节、read_verilog path/bytes、实际唯一 read_liberty path/common.LIB SHA 在实际域均重新核对。旧独立报告和作者旧 QA 保留，不把新修复倒填进旧 source pin。

## 注册及验收门

- `build_preview` 仍不能执行；完整48 recipe与八 retained mapped/input SHA、当前源、HEAD/clean、Lib、精确命令绑定，历史 argv/source unknown保持null。只有显式register才查询工具身份；本轮全部tool calls mock。
- register目录/manifest/registration均独占创建；validate要求固定manifest路径、plan fingerprint、registration中的manifest原字节SHA，再重建当前plan逐字比较。只改manifest空白、recipe、源、输入、库、HEAD或tool identity均被限定测试拒绝。
- anchor的准确边界是**一致性与漂移检测**，依赖本地登记收据写入可信。它是plain SHA收据，不是外部签名或对可任意重写整个输出目录的攻击者不可伪造的授权凭据；不应声称密码学认证。但它不允许不同源/配置绕过 fresh-plan 比较，本轮未发现能由此改变实际科学配置的绕过。
- execute/guarded-run把完整manifest+registration+preregistered+actual association、stage raw input绑定到内部PinGuard，局部FunctionType注入不改生产global。无mapper、无新C调度器、无自动resume。实际source/config来自冻结recipe，CLI不能追加搜索参数。
- staging失败、非零child、timeout、缺产物、manifest中途漂移均保留failure receipt并拒绝complete；timeout API提供的partial stdout/stderr保留。旧目录不再运行；verify见failure即拒绝。
- 两层artifact完整inventory/SHA、非simulated状态、actual config、retained原bytes/initial text、连续commit chain、measured trial association及candidate/base bytes、final text/hash均重核。commit候选原始字节与最后提交链须相同。
- 最终SEC重新核非空proven/零unproven/success/无NoSAT、actual initial/final raw+receipt、gold/gate/helpers split及actual Liberty生成的used model SHA；native preflight binding与实际cells一致。不是仅statuspass或exit0验收。此处是源码/模拟反例覆盖结论，不是正式SEC成功声明。
- reservation/launch/failed计数一致、commits数量、有限final WNS、科学配置与recipe核对存在；正式执行仍需外层watchdog和clean fresh HEAD。

## 独立限定 QA

`test_register_run.py` 38/38通过，17.70秒；wrapper180秒，20秒退出0。日志 `scratch/c_transaction_review/qa.log`。测试进程、工具pin、STA与SEC均为mock；没有真实登记、STA、SEC、映射或新的科学结果。先前author84组合QA仅作为来源证据阅读，本次没有将其冒作独立复跑；当前独立命令只跑38注册事务控制，另精确重放OI-042。

当前可信边界：完整真实tool/WSL正负控制与正式运行尚未发生；完整成功scientific事务未被本轮mock QA冒称为真实通过。外部收据可信写入、已知Boolean/Verilog支持域继续适用。后续仍由root在C′72验收、审查和提交后生成新的clean HEAD preview/pin，再决定正式pilot。
