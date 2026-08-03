# FAECO 方法符号表与算法骨架（Draft 1）

更新时间：2026-07-31

本文档是 N05（方法重写就绪审计）的下游交付物，基于 `docs/paper_audit/method_rewrite_readiness.md` 的 18 项要素审计结果，按 Stage A + Stage B 当前 ready / partial 状态给出 FAECO 方法的符号定义、算法骨架与约束边界。本文档尚未经用户最终审定，结构和措辞仅作为 N05 方法正文的起点，禁止作为论文主表事实性表述。

## 1. 总体符号表

| 符号 | 类型 | 当前定义 | 实现入口 |
|---|---|---|---|
| G = (V, E) | 有向图 | 门级网图，顶点为 gate/port，边为 signal wire | `src/rseco/netlist.py` `build_graph` |
| C(G, t) ⊆ V | 子图 | target output `t` 的 fanin cone | `src/rseco/graph.py` `extract_cone` |
| K(G, t) = (V_K, E_K) | 切图 | 把 cone 内每个 gate 拆成 `gate:in -> gate:out` 的 split graph | `src/rseco/cut.py` `build_weighted_cut_graph` |
| cost(v) ∈ ℝ≥0 | 权重 | 每个 gate 的节点代价，与 critical-path / level / size 联动 | `src/rseco/cut.py` `_node_cost` |
| (S, T, E_split, E_dep) | 4 元组 | s-t split 图：S = source、 T = sink、 E_split 容量边、 E_dep 依赖边 | `src/rseco/cut.py` `build_weighted_cut_graph` |
| Cut(S, T) | 边集 | 把 S 与 T 分开的 cut edges | `src/rseco/cut.py` `solve_weighted_cut` |
| patch = (gates, boundary, size) | patch 表示 | selected gates 列表、boundary ports、size | `src/rseco/patch.py` `Patch` dataclass |
| score(patch) ∈ ℝ | 评分 | timing gain + size + boundary + verification + equivalence penalty | `src/rseco/ranking.py` `score` |
| F1-F5 | 失败类型枚举 | 等价失败 / 边界失败 / size 过大 / timing 收益不足 / 验证超时 | `src/rseco/failures.py` `FailureKind` |
| metric M | 实验指标 | 包含 `patch_size` `score` `equivalence_result` `formal_equivalence_result` `abc_baseline_status` `runtime_total` `runtime_breakdown` `runtime` (structured schema) `toolchain_snapshot` | `src/rseco/metrics.py` + `src/rseco/flow.py` |
| mapping_N22_mapped.v | mapped Verilog | Yosys `synth -noabc + abc -liberty` 输出 | `src/rseco/technology_mapping.py` |
| mapping_N22_mapped.blif | mapped BLIF | Yosys `write_blif` 输出 | `src/rseco/technology_mapping.py` |
| N_normalized.blif | reference BLIF | Yosys `proc; flatten; opt; simplemap; clean; write_blif` 输出 | `src/rseco/yosys_abc.py` `_normalize_to_blif` |
| cec_log | formal log | ABC `cec <ref.blif> <mapped.blif>` 输出 | `src/rseco/yosys_abc.py` `_run_abc_cec` |
| wns, tns, slack, slack_status | STA 指标 | OpenSTA `report_checks` / `report_worst_slack` 输出 | `src/rseco/opensta.py` `parse_sta_report` |

## 2. 总体算法骨架

FAECO 的总体流程（Stage A + Stage B 当前实现）：

```
1.   input: original netlist (Verilog), resynthesized netlist (Verilog),
          target output t
2.   normalize:      Yosys 规范化 original → N_normalized.blif (Stage A reference)
                    Yosys `synth -top t -noabc + abc -liberty <lib>` → mapped.blif
                                            (Stage B technology mapping)
3.   cone:           C(G, t) ← fanin cone of t from original graph G
4.   build graph:    K(G, t) = (S, T, E_split, E_dep) with cost(v) for v ∈ V_K
5.   search cut:     Cut(S, T) ← Edmonds-Karp + residual reachable-set min-cut
6.   rank:           ranked_candidates ← sort(patches, key=score, stable)
7.   refine (P0 proxy): 单轮 F1-F5 → deterministic weight adjustment → re-search
8.   replace:        mapped cone-level internal representation (`replacement.json`)
9.   verify:         structural signature + Yosys-BLIF-ABC `cec`
                    (Stage A 5/5 pass; Stage B 当前 `unavailable` 因 clkinv_1)
10.  STA (Stage B):  OpenSTA pre-layout STA → wns/tns/slack/slack_status
11.  output:         metrics.json + replacement.json + cec_log + sta_report
```

