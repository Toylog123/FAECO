# r24 SPEF v2：保标准单元的helper展开与两份原→flat证明（待root确认）

本设计针对OI051（与OI015关联）的真实helper→leaf注入缺口。v1失败原件、43partial告警、5次实际STA以及非准入结论保持。v2是**新派生输入族**：C′W1/s382原端点→只展开用户dff helper的flat mapped→当前f761双侧SPEF。它不恢复原raw层级支持，不过滤告警，不改生产、HEAD或旧数据。

## 已查复用入口与排除依据

- `code/src/rseco/yosys_abc.py:_normalize_to_blif` 会读入行为cell模型，执行proc/flatten/opt_clean/simplemap/clean并输出Boolean BLIF；不能保原mapped标准cell身份，不作物理测量输入转换。
- `technology_mapping.py`和`run_sequential_timing_check.py`会synth/ABC/dfflibmap，更不适用；不重综合，不借此改变候选。
- 复用Yosys0.33原生 `read_liberty -lib;read_verilog;hierarchy -check -top s382;flatten;write_verilog`，只增加evidence级编排和静态核对。无现成生产CLI提供该严格“保mapped标准cell只flatten用户helper”模式，故不用看似同名的旧normalizer硬替代。
- 复用 `code/scripts/run_r22_cut_ablation.py:final_sec` 的实际Liberty模型、两态门及whole-netlist equiv_simple/equiv_induct/equiv_status流程。其 `sec_designs`要求两侧helper集合完全相同，故SEC用flat top的副本附上原始、字节保持且**不实例化**的dff helper以满足原接口；STA用干净flat top。两文件top须逐字相同，helper只存在于SEC准备副本，不改flat top或功能。

同版本官方源码核对：`read_liberty -lib`创建blackbox；flatten跳过blackbox实现；write_verilog默认跳过blackbox定义，`-norename`保标识符，`-noexpr`避免后端额外bmux/demux映射。引用：[read_liberty源](https://raw.githubusercontent.com/YosysHQ/yosys/yosys-0.33/frontends/liberty/liberty.cc)、[flatten源](https://raw.githubusercontent.com/YosysHQ/yosys/yosys-0.33/passes/techmap/flatten.cc)、[write_verilog源](https://raw.githubusercontent.com/YosysHQ/yosys/yosys-0.33/backends/verilog/verilog_backend.cc)。执行时仍核真实binary/version和实际产物，官方源码不替代本机验证。

## 第一阶段：2次原生flatten，不运行STA

根目录D:/BaiduSyncdisk/01_Papers/03_FAECO；原始输入沿用v1登记的两份 `.../W1/s382/final_sec/{initial_raw,final_raw}.v`，字节SHA分别608cf28c…/5745c7fb…。当前TT库及f761全部源/原pair90-0SEC/已验收72矩阵继续锁；2份新`.ys`将在新 `paired_spef_flat_v2/prepared/` 中登记SHA后执行。

```text
read_liberty -lib "<fixed TT Liberty>"
read_verilog "<exact raw side>"
hierarchy -check -top s382
write_json "<side>.pre_flat.json"
flatten
write_json "<side>.post_flat.json"
write_verilog -noattr -norename -noexpr "<side>.flat.v"
```

只创建empty-blackbox的库定义，21个dfxtp leaf仍是同名type标准单元实例。禁止加载其行为模型来生成STA输入，禁止proc/opt/clean/synth/techmap/ABC/dfflibmap、禁止删net/改port方向/重接信号，禁止以更换cell或常量化绕过支持域。flatten对helper内部线生成必要alias可接受，所有原top信号都必须保留在相同连接等价类中。后端原生`clean_zerowidth`只允许在本输入确认无零宽wire时为no-op。

静态验收不是只看cell数量：

1. 原top的所有端口名称、方向、位宽及同一端口bit顺序完全保持（含CK和所有输出）；不得把inout改input。此s382本来无inout，不据此外推b18。
2. 逐原top组合cell匹配name/type/每个named pin对应原net alias等价类；不能仅比type直方图。
3. 逐21个dff实例，从原helper `.CLK(CK),.D(D),.Q(Q)` 映射到flat实际dfxtp leaf，核type、原CK/D/Q信号一一对应、无增删/改初态/复位或额外state。
4. 比较原设计与flat的全部连接端点集合（模块边界/标准cell/pin），允许的差异仅是用户helper端口替换为既定leaf端点与新增alias线；没有多驱动、漏consumer、断开输出、未知cell。
5. flat仅一个用户top，所有top实例均为固定Liberty标准cells、无残留dff/helper实例；使用现parser required-input/两态/SPEF静态生成并核明确leaf端点。
6. 保存原/flat/JSON/脚本/raw双流/每次launch与returncode、预后源/输入/库hash。静态不过立即停，不进入SEC或STA。

## 第二阶段：2份新独立whole-netlist SEC

分别证明原initial→flatinitial、原final→flatfinal，保持同一TT行为model；不是只证明原pair或两flat互相等价。复用 `final_sec`，单份180秒/整体600秒。为满足其shared-helper合同，SEC准备副本为flat top+原始同一helper（仅定义、没有实例）；逐字核flat top未变，原输入raw另作精确字节快照。所有实际使用库cell模型（包含dfxtp）必须在used-model集合，不允许因escaped leaf instance被正则漏掉而跳模型；原raw helper中的标准dfxtp命名实例提供同一model注册，仍独立检查实际used集合。

每份要求rc0、真实log Equivalence successfully proven、nonzero proven/0unproven，明确equiv top、gold/gate模型域；保存simple/induct拆分，不能根据脚本含induct就说靠10周期弱归纳。初态关系为同一物理寄存器的一一映射和共同任意二值初值，不添加reset/assume。标准cell状态/时钟/输入输出连线的静态映射与这2份证明共同提供派生对象功能保真。

原pairSEC+两个原→flat证明通过后，才可经传递性绑定flat baseline/final。这不恢复历史raw SPEF能力，也不把源变换本身称优化。新flat字节尚不存在，因此其SHA不能预填；生成后先冻结input manifest与canonicalization receipt，再供root核验后进入新STA注册。

## 有界执行与后续门

工具预计复用A8实际Yosys0.33 `2584903a060`，`/usr/bin/yosys` SHA `88c0a12bb814a1a8716b1ae10b482e35d3005ed558e1f5f626b3dc983ea3abd0`，执行前实际查询。总2次flatten（每次60秒）+2次SEC（各180秒），全阶段600秒；不运行新搜索或STA。任何源漂移/工具身份/结构/SEC失败先归因停止，原失败保留，不自动换方法重试。

两flat与证据冻结后，另行给root预注册同样10/40/160+u40同网表对照，最多16API+8annotation。先control，要求零partial/零unannotated且delta0；不得把v1未准入-1.90拿入主稿，也不得忽略leaf告警。此文档只请求批准第一、二阶段，不默认获批后续STA。
