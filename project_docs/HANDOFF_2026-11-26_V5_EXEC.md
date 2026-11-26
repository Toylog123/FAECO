# FAECO V5 实验执行交接（2026-11-26 22:25，实验中断点）

> **给接手智能体的一句话**：Stage 1 已完成、Stage 2 完成 2A 与 2B 第一遍，**Stage 2B 第二遍（600 s 预算）被人工中止、未落盘**；Stage 3/4/5 未启动。按第 2 节命令续跑即可断点续接，不需要重做已完成项。论文修订清单仍见 [HANDOFF_2026-11-26_V5.md](HANDOFF_2026-11-26_V5.md) 第 4 节。

---

## 1. 当前完成度与收据（引用前请自行 `sha256sum` 复核）

| 阶段 | 状态 | 收据 | SHA-256 |
|---|---|---|---|
| Stage 1 功耗/6 角 + 7 nm 受控非零 DRC + 4 线程确定性 | **完成** | `evidence/tcad_v5_revision_20261126/V5_STEP1_POWER_7NM_DET_VERIFIED.json` | `85bfc1657fbc0663649e417abbe7a9c9827d7d1cded05c121133bd150f28a235` |
| Stage 2A UART Setup 去重开/关消融 | **完成**（`uart_dedup_ablation` 两臂齐） | `evidence/tcad_v5_revision_20261126/V5_STEP2_DEDUP_NATIVE_VERIFIED.json` | `917a665550f695198148cd428f3ec56149fa4f8596121db358367724000c95e8` |
| Stage 2B 原生 `recover_power` 挂保护后端（240 s 默认预算，四设计） | **完成**（8 个 key 齐，含 asap7 的 `not_in_action_space` 分类） | 同上 | 同上 |
| Stage 2B 第二遍（SKY 两设计 600 s 预算，key 后缀 `::rt600s`） | **未完成（人工中止）** | — | — |
| Stage 3 双设计四档预算在线搜索 | **未启动** | — | — |
| Stage 4 双 AES 探针子预算敏感性 | **未启动** | — | — |
| Stage 5 万门级 riscv32i-TC 独立 Timing-closed | **未启动** | — | — |

中止时刻机器上**已无任何 openroad / yosys / run_v5 进程**（已确认），无残留并发负载。

### Stage 1 已落盘的关键数字（可直接引用，但请打开 JSON 复核键路径）

- TT 真实 SPEF 功耗（总／组合／漏电）：`SKY130HD AES` 18 门 −0.1019%／−0.1405%／−0.0643%；`ASAP7 UART-TC` 13 门 −0.6595%／−2.1419%／−0.7770%；`ASAP7 UART K=36` 19 门 −0.6228%／−2.2340%／−1.3911%。键：`part2_power_and_6corner.<design>.delta_pct`。
- 6 角：UART-TC 端点 FF／TT／SS Setup 255.927／190.381／28.931 ps、Hold 50.315／67.502／54.054 ps（`still_timing_closed = true`）；AES Hybrid 18 门相对控制点 Δsetup +0.135／−0.035／+1.022 ps、Δhold +0.011／+0.018／+0.459 ps。
- 7 nm 受控非零 DRC：窗内 5 例共 **37 marker，TP 37 / FP 0 / FN 0**，marker 集合与网集合逐例完全相同，注入 aggressor 全部被捕获，单次预检均值提速 **17.34×**；另有 1.05×$H_{\mathrm{row}}$ **窗外负对照** 2 marker 仅全块可见（`scope_control`，作用域边界，不计召回）。键：`part3_asap7_controlled_nonzero_drc`。
- 4 线程确定性：`asap7/uart` 与 `sky130hd/aes` 各 3× 重复完整 DRT+RCX+三角 STA，去日期 SPEF 逐字节一致（`bbc304b8…`／`ee3ed948…`）、判据一致、Setup/Hold 极差 **0.000 ps**。**该 3 门批次本身是 `SS:hold_regression` 拒收**，结论只能写「产物与判据确定性」，不得外推接受性。键：`part4_4thread_drt_determinism`。

### Stage 2A 已落盘的关键数字

| 臂 | 合格回收 / µm² | 门数 | ANYTIME AUC | 物理评估次数 | 去重命中 | 计费墙钟 / s |
|---|---:|---:|---:|---:|---:|---:|
| `dedup_off` | 0.83106 | 13/18 | 0.4344 | 20 | 0 | 634.6 |
| `dedup_on` | 0.83106 | 13/18 | 0.4764 | 19 | 1 | 588.0 |

