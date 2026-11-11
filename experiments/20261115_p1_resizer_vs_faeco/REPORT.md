# P1：FAECO-P（布局后覆盖优先）vs OpenROAD resizer

> 状态：进行中（2026-11-11）。本文件在**看到 F 臂端点读数之前**已写好骨架，读数在 §3 填入。
> 预注册：`PREREGISTRATION.md`（§3 判据、§7 A1/A2 运行期修订）。

## 1. 问题

路线图（`project_docs/FAECO_ROADMAP.md`）的 P1 要回答的唯一问题：

> 在同一份 W1 映射网表、同一 period、同一布局利用率与密度下，
> **FAECO-P（预布局判据 + 布局集成判决 + 覆盖优先调度）拿到的布线后 WNS，
> 是否优于 OpenROAD 内置 resizer（`repair_timing -setup`）？**

判据（预注册，未改）：**≥5/8 电路三布局均值 WNS 优于 resizer，且均值差 ≥0.05 ns** 才算晋级。

## 2. 装置

| 项 | 设定 |
|---|---|
| 电路 | ISCAS89 序贯 s27 / s382 / s420 / s641 / s713 / s820 / s832 / s953 |
| period | 0.50 ns |
| 输入网表 | `experiments/20261016_r22_cut_ablation_v3/W1/<c>/mapped.v`（同一份，全部臂共用） |
| 布局 | util 0.30 / 0.35 / 0.40，density 0.55，aspect 1.0，`sky130hd` |
| 读数组 | 每布局一条，取三布局算术均值 |
| 读数工具 | `rseco.routed_sta`：floorplan→place→CTS→global+detailed route→`extract_parasitics`(rcx)→SPEF→独立 `sta`，理想时钟 |

**三条臂**

| 臂 | 定义 | 读数流程 |
|---|---|---|
| `base` | 未做 ECO 的 W1 网表 | 标准流程 |
| `faecop` | FAECO-P：`--physical-gate --physical-backend placed_ens --placement-utils 0.30,0.35,0.40`，单补丁接受，20 轮 / 500 STA 预算 | 标准流程（对 ECO 后网表重跑布局布线） |
| `resizer` | OpenROAD `repair_timing -setup` + `detailed_placement` | **该臂自己的流程**（标准流程 + repair） |

两臂流程不对称（resizer 臂多一步 repair）是**该臂的定义**，不是漏洞；STA 约定、库、period、util、density 完全一致，读数可比。此不对称在 §5 边界中再次声明。

## 3. 读数（布线后 WNS，ns，三布局均值）

| 电路 | base | resizer | FAECO-P | F−base | F−R | 判定 |
|---|---|---|---|---|---|---|
| s27  | −0.3460 | **−0.2222** | −0.2573 | +0.0887 | −0.0351 | worse |
| s382 | −1.1742 | **−0.8414** | −0.9962 | +0.1780 | −0.1548 | worse |
| s420 | −1.8939 | **−1.1913** | −1.4295 | +0.4643 | −0.2383 | worse |
| s641 | −2.5673 | **−1.1295** | −1.6580 | +0.9093 | −0.5285 | worse |
| s713 | −1.7285 | **−1.2526** | −1.6865 | +0.0420 | −0.4339 | worse |
| s820 | −1.7219 | **−1.2691** | −1.5786 | +0.1433 | −0.3095 | worse |
| s832 | −1.6552 | **−1.0587** | −1.6421 | +0.0131 | −0.5834 | worse |
| s953 | −1.8305 | **−1.2841** | −1.6907 | +0.1399 | −0.4065 | worse |
| **均值** | — | — | — | **+0.2473** | **−0.3362** | 0/8 胜 |

（负的 WNS 越小越差；`F−R > 0` 才表示 FAECO-P 更好。）

**接受动作数**：FAECO-P 在 8 例上共接受 **16** 个补丁（s27 1 / s382 2 / s420 3 / s641 1 / s713 2 / s820 3 / s832 1 / s953 3），全部为 R/G/B 单实例动作。

**动作量的直接对照**（布线后 DEF 的逻辑单元数，剔除 tap/fill/decap）：

| 电路 | base | resizer | FAECO-P | resizer 净增 | FAECO-P 净增 |
|---|---|---|---|---|---|
| s382 | 94 | 102 | 94 | **+8** | 0 |
| s641 | 126 | 135 | 126 | **+9** | 0 |
| s832 | 149 | 162 | 149 | **+13** | 0 |
| s953 | 236 | 274 | 237 | **+38** | +1 |

⇒ resizer 一次调用会**插入 8–38 个缓冲并大量改尺寸**，FAECO-P 全程只改 **1–3 个门**。

## 4. 判定

**判定：H1 双条件均 FAIL —— 0/8 电路优于 resizer，均值差 −0.3362 ns（门槛 +0.05）。PROMOTE = NO。**

- 逐例差全部为负，范围 −0.0351（s27）到 −0.5834（s832），符号检验单侧 p = 1.0（完全没有正向迹象）。
- 把读数拆成两段看：**FAECO-P 相对 base 是净改善的**（均值 **+0.2473 ns**，8/8 例都为正，`F−base` 列），说明机制本身有效；
  但 **resizer 相对 base 是 +0.5836 ns**，是它的 **2.36 倍**。
