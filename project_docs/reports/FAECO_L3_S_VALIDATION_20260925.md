# FAECO-v2 L3 S（窗口局部结构重综合）实现与验证（2026-09-25）

> 对应 r2 技术设计 §4–§5；实现契约 §8.12。
> 目标：把 S 从"设计"推进到"可跑、可判、有证据"——先在真实工具链上打通状态机，
> 再回答"窗口局部重综合到底能不能带来 WNS 收益"。

---

## 0. 一句话结论

**S 的机制成立、门的判据成立，但收益稀疏且很小。**
在 3 个电路上按端点锥枚举窗口：s641 **命中一个被接受候选**（ΔL=1、ΔWNS=+0.03 ns、
ΔTNS=+0.01、CEC-1/CEC-2 双闭合、全网表结构自检通过、逐次复跑逐位相同）；
s382 / s713 **无被接受候选**。原因是**结构深度下降大多落在非时序关键锥上**——
对 WNS 无感；即使落到关键锥（s641），收益也只有 0.03 ns。

---

## 1. 交付物

| 文件 | 内容 |
|---|---|
| `code/src/rseco/structure_resynthesis.py` | S 全部实现：§5.1 数据结构、§5.2 确定性命名、§5.3 状态机、§4.7 归因标签、§4.4 R_S 双阈值、§5.4 真实工具绑定 |
| `code/tests/test_structure_resynthesis.py` | 22 项单测（§5.5 八项 + 6 项本轮新增缺陷回归 + 状态机归因 + canonical hash） |
| `scratch/probe_l3_smoke.py` | 单窗口端到端冒烟（s27 关键路径窗） |
| `scratch/probe_l3_hunt.py` | 窗口猎取：真实电路端点锥上的深度收益扫描 |
| `scratch/probe_l3_accept.py` | **验收扫描**：逐窗口 graft → 真实 STA → ΔL / ΔWNS / ΔTNS |

回归：`477 passed / 4 skipped / 156 subtests passed`（本轮 L3 贡献 +22 项）。

---

## 2. 真实工具链上打通的 7 个缺陷（本轮主要工程量）

S 最危险的是 grafting，但实际把状态机跑到"能出候选"的障碍全在**工具接线**。
以下每个缺陷都会让候选被**误拒**（假阴性），且都在真实 Yosys/ABC/OpenSTA 上复现：

| # | 症状 | 根因 | 处置 |
|---|---|---|---|
| 1 | `F1`（CEC_PRE 失败），日志 `Networks have different number of primary inputs` / `design has 3 root-level modules` | CEC 归一化未传 top module → `flatten` 变空操作，展开后的 SKY130 单元模型模块残留成额外 BLIF 根，ABC miter 计算失败 | 新增 `blif_or_verilog_top()`，CEC 两侧按模块名显式 `hierarchy -check -top` 后再 `flatten` |
| 2 | `S_TECHMAP_MISMATCH`，日志 `Cannot find the model for subcircuit $shr` | `read_blif` 产生的是 `$lut` 单元，ABC 抽取到 **0 gates**（"nothing to map"）→ `abc -liberty` 实际未映射，输出仍是行为级 `4'h1 >> {...}` 移位 | `techmap` 放在 `abc -liberty` 之前（`Using extmapper simplemap for cells of type $lut`） |
| 3 | `W_LIB_OUT_OF_SET` | `_extract_liberty_cells` 返回的是 Liberty 原始 token（`cell ("NAME")` → 含双引号），成员判定永远不命中 | 在 S 内**局部**去引号；**不动**已被验证的共享函数（避免扰动等价门基线） |
| 4 | `depth_before` 恒为 0 | ABC 未 strash 前 `print_stats` 报的是 `nd = N`（节点）而非 `and = N`，`_parse_abc_stats` 只认后者 → "before" 行被丢弃 | 新增 `abc_stats_rows()`，同时接受 `and` / `nd` |
| 5 | `depth_after_sky130` 为 `None` | `ltp -noff` 的 `length=N` 被 `-q` 抑制；且未读单元模型时 `ltp` 数不到单元内部层级 | 去掉 `-q`；读入 `sky130_cells_v2.v` + `flatten` 后再 `ltp`（得到真正的弧级深度） |
| 6 | 所有候选被 `W_STRUCT_ERROR` 拒；窗口输出漏掉馈入触发器的网 | `parse_mapped_netlist` 只匹配 `sky130_fd_sc_hd__*`，而 FAECO 宿主网表用本地 `dff` 包装模块（包一颗 `dfxtp`）→ 触发器既不被计为驱动源（假悬空），也不被计为窗口外部消费者（**窗口输出丢失 → graft 会删掉活跃宿主网的唯一驱动**） | 新增宽松宿主解析 `host_cells()` + `dff`→`dfxtp` 映射（使 `is_dff` 与 `_is_forbidden` 穿透包装） |
| 7 | 窗口输出集合本身算错（被 `boundary_outputs` 兜底掩盖） | `extract_window` 用"被外部驱动"的网判断窗口输出，语义应为"**被外部消费**"的网 | 改为 `_sink_nets`（外部消费者），并新增 `extraction_report["boundary_outputs_extended"]` 记录被自动补齐的边界输出 |

