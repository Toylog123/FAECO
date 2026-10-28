# C03/C04：A证明元数据修订方案（只读，待主线确认）

首选方案是先以固定f761源码、同一Lib和同一final_sec方法，对A的八对精确baseline→accepted对象建立统一的新SEC批次，取得真实同批证明点数和wall time，再修改中英A表。没有执行新证明，没有修改稿件，也没有以缺省时间符号替代补验。旧A6/A2证明及计时原件完整保留。

## 已证实的稿件问题

当前中文长文件445行/表460–479行，英文267行/表274–287行仍将旧A proof的点数与时间并列成8项同一表。六个旧proof的gate不对应效率优先接受终点；六个新确切pair证明已恢复功能身份，但它们的proof时间不等于旧运行时间。

| circuit | 当前中英表 proven/time(s) | 已实读可用proof proven/unproven | 实际来源及time(s) |
|---|---:|---:|---|
| s27 | 11 / .303 | 11/0 | 复用20260826 B exact pair；summary.seconds=1.8，无逐调用walltime receipt |
| s382 | 90 / .382 | 90/0 | A6 result.runtime_s=2.140 |
| s420 | 79 / .368 | 79/0 | A6 result.runtime_s=0.203 |
| s641 | 124 / .381 | 124/0 | A6 result.runtime_s=0.219 |
| s713 | 126 / .410 | 126/0 | A6 result.runtime_s=0.344 |
| s820 | 138 / .454 | 137/0 | 复用20260826 B exact pair；summary.seconds=2.2，无逐调用walltime receipt |
| s832 | 145 / .437 | 146/0 | A6 result.runtime_s=0.375 |
| s953 | 228 / .537 | 228/0 | A6 result.runtime_s=0.344 |

特别是s832应146而非145；s820的确切B复用证明是137而非表中138。六个A6证明runtime全部从实际result.json读取，全部status=pass/rc0，实际日志非零proven/0unproven、脚本含equiv_status -assert，receipt中10个artifact SHA逐件吻合。六份来源pin为8192193，不应倒写成f761证明。

s27/s820复用的是20260826 B verify.ys/log而非旧A verify；实际prep -top equiv并明确gold/gate，分别11/0与137/0；原A初终target与proof pair按非空行一致，最终gate与实际B state相同且state hash匹配。两份旧脚本没有-assert，实际日志有完全证明输出。其summary.seconds是1.8/2.2而不是表中0.303/0.454；日志CPU时间又是另一计时量，不能混用。现存ITC remaining脚本不证明s27/s820使用了同一计时过程。旧来源仍独立登记，不将时间unknown倒签成已恢复。

## A8新批次：精确输入与边界

所有baseline来自原A run/mapped.v，final来自该A接受动作精确对应的fixed/mapped.v。不是A′baseline，尤其s713不换成物理批次的另一个起始对象。八对helpers在UTF8/BOM和通用换行解码后完整相同；接受动作与原A ledger核对。所有原件raw SHA与decoded-text SHA见A8_INPUT_PROPOSAL.json。下列是实际原字节SHA：

- **s27**
  - baseline `experiments/20260805_tcad_sprint1_iscas89/s27/s27/mapped.v`
    SHA `b80c931d0ca423c26c6600f2ad442b0f9f3a36f696878eafeea195cda88cadeb`
  - accepted `experiments/20260807_real_pr_iscas8/s27/fixed/mapped.v`
    SHA `b7d74dc321b08907d523f671d4cd10f63ac223cae605c7db95dc5812cb325976`
- **s382**
  - baseline `experiments/20260805_tcad_sprint1_iscas89/s382/s382/mapped.v`
    SHA `608cf28c7da49b245ec5cb44207552cd112a638275741c3eab74c13be0a06221`
  - accepted `experiments/20260807_real_pr_iscas8/s382/fixed/mapped.v`
    SHA `cdbb670f39933e94d5023e0a29cfab3d1bf1dac5cedf2e50ec704ec01dc8925f`
- **s420**
  - baseline `experiments/20260805_tcad_sprint1_iscas89/s420/s420/mapped.v`
    SHA `19e5679c4356a8aad2f956919501854a367c58620ef47c71606e0cc302fc7ed3`
  - accepted `experiments/20260807_real_pr_iscas8/s420/fixed/mapped.v`
    SHA `c6471a72e9ddd5b7995c5519bdeca2fa6473418ce3789d60267a77e4033bc219`
