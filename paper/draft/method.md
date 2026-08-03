# FAECO Method 章节正文（Draft 1）

更新时间：2026-07-31

本文档为论文 Method 章节的正文初稿，基于：
- `paper/draft/method_symbol_table.md`（N05）符号定义与算法骨架
- `paper/draft/introduction.md`（PM25）方法陈述
- `src/rseco/` 实际实现代码
- `docs/paper_audit/method_rewrite_readiness.md` 18 项要素审计

尚未经用户最终审定；结构和措辞仅作为论文主体核心，禁止作为主表事实性表述。

---

## 1. 方法总览

FAECO 在 RSECO 旧稿"重综合辅助 patch replacement"思路基础上，把修复过程形式化为图 1（占位）所示的三阶段流水线：

(a) **Resynthesis**：对原始网表 $G$（Verilog）经 Yosys `synth -top t -noabc + abc -liberty <lib>` 产生 mapped 网表 $G'$（SKY130 HD Liberty cells）；同时对原始网表用 Yosys `proc; flatten; opt; simplemap; clean; write_blif` 产生 reference BLIF $G_n$。

(b) **Cut & Refine**：以 fanin cone $C(G, t)$ 为基础，构建 s-t split graph $K(G, t) = (S, T, E_{split}, E_{dep})$；通过 Edmonds-Karp + residual reachable-set 求全局最小割 $\text{Cut}(S, T)$，按 score 排序候选 patch $[c_1, ..., c_k]$；当候选出现 F1-F5 失败时按失败类型确定性调整 cut 权重并重新搜索。

(c) **Verify & STA**：对替换后候选做结构签名等价 + Yosys-normalized BLIF vs mapped BLIF 的 ABC `cec` 形式回验；对 mapped Verilog 跑 OpenSTA pre-layout STA，产出 WNS / TNS / slack / slack_status。

## 2. 输入与符号

### 2.1 输入

- **原始网表** $G$：gate-level Verilog（c17 / c432 / c499 / c880 或 EPFL `v2025.1` 风格）。
- **目标输出** $t$：combinational primary output 或 reg-to-reg path endpoint。
- **工艺库** $\mathcal{L}$：SKY130 HD Liberty `.lib`（12,800,135 bytes, SHA256 `ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9`）。

### 2.2 符号表（与 `method_symbol_table.md` §1 一致）

| 符号 | 类型 | 当前定义 |
|---|---|---|
| $G = (V, E)$ | 有向图 | 门级网图，顶点为 gate/port，边为 signal wire |
| $C(G, t) \subseteq V$ | 子图 | target output $t$ 的 fanin cone |
| $K(G, t) = (S, T, E_{split}, E_{dep})$ | 切图 | 把 cone 内每个 gate 拆成 `gate:in → gate:out` 的 split graph |
| $\text{cost}(v) \in \mathbb{R}_{\geq 0}$ | 权重 | 每个 gate 的节点代价 |
| $\text{Cut}(S, T)$ | 边集 | 把 $S$ 与 $T$ 分开的 cut edges |
| $\text{patch} = (\text{gates}, \text{boundary}, \text{size})$ | patch 表示 | selected gates 列表、boundary ports、size |
| $\text{score}(\text{patch}) \in \mathbb{R}$ | 评分 | timing gain + size + boundary + verification + equivalence penalty |
| F1-F5 | 失败类型枚举 | 等价失败 / 边界失败 / size 过大 / timing 收益不足 / 验证超时 |

## 3. 重综合 + Technology Mapping

为生成 mapped 网表，FAECO 采用 Yosys 命令序列：

```
read_verilog <input>
hierarchy -check -top <top>
proc
flatten
opt
synth -top <top> -noabc
abc -liberty <lib>
clean
write_verilog -noattr <mapped.v>
write_blif <mapped.blif>
```

**设计动机**：原始 RSECO 流程仅用 `techmap + abc -liberty`；Yosys 0.9 的 raw `techmap` 流程在 SKY130 HD Liberty 上会产生 `sky130_fd_sc_hd__clkinv_1` placeholder（Liberty 实际不含此 cell），导致下游 ABC `cec` 不可达。采用 `synth -noabc + abc -liberty` 分两步：先 `synth -noabc` 把 Verilog 归约到 ABC primitives，再 `abc -liberty` 映射到 Liberty cells，避开 placeholder 路径。

reference BLIF 由 Yosys `proc; flatten; opt; simplemap; clean; write_blif` 生成；mapped BLIF 由 `write_blif` 在同一 Yosys session 输出。

输入 Verilog SHA256 在 mapping 后保持不变（27 个 SKY130 cell / ctrl case）。

## 4. Fanin Cone 抽取

给定 $G = (V, E)$ 和 $t \in V$，fanin cone $C(G, t) = (V_C, E_C)$ 由反向 BFS 抽取：

```
V_C ← {t}
while frontier (predecessors of V_C not in V_C) non-empty do
  v ← any frontier vertex
  V_C ← V_C ∪ {v}
  E_C ← E_C ∪ {(u, v) ∈ E | u ∈ V_C}
return C(G, t)
```

当前仅覆盖 combinational cone；sequential reg-to-reg cone 待 PM23 (M5) 启动。

## 5. Weighted s-t Min-Cut

在 $C(G, t)$ 上构建 s-t split graph：每个 gate $v$ 拆成 `gate:in → gate:out` 容量边，fanin 依赖用 $\infty$ 容量边。设 $\text{cost}(v)$ 是与 critical-path / level / size 联动的权重，全局最小割由 Edmonds-Karp + residual reachable-set 求出：