口径：同冻结起点、同 18 项池、$1.0\times H_{\mathrm{row}}$ 保护后端、720 s 窗口含筛选。**同终态面积，去重使 AUC +9.7%、少 1 次物理评估、早 46.6 s**——只能这样写，不能写「去重提高回收面积」。

### Stage 2B（240 s 预算）已落盘的结论形态

- `sky130hd_aes`（原生提 120 项）与 `sky130hd_riscv32i`（24 项）：`status = rejected`，原因是**单次保护后端路由触及 240 s 上限**（`rc=None`），**不是**时序或 hold 判定。这正是必须补跑第二遍（600 s）的原因。
- `asap7/uart`（16 项）与 `asap7/aes`（174 项）：`status = not_in_action_space`。原生 `recover_power` 改的是 ORFS 端口缓冲实例（如 `output43`、`u6820`），不在冻结 runner 的可编辑实例集合内（实测 `ref_masters` 531 项不含它们）。这是**动作空间兼容性结论**，不是物理结论。

---

## 2. 续跑命令（WSL2 Ubuntu，独占 6 核，逐条可复制）

```bash
# 0) 接手自检（2 s，无 EDA）
wsl -e bash -lc "python3 /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/tcad_v5_revision_20261126/smoke_verify_v5.py"

# 1) 续跑 Stage 2（2A 与 8 个 240 s key 会自动跳过；只做 2B 第二遍 600 s）
wsl -e bash -lc "cd /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO && bash project_docs/evidence/tcad_v5_revision_20261126/run_all_v5_experiments.sh --stage 2"

# 2) Stage 3（约 100 min，8 臂 × 720 s）
wsl -e bash -lc "cd /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO && bash project_docs/evidence/tcad_v5_revision_20261126/run_all_v5_experiments.sh --stage 3"

# 3) Stage 4（约 75 min，6 臂 × 720 s）
wsl -e bash -lc "cd /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO && bash project_docs/evidence/tcad_v5_revision_20261126/run_all_v5_experiments.sh --stage 4"

# 4) Stage 5（ORFS 全新构建 30 min 预算 + 3 臂 × 720 s ≈ 70 min）
wsl -e bash -lc "cd /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO && bash project_docs/evidence/tcad_v5_revision_20261126/run_all_v5_experiments.sh --stage 5"

# 5) 进度与收据
wsl -e bash -lc "tail -40 /home/toylog/faeco_v5_master.log"
wsl -e bash -lc "sha256sum /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/tcad_v5_revision_20261126/V5_*_VERIFIED.json"
```

**两点必须注意**

1. `run_all_v5_experiments.sh` 对 **Stage 2/3/4 永不跳过**（脚本内 `"$num" != "2" && ...` 判断），Stage 1 与 5 在 JSON 存在时会跳过。Stage 2 重跑靠各函数内部的 key 级跳过，所以**不要加 `--force`**，否则会重做 2A 的 24 min。
2. 执行期间**不要并发跑别的 EDA**：所有 720 s 墙钟计费都按独占 6 核口径，并发会污染 Stage 3/4/5 的时间类结论。

---

## 3. 本轮改过的脚本（6 处，全部是实现层缺陷，未改任何科学设定）

改动尚未提交前的基线是 `a513f5ff`。逐条列清以便复核或回退：

