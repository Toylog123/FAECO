# FAECO 0a 等价门（E1–E6）报告

- 日期：2026-09-23
- 基线侧：`codex/faeco-unified-loop` @ `9435846`（2026-08-28 10:59）
- 被测侧：`main` @ `fcdf06b`（0a 步骤 2–4 合并后：`a12ecab` / `9ac06bf` / `258f588` / `870d062`）
- 产物目录：`experiments/20260923_0a_equiv/E1/`
- 检查工具：`code/scripts/compare_0a_equivalence.py`（本次新增，可复用）

---

## 1. 结论

| 项 | 结果 |
|---|---|
| **Gate A：main 合并后 ≡ codex 基线** | **24/24 项全等 × 3 电路（`s382` / `b03` / `b06`）** |
| 六类等价（E1 候选顺序 / E2 F1–F6 序列 / E3 权重含 cone_limit / E4 接受补丁链 / E5 最终 WNS-TNS-min_slack / E6 STA 计数） | **全部 PASS** |
| 算法行为是否改变 | **未改变**（legacy 档逐位一致） |
| 全量回归 | **411 passed / 4 skipped**（与合并前一致，零回归） |
| 额外收获 | **`s382` 的论文产物被逐字段精确复现，24/24（含 `n_candidate_sta_runs=22`）** |
| 待裁定项 A5（`early_stop` 默认值） | **已裁定：内层 `early_stop=True`（串行）**，见 §5 |
| 新发现问题 | **OI-013**：`b03`/`b06` 的 20260826 产物无法由 codex HEAD 复现，见 §7 |

**0a 第一阶段的门已通过**，可以进入 L2 Adaptive（$\rho=0.5$）。

---

## 2. 方法与运行环境钉死

等价判定必须排除"环境差异伪装成行为差异"。本次逐项钉死：

| 环节 | 值 | 与产物是否同源 |
|---|---|---|
| 综合 Yosys | `0.67+146 (git sha1 468ba27d9-dirty, Release, GNU /usr/bin/x86_64-w64-mingw32-g++ 15.2.1)`，位于 `C:\oss-cad-suite-build\oss-cad-suite\bin\yosys.exe` | ✅ **与产物 `map.log` 逐字相同**；本机另一套 WSL Yosys 0.33 未使用 |
| STA | WSL Ubuntu `/usr/local/bin/sta`（OpenSTA），`-no_splash -exit` | ✅ 与产物 runner 同一调用形式 |
| 工艺库 | `data/raw/benchmarks/raw/openroad_flow_scripts_sky130hd/da8f092a.../lib/sky130_fd_sc_hd__tt_025C_1v80.lib` | ✅ |
| 基准源 | ISCAS89 `raw/iscas89/*.v`；ITC-99 `raw/itc99/v/*.v` | ✅（由产物 `map.ys` 反查确认） |
| 时钟周期 | `--period 0.5` | ✅ |
| 并发 | `--workers 1`（串行，保证确定性） | — |

> `mapped.v` 首行哈希（两次运行、两个仓库布局）逐字相同，证明综合环节可复现。

**codex 侧的运行方式**：`git worktree add scratch/codex_wt codex/faeco-unified-loop` +
`benchmarks/raw` 目录**联结点**指向 `data/raw/benchmarks/raw`（codex 分支是 09-12 迁移*之前*的布局，其
`benchmarks/` 不入库）。这样两侧跑的是同一份源码与同一份数据。

---

## 3. Gate A：逐电路结果

两侧**使用完全相同的命令行**（除输出目录），因此差异只能来自代码：

```
--circuit <c> --iscas89-dir <ITC 时指定 raw/itc99/v> --period 0.5 \
--max-iterations 8 --workers 1 --early-stop [--joint-enumerate-depth 3]
```

| 电路 | 判据 | 结果 |
|---|---|---|
| `s382` | codex `9435846` vs main `fcdf06b` | **24/24 全等，full gate PASS** |
| `b03` | 同上（`--joint-enumerate-depth 3`） | **24/24 全等，full gate PASS** |
| `b06` | 同上（`--joint-enumerate-depth 3`） | **24/24 全等，full gate PASS** |

### 3.1 `s382` 六类等价明细（代表性）