```
build residual graph G_f from (S, T, E_split) with capacities = cost(v)
while augmenting path from S to T in G_f via Edmonds-Karp:
  P ← BFS shortest path from S to T in G_f
  bottleneck ← min capacity along P
  augment G_f by bottleneck along P
R ← vertices reachable from S in final residual graph G_f
Cut(S, T) ← edges (u, v) with u ∈ R, v ∈ V_K \ R
selected_gates ← gate endpoints on S side of Cut(S, T)
return (Cut(S, T), selected_gates)
```

已通过 synthetic regression test 区分全局 min-cut 和单 gate 贪心。

## 6. Failure-Aware Refinement

FAECO 的核心贡献是 F1-F5 失败分类驱动的 refinement：

| 失败类型 | 检测条件 | 反馈动作 |
|---|---|---|
| F1 等价失败 | ABC `cec` 返回非 `pass` | 加权 candidate 的 verification cost |
| F2 边界失败 | `boundary_closed=False` | 收紧 cone 边界；保留已映射 gates |
| F3 size 过大 | $\text{size} > \text{threshold}$ | 提升高 fanout gate 的 cost，强制更小 cut |
| F4 timing 收益不足 | $\Delta\text{WNS} < \text{threshold}$ | 重算 candidate timing gain；保持 candidate |
| F5 验证超时 | $\text{timeout} > \text{threshold}$ | 加权 candidate 的 verification cost |

**当前实现是 single-iteration proxy**（Stage A）：failure_recovery 表 F3/F4 `avg_iterations=1.0`。**多轮 refinement**、residual failure 分类、停止原因和 without F1/F3/F4 消融待 PM22 (X19) 设计获批后启动。

**candidate-specific timing gain 当前是 Stage A proxy**：所有 candidate 共用同一目标输出 logic-level reduction（来自整网表静态值）。Stage B 已接 OpenSTA，可把 per-candidate STA timing gain 作为 ranking feature；当前未实现 round1 self-audit 已记录 (METH-12 partial, P1-4)，待 N31-05 sequential 拓展时一并解决。

## 7. 形式回验

FAECO 同时维护结构签名等价（`src/rseco/equivalence.py`）和形式等价（`src/rseco/yosys_abc.py`）两条路：

```
ABC read_liberty <lib>
ABC read_blif <reference.blif>
ABC read_blif <mapped.blif>
ABC cec <reference.blif> <mapped.blif>
parse log → status ∈ {pass, fail, unavailable, error, timeout}
```

Stage A 5-case (c17×2 + c432 + c499 + c880) Yosys-normalized full-netlist CEC 5/5 `pass`；Stage B 8-case CEC 8/8 `unavailable`，原因是 SKY130 Liberty 不含 `clkinv_1` placeholder（R31-01）。

## 8. Pre-Layout STA

为得到 mapped Verilog 的 pre-layout 时序指标，FAECO 采用 OpenSTA 3.1.0（WSL2 `/usr/local/bin/sta`）：

**SDC 命令序列**（`src/rseco/sdc.py`）：
```
create_clock -name <clk> -period <period>
set_load <load> [get_ports [all_outputs]]
set_driving_cell -lib_cell <buf> -pin X [get_ports [all_inputs]]
set_max_delay 0  (or set_min_delay 0 for min analysis)
```

**Tcl 脚本**（`src/rseco/opensta.py`）：
```
read_liberty <lib_wsl>
read_verilog <v_wsl>
link_design <top>
source <sdc>
report_checks -path_delay max
report_checks -path_delay min
report_worst_slack -max
report_worst_slack -min
```

**Windows→WSL2 路径转换** `_to_sta_path`：把 `D:\foo\bar` 转 `/mnt/d/foo/bar`，Liberty / Verilog / SDC / `sta_script.tcl` 都通过同一函数转换。

**Parser 支持**：`worst slack max INF` / `worst slack min INF` / `No paths found`。当前 8-case 全 combinational，输出 `No paths found.` + `worst slack max INF`，`slack_status=MET`。

## 9. 公开边界

| 主题 | 当前可写 | 当前禁写 |
|---|---|---|
| Cone extraction | combinational fanin；单输出 | fanout / sequential reg-to-reg |
| Cut solver | fixed / weighted s-t Edmonds-Karp | 替代 ABC/LM 算法细节 |
| Refinement | 单轮 F1-F5 deterministic proxy | 多轮 / residual failure / 停止原因 |
| Tech mapping | `synth -noabc + abc -liberty` SKY130 HD Liberty | raw `techmap` / ORFS `cells.v` 配套 |
| STA | pre-layout combinational | signoff timing / SPEF / sequential DFF |
| Equivalence | structural signature + Stage A Yosys-BLIF-ABC full-netlist CEC | Stage B mapped-BLIF CEC（受 `clkinv_1` 限制）/ [F08-B] multi-target 数字 |

## 10. 后续修订

- N05 方法符号表获批后，本章与 `paper/draft/method_symbol_table.md` 同步修订符号。
- PM27 Method 章节正文的伪代码与本文档同步。
- 用户最终审定后迁入 `paper/submission/method.md`。
- X19 multi-iteration refinement 设计获批后，本章第 6 节替换为多轮循环算法。
- SKY130 techmap library 修复后，本章第 3 节去掉对 `synth -noabc` 的 workaround，恢复 raw `techmap`。