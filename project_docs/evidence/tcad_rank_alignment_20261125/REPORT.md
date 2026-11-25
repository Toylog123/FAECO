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

根按旧 v2 独立核实同一 CONTROL、工具、原门、筛选付费和 18 项候选。阶段核验工具两项测试通过，分别检查共同下限对应的实际实收，以及固定与 FAECO 达到同一实收面积的时间比较。前九门实物证据、入口与开跑记录已推送 `c711f813`。

### 六臂运行回执

- 正序固定 `cell_01/arm.json` SHA-256 `7d2c47f4e822024ecc17dea1eecd23d1e669177a08045ec177432d5d11e23939`，4 派／3 成且全过。前 3／6／9 门依次实收 26.2752／48.7968／75.072 µm²，正式窗口首达 140.944343126／217.972797309／534.264250401 RAW s，五个共同下限全部达成。第 4 个候选的 DRT／RCX 在 RAW 硬窗裁剪，末调用停止晚于截止 0.088810127 s。正序单门的新鲜排名已过并启动首个候选。
- 正序固定前缀独验 `verification_prefix_01.json`（`05e1d82e6f395f4d8224889801dc74298c10e98db0e0e212d94bc0c0e6e5a4a9`）。同旧 v2 正序固定相比，相同实际面积 26.2752 µm² 的首达时间由 205.271893856 降至 140.944343126 RAW s，固定窗终由 52.5504 增至 75.072 µm²。当共同下限为 45.0432 µm²，两次首达分别 513.590335 和 217.972797 RAW s，实际收回 52.5504 和 48.7968 µm²。第 3 个候选现场重跑得到和阶段一一致的 ODB／DEF／网表 SHA 和三角读数。
- 正序强单门 `cell_02/arm.json` SHA-256 `cbe37d4d3841d27ab7b83bcb69662895eccf72601e9a1641c6c3d83a319b691f`，8 派／7 成全过，窗内最高 57.5552 µm²，末次 DRT／RCX 裁剪 stop−deadline +0.080968539 s。0.01% 首达 140.512734183 RAW s、实收 8.7584 µm²；同实收 26.2752／48.7968／57.5552 µm² 的首达分别 288.690463833／514.961482155／590.992202129 RAW s。两臂独验 `verification_prefix_02.json`（`e21c24ede6a35b8dfe1bbc747f6518d84f3f8cdee444c7e5719c47d7843e527a`）。旧 v2 正序单门同实收 57.5552 µm² 用 582.955503649 RAW s。算法与排序相同的两次实测相差 8.037 RAW s，后续小幅时差需按复跑量级解读。正序 FAECO 已新排并派出相同前三门。
- 正序 FAECO `cell_03/arm.json` SHA-256 `c962c185cc92f1305722224842e3a8936334a942a16add713f3ab073ec50f543`，4 派／3 成全过，前三个实收 26.2752／48.7968／75.072 µm² 首达 141.325963060／217.747515805／534.574689086 RAW s。以旧 v2 正序 FAECO 的最大 45.0432 µm² 为共同下限，旧、新首达分别 417.688848587、217.747515805 RAW s，实际交付分别 45.0432、48.7968 µm²。末次 DRT／RCX 裁剪 stop−deadline +0.083536492 s。无 hold 延后、二分和拒收缓存复用，FAECO 优先级准备 0.248360685 RAW s。三正序臂独验 SHA-256 `c8b7bbca25e5e8dac309292717ffe0b27780d67169310525d70711414e124979`，固定与 FAECO 之间三个精确实收时间差均小于 0.4 RAW s，四个累计派发动作集合逐项一致。两九门端点 ODB／DEF／网表／DRC 和三角时序同，去单条 `*DATE` 后 SPEF `cmp` 一致，归一化 SHA-256 `b42b639ef95ab889302ed5757e4a23d4fda6446b7f8960629f5473955337e1b1`。反序待完整验收。
- 反序 FAECO `cell_04/arm.json` SHA-256 `e0f68ba009a9b515ed5000bc53aadd08aff654c6434006aecfbec1a373d30153`，复现 4 派／3 成全过，四次累计动作与正序一致。前三实收 26.2752／48.7968／75.072 µm² 的首达为 141.475853083／217.274253568／531.074738135 RAW s。末次 RAW 裁剪 stop−deadline +0.083892178 s；无 hold 延后、二分和拒收缓存复用，优先级准备 0.247030401 RAW s。反序单门已启动。
- 反序单门 `cell_05/arm.json` SHA-256 `fdca598d198194781dec435da7064a70e6f782457def503af5dda1133297dda2`，8 派／7 成全过，0.01% 首达 141.768920730 RAW s、实收 8.7584 µm²。实收 26.2752／48.7968／57.5552 µm² 首达 293.466827445／521.008553904／597.310479761 RAW s。末次 DRT／RCX 裁剪 stop−deadline +0.090423441 s。末臂反序固定已启动。
- 反序固定 `cell_06/arm.json` SHA-256 `41e4fb0b039de25c9d1bfc716fc0f3cd26df4e5fcdba83bd06a797ba417bcb66`，4 派／3 成全过，窗终 75.072 µm²，末次 RAW 裁剪晚 0.086843716 s。六臂生产 rc0、包装 4,043 s。独验 6/6、rc0、用 15 s，32 派／26 个完整合格端点／6 个末次裁剪。六次现场同榜排序各为 1.490–1.704 RAW s，均为臂内第一笔工具费用。六个候选工具停止时间超 RAW 截止 0.080969–0.090423 s，截窗候选均未计入回收。