| 项 | codex 基线 | main 合并后 |
|---|---|---|
| E1 候选顺序 | `["076ee688...", ...]` | 同 |
| E1 逐轮状态 | `[[1,accepted,-0.88],[2,accepted,-0.85],[3,accepted,-0.83],…]` | 同 |
| E2 F1–F6 序列 | `5 × increase_critical_coverage_reward` | 同 |
| E3 最终权重 | `critical_coverage_reward=6.0`，其余 1.0 | 同 |
| E3 cone_limit | `1000` | 同 |
| E4 接受补丁链 | `53f8a1→7ef2ce→cfdf6e→2927efa7` | 同 |
| E4 stop_reason | `max_iterations` | 同 |
| E5 最终 | `wns=-0.83, min_slack=0.42, tns=-11.83, baseline_wns=-0.98` | 同 |
| E5 最终网表哈希 | `2927efa7fdfd58d786dfc4dee1532c550d1cdd078400169d6c489920359107e8` | 同 |
| E6 计数 | `n_candidate_sta_runs=86, sta_runs=53, formal_runs=106` | 同 |

`b03` 更强：连 `E1.candidate_order`（13 个候选身份）与 `E6`（`139 / 28 / 56`）都逐值相同。

---

## 4. 六项等价在工具中的定义

`compare_0a_equivalence.py` 把门拆成 24 个可判定项，并区分两类：

- **decision core**（判定行为是否改变）：`E1.round_status`、`E2.*`、`E3.*`、`E4.*`、`E5.*`
- **bookkeeping**（仪表口径）：`E1.candidate_order`、`E1.current_cone_gates`、`E6.*`

分了类不代表书账项可以不查——**Gate A 里它们同样全等**。分开只是为了在对照历史产物时能准确指出
"差异落在决策还是落在计数仪表"（§7 正是靠这个分类把问题定性清楚的）。

用法：

```bash
python code/scripts/compare_0a_equivalence.py \
  --reference <baseline>/outerloop_result.json \
  --candidate <candidate>/outerloop_result.json [--candidate ...] \
  --json-out <report>.json
```

---

## 5. A5 裁定：`early_stop` 默认值

§8.7.4 遗留的唯一实质分歧，用产物对齐法裁定，**不靠猜**：

| 复现配置 | `s382` 的 `wns_history` | 与产物（`[-0.88,-0.85,-0.83,-0.83]`） |
|---|---|---|
| `--workers 1 --no-early-stop` | `[-0.85,-0.83,×10]` | ✗ 第 1 轮直接跳到 -0.85 |
| `--workers 1 --early-stop` | `[-0.88,-0.85,-0.83,×10]` | 前 3 轮吻合，尾部条目数仍多 |
| **`--workers 1 --early-stop --candidates-per-iteration 1`** | `[-0.88,-0.85,-0.83,-0.83]` | ✅ **24/24 全等** |

**裁定**：

1. 产物使用 **串行（`--workers 1`）+ 内层 `early_stop=True`**。理由：`-0.88` 是"轮内遇到的首个改善候选"，
   不是该轮最优（该轮最优为 `-0.85`）。并行模式下 `early_stop` 被忽略（`real_wns.py:2106` 只在串行分支生效），
   若用并行则第 1 轮会接受 `-0.85`，与产物不符。
2. **main 旧口径的"首次接受即停"现在写作 `--max-patches 1`**，`--no-early-stop` 保留为"强制打开内层循环"的别名。
3. **保留 main trunk 的 `early_stop=True` 作为 CLI 默认**：`--no-early-stop` 显式覆盖即可，不再做静默翻转。
   A5 关闭。

### 5.1 附带钉住：产物使用了 `--candidates-per-iteration 1`

`s382` 产物的 `tested_candidate_hashes` 只有 **4** 个（而默认束宽 8 时为 12 个）。束宽 1 时每轮最多 1 个切分候选，
配合重复候选去重，正好得到 4 个身份与 4 条目 `wns_history`。束宽 2 给出 5 条目，同样不符。
⇒ **20260826 批次的 ISCAS89 主实验使用束宽 1**（`--candidates-per-iteration 1`）。

`b06` 产物另有 **6 个不改善 WNS 却被接受的补丁**，且 TNS 由基线改善（-3.98 → -3.92）——
这是 `--tns-aware` 的行为特征 ⇒ **该批次启用了 `--tns-aware`**。

> ⚠️ 论文侧待办（不阻塞实施）：`tab:configs` 是否需要登记 `candidates_per_iteration` 与 `tns_aware`
> 两个未被记录的开关。登记进 OI-013 的遗留项。

---

## 6. 复现命令

