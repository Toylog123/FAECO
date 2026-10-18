# C′完整矩阵：候选来源、代价与排序

全部8电路×9策略，共72个终点，来自固定3ea0f75与共同输入/库。MATRIX_AUDIT_72逐原件/配置/实际STA台账/提交链/finalSEC独立验收通过。图不是用旧C/D结果拼接；L是同一outerloop运行器的legacy候选政策。

**中文图注草稿。** 候选来源、代价与排序的配对对照。a，各策略相对同电路共同初始映射网表的WNS改善，以ps计。b，候选理想线网STA与初始基线STA的实际调用总数。c、d，分别为同电路中所标两臂的WNS改善差与调用次数差；正的改善差、负的调用差有利于减号左侧策略。全部72项通过登记两态支持域内的最终顺序等价检查。每种确定性策略运行一次，UR1–UR3为三个独立标注的排序种子，不求平均或显著性。

**English legend draft.** Paired comparisons of candidate sources, node costs and ordering. a, WNS gain relative to the shared initial mapped netlist within each circuit, in ps. b, Actual STA invocations, including candidate ideal-wire analyses and the initial baseline analysis. c,d, Within-circuit differences in WNS gain and STA count, respectively, for the labelled arms. A positive gain difference or a negative count difference favours the arm to the left of the minus sign. All 72 endpoints pass final sequential equivalence checks within the registered two-state support domain. Deterministic arms are run once; UR1–UR3 separately label three ordering seeds, without averaging or significance claims.

| ID | 受控设置 |
|---|---|
| W0/U0 | 仅割来源，分别配置代价/均匀代价 |
| W1/U1 | 割+覆盖来源、覆盖优先，分别配置代价/均匀代价 |
| C | 仅覆盖来源 |
| UR1–UR3 | W1候选政策，随机排序种子1–3 |
| L | 同一运行器的legacy候选政策，非历史C族greedy调度 |

两个加权/均匀代价对照在八电路的终点和STA消耗均相同。仅割来源未获得WNS改善；加入覆盖来源后八例均改善。W1相对L达到相同终点，分别少35–75次STA；C与W1终点也全同，其中s641的C少8次STA。随机顺序的差异逐种子保留，包括s27的UR3比W1少5次STA；不将候选来源/排序的差异归因于权重。

原始CSV保留72项，paired CSV保留8对照×8电路=64项配对差；未排除零结果、未抖动、未插值、无误差条。实际接受为WNS严格改善并满足已有TNS不退化等硬约束。图幅170×128mm、编辑PDF/SVG、600dpi PNG；实际PDF最小6.8pt，无小于5pt文字。四面板整体和逐面板视觉检查已通过。QA.json保留渲染时pending状态，VISUAL_REVIEW.json保存后置验收；18PASS/2WARN/0FAIL源预检的警告为项目170mm图幅与PNG预览用途。主稿引用与正文回填仍待其余历史同族证据补齐。


## 2026-10-18 最终布局修订 v3

v1 自动碰撞审计检出6处斜排标签边界重叠；v2先试竖排，v3将渲染前对齐门纳入生成器。v1/v2保留，数据CSV与v1逐字节相同。v3实际PDF碰撞0FAIL/0WARN，对齐门PASS，最小字形6.8pt；四panel及全图已由主线实际查看。旧v1独立数据/机制审查继续适用，v3独立视觉复查另附。

重建须向生成器传 `--alignment-auditor alignment_auditor_snapshot.py`（本目录保存准确副本），并选全新输出目录；从ZIP/7z恢复原始72completion后可按既有输入路径重建。PNG为600dpi预览；170mm项目图幅，不声明特定期刊终稿。
