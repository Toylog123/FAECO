# Git 首次提交范围审计

更新时间：2026-07-20

## 1. 审计目标

本审计用于确定 FAECO 首次 Git 基线中哪些文件可以进入工程历史，哪些文件只应保留在当前同步盘，以及首次提交前还需确认哪些身份、许可和发布边界。这里的许可判断是工程来源治理，不替代正式法律意见。

## 2. 当前仓库事实

| 项 | 当前状态 | 影响 |
|---|---|---|
| Git 历史 | `main` 分支，22 commits (`9482a34..eb07e6e`) | A-only 范围 135 个核心文件已分批入库；按 handoff `initial_commit_scope_audit.md` 实际边界执行 |
| 远端 | 未配置 remote | 仓库当前为本地基线，push 决策由用户决定 |
| 未忽略候选 | 60 个 untracked 顶层目录/文件 | 剩余 untracked 包括 `.codex-handoff.json`、`benchmarks/raw/`、`data/`、`paper/`、`experiments/2026*_*`（实验产物）、`experiments/tmp_yosys_json_probe/`；按 A-only 范围不应入库 |
| `.gitignore` | 已忽略 `tmp/`、Python cache、日志和构建产物 | SAT 正确核验缓存与文档渲染缓存不会进入提交 |
| Git LFS | 已安装 3.7.1；未配置 `.gitattributes` | LFS 只能处理大文件存储，不能授予论文或 benchmark 再分发权 |
| Git 身份 | 当前为 `Toylolog <Toylolog@local>`（local repo 临时身份） | push 前需用真实身份或保留 local 状态 |
| 仓库许可 | 顶层无 `LICENSE`、`NOTICE` 或 `COPYING` | 在决定公开范围前不能把仓库称为公开可再分发项目 |
| 行尾策略 | `core.autocrlf=true` | 22 commits 全部接受 LF → CRLF warning；8 个 mixed / 11 个 CRLF-only / 16 个 BOM 文件仍 untracked；push 前显式决定 `.gitattributes` |

## 3. 文件分层

统计基于 `git ls-files --others --exclude-standard`，不包含 `.git/`、`tmp/` 和 Python cache。

| 分层 | 文件数 | 大小 | 当前处理 |
|---|---:|---:|---|
| A. 工程核心候选 | 136 | 约 0.67 MiB | 已完成隔离副本 dry-run；仍需提交前 staged diff 复核 |
| B. 本机 smoke/不可移植产物 | 51 | 约 0.60 MiB | 推荐不进入可推送历史；待 EPFL 主数据和便携配置替换后再处理 |
| C. 私有或版权原始材料 | 55 | 约 94.08 MiB | 推荐保留在同步盘，不进入工程 Git 历史 |

### A. 工程核心候选

包括项目代码、测试、脚本、派生文档、source manifests、c17 手工最小联调输入和目录占位文件。文档中可以保留对本地材料的相对路径索引，但不携带原始论文正文、生成实验目录或本机工具路径快照。

该分层表示“当前未发现与 B/C 相同的明确再分发障碍”，不等同于仓库已经具备公开发布许可。正式公开前仍需确定仓库 LICENSE，并复核配置是否引用仅本机存在的数据。

### B. 本机 smoke/不可移植产物

当前包括：

- `benchmarks/raw/iscas85/c432.v`、`c499.v`、`c880.v`；
- `data/cases/minimal/iscas85_c432_case01/`、`iscas85_c499_case01/`、`iscas85_c880_case01/`；
- `experiments/configs/minimal_combinational.json`；
- `experiments/20260717_minimal_combinational_demo/`；
- `experiments/20260718_minimal_combinational_batch_demo/`；
- `experiments/environment/toolchain_2026-07-15.json`。

三份 raw Verilog 来自许可未声明的第三方整理仓库；对应 case、5-case config 和 batch artifact 由这些输入派生，因此一起按本地 smoke 处理。single-demo config 和环境快照包含本机绝对路径，也不进入可移植核心。source manifest、来源审计和不可再分发说明属于 A 类，可保留。

### C. 私有或版权原始材料

当前包括：

- `论文/`：3 个文件，约 4.71 MiB；
- `课题构想/`：3 个文件，约 0.06 MiB；
- `ECO相关文献/`：49 个文件，约 89.32 MiB，其中 47 个 PDF。

这些目录继续按“原位、只读、同步盘保留”管理。将 PDF 交给 Git LFS 不会改变版权状态；一旦写入 Git 历史，后续即使删除工作树文件也需要重写历史才能彻底移除。

## 4. 推荐提交策略

推荐采用“工程核心仓库 + 本机材料库”两层结构：

1. 首次提交只纳入 A 类工程核心候选，不使用全量 `git add .`。
2. B 类继续本机 smoke；X21 导入带 MIT notice 的 EPFL 数据后，用许可明确的 cases、便携配置和 batch artifacts 替换论文主数据。
3. C 类不写入工程 Git 历史，由当前同步盘继续承担原始材料归档。
4. 首次提交前确认 Git 作者身份、仓库是否仅私有，以及是否添加项目 LICENSE。
5. staging 后必须检查文件清单、总大小和大文件，再运行测试与 JSON/实验一致性验证。

不推荐“先全量提交，之后再删除”。该做法会把 94 MiB 原始材料和许可不完整数据永久写入首个历史对象，增加后续发布、清理和审计成本。

## 5. 提交前门槛

