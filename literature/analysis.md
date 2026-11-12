# Literature Analysis — FAECO Project

> **Analyst**: Literature-analyst agent  
> **Date**: 2026-11-12  
> **Scope**: 7 papers from `literature/papers/`, analyzed for comparison with FAECO  
> **FAECO reference**: Coverage-first iterative gate sizing + buffer insertion, post-placement stage, ISCAS89 benchmark, sky130 PDK

---

## 1. Jiang et al. 2024 — IR-Aware ECO Timing Optimization Using RL

**Paper**: `jiang2024_ir_eco_rl.pdf`  
**Venue**: MLCAD 2024  
**Authors**: Wenjing Jiang, Vidya A. Chhabria, Sachin S. Sapatnekar (U. Minnesota, Arizona State)

### Problem
Post-PD (power-delivery) IR-drop-induced timing failures at the **ECO stage** (after placement, routing, and power grid synthesis). Only incremental changes allowed due to near-final layout. Fixes timing violations through gate sizing (upsize/downsize) while minimizing placement perturbation.

### Method
- **RL-LR-Sizer**: Deep Q-Network (DQN) with **R-GCN** (Relational Graph Convolutional Network) agent
- Couples RL with **Lagrangian Relaxation (LR)**: uses Lagrange multipliers to dynamically weight constraints, avoiding hand-tuned penalty functions
- Two-step decision: (i) Order — which gate to operate on; (ii) Choice — upsize or downsize
- State: subgraph of critical-path gates + 2-hop neighborhood (global view)
- Action mask prunes action space to critical-path only
- **Novel clock update** method during training for multi-specification transferability
- Built on **OpenROAD** APIs (open-source STA + PDN analysis)

### Benchmarks
- **7 OpenCores designs** (des_area, wb_dma, pid_controller, aes_cipher_top, des_perf, pci_bridge32, wb_conmax)
- **Open 45nm** technology (Nangate)
- 2k–26k gate instances
- IR drop: low (~5mV) and moderate (~10mV) scenarios

### Key Metrics
| Metric | Value |
|--------|-------|
| Power overhead savings (avg) | **29.1%** (max **48.8%**) |
| Power overhead savings (Inf-TC avg) | **24.9%** |
| Runtime reduction vs LR (Inf-TC) | **44.5%** |
| Runtime reduction vs LR (cross-design) | **55.7%** |
| Training time | 40–70 min (one-time, amortized) |
| Recovery example (wb_conmax @ 0.85ns) | **83.3%** of IR-induced power overhead |
| Upsize/downsize count reduction | +3.3% upsizes, −7.8% downsizes vs LR |

### Open Source / Reproducibility
- Built on OpenROAD (open-source), uses PyTorch + DGL
- **Not explicitly open-sourced** (no code repository mentioned)
- Reproducible in principle given open 45nm PDK + OpenROAD

### Key Limitations
1. **IR-drop-specific**: Only addresses timing failures caused by IR drop, not general timing ECO
2. **IR magnitude limited**: Tested only up to ~10mV IR drop; higher drops require major changes beyond ECO scope
3. **Power-only objective**: Minimizes power subject to timing constraints; no area metric reported
4. **Post-PD stage**: Requires completed power grid synthesis (later than post-placement)
5. **Training cost**: RL training from scratch takes 40–70 min per design; inference needs pretrained model
6. **No buffer insertion**: Only gate sizing (upsize/downsize), no buffering or logic restructuring

### Comparison to FAECO
| Aspect | Jiang 2024 | FAECO |
|--------|-----------|-------|
| Stage | Post-PD ECO (after PG synthesis) | Post-placement ECO |
| Technology | Open 45nm | sky130 |
| Benchmarks | OpenCores (7 designs) | ISCAS89 |
| Method | RL (R-GCN + DQN) + LR | Coverage-first greedy + gate sizing + buffer insertion |
| Action space | Upsize/downsize only | Gate sizing + buffer insertion |
| Objective | Power minimization w/ timing constraints | Timing (WNS/TNS) improvement |
| IR-awareness | Yes (core contribution) | No |
| Runtime model | RL training expensive, inference fast | Heuristic (no training) |

