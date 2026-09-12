# Tests

后续测试放在这里。

测试原则：

- 每个算法模块必须有单元测试。
- 每个实验 flow 必须有最小回归测试。
- 等价验证、patch 替换、cut refinement 必须有失败案例测试。

当前测试命令：

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests
```

当前已有测试：

| 文件 | 覆盖内容 |
|---|---|
| `test_metrics_and_failures.py` | 修改比例、逻辑级数收益、F1/F3/F4 失败分类 |
| `test_case_loader_netlist_flow.py` | case loader、c17 Verilog 读取、最小 metrics 构造 |
| `test_graph_equivalence.py` | fanin cone 自动抽取、最小结构等价检查 |
| `test_cut_patch.py` | fixed-min-cut boundary、patch candidate 表示 |