| ID | 门槛 | 当前状态 | 通过条件 |
|---|---|---|---|
| COMMIT-01 | 范围确认 | pending | 明确采用 A-only、private-all 或其他指定范围 |
| COMMIT-02 | 作者身份确认 | pending | `user.name` 和 `user.email` 为期望值 |
| COMMIT-03 | 发布属性确认 | pending | 明确本地私有、私有远端或未来公开 |
| COMMIT-04 | 原始材料隔离 | ready | C 类不进入 staged files |
| COMMIT-05 | benchmark 隔离 | ready | B 类不进入可推送历史，或取得明确许可 |
| COMMIT-06 | 缓存隔离 | pass | `tmp/`、`__pycache__/`、`*.pyc` 已被忽略 |
| COMMIT-07 | staged diff 审计 | not_run | staged 文件数、大小、大文件和路径分类全部符合批准范围 |
| COMMIT-08 | A-only 回归验证 | needs_refresh | `tmp/initial_commit_a_only_dry_run_20260720_01/` 在 OpenSTA 安装和工具链检测修复前通过 47 项测试；当前主工作区已新增工具链回归并通过 50 项测试，首次 staging 前必须刷新 A-only 副本 |
| COMMIT-09 | 便携 batch 配置 | pending | X21 EPFL 配置或获批的 c17-only 配置进入核心，clean checkout 无需 B 类文件即可运行 batch |
| COMMIT-10 | A-only 静态卫生 | pass | 无凭据、私钥、非法 UTF-8、冲突标记、尾随空格、路径碰撞或不可移植绝对路径 |
| COMMIT-11 | 行尾策略 | pending | 确认是否在首次提交前引入 `.gitattributes`，避免 `core.autocrlf` 隐式归一化造成难审计 churn |

## 6. A-only dry-run 证据

最终 A-only 规则排除 B/C 两类以及所有已生成实验目录和本机环境快照。完成 2026-07-20 路线决策同步和 WSL2/OpenSTA 安装前实测记录后，验证副本曾刷新到 Git 忽略的 `tmp/initial_commit_a_only_dry_run_20260720_01/`，不进入提交。

注意：随后本工作区又新增了 OpenSTA 安装记录、`experiments/environment/toolchain_2026-07-20.json`、工具链检测脚本修复和 3 项测试回归，主工作区当前测试数为 50。下表保留为上一版 dry-run 证据，不能直接作为当前首次 staging 的最终通过证据；正式提交前需要按更新后的 A-only 规则重新生成副本、复核文件数/哈希并运行 50 项测试。

| 检查 | 结果 |
|---|---|
| A-only 源路径 | 136 个，约 0.67 MiB；无 PDF/DOCX，无本机工作区绝对路径 |
| 路径清单 SHA256 | `051CB1584CEA537E3101A554878199FB6B47D26A54641C4A5CEDD69599765227` |
| 文件闭包 | 136 个路径全部复制，missing=0、mismatch=0 |
| 单元测试 | 47 项通过；当前主工作区已升级为 50 项，需刷新 |
| single demo | 成功从空实验目录重建 |
| c17 batch probe | 临时 2-case config 成功运行，case_count=2 |
| formal/ABC 边界 | 2 个 case 均为 `unavailable`，未误写为 pass |
| recovery 边界 | `measurement_scope=stage_a_proxy` |

原 5-case `minimal_combinational.json` 在 A-only 副本中会因 c432/c499/c880 被排除而失败。这不是 runner 回归，而是已确认的配置依赖闭包；因此该配置归入 B 类，COMMIT-09 在 EPFL 配置或获批 c17-only 配置进入核心前保持 pending。

## 7. A-only 静态卫生证据

| 检查 | 结果 |
|---|---|
| 凭据模式 | 私钥、AWS/GitHub/OpenAI token、密码赋值和带凭据 URL 命中 0 |
| 身份信息 | 仅命中审计中明确记录的 `Toylog@example.com` 占位身份，COMMIT-02 关闭时替换 |
| 路径 | 大小写碰撞 0、超过 240 字符 0、尾随点/空格组件 0、symlink 0；最长相对路径 83 字符 |
| 内容编码 | 非法 UTF-8 0、NUL byte 0、冲突标记 0、尾随空格 0 |
| 二进制 | A 类 PDF/DOCX/PPTX/XLSX 为 0 |
| 机器路径 | A 类无本机工作区绝对路径；`C:\tools\...` 仅为工具链文档示例 |
| 开发占位标记 | 显式占位注释命中 0 |
| 当前换行分布 | LF-only 116、CRLF-only 11、mixed 8；UTF-8 BOM 16（BOM 与换行类别重叠） |

凭据与可移植性检查通过。换行分布不影响当前测试，但仓库尚无 `.gitattributes` 且 `core.autocrlf=true`；因此不在本批次擅自批量改写这些行尾和编码差异，而把规范化策略作为 COMMIT-11 显式决策。

## 8. 当前结论

当前不应直接创建全量首次提交。A-only 范围曾通过隔离副本测试、single/c17-batch probe 和静态卫生检查，但 OpenSTA 安装记录与工具链检测修复后已需要刷新；推荐的下一步不是引入 Git LFS，而是确认 A-only 范围、真实 Git 身份、仓库发布属性和行尾策略。确认后重新生成 A-only 副本、执行精确 staging、staged diff 审计、正式工作树回归验证和首次提交；便携论文主 batch 配置由 X21 关闭。
