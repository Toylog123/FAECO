# 原B族时序观察的功能证明状态标记

复用原review_r21_figures.py中unified_results()及原B族汇总数据。30行保持原顺序，所有原CSV字段逐字符串核对相同：8 ISCAS89、19 ITC-99和3 PicoRV32（29个数值及regs不适用）。没有导入C′或任何新测量，没有修改原图4、图6或图7。

仅b09、b20、b21改为空心端点和虚线段，图例写“功能证明不支持”。三者实际使用三态类型及旧模型缺漏从r22_b_model_audit_20261016/audit.json（SHA0869d234751af08715a15a58c98636e7ae193d8a1d423401f6181fc88a83365d）实际读取。Pico两例及b17不标为该unsupported状态；未标记不代表本图新增了任何功能证明。原B族时序观察保留，不能把三态组三个较大改善合并为功能已证明收益。原runtime模型身份限制仍保留。

**建议图注补句。** 空心端点与虚线表示b09、b20、b21的实际三态单元超出归档二态证明模型的支持域，其时序观察仍显示，但不计为功能证明通过；其它对象的证明范围与来源见表及正文。PicoRV32 regs无setup路径，改善与证明均不适用。此图各值仍来自原B族统一跨测试集配置。

为三列渲染对齐，保留原棒棒图结构并改为等宽轴；图幅170×90mm给底部状态图例留空间。数据集组名保留，组内改善比率移由TeX图注/正文解释。去除纵网格防止穿过原值标注，无数据删减。Microsoft YaHei/SimHei/Arial字体链与原稿一致；PDF/SVG可编辑、PNG600dpi。

源预检19P/2W/0F，WARN为170mm现稿图幅和PNG预览。actualPDF最小7pt，全部字体嵌入，所有文本边界在页面内；对齐PASS0F0W。碰撞审计0FAIL/2WARN（REVIEW REQUIRED）已逐项实看：+2.75和+1.13数值跨过空白axes填充边缘进入同白色gutter，未碰线、未碰字、未超页面，数据仍完整。它们不是被忽略的实际碰撞，不改变值或删除数据来消警告。三panel及完整PDF渲染已实看；最初QA分面裁片切到了c组标签，改裁片分界后b/c已重新实看，正式图从未裁切。根验收待。

source.csv新增functional_proof_annotation字段，只三例为unsupported_true_tristate；其余为not_flagged_by_this_annotation或无setup路径的不适用。SOURCE_BINDING保存三份精确输入的SHA，SOURCE/QA快照及FINAL_MANIFEST保存复制与核验入口。
