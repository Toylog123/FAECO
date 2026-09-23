# 代码—论文对照审计：失效反馈机制（2026-09-23）

> 触发：用户追问"学习是什么 / 加权最小割是否落后"，核查反馈机制的实际实现时发现论文表述与代码不一致。
> 结论：**三处差异，已全部修正论文表述（不改代码、不改任何实验数字）**。
> 关联未决问题：`project_docs/OPEN_ISSUES.md` OI-008；日志：`project_docs/LOGS.md` LOG-20260923-02。

## 1. 对照方法

| 项 | 内容 |
|---|---|
| 论文侧 | `manuscript/FAECO_面向预布局门级时序ECO的失效驱动候选搜索.tex` §3.3 式(2) 与符号表（表 2）、§3.4 正文与表 `tab:failures` |
| 代码侧 | `code/src/rseco/refinement.py:refine_weights`（F1–F6 反馈的**唯一**实现，被 `flow.py:126` 与 `refinement_loop.py:81` 调用）；`code/src/rseco/cut.py:166–199`（节点代价构造） |
| 历史侧 | `git show 216a118:src/rseco/refinement.py`（引入 F6 的提交，"评审缺陷1/2/4 双目标联合割 + 物理感知内环F6"） |
| 实测侧 | `experiments/20260826_itc99_main/b*/b*/eval_trials.json`（19 电路 / 4044 trials），探针 `scratch/count_failures.py` |

## 2. 实测失败事件分布（权威口径）

| 产物事件名 | 次数 | 现行 `FailureType`（`failures.py`） |
|---|---:|---|
| `acceptance_budget_violation` | 2434 | **F4** `F4_timing_gain_insufficient`（`failures.py:47`，判定"未满足接受判据"）——**旧版事件名** |
| `F5_verification_too_expensive` | 915 | F5 |
| `F1_equivalence_failure` | 138 | F1 |
| `F3_patch_too_large` | 16 | F3 |
| `F2_boundary_invalid` | 3 | F2 |
| `F6_physical_load_failure` | 0 | F6（仅物理门控实验触发） |

**推论**：F4 类事件占 2434/4044 ≈ 60%，与论文 §3.4 "真实 WNS 主循环主要由 F4 驱动"相符；产物事件名与现行代码字符串不同，但判定条件一致，故**所有已发表数字不受影响**。主实验未见 F6（与"F6 仅物理门控实验触发"一致）。

## 3. 三处差异与处置

### 差异 1：F1 反馈动作漏写扇出权重（实质遗漏）

| | 内容 |
|---|---|
| 论文（修正前） | 表 `tab:failures` F1 行："增加边界惩罚 $\lambda_b$，降低此类节点被选作候选边界的概率" |
| 代码（现行与 216a118 一致） | `boundary_penalty += 1.0` **且** `equivalence_stability_reward += 1.0` |
| 影响面 | F1 主实验实测触发 **138 次**，故该动作**实际生效**，非纯表述问题 |
| 处置 | 论文表 F1 行与 §3.4 正文补入"扇出权重 $\lambda_f$" |

符号对应关系：代码 `equivalence_stability_reward` ≡ 式(2) 中的 $\lambda_f$（扇出权重），在 `cut.py:185` 以 `equivalence_stability_reward * 0.1 * fanouts[gate]` 进入节点代价。

### 差异 2：F6 反馈动作多写尺寸惩罚（过度声称）

| | 内容 |
|---|---|
| 论文（修正前） | 表 `tab:failures` F6 行与 §3.4 正文："增加边界惩罚 $\lambda_b$ **与尺寸惩罚 $\lambda_s$**" |
| 代码 | 仅 `boundary_penalty += 1.0`（`actions: increase_boundary_penalty_physical`） |
| 溯源 | `git show 216a118:src/rseco/refinement.py` 显示引入 F6 时即为"仅增 λ_b"，**从未实现过 λ_s 增量**；排除"重构后丢失"的可能 |
| 处置 | 论文删除 $\lambda_s$ 表述（两处） |

### 差异 3：$\lambda_c$ 参与节点代价的方式表述不完整

