# FAECO legacy regression（8 电路 E1–E6 等价门）报告

> 阶段：`0a 状态架构迁移 → legacy regression`（契约 `FAECO_V2_IMPL_CONTRACT_20260923.md` §6）
> 日期：2026-09-23
> 结论：**通过**（8/8 电路 × 24/24 项全等，且敏感性正控制报出预期差异）

---

## 1. 结论

**通过。** 契约 §6 的 legacy regression gate 达成：

| 项 | 结果 |
|---|---|
| **Gate（契约 §6 原句）** | "与 0a 同一 gate，扩到全 8 电路 \| **8/8 电路六项全等**" |
| 电路 | `s27 s382 s420 s641 s713 s820 s832 s953`（全部 ISCAS89） |
| 两侧 | 参考：`codex/faeco-unified-loop @ 9435846`（`scratch/codex_wt`）；候选：`main @ fcdf06b` |
| 判定 | **两个配置均 8/8 电路 × 24/24 项全等**：配置 A（归档批次配置）与配置 A2（+`--tns-aware`）；decision core 与 full gate（含 `E1.candidate_order` / `E1.current_cone_gates` / `E6` 计数）均 PASS；配置 B 的 `s27`（束宽 8）亦 24/24 |
| 工具链指纹 | 两侧 `mapped.v` 头为逐字相同的 `Yosys 0.67+146 (git sha1 468ba27d9-dirty, Release, GNU ... 15.2.1)` |
| **敏感性正控制** | 故意构造"应当有差异"的配置 → **2/2 电路报出 decision-core 差异**（`13/24`）；证明判据非恒真 |

**结论**：0a 的 `SearchState` 架构迁移在**全部 8 个 ISCAS89 电路**上零行为漂移
（不再只是 0a 当初的 3 个哨兵电路），且在**两个配置**下都成立。契约 §6 的下一阶段（L2 Adaptive）解除阻塞。

### 1.2 顺带得到的产物复现性结论（详见 §8，供 OI-013）

配置 A 就是归档 `20260826_iscas89_main` 批次的配置，因此本次顺带完成了一次 8 电路产物复现性检查：
**7/8 电路 decision-reproducible**（5/8 完全 24/24；`s713`/`s820` 仅差一个 `E6` 计数），
唯一 decision-core 例外是 `s832`，且其形态是**"路径不同、终点相同"**（最终 WNS/TNS/补丁/final_netlist_hash
全等，只是接受轮次不同）。相较之下 ITC-99 的 `b03`/`b06` 是**终值不同**，性质更严重。

### 1.1 本次顺带纠正的一处配置误判（影响 OI-013）

0a 报告把 `--tns-aware` 记为"20260826 批次"的开关。本次实测表明**该开关只属于 ITC-99 批次**：
s382 用**不含** `--tns-aware` 的命令复现归档产物 **24/24**；**加上**该开关后首轮接受点从 `-0.88`
变为 `-0.98`（一个 WNS 持平、TNS 改善的候选），匹配度掉到 **11/24**。
详见 §5.3。

---

## 2. 被比对象与判据

| 项 | 内容 |
|---|---|
| 参考侧（reference） | `scratch/codex_wt` = `codex/faeco-unified-loop @ 9435846`（产出论文主实验数字的谱系） |
| 候选侧（candidate） | 仓库根 = `main @ fcdf06b`（0a 迁移后的权威布局） |
| 逐对判据 | `code/scripts/compare_0a_equivalence.py` 的 E1–E6 共 **24 可判定项** |
| 多电路聚合 | `code/scripts/compare_equivalence_sweep.py`（本次新增，`--require-full`） |
| decision core | `E1.round_status` + `E2.*` + `E3.*` + `E4.*` + `E5.*` |
| bookkeeping | `E1.candidate_order` / `E1.current_cone_gates` / `E6.*` |

判据含义见 0a 报告 `FAECO_0A_EQUIVALENCE_20260923.md` §4。0a 的 E1–E6 是**移植不变性**检验
（契约 §5.2），即"0a 重构没有改变算法行为"，**不是**"能复现 20260826 产物"（后者属 OI-013）。

---

## 3. 运行环境钉死

| 项 | 值 |
|---|---|
| Yosys | 原生 OSS-CAD Suite `0.67+146 (git sha1 468ba27d9-dirty)`（`_yosys_env()` 注入 `bin`+`lib`） |
| OpenSTA | WSL2 Ubuntu `/usr/local/bin/sta`（`wsl.exe -d Ubuntu --`） |
| Python | 仓库 `.venv/Scripts/python.exe`（3.11.9） |
| 源 | `data/raw/benchmarks/raw/iscas89/*.v`（两侧显式传**同一绝对路径**） |
| 参考库 | `sky130_fd_sc_hd__tt_025C_1v80.lib`（两侧经 junction 指向同一文件） |
| 并发 | 每个 run 内 `--workers 1`；跨电路串行、两侧并行 |

