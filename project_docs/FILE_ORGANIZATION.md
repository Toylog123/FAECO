# 文件分类与命名规范（多级目录模型）

> **多级目录，每级按一个分类维度**：一级版本 → 二级实验类型 → 三级具体实验 → 四级运行日期 / 批次。
> 查文件时沿层级定位，不混块、不散落。

## 一、多级目录模型（每级一个维度）

| 层级 | 维度 | 示例 |
|------|------|------|
| 一级 | 版本 / 基线 | `v1` / `v2` / `<基线ID>` |
| 二级 | 实验类型 / 域 | `rtl` / `power` / `algorithm` / `paper` |
| 三级 | 具体实验 | `rule_update` / `scan_boundary` / `hit_rate` |
| 四级 | 运行日期 / 批次 | `20260803_r02` |

## 二、各目录应用

### `experiments/`（实验定义）

```text
experiments/
└── v1/                       # 一级：版本
    ├── rtl/                  # 二级：类型
    │   └── rule_update/      # 三级：实验
    │       ├── config/       # 配置
    │       ├── scripts/      # 脚本
    │       └── README.md     # 基线 / 输入 / 命令 / 证据去向
    └── power/
        └── hit_rate/
```

### `project_docs/evidence/`（实验结果，自包含证据包）

```text
project_docs/evidence/
└── v1/                       # 一级：版本
    ├── rtl/
    │   └── rule_update/
    │       └── 20260803_r02/ # 四级：日期_批次（证据包：README+结果+hash）
    └── power/
        └── hit_rate/
            └── 20260805_r01/
```

### `versions/`（版本快照，已按版本）

```text
versions/
└── v1/
    ├── code/  project/  experiments/  docs/
```

## 三、命名规则

- 一级：基线 ID（`v<N>` 或 `<基线ID>`）
- 二级：实验类型（小写）
- 三级：具体实验（下划线）
- 四级：`<YYYYMMDD>_r<N>`

## 四、查找

沿层级：**版本 → 类型 → 实验 → 日期**，逐级进入即定位；或搜索基线 ID / 实验名 / 日期。

## 五、规则

1. 新内容按层级归入，不另起散乱位置。
2. 不同版本、不同实验绝不混在单目录。
3. 临时文件放 `scratch/`；归档位置见 `ARCHIVE_POLICY.md`。
