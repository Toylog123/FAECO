# r24 helper-flat v2：派生输入与原→flat证明完成，STA待审

按root明确批准的 `PAIRED_SPEF_FLAT_V2_DESIGN.json`（ce042520…）仅执行2次Yosys原生helper展开和2次原→flat全网表SEC。没有启动STA或新搜索，没有修改code、HEAD或旧证据；v1的43partial失败继续保留且不准入。

冻结包：`paired_spef_flat_v2/FROZEN_DERIVED_INPUTS.json`，SHA `2a9c6ef58e9fb1588b042f7116b9f9148c1a939511014ca3292346ad8c8e87bd`。它绑定所有新脚本、JSON、flat输入、SEC准备副本、原始双流、证明产物及实际源/库/工具身份。执行器 `run_flatten_sec_v2.py` SHA `7cfc6ca139511fc7840c21cdf215aceef9e4dc3d9071c5b944e7e82ca95c0c9a`；实际26.216秒，620秒wrapper于31秒内返回0，阶段deadline600秒。

| 对象 | flat mapped SHA256 | 原→flat SEC |
|---|---|---|
| baseline | 5f44719a08f03e507cc88481b1075749238f59f22e64bdb9ea8a94817c438e43 | 129 proven/0 unproven |
| final | 1d179ced4f472f34fd4d8ba596cace0af5a65fccb4ed2b026a84d44bfb486d8a | 129 proven/0 unproven |

两侧各106个原top net名称、94个原bit的alias类均保留双射；10个top端口顺序/方向/位宽和bit连接保持。通过原/后native Yosys JSON逐全部实例核对90标准cell（69组合+21dfxtp）的type和每个pin bit连接；21个helper对应dfxtp的CLK/D/Q映射单列，并保原标准cellblackbox。flat文件仅一个s382 top，top不再实例化dff helper；文本parser独立核name/type/pin集合，required-input/两态域/SPEF静态生成通过。

两份SEC均复用原 `run_r22_cut_ablation.final_sec`。为满足其shared-helper合同的SEC副本仅追加与原raw相同的未实例化helper，flat top逐字未变；STA预备对象是纯flat top。实际used库model集合与cells.v严格相同，精确原raw bytes另有快照。真实日志两例均simple新增4、induct新增56，最终129/0；这与A8的simple后已全证情形不同，不混用两个对象的证明分解。

当前工作HEAD仍f761，派生输入来源是C′v3W1/s382原端点，物理生成器将来自当前HEAD。此包只证明mapped层级展开保连接/状态与原对象等价；不修复OI051生产层级支持，不证明新SPEF实际完整注入或任何物理收益。新STA必须另登记这些新flat SHA，先u40同网表反证和真实零partial/零unannotated报告，再按root批准的扫描预算执行。