---

## 2. Agiza & Reda 2023 — GraPhSyM: Graph Physical Synthesis Model

**Paper**: `agiza2023_graphsym.pdf`  
**Venue**: ICCAD 2023  
**Authors**: Ahmed Agiza, Sherief Reda (Brown University)

### Problem
**Predicting post-physical-synthesis delay and area** from pre-synthesis gate-level netlist, **without running the slow physical synthesis flow** (~17s per design). Enables fast design space exploration at logic synthesis stage.

### Method
- **GATv2** (Graph Attention Network v2) supervised learning
- Novel **per-pin labeling**: predicts delay/area *changes* (deltas) at each pin rather than absolute values, accounting for buffer insertion and other structural changes
- **Compositional graph sweeping**: predicts delay-area tradeoffs at relaxed delay targets without retraining
- Trained on prefix adders; tested on adders + generalization to general circuits

### Benchmarks
- **Training**: 10,000 randomly generated prefix adder circuits
- **Evaluation**: held-out prefix adders; 8 general circuits (mult16, mult32, AES Sbox, MD5 core, lzd, axmul16, csela32, priority encoder)
- **Nangate 45nm** open cell library
- Physical synthesis: **OpenPhySyn**

### Key Metrics
| Metric | Value |
|--------|-------|
| Delay accuracy (unseen adders) | **98.3%** (1.7% MAE) |
| Area accuracy (unseen adders) | **96.1%** (3.9% MAE) |
| Delay accuracy (unseen delay targets, sweep) | **98.2%** (1.81% MAE) |
| Area accuracy (unseen delay targets, sweep) | **97.8%** (2.17% MAE) |
| Inference time | **0.22s** vs 17s physical synthesis (**77× speedup**) |
| Generalization (unseen designs, no fine-tuning) | Delay MAE **9.74%**, Area MAE **15.61%** |
| Pre-synthesis baseline error (same unseen designs) | Delay MAE **34.79%**, Area MAE **30.22%** |

### Open Source / Reproducibility
- Uses OpenPhySyn (open-source) and Nangate 45nm (open)
- **Code not open-sourced**
- Reproducible in principle with open tools

### Key Limitations
1. **Prediction only**: GraPhSyM predicts metrics; it does **not perform optimization** — it's a proxy model, not a solver
2. **Training domain narrow**: Trained exclusively on prefix adders; generalization to arbitrary circuits is significantly worse (9.74% delay MAE vs 1.7%)
3. **No power modeling**: Only delay and area; power is mentioned as future work
4. **Pre-synthesis input only**: Requires pre-synthesis netlist; not applicable at post-placement/post-routing ECO stage
5. **Per-pin labeling assumption**: Assumes physical synthesis transformations can be mapped back to pre-synthesis pins (may not hold for major restructuring)

### Comparison to FAECO
| Aspect | GraPhSyM | FAECO |
|--------|---------|-------|
| Purpose | Prediction/proxy | Optimization |
| Stage | Pre-synthesis → post-synthesis prediction | Post-placement ECO |
| Technology | Nangate 45nm | sky130 |
| Benchmarks | Prefix adders + 8 general circuits | ISCAS89 |
| Method | GATv2 supervised learning | Coverage-first greedy heuristic |
| Action | None (prediction only) | Gate sizing + buffer insertion |
| Relevance | Low — different problem entirely | — |

---

## 3. Liu et al. 2026 — GoalEvolve: Goal-Driven Evolution of Physical Design

**Paper**: `liu2026_goalevolve.pdf`  
**Venue**: arXiv:2608.16733 (Aug 2026)  
**Authors**: Haixu Liu, Lei Zhou, Yuhao Ren, Yumao Wu, Zhiang Wang (Fudan University)

### Problem
Physical design **algorithm source-code evolution** accountable for **final full-flow QoR** (not stage-local gains). Existing frameworks optimize stage-local objectives, which may vanish or degrade downstream. GoalEvolve makes algorithm evolution goal-driven: given multi-objective QoR targets, it identifies bottlenecks and modifies OpenROAD source code.

