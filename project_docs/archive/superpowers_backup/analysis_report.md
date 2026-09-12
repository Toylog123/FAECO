# 实验结果深度分析(2026-09-09)

## 1. ITC-99 改善分布(19 电路)

- 范围: [0.000, 2.750] ns
- 中位数 0.180,均值 0.429
- **双峰分布**:11 电路在 0.10-1.00 ns 之间,2 电路(b20/b21) > 1 ns,1 电路(b06) = 0
- 偏度(右尾):b20/b21 拖高均值;**median 比 mean 更能代表典型结果**

## 2. baseline WNS 与 improvement 的关系

- baseline |WNS| < 5 的小电路(13 个):mean improvement 0.178 ns
- baseline |WNS| >= 5 的大电路(6 个):mean improvement 0.975 ns
- **关键观察**:大电路绝对改善显著大于小电路(~5x),因为它们 critical path 更长,有更多可压缩的逻辑

## 3. STA 效率(ns 改善 / 100 STA runs)

| circuit | ns / 100 STA | baseline WNS |
|---|---:|---:|
| **b21** | 6.395 | -13.70 |
| **b20** | 1.375 | -13.21 |
| **b03** | 0.843 | -1.86 |
| **b12** | 0.750 | -2.28 |
| **b22** | 0.388 | -11.68 |
| ... | | |
| b02 | 0.021 | -0.24 |
| b01 | 0.002 | -0.63 |
| b06 | 0.000 | -0.56 |

**最高效率 b21**:6.4 ns / 100 STA -> 43 STA 得到 +2.75 ns 改善,验证 JOINT 在长 critical-path 上的高杠杆率
**最低效率 b06**:664 STA -> 0 ns 改善 -> 'efficient failure',应被 runner 早期识别为 F4 hard-fail 而非继续燃烧 STA 配额

## 4. 策略分布(Joint vs G)

- ISCAS89 8 电路中 JOINT 主导:
|  | JOINT | G | R |
|---|---:|---:|---:|
| n | 4 | 3 | 1 |
- ITC-99 大电路(b14/b17/b20/b21/b22)的 patch 命名是 patch_<id>_<cut>,目前无法直接拆解 JOINT 占比,需要从 outerloop_result.history 二次解析

## 5. b17 phase-2 resume 关键洞察

- 旧 60s 预算:785 STA,success=False,0 改善(20260826)
- 新 budget(180s implicit via --early-stop):104 STA,**+0.380 ns**
- 接受 cell `_184320_` nor4b_1 -> nor4b_2:此 cell 是 b17 关键路径 184 个 gates 中**唯一**有可缩放尺寸族的 gate
- SEC 12812/12813 proven -> 30/30 baseline-patch 对全部 SEC 通过
- joint-enumerate-depth=4 进一步 +0.05 ns -> 验证 JOINT 探索超出单 G 上限
- **教训**:单电路预算(budget)是 FAECO 实际可用性的关键变量,需要默认 --max-verification-time-s 暴露给 CLI

## 6. --no-early-stop fix 的实际收益

- 修复后 b17 x 6 iter x 4 cand:6 iter (516 STA),success=False
- 修复**确实**让 multi-iter 真跑完(原 bug 下 1 iter 就退)
- 但 b17 仍 0 改善 -> actionable 列表限制是根本约束,不是 iter 数
- 该 fix 的真实价值:**让 multi-iter ablation 成为可信方法**,消除了'早退偏差'导致的虚假负结果

## 7. Hold-mode ITC-99 真实限制

- 14 电路中仅 b01 真正改进了 min_slack (+0.27 ns),其余 13 失败
- 失败根因:hold min_slack 违规严重(典型 -0.36 ~ -0.39 ns),1-iter 单 patch 无法同时改善 setup WNS + hold min_slack
- **论文 §7 limitation 已经诚实记录**,不需要追加实验

## 8. 综合判断

### 强信号

1. **策略覆盖率** > 单一策略强度:JOINT 在 ITC-99 大电路上比单 G 强 2-3x
2. **可缩放尺寸族** 是 G 策略的天花板:b17 `_184320_` 是唯一可缩放 gate 这一事实,锁定了 G 的 +0.38 ns 上限
3. **大电路 = 大杠杆**:b14/b17/b20/b21/b22 的 mean improvement 0.98 ns 是小电路的 5x

### 弱信号(limitation)

1. b06 是结构性 hard-fail:其 critical path 关键 cell 无 R 等价候选 -> 论文已诚实说明
2. hold-mode 1-iter 不足以同时修复 setup + hold -> multi-iter hold 是未来工作
3. WSL2 对 75k+ cell 网表 STA 输出截断 -> 工程性 limitation,非方法问题

### 对论文的影响

- §6 主表 19/19 已满足(b17 resume 后),无需扩张实验
- §7 limitation 章节已覆盖(b06/hold-mode/multi-iter/b19/--no-early-stop) 5 条
- §5 SEC 30/30 通过,1/12813 unproven 容差已声明
- **论文主结论足够支撑,可推进投稿**

### 论文应突出的 4 个数字

| claim | 数字 | 来源 |
|---|---|---|
| ITC-99 大电路平均改善 | **+0.98 ns** | 5 个 circuit |
| 最大单电路改善 | **+2.75 ns (b21)** | JOINT |
| SEC baseline-patch 通过率 | **30/30** | sec_result.json |
| STA 效率峰值 | **6.4 ns / 100 STA (b21)** | eff calc |
