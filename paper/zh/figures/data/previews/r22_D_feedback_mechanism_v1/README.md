# D反馈机制：两电路诊断预览

当前选用 **iteration02/r22_D_feedback_mechanism.pdf / .svg / .png**。图件仅涵盖已完成的D/fixed与D/adaptive、s27/s382两对、legacy/beam8设定。未回填主稿或替换旧D图/结果，未运行任何EDA。

上行显示真实逐轮生效权重，下行拆开dispatch顺序差异、集合差异、同base新dispatch身份，再单列candidate records和new candidate STA。候选记录包含缓存回放，不能当作独立测量。边界与规模等重合轨迹保留，不做纵向抖动。s382第7轮起排序变化，但不产生新的dispatch身份；两例实际候选和STA身份序列相同。不能外推反馈普遍有效/无效，其他六电路与完整56结果未在图中表示。

数据绑定实际mechanism audit及其收据/来源manifest，重验四份completion以及四组config/result/eval原件SHA；不从当前源码重新推算实验结果。INPUT_BINDINGS.json逐件列来源SHA。CSV完整保留80条arm×circuit×round权重记录、40条匹配轮诊断、2条实际评估序列汇总。中英图注另见CAPTION_ZH.md/CAPTION_EN.md。

style-only继承既有矩阵图的字体/配色/导出设置；数据结构与机制图重新实现。生成器review_r22_D_feedback_mechanism.py实际调用既有alignment auditor渲染前门。每轮均有源/字体/碰撞/对齐检查。iteration01没有自动失败，但其“Actual candidates”措辞可能混淆独立候选数，iteration02改为“Candidate records”并保留旧原件。实际最终PDF：alignment PASS/0F0W，无豁免；font min7pt/0below5；collision PASS/0F0W；source19P2W0F。两WARN为项目170mm宽度和PNG预览用途，已逐项核对。四panel、实际全PNG及PDF渲染已检查，见VISUAL_REVIEW.json。QA_RENDER保留生成时pending状态，后置视觉结果不倒写。

尺寸170×135mm、可编辑PDF/SVG、600dpi PNG。以新不存在目录传--output-dir重建，具体调用见INVOCATION.json。当前实际脚本与alignment helper原字节随iteration02保存，首次contract先于绘图，所有版本均保留。