### Method
- **LLM-based Teacher-Student framework**: Teacher (GPT-5.6 Terra) diagnoses bottlenecks, generates source hypotheses; Students implement and validate via full-flow evaluation
- **Bottleneck-directed loop**: Converts QoR gaps → normalized target gaps → identifies dominant bottleneck → locates responsible stage via stage-resolved checkpoints → narrows to algorithmic decision + bounded source region
- **Evidence-constrained hypotheses**: Local effects, optimization debt, and downstream retention tracked as mechanism evidence
- Instantiated for **OpenROAD post-placement optimization** (Gate Resizer, Restructure mechanisms)
- Evolution terminates when goal reached or full-flow evaluation budget exhausted

### Benchmarks
- **8 designs**: AES, Ariane, JPEG, MemPool, NVDLA-A/C/M/P
- **ASAP7** technology (7nm predictive)
- **OpenROAD** flow (open-source)
- Design sizes: ~20K–313K instances
- Comparison: OpenROAD default baseline, commercial-tool goals, Codex goal mode

### Key Metrics
| Metric | Value |
|--------|-------|
| Post-route TNS improvement (avg vs OpenROAD default) | **30.67%** |
| Leakage power reduction (avg) | **21.18%** |
| Dynamic power reduction (avg) | **9.42%** |
| Power gap closed (power-dominant designs) | **62.20%** |
| Joint timing–power gap closed | **32.48%** |
| TNS vs Codex goal mode (matched budget) | **+26.46%** better |
| Leakage vs Codex goal mode | **−12.38%** |
| Dynamic power vs Codex goal mode | **−0.76%** |
| Runtime (observer metric) | 46–1,074s per design |
| Outperforms commercial-tool TNS on timing-dominant designs | Yes (2 of 2) |

### Open Source / Reproducibility
- **"We will open-source the GoalEvolve implementation and experimental scripts"** (claimed future)
- Based on OpenROAD + ASAP7 (both open)
- LLM-dependent (GPT-5.6 Terra with high reasoning effort)

### Key Limitations
1. **LLM-dependent**: Requires GPT-5.6 Terra; quality and reproducibility tied to specific model version
2. **Algorithm-level optimization**: Modifies OpenROAD source code, not instance-level gate sizing — different granularity from FAECO
3. **Post-placement only within OpenROAD**: Limited to OpenROAD's post-placement optimization stage
4. **High compute cost**: Each evaluation runs full placement → routing flow; 4 coding agents + 1 Teacher per round
5. **Transferred source limited**: When evolving on AES and transferring to other designs, TNS regresses on NVDLA-C and NVDLA-A despite 46.72% average improvement
6. **No buffer insertion as explicit action**: Modifies Gate Resizer and Restructure mechanisms; buffer insertion is implicit in downstream flow

### Comparison to FAECO
| Aspect | GoalEvolve | FAECO |
|--------|-----------|-------|
| Optimization level | Algorithm source code | Instance-level gate changes |
| Stage | Post-placement (OpenROAD flow) | Post-placement |
| Technology | ASAP7 (7nm) | sky130 (130nm) |
| Benchmarks | 8 large designs (20K–313K instances) | ISCAS89 (small) |
| Method | LLM Teacher-Student | Coverage-first greedy heuristic |
| Actions | Source code edits (C++/Tcl) | Gate sizing + buffer insertion |
| Goal | Multi-objective QoR targets | WNS/TNS improvement |
| Runtime scale | 100s–1000s seconds | ~seconds per candidate |

---

## 4. Fang et al. 2026 — E-Layout: Layout-Stage Logic Restructuring

**Paper**: `fang2026_elayout.pdf`  
**Venue**: ICCAD 2026 (submission)  
**Authors**: (multiple, institution not fully extracted)

### Problem
**Post-placement layout restructuring** that preserves functional equivalence while jointly optimizing logic structure and physical realization. Existing open-source tools (OpenROAD restructuring, OpenPhySyn) either lack layout awareness or are limited to local cell-level edits (pin swapping, gate cloning). The key insight: logic restructuring at layout stage has been neglected because traditional tools cannot reason about physical context when exploring logic alternatives.

