# riscv32i 统一灵敏度起始排序的实物对照

2026-11-25，工作基线 `1c3e17ad`。旧 v2 两序的灵敏度单门、固定批次、现行去重 FAECO 窗内最多回收 57.5552、52.5504、45.0432 µm²。固定与 FAECO 从原冻结池序开始，灵敏度单门从 TT 排名开始。本轮仅将三法的起始排名对齐，检验固定批次和 FAECO 能否在同一排序下改善时间与可交付面积。[旧 v2 报告](../tcad_wallclock_schedule_20261125/REPORT.md)

## 阶段一：前 9 项的累计端点

先从旧 v2 的强单门灵敏度顺序取最前九项，精确绑定实例与替换 master，作为一条累计提议，从原冻结已布线起点全新评估。保留原在线候选 DRT/RCX、三角 STA、setup／hold、独立全块 DRC、天线、电气和非空全网表 SEC。过去已有独立核对的前 3、6 项合格端点作为诊断参照。记录每阶段真实工时、是否重试、原拒因及最终验收。该诊断不会提供阶段二的跨臂物理缓存或候选成绩。[既有精确前缀](../tcad_wallclock_schedule_20261125/RISCV_RANKED_PREFIX_REPLAY.json)

旧正序 `ranking.json` SHA-256 `200b402d5af592a794c05984524d6429a8ef8f61397bd2cfac8d4aa9f5a58bf0`。冻结顺序的前九项实例为 `_4134_`、`_4713_`、`_4162_`、`_4718_`、`_3672_`、`_3900_`、`_6374_`、`_7128_`、`_3714_`。按原候选池的功能单元面积，九项静态减量合计 75.072 µm²，实际合格回收待验收。

## 阶段二：同排位下的六臂纯墙钟对照

三法共享原冻结 CONTROL、I/O 与三角 Liberty、18 项候选池、在线诊断后端和原时序／物理门。每臂从同一参考新做 TT 排名，须与冻结的强单门顺序逐项一致；原筛选费用 64.099573641 RAW s 和各自的新鲜排名费用计入本臂 720 RAW s。每个候选按相同的阶段限时实际执行，池耗尽或截窗分别记录。所有计算和输出绑定本臂原件。完整正反序的具体次序在实发前写入运行配置。

| 方法 | 共享排序之后的派发 |
|---|---|
| 灵敏度单门 | 按排名逐个验证，验收后更新累计集合 |
| 固定三门 | 每批最多三项，采用同一固定批次行为 |
| 排名对齐 FAECO | 原批宽、原失败与 hold 反馈规则，保留已完整确定的 setup-only 同动作拒收去重 |

冻结比较下限为原功能面积的 0.01%（7.14272544 µm²）以及 26.2752、45.0432、52.5504、57.5552 µm²。各项记录本臂窗口内首个达到下限并完成原验收的时间及实际交付面积。未达时标明截窗或池耗尽，不外推完成时间。另记录固定时窗内最佳合法面积、逐角时序及 SEC。与旧 v2 先按同方法同顺序配对，再比较已对齐排名后的固定与 FAECO。用共同面积目标和真实处理次数解释相似或负结果。`riscv32i` 已用于选择本轮改动，结果作为开发对照，独立迁移需要另证。

## 运行与核验回执

按两阶段记录实际命令、输出根、输入／源／工具哈希、CPU 绑定、超时、生产与独验回执。终态表包括逐法首达窗口、最佳端点及相对旧 v2 的变化。

### 前九门实发配置

拟用 CPU 0–5、四线程、原 DRT 64 轮上限、单次 pin access、嵌入导引，原在线后端保护非触达信号网。实际独立 DRC 证据授权最多一次邻网重试。候选阶段限时为 DRT 240 s、每角 STA 180 s、SEC 210 s，候选总窗口 720 RAW s，外层统一超时 800 s。筛选、排序和零动作的既有输入只作该诊断的冻结绑定，完整阶段二各方法现场付费。原工作根不覆盖。

