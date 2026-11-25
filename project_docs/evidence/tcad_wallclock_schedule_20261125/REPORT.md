# 两工艺纯墙钟面积回收对照

2026-11-25，工作基线 `b73d92b8`。本轮检验统一墙钟约束下，一次即时拆分后让出物理验证机会给未试新批，能否提高可交付面积。已有结果说明，某些失败处理会消耗后续候选的验证机会，而同面积的两种派发可能产生不同墙钟与时序结果。[未决项 OI-105](../../OPEN_ISSUES.md)

## 预登记协议

先在开发设计上验证新规则和计时闭环。开发结果连同失败原件保留。规则、源文件与关键参数冻结后，在两个 PDK 中分别核对未用于调参的设计。留出拟 SKY130HD `riscv32i` 与 ASAP7 `ethmac`，各自在原约束下完成冻结起点资格后才能做正式计时。留出对象的起点资格和选择依据在运行前记录。

| 方法 | 派发约束 |
|---|---|
| 现行去重 FAECO | 使用现行排序、失败处理及同一冻结起点上已完整确定的 setup-only 拒收去重 |
| 固定批次 | 按冻结池的固定批次次序访问 |
| 灵敏度排序单门 | 按冻结参考的实际灵敏度派发单门，专用排序费用进表 |
| 一次即时拆分 | 从现行去重 FAECO 出发，每个失败批最多立即派发一次拆分子批，后续优先派发已排序但未试的新批。这项改动以外的候选和后端规则共享 |

变体保留旧首次相对 hold 触发的重排。有未试新批时，多门拒收只立即检查左子组一次；右组和更深的拆分排队，待新批耗尽后继续。立即尝试失败的单门，只有累计接受集合实际改变后可重试一次。无新批时沿用原拆分推进。

每臂为 720 `CLOCK_MONOTONIC_RAW` 秒。计入实际应付的公共筛选、策略排序、预诊断、DRT/RCX、逐角 STA、独立 DRC／天线、SEC、失败与窗尾已启动阶段。纯墙钟模式 `max_evaluations=None`，由共同物理层裁剪到时限；实际候选数用于解释结果。完成联合验收的时刻须在窗内才计面积。记录自然结束、截止、证明未完成和资源异常等不同终态。

各设计在臂间固定原 I/O 和冻结起点、三角库与 RCX、池和后端版本。最终端点保持原 setup／hold、电气、独立全块 DRC、天线与非空 SEC。固定窗口的最大合法回收与同等面积的实际首达分开报告；记录首达实收值、未达与所有零回收臂。既有结果仅作为历史上下文。[AES 强单门原对照](../tcad_ibex_20261123/AES_SENSITIVITY_GREEDY_REPORT.md) · [UART 去重原对照](../tcad_holdout_20261123/UART_REJECTION_DEDUP_REPORT.md)

## 启动与配置回执

在发出开发与各留出前补录确切命令、执行顺序、硬件绑定、原门、候选池及运行源 SHA、输入清单和输出路径。记录启动后读出的配置摘要与冻结清单的一致性。

适配器 opt-in 通过两个专项模块共 51 项测试，耗时 14.65 s；新增两用例在实现前按预期失败。UART 开发共用现有原约束的 18 项冻结池，每臂计 81.563830427 RAW s 的绑定筛选费用。零动作验收是共享起点项。各臂新执行全部候选物理验收。

Windows Python 3.11 收集既有证据脚本时无法解析需要 Python 3.12 的 f-string。使用正式实验的 WSL Python 3.12.3 重跑专项集成回归，68 项通过，耗时 14.66 s。独立验收入口 `verify_wallclock_matrix.py` 已就绪，是否通过按逐臂物理收据核验后登记。

默认关闭新选项时，500 个确定模拟用例对 `b73d92b8` 的轨迹和端点全部一致。覆盖有限次数、不同批宽、hold 延后、setup 去重和末次预留。此复核用来检查默认兼容性。

纯墙钟及交错调度适配器与新增测试冻结在 `50aced718ace7d6016fcac22ba2d367704ca7e09`，该版本已推送 `origin/main`。

只读预检使用 `PYTHONPATH=code/src python3 -B scratch/replay_wallclock_prefix.py` 和同范围 18 个已有的唯一物理点。旧去重调度在去掉六次上限后，第六次是历史未评估的完整批；交错调度先多验 `_0562_` 单门（历史 SS 拒），在第五次遇到历史未评估的新累计四门。重放严格停在第一个未知提议，确认新规则改变真实派发，不能从这个前缀给出胜负。

### UART 开发配置

15:19:46（UTC+8）按以下命令启动，包装进程 334、Python 进程 412，exec session 44907。标准输出在 `/home/toylog/faeco_tcad_uart_wallclock_20261125_v1.stdout.log`，实发协议 SHA-256 `6d36c36ac5e764ed28e5c77f72ed8c167c19083930e2f220575f3f4e34773aab`。正序为 `fixed_online`、`single_sensitivity`、`faeco_dedup`、`faeco_interleave_dedup`，继而完全反序。冻结 `0.01%` 主阈值，另在原轨迹回读 `0.15%`、`0.25%`。灵敏度单门臂在时限内亲自执行 TT 排序查询，两 FAECO 臂计入 incident priority。每臂通过同一 fresh 在线诊断后端。

