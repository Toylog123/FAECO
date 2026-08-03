# Z3 Candidate/Boundary Formal Wrapper 设计文档

更新时间：2026-07-31

本文档是 N31-06 的设计文档，对应 P2 项 "Z3 candidate/boundary formal 未接入"。`paper/reviews/round1_self_audit.md` 列此项为后续工作。本文档不实施代码，仅给出 API 设计、wrapper 签名、case study、与 Stage A/B 边界的对比和 TDD 测试 outline。

## 1. 背景

FAECO 当前有两条等价验证路径：

1. **结构签名** (`src/rseco/equivalence.py`)：基于 gate count + connectivity signature 的快速检查，O(V+E)，但对结构变化不敏感。
2. **Yosys-BLIF-ABC formal CEC** (`src/rseco/yosys_abc.py`)：精确等价但只覆盖 full-netlist Yosys-normalized vs mapped-blif 全主输出。

**缺口**：FAECO 修复后候选 patch 的局部等价验证没有独立形式化手段。当前 candidate-level 验证依赖 replaced cone 的 structural signature，缺少 SAT/SMT 层的 counterexample 解析能力。`[G19]` 已留 F1 等价失败的字段，但 SAT 反例 trace 解析未接入。

Z3（5.0.0 已装在 `.venv`）可以填补这一缺口：在 patch boundary 上建立 SMT 等式约束，对每个 candidate patch 求解 equivalence。如果 SAT → fail，生成 counterexample trace；如果 UNSAT → equivalence 成立；如果 UNKNOWN → 记录 timeout。

## 2. API 设计

### 2.1 `Z3FormalEquivalenceResult`

```python
@dataclass(frozen=True)
class Z3FormalEquivalenceResult:
    status: str  # "pass" / "fail" / "timeout" / "unavailable"
    tool: str = "z3"
    command: str = ""
    runtime_s: float = 0.0
    reason: str = ""
    candidate_id: str = ""
    boundary_ports: tuple[str, ...] = ()
    wns_unaffected_check: bool = True
    returncode: int | None = None
    counterexample_inputs: tuple[tuple[str, int], ...] = ()  # (port_name, value) for FAIL
    stdout_tail: str = ""
    stderr_tail: str = ""

    def to_dict(self) -> dict: ...
```

### 2.2 `check_z3_candidate_boundary_equivalence`

```python
def check_z3_candidate_boundary_equivalence(
    original_netlist_path: str | Path,
    replaced_netlist_path: str | Path,
    *,
    boundary_ports: list[str],
    liberty_path: str | Path | None = None,
    output_dir: str | Path,
    z3_command: str = "z3",
    timeout_s: float = 60.0,
) -> Z3FormalEquivalenceResult:
    """对 candidate patch 局部做 SMT 等价验证。

    实现步骤：
    1. 读 original Verilog + replaced Verilog，分别用 Yosys 归约到 AIG
    2. 从 boundary_ports 抽取 input/output 列表
    3. 构造 Z3 SMT2 problem：
       - 对每个 input 声明 BitVec
       - 对每个 output 声明 BitVec 表达式
       - 对每个 boundary port，施加 (original_output == replaced_output)
    4. 调用 `z3 -smt2 -t:<timeout>` 求解
    5. 解析 sat/unsat/unknown：
       - sat → fail + 提取 counterexample inputs
       - unsat → pass
       - unknown → timeout
    6. 写 smt2 problem 到 artifact_dir/log
    7. 写 smt2 output (model) 到 artifact_dir/counterexample.txt (fail case)
    """
```

## 3. Wrapper 签名

`src/rseco/z3_formal.py` 模块：

```python
# 公开 API
@dataclass
class Z3FormalEquivalenceResult: ...

def check_z3_candidate_boundary_equivalence(
    original_netlist_path, replaced_netlist_path,
    *, boundary_ports, liberty_path=None,
    output_dir, z3_command="z3", timeout_s=60.0,
) -> Z3FormalEquivalenceResult: ...

# 私有 helper
def _read_z3_version() -> str | None: ...
def _build_smt2_for_boundary(
    original_blif_path: Path,
    replaced_blif_path: Path,
    boundary_ports: list[str],
) -> str: ...
def _parse_z3_output(stdout: str) -> tuple[str, dict]: ...
def _extract_counterexample(model_text: str, ports: list[str]) -> tuple[tuple[str, int], ...]: ...
```

## 4. Case Study

### 4.1 FAECO 候选 patch 的等价验证工作流

```
Stage A/B CEC:     full-netlist Yosys-normalized vs mapped BLIF, all primary outputs
                   (无法定位反例是哪个 patch 边界失败)

N31-06 Z3 boundary: replaced cone vs original cone, only boundary_ports
                   (可定位是哪个边界 input 触发反例)
```

N31-06 与 Stage A/B CEC 互补：
- Stage A/B CEC 在 mapped-netlist 全局层面验证
- N31-06 Z3 boundary 在 patch 局部验证，可生成 SAT counterexample trace

### 4.2 与 Stage A/B CEC limitation 关系

Stage B CEC 当前因 `clkinv_1` 不兼容 unavailable（R31-01）。N31-06 Z3 wrapper **不解决**此 limitation —— 它只对 candidate-level boundary 做 SMT 等价，与 ABC `cec` 路径独立。N31-03 ORFS techmap library 才是 Stage B CEC 的修复路径。

但 N31-06 可以：
- 在 Stage A 5-case 上验证：跑 `check_z3_candidate_boundary_equivalence` 对比 Stage A 的 structural signature
- 给 METH-08 提供 candidate-level 形式回验的 fallback（在 ABC `cec` unavailable 时仍能给出部分形式验证）

## 5. TDD 测试 outline

