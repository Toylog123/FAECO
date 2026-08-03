# Paper Submission (占位)

更新时间：2026-07-31

投稿版本目录。当前为空，等待章节初稿全部获用户审定后从 `paper/draft/` 迁入。

## 计划结构

```
paper/submission/
├── README.md
├── introduction.md
├── related_work.md
├── method.md
├── method_symbol_table.md  (附录 A)
├── experiments.md
├── conclusion.md
├── cover_letter.md  (PM31 准备)
└── supplementary/
    ├── toolchain_snapshots.md  (附录 B：实验工具链详细版本)
    ├── stage_a_artifacts.md    (附录 C：Stage A 5-case 完整产物)
    └── stage_b_artifacts.md    (附录 D：Stage B 8-case 完整产物)
```

## 状态

- 当前 `paper/submission/` 仅本 README 占位
- 章节正文迁入等待 L01 / N05 / PM25 / PM27 / PM28 / PM29 全部获用户审定
- supplementary materials 等待各章节定稿后批量生成

## 边界

- 投稿版本与草稿版本分离，避免开发期间修改投稿版本
- 投稿版本一旦生成，必须有 Git tag（如 `submission-v1.0`）作为审计点
- [F08-B] DAC 2018 / [B06] BUFFALO 数据禁止进入投稿版本主表
- 任何 SKY130 techmap library 相关新内容必须先更新 R31-01 状态并同步 stage_b_pre_layout.json `notes`

## 后续修订

- PM31 投稿目标确定（中文期刊/会议）后，本 README 列出对应的格式要求与字数约束。
- PM32 投稿包准备时，本 README 增补 cover letter / supplementary checklist。