缺陷 6/7 有专门回归测试（旧代码必失败）：`test_host_cells_include_wrapper_flops`、
`test_wrapper_flop_sink_forces_window_output`、`test_structure_check_sees_wrapper_flop_driver`。

> 教训：**"假阴性"比"假阳性"更难发现**——它们表现为"没有候选"，而不是"错误候选"。
> 本轮每一个都是靠"候选数=0"逐步回推日志才定位的。

---

## 3. 状态机端到端证据

s27 关键路径窗（`_08_`/`_11_`，2 个组合单元，2 个输出）：

```
EXTRACT → EMIT → RESYNTH(S0/S1/S2) → CEC_PRE ✅ → TECHMAP ✅
        → CEC_POST ✅ → RATIO ✅(R_S=1.00) → DEDUP ✅ → GRAFT ✅ → STRUCT ✅
candidates=1  variant=S0  aig 20→5  blif depth 7→3  sky130 depth 6→6
```

- S1/S2 在该窗上映射结果与 S0 逐位相同 → 被 DEDUP 丢弃（**是 DROP 不是 FAILURE**，
  归因统计未被污染，符合 §4.7）。
- `boundary_outputs_extended` 正确报出被自动补齐的 `G10`（馈入 `DFF_0` 的网）。

---

## 4. 窗口收益扫描（结构层）

`s382` 端点锥（每个触发器 D 网一个窗口，上限 40 门）：

| root | 门数 | R_S | SKY130 深度 | 整网表 ltp |
|---|---|---|---|---|
| C3_Q2VD | 10 | 1.00 | 13→12 | **13→12** |
| C3_Q3VD | 9 | 1.11 | 12→12 | **13→12** |
| TCOMB_GA1 | 6 | 1.00 | 9→8 | 13→13 |
| DFF_16 的 UC_19VD | 7 | 1.14 | 11→9 | 13→13 |
| 其余 17 窗 | 2–13 | 0.88–1.14 | 不变 | 13→13 |

**窗口局部深度下降很常见，整网表深度下降很罕见**（21 窗中仅 2 个）。这一层差异本身
就是"局部优化未必命中全局关键路径"的直接证据。

---

## 5. 验收扫描：ΔL 与 ΔWNS（真实 OpenSTA）

方法：逐窗口跑 S → graft → 写网表 → **与基线同一条 STA 命令**测 WNS/TNS，
`ΔL` 取整网表 `ltp -noff`（层=SKY130，含单元模型展开）。按"覆盖关键实例数"降序尝试，
取**首个 ΔL>0 且 ΔWNS>0** 者为 ACCEPT（对齐 loop 的 accept-first-improvement 纪律）。

| 电路 | 基线 WNS | 基线 TNS | 基线 ltp | 试窗数 | 有候选 | ΔL>0 | **被接受** |
|---|---|---|---|---|---|---|---|
| s382 | −0.98 | −12.74 | 13 | 21 | 21 | 2 | **无**（最佳 ΔWNS=+0.01，但 ΔL=0） |
| s713 | −1.33 | −18.69 | 28 | 19 | 17 | 3 | **无**（ΔL>0 的 3 窗 ΔWNS 全为负：−0.27/−0.46/−0.34） |
| s641 | −1.63 | −20.77 | 28 | 3 | 3 | 2 | **✅ 命中** |

**s641 命中详情**（窗口 `DFF_13`，root=`G127`，29 门，R_S=1.00）：

| 指标 | 基线 | 候选 | Δ |
|---|---|---|---|
| WNS (ns) | −1.63 | −1.60 | **+0.03** |
| TNS (ns) | −20.77 | −20.76 | **+0.01** |
| 整网表 ltp 层 | 28 | 27 | **+1** |

