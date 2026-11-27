# FAECO 第七轮专项复审逐条核对

复审以第六轮发布 `0cb19b3f0f73a97eca78d54e278531a3d5ad08e1` 为起点。用户提供的意见共 28,074 字节，SHA-256 为 `f373450f18b9effc6d4188c6c973503a9d964735e794d8f41dc1b06024bdef21`。本轮保持论文结构和冻结端点。科学证据继续以 `f0fe992b9ce44b8368b620d06b8d95a56179347c` 为主。

## 正文及图表

| 复审项 | 修订位置 | 核对口径 |
| --- | --- | --- |
| P0 图 1 共享验证流程 | 图 1、方法节 | 标明共享 RCX、全池探针无复修、微批次至多一次复修。关闭探针时直接进入微批次。同配置缓存复用限已完成验证的相同累计动作组合。 |
| P0 图 2 真实几何来源及裁切 | 图 2、图注 | 归档 DEF 提供中心线、过孔位置及保护网前后完整路径，单元 LEF 提供引脚、障碍和电源轨轮廓。五处标记中的三处落于图示局部，重叠的 met1 短路属于同一邻网。虚线表示诊断窗口。 |
| P0 两幅图按首次引用重编号 | 第 5.2、5.4 节及图 3、4 | 图 3 先报局部全块配对诊断，图 4 后报验收轨迹。新增标注或编号未改变科学数据。 |
| P1 图 3 坐标、标记与样本 | 图 3 及图注 | 横轴为提议涉及的换门或原地镜像实例数，两轴注明对数底数与刻度含义。(a) 的实空对应诊断路径，(b) 对应历史回放和自然扩展。两类提议各自独立取样。 |
| P2 图 4 可比范围 | 图 4 及图注 | ASAP7 UART 的标题限定终态观测。SKY130HD AES 历史臂的六次派发上限与起序在图注和对应配置表交代。统一纯微批次、Hybrid 和全块诊断的命名。 |
| P1 表 1 池面积上界 | 表 1、附录 G | 六个基准恢复 18 项冻结池的面积上界，明确 TT Setup WNS 和相对 Setup WNS 预算。40 ns 处理器的上界 141.3856 µm² 对应搜索协议的 18 个不同实例。 |
| P0 表 2 计时统计 | 表 2、附录表 S4 | 每个运行先计算已完成预检的单次均值和总和，再按正反序取算术平均。两边均计入后续验证触限但预检已完成的派发。原始均值舍入后，SKY130HD AES 全块为 14.39 s，ASAP7 AES 窗口为 7.02 s。 |
| P0 表 3 全块预检及复修 | 表 3 A、B | 14.21 s 的现场归因为全块预检。常规复修首轮仅放行直连网，关闭前置归因并按重布后 DRC 标记至多复修一次。 |
| P2 表 4 方法次序及突出显示 | 表 4 | 四基准统一方法阅读次序，历史配置 A、B、D 指向表 5。粗体标出每个基准的最高终态回收和时间均值。 |
| P0 表 5 起序条件 | 表 5、第 5.5 节 | A/B 同时改变起序与批宽，C/D 对照用于评估电容重排。末组在固定起序下检验批宽。历史组共同目标列的横线表示未报告。 |
| P2 表 6 分区与精度 | 表 6 | B 为预设探针时间子预算，C 为实际全池验证耗时。A、B 的 SKY130HD 面积采用相同显示精度。 |
| P1 表 7 终态时序 | 表 7、第 5.6 节、附录 D | 500 ps UART-TC 保持相对 Setup 门，三个实际终态的各角 Setup/Hold WNS 非负。独立 40 ns 三臂另执行绝对 Setup 零下限。470.5 ps 临界复验区分相对门和绝对门。正文补代表终态最小裕量，完整逐角来源保留在补件。 |
| P1 面积审计覆盖 | 第 5.4 节及附录 E | 25 条关键交付记录为 20 条 ASAP7、SKY130HD AES 9 门和 18 门终态、40 ns 固定协议三臂。按冻结网表和实际 ODB master 尺寸逐对象核对。 |
| P2 首现缩写、时间积分与结论 | 第 3 节、方法与结论 | 首次出现时给出 STA、RCX、SEC、SDC、ODB 的定义。以合格检查点中的最大累计面积回收定义 (a(t))，将零并入取最大值的集合。结论说明局部冲突见证及检查上下文条件。 |
| P1 跨栏图表与文献分页 | 中文主稿页面 | 以双栏浮动体位置和近邻引用为校对对象，逐页核对图表字号、图号与首现顺序。最终页位、字体和编译核验见本轮交付记录。 |

## 附录与固定归档互校

[补充材料 PDF](../../manuscript/FAECO_R7_补充材料.pdf)与[可编译源](../../manuscript/FAECO_R7_补充材料.tex)一并交付。PDF 共 7 页，含 13 张表。封面 A–G 内链与书签均落在对应附录起页。提取到 59 个外部链接标注、34 个不同的固定 GitHub 文件路径，全部按提交与对象名称核验为存在的 Git blob。两个被引用提交均为远端已公布 R6 标签的祖先。