```bash
bash /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/code/scripts/run_with_timeout.sh 6500 taskset -c 0-5 python3 \
  /mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/project_docs/evidence/tcad_wallclock_schedule_20261125/run_wallclock_matrix.py \
  /home/toylog/faeco_tcad_uart_online_20261125_matrix_v2 \
  /home/toylog/faeco_tcad_uart_wallclock_20261125_v1
```

| 绑定 | SHA-256 |
|---|---|
| 开发入口 | `62c69d4e4525df7dce1042ee6ecaa19df6594dd49b5aa61d0021005cd77c7d5c` |
| 调度适配器 | `c56825f954b2d88fa082728e6c92f45baf1268cc47301a02a98c24e101fc3967` |
| 源 UART 在线协议 | `90bf70bb080d5544d51265e575c3ec94ff72f6342fe6b9aaf452c5476d374a4f` |
| 冻结 18 项候选池 | `73bc816db40e5ca76e4a1dd34392dc1ab9bfeba3a7b9c0cff196ce2188b8fdff` |
| 实测筛选费用收据 | `e3f6003fd6a0c97c8132798c75282308d02550e24eeec26999c58fb104419f56` |

新鲜共享零动作过原门，17.328252706 RAW s，面积 79.00902 µm²，独立 DRC=0、SEC 567/0。`preflight/zero/result.json` SHA-256 `f76436278bc46d83e2f34b16a0c681154061191790b87757db021e2d5ab582be`。输入沿用 270 ps 周期、54 ps I/O、66.270 ps 虚拟时钟延迟。协议实际 `logical_dispatch_cap=null`、批宽三、单次 pin access，setup WNS 损失预算 2.7 ps，FF／TT／SS 的 setup TNS 预算 27／27／136.9736502 ps；每角绝对 hold 非负且相对 hold 容差 0.001 ps。

旧的固定和单门调用入口需要正整数，实发配置以 `18 + 1` 表示池耗尽。它们每次必消耗至少一项未访问动作，因此在 18 项池上先自然结束。两种 FAECO 使用真正的空值上限，由候选池、待处理子组和 720 秒共同决定终点。

### 留出资格

SKY130HD `riscv32i` 起点制备于 15:05:33（UTC+8）写入锁定命令并启动。原始 SDC 主／虚拟时钟 6.0 ns，非时钟 I/O 延迟 1.2 ns，时钟延迟 0.775 ns。CPU 6–11、四线程、外限 1,800 s，ORFS 目标 `6_report.log`。WSL 工作目录 `/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i`。`command.sh` 和 `input_manifest.log` SHA-256 分别为 `77a6e53024d76b91cbf615a84192b466d9c5fe1d7a703b44e56e5e34efe942fc` 和 `1d1e79668ab25047ce72e98d42df3d37482b48bb8895d079ce06f6d445add14e`。

原 ORFS 784.87 s、rc0；原始与导出 SDC 的 104 条规范命令全部匹配。独立全块 DRC、天线、电气均零，起点 SEC 4559/0。FF／TT／SS hold WNS 为 +373.364173／+579.221338／+2019.309830 ps，hold TNS 全零。setup WNS 为 +1855.053／−474.192／−20633.326 ps，冻结并保留原有 TT／SS setup 违例。已复制 `qualification/CONTROL.json` 的原 87,033 字节，逐字节比较一致，SHA-256 `5c85e150d8d8073af9dfef15fa59467b91b678a84e0dadff20ba0fed4902e9e9`。三次正式视图资格 STA，候选 EDA 为零。[原资格收据](RISCV32I_CONTROL.json)

使用 `run_qualified_wallclock.py --confirmed-only` 执行固定、灵敏度单门、现行去重 FAECO 的正反序，保留纯墙钟、同等筛选和原验收。用 `riscv32i` 资格输入的 dry-run 已通过，回执 `/tmp/riscv_confirmed_only_r8rUq2/validate/qualified_inputs.json`，入口 SHA-256 `07ee25e24cc2e294bb8db9275abe412d4b38774f6e238650d02ee53fd6dce446`。在 UART 开发前六臂独验后冻结三方法留出，交错仅存为开发负例，候选正式发出待 UART 八臂终态。

待 UART 八臂及全机 EDA 退出后，对 `riscv32i` 单独实跑一份筛选，使用 `--screen-only --screen-workers 1 --confirmed-only --top riscv --pdk sky130hd`，CPU 0–5、统一总限 1,800 s、每筛选工具 180 s。输出为原起点根下 `screen_qualified_v1`。筛选完成后从实测收据锁定同池、同成本，再由留出六臂使用。

ASAP7 `ethmac` 待原生制备。源 SDC 保留 WB、TX、RX 的 1000／300／300 ps 原周期、200／60／60 ps 相应 I/O 延迟、229.195／55.660／76.515 ps 虚拟时钟延迟、三个逻辑独占组及 `MAX_FANOUT=10`。源 SDC SHA-256 `d65f3d82bda85026f007983fb49a16779fdfa8707a33f54c8ad3ee4b831d89a1`，原 ORFS 设计配置 `a2cfe0258f6bc2cd984746ab8b8959423613d9e6ece22614f2af38312cb3d373`。候选研究预算单独冻结，资格保持三角绝对 hold 非负、hold TNS 零、电气、原生和独立 DRC/天线、真实 RCX、源与导出约束匹配及非空 SEC。继续用 ORFS `da8f092a`、OpenROAD `b511b6a2`、Yosys 与 OpenSTA 3.1.0 的已绑二进制。计划 CPU 6–11、DRT 四线程，制备与资格外限分别为 1,800、500 s。下列命令尚未发出。

