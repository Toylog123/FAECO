# R22 历史结果 correctness 影响审计

日期：2026-10-14。审计者仅写本证据目录，没有运行 EDA、修改论文/生产源码/原实验结果或执行 git。逐项读取旧 result/state、选中候选 provenance、mapped 源、SEC 脚本声明的 gold/gate 和实际日志；复用 r21 图源清单、STA crosswalk 与 r22 历史输入清单，未按候选目录名猜接受对象。

## 已证实结论

**新 pilot 的错误确实影响 D 和部分 C 历史终点，但不能外推为主表 B 全部失效。** B 的28个完全证明对象与实际接受 final 已重新对上；b17仍是原有1点未证明，regs无修改、SEC不适用。A 的旧8份 SEC 脚本都读原 run 的 `mapped.v`，不能直接当接受候选的证明；其中s27/s820可用B已证明的完全相同初始/最终对象恢复功能证据，其余6项暂不可识别。

| 对象 | 实查范围 | valid | invalid | unidentified |
|---|---:|---:|---:|---:|
| A 效率优先8实例 | 8 | 2 | 0 | 6 |
| B 统一主表8ISCAS+19ITC+3Pico | 30 | 28 | 0 | 2 |
| D 固定/EMA/三随机种子 | 40 | 2 | 38 | 0 |
| D 的 k=1 固定/EMA | 16 | 2 | 14 | 0 |
| C 仅s27/s382 × 混合/纯G/纯B/三随机代表 | 12 | 0 | 9 | 3 |

`invalid` 指保留的最终网表已实证违反 module范围/driver闭合，不能当合法 ECO 终点；本审计没有重新运行 SEC 来逐个证明功能不等价。`valid` 指保留对象与已有完整SEC直接绑定，或与已证对象的初始/最终top身份完全一致。`unidentified` 是证明/来源缺失或部分证明，不等于无效。旧SEC大多未捕获当时input SHA；本次文件/script/hash交叉恢复不能伪装成补造的runtime receipt。

完整逐实例判定、helper差异、target F2、选中来源与SEC hashes见 `correctness_audit.json`；原始输入文件 SHA256 见 `input_hashes.json`；可复跑的只读审计程序为 `audit.py`。共登记410个实际来源/依赖，42项r21已锁SHA匹配、22项本次读取的C输入与r22既往SHA匹配；没有来源SHA冲突。

## B：主表28个完全证明对象保持功能有效，14项声明纪律存在缺口

ISCAS89 的8个、ITC-99 的18个（不含b17）、PicoRV32的2个修改对象，SEC脚本实际gate top与 `state.current_netlist_text` 逐字一致，日志均为完整成功；gold与初始mapped top的差异仅是 `strip_to_single_module` 在header后增加空行。只删除空行后逐行完全一致；没有用逻辑归一化掩盖helper改变。最后一次commit的provenance候选文件与final state也未发现不一致。

14个ITC对象为top-first/helper-last。旧B插入把**缓冲门留在top**，但把新wire声明放进末尾dff helper：b01/b03/b04/b05/b06/b07/b08/b10/b11/b12/b14/b15/b20/b22。helper差异删除新增wire声明后完全一致，没有新增/修改helper门或接口；目标模块的buffer连接仍有实际driver。它们在当前严格声明检查下报 `undeclared-consumed`，与新pilot/族D的 `declared-undriven` 不同。绑定到实际final的已有完整SEC为功能保持提供证据，不能仅因这项声明纪律缺口就宣布这14个历史功能结果错误；也不能称其已满足新的严格F2约束。

b06已实际接受B及后续同函数R/延迟单元，最终WNS持平；其实际final和SECgate绑定，属于上述14项。PicoRV32两个对象均为单模块，新增B留在该模块，target F2通过且final SEC绑定。b17的phase-2 dedicated receipt与实际final/gold文件SHA匹配，target F2通过、helper未变，但12812点已证/1点未证仍是部分证明；不借主表旧b17的另一候选PASS代替。regs没有接受final或时序修复对象，记为unidentified/N/A，不算功能失败。

## A：接受对象可识别，旧SEC证明对象错绑

接受对象由 A′ 的显式 `pre_layout_audit_summary.json` netlist字段交叉定位。全部8个fixed对象的变更实例集合和单元类型与A accepted元数据一致，未发现helper逻辑改变；它们不是按目录名猜出来的候选。其接受类型仍为JOINT4/G3/R1，没有单独接受B。

