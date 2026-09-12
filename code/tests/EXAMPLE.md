# 示例测试

> 复制为 `test_<对象>.py`（Python）或 `<对象>_test.*`。

## 结构建议

- 命名：`test_<对象>.py`
- 断言：每项断言注明预期与依据
- 结果：日志与报告归 `project_docs/evidence/`

## 示例断言块

```python
def test_example():
    # 预期：...（依据：project_docs/evidence/...）
    assert result == expected
```

## 规则

1. 关键回归绑定具名基线（`project_docs/baselines/`）。
2. 大数据走 `data/` 治理，不放入 `code/tests/`。