### 720 RAW s 完整比较

下表的阈值首达累计各臂的筛选与实跑排序费用，单位 RAW s，每格为正序／反序。达到下限时的实际交付面积另列。

| 共同面积下限 | 固定三门 | 灵敏度单门 | FAECO | 实收面积（µm²，固定／单门／FAECO） |
|---|---:|---:|---:|---:|
| 0.01%（7.14272544 µm²） | 140.944／141.980 | 140.513／141.769 | 141.326／141.476 | 26.2752／8.7584／26.2752 |
| 26.2752 µm² | 140.944／141.980 | 288.690／293.467 | 141.326／141.476 | 26.2752／26.2752／26.2752 |
| 45.0432 µm² | 217.973／217.939 | 514.961／521.009 | 217.748／217.274 | 48.7968／48.7968／48.7968 |
| 52.5504 µm² | 534.264／530.897 | 590.992／597.310 | 534.575／531.075 | 75.072／57.5552／75.072 |
| 57.5552 µm² | 534.264／530.897 | 590.992／597.310 | 534.575／531.075 | 75.072／57.5552／75.072 |
| **720 RAW s 内最高合格实收** | **75.072 µm²** | **57.5552 µm²** | **75.072 µm²** | 正反序各自相同 |

旧 v2 与同排名重跑相比，固定 52.5504→75.072 µm²，FAECO 45.0432→75.072 µm²，强单门复现 57.5552 µm²。固定达到同实收 26.2752 µm² 两序分别节省 64.328／62.707 RAW s。FAECO 首达至少 45.0432 µm² 分别提前 199.941／202.069 RAW s，实收由 45.0432 增至 48.7968 µm²。新版两种批处理在同实收 26.2752／48.7968 µm² 的比较分别比单门快 147–152／297–304 RAW s，窗内最大回收均多 30.43%。固定与 FAECO 全部四次派发同动作，三个共同实收的两序时间差均不超过 0.67 RAW s。两个 FAECO 臂保留的 hold 延后、二分和 setup-only 去重均未触发。因此该开发对照分离出了起始排序与共用批宽的作用，未测得 FAECO 反馈相对同榜固定的增益。

独验核对各角 setup WNS 损失门 60 ps、TT TNS 损失门 600 ps、SS TNS 损失门 208,627.916436 ps、绝对 hold 0 ps 与相对 hold 容差 0.001 ps，以及原电气、全块 DRC／天线和 SEC。四个批处理最佳九门端点同 ODB `522ce2a747fede96fcaa5ce1c077066d750d6c88c3cbd43fa3d22e61acbf8c9e`，去单条 `*DATE` 后 SPEF 也同（`b42b639e…`），三角指标见阶段一表。单门两序最佳 ODB 相同，FF／TT／SS setup WNS 变化为 −0.129230／+0.068834／+0.005329 ps，setup TNS 变化为 0／+15.166535／−7,517.883205 ps，hold WNS 变化为 −0.000055511／0／+0.000222045 ps。两类最佳端点三角无新增负 setup，独立 DRC／天线 0、SEC 4,559／0。`riscv32i` 已用于本轮排序改动的选择，跨设计的反馈增益仍需另证。

原始目录 `/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i/{probe_ranked_nine_20261125_v1,matrix_rank_aligned_v1}` 保留。正式 [协议](RISCV_RANK_ALIGNED_PROTOCOL.json)、[结果](RISCV_RANK_ALIGNED_RESULTS.json)、[独验](RISCV_RANK_ALIGNED_VERIFIED.json) 与原件逐字节一致，SHA-256 依次 `49ef72e393042902d844fb846df8045747d7a2adfc0dea47c2001f95c7259392`、`7284bbc0a33d2bcab77d39548397bb72bbd80be91f970d04010530b468bf861d`、`38900fbf8f4db24b1c3d0eb72a774ac0a12b534ac1b4a71f402561a2a67910c7`。