```bash
# s382 —— 精确复现论文产物（24/24）
python code/scripts/run_outerloop_real_wns.py \
  --circuit s382 --period 0.5 --max-iterations 8 \
  --workers 1 --early-stop --candidates-per-iteration 1 \
  --output-dir experiments/20260923_0a_equiv/E1/s382_k1

# b03 / b06 —— ITC-99，需指定源目录与联合枚举深度
python code/scripts/run_outerloop_real_wns.py \
  --circuit b03 --iscas89-dir data/raw/benchmarks/raw/itc99/v \
  --period 0.5 --max-iterations 8 --joint-enumerate-depth 3 \
  --workers 1 --early-stop \
  --output-dir experiments/20260923_0a_equiv/E1/b03_main
```

---

## 7. 未闭合：20260826 产物的 revision 未钉死（OI-013）

Gate A 只要求"main ≡ codex"，**不要求复现历史产物**。但既然产物是论文数字的来源，本次顺手做了对照，
结果分两类：

| 电路 | 产物是否可由 codex HEAD 复现 | 差异落在哪 |
|---|---|---|
| `s382` | ✅ **完全复现，24/24** | — |
| `b03` | ✗ 12/24 | decision core 也差：产物 `-1.27`（8 轮每轮接受），HEAD/`30f4164` 给 `-1.21` |
| `b06` | ✗ 8/24 | 产物 6 个 `--tns-aware` 接受（`stop=max_iterations`），HEAD 无接受（`stop=stagnation`） |

已排除的解释（均为实测，非推断）：

- **不是环境**：Yosys 版本与产物逐字相同（§2）。
- **不是参数**：`s382` 已用产物参数做到 24/24，说明参数复原方法本身是有效的；`b03` 在束宽 1 与 8 下
  给出**相同**结果（联合枚举主导），说明束宽不是 `b03` 的差异源。
- **不是 codex HEAD 特有**：在 `3e93fd2`（2026-08-26 11:09）与 `30f4164`（11:20）两处 worktree 定点重跑，
  `b03` 仍给 `-1.21`。

**时间戳证据**：产物批次写入时间 `s382 11:22 / b03 11:25 / b01 11:29 / b06 11:51`，而 08-26 当天有 7 个
代码提交落在 `10:47–12:25` 区间（`cbb5f7d`→`c58ad8e`），其中 `5966991`「Restore critical-path cover as first
constrained cut candidate」、`d595c71`「Keep non-R-rewritable gates in critical-path cover」直接改动候选生成，
`30f4164`/`b7abaac`/`c58ad8e` 改动 F2/SEC 检查（而检查结果经 `r_available_for` 反过来影响候选生成）。
**这是 codex 谱系内部 08-26→08-28 的既有漂移，不是本次合并引入的。**

**影响**：`b03` 的论文数字（`-1.27`）与 HEAD 行为（`-1.21`）不一致，方向是 HEAD **更好**；`s382`、`b06` 的
最终 WNS 一致，仅过程量不同。⇒ 需要裁定"论文主实验基线取哪个 revision"，见 OI-013。

---

## 8. 本次变更清单

| 文件 | 说明 |
|---|---|
| `code/scripts/compare_0a_equivalence.py` | **新增**。E1–E6 等价判定工具，24 项可判定，支持多候选与 JSON 输出 |
| `code/scripts/fix_crcrlf.py` | **新增**。全仓扫描并修复 `\r\r\n` 空行倍增 |
| `code/src/rseco/feedback.py` | 修复 `\r\r\n`（308 处，文件此前整体倍增） |
| `code/tests/test_yosys_map_script_encoding.py` | 修复 `\r\r\n`（60 处） |
| `experiments/20260923_0a_equiv/E1/` | 14 份 `outerloop_result.json` + 日志 + 2 份机器可读对照 JSON |

> `\r\r\n` 是 Windows 文本模式写盘把已有的 `\r\n` 再翻一次造成的（§8.7.2 踩坑记录 2 的复发）。
> 该缺陷不影响 Python 语义（多余空行），故 411 项测试全绿时未暴露；已按仓级扫描清除，全仓现在 0 处。

### 8.1 worktree 说明

为跑 codex 侧建立了三个临时 worktree：`scratch/codex_wt`（HEAD 基线，保留备用）、
`scratch/codex_3e93fd2`、`scratch/codex_30f4164`（定点验证用，可删）。
三者都在 git-ignored 的 `scratch/` 下，且各带一个 `benchmarks/raw` 目录联结点。
