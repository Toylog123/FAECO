# R22 独立静态探针补充

日期：2026-10-14。新族 C′；本文件仅记录控制逻辑的静态验证，无 EDA。

被测生产源码：已钉定 `28c3c2b5c6325ffbad4e4ac54cc3caab237d68a5`。逐一读取 `pinned_manifest.json` 的 43 个生产文件并核 SHA256：全部一致。新增测试不改变生产 source pin。逐文件 hash、解释器、测试列表、耗时与 JUnit hash 见 `domain_static_probes.json`。

本次新文件 `code/tests/test_r22_static_action_gates.py` 有 13 项；联合复跑 static flow、candidate policy、STA launch，共 **39 passed / 0 failed，0.93 s，exit 0**。使用 Python `subprocess.run(..., timeout=120)` 包装 pytest。先尝试仓库 Bash 超时包装器，但 WSL 找不到 Python，未执行测试；改为本机 Python 同等超时包装后通过。没有调用 Yosys/OpenSTA。

| 门 | 被执行路径与输入 | 反例断言及结果 |
|---|---|---|
| P3 | candidate policy；λc=0/1/20 | cover-only 门集相同；weighted-only 不泄漏 cover/旧来源；Full 明确 cover-first；通过既有参数化测试 |
| P4 | 真实 flow；两门锥，只有 g2 critical | weighted R recompute 输入为完整 `{g1,g2}`，legacy 保持 `{g2}`；通过。R可用性由记录桩返回，验证调用域 |
| P6 | 真实 flow；相同初始 epoch，固定/seed1/2/3 | base hash、两区域 pool hashes 相同，dispatch hashes 仅排列变化；通过 |
| P7 | 真实 evaluator `__call__`；10门链，窗口 `{g1,g2,g3}`，critical 含窗口外 g8，max_instances=2，JOINT=0/2，TOPOLOGY off | 全部 R/G/B、JOINT 候选的原门改动仅 `{g3,g2}`；JOINT off 不出现该类型；TOPOLOGY 不出现。空/不存在窗口被拒绝，无全critical fallback；通过 |
| P8 | 真实 `_eval_one`；K=1/2，依次 G/JOINT/B 三个不同动作 | 实际 launch 数=sta_used=cap；超额候选在 STA 前拒绝；cache重放不加序号/预算。K=0拒绝复跑既有测试；通过 |
| P11 | 真实 `_eval_one`，真实 Liberty等价与boundary checker；N10/N20 × G单门/JOINT双门，统一15% | N10：G=.10通过，JOINT=.20硬F3；N20：G=.05、JOINT=.10均通过。F3在STA后判定，拒绝仍消费launch；通过 |
| P11 B | N10/N20 B输入缓冲，identity库单元 | 原门只改g2，新wire被声明，新buf输入B/输出新网，唯一driver且F1/F2/F3通过；故障注入删新wire后真实F2在STA前拒绝；通过 |

正常探针保留真实候选生成、重写、改单元统计和安全检查，仅替换 STA 进程边界。缺 wire 负例另外对候选生成结果注入声明丢失。STA 桩返回确定的改善/不改善数值，不能用于论文时序效果或最终 SEC 结论。

主线另报告最新整体回归 **644 passed / 4 skipped / 156 subtests，99.14 s，超时包装102 s**；本审查者独立运行的是上述 39 项，不将两组数字相加或冒称独立复跑完整套件。P1–P12 逐门总对照见 `project_docs/planning/R22_CODE_REVIEW_20261014.md`。真实 R/G/B参与、来源/预算与提交账、输入/工具及独立最终 SEC 由固定 pilot 动态门核验。
