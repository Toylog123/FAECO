# V5 中文稿定稿验收

| 交付物 | 字节数 | SHA-256 |
|---|---:|---|
| [中文 TeX](../../manuscript/FAECO_v3_后布局可调预算面积回收.tex) | 84,201 | 5be6a90226f08e10a1a0483ab093fec75a6f2dac36a64d66fb2cb963c55bd97d |
| [中文 PDF](../../FAECO_v3_后布局可调预算面积回收.pdf) | 1,557,167 | 3e4b57195ec5bafd46b275a51f0458cdfca8e487e0bbb2ed63174396618f0b1f |
| [图 3](../../figures/tcad_20261126/fig3_anytime_curves_v4_zh.pdf) | — | c1acb2be43b7ddb33d2104a8b257f4a10adc1d413fa7db4f6e73b0a6927c4767 |
| [图 4](../../figures/tcad_20261126/fig4_ablation_v4_zh.pdf) | — | 638ebf577171281dd410d93ee9b55bc68633e80897aaea656c3c681cccb8551e |
| [图 5](../../figures/tcad_20261126/fig5_boxed_drc_scaling_v4_zh.pdf) | — | fe59ec474a6804b0afe87be62b72a8280b87342a7b122eb163f32a0e29e8ae59 |

- 显式选定中文主文件，LuaLaTeX 非交互双遍，零编译错误、零 Overfull、零缺字、零未定义引用。保留旧模板中 Times New Roman 的 OT1 字体形状及黑体、书宋粗斜体替代提示。26 条参考文献与首次引用顺序一致，38 个交叉引用标签唯一。英文摘要约 222 词，正文为中文工作稿。
- 13 页逐页渲染并完整目检，另以原分辨率检查第 8 页主表和第 13 页参考文献。13 页全部含正文或文献，参考文献末项同页保留。图 3–5 的最后输出在源 PDF 中有效文字下限均为 6.2 pt，在整页内分别约 6.16、6.07、6.02 pt。严格碰撞检查及同类面板对齐均通过，面板几何无豁免。保留原两幅机制示意，调整图 2 图注的例示范围。
- Windows 从 Git 发布提交清洁提取、默认开启 CRLF 转换的场景复算通过，标准库 Python 以隔离模式执行，读取 297 份原件和 37 份审稿补证。公开复算见[实验索引](../../../../project_docs/evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md)。
- 图 1–2 的披露修订版 `a01e1262` 确认 Google Antigravity `generate_image`，原机制图与数据图均继续使用同一工件。 [图件溯源](../../figures/CHANGE_LOG.md)
- 更新资源、读档与 AuDoPEDA 排序对照，绑定 `a10f314b` 证据。第一次排入第 25 条文献后单尾条落在第 14 页，压缩讨论的重复句后恢复 13 页。115 dpi 全页比对仅第 6–10、12–13 页发生变化，变化页全部目检，其余逐像素匹配已核版本。150 dpi 检查第 13 页的表 12、致谢、双栏边界和文献 [25]，主目录、源目录和本地 build 目录的三个 PDF 同 SHA-256。 [完整复审](REREVIEW_FINAL.md)

- V6 隔离重建修订仅更新文末代码与实验记录段，链接到 `194e3858`。双遍编译保留既有字体形态替代提示。对前版 13 页以 115 dpi 逐页比对，只有第 13 页左栏该段变化。150 dpi 目检该段、表 12、双栏及最后一条文献，38 个唯一标签、25 条按首用排序的文献复核通过。主目录、源目录及本地 build 目录的三份 PDF 同 SHA-256。 [V6 原件](../../../../project_docs/evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md#从独立输入副本重建-40-ns-处理器参考)

- 追加三臂与 SEC 修订绑定证据 `baab6f5f`，新增 TAPCO-G 预印本。第一遍布局有尾文献落入第 14 页，收紧重复文字后恢复 13 页。LuaLaTeX 双遍、13 页 115 dpi 比对和变动页目检通过，另以 150 dpi 核第 12–13 页、表 12 与文献 [26]。5 图、12 表、38 个唯一标签及 26 条文献复核通过，表 12 源逐字节一致。三份 PDF 副本同指纹，保留已记录的模板字体替代提示。 [实验索引](../../../../project_docs/evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md#重建参考后的三臂在线搜索)