```bash
bash /home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/produce_ethmac.sh
timeout --kill-after=10s 500s taskset -c 6-11 python3 -B \
  /home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/qualify_native.py asap7 ethmac
```

两入口 SHA-256 为 `06e65f773a10eb90aead5198c1e5d3fe5121a9f9374cafb0ef2720dbe3775e05` 和 `3614247ff1aa65f93bde62499de3695516c5ec175f01eabb7fa91b9e1c0384ee`。预计资格回执为 `/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/asap7/ethmac/qualification/CONTROL.json`。

## 结果与归因

按设计、执行顺序和方法记录 720 秒内最大合格面积、共同目标首达时间及真实首达面积、逐角时序变化、派发／工具调用次数、重复抑制和拒收原因。保留端点绑定、独立核验和原件归档收据。

正序固定批次首臂已完成，6 次真实评估自然用尽 18 门。第三次在 155.609207824 RAW s 实收 0.17496 µm²，达到 0.01%／0.15%。第六次累计完整六门在 230.144711114 RAW s 通过，达到 0.25%，窗内最高回收 0.33534 µm²（0.424433%）。`cell_01/arm.json` SHA-256 `2ee47d78dd01e931f5ed5d1be68af6f89772fba642b97778a0468c79594c1f60`。整矩阵独验待全部发布。

正序灵敏度单门自然完成18 次实际物理评估，查 TT 排序耗时 1.361633380 RAW s。三阈值首达为 108.269／134.134／159.555 RAW s，分别实收 0.08748／0.17496／0.26244 µm²。窗内最佳为 0.77274 µm²（0.978040%），来自第 18 次物理评估，`cell_02/arm.json` SHA-256 `20de06306cac2ecbbbf5b5043d6e03e8ee95f8038fb4e7a8e6bc7b01bfe7ac6c`。

正序固定和灵敏度单门两臂已通过独立验收，`verification_prefix_02.json` SHA-256 `c886e7d5673a7d5a5ed36e7802be853f702d713e9ecb6ff175dd8ecae246f598`。

正序现行去重 FAECO 19 次完成，自然结束，跳过一次同臂已完整 setup-only 拒收重复评估。最大 0.83106 µm²（1.051855%）在第 16 次，较同序单门多 0.05832 µm²。三阈值首达 155.122／204.318／229.496 RAW s，实收 0.08748／0.14580／0.32076 µm²。前三臂独验 `verification_prefix_03.json` SHA-256 `c59ab0316a3fda63bd369fb19a1aa21a2514ea336943a1928983072ce18c8e75`。

正序交错去重 FAECO 25/26 完成，最后一次 DRT/RCX 受总墙钟裁剪。三阈值首达 180.382／205.502／205.502 RAW s，实收 0.08748／0.26244／0.26244 µm²。窗内最好为 0.75816 µm²（0.959587%），较同序现行去重少 0.07290 µm²、较灵敏度单门少 0.01458 µm²。原件 `cell_04/arm.json` SHA-256 `c0c9ea43e562381939b7cd30bb804cb35822f3c57276c4115c15da233765727d`。反序已启动。

正序逐请求中，两 FAECO 均验收八个检查点。现行 11 次已完成拒收含 9 次 hold 与 2 次 FF setup，交错 17 次已完成拒收含 14 次 hold 与 3 次 FF setup。交错早先单试 `_0562_` 由 SS 拒收，第 25 次它随不同累计前缀通过。

正序四臂独验通过，`verification_prefix_04.json` SHA-256 `f5fb0cfade757a11baa770f6722e2692f48fc1caba78d14cb0ee527f22109a3e`。现行 #13/#15 和交错 #10/#12 各有一对动作、范围、拒因、ODB/DEF/V、去日期 SPEF 和逐角结果相同的纯 hold 拒收，因此双方各重复一次。交错第 26 次裁剪请求的 12 个动作静态减量相加为 0.81648 µm²，仍小于现行已验收终点的 0.83106 µm²。正序差额也涉及先前派发选择。

按已完成请求的 `finished_raw−admitted_raw` 加总，现行／交错在 hold 拒收用 221.061／344.106 s，其他拒收用 48.631／74.197 s，合格请求用 203.241／204.384 s。交错增加的已完成物理工作主要落在 hold 拒收，超窗请求另计。

反序交错仍为 26 派发、25 完成、8 过、14 hold 拒、3 FF setup 拒，尾次超窗，最好回收 0.75816 µm²，最佳动作及 ODB／DEF／网表和全部视图与正序一致。三阈值首达 180.004／205.270／205.270 RAW s，实收 0.08748／0.26244／0.26244 µm²。`cell_05/arm.json` SHA-256 `d71f13ae6e3b92acb6c7f7ad0b2eb3671d20cc90808b505faf73a2541c3699ad`。

