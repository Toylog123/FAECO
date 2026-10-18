# OI-046：b18_light 的 LOGIC0 来源与保接口恢复设计

客户端日期：2026-10-18。本轮只读分析；未改生产、输入、论文、图件或 Git，未运行 EDA，也未实现以下设计。原件路径、SHA、引用行及实际 Liberty pin 内容均见 AUDIT.json，15 份输入前后 SHA/size 完全一致。

结论：当前基准明确暴露了一个名为 LOGIC0 的外部伪输入，并将同名网列为输出；本次映射前已是 inout。两个待复验 mapped 对象中，该网都只有四个真实 Liberty input 负载，没有查到内部驱动。因此可以设计“保留原 inout 接口、外部边界驱动的被动 RC 网”这一窄域支持；目前尚未验证其 SPEF/OpenSTA 接受性，OI-046 仍开放。现有证据不能把 LOGIC0 钉成 0，也不能把接口改成 input。

## 证据链与边界

| 对象 | 实查结果 |
|---|---|
| 原始保留 bench | bench/b18.bench:6 写明 added a pseudo-input for LOGIC0；49 行 INPUT(LOGIC0)，51 行 OUTPUT(LOGIC0)。24 个门消费该网，无 LOGIC0 左值门定义。 |
| 当前完整 BLIF | b18.blif:2 同时把 LOGIC0 列为 .inputs，3 行列为 .outputs；无驱动它的 .names/.latch。根目录与 bench/ 下两份完整 BLIF SHA 相同。 |
| 预转换 Verilog | v/b18.v:215884 已声明 inout LOGIC0，赋值中只读取它，未找到 assign LOGIC0 左值。文件头注明旧 Yosys 0.9 生成。 |
| 现有转换脚本 | bench→BLIF 保留独立 INPUT/OUTPUT 列表；BLIF→Verilog 使用 read_blif/techmap/write_verilog，再添加 CK 和 dff helper。脚本没有按名字钉 0 或改写 LOGIC0 方向。 |
| 实际 map.ys / map.log | 读取历史路径 benchmarks/raw/itc99/v/b18.v，synth -top b18、dfflibmap、abc、clean、write_verilog；无 LOGIC0/setundef/hilomap 或接口改写命令。map.log 确认旧路径并标识 Yosys 0.67+146。 |
| 实际 baseline | SHA c5c89e3a218557797b9c6868a95b1ffea22f0cf324a7d188bf4d5f669bb5ed33，80 行 inout LOGIC0。 |
| 实际唯一 R 候选 | SHA 42db3970ed14ba9d99689f5489a1db4cc3074b209c5374b55749fd0a3367e10c，接口及该网连接与 baseline 完全相同。pair.diff 的变化仅是另一个实例 _649725_ 从 xor2/X 到 ha/SUM；此处不把差异检查当整机等价证明。 |
| 历史科学族 | 6 条 F6 记录对应 1 个唯一候选，CK/13.15 ns；保留 SPEF 与旧生成器 unit_len_um=1 的重建相等证据属于此前独立审计，不与 0.5 ns 主实验族混用。 |

实际 Liberty SHA 为 ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9。四个端点均经其实际 pin block 核对为 input：

| 端点 | 单元 | mapped 引用行 |
|---|---|---:|
| _649731_:A | and2_0 | 197808 |
| _649732_:A | nand2_1 | 197813 |
| _650494_:A | lpflow_isobufsrc_1 | 202152 |
| _650495_:B | nand2_1 | 202158 |

两对象均未观察到此网的内部 output/inout pin、直接 assign 驱动或 tran 类原语；这仅是该网的静态方向结论，不是整机合法性或顺序证明。