无 EDA 预检绑定 46 条直接信号网，入口 SHA-256 `fba97b8007ac8526f891b9feac47cb5d747a8438ea6029bd4f738312f6bc1322`，预登记收据 SHA-256 `6fe3dfe22f073d395e7a6271ffe3c8d24d735577c12c22b3ea00f996c73893b8`。若 DRT/RCX 已完整且普通 SEC 因其它门拒收未启动，单独对实布网表补诊断 SEC。通过诊断 SEC 的拒收端点仍沿原门记账。

18:55:36（UTC+8）按以下命令实发，包装 PID 511、Python PID 513，exec session 27817。预诊断完成并记录 0 marker，随后进入 DRT/RCX。初次资格回执和阶段二臂不读取该候选终态属性作为输入。

```bash
repo=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
r=/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i
bash "$repo/code/scripts/run_with_timeout.sh" 800 taskset -c 0-5 python3 -B \
  "$repo/project_docs/evidence/tcad_rank_alignment_20261125/probe_ranked_nine.py" \
  "$r/matrix_qualified_v2" "$r/probe_ranked_nine_20261125_v1"
```

初次详细布线、RCX 和三角 STA 完成。完整／解锁 DRC 报 10 个 marker，其中 `_0995_` 与 `net1234` 的 Short 9 个、Cut Short 1 个；报告 SHA-256 `ad421440c499ede9e96a1f830afbb638fdc0e8b7c897d3cba86f23ec157eb0b9`。`trial/retry_decision.json`（`69a60c0e1b0ee169f626fa45f50c65b06aaa8214762e0d9abe0d0e4955d68723`）据此仅将 `net1234` 加入许可范围，已派发一次邻网重试。

### 前九门验收

重试许可 47 网、保持保护 5,501 网。独立全块 DRC／天线 0，原三角时序、电气及 SEC 4,559／0 全过，实布回收 **75.072 µm²**（约 0.1051%）。根以既有 `audit_logical` 重查九项动作、绑定与原验收。各量相对同一冻结零动作测量，负的 setup 变化表示损失。

| 视图 | setup WNS 变化（ps） | setup TNS 变化（ps） | hold WNS 变化（ps） | 新增负 setup 端点 |
|---|---:|---:|---:|---:|
| FF | −0.435652 | 0 | +0.003664 | 0 |
| TT | −0.329958 | −308.133963 | +0.003941 | 0 |
| SS | −0.376588 | −6,293.703336 | +0.017986 | 0 |

端到端 **325.449205905 RAW s**，包装 346 s／rc0。预诊断 10.544134 RAW s，初次／重试 DRT 与 RCX 221.039090／48.168780 RAW s，普通 SEC 9.564701 RAW s，诊断 SEC 分支未触发。上述候选端到端费用采用既有筛选、排名与共享零端点；六臂正式同预算比较另记实际费用。证据 `results.json` SHA-256 `223fd08596d4a766e16f315f4ed3d70976f85f154807252c202ce3b639b638ab`、逻辑 `0afb9a703000b2abb81b64dfab4646c85a5ad212fbaa0b5d03e5d8f611297f2e`、物理 `dcb7182db7d74e43082cb805892de8884a0c9f307d5053333ec19592d1591601`。九门端点说明该累计组合可由原后端验收，三种动态策略能否在其各自窗口找到相同或更好端点由阶段二实测确定。

已逐字节核对并入仓 [协议](RISCV_RANKED_NINE_PROTOCOL.json)、[结果](RISCV_RANKED_NINE_RESULTS.json)、[独验](RISCV_RANKED_NINE_VERIFIED.json)。独验 SHA-256 `5c11f0b7a7ffe9c2ec8e23fa47f4cdcedc934ea5d3873c27b1ca02c6d09c16ca`。

### 比较矩阵无物理预检

