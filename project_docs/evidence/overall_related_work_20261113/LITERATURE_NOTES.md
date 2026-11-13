# 总体机制相近工作核验（2026-11-13）

结论：整体链条的最邻近工作是 E-Layout；调度层的直接先例是 RL-CCD。区域选择、动作交互、STA闭环、可配置权衡各自均有先例，不能把“组合搜索+WNS预算”本身写成新颖性。以下只依据作者/会议原始页面；实际阅读深度分别注明。

| 工作（作者、年份、场合） | 已核实的机制及与FAECO重合处 | 区别/未核实边界 |
|---|---|---|
| **E-Layout: Layout-Stage Logic Restructuring via RL-Optimized Equality-Saturated Graph Retrieval-Augmented Generation**；Wenji Fang, Rongjian Liang, Yi-Chen Lu, Cunxi Yu, Chen Chen, Shang Liu, Chenhui Deng, Wenkai Li, Haoxing Ren, Zhiyao Xie；ICCAD 2026 | 作者全文§4–5已读：MFFC局部等价候选由e-graph构造；RAG联合选择结构、门尺寸和位置；mini-batch跨MFFC联合采样，以INSTA增量全芯片TNS作GRPO反馈；每批保留最好解，再回商业工具合法化、buffer/sizing。MFFC SMT与全设计Formality。整体链条高度重合。 | 是post-placement、多类结构/物理动作，不只是resize；目的主要TNS，面积同时报告。所读原文未建立本项目的固定参考WNS最大损失/hold硬门或每端点新route/SPEF验收。不能因名字含layout就称post-route signoff全约束保证。 |
| **RL-CCD: Concurrent Clock and Data Optimization using Attention-Based Self-Supervised Reinforcement Learning**；Yi-Chen Lu, Wei-Ting Chan, Deyuan Guo, Sudipto Kundu, Vishal Khandelwal, Sung Kyu Lim；DAC 2023 | 作者全文图1–4/§III已读：EP-GNN编码端点扇入锥；LSTM/attention逐个选择违例端点，以锥重叠mask排除高度重叠端点；施加临时margin使选中端点优先useful-skew，随后去margin进入ICC2缓冲/尺寸/逻辑重构/合法化；整个placement结束的TNS作trajectory reward。与区域覆盖/冲突处理/选择顺序/后续物理反馈直接相近。 | RL动作是“端点优先级”，底层多动作由商业工具执行；不是自己直接枚举所有逻辑动作。中间reward为0、末端整体反馈；不能称逐动作STA闭环。总体PPA报告不等于area-first固定WNS预算。 |
| **IR-Aware ECO Timing Optimization Using Reinforcement Learning**；Wenjing Jiang, Vidya A. Chhabria, Sachin S. Sapatnekar；MLCAD 2024 | 作者全文§3–5已读：post-P&R，负slack及两跳邻域组成state；动作同时选择哪个gate和up/down size，critical-path附近mask压缩候选；R-GCN+DQN，LR更新乘子形成power/slack reward；每动作OpenSTA增量更新，OpenROAD SWIG接口执行swap。重合：区域候选→序列决策→实际STA反馈→资源/时序权衡。 | 只gate sizing（up/down），不是逻辑重写/缓冲等多动作；优化power-delay及IR诱发违例。原文已核实post-P&R/OpenSTA，但没有据此确认每次resize重路由/重新寄生提取或与本项目相同hold/SEC门。 |
| **RL-Sizer: VLSI Gate Sizing for Timing Optimization using Deep Reinforcement Learning**；Yi-Chen Lu, Siddhartha Nath, Vishal Khandelwal, Sung Kyu Lim；DAC 2021 | 作者全文§II–III/算法1–2已读：post-route，先full-chip STA找最坏路径及与其交叠的各端点最坏路径；选局部三跳图不交叠的组合实例、拓扑排序；GNN+DDPG产生尺寸动作，整轮统一STA、局部TNS变化作reward；循环直到TNS收敛。直接先例：路径驱动区域/候选、重叠控制、批量动作、实测反馈与调用成本折中。 | 仅组合门resize、无时序单元调整；局部reward是近似。整轮一次STA，非每动作STA，更非逐候选完整route；TNS目标，非固定WNS预算面积最大化。 |
| **Improving Timing & Power Trade-off in Post-place Optimization Using Multi-agent Reinforcement Learning**；Jaemin Seo, Sejin Park, Seokhyeong Kang；ICCAD 2024 | 作者实验室页与官方会议program核title/authors/year。官方会议说明为RL post-place PPA联合优化、动态选有效动作。是需要重点追读的多动作PPA近邻。 | **本轮未成功取得全文**：作者下载链接返回错误，ACM 403，IEEE验证码。不能把第三方摘要声称的buffer/sizing/Vth详细动作、STA频率、寄生更新/约束或固定评估预算当已核实。 |

## 可点击primary来源

1. E-Layout [作者原文](https://arxiv.org/html/2610.26432v1)，[摘要及作者](https://arxiv.org/abs/2610.26432)，[作者主页ICCAD26归属](https://wenjifang.netlify.app/)。作者主页标题省略Logic，引用宜保留所用arXiv原文标题。
2. RL-CCD [作者PDF](https://gtcad.gatech.edu/www/papers/yi-chen_DAC23_RL-CCD.pdf)，[作者主页会议归属](https://yichen-lu.github.io/)。
3. IR-aware ECO [作者原文](https://arxiv.org/html/2402.07781v2)，[作者机构出版元数据/DOI](https://experts.azregents.edu/en/publications/ir-aware-eco-timing-optimization-using-reinforcement-learning/)，DOI 10.1145/3670474.3685945。
4. RL-Sizer [作者PDF](https://gtcad.gatech.edu/www/papers/dac21-3.pdf)，[DAC官方session/作者信息](https://58dac.conference-program.com/session/?sess=sess129)。
5. MARL post-place [作者实验室页](https://csdl.postech.ac.kr/bbs/board.php?bo_table=sub5_1&wr_id=277)，[官方ICCAD2024 program](https://confcats-event-sessions.s3.amazonaws.com/iccad24/uploads/ICCAD_2024_Program_Final.pdf) pp.75–76 session说明， [出版DOI](https://doi.org/10.1145/3676536.3676702)。会议年份2024，不应按2025在线入库误记为ICCAD25。

## 对研究路线的推论（不是原文声明）

- 用“区域→候选→多动作联合/序列→物理评价→反馈调度→接受归档”逐格比较；WNS budget只是接受政策一格。
- 本项目若要主张独立贡献，应证明某个明确机制（如基于失败/交互的补偿候选构造或相同真实STA预算下的搜索分配）相对简单强基线有效。把面积估计排序、beam、reference gate串起来是必要实现，不自动构成独立科学贡献。
- 真实STA、学习代理、局部近似、全layout评价、重route/SPEF、末端signoff是不同测量层次，不能因有物理反馈就合并称同一保真度。
- 本次未查到原文证明上述工作采用与我们相同的“固定实际回调次数预算+所有失败调用计费”协议；这只是本次阅读边界，不能转写为文献普遍缺失。
- GraPhSyM（ICCAD23）更适合作为跨阶段area/delay代理模型相关工作，不宜列作整体ECO闭环直接竞品。2025 ICCAD contest C的标题也明确simultaneous gate sizing/buffering/cell relocation，是领域范围的强证据，但本轮NVIDIA PDF读取失败，不据snippet展开其评测细则。
