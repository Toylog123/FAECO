# FAECO L2 k=1 判别实验报告（2026-09-24）

**定位**：L2 的**最终判别实验**（用户 2026-09-24 裁定，判据在跑之前锁死）。
k=8 三臂（`reports/FAECO_L2_THREEARM_20260924.md`）已证 EMA 在"改枚举顺序"regime 下
无独立贡献；k=1 下权重决定**唯一被验证候选的身份**（而非次序），是 EMA 杠杆最大化的口径。

## 1. 预锁定判据（实验前冻结，不得事后重解释）

| 结果 | 判定 |
|---|---|
| k=1 Adaptive > Fixed（严格多数电路方向一致） | EMA 保留，重定位为 budget-sensitive adaptive selection |
| k=1 Adaptive = Fixed | **EMA 降级**，核心转向 candidate space + weighted ranking + failure attribution |
| k=1 Adaptive < Fixed | EMA 撤出主方法，仅保留为消融/负结果 |

附加机制指标（区分"没改变决策"与"改变决策但无收益"）：
同 `base_netlist_hash` 决策点上 `cut_hash^fixed(t) ≠ cut_hash^adaptive(t)` 的轮数
（`N_rounds where Adaptive selected a different candidate`）。

**不调 ρ/η 做参数搜索**（避免 parameter fishing）；固定 ρ=0.5、η_add=0.5、η_c=0.25。

## 2. 配置

8 电路 × {Fixed, Adaptive} × k=1，其余与 k=8 三臂完全一致：
`--period 0.5 --max-iterations 20 --joint-k 2 --enable-buffer --workers 1 --early-stop
--sta-budget 500`，λ⁰=(1,1,1,1,1)，fixed=`--no-feedback`、adaptive=`--feedback-ema`，
代码基线 `main @ 1a54087`。不跑 Random（k=8 已充分证明现有排序优于随机）。

## 3. 结果

| 电路 | nSTA (fixed→adaptive) | k₁st | 最终 ΔWNS | 身份改变轮数 | 轨迹分叉轮 |
|---|---|---|---|---|---|
| s27 | 43 → 43 | 1 = 1 | 0.100 = 0.100 | **0** | 无 |
| s382 | 170 → 170 | 3 = 3 | 0.220 = 0.220 | **0** | 无 |
| s420 | 378 → 378 | 2 = 2 | 0.970 = 0.970 | **0** | 无 |
| s641 | 230 → 230 | 1 = 1 | 0.640 = 0.640 | **0** | 无 |
| s713 | 99 → 99 | 5 = 5 | 0.130 = 0.130 | **0** | 无 |
| s820 | 102 → 102 | 1 = 1 | 0.020 = 0.020 | **0** | 无 |
| s832 | 73 → 73 | 1 = 1 | 0.090 = 0.090 | **0** | 无 |
| s953 | 76 → 76 | 1 = 1 | 0.110 = 0.110 | **0** | 无 |

**判定：命中预锁定判据第 ② 行——k=1 Adaptive = Fixed（8/8，逐位相同）→ EMA 降级，L2 封板。**

## 4. 机制层结论（比"无收益"更强）

adaptive 臂的 EMA **确实在工作**：s27 17/20 轮、s641 8/20、s953 14/20 推进 EMA，
权重漂移幅度可观（size 1.0→1.50、coverage 1.0→2.00、boundary 至 1.50），
但 **top-1 候选身份在 8 电路 × 最多 20 个决策点上从未改变**（identity_changed=0，
无轨迹分叉，两侧产物逐位一致）。

与 k=8 的观察拼合得到完整机制图景：

- EMA 的加性权重增量（≤η=0.5/轮，clip [1,8]/[0,2]）**低于割评分函数的 top-1 重排阈值**；
- k=8 时只扰动第 2–8 名的深层排序（4 电路 nSTA 变化、终点不变，多花 9%–116% STA）；
- k=1 时只取决于第 1 名 → 完全无差异。

即：**反馈通路（失败→EMA→权重）全通且可观测，但权重增量对"选哪个候选"这一决策
变量在这些基准上无可测杠杆。** 这不是实现问题（0a 等价门 + 轨迹数据双重确认），
是机制在该参数形态下对决策变量不敏感。

## 5. L2 最终裁定（按预锁定判据，正式封板）

- **EMA/failure-driven adaptation 降级为可选机制**（optional adaptive policy），
  不承担性能主张；固定参数下不再做 ρ/η 参数搜索。
- **方法主线收敛为**：Candidate Construction → Weighted Candidate Ranking →
  Failure Attribution → STA/Validation。
  - 候选空间 + 权重排序的价值由 random 臂对照支撑（k₁st 1→123/216/185）；
  - 失败归因（F1–F6 结构化分类）作为搜索诊断机制独立成立；
  - 两者不再与"反馈驱动收敛"捆绑表述。
- 论文表述影响（待用户落笔时执行）：§4.4/§6 中 Failure-Aware 相关主张按上述拆分改写；
  三臂 + k=1 判别作为消融/负结果证据链保留（OI-012 整改的对照实验义务已履行）。

## 6. 执行备注

- s832 首轮双臂 mapping 失败：ABC 子进程在中文用户名临时路径下启动失败
  （`return code -2`，环境性问题、偶发），重跑即成功；不影响结果有效性。
- 产物：`experiments/20260924_l2_k1/{fixed,adaptive}/{circuit}/`，
  判定数据 `experiments/20260924_l2_k1_aggregation/k1_discriminant.json`。
- 工具：`code/scripts/analyze_k1_discriminant.py`（5 项合成 fixture 单测）；
  批次驱动复用 `run_threearm_batch.sh` 新增的 `FAECO_K` 环境变量。
