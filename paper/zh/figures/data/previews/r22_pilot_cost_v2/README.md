# 候选来源与调用代价：预试验配图

预先登记的 s27、s382 两电路，九种策略，共18个独立验收终点。全部数据保留在 CSV；完整八电路矩阵仍在运行。本图尚未插入中英文正文。

**中文图注草稿。** 候选来源与排序策略的收益和代价。a，s27；b，s382。纵轴为终点相对同一初始映射网表的 WNS 收益，横轴为理想线网候选 STA 与初始基线 STA 的实际调用次数之和。每个策略各运行一次，UR1–UR3 分别对应随机排序种子1–3。坐标完全重合的运行合列标签。所有终点均通过独立顺序等价检查。

**English legend draft.** Gain and cost of candidate-source and ordering strategies in the preregistered two-circuit pilot. a, s27. b, s382. WNS gain is measured relative to the shared initial mapped netlist within each circuit. Total STA invocations include candidate ideal-wire analyses and the initial baseline analysis. Each strategy is run once; UR1–UR3 use ordering seeds 1–3. Runs at identical coordinates share a label. All endpoints pass independent sequential equivalence checks.

| 标记 | 含义 |
|---|---|
| W0 | 加权割来源 |
| W1 | 加权割与覆盖割，覆盖割优先 |
| U0 | 均匀节点代价的割来源 |
| U1 | 均匀代价割与覆盖割，覆盖割优先 |
| C | 仅覆盖割 |
| UR1–UR3 | W1 的候选池，随机排序种子1–3 |
| L | 已登记的旧候选策略对照 |

数据来自完整后验核验的18项记录。WNS 差以十进制计算后由 ns 换算为 ps；重合坐标按全部策略名合列，未作抖动或平均。统计单位为独立运行，不绘推断性误差条。

导出为170×72 mm的可编辑 PDF/SVG、600 dpi PNG及源数据 CSV。`QA.json` 保留生成时检查，`VISUAL_REVIEW.json` 保存双面板人工复核和 PDF 字形审计：29个文本运行，最小7 pt；最终标签无碰撞。源预检的两条警告已解释：使用PNG预览而非投稿栅格，170 mm沿用现有论文双栏图幅。

原始 v1 布局迭代及其脚本快照保留；交付预览使用本 v2。
