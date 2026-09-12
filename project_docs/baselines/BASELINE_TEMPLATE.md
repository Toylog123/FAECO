# 基线：<BASELINE_ID>

> 基线定义当前版本：绑定论文、源码与证据。工作树名、运行目录名不定义版本。

- 创建日期：YYYY-MM-DD
- 论文：`paper/zh/manuscript/[主稿件].tex`
- 源码基线：[commit / manifest]
- 证据：`project_docs/evidence/[证据根]/`
- 状态：active / superseded / archived

## 绑定内容

| 项目 | 版本 / 路径 | 说明 |
|------|-------------|------|
| 论文 | … | … |
| 源码 | … | … |
| 测试 | … | 与源码同 commit / 按版本子目录 |
| 证据 | … | … |
| 清单 | …（SHA-256 manifest，含源码 + 测试 + 证据） | … |

## 冻结规则

- 基线一旦标记 superseded 即不可变，作为历史参照保留。
- 新基线须通过完整功能门 + 独立验证后才能取代旧基线。
- 不要在旧基线证据中拼接新基线数据。