- **s641**
  - baseline `experiments/20260805_tcad_sprint1_iscas89/s641/s641/mapped.v`
    SHA `3665ba3076114eff30e701dd57d8d0f5d296f7ebc677fbdf4fdcfbdd79f3855e`
  - accepted `experiments/20260807_real_pr_iscas8/s641/fixed/mapped.v`
    SHA `b3a53ed8a2a6aec8764fadfd98cc89106b13fed599539816b53af7aed86958b1`
- **s713**
  - baseline `experiments/20260805_tcad_sprint1_iscas89/s713/s713/mapped.v`
    SHA `a17cf08d47e8d14861f69b96595e380690b471c3044002f22f9c4bb006afb6fd`
  - accepted `experiments/20260807_real_pr_iscas8/s713/fixed/mapped.v`
    SHA `3c982ac08503110ad5d6c64ed76197da7d4c1fc6acc0cc032a8825d6db43a695`
- **s820**
  - baseline `experiments/20260805_tcad_sprint1_iscas89/s820/s820/mapped.v`
    SHA `12a3bc4d0d9bcdd9071250654a9484b80716f94e1eff454e232e2ab7e76d49e8`
  - accepted `experiments/20260807_real_pr_iscas8/s820/fixed/mapped.v`
    SHA `2d4217b27555d6142c77bf5d707764ce7e6685d0f160f2d8373ce433365f06a6`
- **s832**
  - baseline `experiments/20260805_tcad_sprint1_iscas89/s832/s832/mapped.v`
    SHA `5966dcf411817b457f366951b713ce4579b4bbd8fee38004d621a6eca1675d96`
  - accepted `experiments/20260807_real_pr_iscas8/s832/fixed/mapped.v`
    SHA `11acbbf2bf61512dc800689e15336d804472c8a009917475da2fc948b7e98a99`
- **s953**
  - baseline `experiments/20260805_tcad_sprint1_iscas89/s953/s953/mapped.v`
    SHA `ff5f6a2fdbf03098f8b4fb33c3a6dd9c90d761ddc052b1e9ad4a6b319b83c6bf`
  - accepted `experiments/20260807_real_pr_iscas8/s953/fixed/mapped.v`
    SHA `84d5e6ec40ac37c27a67834f676026eb7e4ebb8d12a83707eceb212775e128c6`

该JSON是proposal而非正式注册。根确认后，应在新exclusive证据根`project_docs/evidence/r22_a_sec_unified_20261018/`正式登记当前HEAD/源码/工具/Lib和这16个raw输入；不覆盖r22_a_sec_20261016_frozen或任何旧B proof。主线须另核实际HEAD仍f761及源码冻结；本次只对锁定D manifest的45份源码逐SHA复核，没有执行Git命令。

统一Lib为`sky130_fd_sc_hd__tt_025C_1v80.lib`，raw SHA `ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9`。预期域是保持相同状态单元/时钟/复位语义的两态全网表顺序等价。当前common.final_sec会先检查实际Lib pin连接和tri/Z支持域，unsupported不得pass；它明确构造gold/gate，hierarchy -top equiv、flatten、equiv_simple、equiv_induct -seq10、equiv_status -assert。不能宣称通用四态、任意初始化/复位或物理时序证明。

## 可复用调用方案（不执行）

使用当前`code/scripts/run_r22_cut_ablation.py:102 final_sec(initial, final, circuit, out)`，不复制证明逻辑、不运行common.execute_circuit/工具版本全查询/映射/STA。只加载此模块后调用final_sec；它的LIB和源码SHA必须先匹配登记。顺序执行8个pair，单proof timeout180s，外层timeout1800s。WSL Yosys命令是`wsl.exe -d Ubuntu -- /usr/bin/yosys <sec.ys>`，该调用不会运行OpenSTA。D的两电路STA占用、manifest/配置、HEAD和生产源码全部保持。

伪代码（待授权wrapper实施，不是本轮已运行）：

```python
# Confirm registered source/input/library SHA and active HEAD before launch.
for case in registered_cases:                 # one proof at a time
    out.mkdir(exist_ok=False)                 # no overwrite/reuse-by-status
    copy_original_bytes_to_source_snapshots() # SHA equals registered raw bytes
    initial = baseline.read_text(encoding='utf-8-sig')
    final = accepted.read_text(encoding='utf-8-sig')
    result = common.final_sec(initial, final, circuit, out)
    # Re-read real log, nonzero proven/zero unproven, rc0/pass; bind all artifacts.
    # Before/after source/input/lib SHA + original/decoded/output identities.
    # Stop on unsupported/timeout/drift/unproven/error; preserve failed attempt.
```

