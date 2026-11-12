# FAECO 文献调研报告

**生成日期**: 2026-11-12  
**调研范围**: post-placement / post-CTS 时序优化、gate sizing、buffer insertion、ML-based ECO  
**检索源**: arXiv (cs.AR, cs.LG)、Semantic Scholar、IEEE Xplore、ACM DL  
**检索时段**: 2022–2026

---

## 1. 核心竞争文献（已下载）

### 1.1 Jiang et al. (2024) — IR-Aware ECO Timing Optimization Using RL
- **出处**: arXiv:2402.07781
- **任务**: post-physical-design ECO gate sizing，考虑 IR drop
- **方法**: RL (R-GCN agent) + Lagrangian Relaxation
- **基准**: 45nm open PDK (FreePDK45)
- **关键指标**: 
  - Pareto front 左移（delay-power tradeoff）
  - Runtime 优于 classical LR algorithm
  - 更少的 cell perturbation
  - 模型可迁移（跨设计、跨时序规格）
- **与 FAECO 差异**: 
  - 聚焦 IR-drop，不是我们做的通用 post-placement ECO
  - 用 RL 选门，不是我们的覆盖优先迭代
  - 报告 delay-power Pareto，不是 area-WNS
  - 不开源

### 1.2 Agiza et al. (2023) — GraPhSyM (ICCAD 2023)
- **出处**: arXiv:2308.03944, ICCAD 2023
- **任务**: 从 pre-synthesis netlist 预测 post-synthesis delay 和 area
- **方法**: GATv2 graph attention network
- **基准**: 6000 prefix adder designs (合成数据)
- **关键指标**: 
  - Delay prediction accuracy: **98.3%**
  - Area prediction accuracy: **96.1%**
  - Inference time: **0.22s**
  - 跨 delay target 泛化
- **与 FAECO 差异**: 
  - 这是预测器，不是优化器
  - 可以作为 ML-based ECO 的 oracle 使用
  - 在加法器上训练，对 ISCAS89 泛化未验证

### 1.3 Liu et al. (2026) — GoalEvolve
- **出处**: arXiv:2608.16733
- **任务**: 完整物理设计流程的 goal-driven 优化
- **方法**: LLM Teacher-Student 进化框架
- **基准**: 8 ASAP7 designs
- **关键指标** (vs default OpenROAD):
  - Post-route **TNS +30.67%**
  - Leakage −21.18%
  - Dynamic power −9.42%
  - vs commercial tool: closes 62.20% power gap on power-dominant designs
- **与 FAECO 差异**: 
  - 全流程优化（不是 ECO）
  - 不同基准（ASAP7 vs ISCAS89）
  - LLM-based，不是确定性算法
  - 不放代码

### 1.4 Fang et al. (2026) — E-Layout (ICCAD 2026)
- **出处**: arXiv:2610.26432, ICCAD 2026
- **任务**: post-placement layout restructuring（逻辑重构 + 物理实现联合优化）
- **方法**: RL + e-graph equality saturation + RAG
- **基准**: 9 diverse designs on commercial physical design flow
- **关键指标** (vs industry-leading commercial PD flow):
  - **TNS +6%**
  - **WNS +2%**
  - **Area −1%**
- **与 FAECO 差异**: 
  - 做 logic restructuring（等价逻辑替换），不是 gate sizing
  - 跑在商业流程上，不是开源
  - 报告的是 vs commercial tool，绝对值已高度优化

### 1.5 Ye et al. (2024) — GNN-Based ECO Timing Optimization
- **出处**: arXiv:2403.08193
- **任务**: VLSI ECO timing optimization
- **方法**: GNN-based general-purpose framework
- **基准**: 待读全文确认
- **关键指标**: 待提取
- **与 FAECO 差异**: 最直接的竞争者，需仔细对比

### 1.6 Gu et al. (2026) — LATCH: LLM-Agent for Hardware Timing Closure
- **出处**: arXiv:2610.16625
- **任务**: FPGA timing closure via LLM agent
- **方法**: LLM agent tool chain
- **基准**: FPGA designs
- **关键指标**: 待提取
- **与 FAECO 差异**: FPGA 领域，非 ASIC gate sizing

### 1.7 Jiang et al. (2025) — EasySize
- **出处**: arXiv:2508.05113
- **任务**: 模拟电路自动 sizing
- **方法**: LLM-guided
- **基准**: 模拟电路 benchmarks
- **与 FAECO 差异**: 模拟电路 domain，非数字 ECO。方法论可参考。

---

## 2. 竞争格局总结

### 2.1 可按指标直接对比的工作

| 方法 | WNS改善 | 面积代价 | 基准 | 阶段 | 开源 |
|------|---------|----------|------|------|------|
| **OpenROAD resizer** | **+28.3%** (s382) | **+50–57%** | ISCAS89 sky130 | post-CTS | ✅ |
| **FAECO-P** | **+15.1%** (s382) | **+13–18%** | ISCAS89 sky130 | post-CTS | ✅ |

### 2.2 不可直接比较但相关的工作

| 方法 | 主要指标 | 为什么不能直接比 |
|------|----------|------------------|
| GoalEvolve | TNS +30.67% | 全流程，不是 ECO；不同基准 (ASAP7) |
| E-Layout | TNS +6%, WNS +2% | Logic restructuring，不是 gate sizing；商业流程 |
| Jiang 2024 | Pareto front 左移 | IR-drop 特化；不同指标 (delay-power) |
| GraPhSyM | 98.3% delay acc | 预测器，不是优化器 |
| Cao 2025 | WNS +35.66% | GNN placement；不同基准 (OpenCores 22nm) |
| Lyn 2024 | +27.75%, +0.2% area | Cell merging；不同机制 |

### 2.3 FAECO 的独特位置

1. **唯一做"覆盖优先迭代 ECO + gate sizing + buffer insertion"的开源方法**
2. **唯一在 ISCAS89 + sky130 上公开报告 WNS+面积 Pareto 的工作**
3. **填补了 resizer "不计面积求 WNS"和理想 ECO "最小改动求功能正确"之间的空白**

---

## 3. FAECO 可提出的贡献（基于现有文献的空白）

### 3.1 已可站住的贡献
- **Coverage-first scheduling**: 文献中独有的"先报告覆盖区域、再逐帧分配预算"的调度策略
- **Pareto-optimal area-WNS point**: Resizer 无法通过调参走到 FAECO 的面积效率水平
- **Pre-registered experimental methodology**: EDA 领域罕见的预注册实验方法论
- **Open-source reproducibility**: 全流程开源（Yosys + OpenROAD + sky130）

### 3.2 需要补充实验才能站住的贡献
- **与 ML-based 方法的对比**: 需要复现 Ye et al. (2024) 或至少定性对比
- **跨设计泛化**: 在 ITC-99 上的结果
- **功耗对比**: 目前只有面积，没有功耗数据

---

## 4. 下一步计划

### 4.1 文献侧
- [x] 下载 7 篇核心论文
- [ ] 逐篇精读，提取完整指标表
- [ ] 写正式 Related Work 段

### 4.2 实验侧
- [ ] 补齐 8 电路全量面积-WNS 数据
- [ ] 跨基准验证（ITC-99）
- [ ] 功耗测量
- [ ] 如可行，复现 Ye et al. (2024) GNN 方法并对比

### 4.3 论文侧
- [ ] 定档位（选定目标会议/期刊）
- [ ] 写 Introduction + Related Work
- [ ] 生成 Pareto 图 (area vs WNS)
- [ ] 写实验段

---

*本文件随文献调研持续更新。*