入口 `run_rank_aligned_wallclock.py` SHA-256 `1138f1c0f43a83d1934b8753d0faef491fdc5c7cd4a51b62ffbf48e1ec2fa00d`。绑定旧 v2 原协议 `a768316f…`、完整独验 `ef949a66…`、正序强单门排名 `200b402d…` 和反序 `81aadfe7…`，两榜 18 项顺序一致。阶段二拟固定→单门→FAECO，随后完全反序，CPU 0–5、四线程、DRT 64 轮、240／180／210 s 子工具限时、外层 6,500 s。沿用 720 RAW s 与 0.1 s 检查间隔、64.099573641 RAW s 原筛选费用。每臂实际新跑的 TT 排名在策略时限第一个工具调用计费。输出拟为原 `riscv32i` 工作根下的 `matrix_rank_aligned_v1`，待阶段一结束后实发。

无物理预检原件 `/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i/preflight_rank_aligned_v1/rank_alignment_inputs.json` SHA-256 `6dc2b91bf5ac659e75af4aba009e10515c056c66af83931a1738bcfafd47721d`，基础资格输入 `e7e29999721a0373f80bfc5c2507ee0f39025aff6d043b475ba228186ffa9a3f`，状态确认协议和原件已核、0 臂完成。三个无物理专项含旧臂账本入口的检查。正式运行另记。

### 比较矩阵实发

阶段一工具完全退出后，19:02:11（UTC+8）启动正式六臂，包装 PID 433、Python 435、exec session 32766。原件 `matrix_rank_aligned_v1.stdout.log` 首行记录完整命令。`qualified_inputs.json` 和 `rank_alignment_inputs.json` SHA 与持久预检一致。运行目录只引用旧 v2 冻结协议及排序，不引用阶段一任何候选产物。

```bash
repo=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
base=/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1
r="$base/sky130hd/riscv32i"
bash "$repo/code/scripts/run_with_timeout.sh" 6500 taskset -c 0-5 python3 -B \
  "$repo/project_docs/evidence/tcad_rank_alignment_20261125/run_rank_aligned_wallclock.py" \
  --rank-source-run "$r/matrix_qualified_v2" --confirmed-only --top riscv --pdk sky130hd \
  --control-dir "$r/results/sky130hd/riscv32i/base" \
  --control-drc "$r/reports/sky130hd/riscv32i/base/5_route_drc.rpt" \
  --original-sdc /home/toylog/faeco_eda/orfs/flow/designs/sky130hd/riscv32i/constraint.sdc \
  --views-json "$r/qualification/CONTROL.json" --sta "$base/sta_native.py" \
  --sec "$base/sec_native.py" --threads 4 --droute-iters 64 \
  --route-timeout 240 --sta-timeout 180 --sec-timeout 210 \
  --screen-pool "$r/screen_qualified_v1/screen/screen_pool.json" \
  --screen-receipt "$r/screen_qualified_v1/screen/screen_receipt.json" \
  --out "$r/matrix_rank_aligned_v1"
```

正式 `protocol.json` SHA-256 `49ef72e393042902d844fb846df8045747d7a2adfc0dea47c2001f95c7259392`，原 `qualified_start` SHA 与 v2 一致。共享严格零 `preflight/zero/result.json` SHA-256 `6254e637c53f89d3f76ab9d6df99bd479dbf60c53d824d29ed0c77ea18815eb6`，原面积 71,427.2544 µm²、失败集合空、独立全块 DRC 0、SEC 通过。正序固定第 1 笔工具调用重新计算 TT 排名，用 1.571247283 RAW s，18 项与旧榜逐项同序，`cell_01/fixed/sensitivity/ranking.json` SHA-256 `2c1d935e1286bf9f276c1e8dba82955e7938949d1c6655e2e775cf85785cff86`。第一次候选按该排名派发 `_4134_`、`_4713_`、`_4162_`，共 15 条直连信号网。

根按旧 v2 独立核实同一 CONTROL、工具、原门、筛选付费和 18 项候选，且新增一项下限与实际实收区别的工具检查已通过。
