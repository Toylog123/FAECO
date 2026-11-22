# 图表复审记录（Round 6）

日期：2026-08-11  
对象：`faeco_paper_jcad.tex` 及其正文图表  
原则：只重排和重绘已有实验结果，不新增实验、不改变数值口径。

## 已处理问题

1. **ISCAS89 主结果**：由分组柱图改为基线--FAECO 配对哑铃图，直接标注每个电路的 WNS 变化。
2. **ITC-99**：保留全部 19 个电路，但按 b01--b13 与 b14--b22 分面，避免大规模电路的负 WNS 量级压缩小电路差异。
3. **收敛配置基线**：改为上下排列的质量点图与 STA 调用次数点图；STA 横轴使用对数轴，随机基线保留 3 种子标准差。
4. **SPEF 扫描**：拆为 s382 R 与 b18 JOINT 两个同纵轴面板，只标注非零改善点，避免原图的文字重叠。
5. **布线后验证**：新增已有 P&R 表格数据的配对差值图，正负颜色只表示改善/回退，不引入新的统计结论。
6. **正文版式**：更新图注和交叉引用；参考文献使用局部 `\small` 收回末页孤立条目，最终保持 11 页。

## 数据来源

- ISCAS89 预布局：`experiments/20260807_real_pr_iscas8/pre_layout_audit_summary.json`
- ITC-99：`experiments/20260805_tcad_sprint1_itc99/*/*/outerloop_result.json`
- P&R 配对差值：`experiments/20260807_real_pr_iscas8/post_route_audit_summary.json`，由已归档的 P&R 对比结果整理，无新增运行。
- 基线竞争图：论文原有 20 轮收敛结果及 3 个随机种子目录。

## 验证结果

- `python -m py_compile paper/zh/figures/gen_figures.py`：通过。
- P&R 8 条记录及 `fixed - baseline = delta`：通过。
- `latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error faeco_paper_jcad.tex`：通过。
- 输出：11 页 PDF；未检出 `Overfull`、`Fatal`、`Emergency`、未定义引用或未定义控制序列。
- 已用 Poppler 渲染最终 PDF，并复核图 5--11 所在页面及参考文献末页：未发现图形裁切、图注重叠、浮动体越界或空白孤页。

## 仍然保留的实验边界

图表只呈现已有确定性 STA/P&R 结果；没有为确定性单次测量虚构误差条，也没有把代理评分、SPEF 门控或 27/110 调用数差异改写为未经实验支持的因果结论。