| | 内容 |
|---|---|
| 论文（修正前） | 符号表（表 2）与 §3.3 正文："$\lambda_c$ 用于关键路径覆盖候选的反馈，**不直接进入**式(2)" |
| 代码 | ① 覆盖割排序：`cut.py:270/291` 使用（论文表述成立）；② **另**作为节点代价分母的深度折扣：`cut.py:193` `critical_divisor = 1 + λ_c·depth/max_depth`（仅 `r_ok` 门） |
| 处置 | 式(2) 补归一化分母项与指示函数；符号表、图 2 注、§3.3 正文统一改为"以折扣形式进入" |

同时补入代码中存在但论文未述的一处**门控设计**：扇出项与分母折扣均以 $\mathbb{1}[v\in\mathcal{R}]$ 门控（`cut.py:188–194`）——无 R 等价候选的门两项同时免除，避免 F4 折扣把不可重写的门推入候选边界而触发 F1。这是"功能约束硬编码入图"的具体实现，属论文应披露的设计点。

## 4. 修改清单（论文 8 处）

| # | 位置 | 修改 |
|---|---|---|
| 1 | 表 2 符号表（$C_c$ 行） | "$\lambda_c$ 仅用于反馈" → "$\lambda_c$ 用于覆盖排序与节点代价深度折扣" |
| 2 | 表 2 符号表（权重行） | 补明 $\lambda_c$ 进入归一化分母 |
| 3 | 图 2 注 | "$\lambda_c$ 反馈处理" → "$\lambda_c$ 的深度折扣及排序反馈处理" |
| 4 | §3.3 正文首段 | 改为"按 $\lambda_c$ 对具备 R 等价候选的门施加深度折扣"；"覆盖奖励降低" → "覆盖折扣与扇出代价同时失效" |
| 5 | §3.3 式(2) | 补归一化分母 $1+\lambda_c\mathbb{1}[v\in\mathcal{R}]\mathrm{depth}(v)/\mathrm{depth}_{\max}$ 与扇出项的指示函数门控 |
| 6 | §3.3 式(2) 说明 | 补 $\mathcal{R}$、$\mathbb{1}[\cdot]$、$\mathrm{depth}_{\max}$ 定义与门控理由；$\lambda_c$ 表述统一 |
| 7 | §3.4 正文 | F1 补 $\lambda_f$；F6 删 $\lambda_s$；F4 措辞由"关键覆盖奖励"统一为"关键路径深度折扣" |
| 8 | 表 `tab:failures` F1/F6 行 | 同步正文 |

**未改动**：任何实验数字、图表数据、SEC 结论、摘要、结论；`code/` 未改动。

## 5. 验证

- 编译：LuaLaTeX 两遍，**0 Error / 0 Overfull / 引用未定义 0**，**9 页**（篇幅未变）。PDF 两处（`paper/zh/manuscript/` 与 `paper/zh/`）SHA256 一致 `034ea72a…`，2,752,947 bytes。
- 编译日志中 5 处 `Font shape ... undefined` 为**字体形状警告**（方正 GBK 商业字库缺失、以系统字体近似所致，见 tex 文件头说明），**非引用问题**；`Reference/Citation ... undefined` 计数为 0。
- 口径复扫（修改后旧表述清零）：`不直接进入` 0 处、`仅用于反馈` 0 处、`关键覆盖奖励` 0 处、`F1/F2 增大` 0 处、`与尺寸惩罚` 0 处；新表述（指示函数 $\mathbb{1}$ / 扇出权重 $\lambda_f$）共 4 处命中。
- 数字对账：本轮未触及任何数字、图表与摘要，`20260826_aggregation/summary.json` 口径不变。
- 术语表核对：`docs/GLOSSARY.md` 的 F1–F6 条目（"六类失效反馈：结构等价、边界、尺寸、时序收益、验证超时、SPEF 复测失败"）描述仍准确，无需同步修改。

## 6. 遗留

- 产物事件名 `acceptance_budget_violation` 与现行 `F4_timing_gain_insufficient` 字符串不一致（语义一致）。投稿前建议在补充材料或代码可用性说明中交代，避免审稿人对照代码时困惑。
- F1 反馈动作虽然生效，但**其独立贡献未被隔离验证**（现有消融同时改变候选空间与反馈配置，论文已如实声明）。改进方向见 `project_docs/OPEN_ISSUES.md` OI-008 与后续设计空间讨论。