---

## 4. 必须显式规避的三个陷阱（否则对照会**静默失效**）

### 4.1 runner 路径两侧不同 → 一侧秒退

| 侧 | runner 相对路径 |
|---|---|
| main | `code/scripts/run_outerloop_real_wns.py` |
| codex | `scripts/run_outerloop_real_wns.py` |

用同一个相对路径跑两侧时 main 侧**秒退**（`can't open file '...\03_FAECO\scripts\...'`，exit=2）。
首轮驱动脚本即踩此坑：8 个 main run 全部 `exit=2`，而 codex 侧正常完成 8/8。
若只看"codex 有产物"就会误以为两侧都跑了。

### 4.2 `.venv` 的 editable `.pth` 把 codex 侧劫持到 main 的 `rseco`

`.venv/Lib/site-packages/__editable__.faeco_rseco-0.1.0.pth` 是一行硬编码路径
`D:\...\03_FAECO\code\src`，因此无论 `cwd` 如何 `import rseco` 都解析到 **main 的 `code/src`**：

```
cd scratch/codex_wt && python -c "import rseco"
    -> D:\...\03_FAECO\code\src\rseco\__init__.py          # 静默劫持
cd scratch/codex_wt && PYTHONPATH=src python -c "import rseco"
    -> D:\...\scratch\codex_wt\src\rseco\__init__.py       # 正确
```

漏设时两侧跑的是**同一份代码**，所有电路必然"全等"，gate 退化为同义反复。
**修法**：两侧均设 `PYTHONPATH=<该侧根>/src`。

### 4.3 Git Bash 的 `pwd` 是 POSIX 形式 → Windows 解释器找不到源文件

`ROOT="$(cd ... && pwd)"` 得到 `/d/BaiduSyncdisk/...`，交给 Windows 版 Python 后被解释成
`\d\BaiduSyncdisk\...`，报 `circuit not found: \d\...`。
**修法**：`ROOT="$(cd ... && { pwd -W 2>/dev/null || pwd; })"`。

> 三者都是"**结果看起来正常、其实是假的**"型缺陷。§6 的敏感性正控制即为证伪手段。

---

## 5. 配置集与 CLI 等价性

### 5.1 四个配置

| 配置 | 目录 | 开关 | 用途 |
|---|---|---|---|
| **A** artifact | `configA_artifact/` | `--period 0.5 --max-iterations 8 --workers 1 --early-stop --candidates-per-iteration 1` | 归档 ISCAS89 批次的配置；兼作产物复现性检查（§8） |
| **A2** k1tns | `configA2_k1tns/` | A + `--tns-aware` | 覆盖 ITC-99 批次才有的开关；**本次 gate 主证据** |
| **B** gateA | `configB_gateA/` | `--period 0.5 --max-iterations 8 --workers 1 --early-stop`（默认束宽 8） | 0a gate 在 3 哨兵上用的配置，拟扩到 8 电路 |
| **C** ctrl | `configC_ctrl/` | B 去掉 `--early-stop` | **敏感性正控制**（非 gate） |

配置 B 在 1/7 电路后主动终止：0a gate 已覆盖过"束宽 8"口径（`s382`/`b03`/`b06`，含 2 个更难
的 ITC-99 电路），其边际信息低于配置 A（直接对齐论文数字）。已终止的产物保留在目录中。

### 5.2 CLI 表面差异（静态核对，39 个 flag 逐项）

| flag | main | codex | 说明 |
|---|---|---|---|
| `--early-stop` | `store_true` + `set_defaults(early_stop=True)` | `store_true`（默认 False） | **唯一默认值分歧** |
| `--no-early-stop` | `store_false` 别名 | （无） | main 独有、纯增量 |
| `--iscas89-dir` | `_BENCH/raw/iscas89` | `ROOT/benchmarks/raw/iscas89` | 默认路径不同；两侧**显式传同一绝对路径** |
| 其余 36 个 | 一致 | 一致 | — |

→ **显式传 `--early-stop` 后，两侧命令行语义完全等价**。这个"唯一分歧"也正是配置 C 的构造依据。

### 5.3 纠正：`--tns-aware` 属于 ITC-99 批次，不属于 ISCAS89 批次

