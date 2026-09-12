# Phase 2 b17 G5 门禁 handoff (2026-09-02)

更新时间：2026-09-02 12:51 (Asia/Shanghai)

状态：T01/T02 完成并落 commit `32b77b0`；T03 当前 HEAD 干净重跑运行中（python3.11 PID 46452，11:35:45 启动），已跑 80 min，iter001 完成（41 子候选），iter002 进行中（10+ 子候选）。预计 ~3h 后产出 `sentinel_manifest.json`（15:25 左右）；若中途崩溃保留 `20260902` 不动并启动 `20260903_phase2_sentinel`。

## 1. 项目背景

- FAECO Phase 2 G5 门禁矩阵需要对 4 个 sentinel case（s27、s382、b15、b17、b18、picorv32）跑完整 outer-loop 并记录 evidence。
- b17 历史 `b17-balanced-20260828T052410861999Z-c7e4b55f` 跑出 160 候选全 rejected，WNS 没动（-16.53）；诊断结论是该 run 早于 `27e6020 fix(acceptance)`，不能作为当前实现的反例。
- 修复已 commit `27e6020`，但缺一次当前 HEAD 的干净重跑证明 `27e6020` 有效。

## 2. 当前状态

- **T01 完成**：G5 矩阵 b17 行从 `pending → running` 改为 `failed`，并补 `docs/phase2/sentinel-b17.md` 描述历史失败原因 + T03 列表。落 commit `32b77b0`。
- **T02 完成**：160 候选全 rejected 的诊断；F5 拒绝原因主要是 `F5_verification_too_expensive` (111) + `acceptance_budget_unavailable` (75) + `acceptance_budget_violation` (27)；其中 56 候选实际改善 WNS 但被旧 F5 错杀。结论：旧运行早于 `27e6020`，不能反证实现缺陷。
- **T03 进行中**：见下表。

| 字段 | 值 |
|---|---|
| 输出目录 | `D:\BaiduSyncdisk\03_FAECO\experiments\20260902_phase2_sentinel\b17` (D 盘) |
| 工作树 | `C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-phase0-stabilization` |
| 分支 / HEAD | `codex/faeco-phase0-stabilization` @ `32b77b0` |
| 进程 | python3.11 PID 46452（父进程已结束，python3.11 直接挂在 session 1 下），started 2026-09-02 11:35:45 |
| 命令 | `python -u scripts/run_outerloop_real_wns.py --circuit b17 --source-file benchmarks/raw/itc99/v/b17.v --period 0.5 --output-dir D:\BaiduSyncdisk\03_FAECO\experiments\20260902_phase2_sentinel --search-policy balanced --max-iterations 4 --candidates-per-iteration 1 --joint-enumerate-depth 3 --strategies R,G,B --priority-table src/rseco/strategy_priority_table.json --workers 1` |
| 已写子候选 | iter001_cand001 完成（41 子候选：17 策略 + 1 topology + 23 JOINT）；iter002_cand002 进行中（10+ 子候选） |
| 当前轮次 | iter2 cand2，子候选按 ~1.4 min/候选推进 |
| 期望完成 | iter002 done ~13:33；iter003 ~14:29；iter004 ~15:25；总时长 ~3h50m |
| 当前 D 盘可用 | ~57 GiB（应该够，sta.log 单文件最大 ~333 MB） |

## 3. 接手人下一步（按顺序）

### 3.1 监控 T03 直至 `sentinel_manifest.json` 落盘

```powershell
# 进程是否还活着
Get-Process python3.11 -ErrorAction SilentlyContinue | Select Id, StartTime, CPU, WS
# 子候选进度
Get-ChildItem 'D:\BaiduSyncdisk\03_FAECO\experiments\20260902_phase2_sentinel\b17\eval' -Recurse -Directory |
  Sort-Object LastWriteTime -Descending | Select -First 10 FullName, LastWriteTime
# 等 manifest
Test-Path 'D:\BaiduSyncdisk\03_FAECO\experiments\20260902_phase2_sentinel\b17\sentinel_manifest.json'
```

如果中途进程消失 / 长时间无新子候选（>30 min）→ 保留 `20260902_phase2_sentinel` 不动，启动 `experiments\20260903_phase2_sentinel\b17` 干净重跑（命令同上，`--output-dir` 改日期目录）。

### 3.2 核对 manifest 字段

