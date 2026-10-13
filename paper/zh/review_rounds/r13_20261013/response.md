# r13 响应：大同行入口改写（已落地 = v11）

## 结论

**采纳，已落地并重冻结 v11。** 结构按用户指定的「大背景 → 具体问题 → 方法 → 结果 → 意义」重排；`.tex` diffstat = **3 insertions / 3 deletions**（恰 3 行替换：摘要 CN + 摘要 EN + §1.1 引言首段）。**零数字、零实验、零代码改动**；10 页 / 0 Error / 0 Overfull / 0 Underfull 不变。

## 一、落地文本

### 中文摘要（v11）

> 随着集成电路规模与设计复杂度持续提升，时序收敛已成为数字芯片设计流程中的关键挑战。工程变更命令（engineering change order，ECO）通过在已有设计上做局部修改，可降低重新综合与物理实现带来的迭代成本。其中，预布局门级时序 ECO 在布局布线前探索局部网表修改方案，但受候选空间限制、候选验证开销较高。为此提出候选探索与失效刻画框架 FAECO：在违例路径局部逻辑上以多特征加权割与关键路径覆盖割生成并排序 R/G/B/JOINT 候选；将候选失效刻画为六类，作为搜索诊断与消融分析的依据；候选按轮提交，依次经函数与结构检查、时序分析与最终等价性检查。在 ISCAS89、ITC-99 和 PicoRV32 上，8/8、18/19 和 2/2 个实例取得预布局理想线网 WNS 改善（PicoRV32 第三个子模块无 setup 路径，不参与改善判定），其余无退化。固定权重、20 轮迭代下，混合候选平均改善 1.07\,ns，高于仅门尺寸调整的 0.16\,ns。消融实验显示，指数滑动平均失效反馈未带来额外收益，结构重综合候选也未带来额外 WNS 改善；逻辑深度降低不等于 WNS 改善，上述结果可为预布局 ECO 搜索策略设计提供参考。

### 英文摘要（v11）

> Timing closure has become a critical challenge in digital chip design as circuit scale and design complexity continue to grow. Engineering change order (ECO) techniques reduce the iteration cost of re-synthesis and physical implementation by applying localized modifications to an existing design. Among them, pre-placement gate-level timing ECO explores local netlist modifications before placement and routing, but its candidate space is limited and per-candidate verification is costly. FAECO is a framework for candidate exploration and failure characterization. It builds and ranks R/G/B/JOINT candidates over the local logic around violating paths via a multi-feature weighted cut and a critical-path cover cut, characterizes candidate failures into six types used for search diagnosis and ablation analysis, and commits candidates round by round through function and structural checks, timing analysis and final equivalence checking. On ISCAS89, ITC-99 and PicoRV32, 8/8, 18/19 and 2/2 instances achieve pre-placement ideal-net WNS improvement (the third PicoRV32 module has no setup path and is excluded), with no regression on the rest. Under fixed weights and 20 rounds, mixed candidates improve WNS by 1.07\,ns on average versus 0.16\,ns for gate sizing alone. Ablations show no extra benefit from moving-average failure feedback or structure-resynthesis candidates; lower logic depth does not imply WNS improvement, and these results inform the design of future pre-placement ECO search strategies.

## 二、与用户草案的 5 处偏离（逐条取证）

| # | 用户草案 | 落地 | 依据 |
|---|---|---|---|
| 1 | 「工程变更**优化**（ECO）」 | 「工程变更**命令**（engineering change order，ECO）」 | **术语错误**：ECO = Engineering Change **Order**；且 §1.1 正文原文即"工程变更命令（engineering change order，ECO）"，照草案写会与正文冲突 |
| 2 | 删「（PicoRV32 第三个子模块无 setup 路径，不参与改善判定）」→「2/2 个**可评估**实例」 | **保留分母解释句** | 该句是 **r12 M2（审稿人 ★★★★）** 指定落点，无正当理由不得回退 |
| 3 | 删「其余无退化」 | **保留** | r6 P0 边界声明（限定预布局理想线网 WNS 口径）；**加入大背景句后边界声明更不可删** |
| 4 | 「能够**快速**探索局部网表修改方案」 | 去「快速」 | 无独立度量支撑（效率结论是候选级 STA 次数少 26.3%，非"快速探索"） |
| 5 | 无「意义」句 | 末句并入「…可为预布局 ECO 搜索策略设计提供参考」 | 用户五段结构中含"意义"；沿用 r11 结论末句口径，不引入新主张 |

## 三、遵从用户自我约束

- **未写"先进制程"**：落文用「集成电路规模与设计复杂度持续提升」，不涉工艺节点（避免与 SKY130 实验被指"先进节点 claim 过大"）。
- **中文首句未用"先进数字芯片"**：改为「数字芯片设计流程」，进一步收敛修饰语。
- **摘要仍无第一人称**：中文不出现「本文」（沿用既有中文摘要口径——用户草案含"本文提出"，已改"为此提出"）；英文无 "we"。

## 四、长度复核

| 项 | v10 | v11 |
|---|---|---|
| 中文摘要（仅汉字） | 244 | **349** |
| 英文摘要（词） | 164 | **214** |

- 「中文 ≤300 字 / 英文 ≤150 词」是 **JCAD 征稿简则**的规则；改投 **Integration** 后该约束**失效**，但新约束（Elsevier 常见 ≤250 词）**须在 OI-028 轮按 Integration 作者指南正式复核**——已记入 OI-028，不沿用失效规则判合规。

## 五、遗留（已向用户提出，待裁定）

- **§1.1 引言入口未同步**：用户指出的是"大同行入口偏窄"，但 §1.1 首句仍直接进入「工程变更命令（ECO）按修复目标可分为功能 ECO 与时序 ECO」——摘要→引言 30 秒后即遇同一堵墙。本轮按用户范围只改摘要；是否在 §1.1 补 1–2 句大背景，待用户裁定。

## 六、验证

| 项 | 值 |
|---|---|
| 页数 | **10 页**（不变） |
| 质检 | Errors 0 / Overfull 0 / Underfull 0 / Overfull vbox 0 / `undefined` 5（字体替身警告）/ `??` 0 |
| 表图引用 | **17/17** |
| 浮动体顺序 | 表 1..14、图 1..3（ALL OK） |
| `.tex` | `8fccfab0…`（62,936 B；668 CRLF / 0 裸 LF） |
| 双副本 PDF 字节 | `a720829b…`（2,773,302 B，两处一致） |
| 内容指纹 | `65e29b84…`（poppler 25.07） |
| manifest | `versions/v11/MANIFEST.sha256` 117 条全 OK（相对 v10 恰 3 条变化） |
| 重冻结 | tag `v2026-10-13-abstract-broaden-r13` + 论文 tag `faeco-paper-final-20261013b` |
