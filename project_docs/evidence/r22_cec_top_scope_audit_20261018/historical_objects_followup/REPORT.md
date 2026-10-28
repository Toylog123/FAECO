# P08 / OI048 旧证明对象跟查（只读）

本轮未发现新增的“错选模块却 pass”具体旧实例。实读并哈希104份来源，结束时逐件重算SHA均一致。没有执行任何Yosys/ABC/STA/科学实验，没有修改code、旧证据或Git。未重审已核81份新proof，也未重审已核S局部86份。

| 实际域 | 本轮实读对象 | 顶层范围结论 |
|---|---|---|
| 20260717最小单例 | formal与ABC baseline共2对CEC/左右BLIF/metrics/config | 两份日志equivalent，四侧均单model；没有OI048的多根首模块条件 |
| 20260718最小批次（c17两例、c432/c499/c880） | formal与baseline共10对CEC、20侧BLIF、metrics/config及source附件 | 10份日志equivalent，20侧均单model；没有多根首模块条件 |
| 20260804 flow_probe baseline | 实际CEC与两侧BLIF、生成日志 | 单model c17_original，日志equivalent；formal旁边的整库对象不能混作这个baseline对象 |
| 同次flow_probe formal | 实际CEC与双侧各378 models | 两侧含整库，日志实际报缺`$mul`模型/读取失败，没有equivalent；是已记录错误，未找到假pass |
| 20260731 EPFL ctrl mapped CEC | actual cec_summary、日志、左右BLIF、mapping_report | 两侧各单model top；实际status=error/rc0，缺clkinv模型读失败；mapped BLIF SHA与原mapping_report完全一致。不是一次成功证明 |
| A复用旧B SEC：s27、s820 | 两份实际verify.ys/verify.log、gold/final源、A实际fixed final与initial、B outerloop state | 均显式rename circuit→gold/gate、equiv_make、`prep -top equiv`；实际日志分别11/0及137/0。与A初终top按非空行相同，gate与B实际state final一致，state hash匹配。未受ABC省top反例影响 |

上述13次成功CEC是13个已有proof对象，不是13个新实验或13个独立科学案例。通过结论仅针对现存对象的顶层范围。没有由方法名、API默认参数或目录名推断旧proof成功。

## 身份绑定仍有缺口

旧demo缺乏同时生成的输入/归一化BLIF SHA receipt。日志里的精确CEC路径与目前保留文件对应，本轮已登记当前SHA；这不能排除历史路径曾被覆盖。三个imported例子的旧`revised.sanitized.v`与当前case resynthesized源码文本不相同，而original附件与旧sanitized副本相同；c17旧revised BLIF名为c17_resynthesized，当前case resynthesized源码module却为c17_original。这里只登记差异，未凭差异猜测历史候选或将当前case当作当时输入。这些候选身份绑定继续unknown。

旧A复用两份脚本真实使用`equiv_status`，没有`-assert`；本轮逐读日志确认非零proven/0unproven和成功输出，没有虚构旧脚本具有新门。它们也不是当前81份新proof的一部分。模型、四态、状态初始化等其它边界没有在本轮重新验证。

## 覆盖边界与可复核文件

`LOG_PATH_DISCOVERY.txt`来自对experiments的包含ignored文件名发现，保留旧generic CEC/baseline命名日志，排除structure_resynth及20261016/20261018新族。22份日志路径中包含7份baseline生成日志，实际15份CEC已全部实读。这个文件名发现不覆盖所有其他命名脚本、版本归档或缺失对象；其余旧证据继续unknown，P08不整体关闭。

`FINAL_OBJECT_AUDIT.json`逐对象保存实际日志路径、命令左右BLIF、model顺序/引用/根、错误诊断、metrics字段和A复用绑定。`FINAL_READ_SHA_MANIFEST.json`保存104份实际实读来源路径/SHA/size。`FINAL_RECEIPT.json`记录全读前后SHA稳定和产物哈希，SHA为`29aa4f191afa2adcab13cf78ee4779f780fd81aafad9bb69ad8cd0d67f7437c7`。

第一版审计脚本把旧SEC模板写成新式hierarchy/assert的字面检查，所以A两项暂列unknown；原版`OBJECT_AUDIT.json`与脚本/日志保留。最终版根据实际`prep -top equiv`和日志证明数适配，不把模板差异当旧证明失败。一次后续查看因默认Windows文本编码读取UTF8 JSON报错，改显式UTF8后可读；来源与JSON本体未变。

最小后续动作：只追查仍有论文用途且缺精确历史候选绑定的对象，找到同时期归档/输入快照/commit与日志才做恢复；若找不到，则登记新pin下的独立完整证明。不能以这13个单根对象替代其他旧族，也不能仅由省top API风险宣称其具体proof失效。