必须保留来源缺口：当前完整 BLIF SHA 为 0be72f0146d850f9795a9c34ceed37c6fb943a660abfbaf9d45af2e88948c528，与早期 acquisition manifest 的 2fe31b69… 不同，符合“原分发截断 BLIF 后经 bench 重建”的既有脚本说明，但没有找到本轮可绑定的完整转换运行收据，不能冒称字节级恢复了当时所有输入。versions/ 当前主要保留版本说明/manifest；搜索未找到另一个 b18 原输入副本。Git 中相关脚本已有框架迁移及路径修复历史，未发现 LOGIC0 特殊改写。原始 EDIF 未在检查的本地原始目录中找到；其更早的物理接地/常量意图仍 unknown。

## 最小恢复设计（待评审、未实施）

1. 仅对“声明为 top inout、内部全为已知 input 负载、无内部 output/inout/tri/switch/驱动 assign”的网，允许显式的外部边界被动网模型。依据完整连接与 alias 闭包判定，禁止按 LOGIC0 名称判定。保留 Verilog、端口方向和逻辑模型原字节。
2. 原接口在 SPEF 的 PORTS/CONN 中仍为 B；同一物理端点只出现一次 P LOGIC0 B，四个 I 端点均保留，方向均为 I。该边界端作为被动 RC 星形网络的根，连接到全部四个负载；不能为了寻找 cell driver 而丢网，不能把 B 偷换 I。四个负载均计入 RC，避免未把端口计入 pins 却套 len(pins)-1 丢一个负载。
3. “边界根”只定义该内部连线的电气激励边界，不推断其逻辑值或外部实体。0/1 仍由基准外部环境自由提供；禁止新增 assign 0、case analysis、setundef 或删除同名输出。外部驱动/负载模型假设必须在新注册中显式写明。
4. 若出现真实双向 cell pin、内部驱动与外部边界竞争、多驱动、三态或解析不全，继续返回明确 unsupported。此设计不提供任意四态/三态解析能力，也不关闭四态问题。
5. 先完成真实两对象静态端点验收；当前拒绝发生在早期 inout 门，放开该门之后是否仍有其他 unsupported 尚未知。通过静态后再以新 clean source pin 登记合法小例、真实 OpenSTA 注入完整性检查及 b18 原族比较。双方各生 SPEF、同 RC、CK/13.15 ns，保输入/库/RC/端点/SPEF/Tcl/log/hash；任何缺 pin 或工具诊断不得成为有效测量。旧 6 条重复记录不改写、不当作 6 个独立候选。

## 最先反驳的测试（尚未执行）

| 测试 | 必须得到的结果 |
|---|---|
| 任意名称的 inout + 四个 Lib input 负载 | 单一 P B、四个 I、RC 对四负载全覆盖；改名不改变结果。 |
| 真实 baseline 与唯一候选 | 保接口和字节 SHA；LOGIC0 的五端点集合完全相同，各侧 SPEF 独立生成。 |
| 无内部驱动的同名 input/output BLIF 接口 | 保留双向声明的边界身份，不制造恒 0；0/1 赋值都保留为可能输入。 |
| 加入内部输出 driver / bidirectional cell pin / tranif / tri-state | 明确 unsupported，不能借本例的纯负载资格通过。 |
| alias 将该网接到另一个 top port 或内部 driver | 保留所有物理端点并重新判角色；不得因 canonicalization 丢端点或隐藏驱动。 |
| 删除一个真实负载、重复 P、把 B 改 I 或按名字钉 0 | 静态/收据对照必须失败。 |
| 边界 fake STA 的 ideal/physical 输出故意不同，注入缺 pin | 只接受相应报告来源；缺 pin 必须非有效，不能只看浮点。 |
| 新登记真实工具最小例与 b18 双方 | 先证明工具接受 B 端点且无缺 pin/未标注网；不要求收益为正，不用收益调 RC。 |

SPEF 中 B 的实际工具解释和完整注入行为仍须在后续有源 pin 的真实控制实验中验证。本报告只给出保持实际基准接口的可检验设计，不宣称 OI-046 或旧 b18 物理结论已闭合。