有效性核对：
- 候选网表与基线**确实不同**（`cand_DFF_13.v` 相对基线 51–71 行差异），
  不是"空操作"导致的 ΔWNS=0。
- **CEC-1（原始窗 ≡ 重综合窗）与 CEC-2（原始窗 ≡ 映射后窗）双通过** → 形式等价。
- **全网表 `structure_check` 通过**（r2 §5.3 硬约束 #2）→ 无 graft 接错网。
- **逐次复跑逐位相同**（同窗口重跑 WNS/TNS/ΔL 完全一致）→ 满足 §5.2 确定性。

**负结果同样要记**：s713 上"结构变浅但更慢"的窗口有 3 个（ΔL=+2/+3 却 ΔWNS=−0.46/−0.27/−0.34），
说明 `resyn2` 系列的深度收缩会**牺牲关键路径上的实际延迟**（更深不一定更慢、更浅不一定更快，
结构深度与时序延迟在单元负载/驱动强度层面不同向）。

---

## 6. 判读

1. **机制成立**：S 能在真实工具链上产出**形式等价 + 结构完整**的新候选类型，
   并至少在一个电路上被"ΔL<0 且 ΔWNS>0"的判据接受。§5.5 的 L3 gate 达成。
2. **收益稀疏**：命中率 1/3 电路，幅度 +0.03 ns（约违例深度的 2%）。
   s382/s713 全部落在"结构变浅但不影响 WNS"，或"结构变浅但更慢"。
3. **原因明确**：
   - 端点锥的**结构深度**下降大多发生在非时序关键锥上；
   - 在最关键的锥上，`resyn2/resub` 常常**已经无深度可压**
     （s382 的关键端点窗 12→12；s713 的 28→25 但 ΔWNS 为负）。
4. **与 L2 的呼应**：L2 的结论是"反馈权重的杠杆不足"；L3 的表征是"候选空间的
   局部深化收益有限"。二者共同指向同一件事——**在单窗、小窗、`resyn2` 族这一 regime 下，
   增量主要来自候选排序与验证纪律，而非新的搜索维度**。
5. **本扫描是下界，不是结论**：它是**代理实验**（仅端点锥、单次 graft、无多轮再分析、
   无 R/G/B 组合、无 `weighted_cut_candidates` 的时序加权选窗）。集成进 loop 后的
   正式口径仍需实测（见 §7）。

---

## 7. 下一步（施工顺序不变：先方案，后论文）

1. **把 S 接入 loop**（r2 §4.9）：S 作为独立候选类型，受 `candidates_per_iteration` 约束；
   至多加一档 `S→G`（仅对同窗口输出锥内新实例做一次 G 寻优）。
   **不改** L2 已封板的反馈通路。
2. **正式口径实验**：8 个 ISCAS89 电路 × {S 开, S 关}，k=8、20 轮，与 L2 三臂同一批次配置；
   比较最终 ΔWNS / k₁st / max B(k)。
3. **按结果决定 S 的论文定位**：
   - 若 S 开显著优于 S 关 → S 作为独立贡献写入 §4/§5，并把本轮"选窗粒度"教训写进设计；
   - 若与代理扫描一致（增益稀疏）→ **如实降级**：S 记为"可选候选类型"，
     主贡献回到"候选构造 + 加权排序 + 失败归因（诊断）+ STA 验证"这条主线
     （与 L2 封板结论合并叙述）。
4. **论文改动一律等上述定案后一次性进行**，本轮未触碰任何 `.tex`。

---

## 8. 复现命令

```bash
# 单测
.venv/Scripts/python.exe -m pytest code/tests/test_structure_resynthesis.py -q

# 单窗口端到端（s27）
.venv/Scripts/python.exe scratch/probe_l3_smoke.py

# 窗口收益扫描
.venv/Scripts/python.exe scratch/probe_l3_hunt.py s382 30 8

# 验收扫描（真实 STA；命中 s641 DFF_13）
.venv/Scripts/python.exe scratch/probe_l3_accept.py s641 40
.venv/Scripts/python.exe scratch/probe_l3_accept.py s382 40
.venv/Scripts/python.exe scratch/probe_l3_accept.py s713 40
```

环境：原生 OSS-CAD Yosys `0.67+146`（`C:\oss-cad-suite-build\oss-cad-suite\bin`
需同时加 `bin` 与 `lib` 进 PATH）+ WSL OpenSTA（`wsl-sta`）。