前五臂独验 `verification_prefix_05.json` SHA-256 `1069d80ed775b644b35ebc1cfe2746395bfd09130718ec3540f53ac479218946`。反序尾次与正序同一 12 门，静态潜力同为 0.81648 µm²；预诊断工作完成，DRT/RCX 由剩余墙钟从 240 s 裁至 13.555 s，未产出最终详细布线／寄生收据。交错规则在开发结果中保留为负例，留出设置待完成现行与基线反序后锁定。

反序现行去重 FAECO 自然完成 19 次，避免一次 setup-only 重复验收。第 16 次的最佳回收 0.83106 µm² 及其物理产物与正序一致，三阈值首达 156.073／205.413／230.476 RAW s。两种反序 FAECO 都有 8 次通过；现行／交错在已完成 hold 拒收的时间为 220.567／343.006 s，其它拒收为 48.987／73.753 s，合格请求为 204.810／204.308 s。`cell_06/arm.json` SHA-256 `3bc43aae0711edd1c7c57e5da0da57cb2f18c7e7384db7b10b1bffc175bb8471`。

首六臂独验 SHA-256 `d224b92481a83a322bffdb0eb9f10085481e4c89b523f5c1f860d0dd58b2ef43`。同实收 0.77274 µm² 的正序回读为灵敏度单门 535.553 RAW s 与现行 FAECO 429.983 RAW s，后者早 105.569 s。反序在 535.004 和 431.482 RAW s 达到同一实际面积，现行 FAECO 早 103.522 s。

反序灵敏度单门 18 次自然完成，现场 TT 排序 1.358792412 RAW s。三阈值首达 108.366／134.077／159.633 RAW s，实收 0.08748／0.17496／0.26244 µm²。最高 0.77274 µm²。原件 `cell_07/arm.json` SHA-256 `a201b4b8d2a44c40d3523e7845b25441f55deedbc5094e30d4cfe99c65ea33ad`。

反序固定 6 次自然完成，三阈值首达 154.824／154.824／227.540 RAW s，实收 0.17496／0.17496／0.33534 µm²，最高 0.33534 µm²。原件 `cell_08/arm.json` SHA-256 `2194318138f06d23fe23d79a6b3c5389af0d68a879c119817d377aa2fe00b06c`。

### UART 开发八臂结果

| 调度 | 正序／反序完成数 | 两序最大合格回收（µm²） | 0.01% 首达（RAW s） | 0.15% 首达（RAW s） | 0.25% 首达（RAW s） |
|---|---:|---:|---:|---:|---:|
| 固定批次 | 6／6 | 0.33534 | 155.609／154.824 | 155.609／154.824 | 230.145／227.540 |
| 灵敏度单门 | 18／18 | 0.77274 | 108.269／108.366 | 134.134／134.077 | 159.555／159.633 |
| 现行去重 FAECO | 19／19 | 0.83106 | 155.122／156.073 | 204.318／205.413 | 229.496／230.476 |
| 交错去重 FAECO | 25／25 | 0.75816 | 180.382／180.004 | 205.502／205.270 | 205.502／205.270 |

八臂共 138 派发、136 完整，138 次预诊断、138 次 DRT/RCX 启动、408 次逐角候选 STA、136 次独立 DRC、60 次候选 SEC、2 次排序 STA。两次截止均来自交错末次 DRT/RCX。生产 rc0，统一包装耗时 3,486 s。全八臂独立验收 rc0，三份仓库收据与 WSL 逐字节一致。[协议](UART_WALLCLOCK_PROTOCOL.json) · [结果](UART_WALLCLOCK_RESULTS.json) · [完整独验](UART_WALLCLOCK_VERIFIED.json)

四个方法的每组最佳端点两序一致。现行去重相对强单门的净回收多 0.05832 µm²（7.547%），到相同 0.77274 µm² 两序早 105.569／103.522 RAW s。三个小阈值均由单门先达。以共享零动作点为参考，现行最好端点最大逐角 setup WNS 损失 1.363215 ps，SS TNS 改善 6.594725 ps，无新增负 setup 端点。四种最佳端点均通过原三角 hold、电气、独立 DRC／天线及非空 SEC 567/0。交错保留为开发负例，独立留出保持现行三方法对照。原件归档另记。

### SKY130HD riscv32i 真实筛选

UART 八臂及物理工具退出后执行一份实际筛选，包装 PID 469、Python 471，CPU 0–5、单 worker、配置总限 1,800 s、每子工具 180 s。`/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/sky130hd/riscv32i/screen_qualified_v1.stdout.log` 记录完整实发命令及 rc0，包装时间 67 s。原 6,000 ps 的 TT 冻结寄生筛选门为 60 ps WNS、600 ps TNS，20 次筛查保留 18 项，两次 TT TNS 拒收。真实筛选 64.099573641 RAW s，其中基线和 20 个候选 TT 子进程合计 33.168903898 RAW s。

`screen_qualified_v1/screen/screen_pool.json` SHA-256 `748d2a2866764f71672e95b968dd1122cf1faf3ecdd92f8246e781c66c01826f`，`screen_receipt.json` 为 `ea7d5a1a9a3ed519f387aa2ce83b33386d4a1f39a7800b62278134cd027570c2`。原筛选收束时物理臂 0/6。修订独验器的原 Liberty 路径识别后，原筛选证据复核通过，筛选原件保持。`independent_verification.json` SHA-256 `445a0d6fd3be225d25acb93278a8c7365c527c73aeb3a549ab536ce995463c61`。