## 3. 算法骨架 1：cone extraction（partial）

输入：gate-level graph G = (V, E), target output t ∈ V
输出：cone C(G, t) = (V_C, E_C)

```
1.  V_C ← {t}
2.  while frontier (predecessors of V_C not in V_C) non-empty do
3.    v ← any frontier vertex
4.    V_C ← V_C ∪ {v}
5.    E_C ← E_C ∪ {(u, v) ∈ E | u ∈ V_C}
6.  return C(G, t)
```

约束：
- 当前实现仅覆盖 combinational cone；sequential reg-to-reg cone 待 PM23 启动（M5）。
- 不实现 fanout cone；当前 baseline protocol (E06) 不需要 fanout。

## 4. 算法骨架 2：weighted s-t min-cut（ready）

输入：split graph K = (S, T, E_split, E_dep), cost function
输出：cut edges Cut(S, T), selected_gates

```
1.  build residual graph G_f from (S, T, E_split) with capacities = cost(v)
2.  while augmenting path from S to T in G_f via Edmonds-Karp:
3.    P ← BFS shortest path from S to T in G_f
4.    bottleneck ← min capacity along P
5.    augment G_f by bottleneck along P
6.  R ← vertices reachable from S in final residual graph G_f
7.  Cut(S, T) ← edges (u, v) with u ∈ R, v ∈ V_K \ R
8.  selected_gates ← gate endpoints on S side of Cut(S, T)
9.  return (Cut(S, T), selected_gates)
```

约束：
- 已通过 synthetic regression test 区分全局 min-cut 和单 gate 贪心。
- 当前 cost(v) 是 Stage A proxy：与 critical-path / level / size 联动；候选级 timing gain 在 F4 fail 时为 0（partial）。
- Stage B 不重做求解器；只用于 baseline_protocol 表字段。

## 5. 算法骨架 3：failure-aware refinement（P0 proxy）

输入：patch candidates P, F1-F5 thresholds
输出：refined candidates P'

```
1.  status ← classify_failures(P, G, t)
2.  for each p ∈ P:
3.    if status[p].F3 (size): reduce candidate size by reweighting cost(v) ↑ for high-fanout gates
4.    if status[p].F4 (timing gain): keep candidate unchanged (proxy)
5.  P' ← re-search under new cost function
6.  return P'
```

约束：
- 当前是 single-iteration proxy：failure_recovery 表 F3/F4 `avg_iterations=1.0`。
- 多轮循环、residual failure 分类、停止原因待 X19 (PM22) 设计审批。
- without F1/F3/F4 消融待 X19 启动后产出。

## 6. 算法骨架 4：technology mapping（ready）

输入：input Verilog, Liberty .lib, top module name
输出：mapped Verilog + mapped BLIF

```
1.  command ← `read_verilog <input>` + `hierarchy -check -top <top>` +
              `proc` + `flatten` + `opt` +
              `synth -top <top> -noabc` +
              `abc -liberty <lib>` +
              `clean` + `write_verilog -noattr <mapped.v>` +
              `write_blif <mapped.blif>`
2.  run Yosys with command, capture stdout/stderr/runtime
3.  verify mapped.v / mapped.blif non-empty
4.  extract Liberty cells, check mapped cells ⊆ Liberty cells
5.  return (status, mapped_verilog_path, mapped_blif_path)
```

约束：
- Stage A 风险 R20 已 mitigated（用 `synth -noabc + abc -liberty` 替代 raw `techmap`）。
- 当前 SKY130 Liberty 不含 `clkinv_1`，mapped BLIF 仍含 `.subckt sky130_fd_sc_hd__clkinv_1`；Stage B CEC 因此 unavailable (R31-01)。
- 输入 Verilog SHA256 在 mapping 后保持不变。

