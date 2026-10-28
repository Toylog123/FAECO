# 仓库存储审计（2026-10-21）

- 审计对象：`D:\BaiduSyncdisk\01_Papers\03_FAECO`
- 方法：`Get-ChildItem -Recurse -Force` 全量枚举 + 扩展名聚合 + 逐字节 SHA256 抽样/全量比对
- 单位：下文 GB 均为 GiB（1 GB = 1024³ 字节），与 PowerShell `1GB` 一致
- 状态：**只读审计，未删除、未移动、未改动任何文件**

## 1. 总量

> **执行状态（2026-10-21 晚）**：本审计后的清理已执行，磁盘已用 424.5 → 307.6 GB（净释放 116.9 GB），
> 逻辑体积 161.40 → 125.18 GB，文件数 622,021 → 570,564。执行明细见
> `project_docs/reports/STORAGE_CLEANUP_20261021/README.md`。下表为清理前基线。

| 项 | 数值 |
|---|---|
| 总占用 | **161.40 GB** |
| 文件数 | **622,021** |
| git 跟踪文件 | 4,232（`.git` 仅 279 MB） |

### 1.1 顶层分布

| 目录 | GB | 文件数 | 说明 |
|---|---:|---:|---|
| `experiments/` | 150.7 | 533,549 | 实验产出，被 `.gitignore` 排除 |
| `scratch/` | 8.7 | 52,047 | 临时区，被 `.gitignore` 排除 |
| `paper/` | 0.77 | 3,220 | 论文源 + 各轮 QA 产物 |
| `data/` | 0.45 | 649 | 原始 benchmark（EPFL/ISCAS/SKY130），合理 |
| `.git/` | 0.27 | — | 历史对象 |
| `project_docs/` | 0.27 | 19,672 | 证据包 |
| `.venv/` | 0.27 | — | 可重建 |
| `skills/` | 0.04 | — | |
| `code/` | 0.006 | — | |

**结论：93.4% 的存储是 `experiments/`，且 100% 不在 git 里。**

## 2. 根因一：STA 全量违例路径转储（128.1 GB，占全仓 79%）

`experiments/` 内 `.log` 共 **155,915 个 / 128.1 GB**：

| 体积档 | 文件数 | 合计 GB |
|---|---:|---:|
| ≥200 MB | 304 | 92.5 |
| 50–200 MB | 6 | 0.9 |
| 10–50 MB | 45 | 1.0 |
| 1–10 MB | 5,871 | 10.0 |
| <1 MB | 149,689 | 23.8 |

**304 个文件（占日志数 0.2%）吃掉 92.5 GB。**

生成这些文件的 Tcl（实测样例 `experiments/20260902_phase2_sentinel/b17/eval/iter003_cand003/002__183930__R/sta.tcl`）：

```tcl
report_checks -path_delay max
report_checks -path_delay max -slack_max 0 -endpoint_count 100000
```

来源：`code/src/rseco/opensta.py:336`（`multi_path` 分支）：

```python
tcl_body += "report_checks -path_delay max -slack_max 0 -endpoint_count 100000\n"
```

实测单个 `sta.log`：**6,641,300 行 / 320 MB / 100,001 个 Startpoint 段**（每段约 66 行完整路径）。
b17 这类 WNS ≈ −15 ns 的设计有约 10 万个违例端点，OpenSTA 把每一条完整路径都打印出来。

调用规模：outer-loop 4 轮 × 每轮数十候选 × 每候选数十个门评估 × 每评估 1 次 STA。

gzip 实测压缩率：**30 MB → 1.13 MB（96.2%）**，即这些日志本质是高度重复的文本。

超大日志的实验族归属（≥100 MB，共 309 个 / 93.3 GB）：

| 实验族 | GB | 个数 |
|---|---:|---:|
| `20260902_phase2_sentinel` | 43.19 | 139 |
| `20260901_phase2_sentinel` | 26.99 | 87 |
| `20260826_itc99_main` | 13.85 | 48 |
| 其余 12 个族 | 9.3 | 35 |

## 3. 根因二：0901 与 0902 是完全重复（27.2 GB）

- `20260901_phase2_sentinel`：27.17 GB / 276 文件，2026-09-01 15:41 中断
- `20260902_phase2_sentinel`：43.46 GB / 439 文件，2026-09-02 11:35 干净重跑

逐文件 SHA256 全量比对结果：

- 276 个文件中 **187 个逐字节相同**
- 89 个不同，合计仅 **0.19 MB**（87 个 `sta.tcl` + `map.ys` + `map.log`）
- **相同字节 27.17 GB / 27.17 GB = 100.00%**

89 个差异文件的内容差异只有绝对路径：旧运行写的是 `/mnt/d/BaiduSyncdisk/03_FAECO/...`，重跑写的是 `/mnt/d/BaiduSyncdisk/01_Papers/03_FAECO/...`（仓库搬迁过）。

即：**0901 是 0902 的路径前缀不同版本，无独立信息**。文档中仅 `project_docs/archive/phase0_worktree_salvage_20260912/` 两处提及，当前证据链不引用。

## 4. 根因三：每门一份 mapped.v（17.9 GB，210,996 文件）

单个候选目录（`iter003_cand003`）内 69 个门评估各带一份 `mapped.v`（约 1.9 MB），合计 124 MB。
各份内容因补丁不同而**确实不同**（不同 hash），不是简单复制；但都是文本 Verilog，压缩率高。
全仓 `.v` 共 210,996 个 / 17.9 GB，是第二大项。

