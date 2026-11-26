# V5 中文稿定稿验收

| 交付物 | 字节数 | SHA-256 |
|---|---:|---|
| [中文 TeX](../../manuscript/FAECO_v3_后布局可调预算面积回收.tex) | 83,529 | 56d0e4add9d0143284c056dd97f8895215268d81c806f89b855fe076261c90d2 |
| [中文 PDF](../../FAECO_v3_后布局可调预算面积回收.pdf) | 1,555,600 | 7fb37c1b55178c2e66f43e51e3c58bdb1ad5288d38701b8c61f44083a1150950 |
| [图 3](../../figures/tcad_20261126/fig3_anytime_curves_v4_zh.pdf) | — | c1acb2be43b7ddb33d2104a8b257f4a10adc1d413fa7db4f6e73b0a6927c4767 |
| [图 4](../../figures/tcad_20261126/fig4_ablation_v4_zh.pdf) | — | 638ebf577171281dd410d93ee9b55bc68633e80897aaea656c3c681cccb8551e |
| [图 5](../../figures/tcad_20261126/fig5_boxed_drc_scaling_v4_zh.pdf) | — | fe59ec474a6804b0afe87be62b72a8280b87342a7b122eb163f32a0e29e8ae59 |

- 显式选定中文主文件，LuaLaTeX 非交互双遍，零编译错误、零 Overfull、零缺字、零未定义引用。保留旧模板中 Times New Roman 的 OT1 字体形状及黑体、书宋粗斜体替代提示。24 条参考文献与首次引用顺序一致，38 个交叉引用标签唯一。英文摘要约 222 词，正文为中文工作稿。
- 13 页逐页渲染并完整目检，另以原分辨率检查第 8 页主表和第 13 页参考文献。13 页全部含正文或文献，参考文献末项同页保留。图 3–5 的最后输出在源 PDF 中有效文字下限均为 6.2 pt，在整页内分别约 6.16、6.07、6.02 pt。严格碰撞检查及同类面板对齐均通过，面板几何无豁免。保留原两幅机制示意，调整图 2 图注的例示范围。
- Windows 从 Git 发布提交清洁提取、默认开启 CRLF 转换的场景复算通过，标准库 Python 以隔离模式执行，读取 297 份原件和 37 份审稿补证。公开复算见[实验索引](../../../../project_docs/evidence/tcad_v5_revision_20261126/REPRODUCIBILITY.md)。
- 在终审交付 `af07096c` 基础上，只改第 803 行致谢，按原调用与图像复算注明图 1–2 的 Google Antigravity `generate_image`。LuaLaTeX 双遍仍为 13 页；115 dpi 像素比对仅第 13 页致谢区域变化。另以 150 dpi 目检末页，核实工具名、双栏边界及参考文献末项 [24]。主目录、源目录和本地 build 目录的三个 PDF 同 SHA-256。 [图件溯源](../../figures/CHANGE_LOG.md)