| 附录 | 起页 | 随稿内容 | 对应冻结链接 |
| --- | ---: | --- | --- |
| A | 1 | 表 S1 逐层 LEF 字段、窗口检查器上下文和 EOL 见证 | [窗口规则及源码](https://github.com/Toylog123/FAECO/blob/f0fe992b9ce44b8368b620d06b8d95a56179347c/project_docs/evidence/tcad_v5_revision_20261126/WINDOW_RULE_SCOPE.md) |
| B | 2 | 表 S2–S4，37 次历史配对回放、7 nm 窗内与窗外注入及十臂端到端对照 | [回放](https://github.com/Toylog123/FAECO/blob/f0fe992b9ce44b8368b620d06b8d95a56179347c/project_docs/evidence/tcad_boxed_drc_20261126/BOXED_DRC_RECALL_AUDIT.json) · [十臂收据](https://github.com/Toylog123/FAECO/blob/f0fe992b9ce44b8368b620d06b8d95a56179347c/project_docs/evidence/tcad_boxed_drc_20261126/BOXED_DRC_VERIFIED.json) |
| C | 3 | 表 S5，六档批宽、三个冻结池规模及第 24 次截停边界 | [候选池读回](https://github.com/Toylog123/FAECO/blob/f0fe992b9ce44b8368b620d06b8d95a56179347c/project_docs/evidence/tcad_v5_revision_20261126/R5_ASAP7_UART_POOL_AUDIT.md) |
| D | 4 | 表 S6–S10，完整交付、TT 功耗、拒收原因、时序和物理核验，含 UART-TC 门配置与处理器各角读数 | [UART-TC](https://github.com/Toylog123/FAECO/blob/f0fe992b9ce44b8368b620d06b8d95a56179347c/project_docs/evidence/tcad_v4_revision_20261126/TIMING_CLOSED_DRC_SENS_VERIFIED.json) · [40 ns 时序和功耗](https://github.com/Toylog123/FAECO/blob/f0fe992b9ce44b8368b620d06b8d95a56179347c/project_docs/evidence/tcad_v5_revision_20261126/R4_STAGE5_POWER_TIMING_REPORT.md) |
| E | 6 | 四个冻结参考、25 条交付的 OpenDB 面积复核与 Liberty 解析影响 | [直接面积复核](https://github.com/Toylog123/FAECO/blob/f0fe992b9ce44b8368b620d06b8d95a56179347c/project_docs/evidence/tcad_v5_revision_20261126/R5_DIRECT_ODB_AREA_REPORT.md) |
| F | 6 | 表 S11，SEC 超时、进程隔离、资源与四工件独立读档 | [修复后验算和采样](https://github.com/Toylog123/FAECO/blob/f0fe992b9ce44b8368b620d06b8d95a56179347c/project_docs/evidence/tcad_v5_revision_20261126/V5_STAGE5_SEC_FIXED_VERIFIED.json) |
| G | 6 | 表 S12–S13，六基准配置、候选池面积上界、各臂开关和收据入口 | [再现实验入口](https://github.com/Toylog123/FAECO/blob/f0fe992b9ce44b8368b620d06b8d95a56179347c/project_docs/evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md) · [三臂搜索协议原件](https://github.com/Toylog123/FAECO/blob/f0fe992b9ce44b8368b620d06b8d95a56179347c/project_docs/evidence/tcad_v5_revision_20261126/V5_STAGE5_SEC_FIXED_COMMON.zip) |

表 S13 区分 ASAP7 AES 纯微批次的双序预检均值 7.02 s 与 Hybrid 回退阶段均值 6.67 s。Hybrid 原运行台账与发布收据的检查点逐字段一致，三条诊断文件的动作列表与原台账请求对应。第三次预检完成，后续候选验证触限。未重跑任何物理验证。[预检对照复算](R7_APPENDIX_DIAGNOSIS_AUDIT.json) · [三个诊断与原进度表](R7_APPENDIX_DIAGNOSIS_ORIGINALS.zip)

补件经 LuaLaTeX 双遍及七页渲染核验，终遍无错误、盒子溢出、欠满或未解析引用。保留既有仿宋加粗替代提示。TeX 与 PDF 的 SHA-256 分别为 `78665ab80577357ee0f4a45a838486fb90be9db1d110ab027fa7ff75abff8a7b`、`5bd142b82c92331d46b730f1705d7b1ceaec8e28aaeba2f076b33320cf758036`。稿件目录和构建目录两份 PDF 逐字节一致。

## 第七轮主稿验收

最终 LuaLaTeX 双遍构建为 11 页、4 图、7 表、1 算法及 26 条参考文献。所有页面已渲染核对。图 1–4 实际在第 3、5、7、8 页，图序与首次引用一致；命题证明及上下文叙述连续排在第 4 页。表 1–7 依次位于第 6、7、7、8、9、10、10 页。主结果数值实测字号 8.966 pt，参考文献从第 10 页开始，字号提高至约 9 pt。编译无错误、盒溢出或未解析引用，保留五条已有字体替代提示。

对照第六轮，表 4 的 18 条数值及两个数据图的逐点输入均未改变。局部诊断表的均值按原精度更新。40 ns 阶段的 11 个已接受检查点按物理收据核对；三臂均通过多角时序及规定验收。50 次活动传播未收敛的功耗数据仅在补充材料辅助报告。主稿内嵌链接打开第七轮独立补充材料，链接所指 Git 对象与随稿 PDF 逐字节一致。主稿三份和补充材料两份副本分别一致，见[工件清单](R7_RELEASE_MANIFEST.json)。未新增物理实验，正式英文稿与投稿待作者确认。
