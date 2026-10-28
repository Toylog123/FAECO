# r24 flat s382双侧SPEF负载敏感性结果

按root批准设计 `887ccacc4fd57a9c87009544cc3e37a0314ea052cd9944e0610d2a335e17bd19` 完成4case：先同网表u40控制，再同一新flat baseline/final的u10、u40、u160。实际16次fresh API STA+8次真实annotation replay=24次STA；包括控制6次和扫描18次，无cache复用或搜索。两次工具身份查询不计STA；v1层级注入失败的5次仍独立保留。

producer结果 `paired_spef_flat_v2_STA_runs/RESULT.json` SHA `eebc53982adeccb789022ebdc50252b65e8fa7196d1724f803afed0f172c358f`；终审 `PAIRED_SPEF_FLAT_V2_STA_POST_AUDIT.json` SHA `8d2d23e9cabf9eba07b8078dfb8aee466e4c65780607c32f56da23e8149b8827`。终审没有新EDA，实际重读16份measurement与原双流、8份replay原双流及Tcl/输入/库/模型；root已通过 `PAIRED_SPEF_FLAT_V2_STA_ROOT_ACCEPTANCE.json`（SHA `43ccd357209d5890fb0a2e700b04260778bc3036b362185660361d1ed2636489`）限定准入，范围仅此flat pair的简化线载后验。

| unit长度（μm） | 新测ideal baseline/final WNS（ns） | ideal Δ（ns） | SPEF baseline WNS（ns） | SPEF final WNS（ns） | SPEF Δ（ns） |
|---:|---|---:|---:|---:|---:|
| 10 | −0.98 / −0.83 | +0.15 | −1.23 | −1.12 | +0.11 |
| 40 | −0.98 / −0.83 | +0.15 | −2.10 | −2.10 | 0.00 |
| 160 | −0.98 / −0.83 | +0.15 | −6.00 | −6.00 | 0.00 |

每一行ideal均来自同一API job的fresh两侧测量，没有借用历史−0.98/−0.83。数值为实际OpenSTA日志0.01ns打印精度，Δ由对应新测两侧差直接重算。u10保留0.11ns改善，而u40/u160收益为0；这只支持该pair在明确简化线载模型下对负载敏感。

先行同网表u40控制：ideal两侧均−0.98ns、SPEF两侧均−2.10ns，两个Δ都0，两个SPEF字节相同，两份真实annotation均0unannotated/0partial。之后所有6份扫描annotation也均0/0；8次replay全部rc0且各自WNS与API完全相同。所有16份API measurement valid/rc0，SPEF模式的read_spef在全部timing report前。24次真实原流无missing pin/unknown instance/native error；未过滤告警。16份API原双流按原UTF-8/errors=replace/通用换行拼接，逐字复现原runner的sta.log；argv、600s内层timeout、returncode与原measurement_receipt一致。

设定固定：当前f761、SKY130 HD TT025C1v80、CK周期0.5ns、未显式设置I/O delay；两侧同RC模型与约束、各自生成并绑定SPEF。L=unit×max(1,sqrt(fanout))，r=0.09Ω/μm、c=0.21fF/μm，fanout/depth penalty均1。它是无几何坐标的简化负载代理。两个flat SHA为5f44719a…/1d179ced…，其原→flat全连接/状态与各129/0SEC及原C′pair证明通过最终manifest360ab10f…绑定；不是未恢复的原raw层级注入。

执行45.575秒（取RESULT实际 `elapsed_s` 四舍五入），1900秒外wrapper实际52秒返回0；case600/global1800/annotation60上限均未触。全部生产源、Lib、实际模型metadata、两个flat、canonicalization最终68成员与HEAD在前后匹配。最后complete事件先写并关闭，之后才建立RESULT的194成员inventory，终审全部SHA/size一致，未再append。新STA所有产物在独立目录，v1失败及原失效freeze原件未覆盖。

本表不恢复旧scan/F6，不说明真实布线寄生或PPA改善，不关闭生产层级端点OI051；没有进行新候选搜索、b18三态/inout试验或额外绘图。
