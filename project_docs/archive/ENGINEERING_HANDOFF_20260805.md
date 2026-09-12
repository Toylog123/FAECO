# FAECO 项目交接说明（2026-08-05 晚）



> 目的：接手人快速恢复真实状态，继续 N31-05（评审短板补齐）的 Hold 修复与收尾。

> 中文交流；所有时间以 `date` 为准。



## 1. 项目与环境



- 项目根：`D:\BaiduSyncdisk\03_FAECO`（git 分支 main，已 push 至 origin/main，HEAD=`48a0c40`）

- 目标：补齐论文评审 5 条短板，**不做叙事降级**，要真实改进（物理感知/决策智能/场景扩展/理论对比/鲁棒性）

- 论文唯一源：`paper/zh/manuscript/faeco_paper.tex`（LaTeX；`paper/draft/*.md` 已废弃）

- 回归：`$env:PYTHONPATH="src"; python -m pytest -q`（最新 **241 passed + 1 subtest**，78s）

- 实验产物（`experiments/2026*_*`）按 A-only 不入库；commit 风格 `feat(N31-05): ...` / `docs(N31-05): ...`



## 2. 当前未提交工作（Hold 修复，短板 3）



已改（未 commit）：

- `src/rseco/opensta.py`：`run_opensta_sequential` 增加 `hold_uncertainty` / `min_path` 参数，解析 `worst slack min` 返回 `min_slack`/`min_slack_status`

- `src/rseco/real_wns.py`：`RealWnsEvaluator` 增加 `hold_mode` / `baseline_min_slack` / `hold_uncertainty`；STA 调用透传；hold 模式按“严格改善 min slack 且不劣化 setup WNS”接受候选；improved 按 min slack 判定

- `scripts/run_sequential_timing_check.py`：`run_opensta` 增加 `hold_uncertainty` 参数 + `min_slack` 解析

- `scripts/run_outerloop_real_wns.py`：新增 `--hold-mode` / `--hold-uncertainty`，baseline/构造/输出均接线

- `tests/test_real_wns.py`：+3 个 hold 测试（接受/拒绝/无 min_slack 兜底）

- 新增 `src/rseco/hold_repair.py` + `tests/test_hold_repair.py`：B 策略 hold 修复（DFF D 端插 buffer 链），6 测试全绿



## 3. 已完成验证（真实数据）



### Hold 场景（刚跑通）

- `tmp_hold_probe/s382/`：Yosys 映射 + `run_opensta(..., hold_uncertainty=0.8)` → `wns=-0.94 min_slack=-0.36`（真实 OpenSTA）

- `run_opensta_sequential(..., min_path=True)` → 解析出 hold 端点 `DFF_2`、58 个 combinational 实例（顺序正确），`min_slack=-0.36 VIOLATED`

- 证明：Hold 修复管线可端到端运行（映射→min-path STA→候选解析→插 buffer→再 STA）



### Adaptive（实验数据在磁盘，A-only）

- `experiments/20260805_adaptive_iscas89/{s820,s832,s953}/outerloop_result.json` 确认：

  - s820：-1.42→-1.28（STA 18）｜s832：-1.15→-1.12（STA 43）｜s953：-1.48→-1.38（STA 11）

  - 全部 success=True，2 轮收敛；s820 自适应超越静态表（-1.36）

- 其余 5 电路（s27/s382/s420/s641/s713）为摘要记录（-0.21/-0.93/-1.75/-1.85/-1.85），本次未逐条重跑核验，见 commit c98edf1 与 task_board



### SPEF 寄生（真实负面结论）

- `experiments/20260805_parasitic_s382/summary.json`：ideal -0.94→-0.93（+0.01），SPEF -2.37→-2.37（0）

- `experiments/20260805_parasitic_b18/summary.json`：ideal -0.69→-0.56（+0.13），SPEF -6.63→-6.63（0）

- 论文已如实记录：理想网络下的修复在寄生 RC 下归零（短板 1 的诚实边界）



## 4. 下一步（按序）



1. **写 Hold 修复 runner**：`scripts/run_hold_repair.py`（用 `HoldRepairEvaluator`），真实跑 s382 hold 场景，验证插 buffer 能改善 `min_slack` 且 WNS 不劣化

2. **审查**：跑完实验后按用户要求出审查记录（不理想找根因）；audit agent `audit_adaptive_spef` 与 `audit_b18_joint` 已被中断，可重启

3. **文档/论文同步**：Hold 支持写入 `docs/engineering/n31_05_sequential_eco.md` §12.x、`docs/task_board.md` N31-05、`docs/project_management/work_log.md`（注意该文件是 GBK 编码，写中文前先确认编码）、`paper/zh/manuscript/faeco_paper.tex`（场景扩展段落 + synthetic hold 标注）

4. **收尾**：清理临时文件（`tmp_hold_probe*`、`tmp_spef_probe*`、`tmp_multipath_verify/`、`zz_patch_probe.txt`、`.codex-handoff.json` 视情况）；`data/cases/minimal/iscas85_c17_case01/results/abc_baseline/abc_rewrite_refactor_resyn.blif` 有一行时间戳噪声（ABC 重跑），建议还原或忽略

5. **提交 + push**：`feat(N31-05): hold-aware repair mode`，再补文档 commit



## 5. 已知坑



- Windows 中文/反斜杠写文件：优先 JS 逐行构造 + utf8ToBase64 → PowerShell 写临时 .py → python 执行；apply_patch 对中文大段不可靠

- JS 模板字符串里 `\n` 会变成真换行；插入 LaTeX/源码需用 `chr(92)`

- tex 曾因 `\textbf{` 孤立残留、`{lcccc}` 列数不符、裸下划线编译失败；**每次改 tex 段落必须 latexmk 编译验证**

- 全量回归 ~75-85s；latexmk ~4-11s

- b19 baseline min slack +0.41（无真实 hold 违例）——hold 实验需人为构造约束，论文要透明标注 synthetic

- 若 audit agent 继续卡住：先 interrupt，再自行只读核验（结果 JSON 都在 experiments/）

## 6. Hold 修复已完成（2026-08-05 收尾）

- commit 4a7f226（代码）+ b82907c（文档/论文），已 push
- s382 hold：min_slack -0.36→-0.33（2 轮 B），WNS -0.94→-0.93；s27 诚实无改善
- 论文 tex 新增 sec:hold（synthetic 透明标注），PDF 编译 10 页
- 全量回归 241+1 全绿；实验产物 experiments/20260805_hold_repair/（A-only）

## 7. 下一步（效果提升，见 docs/EFFECT_IMPROVEMENT_PLAN_20260805.md）

1. P0 物理感知闭环：OpenROAD P&R post-layout 复测，让 G/B 在真实线负载下生效
2. P1 联合动作空间：R+G 组合 / 多策略序列，OpenSTA 实测选优
3. P2 warm-start 决策层 + 候选聚类降探索
4. P3 真实 hold（post-layout min slack 负）替换 synthetic
