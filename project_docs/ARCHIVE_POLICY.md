# 归档与版本迭代规范

> 任何**可能版本迭代的对象**都有明确的归档方式：**当前版本在工作区，历史版本只读归档**。
> 本文档统一规范全项目各对象的归档位置、时机与命名，保证换版本不丢历史、不糅杂。

## 一、总则

1. **当前版本**：工作在最新版本上（`code/`、`paper/zh/manuscript/`、`experiments/` 等）。
2. **历史版本**：归档到约定位置，**只读、不可变**。
3. **切换版本**：通过 git（checkout / tag）、基线（baselines/）、归档目录完成。
4. **归档前先固化**：先 `git commit` / 快照，再归档。
5. **归档只读**：归档后不修改；补充说明写归档目录的 README。

## 二、各对象归档规范

| 对象 | 当前版本位置 | 历史版本归档 | 归档时机 | 命名 |
|------|-------------|-------------|----------|------|
| 源码 / 代码 | `code/src/` | git（commit / tag）+ `versions/<基线ID>/` 完整快照 | 阶段性完成 | commit / 基线ID |
| 测试 / 脚本 | `code/tests/` `code/scripts/` | git + versions 快照 | 同源码 | commit |
| 论文（审稿迭代） | `paper/zh/manuscript/` | `paper/zh/review_rounds/r<N>_<日期>/`（意见+回复+修改前论文） | 每轮审稿 | `r<N>_<YYYYMMDD>` |
| 论文（投稿 / 发表） | manuscript 当前稿 | 基线绑定（`baselines/`）+ versions | 阶段定稿 | 基线ID |
| 实验 / 评估 | `experiments/` 定义 | `project_docs/evidence/` 不可变证据包 | 每次运行 | `<YYYYMMDD>_r<N>` |
| 数据 | `data/manifests/` 登记 | `data/raw|derived/`（git-ignored）+ manifests 记录 | 获取 / 更新时 | manifests |
| 图表 | `figures/candidates/`（草图） | `figures/final/`（定稿）+ `figures/sources/`（源） | 定稿时 | `fig<N>` |
| 文档（技术说明 / 设计） | `docs/` `code/src/DESIGN.md` | git 承载 | 内容变更 | commit |
| 配置 / 环境 | 工作区 | git + `docs/environment.md` | 变更时 | commit |
| 基线 | 当前 active | `baselines/`（superseded / archived） | 冻结时 | 基线ID |
| 技能 | `skills/` | `project_docs/agent_handoff/skill_snapshots/` | 技能变更 | 技能名 |
| 术语 / 交叉表 | `docs/GLOSSARY.md` `paper/GLOSSARY.md` `CROSSWALK` | 随版本同步更新 | 术语 / 数据变更 | 同步 |
| 项目模板本身 | 当前目录 | git tag | 发布 | `v<N>` |

## 三、版本切换流程

1. 确认当前版本状态（`git status`、基线 active）。
2. 归档当前版本：按上表归档 + `git commit`（必要时 `git tag`）。
3. 建立 / 切换到新版本（新基线或 git 分支）。
4. 归档目录与当前工作区互不引用（零交叉，见 `versioning.md`）。

## 四、常见情形演练

### 1. 论文审稿迭代
```
收意见 → review_rounds/r1_日期/（意见+回复+修改前论文）→ 修改 → 一致性检查
      → r2_日期/ → … → 定稿打基线 → 投稿
```

### 2. 代码大改 / 重构
```
git commit / tag 固化 → 复制 versions/<新基线ID>/ 快照 → 改 code/ → 新基线
```

### 3. 实验重跑 / 新配置
```
旧结果 evidence/<旧日期>_r<N>/ 保留（不可变）→ 新结果 evidence/<新日期>_r<N+1>/
→ 交叉表登记新旧 → 不覆盖旧包
```

### 4. 数据更新
```
新数据入 data/raw|derived/（git-ignored）→ 更新 data/manifests/ 登记（新 hash）
→ 旧 manifest 保留 → 证据包引用对应版本
```

### 5. 论文投稿 / 发表
```
定稿 → 打基线（baselines/）+ git tag → manuscript 冻结 → 归档 review 历史
```

### 6. 技能升级
```
更新 skills/<名>/ → 同步 skill_snapshots/<名>.SKILL.md 快照 → 旧快照保留
```

### 7. 文档（技术说明 / 设计）迭代
```
改 docs/ 或 DESIGN.md → git commit（历史由 git 承载）→ 结构变更同步 README/AGENTS
```

### 8. 图表迭代
```
草图 candidates/ → 定稿 final/（源 sources/）→ 旧图不删（candidates 保留）→ 提示词文件留档
```

## 五、规则

1. 归档目录**不堆积无关文件**（每类对象固定结构，见上表）。
2. **禁止**：覆盖已归档版本；在归档目录改文件；新旧版本糅杂在同一位置。
3. 归档与 `versioning.md`（版本定义）、`evidence/`（证据）、`review_rounds/`（审稿）配合。