common.final_sec的runtime_s从外部prover启动前的monotonic起算、到保存日志后计算；不含前置模型/输入准备。八项都使用这个同一wall-time定义，不与旧批次CPU时间或summary秒数混合。common写出的initial_raw/final_raw可能因换行序列化与原raw bytes不同；须另外保存原字节快照并双重绑定raw SHA和解码文本，不能错误要求写出文件raw SHA天然等于输入raw SHA。

每份产物保存source snapshot、cells/helpers/gold/gate、sec.ys/log/result、逐输入/输出SHA和计时；完整成功门为：全部source/Lib/input before-after稳定，8个rc0/pass，实际log非零proven/0unproven及成功标记，确切pair未更换，根独立逐对象验收。旧11/90/79/124/126/137/146/228只是既有proof观察值；同批新模型/flatten可能改变$equiv数量，必须按新log实填，不硬编码要求旧数字。

## 根验收A8后才落稿的最小中英before/after

只动效率优先A段的功能句和tab:sec_iscas8的caption/header/8行/footnote。保持所有WNS、接受动作类型、收益总数、物理数据、B3/C/D结果、摘要及结论不变。

**ZH 445行，原句：**

> 8 个修复网表均通过独立顺序 SEC（通过率 8/8），证明单元数和时间见表~\ref{tab:sec_iscas8}。

**ZH，A8实际全通过后：**

> 独立顺序等价检查完全证明了这8对基线与最终修复网表，证明点数与耗时见表~\ref{tab:sec_iscas8}。

**EN 267行，原句：**

> All final pairs pass independent SEC (Table~\ref{tab:sec_iscas8}).

**EN，A8实际全通过后：**

> Independent SEC fully proves all eight baseline/final repaired pairs; Table~\ref{tab:sec_iscas8} reports the proof counts and wall time.

**表结构建议：**保留4列，`电路 / 已证明/未证明 / SEC / 耗时(s)`；英文`Circuit / Proven/unproven / SEC / Wall time (s)`。8行只能从新A8收据及真实日志生成，SEC列为通过/Proven，不能先把旧批次点数或time填进去。也可删重复SEC列改3列，但不是本次必需。表标题改为`效率优先修复网表对的顺序等价证明` / `Sequential equivalence of the efficiency-first repaired pairs.`。

**ZH新表注（A8验收后）：**

> 八对网表采用同一验证批次和SKY130行为单元模型，以\texttt{equiv\_make}、\texttt{equiv\_simple}和\texttt{equiv\_induct -seq 10}证明，并由\texttt{equiv\_status -assert}检查全部等价点。耗时为每次独立证明调用的墙钟时间，不含候选STA和模型准备。

**EN新表注（A8验收后）：**

> All pairs are checked in one verification batch under SKY130 behavioral cell models using \texttt{equiv\_make}, \texttt{equiv\_simple} and \texttt{equiv\_induct -seq 10}, with \texttt{equiv\_status -assert} requiring complete proof. Wall time covers each independent prover invocation and excludes candidate STA and model preparation.

新批次在补充证明来源表中注明A8实际登记ID/pin、八对原输入/接受对象及完整新receipt。主表不再把6个新proof和2个复用proof伪装成同批；旧A6/A2来源另存追溯，不在结果正文反复讲修订过程。新A8是新功能证明，不是新的STA/时序收益，也不能更新未完成B3/C/D的总体数字。

## 可复查与失败留档

verify_sources.py真实只读运行，83份来源SHA前后稳定、六份receipt artifacts全匹配。build_a8_proposal.py真实只读运行，87份来源/45源码匹配锁定pin，8对proposal已生成，外部prover_started=false。实际脚本与120秒wrapper日志均在本目录。首次build的严格JSON解析遇原A ledger的literal backslash-n trailer失败，失败脚本/日志保留；适配版仅对eval_trials.json精确该2字节已知尾串作显式登记，未改源文件、未接受任意尾部。A6旧manifest已记录六项同类尾串，本次包含s27/s820在内8项逐件记录。

本轮只给proposal，等待根审阅和正式注册/执行授权；未patch/编译主稿，未改figure冻结包、共享记录、code或HEAD。