## 7. 算法骨架 5：SDC + OpenSTA pre-layout STA（ready）

输入：mapped Verilog, Liberty, 端口列表 + virtual clock 名称
输出：wns/tns/slack/slack_status, sta_report.txt

```
1.  parse Liberty → time_unit, capacitive_load_unit
2.  SDC ← `create_clock -name <clk> -period 10` +
           `set_load <load> [get_ports [all_outputs]]` +
           `set_driving_cell -lib_cell <buf> -pin X [get_ports [all_inputs]]` +
           `set_max_delay 0` (or `set_min_delay 0` for min analysis)
3.  sta_script.tcl ← `read_liberty <lib_wsl>` + `read_verilog <v_wsl>` +
                      `link_design <top>` + `source <sdc>` +
                      `report_checks -path_delay {max|min}` +
                      `report_worst_slack {-max|-min}`
4.  invoke sta in WSL2 with `-no_splash -exit <sta_script.tcl>`
5.  parse stdout: WNS / TNS / worst slack max INF / worst slack min INF
6.  return StaResult(status, wns, tns, slack, slack_status)
```

约束：
- `_to_sta_path` 把 `D:\foo` 转 `/mnt/d/foo`，Tcl 脚本路径也走同一转换。
- OpenSTA 3.1.0 不支持 `set_time_unit` / `set_capacitive_load_unit`（由 Liberty 提供）。
- `set_load <val>` 必须带 port 对象：`set_load <val> [get_ports [all_outputs]]`。
- 当前 8-case 全 combinational，`report_checks -path_delay max` 输出 "No paths found." / `worst slack max INF`，slack_status=MET。

## 8. 形式回验骨架（partial）

输入：reference BLIF (Yosys-normalized), mapped BLIF (technology mapping), 全主输出列表
输出：formal equivalence status

```
1.  ABC read_liberty <lib>
2.  ABC read_blif <reference.blif>
3.  ABC read_blif <mapped.blif>
4.  ABC cec <reference.blif> <mapped.blif>
5.  parse log → status ∈ {pass, fail, unavailable, error, timeout}
6.  return YosysAbcEquivalenceResult(status, scope, ...)
```

约束：
- 当前 SKY130 Liberty 不含 `clkinv_1`，Stage B 8-case CEC 全部 `unavailable`。
- Stage A 5-case (c17×2 + c432 + c499 + c880) Yosys-normalized full-netlist CEC 5/5 pass。
- [F08-B] DAC 2018 cost-aware multi-target 仍 B 级，禁止引用算法细节与数字。

## 9. 公开边界声明（与 L01 Related Work 一致）

| 主题 | 当前可写 | 当前禁写 |
|---|---|---|
| Cone extraction | combinational fanin；单输出 | fanout / sequential reg-to-reg |
| Cut solver | fixed / weighted s-t Edmonds-Karp | 替代 ABC/LM 算法细节 |
| Refinement | 单轮 F1-F5 deterministic proxy | 多轮 / residual failure / 停止原因（待 X19） |
| Tech mapping | `synth -noabc + abc -liberty` SKY130 HD Liberty | raw `techmap` / ORFS `cells.v` 配套 |
| STA | pre-layout combinational | signoff timing / SPEF / sequential DFF |
| Equivalence | structural signature + Stage A Yosys-BLIF-ABC full-netlist CEC | Stage B mapped-BLIF CEC（受 `clkinv_1` 限制）/ [F08-B] multi-target 数字 |

## 10. 后续修订

- X19 (PM22) 真正多轮 refinement 设计获批后，本文档第 5 节替换为 multi-iteration loop 骨架。
- SKY130 techmap library (N31-03) 获取后，第 6 节命令序列可去掉对 `synth -noabc` 的 workaround，恢复 raw `techmap`。
- Sequential EPFL benchmark (N31-05) 接入后，第 3 节补充 reg-to-reg cone、第 7 节补充 DFF clock 信号。
- 用户最终审定 N05 后，将本初稿迁入 `paper/submission/method_symbol_table.md`，并按正文段落重新组织。