# 布局后可调预算面积回收：全量重布线物理验收与在线搜索报告

2026-11-20。本报告汇总三项关键推进成果：
1. **ISCAS89 全 8 例真实重布线物理验收 + OpenROAD 原生 `recover_power` 对照 + 全网表 SEC**；
2. **`s382` 在线物理闭环组合搜索（`bounded_search` + `PhysicalEvaluator` + `SPACE_AUDIT`）**；
3. **`b22` 与 `s953` 的转折门隔离 + 续跑二分（Tipping-Gate Isolation + Continued Bisection）**。

## 1. ISCAS89 全 8 例真实重布线物理验收（$B = 10\text{ ps}$）

所有电路均从相同 Resizer `CONTROL` 起点出发，经过 `replace_cell` → `detailed_placement` → 清除信号线 → `pin_access` → `global_route` → `detailed_route -droute_end_iter 15`（全部 `DRC=0`）→ `extract_parasitics` 新生成 SPEF → 独立 `sta` 传播时钟（`set_propagated_clock`）测量，并对全部 6 个有效修改端点完成全网表两态 Yosys SEC（无引脚 tap 显式投影，含转义 DFF）。

| 电路 | 最终策略 | CONTROL 面积 (µm²) | 最终面积 (µm²) | 总面积降幅 | $\Delta\text{WNS}$ (ps) | $\Delta\text{hold}$ (ps) | `NATIVE` (`-recover_power 100`) | SEC |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `s27` | `CONTROL`（0 改） | 193.94 | 193.94 | 0.00% | 0.00 | 0.00 | 0.00% | — |
| `s382` | `RESTORE074` | 1052.26 | 1005.96 | **−4.40%** | −3.10 | +3.58 | 0.00% | PASS (101/0) |
| `s420` | `RECOVERED_V2` | 942.15 | 927.14 | **−1.59%** | −5.70 | +0.00 | 0.00% | PASS |
| `s641` | `RECOVERED_V2` | 1133.59 | 1116.07 | **−1.55%** | −3.88 | −0.50 | 0.00% | PASS |
| `s713` | `RECOVERED_V2` | 1131.08 | 1097.30 | **−2.99%** | −2.94 | +7.17 | 0.00% | PASS |
| `s820` | `CONTROL` 回退 | 1106.06 | 1106.06 | 0.00% | 0.00 | 0.00 | 0.00% | — |
| `s832` | `RECOVERED_V2` | 1167.37 | 1132.34 | **−3.00%** | −8.71 | −4.11 | 0.00% | PASS |
| `s953` | **在线二分隔离 (`14/23`)** | 2433.58 | 2319.72 | **−4.68%** | **+17.26** | −11.31 | 0.00% | PASS |

**核心结论**：
- OpenROAD 原生 `repair_timing -recover_power 100` 在负松弛起点上 **8/8 电路均做 0 次修改（0.00% 回收）**。
- 在严格重布线 + 传播时钟 + 10ps WNS 预算下，**6/8 电路实现 1.55%–4.68% 完整映射单元总面积下降**，全部 `hold > +0.45 ns`（无任何 hold 违例），且 6/6 通过全网表 SEC。
- 固定 SPEF 口径的乐观偏差在 `s820`（−33.63 ps）和 `s953`（−13.30 ps）上被真实重布线检出；在线转折门隔离成功将 `s953` 拉回安全域并额外获得 `+17.26 ps` WNS 改善，而 `s820` 诚实回退至 `CONTROL`。

## 2. `s382` 在线物理闭环组合搜索（`bounded_search` + `PhysicalEvaluator`）

基于新增 [physical_budget_adapter.py](file:///d:/BaiduSyncdisk/01_Papers/03_FAECO/code/src/rseco/physical_budget_adapter.py) 与全库审计 `SPACE_AUDIT.json`（36 个组合逻辑降面积候选），在 `s382` 上执行 14 次在线重布线搜索（`B=10 ps, beam_width=2, max_depth=4`）：
- 发现全库新候选 `rebuffer1 (buf_6 → buf_1)` 与历史动作 `_096_ (nor4_2 → nor4_1)` 的**跨源 Depth-2 组合** `ONLINE_007`：
  - 总面积 `1052.2592 → 1038.4960 µm²`（节省 `13.7632 µm²` / **−1.31%**）；
  - $\Delta\text{WNS} = -7.028\text{ ps}$（单测累加预测为 `−2.865 ps`，实测存在 `−4.163 ps` 非线性耦合）；
  - $\Delta\text{hold} = 0.000\text{ ps}$，`DRC=0`，全网表 SEC **101 proven / 0 unproven**。

## 3. `b22` 转折门隔离 + 续跑二分突破

在 [recover_area.py](file:///d:/BaiduSyncdisk/01_Papers/03_FAECO/code/scripts/recover_area.py) 合入 `parse_named_instances` 全转义识别与 **Tipping-Gate Isolation + Continued Bisection**：
- `b22`（359 处修改，全解析面积 `56892.06 → 66030.83 µm²`）原线性回滚在 `verify_143` 达 600s 超时（0.0%）；
- 新算法仅用 **10 次**验证 STA（9 次二分定位唯一转折门 `_160630_: xor2_4→xor2_1` + 1 次全量续跑），成功回退 **`356 / 359`** 处修改，**回收面积 `3024.15 µm²`（Resizer 净增面积的 33.1%）**，$\Delta\text{WNS} = +0.0011\text{ ns}$。
- 注：`b22` 仍属固定 SPEF 诊断口径（因重布线单次即需十余分钟），但已彻底解除其算法可扩展性瓶颈。