### Method
- **e-graph equality saturation**: Enumerates all functionally equivalent logic structures for each MFFC (Maximum Fanout-Free Cone)
- **Graph RAG** (Retrieval-Augmented Generation): SGFormer graph-transformer backbone retrieves promising structures from the e-graph and generates physical attributes (cell sizes, locations)
- **GRPO** (Group Relative Policy Optimization): RL fine-tuning with full-chip TNS as reward, using INSTA for fast incremental timing feedback
- Three restructuring types: expansion (complex → simpler gates, ~70%), merging (simpler → complex, ~3%), size-only (~27%)
- Operates on MFFC granularity; only MFFCs with >5 equivalent candidates are optimized

### Benchmarks
- **9 diverse designs**: s838_1_bench, wb_dma_top, spi_top, usbf_top, NV_csb_master, NV_bdma, ac97_top, arm_core, Rocket
- Sources: OpenCores, ITC'99, Chipyard, NVDLA
- **ASAP7** (7nm) within a **leading commercial physical design flow**
- Baselines: Commercial flow, OpenROAD-Restructure, OpenPhySyn-Restructure
- Formal verification: SMT-based combinational equivalence checker (MFFC-level) + Synopsys Formality (full-chip)

### Key Metrics
| Metric | Value |
|--------|-------|
| TNS improvement vs commercial baseline (avg) | **6.07%** |
| WNS improvement vs commercial baseline (avg) | **2.29%** |
| Area reduction vs commercial baseline (avg) | **1.07%** |
| OpenROAD-Restructure TNS (avg) | **+21.54% degradation** |
| OpenPhySyn-Restructure TNS (avg) | **+1.37% degradation** |
| MFFCs rewritten | ~9% of candidate cones |
| Avg cells per rewritten MFFC | 3 (range 1–27) |
| Best individual TNS gain (usbf_top) | **16.26%** |
| Best individual WNS gain (usbf_top) | **16.67%** |
| Total runtime | minutes to hours (design-dependent) |
| RAG inference | <1s per batch on GPU |

### Open Source / Reproducibility
- Uses egg-log (open-source) for e-graphs, SGFormer (open-source)
- Relies on **commercial physical design flow** (not fully open)
- **Code not explicitly open-sourced**
- INSTA incremental timer (proprietary)

### Key Limitations
1. **Commercial flow dependency**: Restructuring evaluated within commercial tool flow; open-source standalone reproducibility unclear
2. **MFFC granularity**: Only restructures within MFFCs; cross-MFFC optimizations not considered
3. **Buffering/sizing still commercial**: E-Layout only does restructuring; downstream buffering/sizing handled by commercial tools — final PPA observed only after complete downstream flow
4. **Limited improvement magnitude**: 6% TNS is modest; starting point already heavily optimized by commercial flow
5. **Restructuring bias**: ~70% expansions, only ~3% merges — may miss opportunities for logic compaction
6. **No buffer insertion in restructuring**: Buffers added only by downstream tools

### Comparison to FAECO
| Aspect | E-Layout | FAECO |
|--------|---------|-------|
| Optimization type | Logic restructuring (equivalence-preserving) | Gate sizing + buffer insertion |
| Granularity | MFFC (multi-gate cones) | Individual gates |
| Stage | Post-placement | Post-placement |
| Technology | ASAP7 (7nm) | sky130 (130nm) |
| Benchmarks | 9 diverse designs | ISCAS89 |
| Method | e-graph + Graph RAG + GRPO | Coverage-first greedy |
| Actions | Logic structure changes + sizing/location | Gate sizing + buffer insertion |
| Tool flow | Commercial | Open-source (Yosys + OpenSTA) |
| TNS gain | 6.07% avg | (FAECO-specific numbers not in scope) |

---

## 5. Jiang et al. 2025 — EasySize: LLM-Guided Analog Circuit Sizing