0a 报告 §5.1 由 `b06`（ITC-99）的"6 个 WNS 持平、TNS 改善的接受"推断该批次启用了 `--tns-aware`。
本次在 ISCAS89 上做定点探针，结果相反：

| s382 运行 | 首轮 `(iter, status, wns)` | `n_candidate_sta_runs` | vs 归档产物 |
|---|---|---|---|
| 不含 `--tns-aware` | `(1, accepted, -0.88)` | 22 | **24/24 全等** |
| 含 `--tns-aware`（配置 A2） | `(1, accepted, -0.98)` | 19 | 11/24 |

`-0.98` 恰为该电路的 `baseline_wns`，即使用了 `--tns-aware` 后首轮接受了一个**WNS 持平、
TNS 改善**的候选——正是该开关的语义。

⇒ **归档的 ISCAS89 批次未启用 `--tns-aware`**；该开关属于 ITC-99 批次。
这修正了 OI-013 遗留项里"两个未登记开关"的适用范围，也是配置 A 与 A2 并存的原因。

---

## 6. 敏感性正控制（配置 C）

**目的**：证明 `compare_equivalence_sweep.py` 并非恒真，且两侧确实在跑**不同的代码**
（若 §4.2 的 `PYTHONPATH` 漏设，本控制会**报不出任何差异**）。

**构造**：取 §5.2 静态 diff 出的唯一默认值分歧——`--early-stop`——**不显式传它**，
让 codex 用默认 `False`、main 用默认 `True`。其余参数与配置 B 相同（默认束宽 8）。
预期：至少一个电路出现差异。

**结果**：

```
circuit    items   decision       full  status
s382    13/24       FAIL       FAIL  DECISION_DIFF  core: E1.round_status, E2.feedback_sequence, E3.final_weights, E3.action_multiset, E4.accepted_chain
s832    13/24       FAIL       FAIL  DECISION_DIFF  core: E1.round_status, E2.feedback_sequence, E3.final_weights, E3.action_multiset, E4.accepted_chain
decision core : 0/2 circuits      full gate : 0/2 circuits      SWEEP GATE : FAIL
```

**2/2 电路报出 decision-core 差异** → 判据有效、隔离有效。配置 A2 的 8/8 全等因此是**有内容的结论**。

---

## 7. 逐电路结果（配置 A2，本次 gate 主证据）

两侧在下列每个字段上逐值相同（`codex == main`）：

| 电路 | iterations | `n_candidate_sta_runs` | baseline WNS | WNS | TNS | stop_reason | 24 项 |
|---|---:|---:|---:|---:|---:|---|---|
| s27 | 8 | 35 | -0.27 | -0.18 | -0.37 | max_iterations | 24/24 |
| s382 | 8 | 19 | -0.98 | -0.83 | -11.72 | max_iterations | 24/24 |
| s420 | 8 | 43 | -1.56 | -1.21 | -11.57 | max_iterations | 24/24 |
| s641 | 8 | 127 | -1.63 | -1.17 | -14.66 | max_patches | 24/24 |
| s713 | 8 | 35 | -1.33 | -1.18 | -15.91 | max_patches | 24/24 |
| s820 | 8 | 52 | -1.19 | -1.14 | -5.37 | max_patches | 24/24 |
| s832 | 8 | 29 | -1.23 | -1.16 | -5.47 | max_iterations | 24/24 |
| s953 | 8 | 21 | -1.31 | -1.21 | -25.63 | max_iterations | 24/24 |

**汇总**：`decision core 8/8`，`full gate 8/8`，`SWEEP GATE : PASS (full E1-E6)`。
机读报告：`experiments/20260923_legacy_reg/configA2_k1tns/gate_8circ.json`。

---

## 8. 附带：归档 ISCAS89 产物的复现性（配置 A，供 OI-013）

配置 A（§5.1）同时就是归档 `20260826_iscas89_main` 批次的配置，因此可以把本次产物与归档产物直接对齐。
参考侧取 codex（`configA_artifact/codex/`）：

| 电路 | vs 归档产物 | decision | full | 差异项 |
|---|---|---|---|---|
| s27 | 24/24 | PASS | PASS | — |
| s382 | 24/24 | PASS | PASS | — |
| s420 | 24/24 | PASS | PASS | — |
| s641 | 24/24 | PASS | PASS | — |
| s713 | 23/24 | PASS | FAIL | `E6.n_candidate_sta_runs`（29 vs 30） |
| s820 | 23/24 | PASS | FAIL | `E6.n_candidate_sta_runs` |
| s832 | 13/24 | **FAIL** | FAIL | `E1.round_status` / `E2` / `E3` / `E4` / `E1.candidate_order` / `E6.*`（**`E5.*` 全等**） |
| s953 | 24/24 | PASS | PASS | — |