`tests/test_z3_formal.py`：

| 测试 | 输入 | 期望 |
|---|---|---|
| `test_api_exists` | module-level import | 暴露 `Z3FormalEquivalenceResult` / `check_z3_candidate_boundary_equivalence` |
| `test_two_identical_blifs_pass` | original=replaced, 1 input + 1 output | `status=pass`, runtime < 1s |
| `test_diff_in_output_fails` | original=AND, replaced=OR, 2 inputs | `status=fail`, `counterexample_inputs=[("a", 1), ("b", 0)]` |
| `test_boundary_subset_passes_when_equivalent` | 仅比较 boundary 端口 | `status=pass` |
| `test_timeout_returns_timeout` | timeout_s=1 + 复杂 RTL | `status=timeout` |
| `test_unavailable_when_z3_missing` | z3_command="z3-nonexistent" | `status=unavailable` |
| `test_liberty_optional` | 不传 liberty | 仍能用 BitVec 抽象 |

所有测试不依赖外部工具；fake_z3.py 在测试目录内模拟。

## 6. 设计边界与限制

### 6.1 N31-06 不做的事

- 不修复 Stage B CEC unavailable（这是 N31-03 的职责）
- 不实现 SAT counterexample 反例 trace 的图形化渲染（round 2 之后）
- 不集成到 Stage B runner（runner 仍只跑 ABC CEC；N31-06 作为独立的可选 caller）
- 不实现 multi-output equivalence（单 output 或多 output 但共享 boundary）

### 6.2 与现有代码的集成点

- 调用方：`src/rseco/flow.py` 或 `src/rseco/ranking.py`（可选 caller）
- 输入：mapped Verilog + original Verilog + boundary_ports（来自 cut 求解器）
- 输出：`Z3FormalEquivalenceResult.to_dict()` 可加入 per-case metrics
- 依赖：`z3-solver` Python 包（5.0.0 已装）；`pysmt` 或直接调用 `z3 -smt2` 二进制

### 6.3 性能预期

- c17 cone（4 gates）：< 0.1s
- ctrl EPFL cone（174 gates）：约 0.5-2s
- max EPFL cone（最大 26 outputs）：约 5-30s
- timeout=60s 默认值足够覆盖 8-case Stage B

## 7. 实施状态与后续计划

### 7.1 已实施（2026-08-03）

1. `src/rseco/z3_formal.py` 已创建（约 340 行）——递归下降 `_ExprParser` + wire DAG 解析（`_build_output_exprs` / `_rewrite_wires`）
2. `tests/test_z3_formal.py`（7 项）+ `tests/test_z3_formal_multi.py`（5 项）共 12 项 TDD 全绿
3. 完整回归 90 + 12 = **102 项测试全绿**
4. 支持：multi-output / escaped-identifier（`\B[0]`→`B[0]`）/ `~ & | ^` / 括号 / `1'b0` `1'b1` / unknown-identifier → fresh symbol
5. `scripts/run_z3_candidate_boundary_check.py` 8-case runner 已创建（commit `534be02` + `4eaaa2a`）

### 7.2 端到端 limitation（诚实记录）

- mapped.v 是 SKY130 **门级实例化**（0 assign，含 `clkinv_1` placeholder），assign-only parser 无法构建 replaced 侧 Z3 表达式 → 8-case 端到端全 error
- 单元测试层面（两边纯 assign 风格）已验证全部能力；8-case 端到端需 AIG→SMT 路径
- **AIG→SMT 后续路径**：用 Yosys `aigmap`（或复用 `src/rseco/yosys_json.py`）把 original.v 和 mapped.v 都归约到 AIG，再对 AIG DAG 建 Z3 表达式断言 output 等价；这是 round 2 或 N0803-01 的候选方向。**验证结论（2026-08-03）**：Yosys `aigmap` 对 mapped.v 报 `Module '\sky130_fd_sc_hd__nand2b_1' ... is not part of the design`——mapped.v 的 SKY130 实例化在无 `cells.v` 时是黑盒，无法 AIG 归约。**AIG→SMT 依赖 N31-03 cells.v**，不独立可行；N31-03 修复 CEC 的同时会解锁 AIG→SMT 8-case 端到端

### 7.3 后续计划

1. AIG→SMT 路径实现（解决 8-case 端到端 error）
2. 在 `experiments/20260731_epfl_8case_stage_b/tables/stage_b_case_summary.md` 加 cec_z3 列（AIG→SMT 后）
3. 更新 `paper/draft/method.md` §7 形式回验段，添加 Z3 boundary 描述
4. 更新 `paper/draft/experiments.md` 加 z3 column 表
5. 更新 `paper/reviews/round2_self_audit.md` 把 P2-1 升级为 done

## 8. 边界声明

- N31-06 是 P2 项，P0 项仍是 N31-03 ORFS techmap library
- N31-06 Z3 wrapper 不取代 Stage A/B ABC CEC，是补充
- 任何 [F08-B] DAC 2018 cost-aware multi-target 数字禁止引用到 Z3 wrapper 输出
- N31-06 设计对应 paper/draft/method.md §7 当前 "Stage A 5-case CEC 5/5 pass + Stage B 8-case CEC unavailable (R31-01)" 的补充，boundary 形式验证

## 9. 后续修订

- N31-06 wrapper 已实施（2026-08-03）；设计文档第 7 节已更新为"已实施状态 + 端到端 limitation + 后续 AIG→SMT 路径"。
- 用户决定是否投入 AIG→SMT 路径（解决 8-case 端到端 error）。
- 不投入时，N31-06 wrapper 在单元测试层面保持有效，8-case 端到端 error 作为诚实 limitation 保留；N31-06 在 roadmap 中标 partial。