### SKY130HD riscv32i 留出六臂

16:21:32（UTC+8）开始。PID 343／423，exec session 42647。三方法完全反序，CPU 0–5、四线程、仓库超时包装总限 6,500 s，DRT 64 轮，每次 DRT/RCX、各视图 STA、SEC 的限时依次为 240／180／210 s。实际命令可从下列参数重现，原件保存于输出目录同名 `.stdout.log` 首行。

```bash
repo=/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO
r=/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1
d=$r/sky130hd/riscv32i
bash "$repo/code/scripts/run_with_timeout.sh" 6500 taskset -c 0-5 python3 \
  "$repo/project_docs/evidence/tcad_wallclock_schedule_20261125/run_qualified_wallclock.py" \
  --confirmed-only --top riscv --pdk sky130hd \
  --control-dir "$d/results/sky130hd/riscv32i/base" \
  --control-drc "$d/reports/sky130hd/riscv32i/base/5_route_drc.rpt" \
  --original-sdc /home/toylog/faeco_eda/orfs/flow/designs/sky130hd/riscv32i/constraint.sdc \
  --views-json "$d/qualification/CONTROL.json" \
  --sta "$r/sta_native.py" --sec "$r/sec_native.py" \
  --threads 4 --droute-iters 64 --route-timeout 240 --sta-timeout 180 --sec-timeout 210 \
  --screen-pool "$d/screen_qualified_v1/screen/screen_pool.json" \
  --screen-receipt "$d/screen_qualified_v1/screen/screen_receipt.json" \
  --out "$d/matrix_qualified_v1"
```

实际 `qualified_inputs.json` SHA-256 `b4c71fde9d9f1f429b5f093382a379b9445aaf4bbd2d8da7e8c3e11c10615f2a`，每臂等额计 64.099573641 RAW s。初读为共享前置资格阶段。ASAP7 `ethmac` 起点制备在该矩阵全机计时停止后启动。

正式 `protocol.json` SHA-256 `8b979b6931ca9f5a9f5eb0a20638f5a12dbdc8a6d2a169785fd407e0fb95f419`，`logical_dispatch_cap=null`、setup WNS 60 ps。资格复测 `seed/control/receipt.json` SHA-256 `7f77c245d216b45d0e9b8301c55aab778b24ae78e98338a2d9d186366fc1c8fe`，三角 hold 与 P0 一致。

新鲜共享严格零动作通过，59.361742441 RAW s，面积 71,427.2544 µm²，独立全块 DRC／天线零，SEC 4559/0。`preflight/zero/result.json` SHA-256 `064e0d35be6b8509741f4a8d1f8158fa85ea94a6a534653a7329d4e85ddc8a4e`。固定首臂的第 1 批实际派发三门，候选耗时计入各自窗口。开发证据及留出入口已提交 `bbc28dba`。

固定正序首个合格候选是第 2 次，在 211.831371594 RAW s 验收 26.2752 µm²（0.036786%），独立全块 DRC／天线零，SEC 4559/0。第一次仅 TT TNS 拒收。候选 `cell_01/fixed/02/result.json` SHA-256 `557abad2bb0e16005735a77254a4eee03147bc6596bf3a2765e50bec5e9b961b`，完整臂及矩阵验收待后续。

固定正序第 3 次累计六门的预诊断为 0 marker，首次 DRT/RCX 用 227.897 RAW s 后独立全块 DRC 发现 10 处 Short 或 Cut Short。真实重试的 DRT/RCX 用 47.023 RAW s，独立 DRC 清零，原门及非空 SEC 均过，在 539.183750966 RAW s 验收 52.5504 µm²。`cell_01/fixed/03/result.json` SHA-256 `2d0396274bd993e25a8c2de5d82ea9724ae46bd56187dda1fc48d3ecd66f66f4`。

固定正序 3/4 完整，最终采用第 3 次的 52.5504 µm²（0.073572%），0.01% 在 211.831 RAW s 首达，0.15%／0.25% 未达。尾次初始 DRT/RCX 以 170.524885 s 的剩余时限启动，实测 162.754319 RAW s 后终止，整臂含筛选实际 712.230974 RAW s。`cell_01/arm.json` SHA-256 `e8172bba56f3687ae56c95e2efdefd8c0900989a122991a938ae20f88cd54a9e`。

v1 在第二臂原排序检查处退出，包装 758 s，rc1。新鲜排名 STA 的 TT WNS 与 P0 相同，读取了完整的 18 项。原 SDC 下 `_5736_/Y`、`_6414_/Y`、`_6788_/Y` 均报告 `+Inf`，原 AES 排序要求每个引脚有限，因而第二臂没有实际候选派发。原 TT STA 共记录 995 个未约束端点与 0 个部分未注释驱动。通用留出入口按相同有限公式先处理有有限 slack 的动作，将全 `+Inf` 动作以冻结池序留到队尾。保持原物理与时序门，新根会重新执行完整正反序。v1 原件 SHA-256 `57055442966f46c3186e61905d3d3a79e52c69840064b97951ac2569314e841b`。

