# schemas — 数据结构定义

> 放受跟踪的数据字段与文件格式定义。形式：`<数据集>.schema.md`。

示例：

| 字段 | 类型 | 说明 |
|------|------|------|
| ts | int64 | 时间戳（epoch ms） |
| src_ip | string | 源 IP |

数据实际文件在 `raw/` / `derived/`（git-ignored），本目录只定义其格式。
