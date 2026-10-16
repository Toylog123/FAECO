# 历史 D/C 同族复验设计预览（2026-10-16）

**这是只读档案恢复与执行设计，不是正式可执行 pin。** `execution_ready=false`、`formal_source_pin=null`；未运行 EDA、映射、STA 或 SEC，未修改任何旧结果、源码或测试。新源码尚须主线整体回归和冻结。C′是独立新实验族，不能用它替换这里的 D/C 结果，也不能把调度差异归因到修复本身。

`manifest_preview.json` 登记本次实际读取的 806 个来源文件（逐文件 SHA256/字节数/角色）、5 个历史源码 blob、56 条 D 运行配方和 48 条 C 恢复记录。历史配置、建议新命令和无法恢复的字段分别保留。当前源码哈希只是读取时的预览，绝不代表主线正在验证或即将提交的最终源码 pin。

## D：五臂 × 八电路与 k=1 两臂 × 八电路

实际图源入口是 `paper/zh/figures/data/scripts/review_r21_figures.py:budget_curves`，读取 `experiments/20260924_threearm/{fixed,adaptive,random_s1,random_s2,random_s3}/<c>/` 的 result、ledger、run_config。另逐份读取 `experiments/20260924_l2_k1/{fixed,adaptive}/<c>/`。本次 40+16 份 run_config 全部存在，含运行 argv、解析后参数、feedback config 和 git_head；相应 mapped、map.ys、map.log、sta.tcl、外层日志与最终 state 也均实际读取。56 份最终 state 文本哈希全部回验一致。

| 项目 | 主 D（40 runs） | D k=1（16 runs） |
|---|---|---|
| 记录的 HEAD | `6276cff54310e2078106ec3cef3255034f67d9ed` | `1a54087b0201d49ede2d2b021c865ecc7258c539` |
| 臂 | fixed、EMA adaptive、随机 seed 1/2/3 | fixed、EMA adaptive |
| candidates-per-iteration | 8 | 1 |
| 共同配置 | period=0.5、max-iterations=20、STA budget=500、joint-k=2、joint-enumerate-depth=0、workers=1、max-instances=8 | 相同 |
| 共同开关 | RGB、enable-buffer、early-stop=true；tns-aware=false、proxy=false、physical=false、UCB adaptive=false | 相同 |

八电路为 s27/s382/s420/s641/s713/s820/s832/s953。EMA 实参实际保存为 rho=0.5、eta_add=0.5、eta_c=0.25、clip=true、additive=[1,8]、divisor=[0,2]、F5 rate threshold=0.5、min_recent_triggers=2、window=3、cone_shrink=0.5、cone_min=1。完整字典逐 run 保存在 manifest，不以当前默认值代替历史记录。

**必须保留的隐式行为：** 旧 HEAD 的 `RealWnsEvaluator.enable_topology` 默认 True，旧 CLI 没有关掉它。复验 D 应保留 topology enabled；不得照抄 C′ 的 `--disable-topology`。当前 `--cut-search-policy legacy` 可显式保留旧候选边界路径；不能换为 weighted_st 后仍声称同族同调度复验。`early-stop` 是实例内部首次时序改善的短路开关，不是 C 的“整轮无改进停止”。

### 具体运行命令与输入准备

每个 run 的完整原始 `historical_argv`、`historical_resolved_args`、建议 `proposed_command_argv` 和 `input_stage` 均已逐条写入 manifest 的 `D_runs`，共 56 条，不使用按目录猜测的参数。原 argv 不含 Python 解释器身份；建议命令才显式使用当前 `.venv/Scripts/python.exe`。

新命令以原 argv 为基础，仅改新输出根目录和当前源目录，明确添加 `--skip-mapping --cut-search-policy legacy --no-proxy-ranking`，并把历史 resolved 的 max-instances/joint-enumerate-depth/strategies/clock/epsilon/required-metrics/初始三权重显式化。其余 tns-aware、hold、physical、UCB、topology 状态必须在正式注册时与历史配置逐项核对。

| 臂 | 原 argv 中的臂开关 | 新输出根目录 |
|---|---|---|
| fixed | `--no-feedback` | `experiments/20261016_r22_D_revalidate/fixed` |
| adaptive | `--feedback-ema` | `experiments/20261016_r22_D_revalidate/adaptive` |
| random_s1/s2/s3 | `--no-feedback --random-order --seed 1/2/3` | 同根目录各随机臂 |
| k1 fixed/adaptive | 同上，beam=1 | `experiments/20261016_r22_D_k1_revalidate/{fixed,adaptive}` |

