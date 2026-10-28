# v2 flat双侧SPEF扫描登记（待root批准，未启动STA）

新设计 `PAIRED_SPEF_FLAT_V2_STA_DESIGN.json` SHA `887ccacc4fd57a9c87009544cc3e37a0314ea052cd9944e0610d2a335e17bd19`，绑定已更正并逐件实核的最终manifest `360ab10f848dc2bce275dac004ef13c315b5225c0dc91a560ed2b50aae27f4ae`，同时保留原inventory失效与153B最终事件的审计。STA输出将只写独立 `paired_spef_flat_v2_STA_runs/`，不触v1或flat生成阶段日志/产物。

输入为两个新helper-expanded mapped端点：baseline SHA `5f44719a08f03e507cc88481b1075749238f59f22e64bdb9ea8a94817c438e43`，final SHA `1d179ced4f472f34fd4d8ba596cace0af5a65fccb4ed2b026a84d44bfb486d8a`。原pair90/0SEC+两原→flat各129/0及完整106net/94bit/90cell逐pin/21state/10port检查绑定派生对象；这不是生产层级支持修复，不恢复旧F6。

固定次序与预算沿原批准方向：

| 次序 | 比较 | unit μm | API STA上限 | annotation replay上限 |
|---|---|---:|---:|---:|
| 1 | 同flat baseline与自身 | 40 | 4 | 2 |
| 2 | flat baseline/final | 10 | 4 | 2 |
| 3 | flat baseline/final | 40 | 4 | 2 |
| 4 | flat baseline/final | 160 | 4 | 2 |

总上限24次真实STA过程，串行；同网表先过ideal与SPEF delta0、两侧SPEF bytes相同、两真实annotation均零partial/零unannotated，才继续三个负载点。每侧SPEF由实际对应网表独立生成与绑定，period0.5ns/CK/TT025C1v80及RC公式/penalty与原方案相同。每个job重测ideal，u10不冒充零线载。每case600秒、全局1800秒、原runner内层每测量600秒保持；annotation60秒。任何注入、日志、pin/source/model/Lib/HEAD或timeout异常即停，保留输出，不盲重试。

4个完整绝对CLI argv和8个真实replay argv已登记JSON。调用未改的 `code/scripts/run_parasitic_aware_check.py`；采集worker为另存 `paired_spef_flat_v2_api_worker.py`，SHA `3c199a5a1b71b393cb30d61de09a34f82e0463c374093d621f95c6f88d67f5a2`。相对已审v1 worker唯一适配是capture根目录取设计output_root，防止覆盖旧目录；native argv/timeout/returncode/UTF-8 errors=replace/通用换行语义不变，所有原bytes与逐launch收据保留，不能合成或过滤结果。

执行前先核OpenSTA真实3.1.0/binary SHA `96833cf69282803fc44fc8cc343bfe03ad8279bab9fb276d84a6d4532e15b468`；逐case前后重核最终manifest所有成员和新输入以及生产源/Lib/HEADpin。replay只对原寄生Tcl追加annotation报告，read_spef必须先于全部timing report；回放WNS须与API打印精度相同。任一missing pin或partial>0不采该数据，即使API rc0/valid也不能过门。

最终报告仅此flat pair在明确简化线载模型下的负载敏感性，保留零收益/退化与无注入敏感性的结果；不称真实布线、PPA或普遍收益。收尾先写最后完成/失败journal事件、关闭流，再建立最终inventory，冻结后不再append成员。当前新输出目录不存在、STA未启动，等待root核准。
