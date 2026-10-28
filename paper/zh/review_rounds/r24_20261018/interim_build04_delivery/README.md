# r24 中文稿与配图修订交付（2026-10-18）

当前可审阅工作稿：`paper/zh/manuscript/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.tex`，SHA `a290d707665101d3e691387855a16a3b491c4813f3138ef927b434e135ed65ed`；PDF `paper/zh/build/FAECO_面向预布局门级时序ECO的候选探索与失效刻画.pdf`，SHA `ce085898f1d1ef1162546bd9e8b70cc1bf5cfa508e8dcc10c628609102bcb04e`。15页、9图、18表、14参考文献，三个PDF副本SHA相同；修改前两个镜像PDF已另行备份。原r23审稿与原7图保持不变。

本轮8批原生TeX定点修改的前后精确文本和SHA链见`EDIT_*.json`，总差异见`MANUSCRIPT_REVISION.diff`，最终绑定见`FINAL_PACKAGE.json`。这不是Markdown ARS补丁执行，不声称其授权验证PASS。

## 修改与验证

- `RESPONSE_TO_REVIEW.md/json`逐22条回应：18条在明确证据范围内落实，REV-01/02/05/21仍部分落实；不自动撤销Major Revision。
- 文献定位、算法2/真实六门例、C′72受控组、b17端点与新证明、A8状态关系、三态证明域和同库面积均有原件绑定。
- 新增全部72运行收益/成本图及逐6858次真实STA的已提交收益曲线，保weighted零差异及随机臂局部领先；旧反馈和负收益图保留。
- 新双侧负载配对先记录原raw层级43partial失败，再以逐连接/状态保持的flat派生输入+两个原→flat SEC补验。新24STA得到理想+.15ns、基础长度10μm+.11ns、40/160μm均0，八真实注释全0；不恢复原raw支持或旧F6。
- `build04/BUILD_RECEIPT.json`两遍LuaLaTeX rc0且源pin稳定；`build04/render_qa/STATIC_RENDER_QA.json`与`build04/render_qa/ROOT_VISUAL_QA.json`完成全部15页布局自检，无溢出/缺字/悬空引文。字体回退警告仍如实保留。
- `FIGURE_MANUSCRIPT_CROSSCHECK`37项及`PHYSICAL_MANUSCRIPT_CROSSCHECK`8项是有界作者核对；`ROOT_CURVE_ACCEPTANCE`独立重算曲线与40共同预算反证比较，不是新的盲审。

## 仍待推进

| 任务 | 状态 | 完成标准 |
|---|---|---|
| 历史身份与D/归档 | pending | D正式56和全部8raw包根验收后，按源锁顺序恢复同族证据；当前仍28/56及3/8 |
| 强外部性能基线 | pending | 兼容接口、同库/输入/预算，真实运行而非引用推断 |
| 固定候选池纯排序 | pending | 与策略级总效果分开，对同一全集做多种子次序重放 |
| 原raw层级SPEF及三态证明 | pending | 分别实现完整leaf注入和保enable/Z语义的功能验证后回归；flat或二态删除语义不替代 |

生产代码清洁、HEAD仍`f761ee1996a83fc4f0f3de0999b74d85a8237858`；两门齐前不提交/push。当前上下文与问题清单以`project_docs/agent_handoff/`及`project_docs/OPEN_ISSUES.md`为准。