执行前每例必须将 manifest 的 `input_stage.copy_from` 复制到 `copy_to`，拒绝覆盖，并逐字节校验 `require_same_sha256`。正式运行建议用 `run_with_timeout.sh 3600` 逐 run 包装；3600 秒是本轮建议的外部监测上限，不是恢复出来的历史配置。当前任务未执行这些命令。

`code/scripts/run_threearm_batch.sh` 可复用臂标志、FAECO_K 和臂间并行组织，但原脚本仅因 outerloop_result 已存在便跳过，且不绑定独立 final SEC/input hash。不得直接把旧 batch exit0 当验收。复验器需要在真实 `state.current_netlist_text` 上调用已修复模型的 `run_r22_cut_ablation.final_sec`，保存原始 mapped/final 对象、全部模型/输入/源码哈希和完整 proof receipt；任一合法性门/最终 SEC 失败即停止，不能继续汇总收益。

### 映射与源码来源边界

每电路的主 D 五臂与 k1 两臂共七份归档 mapped 起点字节 SHA 完全一致；全部可用 C canonical 起点也与之相同。可直接复用下面冻结起点，避免重映射引入混杂：

| 电路 | 可复制的归档起点 | SHA256 |
|---|---|---|
| s27 | `experiments/20260924_threearm/fixed/s27/mapped.v` | `b80c931d0ca423c26c6600f2ad442b0f9f3a36f696878eafeea195cda88cadeb` |
| s382 | `experiments/20260924_threearm/fixed/s382/mapped.v` | `608cf28c7da49b245ec5cb44207552cd112a638275741c3eab74c13be0a06221` |
| s420 | `experiments/20260924_threearm/fixed/s420/mapped.v` | `19e5679c4356a8aad2f956919501854a367c58620ef47c71606e0cc302fc7ed3` |
| s641 | `experiments/20260924_threearm/fixed/s641/mapped.v` | `3665ba3076114eff30e701dd57d8d0f5d296f7ebc677fbdf4fdcfbdd79f3855e` |
| s713 | `experiments/20260924_threearm/fixed/s713/mapped.v` | `a17cf08d47e8d14861f69b96595e380690b471c3044002f22f9c4bb006afb6fd` |
| s820 | `experiments/20260924_threearm/fixed/s820/mapped.v` | `12a3bc4d0d9bcdd9071250654a9484b80716f94e1eff454e232e2ab7e76d49e8` |
| s832 | `experiments/20260924_threearm/fixed/s832/mapped.v` | `5966dcf411817b457f366951b713ce4579b4bbd8fee38004d621a6eca1675d96` |
| s953 | `experiments/20260924_threearm/fixed/s953/mapped.v` | `ff5f6a2fdbf03098f8b4fb33c3a6dd9c90d761ddc052b1e9ad4a6b319b83c6bf` |

56 份 D map.log 均报告 `Yosys 0.67+146 (git sha1 468ba27d9-dirty)`；map.ys 明确保存 synth -top、dfflibmap、abc、clean、write_verilog 配方。git_head 可恢复，但 run_config 未捕获运行时 dirty 状态/逐源码 SHA，原始 RTL/Liberty 的运行时字节 hash 也未记录。本次当前 RTL/Liberty SHA 只能声明为当前对应文件，不能倒填为旧 runtime capture。冻结留存 mapped.v 解决起点身份，不恢复缺失的旧源 pin。

历史 correctness 审计中，主 D 为 38 invalid/2 valid，k1 为 14 invalid/2 valid；这里逐例保留原判定，未运行新 SEC。valid 终点也应作为完整同族矩阵的一部分复验，不能只挑失败例并把旧成功结果拼入新矩阵。

## C：六臂 × 八电路，保留原 greedy 调度

| 臂 | 真实来源 | 本次可恢复 | 仍未知 |
|---|---|---|
| hybrid | `experiments/20260807_multiround_8c_067` | 七份 canonical 结果与 launcher；period0.5、rounds20、RGB+B、buf_1/2、joint-pairs3、tns-aware、workers2 | 实际 runtime argv/revision；s382 canonical ledger/绑定缺失 |
| pureG | `experiments/20260826_ablation_pureG/<c>/hybrid_result.json` | 八份结果：period0.5、rounds20、random_order=false、seed20260806，实际 trial 仅 G | 全 argv/revision、实际 only-strategy flag、tns-aware/workers/STA cap/priority/defaults |
| pureB | `experiments/20260826_ablation_pureB/<c>/hybrid_result.json` | 同上，实际 trial 仅 B | 同上，另 buffer type 配置 |
| random1/2/3 | `experiments/20260826_ablation_random_seedN/<c>/hybrid_result.json` | 每臂八份，period0.5、rounds20、random_order=true、seedN，实际 RGB、无 JOINT 记录 | 全 argv/revision、joint-pairs、tns-aware/workers/STA cap/priority/defaults |