| 文件 | 缺陷 | 修法 | 已核实 |
|---|---|---|---|
| `run_v5_step1_power_7nm_det.py` | sky130hd 的 `FF`／`SS` liberty 指向 `orfs/.../sky130hd/lib`，该目录只有 `TT` | 新增 `SKY_LIB_PINNED` 常量，取 `rseco_timing/vendor/OpenROAD-b511b6a/test/sky130hd/`，组成规范三元组 `SKY_CORNER_LIBS` | AES 控制点 FF／TT = 678.249／−380.501 ps，与 `.../ss_hold_targeted_v2b/qualification/CONTROL.json` 逐位一致 |
| 同上 | `measure_3corner_wns` 统一 ×`1e12`。`sta::worst_slack` 实际按 **liberty 时间单位**返回（sky130hd = ns，ASAP7 = ps），ASAP7 端点被放大 $10^{12}$ 而全部误拒 | 新增 `lib_time_scale_ps()` 解析 liberty `time_unit` 逐角换算 | UART-TC 三角 Setup 255.85／190.42／30.29 ps 与既有收据一致；修正后 13 门端点被正确接受 |
| 同上（第 1.3 节整段重写） | 原用 `odb::dbWireEncoder::begin()` 向既有邻居网追加金属。**实测会重写整条线**（`net1060` 长度 67→5、op 29→1），将静默破坏真实布线并污染 TP/FP/FN | 改为「受控合成 aggressor 网 `FAECO_NZ_*`（真实层 M1/M2/M3）＋目标实例自身直连网」同层成对注入；锚点用**放置后实例包围盒中心**（`getAvgXY` 在 ASAP7 返回非块坐标，已弃用）；新增 1.05×$H_{\mathrm{row}}$ 窗外负对照 | 5 例 37 marker、TP/FP/FN = 37/0/0，`markers_outside_window = 0` |
| 同上（第 1.4 节） | 试验目录放在 runner 输出根之外，`compare_ibex.evaluate` 的 `relative_to` 抛错 | 目录改到 `<runner>/rep_N`、`<runner>/diag` | 两设计 3× 重复均跑通 |
| 同上（第 1.4 节） | `sky130hd/aes` 的 `physical` 走 `DiagnosticRepairComparison`，其 `initial_hint` 只在 `prepare_case` 里建立 | 无引导审计显式 `runner.initial_hint = set()` | 同上 |
| `run_v5_step2_dedup_and_native_protected.py` | ① `protected_eval` 同样在 runner 根之外；② `qualify_zero()` 用非递归 `mkdir`，要求 `<runner.output>` 已存在；③ 原生改到动作空间外的实例时抛 `KeyError`；④ 默认 240 s 路由上限使 SKY 结论变成「超时」而非物理判定 | ① 评估目录改到 `<runner>/protected_eval`；② 构造后 `Path(runner.output).mkdir(parents=True, exist_ok=True)`；③ 先比对 `runner.eval.ref_masters`，缺失则记 `status = not_in_action_space` 并附实例样例；④ 函数增参 `designs / route_timeout / key_suffix`，`main()` 增加 600 s 第二遍（key 后缀 `::rt600s`，窗口 840 s） | 2A 两臂、2B 8 个 key 已落盘 |
| `run_v5_step3/4/5_*.py` | 三个脚本对 `sky130hd_aes` 同样会命中 `initial_hint` 缺失 | Stage 3/4 在 `make_boxed_runner` 后加 `hasattr` 保护 | 仅静态编译通过，**未实跑** |
| `run_v5_step5_10k_timing_closed.py` | ORFS 没有 `detailed_route` 这个 make 目标（实测 `No rule to make target`），且 `SKY_CORNERS` 复制了错误路径 | 目标改为 `route finish`；`SKY_CORNERS` 改为复用 `s1.SKY_CORNER_LIBS` | 仅静态编译通过，**未实跑** |

所有脚本改动均通过 `python3 -m py_compile`。除上述之外未动 `HYBRID_FAECO_4DESIGNS_VERIFIED.json` 等既有收据。

---

## 4. 每个阶段跑完后的必查项（不满足就不要把数字写进论文）

**Stage 2（第二遍）**
- `sky130hd_aes::native_std::rt600s` / `...::rt600s` 的 `status` 必须是 `rejected`／`qualified_pass` 之一，且 `failures` 里应是 `SS:setup_budget`／`TT:tns_budget`／`*:hold_regression` 之类**物理原因**；若仍出现 `rc=None` 说明 600 s 也不够，如实记录「该原生方案在本后端 600 s 内不可评估」，**不要**写成「原生回收为 0 所以 FAECO 更优」。
- 若某设计给出 `qualified_pass`，必须核对 `sec_pass = true` 与 `views_delta_ps` 是否全在预算内。

**Stage 3（四档预算）**
- 期望形态：预算收紧（0%）时 `setup_rejections` 上升、`hold_rejections` 变化不大；预算放宽（2%）时回收增加但需检查是否出现新的 SS 负 setup。
- 交叉核对：`asap7/uart @ 1.0%`（即 2.7 ps）应复现既有 0.83106 µm² 附近；`sky130hd/aes @ 1.0%`（36 ps）应复现 98.8448 µm² 或 197.6896 µm² 量级（取决于是否走全池探针）。若不是，先查 `prepare_online` 的共享预检是否命中了同一个起点（`/home/toylog/faeco_v4_hybrid_faeco_20261126_v1/sky_shared_preflight/preflight/result.json`）。
- 每个 key 落盘后 JSON 即时更新，可随时中断。

