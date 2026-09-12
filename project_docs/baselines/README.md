# baselines — 具名基线

> 版本定义 = **论文 + 源码 + 测试 + 证据** 的四元绑定。工作树名、运行目录名不定义版本。

- `BASELINE_INDEX.csv`：基线登记表（`active` / `superseded` / `archived`）。
- `BASELINE_TEMPLATE.md`：新基线文档模板。
- `BASELINE_MANIFEST_<日期>.sha256`：冻结时的 SHA-256 清单（由 `code/scripts/make_manifest.sh` 生成）。

流程：立项评估通过 → 建基线 → 阶段完成打 tag → 完整复制为 `versions/` 快照。详见 `../versioning.md`。