但是 `20260814_iscas89_sec/<c>/verify.ys` 的gate均指向A run的原 `mapped.v`。7个gate与A′明确baseline top逐字相同；s713的A′文件带额外tie-cell变体，不能冒称相同hash。所有gate均未绑定A′的fixed top，旧8/8日志因此不能独立支撑接受网表8/8完全证明。

| A实例 | 本轮状态 | 依据 |
|---|---|---|
| s27 | valid | A′ fixed完整文本hash `a3d508bb…` 与B实际final相同，初始top相同；B SEC完整证明该确切对象 |
| s820 | valid | A′ fixed完整文本hash `4abfd624…` 与B实际final相同，初始top相同；B SEC完整证明该确切对象 |
| s382/s420/s641/s713/s832/s953 | unidentified | 已识别fixed counterpart，但现存A SECgate为其他对象，没有可复用的相同final完整证明 |

s713的合法tie-cell连接 `sky130_fd_sc_hd__conb_1 ... .HI(...)` 超出了本次调用的netlist parser已知输出pin集合，target F2检查返回解析不支持；这是审计工具支持缺口，不是该网表有未驱动网的证据。此处最终判定本来就因SEC错绑而unidentified。原A执行revision/候选runtime hash仍未完全冻结，typed counterpart身份和现存SEC绑定也不能补造它们。

## D：预算和反馈曲线存在已证实的合法性混杂

40个run的final直接来自各自 `state.current_netlist_text`，并检查state hash，无重放/推测。fixed与adaptive各有7/8个最终对象损坏；random_s1/s2/s3各为8/8。k=1的fixed/adaptive各7/8。除固定/EMA的s820外，所有对象的helper新增/修改B相关逻辑，或实际top出现新未驱动消费网；这是实际网表证据，并非因旧源码调用相同函数而推断。

固定/EMA的s27终点完整文本hash为 `49b0a840…`，与本轮失败pilot的非法终点相同：`_bufb__11__A2`在dff里，实际s27的 `_03___buf__11__A2` 未驱动。s820固定/EMA（含k1）未改helper、target F2通过，且与B已完全证明的相同初始/最终top对象绑定，记valid。随机s820也接受了B，不能套用固定臂的证明。

因此D的fixed/adaptive终点相同与旧统计数相同仍可描述为**该有缺陷实现的输出事实**，不能当合法候选上EMA无额外时序收益的结论；预算曲线也不能继续用这些非法候选的收益证明有效搜索效率。此前r21 STA来源/缓存计数对账没有检查module namespace，数字可复算不等于候选合法。本审计没有从计数差反推缓存，也没有重算合法全集的收益曲线。

## C：只对实际代表对象判定，不外推全部48run

复用 `r22_historical_audit_20261014/C_configuration_and_counts.json` 的显式输入/输出角色和hash：混合s27、纯Bs27/s382、random1/2/3的s27/s382，共9个 `mapped_hybrid.v` 实际存在helper逻辑改变/target未驱动新网，记invalid。pureG两实例没有上述损坏，但没有绑定其实际final的独立SEC，记unidentified。canonical hybrid/s382缺台账/最终对象绑定，不拿v3 sibling替代，记unidentified。

这些是保留输出的实证结构判定；C的完整执行revision/逐trial base/final hash缺失仍按既往审计保留。旧运行器调用 `insert_buffer` 只能提示风险，不能据此把未查的其它C实例全判无效。代表已含主表用于混合/纯B/随机比较的对象，1.07/0.54/0.40ns等全集均值不能据这12项恢复为合法ECO收益；须完整逐实例终点/SEC审计或用修复版本按原配置重跑受影响族，不能跨族用新的C′结果覆盖历史C数字。

## 恢复建议与边界

优先补A六个已识别候选的确切功能证明绑定；保留B28个已有完整功能证据及14项声明缺口，不为统一叙事推翻已证明对象。D需要修复后的同臂同输入整族复验，C需要恢复完整对象或重跑受影响矩阵；原结果保留并标注bug影响。修复后的C′用新source pin/目录独立执行，18个pilot通过才扩展；不能用其正向收益替代旧族的失效证据，也不能因本次发现先把来源/反馈机制本身判为无效。
