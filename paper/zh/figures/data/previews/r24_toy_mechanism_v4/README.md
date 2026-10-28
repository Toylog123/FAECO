# 六门静态算法算例

该图是人工输入及人工报告实例序列上的静态算法演算，不是STA、SEC、计时或效果实验。原件绑定METHOD_EVIDENCE.json最终SHA b0eff5f45bf8d6ef91798e37cbbbdf5f92f9aa6ed509d4eafeaa9858471967b2；TOY_INPUT.json保留完整toy键，toy.v按原全文UTF-8/LF保存，SHA4ee5de31828ca35a4addc0b0ddeb9fa57d8eeffabf6c7a96552f37cfa5d9ee60。生成器独立按实际公式重算六个cost，按门与消费关系重算两个区域的输入、输出和内部网；全部与JSON一致。

**图注草稿。** 六门人工静态例中的区域生成与调度。a，输入锥的依赖与全1权重下的节点代价；P=(g1,g4,g6)为人工指定的报告实例序列，浅蓝标识其成员。R+、R−分别表示固定Liberty菜单中有、无R匹配。相同输入信号c同时连接g3的A、B两个引脚。b，覆盖区域Cc按P与锥门的有序交集得到{g1,g4,g6}，输入为{a,n2,n5}，输出为{n6}，内部网为{n1,n4}。c，加权s-t节点割选出Cw={g6}，输入为{n4,n5}，输出为{n6}。full政策先调度Cc再调度Cw，规范区域身份相同时合并来源；该顺序不按节点代价和升序确定。g6虽无R匹配，仍可被加权区域选中。节点代价是搜索代理，此例不表示已获得时序改善或通过独立顺序等价检查。

**假设及边界。** 六门依赖继承原示意的拓扑；具体cell、a/b/c引脚连接、P和全1权重由方法证据人工指定。固定Liberty的SHA及真实R/G/B/JOINT全文witness随TOY_INPUT保存；它们只说明动作可实例化，不能代替STA/SEC或接受判据。λc在此实现进入weighted cost，不改变cover-first，也没有统一实数融合分数。完整分裂图与公式由正文说明，本图不重复绘制全部in/out节点。

图幅170×98mm，字体链Microsoft YaHei/SimHei/Arial，PDF与SVG文字可编辑、PNG600dpi。node_costs.csv保存depth/fanin/fanout/R与未舍入cost。源码与QA快照可复现；节点SVG组ID为node-g1至node-g6，边界组为region-Cc/region-Cw。根验收待。

实际PDF最小7pt且字体嵌入，b/c对齐PASS、0WARN；碰撞0FAIL/0WARN。已查看a/b/c各面板与全图，输入箭头、c双引脚、数值和两边界均清晰。源预检19P/2W/0F，WARN为170mm项目图幅与PNG预览；SVG审计可审计、7–8pt、仅170mm宽度WARN，不声明任何期刊终稿验收。

**兼容与历史记录。** v1发现空集字形缺失及区域边框贴axes边缘，v2改为中文“无”并收进边框；v2默认Matplotlib SVG的外部DOCTYPE被安全解析器拒绝。v3去掉可选DTD声明，审计器另暴露缺少import math及不识别CSS font shorthand的实现问题。v4只补等价font-size属性（原font shorthand、文本、几何均保留），QA通过runpy注入缺失的标准库math，未改审计规则。toy.v另改为按原全文LF字节写入，防Windows换行使SHA不符。初次静态校核公式转写错误在输出前被断言拒绝，核对实际cut.py:181–214后修正；未产生错误图或EDA结果。所有旧目录保留。QA脚本的Windows默认GBK输出曾阻断含Unicode的审计报告，显式UTF-8后通过。MERG字体非必需表提示不影响实际字形/嵌入核查。