**Stage 4（探针敏感性）**
- 注意 `imported_references` 里 0 s 与默认 180 s 两组是**从既有收据导入**（`BOXED_DRC_VERIFIED.json` / `HYBRID_FAECO_4DESIGNS_VERIFIED.json`），本阶段只新跑 60/120/240 s。撰写时必须区分「导入」与「新测」，不要混成五点全部新测。
- 期望形态：$\tau_{\mathrm{probe}}$ 增大到某点后 `phase1_status` 由 `sub_budget_timeout` 转 `passed`；`asap7/aes` 因 44 s 全块预检税在 0 marker 设计上可能始终 `rejected`，这是已知边界。

**Stage 5（riscv32i-TC）**
- 先看 `/home/toylog/faeco_v5_step5_riscv32i_tc_20261126_v1/orfs_build_tc10ns.log` 尾部：确认 `route`/`finish` 成功且 `6_final.odb`／`6_final.sdc` 存在。**若 `make` 超 1800 s**，把脚本里 `subprocess.run(..., timeout=1800)` 调大后重跑（构建有缓存，重跑很快）。
- `ref_info.strictly_timing_closed` 必须为 `true`，否则脚本会 `assert` 中止——这是设计意图，不要绕过。
- 三臂（`single_boxed`／`fixed_boxed`／`faeco_boxed`）的 `evaluate_subset_protected` 会把所有非直连信号网 `setSpecial` 后跑 `detailed_route`；如果三臂全 0，**先看该臂 `route.log`／`full_drc.rpt`**，区分「路由失败」「DRC 非零」「时序门拒收」，不要把实现失败写成方法结论。

---

## 5. 已知坑（本轮踩过的）

1. **日志看似不动**：Stage 1 的 `print` 没有 `flush=True`，经 `tee` 后整段缓冲，`tail` 长时间空白属正常；用产物目录 mtime 判断进度。Stage 2–5 有 `flush=True`，可实时看。
2. **`wsl -e bash -lc` 里写 Windows 风格绝对路径会被 MSYS 改写**，调用 OpenROAD 等 WSL 内二进制时加 `MSYS_NO_PATHCONV=1`。
3. **DeepSeek 之外不要并发 EDA**；`taskset -c 0-5` 只在启动器里，手工跑脚本要自己加。
4. **Stage 2 不能用 `--force`**（会重做 24 min 的 2A）。
5. OpenROAD 二进制本轮一律用 `/home/toylog/.cache/bazel/.../openroad_unstamped`（与 V4 同款），**不要换成 `or26Q3/bin/openroad`**，否则与既有收据不同源。

---

## 6. 跑完之后要做什么

1. 汇总 `project_docs/evidence/tcad_v5_revision_20261126/REPORT.md`（Stage 1 的内容可直接从本文件第 1 节搬，补齐 2–5）。
2. 同步 `project_docs/CANON.md`（新增一条 V5 实测口径）、`project_docs/evidence/EXPERIMENT_REGISTRY.md`（把 V5 条目状态由「已注册待执行」改为实测）、`project_docs/LOGS.md`（续号 `LOG-20261126-11`）。
3. 论文修订按 [HANDOFF_2026-11-26_V5.md](HANDOFF_2026-11-26_V5.md) 第 4 节清单执行（命题 1 严密化、§4.3 非单调可行域、算法 1 七处细节、计时协议措辞、§5–§6 十项一致性修正、表 4/8/10 补列、图 3(d) 与图 4(c) 标注）。
4. 提交按路径逐条 `git add`，**禁 `git add -A`**（工作区仍有大量历史未跟踪的 QA 预览与夹具输出）。

---

## 7. 环境速查

- Windows 工程根 `D:/BaiduSyncdisk/01_Papers/03_FAECO`；WSL 对应 `/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO`。
- V5 脚本与收据：`project_docs/evidence/tcad_v5_revision_20261126/`。
- 各阶段原始产物根：Stage 1 `/home/toylog/faeco_v5_step1_20261126_v1`；Stage 2 `/home/toylog/faeco_v5_step2_dedup_native_20261126_v1`；Stage 3 `/home/toylog/faeco_v5_step3_multibudget_20261126_v1`；Stage 4 `/home/toylog/faeco_v5_step4_probe_sens_20261126_v1`；Stage 5 `/home/toylog/faeco_v5_step5_riscv32i_tc_20261126_v1`。
- Python 用 `.venv/Scripts/python.exe`（Windows）或 WSL `python3`；EDA 只在 WSL。
