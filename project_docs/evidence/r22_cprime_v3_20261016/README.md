# C′v3 当前执行与输入准备证据 — LOG-42

用户于2026-10-18明确“继续推进 做好记录”，当前授权为继续执行。唯一工作区 `D:/BaiduSyncdisk/01_Papers/03_FAECO`，当前main阶段提交为 `7231e0296da357df435414f75b0a41fe78265837`（941files），origin/main已实际push到7231e02（session60883 exit0）；C′原始source pin仍3ea0f75不回写。归档/图件审查已齐，当前进入S/SPEF修复计划先红后绿，生产可按明确文件归属改动，整体回归/独立review/源码新commit后才注册正式EDA；不恢复已结束的session9345。

**C′v3全72已独立验收。** `project_docs/evidence/r22_cprime_v3_20261016/MATRIX_AUDIT_72.json`（SHA `a34da9c3e9854343b976f6eea31eb29c23314fd5149de2796567572288abc738`）实核8电路×9臂、all_matrix_verified/source_stable/completion_set_frozen_at_start均true，72个当前completion SHA匹配。8458候选评估记录、6858 candidate_ideal STA+72初始baseline=6930实际STA过程，other0，192保留提交；每终点独立SEC均非零proven/0unproven。physical/electrical/S均false，不能称物理STA。最终审计exit0/runtime46.546s；剩54原运行wrapper3728s/exit0。stage72五件script/log/invocation/receipt/原运行log保真归档；旧51/54/v1失败/v2仅注册原件不覆盖。

当前接受协议是严格WNS改善并满足TNS不退化等既有硬约束；--tns-aware改变平局选择，不关闭setup_tns预算。零收益与不利结果保留，不调参制造正结果。完整16个weighted/uniform配对已按所有重复同base轮独立核查，5454次交叉比较cut/pool/dispatch全同、16终点全文同（FIGURE_CPRIME_REVIEW269205b9…）；本矩阵未观察到独立权重收益，重复轮不是独立统计样本。新C′不替代旧B3/C/D。

完整v8历史收据为969pass/4skip/156subtests、170源码SHA稳定，OI040/041实现门closed；A6/B2/B17实际对象新证明已各自绑定原pin，B3主线51QA及C作者84/独立注册38QA、原OI042反例拒绝仅关闭工具实现门，尚未新clean pin正式登记同族EDA。四态支持仍open，实际三态/显式Z/switch须unsupported非pass。中英稿时钟元数据OI043已两遍编译/38p视觉/副本验收，仅设置说明门closed；科学回填和投稿声明仍待。


当前接受协议为严格WNS改善并满足TNS不退化等既有硬约束；--tns-aware改变平局选择，不意味着关闭setup_tns预算。W0/s27首候选WNS -.27→-.26但TNS -.49→-.50，被setup_tns硬门拒。零提交/零WNS收益如实保留，不为正结果调参。最终审计分开理想候选、baseline/refresh/physical STA与提交。

## QA重跑路径

qa/是来源字节保真的原件，不是改过根路径的便携测试包。测试的R=parents[2]依赖原scratch/r22_cprime_v3_20261016位置；直接运行qa副本曾20例FileNotFoundError，均未触生产代码。应在原scratch位置重跑，或在新副本显式适配路径/另锁SHA，不修改归档原件。root在最终源码原scratch位置已再测20pass/1.10s；该回显仅属preparer控制；当前完整v8=969已另有来源钉定与后验。

## 确切运行输入快照（LOG-49）

source_snapshot/runtime_inputs.zip与snapshot.json绑定3ea0f75的62份确切字节（44runtime source、Lib1、RTL8、mapped8、prep1）。ZIP 2400670B，SHA620a0eb9809dd08720fd4fdf4bdb85781668ff161a9b061936e7447ade442d7f；root前后source稳定，记录员直接ZIP逐文件SHA独立核验62/62一致。用于换机/换行独立恢复source pin；不含工具可执行文件，工具版本仅登记。全部72验收后提交归档时此ZIP受ignore影响须force-add；运行期间不commit/变HEAD。

## 首18运行与审计归档（LOG-54）

pilot_qa/ARCHIVE_MANIFEST.json新增60份字节原件，包含audit v1/v2、05/07/18报告、原pilot.log和18例completion/最终SEC result/log，来源/目标SHA逐件核验60/60；原调用路径见该目录README。完整candidate raw/STA/models仍在注册experiment目录，由full_artifact_bindings与最终audit逐件绑定。v1/v2不同SHA各对应自己的receipt，不覆盖旧QA。

## 同状态机制诊断（LOG-64，partial）

mechanism_audits/MATCHED_STATE_PAIRS_08覆盖四个已完成电路的八配对，各20条同base SHA轮；非均匀weighted代价存在但cut列表/ordered pool/dispatch和终点全文SHA均同。原脚本3ef4ceaa…以独立ARCHIVE_MANIFEST_08保字节归档。重复轮不作独立样本，本诊断不代全部矩阵验收、不能外推八电路或因果增益；保持注册参数不变。

## 完整证据分电路归档（LOG76/77，首s27主线后验通过）

full_artifact_archives/s27/receipt.json已生成，覆盖1400文件/25616925B，solid7z采用80MiB分卷配置、实际仅1930551B一卷；whole/volume SHA fdd26b5d…已实核。归档工具receipt记录source稳定、成员/size匹配、7zt与独立scratch恢复全部SHA/size匹配。s27 ROOT_POST_VERIFICATION已独立复核1400source/sidecar/volume/7zt全部通过并接受；授权下步s382/s641，尚不预填结果。当前仅s27完成归档及root验收；不是八电路完整证据全部归档，原实验文件没有删除。

归档阶段快照（LOG79）：s27已root后验accepted；s382与s641 producer verified（源2572/4029文件，包5952319/5872335B，各单卷，receipt/volumeSHA实核），root后验此刻待。s420及其余仍待新冻结完整对象审计后授权；尚非完整八电路证据包完成。

## 区域设计静态预研（LOG81，非正式实验）

region_design_review已冻结partial4初始状态的设计contract与有限census：eligible6/11/10/11、212实际编辑仅F1/F2通过，未做SEC/STA/接受，未注册/未更生产和当前矩阵参数。s27top1 null和uniform平局保留；不能由其他三例静态top1差异声称时序/成本增益，全部top1仍singleton。首oracle失败、v2 exact-source、归因与时长更正/最终manifest均保留。此目录不改变正在跑的C′v3验证域。