v2 对 v1 真实 18 项排名作无 EDA 重放，确认 15 项有限 slack 的评分结果和次序保持，3 项全 `+Inf` 位于池尾，非法或缺失仍终止。还将策略窗口中计时、可用预算和工具截止统一到 `CLOCK_MONOTONIC_RAW`，以 100 ms 为轮询间隔。资格复测、筛选和共享零动作保留原执行方法。入口及排序核查 7 项、RAW 计时核查 2 项均过。新入口 SHA-256 `a8324e5b94747193c742d5174c8e71fac89918f1ea699988aea4ca3e5d3e9c35`，计时工具 SHA-256 `03de2e39b8c178d205e5e80f1857040af7f8270a9e062120524cb145a8f2eb8d`。v2 将在 `ethmac` 现有原生任务和资格完成后从新根完整重跑，不混合 v1 和 v2 的臂。

原 `+Inf` 表示该动作没有可用有限 setup 路径读数，保留标签并排在有限值之后。`NaN`、`−Inf`、缺失、重复或未知记录仍使排名失败。v1 固定尾次 DRT 子进程等待没有与 RAW 截止对齐，实际约早 7.770 RAW s 返回，具体系统时钟原因未独立证实。WSL Python3.12 回归 70 项通过，耗时 16.91 s，其中包括两项新的 RAW 限时测试。上述七项模拟与实日志排名核查单列。

最终源重新通过无 EDA 入参检查。`/tmp/riscv_v2_dry_final_ENPGT6/validate/qualified_inputs.json` SHA-256 `e7e29999721a0373f80bfc5c2507ee0f39025aff6d043b475ba228186ffa9a3f`，其 driver 字节绑定为 `a8324e5b94747193c742d5174c8e71fac89918f1ea699988aea4ca3e5d3e9c35`，RAW 轮询 0.1 s，实际计筛选 64.099573641 s。状态 `protocol_and_inputs_validated`，0 个物理臂完成。中间版本的 dry-run 留作开发记录。

最终可复现测试 `test_qualified_ranking.py` 涵盖有限与正无穷排序及五类非法记录，结合 `test_raw_timed_process.py` 共 8 项通过，2.00 s。

`ethmac` 资格进程退出后，于 17:09:34（UTC+8）从新根 `matrix_qualified_v2` 实发六臂。PID 437／439、exec session 85034，CPU 0–5、仓库外限 6,500 s。继续使用前述命令的其它参数，实际输出 `--out "$d/matrix_qualified_v2"`。同名 `.stdout.log` 首行保存完整实发命令。现场 `qualified_inputs.json` SHA-256 `e7e29999721a0373f80bfc5c2507ee0f39025aff6d043b475ba228186ffa9a3f`，与最终 dry-run 逐字节一致。协议 SHA-256 `a768316f012f7386c2c1d31e43829b9490c0da82174ab884dc3b6634ea5f2dae`。六臂用新版 RAW 限时与通用排名，全数重做且与 v1 分开。

v2 的新鲜共享严格零动作 57.497508272 RAW s，原门全过、面积 71,427.2544 µm²。`preflight/zero/result.json` SHA-256 `9e8769707fac96fca71dc8a9ea2e4ebbeb92f0b92b8d77b5489a70699a323d4b`。随后正序固定第 1 批开始候选计费。

v2 正序固定 3/4 完整，0.01% 目标于 205.271893856 RAW s 首达，实收 26.2752 µm²，第三次最高 52.5504 µm²。尾次工具在 RAW 截止后 0.085670931 s 停止，未产出候选终态。0.15%／0.25% 未达。`cell_01/arm.json` SHA-256 `d4ce807a8d6ecf0fa610cfacf58b19e536efbb25983e27e5b359d3d4230ea6ed`，前缀独验 SHA-256 `bc7c456102c04a723bdf6614d4cdcb658a7230e3d7eb9084595cc19888618b51`。随后新鲜灵敏度排名成功，全部 18 动作保留，三个 `+Inf` 的动作按原序排池尾，工具付 1.494135247 RAW s。`ranking.json` SHA-256 `200b402d5af592a794c05984524d6429a8ef8f61397bd2cfac8d4aa9f5a58bf0`。

v2 正序灵敏度单门派发 8，前七个全部完成并通过。第 1 次将 `_4134_` 改为 `nor4_2`，139.934 RAW s 首达 0.01%（8.7584 µm²），582.956 RAW s 验收最高 57.5552 µm²，0.15% 与 0.25% 未达。固定实际首收 26.2752 µm² 在 205.272 RAW s；单门在 285.062 RAW s 达到同一实收。尾次 DRT/RCX 于 RAW 截止后 0.081223718 s 停止。`cell_02/arm.json` SHA-256 `fc9e38c9dffd8087dec911b31ab31129d3777e917677a9a5d820a4a5942bb2e1`，前缀独验 `c48c78bc9e5f2288945bad64a87c5d5ff0431cd0a4953464eb68dae404f05a07`。正序现行去重 FAECO 已开始。

v2 正序现行去重 FAECO 完成 6/7，重用一个已完成的 setup-only 拒收。首达 0.01% 用 204.744 RAW s，实收 10.0096 µm²；第 5 次在约 417.689 RAW s 验收最高 45.0432 µm²，0.15% 与 0.25% 未达。第 6 次累计八门预诊断零标记，首次独立 DRC 发现 10 处违例，真实重试清零，终态仍因 TT TNS／SS WNS 拒收，整项用约 298.486 RAW s。尾次截在预诊断，RAW 工具到截止后 0.038365710 s 停止。`cell_03/arm.json` SHA-256 `31f2feaca2a9f700fdef0742b1c1c176a22755f46698027b071553e5b870b9ab`。反序第一臂已经启动。