**Paper**: `jiang2025_easysize.pdf`  
**Venue**: arXiv preprint (Aug 2025)  
**Authors**: (multiple, institution not fully extracted — uses Sizer framework)

### Problem
**Analog circuit (Op-Amp) transistor sizing** across different process nodes and topologies. Key challenges: high dependency on technology nodes, heavy reliance on human expertise, multi-objective optimization (gain, bandwidth, phase margin, slew rate, bias current). Existing methods (BO, DE, PSO, AutoCkt) are either slow, unstable, or tied to specific nodes.

### Method
- **LLM fine-tuned** (model unspecified, trained on 350nm BSIM3V3.1 data) to **generate loss functions** that guide heuristic search
- **DE + PSO hybrid** as the search engine (from Sizer framework)
- **EOA** (Ease of Attainability): novel concept ranking how easily each metric target can be achieved; used to weight loss function terms
- **Feedback-enhanced flow**: LLM dynamically adjusts loss functions based on optimization state
- Fine-tuned solely on **350nm**; tested zero-shot on 180nm, 45nm, 22nm

### Benchmarks
- **5 Op-Amp netlists** from Analog Designer's Toolbox (ADT): A020005, A020007, A020009, A020014, A020017
- **BSIM PTM** technology nodes: **180nm, 45nm, 22nm** (test); **350nm** (train only)
- Simulator: Ngspice (open-source)
- Baselines: BO-100, AutoCkt (RL-based), pure DE+PSO (Sizer)

