# FAECO 严格复审综合意见（round 5）

更新时间：2026-08-11

本轮按 academic-paper-reviewer、Nature-style data/figure audit 与 user-academic-writing-style 三个视角复核；审查对象为 `faeco_paper_jcad.tex`、重新生成的主图、实验数据字典及 `experiments/` 中的原始产物。

## 综合结论

当前稿件没有需要新增主实验才能成立的科学性或数据完整性问题。正文主张已经按证据层级分开：20 轮策略收敛、27/110 次历史调用对照、ITC-99 19 电路、b18/b19 独立大电路补充、SPEF 估计复测、P&R 后时序核验和 hold 受控场景不再混为同一实验。

## 分视角结论

### Academic reviewer / EIC

- 贡献对象、接受谓词和实验对象已定义；历史主 runner 的测量顺序没有再被表述为未落地的 WNS 代理评分。
- 27/110 已改为描述性调用数差异；候选全集、排序版本和终值未统一保存，因此不再声称同候选空间上的无损加速。
- ITC-99 19 电路的 1693 次调用由 19 个 `outerloop_result.json` 逐项求和复核；18/19、b06 失败和 b20/b21 收益与原始 JSON 一致。
- b18/b19 已明确为不计入 19 电路统计的独立补充实验，避免图 6 的 19 电路主图与大电路补充数据混淆。
- 顺序 SEC、DRC signoff、跨工艺物理泛化、面积/功耗/拥塞和多角验证均以局限或未来工作表述；没有把未做实验写成已完成结果。

### Nature-style data and figure audit

- 主结果图现在直接读取 ISCAS89 预布局审计汇总和 ITC-99 逐电路 JSON；主图不再依赖手填主结果数组。
- 16 个 P&R 预布局核验日志、16 个布线运行日志和 16 个 `final.odb` 已绑定；无 DRC 报告，因此正文保留“布线后时序核验”限定。
- SPEF 扫描和迭代门控已改成“各自使用同一电路的配对基线/修复网表”，不再暗示跨批次共用一张映射网表。
- Nature 风格数据/代码可得性审计已单独记录在 `nature_data_availability_audit_round5.md`。正式投稿前仍需把复现实验包上传到稳定仓库并补真实 DOI/accession；本轮没有虚构外部链接。
- `paper/zh/figures/nature/` 已生成同批图件的 PDF/PNG 版本；当前 JCAD PDF 继续使用 PNG，适配 Nature 时应优先提交矢量版本并按目标期刊规范复核。

### User academic writing style

- 贡献中心线索保持为“候选生成—OpenSTA 实测—失败反馈—物理筛选”，没有把审稿过程或工程防御性说明写进正文。
- 数字集中在图表和实验段落，摘要只保留支持主结论所需的范围和比例。
- 术语先定义后使用；“代理评分”“SPEF”“SEC”“DRC signoff”等均与实际实现边界绑定。
- b18/b19 错配修正后，摘要、方法、实验、结论和局限没有发现新的口径冲突。

## 回归证据

- `python -m pytest -q`：268 passed，1 subtests passed。
- `latexmk -xelatex`：11 页 PDF，编译成功。
- LaTeX 日志：无 Overfull、Fatal、Undefined control sequence 或未定义引用/引用警告。
- PDF 视觉检查：摘要页、ITC-99/基线页、P&R/SPEF 页和附录页无裁切、重叠或表格越界。

## 仍需在投稿前完成的非科学动作

只剩外部 artifact 发布：上传代码、JSON、STA/P&R 日志、必要的 `final.odb`、图表源文件与数据字典，补真实稳定链接和 DOI/accession。该动作不要求新增实验，也不能用本地路径替代公开仓库标识。
