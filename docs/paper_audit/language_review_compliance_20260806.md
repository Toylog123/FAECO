# FAECO 论文《语言清洗对照表》

> 依据：对抗性语言与格式终审报告（语言层面 Major Revision 强制大修）。
> 交付：本对照表 + 最终 clean 版论文（LaTeX + PDF）。
> 日期：2026-08-06。改动全部保留本地未提交。

## 核验基线（全文自动扫描）

| 项目 | 结果 |
| :--- | :--- |
| 时间戳 2026-08 | 0 |
| 裸路径 experiments/ / A-only / toolchain_snapshot | 0 |
| 元叙述词（恰好/如实记录/事后补救/学长/跑/搞/弄/抓/塞/力不从心/投稿前/双轨制/卖点/验尸/诚实/透明声明/全绿/布局前/重构/两轮/晚） | 0 |
| 正文中英粘连（排除 verbatim/数学/texttt） | 0 |
| 正文可译英文术语残留 | 仅首次定义括号、代码标识符与文献标题 |
| Overfull hbox / undefined ref / undefined citation | 0 / 0 / 0（13 页编译通过） |

## 逐条修正结果

| 章节 | 报告原句/问题 | 修正后 | 核验证据 |
| :--- | :--- | :--- | :--- |
| 一、中英粘连（R1） | 英文+中文 无空格粘连（40+ 处） | 正文（排除 verbatim/数学/texttt）中英粘连扫描 = 0 | 2026-08-06 复核脚本：[A-Za-z][一-鿿] 与 [一-鿿][A-Za-z] 命中为 0；仅剩 映射$\rightarrow$STA$\rightarrow$等价验证 等箭头分隔的数学式 |
| 一、中英粘连（R1） | 中文+英文 无空格粘连（35+ 处） | 已清零 | 同上 |
| 一、中英粘连（R1） | 中文句内裸放英文命令/路径（15+ 处） | 命令/文件名/参数统一 texttt 包裹或译中 | techmap/read_blif/mapped.v/std::bad_alloc/.blif/.bench/assign cells.v/CreateProcess/PATH 均 texttt 包裹 |
| 二、可译未译术语 | gate | 门（正文统一；首次定义保留英文括号） | 正文叙述已尽译；残留英文仅首次定义括号、代码标识符与文献标题 |
| 二、可译未译术语 | net | 线网（首次标注） | 同上 |
| 二、可译未译术语 | cell | 单元 | 同上 |
| 二、可译未译术语 | patch | 补丁（首次标注 patch replacement） | 同上 |
| 二、可译未译术语 | cone | 锥（首次标注） | 同上 |
| 二、可译未译术语 | benchmark | 基准/测试电路 | 同上 |
| 二、可译未译术语 | case | 实例/用例 | 同上 |
| 二、可译未译术语 | trial | 实测轮次 | 同上 |
| 二、可译未译术语 | beam | 搜索宽度 | 同上 |
| 二、可译未译术语 | round | 轮次 | 同上 |
| 二、可译未译术语 | baseline | 基线 | 同上 |
| 二、可译未译术语 | recovery rate | 恢复率 | 同上 |
| 二、可译未译术语 | smoke | 冒烟测试 | 同上 |
| 二、可译未译术语 | early-stop | 提前停止 | 同上 |
| 二、可译未译术语 | leave-one-out | 留一法 | 同上 |
| 二、可译未译术语 | cold start / warm-start | 冷启动 / 热启动 | 同上 |
| 二、可译未译术语 | top-2 | 前二 | 同上 |
| 二、可译未译术语 | synthetic | 受控合成 | 同上 |
| 二、可译未译术语 | corner | 工艺角 | 同上 |
| 二、可译未译术语 | commit | 提交哈希 | 同上 |
| 二、可译未译术语 | SHA256 | SHA256 哈希值 | 同上 |
| 二、可译未译术语 | DFF | D 触发器（DFF） | 同上 |
| 二、可译未译术语 | PDK | 工艺设计套件（PDK） | 同上 |
| 二、可译未译术语 | LEF/DEF | 库交换格式/设计交换格式（LEF/DEF） | 同上 |
| 二、可译未译术语 | min-cut / s-t split graph | 最小割 / s-t 分裂图 | 同上 |
| 二、可译未译术语 | residual reachable-set | 残差可达集 | 同上 |
| 二、可译未译术语 | fanin cone | 扇入锥 | 同上 |
| 二、可译未译术语 | critical_path_cover | 关键路径覆盖 | 同上 |
| 二、可译未译术语 | reduction | 级数缩减/逻辑级缩减 | 同上 |
| 二、可译未译术语 | functional equivalence checker | 功能等价检查器 | 同上 |
| 二、可译未译术语 | wrapper | 封装 | 同上 |
| 二、可译未译术语 | lumped RC | 集总 RC（lumped RC） | 同上 |
| 二、可译未译术语 | subcircuit / frontier | 子电路 / 边界顶点 | 同上 |
| 二、可译未译术语 | reg-to-reg | 寄存器间 | 同上 |
| 二、可译未译术语 | SAT sweeping | SAT 扫荡 | 同上 |
| 二、可译未译术语 | symbolic sampling | 符号采样 | 同上 |
| 二、可译未译术语 | rectification point / rewiring / fixability | 修正点 / 线网重连 / 可修复性 | 同上 |
| 二、可译未译术语 | MILP | 混合整数线性规划（MILP） | 同上 |
| 二、可译未译术语 | physical synthesis | 物理综合 | 同上 |
| 二、可译未译术语 | gate-count estimate / wiring-cost ranking | 门数估算 / 布线代价排序 | 同上 |
| 二、可译未译术语 | cube enumeration | 立方体枚举 | 同上 |
| 二、可译未译术语 | k-LUT / STP | k 输入查找表（k-LUT）/ 半张量积（STP） | 同上 |
| 二、可译未译术语 | candidate refinement / technology remapping | 候选细化 / 技术重映射 | 同上 |
| 二、可译未译术语 | post-mask / spare-cell / metal-only | 掩模后（post-mask）/ 备用单元 / 仅金属（metal-only） | 同上 |
| 二、可译未译术语 | timing closure / timing ECO | 时序收敛 / 时序 ECO | 同上 |
| 二、可译未译术语 | failure-aware refinement | 失败感知细化（首次标注） | 同上 |
| 二、可译未译术语 | evaluator / actionable / greedy / Parser | 评估器 / 可操作 / 贪心 / 解析器 | 同上 |
| 二、可译未译术语 | primitives / reference BLIF / upsize | 原语 / 参考 BLIF（首次标注）/ 放大尺寸 | 同上 |
| 二、可译未译术语 | ideal-net / final WNS / period / vs / ON-OFF | 理想线网（首次标注）/ 最终 WNS / 周期 / 对、与 / 开-关 | 同上 |
| 三、元叙述污染 | 2026-08-04，两轮 / 2026-08-04 晚 / 2026-08-05（6+ 处） | 全部删除 | 扫描 2026-08 = 0 处 |
| 三、元叙述污染 | 如实记录为跨工具链差异 | 归因于工具链版本变化 | 已落地 |
| 三、元叙述污染 | 不再依赖事后补救 | 删除 | 扫描 = 0 |
| 三、元叙述污染 | 这恰好量化了静态表的价值 | 这量化了静态表的价值 | 扫描"恰好" = 0 |
| 三、元叙述污染 | 修正先前过于悲观的表述 | 确认无残留 | 扫描 = 0 |
| 三、元叙述污染 | 内部编号（X19） | 删除 | 扫描 X19 = 0 |
| 三、元叙述污染 | B 主力、0.9 时代 | 0.9 工具链下 B 曾为主要贡献者 | 扫描 = 0 |
| 四、本地路径裸露 | experiments/20260805_parasitic_{s382,b18}/，A-only | （仅组合逻辑的对照实验） | 扫描 experiments/ 与 A-only = 0 |
| 四、本地路径裸露 | experiments/20260805_tcad_sprint2_lambda_b18/... | 对同一 JOINT 修复做 SPEF 负载扫描（数据并入正文） | 扫描 = 0 |
| 四、本地路径裸露 | experiments/20260806_b19_067_repair/ | b19 0.67 网表的常规混合修复（数据并入正文） | 扫描 = 0 |
| 四、本地路径裸露 | environment/toolchain_snapshot.json | 正文改为"工具链快照逐实验归档" | 扫描 toolchain_snapshot = 0 |
| 四、本地路径裸露 | D:\foo\bar 示例 / lib/sky130_fd_sc_hd__tt_025C_1v80.lib | 保留（方法中属格式示例/库文件，texttt 包裹） | 已核验保留处均为 texttt 内 |
| 五、R1 | 英文缩写与中文之间加空格（RTL/ABC/Yosys/OpenSTA/SPEF/ideal/WNS/STA/DFF/MILP/SAT 等） | 全部加空格；RTL/综合 阶段 多余空格删除 | 扫描 RTL/综合 阶段 = 0 |
| 五、R2 | 工具/软件名前后空格（同 R1） | 已覆盖 | 同 R1 |
| 五、R3 | 口语动词：跑/抓取/塞入/弄出/搞出/看/压到/省 | 替换为 执行/提取/插入/生成/评估/降至/节省 等 | 扫描 跑/抓/塞/弄/搞/看 等 = 0 |
| 五、R4 | 术语统一：布局前、cell、net、gate、repair | 预布局（pre-layout）/ 单元 / 线网 / 门 / 修复，全文统一 | 已核验 |
| 五、R5 | logic-level reduction/post-mask/reg-to-reg/metal-only/timing closure | 逻辑级缩减/掩模后/寄存器间/仅金属/时序收敛 | 已核验 |
| 六、强制清单 | §IV-D 基于旧 0.9/0.33 工具链的机制分析 标注 | 删除/并入正文 | 扫描"基于旧 0.9/0.33" = 0；工具链版本作为事实保留在实验设置与 limitation |
| 六、强制清单 | §IV-E 五处小节标题时间戳 | 删除 | 扫描 2026-08 = 0 |
| 六、强制清单 | §IV-F/§IV-G 表格 caption 路径（experiments/...） | 删除；相关表已转图 | 扫描 experiments/ = 0 |
| 六、强制清单 | §IV-A environment/toolchain_snapshot.json | 正文改为"工具链快照逐实验归档" | 扫描 toolchain_snapshot = 0 |
| 七、格式 | 表格溢出 / 表格转图 | 本轮按适合度只转物理闭环表（fig:phys_gate），其余 6 张保留表格；Overfull hbox = 0 | latexmk 日志核验：Overfull = 0，无 undefined ref/citation，13 页 |
| 七、交付物 | 《语言清洗对照表》 | 本文件 | docs/paper_audit/language_review_compliance_20260806.md |
| 七、交付物 | 最终 clean 版论文（LaTeX + PDF） | paper/zh/manuscript/faeco_paper.tex + paper/zh/faeco_paper.pdf | 13 页，编译通过，PDF 已同步 |

## 保留说明

- 专有名词与工具名保留英文：Yosys / OpenSTA / ABC / Z3 / NetworkX / OSS-CAD / SKY130 / EPFL / PicoRV32 / ISCAS89 / ITC-99 / WSL2 / Edmonds-Karp / Bezier / Elmore / Steiner / UCB1 等。
- 已定义缩写保留：WNS / TNS / STA / SDC / SPEF / SAT / MILP / k-LUT / STP / OOD / DFF / PDK / LEF/DEF（首次均给出中文全称）。
- 领域术语按 EDA 惯例保留：hold / setup / min slack / pre-layout / post-layout / ideal 网络。
- 代码与命令保留原样并统一 texttt 包裹：命令序列、参数名、文件名、单元名（netlist_audit、boundary_penalty、mapped.v 等）。
- 文献标题按学术惯例保留英文原样。
