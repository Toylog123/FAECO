# python 脚本

> 放可复用的 Python 脚本。形式：

- 文件名：`<用途>.py`（如 `generate_plots.py`、`verify_package.py`）。
- 文件头：docstring 说明用途、用法、输入输出。
- 依赖在 `docs/environment.md` 登记。

```python
"""示例：生成报告。用法：python generate_plots.py"""
def main():
    ...
if __name__ == "__main__":
    main()
```