正序三臂前缀独验 SHA-256 `22241070a1817552e48fbf0246a2b09e89121c96979a941461bda9399c1134c2`。现行去重的三次完整拒收合计 431.868 RAW s，均由 setup 触发。第 1、3、6 次的 TT TNS 分别下降 796.959、797.460、628.020 ps，第 6 次 SS WNS 下降 109.310 ps。按同一 seed TT 参照，从冻结筛选行计算固定第 3 组与现行第 1 组的分项 TNS 变化合计为 −654.747、+235.421 ps，实际重布线后分别为 −144.389、−796.959 ps。这两个方向的偏差均实测，分项冻结结果不足以替代整批实布验收。

按正序灵敏度排名每三项检查一个累计集合，`replay_ranked_prefix.py` 在同 scope 中找到精确匹配的原有合格端点。前 3 项为原单门第 3 次，26.2752 µm²、该请求 73.095478 RAW s；前 6 项为原单门第 6 次，48.7968 µm²、该请求 74.422989 RAW s。前 9 项没有同动作合格收据，重放停止。个别请求耗时保留其原调度身份。此证据只表明前段灵敏度顺序存在合法物理组合。若沿此只读诊断修改规则，`riscv32i` 应当视为开发输入，另需独立验证。[排名前缀原件](RISCV_RANKED_PREFIX_REPLAY.json)

反序现行去重同样 7 派发、6 完成并重用一次 setup-only 拒收。第 2 次 205.322 RAW s 首达，实收 10.0096 µm²；第 5 次 419.343 RAW s 达 45.0432 µm²，和正序最佳 ODB、DEF、V 及时序一致。三次完整 setup 拒收耗时约 430.808 RAW s，未触发 hold。第 7 次预诊断在 RAW 截止后 0.028278466 s 停止。原件 `cell_04/arm.json` SHA-256 `0a76ee9e65cc965d8315c8bedccc24ffbab941c8bdbd44e21f1fdaa16a1b15e3`。

两序 `first_relative_hold_defer=null`。第 5 次的合格端点与第 6 次的重试拒收端点各自在两序 ODB、DEF、网表和时序全同。第 6 次 ODB `442a245c4badbbdec0078a9448f3f0ea921ccde928eeb673663d495b16b62972`，正反序从派发到完整拒收分别约 298.486、298.138 RAW s。第 5 次 ODB `e68c20d692e686286939881b771996452c97a477459bf9ffae604e76d15457f6`。

反序灵敏度单门同样 8 派发、7 完整且均通过。139.237 RAW s 首达 0.01%，实际回收 8.7584 µm²；第 7 次在 584.308 RAW s 验收 57.5552 µm²，最优实物与三角读数全部复现。末次 DRT/RCX 在 RAW 截止后 0.084407044 s 停止。`cell_05/arm.json` SHA-256 `c51faa27c1c49726a277d0bc357fc789043fafe7bb7ae1f7bf5974820439b8ba`。反序固定最后一臂继续。

#### v2 六臂终态

反序固定完成 3/4，于 204.686835858 RAW s 首达 0.01%，实收 26.2752 µm²，第 3 次在 510.244479725 RAW s 验收 52.5504 µm²。`cell_06/arm.json` SHA-256 `23d1094eb4387521b6060733acd6abd7db7fdd62a2833f6f50431165f8344370`。所有六臂均未达到 0.15% 和 0.25%。

| 调度 | 每序派发／完整 | 两序最佳回收（µm²） | 0.01% 正序／反序（RAW s） | 首达实收（µm²） | 至少 45.0432 µm² 正序／反序（RAW s） |
|---|---:|---:|---:|---:|---:|
| 固定批次 | 4／3 | 52.5504 | 205.272／204.687 | 26.2752 | 513.590／510.244 |
| 灵敏度单门 | 8／7 | 57.5552 | 139.934／139.237 | 8.7584 | 507.977／508.962 |
| 现行去重 FAECO | 7／6 | 45.0432 | 204.744／205.322 | 10.0096 | 417.689／419.343 |

表末列为从同一已验前缀后验回读的共同面积下限，固定实际交付 52.5504 µm²，单门 48.7968 µm²，现行 FAECO 45.0432 µm²。按方法，两序各自最高端点的 ODB、DEF、V、去日期 SPEF 及逐角结果一致，均过原门、独立全块 DRC／天线、SEC 4559/0。固定／单门／现行的最大 setup WNS 损失分别为 50.198068／0.129230／0.039080 ps，SS setup TNS 分别变化 −9442.374／−7517.883／−1287.844 ps。

六臂共 38 次派发、32 次完整，38 次预诊断、40 次 DRT/RCX、108 次候选逐角 STA、36 次独立 DRC、24 次候选 SEC、2 次排名 STA。两次预诊断和四次 DRT/RCX 因墙钟被裁剪，末工具停止与各臂 RAW 截止的差值依次为 +0.085671／+0.081224／+0.038366／+0.028278／+0.084407／+0.091800 s。生产 rc0，外包 4,039 s，完整独验 6/6。三份收据已与原件 `cmp`。独验 SHA-256 `ef949a66f62d5645ddbef1876e338484ecededbe0896b2efba467ca09814ed04`。[协议](RISCV_WALLCLOCK_PROTOCOL.json) · [结果](RISCV_WALLCLOCK_RESULTS.json) · [验收](RISCV_WALLCLOCK_VERIFIED.json)

