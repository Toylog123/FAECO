# 第九轮机制图与整体结构复审对照

审阅对象为 [第八轮 12 页中文主稿](../r20261127_r8_mechanism/R8_RELEASE_MANIFEST.json)，基线提交 `12d201420ab89d284d867c828f25fce4c815edcc`。原复审意见共 15,157 字节，SHA-256 为 `354316211393867b1591f670960c4abebe3fefe6e3dd292438703621e3b78baa`，原件保存于本地忽略目录。交付目标为 12 页、6 图、7 表、1 算法，冻结实验和第七轮独立补件沿用。

## 审稿意见与核对

| 意见 | 对照与落点 |
| --- | --- |
| P0，图 2(a) 澄清规则半径 | 增加交互距离上界的图文标识。命题 1 式（5）用异网图形相交定义短路，式（7）用 $r_{\mathrm{drc}}(\ell)\le H_{\mathrm{row}}$ 约束所考查规则的交互距离，式（8）和式（9）分别给出多实例覆盖与请求盒。 |
| 图 2(b) 保持四种区域可辨 | 请求盒、工作单元检查盒、上下文盒与返回标记各有用途。选择工作单元时要求检查盒与请求盒相交，返回标记时要求标记包围盒与请求盒相交。工作单元从独立外扩的上下文盒读取几何。 |
| P0，图 4(b) 明确队列快照 | 图中阶段表示派发前或相应状态更新完成后的快照。算法 1 先从 $\mathcal Q$ 取出队首批次，随后计算和检查累计动作身份。该定义也适用于二分后仍在队列中的 $B_1$。 |
| P1，图 4(b) 恢复重排指引 | 首次符合暂缓条件并启用电容优先级时，按式（11）重排未访问后缀，保留已验收累计集及暂缓队列状态。 |
| 图 4(a) 的集合含义 | 已验证的 $T_3\subsetneq S_{18}$ 对应 $\Phi(T_3)=0$、$\Phi(S_{18})=1$，因此一次子集拒收不足以判定其超集。图 4(a) 与图 3 的三门提议分别对应原有不同证据。 |
| P1，图 4(c) 补足缓存命中动作 | 对同一冻结输入、验收配置与精确累计动作身份下的合格 Setup 拒收，命中后跳过物理验证。多门批次按原序二分并入队首，单门批次直接转下一轮。 |
| P2，图 3(b) 局部放大 | 在既有小图内加绘局部视窗，采用同一组归档标记和引脚几何；其他小图沿用原数据和绘制范围。 |
| P2，末页留白 | 以参考文献的段间距和行距为排版调节对象，保留原正文、图、表及伪代码的字号。 |
| P2，矢量与投稿规范 | 检查 PDF 实际路径、栅格对象及字体嵌入。核对 TCAD 对双栏模板、字体、页数和生成式 AI 的明文要求。正式英文 IEEE 稿与作者材料继续待确认。 |

## 证据交叉核查

