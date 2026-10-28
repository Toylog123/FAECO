# 存储清理执行记录（2026-10-21）

- 授权：用户选择「零风险档 + 论文/scratch 清理」
- 执行环境：`D:\BaiduSyncdisk\01_Papers\03_FAECO`，NTFS，D: 剩余空间 175.5 GB（执行前）
- 原则：不删无法验证的独特数据；删除前先出清单；能归档的一律归档
- 状态：**最后一步 NTFS 压缩仍在后台运行**，其余已完成

## 1. 已执行项

| # | 动作 | 回收 | 依据 | 回退方式 |
|---|---|---:|---|---|
| 1 | 删除 `experiments/20260901_phase2_sentinel` | 27.17 GB | 与 `20260902_phase2_sentinel` 逐文件 SHA256 全量比对：相同字节 27.17 GB / 27.17 GB（100.00%），仅 89 个 <0.2 MB 的 tcl/ys/log 因绝对路径前缀不同而不同 | `20260902_phase2_sentinel` 保留，内容等价；清单见 `manifest_20260901_phase2_sentinel.csv` |
| 2 | 删除 `experiments/_stale_20260924_threearm_oldsign` | 0.90 GB | `.gitignore` 注释明确「stale，不参与任何证据链」；目录名自带 stale | 清单 `manifest_stale_threearm_oldsign.csv`（含 SHA256） |
| 3 | 删除 `.pytest_cache`、`experiments/__pycache__` | <0.01 GB | 可再生缓存 | 重新生成 |
| 4 | 归档后删除 `scratch/tmp` + 11 个 `scratch/r22_*_restorecheck_*` | 8.36 GB → 0.35 GB | 均为整仓副本/临时件；归档保留全部 42,694 个文件（7z 校验：8,976,929,941 字节原始大小） | `scratch/_archive_cleanup_20261021.7z`（7z x 解压即可原样恢复目录结构） |
| 5 | 清理论文中间产物 | 0.15 GB | 被更新构建替代的 render_qa / export_attempt / superseded / tmp | 清单 `manifest_paper_pruned.csv`（含 SHA256）；`superseded/` 中 7 个文件为 git 跟踪，`git checkout -- <path>` 可恢复 |
| 6 | 对 `experiments/` 开启 NTFS 透明压缩 | **80.6 GB（磁盘）** | 路径、文件名、字节内容、SHA256 均不变，仅改变磁盘存储方式 | `compact /u /s /f /i` 可整体解压还原 |

### 第 6 项实测结果

```text
740,422 files within 215,260 directories were compressed.
131,646,198,587 total bytes of data are stored in 45,590,832,493 bytes.
The compression ratio is 2.9 to 1.
用时 24.6 分钟，退出码 0
```

- 抽样校验：`20260902_.../iter003_cand003/002__183930__R/sta.log` 压缩前 SHA256 `F7A39CED…40C139A`，压缩后**完全一致**；磁盘占用 335,515,998 → 125,820,928 字节（2.7:1）
- 全仓：逻辑体积 161.40 → **125.18 GB**；磁盘已用 424.5 → **307.6 GB**（净释放 **116.9 GB**）；文件数 622,021 → 570,564

### 论文侧具体删除项（第 5 项）

- `paper/zh/submission/word/superseded/`（3 份旧 docx + 3 份 PDF + README，git 跟踪）
- 全部 `export_attempt*` 目录（8 个，失败导出的中间件）
- `r24_20261018/build02|build04/render_qa`（最终版为 build05）
- `r22_20261016/.../en_float_refinement_v2|v3|v4`（最终版为 v5）
- `paper/zh/tmp/`（渲染临时件）

保留：每轮最终 build 的 render_qa 页图、`figures/`、所有 `FINAL_DELIVERY`、`project_docs/evidence/`。

## 2. 回执文件

目录：`project_docs/reports/STORAGE_CLEANUP_20261021/`

| 文件 | 内容 |
|---|---|
| `manifest_20260901_phase2_sentinel.csv` | 276 个文件的相对路径 / 字节数 / SHA256 |
| `manifest_stale_threearm_oldsign.csv` | 8,107 个文件的路径 / 字节数 / SHA256 |
| `manifest_paper_pruned.csv` | 378 个文件的路径 / 字节数 / SHA256 |
| `scratch/_archive_cleanup_20261021.7z` | 42,694 文件完整归档（0.35 GB） |

校验归档：

```powershell
& 7z t "D:\BaiduSyncdisk\01_Papers\03_FAECO\scratch\_archive_cleanup_20261021.7z"
& 7z l "D:\BaiduSyncdisk\01_Papers\03_FAECO\scratch\_archive_cleanup_20261021.7z" | Select-Object -Last 3
```

## 3. 未执行（需另行决定）

1. **代码未改**：`code/src/rseco/opensta.py:336` 的 `-endpoint_count 100000` 仍在，下次跑 outer-loop 还会产生 300 MB 级 `sta.log`。改动会改变 STA 报告内容，需走回归测试，未擅自改。
2. **未动 Baidu 同步配置**：`experiments/` 仍在 `BaiduSyncdisk` 下，下次同步客户端启动时可能因压缩导致的文件改动重新上传。
3. **未删**：`20260902_phase2_sentinel`（43.5 GB，历史 G5 门禁证据）、`20260826_itc99_main`（18 GB，被 r22 B3 审计引用）、`20261018_r22_D_revalidate_v1`（7.7 GB，当前证据）、`.venv`（274 MB，可重建）、`data/raw`（456 MB，benchmark 原件）。

## 4. 复核命令

```powershell
$e = "D:\BaiduSyncdisk\01_Papers\03_FAECO\experiments"
# 压缩属性抽查
compact /q "$e\20260902_phase2_sentinel\b17\eval\iter003_cand003\002__183930__R\sta.log"
# 哈希未变抽查（应与清理前一致）
Get-FileHash "$e\20260902_phase2_sentinel\b17\eval\iter003_cand003\002__183930__R\sta.log" -Algorithm SHA256
```