现行去重在该留出上的窗内最大回收低于两种基线，而到中等面积阈值的时间及最优端点的 SS setup TNS 有优势。两序均未触发 hold 重排，完整 setup 拒收约花 431–432 RAW s。冻结单项 TT TNS 相加在已核两组的实际偏差方向相反。下一步对照应先让固定和 FAECO 与灵敏度单门共享初始顺序，再分离批宽和反馈。在 `riscv32i` 上据此作出的规则选择需另用独立设计检验。`ethmac` 的原起点电气资格仍未通过，当前没有对应候选性能读数。

### ASAP7 ethmac 原生资格实发

SKY v1 所有物理进程退出后，`ethmac` 原生制备于 16:35:19（UTC+8）开始。CPU 6–11、四线程、原生 1,800 s。包装、进程限时与 Make PID 为 459／468／470。原目录 `/home/toylog/faeco_tcad_anytime_holdouts_20261125_v1/asap7/ethmac`，实发 `command.sh` SHA-256 `4bc4b6ab2c16af6409a6d4c337cf17c806884e8197753eedddb0f56df10c185f`，`input_manifest.log` 为 `e837ef1534b2ca046f0696b74f9844e59b1e8f694d21d2b9c482d4015f13e7ec`。源码树 `9ce44bb8e318d6d0ab4bf5f84667072f6726a6fd`，源 SDC SHA 与预登记同。当前为原 ORFS 起点制备，资格原件待实收。

原生 1,800 s 限时后 rc124，已完成第 4 轮 DRT，native DRC／天线均零，末段 RCX 在 16% 被截，没有 SPEF。保留部分报告 `recovery_finish_v1/6_report.initial_timeout.log`，SHA-256 `6f0d3a2a0d96ace8afb20135a71ec53cb74d19e10318bdf0f7c5b7e060cc59d1`。`5_route.odb` 和 `6_1_fill.odb` 同为 `65a45d299f5aa1fdff8c831239eb0430bf01b4b20ff4b21b93d01af71009f3b2`。原进程停止后，在 17:04:55（UTC+8）用同一 ORFS 根与冻结输入单独恢复 `6_report.log`，CPU 6–11、四线程、限 600 s。恢复命令及输入绑定 SHA-256 为 `e38c4320f18ef61afc26ca280bd62e5f30e295b2fbf05e3c3a5642871efd2120` 和 `b1ecf6b78f802227d0d05defdb3e2cb6d7da9ca12dc10ce4e675fbbca8163733`。补充 RCX 已提取 60,697 网，资格待验。

末段恢复 rc0，`real 68.64 s`，只有原 `final_report.tcl` 执行。来源 SDC、已布线与填充 ODB、DRT 日志和 JSON 字节一致。RCX 60,697 网和 608,885 个耦合项，SPEF 为 77,878,734 字节。恢复 `producer.log` SHA-256 `99e32c632384a5c4e1e22ecac99931def577bbb6d08089de060e2d1cf5a9138c`。独立恢复资格在 CPU 6–11 以 500 s 外限实发，使用 `qualify_native_recovered.py` SHA-256 `c416e2115946fe93fadd5e5dce2eabb0f7c75c025ee8793f3722324f51823cba`。资格三角与候选评估的结论待分别写入。

现场三角 hold 为 +28.591324／+43.821717／+55.663543 ps。独立全块检查载入 512,346 个 guides 后在 45 s 子工具限时中止，记录实耗 45.846606863 RAW s 与 `returncode=null`，当前没有该次完整 DRC／天线终态。原生零报告与独立验收分别保留。

原起点资格收束为 `qualification_incomplete`、rc1。237 条源／导出 SDC 规范命令完全匹配，正式 FF／TT／SS hold TNS 均 0，SEC 52287/0（76.599 RAW s）。原始三角电气中 max slew 超限数为 0／9／1017，TT 与 SS 的最差裕量分别为 −34.079739、−186.783890 ps，max-cap 违规为零。除电气拒收，独立 DRC／天线仍缺完整验收。没有候选评估。资格收据 358,712 字节逐字节复制，SHA-256 `249a4a5274ff217d2a21f049cf0f318935d54af28a80bc85b1ff7c5b256b2ba6`。[Ethmac 资格结果](ETHMAC_CONTROL_INCOMPLETE.json)

实际原生 CTS、GRT 和最终报告日志只读 RVT FF Liberty，对应原 ORFS `BC`。将资格收据中的 max-slew 引脚映射到 `6_final.v` 字节范围 `[1350000,1950000)` 和 `[5570000,5800000)` 的实例与线网。SS 1,017 项中映射到 990 项，其中 982 个为 `NAND2x1` 受端，该子集共 250 条网。TT 9 项全部匹配，为 `_24399_`、`_24417_`、`_11937_` 三组 `NOR2x1` 驱动网各带三个 `NAND2x1/A`。这是已绑定引脚子集的统计。当前保留原 SDC，后续若试验电气闭合，应在共同起点对实际驱动／负载做多角修复，再走完整原验收。此轮没有重跑物理。