**汇总：7/8 电路 decision-reproducible，5/8 完全 24/24。**

- `s713` / `s820`：唯一差异是 `E6.n_candidate_sta_runs` 这一个 **bookkeeping 计数**（正是判据里
  "生产谱系内被反复重写过的仪表口径"），**决策完全一致**。
- `s832`：唯一 decision-core 例外，但形态是**"路径不同、终点相同"**——
  归档产物与 HEAD 的最终 `wns=-1.16`、`tns=-5.48`、`final_patch_id=patch_G96_critical_path_cover`
  乃至 `final_netlist_hash` **完全一致**；差别只在轨迹：归档在第 1–3 轮接受
  （`-1.18 → -1.17 → -1.16`），HEAD 在第 1–4 轮接受（`-1.19 → -1.18 → -1.17 → -1.16`）。
- 对照：配置 A2（k=1 **+** `--tns-aware`）下只有 `s27`、`s953` 全等，其余 6 个电路均偏离
  ⇒ 配置 A 才是归档 ISCAS89 批次的正确配置（§5.3）。

### 对 OI-013 的更新

| 批次 | 结论 |
|---|---|
| **ISCAS89**（`20260826_iscas89_main`） | **7/8 decision-reproducible**；`s832` 为"终点相同、路径不同"；`s713`/`s820` 仅差一个 E6 计数 |
| **ITC-99**（`20260826_itc99_main`） | `b03`/`b06` 仍不可复现，且**终值不同**（`b03` 产物 `-1.27` vs HEAD `-1.21`）——性质比 s832 严重 |

⇒ "论文主实验基线取哪个 revision"这一裁定的**影响面收窄到 ITC-99（b03/b06）与 s832 的轨迹描述**；
ISCAS89 其余 7 个电路的论文数字可由 HEAD 复现（s713/s820 需接受 E6 计数口径差异）。
仍待用户裁定。

---

## 9. 复现命令

```bash
cd D:/BaiduSyncdisk/01_Papers/03_FAECO

# 复跑（两侧并发；每侧 8 电路串行）
bash code/scripts/run_equivalence_sweep.sh k1tns both      # 配置 A2（本次 gate 主证据）
bash code/scripts/run_equivalence_sweep.sh artifact both   # 配置 A（归档批次配置）
bash code/scripts/run_equivalence_sweep.sh ctrl both s382,s832   # 配置 C（敏感性控制）

# 判定（判据在 code/scripts/compare_0a_equivalence.py，聚合器在 compare_equivalence_sweep.py）
.venv/Scripts/python.exe code/scripts/compare_equivalence_sweep.py \
  --root experiments/20260923_legacy_reg/configA2_k1tns \
  --left codex --right main \
  --circuits s27,s382,s420,s641,s713,s820,s832,s953 \
  --require-full \
  --json-out experiments/20260923_legacy_reg/configA2_k1tns/gate_8circ.json
```

前置条件：`scratch/codex_wt` worktree 存在（`benchmarks/raw` 为指向
`data/raw/benchmarks/raw` 的目录联结点）；原生 OSS-CAD Yosys 与 WSL OpenSTA 可用。

---

## 10. 本次变更清单

| 文件 | 变更 | 为什么 |
|---|---|---|
| `code/scripts/compare_equivalence_sweep.py` | **新增** | 多电路 E1–E6 聚合判定（`N/N 电路六项全等`），复用单对判据不重复定义 |
| `code/scripts/run_equivalence_sweep.sh` | **新增** | 已归档的复跑驱动；把 §4 的三个陷阱与四个配置固化下来（含 `pwd -W` 与 `FAECO_DRY_RUN`） |
| `code/tests/test_compare_equivalence_sweep.py` | **新增** | 6 项：全等/决策差异/仪表差异/缺失产物/退出码/JSON |
| `code/tests/test_run_equivalence_sweep_sh.py` | **新增** | 10 项：静态守卫（`pwd -W`、两侧入口与 `PYTHONPATH`、四配置互不混淆）+ 参数校验与干跑路径 |
| `project_docs/reports/FAECO_LEGACY_REGRESSION_20260923.md` | **新增** | 本报告 |

产物（git-ignored，不入库）：`experiments/20260923_legacy_reg/{configA_artifact,configA2_k1tns,configB_gateA,configC_ctrl}/`。