- 差距的来源不是判据而是**动作量**：resizer 在 s382/s641/s832/s953 上分别净增 **8/9/13/38** 个逻辑单元（外加大量改尺寸），
  FAECO-P 全程只接受 16 个单实例补丁、净增 0–1 个单元。这与本文主线的既有结论一致：
  **收益来自覆盖（动作数量），而不是权重或规模** —— resizer 恰恰是「覆盖」这一侧的上限演示。
- 代价也不利：FAECO-P 每个候选要做 3 次布局（placed_ens）才能判一次，而 resizer 是单次全局 LR 求解。
  ⇒ **P1 这条「以更聪明的判决赢过 resizer」的路线被明确证伪**，不是噪声、不是调参空间问题。

## 5. 边界与读法

1. **流程不对称**：resizer 臂的读数来自「标准流程 + `repair_timing` + `detailed_placement`」这条流程，FAECO-P/base 来自标准流程。两臂的 ECO 动作不同、后续物理流程因此也不同，这是被比较对象的定义差异，但**不是**同一流程下的公平 A/B；引用时必须带这句。
2. **只覆盖 8 个小规模 ISCAS89 序贯电路**（63–400 单元），不能外推到大规模设计；resizer 的全局 LR 求解在小电路上天然吃香（连通性简单、可解性高）。
3. **单次布局**：每臂 3 个利用率，不是多种子；同一 util 的布局由 OpenROAD 决定，随机性小但没有种子重复，故**布局离散未被平均掉**（已知量级 0.05–0.10 ns）。
4. **resizer 臂的参数是默认值**（`repair_timing -setup` 全默认），没有做调参；「打赢默认配置」不等于「打赢这个方法」。
5. **FAECO-P 的动作集**：R（等价改写）+ G（门尺寸）+ B（缓冲插入）+ JOINT（2 实例联合），每轮只接受 1 个补丁；resizer 一次调用会插入/改尺寸很多单元 —— 这是**动作粒度**的差别，也是本文主线（覆盖优先 vs 权重/规模）在布局后的延续。

## 6. 复现

```bash
cd <repo>
export PATH="/c/Windows/System32:/c/oss-cad-suite-build/oss-cad-suite/bin:/c/oss-cad-suite-build/oss-cad-suite/lib:$PATH"
export MSYS_NO_PATHCONV=1 PYTHONUTF8=1

bash experiments/20261115_p1_resizer_vs_faeco/run_resizer.sh              # 8 例 resizer（3 个 util 各一次）
bash experiments/20261115_p1_resizer_vs_faeco/run_faecop.sh               # 8 例 FAECO-P
.venv/Scripts/python.exe experiments/20261115_p1_resizer_vs_faeco/run_endpoints.py --arms base,faecop --workers 2
.venv/Scripts/python.exe experiments/20261115_p1_resizer_vs_faeco/analyze.py
```

产物：
- `arms/Resizer{,_u0.30,_u0.40}/<c>/result.json`（resizer 自有流程读数）
- `arms/FAECO-P/<c>/outerloop_result.json`、`eval_trials.json`
- `endpoint{,_u0.30,_u0.40}/<c>/arm{base,faecop}/result.json`
- `summary.json`（`analyze.py` 输出）

## 4b. Hybrid 组合臂（事后追加，2026-11-11 下午）

**问题**：既然「用更聪明的判决赢 resizer」已被 §4 证伪，唯一还剩的公平问法是**可组合性**——
同一 resizer 流程、**只把起始网表换成 FAECO-P 的终点网表**，我们的 ECO 是否让 resizer 的终点更好？
这是同工具、同流程、只差起始网表的 A/B，不涉及流程不对称。

**判据**（读数前写定，沿用 P1 门）：Hybrid 在 **≥5/8** 电路上优于 resizer **且** 三布局均值差 **≥+0.05 ns**。
两条件都要满足才算晋级；条件本身是事后追加的（P1 判定后才提出该臂），须随结论一起报。

**结果（三布局均值，ns；WNS 越不负越好）**：

| 电路 | resizer | Hybrid | H−R |
|---|---|---|---|
| s27 | -0.2222 | -0.2347 | -0.0125 |
| s382 | -0.8414 | -0.7904 | +0.0510 |
| s420 | -1.1913 | -1.1771 | +0.0142 |
| s641 | -1.1295 | -1.1510 | -0.0214 |
| s713 | -1.2526 | -1.2514 | +0.0012 |
| s820 | -1.2691 | -1.1132 | +0.1559 |
| s832 | -1.0587 | -1.1210 | -0.0623 |
| s953 | -1.2841 | -1.2161 | +0.0680 |

- **胜 5/8**（s382、s420、s713、s820、s953；负 s27、s641、s832），**均值差 +0.0243 ns**。
- **判定：H1 FAIL** —— 胜场达标（5/8）但均值差 +0.0243 未达 +0.05 ns 门槛 ⇒ **PROMOTE = NO**。
- 读法：Hybrid 的增益集中在 s820（+0.1559）与 s953（+0.0680），但在 s27（−0.0125）、s641（−0.0215）、
  s832（−0.0623）反而更差；量级与已知布局离散（0.05–0.10 ns）同阶 ⇒ **不能宣称组合收益**。
  另须注意 Hybrid 相对 resizer 多跑了我们的一次搜索（成本更高），也是不利项。
- **结论**：可组合性同样未兑现。P1 及其组合臂至此封口；若继续本路线，必须换题
  （例如把「覆盖」改成"预算内循环调用 resizer 并按我们的判据验收"这类**调度**问题），见 roadmap §7。