对应 manifest 的 48 条 `C_runs` 逐行保留 recovered/launcher_recovered/missing 分类。只有七例 hybrid 有 `launcher_template_argv_relocated`；它是旧 run_all.bat 的路径迁移配方，不是未保存的实际 argv。其余 run 的 `proposed_command_argv=null`，因为目前证据不足以构造唯一忠实命令。

canonical hybrid/s382 缺失；`20260807_multiround_s382_067_v3/s382/hybrid_result.json` 仅是候选 sibling，虽数值和 mapped 起点吻合，仍未发现发布汇总到该文件的 provenance。manifest 单列该路径/hash并排除 canonical 替代，不补写旧命令。

### 应复用的实现及必须保留的行为

可审查语义快照为 `26058ca:scripts/run_hybrid_repair.py` 与 `cb0bc74:scripts/run_hybrid_repair.py`；当前 `code/scripts/run_hybrid_repair.py` 仍有同样的核心 per-instance greedy 框架，但不是已恢复的实际运行 revision。三个版本的区别和 blob SHA 已登记。适配时必须保持：

1. 每个 pass 开始对当前网表做 STA 并刷新 critical instances。
2. 按关键实例顺序，评估该实例全部候选，再提交其 best；随后下一实例从已更新网表继续。一个 pass 可多次提交。实际 s27 混合日志的首 pass 包含多条 B/R 提交，不能换成统一 loop 每次只选一个 cut/patch 的调度。
3. random_order 只打乱每个实例的候选次序，不打乱 critical-instance 次序；候选并行结果按提交顺序收集，tie 选择与 workers 语义也要保留。
4. 轮后 JOINT 是单独阶段：混合 launcher 明确 joint-pairs=3；随机旧记录没有 JOINT，不能为了“公平”默设同样 3，也不能从缺结果反推出历史 joint-pairs=0。若采用随机 joint=0 的重建设计，必须标为新声明的重建参数，并保留 mixed/random 的 JOINT 不对称，不能声称恢复原 CLI。
5. WNS 严格改善或 WNS 持平/TNS 改善的接受规则，取决于 tns-aware；未知的对照配置必须补证或作为重建决策显式预注册。
6. 整个 pass 无改善则停止，rounds=20 是上限；不得改成强制20轮，也不能换成 D/C′ 的候选首次改善短路。

当前 C runner 不是 failure-feedback/EMA loop；strategy-priorities 是独立候选排序接口，未知旧参数不能写成已恢复的反馈消融。40 份对照的 observed kinds 只证明实际记录的候选类型，并不证明未保存的 flag/default。

### 为什么现在还不能直接启动 C48

当前 `run_hybrid_repair.py` 强制调用 mapping，无冻结 mapped-input 复用开关；主要解析/编辑仍为全文传统路径，缺少本轮要求的 target-scope F1/F2/duplicate-instance 门、不可覆写逐 trial base/candidate/结果身份、精确 STA launch 事件与独立 final SEC 验收。仅换用修复后的 insert_buffer 不等于完整候选管线已获证。

下一轮应以该历史 greedy 框架做独立适配：增显式 mapped-input 入口，保留原候选生成/每实例 evaluate-all/select-best/多提交/JOINT/停止规则；每候选先在正确 top 做合法性门，唯一 trial 目录记录 base/candidate hash；分别记录候选评估、新 STA launch、缓存、baseline/refresh STA、accepted commit 与最终 SEC。不要把当前 `run_r22_cut_ablation.py` 的 C′ arms 或统一 evaluator 调度拿来代替。

配置缺失的恢复路径依次是：查旧 launcher/进程日志/commit/worktree 备份；找到就按真实来源补证；找不到则声明为 C 同族重建实验，并明确选择 workers、tns-aware、STA cap、buf-types、priorities、随机 JOINT 等缺失值。预注册后为完整48矩阵统一冻结新 pin/输入/Liberty/模型，再做首反证和整族复验。不能用脚本当前默认值冒充旧配置，也不能凭代表12例推断全部48终点都已无效。

## 后续待办

| 待办 | 状态 | 执行前的证据门 |
|---|---|---|
| D40 + k1 16 新 pin 与独立终点 SEC 接线 | 配方已恢复，未执行 | 主线整体回归、commit、冻结源码/模型/八起点、配置逐项复核 |
| C 缺失 argv/revision、hybrid s382 来源补证 | unknown 保留 | 实际档案来源；无来源则转明确重建设计 |
| C 历史 greedy runner 安全/证据适配 | 尚未实施 | 保调度的反证测试与整体验证，不换 C′ |
| C48 新冻结复验 | 未执行 | 缺失配置决策预注册、独立 input/model/source pin、每终点完整 SEC |