`sentinel_manifest.json` 必须有：
- `git_head_sha` == `32b77b066e72f6cfb7794b29d0e4647633460ea5`（不是 `null`）
- `toolchain.yosys` / `toolchain.abc` 非空
- `outcome.baseline_wns` / `outcome.wns_history`（4 轮最终 WNS 数组）
- `outcome.iterations` ≥ 1
- `outcome.soft_cost_events`（soft cap 触发计数）
- `outcome.final_patch_id` 若非 null → 必须有 SEC evidence
- SEC 文件存在：`topology-sec/<id>/sec.log` 或 manifest 内 SEC 段

### 3.3 更新 docs

- `docs/phase2/g5-matrix.md` b17 行：根据 T03 结果改 ✅ 或 ❌，并替换 manifest 链接到 `experiments/20260902_phase2_sentinel/b17/sentinel_manifest.json`。
- `docs/phase2/sentinel-b17.md`：把 "Current-head rerun (T03)" 表格里 `20260902` 行替换为真实结果（manifest 路径、SEC 结果、最终 WNS、accepted patch id、wns_history）。

### 3.4 提交 & 推送

- 本地提交：`docs: phase2 b17 sentinel T03 result + g5-matrix update`
- 当前分支无 upstream，`push` 需要用户明确授权（不要自作主张 `git push`）。

## 4. C 盘 worktree 体积来源（已解释）

`C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-phase0-stabilization` 工作树当前 64.18 GiB，来源：

```
experiments/20260828_phase2_sentinel       61.98 GiB  ← 历史失败 b17 run（已 commit）
experiments/20260831_phase2_sentinel_clean  2.20 GiB  ← 老 clean 重跑尝试（commit 过）
experiments/20260831_phase2_sentinel        0.00 GiB  ← preflight-only 占位
```

历史数据已在 git 历史里，rewrite 历史 (`git filter-repo` / BFG) 风险大，建议**保持现状**：
- 不再在 worktree 里跑新实验（已切到 D 盘 `--output-dir`）。
- `experiments/` 在 `.gitignore` 里被忽略，新跑出来不会被 commit。
- 如果未来确实要瘦身，分两步：(a) 备份到 D 盘外部目录；(b) `git filter-repo --path experiments/20260828_phase2_sentinel --invert-paths` 后 force-push 到新分支（需要用户授权 + 远端协调）。

C 盘可用：~43 GiB。**禁止**在 C 盘再开新 worktree 或跑新大实验。

## 5. 不能动的部分

- `D:\BaiduSyncdisk\03_FAECO` 主目录有 130 项历史脏改动；不要 merge、reset、checkout -- 或 cleanup。
- `experiments/20260828_phase2_sentinel/` 是历史失败证据，T01 已把它从 G5 矩阵 `running` 改 `failed`，不要再改回去。
- 修复 commit `27e6020` 在 T03 落盘前不要宣称"`27e6020` 有效"——必须等 manifest + WNS 证据齐了再下笔。

## 6. 关键文件

- 工作树根：`C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-phase0-stabilization`
- 当前 HEAD：`32b77b066e72f6cfb7794b29d0e4647633460ea5`
- G5 矩阵：[docs/phase2/g5-matrix.md](../../docs/phase2/g5-matrix.md)
- b17 文档：[docs/phase2/sentinel-b17.md](../../docs/phase2/sentinel-b17.md)
- 历史失败 manifest（保留）：`experiments/20260828_phase2_sentinel/b17/sentinel_manifest.json`
- 进行中输出：`D:\BaiduSyncdisk\03_FAECO\experiments\20260902_phase2_sentinel\b17`
- 外环脚本：[scripts/run_outerloop_real_wns.py](../../scripts/run_outerloop_real_wns.py)
- 策略优先级表：[src/rseco/strategy_priority_table.json](../../src/rseco/strategy_priority_table.json)

## 7. 接管 snapshot（开新 turn 时第一件事）

```powershell
Set-Location 'C:\Users\佟亚龙\.config\superpowers\worktrees\03_FAECO\faeco-phase0-stabilization'
git status -sb
git log --oneline -3
Get-Process python3.11 -ErrorAction SilentlyContinue | Select Id, StartTime, CPU, WS
Test-Path 'D:\BaiduSyncdisk\03_FAECO\experiments\20260902_phase2_sentinel\b17\sentinel_manifest.json'
Get-ChildItem 'D:\BaiduSyncdisk\03_FAECO\experiments\20260902_phase2_sentinel\b17\eval' -Recurse -Directory |
  Sort-Object LastWriteTime -Descending | Select -First 5 FullName, LastWriteTime
```

如果以上 Python 进程还在、manifest 还没生成 → 继续监控。
如果 Python 已退、manifest 已生成 → 跳到 §3.2 核对并更新文档。
如果 Python 已退、manifest 没生成 → 跳到 §3.1 的 fallback 启动 `20260903_phase2_sentinel`。