- 直接读核固定 OpenROAD `b511b6a2bc936844b0319efc8b4972bb4ad7d911` 的 `TritonRoute.cpp`。代码通过 `drcBox.intersects(requiredDrcBox)` 选取工作单元，分别传入 `drcBox` 与 `extBox`，并在汇集标记时按标记盒与请求盒相交筛选。图 2(b) 的上下文完整性仍是标记召回的额外条件。 [规则及源码审计](../../../../project_docs/evidence/tcad_v5_revision_20261126/WINDOW_RULE_SCOPE.md#openroad-窗口上下文与标记) · [固定 OpenROAD 源码](https://github.com/The-OpenROAD-Project/OpenROAD/blob/b511b6a2bc936844b0319efc8b4972bb4ad7d911/src/drt/src/TritonRoute.cpp#L1181-L1241)
- 算法 1 的队首取批、缓存检查和复用后转轮顺序，与适用配置的源码路径相符。规范化动作检查发生于 `evaluate(trial)` 之前，命中转入既有拒收处理。多动作递归拆分，单动作直接返回；启用首次暂缓重排时，排序范围为未访问后缀。 [固定搜索源码](https://github.com/Toylog123/FAECO/blob/12d201420ab89d284d867c828f25fce4c815edcc/code/src/rseco/physical_budget_adapter.py#L306-L357) · [第八轮实测反例](../r20261127_r8_mechanism/R8_REVIEW_MAP.md#图-4-的实测反例)
- 图 3 的冻结参考 DEF、验收 DEF 和预览全块 DRC 报告与图源记录的 SHA-256 一致。将实际归档报告五条记录按图源原点变换后，类型、对象、层及每一坐标均与 JSON 精确一致。裁图中 `_21033_` 与 `net8148` 的三处 met1 标记有共同纵向范围，两个较窄标记包含于宽标记的包围盒内。按 DEF 的 `ROUTED` 与 `FIXED` 状态分离后，保护网 `_08943_` 的四个端口集合和完整路径几何一致。图上导线按 DEF 中心线编码，图内线宽仅用于辨认；LEF 轮廓和标记盒按归档坐标绘制。 [图源与复绘说明](../../figures/tcad_20261126/FIG2_AES_GEOMETRY_R6.md) · [冻结几何输入](../../figures/tcad_20261126/fig2_aes_geometry_r7.json)
- [R7 独立补件](../../manuscript/FAECO_R7_补充材料.pdf)继续绑定公开提交 `7ac9e86e6d8f1fc4a3003e129432f7b76fdcbe5a`，SHA-256 为 `5bd142b82c92331d46b730f1705d7b1ceaec8e28aaeba2f076b33320cf758036`。冻结实验继续使用 `f0fe992b9ce44b8368b620d06b8d95a56179347c`。

## IEEE TCAD 正式要求

- TCAD 现行投稿页 B 节要求使用 IEEE 双栏模板，明示最小字号 10 pt。常规稿的 14 页为硬上限，修回时所需作者照片与小传也须预留篇幅。当前是中文排版校样，正式英文稿需要按实际 IEEE 模板再核对。 [IEEE TCAD 投稿说明](https://ieee-ceda.org/publications/tcad/tcad-paper-submissions)
- TCAD G 节要求在参考文献之前的致谢中披露是否以及如何使用生成式 AI，写明系统及使用范围。披露覆盖文本、图片和代码等内容，未用也须声明。当前中文稿列明 OpenAI Codex 对正文、英文摘要、复算脚本与核对的辅助，用 ImageGen 处理图 1、图 2、图 4 的构图草案，并注明最终矢量图的证据来源。英文稿应同步据实披露。 [IEEE TCAD 投稿说明](https://ieee-ceda.org/publications/tcad/tcad-paper-submissions) · [IEEE 期刊作者通用政策](https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/)
- IEEE Author Center 接受图件 PDF，要求内嵌所用字体或将文字转路径。其图件说明建议足尺寸时图表文字约为 9–10 pt。图件字号建议、字体嵌入和期刊模板要求各按原文核对，正式英文稿需按最终排版复验。 [IEEE 图件格式](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-graphics-for-your-article/file-formatting/)

## 独立图件验收

在终版源 PDF 中读到图 2(a) 的交互距离上界标签，图 4(b) 的快照时点、下次派发与式（11）提示，以及图 4(c) 的物理验证跳过和后续队列动作。按 2.25 倍渲染目检图 2–4，图 3(b) 局部放大保留重合边界及归档坐标。

| 图号 | 矢量路径数 | 位图对象数 | 已嵌入字体对象数 |
| --- | ---: | ---: | ---: |
| 1 | 41 | 0 | 6 |
| 2 | 39 | 0 | 6 |
| 3 | 286 | 0 | 5 |
| 4 | 30 | 0 | 13 |
| 5 | 131 | 0 | 4 |
| 6 | 119 | 0 | 3 |

图 2、图 3、图 4 的核验 PDF SHA-256 分别以 `5a1e0347`、`ce5c8d8e`、`e7359319` 开头。

## 主稿定稿核验

- 主稿 12 页、6 图、7 表、1 算法、26 条参考文献。图 1–6 仍依次位于第 3–8 页，首次引用顺序与图号一致，重排引用的式（11）已与终版交叉引用核对。七张表及算法 1 的源块与 R8 一致，文献条目身份保持一致。
- 参考文献条目实测字号由 8.966 pt 提升至 9.963 pt，条间距加至 2.5 pt。第 12 页由 10 条增至 14 条，末行文字距页顶由 290.4 pt 移至 530.0 pt。主稿共 12 页，无新增分页。
- 对 12 页 Poppler 渲染逐页检查。LuaLaTeX 终版双遍无编译错误、盒溢出、排版欠满或未解析交叉引用，保留五条原有字体替代提示。主稿三份交付 PDF 同 SHA-256，随稿补件与公开 R7 Git 对象逐字节一致。 [工件清单](R9_RELEASE_MANIFEST.json)
- 全部调整为局部图义及版式校对。正式英文 IEEE 双栏稿、作者安排与投稿仍待作者确认，届时按正式模板重新验证字号、页数和致谢。 [TCAD 投稿规范](https://ieee-ceda.org/publications/tcad/tcad-paper-submissions)