## 5. 次级冗余

| 项 | 体积 | 说明 |
|---|---:|---|
| `experiments/20260826_itc99_main/b17/b17/eval_trials.json` | **1.39 GB** | 单个 JSON，内含全量 gate 列表/call_log |
| `scratch/` 的 `r22_*_restorecheck_*` 目录（10 个） | ~7.0 GB | 每次验收把 code/data/experiments/project_docs 整仓复制一份 |
| `scratch/tmp/` | 1.2 GB | 临时 |
| `paper/zh` PNG | **567 MB / 1,210 个** | 主要是各轮 `render_qa/contact_*.png` 接触表（r22 轮 87 MB） |
| `paper/zh` PDF | 76 MB / **161 份** | 同一份稿在多轮目录里重复副本（r27 一轮就 3 份 3.19 MB 同文件） |
| `paper/zh` 字体 | 82 MB | `paper/zh/fonts/` 44.1 MB + `manuscript/fonts/` 37.7 MB 两套近重复 |
| `.git` loose objects | 124 MB / 3,464 个 | `git gc` 可回收（pack 仅 154 MB） |
| `.venv` | 274 MB | 可重建 |

## 6. 风险提示（比体积更严重）

1. **161 GB 完全不在版本控制内**：`.gitignore` 排除了 `experiments/2026*/` 与 `scratch/*`。误删 = 不可恢复（项目规范要求破坏性操作前有 git 兜底，但这里兜不住）。
2. **目录在 BaiduSyncdisk 下**：这 161 GB 会被同步盘持续扫描/上传，造成同步延迟、云端配额占用与冲突文件风险（`.gitignore` 里已有 `*_冲突文件_*` 规则，说明冲突已发生过）。
3. 单文件 320 MB 的日志让备份、迁移、杀毒扫描都变慢；`622,021` 个文件让任何递归操作（含本次审计）都要数分钟。

## 7. 处置建议（按风险从低到高）

### T0 零风险（不动科学证据）

| 动作 | 回收 | 依据 |
|---|---:|---|
| 归档 0901 的 89 个差异小文件（0.19 MB → zip）后删除 `experiments/20260901_phase2_sentinel` | **27.2 GB** | §3 逐字节证明 100% 重复 |
| 删除 `experiments/_stale_20260924_threearm_oldsign` | 0.9 GB | 目录名与文档均标注 stale |
| 删除 `.pytest_cache`、`__pycache__`、`scratch/tmp` | ~1.2 GB | 可重建 |
| `git gc --prune=now` | ~0.1 GB | 仅打包，不改内容 |
| 合计 | **≈29.4 GB** | 161 → ~132 GB |

### T1 保留证据、压缩归档（推荐）

对 2026-10 之前的历史族（0901/0902/itc99_main 等）的 `sta.log` 用 7z/gzip 原地压缩或打包：

- 实测压缩率 96.2% → 93 GB 日志约可降到 **3.5–4 GB**
- 当前在跑的 r22 族（`20261018_r22_D_revalidate_v1` 6.97 GB 日志）暂不动
- 回收 **≈85–90 GB**，161 → **~45 GB**，且字节可完整还原（可附 SHA256 清单）

### T2 治本（改代码，防再发生）

1. `code/src/rseco/opensta.py:334,336`：`-endpoint_count 100000` 改为可配置上限（如 1,000–5,000），或把全量报告写到临时文件、只保留解析所需的前 N 个关键实例，`sta.log` 仅存摘要 + worst slack/TNS。
2. 给 STA 日志加体积上限（如 >64 MB 截断并记 `TRUNCATED` 标记），或落盘即 gzip。
3. `eval_trials.json` 不内嵌全量 gate 列表，改为引用外部文件（1.39 GB 单文件）。
4. 实验 runner 增加"同族旧目录归档/删除"钩子，避免只追加不回收。

### T3 存储层

- 把 `experiments/` 移出 `BaiduSyncdisk`（如 `D:\work\FAECO\experiments`），或在同步盘客户端里设为"不同步"；用 junction 保持路径兼容。
- 只把 `project_docs/evidence/`（275 MB）留在同步盘做备份。

### T4 论文侧

- `review_rounds/` 只保留每轮最终 `FINAL_DELIVERY` + 最终页图，中间 `render_qa/contact_*.png` 与 `export_attempt*/` 删除：567 MB → ~100 MB。
- `paper/zh/fonts/` 与 `manuscript/fonts/` 保留一套。
- `submission/word/superseded/` 三份 2.33 MB docx 可删。

## 8. 复现命令

```powershell
$root = "D:\BaiduSyncdisk\01_Papers\03_FAECO"
# 顶层占用
Get-ChildItem $root -Directory -Force | ForEach-Object {
  $s=(Get-ChildItem $_.FullName -Recurse -File -Force -ea 0|Measure-Object Length -Sum).Sum
  "{0,10:N1} GB  {1}" -f ($s/1GB), $_.Name }
# 扩展名聚合
Get-ChildItem "$root\experiments" -Recurse -File -Force -ea 0 | Group-Object Extension |
  ForEach-Object { "{0,8:N1} GB  {1,6}  {2}" -f ((($_.Group|Measure-Object Length -Sum).Sum)/1GB), $_.Count, $_.Name }
# ≥200MB 日志
Get-ChildItem "$root\experiments" -Recurse -File -Filter *.log -Force -ea 0 |
  Where-Object Length -ge 200MB | Measure-Object Length -Sum
```