### Key Metrics
| Metric | Value |
|--------|-------|
| Outperforms AutoCkt | **86.67%** of tasks (13/15) |
| Simulation reduction vs AutoCkt | **96.67%** fewer simulations |
| Simulation reduction vs pure heuristic (180nm/45nm) | **>10%** |
| Runtime | Same order of magnitude as BO-100 |
| Cross-node generalization | Trained on 350nm only; works on 180nm/45nm/22nm |
| AutoCkt failures | Failed on 180nm A020007 and A020009 (couldn't find initial point) |
| Success rate | Higher than BO and AutoCkt on most cases |

### Open Source / Reproducibility
- **"EasySize will be open-sourced at a later date"** (soft commitment)
- Built on Sizer (open-source), uses Ngspice (open-source), BSIM PTM (open)
- LLM fine-tuning requires proprietary model access

### Key Limitations
1. **Analog only**: Op-Amp transistor sizing; **completely different domain** from digital gate sizing
2. **Small benchmark**: Only 5 Op-Amp netlists; limited topology diversity
3. **LLM-dependent**: Requires fine-tuned LLM; model identity not disclosed
4. **Simple metrics**: Gain, BW, PM, SR, IDC — no area, no noise, no PSRR
5. **No digital relevance**: Cannot be compared to digital ECO methods
6. **EOA is heuristic**: EOA computed from simulation statistics; not a rigorous metric

### Comparison to FAECO
| Aspect | EasySize | FAECO |
|--------|---------|-------|
| Domain | **Analog** (Op-Amp transistor sizing) | **Digital** (standard-cell gate sizing) |
| Stage | Circuit design (pre-layout) | Post-placement ECO |
| Technology | 180nm/45nm/22nm BSIM PTM | sky130 |
| Method | LLM + DE/PSO | Coverage-first greedy |
| Relevance | **None** — different domain entirely | — |

---

## 6. Gu et al. 2026 — LATCH: LLM-Agent Tool Chain for Hardware Timing Closure

**Paper**: `gu2026_latch.pdf`  
**Venue**: 2026 (submission)  
**Authors**: (multiple, University of Edinburgh)

### Problem
**FPGA post-route timing closure** via LLM-orchestrated backend EDA operations. FPGA timing closure requires iterative application of placement, physical optimization, and routing — traditionally manual and expertise-intensive. LATCH explores what level of agent control (recipes → direct EDA ops → constructed procedures) yields reliable timing improvement.

### Method
- **LATCH framework**: Deterministic execution layer (AMD Vivado 2025.1 + RapidWright) + LLM orchestration layer
- **Three control granularities**:
  1. **Expert recipes**: Agent selects from fixed catalog of engineer-written transforms (e.g., `phys_opt`, `auto_pblock`) — **98.2% pass rate**
  2. **Direct EDA operations**: Agent constructs individual Vivado Tcl commands with bounded operations — **71.4% pass rate**
  3. **Constructed procedures**: Agent generates procedures with intermediate objects — **17.9% pass rate** (most fail before qualifying proposal)
- **Multi-iteration study**: Sequential reasoning vs branching exploration vs knowledge base-guided exploration
- Seven LLMs evaluated: Claude Sonnet 5, DeepSeek v4 Flash/Pro, Gemini 3.6 Flash, GPT-5.6 Luna/Sol/Terra

### Benchmarks
- **16 FPGA designs**: boom_soc, vexriscv_re-place, amd_mini_isp, logicnets_jscl, finn_radioml, rosetta_digit-recognition, rosetta_optical-flow, corescore_500_mod, + v2 variants and additional designs
- **AMD Vivado 2025.1**, Kintex-7 FPGA
- Initial Fmax range: 48.2 MHz (boom_soc) to 405.7 MHz (fir_symmetric_systolic)

### Key Metrics
| Metric | Value |
|--------|-------|
| Recipe functional-pass rate | **98.2%** (110/112) |
| Direct ops functional-pass rate | **71.4%** (80/112) |
| Constructed procedures pass rate | **17.9%** (20/112) |
| Recipe median Fmax improvement | **+3.2%** |
| Direct ops median Fmax improvement | **+3.4%** |
| Constructed procedures median Fmax | **0.0%** |
| Branching exploration: best Fmax gain (boom_soc) | **+102.2%** (49.3% Fmax) |
| Knowledge base-guided: best Fmax gain (vexriscv) | **+51.4%** (159.5 MHz) |
| Sequential reasoning best across 16 designs | +0–31.5% (design-dependent) |
| DeepSeek v4 Flash direct ops: best individual gain | **+117.0 MHz** on LogicNets |
| Fitted heuristic (in-domain) | Strongest on known designs, 0% on 5/8 held-out |

### Open Source / Reproducibility
- **Yes — fully open-source**: https://github.com/aprilaihub/LATCH
- AMD Vivado required (proprietary); RapidWright (open-source)
- 7 LLMs tested, results characterized per model

### Key Limitations
1. **FPGA only**: Vivado-specific; not applicable to ASIC digital design flows
2. **LLM-dependent**: Requires capable LLM; performance varies drastically by model (GPT-5.6 Luna 19% timing improvement vs DeepSeek v4 Flash 88%)
3. **Single-iteration gains modest**: Median ~3% Fmax improvement per trial; multi-iteration needed for substantial gains
4. **Constructed procedures mostly fail**: 82.1% failure rate on the most flexible interface
5. **Vivado coupling**: Cannot generalize to other FPGA or ASIC backends without re-engineering the execution layer
6. **No gate sizing or buffer insertion as explicit primitives**: Operations are at Vivado command level (placement, phys_opt, routing)

### Comparison to FAECO
| Aspect | LATCH | FAECO |
|--------|-------|-------|
| Domain | **FPGA** (Vivado) | **ASIC** (Yosys + OpenSTA) |
| Stage | Post-route FPGA | Post-placement ASIC |
| Technology | Kintex-7 FPGA | sky130 |
| Method | LLM agent + expert recipes | Coverage-first greedy heuristic |
| Actions | Vivado Tcl commands (placement, phys_opt, routing) | Gate sizing + buffer insertion |
| Pass rate | 71.4–98.2% (depending on interface) | Deterministic |
| Reproducibility | Open-source code | (Project state) |
| Relevance | Medium — agent-based timing closure paradigm is relevant, but FPGA domain limits direct comparison | — |

---

## 7. Ye et al. 2024 — GNN-Based Timing Optimization Framework for VLSI ECO

**Paper**: `ye2024_gnn_eco.pdf`  
**Venue**: Submitted to IEEE TCAD (arXiv:2403.08193, Mar 2024)  
**Authors**: Yuyang Ye, Peng Xu, Lizheng Ren, Tinghuan Chen, Hao Yan, Bei Yu, Longxing Shi (Southeast University, CUHK)

### Problem
**Post-routing gate sizing** for timing optimization on large-scale circuits. Existing ML-based methods (RL-Sizer, Transizer) cannot optimize multiple timing paths simultaneously and neglect physical layout constraints (gate density, wire congestion). Poor convergence forces many time-consuming ECO iterations.

### Method
- **Multi-modal GNN**: Combines timing path features (graph attention on netlist paths) + physical layout features (ResNet-ASPP on multi-scale layout grids) + ICC2 optimization gradients
- **Straight-through estimator (STE)**: Handles discrete gate sizes as integer-valued variables for differentiable gradient descent, avoiding Softmax approximations used in prior work (AGD)
- **Adaptive gradient back-propagation**: Gumbel-softmax sampling prioritizing gates with larger WNS; adaptive learning rates per gate
- **ICC2-supervised**: Training labels (gradient direction, optimal gate sizes) from Synopsys ICC2 — learns to *outperform* ICC2 rather than imitate it
- Timing target: weighted combination of TNS and WNS targets (tunable weights μτ, μω)

### Benchmarks
- **Open-source designs**: TATE, ECG, and others (Table I lists 10+ circuits)
- **TSMC 16nm** technology
- Baselines: **ICC2** (commercial), RL-Sizer, TransSizer, AGD
- Training/testing split across designs

### Key Metrics
| Metric | Value |
|--------|-------|
| TNS improvement vs ICC2 (avg) | **16.29%** |
| WNS improvement vs ICC2 (avg) | **18.61%** |
| Speedup vs ICC2 | **6.64×** |
| Speedup vs RL-Sizer | **11.25×** |
| Gate-wise TNS prediction R² (training) | High (exact value in paper Table II) |
| Gate-wise WNS prediction MAE | ~ps level |
| Ablation: removing multi-path features | Largest degradation |
| Ablation: removing multi-scale physical features | Significant degradation |
| Ablation: removing Gumbel sampling (adaptive BP) | Runtime nearly equals ICC2 (no speedup) |

### Open Source / Reproducibility
- Implemented in PyTorch + C++
- **Not explicitly open-sourced**
- Requires **TSMC 16nm** (proprietary) and **ICC2** (commercial) for training labels
- Requires **StarRC** (commercial) for SPEF extraction
- Low reproducibility without commercial tool access

### Key Limitations
1. **ICC2-dependent training**: Gradient labels come from ICC2; the model can at best learn to replicate and slightly improve upon ICC2 behavior — it cannot discover fundamentally different optimization strategies
2. **Post-routing only**: Requires SPEF (parasitic extraction) and detailed routing; not applicable at post-placement stage
3. **TSMC 16nm only**: Single technology node; no demonstration of cross-node transfer
4. **Supervised ceiling**: Training labels bound model quality to commercial tool quality
5. **No buffer insertion**: Only gate sizing (discrete cell selection); no buffering or logic restructuring
6. **Power ignored**: Power reported as observer metric only ("ignorable power overhead"); not an optimization target
7. **Commercial flow dependency**: StarRC, ICC2, TSMC 16nm PDK all proprietary — fully closed ecosystem for training

### Comparison to FAECO
| Aspect | Ye 2024 | FAECO |
|--------|---------|-------|
| Stage | Post-routing ECO | Post-placement ECO |
| Technology | TSMC 16nm (proprietary) | sky130 (open) |
| Benchmarks | Open-source designs (10+) | ISCAS89 |
| Method | Multi-modal GNN + gradient descent | Coverage-first greedy heuristic |
| Actions | Gate sizing only | Gate sizing + buffer insertion |
| Training | Requires ICC2 labels (commercial) | No training needed |
| Toolchain | ICC2 + StarRC (commercial) | Yosys + OpenSTA (open-source) |
| Reproducibility | Low (commercial tools) | High (fully open-source) |

---

## Cross-Paper Summary Table

| Paper | Stage | Domain | Method | Actions | Tech Node | Benchmarks | Best Metric | Open Source |
|-------|-------|--------|--------|---------|-----------|------------|-------------|-------------|
| Jiang 2024 | Post-PD ECO | ASIC Digital | R-GCN + RL + LR | Gate sizing (up/down) | 45nm Nangate | 7 OpenCores | 29.1% power saving | No |
| Agiza 2023 | Pre-synthesis | ASIC Digital | GATv2 | Prediction only | 45nm Nangate | 10K prefix adders | 98.3% delay accuracy | No |
| Liu 2026 | Post-placement | ASIC Digital | LLM Teacher-Student | Source code edits | ASAP7 (7nm) | 8 designs | 30.67% TNS reduction | Claimed future |
| Fang 2026 | Post-placement | ASIC Digital | e-graph + Graph RAG + GRPO | Logic restructuring + sizing | ASAP7 (7nm) | 9 designs | 6.07% TNS improvement | No |
| Jiang 2025 | Pre-layout | Analog | LLM + DE/PSO | Transistor sizing | 180/45/22nm | 5 Op-Amps | 86.67% tasks better than AutoCkt | Claimed future |
| Gu 2026 | Post-route | FPGA | LLM agent + recipes | Vivado Tcl commands | Kintex-7 | 16 FPGA designs | +102.2% Fmax (best) | **Yes** (GitHub) |
| Ye 2024 | Post-routing | ASIC Digital | Multi-modal GNN + gradient descent | Gate sizing | TSMC 16nm | 10+ designs | 16.29% TNS / 18.61% WNS vs ICC2 | No |

---

## Key Gaps Relevant to FAECO

1. **No prior work at post-placement stage with open-source toolchain (sky130 + Yosys + OpenSTA)**: Jiang 2024 operates at post-PD ECO stage with 45nm; Liu 2026 and Fang 2026 use ASAP7 + commercial flow; Ye 2024 uses TSMC 16nm + ICC2 at post-routing. FAECO's post-placement + sky130 + fully open-source combination is unique.

2. **No prior work on coverage-first iterative scheduling for ECO**: All RL/ML methods either use RL for sequential decision-making (Jiang 2024, Ye 2024) or LLM agents for tool orchestration (Liu 2026, Gu 2026). The coverage-first paradigm — prioritizing candidates by endpoint coverage before sizing — is absent from literature.

3. **No prior work coupling gate sizing with buffer insertion in a unified ECO loop**: Jiang 2024 and Ye 2024 do gate sizing only. Fang 2026 does logic restructuring. Liu 2026 modifies OpenROAD source (implicit buffering). FAECO's explicit joint sizing+buffering within one iterative loop is novel at the post-placement stage.

4. **Benchmark gap**: Most works use larger benchmarks (OpenCores, NVDLA, Ariane) and advanced nodes (7nm, 16nm, 45nm). FAECO's ISCAS89 + sky130 is a simpler but fully open and reproducible setup — a different niche from the "chase commercial tool performance" approach of most papers.

5. **Failure characterization gap**: None of the surveyed papers systematically analyze *why* candidates fail or characterize candidate失效模式 (failure modes). FAECO's explicit失效刻画 (failure characterization) is a distinctive contribution.

6. **Only one paper is verifiably open-source**: Gu 2026 (LATCH) provides GitHub code. The rest are either closed or claim future open-sourcing. FAECO's fully open-source toolchain is a strength.

---

## Methodological Trends

- **LLM integration is accelerating**: 3 of 7 papers (Liu 2026, Jiang 2025, Gu 2026) use LLMs as core components; this trend began ~2025
- **GNN dominance for circuit representation**: 4 of 7 papers use GNNs (R-GCN, GATv2, SGFormer, multi-modal GNN)
- **RL remains the optimization backbone**: 3 of 7 papers use RL (DQN, GRPO, RL-Sizer)
- **Commercial tool dependency is the norm**: Only Jiang 2024 and Agiza 2023 use fully open PDKs; the rest depend on commercial tools
- **Shift from prediction to optimization**: Earlier papers (Agiza 2023) focus on prediction; later papers (2024–2026) focus on optimization