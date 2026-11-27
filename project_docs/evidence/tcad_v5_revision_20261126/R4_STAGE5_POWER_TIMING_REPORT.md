# 第四轮 40 ns 处理器功耗传播与终态时序

本核验绑定表 12 的冻结参考及 SEC 清理修复以后实际交付的单门、固定三门和 FAECO 终态。现有三臂面积、验证账本和终态首达时间沿用同次完整运行。功耗诊断是额外读取，未计入原 720 s 搜索窗口。 [表 12 生成结果](V5_STAGE5_TABLE12.json) · [原实验归档](REPRODUCIBILITY.md#sec-修复后的完整三臂验证)

## 终态三工艺角时序

从表 12 各臂最后一个接受点绑定的物理收据读取，时序单位为 ps，三元组均按 FF／TT／SS 排列。Setup 与 Hold TNS 在参考和三个候选的三个工艺角均为 0。显示值保留小数点后 6 位，离线核验脚本读取归档中的原精度。

| 版图 | Setup WNS（FF／TT／SS） | Hold WNS（FF／TT／SS） | Setup／Hold TNS（各角） |
| --- | --- | --- | --- |
| 参考 | 31551.277146／29021.325787／6842.096667 | 386.006060／596.406313／1925.435367 | 0／0 |
| 单门第 7 次 | 31551.245172／29021.110848／6842.096667 | 386.006060／596.406258／1925.454463 | 0／0 |
| 固定三门第 6 次 | 31532.277234／28984.748823／6840.483735 | 386.005894／596.406202／1926.389714 | 0／0 |
| FAECO 第 3 次 | 31551.245172／29021.110848／6842.096667 | 386.006060／596.406313／1925.458015 | 0／0 |

| 版图 | 原归档、成员及 SHA-256 |
| --- | --- |
| 参考 | [隔离重建](V5_STAGE5_ISOLATED_REBUILD_ORIGINALS.zip) · `rebuild/CONTROL.json` · `cee3a4fb2165d30d6ba37177da711e4a1e6b16a58383892870fee272a13288fc` |
| 单门 | [单门臂](V5_STAGE5_SEC_FIXED_SINGLE_BOXED.zip) · `replay/arms/single_boxed/attempt_01/single/07/initial/receipt.json` · `abe1a9d468f37a53395d2d8237660ee3e52edd9eff324e2216f8c566ea3e3c01` |
| 固定三门 | [固定三门臂](V5_STAGE5_SEC_FIXED_FIXED_BOXED.zip) · `replay/arms/fixed_boxed/attempt_01/fixed/06/initial/receipt.json` · `71ab0783cd6d64e5abe38eb163f090910274d51b00fc4096799f420b40d55be0` |
| FAECO | [FAECO 臂](V5_STAGE5_SEC_FIXED_FAECO_BOXED.zip) · `replay/arms/faeco_boxed/attempt_01/faeco/03/initial/receipt.json` · `fc0ba847814ad8860952386178b391a117af27ecaf70d2147de59c21ae59ffe9` |

## 50 轮功耗传播诊断

OpenROAD 源码为 `b511b6a2bc936844b0319efc8b4972bb4ad7d911`，实际二进制 SHA-256 为 `2d9662715130538b50e93b614c33099a5e183eef0cc31b642099daea8d203e19`。内嵌 OpenSTA `2947a0cab3c01713def012381577f1d45decb87c` 将 50 轮上限设为编译期常量，功耗报告与活动设置命令均无上限参数。保持该二进制及其 `read_db` 路径进行诊断。 [固定传播循环](https://github.com/The-OpenROAD-Project/OpenSTA/blob/2947a0cab3c01713def012381577f1d45decb87c/power/Power.cc#L1059-L1082) · [上限常量](https://github.com/The-OpenROAD-Project/OpenSTA/blob/2947a0cab3c01713def012381577f1d45decb87c/power/Power.hh#L290-L299) · [功耗命令](https://github.com/The-OpenROAD-Project/OpenSTA/blob/2947a0cab3c01713def012381577f1d45decb87c/power/Power.tcl#L30-L42)

四次诊断读取与原测量逐字节相同的 TT Liberty、SDC、ODB 和 SPEF，只加入 `sta::set_debug power_activity 1` 并重定向结果。每个对象占同一共享 EDA 锁下的 CPU 0–5、工具单线程，逐对象限 90 s，外限 390 s，实际约 10 s，退出码 0。四份九位有效数字功耗 JSON 主体均与原报告逐字节一致。功耗为工具默认输入活动，未加额外活动注解。

| 版图 | 诊断工具墙钟（s） | 总／组合／漏电功耗相对参考变化（%） | 第 50 轮更新与状态 |
| --- | ---: | --- | --- |
| 参考 | 2.119 | 0／0／0 | 2.58，`_6197_/Y`，STA-2402 |
| 单门 | 2.033 | −0.0285／−0.1440／−0.0506 | 2.58，`_6197_/Y`，STA-2402 |
| 固定三门 | 2.299 | −0.0454／−0.2262／−0.1152 | 2.58，`_6197_/Y`，STA-2402 |
| FAECO | 2.570 | −0.0247／−0.1253／−0.0356 | 2.58，`_6197_/Y`，STA-2402 |

第 50 轮的 2.58 是活动密度或占空比的最大相对变化，使用工具输出精度。源代码比较对应的 0.01 活动变化阈值，并考虑活动来源是否变化。四例终止时均仍有待传播寄存器，触发 STA-2402。此诊断量只描述内部活动更新，不能推得功耗误差的数值界。表 12 的功耗变化用于记录默认活动估计，调度比较使用交付面积、时间均值和首达时刻。 [活动变化实现](https://github.com/The-OpenROAD-Project/OpenSTA/blob/2947a0cab3c01713def012381577f1d45decb87c/power/Power.cc#L734-L787)

## 原件与复核

[诊断原件](R4_STAGE5_POWER_TRACE_ORIGINALS.zip)含四个对象各自的工具 Tcl、日志和报告，加一份运行结果与输入指纹，共 13 个成员、8840 字节，SHA-256 `8a8892c2f15692c45e9baf653ea3e2b0793b3979dbdc490330af7ff99a7c8a85`。原搜索归档保留当时的无调试报告。两类报告由离线脚本直接对照其 JSON 主体和输入绑定。

```bash
e=project_docs/evidence/tcad_v5_revision_20261126
python3 -B "$e/verify_r4_stage5_power_trace.py"
bash code/scripts/run_with_timeout.sh 390 flock -w 8 /home/toylog/faeco_v5_eda.lock \
    python3 -B "$e/replay_r4_stage5_power_trace.py" /var/tmp/faeco_r4_stage5_tt_power_fresh
```

第一条为标准库离线核验，显示源归档读取的完整时序口径和诊断结果。第二条要求冻结 EDA 环境以及表 12 中的实跑输入路径，其输出目录须为新路径。
